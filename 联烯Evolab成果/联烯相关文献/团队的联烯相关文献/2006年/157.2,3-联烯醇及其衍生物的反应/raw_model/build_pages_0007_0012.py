#!/usr/bin/env python3
"""Build evidence-linked machine records for review-PDF pages 7--12."""

import json
from pathlib import Path


DOC = "doc_27796c91f0b5e453"
OUT = Path(__file__).with_name("pages_0007_0012_records.json")
E = {p: [f"{DOC}:page{p}:text", f"{DOC}:page{p}:image"] for p in range(7, 13)}


def ev(*pages):
    return list(dict.fromkeys(x for p in pages for x in E[p]))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


SMILES = {
    "DMDO": "CC1(C)OO1",
    "trimethylamine N-oxide": "C[N+](C)(C)[O-]",
    "dichloromethane": "ClCCl",
    "phenylacetylene": "C#Cc1ccccc1",
    "triethylphosphine": "CCP(CC)CC",
    "THF": "C1CCOC1",
    "diethyl ether": "CCOCC",
    "diiodomethane": "ICI",
    "water": "O",
    "HMPA": "CN(C)P(=O)(N(C)C)N(C)C",
    "TFA": "O=C(O)C(F)(F)F",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    "silver(I) oxide": "[Ag]O[Ag]",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "phenylselenyl chloride": "Cl[Se]c1ccccc1",
    "phenylsulfenyl chloride": "ClSc1ccccc1",
    "bromine": "BrBr",
    "iodine": "II",
    "NBS": "O=C1CCC(=O)N1Br",
    "triphenylphosphine": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "DEAD": "CCOC(=O)N=NC(=O)OCC",
    "benzoic acid": "O=C(O)c1ccccc1",
    "sodium hydroxide": "[Na+].[OH-]",
    "acetic anhydride": "CC(=O)OC(C)=O",
    "pyridine": "n1ccccc1",
    "trichloroacetonitrile": "N#CC(Cl)(Cl)Cl",
    "p-toluenesulfonyl isocyanate": "O=C=NS(=O)(=O)c1ccc(C)cc1",
    "NIS": "O=C1CCC(=O)N1I",
    "triethyl phosphite": "CCOP(OCC)OCC",
    "acetonitrile": "CC#N",
    "sodium fluoride": "[Na+].[F-]",
    "benzylhydroxylamine": "N(O)Cc1ccccc1",
    "triphenyltin hydride": "[SnH](c1ccccc1)(c1ccccc1)c1ccccc1",
    "AIBN": "CC(C)(C#N)N=NC(C)(C)C#N",
    "dimethyl malonate": "COC(=O)CC(=O)OC",
    "ethyl acetoacetate": "CCOC(=O)CC(C)=O",
}


