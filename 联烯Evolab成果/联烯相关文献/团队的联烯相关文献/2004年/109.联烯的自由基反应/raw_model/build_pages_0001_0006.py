#!/usr/bin/env python3
"""Build evidence-linked candidate records for PDF pages 1-6 of the allene review."""

import json
from pathlib import Path


DOC = "doc_eb61b148fa9cdbba"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"


def evid(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def all_evid(pages):
    result = []
    for page in pages:
        result.extend(evid(page))
    return result


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence_ids, targets=None):
    item = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, smiles=None, amounts=None, name=None, evidence_ids=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence_ids) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, evidence_ids) for n, v in (amounts or [])],
    }


def record(sid, pages, kind, participants, conditions=None, outcomes=None, notes=None,
           unresolved=None, add_missing=True):
    evidence_ids = all_evid(pages)
    conditions = list(conditions or [])
    outcomes = list(outcomes or [])
    if add_missing and kind == "literature_example":
        if not any(x[0] == "temperature" for x in conditions):
            conditions.append(("temperature", None))
        if not any(x[0] == "time" for x in conditions):
            conditions.append(("time", None))
        if not any(x[0].endswith("yield") or x[0] == "yield" for x in outcomes):
            outcomes.append(("yield", None, None))
    ps = [part(*p[:6], evidence_ids=evidence_ids) for p in participants]
    step = []
    if kind not in ("mechanism", "general_scheme"):
        step = [{
            "step_id": "step1",
            "participant_ids": [p[0] for p in participants],
            "conditions": [fld(n, v, evidence_ids) for n, v in conditions],
        }]
    out_fields = []
    for name, value, targets in outcomes:
        out_fields.append(fld(name, value, evidence_ids, targets))
    default_unresolved = []
    if kind == "literature_example":
        default_unresolved = [
            "Prior-literature example summarized by this review; it is not a new experiment reported by the review authors.",
            "No explicitly associated supporting information was supplied.",
            "The reviewed pages do not provide a complete original experimental procedure, workup, purification, or yield basis.",
        ]
    else:
        default_unresolved = [
            "Generic or mechanistic drawing; it is not an individual reported experiment.",
            "Generic substituents and/or transient radicals prevent a fully specified structure assignment.",
        ]
    return {
        "record_id": f"{DOC}:{sid}",
        "document_id": DOC,
        "source_reaction_id": sid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence_ids,
        "participants": ps,
        "steps": step,
        "outcomes": out_fields,
        "notes": [fact(x, evidence_ids) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": default_unresolved + list(unresolved or []),
        },
    }


R = []

# Page 2: generic regioaddition mechanism, methyl-radical examples, and CF3I chain addition.
R.append(record("p2_scheme1_regioaddition_mechanism", [2], "mechanism", [
    ("allene_generic", "reactant", "RCH=C=CH2", None, None, None, None),
    ("radical_X", "unspecified_agent", "X radical", None, None, None, None),
    ("hydrogen_donor_XY", "reagent", "XY", None, None, None, None),
    ("central_products", "product", "E-2 / Z-2 / 3", None, None, None, None),
    ("terminal_products", "product", "6 / 7", None, None, None, None),
], notes=["Scheme 1 contrasts central and terminal radical attack and the resulting radical intermediates/products."], add_missing=False))

R.append(record("p2_scheme2_methyl_23_pentadiene", [2], "literature_example", [
    ("substrate", "reactant", "2,3-pentadiene", "CC=C=CC", None, None, None),
    ("methyl_iodide", "reagent", "CH3I", "CI", [("equivalents", {"number": 2, "unit": "equiv"})], None),
    ("product8", "product", "8", None, None, None, None),
], conditions=[("irradiation", "hν"), ("operation", "sealed"), ("atmosphere", "N2"),
               ("time", {"number": 12, "unit": "h"})],
    outcomes=[("overall_yield", {"number": 45, "unit": "%"}, ["product8"]),
              ("stereoisomer_ratio", "Z:E = 3:1", ["product8"])],
    notes=["Scheme 2: terminal-attack methyl-radical addition product."],
    unresolved=["Temperature and yield measurement basis are not stated in Scheme 2."]))

