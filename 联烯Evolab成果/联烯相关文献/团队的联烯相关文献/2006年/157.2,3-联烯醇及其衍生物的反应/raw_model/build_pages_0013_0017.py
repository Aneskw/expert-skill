#!/usr/bin/env python3
"""Build evidence-linked machine records for review-PDF pages 13--17."""

import json
from pathlib import Path


DOC = "doc_27796c91f0b5e453"
OUT = Path(__file__).with_name("pages_0013_0017_records.json")
E = {p: [f"{DOC}:page{p}:text", f"{DOC}:page{p}:image"] for p in range(12, 18)}


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
    "THF": "C1CCOC1",
    "dichloromethane": "ClCCl",
    "methanol": "CO",
    "acetone": "CC(C)=O",
    "triethylamine": "CCN(CC)CC",
    "lithium bromide": "[Li+].[Br-]",
    "lithium chloride": "[Li+].[Cl-]",
    "lithium iodide": "[Li+].[I-]",
    "acetic acid": "CC(=O)O",
    "hydroquinone": "Oc1ccc(O)cc1",
    "titanium tetrachloride": "Cl[Ti](Cl)(Cl)Cl",
    "lithium aluminum hydride": "[Li+].[AlH4-]",
    "methanesulfonyl chloride": "CS(=O)(=O)Cl",
    "toluene": "Cc1ccccc1",
    "oxygen": "O=O",
    "acrolein": "C=CC=O",
    "triphenylphosphine": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "diisopropylethylamine": "CCN(C(C)C)C(C)C",
    "benzonitrile": "N#Cc1ccccc1",
    "p-toluenesulfonic acid": "Cc1ccc(S(=O)(=O)O)cc1",
    "carbon monoxide": "[C-]#[O+]",
    "diphenylphosphinyl chloride": "O=P(Cl)(c1ccccc1)c1ccccc1",
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


COMMON = [
    "The review does not report reaction scale, workup, purification, or yield measurement basis for this cited chemistry.",
    "Depicted substrate/product connectivity and stereochemistry require chemical review.",
]


