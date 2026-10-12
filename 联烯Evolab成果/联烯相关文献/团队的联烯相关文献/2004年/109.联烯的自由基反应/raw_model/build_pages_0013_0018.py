#!/usr/bin/env python3
"""Build evidence-linked records and coverage for PDF pages 13-18."""

import json
from pathlib import Path


DOC = "doc_eb61b148fa9cdbba"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0013_0018.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0013_0018.json"


def evid(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def all_evid(pages):
    return [evidence_id for page in pages for evidence_id in evid(page)]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence_ids, targets=None):
    item = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, smiles=None, amounts=None, name=None, evidence_ids=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence_ids) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(field_name, value, evidence_ids) for field_name, value in (amounts or [])],
    }


def record(sid, pages, kind, participants, conditions=None, outcomes=None, notes=None,
           unresolved=None, add_missing=True, step_specs=None):
    evidence_ids = all_evid(pages)
    conditions = list(conditions or [])
    outcomes = list(outcomes or [])
    if add_missing and kind == "literature_example":
        if not any(name == "temperature" for name, _ in conditions):
            conditions.append(("temperature", None))
        if not any(name == "time" for name, _ in conditions):
            conditions.append(("time", None))
        if not any("yield" in name for name, _, _ in outcomes):
            outcomes.append(("yield", None, None))

    participant_records = [part(*participant[:6], evidence_ids=evidence_ids) for participant in participants]
    if step_specs is not None:
        steps = [
            {
                "step_id": step_id,
                "participant_ids": list(participant_ids),
                "conditions": [fld(name, value, evidence_ids) for name, value in step_conditions],
            }
            for step_id, participant_ids, step_conditions in step_specs
        ]
    elif kind == "mechanism" or (kind == "general_scheme" and not conditions):
        steps = []
    else:
        steps = [{
            "step_id": "step1",
            "participant_ids": [participant[0] for participant in participants],
            "conditions": [fld(name, value, evidence_ids) for name, value in conditions],
        }]

    if kind == "literature_example":
        default_unresolved = [
            "Prior-literature example summarized by this review; it is not a new experiment reported by the review authors.",
            "No explicitly associated supporting information was supplied.",
            "The reviewed pages do not provide a complete original experimental procedure, workup, purification, or yield basis.",
        ]
    else:
        default_unresolved = [
            "Generic or mechanistic drawing; it is not an individual reported experiment.",
            "Generic substituents and/or transient radicals prevent a fully specified structure assignment.",
        ]

    return {
        "record_id": f"{DOC}:{sid}",
        "document_id": DOC,
        "source_reaction_id": sid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence_ids,
        "participants": participant_records,
        "steps": steps,
        "outcomes": [fld(name, value, evidence_ids, targets) for name, value, targets in outcomes],
        "notes": [fact(note, evidence_ids) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": default_unresolved + list(unresolved or []),
        },
    }


R = []

# Page 13: Scheme 28 mechanism and Scheme 29 generic/specific tandem additions.
R.append(record("p13_scheme28_tandem_pathways_mechanism", [13], "mechanism", [
    ("tethered_allene", "reactant", "generic radical-bearing tethered allene in Scheme 28", None, None, None),
    ("radical_b", "unspecified_agent", "b radical; b = Ts or Bu3Sn", None, None, None),
    ("products", "product", "Path A, B, and C products", None, None, None),
], notes=[
    "Scheme 28 compares 5-exo, 4-exo, and 6-exo pathways; a = NZ or CH, Z = NMe2, OBz, or OMe.",
    "The source states that Path B does not occur when a = CH.",
], add_missing=False))