R.append(record("p2_scheme2_methyl_2methyl_23_pentadiene", [2], "literature_example", [
    ("substrate", "reactant", "2-methyl-2,3-pentadiene", "CC=C=C(C)C", None, None, None),
    ("methyl_iodide", "reagent", "CH3I", "CI", [("equivalents", {"number": 2, "unit": "equiv"})], None),
    ("product9", "product", "9", None, None, None, None),
    ("product10", "product", "10", None, None, None, None),
], conditions=[("irradiation", "hν"), ("operation", "sealed"), ("atmosphere", "N2"),
               ("time", {"number": 12, "unit": "h"})],
    outcomes=[("overall_yield", {"number": 45, "unit": "%"}, ["product9", "product10"]),
              ("reported_product_percentage", {"number": 72, "unit": "%"}, ["product9"]),
              ("reported_product_percentage", {"number": 28, "unit": "%"}, ["product10"])],
    notes=["Scheme 2: two terminal-attack-derived products are reported as a 72:28 distribution."],
    unresolved=["Temperature and yield measurement basis are not stated in Scheme 2."]))

R.append(record("p2_scheme3_cf3i_chain_mechanism", [2], "mechanism", [
    ("cf3i", "reactant", "CF3I", "FC(F)(F)I", None, None, None),
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("product11", "product", "11 radical intermediate", None, None, None, None),
    ("product12", "product", "12", "C=C(I)CC(F)(F)F", None, None, None),
], notes=["Scheme 3 shows photolysis of CF3I, terminal addition of CF3 radical to allene, and iodine-atom transfer."], add_missing=False))

R.append(record("p2_eq1_cf3i_23_pentadiene", [2], "literature_example", [
    ("substrate", "reactant", "2,3-pentadiene", "CC=C=CC", None, None, None),
    ("cf3i", "reagent", "CF3I", "FC(F)(F)I", None, None, None),
    ("product13", "product", "13", None, None, None, None),
    ("product14", "product", "14", None, None, None, None),
    ("product15", "product", "15", None, None, None, None),
], conditions=[("irradiation", "hν"), ("operation", "sealed"),
               ("time", {"number": 24, "unit": "h"})],
    outcomes=[("overall_yield", {"number": 44, "unit": "%"}, ["product13", "product14", "product15"]),
              ("reported_product_percentage", {"number": 70.3, "unit": "%"}, ["product13"]),
              ("reported_product_percentage", {"number": 20.3, "unit": "%"}, ["product14"]),
              ("reported_product_percentage", {"number": 9.4, "unit": "%"}, ["product15"])],
    notes=["Equation 1 reports the terminal-attack major product and two minor products."],
    unresolved=["Temperature, atmosphere, and yield measurement basis are not stated for Eq. 1."]))

# Page 3: perfluoroalkyl iodide, BrCCl3, HBr mechanism, and the five-row HBr table.
R.append(record("p3_eq2_perfluoroalkyl_iodide_generic", [3], "general_scheme", [
    ("substituted_allene", "reactant", "R1R2C=C=CHR3", None, None, None, None),
    ("perfluoroalkyl_iodide", "reagent", "Rf-I; Rf = CnF2n+1", None, None, None, None),
    ("product16", "product", "16", None, None, None, None),
], notes=["Equation 2 is a generic literature transformation under hν >300 nm using a Xe lamp and Pyrex."], add_missing=False))

R.append(record("p3_eq3_brccl3_allene", [3], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("bromotrichloromethane", "reagent", "BrCCl3", "ClC(Cl)(Cl)Br", None, None, None),
    ("initiator", "unspecified_agent", "light or peroxide", None, None, None, None),
    ("product17", "product", "17", "C=C(Br)CC(Cl)(Cl)Cl", None, None, None),
], conditions=[("irradiation_or_initiation", "hν or peroxide")], outcomes=[],
    notes=["Equation 3 is described as predominantly terminal attack; product 17 can undergo a second addition."],
    unresolved=["Temperature, time, yield, and the identity/loading of peroxide are not given for Eq. 3."]))

R.append(record("p3_scheme4_brccl3_23_pentadiene", [3], "literature_example", [
    ("substrate", "reactant", "2,3-pentadiene", "CC=C=CC", None, None, None),
    ("bromotrichloromethane", "reagent", "BrCCl3", "ClC(Cl)(Cl)Br", None, None, None),
    ("benzoyl_peroxide", "unspecified_agent", "benzoyl peroxide", "O=C(OOC(=O)c1ccccc1)c1ccccc1", None, None, None),
    ("product18", "product", "18", None, None, None, None),
    ("product19", "product", "19", None, None, None, None),
], conditions=[("temperature", "reflux"), ("time", {"number": 2, "unit": "h"})],
    outcomes=[("overall_yield", {"number": 70, "unit": "%"}, ["product18", "product19"]),
              ("stereoisomer_ratio", "Z:E = 47:12", ["product18"]),
              ("reported_product_percentage", {"number": 41, "unit": "%"}, ["product19"])],
    notes=["Scheme 4 reports both terminal- and central-attack products; 47:12 is printed as the Z:E ratio for 18."],
    unresolved=["The solvent and reflux temperature are not specified; the basis of the 70% overall yield is not stated."]))

