#!/usr/bin/env python3
"""Build evidence-linked records for jo991574t, PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_eba910143e10eeee"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"


def ev(page):
    return f"{DOC}:page{page}:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name else ()),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, conditions=None, outcomes=None,
           notes=None, unresolved=None):
    rid = f"{DOC}:{suffix}"
    return {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions or [],
        }],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Structures are represented by source labels only and remain unverified.",
                "No supporting-information file was supplied or associated; missing experimental details remain unresolved.",
            ],
        },
    }


def missing_conditions():
    return [field("atmosphere", None), field("concentration", None)]


def product_outcomes(product, yield_value, evidence, basis=None, extra=None):
    out = [field("product", product, evidence), field("yield", yield_value, evidence)]
    out.append(field("yield_measurement_basis", basis, evidence if basis else ()))
    for name, value in (extra or []):
        out.append(field(name, value, evidence))
    return out


records = []

# Page 1: generic proposal, four Conditions-A variants, and the explicit NCS failure.
records.append(record(
    "general_scheme_1", "general_scheme", [ev(1)],
    [participant("gs1_allenoic_acid", "reactant", "generic 2,3-allenoic acid 1 (R1/R2/R3)", [ev(1)]),
     participant("gs1_cux2", "reagent", "CuX2", [ev(1)]),
     participant("gs1_product", "product", "generic beta-halobutenolide 2", [ev(1)])],
    [field("conditions", None)],
    notes=["Scheme 1 is a proposed generic transformation with variable R groups and X; it is not an individual reported run."],
))


def cond_a(suffix, halide, additive, time_h, yield_pct, start_mg=None,
           start_mmol=None, product_mg=None, second_yield=None):
    evidence = [ev(1), ev(3)]
    reagent = f"Cu{halide}2"
    product = "2aa" if halide == "Cl" else "2ab"
    ps = [participant(f"{suffix}_1a", "reactant", "1a", evidence,
                      "2-methyl-4-phenyl-2,3-butadienoic acid",
                      [field("mass", {"number": start_mg, "unit": "mg"}, [ev(3)]) if start_mg is not None else field("mass", None),
                       field("amount", {"number": start_mmol, "unit": "mmol"}, [ev(3)]) if start_mmol is not None else field("amount", None)]),
          participant(f"{suffix}_{reagent.lower()}", "reagent", reagent, evidence,
                      amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, [ev(1)])]),
          participant(f"{suffix}_solvent", "solvent", "CH3CN", evidence),
          participant(f"{suffix}_product", "product", product, evidence,
                      amounts=[field("isolated_mass", {"number": product_mg, "unit": "mg"}, [ev(3)]) if product_mg is not None else field("isolated_mass", None)])]
    if additive:
        ps.insert(2, participant(f"{suffix}_additive", "reagent", additive, evidence,
                                 amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, [ev(1)])]))
    outcomes = product_outcomes(product, {"number": yield_pct, "unit": "%"}, evidence, "isolated")
    if second_yield is not None:
        outcomes.append(field("yield_reported_in_detailed_procedure", {"number": second_yield, "unit": "%"}, [ev(3)]))
    conds = [field("temperature", {"number": 25, "unit": "°C"}, evidence),
             field("time", {"number": time_h, "unit": "h"}, evidence),
             field("solvent_volume", {"number": 2.5, "unit": "mL"}, [ev(3)])] + missing_conditions()
    return record(suffix, "optimization_entry", evidence, ps, conds, outcomes,
                  notes=["Conditions A; filtered through a short silica column, solvent removed, then flash chromatography on silica gel with petroleum ether/ethyl acetate 15:1."],
                  unresolved=[
                      "Structures are source-labelled and unverified; SMILES are intentionally null.",
                      "Atmosphere and concentration are not reported.",
                      "The article reports 92% in Scheme 2/prose but 93% in the detailed LiCl procedure; both are retained." if second_yield else
                      ("Scheme 2 labels the 84% product 2ab, while adjacent prose prints 2aa; the graphical assignment is retained and the conflict remains unresolved." if suffix == "scheme2_2ab_no_libr" else "No associated SI was supplied; missing details remain unresolved."),
                  ])


records += [
    cond_a("scheme2_2aa_no_licl", "Cl", None, 24, 83, 44, 0.25, 44),
    cond_a("scheme2_2aa_licl", "Cl", "LiCl", 24, 92, 44, 0.25, 49, 93),
    cond_a("scheme2_2ab_libr", "Br", "LiBr", 12, 70, 42, 0.24, 43),
    cond_a("scheme2_2ab_no_libr", "Br", None, 12, 84, 43, 0.25, 53),
]

records.append(record(
    "eq1_ncs_no_reaction", "reported_experiment", [ev(1)],
    [participant("eq1_1a", "reactant", "1a", [ev(1)], "2-methyl-4-phenyl-2,3-butadienoic acid"),
     participant("eq1_ncs", "reagent", "NCS", [ev(1)]),
     participant("eq1_2aa", "product", "2aa", [ev(1)], "4-chloro-3-methyl-5-phenyl-2(5H)-furanone")],
    missing_conditions(),
    [field("result", "2aa was not afforded", [ev(1)]), field("yield", None), field("detection_limit", None)],
    notes=["Equation 1 is an explicit failed chlorolactonization under previously described conditions."],
    unresolved=["The referenced prior conditions, quantities, duration, workup, and detection limit are not stated locally."],
))


# Page 2 Table 1: optimization of 1b. Footnote prints 1a even though title/scheme identify 1b.
table1 = [
    (1, "CH3CN", 4, 25, 50, "2ba", 52, False),
    (2, "CH3CN", 4, 25, 8, "2bb", 43, False),
    (3, "CH3CN", 0, 25, 24, "2ba", 41, False),
    (4, "CH3CN", 0, 25, 12, "2bb", 37, False),
    (5, "CH3CN", 4, 40, 48, "2ba", 43, False),
    (6, "CH3CN", 4, 25, 48, "2ba", 50, True),
    (7, "CH3CN", 4, 40, 13, "2ba", 34, True),
    (8, "DMF", 4, 40, 51, "2ba", 14, False),
    (9, "acetone/H2O", 0, "65-70", 6.5, "2ba", 87, False),
    (10, "acetone/H2O", 0, "65-70", 2, "2bb", 85, False),
]
for n, solvent, lix, temp, time_h, product, yld, bicarbonate in table1:
    suffix = f"table1_entry{n:02d}"
    is_br = product == "2bb"
    reagent = "CuBr2" if is_br else "CuCl2"
    additive = "LiBr" if is_br else "LiCl"
    evidence = [ev(2)] + ([ev(3)] if n == 9 else []) + ([ev(4)] if n == 10 else [])
    ps = [participant(f"{suffix}_1b", "reactant", "1b", evidence, "2,3-undecadienoic acid"),
          participant(f"{suffix}_cux2", "reagent", reagent, evidence,
                      amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, [ev(2)])]),
          participant(f"{suffix}_solvent", "solvent", solvent, evidence),
          participant(f"{suffix}_product", "product", product, evidence)]
    if lix:
        ps.insert(2, participant(f"{suffix}_lix", "reagent", additive, evidence,
                                 amounts=[field("equivalents", {"number": lix, "unit": "equiv"}, [ev(2)])]))
    if bicarbonate:
        ps.insert(-2, participant(f"{suffix}_nahco3", "reagent", "NaHCO3", evidence,
                                  amounts=[field("equivalents", {"number": 1, "unit": "equiv"}, [ev(2)])]))
    if n in (9, 10):
        ps[1]["amounts"] = [field("equivalents", {"number": 4, "unit": "equiv"}, [ev(2)])]
    temp_value = temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}
    conds = [field("temperature", temp_value, [ev(2)]), field("time", {"number": time_h, "unit": "h"}, [ev(2)])]
    if solvent == "acetone/H2O":
        conds.append(field("solvent_ratio", "acetone:H2O = 2:1", [ev(2)]))
        conds.append(field("workup_and_purification", "dilute with saturated NH4Cl; extract three times with diethyl ether; combine ether phases; dry over MgSO4; evaporate; flash chromatography on silica gel with petroleum ether/ethyl acetate 15:1", [ev(3)]))
    conds += missing_conditions()
    amounts = {
        9: ((45, 0.25), (46, "mg")),
        10: ((46, 0.25), (56, "mg")),
    }
    if n in amounts:
        (smg, smmol), (pmg, unit) = amounts[n]
        ps[0]["amounts"] = [field("mass", {"number": smg, "unit": "mg"}, evidence[1:]), field("amount", {"number": smmol, "unit": "mmol"}, evidence[1:])]
        ps[-1]["amounts"] = [field("isolated_mass", {"number": pmg, "unit": unit}, evidence[1:])]
    records.append(record(
        suffix, "optimization_entry", evidence, ps, conds,
        product_outcomes(product, {"number": yld, "unit": "%"}, evidence, "isolated" if n in (9, 10) else None),
        notes=["Table 1 title and reaction drawing identify substrate 1b; its ratio footnotes visibly print 1a. This source discrepancy is retained for review."] +
              (["Table 1 entry 10 and Scheme 3 entry 5 show the same CuBr2 (4 eq), 2 h, 85% run and are represented once.",
                "The page-4 2bb paragraph prints that the preparation affords 2ba; the product heading, Table 1, and Scheme 3 identify 2bb, so the printed conflict is retained."] if n == 10 else []),
        unresolved=[
            "Table 1 footnote substrate label conflicts with the table title/drawing (1a versus 1b).",
            "Yield measurement basis is not stated for this row." if n not in (9, 10) else "Atmosphere and concentration are not reported.",
            "Structures remain unverified and SI was not supplied." if n != 10 else "The page-4 product paragraph contains an unresolved 2bb/2ba printed inconsistency; structures remain unverified.",
        ],
    ))


# Page 2 Table 2 scope, enriched by the product-specific paragraphs on pages 3-4.
scope = [
    (1, "1a", "C6H5", "CH3", "Cl", 4, "2aa", 93, 3, 43, 0.25, 48),
    (2, "1a", "C6H5", "CH3", "Br", 2, "2ab", 96, 3, 45, 0.26, 63),
    (3, "1c", "c-C6H11", "H", "Cl", 4, "2ca", 92, 3, 83, 0.5, 92),
    (4, "1c", "c-C6H11", "H", "Br", 2, "2cb", 94, 4, 42, 0.25, 68),
    (5, "1d", "C6H5", "n-C3H7", "Cl", 4, "2da", 100, 3, 50, 0.25, 58),
    (6, "1d", "C6H5", "n-C3H7", "Br", 2, "2db", 99, 4, 49, 0.25, 67),
    (7, "1e", "1-naphthyl", "CH3", "Cl", 4, "2ea", 90, 3, 56, 0.25, 58),
    (8, "1e", "1-naphthyl", "CH3", "Br", 2, "2eb", 89, 4, 55, 0.25, 74),
    (9, "1f", "1-naphthyl", "n-C3H7", "Cl", 4, "2fa", 96, 3, 63, 0.25, 69),
    (10, "1f", "1-naphthyl", "n-C3H7", "Br", 2, "2fb", 98, 4, 63, 0.25, 81),
]
product_names = {
    "2aa": "4-chloro-3-methyl-5-phenyl-2(5H)-furanone",
    "2ab": "4-bromo-3-methyl-5-phenyl-2(5H)-furanone",
    "2ca": "4-chloro-5-cyclohexyl-2(5H)-furanone",
    "2cb": "4-bromo-5-cyclohexyl-2(5H)-furanone",
    "2da": "4-chloro-3-(n-propyl)-5-phenyl-2(5H)-furanone",
    "2db": "4-bromo-3-(n-propyl)-5-phenyl-2(5H)-furanone",
    "2ea": "4-chloro-3-methyl-5-(1-naphthyl)-2(5H)-furanone",
    "2eb": "4-bromo-3-methyl-5-(1-naphthyl)-2(5H)-furanone",
    "2fa": "4-chloro-3-(n-propyl)-5-(1-naphthyl)-2(5H)-furanone",
    "2fb": "4-bromo-3-(n-propyl)-5-(1-naphthyl)-2(5H)-furanone",
}
for n, substrate, r1, r2, halide, time_h, product, yld, detail_page, smg, smmol, pmg in scope:
    suffix = f"table2_entry{n:02d}"
    evidence = [ev(2), ev(3), ev(detail_page)]
    if product == "2ab":
        evidence.append(ev(4))
    evidence = list(dict.fromkeys(evidence))
    reagent = f"Cu{halide}2"
    ps = [participant(f"{suffix}_substrate", "reactant", substrate, evidence,
                      amounts=[field("mass", {"number": smg, "unit": "mg"}, [ev(detail_page)]),
                               field("amount", {"number": smmol, "unit": "mmol"}, [ev(detail_page)])]),
          participant(f"{suffix}_cux2", "reagent", reagent, evidence,
                      amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, [ev(2)])]),
          participant(f"{suffix}_acetone", "solvent", "acetone", evidence),
          participant(f"{suffix}_water", "solvent", "H2O", evidence),
          participant(f"{suffix}_product", "product", product, evidence, product_names[product],
                      [field("isolated_mass", {"number": pmg, "unit": "mg"}, [ev(detail_page)])])]
    conds = [field("temperature", "65-70 °C", [ev(2), ev(3)]),
             field("time", {"number": time_h, "unit": "h"}, [ev(2)]),
             field("solvent_ratio", "acetone:H2O = 2:1", [ev(2), ev(3)]),
             field("workup_and_purification", "dilute with saturated NH4Cl; extract three times with diethyl ether; combine ether phases; dry over MgSO4; evaporate; flash chromatography on silica gel with petroleum ether/ethyl acetate 15:1; recrystallize solid products from n-hexane", [ev(3)])] + missing_conditions()
    records.append(record(
        suffix, "substrate_scope_entry", evidence, ps, conds,
        product_outcomes(product, {"number": yld, "unit": "%"}, evidence, "isolated",
                         [("substituent_R1", r1), ("substituent_R2", r2)]),
        unresolved=[
            "Participant structures and stereochemistry are not machine-certified; SMILES remain null.",
            "Atmosphere and concentration are not reported.",
            "The general 0.25 mmol/4.5 mL charge was not imposed where the product paragraph reports a different scale.",
            "No SI file is supplied, although the article announces spectra for selected products.",
        ],
    ))


# Scheme 3 rows not already represented by Table 1 entry 10.
scheme3 = [
    (1, "CuCl2", 4, 6, "2ba", 86, "3b", 0, False),
    (2, "CuCl2", 2, 4, "2ba", 58, "3b", 36, False),
    (3, "CuCl2", 2, 6, "2ba", 71, "3b", 0, True),
    (4, "CuCl", 2, 4, "2ba", 0, "3b", 72, False),
    (6, "CuBr2", 2, 2, "2bb", 73, "3b", 7, False),
]
for n, reagent, equiv, time_h, halo_product, halo_yield, direct_product, direct_yield, bicarbonate in scheme3:
    suffix = f"scheme3_entry{n:02d}"
    ps = [participant(f"{suffix}_1b", "reactant", "1b", [ev(2)], "2,3-undecadienoic acid"),
          participant(f"{suffix}_cu", "reagent", reagent, [ev(2)],
                      amounts=[field("equivalents", {"number": equiv, "unit": "equiv"}, [ev(2)])]),
          participant(f"{suffix}_acetone", "solvent", "acetone", [ev(2)]),
          participant(f"{suffix}_water", "solvent", "H2O", [ev(2)]),
          participant(f"{suffix}_halo", "product", halo_product, [ev(2)]),
          participant(f"{suffix}_direct", "product", direct_product, [ev(2)], "direct cyclization product")]
    if bicarbonate:
        ps.insert(2, participant(f"{suffix}_nahco3", "reagent", "NaHCO3", [ev(2)],
                                 amounts=[field("equivalents", {"number": 1, "unit": "equiv"}, [ev(2)])]))
    records.append(record(
        suffix, "optimization_entry", [ev(2)], ps,
        [field("temperature", "65-70 °C", [ev(2)]), field("time", {"number": time_h, "unit": "h"}, [ev(2)]),
         field("solvent_ratio", "acetone:H2O = 2:1", [ev(2)])] + missing_conditions(),
        [field(f"yield_{halo_product}", {"number": halo_yield, "unit": "%"}, [ev(2)]),
         field(f"yield_{direct_product}", {"number": direct_yield, "unit": "%"}, [ev(2)]),
         field("yield_measurement_basis", None)],
        notes=["Scheme 3 control experiment comparing halolactonization with direct cyclization. Scheme 3 entry 5 is merged into Table 1 entry 10 and is not duplicated."],
        unresolved=["Yield basis, charges beyond displayed equivalents, atmosphere, concentration, workup, and purification are not stated for this control row.", "Structures remain unverified."],
    ))


# Schemes 4 and 5 are proposed mechanisms, not observed runs.
records.append(record(
    "mechanism_scheme4", "mechanism", [ev(2), ev(3)],
    [participant("m4_1", "reactant", "generic 2,3-allenoic acid 1", [ev(3)]),
     participant("m4_cux2", "reagent", "CuX2", [ev(3)]),
     participant("m4_2", "product", "generic beta-halobutenolide 2", [ev(3)]),
     participant("m4_intermediates", "unspecified_agent", "proposed intermediates 3-5 and E-6", [ev(2), ev(3)])],
    [field("mechanistic_status", "proposed pathways a and b", [ev(2), ev(3)])],
    notes=["Proposed coordination/5-endo-trig or water-addition pathways followed by SET/reductive elimination; intermediates are not reported as isolated products."],
))
records.append(record(
    "mechanism_scheme5", "mechanism", [ev(3)],
    [participant("m5_1", "reactant", "generic 2,3-allenoic acid 1", [ev(3)]),
     participant("m5_cux2", "reagent", "CuX2", [ev(3)]),
     participant("m5_2", "product", "generic beta-halobutenolide 2", [ev(3)]),
     participant("m5_intermediates", "unspecified_agent", "proposed Cu-containing intermediates 7 and 8", [ev(3)])],
    [field("mechanistic_status", "proposed halocupration/reductive-elimination pathway", [ev(3)])],
    notes=["Scheme 5 is explicitly presented as another mechanistic possibility, not an observed experiment."],
))


# Locally described but literature-derived starting-material preparations.
records.append(record(
    "starting_materials_1b_1c", "literature_example", [ev(3)],
    [participant("sm_bc_allene", "reactant", "corresponding 1,2-allene", [ev(3)]),
     participant("sm_bc_nbu", "reagent", "n-BuLi", [ev(3)]),
     participant("sm_bc_co2", "reagent", "CO2", [ev(3)]),
     participant("sm_bc_products", "product", "2,3-undecadienoic acid (1b) or 4-cyclohexyl-2,3-butadienoic acid (1c)", [ev(3)])],
    missing_conditions(),
    [field("yield", None)],
    notes=["Starting materials 1b and 1c were prepared according to cited procedure 10 via allenyllithium formation and CO2 reaction."],
    unresolved=["Local text gives no quantities, temperature, duration, workup, purification, or yield; the cited external procedure was not imported."],
))
records.append(record(
    "starting_materials_1a_1d_1f", "literature_example", [ev(3)],
    [participant("sm_adf_acid_chloride", "reactant", "corresponding acid chloride", [ev(3)]),
     participant("sm_adf_ylide", "reagent", "ethyl 2-(triphenylphosphoranylidene)propionate", [ev(3)]),
     participant("sm_adf_naoh", "reagent", "2 N NaOH", [ev(3)]),
     participant("sm_adf_products", "product", "allenic acids 1a and 1d-f", [ev(3)])],
    [field("sequence", "ylide treatment followed by hydrolysis of 2,3-allenoic esters with 2 N NaOH", [ev(3)])] + missing_conditions(),
    [field("yield", None)],
    notes=["Starting materials 1a and 1d-f were prepared according to cited method 9."],
    unresolved=["Local text gives no quantities, temperature, duration, workup, purification, or yield; the cited external method was not imported."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if ev(1) in r["evidence_ids"]]
page2_ids = [r["record_id"] for r in records if ev(2) in r["evidence_ids"]]
page3_ids = [r["record_id"] for r in records if ev(3) in r["evidence_ids"]]
page4_ids = [r["record_id"] for r in records if ev(4) in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Schemes 1-2", "finding": "Generic CuX2 halolactonization plus four Conditions-A variants for 1a, separated by halide/additive conditions.", "evidence_ids": [ev(1)]},
                {"region": "right-column Equation 1 and adjacent prose", "finding": "NCS failed to afford chlorobutenolide 2aa; explicit negative result retained.", "evidence_ids": [ev(1)]},
                {"region": "introductory/background prose and references", "finding": "Prior methods and biological context; not converted into current-paper experiments.", "evidence_ids": [ev(1)]},
            ],
            "record_ids": page1_ids,
            "unresolved": ["Scheme 2/prose reports 92% for the LiCl run while the page-3 detailed procedure reports 93%.", "Equation 1 refers to prior conditions that are not restated locally."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1", "finding": "Ten optimization rows for 1b, including solvent, LiX, NaHCO3 overrides, temperatures, times, products, and yields.", "evidence_ids": [ev(2)]},
                {"region": "lower-left Table 2", "finding": "Ten substrate-scope rows under aqueous-acetone Conditions B.", "evidence_ids": [ev(2)]},
                {"region": "upper-right Scheme 3", "finding": "Six control rows quantify halogenated product 2b and direct-cyclization product 3b; row 5 duplicates Table 1 entry 10 and is merged.", "evidence_ids": [ev(2)]},
                {"region": "lower-right mechanistic prose", "finding": "Proposed pathways feeding Schemes 4-5; classified as mechanism, not observed experiments.", "evidence_ids": [ev(2)]},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Table 1 footnotes print substrate label 1a despite the title and reaction drawing identifying 1b.", "Most optimization/control yield bases and row-specific workups are not stated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left-column Schemes 4-5", "finding": "Two proposed mechanisms with generic intermediates; no isolated intermediate is claimed.", "evidence_ids": [ev(3)]},
                {"region": "lower-left Starting Materials", "finding": "Two literature-derived preparation families for 1b/1c and 1a/1d-f; incomplete local procedures retained as literature examples.", "evidence_ids": [ev(3)]},
                {"region": "upper-right Conditions A/B", "finding": "Detailed Conditions-A variants and general aqueous-acetone procedure merged into matching Scheme 2/Table 1/Table 2 records.", "evidence_ids": [ev(3)]},
                {"region": "right-column product paragraphs", "finding": "Detailed charges, isolated masses, yields, physical descriptions, and characterization begin for 2aa, 2ba, 2ca, 2da, 2ea, 2fa, and 2ab; synthetic facts linked to matching records.", "evidence_ids": [ev(3)]},
            ],
            "record_ids": page3_ids,
            "unresolved": ["Characterization spectra are not normalized into reaction conditions.", "Generic Conditions B volume was not imposed on the 0.5 mmol 2ca scale."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "product characterization paragraphs", "finding": "Continuations/details for 2ab, 2bb, 2cb, 2db, 2eb, and 2fb linked to their existing reaction rows; no duplicate experiments created.", "evidence_ids": [ev(4)]},
                {"region": "Supporting Information notice", "finding": "Article announces 1H NMR spectra for 2aa, 2ba, and 2da, but no SI file is supplied or associated in this pilot.", "evidence_ids": [ev(4)]},
                {"region": "acknowledgment and article footer", "finding": "No additional reaction experiment.", "evidence_ids": [ev(4)]},
            ],
            "record_ids": page4_ids,
            "unresolved": ["SI-only spectra are unavailable; no SI association was inferred.", "The 2bb paragraph visibly says it affords 2ba, a likely source typo retained as an unresolved printed inconsistency."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
