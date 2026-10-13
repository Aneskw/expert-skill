#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--4 of the bisallene review."""
import json
from pathlib import Path

DOC = "doc_59af3e472634c599"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


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


def conditions(evidence, *, time=None, temperature=None, solvent=None, extras=None):
    result = [
        field("time", time, evidence),
        field("temperature", temperature, evidence),
        field("solvent", solvent, evidence),
    ]
    result.extend(extras or [])
    return result


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
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
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


records = []

# Page 1: Scheme 1 and Scheme 2 plus the explicit TsI exception in prose.
e1 = ev(1)
records.append(record(
    "scheme1_radical_scope", "Scheme 1", "literature_example", e1,
    [
        participant("s1_bisallene_1", "reactant", "1 (generic 1,5-bisallene; X = O, NTs, NPh, or CPh2)", e1),
        participant("s1_tsy", "reagent", "TsY (Y = Br or SePh; alternative reagents)", e1),
        participant("s1_aibn", "reagent", "AIBN", e1, "azobisisobutyronitrile", "CC(C)(C#N)N=NC(C)(C)C#N"),
        participant("s1_toluene", "solvent", "toluene", e1, "toluene", "Cc1ccccc1"),
        participant("s1_product_2", "product", "2 (trans-cyclopentane product; generic X/Y scope)", e1),
    ],
    [{"step_id": "radical_cyclization", "participant_ids": ["s1_bisallene_1", "s1_tsy", "s1_aibn", "s1_toluene", "s1_product_2"],
      "conditions": conditions(e1, time=q(4, "h"), temperature=q(90, "°C"), solvent="toluene")}],
    [field("reported_yield_range", qr(55, 73, "%", "55–73%"), e1, ["s1_product_2"]),
     field("yield_measurement_basis", None, e1)],
    ["Scheme 1 summarizes cited work (reference 5), not a new experiment reported in this review.",
     "The yield range pools generic X/Y scope and is not assigned to an individual substrate."],
    ["Generic substituents prevent a unique substrate/product structure or SMILES.",
     "Individual yields for TsBr versus TsSePh and each X value are not given."]
))

records.append(record(
    "prose_tsi_exception", "Page 1 TsI exception", "literature_example", e1,
    [
        participant("tsi_nts_1", "reactant", "1 (NTs-tethered 1,5-bisallene)", e1),
        participant("tsi_reagent", "reagent", "TsI", e1, "p-toluenesulfonyl iodide", "Cc1ccc(S(=O)(=O)I)cc1"),
        participant("tsi_product", "product", "cis/trans cyclopentane product mixture", e1),
    ],
    [{"step_id": "tsi_radical_cyclization", "participant_ids": ["tsi_nts_1", "tsi_reagent", "tsi_product"],
      "conditions": conditions(e1)}],
    [field("total_product_yield", q(22, "%"), e1, ["tsi_product"]),
     field("cis_trans_ratio", None, e1), field("yield_measurement_basis", None, e1)],
    ["The prose reports a cis/trans mixture when TsI was applied; this condition is distinct from the Scheme 1 TsBr/TsSePh scope."],
    ["Temperature, duration, solvent, initiator, measurement basis, and cis/trans ratio are not restated.",
     "The generic product structure cannot be resolved uniquely."]
))


def scheme2_record(suffix, catalyst_label, catalyst_amount, temperature, time, y_label,
                   product_label, product_id, yield_value, extra_outcomes=None, note=None):
    ps = [
        participant(f"{suffix}_1", "reactant", "1 (generic 1,5-bisallene; X scope)", e1),
        participant(f"{suffix}_ysn", "reagent", y_label, e1),
        participant(f"{suffix}_cat", "catalyst", catalyst_label, e1,
                    amounts=[field("catalyst_loading", catalyst_amount, e1)] if catalyst_amount else []),
        participant(f"{suffix}_thf", "solvent", "THF", e1, "tetrahydrofuran", "C1CCOC1"),
        participant(product_id, "product", product_label, e1),
    ]
    outs = [field("reported_yield_range", yield_value, e1, [product_id]), field("yield_measurement_basis", None, e1)]
    outs.extend(extra_outcomes or [])
    return record(suffix, "Scheme 2", "literature_example", e1, ps,
                  [{"step_id": "pd_cyclization", "participant_ids": [p["entity_id"] for p in ps],
                    "conditions": conditions(e1, time=time, temperature=temperature, solvent="THF")}],
                  outs,
                  ["Scheme 2 summarizes cited prior work (references 6a/6b).", note] if note else
                  ["Scheme 2 summarizes cited prior work (references 6a/6b)."],
                  ["Generic X substituents prevent unique substrate/product structures.",
                   "The yield is a scope range rather than a single-substrate result."])