R.append(record("p13_scheme29_generic_tosyl_tandem_cyclization", [13], "general_scheme", [
    ("diallene", "reactant", "X-tethered diallene; X = NPh, NTs, or O", None, None, None),
    ("ptsy", "reagent", "p-TsY; Y = Br or SePh", None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ("toluene", "solvent", "toluene", "Cc1ccccc1", None, None),
    ("bicyclic_product", "product", "generic fused bicyclic tandem-addition product", None, None, None),
], conditions=[
    ("temperature", {"number": 90, "unit": "°C"}),
    ("time", {"number": 4, "unit": "h"}),
], notes=["Scheme 29 upper arrow is a generic transformation with variable X and Y; no row-specific yields are supplied."], add_missing=False))

R.append(record("p13_scheme29_tsi_nts_diallene", [13], "literature_example", [
    ("diallene", "reactant", "NTs-tethered diallene shown in Scheme 29", None, None, None),
    ("tsi", "reagent", "TsI", "Cc1ccc(S(=O)(=O)I)cc1", None, None),
    ("aibn", "unspecified_agent", "AIBN (cat.)", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ("toluene", "solvent", "toluene", "Cc1ccccc1", None, None),
    ("product_major", "product", "Scheme 29 fused bicyclic diastereomer, left", None, None, None),
    ("product_minor", "product", "Scheme 29 fused bicyclic diastereomer, right", None, None, None),
], conditions=[
    ("temperature", {"number": 90, "unit": "°C"}),
    ("time", {"number": 3, "unit": "h"}),
], outcomes=[
    ("reported_yield", {"number": 16, "unit": "%"}, ["product_major"]),
    ("reported_yield", {"number": 6, "unit": "%"}, ["product_minor"]),
], notes=["The two product-specific yields are printed beneath the two depicted diastereomers."],
    unresolved=["AIBN loading, yield measurement basis, and product absolute stereochemistry are not stated in the review."
]))

# Pages 13-14: sodium-naphthalenide examples and ketyl mechanisms.
R.append(record("p14_scheme30_naphthalenide_4eq", [13, 14], "literature_example", [
    ("substrate", "reactant", "dimethyl-substituted allene tethered methyl ketone shown in Scheme 30", None, None, None),
    ("sodium_naphthalenide", "reagent", "NaC10H7", None, [("equivalents", {"number": 4, "unit": "equiv"})], None),
    ("thf", "solvent", "THF", "C1CCOC1", None, None),
    ("cyclized_1", "product", "cyclopentanol product, left", None, None, None),
    ("cyclized_2", "product", "cyclopentenol product, right", None, None, None),
    ("uncyclized_allene", "product", "uncyclized allenyl alcohol", None, None, None),
    ("linear_alkene_1", "product", "linear alkenol product 1", None, None, None),
    ("linear_alkene_2", "product", "linear alkenol product 2", None, None, None),
], conditions=[
    ("temperature", "r.t."),
    ("time", {"number": 5, "unit": "h"}),
], outcomes=[
    ("overall_yield", {"number": 46, "unit": "%"}, ["cyclized_1", "cyclized_2", "uncyclized_allene", "linear_alkene_1", "linear_alkene_2"]),
    ("product_ratio", "cyclized_1:cyclized_2 = 67:30", ["cyclized_1", "cyclized_2"]),
], notes=["Scheme 30 first arrow; 67:30 is retained as a printed ratio and is not normalized to percentages."],
    unresolved=["The review does not assign the remaining mixture balance or state the yield/ratio measurement basis."]))


def scheme30_scope(code, r_value, overall_yield, ratio):
    return record(f"p14_scheme30_scope_{code}", [13, 14], "literature_example", [
        ("substrate", "reactant", f"Scheme 30 allene-ketone substrate; R = {r_value}", None, None, None),
        ("sodium_naphthalenide", "reagent", "NaC10H7", None, [("equivalents", {"number": 3, "unit": "equiv"})], None),
        ("thf", "solvent", "THF", "C1CCOC1", None, None),
        ("product1", "product", "Scheme 30 cyclopentanol product 1", None, None, None),
        ("product2", "product", "Scheme 30 cyclopentanol product 2", None, None, None),
        ("product3", "product", "Scheme 30 alternate cyclized/uncyclized product 3", None, None, None),
        ("product4", "product", "Scheme 30 uncyclized alcohol product 4", None, None, None),
    ], conditions=[], outcomes=[
        ("overall_yield", {"number": overall_yield, "unit": "%"}, ["product1", "product2", "product3", "product4"]),
        ("product_ratio", ratio, ["product1", "product2", "product3", "product4"]),
    ], notes=[f"Scheme 30 row for R = {r_value}; the four printed numbers are retained as a ratio."],
        unresolved=["Temperature, time, sodium-naphthalenide amount basis, product-ratio basis, and yield basis are not stated for this row."])


R.append(scheme30_scope("r_me", "CH3", 53, "75:10:1:6"))
R.append(scheme30_scope("r_h", "H", 59, "27:7:48:14"))

R.append(record("p14_scheme31_ketyl_cyclization_mechanism", [14], "mechanism", [
    ("carbonyl_allenes", "reactant", "three carbonyl/allene substrates shown in Scheme 31", None, None, None),
    ("sodium_naphthalenide", "reagent", "NaC10H7", None, None, None),
    ("ketyl_radicals", "unspecified_agent", "ketyl radical intermediates", None, None, None),
    ("cyclized_products", "product", "endo/exo cyclized alcohol products", None, None, None),
], notes=["Scheme 31 depicts three ketyl-radical cyclization pathways, including labelled endo and exo routes."], add_missing=False))

# Pages 14-15: SmI2 scope and the methoxyallene/hydrazone reaction.
R.append(record("p15_scheme32_smi2_short_tether", [14, 15], "literature_example", [
    ("substrate", "reactant", "short-tether methyl allenoate-aldehyde shown in Scheme 32", None, None, None),
    ("smi2", "reagent", "SmI2", None, [("equivalents", {"number": 2, "unit": "equiv"})], None),
    ("tert_butanol", "reagent", "t-BuOH", "CC(C)(C)O", [("equivalents", {"number": 2, "unit": "equiv"})], None),
    ("thf", "solvent", "THF", "C1CCOC1", None, None),
    ("product1", "product", "Scheme 32 cyclopentenol product 1", None, None, None),
    ("product2", "product", "Scheme 32 exomethylene cyclopentanol product 2", None, None, None),
], outcomes=[("diastereomer_ratio", "dr = 2:1", ["product2"])],
    notes=["The source places dr = 2:1 beneath the second depicted product."],
    unresolved=["Temperature, time, overall yield, ratio basis, and whether the dr applies only to product 2 are not further explained."]))

R.append(record("p15_scheme32_smi2_long_tether", [14, 15], "literature_example", [
    ("substrate", "reactant", "longer-tether methyl allenoate-aldehyde shown in Scheme 32", None, None, None),
    ("smi2", "reagent", "SmI2", None, [("equivalents", {"number": 2, "unit": "equiv"})], None),
    ("tert_butanol", "reagent", "t-BuOH", "CC(C)(C)O", [("equivalents", {"number": 2, "unit": "equiv"})], None),
    ("thf", "solvent", "THF", "C1CCOC1", None, None),
    ("diastereomer1", "product", "Scheme 32 fused product, major diastereomer", None, None, None),
    ("diastereomer2", "product", "Scheme 32 fused product, minor diastereomer", None, None, None),
], outcomes=[("diastereomer_ratio", "15:1", ["diastereomer1", "diastereomer2"])],
    notes=["The brace beneath the two products reports 15:1."],
    unresolved=["Temperature, time, overall yield, ratio basis, and absolute stereochemical assignments are not stated."]))


def scheme32_n_scope(n_value, ratio):
    return record(f"p15_scheme32_smi2_scope_n{n_value}", [14, 15], "literature_example", [
        ("substrate", "reactant", f"methyl allenoate-aldehyde scope substrate; n = {n_value}", None, None, None),
        ("smi2", "reagent", "SmI2", None, None, None),
        ("methanol", "solvent", "methanol", "CO", None, None),
        ("diastereomer1", "product", f"Scheme 32 cyclic alcohol, n = {n_value}, diastereomer 1", None, None, None),
        ("diastereomer2", "product", f"Scheme 32 cyclic alcohol, n = {n_value}, diastereomer 2", None, None, None),
    ], outcomes=[("diastereomer_ratio", ratio, ["diastereomer1", "diastereomer2"])],
        notes=[f"Scheme 32 scope row n = {n_value}."],
        unresolved=["SmI2 amount, temperature, time, overall yield, and ratio basis are not stated for this row."])


R.append(scheme32_n_scope(1, "6:1"))
R.append(scheme32_n_scope(2, "2:1"))


def eq10_scope(code, r_value, yld):
    return record(f"p15_eq10_hydrazone_{code}", [14, 15], "literature_example", [
        ("hydrazone", "reactant", f"chiral cyclic hydrazone shown in Eq. 10; R = {r_value}", None, None, None),
        ("lithiated_methoxyallene", "reagent", "lithiated methoxyallene", None, None, None),
        ("thf", "solvent", "THF", "C1CCOC1", None, None),
        ("product", "product", f"Eq. 10 cyclic hydrazine product; R = {r_value}", None, None, None),
    ], conditions=[
        ("temperature", {"number": -25, "unit": "°C"}),
        ("time", {"number": 16, "unit": "h"}),
    ], outcomes=[("reported_yield", {"number": yld, "unit": "%"}, ["product"])],
        notes=["Eq. 10 is described as proceeding through radical intermediate a."],
        unresolved=["Reagent amounts, atmosphere, workup, purification, yield basis, and stereochemical measurement are not stated."])


R.append(eq10_scope("r_ph", "Ph", 88))
R.append(eq10_scope("r_pme", "p-MeC6H4", 79))
R.append(eq10_scope("r_pome", "p-MeOC6H4", 75))


def eq11_scope(code, r1, r2):
    return record(f"p15_eq11_bu3snh_substrate_{code}", [15], "literature_example", [
        ("substrate", "reactant", f"R1R2C=C=CHCH2CH2I; R1 = {r1}, R2 = {r2}", None, None, None),
        ("tributyltin_hydride", "reagent", "Bu3SnH", None, [("equivalents", {"number": 1.4, "unit": "equiv"})], None),
        ("benzene", "solvent", "benzene", "c1ccccc1", None, None),
        ("reduction_product", "product", "reduced allene product", None, None, None),
        ("cyclopropane_product", "product", "alkenylcyclopropane product", None, None, None),
    ], conditions=[
        ("temperature", "reflux"),
        ("time", {"number": 3, "unit": "h"}),
    ], outcomes=[("product_ratio", "reduction:cyclopropane = 96:4", ["reduction_product", "cyclopropane_product"])],
        notes=["Eq. 11 states that reduction is the major pathway and cyclopropane formation is minor."],
        unresolved=["The review does not state separate overall yields or whether the same 96:4 ratio was measured independently for both substrate variants."])


R.append(eq11_scope("a", "n-C3H7", "H"))
R.append(eq11_scope("b", "CH3", "CH3"))

# Pages 15-16: Bu3SnH cyclization scope/mechanism and generic [2+2] additions.
R.append(record("p16_eq12_cyclization_general", [15, 16], "general_scheme", [
    ("substrate", "reactant", "iodo-tethered substituted allene; n = 2-4; Z = P(O)Ph2, SO2Ph, or SOPh", None, None, None),
    ("tributyltin_hydride", "reagent", "Bu3SnH", None, None, None),
    ("cyclobutane_product", "product", "substituted cyclobutane product shown in Eq. 12", None, None, None),
], outcomes=[
    ("reported_yield_range", {"minimum": 30, "maximum": 81, "unit": "%", "raw_text": "30%-81%"}, ["cyclobutane_product"]),
], notes=["Eq. 12 summarizes a range over multiple n/Z combinations; individual variant yields are not mapped."],
    unresolved=["Variant-specific yields, conditions beyond Bu3SnH, and yield measurement bases are not supplied."], add_missing=False))

R.append(record("p16_eq12_sulfone_specific", [15, 16], "literature_example", [
    ("substrate", "reactant", "SO2Ph-substituted iodo-tethered dimethylallene shown below Eq. 12", None, None, None),
    ("tributyltin_hydride", "reagent", "Bu3SnH", None, None, None),
    ("reduction_product", "product", "iodine-to-hydrogen reduction product", None, None, None),
    ("cyclopropane_product", "product", "phenylsulfonyl-substituted alkenylcyclopropane", None, None, None),
], notes=["The specific SO2Ph substrate gives both reduction and cyclopropane products."],
    unresolved=["Temperature, time, reagent amount, solvent, product ratio, yields, and measurement bases are not stated."]))

R.append(record("p16_scheme33_bu3snh_cyclization_mechanism", [15, 16], "mechanism", [
    ("iodo_tethered_allene", "reactant", "generic iodo-tethered allene; Z = H, P(O)Ph2, SOPh, or SO2Ph; n = 2, 4, 5, or 6", None, None, None),
    ("tributyltin_hydride", "reagent", "Bu3SnH", None, None, None),
    ("radical_intermediates", "unspecified_agent", "central/terminal attack radical intermediates", None, None, None),
    ("products", "product", "reduction, cyclopropane, cyclobutane, and rearranged products", None, None, None),
], notes=["Scheme 33 is a pathway map rationalizing how Z and tether length influence cyclization."], add_missing=False))

R.append(record("p16_scheme34_r_allene_dichlorodifluoroethylene", [16], "general_scheme", [
    ("allene", "reactant", "RCH=C=CH2; R = Cl, CN, MeO, PhS, or Ph", None, None, None),
    ("alkene", "reactant", "F2C=CCl2", "FC(F)=C(Cl)Cl", None, None),
    ("products", "product", "three cyclobutane regio-/stereoisomer classes shown in Scheme 34", None, None, None),
], conditions=[("temperature", {"number": 160, "unit": "°C"})],
    notes=["Scheme 34 upper arrow is a generic prior-work [2+2] cycloaddition; no variant-specific results are supplied."], add_missing=False))

R.append(record("p16_scheme34_tetramethylallene_fluoroalkene", [16], "general_scheme", [
    ("tetramethylallene", "reactant", "1,1,3,3-tetramethylallene", "CC(C)=C=C(C)C", None, None),
    ("fluoroalkene", "reactant", "F2C=CXY; X = F or Cl; Y = F or Cl", None, None, None),
    ("product1", "product", "Scheme 34 cyclobutane product class 1", None, None, None),
    ("product2", "product", "Scheme 34 cyclobutane product class 2", None, None, None),
], conditions=[
    ("temperature", {"minimum": 125, "maximum": 150, "unit": "°C", "raw_text": "125-150 °C"}),
], notes=["Scheme 34 lower arrow is a generic prior-work transformation over multiple X/Y combinations."], add_missing=False))

# Page 17: distinct Scheme 35 examples and the generic Scheme 36 mechanism.
R.append(record("p17_scheme35_fumarate", [17], "literature_example", [
    ("tetramethylallene", "reactant", "1,1,3,3-tetramethylallene", "CC(C)=C=C(C)C", None, None),
    ("fumarate", "reactant", "trans-1,2-bis(ethoxycarbonyl)ethylene shown in Scheme 35; E = CO2C2H5", None, None, None),
    ("product1", "product", "cyclobutane product 1", None, None, None),
    ("product2", "product", "cyclobutane product 2", None, None, None),
    ("product3", "product", "cyclohexene product 3", None, None, None),
], conditions=[
    ("temperature", {"number": 160, "unit": "°C"}),
    ("time", {"number": 5, "unit": "d"}),
], notes=["Scheme 35 first arrow; three products are depicted without numerical distribution."],
    unresolved=["Overall yield, product distribution, solvent, atmosphere, and measurement basis are not stated."]))

R.append(record("p17_scheme35_maleate", [17], "literature_example", [
    ("tetramethylallene", "reactant", "1,1,3,3-tetramethylallene", "CC(C)=C=C(C)C", None, None),
    ("maleate", "reactant", "cis-1,2-bis(ethoxycarbonyl)ethylene shown in Scheme 35; E = CO2C2H5", None, None, None),
    ("products", "product", "six cyclobutane/cyclohexene products shown in Scheme 35", None, None, None),
], conditions=[
    ("temperature", {"number": 160, "unit": "°C"}),
    ("time", {"number": 5, "unit": "d"}),
], notes=["Scheme 35 second arrow; six products are depicted without numerical distribution."],
    unresolved=["Overall yield, individual product distribution, solvent, atmosphere, and measurement basis are not stated."]))

R.append(record("p17_scheme35_23_pentadiene_acrylonitrile", [17], "literature_example", [
    ("allene", "reactant", "stereodefined 2,3-pentadiene shown in Scheme 35", "CC=C=CC", None, None),
    ("acrylonitrile", "reactant", "CH2=CHCN", "C=CC#N", None, None),
    ("products", "product", "four stereoisomeric cyanocyclobutanes shown in Scheme 35", None, None, None),
], conditions=[("temperature", {"number": 150, "unit": "°C"})],
    notes=["The four stereoisomers are depicted separately but no product percentages are printed."],
    unresolved=["Time, overall yield, product distribution, solvent, atmosphere, and measurement basis are not stated."]))

R.append(record("p17_scheme35_phenylallene_npmi", [17], "literature_example", [
    ("phenylallene", "reactant", "phenylallene", "C=C=Cc1ccccc1", None, None),
    ("npmi", "reactant", "N-phenylmaleimide (NPMI)", "O=C1C=CC(=O)N1c1ccccc1", None, None),
    ("products", "product", "multiple cyclobutane/fused or rearranged products shown in Scheme 35", None, None, None),
], conditions=[("temperature", {"number": 160, "unit": "°C"})],
    notes=["Scheme 35 depicts several products, including a lower rearranged aromatic imide product; no numerical distribution is supplied."],
    unresolved=["One product at the far right is partly clipped by the printed column boundary; time, overall yield, distribution, solvent, and measurement basis are not stated."]))

R.append(record("p17_scheme35_allene_acetylene", [17], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("acetylene", "reactant", "acetylene", "C#C", None, None),
    ("product", "product", "methylenecyclobutene shown in Scheme 35", "C=C1C=CC1", None, None),
], conditions=[
    ("temperature", {"number": 160, "unit": "°C"}),
    ("time", {"number": 5, "unit": "d"}),
], notes=["Scheme 35 final arrow."],
    unresolved=["Overall yield, solvent, atmosphere, and measurement basis are not stated."]))

R.append(record("p17_scheme36_biradical_cycloaddition_mechanism", [17], "mechanism", [
    ("substituted_allene", "reactant", "stereodefined R1/R2-substituted allene", None, None, None),
    ("alkene", "reactant", "CH2=CXY", None, None, None),
    ("biradicals", "unspecified_agent", "two diastereomeric biradical intermediates", None, None, None),
    ("products", "product", "four cyclobutane stereoisomers", None, None, None),
], notes=["Scheme 36 proposes the stepwise biradical mechanism; the illustrated example states R1 = R2 = Me, X = H, Y = CN."], add_missing=False))

# Page 18: sequential allene/tetrafluoroethylene additions, carbene chemistry, and ketene additions.
R.append(record("p18_scheme37_allene_tfe_primary", [18], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("tetrafluoroethylene", "reactant", "CF2=CF2", "FC(F)=C(F)F", None, None),
    ("product", "product", "1:1 fluorinated methylenecyclobutane product", None, None, None),
], outcomes=[("reported_yield", {"minimum": 30, "maximum": 38, "unit": "%", "raw_text": "30%-38%"}, ["product"])],
    notes=["Scheme 37 upper first arrow."],
    unresolved=["Temperature, time, pressure, solvent, and yield measurement basis are not stated."]))

