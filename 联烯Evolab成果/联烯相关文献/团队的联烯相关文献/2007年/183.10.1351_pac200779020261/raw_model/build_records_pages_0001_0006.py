#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = "doc_cc2bd70aeb39d26b"
OUT = ROOT / "runs/current"


def ev(page, *kinds):
    if not kinds:
        kinds = ("text", "image")
    return [f"{DOC}:page{page}:{kind}" for kind in kinds]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def q(number=None, unit=None, minimum=None, maximum=None, qualifier=None, raw_text=None):
    value = {"unit": unit}
    if number is not None:
        value["number"] = number
    else:
        value["minimum"] = minimum
        value["maximum"] = maximum
    if qualifier:
        value["qualifier"] = qualifier
    if raw_text:
        value["raw_text"] = raw_text
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "iodine": "[I][I]",
    "bromine": "BrBr",
    "NBS": "O=C1CCC(=O)N1Br",
    "acetonitrile": "CC#N",
    "acetone": "CC(=O)C",
    "water": "O",
    "hexane": "CCCCCC",
    "diethyl ether": "CCOCC",
    "benzyl mercaptan": "SCC1=CC=CC=C1",
    "dibenzyl disulfide": "c1ccccc1CSSCc1ccccc1",
    "sodium carbonate": "[Na+].[Na+].[O-]C([O-])=O",
    "lithium acetate dihydrate": "[Li+].CC(=O)[O-].O.O",
}


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    if smiles is None:
        smiles = SMILES.get(name or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, value, evidence):
    return fld(name, value, evidence)


def record(suffix, kind, evidence, participants, conditions=None, outcomes=None,
           notes=None, unresolved=None, step_id="reaction"):
    conditions = list(conditions or [])
    outcomes = list(outcomes or [])
    notes = list(notes or [])
    experimental = kind in {"reported_experiment", "optimization_entry", "substrate_scope_entry", "literature_example"}
    if experimental:
        existing = {x["name"] for x in conditions}
        for missing_name in ("time", "temperature", "atmosphere", "workup", "purification"):
            if missing_name not in existing:
                conditions.append(fld(missing_name, None, []))
        if any("yield" in x["name"] for x in outcomes) and not any(x["name"] == "yield_measurement_basis" for x in outcomes):
            outcomes.append(fld("yield_measurement_basis", None, []))
    default_unresolved = []
    if experimental:
        default_unresolved.append("This review article summarizes a cited publication; experiment-level details absent here require review against the original cited paper.")
    default_unresolved.append("All machine structures and stereochemical assignments remain unverified.")
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": step_id,
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if participants or conditions else [],
        "outcomes": outcomes,
        "notes": [fact(value, note_ev) for value, note_ev in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": default_unresolved + list(unresolved or []),
        },
    }


records = []

# Page 1, Scheme 1: conceptual regio-/stereochemical possibilities, not one executed experiment.
e = ev(1)
records.append(record(
    "scheme1_generic_electrophilic_addition_outcomes", "general_scheme", e,
    [part("s1_allene", "reactant", "generic substituted allene", e),
     part("s1_z1", "reagent", "Z1 (reagent no. 1)", e),
     part("s1_z2", "reagent", "Z2 (reagent no. 2)", e),
     part("s1_products", "product", "four generic regio-/stereoisomeric addition products", e)],
    notes=[("Scheme 1 is a conceptual map of possible sequential electrophilic-addition outcomes and has no row-level conditions or yields.", e)],
    unresolved=["R, Z1, and Z2 are generic groups; no complete molecular structures can be assigned."]
))

# Scheme 2 branches. Page 1 supplies the review context; page 2 supplies the arrows.
e = ev(1) + ev(2)
common_s2 = lambda prefix: [part(f"{prefix}_substrate", "reactant", "generic 1,2-allenyl sulfoxide", e),
                            part(f"{prefix}_product", "product", "E-halohydroxylation product", e)]
