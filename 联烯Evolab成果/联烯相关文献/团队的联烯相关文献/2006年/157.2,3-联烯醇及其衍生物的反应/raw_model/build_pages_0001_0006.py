#!/usr/bin/env python3
"""Build machine extraction records for source PDF pages 1--6.

The source is a review article.  Specific cited examples are therefore marked
as literature_example, while generic transformations and proposed pathways
are kept as general_scheme and mechanism records respectively.
"""

import json
from pathlib import Path


DOC = "doc_27796c91f0b5e453"
OUT = Path(__file__).with_name("pages_0001_0006_records.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


E = {page: ev(page) for page in range(1, 7)}


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


SMILES = {
    "chloroform": "ClC(Cl)Cl",
    "dichloromethane": "ClCCl",
    "hexane": "CCCCCC",
    "DMSO": "CS(C)=O",
    "potassium tert-butoxide": "[K+].[O-]C(C)(C)C",
    "silver nitrate": "[Ag+].[O-][N+](=O)[O-]",
    "water": "O",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "DMF": "CN(C)C=O",
    "iodobenzene": "Ic1ccccc1",
    "4-iodotoluene": "Cc1ccc(I)cc1",
    "4-iodoanisole": "COc1ccc(I)cc1",
    "benzylamine": "NCc1ccccc1",
    "triethylamine": "CCN(CC)CC",
    "allyl bromide": "C=CCBr",
    "pyrrolidine": "C1CCNC1",
    "triphenylphosphine": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "DMA": "CC(=O)N(C)C",
    "THF": "C1CCOC1",
    "TFA": "O=C(O)C(F)(F)F",
    "LiBr": "[Li+].[Br-]",
    "oxygen": "O=O",
    "acetonitrile": "CC#N",
    "carbon monoxide": "[C-]#[O+]",
    "1,4-dioxane": "O1CCOCC1",
    "tert-butyl hydroperoxide": "CC(C)(C)OO",
    "benzene": "c1ccccc1",
    "2,3-allenol 11": "C=C=CC1(O)CCCCC1",
    "2,3-allenoic acid 17": "CC(=C=Cc1ccccc1)C(=O)O",
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


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def missing_conditions(evidence, *, time=True, temperature=True):
    result = []
    if time:
        result.append(fld("time", None, evidence))
    if temperature:
        result.append(fld("temperature", None, evidence))
    return result


def record(suffix, source_id, kind, evidence, participants, conditions, outcomes,
           notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
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
            "unresolved": list(unresolved),
        },
    }


records = []


def add(*args, **kwargs):
    records.append(record(*args, **kwargs))


# Page 2: cycloisomerization examples and Scheme 2 elimination variants.
add(
    "p2_eq1_ag_or_hg_cycloisomerization", "Eq. 1", "general_scheme", E[2],
    [part("allenol", "reactant", "generic 2,3-allenol", E[2]),
     part("silver_or_mercury", "catalyst", "Ag+ or Hg2+", E[2]),
     part("dihydrofuran", "product", "generic 2,5-dihydrofuran", E[2])],
    missing_conditions(E[2]),
    [fld("reported_yield", None, E[2], ["dihydrofuran"])],
    notes=["The review describes this transformation as highly regioselective."],
    unresolved=["Generic R groups are not fully specified.", "Catalyst loading, solvent, time, temperature, and yield are not reported here."])

add(
    "p2_eq2_hcl_cycloisomerization", "Eq. 2", "literature_example", E[2],
    [part("allenol", "reactant", "depicted chiral 2,3-allenol", E[2],
          amounts=[fld("starting_material_diastereomer_ratio", "90:10", E[2])]),
     part("hcl", "reagent", "HCl", E[2]),
     part("chloroform", "solvent", "CHCl3", E[2], name="chloroform"),
     part("product", "product", "depicted chiral 2,5-dihydrofuran", E[2])],
    missing_conditions(E[2]),
    [fld("reported_yield", q(90, "%"), E[2], ["product"]),
     fld("product_diastereomer_ratio", "90:10", E[2], ["product"]),
     fld("yield_measurement_basis", None, E[2], ["product"])],
    notes=["The review states that chirality transfer occurs."],
    unresolved=["Reaction time, temperature, scale, workup, purification, and yield basis are not reported.", "The depicted stereostructures require chemical review."])

add(
    "p2_eq3_aucl3_cycloisomerization", "Eq. 3", "general_scheme", E[2],
    [part("allenol", "reactant", "generic chiral 2,3-allenol", E[2]),
     part("aucl3", "catalyst", "AuCl3", E[2], amounts=[fld("catalyst_loading", rng(5, 10, "mol%", "5-10 mol%"), E[2])]),
     part("dichloromethane", "solvent", "CH2Cl2", E[2], name="dichloromethane"),
     part("product", "product", "generic chiral 2,5-dihydrofuran", E[2])],
    [fld("temperature", "r.t.", E[2]), fld("time", None, E[2])],
    [fld("reported_yield", rng(24, 100, "%", "24%-100%"), E[2], ["product"]),
     fld("yield_measurement_basis", None, E[2], ["product"])],
    notes=["The review reports axial-to-central chirality transfer and broad substituent tolerance."],
    unresolved=["Generic R groups, time, scale, workup, purification, and yield basis are not reported."])

add(
    "p2_scheme1_primary_amine_cyclization", "Scheme 1", "literature_example", E[2],
    [part("compound1", "reactant", "2,3-allenol 1", E[2]),
     part("primary_amine", "catalyst", "RNH2 (primary amine)", E[2]),
     part("hexane", "solvent", "hexane", E[2], name="hexane"),
     part("product", "product", "TIPS/fluoro-substituted dihydrofuran", E[2])],
    [fld("temperature", "r.t.", E[2]), fld("time", q(20, "h"), E[2])],
    [fld("reported_yield", q(89, "%"), E[2], ["product"]), fld("yield_measurement_basis", None, E[2], ["product"])],
    notes=["R on the primary amine is unspecified in the scheme."],
    unresolved=["Catalyst loading, scale, workup, purification, and yield basis are not reported.", "Full stereochemistry and the amine identity are unspecified."])

add(
    "p2_eq4_benzotriazole_allenol_cyclization", "Eq. 4", "literature_example", E[2],
    [part("compound2", "reactant", "benzotriazole-substituted 2,3-allenol 2", E[2]),
     part("hydroxide", "reagent", "OH-", E[2]),
     part("product", "product", "depicted fused dihydrofuran product", E[2])],
    missing_conditions(E[2]),
    [fld("reported_yield", q(60, "%"), E[2], ["product"]), fld("yield_measurement_basis", None, E[2], ["product"])],
    unresolved=["Base identity/amount, solvent, time, temperature, scale, workup, purification, and yield basis are not reported.", "Product structure requires chemical review."])

add(
    "p2_eq5_tbuok_cyclization", "Eq. 5", "literature_example", E[2],
    [part("compound3", "reactant", "tertiary 2,3-allenol 3", E[2]),
     part("tbuok", "reagent", "t-BuOK", E[2], name="potassium tert-butoxide"),
     part("dmso", "solvent", "DMSO", E[2], name="DMSO"),
     part("product", "product", "depicted bicyclic dihydrofuran product", E[2])],
    missing_conditions(E[2]),
    [fld("reported_yield", q(90, "%"), E[2], ["product"]), fld("yield_measurement_basis", None, E[2], ["product"])],
    notes=["The review says the reaction may proceed by a single-electron-transfer radical process."],
    unresolved=["Reagent amount, time, temperature, scale, workup, purification, and yield basis are not reported."])

for compound, leaving, product_label in [
    ("4", "-MeOH", "PhS-substituted furan from 4"),
    ("5", "-PhSH", "MeO-substituted furan from 5"),
]:
    add(
        f"p2_scheme2_compound{compound}", f"Scheme 2, compound {compound}", "literature_example", E[2],
        [part("substrate", "reactant", f"2,3-allenol {compound}", E[2]),
         part("hgcl2", "catalyst", "HgCl2", E[2]),
         part("dichloromethane", "solvent", "CH2Cl2", E[2], name="dichloromethane"),
         part("product", "product", product_label, E[2])],
        [fld("temperature", "r.t.", E[2]), fld("time", None, E[2])],
        [fld("reported_yield", None, E[2], ["product"])],
        notes=[f"The depicted cyclization-elimination sequence shows {leaving}."],
        unresolved=["Generic substituents are not fully specified.", "Catalyst loading, time, scale, workup, purification, and yield are not reported."])

add(
    "p2_scheme2_compound6", "Scheme 2, compound 6", "literature_example", E[2],
    [part("compound6", "reactant", "TIPS/fluoro-substituted 2,3-allenol 6", E[2]),
     part("agno3", "catalyst", "AgNO3", E[2], name="silver nitrate", amounts=[fld("catalyst_loading", q(20, "mol%"), E[2])]),
     part("dichloromethane", "solvent", "CH2Cl2", E[2], name="dichloromethane"),
     part("product", "product", "TIPS-substituted furan", E[2])],
    missing_conditions(E[2]),
    [fld("reported_yield", q(65, "%"), E[2], ["product"]), fld("yield_measurement_basis", None, E[2], ["product"])],
    notes=["The depicted cyclization-elimination sequence shows loss of HF."],
    unresolved=["Time, temperature, scale, workup, purification, and yield basis are not reported."])


# Page 3: water-dependent Scheme 3 and palladium coupling chemistry.
add(
    "p3_scheme3_anhydrous", "Scheme 3, anhydrous branch", "literature_example", E[3],
    [part("compound7", "reactant", "TMS-substituted 2,3-allenol 7", E[3]),
     part("agno3", "catalyst", "AgNO3", E[3], name="silver nitrate"),
     part("product", "product", "TMS-substituted dihydrofuran from 7", E[3])],
    missing_conditions(E[3]),
    [fld("reported_yield", None, E[3], ["product"])],
    notes=["The prose explicitly assigns this cycloisomerization to the water-free system."],
    unresolved=["Generic R groups and all numerical conditions/outcomes are missing."])

add(
    "p3_scheme3_aqueous", "Scheme 3, water-added branch", "literature_example", E[3],
    [part("compound7", "reactant", "TMS-substituted 2,3-allenol 7", E[3]),
     part("agno3", "catalyst", "AgNO3", E[3], name="silver nitrate"),
     part("water", "reagent", "H2O", E[3], name="water"),
     part("product8", "product", "alpha,beta-unsaturated ketone 8", E[3])],
    missing_conditions(E[3]),
    [fld("reported_yield", "low", E[3], ["product8"])],
    notes=["The review reports only that the yield is low."],
    unresolved=["Water amount, catalyst loading, solvent, time, temperature, and numerical yield are not reported."])

add(
    "p3_scheme4_tsuji_beta_h_elimination", "Scheme 4, path a", "general_scheme", E[3],
    [part("allenol", "reactant", "generic 2,3-allenol", E[3]),
     part("halide", "reactant", "generic organic halide R2X", E[3]),
     part("pd0", "catalyst", "Pd(0)", E[3]),
     part("tertiary_amine", "reagent", "NR3 (tertiary amine)", E[3]),
     part("ketone", "product", "generic alpha,beta-unsaturated ketone", E[3])],
    missing_conditions(E[3]),
    [fld("reported_yield", None, E[3], ["ketone"])],
    notes=["Only path a is stated as prior chemistry; the b/c ring products in Scheme 4 are posed as questions and are not treated as experiments."],
    unresolved=["All numerical conditions and substituent identities are missing."])

add(
    "p3_eq6_generic_epoxide_scope", "Eq. 6", "general_scheme", E[3],
    [part("allenol", "reactant", "generic 2,3-allenol", E[3]),
     part("iodide", "reactant", "aryl or alkenyl iodide R2X", E[3]),
     part("pdpph3", "catalyst", "Pd(PPh3)4", E[3]),
     part("k2co3", "reagent", "K2CO3", E[3], name="potassium carbonate"),
     part("dmf", "solvent", "DMF", E[3], name="DMF"),
     part("epoxide", "product", "generic trans-vinylic epoxide", E[3])],
    [fld("temperature", q(55, "°C"), E[3]), fld("time", None, E[3])],
    [fld("reported_yield", rng(46, 95, "%", "46%-95%"), E[3], ["epoxide"]),
     fld("diastereomer_ratio", "92:8-100:0", E[3], ["epoxide"]),
     fld("yield_measurement_basis", None, E[3], ["epoxide"])],
    notes=["The alternative 2,5-dihydrofuran product was not detected."],
    unresolved=["Catalyst/base amounts, time, scale, workup, purification, and yield basis are not reported.", "Generic R groups are not fully specified."])

scheme5_rows = [
    ("vinyl_iodide", "depicted n-butyl-substituted vinyl iodide", None, 52, 98.0),
    ("p_iodotoluene", "4-iodotoluene", "4-iodotoluene", 85, 96.0),
    ("p_iodoanisole", "4-iodoanisole", "4-iodoanisole", 74, 97.5),
]
for suffix, reagent_label, reagent_name, yield_value, product_ee in scheme5_rows:
    add(
        f"p3_scheme5_{suffix}", f"Scheme 5, {suffix}", "literature_example", E[3],
        [part("allenol", "reactant", "depicted optically active 2,3-allenol", E[3], amounts=[fld("starting_material_ee", q(98, "%"), E[3])]),
         part("iodide", "reactant", reagent_label, E[3], name=reagent_name),
         part("pdpph3", "catalyst", "Pd(PPh3)4", E[3]),
         part("k2co3", "reagent", "K2CO3", E[3], name="potassium carbonate"),
         part("dmf", "solvent", "DMF", E[3], name="DMF"),
         part("product", "product", "depicted chiral vinylic epoxide", E[3])],
        [fld("temperature", q(55, "°C"), E[3]), fld("time", None, E[3])],
        [fld("reported_yield", q(yield_value, "%"), E[3], ["product"]),
         fld("product_ee", q(product_ee, "%"), E[3], ["product"]),
         fld("absolute_configuration", "R,R", E[3], ["product"]),
         fld("yield_measurement_basis", None, E[3], ["product"])],
        unresolved=["Catalyst/base amounts, time, scale, workup, purification, and yield basis are not reported.", "The depicted structures and stereochemistry require chemical review."])

add(
    "p3_scheme6_compound9_allyl_bromide", "Scheme 6", "literature_example", E[3],
    [part("compound9", "reactant", "2,3-allenol 9", E[3]),
     part("allyl_bromide", "reactant", "allyl bromide", E[3], name="allyl bromide"),
     part("pdcl2", "catalyst", "PdCl2", E[3]),
     part("product10", "product", "dihydrofuran 10", E[3])],
    missing_conditions(E[3]),
    [fld("reported_yield", q(76, "%"), E[3], ["product10"]), fld("yield_measurement_basis", None, E[3], ["product10"])],
    notes=["The review describes the outcome as regioselectively different from the Pd(0) reaction."],
    unresolved=["Catalyst loading, solvent, time, temperature, scale, workup, purification, and yield basis are not reported."])

add(
    "p3_scheme6_proposed_pathway", "Scheme 6 pathway", "mechanism", E[3],
    [part("compound9", "reactant", "2,3-allenol 9", E[3]),
     part("allyl_bromide", "reactant", "allyl bromide", E[3], name="allyl bromide"),
     part("pdcl2", "catalyst", "PdCl2/Pd(II)", E[3]),
     part("product10", "product", "dihydrofuran 10", E[3])],
    [], [],
    notes=["The depicted proposal proceeds through palladation, carbopalladation, and beta-palladium halide elimination."],
    unresolved=["This is a proposed pathway, not a separately reported isolated experiment."])

for branch, r1_class, product_label in [
    ("a", "R1 = alkyl", "gamma-amino alcohol"),
    ("b", "R1 = aryl", "alpha-amino alcohol"),
]:
    add(
        f"p3_scheme7_branch_{branch}", f"Scheme 7, branch {branch}", "general_scheme", E[3],
        [part("allenol", "reactant", f"generic 2,3-allenol ({r1_class})", E[3]),
         part("iodide", "reactant", "aryl or alkenyl iodide R2I", E[3]),
         part("secondary_amine", "reactant", "secondary amine R3R4NH", E[3]),
         part("pd0", "catalyst", "Pd(0)", E[3]),
         part("triethylamine", "solvent", "Et3N", E[3], name="triethylamine"),
         part("product", "product", product_label, E[3])],
        missing_conditions(E[3]),
        [fld("reported_yield", None, E[3], ["product"])],
        notes=[f"The review assigns branch {branch} to {r1_class} and depicts regio-/stereochemical control through an allylpalladium intermediate."],
        unresolved=["Generic substituents, catalyst identity/loading, reagent amounts, time, temperature, and yield are not reported."])


# Page 4: Scheme 8 examples, Scheme 9 hydroamination, and Eq. 7/8 condition rows.
scheme8_rows = [
    ("phenyl", "depicted phenyl-substituted chiral 2,3-allenol", 98, 70, 42, 57, 98),
    ("pentyl", "depicted n-pentyl-substituted chiral 2,3-allenol", 97, 74, 44, 58, 96),
    ("octyl", "depicted n-octyl-substituted 2,3-allenol", None, 77, 36, 87, None),
]
for suffix, substrate_label, starting_ee, temp, hours, yield_value, product_ee in scheme8_rows:
    substrate_amounts = [fld("starting_material_ee", q(starting_ee, "%"), E[4])] if starting_ee is not None else []
    outcomes = [fld("reported_yield", q(yield_value, "%"), E[4], ["product"]), fld("yield_measurement_basis", None, E[4], ["product"])]
    if product_ee is not None:
        outcomes.append(fld("product_ee", q(product_ee, "%"), E[4], ["product"]))
    add(
        f"p4_scheme8_{suffix}", f"Scheme 8, {suffix} example", "literature_example", E[4],
        [part("allenol", "reactant", substrate_label, E[4], amounts=substrate_amounts),
         part("iodobenzene", "reactant", "PhI", E[4], name="iodobenzene"),
         part("benzylamine", "reactant", "BnNH2", E[4], name="benzylamine"),
         part("pdpph3", "catalyst", "Pd(PPh3)4", E[4], amounts=[fld("catalyst_loading", q(5, "mol%"), E[4])]),
         part("triethylamine", "solvent", "Et3N", E[4], name="triethylamine"),
         part("product", "product", "depicted amino alcohol product", E[4])],
        [fld("temperature", q(temp, "°C"), E[4]), fld("time", q(hours, "h"), E[4])],
        outcomes,
        unresolved=["Reactant quantities, scale, workup, purification, and yield basis are not reported.", "Depicted stereochemistry requires chemical review."])

add(
    "p4_scheme9_hydroamination", "Scheme 9 transformation", "literature_example", E[4],
    [part("compound11", "reactant", "2,3-allenol 11", E[4], name="2,3-allenol 11"),
     part("pyrrolidine", "reactant", "pyrrolidine", E[4], name="pyrrolidine"),
     part("pd2dba3", "catalyst", "Pd2(dba)3·CHCl3", E[4], amounts=[fld("catalyst_loading", q(5, "mol%"), E[4])]),
     part("pph3", "reagent", "PPh3", E[4], name="triphenylphosphine", amounts=[fld("reported_loading", q(10, "mol%"), E[4])]),
     part("et3nhi", "unspecified_agent", "Et3NHI", E[4], amounts=[fld("reported_loading_percentage", rng(15, 20, "%", "15%-20%"), E[4])]),
     part("thf", "solvent", "THF", E[4], name="THF"),
     part("product", "product", "depicted pyrrolidinyl amino alcohol", E[4])],
    [fld("temperature", "reflux", E[4]), fld("time", None, E[4])],
    [fld("reported_yield", q(60, "%"), E[4], ["product"]), fld("yield_measurement_basis", None, E[4], ["product"])],
    unresolved=["Time, reactant quantities, scale, workup, purification, and yield basis are not reported.", "The exact role and unit convention for 15%-20% Et3NHI require source review."])

add(
    "p4_scheme9_proposed_hydroamination_paths", "Scheme 9 pathways c/d", "mechanism", E[4],
    [part("compound11", "reactant", "2,3-allenol 11", E[4], name="2,3-allenol 11"),
     part("pyrrolidine", "reactant", "pyrrolidine", E[4], name="pyrrolidine"),
     part("pd0", "catalyst", "Pd(0)/HPdI", E[4]),
     part("product", "product", "depicted pyrrolidinyl amino alcohol", E[4])],
    [], [],
    notes=["Path c invokes pi-allylpalladium intermediate 12; path d invokes intermediate 13 from HPdI coordination to the terminal allene double bond."],
    unresolved=["The source presents two possible explanations and does not resolve which pathway operates."])

eq7_rows = [
    ("5eq_4h", 5.0, 4, q(65, "%"), q(4, "%")),
    ("0p25eq_10h", 0.25, 10, q(73, "%"), "trace"),
    ("0eq_48h", 0.0, 48, q(24, "%"), "table dash (—)"),
]
for suffix, allyl_eq, hours, y14, y15 in eq7_rows:
    add(
        f"p4_eq7_{suffix}", f"Eq. 7, {allyl_eq:g} equiv allyl bromide", "optimization_entry", E[4],
        [part("compound11", "reactant", "2,3-allenol 11", E[4], name="2,3-allenol 11"),
         part("allyl_bromide", "reactant", "allyl bromide", E[4], name="allyl bromide", amounts=[fld("equivalents", q(allyl_eq, "equiv"), E[4])]),
         part("pdcl2", "catalyst", "PdCl2", E[4], amounts=[fld("catalyst_loading", q(5, "mol%"), E[4])]),
         part("dma", "solvent", "DMA", E[4], name="DMA"),
         part("product14", "product", "dimeric coupling product 14", E[4]),
         part("product15", "product", "4-allyl-substituted dihydrofuran 15", E[4])],
        [fld("temperature", "r.t.", E[4]), fld("time", q(hours, "h"), E[4])],
        [fld("reported_yield_product_14", y14, E[4], ["product14"]),
         fld("reported_yield_product_15", y15, E[4], ["product15"]),
         fld("yield_measurement_basis", None, E[4], ["product14", "product15"])],
        notes=["The zero-loading row explicitly omits allyl bromide; the participant is retained to preserve the source condition." if allyl_eq == 0 else "Eq. 7 presents this as one of three distinct allyl-bromide loading/time rows."],
        unresolved=["Substrate/catalyst quantities, scale, workup, purification, and yield basis are not reported.", "The dash for product 15 is preserved without interpreting it as zero or not detected."] if allyl_eq == 0 else ["Substrate/catalyst quantities, scale, workup, purification, and yield basis are not reported."])

add(
    "p4_eq8_allenyl_bromide", "Eq. 8", "literature_example", E[4],
    [part("compound11", "reactant", "2,3-allenol 11", E[4], name="2,3-allenol 11"),
     part("allenyl_bromide", "reactant", "depicted allenyl bromide", E[4]),
     part("pdcl2", "catalyst", "PdCl2", E[4], amounts=[fld("catalyst_loading", q(5, "mol%"), E[4])]),
     part("dma", "solvent", "DMA", E[4], name="DMA"),
     part("product16", "product", "expected coupling product 16", E[4]),
     part("product14", "product", "dimeric coupling product 14", E[4])],
    [fld("temperature", "r.t.", E[4]), fld("time", q(9, "h"), E[4])],
    [fld("combined_reported_yield", q(55, "%"), E[4], ["product16", "product14"]),
     fld("product_16_to_14_ratio", "92:8", E[4], ["product16", "product14"]),
     fld("yield_measurement_basis", None, E[4], ["product16", "product14"])],
    unresolved=["Reactant quantities, scale, workup, purification, and yield basis are not reported.", "The 55% is treated as a combined outcome because no product-specific yield is shown."])


# Page 5: allenoic-acid coupling/cyclization and mechanistic proposals.
for suffix, allenol_label, yield_min, yield_max, note in [
    ("r4_ne_h_r5_h", "generic tertiary 2,3-allenol (R4 != H, R5 = H)", 52, 75, "The review states that this substitution class gives only the E product."),
    ("secondary_allenol", "generic secondary 2,3-allenol", 52, 82, "The product is depicted as the E isomer."),
]:
    add(
        f"p5_scheme10_{suffix}", f"Scheme 10, {suffix}", "general_scheme", E[5],
        [part("allenoic_acid", "reactant", "generic 2,3-allenoic acid", E[5]),
         part("allenol", "reactant", allenol_label, E[5]),
         part("pdcl2", "catalyst", "PdCl2", E[5], amounts=[fld("catalyst_loading", q(5, "mol%"), E[5])]),
         part("dma", "solvent", "DMA", E[5], name="DMA"),
         part("product", "product", "generic 2(5H)-furanone coupling product", E[5])],
        [fld("temperature", q(30, "°C"), E[5]), fld("time", None, E[5])],
        [fld("reported_yield", rng(yield_min, yield_max, "%", f"{yield_min}%-{yield_max}%"), E[5], ["product"]),
         fld("product_geometry", "E", E[5], ["product"]),
         fld("yield_measurement_basis", None, E[5], ["product"])],
        notes=[note],
        unresolved=["Generic substituents, reactant quantities, time, scale, workup, purification, and yield basis are not reported."])

add(
    "p5_eq9_compounds17_11", "Eq. 9", "literature_example", E[5],
    [part("compound17", "reactant", "2,3-allenoic acid 17", E[5], name="2,3-allenoic acid 17"),
     part("compound11", "reactant", "2,3-allenol 11", E[5], name="2,3-allenol 11"),
     part("pdcl2", "catalyst", "PdCl2", E[5], amounts=[fld("catalyst_loading", q(5, "mol%"), E[5])]),
     part("dma", "solvent", "DMA", E[5], name="DMA"),
     part("product18", "product", "target furanone 18", E[5]),
     part("product14", "product", "allenol dimerization product 14", E[5])],
    [fld("temperature", q(30, "°C"), E[5]), fld("time", q(22, "h"), E[5])],
    [fld("reported_yield_product_18", q(67, "%"), E[5], ["product18"]),
     fld("reported_yield_product_14", q(4, "%"), E[5], ["product14"]),
     fld("yield_measurement_basis", None, E[5], ["product18", "product14"])],
    unresolved=["Reactant quantities, scale, workup, purification, and yield basis are not reported.", "Candidate SMILES omit axial stereochemistry and remain unverified."])

for suffix, tfa_equiv, product_yield, product_ee in [
    ("no_tfa", None, 58, 36),
    ("tfa_0p8eq", 0.8, 62, 98),
]:
    participants = [
        part("compound17", "reactant", "R-(-)-2,3-allenoic acid 17", E[5], name="2,3-allenoic acid 17", amounts=[fld("starting_material_ee", q(98, "%"), E[5])]),
        part("compound19", "reactant", "2,3-allenol 19", E[5]),
        part("pdcl2", "catalyst", "PdCl2", E[5], amounts=[fld("catalyst_loading", q(5, "mol%"), E[5])]),
        part("dma", "solvent", "DMA", E[5], name="DMA"),
        part("product20", "product", "R-(-)-furanone 20", E[5]),
    ]
    if tfa_equiv is not None:
        participants.insert(4, part("tfa", "reagent", "TFA", E[5], name="TFA", amounts=[fld("equivalents", q(tfa_equiv, "equiv"), E[5])]))
    add(
        f"p5_eq10_{suffix}", f"Eq. 10, {suffix}", "optimization_entry", E[5], participants,
        [fld("temperature", q(30, "°C"), E[5]), fld("time", None, E[5])],
        [fld("reported_yield", q(product_yield, "%"), E[5], ["product20"]),
         fld("product_ee", q(product_ee, "%"), E[5], ["product20"]),
         fld("yield_measurement_basis", None, E[5], ["product20"])],
        notes=["No TFA was added." if tfa_equiv is None else "The review states that added TFA suppresses product racemization."],
        unresolved=["Reactant quantities, time, scale, workup, purification, and yield basis are not reported.", "Candidate starting-material SMILES omit axial stereochemistry and remain unverified."])

add(
    "p5_scheme11_coupling_cycle", "Scheme 11", "mechanism", E[5],
    [part("compound17", "reactant", "R-(-)-2,3-allenoic acid 17", E[5], name="2,3-allenoic acid 17"),
     part("compound19", "reactant", "2,3-allenol 19", E[5]),
     part("pdx2", "catalyst", "PdX2", E[5]),
     part("product20", "product", "R-(-)-furanone 20", E[5])],
    [], [],
    notes=["Proposed cycle: cyclopalladation gives M1, carbopalladation with 19 gives pi-allylpalladium M2, beta-OH elimination gives 20 and XPd+[OH]-, and HX/H2O turnover regenerates PdX2."],
    unresolved=["This is a proposed mechanism, not a separately isolated experiment; X is not specified."])

add(
    "p5_scheme12_e_selectivity_model", "Scheme 12", "mechanism", E[5],
    [part("m3", "unspecified_agent", "proposed intermediate M3", E[5]),
     part("m4", "unspecified_agent", "proposed intermediate M4", E[5]),
     part("e_product", "product", "E isomer", E[5]),
     part("z_product", "product", "Z isomer", E[5])],
    [],
    [fld("E_isomer_observation", "observed", E[5], ["e_product"]),
     fld("Z_isomer_observation", "not detected", E[5], ["z_product"])],
    notes=["The review proposes that M3 is thermodynamically more stable than M4 and invokes a sigma-pi-sigma transition state to explain E selectivity."],
    unresolved=["This is a qualitative selectivity rationale, not a separately reported experiment."])


# Pages 5--6: Scheme 13/14 and Eq. 11 begin in page-5 prose and are depicted on page 6.
E56 = E[5] + E[6]
for compound, product, temp, yield_value in [
    ("21a", "22a", "r.t.", 48),
    ("21b", "22b", "reflux", 52),
    ("21c", "22c", "r.t.", 41),
]:
    add(
        f"p6_scheme13_{compound}", f"Scheme 13, {compound}", "literature_example", E56,
        [part("substrate", "reactant", f"terminal-alkynyl 2,3-allenol {compound}", E56),
         part("pdoac2", "catalyst", "Pd(OAc)2", E56, amounts=[fld("catalyst_loading", q(10, "mol%"), E56)]),
         part("libr", "reagent", "LiBr", E56, name="LiBr"),
         part("cuoac2", "reagent", "Cu(OAc)2", E56),
         part("k2co3", "reagent", "K2CO3", E56, name="potassium carbonate"),
         part("oxygen", "reagent", "O2", E56, name="oxygen"),
         part("acetonitrile", "solvent", "CH3CN", E56, name="acetonitrile"),
         part("product", "product", f"intramolecular domino product {product}", E56)],
        [fld("temperature", temp, E56), fld("time", None, E56)],
        [fld("reported_yield", q(yield_value, "%"), E56, ["product"]), fld("yield_measurement_basis", None, E56, ["product"])],
        unresolved=["LiBr, Cu(OAc)2, K2CO3, O2, and substrate amounts are not reported.", "Time, scale, workup, purification, and yield basis are not reported.", "The complex depicted structures require chemical review."])

add(
    "p6_scheme14_domino_mechanism", "Scheme 14", "mechanism", E56,
    [part("compound21a", "reactant", "2,3-allenol 21a", E56),
     part("pdii", "catalyst", "Pd(II)", E56),
     part("bromide", "reagent", "Br-", E56),
     part("intermediate23a", "unspecified_agent", "pi-allylpalladium intermediate 23a", E56),
     part("product22a", "product", "five-membered-ring product 22a", E56)],
    [], [],
    notes=["Proposed sequence: trans bromopalladation forms 23a, followed by intramolecular cyclization and O-nucleophilic attack on the pi-allylpalladium unit."],
    unresolved=["This is a proposed pathway, not a separately isolated experiment."])

add(
    "p6_eq11_ru_carbonylation", "Eq. 11", "general_scheme", E56,
    [part("allenol", "reactant", "generic 2,3-allenol", E56),
     part("ru3co12", "catalyst", "Ru3(CO)12", E56, amounts=[fld("catalyst_loading", q(1, "mol%"), E56)]),
     part("triethylamine", "reagent", "NEt3", E56, name="triethylamine"),
     part("co", "reagent", "CO", E56, name="carbon monoxide"),
     part("dioxane", "solvent", "dioxane", E56, name="1,4-dioxane"),
     part("product", "product", "generic 2(5H)-furanone", E56)],
    [fld("CO_pressure_as_reported", "1.01 MPa", E56), fld("temperature", q(100, "°C"), E56), fld("time", None, E56)],
    [fld("reported_yield", rng(85, 99, "%", "85%-99%"), E56, ["product"]), fld("yield_measurement_basis", None, E56, ["product"])],
    notes=["Both the hydroxyl group and allene unit are described as participating in the cyclic carbonylation."],
    unresolved=["Generic substituents, reactant/base quantities, time, scale, workup, purification, and yield basis are not reported."])


# Page 6: vanadium aldol-like addition, its proposed cycle, and oxidative cyclizations.
add(
    "p6_scheme15_vanadium_aldehyde_addition", "Scheme 15 transformation", "general_scheme", E[6],
    [part("compound24", "reactant", "generic 2,3-allenol 24", E[6]),
     part("aldehyde", "reactant", "generic aldehyde R1CHO", E[6]),
     part("vanadium", "catalyst", "VO(OSiPh3)3", E[6], amounts=[fld("catalyst_loading", q(5, "mol%"), E[6])]),
     part("dichloromethane", "solvent", "CH2Cl2", E[6], name="dichloromethane"),
     part("product25", "product", "aldol-like addition product 25", E[6]),
     part("product26", "product", "allenol isomerization product 26", E[6])],
    [fld("temperature", "r.t.", E[6]), fld("time", None, E[6])],
    [fld("relative_product_amount_25", "major", E[6], ["product25"]),
     fld("relative_product_amount_26", "minor", E[6], ["product26"]),
     fld("reported_yield", None, E[6], ["product25", "product26"])],
    unresolved=["Generic substituents, reactant quantities, time, scale, workup, purification, and numerical yields are not reported."])

add(
    "p6_scheme15_vanadium_cycle", "Scheme 15 mechanism", "mechanism", E[6],
    [part("compound24", "reactant", "generic 2,3-allenol 24", E[6]),
     part("aldehyde", "reactant", "generic aldehyde", E[6]),
     part("vanadium", "catalyst", "vanadium siloxide complex", E[6]),
     part("product25", "product", "aldol-like product 25", E[6]),
     part("product26", "product", "isomerization product 26", E[6])],
    [], [],
    notes=["Proposed cycle: ligand substitution gives 27, rearrangement gives 28, protonation of 28 gives 26, or aldehyde addition gives 29 followed by protonation to 25 and catalyst regeneration."],
    unresolved=["This is a proposed catalytic cycle, not a separately reported experiment."])

add(
    "p6_scheme16_compound30", "Scheme 16, compound 30", "literature_example", E[6],
    [part("compound30", "reactant", "allyl-substituted 2,3-allenol 30", E[6]),
     part("tbuooh", "reagent", "t-BuOOH", E[6], name="tert-butyl hydroperoxide"),
     part("voacac2", "catalyst", "VO(acac)2", E[6]),
     part("benzene", "solvent", "PhH", E[6], name="benzene"),
     part("product32", "product", "cyclopentenone 32", E[6])],
    [fld("temperature", rng(20, 50, "°C", "20-50 °C"), E[6]), fld("time", None, E[6])],
    [fld("reported_yield", q(45, "%"), E[6], ["product32"]), fld("yield_measurement_basis", None, E[6], ["product32"])],
    unresolved=["Reagent/catalyst amounts, time, scale, workup, purification, and yield basis are not reported."])

add(
    "p6_scheme16_compound31", "Scheme 16, compound 31", "literature_example", E[6],
    [part("compound31", "reactant", "allyl-substituted 2,3-allenol 31", E[6]),
     part("tbuooh", "reagent", "t-BuOOH", E[6], name="tert-butyl hydroperoxide"),
     part("voacac2", "catalyst", "VO(acac)2", E[6]),
     part("dichloromethane", "solvent", "CH2Cl2", E[6], name="dichloromethane"),
     part("product33", "product", "cyclopentenone 33", E[6]),
     part("epoxide_byproduct", "product", "depicted epoxidized allenol byproduct", E[6])],
    missing_conditions(E[6]),
    [fld("reported_yield_product_33", q(60, "%"), E[6], ["product33"]),
     fld("reported_yield_epoxide_byproduct", q(20, "%"), E[6], ["epoxide_byproduct"]),
     fld("yield_measurement_basis", None, E[6], ["product33", "epoxide_byproduct"])],
    unresolved=["Reagent/catalyst amounts, time, temperature, scale, workup, purification, and yield basis are not reported.", "The byproduct structure requires chemical review."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