R.append(record("p3_scheme4_brccl3_cyclononadiene", [3], "literature_example", [
    ("substrate", "reactant", "1,2-cyclononadiene", None, None, None, None),
    ("bromotrichloromethane", "reagent", "BrCCl3", "ClC(Cl)(Cl)Br", None, None, None),
    ("benzoyl_peroxide", "unspecified_agent", "benzoyl peroxide", "O=C(OOC(=O)c1ccccc1)c1ccccc1", None, None, None),
    ("product20", "product", "20", None, None, None, None),
], conditions=[("temperature", "reflux"), ("time", {"number": 2, "unit": "h"})],
    outcomes=[("overall_yield", {"number": 70, "unit": "%"}, ["product20"])],
    notes=["Scheme 4 attributes formation of a single product to steric effects."],
    unresolved=["The solvent and reflux temperature are not specified; the basis of the 70% yield is not stated."]))

R.append(record("p3_scheme5_hbr_attack_mechanism", [3], "mechanism", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("bromine_radical", "unspecified_agent", "Br radical", "[Br]", None, None, None),
    ("product21", "product", "21 (terminal-attack pathway product)", "C=CCBr", None, None, None),
    ("product22", "product", "22 (central-attack pathway product)", "C=C(Br)C", None, None, None),
], notes=["Scheme 5 compares terminal (kT) and central (kC) bromine-radical attack before hydrogen transfer."], add_missing=False))

def hbr_row(sid, substrate_label, substrate_smiles, yield_value, products, percentages, notes):
    participants = [
        ("substrate", "reactant", substrate_label, substrate_smiles, None, None, None),
        ("hbr", "reagent", "HBr", "Br", None, None, None),
    ]
    for pid, label, smiles in products:
        participants.append((pid, "product", label, smiles, None, None, None))
    outcomes = [("overall_yield", {"number": yield_value, "unit": "%"}, [p[0] for p in products])]
    outcomes.extend(("selectivity", {"number": value, "unit": "%"}, [pid]) for pid, value in percentages)
    return record(sid, [3], "literature_example", participants,
                  conditions=[("phase", "gas phase"), ("initiation", "photoinitiated")],
                  outcomes=outcomes, notes=[notes],
                  unresolved=["The table does not state temperature, time, pressure, HBr ratio, or yield measurement basis for this row."])

R.append(hbr_row("p3_hbr_table_row1_allene", "allene", "C=C=C", 98,
                 [("product", "2-bromopropene", "C=C(Br)C")], [("product", 100)],
                 "HBr table row 1: one central-attack product is shown."))
R.append(hbr_row("p3_hbr_table_row2_1_2_butadiene", "1,2-butadiene", "CC=C=C", 98,
                 [("terminal_product", "terminal-attack product", "C=C(Br)CC"),
                  ("central_Z", "central-attack Z isomer", None),
                  ("central_E", "central-attack E isomer", None)],
                 [("terminal_product", 6.5), ("central_Z", 83), ("central_E", 10.5)],
                 "HBr table row 2 prints 6.5% for the terminal product and Z:E = 83:10.5 for the central-attack isomers."))
R.append(hbr_row("p3_hbr_table_row3_dimethylallene", "3-methyl-1,2-butadiene", "C=C=C(C)C", 97,
                 [("product", "central-attack bromoalkene", "CC(Br)=C(C)C")], [("product", 100)],
                 "HBr table row 3: one product is shown with 100% selectivity."))
R.append(hbr_row("p3_hbr_table_row4_23_pentadiene", "2,3-pentadiene", "CC=C=CC", 96,
                 [("major_product", "major bromoalkene", None), ("minor_product", "minor bromoalkene", None)],
                 [("major_product", 94), ("minor_product", 6)],
                 "HBr table row 4 reports two regioisomeric products in a 94:6 distribution."))
R.append(hbr_row("p3_hbr_table_row5_tetramethylallene", "1,1,3,3-tetramethylallene", "CC(C)=C=C(C)C", 89,
                 [("product", "bromoalkene product", None)], [("product", 100)],
                 "HBr table row 5: one product is shown with 100% selectivity."))

