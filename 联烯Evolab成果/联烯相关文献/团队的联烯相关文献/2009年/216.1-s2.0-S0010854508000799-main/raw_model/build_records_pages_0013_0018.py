#!/usr/bin/env python3
"""Build evidence-linked review records for doc_0a0328e571461b17, PDF pages 13--18."""

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
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "1,2-propadiene": "C=C=C",
    "allene": "C=C=C",
    "1-methylallene": "C=C=CC",
    "1,1-dimethylallene": "C=C=C(C)C",
    "phenylallene": "C=C=Cc1ccccc1",
    "carbon monoxide": "[C-]#[O+]",
    "water": "O",
    "trimethylamine": "CN(C)C",
    "benzene": "c1ccccc1",
    "toluene": "Cc1ccccc1",
    "dichloromethane": "ClCCl",
    "THF": "C1CCOC1",
    "acetonitrile": "CC#N",
    "n-hexane": "CCCCCC",
    "n-octane": "CCCCCCCC",
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


def mol(entity_id, role, label, evidence, *, smiles=None, amounts=()):
    return participant(entity_id, role, label, evidence, smiles=smiles, amounts=amounts)


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
                "Organometallic connectivity and coordination mode require chemistry review.",
            ],
        },
    }


records = []


def add_lit(rid, evidence, participants, **kwargs):
    records.append(base_record(rid, "literature_example", evidence, participants, **kwargs))


def add_mech(rid, evidence, participants, **kwargs):
    records.append(base_record(rid, "mechanism", evidence, participants, **kwargs))


# Page 13, Scheme 41. This replaces/enriches the existing page-12 prose record,
# rather than creating a duplicate reaction.
e1213 = [ev(12, "image"), ev(12, "text"), ev(13, "image"), ev(13, "text")]
add_lit(
    "page12_complex157_tertbutylallene_to_158", e1213,
    [mol("complex157", "reactant", "CO-free ruthenium hydride complex 157", e1213),
     mol("allene", "reactant", "CH2=C=CHCMe3", e1213),
     mol("product158", "product", "vinyl ruthenium complex 158", e1213)],
    notes=["The page-12 prose and page-13 Scheme 41 describe the same literature reaction."],
    unresolved=["The review omits scale, time, temperature, atmosphere, workup, purification, and yield."],
)


# Page 13, Scheme 42. Six explicit 159a/159b combinations and two 159c/159d
# phenylallene cases are kept separate; no unsupported Cartesian expansion is used.
e13 = [ev(13, "image"), ev(13, "text")]
scheme42_main = [
    ("160a", "159a (R1=Ph)", "phenylallene (R2=Ph)"),
    ("160b", "159a (R1=Ph)", "allene with R2=CO2Me"),
    ("160c", "159a (R1=Ph)", "allene with R2=COMe"),
    ("160d", "159a (R1=Ph)", "methoxyallene (R2=OMe)"),
    ("161a", "159b (R1=CO2Me)", "phenylallene (R2=Ph)"),
    ("161b", "159b (R1=CO2Me)", "allene with R2=CO2Me"),
]
for product, start, substrate in scheme42_main:
    add_lit(
        f"scheme42_complex{start.split()[0]}_{product}", e13,
        [mol("complex159", "reactant", f"alkenyl ruthenium complex {start}", e13),
         mol("allene", "reactant", substrate, e13),
         mol("product", "product", f"vinylmetallated eta3-allyl ruthenium complex {product}", e13)],
        outcomes=[field("product_selectivity", "only product", e13, ["product"]),
                  field("reported_yield", "good yield", e13, ["product"]),
                  field("yield_measurement_basis", None)],
    )
for suffix, start in [("a", "159c (R1=SiMe3)"), ("b", "159d (R1=n-Bu)")]:
    add_lit(
        f"scheme42_complex{start.split()[0]}_phenylallene_to_162{suffix}_152b", e13,
        [mol("complex159", "reactant", f"alkenyl ruthenium complex {start}", e13),
         allene("phenylallene", "phenylallene", e13),
         mol("product162", "product", f"carbometallated eta3-allyl ruthenium complex 162{suffix}", e13),
         mol("product152b", "product", "hydrometallation product 152b", e13)],
        outcomes=[field("major_product", "complex 162", e13, ["product162"]),
                  field("minor_product", "complex 152b", e13, ["product152b"]),
                  field("reported_yield", None, targets=["product162", "product152b"]),
                  field("yield_measurement_basis", None)],
    )


# Page 13, Scheme 43.
for suffix, substrate in [("a", "phenylallene"), ("b", "benzylallene (R=CH2Ph)")]:
    add_lit(
        f"scheme43_complex163_{suffix}_to_164{suffix}", e13,
        [mol("complex163", "reactant", "OsHCl(CO)(PPh3)3 complex 163", e13),
         mol("allene", "reactant", substrate, e13),
         mol("product164", "product", f"allyl osmium complex 164{suffix}", e13)],
    )
for suffix, substrate in [("a", "tert-butylallene (R=CMe3)"), ("b", "phenylallene"), ("c", "ethyl allenoate (R=CO2Et)")]:
    add_lit(
        f"scheme43_complex165_{suffix}_to_166{suffix}", e13,
        [mol("complex165", "reactant", "CO-free OsHCl(PPh3)3 complex 165", e13),
         mol("allene", "reactant", substrate, e13),
         mol("product166", "product", f"vinyl osmium complex 166{suffix}", e13)],
    )


