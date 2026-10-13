#!/usr/bin/env python3
"""Generate source-linked machine records for PDF pages 1--6 of b917793k."""
import json
from pathlib import Path

DOC = "doc_4e9a90c5ea8a1795"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(*pages):
    ids = []
    for page in pages:
        ids += [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    return ids


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


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
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


def record(suffix, kind, evidence, participants, conditions, outcomes, notes=None, unresolved=None, step_ids=None):
    if step_ids is None:
        step_ids = [p["entity_id"] for p in participants]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{"step_id": "reaction", "participant_ids": step_ids, "conditions": conditions}] if conditions else [],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or ["No explicitly associated SI was supplied; structures and omitted operational details remain unverified."],
        },
    }


records = []

# Table 1: fourteen independent optimization experiments.
table1 = [
    (1, 1.2, "MeCN", None, 19.5, 19, 35, "35/65", 7, False),
    (2, 1.2, "MeCN", ("Li2CO3", 2.0), 11.5, 12.5, 4.5, "74/26", 8, False),
    (3, 2.0, "MeCN", ("Li2CO3", 2.0), 14, 32, 13, "71/29", "table dash (–)", False),
    (4, 2.0, "MeCN", ("Na2CO3", 2.0), 19.3, 9, 3, "75/25", 3.5, False),
    (5, 2.0, "MeCN", ("K2CO3", 2.0), 19.3, 10, "table dash (–)", "87/13", 28, False),
    (6, 2.0, "MeCN", ("Cs2CO3", 2.0), 19, "trace", "trace", "table dash (–)", 33, False),
    (7, 3.0, "anhydrous MeCN", None, 9, 26, "table dash (–)", "98/2", "table dash (–)", True),
    (8, 3.0, "anhydrous MeCN", ("H2O", 0.5), 10.5, 60, 1.6, "97/3", "table dash (–)", True),
    (9, 3.0, "anhydrous MeCN", ("H2O", 1.0), 10, 26, 1.3, "95/5", "table dash (–)", True),
    (10, 1.5, "MeCN/H2O = 5/1", None, 12, "table dash (–)", 54, "1/99", 3, False),
    (11, 1.5, "MeCN/H2O = 3/1", None, 11.5, "table dash (–)", 50, "1/99", 2, False),
    (12, 1.5, "MeCN/H2O = 2/1", None, 11.5, "table dash (–)", 57, "1/99", 4, False),
    (13, 1.5, "MeCN/H2O = 1/1", None, 10.5, "table dash (–)", 44, "1/99", "table dash (–)", False),
    (14, 1.7, "MeCN/H2O = 2/1", None, 14.7, "table dash (–)", 56, "1/99", "table dash (–)", False),
]
e12 = ev(1, 2)
for entry, sel_eq, solvent, additive, hours, y3, y4, ratio, recovery, under_n2 in table1:
    parts = [
        participant("substrate_1a", "reactant", "1a", e12, "ethyl 2-methyl-4-phenyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccccc1"),
        participant("selectfluor_2", "reagent", "2", e12, "Selectfluor", amounts=[field("equivalents", qty(sel_eq, "equiv"), e12)]),
        participant("product_E3a", "product", "E-3a", e12, "ethyl 3-fluoro-2-methyl-4-oxo-4-phenyl-2(E)-butenoate", "CCOC(=O)C(C)=C(F)C(=O)c1ccccc1"),
        participant("product_4a", "product", "4a", e12, "4-fluoro-3-methyl-5-phenyl-2(5H)-furanone", "CC1=C(F)OC(c2ccccc2)C1=O"),
        participant("solvent", "solvent", solvent, e12),
    ]
    if additive:
        parts.append(participant("additive", "reagent", additive[0], e12, amounts=[field("equivalents", qty(additive[1], "equiv"), e12)]))
    conditions = [field("temperature", qty(80, "°C"), e12), field("reaction_time", qty(hours, "h"), e12), field("solvent", solvent, e12)]
    if under_n2:
        conditions.append(field("atmosphere", "N2", e12))
        conditions.append(field("operation", "MeCN refluxed with CaH2 for 10 h and distilled immediately before use", e12))
    outcomes = [
        field("NMR_yield_E3a", qty(y3, "%") if isinstance(y3, (int, float)) else y3, e12, ["product_E3a"]),
        field("NMR_yield_4a", qty(y4, "%") if isinstance(y4, (int, float)) else y4, e12, ["product_4a"]),
        field("product_ratio_3a_to_4a", ratio, e12, ["product_E3a", "product_4a"]),
        field("recovered_starting_material_yield", qty(recovery, "%") if isinstance(recovery, (int, float)) else recovery, e12, ["substrate_1a"]),
        field("yield_measurement_basis", "1H NMR of crude mixture using 1,3,5-trimethylbenzene as internal standard", e12),
        field("ratio_measurement_basis", "19F NMR where marked by footnote d; otherwise source gives no separate method", e12),
    ]
    records.append(record(f"table1_entry{entry}", "optimization_entry", e12, parts, conditions, outcomes,
                          unresolved=["Structures are machine-encoded candidates and remain unverified; table dashes are preserved rather than interpreted as zero."]))


