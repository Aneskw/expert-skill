#!/usr/bin/env python3
"""Build evidence-linked records for doc_0a0328e571461b17, PDF pages 7--12."""

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


SMILES = {
    "1,2-propadiene": "C=C=C",
    "1-methylallene": "C=C=CC",
    "1,1-dimethylallene": "C=C=C(C)C",
    "tetramethylallene": "CC(C)=C=C(C)C",
    "phenylallene": "C=C=Cc1ccccc1",
    "1,2-heptadiene": "C=C=CCCCC",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    "n-octane": "CCCCCCCC",
    "methanol": "CO",
    "acetone": "CC(=O)C",
    "dichloromethane": "ClCCl",
    "THF": "C1CCOC1",
    "acetic acid": "CC(=O)O",
    "carbon monoxide": "[C-]#[O+]",
    "sodium iodide": "[Na+].[I-]",
    "trimethylsilyl chloride": "C[Si](C)(C)Cl",
    "sodium ethoxide": "CC[O-].[Na+]",
}


def mol(entity_id, role, label, evidence, *, amounts=(), smiles=None):
    return participant(entity_id, role, label, evidence, smiles=smiles or SMILES.get(label), amounts=amounts)


def allene(entity_id, label, evidence, *, equivalents=None):
    amounts = []
    if equivalents is not None:
        amounts.append(field("equivalents", {"number": equivalents, "unit": "equiv"}, evidence))
    return mol(entity_id, "reactant", label, evidence, amounts=amounts)


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


# Page 7, Schemes 17--19. Generic family arrows are not expanded into
# unsupported Cartesian products.
e7 = [ev(7, "image"), ev(7, "text")]
add_lit(
    "scheme17_complex57_dimethylallene_to_58", e7,
    [mol("complex57", "reactant", "neutral alkyl palladium complex 57", e7),
     allene("allene", "1,1-dimethylallene", e7),
     mol("product58", "product", "cationic pi-allyl palladium complex 58", e7)],
)
add_lit(
    "scheme17_complex59_family_to_60", e7,
    [mol("complex59", "reactant", "neutral palladium complex 59 (R = Me or COMe)", e7),
     allene("allene", "1,1-dimethylallene", e7),
     mol("product60", "product", "cationic pi-allyl palladium complex family 60", e7)],
    unresolved=["The single generic arrow covers R = Me and COMe without variant-specific conditions or yields."],
)
add_lit(
    "scheme17_complex61_allene_family_to_62", e7,
    [mol("complex61", "reactant", "neutral palladium complex 61 (R = Me, COMe, or COPh)", e7),
     mol("allene", "reactant", "allene family with R' = H or n-Bu", e7),
     mol("product62", "product", "cationic pi-allyl palladium complex family 62", e7)],
    unresolved=["The review does not map each R/R' combination to a separate outcome or procedure."],
)
add_lit(
    "scheme17_complex63_two_variants_to_64", e7,
    [mol("complex63", "reactant", "neutral palladium complex 63, two explicitly listed substitution sets", e7),
     mol("allene", "reactant", "substituted allene shown in Scheme 17", e7),
     mol("product64", "product", "cationic pi-allyl palladium complex family 64", e7)],
    notes=["The arrow lists two complete substitution sets beneath Scheme 17."],
    unresolved=["The two substitution sets share one family arrow and no variant-specific conditions or yields are given."],
)
add_lit(
    "scheme18_complex65a_65b_heptadiene_to_66", e7,
    [mol("complex65", "reactant", "Pd(p-An-BIAN) acyl complexes 65a (R=COMe) and 65b (R=COPh)", e7),
     allene("allene", "1,2-heptadiene", e7),
     mol("product66", "product", "cationic allyl palladium complex family 66", e7)],
    unresolved=["The common arrow does not give separate conditions or yields for 65a and 65b."],
)
add_lit(
    "scheme18_complex65a_65c_allene_family_to_67", e7,
    [mol("complex65", "reactant", "Pd(p-An-BIAN) complexes 65a (R=COMe) and 65c (R=Me)", e7),
     mol("allene", "reactant", "1,2-propadiene, 1,1-dimethylallene, or tetramethylallene", e7),
     mol("product67", "product", "neutral allyl palladium complex family 67", e7)],
    unresolved=["The review supplies a family matrix but no unique complex/allene-to-product mapping or variant yields."],
)
add_lit(
    "scheme18_complex65d_allene_family_to_68", e7,
    [mol("complex65d", "reactant", "Pd(p-An-BIAN) complex 65d", e7),
     mol("allene", "reactant", "1,2-propadiene or 1,1-dimethylallene", e7),
     mol("dcm", "solvent", "dichloromethane", e7),
     mol("product68", "product", "neutral allyl palladium complex family 68", e7)],
    conditions=[field("temperature", {"number": 20, "unit": "°C"}, e7)],
    unresolved=["The common arrow does not report separate outcomes for the two allene variants."],
)
add_lit(
    "scheme19_complex69_allene_family_to_70", e7,
    [mol("complex69", "reactant", "pyridinylmethylthioether palladium complex family 69", e7),
     mol("allene", "reactant", "1,1-dimethylallene or tetramethylallene", e7),
     mol("naclo4", "reagent", "sodium perchlorate", e7),
     mol("dcm", "solvent", "dichloromethane", e7),
     mol("product70", "product", "cationic pi-allyl palladium complex family 70", e7)],
    unresolved=["R1/R2/R3 and allene variants are shown as a family matrix without individual yields."],
)