records.append(record(
    "scheme2_iodohydroxylation", "literature_example", e,
    common_s2("s2i") + [part("s2i_i2", "reagent", "I2", e, "iodine"),
                        part("s2i_lioac", "reagent", "LiOAc·2H2O", e, "lithium acetate dihydrate"),
                        part("s2i_mecn", "solvent", "MeCN", e, "acetonitrile"),
                        part("s2i_water", "solvent", "H2O", e, "water")],
    [fld("solvent", "MeCN/H2O (7:1)", e), fld("temperature", "r.t.", e),
     fld("time", "within a couple of hours", ev(1))],
    [fld("reported_scope_yield", q(unit="%", minimum=74, maximum=92, raw_text="74–92%"), ev(2), ["s2i_product"])],
    unresolved=["Exact substrate identities, reagent amounts, and row-specific yields are not provided in the review scheme."]
))
records.append(record(
    "scheme2_bromohydroxylation_cubr2", "literature_example", e,
    common_s2("s2bcu") + [part("s2bcu_cubr2", "reagent", "CuBr2", e),
                          part("s2bcu_acetone", "solvent", "acetone", e, "acetone"),
                          part("s2bcu_water", "solvent", "H2O", e, "water")],
    [fld("solvent", "acetone/H2O", ev(2)), fld("temperature", None, []),
     fld("time", "within a couple of hours", ev(1))],
    [fld("reported_collective_scope_yield", q(unit="%", minimum=68, maximum=98, raw_text="68–98%"), ev(2), ["s2bcu_product"])],
    unresolved=["The 68–98% range is printed for the combined CuBr2-or-NBS branch and is not assignable to a specific reagent/substrate case."]
))
records.append(record(
    "scheme2_bromohydroxylation_nbs", "literature_example", e,
    common_s2("s2bnbs") + [part("s2bnbs_nbs", "reagent", "NBS", e, "NBS"),
                           part("s2bnbs_lioac", "reagent", "LiOAc·2H2O", e, "lithium acetate dihydrate"),
                           part("s2bnbs_mecn", "solvent", "MeCN", e, "acetonitrile"),
                           part("s2bnbs_water", "solvent", "H2O", e, "water")],
    [fld("solvent", "MeCN/H2O", ev(2)), fld("temperature", "r.t.", ev(2)),
     fld("time", "within a couple of hours", ev(1))],
    [fld("reported_collective_scope_yield", q(unit="%", minimum=68, maximum=98, raw_text="68–98%"), ev(2), ["s2bnbs_product"])],
    unresolved=["The 68–98% range is printed for the combined CuBr2-or-NBS branch and is not assignable to a specific reagent/substrate case."]
))
records.append(record(
    "scheme2_chlorohydroxylation", "literature_example", e,
    common_s2("s2cl") + [part("s2cl_cucl2", "reagent", "CuCl2·2H2O", e),
                         part("s2cl_silica", "unspecified_agent", "silica gel", e)],
    [fld("solvent", "no solvent", ev(2)), fld("temperature", None, []),
     fld("time", "within a couple of hours", ev(1))],
    [fld("reported_scope_yield", q(unit="%", minimum=49, maximum=84, raw_text="49–84%"), ev(2), ["s2cl_product"])],
    notes=[("The source prints the temperature expression as 'rt~65 °C'; it is retained here without converting room temperature to an assumed numeric bound.", ev(2))],
    unresolved=["The exact temperature program represented by 'rt~65 °C' is ambiguous."]
))

# Scheme 3 contains both a substrate-specific prior-work example and a proposed mechanism.
e = ev(2)
records.append(record(
    "scheme3_compound1_to_2", "literature_example", e,
    [part("s3_1", "reactant", "optically active 1,2-allenyl sulfoxide 1", e),
     part("s3_i2", "reagent", "I2", e, "iodine", amounts=[amount("equivalents", q(1.2, "equiv"), e)]),
     part("s3_lioac", "reagent", "LiOAc·2H2O", e, "lithium acetate dihydrate"),
     part("s3_mecn", "solvent", "MeCN", e, "acetonitrile"),
     part("s3_water", "solvent", "H2O", e, "water"),
     part("s3_2", "product", "E-iodohydroxylation product 2", e)],
    [fld("solvent", "MeCN/H2O (7:1)", e), fld("temperature", "r.t.", e)],
    [fld("reported_yield", q(97, "%"), e, ["s3_2"])],
    notes=[("The sulfur center is reported to invert absolute configuration during the transformation.", e)],
    unresolved=["The complex cage-containing substrate/product connectivity and absolute stereochemistry were not encoded as SMILES."]
))
records.append(record(
    "scheme3_proposed_cyclic_pathway", "mechanism", e,
    [part("s3m_1", "reactant", "optically active 1,2-allenyl sulfoxide 1", e),
     part("s3m_i2", "reagent", "I2", e, "iodine"),
     part("s3m_3", "unspecified_agent", "cyclic cationic intermediate 3", e),
     part("s3m_4", "unspecified_agent", "cyclic intermediate 4", e),
     part("s3m_water", "reagent", "H2O", e, "water"),
     part("s3m_2", "product", "product 2 after sulfur inversion", e)],
    notes=[("The authors propose intermediates 3 and 4 to rationalize regioselectivity and inversion at sulfur; this is mechanistic, not a separately executed experiment.", e)],
    unresolved=["Intermediates 3 and 4 are proposed and their structures remain unverified."]
))