def part(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    if smiles is None:
        smiles = SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence, participants, conditions, outcomes,
           notes=(), unresolved=(), steps=None):
    if steps is None:
        steps = [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []


def add(*args, **kwargs):
    records.append(record(*args, **kwargs))


MISSING_COMMON = [
    "The review does not report reaction scale, workup, purification, or yield measurement basis for this cited example.",
    "Depicted complex structures and stereochemistry require chemical review.",
]


# Page 7: oxidative cyclization, Pauson-Khand, terminal-alkyne coupling, copper addition, and Sm cyclopropanation.
e = E[7]
add(
    "p7_scheme17_dmdo_oxidative_cyclization", "Scheme 17", "literature_example", e,
    [part("compound34", "reactant", "2,3-allenol 34", e),
     part("dmdo", "reagent", "DMDO", e, name="DMDO"),
     part("product", "product", "oxidative cyclization product from 34", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", q(55, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    notes=["A bis-epoxide-like bracketed species is depicted between 34 and the product."],
    unresolved=MISSING_COMMON + ["DMDO amount and solvent are not reported."])

for r_value, yield_value in [("H", 40), ("Ac", 42)]:
    add(
        f"p7_scheme18_r_{r_value.lower()}", f"Scheme 18, R = {r_value}", "literature_example", e,
        [part("compound35", "reactant", f"terminal-alkynyl 2,3-allenol 35 (R = {r_value})", e),
         part("co2co8", "reagent", "[Co2(CO)8]", e),
         part("me3no", "reagent", "Me3NO", e, name="trimethylamine N-oxide"),
         part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"),
         part("compound36", "product", f"Pauson-Khand cyclopentenone 36 (R = {r_value})", e)],
        [fld("temperature", "r.t.", e), fld("time", None, e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["compound36"]), fld("yield_measurement_basis", None, e, ["compound36"])],
        unresolved=MISSING_COMMON + ["Reagent quantities and reaction time are not reported."])

for metal, catalyst, cat_loading, ligand, lig_loading, product_id, yield_value in [
    ("Rh", "HRh(CO)(PPh3)3", 5, "PEt3", 35, "37", 81),
    ("Ru", "RuH2(PPh3)4", 15, "ferrocenyl-diphosphane", 40, "38", 61),
]:
    ps = [
        part("compound11", "reactant", "2,3-allenol 11", e),
        part("phenylacetylene", "reactant", "phenylacetylene", e, name="phenylacetylene"),
        part("catalyst", "catalyst", catalyst, e, amounts=[fld("catalyst_loading", q(cat_loading, "mol%"), e)]),
        part("ligand", "reagent", ligand, e, name="triethylphosphine" if ligand == "PEt3" else None,
             amounts=[fld("reported_loading", q(lig_loading, "mol%"), e)]),
        part("thf", "solvent", "THF", e, name="THF"),
        part("product", "product", f"{metal}-selective coupling product {product_id}", e),
    ]
    add(
        f"p7_scheme19_{metal.lower()}_coupling", f"Scheme 19, {metal} branch", "literature_example", e,
        ps, [fld("temperature", "reflux", e), fld("time", None, e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
        notes=["The Rh and Ru catalysts give different regioisomeric coupling products."],
        unresolved=MISSING_COMMON + ["Reactant quantities and reaction time are not reported."])

for metal, product_id, intermediates in [
    ("Rh", "37", "Rh intermediates 39 and 40"),
    ("Ru", "38", "Ru intermediates 41 and 42"),
]:
    add(
        f"p7_scheme20_{metal.lower()}_cycle", f"Scheme 20, {metal} cycle", "mechanism", e,
        [part("compound11", "reactant", "2,3-allenol 11", e),
         part("phenylacetylene", "reactant", "phenylacetylene", e, name="phenylacetylene"),
         part("metal_hydride", "catalyst", f"[{metal}]-H", e),
         part("product", "product", f"coupling product {product_id}", e)],
        [], [], notes=[f"Proposed hydrometallation/oxidative-addition/reductive-elimination cycle through {intermediates}."],
        unresolved=["This is a proposed mechanism, not a separately isolated experiment."])

add(
    "p7_scheme21_me2culi_addition_lactonization", "Scheme 21", "general_scheme", e,
    [part("compound43", "reactant", "generic 2,3-allenol ester 43", e),
     part("me2culi", "reagent", "Me2CuLi", e),
     part("ether", "solvent", "Et2O", e, name="diethyl ether"),
     part("water", "reagent", "H2O", e, name="water"),
     part("compound44", "product", "generic delta-lactone 44", e)],
    [fld("temperature", rng(-78, -40, "°C", "-78 to -40 °C"), e), fld("time", None, e)],
    [fld("reported_yield", None, e, ["compound44"])],
    notes=["The drawing shows conjugate addition followed by aqueous protonation and lactonization."],
    unresolved=["Generic R groups prevent a complete structure assignment.", "Reagent amounts, time, and yield are not reported."])

add(
    "p7_eq12_sm_cyclopropanation_scope", "Eq. 12", "general_scheme", e,
    [part("allenol", "reactant", "generic 2,3-allenol", e),
     part("sm", "reagent", "Sm", e),
     part("ch2i2", "reagent", "CH2I2", e, name="diiodomethane"),
     part("thf", "solvent", "THF", e, name="THF"),
     part("major", "product", "major regioisomeric cyclopropane", e),
     part("minor", "product", "minor regioisomeric cyclopropane", e)],
    [fld("initial_temperature", q(-78, "°C"), e), fld("warm_to", "r.t.", e), fld("time", None, e)],
    [fld("reported_combined_yield", rng(30, 73, "%", "30%-73%"), e, ["major", "minor"]),
     fld("yield_measurement_basis", None, e, ["major", "minor"])],
    notes=["The left cyclopropane is labelled major and the right is labelled minor."],
    unresolved=["Generic R groups and the product ratio are not specified.", "Reagent quantities, time, workup, purification, and yield basis are not reported."])


# Pages 7--8: specific Sm example and page-8 ring-expansion chemistry.
e78 = ev(7, 8)
add(
    "p8_eq13_compound45", "Eq. 13", "literature_example", e78,
    [part("compound45", "reactant", "2,3-allenol 45", e78, amounts=[fld("starting_material_ee", q(85, "%"), e78)]),
     part("sm", "reagent", "Sm", e78),
     part("ch2i2", "reagent", "CH2I2", e78, name="diiodomethane"),
     part("thf", "solvent", "THF", e78, name="THF"),
     part("compound46", "product", "cyclopropane 46", e78)],
    [fld("initial_temperature", q(-78, "°C"), e78), fld("warm_to", "r.t.", e78), fld("time", None, e78)],
    [fld("reported_yield", q(64, "%"), e78, ["compound46"]), fld("product_ee", q(84, "%"), e78, ["compound46"]),
     fld("yield_measurement_basis", None, e78, ["compound46"])],
    unresolved=MISSING_COMMON + ["Reagent quantities and reaction time are not reported."])

e = E[8]
add(
    "p8_scheme22_ring_expansion_overview", "Scheme 22", "mechanism", e,
    [part("allenol", "reactant", "generic cyclic 2,3-allenol", e),
     part("products", "product", "generic ring-expanded products", e)],
    [], [],
    notes=["Conceptual overview of Pd/ArI carbopalladation, Pd-hydride, strong-base, and strong-acid ring-expansion pathways."],
    unresolved=["This is a four-pathway conceptual scheme, not a separately reported experiment; generic ring and R groups remain unspecified."])

for compound, mode in [("47", "intermolecular Pd(0)/ArI ring expansion"), ("48", "intramolecular Pd(0) ring expansion")]:
    participants = [part("substrate", "reactant", f"2,3-allenol {compound}", e), part("pd0", "catalyst", "Pd(0)", e), part("product", "product", f"ring-expanded product from {compound}", e)]
    if compound == "47":
        participants.insert(1, part("ari", "reactant", "generic aryl iodide ArI", e))
    add(
        f"p8_scheme23_compound{compound}", f"Scheme 23, compound {compound}", "literature_example", e,
        participants, [fld("time", None, e), fld("temperature", None, e)],
        [fld("reported_yield", None, e, ["product"])], notes=[mode],
        unresolved=["Catalyst identity/loading, time, temperature, solvent, and yield are not reported.", "Generic substituents prevent full structure assignment."])

add(
    "p8_eq14_compound49_scope", "Eq. 14", "general_scheme", e,
    [part("compound49", "reactant", "generic substituted 2,3-allenol 49", e),
     part("ari", "reactant", "ArI", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[fld("catalyst_loading", q(5, "mol%"), e)]),
     part("ag2co3", "reagent", "Ag2CO3", e),
     part("toluene", "solvent", "toluene", e, name="toluene"),
     part("major", "product", "major ring-expanded isomer", e),
     part("minor", "product", "minor ring-expanded isomer", e)],
    [fld("temperature", q(80, "°C"), e), fld("time", None, e)],
    [fld("reported_combined_yield", rng(20, 89, "%", "20%-89%"), e, ["major", "minor"]), fld("yield_measurement_basis", None, e, ["major", "minor"])],
    unresolved=["Generic substituents and major/minor ratios are not reported.", "Reagent quantities, time, workup, purification, and yield basis are not reported."])

add(
    "p8_scheme24_compound50_scope", "Scheme 24, compound 50", "general_scheme", e,
    [part("compound50", "reactant", "generic 2,3-allenol 50", e),
     part("ari", "reactant", "ArI", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[fld("catalyst_loading", q(5, "mol%"), e)]),
     part("k2co3", "reagent", "K2CO3", e, name="potassium carbonate"),
     part("thf", "solvent", "THF", e, name="THF"),
     part("product", "product", "ring-expanded product from 50", e)],
    [fld("temperature", "reflux", e), fld("time", None, e)],
    [fld("reported_yield", rng(38, 92, "%", "38%-92%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=["Generic R groups and ArI identity are not specified.", "Reagent quantities, time, workup, purification, and yield basis are not reported."])

for r_value, hours, yield_value in [("Me", 16, 72), ("OMe", 19, 37)]:
    add(
        f"p8_scheme24_compound51_r_{r_value.lower()}", f"Scheme 24, compound 51, R = {r_value}", "literature_example", e,
        [part("compound51", "reactant", f"intramolecular aryl-iodide 2,3-allenol 51 (R = {r_value})", e),
         part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[fld("catalyst_loading", q(5, "mol%"), e)]),
         part("k2co3", "reagent", "K2CO3", e, name="potassium carbonate"),
         part("thf", "solvent", "THF", e, name="THF"),
         part("product", "product", f"fused ring-expanded product (R = {r_value})", e)],
        [fld("temperature", "reflux", e), fld("time", q(hours, "h"), e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
        unresolved=MISSING_COMMON + ["Reactant/base quantities are not reported."])

add(
    "p8_scheme25_palladium_hydride_scope", "Scheme 25", "general_scheme", e,
    [part("compound52", "reactant", "generic 2,3-allenol 52", e),
     part("pd", "catalyst", "Pd(PPh3)4", e),
     part("ligand", "reagent", "P(o-tolyl)3", e),
     part("thf", "solvent", "THF", e, name="THF"),
     part("product", "product", "generic Pd-hydride ring-expanded product", e)],
    [fld("temperature", "reflux", e), fld("time", None, e)],
    [fld("reported_yield", rng(71, 98, "%", "71%-98%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    notes=["The depicted scope defines X = O or R2 and Y = NR1, O, or CR2."],
    unresolved=["Catalyst/ligand amounts, time, scale, workup, purification, and yield basis are not reported.", "Generic X/Y/R groups prevent full structure assignment."])


# Page 9: base/acid/thermal ring expansion and electrophile chemistry.
e = E[9]
for code, r_value, base_label, hours, yield_value in [
    ("a", "Et", "n-BuLi", 4.5, 73),
    ("b", "n-Pr", "n-BuLi", 3.5, 67),
    ("c", "i-Pr", "n-BuLi", 0.5, 73),
    ("d", "Bn", "(TMS)2NNa", 0.5, 80),
]:
    add(
        f"p9_eq15_{code}", f"Eq. 15, {code}", "literature_example", ev(8, 9),
        [part("compound53", "reactant", f"2,3-allenol 53 (R = {r_value})", ev(8, 9)),
         part("base", "reagent", base_label, ev(8, 9), amounts=[fld("equivalents", q(1.2, "equiv"), ev(8, 9))]),
         part("thf", "solvent", "THF", ev(8, 9), name="THF"),
         part("hcl", "reagent", "10% HCl", ev(8, 9), amounts=[fld("reported_HCl_percentage", q(10, "%"), ev(8, 9))]),
         part("product", "product", f"ring-expanded product from 53 (R = {r_value})", ev(8, 9))],
        [fld("initial_temperature", q(0, "°C"), ev(8, 9)), fld("warm_to", "r.t.", ev(8, 9)), fld("final_temperature", "reflux", ev(8, 9)), fld("time", q(hours, "h"), ev(8, 9))],
        [fld("reported_yield", q(yield_value, "%"), ev(8, 9), ["product"]), fld("yield_measurement_basis", None, ev(8, 9), ["product"])],
        unresolved=MISSING_COMMON + ["The basis of the printed 10% HCl is not specified."])

for code, r_value, hours, yield_value in [
    ("a", "Me", 5, 73), ("b", "Et", 6, 80), ("c", "n-Pr", 6, 76), ("d", "Bn", 4, 85)
]:
    add(
        f"p9_eq16_{code}", f"Eq. 16, {code}", "literature_example", e,
        [part("compound54", "reactant", f"2,3-allenol 54 (R = {r_value})", e),
         part("base", "reagent", "(TMS)2NLi", e, amounts=[fld("equivalents", q(1.2, "equiv"), e)]),
         part("hmpa", "reagent", "HMPA", e, name="HMPA", amounts=[fld("equivalents", q(1.2, "equiv"), e)]),
         part("thf", "solvent", "THF", e, name="THF"),
         part("water", "reagent", "H2O", e, name="water"),
         part("product", "product", f"ring-expanded product from 54 (R = {r_value})", e)],
        [fld("temperature", "reflux", e), fld("time", q(hours, "h"), e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
        notes=["Water is shown as a second-step quench/reagent."],
        unresolved=MISSING_COMMON + ["Reaction scale and water amount are not reported."])

add(
    "p9_scheme26_tfa_ring_expansion", "Scheme 26 transformation", "general_scheme", e,
    [part("compound55", "reactant", "generic 2,3-allenol 55", e),
     part("tfa", "reagent", "TFA", e, name="TFA"),
     part("thf", "solvent", "THF", e, name="THF"),
     part("water", "solvent", "H2O", e, name="water"),
     part("compound57", "product", "generic ring-expanded product 57", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", rng(40, 92, "%", "40%-92%"), e, ["compound57"]), fld("yield_measurement_basis", None, e, ["compound57"])],
    unresolved=["Generic R groups, TFA/solvent amounts, time, temperature, workup, purification, and yield basis are not reported."])

add(
    "p9_scheme26_ketone_rearrangement", "Scheme 26 mechanism", "mechanism", e,
    [part("compound55", "reactant", "generic 2,3-allenol 55", e),
     part("compound56", "unspecified_agent", "proposed ketone intermediate 56", e),
     part("compound57", "product", "ring-expanded product 57", e)],
    [], [], notes=["The review proposes acid-promoted ketone formation followed by rearrangement."],
    unresolved=["Intermediate 56 is mechanistic and is not reported as an isolated compound here."])

# Scheme 27 is a three-arrow sequence; retain each stage separately.
add(
    "p9_scheme27_thermal_ring_expansion", "Scheme 27, thermal stage", "literature_example", e,
    [part("compound58", "reactant", "2,3-allenol 58", e), part("toluene", "solvent", "toluene", e, name="toluene"),
     part("hydroquinone", "product", "ring-expanded/aromatized hydroquinone intermediate", e)],
    [fld("temperature", q(110, "°C"), e), fld("time", None, e)], [fld("reported_yield", None, e, ["hydroquinone"])],
    unresolved=["Time and yield for this stage are not reported.", "The intermediate has no compound number and its structure remains unverified."])
add(
    "p9_scheme27_ag2o_oxidation", "Scheme 27, Ag2O oxidation", "literature_example", e,
    [part("hydroquinone", "reactant", "ring-expanded hydroquinone intermediate", e),
     part("ag2o", "reagent", "Ag2O", e, name="silver(I) oxide"),
     part("k2co3", "reagent", "K2CO3", e, name="potassium carbonate"),
     part("benzene", "solvent", "C6H6", e, name="benzene"),
     part("quinone", "product", "oxidized quinone intermediate", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["quinone"])],
    unresolved=["Reagent amounts, time, temperature, and yield are not reported.", "The intermediate has no compound number and its structure remains unverified."])
add(
    "p9_scheme27_tfa_cyclization", "Scheme 27, TFA stage", "literature_example", e,
    [part("quinone", "reactant", "oxidized quinone intermediate", e), part("tfa", "reagent", "TFA", e, name="TFA"),
     part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"), part("product", "product", "benzofuran product from 58", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["product"])],
    unresolved=["TFA amount, time, temperature, and yield are not reported.", "The final product is not numbered and its structure remains unverified."])

add(
    "p9_scheme28_compound59_scope", "Scheme 28, compound 59", "general_scheme", e,
    [part("compound59", "reactant", "generic terminally substituted 2,3-allenol 59", e),
     part("electrophile", "reagent", "PhSeCl or PhSCl", e),
     part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"),
     part("compound60", "product", "generic 3-substituted 2,5-dihydrofuran 60", e)],
    [fld("temperature", "r.t.", e), fld("time", None, e)],
    [fld("reported_yield", rng(70, 100, "%", "70%-100%"), e, ["compound60"]), fld("yield_measurement_basis", None, e, ["compound60"])],
    unresolved=["The collective range is not assigned to individual electrophiles or substrates.", "Generic R groups, reagent amounts, time, workup, purification, and yield basis are not reported."])

for code, electrophile, yield_value in [("br", "Br2", 93), ("phs", "PhSCl", 72)]:
    name = "bromine" if code == "br" else "phenylsulfenyl chloride"
    add(
        f"p9_scheme28_compound61_{code}", f"Scheme 28, compound 61, {electrophile}", "literature_example", e,
        [part("compound61", "reactant", "2,3-allenol 61", e), part("electrophile", "reagent", electrophile, e, name=name),
         part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"), part("compound62", "product", f"dihydrofuran 62 (E = {'Br' if code == 'br' else 'PhS'})", e)],
        [fld("temperature", "r.t.", e), fld("time", None, e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["compound62"]), fld("yield_measurement_basis", None, e, ["compound62"])],
        unresolved=MISSING_COMMON + ["Electrophile amount and reaction time are not reported."])

add(
    "p9_scheme28_compound61_i2_mixture", "Scheme 28, compound 61, I2", "literature_example", e,
    [part("compound61", "reactant", "2,3-allenol 61", e), part("iodine", "reagent", "I2", e, name="iodine"),
     part("base", "reagent", "unspecified base", e), part("polar_solvent", "solvent", "unspecified polar solvent", e),
     part("compound63", "product", "iododihydrofuran 63", e), part("compound64", "product", "dihydrofuran byproduct 64", e)],
    [fld("temperature", "r.t.", e), fld("time", None, e)],
    [fld("reported_combined_yield", rng(40, 60, "%", "40%-60%"), e, ["compound63", "compound64"]), fld("yield_measurement_basis", None, e, ["compound63", "compound64"])],
    notes=["Changing iodine amount or base did not suppress formation of 64."],
    unresolved=["Iodine/base amounts, base identity, solvent identity, time, product ratio, workup, purification, and yield basis are not reported."])

add(
    "p9_scheme29_65_to_66_mitsunobu", "Scheme 29, 65 to 66", "literature_example", e,
    [part("compound65", "reactant", "optically active 2,3-allenol 65", e),
     part("pph3", "reagent", "Ph3P", e, name="triphenylphosphine"), part("dead", "reagent", "DEAD", e, name="DEAD"),
     part("benzoic_acid", "reagent", "PhCO2H", e, name="benzoic acid"), part("compound66", "product", "optically active 2,3-allenol 66", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", q(90, "%"), e, ["compound66"]), fld("yield_measurement_basis", None, e, ["compound66"])],
    unresolved=MISSING_COMMON + ["Reagent quantities, solvent, time, and temperature are not reported."])

for substrate, product, nbs_yield, pse_yield in [("65", "67", 66, 66), ("66", "68", 64, 62)]:
    add(
        f"p9_scheme29_{substrate}_nbs", f"Scheme 29, {substrate} + NBS", "literature_example", e,
        [part("substrate", "reactant", f"optically active 2,3-allenol {substrate}", e), part("nbs", "reagent", "NBS", e, name="NBS"),
         part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"), part("product", "product", f"bromodihydrofuran {product}", e)],
        [fld("temperature", "r.t.", e), fld("time", None, e)],
        [fld("reported_yield", q(nbs_yield, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
        unresolved=MISSING_COMMON + ["NBS amount and reaction time are not reported."])
    add(
        f"p9_scheme29_{substrate}_phsecl", f"Scheme 29, {substrate} + PhSeCl", "literature_example", e,
        [part("substrate", "reactant", f"optically active 2,3-allenol {substrate}", e), part("phsecl", "reagent", "PhSeCl", e, name="phenylselenyl chloride"),
         part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"), part("product", "product", f"phenylseleno-dihydrofuran {product}", e),
         part("byproduct", "product", f"chlorohydrin byproduct from {substrate}", e)],
        [fld("temperature", "r.t.", e), fld("time", None, e)],
        [fld("reported_yield", q(pse_yield, "%"), e, ["product"]), fld("reported_byproduct_yield", q(17, "%"), e, ["byproduct"]),
         fld("yield_measurement_basis", None, e, ["product", "byproduct"])],
        unresolved=MISSING_COMMON + ["PhSeCl amount and reaction time are not reported."])


# Page 10: electrophile-induced additions/rearrangements and Nazarov chemistry.
e = E[10]
add(
    "p10_scheme30_iodination_of_69", "Scheme 30, iodination stage", "literature_example", e,
    [part("compound69", "reactant", "generic secondary 2,3-allenol 69", e), part("iodine", "reagent", "I2", e, name="iodine"),
     part("ether", "solvent", "Et2O", e, name="diethyl ether"), part("iodo_intermediate", "product", "iodinated allylic alcohol intermediate", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["iodo_intermediate"])],
    unresolved=["Generic R group, iodine amount, time, temperature, and intermediate yield are not reported."])
add(
    "p10_scheme30_base_epoxidation", "Scheme 30, base-treatment stage", "general_scheme", e,
    [part("iodo_intermediate", "reactant", "iodinated allylic alcohol intermediate from 69", e),
     part("base", "reagent", "(TMS)2NNa", e), part("trans70", "product", "trans iodo-vinylic epoxide 70", e),
     part("cis70", "product", "cis iodo-vinylic epoxide 70", e)],
    [fld("temperature", rng(0, 20, "°C", "0-20 °C"), e), fld("time", None, e)],
    [fld("reported_combined_yield", rng(65, 93, "%", "65%-93%"), e, ["trans70", "cis70"]),
     fld("relative_amount_trans70", "major", e, ["trans70"]), fld("relative_amount_cis70", "minor", e, ["cis70"]),
     fld("yield_measurement_basis", None, e, ["trans70", "cis70"])],
    unresolved=["Generic R group, base amount, time, product ratio, workup, purification, and yield basis are not reported."])

# Scheme 31, upper three-arrow sequence.
add(
    "p10_scheme31_upper_tosylcarbamate", "Scheme 31, upper stage 1", "general_scheme", e,
    [part("allenol", "reactant", "generic secondary 2,3-allenol", e), part("tsnco", "reagent", "TsNCO", e, name="p-toluenesulfonyl isocyanate"),
     part("carbamate", "product", "allenyl tosylcarbamate intermediate", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["carbamate"])],
    unresolved=["Generic R group and all numerical conditions/outcomes are missing."])
add(
    "p10_scheme31_upper_iodocyclization", "Scheme 31, upper stage 2", "general_scheme", e,
    [part("carbamate", "reactant", "allenyl tosylcarbamate intermediate", e), part("iodine", "reagent", "I2", e, name="iodine"),
     part("base", "reagent", "unspecified base", e), part("iodide_a", "product", "first cyclic iodide stereoisomer", e),
     part("iodide_b", "product", "second cyclic iodide stereoisomer", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["iodide_a", "iodide_b"])],
    unresolved=["Base identity, reagent amounts, time, temperature, product ratio, and yield are not reported."])
add(
    "p10_scheme31_upper_hydrolysis_acetylation", "Scheme 31, upper stage 3", "general_scheme", e,
    [part("iodides", "reactant", "cyclic iodide stereoisomer mixture", e), part("naoh", "reagent", "NaOH", e, name="sodium hydroxide"),
     part("ac2o", "reagent", "Ac2O", e, name="acetic anhydride"), part("pyridine", "reagent", "Py", e, name="pyridine"),
     part("major", "product", "major acetoxy sulfonamide product", e), part("minor", "product", "minor acetoxy sulfonamide product", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("relative_amount_major", "major", e, ["major"]), fld("relative_amount_minor", "minor", e, ["minor"]), fld("reported_yield", None, e, ["major", "minor"])],
    unresolved=["Reagent amounts, time, temperature, product ratio, and yield are not reported."])

# Scheme 31, lower two-arrow sequence.
add(
    "p10_scheme31_lower_imidate", "Scheme 31, lower stage 1", "general_scheme", e,
    [part("allenol", "reactant", "generic hydroxyalkyl-substituted 2,3-allenol", e),
     part("tcan", "reagent", "Cl3CCN", e, name="trichloroacetonitrile"), part("imidate", "product", "trichloroacetimidate intermediate", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["imidate"])],
    unresolved=["Generic R group and all numerical conditions/outcomes are missing."])
add(
    "p10_scheme31_lower_iodocyclization", "Scheme 31, lower stage 2", "general_scheme", e,
    [part("imidate", "reactant", "trichloroacetimidate intermediate", e), part("iodine", "reagent", "I2", e, name="iodine"),
     part("k2co3", "reagent", "K2CO3", e, name="potassium carbonate"), part("ether", "solvent", "Et2O", e, name="diethyl ether"),
     part("product", "product", "cyclic imidate product mixture", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("Z_to_E_ratio", "5:1-33:1", e, ["product"]), fld("reported_yield", None, e, ["product"])],
    unresolved=["Reagent amounts, time, temperature, row-level ratio assignments, and yield are not reported."])

add(
    "p10_scheme32_71_to_72", "Scheme 32, 71 to 72", "general_scheme", e,
    [part("compound71", "reactant", "generic tertiary 2,3-allenol 71", e),
     part("tsnco", "reagent", "TsNCO", e, name="p-toluenesulfonyl isocyanate"), part("nis", "reagent", "NIS", e, name="NIS"),
     part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"), part("compound72", "product", "alpha-iodo alpha,beta-unsaturated ketone 72", e)],
    [fld("stage_1_time", q(15, "h"), e), fld("stage_2_time", q(1, "h"), e), fld("temperature", "r.t.", e)],
    [fld("reported_yield", rng(29, 67, "%", "29%-67%"), e, ["compound72"]), fld("yield_measurement_basis", None, e, ["compound72"])],
    unresolved=["Generic R groups, reagent amounts, workup, purification, and yield basis are not reported."])
add(
    "p10_scheme32_72_to_73", "Scheme 32, 72 to 73", "general_scheme", e,
    [part("compound72", "reactant", "generic alpha-iodo enone 72", e), part("p_oet3", "reagent", "P(OEt)3", e, name="triethyl phosphite"),
     part("benzene", "solvent", "C6H6", e, name="benzene"), part("compound73", "product", "vinyl phosphonate 73", e)],
    [fld("temperature", "reflux", e), fld("time", None, e)],
    [fld("reported_yield", rng(74, 94, "%", "74%-94%"), e, ["compound73"]), fld("yield_measurement_basis", None, e, ["compound73"])],
    unresolved=["Generic R groups, reagent amount, time, workup, purification, and yield basis are not reported."])

add(
    "p10_scheme33_aryl_shift_scope", "Scheme 33, aryl-shift branch", "general_scheme", e,
    [part("compound74a", "reactant", "generic aryl-substituted 2,3-allenol 74a", e),
     part("electrophile", "reagent", "I2, Br2, or NBS", e, amounts=[fld("equivalents", q(2.0, "equiv"), e)]),
     part("mecn", "solvent", "CH3CN", e, name="acetonitrile"), part("water", "solvent", "H2O", e, name="water"),
     part("compound75", "product", "1,2-aryl-migration aldehyde 75", e)],
    [fld("solvent_ratio_CH3CN_to_H2O", "15:1", e), fld("temperature", "r.t.", e), fld("time", None, e)],
    [fld("reported_yield", rng(52, 93, "%", "52%-93%"), e, ["compound75"]), fld("yield_measurement_basis", None, e, ["compound75"])],
    unresolved=["The collective yield range is not assigned to individual electrophiles/substrates.", "Time, scale, workup, purification, and yield basis are not reported."])
add(
    "p10_scheme33_hydride_shift_scope", "Scheme 33, hydride-shift branch", "general_scheme", e,
    [part("compound9", "reactant", "alkyl-substituted 2,3-allenol 9", e),
     part("electrophile", "reagent", "I2 or Br2", e, amounts=[fld("equivalents", q(2.0, "equiv"), e)]),
     part("mecn", "solvent", "CH3CN", e, name="acetonitrile"), part("water", "solvent", "H2O", e, name="water"),
     part("compound76", "product", "1,2-hydride-migration ketone 76", e)],
    [fld("solvent_ratio_CH3CN_to_H2O", "15:1", e), fld("temperature", "r.t.", e), fld("time", None, e)],
    [fld("reported_yield", None, e, ["compound76"])],
    unresolved=["The source gives no numerical yield for this branch on the inspected page.", "Time, scale, workup, and purification are not reported."])

add(
    "p10_scheme34_migration_mechanism", "Scheme 34", "mechanism", e,
    [part("compound74", "reactant", "generic terminal 2,3-allenol 74", e), part("electrophile", "reagent", "X+", e),
     part("halonium77", "unspecified_agent", "halonium ion 77", e), part("intermediate78", "unspecified_agent", "aryl-shift intermediate 78", e),
     part("intermediate79", "unspecified_agent", "hydride-shift intermediate 79", e), part("compound75", "product", "aldehyde 75", e),
     part("compound76", "product", "ketone 76", e)],
    [], [], notes=["Proposed branching mechanism: R2 = aryl undergoes 1,2-aryl shift; R2 = Me undergoes 1,2-hydride shift."],
    unresolved=["This is a proposed mechanism, not a separately isolated experiment."])

add(
    "p10_scheme35_nazarov_cyclization", "Scheme 35 transformation", "literature_example", e,
    [part("compound80", "reactant", "2,3-allenol 80", e), part("naf", "reagent", "NaF", e, name="sodium fluoride"),
     part("hfpy", "reagent", "(HF)n·Py", e), part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"),
     part("compound82", "product", "cyclopentenone 82", e)],
    [fld("temperature", q(0, "°C"), e), fld("time", None, e)],
    [fld("reported_yield", q(45, "%"), e, ["compound82"]), fld("yield_measurement_basis", None, e, ["compound82"])],
    unresolved=MISSING_COMMON + ["Reagent quantities and reaction time are not reported."])
add(
    "p10_scheme35_nazarov_mechanism", "Scheme 35 intermediate", "mechanism", e,
    [part("compound80", "reactant", "2,3-allenol 80", e), part("compound81", "unspecified_agent", "allyl-methoxyallene intermediate 81", e),
     part("compound82", "product", "cyclopentenone 82", e)],
    [], [], notes=["The review states that 80 proceeds through intermediate 81 before Nazarov cyclization."],
    unresolved=["Intermediate 81 is proposed and is not reported as an isolated experiment here."])


# Page 11: intramolecular cycloadditions and radical reactions.
e = E[11]
add(
    "p11_scheme36_compound83", "Scheme 36", "literature_example", e,
    [part("compound83", "reactant", "2,3-allenol 83", e), part("compound85", "product", "seven-membered/two-four-membered fused product 85", e),
     part("compound84", "product", "alternative six-membered/two-four-membered fused product 84", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("product_85_observation", "observed selectively", e, ["compound85"]), fld("product_84_observation", "not detected", e, ["compound84"]),
     fld("reported_yield", None, e, ["compound85"])],
    unresolved=["Conditions and numerical yield are not reported on the inspected page.", "Generic R groups and complex stereochemistry remain unverified."])

for scaffold, r_value, yield_value in [
    ("upper", "H", 40), ("upper", "Me", 56), ("upper", "Ph", 58),
    ("lower", "Me", 60), ("lower", "Ph", 34),
]:
    add(
        f"p11_scheme37_{scaffold}_r_{r_value.lower()}", f"Scheme 37, {scaffold} substrate, R = {r_value}", "literature_example", e,
        [part("substrate", "reactant", f"Scheme 37 {scaffold} 2,3-allenol (R = {r_value})", e),
         part("toluene", "solvent", "toluene", e, name="toluene"), part("product", "product", f"tricyclic product (R = {r_value})", e)],
        [fld("temperature", q(220, "°C"), e), fld("operation", "sealed tube", e), fld("time", None, e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("diastereomer_ratio", "100:0", e, ["product"]),
         fld("yield_measurement_basis", None, e, ["product"])],
        unresolved=MISSING_COMMON + ["Reaction time is not reported."])

add(
    "p11_scheme38_compound86_scope", "Scheme 38", "general_scheme", e,
    [part("compound86", "reactant", "generic 2,3-allenol 86", e), part("product", "product", "generic intramolecular [2+2] cycloadduct", e)],
    [fld("temperature", "heated (exact temperature not reported)", e), fld("time", None, e)],
    [fld("reported_yield", rng(79, 100, "%", "79%-100%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=["Generic R groups, exact temperature, time, scale, workup, purification, and yield basis are not reported."])

add(
    "p11_scheme39_compound87", "Scheme 39", "literature_example", e,
    [part("compound87", "reactant", "2,3-allenol 87", e), part("bnnoh", "reagent", "PhCH2NHOH", e, name="benzylhydroxylamine"),
     part("benzene", "solvent", "benzene", e, name="benzene"), part("product", "product", "intramolecular [3+2] cycloadduct from 87", e)],
    [fld("temperature", "reflux", e), fld("time", None, e)],
    [fld("reported_yield", q(37, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=MISSING_COMMON + ["Reagent amount and reaction time are not reported."])

for code, substrate, r_value, product, yield_value, ze in [
    ("88a_me", "88a", "Me", "89", 64, "100:0"),
    ("88a_ph", "88a", "Ph", "89", 49, "100:0"),
    ("88b", "88b", "Me/PMP scaffold", "90", 47, "0:100"),
]:
    add(
        f"p11_scheme40_{code}", f"Scheme 40, {code}", "literature_example", e,
        [part("substrate", "reactant", f"terminal-alkynyl 2,3-allenol {substrate} ({r_value})", e),
         part("ph3snh", "reagent", "Ph3SnH", e, name="triphenyltin hydride"), part("aibn", "reagent", "AIBN", e, name="AIBN"),
         part("benzene", "solvent", "C6H6", e, name="benzene"), part("product", "product", f"radical cyclization product {product}", e)],
        [fld("temperature", q(80, "°C"), e), fld("time", None, e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("Z_to_E_ratio", ze, e, ["product"]),
         fld("yield_measurement_basis", None, e, ["product"])],
        unresolved=MISSING_COMMON + ["Reagent quantities and reaction time are not reported."])

add(
    "p11_scheme41_radical_cycle", "Scheme 41", "mechanism", e,
    [part("compound88a", "reactant", "2,3-allenol 88a", e), part("ph3snh", "reagent", "Ph3SnH", e, name="triphenyltin hydride"),
     part("radical91", "unspecified_agent", "triphenyltin radical 91", e), part("radical92", "unspecified_agent", "cyclizing radical 92", e),
     part("compound89", "product", "radical cyclization product 89", e)],
    [], [], notes=["Proposed chain: tin-radical addition, attack at the allene central carbon, ring closure, and hydrogen abstraction."],
    unresolved=["This is a proposed radical mechanism, not a separately isolated experiment."])


# Page 12: methylene-pi-allylpalladium chemistry.
e = E[12]
for branch, nucleophile, product in [
    ("soft", "soft nucleophile E-E", "allene 94"),
    ("hard", "R6ZnX or R6MgX", "1,3-diene 95"),
]:
    add(
        f"p12_scheme42_{branch}_nucleophile", f"Scheme 42, {branch} nucleophile branch", "mechanism", ev(11, 12),
        [part("derivative", "reactant", "generic 2,3-allenol derivative", ev(11, 12)), part("pd0", "catalyst", "Pd(0)", ev(11, 12)),
         part("intermediate93", "unspecified_agent", "methylene-pi-allylpalladium intermediate 93", ev(11, 12)),
         part("nucleophile", "reactant", nucleophile, ev(11, 12)), part("product", "product", product, ev(11, 12))],
        [], [], notes=[f"Conceptual selectivity branch leading to {product}."],
        unresolved=["This is a generic mechanistic scheme with R groups, not a separately reported experiment."])

add(
    "p12_scheme43_acetate96_dimethyl_malonate", "Scheme 43, acetate 96", "literature_example", e,
    [part("compound96", "reactant", "2,3-allenol acetate 96", e), part("malonate", "reactant", "dimethyl malonate", e, name="dimethyl malonate"),
     part("pd", "catalyst", "Pd(PPh3)4", e), part("compound94a", "product", "monoallenylation product 94a", e),
     part("compound97", "product", "bis-allenylation product 97", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield_94a", q(47, "%"), e, ["compound94a"]), fld("reported_yield_97", q(26, "%"), e, ["compound97"]),
     fld("yield_measurement_basis", None, e, ["compound94a", "compound97"])],
    unresolved=MISSING_COMMON + ["Catalyst/reactant quantities, solvent, time, and temperature are not reported."])

add(
    "p12_scheme43_phosphate98_dimethyl_malonate", "Scheme 43, phosphate 98 + dimethyl malonate", "literature_example", e,
    [part("compound98", "reactant", "2,3-allenol phosphate 98", e), part("malonate", "reactant", "dimethyl malonate", e, name="dimethyl malonate"),
     part("pddba2", "catalyst", "Pd(dba)2", e), part("pph3", "reagent", "PPh3", e, name="triphenylphosphine", amounts=[fld("reported_stoichiometry", "6 PPh3 per Pd(dba)2 as printed", e)]),
     part("thf", "solvent", "THF", e, name="THF"), part("compound94a", "product", "monoallenylation product 94a", e),
     part("compound97", "product", "bis-allenylation product 97", e)],
    [fld("temperature", q(20, "°C"), e), fld("time", None, e)],
    [fld("reported_yield_94a", q(80, "%"), e, ["compound94a"]), fld("reported_yield_97", q(0, "%"), e, ["compound97"]),
     fld("yield_measurement_basis", None, e, ["compound94a", "compound97"])],
    unresolved=MISSING_COMMON + ["Catalyst/reactant quantities and reaction time are not reported; the printed '6 PPh3' is retained without inferring mol% or equivalents."])

add(
    "p12_scheme43_phosphate98_ethyl_acetoacetate", "Scheme 43, phosphate 98 + ethyl acetoacetate", "literature_example", e,
    [part("compound98", "reactant", "2,3-allenol phosphate 98", e), part("acetoacetate", "reactant", "ethyl acetoacetate", e, name="ethyl acetoacetate"),
     part("pddba2", "catalyst", "Pd(dba)2", e), part("pph3", "reagent", "PPh3", e, name="triphenylphosphine", amounts=[fld("reported_stoichiometry", "6 PPh3 per Pd(dba)2 as printed", e)]),
     part("thf", "solvent", "THF", e, name="THF"), part("compound94b", "product", "allenylation product 94b", e),
     part("compound99", "product", "cyclopropane byproduct 99", e)],
    [fld("temperature", q(65, "°C"), e), fld("time", q(1, "h"), e)],
    [fld("reported_yield_94b", q(61, "%"), e, ["compound94b"]), fld("reported_yield_99", q(13, "%"), e, ["compound99"]),
     fld("yield_measurement_basis", None, e, ["compound94b", "compound99"])],
    unresolved=MISSING_COMMON + ["Catalyst/reactant quantities are not reported; the printed '6 PPh3' is retained without inferring mol% or equivalents."])

add(
    "p12_scheme43_cyclopropane99_mechanism", "Scheme 43, formation of 99", "mechanism", e,
    [part("compound98", "reactant", "2,3-allenol phosphate 98", e), part("compound94b", "reactant", "allenylation product 94b", e),
     part("palladium", "catalyst", "PdXLn", e), part("base", "reagent", "unspecified base", e),
     part("compound99", "product", "cyclopropane 99", e)],
    [], [], notes=["The drawing proposes reaction of 94b with a 2-(1,3-butadienyl)palladium intermediate followed by base-promoted cyclopropane formation."],
    unresolved=["This is a proposed mechanism; the base, X, ligand set, and intermediate isolation are not specified."])

add(
    "p12_eq17_asymmetric_allenylation_scope", "Eq. 17", "general_scheme", e,
    [part("compound100", "reactant", "generic 2,3-allenol phosphate 100", e), part("malonate", "reactant", "generic substituted malonate", e),
     part("pd_ligand", "catalyst", "Pd-(R)-MeOBIPHEP", e), part("bsa", "reagent", "BSA", e),
     part("thf", "solvent", "THF", e, name="THF"), part("product", "product", "chiral substituted allene product", e)],
    [fld("temperature", "r.t.", e), fld("time", None, e)],
    [fld("reported_yield", rng(69, 90, "%", "69%-90%"), e, ["product"]), fld("product_ee", rng(60, 90, "%", "60%-90% ee"), e, ["product"]),
     fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=["Generic R groups, catalyst loading, participant quantities, time, workup, purification, and yield basis are not reported."])

add(
    "p12_eq18_bromodiene_allenylation", "Eq. 18", "general_scheme", e,
    [part("bromodiene", "reactant", "generic 2-bromo-1,3-butadiene", e), part("nucleophile", "reactant", "Nu-", e),
     part("pd", "catalyst", "Pd catalyst", e), part("intermediate102", "unspecified_agent", "methylene-pi-allylpalladium intermediate 102", e),
     part("product", "product", "generic substituted allene", e)],
    [fld("time", None, e), fld("temperature", None, e)], [fld("reported_yield", None, e, ["product"])],
    unresolved=["This is a generic equation; catalyst identity/loading, nucleophile identity, conditions, and yield are not reported."])

add(
    "p12_eq19_bromodiene103_scope", "Eq. 19", "general_scheme", e,
    [part("compound103", "reactant", "generic 2-bromo-1,3-butadiene 103", e), part("nucleophile", "reactant", "M-Nu", e),
     part("pd", "catalyst", "[PdCl(eta3-C3H5)]2/dpbp", e, amounts=[fld("catalyst_loading", q(2, "mol%"), e)]),
     part("thf", "solvent", "THF", e, name="THF"), part("compound104", "product", "generic allene 104", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", rng(62, 93, "%", "62%-93%"), e, ["compound104"]), fld("yield_measurement_basis", None, e, ["compound104"])],
    unresolved=["Generic R/M/Nu groups, participant quantities, time, temperature, workup, purification, and yield basis are not reported."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
