#!/usr/bin/env python3
"""Build evidence-linked records for doc_0a0328e571461b17, PDF pages 1--6."""

from __future__ import annotations

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
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, *, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None),
        "smiles": fact(smiles, evidence if smiles else ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


SOLVENT_SMILES = {
    "THF": "C1CCOC1",
    "diethyl ether": "CCOCC",
    "benzene": "c1ccccc1",
    "benzonitrile": "N#Cc1ccccc1",
    "methanol": "CO",
    "acetic acid": "CC(=O)O",
    "dichloromethane": "ClCCl",
    "CDCl3": "[2H]C(Cl)(Cl)Cl",
    "chloroform": "ClC(Cl)Cl",
    "toluene": "Cc1ccccc1",
    "acetone": "CC(=O)C",
}

ALLENE_SMILES = {
    "1,2-propadiene": "C=C=C",
    "1-methylallene": "C=C=CC",
    "1,1-dimethylallene": "C=C=C(C)C",
    "3,3-dimethylallene": "C=C=C(C)C",
    "1,3-dimethylallene": "CC=C=CC",
    "tetramethylallene": "CC(C)=C=C(C)C",
    "phenylallene": "C=C=Cc1ccccc1",
    "1,2,6-heptatriene": "C=C=CCCC=C",
}


def solvent(entity_id, name, evidence):
    return participant(entity_id, "solvent", name, evidence, smiles=SOLVENT_SMILES.get(name))


def allene(entity_id, name, evidence, *, equivalents=None):
    amounts = []
    if equivalents is not None:
        amounts.append(field("equivalents", {"number": equivalents, "unit": "equiv"}, evidence))
    return participant(entity_id, "reactant", name, evidence, smiles=ALLENE_SMILES.get(name), amounts=amounts)


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
                "Complex connectivity and coordination mode require chemistry review.",
            ],
        },
    }


records = []


def add_lit(rid, evidence, participants, **kwargs):
    rec = base_record(rid, "literature_example", evidence, participants, **kwargs)
    records.append(rec)
    return rec["record_id"]


def add_mech(rid, evidence, participants, **kwargs):
    rec = base_record(rid, "mechanism", evidence, participants, **kwargs)
    records.append(rec)
    return rec["record_id"]


# Page 2, Scheme 1: cited nickel insertion chemistry.
e2 = [ev(2, "image"), ev(2, "text")]
add_lit(
    "scheme1_complex1_allene_to_2", e2,
    [participant("complex1", "reactant", "sigma-carbamoyl nickel(II) complex 1", e2),
     allene("allene", "1,2-propadiene", e2, equivalents=1),
     solvent("thf", "THF", e2),
     participant("product2", "product", "neutral 2-carbamoyl eta3-allylnickel(II) complex 2", e2)],
    notes=["Scheme 1 literature example attributed to reference 9; THF gives neutral complex 2."],
)
add_lit(
    "scheme1_complex1_allene_to_3", e2,
    [participant("complex1", "reactant", "sigma-carbamoyl nickel(II) complex 1", e2),
     allene("allene", "1,2-propadiene", e2, equivalents=1),
     participant("diethylamine", "reagent", "diethylamine", e2, smiles="CCNCC"),
     solvent("ether", "diethyl ether", e2),
     participant("product3", "product", "cationic 2-carbamoyl eta3-allylnickel(II) complex 3", e2)],
    notes=["Scheme 1 literature example attributed to reference 9; Et2NH/Et2O gives cationic complex 3."],
)
add_lit(
    "scheme1_complex3_allene_to_4", e2,
    [participant("complex3", "reactant", "cationic allylnickel(II) complex 3", e2),
     allene("allene", "1,2-propadiene", e2),
     participant("product4", "product", "neutral further-insertion allylnickel complex 4", e2)],
    notes=["Further insertion shown in Scheme 1 and attributed to reference 9b."],
)


# Page 3, Scheme 2; prose begins on page 2.
e23 = [ev(2, "text"), ev(2, "image"), ev(3, "image"), ev(3, "text")]
scheme2_variants = [
    ("5a", "1,2-propadiene", "dimeric (2-chloro)allylpalladium chloride 5a"),
    ("5b", "1-methylallene", "dimeric allylpalladium chloride 5b"),
    ("5c", "1,1-dimethylallene", "dimeric allylpalladium chloride 5c"),
    ("5d", "tetramethylallene", "dimeric allylpalladium chloride 5d"),
]
for label, substrate, product_label in scheme2_variants:
    add_lit(
        f"scheme2_pdcl2_{label}", e23,
        [participant("pd_complex", "reactant", "PdCl2(PhCN)2", e23),
         allene("allene", substrate, e23), solvent("benzene", "benzene", e23),
         participant("product", "product", product_label, e23)],
        notes=[f"Scheme 2 literature example giving {label}; the review cites references 11/12 as applicable."],
    )