R.append(record("p18_scheme37_primary_tfe_second", [18], "literature_example", [
    ("primary_product", "reactant", "Scheme 37 1:1 allene/tetrafluoroethylene adduct", None, None, None),
    ("tetrafluoroethylene", "reactant", "CF2=CF2", "FC(F)=C(F)F", None, None),
    ("product", "product", "1:2 spirocyclic fluorinated product", None, None, None),
], outcomes=[("reported_yield", {"minimum": 11, "maximum": 12, "unit": "%", "raw_text": "11%-12%"}, ["product"])],
    notes=["Scheme 37 upper second arrow is a further tetrafluoroethylene addition."],
    unresolved=["Temperature, time, pressure, solvent, and yield measurement basis are not stated."]))

R.append(record("p18_scheme37_allene_dimerization", [18], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("dimer", "product", "allene dimer with two exocyclic methylene groups", None, None, None),
], notes=["Scheme 37 downward arrow depicts allene self-dimerization before alkene addition."],
    unresolved=["No temperature, time, pressure, solvent, yield, or measurement basis is supplied for the dimerization stage."]))

R.append(record("p18_scheme37_dimer_tfe", [18], "literature_example", [
    ("allene_dimer", "reactant", "allene dimer shown in Scheme 37", None, None, None),
    ("tetrafluoroethylene", "reactant", "CF2=CF2", "FC(F)=C(F)F", None, None),
    ("product", "product", "2:1 fused-ring fluorinated product", None, None, None),
], outcomes=[("reported_yield", {"minimum": 2, "maximum": 18, "unit": "%", "raw_text": "2%-18%"}, ["product"])],
    notes=["Scheme 37 lower first horizontal arrow."],
    unresolved=["Temperature, time, pressure, solvent, and yield measurement basis are not stated."]))