# Page 3, Scheme 4.
e = ev(3)
records.append(record(
    "scheme4_bnsh_reductive_iodohydroxylation", "literature_example", e,
    [part("s4_sub", "reactant", "generic 1,2-allenyl sulfoxide", e),
     part("s4_bnsh", "reagent", "BnSH", e, "benzyl mercaptan"),
     part("s4_i2", "reagent", "I2", e, "iodine"),
     part("s4_mecn", "solvent", "MeCN", e, "acetonitrile"),
     part("s4_prod", "product", "3-hydroxy-2-iodo-2(E)-alkenyl phenyl sulfide", e),
     part("s4_bndisulfide", "product", "BnSSBn", e, "dibenzyl disulfide")],
    [fld("solvent", "MeCN", e)],
    [fld("reported_scope_yield", q(unit="%", minimum=50, maximum=80, raw_text="50–80%"), e, ["s4_prod"])],
    notes=[("The review states that the sulfoxide is reduced to sulfide and proposes that its oxygen becomes the hydroxyl group while BnSH becomes BnSSBn.", e)],
    unresolved=["Exact substituent combinations, reagent quantities, temperature, and duration are absent."]
))

# Scheme 5 has two independent solvent-screen rows.
e = ev(3)
def scheme5_record(suffix, solvent_label, solvent_name, ratio, hours, y7, ratio7, y8, ratio8):
    ps = [part(f"{suffix}_5", "reactant", "1,2-allenyl sulfide 5", e,
               smiles="c1ccccc1SC=C=C(C)Cc1ccccc1"),
          part(f"{suffix}_i2", "reagent", "I2", e, "iodine"),
          part(f"{suffix}_solvent", "solvent", solvent_label, e, solvent_name),
          part(f"{suffix}_water", "solvent", "H2O", e, "water"),
          part(f"{suffix}_7", "product", "2-iodo-3-methyl-4-phenyl-2-butenal 7", e,
               smiles="O=CC(I)=C(C)Cc1ccccc1"),
          part(f"{suffix}_8", "product", "iodohydroxylation product Z-8", e,
               smiles="c1ccccc1SC=C(I)C(O)(C)Cc1ccccc1")]
    outs = [fld("reported_yield_7", q(y7, "%"), e, [f"{suffix}_7"]),
            fld("reported_E_Z_ratio_7", ratio7, e, [f"{suffix}_7"]),
            fld("reported_yield_8", q(y8, "%"), e, [f"{suffix}_8"])]
    if ratio8:
        outs.append(fld("reported_Z_E_ratio_8", ratio8, e, [f"{suffix}_8"]))
    return record(suffix, "literature_example", e, ps,
                  [fld("solvent", f"{solvent_label}/H2O ({ratio})", e), fld("time", q(hours, "h"), e)],
                  outs,
                  unresolved=["The iodine loading, temperature, atmosphere, workup, purification, and yield basis are not stated in this review table."])

records.append(scheme5_record("scheme5_mecn_row", "MeCN", "acetonitrile", "4:1", 16, 30, "1.08:1", 0, None))
records.append(scheme5_record("scheme5_acetone_row", "acetone", "acetone", "2:1", 10.5, 12, "1.07:1", 66, ">99:1"))