add_lit(
    "scheme2_pdcl2_dienyl_allene_to_5e", e23,
    [participant("pd_complex", "reactant", "PdCl2(PhCN)2", e23),
     participant("allene", "reactant", "CH2=C=CH(CH2)4CH=CH2", e23),
     solvent("benzene", "benzene", e23),
     participant("product", "product", "dimeric allylpalladium complex 5e", e23)],
    notes=["Scheme 2 literature example attributed to reference 13."],
)
add_lit(
    "scheme2_pdcl2_heptatriene_to_5f_5g", e23,
    [participant("pd_complex", "reactant", "PdCl2(PhCN)2", e23),
     allene("allene", "1,2,6-heptatriene", e23), solvent("benzene", "benzene", e23),
     participant("product5f", "product", "polymeric/dimeric allylpalladium complex 5f", e23),
     participant("product5g", "product", "cyclized allylpalladium complex 5g", e23)],
    outcomes=[field("product_mixture", "mixture of 5f and 5g", e23, ["product5f", "product5g"])],
    notes=["Scheme 2 reports a mixture of 5f and 5g and attributes it to reference 13."],
)
add_lit(
    "scheme2_pdbr2_functionalized_allene_to_5h", e23,
    [participant("pd_complex", "reactant", "PdBr2(PhCN)2", e23),
     participant("allene", "reactant", "functionalized allene bearing R = NHTs or OH", e23),
     solvent("benzene", "benzene", e23),
     participant("product", "product", "allylpalladium bromide complex 5h", e23)],
    notes=["One generic Scheme 2 arrow covers the NHTs and OH variants; individual conditions and yields are not supplied."],
    unresolved=["The generic R=NHTs/OH arrow does not resolve separate substrate-specific conditions or outcomes.",
                "Complex connectivity requires chemistry review."],
)


# Page 3, Scheme 3 and proposed intermediate 6d.
add_lit(
    "scheme3_pdcl2_allene_benzene_to_6a", e23,
    [participant("pd_complex", "reactant", "PdCl2(PhCN)2", e23),
     allene("allene", "1,2-propadiene", e23), solvent("benzene", "benzene", e23),
     participant("product", "product", "allylpalladium complex 6a", e23)],
    notes=["The review states that PdCl2(PhCN)2 was introduced as a solid to allene in benzene and 6a was the major product."],
)
add_lit(
    "scheme3_pdcl2_allene_phcn_to_6b", e23,
    [participant("pd_complex", "reactant", "PdCl2(PhCN)2", e23),
     allene("allene", "1,2-propadiene", e23), solvent("phcn", "benzonitrile", e23),
     participant("product", "product", "allylpalladium complex 6b", e23)],
)
add_lit(
    "scheme3_pdcl2_allene_meoh_to_6b_6c", e23,
    [participant("pd_complex", "reactant", "PdCl2(PhCN)2", e23),
     allene("allene", "1,2-propadiene", e23), solvent("meoh", "methanol", e23),
     participant("product6b", "product", "allylpalladium complex 6b", e23),
     participant("product6c", "product", "methoxy-substituted allylpalladium complex 6c", e23)],
    outcomes=[field("isolated_yield_6b", {"number": 30, "unit": "%"}, e23, ["product6b"]),
              field("isolated_yield_6c", {"number": 46, "unit": "%"}, e23, ["product6c"]),
              field("yield_measurement_basis", "isolated", e23)],
)
add_lit(
    "scheme3_na2pdcl4_allene_meoh_to_6b", e23,
    [participant("pd_complex", "reactant", "Na2PdCl4", e23),
     allene("allene", "1,2-propadiene", e23), solvent("meoh", "methanol", e23),
     participant("product", "product", "allylpalladium complex 6b", e23)],
    outcomes=[field("reported_yield_6b", {"number": 88, "unit": "%"}, e23, ["product"]),
              field("yield_measurement_basis", None)],
)
add_lit(
    "scheme3_na2pdcl4_allene_hoac_naoac_to_7", e23,
    [participant("pd_complex", "reactant", "Na2PdCl4", e23),
     allene("allene", "1,2-propadiene", e23), solvent("hoac", "acetic acid", e23),
     participant("naoac", "reagent", "sodium acetate", e23, smiles="CC(=O)[O-].[Na+]"),
     participant("product", "product", "2-acetoxy allylpalladium complex 7", e23)],
)
add_mech(
    "scheme3_proposed_vinyl_intermediate_6d", e23,
    [participant("coordinated_allene", "reactant", "coordinated 1,2-propadiene", e23),
     participant("nucleophile", "reagent", "external nucleophile Nu = Cl or OMe", e23),
     participant("intermediate", "product", "vinyl palladium intermediate 6d", e23)],
    outcomes=[field("mechanistic_status", "proposed intermediate leading to 6a, 6b, and 6c", e23, ["intermediate"])],
    notes=["The review says 6a-6c can be thought of as arising by insertion into Pd-C bonds of 6d."],
    unresolved=["Intermediate 6d is proposed, not independently reported as an isolated experiment."],
)


