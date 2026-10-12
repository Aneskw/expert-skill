#!/usr/bin/env python3
"""Build evidence-linked candidate records for PDF pages 7-12 of the allene review."""

import json
from pathlib import Path


DOC = "doc_eb61b148fa9cdbba"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0007_0012.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0007_0012.json"


def evid(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def all_evid(pages):
    return [eid for page in pages for eid in evid(page)]


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
           unresolved=None, add_missing=True, step_specs=None):
    evidence_ids = all_evid(pages)
    conditions = list(conditions or [])
    outcomes = list(outcomes or [])
    if add_missing and kind == "literature_example":
        if not any(x[0] == "temperature" for x in conditions):
            conditions.append(("temperature", None))
        if not any(x[0] == "time" for x in conditions):
            conditions.append(("time", None))
        if not any("yield" in x[0] for x in outcomes):
            outcomes.append(("yield", None, None))
    ps = [part(*p[:6], evidence_ids=evidence_ids) for p in participants]
    if step_specs is not None:
        steps = [
            {
                "step_id": step_id,
                "participant_ids": list(participant_ids),
                "conditions": [fld(n, v, evidence_ids) for n, v in step_conditions],
            }
            for step_id, participant_ids, step_conditions in step_specs
        ]
    elif kind in ("mechanism", "general_scheme"):
        steps = []
    else:
        steps = [{
            "step_id": "step1",
            "participant_ids": [p[0] for p in participants],
            "conditions": [fld(n, v, evidence_ids) for n, v in conditions],
        }]
    out_fields = [fld(name, value, evidence_ids, targets) for name, value, targets in outcomes]
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
        "steps": steps,
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

# Page 7, Scheme 13: replace the page-6 prose-only record with the complete cross-page scheme.
R.append(record("p6_ref20_propylthiol_allene", [6, 7], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", [("amount", {"number": 0.7, "unit": "mol"})], None),
    ("propylthiol", "reagent", "C3H7SH (propyl isomer not specified)", None, [("amount", {"number": 0.4, "unit": "mol"})], None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", [("amount", {"number": 0.012, "unit": "mol"})], None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None),
    ("product43", "product", "43, C3H7S-CH2-CH=CH2 (terminal-attack primary product)", None, None, None),
    ("product44", "product", "44, C3H7S-C(CH3)=CH2 (central-attack primary product)", None, None, None),
    ("product45", "product", "45, C3H7S-CH2-CH2-CH2-SC3H7", None, None, None),
    ("product46", "product", "46, C3H7S-CH(CH3)-CH2-SC3H7", None, None, None),
], conditions=[("temperature", {"number": 82, "unit": "°C"}), ("time", {"number": 4, "unit": "h"})],
    outcomes=[("reported_yield", {"number": 57, "unit": "%"}, ["product43"]),
              ("reported_yield", {"number": 30, "unit": "%"}, ["product46"])],
    notes=["Scheme 13 depicts primary terminal/central addition products 43/44 and their further propylthiol additions 45/46."],
    unresolved=["The scheme gives no separate yields for 44 or 45 and no measurement basis for the 57% and 30% values."],
    step_specs=[
        ("step1_primary_addition", ["allene", "propylthiol", "aibn", "benzene", "product43", "product44"],
         [("temperature", {"number": 82, "unit": "°C"}), ("time", {"number": 4, "unit": "h"})]),
        ("step2_further_addition", ["propylthiol", "product43", "product44", "product45", "product46"], []),
    ]))


def scheme14_row(code, r_label, rsh_label, rsh_smiles, total_yield, values, smiles):
    pids = ["terminal_mono", "terminal_double", "central_double"]
    return record(f"p7_scheme14_{code}", [7], "literature_example", [
        ("allene", "reactant", "allene", "C=C=C", None, None),
        ("rsh", "reagent", rsh_label, rsh_smiles, None, None),
        ("terminal_mono", "product", f"RSCH2CH=CH2; R = {r_label}", smiles[0], None, None),
        ("terminal_double", "product", f"RS(CH2)3SR; R = {r_label}", smiles[1], None, None),
        ("central_double", "product", f"RSCH(CH3)CH2SR; R = {r_label}", smiles[2], None, None),
    ], conditions=[("temperature", {"number": 17, "unit": "°C"}), ("time", {"number": 15, "unit": "min"})],
        outcomes=[("overall_yield", {"number": total_yield, "unit": "%"}, pids),
                  ("mixture_component_percentage", {"number": values[0], "unit": "%"}, ["terminal_mono"]),
                  ("mixture_component_percentage", {"number": values[1], "unit": "%"}, ["terminal_double"]),
                  ("mixture_component_percentage", {"number": values[2], "unit": "%"}, ["central_double"]),
                  ("central_attack_selectivity", {"number": values[2], "unit": "%"}, ["central_double"])],
        notes=["Scheme 14 table row; component values are explicitly headed mol%."],
        unresolved=["The source does not state radical-initiation details, workup, or the basis of the total yield."])


R.append(scheme14_row("methylthiyl", "CH3", "CH3SH", "CS", 54, (74, 13, 13),
                      ("C=CCSC", "CSCCCSC", "CSC(C)CSC")))