# Table 2 scope rows merged with the matching experimental paragraphs on pages 4--6.
table2 = [
    (1, "1a", "Ph", "Me", 10.5, "E-3a", 55, "97/3", 4, 0.20, 39.9, 0.60, 223.2, 2.0, 25.8, "CCOC(=O)C(C)=C(F)C(=O)c1ccccc1"),
    (2, "1b", "Ph", "Et", 10, "E-3b", 56, "98/2", 4, 0.30, 64.1, 0.90, 336.2, 3.0, 41.5, "CCOC(=O)C(CC)=C(F)C(=O)c1ccccc1"),
    (3, "1c", "Ph", "n-Pr", 11, "E-3c", 53, "98/2", 5, 0.31, 70.2, 0.91, 339.3, 3.0, 42.8, "CCOC(=O)C(CCC)=C(F)C(=O)c1ccccc1"),
    (4, "1d", "Ph", "Bn", 11.5, "E-3d", 45, "98/2", 5, 0.30, 83.9, 0.90, 336.1, 3.0, 42.1, "CCOC(=O)C(Cc1ccccc1)=C(F)C(=O)c1ccccc1"),
    (5, "1e", "p-FC6H4", "Me", 10, "E-3e", 45, "99/1", 5, 0.30, 65.8, 0.90, 335.6, 3.0, 34.1, "CCOC(=O)C(C)=C(F)C(=O)c1ccc(F)cc1"),
    (6, "1f", "p-ClC6H4", "Me", 10.5, "E-3f", 46, "98/2", 5, 0.30, 71.4, 0.90, 335.4, 3.0, 37.2, "CCOC(=O)C(C)=C(F)C(=O)c1ccc(Cl)cc1"),
    (7, "1g", "p-BrC6H4", "Me", 12, "E-3g", 55, "98/2", 5, 0.30, 83.8, 0.90, 335.5, 3.0, 51.5, "CCOC(=O)C(C)=C(F)C(=O)c1ccc(Br)cc1"),
    (8, "1h", "p-BrC6H4", "n-Pr", 10.5, "E-3h", 46, "98/2", 5, 0.29, 91.1, 0.89, 330.6, 3.0, 46.7, "CCOC(=O)C(CCC)=C(F)C(=O)c1ccc(Br)cc1"),
    (9, "1i", "p-MeC6H4", "Me", 10, "E-3i", 43, "98/2", 5, 0.30, 64.6, 0.90, 335.9, 3.0, 32.4, "CCOC(=O)C(C)=C(F)C(=O)c1ccc(C)cc1"),
    (10, "1j", "p-MeC6H4", "Et", 9.5, "E-3j", 39, "98/2", 5, 0.30, 69.3, 0.90, 336.0, 3.0, 30.7, "CCOC(=O)C(CC)=C(F)C(=O)c1ccc(C)cc1"),
]
for entry, sub, r1, r2, hours, prod, yld, ratio, detail_page, sub_mmol, sub_mg, sf_mmol, sf_mg, vol, prod_mg, prod_smiles in table2:
    pages = sorted(set([2, detail_page] + ([4] if entry > 1 else [])))
    evidence = ev(*pages)
    parts = [
        participant("substrate", "reactant", sub, evidence, f"2,3-allenoate {sub} (R1={r1}, R2={r2})",
                    amounts=[field("amount", qty(sub_mmol, "mmol"), evidence), field("mass", qty(sub_mg, "mg"), evidence)]),
        participant("selectfluor", "reagent", "2", evidence, "Selectfluor",
                    amounts=[field("amount", qty(sf_mmol, "mmol"), evidence), field("mass", qty(sf_mg, "mg"), evidence), field("equivalents", qty(3, "equiv"), evidence), field("purity", qty(95, "%"), evidence)]),
        participant("water", "reagent", "H2O", evidence, "water", amounts=[field("equivalents", qty(0.5, "equiv"), evidence)]),
        participant("mecn", "solvent", "MeCN", evidence, "anhydrous acetonitrile", amounts=[field("volume", qty(vol, "mL"), evidence)]),
        participant("product", "product", prod, evidence, smiles=prod_smiles),
    ]
    purification = "silica-gel chromatography; petroleum ether/ethyl acetate 80:1" if entry == 1 else ("flash chromatography; petroleum ether/ethyl acetate 100:1" if entry == 8 else "prepared according to Conditions A typical procedure; specific eluent not restated")
    conditions = [
        field("atmosphere", "N2", evidence), field("temperature", qty(80, "°C"), evidence),
        field("reaction_time", qty(hours, "h"), evidence), field("solvent", "anhydrous MeCN containing the stated water addition", evidence),
        field("operation", "H2O–MeCN premixed at 0.9 μL mL−1 (source notation)", evidence),
        field("workup", "quenched with water, ether extraction, brine wash, drying over Na2SO4, filtration and evaporation (typical procedure)", evidence),
        field("purification", purification, evidence),
    ]
    outcomes = [
        field("isolated_yield", qty(yld, "%"), evidence, ["product"]), field("product_mass", qty(prod_mg, "mg"), evidence, ["product"]),
        field("product_ratio_3_to_4", ratio, evidence, ["product"]), field("ratio_measurement_basis", "19F NMR spectrum of crude products", evidence),
        field("yield_measurement_basis", "isolated yield", evidence),
    ]
    records.append(record(f"table2_entry{entry}_{prod.lower().replace('-', '')}", "substrate_scope_entry", evidence, parts, conditions, outcomes,
                          notes=["The detailed paragraph is matched to the same table row by substrate and product labels."],
                          unresolved=["Candidate SMILES was derived from the fully specified product name but has not been independently structure-verified; no SI is associated."]))