# Page 13, Scheme 44: three explicitly listed electrophile variants plus the
# proposed 169/170 pathway.
for suffix, substitution in [("a", "R1=R2=H"), ("b", "R1=R2=Me"), ("c", "R1=H, R2=Me")]:
    add_lit(
        f"scheme44_complex167_allenic_electrophile_to_168{suffix}", e13,
        [mol("complex167", "reactant", "Na[CpMo(CO)3] complex 167", e13),
         mol("electrophile", "reactant", f"allenic tosylate electrophile ({substitution})", e13),
         mol("product168", "product", f"eta3-2-alkylidene cyclobutanone molybdenum complex 168{suffix}", e13)],
    )
add_mech(
    "scheme44_proposed_intermediates169_170", e13,
    [mol("complex167", "reactant", "Na[CpMo(CO)3] complex 167", e13),
     mol("electrophile", "reactant", "allenic tosylate electrophile family", e13),
     mol("intermediate169", "product", "allenyl molybdenum intermediate 169", e13),
     mol("intermediate170", "product", "acyl intermediate 170 after CO insertion", e13),
     mol("product168", "product", "cyclobutanone complex family 168", e13)],
    outcomes=[field("mechanistic_status", "postulated CO insertion followed by intramolecular allene insertion", e13,
                    ["intermediate169", "intermediate170", "product168"])],
    unresolved=["Intermediates 169 and 170 are postulated and are not stated to be isolated."],
)


# Page 14, Scheme 45.
e14 = [ev(14, "image"), ev(14, "text")]
add_lit(
    "scheme45_complex171_allenyl_bromide_to_172_family", e14,
    [mol("complex171", "reactant", "[CpMo(CO)2L]- complex family 171a-d", e14),
     mol("bromide", "reactant", "3,4-allenyl bromide family (R=H or Me)", e14),
     mol("thf", "solvent", "THF", e14),
     mol("product172", "product", "3,4-allenyl molybdenum complex family 172", e14)],
    conditions=[field("temperature", "ambient temperature", e14)],
    unresolved=["The review gives a ligand/substrate family rather than variant-specific procedures or yields."],
)
add_lit(
    "scheme45_complex172_co_allene_insertion_to_173_family", e14,
    [mol("complex172", "reactant", "3,4-allenyl molybdenum complex family 172", e14),
     mol("thf", "solvent", "THF", e14),
     mol("product173", "product", "allyl molybdenum complex family 173 with a cyclopentanone unit", e14)],
    conditions=[field("operation", "CO insertion and intramolecular allene insertion", e14)],
    unresolved=["The scheme labels CO insertion but does not state whether external CO was introduced or released from the complex."],
)


# Page 14, Scheme 46.
add_lit(
    "scheme46_complex174_nme3_water_to_175", e14,
    [mol("complex174", "reactant", "cationic molybdenum allene complex 174", e14),
     mol("nme3", "reagent", "trimethylamine", e14), mol("water", "reagent", "water", e14),
     mol("mecn", "solvent", "acetonitrile", e14),
     mol("product175", "product", "anti-eta3-allyl molybdenum complex 175", e14)],
    outcomes=[field("reported_yield", {"number": 74, "unit": "%"}, e14, ["product175"]),
              field("yield_measurement_basis", None)],
)
add_lit(
    "scheme46_complex174_kscn_water_to_176", e14,
    [mol("complex174", "reactant", "cationic molybdenum allene complex 174", e14),
     mol("kscn", "reagent", "potassium thiocyanate", e14), mol("water", "reagent", "water", e14),
     mol("product176", "product", "eta3-2-hydroxycarbonylallyl molybdenum complex 176", e14)],
)
add_mech(
    "scheme46_common_intermediate177_to_175", e14,
    [mol("intermediate177", "reactant", "proposed common hydroxycarbonyl intermediate 177", e14),
     mol("product175", "product", "anti-eta3-allyl molybdenum complex 175", e14)],
    outcomes=[field("mechanistic_status", "proposed CO2 extrusion to a hydride followed by allene insertion", e14, ["product175"])],
    unresolved=["Intermediate 177 and the hydride are proposed; isolation is not stated."],
)
for suffix, substrate in [("a", "1,2-propadiene (R=H)"), ("b", "triphenylmethyl-substituted allene (R=CPh3)")]:
    add_lit(
        f"scheme46_complex178_{suffix}_to_179{suffix}", e14,
        [mol("complex178", "reactant", "molybdenum complex 178", e14),
         mol("allene", "reactant", substrate, e14),
         mol("product179", "product", f"acylmetallated allyl molybdenum complex 179{suffix}", e14)],
    )


# Page 14, Scheme 47.
add_lit(
    "scheme47_complex180_benzylamide_to_181", e14,
    [mol("complex180", "reactant", "cationic tungsten allene complex 180", e14),
     mol("bnnh", "reagent", "benzylamide anion (BnNH-)", e14),
     mol("product181", "product", "eta3-allyl tungsten complex 181", e14)],
)
add_lit(
    "scheme47_complex182_gaseous_allene_to_183", e14,
    [mol("complex182", "reactant", "bimetallic tungsten acyl complex 182", e14),
     allene("allene", "allene", e14), mol("dcm", "solvent", "dichloromethane", e14),
     mol("product183", "product", "dinuclear acylmetallated allyl tungsten complex 183", e14)],
    outcomes=[field("reported_yield", {"number": 92, "unit": "%"}, e14, ["product183"]),
              field("yield_measurement_basis", None)],
    notes=["The review specifies gaseous allene."],
)


