#!/usr/bin/env python3
"""Build evidence-linked review records for PDF pages 19--24."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_0a0328e571461b17"


def ev(page: int, kind: str) -> str:
    return f"{DOC}:page{page}:{kind}"


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": uniq(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=(), targets=()):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "1,2-propadiene": "C=C=C",
    "allene": "C=C=C",
    "1,1-dimethylallene": "C=C=C(C)C",
    "phenylallene": "C=C=Cc1ccccc1",
    "methyl iodide": "CI",
    "hydrogen chloride": "Cl",
    "hexafluorophosphoric acid": "F[P-](F)(F)(F)(F)F.[H+]",
    "tetrafluoroboric acid": "F[B-](F)(F)F.[H+]",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    "dichloromethane": "ClCCl",
    "C6D6": "[2H]c1c([2H])c([2H])c([2H])c([2H])c1[2H]",
    "carbon monoxide": "[C-]#[O+]",
    "4-methyl-1,3-pentadiene": "CC(=CC=C)C",
    "butadiene": "C=CC=C",
    "trimethylphosphine": "CP(C)C",
    "tetramethylsilane": "C[Si](C)(C)C",
}


def participant(entity_id, role, label, evidence, *, smiles=None, amounts=()):
    candidate = smiles if smiles is not None else SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None),
        "smiles": fact(candidate, evidence if candidate else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def mol(entity_id, role, label, evidence, *, smiles=None, equivalents=None):
    amounts = []
    if equivalents is not None:
        amounts.append(field("equivalents", {"number": equivalents, "unit": "equiv"}, evidence))
    return participant(entity_id, role, label, evidence, smiles=smiles, amounts=amounts)


def base_record(rid, kind, evidence, participants, *, conditions=(), outcomes=(), notes=(), unresolved=()):
    condition_list = list(conditions)
    present = {x["name"] for x in condition_list}
    for name in ("temperature", "time", "atmosphere", "workup", "purification"):
        if name not in present:
            condition_list.append(field(name, None))
    product_ids = [p["entity_id"] for p in participants if p["role"] == "product"]
    outcome_list = list(outcomes)
    if not any("yield" in x["name"] for x in outcome_list):
        outcome_list.append(field("reported_yield", None, targets=product_ids))
    if not any(x["name"] == "yield_measurement_basis" for x in outcome_list):
        outcome_list.append(field("yield_measurement_basis", None))
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": condition_list,
        }],
        "outcomes": outcome_list,
        "notes": [fact(text, evidence) for text in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "This review article does not supply a complete primary experimental procedure.",
                "Organometallic connectivity and coordination mode require chemistry review.",
            ],
        },
    }


records = []


def add_lit(rid, evidence, participants, **kwargs):
    records.append(base_record(rid, "literature_example", evidence, participants, **kwargs))


def add_mech(rid, evidence, participants, **kwargs):
    records.append(base_record(rid, "mechanism", evidence, participants, **kwargs))


# Page 19 begins with prose completing Schemes 63 and 64 on page 18. Reuse
# those record IDs and add the now-inspected page-19 image evidence.
dataset = json.loads((RUN / "dataset.json").read_text())
existing = {r["record_id"]: r for r in dataset["experiments"]}
carry_ids = [
    f"{DOC}:scheme63_complex253_allene_to_254_255",
    f"{DOC}:scheme64_complex256_allene_photolysis_mixture",
    f"{DOC}:scheme64_complex257_allene_to_259",
]
for record_id in carry_ids:
    rec = copy.deepcopy(existing[record_id])
    rec["status"] = "candidate"
    rec["evidence_ids"] = uniq(rec["evidence_ids"] + [ev(19, "image")])
    rec["review"]["method"] = "none"
    rec["review"]["reviewer"] = None
    rec["review"]["checked_fields"] = []
    records.append(rec)


e19 = [ev(19, "image"), ev(19, "text")]
add_lit(
    "page19_pcy2_diiron_allene_to_254_analogue", e19,
    [mol("complex", "reactant", "hydrido-bridged PCy2 diiron complex analogous to 253", e19),
     mol("allene", "reactant", "1,2-propadiene", e19),
     mol("product", "product", "vinyl diiron complex analogous to 254 with PCy2 replacing PPh2", e19)],
    unresolved=["The prose-only analogue has no compound number, conditions, yield, or complete primary procedure."],
)
add_lit(
    "scheme65_complex212a_dimethylallene_to_261", e19,
    [mol("complex212a", "reactant", "Rh-Os methylene-bridged complex 212a", e19),
     mol("allene", "reactant", "1,1-dimethylallene", e19),
     mol("product261", "product", "vinyl Rh-Os dinuclear complex 261", e19)],
    conditions=[field("temperature", {"number": -10, "unit": "°C"}, e19)],
)
add_lit(
    "scheme65_complex261_ambient_to_262", e19,
    [mol("complex261", "reactant", "vinyl Rh-Os dinuclear complex 261", e19),
     mol("product262", "product", "4-methyl-1,3-pentadiene", e19)],
    conditions=[field("temperature", "ambient temperature", e19)],
    outcomes=[field("transformation", "decomposition via beta-H elimination", e19, ["product262"])],
)
add_lit(
    "scheme65_complex212b_dimethylallene_to_263", e19,
    [mol("complex212b", "reactant", "Rh-Ru methylene-bridged complex 212b", e19),
     mol("allene", "reactant", "1,1-dimethylallene", e19),
     mol("product263", "product", "carbonyl-migratory-insertion Rh-Ru complex 263", e19)],
    conditions=[field("temperature", {"number": -10, "unit": "°C"}, e19)],
)
add_lit(
    "scheme66_complex264_allene_to_265", e19,
    [mol("complex264", "reactant", "Fe-Pt dinuclear complex 264", e19),
     mol("allene", "reactant", "1,2-propadiene", e19), mol("dcm", "solvent", "dichloromethane", e19),
     mol("product265", "product", "vinyl Pt-Fe dinuclear complex 265", e19)],
    conditions=[field("temperature", {"number": 20, "unit": "°C"}, e19), field("time", "several days", e19)],
    outcomes=[field("reported_yield", "moderate yield", e19, ["product265"]), field("yield_measurement_basis", None)],
)
add_lit(
    "scheme66_complex265_heat_to_266", e19,
    [mol("complex265", "reactant", "vinyl Pt-Fe dinuclear complex 265", e19),
     mol("benzene", "solvent", "benzene", e19), mol("product266", "product", "allyl Fe-Pt complex 266", e19),
     mol("co", "product", "carbon monoxide", e19)],
    conditions=[field("temperature", {"number": 80, "unit": "°C"}, e19)],
    outcomes=[field("reported_yield", "high yield", e19, ["product266"]), field("yield_measurement_basis", None)],
    notes=["Scheme 66 explicitly labels loss of two CO ligands."],
)
add_lit(
    "scheme66_complex264_allene_to_267", e19,
    [mol("complex264", "reactant", "Fe-Pt dinuclear complex 264", e19),
     mol("allene", "reactant", "1,2-propadiene", e19), mol("benzene", "solvent", "benzene", e19),
     mol("product267", "product", "dimetalation product 267", e19)],
    conditions=[field("temperature", {"number": 80, "unit": "°C"}, e19)],
    outcomes=[field("reported_yield", "moderate yield", e19, ["product267"]), field("yield_measurement_basis", None)],
    notes=["The scheme labels the product 267; the adjacent prose appears to call the same dimetalation product 266."],
    unresolved=["Scheme 66 labels the intermediate 267, while adjacent prose gives 266; the scheme label is retained and the conflict is not silently corrected."],
)
add_lit(
    "scheme66_complex267_heat_to_266", e19,
    [mol("complex267", "reactant", "dimetalation product 267", e19), mol("benzene", "solvent", "benzene", e19),
     mol("product266", "product", "allyl Fe-Pt complex 266", e19), mol("co", "product", "carbon monoxide", e19)],
    conditions=[field("temperature", {"number": 80, "unit": "°C"}, e19)],
    outcomes=[field("reported_yield", "high yield", e19, ["product266"]), field("yield_measurement_basis", None)],
    notes=["Scheme 66 explicitly labels loss of two CO ligands."],
)
for suffix, substrate, substitution in [
    ("ph", "phenylallene", "R1=H, R2=Ph"),
    ("me", "1,1-dimethylallene", "R1=R2=Me"),
]:
    add_lit(
        f"scheme66_complex264_{suffix}_allene_to_268", e19,
        [mol("complex264", "reactant", "Fe-Pt dinuclear complex 264", e19),
         mol("allene", "reactant", substrate, e19), mol("benzene", "solvent", "benzene", e19),
         mol("product268", "product", f"allyl Fe-Pt complex 268 ({substitution})", e19),
         mol("co", "product", "carbon monoxide", e19)],
        conditions=[field("temperature", {"number": 80, "unit": "°C"}, e19)],
        notes=["Scheme 66 explicitly labels loss of two CO ligands."],
    )


# Page 20, Schemes 67--70 and literature examples described in the prose.
e20 = [ev(20, "image"), ev(20, "text")]
add_lit(
    "scheme67_complex269_heat_to_271", e20,
    [mol("complex269", "reactant", "iridium vinyl complex 269", e20), mol("c6d6", "solvent", "C6D6", e20),
     mol("product271", "product", "eta3-allyl iridium complex 271", e20)],
    conditions=[field("temperature", {"number": 90, "unit": "°C"}, e20), field("time", {"number": 8, "unit": "h"}, e20)],
    outcomes=[field("reaction_rate", "slow isomerization", e20, ["product271"])],
)
add_mech(
    "scheme67_proposed_pathway_via_270", e20,
    [mol("complex269", "reactant", "iridium vinyl complex 269", e20),
     mol("intermediate270", "product", "hydrido-allene iridium intermediate 270", e20),
     mol("product271", "product", "eta3-allyl iridium complex 271", e20)],
    outcomes=[field("mechanistic_status", "suggested beta-H elimination followed by migratory insertion", e20, ["intermediate270", "product271"])],
    unresolved=["Intermediate 270 is proposed and is not stated to be isolated."],
)
for suffix, ligand in [("a", "CO"), ("b", "PPh3")]:
    add_lit(
        f"scheme67_complex272{suffix}_lithiobutene_to_274{suffix}", e20,
        [mol("complex272", "reactant", f"rhodium complex 272{suffix} (L={ligand})", e20),
         mol("lithio", "reagent", "trans-2-lithio-2-butene", e20),
         mol("product274", "product", f"allyl rhodium complex 274{suffix}", e20)],
        outcomes=[field("expected_vinyl_intermediate_273", "could not be isolated", e20, ["product274"])],
    )
add_lit(
    "page20_tpprimew_vinyl_family_to_allyl", e20,
    [mol("vinyl", "reactant", "Tp'W(CO)2(eta2-H2C=CCH2R) vinyl complex family (R=H, Pr, Ph, CH2Ph)", e20),
     mol("product", "product", "Tp'W(CO)2(eta3-H2CCHCHR) allyl complex family", e20)],
    conditions=[field("temperature", "room temperature or heated in toluene", e20)],
    unresolved=["The generic prose does not map each R group to a unique temperature, time, or yield."],
)
add_lit(
    "page20_tpprimewh_alkyne_family_to_allyl", e20,
    [mol("hydride", "reactant", "Tp'WH(CO)3", e20),
     mol("alkyne", "reactant", "MeC≡CR (R=Me or SiMe3)", e20),
     mol("product", "product", "Tp'W(CO)2(eta3-H2CCHCHR) allyl complex family", e20)],
    conditions=[field("operation", "photochemically induced insertion", e20)],
    unresolved=["The two alkyne variants share a prose summary without variant-specific conditions or yields."],
)
add_lit(
    "page20_cpprimewh_alkyne_family_to_allyl", e20,
    [mol("hydride", "reactant", "Cp'WH(CO)3 (Cp'=C5H5 or C5Me5)", e20),
     mol("alkyne", "reactant", "MeC≡CR (R=H or Me)", e20),
     mol("product", "product", "Cp'W(CO)2(eta3-H2CCHCHR) allyl complex family", e20)],
    unresolved=["The Cp'/R family matrix and individual conditions are not resolved in the review."],
)
add_lit(
    "scheme68_complex275_mei_to_279", e20,
    [mol("complex275", "reactant", "iridium vinylidene complex 275", e20),
     mol("mei", "reagent", "methyl iodide", e20), mol("product279", "product", "eta3-allyl iridium complex 279", e20)],
    conditions=[field("temperature", "room temperature", e20)],
)
add_mech(
    "scheme68_pathway_intermediates276_278", e20,
    [mol("complex275", "reactant", "iridium vinylidene complex 275", e20), mol("mei", "reagent", "methyl iodide", e20),
     mol("intermediate276", "product", "methylated vinylidene complex 276", e20),
     mol("intermediate277", "product", "vinyl complex 277", e20),
     mol("intermediate278", "product", "hydrido-allene complex 278", e20),
     mol("product279", "product", "eta3-allyl iridium complex 279", e20)],
    conditions=[field("temperature_stage_1", {"number": -30, "unit": "°C"}, e20), field("temperature_stage_2", "room temperature", e20)],
    outcomes=[field("observation_of_277", "observed spectroscopically", e20, ["intermediate277"]),
              field("mechanistic_status", "proposed sequence 276 to 277 to 278 to 279", e20, ["intermediate276", "intermediate277", "intermediate278", "product279"])],
    unresolved=["The source proposes the sequence; it does not state that every intermediate was isolated."],
)
add_lit(
    "scheme69_complex280_hbf4_to_281", e20,
    [mol("complex280", "reactant", "osmium alkyne complex 280", e20),
     mol("hbf4", "reagent", "tetrafluoroboric acid", e20), mol("product281", "product", "allyl osmium complex 281", e20)],
)
add_mech(
    "scheme69_deuterium_supported_pathway282_285", e20,
    [mol("complex280", "reactant", "osmium alkyne complex 280", e20),
     mol("intermediates", "product", "proposed osmium intermediates 282-285", e20),
     mol("product281", "product", "allyl osmium complex 281", e20)],
    outcomes=[field("mechanistic_status", "pathway suggested by a deuterium-labeling experiment", e20, ["intermediates", "product281"])],
    unresolved=["Intermediates 282-285 are mechanistic structures; isolation is not stated."],
)
add_lit(
    "scheme70_complex286_hpf6_to_126", e20,
    [mol("complex286", "reactant", "rhodium alkyne complex 286", e20),
     mol("hpf6", "reagent", "hexafluorophosphoric acid", e20), mol("product126", "product", "eta3-allyl rhodium complex 126", e20)],
)
add_mech(
    "scheme70_proposed_pathway287_290", e20,
    [mol("complex286", "reactant", "rhodium alkyne complex 286", e20),
     mol("intermediates", "product", "proposed rhodium intermediates 287-290", e20),
     mol("product126", "product", "eta3-allyl rhodium complex 126", e20)],
    outcomes=[field("mechanistic_status", "proposed protonation, insertion, allene rearrangement, and insertion sequence", e20, ["intermediates", "product126"])],
    unresolved=["Intermediates 287-290 are proposed; isolation is not stated."],
)


# Scheme 71 is described on page 20 and drawn on page 21.
e2021 = [ev(20, "image"), ev(20, "text"), ev(21, "image"), ev(21, "text")]
add_lit(
    "scheme71_complex291_hydride_to_292_family", e2021,
    [mol("complex291", "reactant", "[CpMo(P(OMe)3)2(eta2-MeC≡CR)]BF4 family 291 (R=Me, Et, Pr)", e2021),
     mol("hydride", "reagent", "hydride donor H- (NaBH4 or K[BHBu3])", e2021),
     mol("product292", "product", "allyl molybdenum complex family 292", e2021)],
    unresolved=["The family arrow does not uniquely map each R group and hydride donor to separate conditions or yields."],
)
add_mech(
    "scheme71_proposed_pathway293_295", e2021,
    [mol("complex291", "reactant", "cationic molybdenum alkyne complex 291", e2021),
     mol("intermediates", "product", "hydrido-alkyne, vinyl, and hydrido-allene intermediates 293-295", e2021),
     mol("product292", "product", "allyl molybdenum complex 292", e2021)],
    outcomes=[field("mechanistic_status", "key proposed intermediates for formation of 292", e2021, ["intermediates", "product292"])],
    unresolved=["Intermediates 293-295 are assigned mechanistically; isolation is not stated."],
)
add_lit(
    "scheme71_complex296_hydride_to_297", e2021,
    [mol("complex296", "reactant", "cationic molybdenum alkyne complex 296", e2021),
     mol("hydride", "reagent", "hydride donor H-", e2021), mol("product297", "product", "eta3-allyl molybdenum complex 297", e2021)],
)
add_lit(
    "page20_tpprimew_alkyne_libh3et_to_allyl", e2021,
    [mol("complex", "reactant", "Tp'W(CO)2(eta2-RC≡CMe) complex family (R=Me or Ph)", e2021),
     mol("libhet3", "reagent", "LiBHEt3", e2021),
     mol("product", "product", "Tp'W(CO)2(eta3-H2CCHCHR) allyl complex family", e2021)],
    unresolved=["The R=Me/Ph variants share a prose summary without individual conditions or yields."],
)


# Pages 21--23, Schemes 72--78.
e21 = [ev(21, "image"), ev(21, "text")]
for suffix, reagent, product, substitution in [
    ("hcl", "hydrogen chloride", "coupled iridium product 299", "R=H, X=Cl"),
    ("mei", "methyl iodide", "coupled iridium product 300", "R=Me, X=I"),
]:
    add_lit(
        f"scheme72_complex298_{suffix}_to_{product.split()[-1]}", e21,
        [mol("complex298", "reactant", "iridium acetylide complex 298", e21),
         mol("rx", "reagent", reagent, e21), mol("product", "product", f"{product} ({substitution})", e21)],
    )
add_mech(
    "scheme72_proposed_pathway301_303", e21,
    [mol("complex298", "reactant", "iridium acetylide complex 298", e21),
     mol("rx", "reagent", "RX (HCl or MeI)", e21),
     mol("intermediates", "product", "proposed iridium intermediates 301-303", e21),
     mol("products", "product", "coupled products 299 and 300", e21)],
    outcomes=[field("mechanistic_status", "proposed pathway involving hydrido-allene complex 303", e21, ["intermediates", "products"])],
    unresolved=["Intermediates 301-303 are proposed and are not independent experimental batches."],
)

e2122 = [ev(21, "image"), ev(21, "text"), ev(22, "image"), ev(22, "text")]
add_lit(
    "scheme73_complex304_hcl_to_305_306_307", e2122,
    [mol("complex304", "reactant", "iridium acetylide complex 304", e2122),
     mol("hcl", "reagent", "hydrogen chloride", e2122),
     mol("product305", "product", "iridium dichloride complex 305", e2122),
     mol("product306", "product", "organic compound 306", e2122),
     mol("product307", "product", "organic compound 307", e2122)],
    outcomes=[field("reported_products", "complex 305 and organic compounds 306 and 307", e2122, ["product305", "product306", "product307"])],
)
add_mech(
    "scheme73_deuterium_supported_pathway308_311", e2122,
    [mol("complex304", "reactant", "iridium acetylide complex 304", e2122),
     mol("hcl", "reagent", "hydrogen chloride", e2122),
     mol("intermediates", "product", "proposed iridium intermediates 308-311", e2122),
     mol("products", "product", "products 305-307", e2122)],
    outcomes=[field("mechanistic_status", "allene-insertion pathway suggested by deuterium labeling", e2122, ["intermediates", "products"])],
    unresolved=["Intermediates 308-311 belong to the proposed pathway and are not presented as separate isolated experiments."],
)
add_lit(
    "scheme74_complex312_alkyne_family_to_313_314", e2122,
    [mol("complex312", "reactant", "bimetallic Mn-Mn complex 312", e2122),
     mol("alkyne", "reactant", "alkyne family MeC≡CH, MeC≡CMe, EtC≡CH, or MeC≡CPh", e2122),
     mol("product313", "product", "vinyl bimetallic complex 313", e2122),
     mol("product314a", "product", "eta3-allyl bimetallic complex 314a", e2122),
     mol("product314b", "product", "eta3-allyl bimetallic complex 314b", e2122)],
    outcomes=[field("product_mixture", "mixture of vinyl and eta3-allyl complexes", e2122, ["product313", "product314a", "product314b"])],
    unresolved=["The review does not map each alkyne variant to a separate product ratio, condition set, or yield."],
)
add_lit(
    "page21_complex200b_alkyne_family_to_201_analogues", e2122,
    [mol("complex200b", "reactant", "Cp(CO)2Mo(mu-PPh2)(mu-H)Mn(CO)4 complex 200b", e2122),
     mol("alkyne", "reactant", "MeC≡CH, MeC≡CMe, or EtC≡CH", e2122),
     mol("product", "product", "eta3-allyl complexes analogous to 201c-d", e2122)],
    unresolved=["The prose-only family omits compound numbers for products, individual conditions, and yields."],
)
add_lit(
    "scheme75_complex185_heat_to_315", e2122,
    [mol("complex185", "reactant", "allyl tantalum complex 185", e2122),
     mol("product315", "product", "hydrido-alkyne tantalum complex 315", e2122)],
    conditions=[field("temperature", {"number": 60, "unit": "°C"}, e2122), field("time", {"number": 3, "unit": "d"}, e2122)],
)
add_mech(
    "scheme75_proposed_pathway316_318", e2122,
    [mol("complex185", "reactant", "allyl tantalum complex 185", e2122),
     mol("intermediates", "product", "allene/hydride and vinyl tantalum intermediates 316-318", e2122),
     mol("product315", "product", "hydrido-alkyne tantalum complex 315", e2122)],
    outcomes=[field("mechanistic_status", "suggested deinsertion/insertion/beta-H-elimination pathway", e2122, ["intermediates", "product315"])],
    unresolved=["Intermediates 316-318 are proposed; isolation is not stated."],
)
add_lit(
    "scheme75_complex184_butadiene_to_320", e2122,
    [mol("complex184", "reactant", "Cp*2TaH3 complex 184", e2122),
     mol("butadiene", "reactant", "butadiene", e2122, equivalents=2),
     mol("product320", "product", "hydrido-alkyne tantalum complex 320", e2122)],
    conditions=[field("temperature", {"number": 80, "unit": "°C"}, e2122), field("time", "prolonged warming", e2122)],
    outcomes=[field("reported_yield", "high yield", e2122, ["product320"]), field("yield_measurement_basis", None)],
    notes=["The review says several complexes can form depending on conditions; prolonged warming favors 320 in high yield."],
)
add_mech(
    "scheme75_proposed_pathway319_321_to_320", e2122,
    [mol("complex184", "reactant", "Cp*2TaH3 complex 184", e2122), mol("butadiene", "reactant", "butadiene", e2122),
     mol("intermediate319", "product", "tantalum allene complex 319", e2122),
     mol("intermediate321", "product", "vinyl tantalum intermediate 321", e2122),
     mol("product320", "product", "hydrido-alkyne tantalum complex 320", e2122)],
    outcomes=[field("mechanistic_status", "319 is reported as an intermediate; formation of 320 through 321 is considered likely", e2122,
                    ["intermediate319", "intermediate321", "product320"])],
    unresolved=["The exact condition-dependent distribution of the several complexes is not reported in the review."],
)
add_lit(
    "scheme76_complex322_heat_to_323", e2122,
    [mol("complex322", "reactant", "allyl titanium complex 322", e2122),
     mol("product323", "product", "vinyl titanium complex 323", e2122)],
    conditions=[field("temperature", "heat", e2122)],
)
add_mech(
    "scheme76_nmr_pathway324_326", e2122,
    [mol("complex322", "reactant", "allyl titanium complex 322", e2122),
     mol("intermediates", "product", "allene, vinyl, and alkyne titanium intermediates 324-326", e2122),
     mol("product323", "product", "vinyl titanium complex 323", e2122)],
    outcomes=[field("observation_method", "intermediates monitored by NMR", e2122, ["intermediates"]),
              field("mechanistic_status", "isomerization pathway through 324-326", e2122, ["intermediates", "product323"])],
)

e2123 = [ev(21, "image"), ev(21, "text"), ev(23, "image"), ev(23, "text")]
add_lit(
    "scheme77_complex327_alkyne_family_to_328", e2123,
    [mol("complex327", "reactant", "ReH4(mq)(PPh3)2 complex 327", e2123),
     mol("alkyne", "reactant", "1-phenyl-1-butyne or 2-phenyl-2-butyne as drawn", e2123),
     mol("hpf6", "reagent", "hexafluorophosphoric acid", e2123),
     mol("product328", "product", "rhenium carbyne complex 328", e2123)],
    unresolved=["The scheme presents alternative alkyne substrates without variant-specific conditions or yields."],
)
add_lit(
    "scheme77_complex327_alkyne_family_to_329", e2123,
    [mol("complex327", "reactant", "ReH4(mq)(PPh3)2 complex 327", e2123),
     mol("alkyne", "reactant", "internal or terminal methyl-substituted alkyne drawn for complex 329", e2123),
     mol("hpf6", "reagent", "hexafluorophosphoric acid", e2123),
     mol("product329", "product", "rhenium carbyne complex 329", e2123)],
    unresolved=["The two alternative substrate drawings are not expanded into separate experiments because variant-specific outcomes are absent."],
)
add_mech(
    "scheme77_proposed_isomerization_pathway330_334", e2123,
    [mol("complex327", "reactant", "rhenium hydride complex 327", e2123),
     mol("alkyne", "reactant", "internal alkyne", e2123),
     mol("intermediates", "product", "proposed rhenium intermediates 330-334", e2123),
     mol("product328", "product", "rhenium carbyne complex 328", e2123)],
    outcomes=[field("mechanistic_status", "general proposed internal-to-terminal alkyne isomerization through allene/vinyl intermediates", e2123,
                    ["intermediates", "product328"])],
    unresolved=["The pathway is mechanistic and does not specify independent isolation of 330-334."],
)
add_lit(
    "scheme78_complex335_sime4_to_338", e2123,
    [mol("complex335", "reactant", "tungsten complex 335", e2123),
     mol("sime4", "reactant", "tetramethylsilane", e2123), mol("product338", "product", "allyl tungsten complex 338", e2123)],
    outcomes=[field("transformation", "C-H bond activation", e2123, ["product338"])],
)
add_lit(
    "scheme78_complex335_benzene_to_339", e2123,
    [mol("complex335", "reactant", "tungsten complex 335", e2123),
     mol("benzene", "reactant", "benzene", e2123), mol("product339", "product", "allyl tungsten complex 339", e2123)],
    outcomes=[field("transformation", "C-H bond activation", e2123, ["product339"])],
)
add_lit(
    "scheme78_intermediate336_pme3_to_337", e2123,
    [mol("intermediate336", "reactant", "tungsten allene intermediate 336", e2123),
     mol("pme3", "reagent", "trimethylphosphine", e2123),
     mol("product337", "product", "trapped tungsten allene complex 337", e2123)],
    notes=["The review states that key intermediate 336 can be trapped with PMe3."],
)
add_mech(
    "scheme78_key_intermediate336_and_ts340", e2123,
    [mol("complex335", "reactant", "tungsten complex 335", e2123),
     mol("intermediate336", "product", "key tungsten allene intermediate 336", e2123),
     mol("ts340", "product", "computed C-H-addition transition state 340", e2123)],
    outcomes=[field("study_type", "proposed intermediate plus theoretical transition-state study", e2123, ["intermediate336", "ts340"])],
    unresolved=["Transition state 340 is computational and intermediate 336 is mechanistic; neither is a separate preparative batch."],
)


# Page 23, Schemes 79 and 80.
e2223 = [ev(22, "image"), ev(22, "text"), ev(23, "image"), ev(23, "text")]
add_lit(
    "scheme79_complex341_phenylallene_to_343_family", e2223,
    [mol("complex341", "reactant", "Fischer carbene complex (CO)5M=C(OEt)Ph 341 (M=Cr, Mo, W)", e2223),
     mol("phenylallene", "reactant", "phenylallene", e2223),
     mol("product343a", "product", "trimethylenemethane complex family 343a", e2223),
     mol("product343b", "product", "trimethylenemethane complex family 343b", e2223)],
    outcomes=[field("reported_isolation", "well-defined trimethylenemethane complex 343 was isolated", e2223, ["product343a", "product343b"])],
    unresolved=["The M=Cr/Mo/W family and depicted 343a/343b forms are not mapped to variant-specific conditions or yields."],
)
add_mech(
    "scheme79_proposed_intermediate342", e2223,
    [mol("complex341", "reactant", "Fischer carbene complex 341", e2223),
     mol("phenylallene", "reactant", "phenylallene", e2223),
     mol("intermediate342", "product", "proposed metallacyclic intermediate 342", e2223),
     mol("product343", "product", "trimethylenemethane complex 343", e2223)],
    outcomes=[field("mechanistic_status", "reaction proposed to proceed through intermediate 342", e2223, ["intermediate342", "product343"])],
    unresolved=["Intermediate 342 is proposed and not reported as an independently isolated product."],
)
e23 = [ev(23, "image"), ev(23, "text")]
add_lit(
    "page23_chromium_carbene_functionalized_allene_family", e23,
    [mol("carbene", "reactant", "(CO)5Cr=C(OEt)Ph", e23),
     mol("allene", "reactant", "CH2=C=CHCH2R (R=OH, CO2Et, or CH2OH)", e23),
     mol("product", "product", "functionalized trimethylenemethane chromium complex family", e23),
     mol("byproduct", "product", "enol ether CH2=C(OEt)Ph", e23)],
    outcomes=[field("byproduct_amount", "small amount", e23, ["byproduct"]),
              field("byproduct_origin", "metathesis reaction", e23, ["byproduct"])],
    unresolved=["The three R variants share a prose summary without individual products, conditions, or yields."],
)
add_lit(
    "scheme79_complex344_allene_family_to_345", e23,
    [mol("complex344", "reactant", "iron carbene Fe(CO)4=C(OEt)R family 344 (R=Ph or Me)", e23),
     mol("allene", "reactant", "allene family (R'=H, Ph, or OMe)", e23),
     mol("product345a", "product", "eta4-trimethylenemethane iron complex family 345a", e23),
     mol("product345b", "product", "eta4-trimethylenemethane iron complex family 345b", e23)],
    unresolved=["The R/R' family matrix is not resolved into variant-specific conditions, products, or yields."],
)
add_lit(
    "page23_fe2_methylene_allene_to_tmm_complex", e23,
    [mol("complex", "reactant", "Fe2(CO)8(mu-CH2)", e23), mol("allene", "reactant", "allene", e23),
     mol("product", "product", "(eta4-C(CH2)3)Fe(CO)3 trimethylenemethane complex", e23)],
    unresolved=["The prose-only literature example omits conditions, scale, yield, workup, and purification."],
)
add_lit(
    "scheme79_complex346_allene_to_347", e23,
    [mol("complex346", "reactant", "iridium carbene complex 346", e23), mol("allene", "reactant", "allene", e23),
     mol("product347", "product", "eta4-trimethylenemethane iridium complex 347", e23)],
)
add_lit(
    "scheme80_complex348_excess_allene_to_349", e23,
    [mol("complex348", "reactant", "monomeric titanium oxo complex 348", e23),
     mol("allene", "reactant", "allene", e23), mol("toluene", "solvent", "toluene", e23),
     mol("product349", "product", "oxametallacyclobutane titanium complex 349", e23)],
    conditions=[field("operation", "[2+2] cycloaddition with loss of pyridine", e23)],
    notes=["Scheme 80 labels allene as excess and shows pyridine loss."],
)


# Page 24, Scheme 81. Conclusion, acknowledgments, and references contain no
# additional independent reaction arrows.
e24 = [ev(24, "image"), ev(24, "text")]
add_lit(
    "scheme81_complex350_allene_family_to_351", e24,
    [mol("complex350", "reactant", "(ebthi)Zr=NAr(THF) imidozirconium complex 350 (Ar=2,6-Me2Ph)", e24),
     mol("allene", "reactant", "RHC=C=CHR (R=H, Ph, C2H5, or C3H7)", e24),
     mol("product351", "product", "azametallacycle family 351", e24)],
    conditions=[field("operation", "[2+2] cycloaddition", e24)],
    unresolved=["The four R variants share one family arrow without variant-specific conditions or yields."],
)
add_lit(
    "scheme81_complex350_mixed_allene_to_352a_352b", e24,
    [mol("complex350", "reactant", "(ebthi)Zr=NAr(THF) imidozirconium complex 350 (Ar=2,6-Me2Ph)", e24),
     mol("allene", "reactant", "MeHC=C=CHPh", e24),
     mol("product352a", "product", "azametallacycle regioisomer 352a", e24),
     mol("product352b", "product", "azametallacycle regioisomer 352b", e24)],
    conditions=[field("operation", "[2+2] cycloaddition", e24)],
    outcomes=[field("product_mixture", "regioisomers 352a and 352b", e24, ["product352a", "product352b"])],
)
add_lit(
    "scheme81_complex353_allene_family_to_354", e24,
    [mol("complex353", "reactant", "imido titanium complex 353a or 353b", e24),
     mol("allene", "reactant", "phenylallene or 1-methylallene (R=Ph or Me)", e24),
     mol("product354", "product", "azametallacyclic titanium complex family 354", e24)],
    conditions=[field("operation", "[2+2] cycloaddition", e24)],
    unresolved=["The two catalyst structures and two allene variants share one family arrow without variant-specific conditions or yields."],
)


def ids_for_page(page):
    image_id = ev(page, "image")
    text_id = ev(page, "text")
    return [r["record_id"] for r in records if image_id in r["evidence_ids"] or text_id in r["evidence_ids"]]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 19,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 65", "finding": "Three temperature-defined literature transformations were extracted: 212a to vinyl complex 261, ambient decomposition 261 to diene 262, and 212b to carbonyl-inserted complex 263.", "evidence_ids": [ev(19, "image"), ev(19, "text")]},
                {"region": "left and center prose completing Schemes 63-64", "finding": "Three existing cross-page records were updated with page-19 image evidence; a separate PCy2 diiron analogue was added, while the repeated 200a-to-201a statement remains linked to its existing earlier record and was not duplicated.", "evidence_ids": [ev(19, "image"), ev(19, "text")]},
                {"region": "lower Scheme 66 and adjacent prose", "finding": "Six distinct condition/substrate routes were extracted, including separate 265-to-266 and 267-to-266 heating operations and two substituted-allene routes to 268.", "evidence_ids": [ev(19, "image"), ev(19, "text")]},
            ],
            "record_ids": uniq(ids_for_page(19) + [f"{DOC}:scheme52_complex200a_allene_to_201a"]),
            "unresolved": ["Scheme 66 labels the dimetalation intermediate 267, while adjacent prose appears to label it 266; the scheme label was retained.", "Most literature examples omit scale, atmosphere, workup, purification, and numeric yield."],
        },
        {
            "page": 20,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 67 and section 4.1 prose", "finding": "The observed 269-to-271 isomerization and two 272-to-274 ligand variants were extracted; proposed 270 and nonisolated 273 were not promoted to reported products.", "evidence_ids": [ev(20, "image"), ev(20, "text")]},
                {"region": "lower-left Scheme 68", "finding": "The overall 275/MeI-to-279 reaction was separated from the proposed 276-278 pathway, preserving the spectroscopic observation of 277 and the -30 °C/room-temperature stages.", "evidence_ids": [ev(20, "image"), ev(20, "text")]},
                {"region": "right Schemes 69-70 and surrounding prose", "finding": "Two protonation reactions and their distinct isotope-supported/proposed pathways were extracted; generic Mo/W hydride-donor families continuing into Scheme 71 were retained without speculative expansion.", "evidence_ids": [ev(20, "image"), ev(20, "text"), ev(21, "image")]},
            ],
            "record_ids": ids_for_page(20),
            "unresolved": ["Several family examples do not map ligand/substrate variants to individual conditions or yields; proposed intermediates are not stated to be isolated."],
        },
        {
            "page": 21,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 71", "finding": "Two hydride-addition literature reactions and the 293-295 mechanistic sequence were extracted; the R-group/hydride-donor matrix remains generic.", "evidence_ids": [ev(21, "image"), ev(21, "text"), ev(20, "text")]},
                {"region": "lower Scheme 72", "finding": "HCl and MeI reactions of 298 were split because they produce 299 and 300 under different reagent identities; intermediates 301-303 form a separate mechanism record.", "evidence_ids": [ev(21, "image"), ev(21, "text")]},
                {"region": "middle/right prose introducing Schemes 73-78", "finding": "Cross-page literature reactions and mechanisms were linked to their page-22/page-23 drawings, including Scheme 75's explicit 60 °C for 3 d and Scheme 76's NMR-monitored intermediates.", "evidence_ids": [ev(21, "image"), ev(21, "text"), ev(22, "image"), ev(23, "image")]},
            ],
            "record_ids": ids_for_page(21),
            "unresolved": ["Generic alkyne and ligand families lack variant-specific yields and primary procedures; some intermediates are only mechanistically assigned."],
        },
        {
            "page": 22,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 73", "finding": "The HCl protonation yielding complex 305 plus organic products 306/307 was extracted as one literature experiment; structures 308-311 were classified as a deuterium-supported pathway.", "evidence_ids": [ev(22, "image"), ev(22, "text"), ev(21, "text")]},
                {"region": "middle Schemes 74 and 76", "finding": "The generic alkyne reaction of 312 and the heat-induced 322-to-323 isomerization were extracted; the respective allyl/vinyl and 324-326 pathway details remain separate mechanism information.", "evidence_ids": [ev(22, "image"), ev(22, "text"), ev(21, "text")]},
                {"region": "lower-left Scheme 75", "finding": "The isolated 185-to-315 transformation and 184/butadiene-to-320 high-yield route were separated from proposed intermediates 316-321.", "evidence_ids": [ev(22, "image"), ev(22, "text"), ev(21, "text")]},
                {"region": "lower-right section 5 introduction", "finding": "Review context and broad proposed catalytic roles only; no additional independent experiment was created from this prose.", "evidence_ids": [ev(22, "image"), ev(22, "text")]},
            ],
            "record_ids": ids_for_page(22),
            "unresolved": ["Scheme 74 does not resolve the alkyne family into variant-specific products or yields; many pathway intermediates are not stated to be isolated."],
        },
        {
            "page": 23,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 77 and 78", "finding": "Two rhenium carbyne product families, three tungsten trapping/C-H-activation outcomes, and their distinct proposed/computational pathways were extracted.", "evidence_ids": [ev(23, "image"), ev(23, "text"), ev(21, "text")]},
                {"region": "lower Scheme 79 and adjacent prose", "finding": "Carbene/allene literature families for complexes 341, 344, and 346 plus a prose-only Fe2(CO)8 example were extracted; intermediate 342 is a mechanism record and the small enol-ether byproduct remains product-targeted qualitative data.", "evidence_ids": [ev(23, "image"), ev(23, "text"), ev(22, "text")]},
                {"region": "middle-right Scheme 80", "finding": "The excess-allene [2+2] cycloaddition of oxo complex 348 in toluene to oxametallacyclobutane 349 was extracted with pyridine loss retained as an operation note.", "evidence_ids": [ev(23, "image"), ev(23, "text")]},
            ],
            "record_ids": ids_for_page(23),
            "unresolved": ["Several schemes present unresolved metal/substituent family matrices; most lack scale, time, numeric yield, atmosphere, workup, and purification."],
        },
        {
            "page": 24,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 81 and section 5.2 prose", "finding": "Three imido-metal [2+2] cycloaddition records were extracted: a four-member zirconium substrate family, the mixed-substituent allene giving regioisomers 352a/352b, and the titanium complex/allene family giving 354.", "evidence_ids": [ev(24, "image"), ev(24, "text")]},
                {"region": "lower-left conclusion and outlook", "finding": "Review-level synthesis of product trends and research outlook; no new independent reaction record was created.", "evidence_ids": [ev(24, "image"), ev(24, "text")]},
                {"region": "lower-right acknowledgment and references", "finding": "Funding and bibliography only; no reaction arrow or experimental row is present.", "evidence_ids": [ev(24, "image"), ev(24, "text")]},
            ],
            "record_ids": ids_for_page(24),
            "unresolved": ["Scheme 81 family arrows omit variant-specific conditions and yields; exact organometallic connectivity remains unverified."],
        },
    ],
}


raw_path = RUN / "raw_model" / "records_pages_0019_0024.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage_path = RUN / "coverage" / "pages_0019_0024.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(19, 25)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "submitted_records": len(records),
    "new_record_ids": len(records) - len(carry_ids),
    "updated_existing_records": len(carry_ids),
    "coverage_pages": len(coverage["pages"]),
    "raw": str(raw_path),
}, ensure_ascii=False))