records.append(scheme2_record(
    "scheme2_tms_condition_a", "Pd(PPh3)4", q(5, "mol%"), "reflux", q(3, "h"),
    "(trimethylsilyl)tributylstannane (TMS-SnBu3)", "5 (trans product, Y = TMS)", "s2a_product_5",
    qr(71, 78, "%", "71–78%"), note="Condition A is 5 mol% Pd(PPh3)4 in refluxing THF for 3 h."
))
records.append(scheme2_record(
    "scheme2_tms_condition_b", "(allyl)2PdCl2", q(5, "mol%"), "room temperature", q(3, "h"),
    "(trimethylsilyl)tributylstannane (TMS-SnBu3)", "5 (trans product, Y = TMS)", "s2b_product_5",
    qr(71, 78, "%", "71–78%"), note="Condition B is 5 mol% (allyl)2PdCl2 in THF at room temperature for 3 h; the scheme does not allocate individual yields between A and B."
))
records.append(scheme2_record(
    "scheme2_distannane_3h", "Pd catalyst under condition A or B (alternative not assigned)", None,
    "reflux or room temperature (condition alternative unresolved)", q(3, "h"),
    "Bu3SnSnBu3", "7 (cis product, Y = SnBu3)", "s2sn_product_7",
    qr(53, 80, "%", "53–80%"), note="The prose says distannane gives cis products under the same reaction conditions but does not assign A versus B to individual results."
))
records.append(scheme2_record(
    "scheme2_distannane_12h", "Pd catalyst under condition A or B (alternative not assigned)", None,
    "reflux or room temperature (condition alternative unresolved)", q(12, "h"),
    "Bu3SnSnBu3", "9 (cis-fused bicyclo[3.2.0] product)", "s2long_product_9",
    qr(48, 62, "%", "48–62%"), note="Prolonging the reaction to 12 h leads through 6/8 to bicyclic product 9."
))


def scheme2_ge(suffix, y_label, major_label, major_id, major_yield):
    byproduct = f"{suffix}_byproduct_9"
    result = scheme2_record(
        suffix, "Pd catalyst under similar reaction conditions (identity not restated)", None,
        None, None, y_label, major_label, major_id, major_yield,
        [field("byproduct_yield_range", qr(14, 27, "%", "14–27%"), e1, [byproduct])],
        note="The review states that cis-fused bicyclic diene 9 is formed in 14–27% yield in all germylstannane reactions except when X is oxygen."
    )
    result["participants"].append(participant(byproduct, "product", "9 (cis-fused bicyclic diene byproduct; absent for X = O)", e1))
    result["steps"][0]["participant_ids"].append(byproduct)
    result["review"]["unresolved"].append("The exact catalyst, temperature, time, and solvent are only described as similar conditions.")
    return result


records.append(scheme2_ge("scheme2_gebu3", "Bu3GeSnBu3", "7 (cis product, Y = GeBu3)", "s2gebu_product_7", qr(41, 51, "%", "41–51%")))
records.append(scheme2_ge("scheme2_geph3", "Ph3GeSnBu3", "5 (trans product, Y = GePh3)", "s2geph_product_5", qr(61, 77, "%", "61–77%")))