R.append(scheme14_row("acetylthiyl", "CH3CO", "CH3COSH", "CC(=O)S", 92, (73, 18, 9),
                      ("C=CCSC(C)=O", "CC(=O)SCCCSC(C)=O", "CC(=O)SC(C)CSC(C)=O")))

# Page 7, Schemes 15-16.
tbu_allene = ("substrate", "reactant", "tert-butyl-substituted allene shown in Schemes 15-17", None, None, None)
R.append(record("p7_scheme15_diphenyl_disulfide", [7], "literature_example", [
    tbu_allene,
    ("diphenyl_disulfide", "reagent", "(PhS)2", None, [("equivalents", {"number": 1, "unit": "equiv"})], None),
    ("cdcl3", "solvent", "CDCl3", "ClC(Cl)Cl", None, None),
    ("mixture", "product", "a complex mixture", None, None, None),
], conditions=[("irradiation", "hν (>300 nm)"), ("temperature", {"number": 15, "unit": "°C"}),
               ("time", {"number": 24, "unit": "h"})],
    outcomes=[("reaction_result", "a complex mixture", ["mixture"])],
    notes=["Scheme 15 reports a complex mixture rather than an isolated product."],
    unresolved=["No component identities, yields, or measurement basis are provided."]))

R.append(record("p7_scheme15_diphenyl_diselenide", [7], "literature_example", [
    tbu_allene,
    ("diphenyl_diselenide", "reagent", "(PhSe)2", None, [("equivalents", {"number": 1, "unit": "equiv"})], None),
    ("cdcl3", "solvent", "CDCl3", "ClC(Cl)Cl", None, None),
    ("product", "product", "bis(phenylseleno) addition product shown in Scheme 15", None, None, None),
], conditions=[("irradiation", "hν (>300 nm)"), ("temperature", {"number": 15, "unit": "°C"}),
               ("time", {"number": 1, "unit": "h"})],
    outcomes=[("reported_yield", {"number": 82, "unit": "%"}, ["product"]),
              ("stereoisomer_ratio", "E:Z = 28:72", ["product"])],
    notes=["Scheme 15 identifies (PhSe)2 as the successful member of the Ph2Y2 series."],
    unresolved=["Yield measurement basis and stereoisomer-assay method are not stated."]))

R.append(record("p7_scheme15_diphenyl_ditelluride", [7], "literature_example", [
    tbu_allene,
    ("diphenyl_ditelluride", "reagent", "(PhTe)2", None, [("equivalents", {"number": 1, "unit": "equiv"})], None),
    ("cdcl3", "solvent", "CDCl3", "ClC(Cl)Cl", None, None),
], conditions=[("irradiation", "hν (>300 nm)"), ("temperature", {"number": 15, "unit": "°C"}),
               ("time", {"number": 1, "unit": "h"})],
    outcomes=[("reaction_result", "no reaction", None)],
    notes=["Scheme 15 explicitly reports no reaction."],
    unresolved=["No conversion or detection-limit basis is supplied."]))


def scheme16_record(code, reagent_label, irradiation, values, prefix):
    participants = [tbu_allene, ("hydrogen_donor", "reagent", reagent_label, None,
                                 [("equivalents", {"number": 1, "unit": "equiv"})] if reagent_label == "PhSeH" else None, None)]
    products = []
    for i, descriptor in enumerate(("central-attack alkene isomer", "central-attack exomethylene isomer", "terminal-attack product"), 1):
        pid = f"product{i}"
        participants.append((pid, "product", f"{prefix} {descriptor}", None, None, None))
        products.append(pid)
    return record(f"p7_scheme16_{code}", [7], "literature_example", participants,
                  conditions=[("irradiation", irradiation)],
                  outcomes=[("reported_product_percentage", {"number": v, "unit": "%"}, [pid])
                            for pid, v in zip(products, values)],
                  notes=["Scheme 16 reports three regioisomeric products in the printed left-to-right order."],
                  unresolved=["No overall yield, temperature, time, solvent, or percentage measurement basis is stated."])


R.append(scheme16_record("thiophenol", "PhSH", "UV", (37, 38, 25), "PhS"))
R.append(scheme16_record("benzeneselenol", "PhSeH", "hν (>300 nm)", (70, 8, 0), "PhSe"))

# Page 8, Scheme 17.
scheme17_rows = [
    ("phs2_phse2", "(PhS)2", "(PhSe)2", {"number": 1, "unit": "equiv"}, "hν (>300 nm)", 3, 99, "E:Z = 22:78", "mixed PhS/PhSe adduct"),
    ("phs2_phte2", "(PhS)2", "(PhTe)2", {"number": 1, "unit": "equiv"}, "hν (>400 nm)", 20, 50, "E:Z = 24:76", "mixed PhS/PhTe adduct"),
    ("phs2_phte2_catalytic", "(PhS)2", "(PhTe)2", {"number": 30, "unit": "mol%"}, "hν (>400 nm)", 50, 62, "E:Z = 14:86", "bis(phenylthio) adduct"),
]
for code, r1, r2, amount2, light, hours, yld, ratio, product_label in scheme17_rows:
    R.append(record(f"p8_scheme17_{code}", [8], "literature_example", [
        tbu_allene,
        ("reagent1", "reagent", r1, None, [("equivalents", {"number": 1, "unit": "equiv"})], None),
        ("reagent2", "reagent", r2, None, [("loading", amount2)], None),
        ("cdcl3", "solvent", "CDCl3", "ClC(Cl)Cl", None, None),
        ("product", "product", product_label, None, None, None),
    ], conditions=[("irradiation", light), ("temperature", {"number": 40, "unit": "°C"}),
                   ("time", {"number": hours, "unit": "h"})],
        outcomes=[("reported_yield", {"number": yld, "unit": "%"}, ["product"]),
                  ("stereoisomer_ratio", ratio, ["product"])],
        notes=["Scheme 17 two-component photochemical addition row."],
        unresolved=["Yield and E/Z measurement bases are not stated."]))