# Page 14, Scheme 48.
add_lit(
    "scheme48_complex184_excess_allene_to_185", e14,
    [mol("complex184", "reactant", "Cp*2TaH3 complex 184", e14),
     allene("allene", "allene", e14), mol("solvent", "solvent", "benzene or toluene", e14),
     mol("product185", "product", "eta3-allyl tantalum complex 185", e14),
     mol("hydrogen", "product", "hydrogen", e14, smiles="[H][H]"),
     mol("propene", "product", "propene", e14, smiles="CC=C")],
    conditions=[field("temperature", {"number": 80, "unit": "°C"}, e14)],
    notes=["The scheme labels allene as excess."],
)
add_lit(
    "scheme48_complex186_allene_to_187_in_situ", e14,
    [mol("complex186", "reactant", "chiral tantalum hydride complex (R,R)-186", e14),
     allene("allene", "1,2-propadiene", e14),
     mol("c6d6", "solvent", "C6D6", e14),
     mol("product187", "product", "allyl tantalum complex 187", e14)],
    outcomes=[field("observation_method", "observed by in situ NMR", e14, ["product187"]),
              field("preparative_result", "preparative attempt unsuccessful", e14, ["product187"]),
              field("reported_yield", None, targets=["product187"]), field("yield_measurement_basis", None)],
    notes=["Complex 187 was not stable in the absence of an allene atmosphere."],
    unresolved=["No isolable preparative product, yield, scale, time, or workup is reported."],
)


# Scheme 49 crosses pages 14--15.
e1415 = [ev(14, "image"), ev(14, "text"), ev(15, "image"), ev(15, "text")]
add_lit(
    "scheme49_complex188_allene_to_189", e1415,
    [mol("complex188", "reactant", "cationic zirconium hydride complex 188", e1415),
     allene("allene", "1,2-propadiene", e1415),
     mol("product189", "product", "pi-allyl zirconium complex 189", e1415)],
    outcomes=[field("reaction_rate", "rapid", e1415, ["product189"])],
)
add_lit(
    "scheme49_complex190_allene_to_191", e1415,
    [mol("complex190", "reactant", "cationic zirconium methyl complex 190", e1415),
     allene("allene", "1,2-propadiene", e1415),
     mol("product191", "product", "pi-allyl zirconium complex 191", e1415)],
    outcomes=[field("reaction_rate", "rapid", e1415, ["product191"])],
)
add_lit(
    "scheme49_complex192_allene_to_193", e1415,
    [mol("complex192", "reactant", "Cp*2HfH2 complex 192", e1415),
     allene("allene", "1,2-propadiene", e1415, equivalents=1),
     mol("product193", "product", "pi-allyl hafnium complex 193", e1415)],
    notes=["The review states a 1:1 reactant ratio."],
)


# Page 15, Schemes 50--52.
e15 = [ev(15, "image"), ev(15, "text")]
add_lit(
    "scheme50_complex194_excess_allene_to_195a_195b", e15,
    [mol("complex194", "reactant", "cyclometallated 6-phenylpyridyl zirconium complex 194", e15),
     allene("allene", "1,2-propadiene", e15),
     mol("dce", "solvent", "1,2-dichloroethane", e15, smiles="ClCCCl"),
     mol("product195a", "product", "vinyl zirconium complex 195a", e15),
     mol("product195b", "product", "allyl zirconium complex 195b", e15)],
    conditions=[field("temperature", {"number": 65, "unit": "°C"}, e15)],
    outcomes=[field("product_ratio", "195a:195b = 1:1", e15, ["product195a", "product195b"]),
              field("reported_yield", None, targets=["product195a", "product195b"]),
              field("yield_measurement_basis", None)],
    notes=["The review specifies excess 1,2-propadiene."],
)
for suffix, metal in [("a", "Cp2Zr"), ("b", "(MeCp)2Zr"), ("c", "Cp2Hf")]:
    add_lit(
        f"scheme50_complex196{suffix}_allene_to_197{suffix}", e15,
        [mol("complex196", "reactant", f"allyl metal complex 196{suffix} ({metal})", e15),
         allene("allene", "1,2-propadiene", e15),
         mol("product197", "product", f"vinyl metal complex 197{suffix} ({metal})", e15)],
    )