R.append(record("p18_scheme37_fused_tfe_second", [18], "literature_example", [
    ("fused_product", "reactant", "Scheme 37 2:1 fused-ring product", None, None, None),
    ("tetrafluoroethylene", "reactant", "CF2=CF2", "FC(F)=C(F)F", None, None),
    ("product", "product", "2:2 fused-ring fluorinated product", None, None, None),
], outcomes=[("reported_yield", {"minimum": 0, "maximum": 0.5, "unit": "%", "raw_text": "0%-0.5%"}, ["product"])],
    notes=["Scheme 37 lower second horizontal arrow."],
    unresolved=["Temperature, time, pressure, solvent, and yield measurement basis are not stated."]))

R.append(record("p18_scheme38_dibromocarbene", [18], "literature_example", [
    ("dimethylallene", "reactant", "3-methyl-1,2-butadiene", "C=C=C(C)C", None, None),
    ("dibromocarbene", "reagent", ":CBr2", None, None, None),
    ("product", "product", "gem-dibromocyclopropane product shown in Scheme 38", None, None, None),
], notes=["Scheme 38 first carbene-addition arrow."],
    unresolved=["Carbene-generation method, reagent amounts, temperature, time, solvent, yield, and measurement basis are not stated."]))

R.append(record("p18_scheme38_perfluoroallene_carbene_general", [18], "general_scheme", [
    ("perfluoroallene", "reactant", "(F3C)2C=C=CF2", None, None, None),
    ("carbene", "reagent", ":CX2; X = F or Cl", None, None, None),
    ("product", "product", "fluorinated cyclopropane product shown in Scheme 38", None, None, None),
], notes=["Scheme 38 second arrow is generic over X = F or Cl."], add_missing=False))