# Page 3, Scheme 4.
e3 = [ev(2, "text"), ev(3, "image"), ev(3, "text")]
add_lit(
    "scheme4_pdoac2_allene_to_9", e3,
    [participant("pd_oac", "reactant", "Pd(OAc)2", e3), allene("allene", "1,2-propadiene", e3),
     solvent("benzene", "benzene", e3), participant("product", "product", "bis-eta3-allyl dipalladium complex 9", e3)],
    conditions=[field("time", "overnight", e3)],
    outcomes=[field("isolated_yield_9", {"number": 18, "unit": "%"}, e3, ["product"]),
              field("yield_measurement_basis", "isolated after silica-gel chromatography", e3)],
)
add_lit(
    "scheme4_complex8_allene_to_9", e3,
    [participant("complex8", "reactant", "di-mu-acetato-2,2'-bi-eta3-allyldipalladium(II) complex 8", e3),
     allene("allene", "1,2-propadiene", e3), solvent("dcm", "dichloromethane", e3),
     participant("product", "product", "bis-eta3-allyl dipalladium complex 9", e3)],
    outcomes=[field("reported_yield_9", {"number": 94, "unit": "%"}, e3, ["product"]),
              field("yield_measurement_basis", None)],
)


# Page 4, Schemes 5 and 6; their opening prose appears on page 3.
e34 = [ev(3, "text"), ev(3, "image"), ev(4, "image"), ev(4, "text")]
scheme5 = [
    ("a", "R=R1=R2=H"), ("b", "R=Me, R1=R2=H"),
    ("c", "R=R2=H, R1=Me"), ("d", "R=H, R1=R2=Me"),
]
for suffix, substitution in scheme5:
    add_lit(
        f"scheme5_complex10{suffix}_allene_to_11{suffix}", e34,
        [participant("complex10", "reactant", f"dimeric eta3-allylpalladium chloride complex 10{suffix} ({substitution})", e34),
         allene("allene", "1,2-propadiene", e34),
         participant("product", "product", f"double-insertion dimeric allylpalladium complex 11{suffix}", e34)],
        outcomes=[field("insertion_count", "double insertion", e34, ["product"])],
    )

for suffix, substitution in scheme5:
    add_lit(
        f"scheme6_complex12{suffix}_allene_to_13{suffix}_14", e34,
        [participant("complex12", "reactant", f"monomeric eta3-allylpalladium acac complex 12{suffix} ({substitution})", e34),
         allene("allene", "1,2-propadiene", e34),
         participant("product13", "product", f"allylpalladium complex 13{suffix}", e34),
         participant("product14", "product", "bimetallic 2,2'-bis-eta3-allyl complex 14", e34)],
        outcomes=[field("major_product", "mainly product 13", e34, ["product13"]),
                  field("trace_product_yield_14", "trace", e34, ["product14"]),
                  field("yield_measurement_basis", None)],
    )