# Page 2: Schemes 3--6. Scheme 5 is purely mechanistic.
e2 = ev(2)
records.append(record(
    "scheme3_three_component_cascade", "Scheme 3", "literature_example", e2,
    [
        participant("s3_bisallene_1", "reactant", "1 (generic 1,5-bisallene)", e2),
        participant("s3_propargyl_carbonate", "reactant", "propargylic methyl carbonate (generic R1/R2/R3)", e2),
        participant("s3_boronic_acid", "reactant", "R4B(OH)2 (organoboronic acid)", e2),
        participant("s3_pd", "catalyst", "Pd(dba)2", e2),
        participant("s3_product_14", "product", "14 (cis-fused bicyclo[4.3.0]nonene; generic substituents)", e2),
    ],
    [{"step_id": "three_component_cascade", "participant_ids": ["s3_bisallene_1", "s3_propargyl_carbonate", "s3_boronic_acid", "s3_pd", "s3_product_14"],
      "conditions": conditions(e2)}],
    [field("reported_yield_range", qr(41, 77, "%", "41–77%"), e2, ["s3_product_14"]), field("yield_measurement_basis", None, e2)],
    ["The figure combines oxidative addition, double carbopalladation, allylic isomerization, and Suzuki coupling as a cited reaction pathway (reference 7).",
     "The stereochemical note applies when R1 and R2 differ and R1 is larger than R2."],
    ["Catalyst loading, solvent, temperature, time, and measurement basis are absent.",
     "Generic R groups prevent unique structures and substrate-level yields."]
))
records.append(record(
    "scheme4_pdii_bisallenol", "Scheme 4", "literature_example", e2,
    [
        participant("s4_bisallenol_1a", "reactant", "1a (generic bisallenol; X = CH2, NTs, O, or SO2; Y = H or Ac)", e2),
        participant("s4_pdii", "catalyst", "Pd(II)", e2),
        participant("s4_product_17", "product", "17 (2,5-dihydrofuran-fused bicyclic product)", e2),
    ],
    [{"step_id": "oxypalladation_carbopalladation_elimination", "participant_ids": ["s4_bisallenol_1a", "s4_pdii", "s4_product_17"],
      "conditions": conditions(e2)}],
    [field("reported_yield_range", qr(51, 81, "%", "51–81%"), e2, ["s4_product_17"]), field("yield_measurement_basis", None, e2)],
    ["The review attributes this cited reaction to reference 8 and depicts intermediates 15 and 16."],
    ["The Pd(II) species/loading, solvent, temperature, time, and yield basis are absent.",
     "Generic substituents prevent unique structures and substrate-level yields."]
))
records.append(record(
    "scheme5_cyclometallation_modes", "Scheme 5", "mechanism", e2,
    [
        participant("s5_bisallene_1", "reactant", "1 (generic 1,5-bisallene)", e2),
        participant("s5_metal", "catalyst", "M (unspecified metal center)", e2),
        participant("s5_i1", "product", "I-1 (internal/terminal C=C cyclometallation intermediate)", e2),
        participant("s5_i2", "product", "I-2 (terminal/terminal C=C cyclometallation intermediate)", e2),
        participant("s5_i3", "product", "I-3 (internal/internal C=C cyclometallation intermediate)", e2),
    ],
    [{"step_id": "three_possible_cyclometallations", "participant_ids": ["s5_bisallene_1", "s5_metal", "s5_i1", "s5_i2", "s5_i3"],
      "conditions": [field("operation", "three alternative cyclometallation modes a, b, and c", e2)]}],
    [],
    ["Scheme 5 is a conceptual mechanism classification, not an experimental reaction or yield-bearing scope entry."],
    ["Metal identity and all operational conditions are unspecified; generic intermediates have no unique SMILES."]
))
records.append(record(
    "scheme6_rh_bisallene_dimerization", "Scheme 6", "literature_example", e2,
    [
        participant("s6_bisallene_x", "reactant", "1 (1,5-bisallene; tether X)", e2),
        participant("s6_bisallene_y", "reactant", "second 1,5-bisallene (tether Y; may equal X)", e2),
        participant("s6_rh", "catalyst", "trans-RhCl(CO)(PPh3)2", e2),
        participant("s6_toluene", "solvent", "toluene", e2, "toluene", "Cc1ccccc1"),
        participant("s6_product_19", "product", "19 (18,19-norsteroid/heterosteroid derivative)", e2),
    ],
    [{"step_id": "rh_cyclization_cascade", "participant_ids": ["s6_bisallene_x", "s6_bisallene_y", "s6_rh", "s6_toluene", "s6_product_19"],
      "conditions": conditions(e2, solvent="toluene")}],
    [field("reported_yield_range", qr(57, 74, "%", "57–74%"), e2, ["s6_product_19"]),
     field("diastereoselectivity", "excellent", e2, ["s6_product_19"]), field("yield_measurement_basis", None, e2)],
    ["Scheme 6 summarizes cited work (references 9a/9b), including homo- and cross-cyclization where X may or may not equal Y."],
    ["Temperature, time, catalyst loading, and yield basis are absent.",
     "The generic tether set and qualitative diastereoselectivity do not resolve individual examples."]
))