# Page 4: F, H2S, PH3, phosphorus/sulfur acids, thiophenol, and substituted-allene examples.
R.append(record("p4_scheme6_fluorine_attack_mechanism", [4], "mechanism", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("fluorine_radical", "unspecified_agent", "F radical", "[F]", None, None, None),
    ("nf3", "reagent", "NF3", "FN(F)F", None, None, None),
    ("product23", "product", "23", None, None, None, None),
    ("product24", "product", "24", None, None, None, None),
], notes=["Scheme 6 shows central addition and an H-abstraction/substitution pathway; it is mechanistic, not an experimental procedure."], add_missing=False))

R.append(record("p4_scheme7_h2s_allene_primary", [4], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("h2s", "reagent", "H2S", "[SH2]", None, None, None),
    ("initiator", "unspecified_agent", "AIBN or tert-butyl hydroperoxide", None, None, None, None),
    ("product25", "product", "25 (allyl mercaptan)", "C=CCS", None, None, None),
], conditions=[("irradiation", "hν"), ("temperature", {"minimum": -80, "maximum": -70, "unit": "°C", "raw_text": "-70 to -80 °C"})],
    outcomes=[], notes=["Scheme 7 primary terminal addition of H2S to allene."],
    unresolved=["Time, initiator identity/loading, and yield are not stated."]))

R.append(record("p4_scheme7_h2s_second_addition", [4], "literature_example", [
    ("product25", "reactant", "25 (allyl mercaptan)", "C=CCS", None, None, None),
    ("h2s", "reagent", "H2S", "[SH2]", None, None, None),
    ("product26", "product", "26 (1,3-propanedithiol)", "SCCCS", None, None, None),
], outcomes=[], notes=["Excess H2S drives a further addition from 25 to 26."],
    unresolved=["The continuation arrow has no separate time, temperature, initiator, or yield."]))

R.append(record("p4_scheme7_allene_second_addition", [4], "literature_example", [
    ("product25", "reactant", "25 (allyl mercaptan)", "C=CCS", None, None, None),
    ("allene", "reagent", "allene", "C=C=C", None, None, None),
    ("product27", "product", "27 (diallyl sulfide)", "C=CCSCC=C", None, None, None),
], outcomes=[], notes=["Excess allene drives a further addition from 25 to 27."],
    unresolved=["The continuation arrow has no separate time, temperature, initiator, or yield."]))

R.append(record("p4_eq4_ph3_allene", [4], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("ph3", "reagent", "PH3", "[PH3]", None, None, None),
    ("polymer", "product", "polymer (major product)", None, None, None, None),
    ("minor_product", "product", "CH2=C(CH3)PH2 (minor central-attack product)", "C=C(C)[PH2]", None, None, None),
], conditions=[("irradiation", "hν")], outcomes=[],
    notes=["Equation 4: polymer is the predominant outcome; only a small amount of the depicted central-attack product is formed."],
    unresolved=["No quantitative polymer yield, minor-product yield, temperature, or time is reported."]))

for sid, reactants, product, note in [
    ("p4_scheme8_path29", [("allene", "reactant", "allene", "C=C=C", None, None, None),
                           ("acid", "reagent", "(RO)2P(S)SH", None, [("equivalents", {"number": 2, "unit": "equiv"})], None)],
     ("product29", "product", "29", None, None, None, None), "Scheme 8 upper primary-addition branch."),
    ("p4_scheme8_path30", [("product29", "reactant", "29", None, None, None, None),
                           ("acid", "reagent", "(RO)2P(S)SH", None, None, None)],
     ("product30", "product", "30", None, None, None, None), "Scheme 8 second addition from 29 to 30."),
    ("p4_scheme8_path31", [("allene", "reactant", "allene", "C=C=C", None, None, None),
                           ("acid", "reagent", "(RO)2P(S)SH", None, [("equivalents", {"number": 2, "unit": "equiv"})], None)],
     ("product31", "product", "31 (bracketed intermediate)", None, None, None, None), "Scheme 8 lower primary-addition branch; 31 is drawn in brackets."),
    ("p4_scheme8_path32", [("product31", "reactant", "31 (bracketed intermediate)", None, None, None, None),
                           ("acid", "reagent", "(RO)2P(S)SH", None, None, None)],
     ("product32", "product", "32", None, None, None, None), "Scheme 8 second addition from 31 to 32."),
]:
    cond = [("irradiation", "hν"), ("temperature", {"number": 17, "unit": "°C"})] if "path29" in sid or "path31" in sid else []
    R.append(record(sid, [4], "literature_example", reactants + [product], conditions=cond, outcomes=[], notes=[note],
                    unresolved=["No product yield or separate timing is reported for this arrow."]))