# Page 4, Scheme 7.
e4 = [ev(4, "image"), ev(4, "text"), ev(5, "text")]
scheme7_allenes = [
    ("a", "1,2-propadiene"),
    ("b", "1,3-dimethylallene"),
    ("c", "tetramethylallene"),
]
for suffix, substrate in scheme7_allenes:
    add_lit(
        f"scheme7_complex15_{suffix}_to_16{suffix}", e4,
        [participant("complex15", "reactant", "cyclic eta3-allyl chloropalladium complex 15", e4),
         allene("allene", substrate, e4), solvent("cdcl3", "CDCl3", e4),
         participant("product", "product", f"ring-opened allylpalladium complex 16{suffix}", e4)],
        notes=["The review states that a stoichiometric amount of allene was used."],
    )

for start_label, product_label, ligand in [("18", "20", "acac (R=Me)"), ("19", "21", "Hfacac (R=CF3)")]:
    for suffix, substrate in scheme7_allenes:
        add_lit(
            f"scheme7_complex{start_label}_{suffix}_to_{product_label}{suffix}", e4,
            [participant("complex", "reactant", f"palladium complex {start_label} with {ligand}", e4),
             allene("allene", substrate, e4), solvent("cdcl3", "CDCl3", e4),
             participant("product", "product", f"allylpalladium complex {product_label}{suffix}", e4)],
        )
add_mech(
    "scheme7_ring_opening_via_17", e4,
    [participant("complex15", "reactant", "cyclic eta3-allyl chloropalladium complex 15", e4),
     participant("intermediate17", "product", "vinyl palladium intermediate 17", e4)],
    outcomes=[field("mechanistic_status", "proposed initial ring opening before allene insertion", e4, ["intermediate17"])],
    unresolved=["Intermediate 17 is suggested mechanistically and is not presented as an isolated product."],
)


# Page 4, Scheme 8.
scheme8_variants = [
    ("a", "22A", "R1=R2=R3=R4=H; R=Ac", "1,2-propadiene"),
    ("b", "22A", "R1=Me; R2=R3=R4=H; R=Ac", "1-methylallene"),
    ("c", "22A", "R1=R2=Me; R3=R4=H; R=Ac", "1,1-dimethylallene"),
    ("d", "22A", "R1=R3=Me; R2=R4=H; R=Ac", "1,3-dimethylallene"),
    ("e", "22A", "R1=R2=R3=R4=Me; R=Ac", "tetramethylallene"),
    ("f", "22B", "R1=R2=R3=R4=H; R=Me", "1,2-propadiene"),
    ("g", "22B", "R1=R2=Me; R3=R4=H; R=Me", "1,1-dimethylallene"),
]
for suffix, start_label, substitution, substrate in scheme8_variants:
    add_lit(
        f"scheme8_{start_label}_{suffix}_to_24{suffix}", e4,
        [participant("complex22", "reactant", f"Hfacac norbornenyl complex {start_label}", e4),
         allene("allene", substrate, e4), solvent("chloroform", "chloroform", e4),
         participant("product", "product", f"eta3-allylpalladium complex 24{suffix} ({substitution})", e4)],
        notes=["Scheme 8 literature example attributed to reference 20."],
    )
add_mech(
    "scheme8_nortricyclenyl_allene_intermediate_23", e4,
    [participant("complex22", "reactant", "Hfacac norbornenyl complex 22", e4),
     participant("allene", "reactant", "allene CH2=C=CR2 family", e4),
     participant("intermediate23", "product", "nortricyclenyl-allene intermediate 23", e4)],
    outcomes=[field("mechanistic_status", "proposed intermediate en route to complex 24", e4, ["intermediate23"])],
    unresolved=["Intermediate 23 is presented as a pathway intermediate; isolation is not stated."],
)


# Page 5, Scheme 9.
e5 = [ev(5, "image"), ev(5, "text")]
scheme9_variants = [
    ("a", "R=R'=Me"), ("b", "R=H, R'=OMe"),
    ("c", "R=H, R'=n-Bu"), ("d", "R'=H, R=n-Bu"),
]
for suffix, substitution in scheme9_variants:
    add_lit(
        f"scheme9_complex25_{suffix}_to_26{suffix}", e5,
        [participant("complex25", "reactant", "cyclopalladated dimeric aryl complex 25", e5),
         participant("allene", "reactant", f"substituted allene, {substitution}", e5),
         participant("product", "product", f"dimeric allylpalladium complex 26{suffix}", e5)],
    )
for suffix in ("a", "b", "c"):
    add_lit(
        f"scheme9_complex27{suffix}_to_28{suffix}", e5,
        [participant("complex27", "reactant", f"cyclometallated palladium complex 27{suffix}", e5),
         allene("allene", "1,1-dimethylallene", e5),
         participant("product", "product", f"dimeric allylpalladium complex 28{suffix}", e5)],
    )