R.append(record("p8_scheme18_mixed_thiyl_selenyl_mechanism", [8], "mechanism", [
    ("substituted_allene", "reactant", "R-substituted allene", None, None, None),
    ("phenylselenyl", "unspecified_agent", "PhSe radical", None, None, None),
    ("diphenyl_disulfide", "reagent", "PhSSPh", None, None, None),
    ("product", "product", "mixed PhSe/PhS addition product", None, None, None),
], notes=["Scheme 18 proposes PhSe radical addition, radical delocalization, and sulfur-atom transfer."], add_missing=False))

R.append(record("p8_scheme19_oxygen_diphenyl_allene", [8], "literature_example", [
    ("substrate", "reactant", "phenyl/methyl-substituted allene shown in Scheme 19", None, None, None),
    ("phseh", "reagent", "PhSeH", None, None, None),
    ("oxygen", "reagent", "O2", "O=O", None, None),
    ("product47", "product", "47, central-attack allylic selenide", None, None, None),
    ("product48", "product", "48, terminal-attack exomethylene selenide", None, None, None),
], conditions=[], outcomes=[
    ("reported_product_percentage", {"number": 88, "unit": "%"}, ["product47"]),
    ("stereoisomer_ratio", "E:Z = 4:3", ["product47"]),
    ("reported_product_percentage", {"number": 12, "unit": "%"}, ["product48"]),
], notes=["Scheme 19 explicitly attributes the high central-attack selectivity to O2 initiation."],
    unresolved=["No overall yield, temperature, time, solvent, or percentage basis is stated."]))

R.append(record("p8_scheme19_oxygen_dimethylallene", [8], "literature_example", [
    ("substrate", "reactant", "3-methyl-1,2-butadiene", "C=C=C(C)C", None, None),
    ("phseh", "reagent", "PhSeH", None, None, None),
    ("oxygen", "reagent", "O2", "O=O", None, None),
    ("product49", "product", "49, central-attack phenylseleno alkene", None, None, None),
], conditions=[], outcomes=[("reported_yield", {"number": 83, "unit": "%"}, ["product49"])],
    notes=["Scheme 19 lower example."],
    unresolved=["Temperature, time, solvent, and yield measurement basis are not stated."]))

R.append(record("p8_eq7_phselenyl_central_attack_mechanism", [8], "mechanism", [
    ("substituted_allene", "reactant", "R-substituted allene", None, None, None),
    ("phenylselenyl", "unspecified_agent", "PhSe radical", None, None, None),
    ("diphenyl_diselenide", "reagent", "(PhSe)2", None, None, None),
    ("product50", "product", "50", None, None, None),
], notes=["Equation 7 proposes central attack followed by selenium transfer from diphenyl diselenide."], add_missing=False))

R.append(record("p8_scheme20_dicyanomethyl_attack_mechanism", [8], "mechanism", [
    ("bromomalononitrile", "reagent", "BrCH(CN)2", "N#CC(Br)C#N", None, None),
    ("dicyanomethyl_radical", "unspecified_agent", "CH(CN)2 radical", None, None, None),
    ("substituted_allene", "reactant", "R1R2C=C=CR3R4", None, None, None),
    ("products", "product", "addition products a-d", None, None, None),
], notes=["Scheme 20 defines central- and terminal-attack pathways and product classes a-d for the table continued on page 9."], add_missing=False))


def scheme20_row(code, label, smiles, distribution, central):
    participants = [
        ("substrate", "reactant", label, smiles, None, None),
        ("bromomalononitrile", "reagent", "BrCH(CN)2", "N#CC(Br)C#N", None, None),
    ]
    outcomes = []
    for product_code, value in distribution:
        pid = f"product_{product_code}"
        participants.append((pid, "product", f"Scheme 20 product {product_code}", None, None, None))
        outcomes.append(("reported_product_percentage", value, [pid]))
    outcomes.append(("central_attack_selectivity", central, [f"product_{x}" for x, _ in distribution if x in ("a", "b")]))
    return record(f"p9_scheme20_table_{code}", [8, 9], "literature_example", participants,
                  conditions=[("irradiation", "hν")], outcomes=outcomes,
                  notes=["Scheme 20 table row; blank product columns were not converted to zero."],
                  unresolved=["The table does not give temperature, time, solvent, overall yield, or the analytical basis of percentages."])