# Page 13: Pd(0) reactions of allenol derivatives (Schemes 44--49).
e = ev(12, 13)
add(
    "p13_scheme44_malonate_asymmetric_allenylation", "Scheme 44, malonate branch", "general_scheme", e,
    [part("compound101", "reactant", "generic 2,3-allenol acetate 101", e),
     part("malonate", "reactant", "generic substituted dialkyl malonate", e),
     part("pd2dba3", "catalyst", "Pd2(dba)3·CHCl3", e, amounts=[fld("catalyst_loading", q(2.5, "mol%"), e)]),
     part("ligand", "reagent", "(S,S)-L", e, amounts=[fld("reported_loading", q(7.5, "mol%"), e)]),
     part("thacl", "reagent", "THACl", e, amounts=[fld("reported_loading", q(5, "mol%"), e)]),
     part("lihm_ds", "reagent", "LiHMDS", e, amounts=[fld("equivalents", q(1.1, "equiv"), e)]),
     part("thf", "solvent", "THF", e, name="THF"),
     part("product", "product", "generic chiral substituted allene", e)],
    [fld("temperature", "r.t.", e), fld("time", rng(18, 24, "h", "18-24 h"), e)],
    [fld("reported_yield", rng(63, 97, "%", "63%-97%"), e, ["product"]),
     fld("product_ee", rng(86, 91, "%", "86%-91% ee"), e, ["product"]),
     fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=COMMON + ["Generic R groups and malonate substituents prevent complete structure assignment."])

add(
    "p13_scheme44_secondary_amine_allenylation", "Scheme 44, secondary-amine branch", "general_scheme", e,
    [part("compound101", "reactant", "generic 2,3-allenol acetate 101", e),
     part("secondary_amine", "reactant", "generic secondary amine R2R3NH", e),
     part("pd2dba3", "catalyst", "Pd2(dba)3·CHCl3", e, amounts=[fld("catalyst_loading", q(2.5, "mol%"), e)]),
     part("ligand", "reagent", "(S,S)-L", e, amounts=[fld("reported_loading", q(7.5, "mol%"), e)]),
     part("thacl", "reagent", "THACl", e, amounts=[fld("reported_loading", q(5, "mol%"), e)]),
     part("base", "reagent", "unspecified base", e),
     part("thf", "solvent", "THF", e, name="THF"),
     part("product", "product", "generic chiral 2,3-allenamine", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", None, e, ["product"])],
    unresolved=["The base identity, time, temperature, yield, quantities, scale, workup, and purification are not reported.",
                "Generic R groups and stereochemistry prevent complete structure assignment."])

e = E[13]
add(
    "p13_scheme45_grignard_c7h15", "Scheme 45, Grignard example", "literature_example", e,
    [part("allenyl_phosphate", "reactant", "depicted 2,3-allenol phosphate derivative", e),
     part("grignard", "reactant", "C7H15MgBr", e),
     part("pd", "catalyst", "Pd(PPh3)4", e),
     part("product", "product", "depicted C7H15-substituted 1,3-diene", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", q(80, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=COMMON + ["Catalyst loading, solvent, time, temperature, and reactant quantities are not reported."])

add(
    "p13_scheme45_organozinc_scope", "Scheme 45, organozinc scope", "general_scheme", e,
    [part("allenol_derivative", "reactant", "generic cyclic 2,3-allenol derivative", e),
     part("organozinc", "reactant", "RZnCl", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[fld("catalyst_loading", q(2, "mol%"), e)]),
     part("thf", "solvent", "THF", e, name="THF"),
     part("product", "product", "generic substituted 1,3-diene", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", rng(50, 95, "%", "50%-95%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=["Generic R groups, organozinc identity/amount, time, temperature, scale, workup, purification, and yield basis are not reported."])

add(
    "p13_scheme45_phcu_example", "Scheme 45, PhCu example", "literature_example", e,
    [part("allenol_derivative", "reactant", "depicted methoxy/methyl substituted 2,3-allenol derivative", e),
     part("phcu", "reactant", "PhCu", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[fld("catalyst_loading", q(4, "mol%"), e)]),
     part("thf", "solvent", "THF", e, name="THF"),
     part("product", "product", "depicted phenyl-substituted 1,3-diene", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", q(90, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=COMMON + ["PhCu amount, time, and temperature are not reported."])

add(
    "p13_scheme46_carbonylation_scope", "Scheme 46", "general_scheme", e,
    [part("compound105", "reactant", "generic 2,3-allenol carbonate 105", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[fld("catalyst_loading", q(3, "mol%"), e)]),
     part("methanol", "solvent", "MeOH", e, name="methanol"),
     part("co", "reagent", "CO", e, name="carbon monoxide"),
     part("compound106", "product", "generic carbonylated 1,3-diene 106", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", rng(91, 99, "%", "91%-99%"), e, ["compound106"]), fld("yield_measurement_basis", None, e, ["compound106"])],
    notes=["A PdOMeLn-bound diene is depicted as a non-isolated intermediate before CO insertion."],
    unresolved=["Generic R groups, CO pressure, time, temperature, participant quantities, scale, workup, purification, and yield basis are not reported."])

add(
    "p13_scheme47_allenamine_carbonylation", "Scheme 47", "general_scheme", e,
    [part("compound107", "reactant", "generic 2,3-allenamine 107", e),
     part("pd2dba3", "catalyst", "Pd2(dba)3·CHCl3", e, amounts=[fld("catalyst_loading", q(0.5, "mol%"), e)]),
     part("dppp", "reagent", "dppp", e, amounts=[fld("reported_loading", q(1, "mol%"), e)]),
     part("ptsoh", "reagent", "p-TsOH", e, name="p-toluenesulfonic acid", amounts=[fld("reported_loading", q(1, "mol%"), e)]),
     part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"),
     part("co", "reagent", "CO", e, name="carbon monoxide"),
     part("secondary_amine", "reactant", "generic secondary amine HNR6R7", e),
     part("compound108", "product", "generic carbonylated diene amide 108", e)],
    [fld("temperature", q(75, "°C"), e), fld("time", None, e)],
    [fld("reported_yield", rng(59, 84, "%", "59%-84%"), e, ["compound108"]), fld("yield_measurement_basis", None, e, ["compound108"])],
    unresolved=["Generic R groups, CO pressure, time, reactant quantities, scale, workup, purification, and yield basis are not reported."])

add(
    "p13_scheme48_prepare_bromide109", "Scheme 48, preparation of 109", "literature_example", e,
    [part("allenol", "reactant", "depicted TIPS/difluoro-substituted 2,3-allenol", e),
     part("tea", "reagent", "TEA", e, name="triethylamine"),
     part("mscl", "reagent", "MsCl", e, name="methanesulfonyl chloride"),
     part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"),
     part("libr", "reagent", "LiBr", e, name="lithium bromide", amounts=[fld("equivalents", q(1.0, "equiv"), e)]),
     part("acetone", "solvent", "CH3COCH3", e, name="acetone"),
     part("compound109", "product", "TIPS/difluoro-substituted allenyl bromide 109", e)],
    [],
    [fld("reported_yield", q(93, "%"), e, ["compound109"]), fld("yield_measurement_basis", None, e, ["compound109"])],
    steps=[
        {"step_id": "step1", "participant_ids": ["allenol", "tea", "mscl", "dcm"],
         "conditions": [fld("temperature", q(0, "°C"), e), fld("time", None, e)]},
        {"step_id": "step2", "participant_ids": ["libr", "acetone", "compound109"],
         "conditions": [fld("time", q(5, "h"), e), fld("temperature", None, e)]},
    ],
    unresolved=COMMON + ["TEA/MsCl amounts, step-1 time, step-2 temperature, and reaction scale are not reported."])

add(
    "p13_scheme48_aryl_boron_coupling_scope", "Scheme 48, aryl/boron branch", "general_scheme", e,
    [part("compound109", "reactant", "allenyl bromide 109", e),
     part("coupling_partner", "reactant", "R1X (R1 = Ar; X = Br, I, or B(OH)2)", e),
     part("pd0", "catalyst", "Pd(0)", e),
     part("compound110a", "product", "generic aryl-substituted 1,3-diene 110a", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", None, e, ["compound110a"])],
    unresolved=["Catalyst identity/loading, participant quantities, solvent, time, temperature, and yield are not reported.", "The arrow collectively represents aryl halide and boron-reagent couplings."])

add(
    "p13_scheme48_terminal_alkyne_coupling_scope", "Scheme 48, terminal-alkyne branch", "general_scheme", e,
    [part("compound109", "reactant", "allenyl bromide 109", e),
     part("alkyne", "reactant", "generic terminal alkyne R2CCH", e),
     part("pd0", "catalyst", "Pd(0)", e),
     part("compound110b", "product", "generic alkynyl-substituted 1,3-diene 110b", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", None, e, ["compound110b"])],
    unresolved=["Catalyst identity/loading, participant quantities, solvent, time, temperature, and yield are not reported.", "The terminal-alkyne substituent is generic."])

add(
    "p13_scheme49_carbonylative_rearrangement", "Scheme 49 transformation", "literature_example", e,
    [part("compound111", "reactant", "triflate-substituted 1,3-diene 111", e),
     part("pd", "catalyst", "Pd(PPh3)4", e),
     part("co", "reagent", "CO", e, name="carbon monoxide"),
     part("dipea", "reagent", "i-Pr2NEt", e, name="diisopropylethylamine"),
     part("phcn", "solvent", "PhCN", e, name="benzonitrile"),
     part("compound113", "product", "polycyclic carbonylative-rearrangement product 113", e)],
    [fld("CO_pressure_as_reported", "5.5 MPa CO", e), fld("temperature", rng(65, 110, "°C", "65-110 °C"), e), fld("time", None, e)],
    [fld("reported_yield", q(56, "%"), e, ["compound113"]), fld("yield_measurement_basis", None, e, ["compound113"])],
    unresolved=COMMON + ["Catalyst/base quantities and reaction time are not reported."])

add(
    "p13_scheme49_proposed_pathway", "Scheme 49 pathway", "mechanism", e,
    [part("compound111", "reactant", "triflate-substituted 1,3-diene 111", e),
     part("pd0", "catalyst", "Pd(0)", e),
     part("co", "reagent", "CO", e, name="carbon monoxide"),
     part("intermediate112", "unspecified_agent", "methylene-pi-allylpalladium intermediate 112", e),
     part("compound113", "product", "polycyclic product 113", e)],
    [], [],
    notes=["The depicted proposal includes oxidative addition, CO insertion, cyclization, and a final [3,3] rearrangement."],
    unresolved=["Intermediate 112 and the subsequent palladium species are proposed, not reported as isolated compounds."])


# Page 14: SN2'-type substitution and rearrangements (Schemes 50--55, Eqs. 20--21).
e = E[14]
add(
    "p14_eq20_pdii_bromodiene_scope", "Eq. 20", "general_scheme", e,
    [part("allenyl_acetate", "reactant", "generic 2,3-allenol acetate derivative", e),
     part("pdoac2", "catalyst", "Pd(OAc)2", e),
     part("libr", "reagent", "LiBr", e, name="lithium bromide"),
     part("major", "product", "major 2-bromo-1,3-diene stereoisomer", e),
     part("minor", "product", "minor 2-bromo-1,3-diene stereoisomer", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("relative_amount_major", "major", e, ["major"]), fld("relative_amount_minor", "minor", e, ["minor"]), fld("reported_yield", None, e, ["major", "minor"])],
    unresolved=["Generic R groups, catalyst/reagent quantities, solvent, time, temperature, product ratio, and yield are not reported."])

add(
    "p14_scheme50_bromopalladation_cycle", "Scheme 50", "mechanism", e,
    [part("compound114", "reactant", "generic 2,3-allenol acetate 114", e),
     part("pdoac2", "catalyst", "Pd(OAc)2/Pd(II)", e),
     part("libr", "reagent", "LiBr", e, name="lithium bromide"),
     part("intermediate115", "unspecified_agent", "palladium intermediate 115", e),
     part("compound116", "product", "2-bromo-1,3-diene 116", e)],
    [], [], notes=["Proposed bromopalladation followed by acid-promoted AcOH elimination and Pd(II) regeneration."],
    unresolved=["Intermediate 115 is mechanistic and not reported as an isolated compound."])

for x, reagent_name, hours, minutes, yield_value in [
    ("Cl", "lithium chloride", 1, None, 62),
    ("Br", "lithium bromide", 4, None, 74),
    ("I", "lithium iodide", None, 5, 82),
]:
    time_value = q(hours, "h") if hours is not None else q(minutes, "min")
    add(
        f"p14_eq21_x_{x.lower()}", f"Eq. 21, X = {x}", "literature_example", e,
        [part("substrate", "reactant", "depicted spirocyclic 2,3-allenol acetate", e),
         part("pdoac2", "catalyst", "Pd(OAc)2", e),
         part("lix", "reagent", f"Li{x}", e, name=reagent_name),
         part("product", "product", f"2-{x.lower()}-substituted 1,3-diene", e)],
        [fld("time", time_value, e), fld("temperature", None, e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
        unresolved=COMMON + ["Catalyst/reagent quantities, solvent, and temperature are not reported."])

add(
    "p14_scheme51_117a_scope", "Scheme 51, 117a", "general_scheme", e,
    [part("compound117a", "reactant", "generic aryl-substituted 2,3-allenol 117a", e),
     part("lix", "reagent", "LiX (X = Cl or Br)", e),
     part("hoac", "solvent", "HOAc", e, name="acetic acid"),
     part("hydroquinone", "reagent", "hydroquinone", e, name="hydroquinone", amounts=[fld("reported_loading", q(20, "mol%"), e)]),
     part("product", "product", "generic 2-halo-1,3-diene from 117a", e)],
    [fld("temperature", q(50, "°C"), e), fld("time", None, e)],
    [fld("reported_yield", rng(33, 88, "%", "33%-88%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
    unresolved=["The collective range is not assigned to individual X/substrate cases; time, LiX amount, scale, workup, purification, and yield basis are not reported."])

for x, reagent_name, yield_value in [("Cl", "lithium chloride", 90), ("Br", "lithium bromide", 85)]:
    add(
        f"p14_scheme51_117b_x_{x.lower()}", f"Scheme 51, 117b, X = {x}", "literature_example", e,
        [part("compound117b", "reactant", "diphenyl-substituted 2,3-allenol 117b", e),
         part("lix_hydrate", "reagent", f"Li{x}·H2O", e, amounts=[fld("equivalents", q(3.0, "equiv"), e)]),
         part("hoac", "solvent", "HOAc", e, name="acetic acid"),
         part("hydroquinone", "reagent", "hydroquinone", e, name="hydroquinone", amounts=[fld("reported_loading", q(20, "mol%"), e)]),
         part("product", "product", f"2-{x.lower()}-substituted diene from 117b", e)],
        [fld("temperature", q(50, "°C"), e), fld("time", q(40, "min"), e)],
        [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])],
        unresolved=COMMON + ["Reaction scale and workup/purification are not reported."])

for x, reagent_name, hours, yield_value, ratio_name, ratio_value in [
    ("Cl", "lithium chloride", 3.0, 87, "Z_to_E_ratio", "1.4:1"),
    ("Br", "lithium bromide", 3.5, 73, "E_to_Z_ratio", "5.2:1"),
]:
    add(
        f"p14_scheme51_117c_x_{x.lower()}", f"Scheme 51, 117c, X = {x}", "literature_example", e,
        [part("compound117c", "reactant", "substituted 2,3-allenol 117c", e),
         part("lix_hydrate", "reagent", f"Li{x}·H2O", e),
         part("hoac", "solvent", "HOAc", e, name="acetic acid"),
         part("hydroquinone", "reagent", "hydroquinone", e, name="hydroquinone", amounts=[fld("reported_loading", q(20, "mol%"), e)]),
         part("e_product", "product", f"E 2-{x.lower()}-substituted diene from 117c", e),
         part("z_product", "product", f"Z 2-{x.lower()}-substituted diene from 117c", e)],
        [fld("temperature", q(50, "°C"), e), fld("time", q(hours, "h"), e)],
        [fld("reported_combined_yield", q(yield_value, "%"), e, ["e_product", "z_product"]),
         fld(ratio_name, ratio_value, e, ["e_product", "z_product"]),
         fld("yield_measurement_basis", None, e, ["e_product", "z_product"])],
        unresolved=COMMON + ["LiX hydrate amount and reaction scale are not reported."])

add(
    "p14_scheme52_ticl4_chlorination", "Scheme 52", "literature_example", e,
    [part("compound118", "reactant", "allenyl silyl ether 118", e),
     part("ticl4", "reagent", "TiCl4", e, name="titanium tetrachloride"),
     part("product", "product", "depicted 2-chloro-1,3-diene", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", None, e, ["product"])],
    unresolved=["TiCl4 amount, solvent, time, temperature, scale, workup, purification, and yield are not reported.", "The intermediate titanium complex is mechanistic and not isolated."])

add(
    "p14_scheme53_lialh4_hydrogenation_scope", "Scheme 53", "general_scheme", e,
    [part("compound119", "reactant", "generic 2-trimethylsilyl-substituted 2,3-allenol 119", e),
     part("lialh4", "reagent", "LiAlH4", e, name="lithium aluminum hydride"),
     part("thf", "solvent", "THF", e, name="THF"),
     part("products", "product", "generic 2-hydrogen-substituted 1,3-diene isomers", e)],
    [fld("time", rng(15, 18, "h", "15-18 h"), e), fld("temperature", "r.t.", e)],
    [fld("reported_combined_yield", rng(42, 80, "%", "42%-80%"), e, ["products"]), fld("yield_measurement_basis", None, e, ["products"])],
    unresolved=["Generic R groups, LiAlH4 amount, isomer ratio, scale, workup, purification, and yield basis are not reported."])

add(
    "p14_scheme54_acetate120_rearrangement", "Scheme 54, acetate 120", "literature_example", e,
    [part("compound120", "reactant", "2,3-allenol acetate 120", e),
     part("acid", "reagent", "unspecified acid", e),
     part("product", "product", "depicted rearranged 1,3-diene acetate", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", None, e, ["product"])],
    unresolved=["Acid identity/amount, solvent, time, temperature, scale, workup, purification, and yield are not reported."])

add(
    "p14_scheme54_carbamate121_rearrangement", "Scheme 54, carbamate 121", "general_scheme", e,
    [part("compound121", "reactant", "generic 2,3-allenol carbamate 121", e),
     part("product", "product", "generic rearranged 1,3-diene carbamate", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", None, e, ["product"])],
    unresolved=["Generic R groups and all reaction conditions/outcomes are missing."])

e = ev(14, 15)
add(
    "p15_scheme55_ph2pcl_rearrangement", "Scheme 55, 122 to 124", "mechanism", e,
    [part("compound122", "reactant", "generic 2,3-allenol 122", e),
     part("ph2pcl", "reagent", "Ph2PCl", e),
     part("intermediate123", "unspecified_agent", "proposed cyclic phosphorus intermediate 123", e),
     part("compound124", "product", "generic phosphine-oxide diene 124", e)],
    [], [], notes=["The review proposes initial phosphorus derivatization followed by intramolecular rearrangement through 123."],
    unresolved=["This is a proposed rearrangement pathway; reagent amount, solvent, time, temperature, and yield are not reported."])

add(
    "p15_scheme55_mscl_rearrangement", "Scheme 55, 125 to 127", "mechanism", e,
    [part("compound125", "reactant", "generic 2,3-allenol 125", e),
     part("mscl", "reagent", "CH3SO2Cl", e, name="methanesulfonyl chloride"),
     part("tea", "reagent", "Et3N", e, name="triethylamine"),
     part("dcm", "solvent", "CH2Cl2", e, name="dichloromethane"),
     part("intermediate126", "unspecified_agent", "in-situ 2,3-allenol mesylate 126", e),
     part("compound127", "product", "generic rearranged 1,3-diene 127", e)],
    [fld("temperature", "r.t.", e), fld("time", None, e)], [],
    notes=["The depicted proposal assigns formation of 127 to a [3,3] rearrangement of in-situ derivative 126."],
    unresolved=["Intermediate 126 is not reported as isolated; reagent amounts, time, scale, workup, purification, and yield are not reported."])


# Page 15: tandem rearrangement/cycloaddition and Pd(II) cyclizations.
e = E[15]
for compound, yield_value, dr in [
    ("128a", 43, "100:0"),
    ("128b", 35, "100:0"),
    ("128c", 45, "100:0"),
    ("128d", 48, None),
]:
    outcomes = [fld("reported_yield", q(yield_value, "%"), e, ["product"]), fld("yield_measurement_basis", None, e, ["product"])]
    if dr:
        outcomes.insert(1, fld("diastereomer_ratio", dr, e, ["product"]))
    add(
        f"p15_scheme56_{compound}", f"Scheme 56, {compound}", "literature_example", e,
        [part("substrate", "reactant", f"2,3-allenol {compound}", e),
         part("mscl", "reagent", "CH3SO2Cl", e, name="methanesulfonyl chloride"),
         part("tea", "reagent", "Et3N", e, name="triethylamine"),
         part("toluene", "solvent", "toluene", e, name="toluene"),
         part("product", "product", f"tandem rearrangement/cyclization product from {compound}", e)],
        [fld("temperature", q(190, "°C"), e), fld("operation", "sealed tube", e), fld("time", None, e)],
        outcomes,
        notes=["The source describes in-situ diene formation followed by intramolecular Diels-Alder cyclization."],
        unresolved=COMMON + ["Reagent quantities and reaction time are not reported."])

add(
    "p15_scheme57_carbamate129_cyclization", "Scheme 57 transformation", "literature_example", e,
    [part("compound129", "reactant", "2,3-allenol carbamate 129", e),
     part("libr", "reagent", "LiBr", e, name="lithium bromide"),
     part("pdoac2", "catalyst", "Pd(OAc)2 (catalytic)", e),
     part("cuii", "reagent", "Cu(II)", e),
     part("oxygen", "reagent", "O2", e, name="oxygen"),
     part("compound131", "product", "brominated cyclic carbamate 131", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("reported_yield", q(70, "%"), e, ["compound131"]), fld("yield_measurement_basis", None, e, ["compound131"])],
    unresolved=COMMON + ["LiBr/Pd/Cu/O2 quantities, solvent, time, and temperature are not reported."])

add(
    "p15_scheme57_carbamate129_cycle", "Scheme 57 mechanism", "mechanism", e,
    [part("compound129", "reactant", "2,3-allenol carbamate 129", e),
     part("pdii", "catalyst", "Pd(II)", e),
     part("bromide", "reagent", "Br-", e),
     part("bq", "reagent", "benzoquinone (BQ)", e),
     part("intermediate130", "unspecified_agent", "palladium intermediate 130", e),
     part("compound131", "product", "brominated cyclic carbamate 131", e)],
    [], [], notes=["Proposed bromopalladation, N-nucleophilic ring closure, and acid/BQ-assisted Pd(II) regeneration."],
    unresolved=["Intermediate 130 is proposed and not reported as isolated; the relationship between the top-arrow Cu(II)/O2 conditions and the depicted H+/BQ turnover requires source review."])

add(
    "p15_scheme58_carbamate132_acrolein", "Scheme 58 transformation", "literature_example", e,
    [part("compound132", "reactant", "2,3-allenol carbamate 132", e),
     part("acrolein", "reactant", "acrolein", e, name="acrolein"),
     part("libr", "reagent", "LiBr", e, name="lithium bromide"),
     part("pdoac2", "catalyst", "Pd(OAc)2", e),
     part("thf", "solvent", "THF", e, name="THF"),
     part("compound134", "product", "acrolein-coupled cyclic carbamate 134", e)],
    [fld("temperature", "r.t.", e), fld("time", None, e)],
    [fld("reported_yield", q(74, "%"), e, ["compound134"]), fld("yield_measurement_basis", None, e, ["compound134"])],
    unresolved=COMMON + ["Participant quantities and reaction time are not reported."])

add(
    "p15_scheme58_aminopalladation_cycle", "Scheme 58 mechanism", "mechanism", e,
    [part("compound132", "reactant", "2,3-allenol carbamate 132", e),
     part("acrolein", "reactant", "acrolein", e, name="acrolein"),
     part("pdii", "catalyst", "Pd(II)", e),
     part("intermediate133", "unspecified_agent", "palladium intermediate 133", e),
     part("compound134", "product", "acrolein-coupled cyclic carbamate 134", e)],
    [], [], notes=["Proposed intramolecular aminopalladation, acrolein insertion, and protonolysis."],
    unresolved=["Intermediate 133 and the carbon-palladium insertion sequence are proposed, not isolated experiments."])


# Pages 15--16: Ti/Mg addition and cobalt acylation/cyclization.
e = ev(15, 16)
add(
    "p16_scheme59_ti_mg_quench_scope", "Scheme 59 transformation", "general_scheme", e,
    [part("compound135", "reactant", "generic 2,3-allenol carbonate 135", e),
     part("tioipr4", "reagent", "Ti(O-i-Pr)4", e),
     part("iprmgx", "reagent", "i-PrMgX (coefficient 2 as drawn)", e),
     part("electrophile", "reagent", "E+ (E = RCHO, I2, or H3O+)", e),
     part("compound137", "product", "generic substituted allene 137", e),
     part("compound138", "product", "generic 1,3-diene 138", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("product_relation", "137 and/or 138 depending on electrophilic quench", e, ["compound137", "compound138"]),
     fld("reported_yield", None, e, ["compound137", "compound138"])],
    unresolved=["The source gives no quantitative conditions, product-specific quench mapping, ratio, or yield; generic R/X groups prevent complete structures.",
                "The printed coefficient 2 before i-PrMgX is preserved in the label without inferring an equivalents basis."])

add(
    "p16_scheme59_titanium_intermediate", "Scheme 59 pathway", "mechanism", e,
    [part("compound135", "reactant", "generic 2,3-allenol carbonate 135", e),
     part("titanium_reagent", "reagent", "allyltitanium species from Ti(O-i-Pr)4/i-PrMgX", e),
     part("intermediate136", "unspecified_agent", "titanium intermediate 136", e),
     part("compound137", "product", "generic substituted allene 137", e),
     part("compound138", "product", "generic 1,3-diene 138", e)],
    [], [], notes=["The review proposes oxidative addition to 136 followed by electrophilic quench to 137 and/or 138."],
    unresolved=["Intermediate 136 is mechanistic and not reported as isolated; product selection by electrophile is not specified on the inspected pages."])

add(
    "p16_scheme60_cobalt_acylation_cyclization", "Scheme 60 transformation", "literature_example", e,
    [part("compound139", "reactant", "sulfonamide-substituted allenol derivative 139", e),
     part("acetyl_cobalt", "reagent", "acetylcobalt tetracarbonyl", e),
     part("tea", "reagent", "Et3N", e, name="triethylamine"),
     part("compound141", "product", "trans tetrahydropyrrole 141", e)],
    [fld("time", None, e), fld("temperature", None, e)],
    [fld("product_stereochemistry", "trans (major as described)", e, ["compound141"]), fld("reported_yield", None, e, ["compound141"])],
    unresolved=["Reagent quantities, solvent, time, temperature, product ratio, yield, scale, workup, and purification are not reported.",
                "The OR substituent and complex depicted connectivity require chemical review."])

add(
    "p16_scheme60_pi_allylcobalt_pathway", "Scheme 60 pathway", "mechanism", e,
    [part("compound139", "reactant", "sulfonamide-substituted allenol derivative 139", e),
     part("acetyl_cobalt", "reagent", "acetylcobalt tetracarbonyl", e),
     part("intermediate140", "unspecified_agent", "pi-allylcobalt intermediate 140", e),
     part("compound141", "product", "trans tetrahydropyrrole 141", e)],
    [], [], notes=["The review proposes acyl attack to form pi-allylcobalt intermediate 140 followed by intramolecular nucleophilic substitution."],
    unresolved=["Intermediate 140 is proposed and not reported as an isolated compound."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