# Page 8, continuation of Scheme 19 and Schemes 20--22.
e78 = [ev(7, "image"), ev(7, "text"), ev(8, "image"), ev(8, "text")]
add_lit(
    "scheme19_complex71_allene_family_to_72", e78,
    [mol("complex71", "reactant", "chelating N,S-palladium complex family 71 (R=Me or COMe; n=1 or 2)", e78),
     mol("allene", "reactant", "1,1-dimethylallene or tetramethylallene", e78),
     mol("product72", "product", "cationic allyl palladium complex family 72", e78)],
    outcomes=[field("reaction_rate", "rapid", e78, ["product72"])],
    unresolved=["The family arrow does not resolve each ligand/allene combination or give individual yields."],
)
e8 = [ev(8, "image"), ev(8, "text")]
add_lit(
    "scheme20_complex73_allene_family_to_74", e8,
    [mol("complex73", "reactant", "terpy acyl palladium complex 73", e8),
     mol("allene", "reactant", "CH2=C=CR2 (R = H or Me)", e8),
     mol("product74", "product", "eta1-allyl palladium complex family 74", e8)],
    unresolved=["The common arrow covers R=H and R=Me without separate procedures or yields."],
)
add_lit(
    "scheme20_complex75_allene_family_to_76", e8,
    [mol("complex75", "reactant", "palladium complex 75 with a flexible tridentate ligand", e8),
     mol("allene", "reactant", "allene family with R1/R2 = H or Me", e8),
     mol("product76", "product", "N,N-bidentate eta3-allyl palladium complex family 76", e8)],
    unresolved=["The family arrow does not uniquely resolve each R1/R2 combination."],
)
add_lit(
    "scheme21_complex77_dimethylallene_to_78", e8,
    [mol("complex77", "reactant", "pyridylbisthioether palladium methyl complex family 77 (R=Me, t-Bu, or Ph)", e8),
     allene("allene", "1,1-dimethylallene", e8),
     mol("product78", "product", "eta3-allyl palladium complex family 78", e8)],
    unresolved=["The common arrow covers three thioether substituents without separate yields."],
)
add_lit(
    "scheme21_complex79_dimethylallene_to_80", e8,
    [mol("complex79", "reactant", "cationic pyridylbisthioether palladium methyl complex 79", e8),
     allene("allene", "1,1-dimethylallene", e8),
     mol("product80", "product", "cationic eta3-allyl palladium complex 80", e8)],
)
scheme22 = [
    ("a", "PdCl(Me)(COD) complex 81a", "1,2-propadiene", "R=Me; R1=R2=H"),
    ("b", "PdCl(Me)(COD) complex 81a", "1,1-dimethylallene", "R=Me; R1=H, R2=Me"),
    ("c", "PdCl(Me)(COD) complex 81a", "tetramethylallene", "R=Me; R1=R2=Me"),
    ("d", "PdCl(COMe)(COD) complex 81b", "1,1-dimethylallene", "R=COMe; R1=H, R2=Me"),
]
for suffix, start, substrate, substitution in scheme22:
    add_lit(
        f"scheme22_complex81_{suffix}_to_82{suffix}", e8,
        [mol("complex81", "reactant", start, e8), allene("allene", substrate, e8),
         mol("product82", "product", f"dimeric allyl palladium complex 82{suffix} ({substitution})", e8)],
        conditions=[field("temperature", "room temperature", e8)],
    )


# Pages 8--9, Schemes 23 and 24.
e89 = [ev(8, "image"), ev(8, "text"), ev(9, "image"), ev(9, "text")]
add_lit(
    "scheme23_complex83_allene_to_84", e89,
    [mol("complex83", "reactant", "platinum hydride complex 83", e89),
     allene("allene", "1,2-propadiene", e89),
     mol("nabph4", "reagent", "sodium tetraphenylborate", e89),
     mol("meoh", "solvent", "methanol", e89),
     mol("product84", "product", "pi-allyl platinum complex 84", e89)],
)
add_lit(
    "scheme23_complex85_allene_to_86", e89,
    [mol("complex85", "reactant", "cationic platinum hydride complex family 85 (PR3=PPh3, PPh2Me, or PMe2Ph)", e89),
     allene("allene", "1,2-propadiene", e89), mol("acetone", "solvent", "acetone", e89),
     mol("product86", "product", "eta3-allyl platinum complex family 86", e89)],
    conditions=[field("temperature", "r.t.", e89)],
    unresolved=["The ligand variants share one arrow and no individual yields are reported."],
)
add_lit(
    "scheme23_complex87_allene_to_88", e89,
    [mol("complex87", "reactant", "platinum hydridoalkyl complex 87", e89),
     allene("allene", "1,2-propadiene", e89), mol("dcm", "solvent", "dichloromethane", e89),
     mol("product88", "product", "eta1-allyl platinum complex 88", e89)],
    conditions=[field("temperature", {"number": 60, "unit": "°C"}, e89),
                field("time", {"number": 4, "unit": "h"}, e89)],
)
add_lit(
    "scheme24_complex89_alkyne_family_to_90", e89,
    [mol("complex89", "reactant", "PtHX(PEt3)2 hydride complex 89", e89),
     mol("alkyne", "reactant", "alkyne R1C≡CR2 family", e89),
     mol("product90", "product", "vinyl platinum complex family 90", e89)],
    notes=["Scheme 24 shows preparation of 90 by hydrometallation before allene insertion."],
    unresolved=["The preparation arrow gives no conditions or variant-specific yields."],
)
scheme24 = [
    ("a", "R1=R2=Me; X=PF6"),
    ("b", "R1=Me, R2=Cy; X=PF6"),
    ("c", "R1=Me, R2=Ph; X=NO3"),
    ("d", "R1=R2=COOMe; X=PF6"),
    ("e", "R1=R2=CF3; X=PF6"),
]
for suffix, substitution in scheme24:
    add_lit(
        f"scheme24_complex90_{suffix}_allene_to_91{suffix}", e89,
        [mol("complex90", "reactant", f"vinyl platinum complex 90{suffix} ({substitution})", e89),
         allene("allene", "1,2-propadiene", e89),
         mol("product91", "product", f"pi-allyl platinum complex 91{suffix}", e89)],
    )