ge95 = {"number": 95, "unit": "%", "qualifier": "ge", "raw_text": "≥95%"}
le5 = {"number": 5, "unit": "%", "qualifier": "le", "raw_text": "≤5%"}
R.extend([
    scheme20_row("row1_allene", "allene", "C=C=C", [("c", ge95)], le5),
    scheme20_row("row2_methylallene", "1,2-butadiene", "CC=C=C", [("a", {"number": 70, "unit": "%"}), ("c", {"number": 18, "unit": "%"}), ("d", {"number": 12, "unit": "%"})], {"number": 70, "unit": "%"}),
    scheme20_row("row3_ethylallene", "1,2-pentadiene", "CCC=C=C", [("a", {"number": 45, "unit": "%"}), ("b", {"number": 15, "unit": "%"}), ("c", {"number": 40, "unit": "%"})], {"number": 60, "unit": "%"}),
    scheme20_row("row4_dimethylallene", "3-methyl-1,2-butadiene", "C=C=C(C)C", [("a", ge95)], ge95),
    scheme20_row("row5_linear_alkyl_allene", "linear alkyl-substituted allene, Scheme 20 table row 5", None, [("a", {"number": 89, "unit": "%"}), ("c", {"number": 11, "unit": "%"})], {"number": 89, "unit": "%"}),
    scheme20_row("row6_linear_alkyl_allene", "linear alkyl-substituted allene, Scheme 20 table row 6", None, [("a", ge95)], ge95),
])

# Page 9, Equation 8 and trimethyltin-hydride table.
R.append(record("p9_eq8_trimethyltin_chain_mechanism", [9], "mechanism", [
    ("trimethyltin_radical", "unspecified_agent", "Me3Sn radical", None, None, None),
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ("trimethyltin_hydride", "reagent", "Me3SnH", None, None, None),
    ("product", "product", "Me3SnCH2CH=CH2", None, None, None),
], notes=["Equation 8 shows terminal addition of Me3Sn radical followed by H-atom transfer."], add_missing=False))


def sn_table_row(code, label, smiles, overall, components, ratios=None):
    participants = [
        ("substrate", "reactant", label, smiles, None, None),
        ("trimethyltin_hydride", "reagent", "(CH3)3SnH", None, None, None),
        ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ]
    outcomes = []
    for pid, product_label, value in components:
        participants.append((pid, "product", product_label, None, None, None))
        outcomes.append(("reported_product_percentage", {"number": value, "unit": "%"}, [pid]))
    for pid, value in (ratios or []):
        outcomes.append(("stereoisomer_ratio", value, [pid]))
    outcomes.insert(0, ("overall_yield", {"number": overall, "unit": "%"}, [x[0] for x in components]))
    return record(f"p9_trimethyltin_table_{code}", [8, 9], "literature_example", participants,
                  conditions=[("temperature", {"number": 100, "unit": "°C"}), ("time", {"number": 9, "unit": "h"})],
                  outcomes=outcomes,
                  notes=["The page-8 prose supplies AIBN, 100 °C, 9 h, excess-allene context for this page-9 table row."],
                  unresolved=["The table does not state reagent amounts, solvent, workup, or yield/percentage measurement bases."])


R.extend([
    sn_table_row("allene", "allene", "C=C=C", 67,
                 [("product1", "central-attack trimethyltin product", 45.2),
                  ("product2", "terminal-attack trimethyltin product", 54.8)]),
    sn_table_row("methylallene", "1,2-butadiene", "CC=C=C", 72.6,
                 [("product1", "depicted trimethyltin regioisomer 1", 31.5),
                  ("product2_z", "depicted trimethyltin regioisomer 2, Z", 16.3),
                  ("product2_e", "depicted trimethyltin regioisomer 2, E", 38.6),
                  ("product3_z", "depicted trimethyltin regioisomer 3, Z", 3.5),
                  ("product3_e", "depicted trimethyltin regioisomer 3, E", 10.0)]),
    sn_table_row("dimethylallene", "3-methyl-1,2-butadiene", "C=C=C(C)C", 72,
                 [("product1", "depicted central-attack trimethyltin product", 26.8),
                  ("product2", "depicted terminal-attack trimethyltin product", 73.2)]),
    sn_table_row("23_pentadiene", "2,3-pentadiene", "CC=C=CC", 65,
                 [("product", "depicted trimethyltin alkene product", 100)],
                 [("product", "Z:E = 54:46")]),
    sn_table_row("trimethylallene", "1,1,3-trimethylallene", "CC=C=C(C)C", 82.5,
                 [("product1", "depicted trimethyltin regioisomer 1", 54.5),
                  ("product2", "depicted trimethyltin regioisomer 2", 45.5)],
                 [("product1", "Z:E = 22.4:77.6")]),
])