# Table 3 scope entries, enriching the six examples whose detailed paragraphs occur on page 6.
table3 = [
    (1, "1a", "Ph", "H", "Me", "B", 14.7, 51, "4a", ">99/1", "table dash (–)", 1.7),
    (2, "1b", "Ph", "H", "Et", "B", 23.5, 50, "4b", ">99/1", "table dash (–)", 2.5),
    (3, "1c", "Ph", "H", "n-Pr", "B", 23.5, 47, "4c", ">99/1", "table dash (–)", 2.5),
    (4, "1e", "p-FC6H4", "H", "Me", "B", 26, 60, "4e", ">99/1", "table dash (–)", 1.7),
    (5, "1g", "p-BrC6H4", "H", "Me", "B", 21.5, 42, "4g", ">99/1", "table dash (–)", 1.7),
    (6, "1i", "p-MeC6H4", "H", "Me", "B", 21, 64, "4i", ">99/1", "table dash (–)", 1.7),
    (7, "1n", "Ph", "Me", "Me", "C", 5.3, 80, "4n", "table dash (–)", "99/1", 1.2),
    (8, "1o", "Ph", "Ph", "Me", "C", 5.5, 93, "4o", "table dash (–)", "99/1", 1.2),
    (9, "1p", "Ph", "Et", "Me", "C", 5.5, 95, "4p", "table dash (–)", "98/2", 1.2),
    (10, "1q", "Ph", "Et", "n-Pr", "C", 5, 91, "4q", "table dash (–)", "99/1", 1.2),
    (11, "1r", "Ph", "Et", "H", "C", 5, 76, "4r", "table dash (–)", "98/2", 1.2),
    (12, "1s", "-(CH2)5-", "", "Me", "C", 11, 30, "4s", "table dash (–)", "98/2", 1.2),
    (13, "1s", "-(CH2)5-", "", "Me", "C/MeNO2", 10.8, 42, "4s", "table dash (–)", "98/2", 1.2),
]
details3 = {
    1: (0.20, 40.7, 0.34, 126.6, 1.4, 0.65, 19.9),
    2: (0.20, 42.6, 0.50, 186.9, 1.3, 0.7, 20.3),
    3: (0.20, 46.5, 0.50, 187.3, 1.3, 0.7, 20.8),
    4: (0.39, 85.4, 0.66, 246.8, 2.7, 1.3, 48.6),
    5: (0.40, 113.0, 0.68, 254.8, 2.7, 1.3, 45.3),
    6: (0.40, 86.8, 0.68, 254.8, 2.7, 1.3, 52.6),
}
for entry, sub, r1, r3, r2, cond, hours, yld, prod, ratio43, ratio45, sf_eq in table3:
    evidence = ev(3, 6) if entry <= 6 else ev(3)
    sub_amounts = []
    sf_amounts = [field("equivalents", qty(sf_eq, "equiv"), evidence)]
    solvent_parts = []
    product_amounts = []
    if entry in details3:
        smmol, smg, fmmol, fmg, mecn_ml, water_ml, pmg = details3[entry]
        sub_amounts = [field("amount", qty(smmol, "mmol"), evidence), field("mass", qty(smg, "mg"), evidence)]
        sf_amounts += [field("amount", qty(fmmol, "mmol"), evidence), field("mass", qty(fmg, "mg"), evidence), field("purity", qty(95, "%"), evidence)]
        solvent_parts = [participant("mecn", "solvent", "MeCN", evidence, amounts=[field("volume", qty(mecn_ml, "mL"), evidence)]), participant("water", "solvent", "H2O", evidence, amounts=[field("volume", qty(water_ml, "mL"), evidence)])]
        product_amounts = [field("mass", qty(pmg, "mg"), evidence)]
    else:
        solvent_name = "MeNO2" if entry == 13 else "MeCN"
        solvent_parts = [participant("solvent", "solvent", solvent_name, evidence, amounts=[field("volume", qty(2, "mL"), evidence)])]
        if cond == "B":
            solvent_parts.append(participant("water", "solvent", "H2O", evidence))
    parts = [
        participant("substrate", "reactant", sub, evidence, f"2,3-allenoate {sub} (R1={r1}, R3={r3 or 'cyclic'}, R2={r2})", amounts=sub_amounts),
        participant("selectfluor", "reagent", "2", evidence, "Selectfluor", amounts=sf_amounts),
        *solvent_parts,
        participant("product", "product", prod, evidence, f"4-fluoro-2(5H)-furanone {prod}", amounts=product_amounts),
    ]
    solvent_text = "MeCN/H2O = 2/1 (v/v)" if cond == "B" else ("MeNO2" if entry == 13 else "MeCN")
    conditions = [field("temperature", qty(80, "°C"), evidence), field("reaction_time", qty(hours, "h"), evidence), field("solvent", solvent_text, evidence)]
    if entry <= 6:
        conditions += [field("workup", "water quench, ether extraction, brine wash, Na2SO4 drying, filtration and evaporation (typical procedure)", evidence), field("purification", "silica-gel chromatography; petroleum ether/ethyl acetate 30:1 (typical procedure)", evidence)]
    outcomes = [field("isolated_yield", qty(yld, "%"), evidence, ["product"]), field("product_ratio_4_to_3", ratio43, evidence, ["product"]), field("product_ratio_4_to_5", ratio45, evidence, ["product"]), field("ratio_measurement_basis", "19F NMR analysis of crude products", evidence), field("yield_measurement_basis", "isolated yield", evidence)]
    records.append(record(f"table3_entry{entry}_{prod}", "substrate_scope_entry", evidence, parts, conditions, outcomes,
                          unresolved=["Product and substrate structures are retained by label/R-group description; no independent structure verification or SI association is available."]))