add_lit(
    "scheme24_methanol_complex92_allene_to_93", e89,
    [mol("complex92", "reactant", "platinum methanol complex 92", e89),
     allene("allene", "1,2-propadiene", e89),
     mol("product93", "product", "six-membered platinum metallacycle 93", e89)],
    notes=["The review states that the detailed mechanism is not well-defined."],
)


# Page 9, Schemes 25--27.
e9 = [ev(9, "image"), ev(9, "text")]
for suffix, ligand in [("pphme2", "PPhMe2"), ("asme3", "AsMe3")]:
    add_lit(
        f"scheme25_complex94_{suffix}_allene_to_95", e9,
        [mol("complex94", "reactant", f"trans-[PtMe(acetone)L2]PF6 complex 94 (L={ligand})", e9),
         allene("allene", "1,2-propadiene", e9), mol("dcm", "solvent", "dichloromethane", e9),
         mol("product95", "product", f"allene-platinum coordination complex 95 (L={ligand})", e9)],
        conditions=[field("temperature", {"number": 0, "unit": "°C", "qualifier": "lt", "raw_text": "below 0 °C"}, e9)],
    )
    add_lit(
        f"scheme25_complex95_{suffix}_to_96", e9,
        [mol("complex95", "reactant", f"allene-platinum complex 95 (L={ligand})", e9),
         mol("product96", "product", f"eta3-allyl platinum complex 96 (L={ligand})", e9)],
        conditions=[field("temperature", {"number": 0, "unit": "°C", "qualifier": "gt", "raw_text": "above 0 °C"}, e9)],
        notes=["Neutral or anionic ligands I-, NO3-, CO, and PPh3 inhibit the insertion according to the review."],
    )
add_lit(
    "scheme25_complex97_phenylallene_to_98", e9,
    [mol("complex97", "reactant", "2,2'-bipyridine phenyl platinum complex 97", e9),
     allene("allene", "phenylallene", e9),
     mol("product98", "product", "pi-allyl platinum complex 98", e9)],
    outcomes=[field("syn_anti_ratio", "52:48", e9, ["product98"])],
)
add_lit(
    "scheme26_complex99_dimethylallene_to_100", e9,
    [mol("complex99", "reactant", "cationic platinum complex family 99", e9),
     allene("allene", "1,1-dimethylallene", e9),
     mol("product100", "product", "pi-allyl platinum complex family 100", e9)],
    unresolved=["The R/R' family is not resolved into variant-specific conditions or yields."],
)
add_lit(
    "scheme26_complex101_dimethylallene_to_102", e9,
    [mol("complex101", "reactant", "cationic platinum complex family 101", e9),
     allene("allene", "1,1-dimethylallene", e9),
     mol("product102", "product", "pi-allyl platinum complex family 102", e9)],
    unresolved=["The R/R' family is not resolved into variant-specific conditions or yields."],
)
scheme27 = [
    ("105", 1, "r.t.", "loss of H2"),
    ("106", 1, {"number": 50, "unit": "°C"}, "loss of H2"),
    ("107", 3, "r.t.", "formation of ArHC=CMe shown on arrow"),
]
for product, equivalents, temperature, arrow_note in scheme27:
    add_lit(
        f"scheme27_complex103_arylallene_to_{product}", e9,
        [mol("complex103", "reactant", "Pt(SiHPh2)2(PMe3)2 complex 103", e9),
         mol("allene104", "reactant", "p-fluorophenylallene 104", e9,
             amounts=[field("equivalents", {"number": equivalents, "unit": "equiv"}, e9)]),
         mol("product", "product", f"platinum complex {product}", e9)],
        conditions=[field("temperature", temperature, e9)],
        notes=[f"Scheme 27 indicates a 103:104 ratio of 1:{equivalents} and {arrow_note}."],
    )