# Page 4, Schemes 6-9.
e = ev(3) + ev(4)
records.append(record(
    "scheme6_iodohydroxylation_allenyl_sulfides", "literature_example", e,
    [part("s6_sub", "reactant", "generic 1,2-allenyl phenyl sulfide", e),
     part("s6_i2", "reagent", "I2", e, "iodine", amounts=[amount("equivalents", q(2, "equiv"), ev(4))]),
     part("s6_acetone", "solvent", "acetone", e, "acetone"),
     part("s6_water", "solvent", "H2O", e, "water"),
     part("s6_prod", "product", "2-iodo-3-hydroxy-1(Z)-alkenyl phenyl sulfide", e)],
    [fld("solvent", "acetone/H2O (4:1)", ev(4)), fld("temperature", "r.t.", ev(4))],
    [fld("reported_scope_yield", q(unit="%", minimum=53, maximum=94, raw_text="53–94%"), ev(4), ["s6_prod"])],
    unresolved=["Substituent-specific rows and durations are not provided in the review."]
))

e = ev(4)
records.append(record(
    "scheme7_bromohydroxylation_allenyl_sulfides", "literature_example", e,
    [part("s7_sub", "reactant", "generic 1,2-allenyl phenyl sulfide", e),
     part("s7_br2", "reagent", "Br2", e, "bromine", amounts=[amount("equivalents", q(2, "equiv"), e)]),
     part("s7_na2co3", "reagent", "Na2CO3", e, "sodium carbonate", amounts=[amount("equivalents", q(1, "equiv"), e)]),
     part("s7_mecn", "solvent", "MeCN", e, "acetonitrile"),
     part("s7_water", "solvent", "H2O", e, "water"),
     part("s7_prod", "product", "Z-bromohydroxylation product", e)],
    [fld("solvent", "MeCN/H2O (4:1)", e), fld("temperature", q(0, "°C"), e)],
    [fld("reported_scope_yield", q(unit="%", minimum=47, maximum=86, raw_text="47–86%"), e, ["s7_prod"])],
    unresolved=["Substituent-specific rows and durations are not provided in the review."]
))
records.append(record(
    "scheme8_iodohydroxylation_allenyl_selenides", "literature_example", e,
    [part("s8_sub", "reactant", "generic 1,2-allenyl selenide", e),
     part("s8_i2", "reagent", "I2", e, "iodine", amounts=[amount("equivalents", q(4, "equiv"), e)]),
     part("s8_mecn", "solvent", "MeCN", e, "acetonitrile"),
     part("s8_water", "solvent", "H2O", e, "water"),
     part("s8_prod", "product", "Z-iodohydroxylation product from allenyl selenide", e)],
    [fld("solvent", "MeCN/H2O (4:1 v/v)", e), fld("temperature", q(0, "°C"), e), fld("atmosphere", "N2", e)],
    [fld("reported_scope_yield", q(unit="%", minimum=33, maximum=74, raw_text="33–74%"), e, ["s8_prod"])],
    unresolved=["The generic R group, exact water/substrate quantities, and durations are not provided."]
))
records.append(record(
    "scheme9_four_component_amide_formation", "literature_example", e,
    [part("s9_sub", "reactant", "generic 1,2-allenyl selenide", e),
     part("s9_nitrile", "reactant", "R'CN", e),
     part("s9_i2", "reagent", "I2", e, "iodine", amounts=[amount("equivalents", q(2, "equiv"), e)]),
     part("s9_water", "reagent", "H2O", e, "water", amounts=[amount("equivalents", q(1, "equiv"), e)]),
     part("s9_hexane", "solvent", "n-hexane", e, "hexane"),
     part("s9_prod", "product", "N-(2(Z)-iodo-3-seleno)-2-propenyl amide 9", e)],
    [fld("solvent", "R'CN/n-hexane (1:1)", e), fld("temperature", q(25, "°C"), e), fld("atmosphere", "N2", e)],
    [fld("reported_scope_yield", q(unit="%", minimum=23, maximum=62, raw_text="23–62%"), e, ["s9_prod"])],
    unresolved=["R and R' are generic, and the duration, workup, purification, and yield basis are absent."]
))