R.append(record("p4_eq5_thiophenol_allene", [4], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", [("amount", {"number": 0.3, "unit": "mol"})], None, None),
    ("thiophenol", "reagent", "C6H5SH", "Sc1ccccc1", [("amount", {"number": 0.1, "unit": "mol"})], None),
    ("di_tbutyl_peroxide", "unspecified_agent", "(t-BuO)2", "CC(C)(C)OOC(C)(C)C", [("amount", {"number": 0.001, "unit": "mol"})], None),
    ("terminal_mono", "product", "allyl phenyl sulfide (terminal attack)", "C=CCSc1ccccc1", None, None, None),
    ("terminal_double", "product", "1,3-bis(phenylthio)propane (terminal sequence)", "c1ccccc1SCCCSc2ccccc2", None, None, None),
    ("central_double", "product", "central-attack bis(phenylthio) product", None, None, None, None),
], conditions=[("irradiation", "irradiated in a quartz tube"), ("time", {"number": 3.5, "unit": "h"}),
               ("temperature", {"number": 17, "unit": "°C"})],
    outcomes=[("overall_yield", {"number": 83, "unit": "%"}, ["terminal_mono", "terminal_double", "central_double"]),
              ("reported_product_percentage", {"number": 72, "unit": "%"}, ["terminal_mono"]),
              ("reported_product_percentage", {"number": 7, "unit": "%"}, ["terminal_double"]),
              ("reported_product_percentage", {"number": 21, "unit": "%"}, ["central_double"])],
    notes=["Equation 5 brackets the first two products as terminal attack and labels the third as central attack."],
    unresolved=["The yield measurement basis and workup are not reported."]))

R.append(record("p4_scheme9_thiophenoxy_substituted_allene", [4], "literature_example", [
    ("substrate", "reactant", "ethyl-substituted allene shown in Scheme 9", None, None, None, None),
    ("thiophenoxy", "unspecified_agent", "C6H5S radical", "[S]c1ccccc1", None, None, None),
    ("product33", "product", "33", None, None, None, None),
    ("product34", "product", "34", None, None, None, None),
    ("product35", "product", "35", None, None, None, None),
    ("product36", "product", "36", None, None, None, None),
], outcomes=[("reported_product_percentage", {"number": 32.8, "unit": "%"}, ["product33"]),
              ("reported_product_percentage", {"number": 1.4, "unit": "%"}, ["product34"]),
              ("reported_product_percentage", {"number": 48.7, "unit": "%"}, ["product35"]),
              ("reported_product_percentage", {"number": 17.1, "unit": "%"}, ["product36"])],
    notes=["Scheme 9 compares central- and terminal-attack products for a substituted allene."],
    unresolved=["The scheme does not state explicit reaction time, temperature, solvent, initiator, or percentage basis."]))

# Page 5: seven Scheme 10 rows, two prose examples, and two Scheme 11 mechanism branches.
scheme10 = [
    ("pha", "PHA (phenylallene)", "C=C=Cc1ccccc1", "Z:E = 51:49"),
    ("cna", "CNA (cyanoallene)", "N#CC=C=C", "Z:E = 39:61"),
    ("meoa", "MeOA (methoxyallene)", "COC=C=C", "Z:E = 82:18"),
    ("cba", "CBA (methyl allenoate)", "COC(=O)C=C=C", "Z:E = 28:72"),
    ("cla", "ClA (chloroallene)", "ClC=C=C", "monoaddition Z:E = 80:20; double-addition pair = 53.4:46.6"),
    ("phsa", "PHSA (phenylthioallene)", "C=C=CSc1ccccc1", "Z:E = 60:40"),
    ("mphsa", "MPHSA (p-tolylthioallene)", "C=C=CSc1ccc(C)cc1", "Z:E = 60:40"),
]
for code, label, smiles, ratio in scheme10:
    products = [("product", "product", "product(s) shown for " + label, None, None, None, None)]
    R.append(record(f"p5_scheme10_{code}", [5], "literature_example", [
        ("substrate", "reactant", label, smiles, None, None, None),
        ("thiophenol", "reagent", "C6H5SH", "Sc1ccccc1", None, None, None),
    ] + products, conditions=[("irradiation", "sunlight")],
        outcomes=[("stereoisomer_ratio", ratio, ["product"])],
        notes=["Scheme 10 row for " + label + "."],
        unresolved=["No time, temperature, solvent, isolated yield, or yield basis is reported for this row."]))