# Page 10, Ph3SnH/Ph3GeH table.
def page10_table_row(code, substrate, donor, products, ratio=None):
    participants = [
        ("substrate", "reactant", substrate, None, None, None),
        ("hydride_donor", "reagent", donor, None, None, None),
        ("et3b", "unspecified_agent", "Et3B", "CCB(CC)CC", None, None),
    ]
    outcomes = []
    for pid, label, yld in products:
        participants.append((pid, "product", label, None, None, None))
        outcomes.append(("reported_yield", {"number": yld, "unit": "%"}, [pid]))
    if ratio:
        outcomes.append(("stereoisomer_ratio", ratio[1], [ratio[0]]))
    return record(f"p10_hydride_table_{code}", [10], "literature_example", participants,
                  conditions=[("initiation", "Et3B initiated")], outcomes=outcomes,
                  notes=["Page-10 prior-literature hydride-addition table row."],
                  unresolved=["The table does not state temperature, time, solvent, reagent loadings, workup, or yield basis."])


R.extend([
    page10_table_row("allene_ph3snh", "allene", "Ph3SnH", [
        ("product1", "H2C=CHCH2SnPh3", 36), ("product2", "CH2=C(Me)SnPh3", 24)]),
    page10_table_row("allene_ph3geh", "allene", "Ph3GeH", [
        ("product", "H2C=CHCH2GePh3", 57)]),
    page10_table_row("n_c10_allene_ph3snh", "n-C10H21CH=C=CH2", "Ph3SnH", [
        ("product1", "n-C10H21CH=C(Me)SnPh3", 51),
        ("product2", "n-C10H21CH2C(SnPh3)=CH2", 10),
        ("product3", "n-C10H21CH=CHCH2SnPh3", 5)], ("product1", "E:Z = 3:2")),
    page10_table_row("n_c10_allene_ph3geh", "n-C10H21CH=C=CH2", "Ph3GeH", [
        ("product", "n-C10H21CH=CHCH2GePh3", 82)]),
    page10_table_row("silylallene_ph3snh", "PhMe2SiCH=C=CH2", "Ph3SnH", [
        ("product1", "PhMe2SiCH2C(SnPh3)=CH2", 62),
        ("product2", "PhMe2SiCH=C(Me)SnPh3", 33)]),
    page10_table_row("silylallene_ph3geh", "PhMe2SiCH=C=CH2", "Ph3GeH", [
        ("product1", "PhMe2SiCH=CHCH2GePh3", 69),
        ("product2", "PhMe2SiCH=C(Me)GePh3", 28)]),
    page10_table_row("67_tridecadiene_ph3geh", "6,7-tridecadiene", "Ph3GeH", [
        ("product", "n-C5H11CH=C(SnPh3)CH2C5H11 (label as printed)", 81)], ("product", "E:Z = 32:68")),
    page10_table_row("cyclononadiene_ph3snh", "1,2-cyclononadiene", "Ph3SnH", [
        ("product", "1-(triphenylstannyl)cyclononene", 74)]),
])

R.append(record("p10_scheme21_tbuocl_mechanism", [10], "mechanism", [
    ("dimethylallene", "reactant", "3-methyl-1,2-butadiene", "C=C=C(C)C", None, None),
    ("tert_butoxy_radical", "unspecified_agent", "t-BuO radical", None, None, None),
    ("tert_butyl_hypochlorite", "reagent", "t-BuOCl", "CC(C)(C)OCl", None, None),
    ("products", "product", "four chlorinated allene/alkyne/diene products shown in Scheme 21", None, None, None),
], notes=["Scheme 21 is a mechanistic network for H abstraction/addition followed by chlorine transfer."], add_missing=False))

# Pages 10-11, Schemes 22-24.
R.append(record("p11_scheme22_allene", [10, 11], "literature_example", [
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("arylsulfonyl_iodide", "reagent", "ArSO2I", None, None, None),
    ("product1", "product", "iodo/arylsulfonyl product, Scheme 22 major", None, None, None),
    ("product2", "product", "bis(arylsulfonyl) product, Scheme 22 minor", None, None, None),
], conditions=[("operation", "sealed tube"), ("irradiation", "200 W")], outcomes=[
    ("overall_yield", {"number": 64, "unit": "%"}, ["product1", "product2"]),
    ("reported_product_percentage", {"number": 80, "unit": "%"}, ["product1"]),
    ("reported_product_percentage", {"number": 20, "unit": "%"}, ["product2"]),
], notes=["Scheme 22 first arrow reports 64% total and an 80:20 product distribution."],
    unresolved=["Ar is unspecified; temperature, time, solvent, and yield/ratio measurement bases are not given."]))

R.append(record("p11_scheme22_methylallene", [10, 11], "literature_example", [
    ("substrate", "reactant", "1,2-butadiene", "CC=C=C", None, None),
    ("arylsulfonyl_iodide", "reagent", "ArSO2I", None, None, None),
    ("product", "product", "central-attack iodo/arylsulfonyl alkene shown in Scheme 22", None, None, None),
], conditions=[("operation", "sealed tube"), ("irradiation", "200 W")],
    outcomes=[("reported_yield", {"number": 73, "unit": "%"}, ["product"])],
    notes=["Scheme 22 second arrow."],
    unresolved=["Ar is unspecified; temperature, time, solvent, and yield basis are not given."]))