# Scheme 10 crosses pages 4-5 and is explicitly a rationale.
e = ev(4) + ev(5)
records.append(record(
    "scheme10_competing_water_nitrile_pathways", "mechanism", e,
    [part("s10_sub", "reactant", "generic allenyl sulfide or selenide", e),
     part("s10_x", "reagent", "X+", e),
     part("s10_10", "unspecified_agent", "cationic intermediate 10", e),
     part("s10_water", "reagent", "H2O", e, "water"),
     part("s10_mecn", "reagent", "MeCN", e, "acetonitrile"),
     part("s10_hydroxy", "product", "halohydroxylation product", e),
     part("s10_11", "unspecified_agent", "nitrilium intermediate 11", e),
     part("s10_amide", "product", "amide product", e)],
    notes=[("The proposed pathway has water trapping intermediate 10 to give halohydroxylation, or MeCN trapping when water is limited followed by hydrolysis to the amide.", e)],
    unresolved=["The pathway is proposed; generic groups, charges, and intermediate structures remain unverified."]
))

# Scheme 11 is explicitly Friesen et al. (1993); separate the two executed stages.
e = ev(5)
records.append(record(
    "scheme11_friesen_iodination_stage", "literature_example", e,
    [part("s11a_sub", "reactant", "generic 2,3-allenol", e),
     part("s11a_i2", "reagent", "I2", e, "iodine"),
     part("s11a_ether", "solvent", "Et2O", e, "diethyl ether"),
     part("s11a_prod", "product", "E/Z 4-hydroxy-2-iodo-2-alkenyl iodide mixture", e)],
    [fld("solvent", "Et2O", e)],
    [fld("reported_Z_E_ratio", "7:1 to 9:1", e, ["s11a_prod"])],
    unresolved=["No stage-1 yield, time, temperature, amounts, atmosphere, workup, or purification is reported in the review."]
))
records.append(record(
    "scheme11_friesen_base_cyclization_stage", "literature_example", e,
    [part("s11b_mix", "reactant", "E/Z 4-hydroxy-2-iodo-2-alkenyl iodide mixture", e),
     part("s11b_base", "reagent", "base (unspecified)", e),
     part("s11b_prod", "product", "1-iodovinylic epoxides", e)],
    outcomes=[fld("reported_scope_yield", q(unit="%", minimum=65, maximum=93, raw_text="65–93%"), e, ["s11b_prod"])],
    unresolved=["Base identity, quantities, time, temperature, atmosphere, workup, purification, and yield basis are absent."]
))

# Scheme 12 begins in prose on page 5 and is drawn on page 6.
e = ev(5) + ev(6)
records.append(record(
    "scheme12_primary_allenol_cyclization", "literature_example", e,
    [part("s12_sub", "reactant", "generic primary 2,3-allenol", e),
     part("s12_i2", "reagent", "I2", e, "iodine", amounts=[amount("equivalents", q(2, "equiv"), ev(6))]),
     part("s12_mecn", "solvent", "CH3CN", e, "acetonitrile"),
     part("s12_water", "solvent", "H2O", e, "water"),
     part("s12_prod", "product", "3-iodo-2,5-dihydrofuran 12", e)],
    [fld("solvent", "CH3CN/H2O (15:1)", ev(6)), fld("temperature", "r.t.", ev(6))],
    [fld("reported_scope_yield", q(unit="%", minimum=50, maximum=82, raw_text="50–82%"), e, ["s12_prod"])],
    unresolved=["R1/R2 substrate identities and durations are not enumerated in this review scheme."]
))

# Scheme 13 alternatives must remain separate conditions even though the review prints one collective range.
e = ev(6)
def scheme13(suffix, reagent_label, reagent_name, halogen):
    return record(
        suffix, "literature_example", e,
        [part(f"{suffix}_sub", "reactant", "generic 1-aryl-2,3-allenol", e),
         part(f"{suffix}_reagent", "reagent", reagent_label, e, reagent_name,
              amounts=[amount("equivalents", q(2, "equiv"), e)]),
         part(f"{suffix}_mecn", "solvent", "MeCN", e, "acetonitrile"),
         part(f"{suffix}_water", "solvent", "H2O", e, "water"),
         part(f"{suffix}_prod", "product", f"2-aryl-3-{halogen}-3-alkenal 13", e)],
        [fld("solvent", "MeCN/H2O (15:1)", e), fld("temperature", "r.t.", e)],
        [fld("reported_collective_scope_yield", q(unit="%", minimum=52, maximum=93, raw_text="52–93%"), e, [f"{suffix}_prod"])],
        notes=[("The review states that R2 is H or an electron-donating group for clean high-yield formation.", e)],
        unresolved=["The 52–93% range covers the combined I2/Br2/NBS scope and is not reagent-specific."]
    )

