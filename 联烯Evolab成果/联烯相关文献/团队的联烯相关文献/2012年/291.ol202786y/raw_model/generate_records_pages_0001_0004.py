#!/usr/bin/env python3
"""Generate evidence-linked machine extraction for PDF pages 1--4."""
import json
from pathlib import Path

DOC = "doc_d3a53bb06fa97c3e"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"


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


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def record(suffix, page, kind, participants, steps, outcomes, notes, unresolved, extra_evidence=()):
    evidence = ev(page) + list(extra_evidence)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SOLVENT_SMILES = {
    "THF": "C1CCOC1",
    "Dioxane": "C1COCCO1",
    "DME": "COCCOC",
    "Toluene": "Cc1ccccc1",
    "Benzene": "c1ccccc1",
    "CH3CN": "CC#N",
    "MTBE": "COC(C)(C)C",
    "DMF": "CN(C)C=O",
    "EtOH": "CCO",
    "t-BuOH": "CC(C)(C)O",
}

SMILES_1A = "CC(=O)C(C)C(=O)OCC=C=CCCCCCCCCC"
SMILES_2A = "CC(=O)C(C)CC=C=CCCCCCCCCC"
SMILES_4A = "C=CC#CCCCCCCCCC"


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def common_1a(page, products=("2a", "4a"), scale=0.2):
    evidence = ev(page)
    ps = [participant("1a", "reactant", "1a", evidence,
                      name="allenyl 3-oxoalkanoate 1a", smiles=SMILES_1A,
                      amounts=[amount("amount", scale, "mmol", evidence)] if scale else [])]
    for label in products:
        smiles = SMILES_2A if label == "2a" else SMILES_4A if label == "4a" else None
        ps.append(participant(label, "product", label, evidence, smiles=smiles))
    return ps


records = []

# Page 1 graphical abstract: a generic summary, not an individual batch experiment.
e = ev(1)
records.append(record(
    "graphical_abstract_general_transformation", 1, "general_scheme",
    [
        participant("generic_allenyl_3_oxoalkanoate", "reactant", "allenyl 3-oxoalkanoate", e),
        participant("generic_3_4_allenyl_ketone", "product", "3,4-allenyl ketone", e),
        participant("Pd_dba_2", "catalyst", "Pd(dba)2", e,
                    amounts=[amount("catalyst_loading", 5, "mol%", e)]),
        participant("DPEphos", "reagent", "DPEphos", e,
                    amounts=[amount("ligand_loading", 5, "mol%", e)]),
        participant("generic_solvent", "solvent", "t-BuOH or THF", e),
        participant("CO2", "product", "CO2", e, name="carbon dioxide", smiles="O=C=O"),
    ],
    [{"step_id": "summary_arrow", "participant_ids": ["generic_allenyl_3_oxoalkanoate", "Pd_dba_2", "DPEphos", "generic_solvent"],
      "conditions": [field("temperature", {"number": 25, "unit": "°C"}, e), field("solvent", "t-BuOH or THF", e)]}],
    [],
    ["Graphical abstract depicts a generic R-group transformation and CO2 byproduct."],
    ["Generic R1/R2 structures are not complete molecules; no batch scale, time, or yield is shown."],
))