R.append(record("p11_scheme22_trimethylallene", [10, 11], "literature_example", [
    ("substrate", "reactant", "1,1,3-trimethylallene", "CC=C=C(C)C", None, None),
    ("arylsulfonyl_iodide", "reagent", "ArSO2I", None, None, None),
    ("product", "product", "central-attack iodo/arylsulfonyl alkene shown in Scheme 22", None, None, None),
], conditions=[("operation", "sealed tube"), ("irradiation", "200 W")],
    outcomes=[("reported_yield", {"number": 99, "unit": "%"}, ["product"])],
    notes=["Scheme 22 third arrow."],
    unresolved=["Ar is unspecified; temperature, time, solvent, and yield basis are not given."]))

R.append(record("p11_scheme23_sulfonyl_addition_mechanism", [10, 11], "mechanism", [
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("sulfonyl_radical", "unspecified_agent", "RSO2 radical", None, None, None),
    ("sulfonyl_iodide", "reagent", "RSO2I", None, None, None),
    ("products", "product", "central/terminal mono- and bis-sulfonyl products", None, None, None),
], notes=["Scheme 23 compares terminal and central sulfonyl-radical pathways and rapid delocalization."], add_missing=False))


def scheme24_record(code, substrate, reagent, product):
    return record(f"p11_scheme24_{code}", [10, 11], "literature_example", [
        ("substrate", "reactant", substrate, None, None, None),
        ("tsx", "reagent", reagent, None, [("equivalents", {"number": 1.2, "unit": "equiv"})], None),
        ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
        ("toluene", "solvent", "toluene", "Cc1ccccc1", None, None),
        ("product", "product", product, None, None, None),
    ], conditions=[("temperature", {"number": 90, "unit": "°C"}), ("time", {"number": 2, "unit": "h"})],
        outcomes=[], notes=["Scheme 24 prior-literature TsX radical addition/cyclization example."],
        unresolved=["No product yield, reagent loading for AIBN, workup, or purification is reported."])


R.extend([
    scheme24_record("octylallene", "C8H17-substituted allene shown in Scheme 24", "p-TsBr", "52"),
    scheme24_record("phenylallene", "phenylallene", "p-TsBr", "53"),
    scheme24_record("hydroxy_tethered", "hydroxy-tethered allene shown in Scheme 24", "TsI", "cyclic ether 54"),
    scheme24_record("tosylamino_tethered", "NHTs-tethered allene shown in Scheme 24", "TsBr", "cyclic sulfonamide 55"),
])

R.append(record("p11_eq9_smi2_carbonyl_allene", [11], "literature_example", [
    ("cyclopentanone", "reactant", "cyclopentanone", "O=C1CCCC1", None, None),
    ("diphenyl_allene", "reactant", "diphenyl-substituted allene shown in Eq. 9", None, None, None),
    ("smi2", "reagent", "SmI2", None, None, None),
    ("hmpa", "unspecified_agent", "HMPA", "O=P(N(C)C)(N(C)C)N(C)C", None, None),
    ("tert_butanol", "reagent", "t-BuOH", "CC(C)(C)O", None, None),
    ("thf", "solvent", "THF", "C1CCOC1", None, None),
    ("product56", "product", "56, cyclopentanol/allene coupling product", None, None, None),
], conditions=[("temperature", "r.t."), ("time", {"number": 16, "unit": "h"})], outcomes=[],
    notes=["Equation 9 is a concrete prior-literature SmI2-mediated carbonyl/allene coupling."],
    unresolved=["No yield, amounts, atmosphere, workup, or purification are provided."]))

# Pages 11-12, Schemes 25-27.
R.append(record("p12_scheme25_carbonyl_methoxyallene_mechanism", [11, 12], "mechanism", [
    ("carbonyl", "reactant", "R2C=O (aldehyde or ketone)", None, None, None),
    ("methoxyallene", "reactant", "methoxyallene", "COC=C=C", None, None),
    ("smi2", "reagent", "SmI2", None, None, None),
    ("tert_butanol", "reagent", "t-BuOH", "CC(C)(C)O", None, None),
    ("product", "product", "homoallylic alcohol/ether coupling product", None, None, None),
], notes=["Scheme 25 proposes SET to the carbonyl, radical addition to methoxyallene, and protonation."], add_missing=False))

R.append(record("p12_scheme26_allene", [11, 12], "literature_example", [
    ("n_chlorodiethylamine", "reagent", "(C2H5)2NCl", None, None, None),
    ("allene", "reactant", "allene", "C=C=C", None, None),
    ("acid_mixture", "unspecified_agent", "H2SO4-HOAc", None, None, None),
    ("product", "product", "(C2H5)2NCH2C(Cl)CH2", None, None, None),
], conditions=[("temperature", {"number": 40, "unit": "°C"})],
    outcomes=[("reported_yield", {"number": 35, "unit": "%"}, ["product"])],
    notes=["Scheme 26 first example, terminal addition."],
    unresolved=["Time, reagent amounts, acid-mixture composition, workup, purification, and yield basis are not stated."]))