records.append(scheme13("scheme13_iodine_condition", "I2", "iodine", "iodo"))
records.append(scheme13("scheme13_bromine_condition", "Br2", "bromine", "bromo"))
records.append(scheme13("scheme13_nbs_condition", "NBS", "NBS", "bromo"))

# Scheme 14 mechanism.
e = ev(6)
records.append(record(
    "scheme14_proposed_phenyl_shift", "mechanism", e,
    [part("s14_sub", "reactant", "allenol precursor to 13a", e),
     part("s14_br2", "reagent", "Br2", e, "bromine"),
     part("s14_14", "unspecified_agent", "cationic 2-bromo-pi-allylic intermediate 14", e),
     part("s14_13a", "product", "2-aryl-3-bromo-3-alkenal 13a", e)],
    notes=[("The aldehyde 13a is proposed to arise by a 1,2-phenyl shift from intermediate 14.", e)],
    unresolved=["This is a proposed mechanism; intermediate 14 is not an isolated experimental product."]
))

# Scheme 15 arrow is on page 7, outside the claimed coverage; page-6 prose still states two reagent classes.
e = ev(6)
for suffix, reagent_label, reagent_name, halogen in [
    ("scheme15_iodine_condition_from_page6_prose", "I2", "iodine", "iodo"),
    ("scheme15_bromine_condition_from_page6_prose", "Br2", "bromine", "bromo"),
]:
    records.append(record(
        suffix, "literature_example", e,
        [part(f"{suffix}_sub", "reactant", "3-alkyl-3,4-pentadien-2-ol", e),
         part(f"{suffix}_reagent", "reagent", reagent_label, e, reagent_name),
         part(f"{suffix}_prod", "product", f"4-{halogen}-4-en-2-one (products 15–17)", e)],
        notes=[("Page 6 attributes product formation to a 1,2-H shift from a 14-type cationic intermediate.", e)],
        unresolved=["The Scheme 15 drawing and any product-specific conditions are on page 7, outside this session's claimed coverage; only the page-6 prose is structured."]
    ))

assert len(records) == 24, len(records)