# Page 5, Scheme 10.
add_lit(
    "scheme10_hydride29_to_30", e5,
    [participant("complex29", "reactant", "palladium hydride complex 29", e5),
     allene("allene", "1,1-dimethylallene", e5),
     participant("product", "product", "allylpalladium complex 30", e5)],
)
add_lit(
    "scheme10_allyl31_allene_to_32", e5,
    [participant("complex31", "reactant", "eta3-allylpalladium phosphine complex 31", e5),
     allene("allene", "1,2-propadiene", e5),
     participant("product", "product", "insertion product 32", e5)],
    conditions=[field("temperature", "room temperature", e5), field("time", "one year", e5)],
    notes=["The review describes this insertion as extremely slow and taking a year to completion."],
)
add_lit(
    "scheme10_vinyl33_allene_to_34", e5,
    [participant("complex33", "reactant", "vinyl palladium complex 33", e5),
     allene("allene", "1,2-propadiene", e5), solvent("toluene", "toluene", e5),
     participant("product", "product", "allylpalladium insertion product 34", e5)],
    conditions=[field("time", {"number": 18, "unit": "h"}, e5)],
)


# Page 5, Schemes 11 and 12.
add_lit(
    "scheme11_complex35_to_36", e5,
    [participant("complex35", "reactant", "Pd(Me)Cl(PPh3)2 complex 35", e5),
     allene("allene", "3,3-dimethylallene", e5),
     participant("product", "product", "methylpalladation product 36", e5)],
    conditions=[field("temperature", {"number": 45, "unit": "°C"}, e5),
                field("time", {"number": 1, "unit": "d"}, e5)],
)
add_lit(
    "scheme11_complex35_co_allene_to_37_38", e5,
    [participant("complex35", "reactant", "Pd(Me)Cl(PPh3)2 complex 35", e5),
     allene("allene", "3,3-dimethylallene", e5),
     participant("co", "reagent", "carbon monoxide", e5, smiles="[C-]#[O+]"),
     participant("product37", "product", "successive CO/allene insertion complex 37", e5),
     participant("product38", "product", "successive CO/allene insertion complex 38", e5)],
    conditions=[field("temperature", {"number": 40, "unit": "°C"}, e5),
                field("time", {"number": 2, "unit": "d"}, e5)],
    outcomes=[field("product_mixture", "complexes 37 and 38", e5, ["product37", "product38"])],
)
add_lit(
    "scheme12_acyl39_allene_to_40", e5,
    [participant("complex39", "reactant", "cationic acyl palladium complex 39", e5),
     allene("allene", "3,3-dimethylallene", e5), solvent("cdcl3", "CDCl3", e5),
     participant("product", "product", "2-acyl-substituted eta3-allylpalladium complex 40", e5)],
    conditions=[field("temperature", "r.t.", e5), field("time", {"number": 6, "unit": "h"}, e5)],
)
add_lit(
    "scheme12_complex40_co_allene_to_41_42", e5,
    [participant("complex40", "reactant", "allylpalladium complex 40", e5),
     allene("allene", "1,1-dimethylallene", e5),
     participant("co", "reagent", "carbon monoxide", e5, smiles="[C-]#[O+]"),
     participant("product41", "product", "acyl palladium complex 41", e5),
     participant("product42", "product", "polymeric-chain eta3-allylpalladium complex 42", e5)],
    conditions=[field("temperature", "r.t.", e5), field("time", {"number": 18, "unit": "h"}, e5)],
    outcomes=[field("product_mixture", "complexes 41 and 42", e5, ["product41", "product42"])],
)


# Page 6, Schemes 13--16.
e6 = [ev(6, "image"), ev(6, "text")]
for suffix, substrate in [("h", "1,1-dimethylallene"), ("me", "tetramethylallene")]:
    add_lit(
        f"scheme13_complex43_{suffix}_to_44", e6,
        [participant("complex43", "reactant", "[PdMe(MeCN)(dppp)]BF4 complex 43", e6),
         allene("allene", substrate, e6),
         participant("co", "reagent", "carbon monoxide", e6, smiles="[C-]#[O+]"),
         participant("product", "product", f"mono-insertion eta3-allylpalladium complex 44 ({substrate})", e6)],
        conditions=[field("temperature", "r.t.", e6)],
        outcomes=[field("product_selectivity", "mono-insertion product as the only product", e6, ["product"]),
                  field("carbon_monoxide_insertion", "not observed", e6, ["product"])],
        notes=["The review states that complexes 44 do not undergo insertion with carbon monoxide."],
    )