# Pages 9--10, Schemes 28 and 29.
e910 = [ev(9, "image"), ev(9, "text"), ev(10, "image"), ev(10, "text")]
add_lit(
    "scheme28_complex108_allene_to_109", e910,
    [mol("complex108", "reactant", "eta3-allyl cobalt tricarbonyl complex 108", e910),
     allene("allene", "1,2-propadiene", e910), mol("octane", "solvent", "n-octane", e910),
     mol("product109", "product", "eta3-2-allyl-1,1-dimethylallyl cobalt tricarbonyl complex 109", e910)],
)
for suffix, start, product in [
    ("a", "benzoyl cobalt tetracarbonyl complex 110a", "pi-allyl cobalt tricarbonyl complex 111a"),
    ("b", "acetyl cobalt tetracarbonyl complex 110b", "pi-allyl cobalt tricarbonyl complex 111b"),
]:
    add_lit(
        f"scheme28_complex110{suffix}_allene_to_111{suffix}", e910,
        [mol("complex110", "reactant", start, e910), allene("allene", "1,2-propadiene", e910),
         mol("product111", "product", product, e910), mol("co", "product", "carbon monoxide", e910)],
    )
add_lit(
    "scheme28_complex110b_dimethylallene_to_111c", e910,
    [mol("complex110b", "reactant", "acetyl cobalt tetracarbonyl complex 110b", e910),
     allene("allene", "1,1-dimethylallene", e910),
     mol("product111c", "product", "pi-allyl cobalt tricarbonyl complex 111c", e910),
     mol("co", "product", "carbon monoxide", e910)],
)
for start, product, eq in [("112", "113", 2), ("113", "114", 1), ("114", "115", 1)]:
    participants = [mol("start", "reactant", f"cobalt complex {start}", e910),
                    allene("allene", "1,1-dimethylallene", e910, equivalents=eq),
                    mol("product", "product", f"carbonylative metallation complex {product}", e910)]
    if start == "112":
        participants.append(mol("co", "product", "carbon monoxide", e910))
    add_lit(
        f"scheme29_complex{start}_dimethylallene_to_{product}", e910, participants,
        conditions=[field("temperature", "r.t.", e910)],
        notes=[f"Scheme 29 shows the staged 112 to 113 to 114 to 115 sequence; this arrow uses {eq} equivalent(s) of allene."],
    )


# Page 10, Schemes 30--32 and a computational mechanism.
e10 = [ev(10, "image"), ev(10, "text")]
scheme30 = [
    ("a", "1,2-propadiene", "R=H"),
    ("b", "methoxyallene", "R=OMe"),
    ("c", "phenylallene", "R=Ph"),
    ("d", "p-methylphenylallene", "R=C6H4Me-p"),
    ("e", "p-methoxyphenylallene", "R=C6H4OMe-p"),
    ("f", "p-fluorophenylallene", "R=C6H4F-p"),
    ("g", "p-chlorophenylallene", "R=C6H4Cl-p"),
]
for suffix, substrate, substitution in scheme30:
    add_lit(
        f"scheme30_complex116_{suffix}_to_117{suffix}", e10,
        [mol("complex116", "reactant", "RhH(CO)(PPh3)3 complex 116", e10),
         mol("allene", "reactant", substrate, e10), mol("toluene", "solvent", "toluene", e10),
         mol("product117", "product", f"pi-allyl rhodium complex 117{suffix} ({substitution})", e10)],
        conditions=[field("temperature", "r.t.", e10)],
    )
add_lit(
    "scheme30_complex118_allene_to_119", e10,
    [mol("complex118", "reactant", "RhH(PF3)4 complex 118", e10),
     allene("allene", "1,2-propadiene", e10), mol("toluene", "solvent", "toluene", e10),
     mol("product119", "product", "pi-allyl rhodium complex 119", e10)],
    notes=["Scheme 30 shows loss of PF3."],
)
add_mech(
    "page10_computational_hco_allene_hydroformylation", e10,
    [mol("hcoco3", "reactant", "HCo(CO)3", e10), allene("allene", "1,2-propadiene", e10),
     mol("product", "product", "Co(eta3-C3H5)(CO)3", e10)],
    outcomes=[field("study_type", "computational study connected with allene hydroformylation mechanism", e10, ["product"])],
    unresolved=["This is a cited computational result, not an isolated experimental batch."],
)
scheme31_aryl = [
    ("a", "phenyl"), ("b", "p-methylphenyl"), ("c", "p-methoxyphenyl"),
    ("d", "p-tert-butylphenyl"), ("e", "p-chlorophenyl"), ("f", "p-fluorophenyl"),
]
for suffix, aryl in scheme31_aryl:
    add_lit(
        f"scheme31_complex120_{suffix}_to_121{suffix}", e10,
        [mol("complex120", "reactant", "RhH(PPh3)4 complex 120", e10),
         mol("allene", "reactant", f"{aryl}allene", e10,
             amounts=[field("equivalents", {"number": 5, "unit": "equiv"}, e10)]),
         mol("toluene", "solvent", "toluene", e10),
         mol("product121", "product", f"multi-insertion rhodium complex 121{suffix}", e10)],
        conditions=[field("temperature", "room temperature", e10)],
        outcomes=[field("reported_yield", {"number": 80, "unit": "%", "qualifier": "gt", "raw_text": ">80%"}, e10, ["product121"]),
                  field("yield_measurement_basis", None)],
        notes=["Scheme 31 shows loss of two PPh3 ligands."],
    )