# Page 2 Scheme 1 separates a cited literature reaction from the authors' proposed pathway.
e = ev(2)
records.append(record(
    "scheme1_chung_2008_literature_example", 2, "literature_example",
    [
        participant("lit_buta_2_3_dienyl_2_alkynoate", "reactant", "buta-2,3-dienyl 2'-alkynoate (generic R1/R2/R3)", e),
        participant("lit_2_alkynyl_buta_1_3_diene", "product", "2-alkynyl buta-1,3-diene (generic R1/R2/R3)", e),
        participant("lit_Pd_PPh3_4", "catalyst", "Pd(PPh3)4", e,
                    amounts=[amount("catalyst_loading", 1, "mol%", e)]),
        participant("lit_toluene", "solvent", "Toluene", e, smiles=SOLVENT_SMILES["Toluene"]),
    ],
    [{"step_id": "literature_arrow", "participant_ids": ["lit_buta_2_3_dienyl_2_alkynoate", "lit_Pd_PPh3_4", "lit_toluene"],
      "conditions": [field("temperature", {"number": 100, "unit": "°C"}, e), field("solvent", "Toluene", e)]}],
    [], ["Scheme labels this reaction as ref 11; it is not a new experiment in this paper."],
    ["Generic R groups prevent complete structure encoding; time, scale, and yield are not shown in this scheme."],
))
records.append(record(
    "scheme1_proposed_decarboxylation_pathway", 2, "mechanism",
    [
        participant("generic_allenyl_3_oxoalkanoate", "reactant", "allenyl 3-oxoalkanoate (generic R1/R2)", e),
        participant("generic_allenyl_ketone", "product", "3,4-allenyl ketone (generic R1/R2)", e),
        participant("generic_dienyl_ketone", "product", "1,3-dienyl ketone (generic R1/R2)", e),
        participant("Pd0", "catalyst", "Pd(0)", e),
    ],
    [], [],
    ["Scheme proposes alpha-methylene pi-allylpalladium/resonance intermediates and alternative beta-keto-acid pathways with CO2 loss."],
    ["This is a mechanistic proposal rather than a reported batch; generic R groups and intermediates are not encoded as verified structures."],
))


def table1_record(entry, catalyst, ligand, ligand_loading, time_h, result_2a, result_4a,
                  isolated_2a=None, extra_notes=(), extra_outcomes=()):
    evidence = ev(2)
    ps = common_1a(2)
    ps.append(participant(f"cat_t1_{entry}", "catalyst", catalyst, evidence,
                          amounts=[amount("catalyst_loading", 5, "mol%", evidence)]))
    ids = ["1a", f"cat_t1_{entry}"]
    if ligand:
        ps.append(participant(f"lig_t1_{entry}", "reagent", ligand, evidence,
                              amounts=[amount("ligand_loading", ligand_loading, "mol%", evidence)]))
        ids.append(f"lig_t1_{entry}")
    ps.append(participant("solvent_THF", "solvent", "THF", evidence,
                          smiles=SOLVENT_SMILES["THF"], amounts=[amount("volume", 2, "mL", evidence)]))
    ids.append("solvent_THF")
    outcomes = []
    if result_2a == "complicated":
        outcomes.append(field("reaction_result", "complicated", evidence))
    else:
        outcomes.append(field("nmr_yield_2a", result_2a, evidence, ["2a"]))
    if isolated_2a is not None:
        outcomes.append(field("isolated_yield_2a", {"number": isolated_2a, "unit": "%"}, evidence, ["2a"]))
    if result_4a is not None:
        outcomes.append(field("nmr_yield_4a", result_4a, evidence, ["4a"]))
    outcomes.extend(extra_outcomes)
    return record(
        f"table1_entry{entry}", 2, "optimization_entry", ps,
        [{"step_id": "decarboxylation", "participant_ids": ids,
          "conditions": [field("atmosphere", "argon", evidence),
                         field("temperature", {"number": 50, "unit": "°C"}, evidence),
                         field("time", {"number": time_h, "unit": "h"}, evidence),
                         field("solvent", "THF", evidence)]}],
        outcomes + [field("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard; parenthesized values are isolated yields", evidence)],
        list(extra_notes),
        ["Workup and purification are not reported in the main-text table; SI association is unestablished."
         " Substrate/product structure candidates remain unverified."],
    )