# Scheme 1: failed alkyl substrate and ortho-chlorophenyl example.
e3 = ev(3)
parts = [participant("substrate", "reactant", "1k", e3, "2,3-allenoate 1k (R=n-C7H15, R2=Me)"), participant("selectfluor", "reagent", "2", e3, "Selectfluor", amounts=[field("equivalents", qty(3, "equiv"), ev(2, 3))]), participant("water", "reagent", "H2O", e3, amounts=[field("equivalents", qty(0.5, "equiv"), e3)]), participant("expected_3k", "product", "3k", e3), participant("expected_4k", "product", "4k", e3)]
records.append(record("scheme1_1k_conditionsA_failure", "reported_experiment", ev(2, 3), parts,
                      [field("atmosphere", "N2", e3), field("temperature", qty(80, "°C"), e3), field("reaction_time", qty(10.5, "h"), e3), field("solvent", "MeCN", e3)],
                      [field("formation_of_3k", "not formed", e3, ["expected_3k"]), field("formation_of_4k", "not formed", e3, ["expected_4k"])],
                      unresolved=["No product identity, isolated material, or workup is reported for the failed experiment."]))

parts = [participant("substrate", "reactant", "1l", e3, "ethyl 4-(2-chlorophenyl)-2-methyl-2,3-butadienoate"), participant("selectfluor", "reagent", "2", e3, "Selectfluor", amounts=[field("equivalents", qty(3, "equiv"), ev(2, 3))]), participant("water", "reagent", "H2O", e3, amounts=[field("equivalents", qty(0.5, "equiv"), e3)]), participant("product_3l", "product", "E-3l", e3), participant("product_4l", "product", "4l", e3)]
records.append(record("scheme1_1l_conditionsA", "reported_experiment", ev(2, 3), parts,
                      [field("atmosphere", "N2", e3), field("temperature", qty(80, "°C"), e3), field("reaction_time", qty(34.5, "h"), e3), field("solvent", "MeCN", e3)],
                      [field("isolated_yield_E3l", qty(34, "%"), e3, ["product_3l"]), field("isolated_yield_4l", qty(5, "%"), e3, ["product_4l"]), field("product_ratio_3l_to_4l", "87/13", e3, ["product_3l", "product_4l"])],
                      unresolved=["Exact batch quantities and product structures are not supplied on covered pages."]))