add_lit(
    "scheme51_complex198_excess_allene_to_199", e15,
    [mol("complex198", "reactant", "dimeric scandium hydride complex 198", e15),
     allene("allene", "allene", e15),
     mol("product199", "product", "eta3-allyl scandium complex 199", e15)],
    notes=["The review states that excess allene was used."],
)
add_lit(
    "page15_cpsc_hydride_allene_to_allyl", e15,
    [mol("hydride", "reactant", "unstable [Cp*2ScH]n hydride complex", e15),
     allene("allene", "allene", e15),
     mol("product", "product", "Cp*2Sc(eta3-CH2CHCH2) allyl complex", e15)],
    unresolved=["This prose-only literature example omits conditions, yield, and a compound number."],
)
add_lit(
    "scheme52_complex200a_allene_to_201a", e15,
    [mol("complex200a", "reactant", "hydrido-bridged dimolybdenum complex 200a", e15),
     allene("allene", "1,2-propadiene", e15, equivalents=2),
     mol("product201a", "product", "eta3-allyl dimolybdenum complex 201a", e15)],
    conditions=[field("operation", "photolysis", e15)],
    outcomes=[field("product_selectivity", "only product", e15, ["product201a"])],
)
add_lit(
    "scheme52_complex200b_dimethylallene_to_201b", e15,
    [mol("complex200b", "reactant", "hydrido-bridged Mo-Mn complex 200b", e15),
     allene("allene", "1,1-dimethylallene", e15),
     mol("solvent", "solvent", "hexane-benzene", e15),
     mol("product201b", "product", "allyl bimetallic complex 201b", e15)],
    conditions=[field("operation", "photolysis", e15)],
    outcomes=[field("product_selectivity", "only product", e15, ["product201b"])],
)
add_lit(
    "scheme52_complex200b_allene_to_201c_201d_201e", e15,
    [mol("complex200b", "reactant", "hydrido-bridged Mo-Mn complex 200b", e15),
     allene("allene", "1,2-propadiene", e15),
     mol("solvent", "solvent", "hexane-benzene", e15),
     mol("product201c", "product", "allyl bimetallic complex 201c", e15),
     mol("product201d", "product", "allyl bimetallic complex 201d", e15),
     mol("product201e", "product", "allyl bimetallic complex 201e", e15)],
    conditions=[field("operation", "photolysis", e15)],
    outcomes=[field("product_mixture", "complexes 201c-201e", e15, ["product201c", "product201d", "product201e"]),
              field("reported_yield", None, targets=["product201c", "product201d", "product201e"]),
              field("yield_measurement_basis", None)],
)


# Page 16, Scheme 53.
e16 = [ev(16, "image"), ev(16, "text")]
for suffix, substitution in [("a", "R1=Me, R2=H"), ("b", "R1=R2=Me"), ("c", "R1=H, R2=Et")]:
    add_lit(
        f"scheme53_complex202{suffix}_allene_to_203{suffix}", e16,
        [mol("complex202", "reactant", f"vinyl-bridged dimolybdenum complex 202{suffix} ({substitution})", e16),
         allene("allene", "1,2-propadiene", e16),
         mol("product203", "product", f"vinylmetallated eta3-allyl dimolybdenum complex 203{suffix}", e16)],
        conditions=[field("operation", "photolysis", e16)],
    )


# Page 16, Scheme 54. Each temperature-defined arrow is a separate stage for
# each of the two explicitly reported monosubstituted allenes.
for suffix, substrate, r_value in [("h", "1,2-propadiene", "R=H"), ("me", "1-methylallene", "R=Me")]:
    add_lit(
        f"scheme54_complex204_{suffix}_to_205", e16,
        [mol("complex204", "reactant", "[Ir2(CH3)(CO)(mu-CO)(dppm)2][CF3SO3] complex 204", e16),
         allene("allene", substrate, e16), mol("cd2cl2", "solvent", "CD2Cl2", e16),
         mol("product205", "product", f"eta2-allene iridium complex 205 ({r_value})", e16)],
        conditions=[field("temperature", {"number": -60, "unit": "°C"}, e16)],
    )
    add_lit(
        f"scheme54_complex205_{suffix}_to_206", e16,
        [mol("complex205", "reactant", f"eta2-allene iridium complex 205 ({r_value})", e16),
         mol("product206", "product", f"2-metallated allyl iridium complex 206 ({r_value})", e16)],
        conditions=[field("temperature", {"number": -10, "unit": "°C"}, e16)],
    )
    add_lit(
        f"scheme54_complex206_{suffix}_to_207", e16,
        [mol("complex206", "reactant", f"2-metallated allyl iridium complex 206 ({r_value})", e16),
         mol("product207", "product", f"2-methylated allyl iridium complex 207 ({r_value})", e16)],
        conditions=[field("temperature", "room temperature", e16)],
    )
add_lit(
    "scheme54_complex204_difluoroallene_to_208", e16,
    [mol("complex204", "reactant", "iridium complex 204", e16),
     mol("allene", "reactant", "1,1-difluoroallene (CH2=C=CF2)", e16),
     mol("product208", "product", "simple coordination complex 208", e16)],
    outcomes=[field("insertion_result", "no insertion; simple coordination only", e16, ["product208"])],
)
add_lit(
    "scheme54_complex204_dimethylallene_to_209", e16,
    [mol("complex204", "reactant", "iridium complex 204", e16),
     allene("allene", "1,1-dimethylallene", e16),
     mol("product209", "product", "simple coordination complex 209", e16)],
    outcomes=[field("insertion_result", "no insertion; simple coordination only", e16, ["product209"])],
)


# Page 16, Scheme 55.
add_lit(
    "scheme55_complex210_allene_to_211", e16,
    [mol("complex210", "reactant", "methylene-bridged Ni-W complex 210", e16),
     allene("allene", "1,2-propadiene", e16), mol("hexane", "solvent", "n-hexane", e16),
     mol("product211", "product", "trimethylenemethane Ni-W complex 211", e16)],
    outcomes=[field("reported_yield", {"number": 74, "unit": "%"}, e16, ["product211"]),
              field("yield_measurement_basis", None),
              field("chemoselectivity", "chemoselective formal insertion into the Ni-CH2 bond", e16, ["product211"])],
)
for suffix, start, product in [
    ("a", "Rh-Os methylene-bridged complex 212a (X=BF4)", "trimethylenemethane-bridged complex 213a"),
    ("b", "Rh-Ru methylene-bridged complex 212b (X=CF3SO3)", "trimethylenemethane-bridged complex 213b"),
]:
    add_lit(
        f"scheme55_complex212{suffix}_allene_to_213{suffix}", e16,
        [mol("complex212", "reactant", start, e16), allene("allene", "1,2-propadiene", e16),
         mol("product213", "product", product, e16)],
    )
