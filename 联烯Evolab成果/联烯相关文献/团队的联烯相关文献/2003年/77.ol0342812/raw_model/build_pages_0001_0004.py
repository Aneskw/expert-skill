#!/usr/bin/env python3
"""Build evidence-linked machine records for ol0342812, PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_e9526a5ba73b3346"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0004.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


E1, E2, E3, E4 = (ev(i) for i in range(1, 5))


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


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name is not None else []),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, conditions, outcomes, notes, unresolved):
    rid = f"{DOC}:{suffix}"
    step = []
    if participants or conditions:
        step = [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }]
    return {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": step,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SMILES = {
    "1a": "O=C(O)C(CCC)=C=Cc1ccccc1",
    "1b": "O=C(O)C(C)=C=Cc1ccccc1",
    "1c": "O=C(O)C(Cc1ccccc1)=C=Cc1ccccc1",
    "1d": "O=C(O)C(C)=C=Cc1cccc2ccccc12",
    "1e": "O=C(O)C(CCC)=C=Cc1cccc2ccccc12",
    "1f": "O=C(O)C(Cc1ccccc1)=C=CC",
    "3a": "O=C1OC(c2ccccc2)C(C3=C(CCC)C(=O)OC3c4ccccc4)=C1CCC",
    "4a": "O=C1OC(c2ccccc2)C=C1CCC",
    "3b": "O=C1OC(c2ccccc2)C(C3=C(C)C(=O)OC3c4ccccc4)=C1C",
    "3c": "O=C1OC(c2ccccc2)C(C3=C(Cc4ccccc4)C(=O)OC3c4ccccc4)=C1Cc1ccccc1",
    "3d": "O=C1OC(c2cccc3ccccc23)C(C2=C(C)C(=O)OC2c2cccc3ccccc23)=C1C",
    "3e": "O=C1OC(c2cccc3ccccc23)C(C2=C(CCC)C(=O)OC2c2cccc3ccccc23)=C1CCC",
    "3f": "CC1OC(=O)C(Cc2ccccc2)=C1C1=C(Cc2ccccc2)C(=O)OC1C",
}


def substrate(label, evidence, amounts=None):
    names = {
        "1a": "4-phenyl-2-propyl-2,3-butadienoic acid",
        "1b": "2-methyl-4-phenyl-2,3-butadienoic acid",
    }
    return part(f"substrate_{label}", "reactant", label, evidence,
                names.get(label), SMILES.get(label), amounts)


def product(label, evidence, amounts=None, entity=None):
    return part(entity or f"product_{label}", "product", label, evidence,
                None, SMILES.get(label), amounts)


def pdcl2(evidence, amounts=None, role="catalyst"):
    return part("pdcl2", role, "PdCl2", evidence, "palladium(II) chloride",
                "Cl[Pd]Cl", amounts)


def chemical(entity, role, label, name, smiles, evidence, amounts=None):
    return part(entity, role, label, evidence, name, smiles, amounts)


records = []

# Abstract/Table 2 general transformation. This is not an individual experiment.
generic_ev = E1 + E3
generic_parts = [
    part("generic_allenoic_acid_1", "reactant", "1 (R1/R2-variable 2,3-allenoic acid)", generic_ev),
    chemical("propyl_iodide", "reagent", "2a", "1-iodopropane", "CCCI", generic_ev,
             [field("equivalents", {"number": 5, "unit": "equiv"}, generic_ev)]),
    pdcl2(generic_ev, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, generic_ev)]),
    chemical("dma", "solvent", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", generic_ev),
    part("generic_bibutenolide_3", "product", "3 (R1/R2-variable bibutenolide)", generic_ev),
]
records.append(record(
    "general_oxidative_dimeric_cyclization_coupling", "general_scheme", generic_ev,
    generic_parts,
    [field("solvent", "DMA", generic_ev), field("temperature", {"number": 80, "unit": "°C"}, generic_ev)],
    [field("reported_scope_yield_range", {"minimum": 64, "maximum": 75, "unit": "%", "raw_text": "64-75%"}, E1,
           ["generic_bibutenolide_3"])],
    ["The abstract graphic summarizes the scope and is not an individual experiment."],
    ["Generic R-group structures cannot be assigned complete SMILES.", "Yield range aggregates multiple substrate-scope experiments."],
))

# Scheme 1 contains two conceptual arrows, neither a reported experiment.
for suffix, label, note in [
    ("scheme1_single_allene_concept", "single functionalized allene", "Conceptual intramolecular cyclization arrow."),
    ("scheme1_biallene_concept", "two different functionalized allenes", "Conceptual biallene cyclization-dimerization arrow."),
]:
    parts = [part("generic_reactant", "reactant", label, E2),
             part("generic_catalyst", "catalyst", "catalyst", E2),
             part("generic_product", "product", "generic bicyclic product", E2)]
    records.append(record(suffix, "general_scheme", E2, parts, [], [], [note],
                          ["Scheme 1 uses generic R/FG/X groups and supplies no experiment-specific quantities."]))

# Equation 1 is explicitly described as the authors' previously reported work (reference 12d).
eq1_parts = [
    part("generic_allenoic_acid", "reactant", "R-substituted 2,3-allenoic acid", E2),
    part("generic_allenyl_ketone", "reactant", "R-substituted 1,2-allenyl ketone", E2),
    chemical("pd_me_cn", "catalyst", "PdCl2(MeCN)2", "bis(acetonitrile)palladium(II) dichloride", None, E2,
             [field("catalyst_loading", {"number": 5, "unit": "mol%"}, E2)]),
    chemical("mecn", "solvent", "CH3CN", "acetonitrile", "CC#N", E2),
    part("furanyl_butenolide", "product", "4-(3'-furanyl)butenolide", E2),
]
records.append(record(
    "equation1_prior_work", "literature_example", E2, eq1_parts,
    [field("solvent", "CH3CN", E2), field("temperature", "r.t.", E2),
     field("time", {"number": 4, "unit": "h"}, E2)],
    [field("yield", None, [], ["furanyl_butenolide"])],
    ["The prose attributes equation 1 to reference 12d; it is not a new experiment in this article."],
    ["Generic R-group structures and the yield are not specified on this page."],
))


TABLE1 = [
    (1, None, None, "DMA", "CC(=O)N(C)C", {"number": 80, "unit": "°C"}, {"number": 4.5, "unit": "h"}, {"number": 0, "unit": "%"}, {"number": 76, "unit": "%"}),
    (2, "C3H7I", 5, "DMA", "CC(=O)N(C)C", {"number": 80, "unit": "°C"}, {"number": 10, "unit": "h"}, {"number": 74, "unit": "%"}, {"number": 0, "unit": "%"}),
    (3, "C3H7I", 3, "DMA", "CC(=O)N(C)C", {"number": 80, "unit": "°C"}, {"number": 6.5, "unit": "h"}, {"number": 62, "unit": "%"}, {"number": 0, "unit": "%"}),
    (4, "CH3I", 5, "DMA", "CC(=O)N(C)C", {"number": 80, "unit": "°C"}, {"number": 4, "unit": "h"}, {"number": 74, "unit": "%"}, {"number": 0, "unit": "%"}),
    (5, "CH3I", 3, "DMA", "CC(=O)N(C)C", {"number": 80, "unit": "°C"}, {"number": 6, "unit": "h"}, {"number": 60, "unit": "%"}, {"number": 20, "unit": "%"}),
    (6, "C3H7I", 5, "THF", "C1CCOC1", "reflux", {"number": 46, "unit": "h"}, "trace", {"number": 0, "unit": "%"}),
    (7, "C3H7I", 5, "MeCN", "CC#N", "reflux", {"number": 16, "unit": "h"}, {"number": 66, "unit": "%"}, {"number": 8, "unit": "%"}),
    (8, "C3H7I", 5, "EtOH", "CCO", {"number": 80, "unit": "°C"}, {"number": 10, "unit": "h"}, {"number": 42, "unit": "%"}, {"number": 14, "unit": "%"}),
    (9, "C3H7I", 5, "CH2Cl2", "ClCCl", "reflux", {"number": 39, "unit": "h"}, {"number": 0, "unit": "%"}, "trace"),
]


for entry, iodide, equiv, solv, solv_smiles, temp, duration, y3, y4 in TABLE1:
    evidence = E2 + (E3 if entry == 2 else [])
    sub_amounts = []
    pd_amounts = [field("catalyst_loading", {"number": 5, "unit": "mol%"}, E2)]
    solv_amounts = []
    prod_amounts = []
    if entry == 2:
        sub_amounts = [field("mass", {"number": 50, "unit": "mg"}, E3),
                       field("amount", {"number": 0.248, "unit": "mmol"}, E3)]
        pd_amounts += [field("mass", {"number": 2, "unit": "mg"}, E3),
                       field("amount", {"number": 0.011, "unit": "mmol"}, E3)]
        solv_amounts = [field("volume", {"number": 2, "unit": "mL"}, E3)]
        prod_amounts = [field("mass", {"number": 37, "unit": "mg"}, E3)]
    parts = [substrate("1a", evidence, sub_amounts), pdcl2(evidence, pd_amounts),
             chemical("solvent", "solvent", solv, solv, solv_smiles, evidence, solv_amounts),
             product("3a", evidence, prod_amounts), product("4a", evidence)]
    if iodide:
        is_propyl = iodide == "C3H7I"
        iod_ev = E2 + (E3 if entry == 2 else [])
        amounts = [field("equivalents", {"number": equiv, "unit": "equiv"}, E2)]
        if entry == 2:
            amounts += [field("volume", {"number": 0.13, "unit": "mL"}, E3),
                        field("mass", {"number": 224, "unit": "mg"}, E3),
                        field("amount", {"number": 1.32, "unit": "mmol"}, E3)]
        parts.insert(1, chemical("alkyl_iodide", "reagent", iodide,
                                "1-iodopropane" if is_propyl else "iodomethane",
                                "CCCI" if is_propyl else "CI", iod_ev, amounts))
    notes = ["Table 1 optimization row; zero and trace outcomes are preserved as printed."]
    unresolved = ["Supporting Information was mentioned but was not supplied or explicitly associated."]
    outcomes = [field("yield_3a", y3, E2, ["product_3a"]),
                field("yield_4a", y4, E2, ["product_4a"]),
                field("yield_measurement_basis", None, [])]
    conditions = [field("solvent", solv, E2), field("temperature", temp, E2), field("time", duration, E2)]
    if entry == 2:
        # Table 2 entry 1 and the typical procedure are the same experiment as Table 1 entry 2.
        parts += [
            product("3a (R*,R*) isomer", E2 + E3, entity="product_3a_rr"),
            product("3a (R*,S*) isomer", E2 + E3, entity="product_3a_rs"),
            chemical("ether_workup", "solvent", "ether", "diethyl ether", "CCOCC", E3,
                     [field("volume", {"number": 50, "unit": "mL"}, E3)]),
            chemical("water_wash", "reagent", "water", "water", "O", E3,
                     [field("volume_per_wash", {"number": 10, "unit": "mL"}, E3)]),
            chemical("mgso4", "reagent", "MgSO4", "magnesium sulfate", "[Mg+2].[O-]S(=O)(=O)[O-]", E3),
            chemical("petroleum_ether", "solvent", "petroleum ether", "petroleum ether", None, E3),
            chemical("ethyl_acetate", "solvent", "ethyl acetate", "ethyl acetate", "CCOC(C)=O", E3),
            chemical("dcm_eluent", "solvent", "CH2Cl2", "dichloromethane", "ClCCl", E3),
        ]
        outcomes += [
            field("diastereomer_ratio_RstarRstar_to_RstarSstar", "1:1.87", E3,
                  ["product_3a_rr", "product_3a_rs"]),
            field("diastereomer_ratio_measurement_basis", "1H NMR", E3,
                  ["product_3a_rr", "product_3a_rs"]),
            field("melting_point_temperature_RstarRstar", {"minimum": 143, "maximum": 145, "unit": "°C", "raw_text": "143-145 °C"}, E3,
                  ["product_3a_rr"]),
            field("melting_point_temperature_RstarSstar", {"minimum": 186, "maximum": 187, "unit": "°C", "raw_text": "186-187 °C"}, E3,
                  ["product_3a_rs"]),
        ]
        # Replace the missing measurement basis with the explicit isolated workup basis.
        outcomes[2] = field("yield_measurement_basis", "isolated after flash chromatography", E3, ["product_3a"])
        conditions += [
            field("workup", "diluted with ether; washed twice with water; dried over MgSO4; evaporated", E3),
            field("purification", "flash chromatography on silica gel with petroleum ether/ethyl acetate (5:1)", E3),
            field("operation", "the two isomers could be separated by flash chromatography on silica gel with CH2Cl2", E3),
        ]
        notes += ["Merged duplicate representations: Table 1 entry 2, Table 2 entry 1, and the typical procedure in footnote 15.",
                  "The water wash volume is recorded per wash; the procedure specifies two washes."]
        unresolved += ["Candidate product SMILES captures connectivity but omits the two relative stereochemical assignments; structure remains unverified."]
    records.append(record(f"table1_entry_{entry}", "optimization_entry", evidence, parts, conditions,
                          outcomes, notes, unresolved))


# Table 2 entries 2-6. Entry 1 is already merged into Table 1 entry 2 above.
TABLE2 = [
    (2, "1b", "3b", {"number": 4, "unit": "h"}, 64, "1:1.62", "isolation", None),
    (3, "1c", "3c", {"number": 11.5, "unit": "h"}, 75, "1:1.53", "isolation", None),
    (4, "1d", "3d", {"number": 4, "unit": "h"}, 71, "1:1.28", "1H NMR", None),
    (5, "1e", "3e", {"number": 4.5, "unit": "h"}, 64, "1:1.43", "1H NMR", None),
    (6, "1f", "3f", {"number": 3.5, "unit": "h"}, 72, "1.04:1", "1H NMR", 21),
]
for entry, sub, prod, duration, yld, ratio, ratio_basis, cyclo_yield in TABLE2:
    parts = [
        substrate(sub, E3),
        chemical("propyl_iodide", "reagent", "2a", "1-iodopropane", "CCCI", E3,
                 [field("equivalents", {"number": 5, "unit": "equiv"}, E3)]),
        pdcl2(E3, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, E3)]),
        chemical("dma", "solvent", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", E3),
        product(prod, E3),
    ]
    outcomes = [
        field(f"yield_{prod}", {"number": yld, "unit": "%"}, E3, [f"product_{prod}"]),
        field("yield_measurement_basis", None, []),
        field("diastereomer_ratio_RstarRstar_to_RstarSstar", ratio, E3, [f"product_{prod}"]),
        field("diastereomer_ratio_measurement_basis", ratio_basis, E3, [f"product_{prod}"]),
    ]
    notes = ["Table 2 substrate-scope row."]
    unresolved = ["Supporting Information was mentioned but was not supplied or explicitly associated.",
                  "Relative configurations for products other than 3a are tentative according to table footnote a.",
                  "Candidate SMILES omits relative stereochemistry and remains unverified."]
    if cyclo_yield is not None:
        parts.append(part("cycloisomerization_product", "product", "cycloisomerization product (label not specified in footnote c)", E3))
        outcomes.append(field("yield_cycloisomerization_product", {"number": cyclo_yield, "unit": "%"}, E3,
                              ["cycloisomerization_product"]))
        notes.append("Footnote c reports a cycloisomerization product in addition to 3f; no product label is printed in the footnote.")
    records.append(record(
        f"table2_entry_{entry}", "substrate_scope_entry", E3, parts,
        [field("solvent", "DMA", E3), field("temperature", {"number": 80, "unit": "°C"}, E3), field("time", duration, E3)],
        outcomes, notes, unresolved,
    ))


# Equation 2: stoichiometric PdCl2 control without alkyl iodide.
parts = [
    substrate("1a", E3),
    pdcl2(E3, [field("equivalents", {"number": 0.5, "unit": "equiv"}, E3)], role="unspecified_agent"),
    chemical("dma", "solvent", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", E3),
    product("3a", E3), product("4a", E3),
]
records.append(record(
    "equation2_half_equiv_pdcl2", "optimization_entry", E3, parts,
    [field("solvent", "DMA", E3), field("temperature", {"number": 80, "unit": "°C"}, E3),
     field("time", {"number": 2, "unit": "h"}, E3)],
    [field("yield_3a", {"number": 42, "unit": "%"}, E3, ["product_3a"]),
     field("yield_4a", {"number": 6, "unit": "%"}, E3, ["product_4a"]),
     field("yield_measurement_basis", None, [])],
    ["Control experiment using 0.5 equivalent PdCl2 and no alkyl iodide shown in equation 2."],
    ["Yield measurement basis and workup are not reported in the main-text equation.", "Supporting Information was not supplied."],
))


# Equations 3 and 4: high-boiling iodides are largely recovered.
for eqno, label, iod_name, iod_smiles, duration, prod_yield, recovery in [
    (3, "2c", "1-iodo-3-phenylpropane (candidate identity from drawing)", "ICCCc1ccccc1", 4.5, 72, 94),
    (4, "2d", "1-(3-iodopropyl)-4-methoxybenzene (candidate identity from drawing)", "ICCCc1ccc(OC)cc1", 4, 56, 95),
]:
    parts = [
        substrate("1a", E3),
        chemical("alkyl_iodide", "reagent", label, iod_name, iod_smiles, E3,
                 [field("equivalents", {"number": 5, "unit": "equiv"}, E3)]),
        pdcl2(E3, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, E3)]),
        chemical("dma", "solvent", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", E3),
        product("3a", E3),
    ]
    records.append(record(
        f"equation{eqno}_iodide_recovery", "optimization_entry", E3, parts,
        [field("solvent", "DMA", E3), field("temperature", {"number": 80, "unit": "°C"}, E3),
         field("time", {"number": duration, "unit": "h"}, E3)],
        [field("yield_3a", {"number": prod_yield, "unit": "%"}, E3, ["product_3a"]),
         field("recovery_yield_alkyl_iodide", {"number": recovery, "unit": "%"}, E3, ["alkyl_iodide"]),
         field("yield_measurement_basis", None, [])],
        [f"Control experiment in equation {eqno}; the alkyl iodide was recovered."],
        ["Names and SMILES for the high-boiling iodides are candidates transcribed from the drawings and require structure review.",
         "Yield/recovery measurement bases and workup are not stated in the main text.", "Supporting Information was not supplied."],
    ))


# Equation 5: reaction under argon.
parts = [
    substrate("1a", E3),
    chemical("propyl_iodide", "reagent", "2a", "1-iodopropane", "CCCI", E3,
             [field("equivalents", {"number": 5, "unit": "equiv"}, E3)]),
    pdcl2(E3, [field("catalyst_loading", {"number": 5, "unit": "mol%"}, E3)]),
    chemical("dma", "solvent", "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", E3),
    product("3a", E3), product("4a", E3),
]
records.append(record(
    "equation5_argon_control", "optimization_entry", E3, parts,
    [field("atmosphere", "Ar", E3), field("solvent", "DMA", E3),
     field("temperature", {"number": 80, "unit": "°C"}, E3), field("time", {"number": 4, "unit": "h"}, E3)],
    [field("yield_3a", {"number": 26, "unit": "%"}, E3, ["product_3a"]),
     field("yield_4a", {"number": 12, "unit": "%"}, E3, ["product_4a"]),
     field("yield_measurement_basis", None, [])],
    ["Argon-atmosphere control experiment shown in equation 5."],
    ["Yield measurement basis and workup are not reported in the main text.", "Supporting Information was not supplied."],
))


# Separate qualitative oxygen-bubbling observation; no time or yield is supplied.
parts = [
    substrate("1a", E3),
    chemical("oxygen", "unspecified_agent", "O2", "oxygen", "O=O", E3),
]
records.append(record(
    "pure_oxygen_bubbling_observation", "optimization_entry", E3, parts,
    [field("atmosphere", "pure O2 bubbled through reaction", E3), field("time", None, [])],
    [field("qualitative_rate_outcome", "reaction was much faster", E3), field("yield", None, [])],
    ["The prose reports only a qualitative rate observation with pure oxygen bubbling."],
    ["The complete reaction composition, exact rate/time, yield, and workup are not reported for this observation.",
     "Supporting Information was not supplied."],
))


# Proposed catalytic cycle in page-4 prose, classified as mechanism rather than experiment.
mechanism_ev = E3 + E4
mech_parts = [
    part("allene_substrate", "reactant", "2,3-allenoic acid/allene moiety", mechanism_ev),
    part("pdii", "catalyst", "Pd(II) species", mechanism_ev),
    part("pdzero", "unspecified_agent", "Pd(0) species", mechanism_ev),
    chemical("oxygen", "reagent", "O2", "oxygen", "O=O", mechanism_ev),
    part("alkyl_iodide", "reagent", "alkyl iodide (RI)", mechanism_ev),
    part("bibutenolide", "product", "bibutenolide 3", mechanism_ev),
]
records.append(record(
    "proposed_mechanism", "mechanism", mechanism_ev, mech_parts,
    [field("operation", "Pd(II) coordination to allene, double cyclic oxypalladation, reductive elimination, and O2/RI reoxidation of Pd(0)", mechanism_ev)],
    [],
    ["This is the authors' proposed mechanism based on the control experiments, not a separately reported experiment."],
    ["No kinetic or intermediate-isolation data are supplied on page 4."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "output": str(OUT),
    "records": len(records),
    "by_kind": {kind: sum(r["record_kind"] == kind for r in records)
                for kind in sorted({r["record_kind"] for r in records})},
}, ensure_ascii=False, indent=2))