# Scheme 2: three distinct condition sets for substrate 1m.
for cond, hours, y4, y5, pages in [("A", 1.5, 93, 5, (3, 6)), ("B", 5, 86, 7, (2, 3)), ("C", 5.5, 90, "table dash (–)", (2, 3, 6))]:
    evidence = ev(*pages)
    sf_eq = 3 if cond == "A" else (1.7 if cond == "B" else 1.2)
    parts = [participant("substrate", "reactant", "1m", evidence, "ethyl 4,4-diphenyl-2-propyl-2,3-butadienoate"), participant("selectfluor", "reagent", "2", evidence, "Selectfluor", amounts=[field("equivalents", qty(sf_eq, "equiv"), evidence)]), participant("product_4m", "product", "4m", evidence, "4-fluoro-5,5-diphenyl-3-propyl-2(5H)-furanone"), participant("product_E5m", "product", "E-5m", evidence, "ethyl 3-fluoro-4-hydroxy-4,4-diphenyl-2-propyl-2(E)-butenoate")]
    if cond == "A":
        parts[0]["amounts"] = [field("amount", qty(2.01, "mmol"), evidence), field("mass", qty(0.6162, "g"), evidence)]
        parts[1]["amounts"] += [field("amount", qty(6.02, "mmol"), evidence), field("mass", qty(2.2435, "g"), evidence), field("purity", qty(95, "%"), evidence)]
    if cond == "C":
        parts[0]["amounts"] = [field("amount", qty(0.20, "mmol"), evidence), field("mass", qty(60.9, "mg"), evidence)]
        parts[1]["amounts"] += [field("amount", qty(0.24, "mmol"), evidence), field("mass", qty(85.3, "mg"), evidence)]
    solvent = "H2O/MeCN under N2 (Conditions A)" if cond == "A" else ("MeCN/H2O = 2/1 (Conditions B)" if cond == "B" else "MeCN (Conditions C)")
    conditions = [field("temperature", qty(80, "°C"), evidence), field("reaction_time", qty(hours, "h"), evidence), field("solvent", solvent, evidence)]
    if cond == "A": conditions.append(field("atmosphere", "N2", evidence))
    if cond == "C":
        conditions += [field("workup", "water quench, ether extraction, brine wash, Na2SO4 drying, filtration and evaporation", evidence), field("purification", "silica-gel chromatography; petroleum ether/ethyl acetate 30:1", evidence)]
    outcomes = [field("isolated_yield_4m", qty(y4, "%"), evidence, ["product_4m"]), field("isolated_yield_E5m", qty(y5, "%") if isinstance(y5, (int, float)) else y5, evidence, ["product_E5m"])]
    if cond == "A": outcomes += [field("product_mass_4m", qty(0.5558, "g"), evidence, ["product_4m"]), field("product_mass_E5m", qty(0.0375, "g"), evidence, ["product_E5m"])]
    if cond == "C": outcomes += [field("product_mass_4m", qty(52.8, "mg"), evidence, ["product_4m"]), field("product_ratio_4m_to_E5m", "98/2", evidence, ["product_4m", "product_E5m"]), field("ratio_measurement_basis", "19F NMR analysis of crude reaction mixture", evidence)]
    records.append(record(f"scheme2_1m_conditions{cond}", "reported_experiment", evidence, parts, conditions, outcomes,
                          unresolved=["No SI is associated; structures remain unverified. Details outside covered pages were not imported."]))