add_lit(
    "page16_complex212a_methylallene_to_213a_analogue", e16,
    [mol("complex212a", "reactant", "Rh-Os methylene-bridged complex 212a", e16),
     allene("allene", "1-methylallene", e16),
     mol("product", "product", "methyl-substituted trimethylenemethane-bridged Rh-Os complex analogous to 213a", e16)],
    unresolved=["The prose gives no separate compound number, conditions, or yield."],
)
add_lit(
    "scheme55_complex214_allene_to_215", e16,
    [mol("complex214", "reactant", "methylene-bridged Ru-Ru complex 214", e16),
     allene("allene", "1,2-propadiene", e16),
     mol("product215", "product", "trimethylenemethane-bridged Ru-Ru complex 215", e16)],
)


# Page 16, Scheme 56. The allene substitution list is a family; starting
# complexes 216--218 map explicitly to product families 219--221.
for start, product, ligands in [
    ("216", "219", "X2=(CH2SiMe3)2"),
    ("217", "220", "X2=(CH2SiMe3)(OBu-t)"),
    ("218", "221", "X2=(OPr-i)2"),
]:
    add_lit(
        f"scheme56_complex{start}_allene_family_to_{product}", e16,
        [mol("complex", "reactant", f"alkylidyne-bridged ditungsten complex {start} ({ligands})", e16),
         mol("allene", "reactant", "allene family shown in Scheme 56 (R1/R2=H, Me, or Ph)", e16),
         mol("product", "product", f"C-C-coupled bimetallic complex family {product}", e16)],
        unresolved=["The scheme does not map each allene substitution pattern to variant-specific conditions or yields."],
    )


# Page 17, Scheme 57 and prose-only related examples.
e17 = [ev(17, "image"), ev(17, "text")]
add_lit(
    "scheme57_complex222_dimethylallene_to_223", e17,
    [mol("complex222", "reactant", "alkyne-bridged Ru-Co complex 222", e17),
     allene("allene", "1,1-dimethylallene", e17), mol("hexane", "solvent", "n-hexane", e17),
     mol("product223", "product", "allene-alkyne C-C coupled Ru-Co complex 223", e17)],
    conditions=[field("temperature", "room temperature", e17)],
)
add_lit(
    "scheme57_complex224_alkyne_to_225_226", e17,
    [mol("complex224", "reactant", "allene-bridged dimolybdenum complex 224", e17),
     mol("alkyne", "reactant", "dimethyl acetylenedicarboxylate (R=CO2Me)", e17),
     mol("octane", "solvent", "n-octane", e17),
     mol("product225", "product", "C-C coupled complex 225", e17),
     mol("product226", "product", "C-C coupled complex 226", e17)],
    conditions=[field("temperature", "reflux", e17), field("time", {"number": 16, "unit": "h"}, e17)],
    outcomes=[field("isolated_yield_225", {"number": 19, "unit": "%"}, e17, ["product225"]),
              field("isolated_yield_226", {"number": 24, "unit": "%"}, e17, ["product226"]),
              field("yield_measurement_basis", "isolated", e17)],
)
for suffix, complex_label in [
    ("w", "dinuclear W(OR)6(Py)(mu-HC=CH) complex"),
    ("os", "Os4(CO)11(mu-HC=CCO2Me)(mu4-S) cluster"),
]:
    add_lit(
        f"page17_{suffix}_bridging_alkyne_allene_coupling", e17,
        [mol("complex", "reactant", complex_label, e17), allene("allene", "allene", e17)],
        outcomes=[field("observed_transformation", "C-C bond formation with a bridging alkyne ligand", e17)],
        unresolved=["The review gives no product label, conditions, yield, or complete procedure for this prose-only example."],
    )


# Page 17, Scheme 58.
add_lit(
    "scheme58_complex112_allene_to_227", e17,
    [mol("complex112", "reactant", "Co2(CO)8 complex 112", e17),
     allene("allene", "allene", e17),
     mol("product227", "product", "acyl-allyl dicobalt complex 227", e17)],
)
add_lit(
    "scheme58_complex228_allene_to_229_232", e17,
    [mol("complex228", "reactant", "Fe(CO)5 complex 228", e17),
     allene("allene", "allene", e17),
     mol("product229", "product", "iron allene insertion complex 229", e17),
     mol("product232", "product", "carbonylative iron-allene complex 232", e17)],
    conditions=[field("operation", "photolysis", e17)],
    outcomes=[field("observed_products", "complexes 229 and 232", e17, ["product229", "product232"]),
              field("reported_yield", None, targets=["product229", "product232"]),
              field("yield_measurement_basis", None)],
)
add_mech(
    "scheme58_intermediates230_231", e17,
    [mol("complex229", "reactant", "iron complex 229", e17),
     allene("allene", "allene", e17),
     mol("intermediate230", "product", "decarbonylated intermediate 230", e17),
     mol("intermediate231", "product", "second-allene intermediate 231", e17),
     mol("product232", "product", "iron complex 232", e17)],
    outcomes=[field("mechanistic_status", "scheme pathway 229 <-> 230, 230 + allene -> 231, and 231 <-> 232", e17,
                    ["intermediate230", "intermediate231", "product232"])],
    unresolved=["The review calls 230 and 231 intermediates and does not provide independent batch conditions or yields."],
)
add_lit(
    "page17_complex228_phenylallene_to_229_232_analogues", e17,
    [mol("complex228", "reactant", "Fe(CO)5 complex 228", e17),
     allene("phenylallene", "phenylallene", e17),
     mol("products", "product", "complexes analogous to 229 and 232", e17)],
    unresolved=["The prose-only phenylallene example gives no compound numbers, conditions, or yields."],
)