add_mech(
    "scheme31_proposed_multi_insertion_pathway_122_124", e10,
    [mol("complex120", "reactant", "RhH(PPh3)4 complex 120", e10),
     mol("allene", "reactant", "arylallene", e10),
     mol("intermediates", "product", "proposed allyl/vinyl rhodium intermediates 122, 123, and 124", e10)],
    outcomes=[field("mechanistic_status", "suggested sequence leading to complex 121", e10, ["intermediates"])],
    unresolved=["Intermediates 122-124 are suggested mechanistically and are not presented as isolated products."],
)
for start_label in ["RhH(CO)(PPh3)3 complex 116", "phenyl-substituted allyl rhodium complex 117c"]:
    suffix = "116" if "116" in start_label else "117c"
    add_lit(
        f"page10_complex{suffix}_phenylallene_to_121a", e10,
        [mol("start", "reactant", start_label, e10), allene("allene", "phenylallene", e10),
         mol("product121a", "product", "multi-insertion rhodium complex 121a", e10)],
        unresolved=["The prose gives no conditions or yield for this alternative route to 121a."],
    )
add_lit(
    "scheme32_complex125_hpf6_to_126", e10,
    [mol("complex125", "reactant", "rhodium allene complex 125", e10),
     mol("hpf6", "reagent", "hexafluorophosphoric acid", e10),
     mol("product126", "product", "allyl rhodium complex 126", e10)],
)
add_lit(
    "scheme32_complex125_tfa_nai_to_127", e10,
    [mol("complex125", "reactant", "rhodium allene complex 125", e10),
     mol("tfa", "reagent", "trifluoroacetic acid", e10), mol("nai", "reagent", "sodium iodide", e10),
     mol("product127", "product", "vinyl rhodium complex 127", e10)],
)
add_lit(
    "page10_rhodium_dihydride_allene_insertion", e10,
    [mol("dihydride", "reactant", "[RhH2Cl(PiPr3)]2", e10), allene("allene", "1,2-propadiene", e10),
     mol("product", "product", "[RhCl(MeCH=CH2)(PiPr3)]2", e10)],
    unresolved=["This prose-only literature example omits conditions, yield, and complete procedure."],
)


# Pages 10--11, Schemes 33 and 34.
e1011 = [ev(10, "image"), ev(10, "text"), ev(11, "image"), ev(11, "text")]
add_lit(
    "scheme33_complex128_allene_to_129a", e1011,
    [mol("complex128", "reactant", "IrH(CO)2(PPh3)2 complex 128", e1011),
     allene("allene", "1,2-propadiene", e1011), mol("benzene", "solvent", "benzene", e1011),
     mol("product129a", "product", "pi-allyl iridium complex 129a", e1011)],
    conditions=[field("temperature", "r.t.", e1011), field("time", {"number": 30, "unit": "min"}, e1011)],
)
add_lit(
    "scheme33_complex128_tetramethylallene_to_129b", e1011,
    [mol("complex128", "reactant", "IrH(CO)2(PPh3)2 complex 128", e1011),
     allene("allene", "tetramethylallene", e1011), mol("benzene", "solvent", "benzene", e1011),
     mol("product129b", "product", "pi-allyl iridium complex 129b", e1011)],
    conditions=[field("temperature", "r.t.", e1011), field("time", {"number": 12, "unit": "h"}, e1011)],
)
for suffix, aryl in [("c", "phenyl"), ("d", "p-methylphenyl"), ("e", "p-bromophenyl")]:
    add_lit(
        f"scheme33_complex130_{suffix}_to_129{suffix}", e1011,
        [mol("complex130", "reactant", "IrH(CO)(PPh3)3 complex 130", e1011),
         mol("allene", "reactant", f"{aryl}allene", e1011),
         mol("product129", "product", f"pi-allyl iridium complex 129{suffix}", e1011)],
    )
e11 = [ev(11, "image"), ev(11, "text")]
add_lit(
    "scheme34_complex131_dimethylallene_to_132", e11,
    [mol("complex131", "reactant", "dihydrogen iron hydride complex 131", e11),
     allene("allene", "1,1-dimethylallene", e11),
     mol("product132", "product", "vinyl iron complex 132 with an agostic C-H interaction", e11)],
)
add_lit(
    "page11_complex131_allene_similar_vinyl_product", e11,
    [mol("complex131", "reactant", "dihydrogen iron hydride complex 131", e11),
     allene("allene", "1,2-propadiene", e11),
     mol("product", "product", "vinyl iron complex analogous to 132", e11)],
    unresolved=["The prose does not assign a compound number, conditions, or yield to the analogous product."],
)


# Page 11, Schemes 35 and 36.
add_lit(
    "scheme35_complex133_etbr_to_134", e11,
    [mol("complex133", "reactant", "Na2Fe(CO)4 complex 133", e11),
     mol("etbr", "reactant", "ethyl bromide", e11, smiles="CCBr"),
     mol("product134", "product", "sodium acyl iron tricarbonyl intermediate 134", e11)],
    notes=["Scheme 35 shows loss of NaBr."],
)
for suffix, substitution in [("a", "R=R'=H"), ("b", "R=R'=Me"), ("c", "R=H, R'=Ph")]:
    add_lit(
        f"scheme35_complex134_allene_to_135{suffix}", e11,
        [mol("complex134", "reactant", "sodium acyl iron tricarbonyl intermediate 134", e11),
         mol("allene", "reactant", f"allene variant {substitution}", e11),
         mol("product135", "product", f"allyl iron complex 135/135' ({substitution})", e11)],
        outcomes=[field("tautomeric_or_resonance_forms", "135 and 135' are both depicted", e11, ["product135"])],
    )