R.append(record("p18_scheme38_arylcarbene_mechanism", [18], "mechanism", [
    ("dimethylallene", "reactant", "3-methyl-1,2-butadiene", "C=C=C(C)C", None, None),
    ("arylcarbene", "reagent", "ArCH carbene", None, None, None),
    ("direct_product", "product", "direct cyclopropane product", None, None, None),
    ("biradical", "unspecified_agent", "depicted biradical intermediate", None, None, None),
    ("rearranged_product", "product", "alternative cyclopropane product formed through the biradical", None, None, None),
], notes=["Scheme 38 contrasts a direct [2+1]-type product with a stepwise biradical route; the text notes mechanistic disagreement."], add_missing=False))

R.append(record("p18_scheme39_tetramethylallene_dimethylketene", [18], "literature_example", [
    ("tetramethylallene", "reactant", "1,1,3,3-tetramethylallene", "CC(C)=C=C(C)C", None, None),
    ("dimethylketene", "reactant", "dimethylketene", "CC(C)=C=O", None, None),
    ("product1", "product", "Scheme 39 cyclobutanone regioisomer 1", None, None, None),
    ("product2", "product", "Scheme 39 cyclobutanone regioisomer 2", None, None, None),
], conditions=[
    ("temperature", {"number": 120, "unit": "°C"}),
    ("time", {"number": 2, "unit": "h"}),
], outcomes=[("product_ratio", "71:29", ["product1", "product2"])],
    notes=["The printed 71:29 values are retained as a product ratio, not interpreted as isolated yields."],
    unresolved=["Overall yield, solvent, atmosphere, ratio measurement basis, and product-specific yields are not stated."]))