R.append(record("p12_scheme26_dimethylallene", [11, 12], "literature_example", [
    ("n_chlorodiethylamine", "reagent", "(C2H5)2NCl", None, None, None),
    ("dimethylallene", "reactant", "3-methyl-1,2-butadiene", "C=C=C(C)C", None, None),
    ("acid_mixture", "unspecified_agent", "H2SO4-HOAc", None, None, None),
    ("product1", "product", "AcOCH2C(Cl)C(CH3)2 (printed condensed formula)", None, None, None),
    ("product2", "product", "(C2H5)2NCH2C(Cl)C(CH3)2 (printed condensed formula)", None, None, None),
    ("product3", "product", "(C2H5)2NCH2C(CH3)C(Cl)CH2Cl", None, None, None),
    ("product4", "product", "(C2H5)2NCH2C(Cl)C(CH3)CH2Cl", None, None, None),
], conditions=[("temperature", {"number": 30, "unit": "°C"})], outcomes=[
    ("reported_yield", {"number": 16, "unit": "%"}, ["product1"]),
    ("reported_yield", {"number": 11, "unit": "%"}, ["product2"]),
    ("reported_yield", {"number": 34, "unit": "%"}, ["product3"]),
    ("reported_yield", {"number": 17, "unit": "%"}, ["product4"]),
], notes=["Scheme 26 second example; four printed product yields are kept product-specific."],
    unresolved=["The small subscripts in the first two condensed formulas are visually difficult; their SMILES are therefore left null. Time, amounts, workup, purification, and yield bases are absent."]))