add_lit(
    "scheme35_complex135_acid_to_136", e11,
    [mol("complex135", "reactant", "allyl iron complex family 135", e11),
     mol("acid", "reagent", "acetic acid", e11),
     mol("product136", "product", "eta4-heterodiene iron tricarbonyl complex family 136", e11)],
)
add_lit(
    "scheme35_complex135_tmscl_to_137", e11,
    [mol("complex135", "reactant", "allyl iron complex family 135", e11),
     mol("tmscl", "reagent", "trimethylsilyl chloride", e11),
     mol("product137", "product", "silyloxy heterodiene iron tricarbonyl complex family 137", e11)],
)
add_lit(
    "scheme36_complex138_phenylallene_mei_to_139a_139b", e11,
    [mol("complex138", "reactant", "[n-Bu4N][Fe(CO)3(NO)] complex 138", e11),
     allene("allene", "phenylallene", e11), mol("mei", "reactant", "methyl iodide", e11, smiles="CI"),
     mol("product139a", "product", "allyl iron complex 139a", e11),
     mol("product139b", "product", "allyl iron complex 139b", e11)],
    outcomes=[field("product_mixture", "complexes 139a and 139b", e11, ["product139a", "product139b"])],
)
add_lit(
    "scheme36_complex138_allene_rx_to_140a_140b", e11,
    [mol("complex138", "reactant", "[n-Bu4N][Fe(CO)3(NO)] complex 138", e11),
     mol("allene", "reactant", "terminal allene family shown in Scheme 36", e11),
     mol("rx", "reactant", "alkyl halide family RX listed in Scheme 36", e11),
     mol("product140a", "product", "allyl iron complex family 140a", e11),
     mol("product140b", "product", "allyl iron complex family 140b", e11)],
    outcomes=[field("product_mixture", "complex families 140a and 140b", e11, ["product140a", "product140b"])],
    unresolved=["The R/R'/X lists define a family but are not mapped to individual product yields."],
)
add_lit(
    "scheme36_complex138_cyclic_allene_mei_to_141", e11,
    [mol("complex138", "reactant", "[n-Bu4N][Fe(CO)3(NO)] complex 138", e11),
     mol("allene", "reactant", "cyclic allene depicted in Scheme 36", e11),
     mol("mei", "reactant", "methyl iodide", e11, smiles="CI"),
     mol("product141", "product", "cyclic allyl iron complex 141", e11)],
    unresolved=["The cyclic allene ring size/connectivity is retained from the drawing and not forced into SMILES."],
)


# Pages 11--12, Schemes 37 and 38.
e1112 = [ev(11, "image"), ev(11, "text"), ev(12, "image"), ev(12, "text")]
scheme37 = [("a", "R=R'=H"), ("b", "R=H, R'=Me"), ("c", "R=Me, R'=H")]
for suffix, substitution in scheme37:
    add_lit(
        f"scheme37_complex142_allenyl_bromide_to_143{suffix}", e1112,
        [mol("complex142", "reactant", "[CpFe(CO)2]Na complex 142", e1112),
         mol("bromide", "reactant", f"3,4-allenylic bromide ({substitution})", e1112),
         mol("thf", "solvent", "THF", e1112),
         mol("product143", "product", f"3,4-allenyl iron complex 143{suffix}", e1112)],
        notes=["Scheme 37 shows loss of NaBr."],
    )
    add_lit(
        f"scheme37_complex143{suffix}_to_144{suffix}", e1112,
        [mol("complex143", "reactant", f"3,4-allenyl iron complex 143{suffix}", e1112),
         mol("thf", "solvent", "THF", e1112),
         mol("product144", "product", f"cyclic allyl iron complex 144{suffix}", e1112)],
        conditions=[field("temperature", {"number": 60, "unit": "°C"}, e1112),
                    field("time", {"number": 24, "unit": "h"}, e1112)],
        notes=["The review describes this stage as CO and intramolecular allene insertion."],
    )
add_lit(
    "scheme37_complex133_allenyl_bromide_to_145", e1112,
    [mol("complex133", "reactant", "Na2Fe(CO)4 complex 133", e1112),
     mol("bromide", "reactant", "3,4-allenylic bromide shown in Scheme 37", e1112),
     mol("product145", "product", "cyclic allyl iron complex 145", e1112)],
)
add_lit(
    "scheme37_complex145_tmscl_to_146", e1112,
    [mol("complex145", "reactant", "cyclic allyl iron complex 145", e1112),
     mol("tmscl", "reagent", "trimethylsilyl chloride", e1112),
     mol("product146", "product", "silyloxy iron complex 146", e1112)],
)
add_lit(
    "scheme38_complex147_nucleophile_family_to_148", e1112,
    [mol("complex147", "reactant", "cationic coordinated-allene iron complex 147 (R=Me or Ph)", e1112),
     mol("nucleophile", "reagent", "NaBH4, NHEt2, or PPh3", e1112),
     mol("product148", "product", "vinyl iron complex family 148", e1112)],
    unresolved=["The generic arrow covers two R groups and three nucleophiles without a variant-specific outcome matrix."],
)
add_lit(
    "scheme38_complex147_naoet_to_149", e1112,
    [mol("complex147", "reactant", "cationic coordinated-allene iron complex 147", e1112),
     mol("naoet", "reagent", "sodium ethoxide", e1112),
     mol("product149", "product", "ethoxycarbonyl iron intermediate 149", e1112)],
    notes=["The review calls 149 a presumed intermediate."],
    unresolved=["Intermediate 149 is proposed/presumed and no isolation is stated."],
)
add_mech(
    "scheme38_intermediate149_to_150", e1112,
    [mol("intermediate149", "reactant", "presumed ethoxycarbonyl iron intermediate 149", e1112),
     mol("product150", "product", "allyl iron complex 150", e1112)],
    outcomes=[field("mechanistic_status", "proposed conversion to observed complex 150", e1112, ["product150"])],
    unresolved=["The 149-to-150 step is a proposed pathway rather than an independently specified experiment."],
)