# Scheme 3: four failed/mixture experiments, preserving recovery separately.
e34 = ev(3, 4)
for cond, hours in [("B", 47.7), ("C", 6.5)]:
    parts = [participant("substrate", "reactant", "1k", e34, "2,3-allenoate 1k (R=n-C7H15, R2=Me)"), participant("selectfluor", "reagent", "2", e34, "Selectfluor", amounts=[field("equivalents", qty(1.7 if cond == "B" else 1.2, "equiv"), e34)]), participant("mixture", "product", "mixture", e34, "unidentified product mixture")]
    records.append(record(f"scheme3_1k_conditions{cond}_mixture", "reported_experiment", e34, parts,
                          [field("temperature", qty(80, "°C"), e34), field("reaction_time", qty(hours, "h"), e34), field("solvent", "MeCN/H2O = 2/1" if cond == "B" else "MeCN", e34)],
                          [field("reported_outcome", "mixture", e34, ["mixture"]), field("recovered_starting_material_yield", qty(9, "%"), e34, ["substrate"])],
                          unresolved=["Mixture components and product yield are not identified."]))
for solvent, hours, suffix in [("MeCN", 9, "mecn"), ("MeNO2", 13, "meno2")]:
    parts = [participant("substrate", "reactant", "1t", ev(4), "4,4-dialkyl-substituted allenoate 1t"), participant("selectfluor", "reagent", "2", ev(4), "Selectfluor", amounts=[field("equivalents", qty(1.2, "equiv"), ev(3, 4))]), participant("mixture", "product", "mixture", ev(4), "unidentified product mixture"), participant("expected_lactone", "product", "corresponding lactone", ev(3, 4))]
    records.append(record(f"scheme3_1t_conditionsC_{suffix}_mixture", "reported_experiment", ev(3, 4), parts,
                          [field("temperature", qty(80, "°C"), ev(3, 4)), field("reaction_time", qty(hours, "h"), ev(4)), field("solvent", solvent, ev(4))],
                          [field("reported_outcome", "mixture", ev(4), ["mixture"]), field("target_lactone_formation", "not afforded", ev(3, 4), ["expected_lactone"])],
                          unresolved=["Mixture identity and yield are not reported; substrate 1t is shown only as a structure/label on covered pages."]))


# Scheme 4 is a proposed mechanism, not a reported batch experiment.
parts = [participant("allenoate_1", "reactant", "1", ev(3, 4), "generic 2,3-allenoate"), participant("fluorinating_species", "reagent", "F+", ev(4), "electrophilic fluorine from Selectfluor"), participant("intermediate_6", "unspecified_agent", "6", ev(4), "cyclic intermediate"), participant("intermediate_5", "unspecified_agent", "5", ev(4), "fluorohydroxylation intermediate"), participant("product_3", "product", "3", ev(4), "3-fluoro-4-oxo-2(E)-alkenoate"), participant("product_4", "product", "4", ev(4), "4-fluoro-2(5H)-furanone")]
records.append(record("scheme4_proposed_mechanism", "mechanism", ev(3, 4), parts,
                      [field("operation", "proposed fluorination to cyclic intermediate 6, hydration to 5, then oxidation (Path I) or dealkylative lactonization (Path II)", ev(4))], [],
                      notes=["The paper explicitly presents this as a plausible mechanism; it is not treated as an independent experimental yield."],
                      unresolved=["Generic R-group structures and mechanistic intermediates are not assigned SMILES."]))