R.append(record("p5_ref20_allene_thiophenol", [5], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("thiophenol", "reagent", "C6H5SH", "Sc1ccccc1", None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None, None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None, None),
    ("central_product", "product", "central-attack monoaddition product", None, None, None, None),
    ("double_product", "product", "double-addition product formed with increased thiophenol", None, None, None, None),
], conditions=[("temperature", {"number": 82, "unit": "°C"})], outcomes=[],
    notes=["The prose states central attack is predominant and increased thiophenol gives further double addition."],
    unresolved=["No time, product structures, yields, or reagent loadings are given in this prose summary."]))

R.append(record("p5_ref20_allene_alpha_toluenethiol", [5], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("thiol", "reagent", "alpha-CH3C6H4SH (as printed)", None, None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None, None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None, None),
    ("central_product", "product", "central-attack addition product", None, None, None, None),
], conditions=[("temperature", {"number": 82, "unit": "°C"})], outcomes=[],
    notes=["The exact identity implied by the printed alpha-CH3C6H4SH notation is retained without structural expansion."],
    unresolved=["No time, product structure, yield, or reagent loading is given; the thiol notation is chemically ambiguous."]))

R.append(record("p5_scheme11_bicyclic_allene_mechanism", [5], "mechanism", [
    ("bicyclic_allene", "reactant", "bicyclic allene shown in Scheme 11", None, None, None, None),
    ("thiophenol", "reagent", "C6H5SH", "Sc1ccccc1", None, None, None),
    ("product37", "product", "37", None, None, None, None),
], notes=["Scheme 11 upper branch shows thiophenoxy addition, radical cyclization, and H abstraction to product 37."], add_missing=False))

R.append(record("p5_scheme11_cyclopropyl_allene_mechanism", [5], "mechanism", [
    ("cyclopropyl_allene", "reactant", "cyclopropyl allene shown in Scheme 11", None, None, None, None),
    ("thiophenol", "reagent", "C6H5SH", "Sc1ccccc1", None, None, None),
    ("product38", "product", "38", None, None, None, None),
], notes=["Scheme 11 lower branch shows thiophenoxy addition and H abstraction to product 38."], add_missing=False))

# Pages 5-6: C2H5S table, generic RSAr equation, propylthiol prose example, and Scheme 12.
def ethylthiyl_row(sid, label, smiles, percentages):
    return record(sid, [5, 6], "literature_example", [
        ("substrate", "reactant", label, smiles, None, None, None),
        ("ethylthiyl", "unspecified_agent", "C2H5S radical", "CC[S]", None, None, None),
        ("products", "product", "regioisomeric addition products represented by attack arrows", None, None, None, None),
        ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None, None),
    ], conditions=[("temperature", {"number": 67, "unit": "°C"})],
        outcomes=[("addition_mode_ratio", percentages, ["products"])],
        notes=["The page-6 table reports percentages beside attack arrows; the values are preserved in printed left/central/right order."],
        unresolved=["The table does not provide time, solvent, product structures, or isolated yield."])

R.append(ethylthiyl_row("p6_c2h5s_table_row1_allene", "allene", "C=C=C", "left terminal 43.6%; central 12.8%; right terminal 43.6%"))
R.append(ethylthiyl_row("p6_c2h5s_table_row2_methylallene", "1,2-butadiene", "CC=C=C", "left terminal 6.3%; central 48.2%; right terminal 45.5%"))
R.append(ethylthiyl_row("p6_c2h5s_table_row3_dimethylallene", "3-methyl-1,2-butadiene", "C=C=C(C)C", "depicted attack site 100%"))

R.append(record("p6_eq6_rsar_generic", [5, 6], "general_scheme", [
    ("substituted_allene", "reactant", "substituted allene with Me/R groups", None, None, None, None),
    ("rsar_precursor", "reagent", "RSAr-type photolabile precursor shown in Eq. 6", None, None, None, None),
    ("product_set", "product", "four product classes shown in Eq. 6", None, None, None, None),
], notes=["Equation 6 is a generic RSAr addition scheme with variable R groups and includes monoadduct, rearranged/double-adduct, and oligomeric product classes."], add_missing=False))