# Cross-page records: the prose begins on page 2 and Schemes 7--9 appear on page 3.
e3 = ev(3)
e23 = e2 + e3
records.append(record(
    "scheme7_mechanistic_cross_cyclization", "Scheme 7", "mechanism", e23,
    [
        participant("s7_1b", "reactant", "1b (malonate-tethered 1,5-bisallene)", e23),
        participant("s7_1c", "reactant", "1c (sulfur-tethered 1,5-bisallene)", e23),
        participant("s7_rh", "catalyst", "trans-RhCl(CO)(PPh3)2", e23),
        participant("s7_toluene", "solvent", "toluene", e23, "toluene", "Cc1ccccc1"),
        participant("s7_19b", "product", "19b (normal cross-cyclization product)", e23),
        participant("s7_20", "product", "20 (tricyclic product supporting six-membered-ring-first pathway)", e23),
    ],
    [{"step_id": "mechanistic_cross_cyclization", "participant_ids": ["s7_1b", "s7_1c", "s7_rh", "s7_toluene", "s7_19b", "s7_20"],
      "conditions": conditions(e23, temperature="reflux", solvent="toluene")}],
    [field("product_19b_yield", None, e23, ["s7_19b"]), field("product_20_yield", None, e23, ["s7_20"])],
    ["Scheme 7 is explicitly captioned as evidence for the mechanism; the two observed products are retained without inventing yields."],
    ["Reaction time, catalyst loading, both product yields, and unique structures are not specified in this review figure."]
))
records.append(record(
    "scheme8_monoallene_trapping", "Scheme 8", "literature_example", e23,
    [
        participant("s8_bisallene", "reactant", "1,5-bisallene forming I-1a (X = C(SO2Ph)2)", e23),
        participant("s8_monoallene", "reactant", "monoallene (R = alkyl or aryl)", e23),
        participant("s8_rh", "catalyst", "trans-RhCl(CO)(PPh3)2", e23),
        participant("s8_product_21", "product", "21 (bicyclo[4.4.0]decene derivative)", e23),
    ],
    [{"step_id": "monoallene_trapping", "participant_ids": ["s8_bisallene", "s8_monoallene", "s8_rh", "s8_product_21"],
      "conditions": conditions(e23)}],
    [field("reported_yield_range", qr(46, 56, "%", "46–56%"), e23, ["s8_product_21"]), field("yield_measurement_basis", None, e23)],
    ["The review attributes this prior-literature trapping reaction to reference 9c."],
    ["Solvent, temperature, time, catalyst loading, measurement basis, and substrate-level outcomes are absent."]
))
records.append(record(
    "scheme9_seven_membered_ring", "Scheme 9", "literature_example", e23,
    [
        participant("s9_1d", "reactant", "1d (terminal-disubstituted 1,5-bisallene; X = NTs, O, or C(EWG)2)", e23),
        participant("s9_rh", "catalyst", "[RhCl(CO)2]2 or [RhCl(COD)]2 (alternative catalysts)", e23),
        participant("s9_solvent", "solvent", "MeCN or DMF (alternative solvents)", e23),
        participant("s9_product_23", "product", "23 (monocyclic seven-membered triene)", e23),
    ],
    [{"step_id": "rh_seven_membered_ring_formation", "participant_ids": ["s9_1d", "s9_rh", "s9_solvent", "s9_product_23"],
      "conditions": conditions(e23, solvent="MeCN or DMF (alternative solvents)")}],
    [field("reported_yield_range", qr(48, 78, "%", "48–78%"), e23, ["s9_product_23"]), field("yield_measurement_basis", None, e23)],
    ["Scheme 9 summarizes cited work (reference 10); catalyst/solvent alternatives are not assigned to individual members of the yield range."],
    ["Temperature, time, catalyst loading, measurement basis, and individual R/X outcomes are absent."]
))