add_lit(
    "scheme14_alkoxycarbonyl45_allene_to_46", e6,
    [participant("complex45", "reactant", "alkoxycarbonyl palladium complex 45", e6),
     allene("allene", "1,2-propadiene", e6),
     participant("product", "product", "unexpected allylpalladium complex 46", e6)],
    outcomes=[field("allene_insertion_product", "expected product not obtained", e6),
              field("observed_product", "unexpected allyl complex 46", e6, ["product"])],
    notes=["Scheme 14 labels allene as excess and shows loss of MeCO2-."],
)
add_lit(
    "scheme15_complex47_phenylallene_to_48", e6,
    [participant("complex47", "reactant", "bipyridine aryl palladium complex 47", e6),
     allene("allene", "phenylallene", e6),
     participant("agbf4", "reagent", "silver tetrafluoroborate", e6),
     solvent("acetone", "acetone", e6),
     participant("product", "product", "cationic eta3-allylpalladium complex 48", e6)],
    outcomes=[field("syn_anti_ratio", "2:1", e6, ["product"])],
)
add_lit(
    "scheme15_generic_complex49_allenes_to_50", e6,
    [participant("complex49", "reactant", "bipyridine palladium complex family 49", e6),
     participant("allene", "reactant", "1,2-propadiene, 1,1-dimethylallene, or tetramethylallene", e6),
     participant("product", "product", "eta3-allylpalladium complex family 50", e6)],
    notes=["One generic Scheme 15 arrow covers several R, R1, R2, and counterion combinations."],
    unresolved=["The generic scheme does not map every R/R1/R2/Y combination to a separate reported outcome.",
                "No yield or complete procedure is supplied."],
)
for suffix, r_value in [("a", "R=H"), ("b", "R=Me")]:
    add_lit(
        f"scheme16_complex51{suffix}_to_52{suffix}", e6,
        [participant("complex51", "reactant", f"cationic alkyl palladium complex 51{suffix} ({r_value})", e6),
         allene("allene", "1,1-dimethylallene", e6),
         participant("product", "product", f"cationic eta3-allylpalladium complex 52{suffix}", e6)],
    )
add_lit(
    "scheme16_complex53_to_54", e6,
    [participant("complex53", "reactant", "cationic alkyl palladium complex 53", e6),
     allene("allene", "1,1-dimethylallene", e6),
     participant("product", "product", "cationic eta3-allylpalladium complex 54", e6)],
)
add_lit(
    "scheme16_generic_complex55_allenes_to_56", e6,
    [participant("complex55", "reactant", "cationic Pd(p-An-BIAN) complex family 55a/55b (R=Me or COMe)", e6),
     participant("allene", "reactant", "allene family with R1/R2 = H or Me", e6),
     participant("product", "product", "cationic eta3-allylpalladium complex family 56", e6)],
    notes=["One generic Scheme 16 arrow covers 55a/55b and three allene substitution patterns."],
    unresolved=["The page does not resolve a complete experiment matrix or individual yields for the generic 55-to-56 arrow.",
                "Complex structures remain unverified."],
)