R.append(record("p6_ref20_propylthiol_allene", [6], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None, None),
    ("propylthiol", "reagent", "C3H7SH (isomer not specified on page)", None, None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None, None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None, None),
    ("product43", "product", "43 (terminal-attack product; structure continues in Scheme 13)", None, None, None, None),
    ("central_2to1", "product", "2:1 addition product from central attack", None, None, None, None),
], conditions=[("temperature", {"number": 80, "unit": "°C"})],
    outcomes=[("reported_yield", {"number": 57, "unit": "%"}, ["product43"]),
              ("reported_yield", {"number": 30, "unit": "%"}, ["central_2to1"])],
    notes=["The products are stated to react further with C3H7SH; Scheme 13 structures are outside the inspected page range."],
    unresolved=["Time, reagent loadings, yield basis, and downstream product structures are not available on page 6."]))

R.append(record("p6_scheme12_methyl_allenoate", [5, 6], "literature_example", [
    ("substrate", "reactant", "methyl-substituted methyl allenoate shown in Scheme 12", None, None, None, None),
    ("thiophenoxy", "unspecified_agent", "PhS radical", "[S]c1ccccc1", None, None, None),
    ("thiophenol", "reagent", "PhSH", "Sc1ccccc1", None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None, None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None, None),
    ("z39", "product", "Z-39", None, None, None, None),
    ("product40", "product", "40", None, None, None, None),
    ("e39", "product", "E-39", None, None, None, None),
], conditions=[("temperature", "reflux")],
    outcomes=[("reported_product_percentage", {"number": 80, "unit": "%"}, ["z39"]),
              ("reported_product_percentage", {"number": 2, "unit": "%"}, ["product40"]),
              ("reported_product_percentage", {"number": 18, "unit": "%"}, ["e39"])],
    notes=["Scheme 12 upper example; page 5 supplies benzene/AIBN/reflux context and page 6 supplies products and percentages."],
    unresolved=["Reaction time, reagent loadings, workup, and percentage basis are not reported."]))

R.append(record("p6_scheme12_disubstituted_allenoate", [5, 6], "literature_example", [
    ("substrate", "reactant", "disubstituted allenoate shown in Scheme 12", None, None, None, None),
    ("thiophenoxy", "unspecified_agent", "PhS radical", "[S]c1ccccc1", None, None, None),
    ("thiophenol", "reagent", "PhSH", "Sc1ccccc1", None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None, None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None, None),
    ("z41", "product", "Z-41", None, None, None, None),
    ("e41", "product", "E-41", None, None, None, None),
    ("z42", "product", "Z-42", None, None, None, None),
    ("e42", "product", "E-42", None, None, None, None),
], conditions=[("temperature", "reflux")],
    outcomes=[("reported_product_percentage", {"number": 38, "unit": "%"}, ["z41"]),
              ("reported_product_percentage", {"number": 23, "unit": "%"}, ["e41"]),
              ("reported_product_percentage", {"number": 34, "unit": "%"}, ["z42"]),
              ("reported_product_percentage", {"number": 5, "unit": "%"}, ["e42"])],
    notes=["Scheme 12 lower example; page 5 supplies benzene/AIBN/reflux context and page 6 supplies products and percentages."],
    unresolved=["Reaction time, reagent loadings, workup, and percentage basis are not reported."]))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")