R.append(record("p18_scheme39_cyclohexylallene_dimethylketene", [18], "literature_example", [
    ("cyclohexylallene", "reactant", "cyclohexyl-substituted allene shown in Scheme 39", None, None, None),
    ("dimethylketene", "reactant", "dimethylketene", "CC(C)=C=O", None, None),
    ("product1", "product", "Scheme 39 cyclobutanone regioisomer 1", None, None, None),
    ("product2", "product", "Scheme 39 cyclobutanone regioisomer 2", None, None, None),
], conditions=[
    ("temperature", {"number": 120, "unit": "°C"}),
    ("time", {"number": 2, "unit": "h"}),
], outcomes=[("product_ratio", "51:49", ["product1", "product2"])],
    notes=["The printed 51:49 values are retained as a product ratio, not interpreted as isolated yields."],
    unresolved=["The allene substituent connectivity is retained by the drawing label; overall yield, solvent, atmosphere, ratio basis, and product-specific yields are not stated."]))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")


def ids(prefixes):
    return [item["record_id"] for item in R if any(item["source_reaction_id"].startswith(prefix) for prefix in prefixes)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 13,
            "state": "attempted",
            "regions": [
                {"region": "上半页 Scheme 28", "finding": "三条自由基串联路径（5-exo、4-exo、6-exo）为机理图；a、b、Z均为变量，分类为mechanism。", "evidence_ids": evid(13)},
                {"region": "中下部 Scheme 29 上箭头", "finding": "X/Y可变的AIBN/甲苯/90 °C/4 h串联环化通式，分类为general_scheme。", "evidence_ids": evid(13)},
                {"region": "中下部 Scheme 29 下箭头", "finding": "NTs联烯底物与TsI的具体引用实例，保存90 °C、3 h及两个产物专属收率16%和6%。", "evidence_ids": evid(13)},
                {"region": "页底2.2节引言", "finding": "说明溶解金属还原生成自由基并引向第14页Scheme 30；与跨页的三条Scheme 30记录合并证据。", "evidence_ids": evid(13) + evid(14)},
            ],
            "record_ids": ids(["p13_", "p14_scheme30_"]),
            "unresolved": ["Scheme 28为变量机理，不能唯一结构化；Scheme 29未给AIBN用量或收率测定基础；Scheme 30正文仅提供跨页背景。"],
        },
        {
            "page": 14,
            "state": "attempted",
            "regions": [
                {"region": "上半页 Scheme 30 第一箭头", "finding": "NaC10H7（4 equiv）/THF/r.t./5 h反应，记录46%总收率、两环化产物67:30及三种未环化产物。", "evidence_ids": evid(14) + evid(13)},
                {"region": "上半页 Scheme 30 R=CH3与R=H两行", "finding": "按R值拆为两条引用实例，分别保存53%与59%总收率以及75:10:1:6和27:7:48:14原始产品比。", "evidence_ids": evid(14) + evid(13)},
                {"region": "下半页 Scheme 31", "finding": "三条ketyl自由基endo/exo环化路径为机理汇总，分类为mechanism。", "evidence_ids": evid(14)},
                {"region": "下方正文至第15页Scheme 32与Eq. 10", "finding": "说明SmI2相似反应及甲氧基联烯锂/腙反应的自由基中间体；与第15页对应记录合并。", "evidence_ids": evid(14) + evid(15)},
            ],
            "record_ids": ids(["p14_", "p15_scheme32_", "p15_eq10_"]),
            "unresolved": ["Scheme 30两行比例和总收率的测定基础未说明，比例总和不强制归一；Scheme 31无独立实验条件；跨页实例缺完整原始操作。"],
        },
        {
            "page": 15,
            "state": "attempted",
            "regions": [
                {"region": "上半页 Scheme 32", "finding": "逐箭头/逐n值建立四条SmI2引用实例，保存2 equiv SmI2、2 equiv t-BuOH、THF、甲醇以及2:1、15:1、6:1、2:1选择性。", "evidence_ids": evid(15) + evid(14)},
                {"region": "中部 Eq. 10", "finding": "R=Ph、p-MeC6H4、p-MeOC6H4三行分别记录；共同条件THF、-25 °C、16 h，产率88%、79%、75%。", "evidence_ids": evid(15) + evid(14)},
                {"region": "页底 Eq. 11", "finding": "a、b两个不同R1/R2底物拆分记录；共同条件Bu3SnH 1.4 equiv、苯、回流3 h，保留还原/环丙烷96:4。", "evidence_ids": evid(15)},
                {"region": "右下正文至第16页Eq. 12/Scheme 33", "finding": "P(O)Ph2、SOPh、SO2Ph促进中心碳环化的跨页说明，与第16页通式、实例和机理合并。", "evidence_ids": evid(15) + evid(16)},
            ],
            "record_ids": ids(["p15_", "p16_eq12_", "p16_scheme33_"]),
            "unresolved": ["Scheme 32未给总收率/时间/温度；Eq. 10缺用量和收率基础；Eq. 11未说明96:4是否对a、b分别测得。"],
        },
        {
            "page": 16,
            "state": "attempted",
            "regions": [
                {"region": "页首 Eq. 12与具体SO2Ph实例", "finding": "通式保留n=2-4、Z三类和30%-81%未映射范围；具体SO2Ph箭头另记为一条有还原/环丙烷双产物的引用实例。", "evidence_ids": evid(16) + evid(15)},
                {"region": "上中部 Scheme 33", "finding": "Bu3SnH自由基对不同Z/n底物的中心/末端进攻与环化网络，分类为mechanism。", "evidence_ids": evid(16) + evid(15)},
                {"region": "下半页 Scheme 34 上箭头", "finding": "R可变联烯与F2C=CCl2在160 °C的[2+2]通式，分类为general_scheme。", "evidence_ids": evid(16)},
                {"region": "下半页 Scheme 34 下箭头", "finding": "四甲基联烯与F2C=CXY在125-150 °C的通式，保留温度范围与X/Y变量。", "evidence_ids": evid(16)},
            ],
            "record_ids": ids(["p16_"]),
            "unresolved": ["Eq. 12的30%-81%不能映射至具体n/Z组合；SO2Ph实例无条件或比例；Scheme 34无逐变体产率、时间和分析基础。"],
        },
        {
            "page": 17,
            "state": "attempted",
            "regions": [
                {"region": "上部 Scheme 35两条E=CO2C2H5箭头", "finding": "顺/反二羧酸酯烯烃与四甲基联烯的160 °C、5 d反应分别记录，产品集合不合并。", "evidence_ids": evid(17)},
                {"region": "中部 Scheme 35丙烯腈与NPMI箭头", "finding": "2,3-戊二烯/丙烯腈（150 °C）及苯基联烯/NPMI（160 °C）作为两条不同引用实例；保留各自产物集合。", "evidence_ids": evid(17)},
                {"region": "中下部 Scheme 35乙炔箭头", "finding": "丙二烯与乙炔在160 °C、5 d生成亚甲基环丁烯，单独记录。", "evidence_ids": evid(17)},
                {"region": "下部 Scheme 36", "finding": "以丙烯腈为例的双自由基[2+2]立体化学路径，分类为mechanism。", "evidence_ids": evid(17)},
            ],
            "record_ids": ids(["p17_"]),
            "unresolved": ["Scheme 35各箭头均未给总收率或产品分布；NPMI箭头最右产物受印刷栏边裁切，不能完整唯一识别。"],
        },
        {
            "page": 18,
            "state": "attempted",
            "regions": [
                {"region": "上部 Scheme 37", "finding": "按连续箭头拆为五条阶段记录：1:1、进一步1:2、丙二烯自聚、2:1及2:2产物；保留30%-38%、11%-12%、2%-18%、0%-0.5%范围。", "evidence_ids": evid(18)},
                {"region": "中部 Scheme 38前两箭头", "finding": "二溴卡宾具体实例与X=F/Cl的全氟联烯通式分开记录。", "evidence_ids": evid(18)},
                {"region": "中部 Scheme 38芳基卡宾路径", "finding": "直接[2+1]与双自由基分步路径存在机理分歧，分类为mechanism而非实验。", "evidence_ids": evid(18)},
                {"region": "下部 Scheme 39两行", "finding": "四甲基联烯和环己基取代联烯与二甲基乙烯酮的120 °C、2 h反应分别记录，产品比分别71:29和51:49。", "evidence_ids": evid(18)},
            ],
            "record_ids": ids(["p18_"]),
            "unresolved": ["Scheme 37未给反应条件和收率测定基础；Scheme 38未给卡宾生成条件或收率；Scheme 39比例不是总收率且分析基础未知。"],
        },
    ],
}

COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    prefix = f"{DOC}:page"
    task_id = task.get("task_id", "")
    if not task_id.startswith(prefix) or not task_id.endswith(":text"):
        continue
    page = int(task_id[len(prefix):].split(":", 1)[0])
    if 13 <= page <= 18:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; findings and unresolved issues are recorded in coverage/pages_0013_0018.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(R), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