# Scheme 59 crosses pages 17--18.
e1718 = [ev(17, "image"), ev(17, "text"), ev(18, "image"), ev(18, "text")]
add_lit(
    "scheme59_complex233_decarbonylation_to_237", e1718,
    [mol("complex233", "reactant", "carbonyl-bridged diiron complex 233", e1718),
     mol("thf", "solvent", "THF", e1718),
     mol("product237", "product", "phosphido-bridged diiron complex 237", e1718)],
    conditions=[field("temperature", "heated", e1718)],
    notes=["The review describes formation of 237 by decarbonylation of 233."],
)
add_lit(
    "scheme59_complex233_allene_to_234", e1718,
    [mol("complex233", "reactant", "carbonyl-bridged diiron complex 233", e1718),
     allene("allene", "1,2-propadiene", e1718),
     mol("product234", "product", "pi-allyl diiron complex 234", e1718)],
    conditions=[field("operation", "photolysis with decarbonylation", e1718)],
)
add_lit(
    "scheme59_complex234_heat_to_235", e1718,
    [mol("complex234", "reactant", "pi-allyl diiron complex 234", e1718),
     mol("thf", "solvent", "THF", e1718),
     mol("product235", "product", "decarbonylated diiron complex 235", e1718)],
    conditions=[field("temperature", "heated", e1718)],
)
add_lit(
    "scheme59_complex235_allene_to_236", e1718,
    [mol("complex235", "reactant", "decarbonylated diiron complex 235", e1718),
     allene("allene", "1,2-propadiene", e1718),
     mol("product236", "product", "carbometallated 2,2'-bisallyl diiron complex 236", e1718)],
    notes=["Scheme 59 labels loss of CO."],
)
add_lit(
    "scheme59_complex237_allene_to_238", e1718,
    [mol("complex237", "reactant", "phosphido-bridged diiron complex 237", e1718),
     allene("allene", "1,2-propadiene", e1718),
     mol("product238", "product", "pi-allyl diiron complex 238", e1718)],
    notes=["Allene inserts into the Fe-P bond rather than the Fe-CH2 bond; Scheme 59 labels loss of CO."],
)


# Scheme 60 crosses pages 17--18.
add_lit(
    "scheme60_complex239_allene_to_240", e1718,
    [mol("complex239", "reactant", "phosphido-bridged dicobalt complex 239", e1718),
     allene("allene", "1,2-propadiene", e1718),
     mol("product240", "product", "allyl dicobalt complex 240", e1718)],
    outcomes=[field("reported_yield", {"number": 81, "unit": "%"}, e1718, ["product240"]),
              field("yield_measurement_basis", None)],
)
add_lit(
    "scheme60_complex241_allene_to_242_243", e1718,
    [mol("complex241", "reactant", "phosphido-bridged dimanganese complex 241", e1718),
     allene("allene", "1,2-propadiene", e1718),
     mol("product242", "product", "allene-insertion dimanganese complex 242", e1718),
     mol("product243", "product", "allene-insertion dimanganese complex 243", e1718)],
    conditions=[field("operation", "photolysis", e1718)],
    outcomes=[field("isolated_yield_242", {"number": 5, "unit": "%"}, e1718, ["product242"]),
              field("isolated_yield_243", {"number": 12, "unit": "%"}, e1718, ["product243"]),
              field("yield_measurement_basis", "isolated", e1718),
              field("reaction_mixture", "at least 15 compounds", e1718, ["product242", "product243"])],
)