# Page 3: Schemes 10--13 and explicit exceptions from the discussion.
records.append(record(
    "scheme10_corh_pauson_khand", "Scheme 10", "literature_example", e3,
    [
        participant("s10_1e", "reactant", "1e (generic 1,5-bisallene; X = NTs or O)", e3),
        participant("s10_corh", "catalyst", "Co2Rh2 nanoparticles", e3),
        participant("s10_co", "reagent", "CO", e3, "carbon monoxide", "[C-]#[O+]"),
        participant("s10_toluene", "solvent", "toluene", e3, "toluene", "Cc1ccccc1"),
        participant("s10_product_25", "product", "25 ([2+2+1] cycloadduct after 1,3-hydrogen shift)", e3),
    ],
    [{"step_id": "intramolecular_pauson_khand", "participant_ids": ["s10_1e", "s10_corh", "s10_co", "s10_toluene", "s10_product_25"],
      "conditions": conditions(e3, temperature=q(100, "°C"), solvent="toluene", extras=[field("CO_pressure", "2 atm", e3)])}],
    [field("reported_yield_range", qr(45, 68, "%", "45–68%"), e3, ["s10_product_25"]), field("yield_measurement_basis", None, e3)],
    ["Scheme 10 summarizes cited prior work (reference 12); intermediate I-2b and carbonylated intermediate 24 are mechanistic, not separate experiments."],
    ["Reaction time, catalyst loading, yield basis, and individual substrate results are absent."]
))
records.append(record(
    "scheme10_nts_me_failure", "Scheme 10 discussion exception", "literature_example", e3,
    [
        participant("s10f_1d", "reactant", "1d (X = NTs, R = Me)", e3),
        participant("s10f_corh", "catalyst", "Co/Rh nanoparticle system (context of Scheme 10)", e3),
        participant("s10f_desired", "product", "corresponding Pauson-Khand product (not afforded)", e3),
        participant("s10f_23", "product", "23 (monocyclic seven-membered triene; observed product)", e3),
    ],
    [{"step_id": "failed_pauson_khand_variant", "participant_ids": ["s10f_1d", "s10f_corh", "s10f_desired", "s10f_23"],
      "conditions": conditions(e3)}],
    [field("desired_product_formation", "not afforded", e3, ["s10f_desired"]),
     field("observed_product_yield", q(75, "%"), e3, ["s10f_23"]), field("yield_measurement_basis", None, e3)],
    ["The exception explicitly reports failure of the Pauson-Khand outcome and formation of Scheme 9 product 23 instead."],
    ["The exact operational conditions and yield basis for this exception are not restated."]
))
records.append(record(
    "scheme11_rh_pauson_khand", "Scheme 11", "literature_example", e3,
    [
        participant("s11_1f", "reactant", "1f (bis(phenylsulfonylallene) derivative; generic X/R1)", e3),
        participant("s11_rh", "catalyst", "[RhCl(CO)(dppp)]2 or [RhCl(CO)2]2 (alternative catalysts)", e3),
        participant("s11_co", "reagent", "CO", e3, "carbon monoxide", "[C-]#[O+]"),
        participant("s11_toluene", "solvent", "toluene", e3, "toluene", "Cc1ccccc1"),
        participant("s11_product_27", "product", "27 (bicyclo[5.3.0]decadienone)", e3),
    ],
    [{"step_id": "rh_pauson_khand", "participant_ids": ["s11_1f", "s11_rh", "s11_co", "s11_toluene", "s11_product_27"],
      "conditions": conditions(e3, temperature=q(80, "°C"), solvent="toluene")}],
    [field("reported_yield_range", qr(15, 100, "%", "15–100%"), e3, ["s11_product_27"]), field("yield_measurement_basis", None, e3)],
    ["Scheme 11 summarizes cited work (reference 13). The prose says [RhCl(CO)(dppp)]2 is generally better, except when X = C(CO2Me)2."],
    ["CO pressure, reaction time, catalyst loading, measurement basis, and row-level catalyst/yield mapping are absent."]
))
records.append(record(
    "scheme11_no_phenylsulfonyl_failure", "Scheme 11 no-SO2Ph exception", "literature_example", e3,
    [
        participant("s11n_substrate", "reactant", "1f analogue without phenylsulfonyl group", e3),
        participant("s11n_rh", "catalyst", "Rh catalyst system from Scheme 11 (exact alternative not assigned)", e3),
        participant("s11n_co", "reagent", "CO", e3, "carbon monoxide", "[C-]#[O+]"),
        participant("s11n_toluene", "solvent", "toluene", e3, "toluene", "Cc1ccccc1"),
        participant("s11n_product", "product", "corresponding [2+2+1] product", e3),
    ],
    [{"step_id": "no_phenylsulfonyl_control", "participant_ids": ["s11n_substrate", "s11n_rh", "s11n_co", "s11n_toluene", "s11n_product"],
      "conditions": conditions(e3, temperature=q(80, "°C"), solvent="toluene")}],
    [field("product_formation", "not afforded", e3, ["s11n_product"]), field("reported_yield", None, e3, ["s11n_product"])],
    ["The prose explicitly states that removal of the phenylsulfonyl group gives no [2+2+1] product."],
    ["Exact catalyst choice, CO pressure, reaction time, catalyst loading, and the analogue structure are not specified."]
))
records.append(record(
    "scheme11_r1_h_poor", "Scheme 11 R1=H exception", "literature_example", e3,
    [
        participant("s11h_1f", "reactant", "1f (R1 = H)", e3),
        participant("s11h_rh", "catalyst", "Rh catalyst system from Scheme 11 (exact alternative not assigned)", e3),
        participant("s11h_co", "reagent", "CO", e3, "carbon monoxide", "[C-]#[O+]"),
        participant("s11h_toluene", "solvent", "toluene", e3, "toluene", "Cc1ccccc1"),
        participant("s11h_27", "product", "27 (R1 = H variant)", e3),
    ],
    [{"step_id": "r1_h_variant", "participant_ids": ["s11h_1f", "s11h_rh", "s11h_co", "s11h_toluene", "s11h_27"],
      "conditions": conditions(e3, temperature=q(80, "°C"), solvent="toluene")}],
    [field("reported_yield", "poor", e3, ["s11h_27"]), field("reported_selectivity", "poor", e3, ["s11h_27"])],
    ["The review gives only qualitative yield and selectivity for the R1 = H case."],
    ["Exact yield, selectivity ratio/type, catalyst choice, CO pressure, time, and catalyst loading are absent."]
))
records.append(record(
    "scheme12_rh_entry", "Scheme 12 Rh entry", "literature_example", e3,
    [
        participant("s12r_1g", "reactant", "1g", e3),
        participant("s12r_rh", "catalyst", "[RhCl(CO)2]2", e3),
        participant("s12r_dppb", "reagent", "dppb", e3, "1,4-bis(diphenylphosphino)butane"),
        participant("s12r_co", "reagent", "CO", e3, "carbon monoxide", "[C-]#[O+]"),
        participant("s12r_dce", "solvent", "DCE", e3, "1,2-dichloroethane", "ClCCCl"),
        participant("s12r_28", "product", "28", e3),
    ],
    [{"step_id": "rh_pauson_khand", "participant_ids": ["s12r_1g", "s12r_rh", "s12r_dppb", "s12r_co", "s12r_dce", "s12r_28"],
      "conditions": conditions(e3, temperature="reflux", solvent="DCE", extras=[field("CO_pressure", "1 atm", e3)])}],
    [field("reported_yield", q(88, "%"), e3, ["s12r_28"]), field("yield_measurement_basis", None, e3)],
    ["This is one of two distinct literature examples shown by separate arrows in Scheme 12 (reference 14)."],
    ["Reaction time, catalyst/ligand loading, reflux temperature, and yield basis are absent.",
     "Structures 1g and 28 were not converted to SMILES from the small drawing."]
))
records.append(record(
    "scheme12_mo_entry", "Scheme 12 Mo entry", "literature_example", e3,
    [
        participant("s12m_1h", "reactant", "1h", e3),
        participant("s12m_moco6", "catalyst", "Mo(CO)6", e3, "molybdenum hexacarbonyl",
                    amounts=[field("equivalents", q(1.2, "equiv"), e3)]),
        participant("s12m_dmso", "reagent", "DMSO", e3, "dimethyl sulfoxide", "CS(C)=O",
                    amounts=[field("equivalents", q(10, "equiv"), e3)]),
        participant("s12m_mecn", "solvent", "MeCN", e3, "acetonitrile", "CC#N"),
        participant("s12m_29", "product", "29", e3),
    ],
    [{"step_id": "mo_pauson_khand", "participant_ids": ["s12m_1h", "s12m_moco6", "s12m_dmso", "s12m_mecn", "s12m_29"],
      "conditions": conditions(e3, time=q(30, "min"), temperature="reflux", solvent="MeCN")}],
    [field("reported_yield", q(34, "%"), e3, ["s12m_29"]), field("yield_measurement_basis", None, e3)],
    ["This is the second distinct arrow in Scheme 12; the source labels the transformation Mo-catalyzed despite 1.2 equivalents of Mo(CO)6."],
    ["Reflux temperature and yield basis are absent.",
     "Structures 1h and 29 were not converted to SMILES from the small drawing."]
))
records.append(record(
    "scheme13_pd_head_to_head", "Scheme 13", "literature_example", e3,
    [
        participant("s13_1", "reactant", "1 (generic 1,5-bisallene; X = NTs or C(EWG)2, etc.)", e3),
        participant("s13_pd", "catalyst", "Pd(PPh3)4", e3),
        participant("s13_tban_i", "reagent", "n-Bu4NI", e3, "tetrabutylammonium iodide", "CCCC[N+](CCCC)(CCCC)CCCC.[I-]"),
        participant("s13_9", "product", "9 (head-to-head bicyclo[3.2.0] product)", e3),
    ],
    [{"step_id": "pd_head_to_head_2plus2", "participant_ids": ["s13_1", "s13_pd", "s13_tban_i", "s13_9"],
      "conditions": conditions(e3)}],
    [field("reported_yield_range", qr(45, 66, "%", "45–66%"), e3, ["s13_9"]), field("yield_measurement_basis", None, e3)],
    ["Scheme 13 summarizes cited prior work (reference 18); I− is discussed as a ligand promoting reductive elimination."],
    ["Solvent, temperature, time, catalyst/additive loading, yield basis, and substrate-level outcomes are absent."]
))