table1 = [
    (1, "Pd(PPh3)4", None, None, 21, "complicated", None, None),
    (2, "Pd(OAc)2", "PPh3", 15, 21, "complicated", None, None),
    (3, "Pd(dba)2", "PPh3", 15, 21, "complicated", None, None),
    (4, "Pd(dba)2", "LB-phos", 15, 33, "complicated", None, None),
    (5, "Pd(dba)2", "dppf", 5, 5.5, None, "table dash (–)", 33),
    (6, "Pd(dba)2", "dppe", 5, 2.2, {"number": 14, "unit": "%", "qualifier": "lt", "raw_text": "<14%"}, "table dash (–)", None),
    (7, "Pd(dba)2", "binap", 5, 2.3, {"number": 30, "unit": "%"}, {"number": 19, "unit": "%"}, None),
    (8, "Pd(dba)2", "MeOBIPHEP", 5, 1.5, {"number": 48, "unit": "%", "qualifier": "lt", "raw_text": "<48%"}, {"number": 16, "unit": "%"}, None),
    (9, "Pd(dba)2", "Xantphos", 5, 1.2, {"number": 57, "unit": "%"}, {"number": 16, "unit": "%"}, None),
    (10, "Pd(dba)2", "DPEphos", 5, 0.5, {"number": 66, "unit": "%"}, {"number": 17, "unit": "%"}, 59),
]
for args in table1:
    entry = args[0]
    notes = []
    extra = []
    if entry == 1:
        notes.append("Narrative states neither expected allenyl ketone 2a nor 1,3-dienyl ketone 3a was afforded.")
        extra.append(field("product_3a_formation", "not detected", ev(2), ["3a"]))
    if entry == 10:
        notes.append("Narrative states dienyl ketone 3a was not observed.")
        extra.append(field("product_3a_formation", "not detected", ev(2), ["3a"]))
    rec = table1_record(*args, extra_notes=notes, extra_outcomes=extra)
    if entry in (1, 10):
        rec["participants"].append(participant("3a", "product", "3a", ev(2), name="1,3-dienyl ketone 3a"))
    records.append(rec)


def table2_record(entry, solvent, time_h, nmr_2a, nmr_4a, isolated=None, temperature=50):
    evidence = ev(3)
    ps = common_1a(3)
    ps += [
        participant(f"cat_t2_{entry}", "catalyst", "Pd(dba)2", evidence,
                    amounts=[amount("catalyst_loading", 5, "mol%", evidence)]),
        participant(f"lig_t2_{entry}", "reagent", "DPEphos", evidence,
                    amounts=[amount("ligand_loading", 5, "mol%", evidence)]),
        participant(f"solvent_t2_{entry}", "solvent", solvent, evidence,
                    smiles=SOLVENT_SMILES[solvent], amounts=[amount("volume", 2, "mL", evidence)]),
    ]
    outcomes = [
        field("nmr_yield_2a", {"number": nmr_2a, "unit": "%"}, evidence, ["2a"]),
        field("nmr_yield_4a", {"number": nmr_4a, "unit": "%"}, evidence, ["4a"]),
        field("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard; parenthesized values are isolated yields", evidence),
    ]
    if isolated is not None:
        outcomes.insert(1, field("isolated_yield_2a", {"number": isolated, "unit": "%"}, evidence, ["2a"]))
    return record(
        f"table2_entry{entry}", 3, "optimization_entry", ps,
        [{"step_id": "decarboxylation", "participant_ids": ["1a", f"cat_t2_{entry}", f"lig_t2_{entry}", f"solvent_t2_{entry}"],
          "conditions": [field("atmosphere", "argon", evidence),
                         field("temperature", {"number": temperature, "unit": "°C"}, evidence),
                         field("time", {"number": time_h, "unit": "h"}, evidence),
                         field("solvent", solvent, evidence)]}],
        outcomes, [],
        ["Workup and purification are not reported in the main-text table; SI association is unestablished. Substrate/product structure candidates remain unverified."],
    )


# Table 2 entry 1 is the same experiment as Table 1 entry 10. Merge the page-3 evidence into that record.
t1e10 = next(r for r in records if r["record_id"].endswith(":table1_entry10"))
for evidence_id in ev(3):
    t1e10["evidence_ids"].append(evidence_id)
t1e10["source_reaction_id"] = "Table 1 entry 10 / Table 2 entry 1"
t1e10["notes"].append(fact("Table 2 entry 1 repeats the same THF, 50 °C, 0.5 h conditions and 66%/59% 2a plus 17% 4a outcomes.", ev(3)))

for row in [
    (2, "Dioxane", 0.6, 63, 18, None, 50),
    (3, "DME", 0.6, 62, 18, None, 50),
    (4, "Toluene", 0.6, 59, 13, None, 50),
    (5, "Benzene", 0.6, 58, 15, None, 50),
    (6, "CH3CN", 0.6, 66, 19, None, 50),
    (7, "MTBE", 0.6, 59, 15, None, 50),
    (8, "DMF", 0.6, 65, 18, None, 50),
    (9, "EtOH", 8, 55, 4, None, 50),
    (10, "t-BuOH", 0.6, 70, 10, 66, 50),
    (11, "t-BuOH", 6.5, 80, 6, 77, 25),
]:
    records.append(table2_record(*row))