# Page 18, Schemes 61--64 and prose transformations.
e18 = [ev(18, "image"), ev(18, "text")]
add_lit(
    "scheme61_complex244_allene_to_245_246", e18,
    [mol("complex244", "reactant", "phosphido-bridged dicobalt complex 244", e18),
     allene("allene", "allene", e18), mol("toluene", "solvent", "toluene", e18),
     mol("product245", "product", "Co-C(O) insertion complex 245", e18),
     mol("product246", "product", "Co-P insertion/1,3-H-shift complex 246", e18)],
    conditions=[field("temperature", {"number": 338, "unit": "K"}, e18),
                field("operation", "allene slowly bubbled through the heated solution", e18)],
    outcomes=[field("isolated_yield_245", {"number": 13, "unit": "%"}, e18, ["product245"]),
              field("isolated_yield_246", {"number": 35, "unit": "%"}, e18, ["product246"]),
              field("yield_measurement_basis", "isolated", e18)],
)
add_lit(
    "page18_formal_allene_insertion_into_m_cp_bond", e18,
    [mol("start", "reactant", "CpNi(mu-eta1,eta3-CH2=C=CMe2)W(CO)2(eta5-C5H4Me)", e18),
     mol("product", "product", "(eta5-C5H4Me)W(CO)2(eta3-CH2C(C5H4)CMe2)", e18)],
    conditions=[field("temperature", "thermolysis", e18)],
    notes=["The review describes this as formal insertion of an allene unit into an M-Cp bond."],
    unresolved=["The prose-only example omits numeric temperature, time, solvent, scale, and yield."],
)
add_lit(
    "page18_cpd_palladium_isomerization", e18,
    [mol("start", "reactant", "CpPd(L)-Pd(L)(eta3-CH2CClCH2), L=PiPr3", e18),
     mol("product", "product", "(eta3-CH2C(C5H5)CH2)PdL2", e18)],
    outcomes=[field("transformation", "isomerization", e18, ["product"])],
    unresolved=["The related prose-only transformation omits conditions, scale, and yield."],
)
add_lit(
    "scheme62_complex247_allene_to_248_249", e18,
    [mol("complex247", "reactant", "[RhOsH(CO)3(dppm)2] complex 247", e18),
     allene("allene", "1,2-propadiene", e18),
     mol("product248", "product", "vinyl Rh-Os complex 248", e18),
     mol("product249", "product", "eta3-allyl Rh-Os complex 249", e18)],
    outcomes=[field("major_product", "complex 248", e18, ["product248"]),
              field("product_fraction_249", {"number": 10, "unit": "%", "qualifier": "approx", "raw_text": "approximately 10%"}, e18, ["product249"]),
              field("measurement_basis_249", "31P NMR", e18, ["product249"]),
              field("interconversion", "not observed even under heating", e18, ["product248", "product249"]),
              field("reported_yield", None, targets=["product248", "product249"]),
              field("yield_measurement_basis", None)],
)
add_lit(
    "scheme62_complex247_dimethylallene_to_250", e18,
    [mol("complex247", "reactant", "[RhOsH(CO)3(dppm)2] complex 247", e18),
     allene("allene", "1,1-dimethylallene", e18),
     mol("product250", "product", "vinyl Rh-Os complex 250", e18)],
    outcomes=[field("product_selectivity", "only product", e18, ["product250"])],
)
add_lit(
    "scheme62_complex251_allene_to_252", e18,
    [mol("complex251", "reactant", "Mn-Rh binuclear hydride complex 251", e18),
     allene("allene", "allene", e18),
     mol("product252", "product", "vinyl Mn-Rh complex 252", e18)],
)


