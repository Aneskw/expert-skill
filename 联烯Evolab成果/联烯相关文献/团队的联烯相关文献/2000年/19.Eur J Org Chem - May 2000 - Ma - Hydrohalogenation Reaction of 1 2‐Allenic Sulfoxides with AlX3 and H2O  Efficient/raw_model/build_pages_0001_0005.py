#!/usr/bin/env python3
"""Build evidence-linked extraction records for doc_8e6005e6970a463f, pages 1-5."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_8e6005e6970a463f"


def evidence(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def ev_pages(pages) -> list[str]:
    if isinstance(pages, int):
        pages = [pages]
    out: list[str] = []
    for page in pages:
        out.extend(evidence(page))
    return list(dict.fromkeys(out))


def fact(value, pages=None):
    if value is None:
        return {"value": None, "evidence_ids": [], "verification": "missing"}
    return {"value": value, "evidence_ids": ev_pages(pages), "verification": "unreviewed"}


def field(name, value, pages=None):
    return {"name": name, "fact": fact(value, pages)}


def participant(entity_id, role, label, pages, *, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, pages),
        "name": fact(name, pages) if name else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(k, v, p) for k, v, p in (amounts or [])],
    }


def record(
    suffix,
    kind,
    pages,
    participants,
    conditions=None,
    outcomes=None,
    notes=None,
    unresolved=None,
):
    pids = [p["entity_id"] for p in participants]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev_pages(pages),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": pids,
            "conditions": [field(k, v, p) for k, v, p in (conditions or [])],
        }] if participants or conditions else [],
        "outcomes": [field(k, v, p) for k, v, p in (outcomes or [])],
        "notes": [fact(v, p) for v, p in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": (unresolved or []) + [
                "No supporting-information file is supplied or explicitly associated; missing experimental details remain missing.",
                "Participant structures were not promoted to verified SMILES.",
            ],
        },
    }


def q(number, unit):
    return {"number": number, "unit": unit}


records = []

# Page 1: cited comparison and initial screening.
records.append(record(
    "scheme1_allenyl_sulfone_prior_hydrohalogenation", "literature_example", 1,
    [participant("sulfone_generic", "reactant", "1,2-allenyl sulfone (generic)", 1),
     participant("halide_generic", "reagent", "X− (X = Cl, Br, I)", 1),
     participant("halo_product_generic", "product", "β-halo allylic sulfone (generic)", 1)],
    conditions=[("acid", "H+", 1), ("temperature", "heat", 1)],
    outcomes=[("reported_yield_range", "79-87%", 1)],
    notes=[("Scheme 1 presents this successful sulfone reaction as earlier work cited in references 10-13.", 1)],
    unresolved=["Substrate-specific examples, quantities, time, solvent, workup, and yield basis are not given locally."],
))
records.append(record(
    "scheme1_allenyl_sulfoxide_prior_failure", "literature_example", 1,
    [participant("sulfoxide_generic", "reactant", "1,2-allenyl sulfoxide (generic)", 1),
     participant("halide_generic", "reagent", "X− (X = Cl, Br, I)", 1),
     participant("low_polarity_mixture", "product", "mixture of products with low polarity", 1)],
    conditions=[("acid", "H+", 1), ("temperature", "heat", 1)],
    outcomes=[("expected_2_haloallyl_sulfoxide_observed", False, 1),
              ("observed_result", "mixture of products with low polarity", 1)],
    notes=[("Scheme 1 contrasts the failed sulfoxide result with the cited sulfone chemistry.", 1)],
    unresolved=["Exact halide, temperature, time, quantities, solvent, and analytical basis are not reported locally."],
))

for reagent, suffix in [
    ("FeCl3", "fecl3"), ("ZnBr2", "znbr2"), ("MgCl2", "mgcl2"),
    ("Al2O3", "al2o3"), ("Ti(OiPr)4", "ti_oipr4"),
]:
    records.append(record(
        f"lewis_acid_screen_{suffix}_no_effect", "optimization_entry", 1,
        [participant("substrate_1a", "reactant", "1a", 1,
                     name="(1,2-propadienylsulfinyl)benzene"),
         participant("screening_reagent", "reagent", reagent, 1)],
        outcomes=[("catalytic_effect_observed", False, 1)],
        notes=[(f"The article states that {reagent} did not show any catalytic effect during condition screening.", 1)],
        unresolved=["Exact reagent loading, solvent, temperature, time, product analysis, and numerical yield are not reported for this screen."],
    ))

records.append(record(
    "initial_alcl3_then_water_quench_2aa", "reported_experiment", 1,
    [participant("substrate_1a", "reactant", "1a", 1,
                 name="(1,2-propadienylsulfinyl)benzene"),
     participant("alcl3", "reagent", "AlCl3", 1),
     participant("thf", "solvent", "THF", 1),
     participant("water", "reagent", "H2O (quench after reaction)", 1),
     participant("product_2aa", "product", "2aa", 1,
                 name="[(2-chloro-2-propenyl)sulfinyl]benzene")],
    conditions=[("reaction_temperature", "room temperature", 1),
                ("reaction_time", q(24, "h"), 1),
                ("addition_order", "AlCl3 reaction first; H2O added as quench", 1)],
    outcomes=[("yield", q(40, "%"), 1)],
    unresolved=["Substrate scale, AlCl3 loading, water amount, workup detail, and yield basis are not specified in the displayed initial experiment."],
))

# Table 1. Entry 7 is also Table 2 entry 1 and the detailed 2aa procedure.
table1_al = [1.1, 1.1, 1.1, 1.1, 1.1, 0.38, 0.55, 0.77]
table1_h2o = [1, 2, 3, 4, 6, 1, 1, 1]
table1_y = [97, 96, 96, 95, 6, 87, 95, 96]
for entry, (al, water, yld) in enumerate(zip(table1_al, table1_h2o, table1_y), 1):
    pages = [1, 2, 3] if entry == 7 else 1
    ps = [
        participant("substrate_1a", "reactant", "1a", pages,
                    name="(1,2-propadienylsulfinyl)benzene",
                    amounts=[("mass", q(164, "mg"), 3), ("amount", q(1.0, "mmol"), 3)] if entry == 7 else []),
        participant("alcl3", "reagent", "commercial AlCl3", pages,
                    amounts=[("equivalents", q(al, "equiv"), 1)] +
                            ([('solution_concentration', q(0.55, 'M'), 3), ('solution_volume', q(1, 'mL'), 3), ('amount', q(0.55, 'mmol'), 3)] if entry == 7 else [])),
        participant("water", "reagent", "H2O", pages,
                    amounts=[("equivalents", q(water, "equiv"), 1)] +
                            ([('solution_concentration', q(1, 'M'), 3), ('solution_volume', q(1, 'mL'), 3), ('amount', q(1, 'mmol'), 3)] if entry == 7 else [])),
        participant("thf", "solvent", "THF", pages,
                    amounts=[("volume", q(3, "mL"), 3)] if entry == 7 else []),
        participant("product_2aa", "product", "2aa", pages,
                    name="[(2-chloro-2-propenyl)sulfinyl]benzene",
                    amounts=[("isolated_mass", q(177, "mg"), 3)] if entry == 7 else []),
    ]
    outcomes = [("nmr_yield", q(yld, "%"), 1),
                ("nmr_internal_standard", "CH2Br2", 1)]
    conds = [("solvent", "THF", 1), ("temperature", "room temperature", 1),
             ("time", q(4, "h"), 1)]
    notes = []
    unresolved = ["Row-specific substrate mass, solution volumes, workup, and purification are not reported for this optimization row."]
    if entry == 7:
        outcomes += [("isolated_yield", q(89, "%"), [2, 3]),
                     ("physical_form", "solid", 3),
                     ("melting_point", "46-47 °C", 3)]
        conds += [
            ("monitoring", "TLC; 1,2-dichloroethane/THF 20:1", 3),
            ("quench", "water (2 mL)", 3),
            ("extraction", "diethyl ether (2 × 10 mL)", 3),
            ("drying", "MgSO4", 3),
            ("purification", "flash chromatography on silica gel; hexane/ethyl acetate 2:1", 3),
        ]
        notes += [
            ("This record merges Table 1 entry 7, the with-water kinetic presentation, Table 2 entry 1, and the detailed 2aa procedure because substrate, reagent ratio, solvent, temperature, and 4 h time match.", [1, 2, 3]),
            ("The two reported yields have different bases: 95% NMR in Table 1 and 89% isolated in Table 2/Experimental.", [1, 2, 3]),
        ]
        unresolved = ["Reaction concentration and product purity are not reported; Figure 1 point values beyond the textual 4 h result were not digitized."]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", pages, ps,
        conditions=conds, outcomes=outcomes, notes=notes, unresolved=unresolved,
    ))

# Additional prose comparisons and failures on page 2.
records.append(record(
    "kinetic_comparison_no_added_water", "reported_experiment", 2,
    [participant("substrate_1a", "reactant", "1a", 2,
                 amounts=[("amount", q(1.0, "mmol"), 2)]),
     participant("alcl3", "reagent", "commercial AlCl3", 2,
                 amounts=[("amount", q(0.55, "mmol"), 2), ("solution_volume", q(1, "mL"), 2)]),
     participant("thf", "solvent", "THF", 2),
     participant("product_2aa", "product", "2aa", 2)],
    conditions=[("added_water", False, 2), ("temperature", "room temperature", 2),
                ("monitoring_interval", "0-5 h as plotted in Figure 1", 2)],
    outcomes=[("qualitative_result", "much slower product formation than the with-water reaction", 2)],
    notes=[("Approximate graph points were not converted into exact yields.", 2)],
    unresolved=["The exact no-water time-series values and analytical sampling procedure are not stated in text."],
))
records.append(record(
    "purified_dry_alcl3_no_water", "reported_experiment", 2,
    [participant("substrate_1a", "reactant", "1a", 2),
     participant("alcl3", "reagent", "AlCl3 purified and dried by sublimation", 2),
     participant("product_2aa", "product", "2aa", 2)],
    conditions=[("water_added", False, 2), ("time", q(5, "h"), 2)],
    outcomes=[("yield", q(5, "%"), 2), ("starting_material_recovered", q(90, "%"), 2)],
    unresolved=["AlCl3 loading, solvent, temperature, workup, and yield basis are not fully restated for this comparison."],
))
records.append(record(
    "acetonitrile_solvent_comparison", "reported_experiment", 2,
    [participant("substrate_1a", "reactant", "1a", 2),
     participant("alcl3", "reagent", "AlCl3", 2),
     participant("water", "reagent", "H2O", 2),
     participant("acetonitrile", "solvent", "CH3CN", 2),
     participant("product_2aa", "product", "2aa", 2)],
    conditions=[("temperature", "room temperature", 2), ("time", q(18, "h"), 2)],
    outcomes=[("yield", q(55, "%"), 2), ("starting_material_remaining", q(40, "%"), 2)],
    unresolved=["Exact reagent charges, workup, purification, and yield basis are not reported for this solvent comparison."],
))

for label, name in [
    ("1e", "1-methyl-1-(methylsulfinyl)-1,2-propadiene"),
    ("1f", "(1-methyl-1,2-propadienylsulfinyl)benzene"),
    ("1g", "(3-methyl-1,2-butadienylsulfinyl)benzene"),
]:
    records.append(record(
        f"sterically_hindered_{label}_no_reaction", "substrate_scope_entry", [1, 2],
        [participant(f"substrate_{label}", "reactant", label, [1, 2], name=name)],
        outcomes=[("reaction_proceeded", False, [1, 2])],
        notes=[("The authors attribute the lack of reaction to substrate steric hindrance.", [1, 2])],
        unresolved=["The phrase 'under the same reaction conditions' does not uniquely identify AlCl3 versus AlBr3, reagent quantities, time, or analytical detection limit."],
    ))

# Table 2 entries 2-8, merged with their detailed experimental paragraphs.
scope = [
    dict(entry=2, sub="1a", subname="(1,2-propadienylsulfinyl)benzene", smass=164, smmol=1,
         reagent="AlBr3", rconc=1, rvol=1, rmmol=1, rsolv="CS2", water=(1, 1, 1), extra_thf=None,
         product="2ab", pname="[(2-bromo-2-propenyl)sulfinyl]benzene", time=1, mass=199, y=81, ratio=None, pages=[2, 3]),
    dict(entry=3, sub="1b", subname="1-(methylsulfinyl)-1,2-propadiene", smass=51, smmol=.5,
         reagent="AlCl3", rconc=.55, rvol=.5, rmmol=.27, rsolv="THF", water=(.5, 1, .5), extra_thf=None,
         product="2ba", pname="2-chloro-3-(methylsulfinyl)-1-propene", time=1.5, mass=49, y=71, ratio=None, pages=[2, 3]),
    dict(entry=4, sub="1b", subname="1-(methylsulfinyl)-1,2-propadiene", smass=51, smmol=.5,
         reagent="AlBr3", rconc=1, rvol=.5, rmmol=.5, rsolv="CS2", water=None, extra_thf=1,
         product="2bb", pname="2-bromo-3-(methylsulfinyl)-1-propene", time=29, mass=58, y=64, ratio=None, pages=[2, 3, 4]),
    dict(entry=5, sub="1c", subname="(1,2-butadienylsulfinyl)benzene", smass=534, smmol=3,
         reagent="AlCl3", rconc=.55, rvol=3, rmmol=1.65, rsolv="THF", water=(1, 3, 3), extra_thf=None,
         product="2ca", pname="[(2-chloro-2-butenyl)sulfinyl]benzene", time=4, mass=522, y=81, ratio="65:35", pages=[2, 4]),
    dict(entry=6, sub="1c", subname="(1,2-butadienylsulfinyl)benzene", smass=178, smmol=1,
         reagent="AlBr3", rconc=.55, rvol=2, rmmol=1, rsolv="CS2", water=(1, .5, .5), extra_thf=None,
         product="2cb", pname="[(2-bromo-2-butenyl)sulfinyl]benzene", time=8.5, mass=195, y=75, ratio="83:17", pages=[2, 4]),
    dict(entry=7, sub="1d", subname="(1,2-heptadienylsulfinyl)benzene", smass=220, smmol=1,
         reagent="AlCl3", rconc=.55, rvol=1, rmmol=.55, rsolv="THF", water=(.5, 2.5, 1.25), extra_thf=None,
         product="2da", pname="[(2-chloro-2-heptenyl)sulfinyl]benzene", time=7, mass=211, y=82, ratio="60:40", pages=[2, 4]),
    dict(entry=8, sub="1d", subname="(1,2-heptadienylsulfinyl)benzene", smass=220, smmol=1,
         reagent="AlBr3", rconc=1, rvol=1, rmmol=1, rsolv="CS2", water=(.5, 2.5, 1.25), extra_thf=2,
         product="2db", pname="[(2-bromo-2-heptenyl)sulfinyl]benzene", time=3.5, mass=169, y=56, ratio="83:17", pages=[2, 4]),
]
for row in scope:
    pages = row["pages"]
    ps = [
        participant(f"substrate_{row['sub']}", "reactant", row["sub"], pages, name=row["subname"],
                    amounts=[("mass", q(row["smass"], "mg"), pages[-1]), ("amount", q(row["smmol"], "mmol"), pages[-1])]),
        participant(row["reagent"].lower(), "reagent", row["reagent"], pages,
                    amounts=[("solution_concentration", q(row["rconc"], "M"), pages[-1]),
                             ("solution_volume", q(row["rvol"], "mL"), pages[-1]),
                             ("reported_amount", q(row["rmmol"], "mmol"), pages[-1])]),
        participant("product_" + row["product"], "product", row["product"], pages, name=row["pname"],
                    amounts=[("isolated_mass", q(row["mass"], "mg"), pages[-1])]),
    ]
    if row["water"]:
        wc, wv, wm = row["water"]
        ps.append(participant("water", "reagent", "H2O", pages,
                              amounts=[("solution_concentration", q(wc, "M"), pages[-1]),
                                       ("solution_volume", q(wv, "mL"), pages[-1]),
                                       ("amount", q(wm, "mmol"), pages[-1])]))
    if row["extra_thf"] is not None:
        ps.append(participant("thf", "solvent", "THF", pages,
                              amounts=[("volume", q(row["extra_thf"], "mL"), pages[-1])]))
    outs = [("isolated_yield", q(row["y"], "%"), pages)]
    if row["ratio"]:
        outs.append(("Z_E_ratio", row["ratio"], pages))
    unresolved = ["Atmosphere, reaction concentration, and full workup/purification are not restated for this similarly prepared product."]
    notes = [("Table 2 supplies the reaction time and isolated-yield basis; the Experimental section supplies charges and isolated mass.", pages)]
    if row["entry"] == 6:
        notes.append(("The source prints AlBr3 as 0.55 M in CS2, 2 mL, 1 mmol; the concentration-volume product is not silently reconciled with the printed mmol value.", 4))
        unresolved.append("Printed AlBr3 concentration/volume/amount inconsistency requires source review.")
    if row["entry"] in (7, 8):
        notes.append(("The isolated E isomer is described as contaminated by a trace amount of the Z isomer.", 4))
    records.append(record(
        f"table2_entry{row['entry']}", "substrate_scope_entry", pages, ps,
        conditions=[("reagent_solution_solvent", row["rsolv"], pages[-1]),
                    ("temperature", "room temperature", 2),
                    ("time", q(row["time"], "h"), 2),
                    ("water_used", bool(row["water"]), pages)],
        outcomes=outs, notes=notes, unresolved=unresolved,
    ))

# Hydroiodination and the one-equivalent NaI comparison.
records.append(record(
    "nai_one_equiv_chlorination_side_product", "optimization_entry", 2,
    [participant("substrate_1a", "reactant", "1a", 2, amounts=[("equivalents", q(1, "equiv"), 2)]),
     participant("nai", "reagent", "NaI", 2, amounts=[("equivalents", q(1, "equiv"), 2)]),
     participant("alcl3", "reagent", "AlCl3", 2, amounts=[("equivalents", q(.55, "equiv"), 2)]),
     participant("product_2aa", "product", "hydrochlorination product 2aa", 2)],
    outcomes=[("2aa_yield", q(20, "%"), 2)],
    unresolved=["Water amount, solvent, temperature, time, iodinated-product outcome, workup, and yield basis are not stated in this comparison sentence."],
))
records.append(record(
    "scheme3_2ac_hydroiodination", "substrate_scope_entry", [2, 4],
    [participant("substrate_1a", "reactant", "1a", [2, 4], name="(1,2-propadienylsulfinyl)benzene",
                 amounts=[("mass", q(164, "mg"), 4), ("amount", q(1, "mmol"), 4)]),
     participant("nai", "reagent", "dry NaI", [2, 4], amounts=[("mass", q(600, "mg"), 4), ("amount", q(4, "mmol"), 4)]),
     participant("water", "reagent", "H2O", [2, 4], amounts=[("solution_concentration", q(1, "M"), 4), ("solution_volume", q(1, "mL"), 4), ("amount", q(1, "mmol"), 4)]),
     participant("alcl3", "reagent", "AlCl3", [2, 4], amounts=[("solution_concentration", q(.55, "M"), 4), ("solution_volume", q(1, "mL"), 4), ("amount", q(.55, "mmol"), 4)]),
     participant("thf", "solvent", "THF", [2, 4], amounts=[("volume", q(2, "mL"), 4)]),
     participant("product_2ac", "product", "2ac", [2, 4], name="[(2-iodo-2-propenyl)sulfinyl]benzene",
                 amounts=[("isolated_mass", q(230, "mg"), 4)]),
     participant("product_2aa", "product", "hydrochlorination product 2aa", 2)],
    conditions=[("atmosphere", "nitrogen", 4), ("temperature", "room temperature", [2, 4]),
                ("time", q(4, "h"), [2, 4]), ("monitoring", "TLC; 1,2-dichloroethane/THF 20:1", 4),
                ("quench", "water (2 mL)", 4), ("extraction", "diethyl ether (2 × 10 mL)", 4),
                ("drying", "MgSO4", 4),
                ("purification", "flash chromatography on silica gel; hexane/ethyl acetate 2:1", 4)],
    outcomes=[("isolated_yield", q(79, "%"), [2, 4]),
              ("hydrochlorination_product_2aa_observed", False, 2),
              ("physical_form", "liquid", 4)],
    notes=[("The no-2aa statement for four equivalents of NaI and 0.55 equivalents of AlCl3 is merged with the matching typical 2ac procedure.", [2, 4])],
    unresolved=["Product purity and reaction concentration are not reported."],
))
records.append(record(
    "scheme3_2cc_hydroiodination", "substrate_scope_entry", [2, 4, 5],
    [participant("substrate_1c", "reactant", "1c", [2, 4], name="(1,2-butadienylsulfinyl)benzene",
                 amounts=[("mass", q(89, "mg"), 4), ("amount", q(.5, "mmol"), 4)]),
     participant("nai", "reagent", "NaI", [2, 4], amounts=[("mass", q(300, "mg"), 4), ("amount", q(2, "mmol"), 4)]),
     participant("alcl3", "reagent", "AlCl3", [2, 4], amounts=[("solution_concentration", q(.55, "M"), 4), ("solution_volume", q(.5, "mL"), 4), ("amount", q(.27, "mmol"), 4)]),
     participant("water", "reagent", "H2O", [2, 4], amounts=[("solution_concentration", q(1, "M"), 4), ("solution_volume", q(.5, "mL"), 4), ("amount", q(.5, "mmol"), 4)]),
     participant("product_2cc", "product", "2cc", [2, 4, 5], name="[(2-iodo-2-butenyl)sulfinyl]benzene",
                 amounts=[("isolated_mass", q(105, "mg"), 4)])],
    conditions=[("temperature", "room temperature", 2), ("time", q(3, "h"), 2),
                ("preparation_relation", "prepared similarly to Conditions B for 2ac", 4)],
    outcomes=[("isolated_yield", q(69, "%"), [2, 4]), ("Z_E_ratio", "92:8", [2, 4]),
              ("Z_isomer_configuration_method", "2D 1H-1H NOESY", 2),
              ("Z_isomer_physical_form", "liquid", 4), ("E_isomer_description", "crude product", 5)],
    unresolved=["THF volume, atmosphere, row-specific workup/purification, and purity are not independently restated for 2cc."],
))

# Scheme 4 observed isomerization and its proposed pathway.
records.append(record(
    "scheme4_e_2cb_isomerization", "reported_experiment", [2, 3],
    [participant("e_2cb", "reactant", "(E)-2cb", [2, 3]),
     participant("z_2cb", "product", "(Z)-2cb", [2, 3]),
     participant("remaining_e_2cb", "product", "remaining (E)-2cb", 3)],
    conditions=[("temperature", q(60, "°C"), [2, 3]), ("time", q(2, "h"), [2, 3])],
    outcomes=[("Z_isomer", q(86, "%"), 3), ("E_isomer", q(14, "%"), 3)],
    unresolved=["Scale, solvent, atmosphere, workup, and analytical basis are not reported."],
))
records.append(record(
    "scheme4_sigmatropic_rearrangement_mechanism", "mechanism", 3,
    [participant("e_2cb", "reactant", "(E)-2cb", 3),
     participant("z_2cb", "product", "(Z)-2cb", 3)],
    outcomes=[("proposed_process", "[2,3]-sigmatropic rearrangement converting E to thermodynamically more stable Z isomer", 3)],
    notes=[("The cyclic structures in Scheme 4 are proposed intermediates/transition representations, not isolated species.", 3)],
    unresolved=["The mechanism is proposed, not directly established by isolation of intermediates."],
))

# Page 3 controls and mechanistic probes (Scheme 5 plus prose-only comparisons).
controls = [
    dict(suffix="nacl_hoac_rt", agent="NaCl", amounts=[], solvent="HOAc", temp="room temperature", time=None,
         outcomes=[("product_2aa_observed_in_decent_yield", False), ("starting_material_recovered", ">95%")],
         note="Prose-only NaCl control."),
    dict(suffix="licl_hoac_rt", agent="LiCl", amounts=[("equivalents", q(2.0, "equiv"))], solvent="HOAc", temp="room temperature", time=q(4, "h"),
         outcomes=[("product_2aa_observed_in_decent_yield", False), ("starting_material_recovered", ">90%")],
         note="Scheme 5 LiCl/HOAc control."),
    dict(suffix="licl_hoac_hot", agent="LiCl", amounts=[], solvent="HOAc", temp="95-100 °C", time=None,
         outcomes=[("starting_material_consumed_completely", True), ("observed_result", "complex mixture of products with low polarity")],
         note="High-temperature LiCl/HOAc control."),
    dict(suffix="licl_h2so4_aq", agent="LiCl + aqueous H2SO4", amounts=[("H2SO4_equivalents", q(2, "equiv"))], solvent="THF", temp="room temperature", time=None,
         outcomes=[("starting_material_consumed_completely", True), ("observed_result", "complex mixture of products with low polarity")],
         note="Acidic LiCl/H2SO4 control."),
    dict(suffix="aqueous_hcl", agent="aqueous HCl", amounts=[("equivalents", "1-2 equiv")], solvent="THF/H2O", temp="room temperature", time=q(4, "h"),
         outcomes=[("starting_material_recovered", ">95%")], note="Scheme 5 aqueous-HCl control."),
    dict(suffix="gaseous_hcl", agent="gaseous HCl", amounts=[], solvent="THF", temp="room temperature", time=q(4, "h"),
         outcomes=[("starting_material_recovered", ">85%")], note="Scheme 5 gaseous-HCl control."),
]
for c in controls:
    records.append(record(
        "scheme5_" + c["suffix"], "reported_experiment", 3,
        [participant("substrate_1a", "reactant", "1a", 3),
         participant("agent", "reagent", c["agent"], 3,
                     amounts=[(k, v, 3) for k, v in c["amounts"]]),
         participant("solvent", "solvent", c["solvent"], 3)],
        conditions=[("temperature", c["temp"], 3), ("time", c["time"], 3)],
        outcomes=[(k, v, 3) for k, v in c["outcomes"]],
        notes=[(c["note"], 3)],
        unresolved=["Unstated quantities, workup, product identities, detection limit, and yield/recovery measurement basis remain missing."],
    ))

records.append(record(
    "scheme5_alcl3_d2o_probe", "reported_experiment", 3,
    [participant("substrate_1a", "reactant", "1a", 3),
     participant("d2o", "reagent", "D2O", 3, amounts=[("equivalents", q(1.0, "equiv"), 3)]),
     participant("alcl3", "reagent", "AlCl3", 3, amounts=[("equivalents", q(.55, "equiv"), 3)]),
     participant("thf", "solvent", "THF", 3),
     participant("product_2aa_d", "product", "deuterated 2aa", 3),
     participant("product_2aa_h", "product", "non-deuterated 2aa", 3)],
    conditions=[("temperature", "room temperature", 3), ("time", q(4, "h"), 3)],
    outcomes=[("combined_yield", q(89, "%"), 3), ("deuterated_fraction", "~70%", 3),
              ("non_deuterated_fraction", "~30%", 3)],
    unresolved=["Scale, workup, purification, isotopic-analysis method, and yield basis are not stated."],
))

for equiv, yld, recovered in [(.5, 71, 19), (1.0, 67, 33)]:
    tag = "0_5eq" if equiv == .5 else "1_0eq"
    records.append(record(
        f"scheme5_triethylamine_{tag}", "optimization_entry", 3,
        [participant("substrate_1a", "reactant", "1a", 3),
         participant("water", "reagent", "H2O", 3, amounts=[("equivalents", q(1.0, "equiv"), 3)]),
         participant("alcl3", "reagent", "AlCl3", 3, amounts=[("equivalents", q(.55, "equiv"), 3)]),
         participant("triethylamine", "reagent", "Et3N", 3, amounts=[("equivalents", q(equiv, "equiv"), 3)]),
         participant("thf", "solvent", "THF", 3),
         participant("product_2aa", "product", "2aa", 3)],
        conditions=[("temperature", "room temperature", 3), ("time", q(4, "h"), 3)],
        outcomes=[("2aa_yield", q(yld, "%"), 3), ("starting_material_recovered", q(recovered, "%"), 3)],
        notes=[("Triethylamine slowed the reaction, which the authors attribute to complexation with Al(III).", 3)],
        unresolved=["Scale, workup, purification, and yield/recovery measurement bases are not reported."],
    ))

records.append(record(
    "proposed_aluminum_mediated_hydrohalogenation", "mechanism", 3,
    [], outcomes=[("proposed_mechanism", "Al(III)-mediated nucleophilic attack of X− at the middle carbon of the electron-deficient allene", 3)],
    notes=[("The proposal follows the acid controls, D2O labeling, and triethylamine inhibition observations; no discrete intermediate is reported as isolated.", 3)],
    unresolved=["The exact AlX3/H2O active species and full elementary-step sequence are not established."],
))

# General/reagent preparation context from the Experimental section.
records.append(record(
    "albr3_reagent_preparation", "reported_experiment", 3,
    [participant("aluminum", "reactant", "Al", 3), participant("bromine", "reactant", "Br2", 3),
     participant("cs2", "solvent", "CS2", 3), participant("albr3", "product", "AlBr3", 3)],
    conditions=[("temperature", "reflux", 3), ("time", q(3, "h"), 3)],
    notes=[("AlBr3 was prepared according to reference 20.", 3)],
    unresolved=["Quantities, atmosphere, workup, purification, isolated amount, and yield are not provided locally."],
))
records.append(record(
    "starting_materials_1a_1g_cited_preparations", "literature_example", 3,
    [participant("starting_material_family", "product", "1a-1g (1,2-allenic sulfoxides)", 3)],
    notes=[("Compounds 1a-1g are stated to have been prepared according to published procedures in reference 21.", 3)],
    unresolved=["Individual precursor identities, quantities, conditions, workups, purification, and yields are not reported in this paper."],
))


# Coverage ledger derives page-linked record IDs but keeps region-level source decisions explicit.
def ids_for_page(page: int) -> list[str]:
    token = f":page{page}:"
    return [r["record_id"] for r in records if any(token in eid for eid in r["evidence_ids"])]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper article header, abstract, and introduction", "finding": "Article scope, optimized 1:0.55:1 ratio, 56-89% isolated-yield range, and no-reaction substrates 1e-1g were checked; introduction cites earlier allene hydrohalogenation work.", "evidence_ids": evidence(1)},
                {"region": "Scheme 1", "finding": "Prior/cited sulfone hydrohalogenation and contrasting sulfoxide failure were classified as literature examples, not current successful experiments.", "evidence_ids": evidence(1)},
                {"region": "Results and Discussion screening prose", "finding": "Five ineffective Lewis-acid screens and the initial 40% AlCl3/then-water result were extracted separately.", "evidence_ids": evidence(1)},
                {"region": "Table 1 and its reaction drawings/footnotes", "finding": "Eight optimization rows were extracted; commercial AlCl3, THF solution concentrations, H2O equivalents, and CH2Br2 NMR basis were applied row by row.", "evidence_ids": evidence(1)},
            ],
            "record_ids": ids_for_page(1),
            "unresolved": ["Scheme 1 local conditions are incomplete and attributed to earlier work.", "Exact conditions and numerical outcomes for the five ineffective Lewis-acid screens are not printed."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Figure 1 and adjacent kinetics prose", "finding": "With-water and no-added-water monitoring were checked; graph points were not falsely digitized as exact values.", "evidence_ids": evidence(2)},
                {"region": "solvent, dry-AlCl3, and substrate-failure prose", "finding": "Dry-AlCl3/no-water, CH3CN comparison, and failures of 1e-1g were retained with missing conditions explicit.", "evidence_ids": evidence(2)},
                {"region": "Scheme 2 and Table 2 including footnotes", "finding": "Eight substrate/halide rows were reviewed; entry 1 was merged with Table 1 entry 7 and the 2aa procedure, while entries 2-8 remain distinct.", "evidence_ids": evidence(2)},
                {"region": "Scheme 3, hydroiodination prose, and Figure 2", "finding": "2ac, 2cc, the one-equivalent NaI side-product run, and NOESY assignment were linked without treating Figure 2 as a reaction.", "evidence_ids": evidence(2)},
                {"region": "bottom isomerization prose", "finding": "The E-2cb to Z-2cb experiment continues onto page 3 and was merged across pages.", "evidence_ids": evidence(2)},
            ],
            "record_ids": ids_for_page(2),
            "unresolved": ["The exact conditions for the reported 1e-1g failures are not uniquely specified.", "Figure 1 exact plotted values are not tabulated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 4 and isomerization prose", "finding": "Observed 60 °C/2 h isomerization was separated from the proposed [2,3]-sigmatropic pathway.", "evidence_ids": evidence(3)},
                {"region": "control-experiment prose and Scheme 5", "finding": "NaCl, LiCl, hot/acidic LiCl, aqueous/gaseous HCl, D2O, and two Et3N-load controls were split by condition and explicit failures/recoveries retained.", "evidence_ids": evidence(3)},
                {"region": "conclusion and general Experimental section", "finding": "Proposed Al(III)-mediated mechanism, cited 1a-1g preparations, and the local AlBr3 preparation were classified separately.", "evidence_ids": evidence(3)},
                {"region": "2aa, 2ab, 2ba, and 2bb preparation paragraphs", "finding": "Detailed charges and isolated masses were merged into matching Table 1/Table 2 records rather than duplicated.", "evidence_ids": evidence(3)},
            ],
            "record_ids": ids_for_page(3),
            "unresolved": ["Most control experiments omit scale, measurement basis, workup, and product detection limits.", "The mechanistic active aluminum species is not identified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "2ca, 2cb, 2da, and 2db preparation/characterization paragraphs", "finding": "Charges, isolated masses, yields, Z/E ratios, physical descriptions, and trace Z contamination statements were linked to Table 2 entries 5-8.", "evidence_ids": evidence(4)},
                {"region": "2ac typical procedure", "finding": "Full Conditions-B charge, nitrogen atmosphere, TLC, workup, chromatography, mass, and isolated yield were merged with Scheme 3.", "evidence_ids": evidence(4)},
                {"region": "2cc abbreviated preparation", "finding": "Printed charges, isolated mass, yield, and Z/E ratio were linked to Scheme 3; 'prepared similarly' was not expanded into unprinted row-specific quantities.", "evidence_ids": evidence(4)},
            ],
            "record_ids": ids_for_page(4),
            "unresolved": ["The 2cb AlBr3 concentration × volume does not equal the printed mmol value.", "Several procedures say products were prepared similarly and do not restate atmosphere/workup/purification."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of 2cc characterization", "finding": "Z-2cc characterization continuation and crude E-isomer description were linked to the existing 2cc reaction; no new experiment was created.", "evidence_ids": evidence(5)},
                {"region": "acknowledgments and references", "finding": "No current-paper reaction experiment is reported; bibliography entries were not converted into experiments.", "evidence_ids": evidence(5)},
                {"region": "remaining lower page area", "finding": "Blank/article-footer area contains no reaction, table, arrow, or experimental procedure.", "evidence_ids": evidence(5)},
            ],
            "record_ids": ids_for_page(5),
            "unresolved": ["No SI is supplied; characterization beyond the printed main-text data remains unavailable."],
        },
    ],
}


raw_path = RUN / "raw_model" / "records_pages_0001_0005.json"
coverage_path = RUN / "coverage" / "pages_0001_0005.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 6)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; reaction-bearing regions checked and represented in coverage ledger."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