def scope_record(table, entry, substrate, product, r1, r2, time_h, isolated_yield,
                 *, solvent="t-BuOH", scale_mmol=0.4, scale_g=None, dr=None):
    evidence = ev(3)
    ps = [
        participant(substrate, "reactant", substrate, evidence,
                    name=f"allenyl 3-oxoalkanoate {substrate} (R1={r1}; R2={r2})",
                    amounts=([amount("mass", scale_g, "g", evidence)] if scale_g else
                             [amount("amount", scale_mmol, "mmol", evidence)] if scale_mmol else [])),
        participant(product, "product", product, evidence),
        participant(f"cat_{table}_{entry}", "catalyst", "Pd(dba)2", evidence,
                    amounts=[amount("catalyst_loading", 5, "mol%", evidence)]),
        participant(f"lig_{table}_{entry}", "reagent", "DPEphos", evidence,
                    amounts=[amount("ligand_loading", 5, "mol%", evidence)]),
        participant(f"solvent_{table}_{entry}", "solvent", solvent, evidence,
                    smiles=SOLVENT_SMILES[solvent], amounts=[amount("volume", 2, "mL", evidence)]),
    ]
    outcomes = [field(f"isolated_yield_{product}", {"number": isolated_yield, "unit": "%"}, evidence, [product]),
                field("yield_measurement_basis", "isolated yield", evidence)]
    if dr:
        outcomes.append(field("diastereomer_ratio", dr, evidence, [product]))
    return record(
        f"{table}_entry{entry}", 3, "substrate_scope_entry", ps,
        [{"step_id": "decarboxylative_coupling", "participant_ids": [substrate, f"cat_{table}_{entry}", f"lig_{table}_{entry}", f"solvent_{table}_{entry}"],
          "conditions": [field("atmosphere", "argon", evidence), field("temperature", {"number": 25, "unit": "°C"}, evidence),
                         field("time", {"number": time_h, "unit": "h"}, evidence), field("solvent", solvent, evidence)]}],
        outcomes, [],
        ["Workup and purification are not reported in the main-text table; SI association is unestablished. Drawn substrate/product structures and stereochemical assignments remain unverified."],
    )


for row in [
    (1, "1a", "2a", "n-C9H19", "CH3", 5, 76, 0.4, None, "~1:1"),
    (2, "1a", "2a", "n-C9H19", "CH3", 3, 77, None, 1, "~1:1"),
    (3, "1b", "2b", "n-C9H19", "Bn", 4, 65, 0.4, None, "~1:1"),
    (4, "1c", "2c", "n-C4H9", "Bn", 4.5, 63, 0.4, None, "~1:1"),
    (5, "1d", "2d", "H", "Bn", 2.5, 62, 0.4, None, None),
]:
    entry, sub, prod, r1, r2, tm, y, mmol, grams, dr = row
    records.append(scope_record("table3", entry, sub, prod, r1, r2, tm, y,
                                scale_mmol=mmol, scale_g=grams, dr=dr))

for row in [
    (1, "1e", "2e", "n-C9H19", "H", 4, 72, "t-BuOH", "~1:1"),
    (2, "1f", "2f", "cyclohexyl", "H", 5.5, 74, "t-BuOH", "~1:1"),
    (3, "1g", "2g", "tert-butyl", "H", 0.8, 48, "THF", "~1:1"),
    (4, "1h", "2h", "H", "Ph", 7.5, 70, "t-BuOH", None),
    (5, "1i", "2i", "H", "CO2Me", 3, 60, "t-BuOH", None),
]:
    entry, sub, prod, r1, r2, tm, y, solv, dr = row
    records.append(scope_record("table4", entry, sub, prod, r1, r2, tm, y, solvent=solv, dr=dr))