records_path = OUT / "raw_model/records_pages_0001_0006.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page_records = {
    1: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme1_", "scheme2_"))],
    2: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme2_", "scheme3_"))],
    3: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme4_", "scheme5_", "scheme6_"))],
    4: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme6_", "scheme7_", "scheme8_", "scheme9_", "scheme10_"))],
    5: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme10_", "scheme11_", "scheme12_"))],
    6: [r["record_id"] for r in records if r["source_reaction_id"].startswith(("scheme12_", "scheme13_", "scheme14_", "scheme15_"))],
}

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction", "finding": "Review-level context only; abstract claims were not duplicated as experiments.", "evidence_ids": ev(1)},
                {"region": "middle-lower Scheme 1", "finding": "One generic conceptual map of four possible sequential electrophilic-addition outcomes; classified as general_scheme.", "evidence_ids": ev(1)},
                {"region": "lower prose introducing Scheme 2", "finding": "Collective prior-work statement for I2/CuBr2/NBS/CuCl2 halohydroxylations; merged with the separate Scheme 2 condition records on page 2.", "evidence_ids": ev(1)},
            ],
            "record_ids": page_records[1],
            "unresolved": ["The page-1 'high yields within a couple of hours' statement is collective and lacks substrate-specific values."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 2", "finding": "Iodination, two alternative bromination conditions, and chlorination were separated into four cited prior-work condition records with their printed yield ranges.", "evidence_ids": ev(2)},
                {"region": "lower Scheme 3 and surrounding prose", "finding": "The substrate-specific 1-to-2 reaction was separated from the proposed cyclic-intermediate mechanism through 3 and 4.", "evidence_ids": ev(2)},
            ],
            "record_ids": page_records[2],
            "unresolved": ["Scheme 2 gives collective scope ranges rather than row-level identities; the chlorination temperature is printed ambiguously as rt~65 °C."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 4", "finding": "Generic BnSH-assisted reductive iodohydroxylation from cited prior work, including BnSSBn formation and 50–80% scope yield.", "evidence_ids": ev(3)},
                {"region": "middle-lower Scheme 5 table", "finding": "Two independent solvent-screen rows extracted with times, separate product yields, and E/Z or Z/E ratios.", "evidence_ids": ev(3)},
                {"region": "bottom prose introducing Scheme 6", "finding": "Generic cited sulfide scope statement linked to the page-4 Scheme 6 arrow rather than duplicated.", "evidence_ids": ev(3)},
            ],
            "record_ids": page_records[3],
            "unresolved": ["Scheme 4 and the Scheme 5 table omit several quantities, operational details, and yield bases."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 6", "finding": "Generic cited iodohydroxylation scope of allenyl sulfides extracted with iodine equivalents, solvent ratio, room temperature, and yield range.", "evidence_ids": ev(4)},
                {"region": "upper-middle Scheme 7", "finding": "Generic bromohydroxylation scope extracted with Br2 and Na2CO3 equivalents, solvent ratio, 0 °C, and yield range.", "evidence_ids": ev(4)},
                {"region": "middle Scheme 8", "finding": "Generic allenyl-selenide iodohydroxylation scope extracted with iodine loading, solvent ratio, N2, 0 °C, and yield range.", "evidence_ids": ev(4)},
                {"region": "lower Scheme 9", "finding": "Four-component nitrile-incorporating amide formation extracted with component loadings, solvent ratio, N2, 25 °C, and yield range.", "evidence_ids": ev(4)},
                {"region": "bottom mechanism prose continuing to page 5", "finding": "Start of proposed water-versus-MeCN trapping rationale linked to Scheme 10.", "evidence_ids": ev(4)},
            ],
            "record_ids": page_records[4],
            "unresolved": ["Generic substituent rows and reaction durations are not supplied; Scheme 10 is explicitly mechanistic."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper Scheme 10", "finding": "Proposed competing water and nitrile trapping pathways classified as mechanism, not a reported experiment.", "evidence_ids": ev(5)},
                {"region": "middle Scheme 11", "finding": "Friesen et al. 1993 prior work split into iodination-mixture formation and subsequent base cyclization stages.", "evidence_ids": ev(5)},
                {"region": "lower prose introducing Scheme 12", "finding": "Primary-allenol cyclization claim merged with the full page-6 Scheme 12 conditions.", "evidence_ids": ev(5)},
            ],
            "record_ids": page_records[5],
            "unresolved": ["Scheme 11 omits the base identity and most operation details; its first-stage yield is not reported."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 12", "finding": "Generic primary-2,3-allenol iodocyclization extracted with iodine loading, solvent ratio, room temperature, and 50–82% scope yield.", "evidence_ids": ev(6)},
                {"region": "middle Scheme 13", "finding": "I2, Br2, and NBS alternatives retained as three distinct cited conditions sharing a collective 52–93% scope range.", "evidence_ids": ev(6)},
                {"region": "lower Scheme 14", "finding": "Proposed cationic intermediate and 1,2-phenyl shift classified as mechanism.", "evidence_ids": ev(6)},
                {"region": "bottom prose introducing Scheme 15", "finding": "I2 and Br2 reactions of 3-alkyl-3,4-pentadien-2-ols retained as two partial prior-work records; the Scheme 15 drawing lies on page 7 and is not claimed as covered.", "evidence_ids": ev(6)},
            ],
            "record_ids": page_records[6],
            "unresolved": ["Scheme 13 yields are collective rather than reagent-specific.", "Scheme 15 product drawings and any additional details lie outside the requested page range."],
        },
    ],
}

coverage_path = OUT / "coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "records_path": str(records_path), "coverage_path": str(coverage_path)}, ensure_ascii=False))