# Page 12, Schemes 39 and 40 plus the prose-only Scheme 41 result.
e12 = [ev(12, "image"), ev(12, "text")]
for suffix, substrate, r_value in [
    ("a", "1,2-propadiene", "R=H"),
    ("b", "phenylallene", "R=Ph"),
    ("c", "methyl 2,3-butadienoate", "R=CO2Me"),
]:
    add_lit(
        f"scheme39_complex151_{suffix}_to_152{suffix}", e12,
        [mol("complex151", "reactant", "RuHCl(CO)(PPh3)3 complex 151", e12),
         mol("allene", "reactant", substrate, e12),
         mol("product152", "product", f"pi-allyl ruthenium complex 152{suffix} ({r_value})", e12)],
    )
add_lit(
    "scheme39_complex151_dimethylallene_to_152d", e12,
    [mol("complex151", "reactant", "RuHCl(CO)(PPh3)3 complex 151", e12),
     allene("allene", "1,1-dimethylallene", e12),
     mol("product152d", "product", "endo/exo pi-allyl ruthenium complex 152d", e12)],
)
add_lit(
    "scheme39_complex152d_on_standing_to_152e", e12,
    [mol("complex152d", "reactant", "pi-allyl ruthenium complex 152d", e12),
     mol("product152e", "product", "isomeric eta3-allyl ruthenium complex 152e", e12)],
    conditions=[field("time", "on standing", e12)],
    notes=["The review states that isomerization occurs slowly in solution or in the solid state."],
)
for suffix, substrate, r_value in [
    ("ph", "phenylallene", "R1=Ph"),
    ("co2et", "ethyl 2,3-butadienoate", "R1=CO2Et"),
    ("c5h11", "1,2-octadiene", "R1=C5H11"),
]:
    add_lit(
        f"scheme40_complex153_{suffix}_to_154", e12,
        [mol("complex153", "reactant", "RuH(NO)(PPh3)3 complex 153", e12),
         mol("allene", "reactant", substrate, e12),
         mol("product154", "product", f"eta3-allyl ruthenium complex 154 ({r_value})", e12)],
    )