# Schemes 63 and 64 are drawn on page 18; their outcome prose continues on
# page 19, used only as cross-page context (page 19 is not marked attempted).
e1819 = [ev(18, "image"), ev(18, "text"), ev(19, "text")]
add_lit(
    "scheme63_complex253_allene_to_254_255", e1819,
    [mol("complex253", "reactant", "hydrido-bridged diiron complex 253", e1819),
     allene("allene", "1,2-propadiene", e1819),
     mol("product254", "product", "2-propenyl diiron complex 254", e1819),
     mol("product255", "product", "2-propenyl diiron complex 255", e1819)],
    outcomes=[field("combined_yield_254_255", {"number": 70, "unit": "%"}, e1819, ["product254", "product255"]),
              field("product_ratio_254_255", "2:1", e1819, ["product254", "product255"]),
              field("measurement_basis", "1H NMR", e1819, ["product254", "product255"])],
)
add_lit(
    "scheme64_complex256_allene_photolysis_mixture", e1819,
    [mol("complex256", "reactant", "hydrido-bridged dimolybdenum complex 256", e1819),
     allene("allene", "1,2-propadiene", e1819, equivalents=2),
     mol("product257", "product", "2-propenyl dimolybdenum complex 257", e1819),
     mol("product258", "product", "eta3-allyl dimolybdenum complex 258", e1819),
     mol("product259", "product", "eta3-allyl dimolybdenum complex 259", e1819),
     mol("product260", "product", "eta3-allyl dimolybdenum complex 260", e1819)],
    conditions=[field("operation", "prolonged photolysis", e1819)],
    outcomes=[field("product_mixture", "mixture including complexes 257-260", e1819,
                    ["product257", "product258", "product259", "product260"]),
              field("reported_yield", None, targets=["product257", "product258", "product259", "product260"]),
              field("yield_measurement_basis", None)],
)
add_lit(
    "scheme64_complex257_allene_to_259", e1819,
    [mol("complex257", "reactant", "2-propenyl dimolybdenum complex 257", e1819),
     allene("allene", "1,2-propadiene", e1819),
     mol("product259", "product", "eta3-allyl dimolybdenum complex 259", e1819)],
    unresolved=["The page-19 prose gives no conditions or yield for this alternative preparation of 259."],
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
            "page": 13,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 41 and 43", "finding": "Scheme 41 was merged into the existing page-12 prose record; five osmium hydrometallation variants from Scheme 43 were extracted as cited literature examples.", "evidence_ids": [ev(13, "image"), ev(13, "text")]},
                {"region": "lower-left Scheme 42", "finding": "Six explicit 159a/159b substrate combinations and two 159c/159d phenylallene cases were split; good-yield/only-product and major/minor statements were preserved qualitatively.", "evidence_ids": [ev(13, "image"), ev(13, "text")]},
                {"region": "upper-right Scheme 44 and adjacent prose", "finding": "Three allenic-electrophile variants were extracted; intermediates 169/170 were classified as a postulated mechanism rather than isolated experiments.", "evidence_ids": [ev(13, "image"), ev(13, "text")]},
            ],
            "record_ids": ids_for_page(13),
            "unresolved": ["The review omits primary-paper scales and full procedures; organometallic structures remain unverified."],
        },
        {
            "page": 14,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 45", "finding": "The generic oxidative-addition stage 171-to-172 and subsequent CO/intramolecular-allene-insertion stage 172-to-173 were retained separately without inventing a Cartesian variant matrix.", "evidence_ids": [ev(14, "image"), ev(14, "text")]},
                {"region": "middle/lower-left Schemes 46 and 47", "finding": "Two 174 transformations, the proposed common-intermediate pathway, two 178 substrate variants, and two tungsten examples were extracted; reported 74% and 92% values were retained.", "evidence_ids": [ev(14, "image"), ev(14, "text")]},
                {"region": "upper/right Schemes 48 and 49", "finding": "Two tantalum examples and three Zr/Hf insertions were extracted; the in-situ-only 187 result retains the unsuccessful preparative attempt and instability statement.", "evidence_ids": [ev(14, "image"), ev(14, "text")]},
            ],
            "record_ids": ids_for_page(14),
            "unresolved": ["Most examples lack time, scale, atmosphere, workup, purification, and yield basis; complex 187 was not isolated preparatively."],
        },
        {
            "page": 15,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 50 and 51", "finding": "The 194 reaction retains the 1:1 vinyl/allyl mixture; three explicit 196 metal variants and two scandium-hydride examples were extracted.", "evidence_ids": [ev(15, "image"), ev(15, "text")]},
                {"region": "lower Scheme 52", "finding": "The 200a photolysis, the 200b/dimethylallene single-product case, and the 200b/propadiene 201c-e mixture were kept as distinct literature experiments.", "evidence_ids": [ev(15, "image"), ev(15, "text")]},
                {"region": "right-column section transition", "finding": "General review narrative introducing dinuclear complexes was classified as context and not duplicated as an experiment.", "evidence_ids": [ev(15, "image"), ev(15, "text")]},
            ],
            "record_ids": ids_for_page(15),
            "unresolved": ["The family Scheme 50 examples omit individual conditions and yields; the prose-only scandium analogue has no compound number."],
        },
        {
            "page": 16,
            "state": "attempted",
            "regions": [
                {"region": "top Schemes 53 and 54", "finding": "Three 202-to-203 variants were split. Each of the two 204/allene sequences was retained as three temperature-defined stages; difluoro- and dimethylallene cases preserve simple coordination without insertion.", "evidence_ids": [ev(16, "image"), ev(16, "text")]},
                {"region": "middle-right Scheme 55", "finding": "Ni-W, Rh-Os, Rh-Ru, methylallene, and Ru-Ru trimethylenemethane examples were extracted; the 74% value is product-targeted.", "evidence_ids": [ev(16, "image"), ev(16, "text")]},
                {"region": "lower-right Scheme 56", "finding": "Starting complexes 216-218 were mapped to product families 219-221 while the unresolved allene substitution matrix was left generic.", "evidence_ids": [ev(16, "image"), ev(16, "text")]},
            ],
            "record_ids": ids_for_page(16),
            "unresolved": ["Scheme 56 does not map each allene variant to separate conditions or yields; most examples lack complete procedures."],
        },
        {
            "page": 17,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 57 and adjacent prose", "finding": "The 222 case and the 224/alkyne experiment were extracted; separate 19% and 24% isolated yields target 225 and 226. Two prose-only bridging-alkyne examples remain incomplete literature records.", "evidence_ids": [ev(17, "image"), ev(17, "text")]},
                {"region": "upper-right Scheme 58", "finding": "The dicobalt example and Fe(CO)5 products were extracted; 230/231 were classified as pathway intermediates, and the phenylallene analogue remains a separate incomplete example.", "evidence_ids": [ev(17, "image"), ev(17, "text")]},
                {"region": "lower Schemes 59 and 60", "finding": "Five distinct Scheme-59 operations and two Scheme-60 experiments were split; the 81%, 5%, and 12% values and the at-least-15-compound mixture statement were preserved.", "evidence_ids": [ev(17, "image"), ev(17, "text")]},
            ],
            "record_ids": ids_for_page(17),
            "unresolved": ["The review does not establish whether intermediates 230/231 were isolated; multiple prose-only examples omit product identity and conditions."],
        },
        {
            "page": 18,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 61 and adjacent prose", "finding": "The 244/allene experiment retains slow bubbling, toluene, 338 K, and separate 13%/35% isolated yields; two related prose transformations were kept separate.", "evidence_ids": [ev(18, "image"), ev(18, "text")]},
                {"region": "upper-right Scheme 62", "finding": "Three dinuclear-hydride reactions were extracted; complex 249 remains an approximately 10% 31P-NMR minor product and the dimethylallene case remains an only-product result.", "evidence_ids": [ev(18, "image"), ev(18, "text")]},
                {"region": "lower Schemes 63 and 64", "finding": "Scheme 63 and 64 arrows were inspected on page 18; outcome text continuing on page 19 was used only as cross-page context for the 70%/2:1 result and the 257-260 mixture, without marking page 19 covered.", "evidence_ids": [ev(18, "image"), ev(18, "text"), ev(19, "text")]},
            ],
            "record_ids": ids_for_page(18),
            "unresolved": ["Schemes 63-64 continue in page-19 prose; page 19 was not visually inspected or claimed as covered. Primary experimental procedures remain unavailable."],
        },
    ],
}


raw_path = RUN / "raw_model" / "records_pages_0013_0018.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage_path = RUN / "coverage" / "pages_0013_0018.json"
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(p, "text") for p in range(13, 19)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "submitted_records": len(records),
    "new_record_ids": len({r["record_id"] for r in records}) - 1,
    "updated_existing_records": 1,
    "coverage_pages": len(coverage["pages"]),
    "raw": str(raw_path),
}, ensure_ascii=False))