# Scheme 5: two independent 5 mmol scale batches.
e4 = ev(4)
parts = [participant("substrate", "reactant", "1a", e4, "ethyl 2-methyl-4-phenyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccccc1", [field("amount", qty(5.0, "mmol"), e4), field("mass", qty(1.0130, "g"), e4)]), participant("selectfluor", "reagent", "2", e4, "Selectfluor", amounts=[field("equivalents", qty(3.0, "equiv"), e4), field("amount", qty(15.0, "mmol"), e4), field("mass", qty(5.5996, "g"), e4), field("purity", qty(95, "%"), e4)]), participant("water", "reagent", "H2O", e4, amounts=[field("equivalents", qty(0.5, "equiv"), e4)]), participant("mecn", "solvent", "MeCN", e4, amounts=[field("volume", qty(50, "mL"), e4)]), participant("product_3a", "product", "E-3a", e4, amounts=[field("mass", qty(0.5162, "g"), e4)]), participant("product_4a", "product", "4a", e4, amounts=[field("mass", qty(0.0323, "g"), e4)])]
records.append(record("scheme5_large_scale_conditionsA", "reported_experiment", e4, parts,
                      [field("atmosphere", "N2", e4), field("temperature", qty(80, "°C"), e4), field("reaction_time", qty(11, "h"), e4), field("solvent", "H2O/MeCN premix", e4), field("workup", "water quench, ether extraction, brine wash, Na2SO4 drying, filtration and evaporation", e4), field("purification", "silica-gel chromatography; petroleum ether/ethyl acetate 80:1 to 20:1", e4)],
                      [field("isolated_yield_E3a", qty(44, "%"), e4, ["product_3a"]), field("isolated_yield_4a", qty(3, "%"), e4, ["product_4a"]), field("product_ratio_3a_to_4a", "94/6", e4, ["product_3a", "product_4a"])],
                      unresolved=["No SI is associated; candidate structures remain unverified."]))

parts = [participant("substrate", "reactant", "1a", e4, "ethyl 2-methyl-4-phenyl-2,3-butadienoate", "CCOC(=O)C(C)=C=Cc1ccccc1", [field("amount", qty(5.0, "mmol"), e4), field("mass", qty(1.0101, "g"), e4)]), participant("selectfluor", "reagent", "2", e4, "Selectfluor", amounts=[field("equivalents", qty(1.7, "equiv"), e4), field("amount", qty(8.5, "mmol"), e4), field("mass", qty(3.1655, "g"), e4), field("purity", qty(95, "%"), e4)]), participant("mecn", "solvent", "MeCN", e4, amounts=[field("volume", qty(33.5, "mL"), e4)]), participant("water", "solvent", "H2O", e4, amounts=[field("volume", qty(16.5, "mL"), e4)]), participant("product", "product", "4a", e4, "4-fluoro-3-methyl-5-phenyl-2(5H)-furanone", "CC1=C(F)OC(c2ccccc2)C1=O", [field("mass", qty(0.5532, "g"), e4)])]
records.append(record("scheme5_large_scale_conditionsB", "reported_experiment", e4, parts,
                      [field("temperature", qty(80, "°C"), e4), field("reaction_time", qty(15, "h"), e4), field("solvent", "MeCN/H2O = 2/1", e4), field("workup", "water quench, ether extraction, brine wash, Na2SO4 drying, filtration and evaporation", e4), field("purification", "silica-gel chromatography; petroleum ether/ethyl acetate 30:1", e4)],
                      [field("isolated_yield", qty(58, "%"), e4, ["product"])],
                      unresolved=["No SI is associated; candidate structures remain unverified."]))


assert len(records) == 49, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
