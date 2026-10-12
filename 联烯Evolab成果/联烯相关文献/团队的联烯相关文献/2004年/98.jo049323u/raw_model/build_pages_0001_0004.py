#!/usr/bin/env python3
"""Build raw, evidence-linked records for doc_937b6501ba8d1977 pages 1-4."""
import json
from pathlib import Path

DOC = "doc_937b6501ba8d1977"
BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "raw_model" / "extracted_records_pages_0001_0004.json"
COVERAGE = BASE / "coverage" / "pages_0001_0004.json"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, smiles=None, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name else []),
        "smiles": fact(smiles, evidence if smiles else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SMILES = {
    "allenol_1a": "C=C=C(CCCC)C(C)O",
    "acetate_1a": "C=C=C(CCCC)C(C)OC(C)=O",
    "2a": "C=C=C(CCCC)C(C)C(C(=O)OC)C(=O)OC",
    "2b": "C=C=C(CCCCCC)C(C)C(C(=O)OC)C(=O)OC",
    "2c": "C=C=C(CCCCCC)C(c1ccccc1)C(C(=O)OC)C(=O)OC",
    "2d": "C=C=C(C)C(C)C(C(=O)OC)C(=O)OC",
    "2e": "C=C=C(Cc1ccccc1)C(C)C(C(=O)OC)C(=O)OC",
    "4aa": "COC(=O)C1(C(=O)OC)C(C)C1(CCCC)C(=C)c1ccccc1",
    "4ba": "COC(=O)C1(C(=O)OC)C(C)C1(CCCCCC)C(=C)c1ccccc1",
    "4ca": "COC(=O)C1(C(=O)OC)C(c2ccccc2)C1(CCCCCC)C(=C)c1ccccc1",
    "4da": "COC(=O)C1(C(=O)OC)C(C)C1(C)C(=C)c1ccccc1",
    "4ea": "COC(=O)C1(C(=O)OC)C(C)C1(Cc2ccccc2)C(=C)c1ccccc1",
    "3a": "Ic1ccccc1",
    "3b": "COC(=O)c1ccc(I)cc1",
    "3c": "I/C=C/c1ccccc1",
    "3d": "Ic1cccs1",
    "3e": "I/C=C/CCCC",
    "dimethyl_malonate": "COC(=O)CC(=O)OC",
    "acetic_anhydride": "CC(=O)OC(C)=O",
    "triethylamine": "CCN(CC)CC",
    "dmap": "CN(C)c1ccncc1",
    "diethyl_ether": "CCOCC",
    "dce": "ClCCCl",
    "sodium_hydride": "[Na+].[H-]",
    "potassium_carbonate": "[K+].[K+].[O-]C([O-])=O",
    "tetrabutylammonium_bromide": "[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
    "acetonitrile": "CC#N",
    "dmso": "CS(C)=O",
    "dmf": "CN(C)C=O",
    "toluene": "Cc1ccccc1",
}


def qty(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


records = []

# Page 1: explicitly classify the generic pathway/mechanistic drawing.
e1 = ev(1)
records.append(record(
    "scheme1_generic_pi_allylpalladium_pathway", "mechanism", e1,
    participants=[
        participant("scheme1_allenylmalonate", "reactant", "generic substituted allenylmalonate", e1),
        participant("scheme1_organic_halide", "reactant", "R5-X", e1),
        participant("scheme1_palladium", "catalyst", "Pd(0)/PdLn", e1),
        participant("scheme1_base", "reagent", "base", e1),
        participant("scheme1_intermediate", "unspecified_agent", "generic pi-allylpalladium intermediate", e1),
        participant("scheme1_cyclopropane", "product", "generic cyclopropane regioisomer", e1),
        participant("scheme1_cyclopentene", "product", "generic cyclopentene regioisomer", e1),
    ],
    steps=[{"step_id": "mechanistic_pathway", "participant_ids": [
        "scheme1_allenylmalonate", "scheme1_organic_halide", "scheme1_palladium",
        "scheme1_base", "scheme1_intermediate", "scheme1_cyclopropane",
        "scheme1_cyclopentene"], "conditions": []}],
    unresolved=[
        "Scheme 1 is generic and mechanistic; R groups, scale, time, temperature, and outcomes are not specified.",
        "Generic R-group drawings are not encoded as complete structures.",
    ],
))

# Page 2 Scheme 2: two generic arrows, kept distinct from detailed 1a/2a experiments.
e2 = ev(2)
records.append(record(
    "scheme2_arrow1_allenols_to_acetates", "general_scheme", e2,
    participants=[
        participant("s2_allenol_family", "reactant", "2,3-allenol family (precursors to 1a-e)", e2),
        participant("s2_ac2o", "reagent", "Ac2O", e2, SMILES["acetic_anhydride"]),
        participant("s2_et3n", "reagent", "Et3N", e2, SMILES["triethylamine"]),
        participant("s2_dmap", "catalyst", "DMAP", e2, SMILES["dmap"]),
        participant("s2_ether", "solvent", "Et2O", e2, SMILES["diethyl_ether"]),
        participant("s2_acetate_family", "product", "2,3-alkadienyl acetates 1a-e", e2),
    ],
    steps=[{"step_id": "acetylation", "participant_ids": [
        "s2_allenol_family", "s2_ac2o", "s2_et3n", "s2_dmap", "s2_ether",
        "s2_acetate_family"], "conditions": [field("temperature", "r.t.", e2), field("time", None)]}],
    outcomes=[field("yield", None, targets=["s2_acetate_family"])],
    unresolved=["Scheme 2 arrow 1 gives no time, scale, or product-specific yields."],
))
records.append(record(
    "scheme2_arrow2_acetates_to_allenylmalonates", "general_scheme", e2,
    participants=[
        participant("s2_acetates", "reactant", "2,3-alkadienyl acetates 1a-e", e2),
        participant("s2_dimethyl_malonate", "reactant", "dimethyl malonate", e2, SMILES["dimethyl_malonate"]),
        participant("s2_palladium", "catalyst", "Pd(PPh3)4", e2, amounts=[qty("catalyst_loading", 5, "mol%", e2)]),
        participant("s2_nah", "reagent", "NaH", e2, SMILES["sodium_hydride"], amounts=[qty("equivalents", 1.1, "equiv", e2)]),
        participant("s2_dce", "solvent", "ClCH2CH2Cl", e2, SMILES["dce"]),
        participant("s2_allenylmalonates", "product", "allenylmalonates 2a-e", e2),
    ],
    steps=[{"step_id": "palladium_catalyzed_alkylation", "participant_ids": [
        "s2_acetates", "s2_dimethyl_malonate", "s2_palladium", "s2_nah", "s2_dce",
        "s2_allenylmalonates"], "conditions": [field("temperature", "r.t.", e2), field("time", None)]}],
    outcomes=[field("yield", {"minimum": 82, "maximum": 87, "unit": "%", "raw_text": "82-87%"}, e2, ["s2_allenylmalonates"]),
              field("yield_measurement_basis", None)],
    unresolved=["The 82-87% range is printed for the 2a-e family and cannot be assigned to individual products.",
                "Scheme 2 arrow 2 gives no reaction time or scale."],
))

# Detailed preparation of acetate 1a, spanning pages 2-3.
e23 = ev(2) + ev(3)
records.append(record(
    "reported_preparation_1a", "reported_experiment", e23,
    participants=[
        participant("p1a_allenol", "reactant", "(3-n-butyl)penta-3,4-dien-2-ol", e23, SMILES["allenol_1a"], amounts=[qty("mass", 1.12, "g", e23), qty("amount", 8, "mmol", e23)]),
        participant("p1a_ac2o", "reagent", "acetic anhydride", e23, SMILES["acetic_anhydride"], amounts=[qty("volume", 1.1, "mL", e23), qty("amount", 11.2, "mmol", e23)]),
        participant("p1a_et3n", "reagent", "Et3N", e23, SMILES["triethylamine"], amounts=[qty("volume", 1.52, "mL", e23), qty("amount", 11, "mmol", e23)]),
        participant("p1a_dmap", "catalyst", "DMAP", e23, SMILES["dmap"], amounts=[qty("mass", 97, "mg", e23), qty("amount", 0.8, "mmol", e23)]),
        participant("p1a_ether", "solvent", "Et2O", e23, SMILES["diethyl_ether"], amounts=[qty("volume", 25, "mL", e23)]),
        participant("p1a_product", "product", "(3-n-butyl)penta-3,4-dien-2-yl acetate (1a)", e23, SMILES["acetate_1a"], amounts=[]),
    ],
    steps=[{"step_id": "acetylation_and_isolation", "participant_ids": [
        "p1a_allenol", "p1a_ac2o", "p1a_et3n", "p1a_dmap", "p1a_ether", "p1a_product"],
        "conditions": [field("temperature", "room temperature", e23), qty("time", 1, "h", e23),
                       field("operation", "stirred and monitored by TLC; solvent evaporated", e23),
                       field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate = 20:1", e23)]}],
    outcomes=[qty("product_mass", 1.455, "g", e23) | {"target_entity_ids": ["p1a_product"]},
              qty("yield", 100, "%", e23) | {"target_entity_ids": ["p1a_product"]},
              field("yield_measurement_basis", "after evaporation and flash chromatography", e23, ["p1a_product"])],
    unresolved=["The source does not state an atmosphere or a separate aqueous workup for this preparation."],
))

# Detailed preparation of allenylmalonate 2a.
e3 = ev(3)
records.append(record(
    "reported_preparation_2a", "reported_experiment", e3,
    participants=[
        participant("p2a_1a", "reactant", "(3-n-butyl)penta-3,4-dien-2-yl acetate (1a)", e3, SMILES["acetate_1a"], amounts=[qty("mass", 46, "mg", e3), qty("amount", 0.25, "mmol", e3)]),
        participant("p2a_malonate", "reactant", "dimethyl malonate", e3, SMILES["dimethyl_malonate"], amounts=[qty("volume", 0.09, "mL", e3), qty("equivalents", 3.0, "equiv", e3)]),
        participant("p2a_nah", "reagent", "NaH (60% dispersion in mineral oil)", e3, SMILES["sodium_hydride"], amounts=[qty("mass", 11, "mg", e3), qty("equivalents", 1.1, "equiv", e3)]),
        participant("p2a_pd", "catalyst", "Pd(PPh3)4", e3, amounts=[qty("mass", 14.5, "mg", e3), qty("catalyst_loading", 5, "mol%", e3)]),
        participant("p2a_dce", "solvent", "dry ClCH2CH2Cl", e3, SMILES["dce"], amounts=[qty("volume", 2.0, "mL", e3)]),
        participant("p2a_product", "product", "dimethyl 2-(1-methyl-2-butyl-2,3-butadienyl)malonate (2a)", e3, SMILES["2a"]),
    ],
    steps=[{"step_id": "alkylation", "participant_ids": ["p2a_1a", "p2a_malonate", "p2a_nah", "p2a_pd", "p2a_dce", "p2a_product"],
            "conditions": [field("atmosphere", "nitrogen", e3), field("temperature", "room temperature", e3), qty("time", 24, "h", e3),
                           field("operation", "NaH/Pd mixture followed by sequential addition of dimethyl malonate and 1a; monitored by TLC", e3),
                           field("workup", "quenched with saturated aqueous NaCl (2 mL), extracted with ether (20 mL), washed with brine (3 x 8 mL), dried over anhydrous Na2SO4, evaporated", e3),
                           field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate = 20:1", e3)]}],
    outcomes=[qty("product_mass", 53, "mg", e3) | {"target_entity_ids": ["p2a_product"]},
              qty("yield", 83, "%", e3) | {"target_entity_ids": ["p2a_product"]},
              field("yield_measurement_basis", "isolated after flash chromatography", e3, ["p2a_product"])],
    unresolved=["No concentration is stated."],
))

# Detailed 4aa experiment (Scheme 3 plus page-3 procedure).
records.append(record(
    "reported_coupling_4aa_condition_a", "reported_experiment", e2 + e3,
    participants=[
        participant("p4aa_2a", "reactant", "allenylmalonate 2a", e2 + e3, SMILES["2a"], amounts=[qty("mass", 51, "mg", e3), qty("amount", 0.2, "mmol", e3)]),
        participant("p4aa_phi", "reactant", "iodobenzene (3a)", e2 + e3, SMILES["3a"], amounts=[qty("mass", 49, "mg", e3), qty("amount", 0.24, "mmol", e3), qty("equivalents", 1.2, "equiv", e3)]),
        participant("p4aa_k2co3", "reagent", "K2CO3", e2 + e3, SMILES["potassium_carbonate"], amounts=[qty("mass", 112, "mg", e3), qty("amount", 0.8, "mmol", e3), qty("equivalents", 4.0, "equiv", e2)]),
        participant("p4aa_tbab", "reagent", "n-Bu4NBr", e2 + e3, SMILES["tetrabutylammonium_bromide"], amounts=[qty("mass", 6.4, "mg", e3), qty("catalyst_loading", 10, "mol%", e3)]),
        participant("p4aa_pd", "catalyst", "Pd(PPh3)4", e2 + e3, amounts=[qty("mass", 12, "mg", e3), qty("catalyst_loading", 5, "mol%", e3)]),
        participant("p4aa_me_cn", "solvent", "CH3CN", e2 + e3, SMILES["acetonitrile"], amounts=[qty("volume", 2, "mL", e3)]),
        participant("p4aa_product", "product", "cyclopropane 4aa (cis/trans mixture)", e2 + e3, SMILES["4aa"]),
        participant("p4aa_5aa", "product", "cyclopentene 5aa", e2 + e3),
    ],
    steps=[{"step_id": "coupling_cyclization_and_isolation", "participant_ids": [
        "p4aa_2a", "p4aa_phi", "p4aa_k2co3", "p4aa_tbab", "p4aa_pd", "p4aa_me_cn", "p4aa_product", "p4aa_5aa"],
        "conditions": [field("atmosphere", "nitrogen", e3), field("temperature", "reflux", e2 + e3), qty("time", 24, "h", e2 + e3),
                       field("operation", "monitored by TLC; filtered, washed with ether, and evaporated", e3),
                       field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate = 20:1", e3)]}],
    outcomes=[qty("product_mass", 62, "mg", e3) | {"target_entity_ids": ["p4aa_product"]},
              qty("yield", 94, "%", e2 + e3) | {"target_entity_ids": ["p4aa_product"]},
              field("cis_trans_ratio", "4:96", e2 + e3, ["p4aa_product"]),
              field("yield_measurement_basis", "isolated after flash chromatography", e3, ["p4aa_product"]),
              field("formation", "not observed", e2, ["p4aa_5aa"])],
    notes=["The trans/cis assignment of 4aa was based on 1H-1H NOESY (Figure 1)."],
    unresolved=["The individual masses/yields of cis-4aa and trans-4aa are not reported."],
))


def common_table_record(suffix, kind, evidence, allene_label, allene_smiles, halide_label,
                        halide_smiles, product_label, product_smiles, condition, solvent,
                        time_h, yield_pct, ratio, temperature="reflux", extra_notes=None,
                        extra_unresolved=None):
    participants = [
        participant("substrate", "reactant", allene_label, evidence, allene_smiles),
        participant("halide", "reactant", halide_label, evidence, halide_smiles,
                    amounts=[qty("equivalents", 1.2, "equiv", evidence)]),
        participant("palladium", "catalyst", "Pd(PPh3)4", evidence,
                    amounts=[qty("catalyst_loading", 5, "mol%", evidence)]),
        participant("carbonate", "reagent", "K2CO3", evidence, SMILES["potassium_carbonate"],
                    amounts=[qty("equivalents", 4.0, "equiv", evidence)]),
    ]
    if condition == "A":
        participants.append(participant("tbab", "reagent", "n-Bu4NBr", evidence,
                                        SMILES["tetrabutylammonium_bromide"],
                                        amounts=[qty("catalyst_loading", 10, "mol%", evidence)]))
    solvent_smiles = {"CH3CN": SMILES["acetonitrile"], "DMSO": SMILES["dmso"],
                      "DMF": SMILES["dmf"], "toluene": SMILES["toluene"]}.get(solvent)
    participants += [participant("solvent", "solvent", solvent, evidence, solvent_smiles),
                     participant("product", "product", product_label, evidence, product_smiles)]
    conditions = [qty("time", time_h, "h", evidence), field("temperature", temperature, evidence if temperature else [])]
    unresolved = ["Yield measurement basis, scale, atmosphere, workup, purification, and concentration are not stated for this table entry."]
    if not temperature:
        unresolved.append("Reaction temperature is not explicitly given for this solvent-screen entry.")
    unresolved += extra_unresolved or []
    return record(
        suffix, kind, evidence, participants,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        [qty("yield", yield_pct, "%", evidence) | {"target_entity_ids": ["product"]},
         field("cis_trans_ratio", ratio, evidence, ["product"]), field("yield_measurement_basis", None)],
        notes=extra_notes, unresolved=unresolved,
    )


# Table 1. Entry 1 is also Table 2 row 1 Condition A and therefore has page-3 evidence.
table1 = [
    (1, "CH3CN", 17, 86, "5:95", "A", "reflux"),
    (2, "CH3CN", 16, 93, "6:94", "B", "reflux"),
    (3, "DMSO", 16, 81, "8:92", "A", None),
    (4, "DMF", 34, 85, "6:94", "A", None),
    (5, "toluene", 60, 85, "6:94", "A", None),
]
for row, solvent, time_h, yld, ratio, cond, temp in table1:
    evidence = e2 + (e3 if row == 1 else [])
    if row == 2:
        evidence += ev(4)
    rec = common_table_record(
        f"table1_entry{row}_condition_{cond.lower()}", "optimization_entry", evidence,
        "allenylmalonate 2b", SMILES["2b"], "iodobenzene (3a)", SMILES["3a"],
        "cyclopropane 4ba (cis/trans mixture)", SMILES["4ba"], cond, solvent,
        time_h, yld, ratio, temp,
        extra_unresolved=(["Table 2 row 1 Condition B reports 10 h for the same labels/conditions/yield; this 16 h entry is kept separate."] if row == 2 else None),
    )
    records.append(rec)

# Enrich Table 1 entry 2 with the detailed page-4 quantities and workup, without duplicating it.
t1e2 = records[-4]
t1e2["participants"] = [
    participant("substrate", "reactant", "allenylmalonate 2b", t1e2["evidence_ids"], SMILES["2b"], amounts=[qty("mass", 70, "mg", ev(4)), qty("amount", 0.25, "mmol", ev(4))]),
    participant("halide", "reactant", "iodobenzene (3a)", t1e2["evidence_ids"], SMILES["3a"], amounts=[qty("mass", 61, "mg", ev(4)), qty("amount", 0.3, "mmol", ev(4)), qty("equivalents", 1.2, "equiv", t1e2["evidence_ids"])]),
    participant("palladium", "catalyst", "Pd(PPh3)4", t1e2["evidence_ids"], amounts=[qty("mass", 15, "mg", ev(4)), qty("catalyst_loading", 5, "mol%", t1e2["evidence_ids"])]),
    participant("carbonate", "reagent", "K2CO3", t1e2["evidence_ids"], SMILES["potassium_carbonate"], amounts=[qty("mass", 140, "mg", ev(4)), qty("amount", 1.0, "mmol", ev(4)), qty("equivalents", 4.0, "equiv", t1e2["evidence_ids"])]),
    participant("solvent", "solvent", "CH3CN", t1e2["evidence_ids"], SMILES["acetonitrile"], amounts=[qty("volume", 2, "mL", ev(4))]),
    participant("product", "product", "cyclopropane 4ba (cis/trans mixture)", t1e2["evidence_ids"], SMILES["4ba"]),
]
t1e2["steps"] = [{"step_id": "coupling_cyclization_and_isolation", "participant_ids": [p["entity_id"] for p in t1e2["participants"]],
                  "conditions": [field("atmosphere", "nitrogen", ev(4)), field("temperature", "reflux", t1e2["evidence_ids"]), qty("time", 16, "h", t1e2["evidence_ids"]),
                                 field("operation", "monitored by TLC; filtered, washed with ether, and evaporated", ev(4)),
                                 field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate = 20:1", ev(4))]}]
t1e2["outcomes"] = [qty("product_mass", 83, "mg", ev(4)) | {"target_entity_ids": ["product"]},
                     qty("yield", 93, "%", t1e2["evidence_ids"]) | {"target_entity_ids": ["product"]},
                     field("cis_trans_ratio", "6:94", t1e2["evidence_ids"], ["product"]),
                     field("yield_measurement_basis", "isolated after flash chromatography", ev(4), ["product"])]
t1e2["review"]["unresolved"] = ["Table 2 row 1 Condition B reports 10 h for the same labels/conditions/yield; this detailed 16 h experiment is kept separate."]

# Table 2: row 1 A is already Table 1 entry 1. Row 1 B differs in time (10 h) and is independent.
table2 = [
    (1, "2b", "n-C6H13/Me", "4ba", "B", 10, 93, "6:94"),
    (2, "2c", "n-C6H13/Ph", "4ca", "A", 36, 86, "4:96"),
    (2, "2c", "n-C6H13/Ph", "4ca", "B", 13, 91, "4:96"),
    (3, "2d", "Me/Me", "4da", "A", 21, 93, "6:94"),
    (3, "2d", "Me/Me", "4da", "B", 25, 72, "5:95"),
    (4, "2e", "Bn/Me", "4ea", "A", 42, 88, "20:80"),
    (4, "2e", "Bn/Me", "4ea", "B", 25, 80, "13:87"),
]
for row, substrate, substituents, product, cond, time_h, yld, ratio in table2:
    records.append(common_table_record(
        f"table2_entry{row}_condition_{cond.lower()}", "substrate_scope_entry", e3,
        f"allenylmalonate {substrate} (R1/R2 = {substituents})", SMILES[substrate],
        "iodobenzene (3a)", SMILES["3a"], f"cyclopropane {product} (cis/trans mixture)",
        SMILES[product], cond, "CH3CN", time_h, yld, ratio,
        extra_unresolved=(["Table 1 entry 2 and the detailed procedure report 16 h for the same labels/conditions/yield; this printed 10 h row is kept separate."] if row == 1 else None),
    ))


def table3_product_smiles(substrate, halide):
    # Candidate connectivity only; alkene stereochemistry is intentionally not certified.
    r1 = "CCCCCC"
    r2 = "C" if substrate == "2b" else "c2ccccc2"
    r3 = {"3b": "c1ccc(C(=O)OC)cc1", "3c": "/C=C/c1ccccc1",
          "3d": "c1cccs1", "3e": "/C=C/CCCC"}[halide]
    return f"COC(=O)C1(C(=O)OC)C({r2})C1({r1})C(=C){r3}"


table3 = [
    (1, "2b", "n-C6H13/Me", "3b", "methyl 4-iodobenzoate", "4bb", 9, 35, 77, "6:94", 49, "6:94"),
    (2, "2b", "n-C6H13/Me", "3c", "(E)-1-iodo-2-phenylethene", "4bc", 20, 13, 98, "11:89", 72, "7:93"),
    (3, "2b", "n-C6H13/Me", "3d", "2-iodothiophene", "4bd", 21, 13, 83, "8:92", 61, "7:93"),
    (4, "2b", "n-C6H13/Me", "3e", "(E)-1-iodohex-1-ene", "4be", 21, 24, 88, "6:94", 60, "5:95"),
    (5, "2c", "n-C6H13/Ph", "3b", "methyl 4-iodobenzoate", "4cb", 99, 72, 76, "5:95", 60, "7:93"),
    (6, "2c", "n-C6H13/Ph", "3c", "(E)-1-iodo-2-phenylethene", "4cc", 20, 13, 86, "6:94", 88, "6:94"),
]
for row, substrate, substituents, halide, halide_name, product, time_a, time_b, yield_a, ratio_a, yield_b, ratio_b in table3:
    for cond, time_h, yld, ratio in [("A", time_a, yield_a, ratio_a), ("B", time_b, yield_b, ratio_b)]:
        notes = []
        if row in (2, 4, 6):
            notes.append("The source states that the C=C configuration of the 1-alkenyl iodide remained unchanged during the reaction.")
        records.append(common_table_record(
            f"table3_entry{row}_condition_{cond.lower()}", "substrate_scope_entry", e3,
            f"allenylmalonate {substrate} (R1/R2 = {substituents})", SMILES[substrate],
            f"{halide_name} ({halide})", SMILES[halide], f"cyclopropane {product} (cis/trans mixture)",
            table3_product_smiles(substrate, halide), cond, "CH3CN", time_h, yld, ratio,
            extra_notes=notes,
            extra_unresolved=["Product SMILES is a non-stereochemical connectivity candidate derived from the fully specified table drawing and remains unverified."],
        ))

# Coverage: each page includes its original image evidence, and record IDs resolve to raw records.
ids = {r["source_reaction_id"]: r["record_id"] for r in records}
page1_ids = [ids["scheme1_generic_pi_allylpalladium_pathway"]]
page2_ids = [ids[x] for x in [
    "scheme2_arrow1_allenols_to_acetates", "scheme2_arrow2_acetates_to_allenylmalonates",
    "reported_preparation_1a", "reported_coupling_4aa_condition_a",
    "table1_entry1_condition_a", "table1_entry2_condition_b", "table1_entry3_condition_a",
    "table1_entry4_condition_a", "table1_entry5_condition_a"]]
page3_ids = [ids["reported_preparation_1a"], ids["reported_preparation_2a"], ids["reported_coupling_4aa_condition_a"],
             ids["table1_entry1_condition_a"]] + [ids[f"table2_entry{row}_condition_{cond}"] for row, cond in [(1,"b"),(2,"a"),(2,"b"),(3,"a"),(3,"b"),(4,"a"),(4,"b")]] + [ids[f"table3_entry{row}_condition_{cond}"] for row in range(1,7) for cond in ("a","b")]
page4_ids = [ids["reported_coupling_4aa_condition_a"], ids["table1_entry2_condition_b"]]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "upper-right Scheme 1", "finding": "Generic pi-allylpalladium pathway with alternative cyclopropane/cyclopentene closures; classified as mechanism, not a reported experiment.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            {"region": "title, abstract, and two-column introduction", "finding": "Article overview and cited prior work; no discrete current-paper experimental procedure or table row is reported in this region.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
        ], "record_ids": page1_ids, "unresolved": ["Scheme 1 contains generic R groups and no scale, time, temperature, or product-specific outcome."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "top Scheme 2", "finding": "Two generic synthetic arrows: allenols to acetates 1a-e, then acetate/malonate coupling to allenylmalonates 2a-e; kept as two general-scheme records.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "middle-left Scheme 3 and accompanying prose", "finding": "Condition-A 2a + PhI coupling gives cyclopropane 4aa in 94% yield, cis/trans 4:96; cyclopentene 5aa not observed; merged with page-3 detailed procedure.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "middle-right Table 1", "finding": "Five solvent-screen entries read row-by-row; footnote c removes n-Bu4NBr only from entry 2 and footnote a supplies 1.2 equiv PhI.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "lower-right Figure 1", "finding": "NOE stereochemical assignment for trans-4aa; characterization evidence, not a separate reaction.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "lower-right start of Experimental Section", "finding": "Preparation of acetate 1a begins and continues on page 3; represented once with both pages' evidence.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
        ], "record_ids": page2_ids, "unresolved": ["Scheme 2 family yield 82-87% is not product-specific.", "Table 1 entries 3-5 do not explicitly print reaction temperature."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 2", "finding": "Four substrate rows under Conditions A and B. Row 1/A duplicates Table 1 entry 1; row 1/B prints 10 h and is kept separate from Table 1/detailed 16 h experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "left-column experimental prose", "finding": "Completion of preparation 1a and full detailed preparation of allenylmalonate 2a, including quantities, workup, purification, mass, and yield.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "upper-right detailed Conditions A procedure", "finding": "Detailed 4aa coupling/isolation procedure merged with Scheme 3 rather than duplicated.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "bottom Table 3", "finding": "Six organic-halide rows, each split into independent Conditions A and B records (12 records); 1.2 equiv RI footnote structured for every row.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
        ], "record_ids": page3_ids, "unresolved": ["Table-only entries lack scale, atmosphere, workup, purification, concentration, and yield measurement basis.", "The printed 10 h versus 16 h Condition-B discrepancy for 4ba is preserved, not resolved."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "left-column Conditions B procedure", "finding": "Detailed 2b + PhI experiment without n-Bu4NBr: 16 h reflux, 83 mg 4ba, 93% yield, trans/cis 94:6; merged with Table 1 entry 2.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "top-right analytical continuation", "finding": "4ba analytical characterization; no additional reaction.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "right-column Supporting Information statement", "finding": "The article states SI is available, but no SI file was explicitly supplied in this workspace; no SI association was inferred.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
        ], "record_ids": page4_ids, "unresolved": ["Supporting information is mentioned but not provided/associated, so procedures and analytical data for unlisted compounds remain unavailable.", "Page 4 continues 4aa analytical data from page 3 but adds no new operational step."]},
    ],
}

assert len(coverage["pages"]) == 4
assert [p["page"] for p in coverage["pages"]] == [1, 2, 3, 4]
assert all(p["regions"] for p in coverage["pages"])
assert len({r["record_id"] for r in records}) == len(records)

RAW.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and 1 <= int(task["task_id"].split(":page")[1].split(":")[0]) <= 4:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text inspected; see coverage/pages_0001_0004.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": 4, "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