def scheme_scope(suffix, substrate, product, solvent, time_h, yld, dr=None, page=3):
    evidence = ev(page)
    ps = [
        participant(substrate, "reactant", substrate, evidence),
        participant(product, "product", product, evidence),
        participant(f"cat_{suffix}", "catalyst", "Pd(dba)2", evidence,
                    amounts=[amount("catalyst_loading", 5, "mol%", evidence)]),
        participant(f"lig_{suffix}", "reagent", "DPEphos", evidence,
                    amounts=[amount("ligand_loading", 5, "mol%", evidence)]),
        participant(f"solvent_{suffix}", "solvent", solvent, evidence, smiles=SOLVENT_SMILES[solvent]),
    ]
    outcomes = [field(f"isolated_yield_{product}", {"number": yld, "unit": "%"}, evidence, [product]),
                field("yield_measurement_basis", "isolated yield", evidence)]
    if dr:
        outcomes.append(field("diastereomer_ratio", dr, evidence, [product]))
    return record(
        suffix, page, "substrate_scope_entry", ps,
        [{"step_id": "decarboxylative_coupling", "participant_ids": [substrate, f"cat_{suffix}", f"lig_{suffix}", f"solvent_{suffix}"],
          "conditions": [field("temperature", {"number": 25, "unit": "°C"}, evidence),
                         field("time", {"number": time_h, "unit": "h"}, evidence), field("solvent", solvent, evidence)]}],
        outcomes, [],
        ["Scale, solvent volume, atmosphere, workup, and purification are not stated on this scheme; SI association is unestablished. Drawn structures remain unverified."],
    )


records.append(scheme_scope("scheme2_allenyne_1j_to_2j", "1j", "2j", "THF", 1, 45))
records.append(scheme_scope("scheme2_bisallene_1k_to_2k", "1k", "2k", "t-BuOH", 2.5, 67, "~1:1"))

# Page 4: one experiment gives two isolated products.
e = ev(4)
records.append(record(
    "equation1_mono_and_diallenylation", 4, "substrate_scope_entry",
    [
        participant("1l", "reactant", "1l", e, name="2-unsubstituted allenyl 3-oxoalkanoate 1l"),
        participant("2l", "product", "2l", e, name="monoallenylation product 2l"),
        participant("2m", "product", "2m", e, name="diallenylation product 2m"),
        participant("cat_eq1", "catalyst", "Pd(dba)2", e, amounts=[amount("catalyst_loading", 5, "mol%", e)]),
        participant("lig_eq1", "reagent", "DPEphos", e, amounts=[amount("ligand_loading", 5, "mol%", e)]),
        participant("solvent_eq1", "solvent", "t-BuOH", e, smiles=SOLVENT_SMILES["t-BuOH"]),
    ],
    [{"step_id": "decarboxylative_coupling", "participant_ids": ["1l", "cat_eq1", "lig_eq1", "solvent_eq1"],
      "conditions": [field("temperature", {"number": 25, "unit": "°C"}, e), field("time", {"number": 2.5, "unit": "h"}, e), field("solvent", "t-BuOH", e)]}],
    [field("isolated_yield_2l", {"number": 41, "unit": "%"}, e, ["2l"]),
     field("isolated_yield_2m", {"number": 27, "unit": "%"}, e, ["2m"]),
     field("yield_measurement_basis", "isolated yield", e)],
    ["The same reaction furnished monoallenylation product 2l and diallenylation product 2m."],
    ["Scale, solvent volume, atmosphere, workup, and purification are not stated; SI association is unestablished. Drawn structures remain unverified."],
))

# Figure 1 explicitly reports three separate unsuccessful substrates.
for label in ("1m", "1n", "1o"):
    records.append(record(
        f"figure1_failed_{label}", 4, "substrate_scope_entry",
        [participant(label, "reactant", label, e),
         participant(f"expected_product_{label}", "product", f"corresponding decarboxylation product from {label}", e)],
        [],
        [field("reaction_result", "complicated", e),
         field("corresponding_decarboxylation_product_formation", "not obtained", e, [f"expected_product_{label}"])],
        [f"Figure 1 and adjacent prose report that reaction of substrate {label} was complicated and failed to afford the corresponding decarboxylation product."],
        ["The figure does not state time, temperature, scale, catalyst loading, solvent, workup, purification, or a product identifier; the intended product structure is not encoded."],
    ))

for suffix, sub, prod, tm, yld in [
    ("scheme3_cyclic_1p_to_2n", "1p", "2n", 2.5, 71),
    ("scheme3_cyclic_1q_to_2o", "1q", "2o", 2.5, 74),
    ("scheme3_cyclic_1r_to_2p", "1r", "2p", 3, 71),
]:
    records.append(scheme_scope(suffix, sub, prod, "t-BuOH", tm, yld, page=4))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