def ids(prefixes):
    result = []
    for item in R:
        if any(item["source_reaction_id"].startswith(x) for x in prefixes):
            result.append(item["record_id"])
    return result


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "整页：题名、摘要、英文摘要与引言", "finding": "综述首页；仅概述联烯自由基反应类型和一般区域选择性，无独立实验箭头、表格或可记录实验。", "evidence_ids": evid(1)},
            ],
            "record_ids": [],
            "unresolved": ["首页无实验细节；摘要中的一般规律未拆成实验记录。"],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "左栏 Scheme 1", "finding": "通用中心/末端进攻机理，分类为 mechanism。", "evidence_ids": evid(2)},
                {"region": "右上 Scheme 2", "finding": "两条不同底物的甲基自由基加成既往文献例子，分别记录。", "evidence_ids": evid(2)},
                {"region": "右下 Scheme 3 与 Eq. 1", "finding": "CF3I 链机理与一条 2,3-戊二烯实例；机理和实验分开记录。", "evidence_ids": evid(2)},
            ],
            "record_ids": ids(["p2_"]),
            "unresolved": ["Scheme 2/Eq. 1 未给温度和收率测定基础；产物结构保留原标签，复杂结构未强行生成 SMILES。"],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "左上 Eq. 2 与 Eq. 3", "finding": "一个带 R 基的通式和一个 BrCCl3/联烯既往例子。", "evidence_ids": evid(3)},
                {"region": "左中 Scheme 4", "finding": "2,3-戊二烯与环壬二烯两条独立箭头，分别记录。", "evidence_ids": evid(3)},
                {"region": "右上 Scheme 5", "finding": "HBr 中心/末端进攻动力学机理，分类为 mechanism。", "evidence_ids": evid(3)},
                {"region": "右下 HBr 表", "finding": "逐行放大核对，共五个不同联烯底物行，分别保存产率及选择性。", "evidence_ids": evid(3)},
            ],
            "record_ids": ids(["p3_"]),
            "unresolved": ["HBr 表未逐行给出温度、时间、压力和配比；表中百分数的实验测定基础未说明。"],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "左上 Scheme 6", "finding": "F·加成/攫氢机理，分类为 mechanism。", "evidence_ids": evid(4)},
                {"region": "左中 Scheme 7 与 Eq. 4", "finding": "H2S 初次加成及两条后续加成分别记录；PH3 反应保留主要聚合失败/少量产物结论。", "evidence_ids": evid(4)},
                {"region": "右上 Scheme 8", "finding": "两条初次加成分支和两条后续加成箭头分开记录。", "evidence_ids": evid(4)},
                {"region": "右中 Eq. 5", "finding": "逐项结构化 allene、thiophenol、过氧化物用量、时间、温度、总收率及 72:7:21 产品分布。", "evidence_ids": evid(4)},
                {"region": "右下 Scheme 9", "finding": "取代联烯四个产品的既往文献例子，保存四个报告百分数。", "evidence_ids": evid(4)},
            ],
            "record_ids": ids(["p4_"]),
            "unresolved": ["多个连续箭头未给各阶段独立条件或收率；Scheme 8 的 R 基和中间体 31 不完全指定。"],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "左栏 Scheme 10", "finding": "放大逐行核对七种取代联烯，分别记录光照条件和印刷的 Z:E/产品比。", "evidence_ids": evid(5)},
                {"region": "右上 Ref. 20 正文", "finding": "苯/AIBN/82 °C 下 PhSH 与另一含糊标记硫酚的两条既往例子分开记录。", "evidence_ids": evid(5)},
                {"region": "右中 Scheme 11", "finding": "两条底物分支均为自由基机理路径，分别分类为 mechanism。", "evidence_ids": evid(5)},
                {"region": "右下 Scheme 12/RSAr/C2H5S 衔接正文", "finding": "为第6页的 Eq. 6、C2H5S 表及 Scheme 12 提供条件和分类上下文，跨页合并证据而不重复建记录。", "evidence_ids": evid(5)},
            ],
            "record_ids": ids(["p5_", "p6_c2h5s_", "p6_eq6_", "p6_scheme12_"]),
            "unresolved": ["Scheme 10 无逐行收率/时间/温度；alpha-CH3C6H4SH 的印刷标记不能安全展开成唯一结构。"],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "左上 C2H5S· 加成方式表", "finding": "放大逐行核对三种底物；按印刷箭头位置保存 43.6/12.8/43.6、6.3/48.2/45.5 和 100%。", "evidence_ids": evid(6)},
                {"region": "右上 Eq. 6", "finding": "含可变 R 基及多类产物的通式，分类为 general_scheme。", "evidence_ids": evid(6)},
                {"region": "右中 C3H7S· 正文", "finding": "保存苯/AIBN/80 °C、57% 末端产物和 30% 中心进攻 2:1 加成产物；Scheme 13 结构在范围外。", "evidence_ids": evid(6)},
                {"region": "下半页 Scheme 12", "finding": "两条底物箭头分别记录，并将 Z/E-39、40、Z/E-41、Z/E-42 百分数关联到具体产品。", "evidence_ids": evid(6)},
            ],
            "record_ids": ids(["p6_"]),
            "unresolved": ["C2H5S 表缺产品结构和独立产率；Scheme 13 不在本次页范围；Scheme 12 的百分数测定基础未说明。"],
        },
    ],
}

COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    prefix = f"{DOC}:page"
    task_id = task.get("task_id", "")
    if not task_id.startswith(prefix) or not task_id.endswith(":text"):
        continue
    page = int(task_id[len(prefix):].split(":", 1)[0])
    if 1 <= page <= 6:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; findings and unresolved issues are recorded in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(R), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