# Coverage: exactly the requested six pages. Record associations are derived from record evidence.
def ids_for_page(page):
    image_id = ev(page, "image")
    text_id = ev(page, "text")
    return [r["record_id"] for r in records if image_id in r["evidence_ids"] or text_id in r["evidence_ids"]]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [{
                "region": "title, abstract, article information, and contents across the original page",
                "finding": "Review front matter only; no reaction arrow, table row, or independent experiment is shown.",
                "evidence_ids": [ev(1, "image"), ev(1, "text")],
            }],
            "record_ids": [],
            "unresolved": ["Abstract-level claims were not converted into duplicate reaction records."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left and lower-left introduction",
                    "finding": "Background and scope of a review article; cited catalytic reaction classes are not present-paper experiments.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
                {
                    "region": "upper-right Scheme 1",
                    "finding": "Three cited nickel-complex insertion arrows were extracted as literature examples, including the further insertion 3 to 4.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
                {
                    "region": "right-column palladium discussion",
                    "finding": "Narrative conditions and yields for Schemes 2-4 on page 3 were merged with the corresponding page-3 arrows; the proposed vinyl intermediate 6d is classified as mechanism.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text"), ev(3, "image")],
                },
            ],
            "record_ids": ids_for_page(2),
            "unresolved": ["Most cited primary experiments lack complete scale, time, atmosphere, workup, and purification details in the review."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper Scheme 2",
                    "finding": "Seven independent/generic PdX2(PhCN)2 allene-insertion arrows were extracted as literature examples; the 1,2,6-heptatriene arrow retains both products 5f and 5g.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text"), ev(2, "text")],
                },
                {
                    "region": "middle Scheme 3",
                    "finding": "Five solvent/reagent-specific palladium examples were extracted; the methanol experiment retains separate 30% and 46% isolated yields, and 6d is a proposed mechanism record.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text"), ev(2, "text")],
                },
                {
                    "region": "lower Scheme 4",
                    "finding": "Two routes to complex 9 were kept separate because starting complexes, solvents, and yields differ.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text"), ev(2, "text")],
                },
                {
                    "region": "lower prose introducing Schemes 5 and 6",
                    "finding": "Narrative context was linked to page-4 variant records; no duplicate experiment was created.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text"), ev(4, "image")],
                },
            ],
            "record_ids": ids_for_page(3),
            "unresolved": ["Many complex structures and variant-specific primary procedures are unavailable in the review."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "top Schemes 5 and 6",
                    "finding": "Four substitution variants per scheme were extracted separately; Scheme 6 retains product 13 as main and complex 14 as trace.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text"), ev(3, "text")],
                },
                {
                    "region": "middle Scheme 7",
                    "finding": "Nine substrate/ligand combinations were extracted as literature examples; proposed ring opening through 17 is a mechanism record.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text"), ev(5, "text")],
                },
                {
                    "region": "bottom Scheme 8",
                    "finding": "Seven explicitly lettered complex/allene variants were extracted; intermediate 23 is classified as proposed mechanism.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text"), ev(5, "text")],
                },
            ],
            "record_ids": ids_for_page(4),
            "unresolved": ["Scheme variants do not provide numeric yields or complete primary procedures."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 9",
                    "finding": "Four complex-25 allene variants and three complex-27 variants were extracted as separate literature examples.",
                    "evidence_ids": [ev(5, "image"), ev(5, "text")],
                },
                {
                    "region": "upper-right Schemes 10 and 11",
                    "finding": "Three phosphine-supported insertion examples and two Pd(Me)Cl(PPh3)2 examples were extracted with the reported time/temperature conditions.",
                    "evidence_ids": [ev(5, "image"), ev(5, "text")],
                },
                {
                    "region": "bottom Scheme 12",
                    "finding": "The 39-to-40 insertion and subsequent CO/allene conversion to 41/42 were retained as distinct operations.",
                    "evidence_ids": [ev(5, "image"), ev(5, "text")],
                },
            ],
            "record_ids": ids_for_page(5),
            "unresolved": ["Scheme 10's one-year duration is preserved qualitatively because the supported quantity-unit list has no year unit.",
                           "Most examples omit scale, atmosphere, workup, purification, and yield."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {
                    "region": "top Schemes 13 and 14",
                    "finding": "Two allene variants for complex 43 and the unexpected 45-to-46 transformation were extracted; lack of CO insertion and failure of the expected product are preserved as negative results.",
                    "evidence_ids": [ev(6, "image"), ev(6, "text")],
                },
                {
                    "region": "upper-right Scheme 15",
                    "finding": "The phenylallene/47 experiment retains AgBF4, acetone, and syn:anti 2:1; the broad 49-to-50 arrow remains one generic literature example because the combination matrix is not resolved.",
                    "evidence_ids": [ev(6, "image"), ev(6, "text")],
                },
                {
                    "region": "bottom Scheme 16",
                    "finding": "Two 51 variants, the 53 example, and one generic 55-to-56 family arrow were extracted as literature examples.",
                    "evidence_ids": [ev(6, "image"), ev(6, "text")],
                },
            ],
            "record_ids": ids_for_page(6),
            "unresolved": ["Generic Schemes 15 and 16 do not uniquely map every R-group combination to its own conditions or yield.",
                           "Complex connectivity and coordination modes remain unverified."],
        },
    ],
}


raw_path = RUN / "raw_model" / "records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage_path = RUN / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(1, 7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "raw": str(raw_path)}, ensure_ascii=False))