# Page 4: Schemes 14 and 15. Their discussion starts on page 3, so retain both pages as evidence.
e4 = ev(4)
e34 = e3 + e4
records.append(record(
    "scheme14_thermal_2plus2", "Scheme 14", "literature_example", e34,
    [
        participant("s14_1i", "reactant", "1i (generic 1,5-bisallene; X = NTs or C(EWG)2)", e34),
        participant("s14_xylene", "solvent", "xylene (isomer not specified)", e34, "xylene"),
        participant("s14_30", "product", "30 (tail-to-tail bicyclo[5.2.0] product)", e34),
    ],
    [{"step_id": "thermal_tail_to_tail_2plus2", "participant_ids": ["s14_1i", "s14_xylene", "s14_30"],
      "conditions": conditions(e34, temperature="reflux", solvent="xylene")}],
    [field("reported_yield_range", qr(38, 78, "%", "38–78%"), e34, ["s14_30"]), field("yield_measurement_basis", None, e34)],
    ["Scheme 14 summarizes cited prior work (reference 18). R1/R2 may be H, Me, Et, or n-Pr."],
    ["Reaction time, xylene isomer/reflux temperature, yield basis, and individual substrate outcomes are absent.",
     "Generic substituents prevent unique substrate/product SMILES."]
))
records.append(record(
    "scheme15_au_2plus2", "Scheme 15", "literature_example", e34,
    [
        participant("s15_1j", "reactant", "1j (amino-tethered 1,5-bisallene; generic R/R1/R2)", e34),
        participant("s15_au", "catalyst", "Au(IPr)Cl", e34),
        participant("s15_agbf4", "reagent", "AgBF4", e34),
        participant("s15_32", "product", "32 (Au-catalyzed [2+2] cycloadduct)", e34),
    ],
    [{"step_id": "au_2plus2", "participant_ids": ["s15_1j", "s15_au", "s15_agbf4", "s15_32"],
      "conditions": conditions(e34)}],
    [field("reported_yield_range", qr(74, 98, "%", "74–98%"), e34, ["s15_32"]), field("yield_measurement_basis", None, e34)],
    ["Scheme 15 summarizes cited work (reference 19); Au intermediate 31 is a DFT-supported mechanistic intermediate, not a separate experiment."],
    ["Solvent, temperature, time, catalyst/cocatalyst loading, yield basis, and individual substrate outcomes are absent.",
     "Generic substituents prevent unique substrate/product SMILES."]
))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