R.append(record("p12_scheme27_bu3snh_cyclization_general", [12], "general_scheme", [
    ("allene_radical_acceptor", "reactant", "allene bearing an oxime/hydrazone radical acceptor; Y = OMe or NMe2", None, None, None),
    ("tributyltin_hydride", "reagent", "Bu3SnH", None, None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ("benzene", "solvent", "PhH", "c1ccccc1", None, None),
    ("hcl_ether", "reagent", "HCl/Et2O", None, None, None),
    ("product", "product", "cyclopentene product after tin-radical cyclization and HCl treatment", None, None, None),
], notes=["Scheme 27 upper general transformation: Bu3SnH/AIBN in PhH at reflux, followed by HCl/Et2O."], add_missing=False))

R.append(record("p12_scheme27_tosyl_cyclization_mechanism", [12], "mechanism", [
    ("tethered_allene", "reactant", "allene bearing an O-benzoyl oxime radical acceptor", None, None, None),
    ("tosyl_radical", "unspecified_agent", "Ts radical", None, None, None),
    ("product", "product", "tosylated cyclic imine product", None, None, None),
], notes=["Scheme 27 middle sequence shows Ts radical addition, cyclization, resonance, and benzoyloxy-radical loss."], add_missing=False))


def scheme27_scope(code, r_value, y1, y2):
    return record(f"p12_scheme27_scope_{code}", [12], "literature_example", [
        ("substrate", "reactant", f"tethered allene/diene substrate in Scheme 27; R = {r_value}", None, None, None),
        ("tosyl_bromide", "reagent", "TsBr", None, None, None),
        ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
        ("benzene", "solvent", "C6H6", "c1ccccc1", None, None),
        ("bicyclic_product", "product", "bicyclic bromide product shown in Scheme 27", None, None, None),
        ("aromatic_product", "product", "alternative aromatic product shown in Scheme 27", None, None, None),
    ], conditions=[("temperature", "Δ")], outcomes=[
        ("reported_yield", {"number": y1, "unit": "%"}, ["bicyclic_product"]),
        ("reported_yield", {"number": y2, "unit": "%"}, ["aromatic_product"]),
    ], notes=["Scheme 27 lower substrate row."],
        unresolved=["Heating temperature, time, reagent loadings, workup, purification, and yield basis are not stated."])


R.extend([
    scheme27_scope("r_h", "H", 82, 0),
    scheme27_scope("r_ch3", "CH3", 35, 58),
    scheme27_scope("r_c6h5", "C6H5", 0, 51),
])


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")


def ids(prefixes):
    return [r["record_id"] for r in R if any(r["source_reaction_id"].startswith(p) for p in prefixes)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "页首 Scheme 13", "finding": "与第6页正文同一丙硫醇/丙二烯实验；合并为一条跨页记录，补入0.4/0.7/0.012 mol、苯、82 °C、4 h、43–46结构标签及57%/30%。", "evidence_ids": evid(7) + evid(6)},
                {"region": "中部 Scheme 14 表", "finding": "CH3S·与CH3COS·两行分别记录；保存17 °C、15 min、总收率及三组分mol%/中心进攻比例。", "evidence_ids": evid(7)},
                {"region": "下部 Scheme 15", "finding": "逐箭头记录(PhS)2复杂混合物、(PhSe)2 82%产物和(PhTe)2无反应。", "evidence_ids": evid(7)},
                {"region": "页底 Scheme 16", "finding": "PhSH与PhSeH两条底物相同但试剂/选择性不同的实例分开记录，保留37/38/25与70/8/0的产品百分数。", "evidence_ids": evid(7)},
            ],
            "record_ids": ids(["p6_ref20_propylthiol_allene", "p7_"]),
            "unresolved": ["Scheme 13未给44、45独立收率；Scheme 15–16多处缺收率测定基础、溶剂/温度/时间；复杂混合物成分未鉴定。"],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "左上 Scheme 17", "finding": "三条双组分光化学箭头分开记录，保留波长、CDCl3、40 °C、3/20/50 h、30 mol%脚注、收率和E:Z。", "evidence_ids": evid(8)},
                {"region": "左中 Scheme 18", "finding": "PhSe·/PhSSPh双组分反应机理，分类为mechanism。", "evidence_ids": evid(8)},
                {"region": "右上 Scheme 19 与 Eq. 7", "finding": "O2引发的两条PhSeH加成实例分别记录；Eq. 7为中心进攻机理。", "evidence_ids": evid(8)},
                {"region": "页底 Scheme 20 与1.9/1.10正文", "finding": "Scheme 20为二氰甲基自由基中心/末端进攻机理；其逐行结果与第9页表合并。正文同时给第9页Me3SnH表的AIBN、100 °C、9 h上下文。", "evidence_ids": evid(8)},
            ],
            "record_ids": ids(["p8_", "p9_scheme20_table_", "p9_trimethyltin_table_"]),
            "unresolved": ["Scheme 19未给时间、温度和总收率；Scheme 20第5、6行烷基链长度在原图中不能可靠唯一命名。"],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "上半页 Scheme 20结果表", "finding": "六个联烯底物行逐行记录a–d产品百分数和中心进攻比例；空白格未作0处理，≥95与≤5保留界限。", "evidence_ids": evid(9) + evid(8)},
                {"region": "中部 Eq. 8", "finding": "Me3Sn·末端进攻及氢转移链机理，分类为mechanism。", "evidence_ids": evid(9)},
                {"region": "下半页Me3SnH结果表", "finding": "五个底物行逐行记录总收率、产品百分数及E:Z；条件从第8页正文跨页关联。", "evidence_ids": evid(9) + evid(8)},
            ],
            "record_ids": ids(["p9_"]),
            "unresolved": ["上表第5、6行底物链长难以从低分辨率线式唯一判定；两表均未给完整用量、溶剂/操作或分析基础。"],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "中部Ph3SnH/Ph3GeH表", "finding": "按自由基供体和联烯底物拆成八条实例；逐个产品关联36/24、57、51/10/5、82、62/33、69/28、81、74%及表中E:Z。", "evidence_ids": evid(10)},
                {"region": "下部 Scheme 21", "finding": "t-BuOCl对二甲基联烯的攫氢/加成与氯转移网络，分类为mechanism。", "evidence_ids": evid(10)},
                {"region": "页首/右栏1.12–1.13正文", "finding": "为第11页Scheme 22–24提供RSO2·与TsX区域选择性背景；跨页合并证据，不重复建正文记录。", "evidence_ids": evid(10)},
            ],
            "record_ids": ids(["p10_", "p11_scheme22_", "p11_scheme23_", "p11_scheme24_"]),
            "unresolved": ["氢化表未给温度、时间、溶剂、用量或收率测定基础；6,7-tridecadiene一行产物式按原印刷标签保留。"],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "上部 Scheme 22", "finding": "ArSO2I对三种联烯的三条箭头分别记录；保存密封管、200 W、64/73/99%及首行80:20。", "evidence_ids": evid(11) + evid(10)},
                {"region": "中部 Scheme 23", "finding": "RSO2·中心/末端进攻及离域机理，分类为mechanism。", "evidence_ids": evid(11) + evid(10)},
                {"region": "左下 Scheme 24", "finding": "四条TsBr/TsI实例分别记录；脚注1.2 equiv进入参与物amounts，AIBN、甲苯、90 °C、2 h结构化。", "evidence_ids": evid(11) + evid(10)},
                {"region": "右下 Eq. 9及Scheme 25/26引言", "finding": "Eq. 9作为具体SmI2羰基/联烯实例记录；Scheme 25机理和Scheme 26实例与第12页图合并。", "evidence_ids": evid(11)},
            ],
            "record_ids": ids(["p11_", "p12_scheme25_", "p12_scheme26_"]),
            "unresolved": ["Ar、部分复杂底物及产物结构未完全指定；Scheme 24无收率；Eq. 9无收率和用量。"],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "页首 Scheme 25", "finding": "SmI2介导羰基化合物与甲氧基联烯的SET/自由基机理，分类为mechanism。", "evidence_ids": evid(12) + evid(11)},
                {"region": "上中 Scheme 26", "finding": "N-氯二乙胺与丙二烯、二甲基联烯两条实例分开记录；保存40/30 °C及35%、16/11/34/17%产品专属收率。", "evidence_ids": evid(12) + evid(11)},
                {"region": "下部 Scheme 27", "finding": "上方Bu3SnH/AIBN通式为general_scheme，中部Ts·环化为mechanism，下方R=H/CH3/C6H5三行按底物分别记录82/0、35/58、0/51%结果。", "evidence_ids": evid(12)},
            ],
            "record_ids": ids(["p12_"]),
            "unresolved": ["Scheme 26首两个缩合式小下标清晰度有限，未生成SMILES；Scheme 27下表未给具体温度、时间、用量和收率基础。"],
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
    if 7 <= page <= 12:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; findings and unresolved issues are recorded in coverage/pages_0007_0012.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(R), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