add_lit(
    "page12_complex153_disubstituted_allenes_no_insertion", e12,
    [mol("complex153", "reactant", "RuH(NO)(PPh3)3 complex 153", e12),
     mol("allene", "reactant", "disubstituted allenes", e12)],
    outcomes=[field("insertion_product", "not formed", e12)],
    notes=["The review explicitly contrasts this negative result with terminal-allene insertion."],
    unresolved=["The individual disubstituted allenes and full conditions are not specified on the covered page."],
)
add_lit(
    "scheme40_complex155_arylallene_family_to_156", e12,
    [mol("complex155", "reactant", "ruthenium hydride complex family 155 with a chelating bidentate ligand", e12),
     mol("allene", "reactant", "arylallene family (R=Ph, tolyl, or p-tert-butylphenyl)", e12),
     mol("product156", "product", "allyl ruthenium complex family 156", e12)],
    unresolved=["The ligand/allene family is shown generically and variant-specific conditions and yields are absent."],
)
add_lit(
    "page12_complex157_tertbutylallene_to_158", e12,
    [mol("complex157", "reactant", "CO-free ruthenium hydride complex 157", e12),
     mol("allene", "reactant", "CH2=C=CHCMe3", e12),
     mol("product158", "product", "vinyl ruthenium complex 158", e12)],
    notes=["The reaction is stated in page-12 prose; Scheme 41 itself is on the following page and is not claimed as inspected here."],
    unresolved=["The covered prose omits reaction conditions, yield, and complete procedure."],
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
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 17 and adjacent prose", "finding": "Four generic/variant palladium insertion arrows were extracted as cited literature examples; unresolved family matrices were not expanded speculatively.", "evidence_ids": [ev(7, "image"), ev(7, "text")]},
                {"region": "lower Scheme 18", "finding": "Three Pd(p-An-BIAN) family arrows were extracted; the 65d arrow retains CH2Cl2 and 20 °C.", "evidence_ids": [ev(7, "image"), ev(7, "text")]},
                {"region": "upper-right Scheme 19", "finding": "The complex-69 family arrow and its NaClO4/CH2Cl2 conditions were extracted; the complex-71 continuation is linked across page 8.", "evidence_ids": [ev(7, "image"), ev(7, "text"), ev(8, "image")]},
            ],
            "record_ids": ids_for_page(7),
            "unresolved": ["Schemes 17-19 contain family matrices without variant-specific yields or complete primary procedures."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "upper Schemes 20 and 21", "finding": "Two tridentate-ligand family arrows and two pyridylbisthioether insertion arrows were extracted as literature examples.", "evidence_ids": [ev(8, "image"), ev(8, "text")]},
                {"region": "lower Scheme 22", "finding": "Four explicitly lettered PdCl(R)(COD) variants were split and retain the stated room-temperature condition.", "evidence_ids": [ev(8, "image"), ev(8, "text")]},
                {"region": "lower-right platinum discussion", "finding": "Narrative conditions for Schemes 23-24 on page 9 were merged with the corresponding image records rather than duplicated.", "evidence_ids": [ev(8, "image"), ev(8, "text"), ev(9, "image")]},
            ],
            "record_ids": ids_for_page(8),
            "unresolved": ["Most family arrows omit scale, yield, atmosphere, workup, and purification."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 23-25", "finding": "Three platinum-hydride insertions, preparation/insertion family 89-91, the 92-to-93 metallacycle, and temperature-staged 94-96 transformations were extracted.", "evidence_ids": [ev(9, "image"), ev(9, "text"), ev(8, "text")]},
                {"region": "upper-right Schemes 26 and 27", "finding": "Three Scheme-26 arrows and three ratio/temperature-specific Scheme-27 routes were extracted; the possible Pt-Si insertion remains an unresolved mechanistic interpretation.", "evidence_ids": [ev(9, "image"), ev(9, "text")]},
                {"region": "lower group-9 discussion", "finding": "Prose conditions for Schemes 28-29 were linked to page-10 arrows.", "evidence_ids": [ev(9, "image"), ev(9, "text"), ev(10, "image")]},
            ],
            "record_ids": ids_for_page(9),
            "unresolved": ["Most platinum examples lack primary-paper scales, yields, atmosphere, workup, and purification."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 28-30 and lower Scheme 29", "finding": "Four cobalt insertion arrows, three staged carbonylative metallations, seven explicitly lettered RhH(CO)(PPh3)3 variants, and the 118-to-119 arrow were extracted.", "evidence_ids": [ev(10, "image"), ev(10, "text"), ev(9, "text")]},
                {"region": "upper-right Scheme 31", "finding": "Six arylallene variants retain 1:5 stoichiometry, room temperature, and >80% yield; proposed intermediates 122-124 are a mechanism record.", "evidence_ids": [ev(10, "image"), ev(10, "text")]},
                {"region": "middle-right Scheme 32 and prose", "finding": "Two acid-dependent products, one prose-only rhodium-dihydride insertion, two alternative routes to 121a, and a cited computational mechanism were retained separately.", "evidence_ids": [ev(10, "image"), ev(10, "text")]},
            ],
            "record_ids": ids_for_page(10),
            "unresolved": ["Alternative routes and the computational study omit complete experimental details; exact organometallic connectivity remains unverified."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 33 and 34", "finding": "Five explicitly resolved iridium variants, the depicted 131-to-132 iron insertion, and the prose-only analogous propadiene result were extracted.", "evidence_ids": [ev(11, "image"), ev(11, "text"), ev(10, "text")]},
                {"region": "upper-right Scheme 35", "finding": "The acyl-intermediate preparation, three allene variants, and two downstream derivatizations were retained as distinct arrows.", "evidence_ids": [ev(11, "image"), ev(11, "text")]},
                {"region": "lower Scheme 36", "finding": "Three family/branch reactions of complex 138 were extracted; variant matrices and cyclic-allene connectivity remain unresolved.", "evidence_ids": [ev(11, "image"), ev(11, "text")]},
                {"region": "right-column discussion of Schemes 37-39", "finding": "Cross-page narrative was merged with the page-12 arrows and not counted twice.", "evidence_ids": [ev(11, "image"), ev(11, "text"), ev(12, "image")]},
            ],
            "record_ids": ids_for_page(11),
            "unresolved": ["Scheme 36 does not map every R/R'/X family member to separate products or yields."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 37 and 38", "finding": "Three two-stage intramolecular insertion variants, two Na2Fe(CO)4 route arrows, a generic nucleophile family, and the proposed 149-to-150 pathway were extracted.", "evidence_ids": [ev(12, "image"), ev(12, "text"), ev(11, "text")]},
                {"region": "lower Scheme 39", "finding": "Three RuHCl(CO)(PPh3)3 substrate variants, the 152d formation, and its slow on-standing isomerization to 152e were retained separately.", "evidence_ids": [ev(12, "image"), ev(12, "text")]},
                {"region": "right Scheme 40 and adjacent prose", "finding": "Three terminal-allene variants, the explicit disubstituted-allene failure, a generic complex-155 family, and the prose-only 157-to-158 result were extracted.", "evidence_ids": [ev(12, "image"), ev(12, "text")]},
            ],
            "record_ids": ids_for_page(12),
            "unresolved": ["Scheme 41 is outside the covered range; only its page-12 prose statement is represented. Most cited examples lack complete primary procedures and yields."],
        },
    ],
}


raw_path = RUN / "raw_model" / "records_pages_0007_0012.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage_path = RUN / "coverage" / "pages_0007_0012.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(7, 13)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "raw": str(raw_path)}, ensure_ascii=False))
