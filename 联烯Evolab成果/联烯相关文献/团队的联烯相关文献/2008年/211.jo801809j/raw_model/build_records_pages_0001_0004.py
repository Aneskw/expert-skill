#!/usr/bin/env python3
"""Build evidence-linked machine records for jo801809j, PDF pages 1--4."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
DOC = "doc_b902e613c84b0f3d"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, raw_text=None, qualifier=None):
    item = {"number": number, "unit": unit}
    if raw_text is not None:
        item["raw_text"] = raw_text
    if qualifier is not None:
        item["qualifier"] = qualifier
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(rid, page, kind, participants, conditions, outcomes, *, evidence=None, notes=None, unresolved=None):
    evidence = list(evidence or ev(page))
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if participants or conditions else [],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


def missing_standard(evidence, *, time=False, temperature=False, atmosphere=True, workup=True, purification=True):
    fields = []
    if time:
        fields.append(fld("time", None, evidence))
    if temperature:
        fields.append(fld("temperature", None, evidence))
    if atmosphere:
        fields.append(fld("atmosphere", None, evidence))
    if workup:
        fields.append(fld("workup", None, evidence))
    if purification:
        fields.append(fld("purification", None, evidence))
    return fields


def outcome_yield(value, evidence, product_id, basis):
    return [
        fld(f"{basis}_yield", qty(value, "%"), evidence, [product_id]),
        fld("yield_measurement_basis", basis.replace("_", " "), evidence, [product_id]),
    ]


records = []

# Page 1: conceptual Scheme 1 and the distinct Fe(acac)3 experiment.
e1 = ev(1)
records.append(record(
    "scheme1_generic_organometallic_reactivity", 1, "general_scheme",
    [
        participant("generic_allenoate", "reactant", "generic 2,3-allenoate", e1, name="R-substituted 2,3-allenoate"),
        participant("generic_r4m", "reagent", "R4M", e1, name="generic main-group organometallic reagent"),
        participant("generic_12_products", "product", "generic 1,2-addition products", e1),
        participant("generic_14_products", "product", "generic 1,4-addition products", e1),
        participant("generic_migration_products", "product", "generic migrated products", e1),
    ],
    [fld("operation", "Conceptual alternatives: 1,2-addition, 1,4-addition, and carbon-carbon double-bond migration", e1)],
    [],
    notes=["Scheme 1 is a generic reactivity map with R groups, not a single completed experiment."],
    unresolved=["Generic R groups prevent complete structures; no experimental quantities or yields are assigned to Scheme 1."],
))

smiles_1a = "CCOC(=O)C(CCC)=C=Cc1ccccc1"
smiles_2a = "C=CC(O)(CC=C)C(CCC)=C=Cc1ccccc1"
records.append(record(
    "equation1_feacac3_1a_to_2a", 1, "reported_experiment",
    [
        participant("eq1_1a", "reactant", "1a", e1, name="ethyl 4-phenyl-2-(n-propyl)-2,3-butadienoate", smiles=smiles_1a),
        participant("eq1_allylmgcl", "reagent", "allyl magnesium chloride", e1, amounts=[fld("equivalents", qty(3, "equiv"), e1), fld("stock_concentration", qty(1.7, "M"), e1)]),
        participant("eq1_feacac3", "catalyst", "Fe(acac)3", e1, amounts=[fld("catalyst_loading", qty(5, "mol%"), e1)]),
        participant("eq1_toluene", "solvent", "toluene", e1, smiles="Cc1ccccc1"),
        participant("eq1_2a", "product", "2a", e1, name="4-allyl-1-phenyl-3-(n-propyl)-1,2,6-heptatrien-4-ol", smiles=smiles_2a),
    ],
    [fld("temperature", qty(-78, "°C"), e1), fld("time", qty(1.5, "h"), e1), fld("solvent", "toluene", e1)] + missing_standard(e1),
    outcome_yield(85, e1, "eq1_2a", "isolated") + [fld("1,4_addition_product", "not observed", e1, ["eq1_2a"])],
    unresolved=["Reaction scale, solvent volume, atmosphere, workup, and purification are not stated for equation 1."],
))

# Page 2, Table 1: four independent optimization experiments.
e2 = ev(2)
table1 = [
    (1, "toluene", "Cc1ccccc1", -78, 51, 86),
    (2, "toluene", "Cc1ccccc1", "r.t.", 52, 90),
    (3, "THF", "C1CCOC1", "r.t.", 33, 91),
    (4, "Et2O", "CCOCC", "r.t.", 26, 89),
]
smiles_1b = "CCOC(=O)C(CCC)=C=Cc1ccc(Br)cc1"
smiles_2b = "C=CC(O)(CC=C)C(CCC)=C=Cc1ccc(Br)cc1"
for entry, solvent, solvent_smiles, temp, minutes, yld in table1:
    ps = [
        participant(f"t1e{entry}_1b", "reactant", "1b", e2, name="ethyl 4-(p-bromophenyl)-2-propyl-2,3-butadienoate", smiles=smiles_1b,
                    amounts=[fld("reaction_scale", qty(0.4, "mmol"), e1)] if entry == 3 else []),
        participant(f"t1e{entry}_allylmgcl", "reagent", "allyl magnesium chloride", e2,
                    amounts=[fld("equivalents", qty(3, "equiv"), e2), fld("stock_concentration", qty(1.7, "M"), e2)]),
        participant(f"t1e{entry}_solvent", "solvent", solvent, e2, smiles=solvent_smiles,
                    amounts=[fld("volume", qty(5, "mL"), e1)] if entry == 3 else []),
        participant(f"t1e{entry}_2b", "product", "2b", e2, smiles=smiles_2b),
    ]
    records.append(record(
        f"table1_entry{entry}", 2, "optimization_entry", ps,
        [fld("temperature", temp if isinstance(temp, str) else qty(temp, "°C"), e2), fld("time", qty(minutes, "min"), e2), fld("solvent", solvent, e2)] + missing_standard(e2),
        outcome_yield(yld, e2, f"t1e{entry}_2b", "NMR"),
        evidence=list(dict.fromkeys(e2 + (e1 if entry == 3 else []))),
        unresolved=["Atmosphere, workup, purification, and NMR internal standard are not stated; scale and solvent volume are explicit only for standard entry 3."],
    ))

# Page 2, Table 2: 19 independent substrate-scope rows.
scope = [
    (1, "Ph", "H", "n-Pr", "1a", "2a", 3, 94, 0.4, "CCOC(=O)C(CCC)=C=Cc1ccccc1", "4-allyl-1-phenyl-3-(n-propyl)-1,2,6-heptatrien-4-ol"),
    (2, "p-BrC6H4", "H", "n-Pr", "1b", "2b", 33, 95, 0.4, "CCOC(=O)C(CCC)=C=Cc1ccc(Br)cc1", None),
    (3, "Ph", "H", "Me", "1c", "2c", 20, 85, 0.4, "CCOC(=O)C(C)=C=Cc1ccccc1", None),
    (4, "p-ClC6H4", "H", "Me", "1d", "2d", 4, 90, 0.4, "CCOC(=O)C(C)=C=Cc1ccc(Cl)cc1", None),
    (5, "p-FC6H4", "H", "Me", "1e", "2e", 19, 88, 0.4, "CCOC(=O)C(C)=C=Cc1ccc(F)cc1", None),
    (6, "p-MeOC6H4", "H", "Me", "1f", "2f", 3, 79, 0.4, "CCOC(=O)C(C)=C=Cc1ccc(OC)cc1", None),
    (7, "Ph", "H", "Et", "1g", "2g", 4, 94, 0.4, "CCOC(=O)C(CC)=C=Cc1ccccc1", None),
    (8, "n-C4H9", "H", "Me", "1h", "2h", 4, 86, 0.4, "CCOC(=O)C(C)=C=CCCCC", None),
    (9, "n-C4H9", "H", "Bn", "1i", "2i", 8, 100, 0.4, "CCOC(=O)C(Cc1ccccc1)=C=CCCCC", "4-allyl-5-benzyl-1,5,6-undecatrien-4-ol"),
    (10, "n-C4H9", "H", "Bn", "1i", "2i", 4, 97, 2.0, "CCOC(=O)C(Cc1ccccc1)=C=CCCCC", "4-allyl-5-benzyl-1,5,6-undecatrien-4-ol"),
    (11, "Ph", "Ph", "H", "1j", "2j", 3, 83, 0.4, "CCOC(=O)C=C=C(c1ccccc1)c1ccccc1", None),
    (12, "n-C7H15", "H", "H", "1k", "2k", 6, 97, 0.4, "CCOC(=O)C=C=CCCCCCCC", None),
    (13, "Ph", "Me", "Me", "1l", "2l", 33, 97, 0.4, "CCOC(=O)C(C)=C=C(C)c1ccccc1", None),
    (14, "Ph", "Et", "Me", "1m", "2m", 3, 91, 0.4, "CCOC(=O)C(C)=C=C(CC)c1ccccc1", None),
    (15, "Ph", "Ph", "Me", "1n", "2n", 2, 90, 0.4, "CCOC(=O)C(C)=C=C(c1ccccc1)c1ccccc1", None),
    (16, "Et", "Et", "Me", "1o", "2o", 35, 60, 0.4, "CCOC(=O)C(C)=C(CC)CC", None),
    (17, "(CH2)5", "ring", "Me", "1p", "2p", 3, 94, 0.4, "CCOC(=O)C(C)=C=C1CCCCC1", None),
    (18, "H", "H", "Me", "1q", "2q", 2, 63, 2.0, "CCOC(=O)C(C)=C=C", None),
    (19, "H", "H", "H", "1r", "2r", 20, 64, 0.4, "COC(=O)C=C=C", None),
]


def double_addition_product(substrate_smiles):
    for prefix in ("CCOC(=O)", "COC(=O)"):
        if substrate_smiles.startswith(prefix):
            return "C=CC(O)(CC=C)" + substrate_smiles[len(prefix):]
    return None


for entry, r1, r2, r3, sublabel, prodlabel, minutes, yld, scale, subsmiles, prodname in scope:
    pid = f"t2e{entry}_{prodlabel}"
    sid = f"t2e{entry}_{sublabel}"
    ps = [
        participant(sid, "reactant", sublabel, e2, name=f"2,3-allenoate {sublabel}; R1={r1}, R2={r2}, R3={r3}", smiles=subsmiles,
                    amounts=[fld("reaction_scale", qty(scale, "mmol"), e2)]),
        participant(f"t2e{entry}_allylmgcl", "reagent", "allyl magnesium chloride", e2,
                    amounts=[fld("equivalents", qty(3, "equiv"), e2), fld("stock_concentration", qty(1.7, "M"), e2)]),
        participant(f"t2e{entry}_thf", "solvent", "THF", e2, smiles="C1CCOC1", amounts=[fld("volume", qty(5, "mL"), e2)]),
        participant(pid, "product", prodlabel, e2, name=prodname, smiles=double_addition_product(subsmiles)),
    ]
    evidence = list(e2)
    cond = [fld("temperature", "r.t.", e2), fld("time", qty(minutes, "min"), e2), fld("solvent", "THF", e2)]
    notes = []
    unresolved = ["The table does not state atmosphere, workup, or purification for this row; product candidate connectivity is unverified."]
    if entry == 1:
        evidence = list(dict.fromkeys(e2 + ev(3)))
        e3 = ev(3)
        ps[0]["amounts"] += [fld("mass", qty(92.5, "mg"), e3)]
        ps[1]["amounts"] += [fld("volume", qty(0.7, "mL"), e3), fld("amount", qty(1.2, "mmol"), e3)]
        ps[2]["amounts"] = [fld("volume", qty(5, "mL"), e3)]
        ps[3]["amounts"] = [fld("isolated_mass", qty(101.8, "mg"), e3)]
        cond += [
            fld("atmosphere", "nitrogen", e3),
            fld("operation", "Allyl magnesium chloride solution was added by syringe to 1a in a dry Schlenk tube at room temperature; reaction monitored by TLC.", e3),
            fld("workup", "Slow quench with saturated NH4Cl (1 mL) at room temperature; extract with ether (60 mL); wash with 1% aqueous HCl, saturated aqueous NaHCO3, and brine; dry over anhydrous Na2SO4; evaporate.", e3),
            fld("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate 100:1", e3),
        ]
        unresolved = ["Product structure and stereochemical representation remain unverified; SI was not supplied."]
    else:
        cond += missing_standard(e2)
    records.append(record(
        f"table2_entry{entry}_{prodlabel}", 2, "substrate_scope_entry", ps, cond,
        outcome_yield(yld, e2, pid, "isolated"), evidence=evidence, notes=notes, unresolved=unresolved,
    ))

# Page 2, equations 2--4.
records.append(record(
    "equation2_bis_allenoate_3_to_4", 2, "reported_experiment",
    [
        participant("eq2_3", "reactant", "3", e2, name="diethyl 2,9-dimethyl-2,3,7,8-decatetraenedioate"),
        participant("eq2_allylmgcl", "reagent", "allyl magnesium chloride", e2, amounts=[fld("equivalents", qty(6, "equiv"), e2), fld("stock_concentration", qty(1.7, "M"), e2)]),
        participant("eq2_thf", "solvent", "THF", e2, smiles="C1CCOC1"),
        participant("eq2_4", "product", "4", e2, name="tetraallyl-substituted bis-allenol 4"),
    ],
    [fld("temperature", "r.t.", e2), fld("time", qty(19, "min"), e2), fld("solvent", "THF", e2)] + missing_standard(e2),
    outcome_yield(82, e2, "eq2_4", "reported") + [fld("diastereomeric_ratio", "dr ≈ 1:1", e2, ["eq2_4"])],
    unresolved=["Yield basis, scale, atmosphere, workup, purification, and complete candidate structures are not stated or verified."],
))

smiles_1c = "CCOC(=O)C(C)=C=Cc1ccccc1"
smiles_2c = double_addition_product(smiles_1c)
records.append(record(
    "equation3_optically_active_1c_to_2c", 2, "reported_experiment",
    [
        participant("eq3_r_1c", "reactant", "R-(−)-1c", e2, name="optically active 2,3-allenoate R-(−)-1c", smiles=smiles_1c),
        participant("eq3_allylmgcl", "reagent", "allyl magnesium chloride", e2, amounts=[fld("equivalents", qty(3, "equiv"), e2), fld("stock_concentration", qty(1.7, "M"), e2)]),
        participant("eq3_thf", "solvent", "THF", e2, smiles="C1CCOC1"),
        participant("eq3_r_2c", "product", "R-(−)-2c", e2, name="optically active allenol R-(−)-2c", smiles=smiles_2c),
    ],
    [fld("temperature", "r.t.", e2), fld("time", qty(2, "min"), e2), fld("solvent", "THF", e2)] + missing_standard(e2),
    outcome_yield(90, e2, "eq3_r_2c", "isolated") + [fld("starting_material_ee", qty(98, "%"), e2, ["eq3_r_1c"]), fld("product_ee", qty(97, "%"), e2, ["eq3_r_2c"])],
    unresolved=["Scale, atmosphere, workup, purification, and absolute axial-configuration encoding are not established."],
))

records.append(record(
    "equation4_2_methylallylmagnesium_1i_to_2s", 2, "reported_experiment",
    [
        participant("eq4_1i", "reactant", "1i", e2, name="ethyl 2-benzylocta-2,3-dienoate", smiles="CCOC(=O)C(Cc1ccccc1)=C=CCCCC"),
        participant("eq4_2methylallylmgcl", "reagent", "2-methylallyl magnesium chloride", e2, amounts=[fld("equivalents", qty(3, "equiv"), e2), fld("stock_concentration", qty(0.4, "M"), e2)]),
        participant("eq4_thf", "solvent", "THF", e2, smiles="C1CCOC1"),
        participant("eq4_2s", "product", "2s", e2),
    ],
    [fld("temperature", "r.t.", e2), fld("time", qty(35, "min"), e2), fld("solvent", "THF", e2)] + missing_standard(e2),
    outcome_yield(98, e2, "eq4_2s", "reported"),
    unresolved=["Yield basis, scale, atmosphere, workup, purification, and product candidate SMILES are not stated or verified."],
))

# Page 2 prose: unsuccessful or selectivity-changing Grignard tests are distinct experiments.
alternative_grignards = [
    ("1_buten_3_yl", "1-buten-3-yl magnesium chloride", "complicated mixture", None, None),
    ("2_butenyl", "2-butenyl magnesium chloride", "complicated mixture", None, None),
    ("3_phenyl_2_propenyl", "3-phenyl-2-propenyl magnesium chloride", "complicated mixture", None, None),
    ("vinyl", "vinyl magnesium chloride", "complicated mixture", "THF", "r.t."),
    ("methyl", "methyl magnesium chloride", "related conjugated-addition product(s)", "THF", "r.t."),
    ("phenyl", "phenyl magnesium chloride", "related conjugated-addition product(s)", "THF", "r.t."),
]
for key, reagent_name, result, solvent, temperature in alternative_grignards:
    ps = [
        participant(f"alt_{key}_1i", "reactant", "1i", e2, name="ethyl 2-benzylocta-2,3-dienoate", smiles="CCOC(=O)C(Cc1ccccc1)=C=CCCCC"),
        participant(f"alt_{key}_grignard", "reagent", reagent_name, e2),
    ]
    conditions = []
    if solvent:
        ps.append(participant(f"alt_{key}_thf", "solvent", solvent, e2, smiles="C1CCOC1"))
        conditions.append(fld("solvent", solvent, e2))
    conditions += [fld("temperature", temperature, e2) if temperature else fld("temperature", None, e2)]
    conditions += missing_standard(e2, time=True, temperature=False)
    records.append(record(
        f"prose_1i_{key}_grignard", 2, "reported_experiment", ps, conditions,
        [fld("reaction_result", result, e2)],
        notes=["The authors attribute complicated mixtures for allylic Grignards to a probable regioselectivity issue."] if "complicated" in result and key not in ("vinyl",) else [],
        unresolved=["No product identity/yield, scale, duration, atmosphere, workup, or purification is reported; reagent loading and stock concentration are also unstated for this specific test."],
    ))

# Pages 3--4, Scheme 2 and matching detailed procedures.
e3 = ev(3)
e4 = ev(4)
smiles_2i = double_addition_product("CCOC(=O)C(Cc1ccccc1)=C=CCCCC")

records.append(record(
    "scheme2_iodocyclization_2i_to_5", 3, "reported_experiment",
    [
        participant("s2_5_2i", "reactant", "2i", e3, name="4-allyl-5-benzyl-1,5,6-undecatrien-4-ol", smiles=smiles_2i,
                    amounts=[fld("mass", qty(58.9, "mg"), e3), fld("amount", qty(0.2, "mmol"), e3)]),
        participant("s2_5_i2", "reagent", "I2", e3, smiles="II", amounts=[fld("mass", qty(131.0, "mg"), e3), fld("amount", qty(0.5, "mmol"), e3), fld("equivalents", qty(2.5, "equiv"), e3)]),
        participant("s2_5_meCN", "solvent", "CH3CN", e3, smiles="CC#N", amounts=[fld("volume", qty(2, "mL"), e3)]),
        participant("s2_5_water", "solvent", "H2O", e3, smiles="O", amounts=[fld("volume", qty(0.13, "mL"), e3)]),
        participant("s2_5_product", "product", "5", e3, name="2,2-diallyl-3-benzyl-5-butyl-4-iodo-2,5-dihydrofuran", amounts=[fld("isolated_mass", qty(74.4, "mg"), e3)]),
    ],
    [
        fld("temperature", "r.t.", e3), fld("time", qty(2, "h"), e3), fld("solvent", "CH3CN/H2O (15:1)", e3), fld("atmosphere", None, e3),
        fld("operation", "Stirred at room temperature and monitored by TLC.", e3),
        fld("workup", "Quenched with saturated aqueous Na2S2O3; extracted with ether (3 × 25 mL); washed with aqueous NaCl; dried over Na2SO4; concentrated.", e3),
        fld("purification", "Silica-gel chromatography: petroleum ether, then petroleum ether/ethyl acetate 40:1", e3),
    ],
    outcome_yield(89, e3, "s2_5_product", "isolated"),
    unresolved=["Atmosphere and product candidate SMILES are not established; the paper cites earlier cyclization methodology but reports this batch here."],
))

records.append(record(
    "scheme2_palladium_allylation_2i_to_6", 3, "reported_experiment",
    [
        participant("s2_6_2i", "reactant", "2i", e3, name="4-allyl-5-benzyl-1,5,6-undecatrien-4-ol", smiles=smiles_2i,
                    amounts=[fld("mass", qty(89.0, "mg"), e3), fld("amount", qty(0.3, "mmol"), e3)]),
        participant("s2_6_allylbr", "reagent", "allyl bromide", e3, smiles="C=CCBr", amounts=[fld("mass", qty(188.0, "mg"), e3), fld("amount", qty(1.5, "mmol"), e3), fld("equivalents", qty(5, "equiv"), e3)]),
        participant("s2_6_pdcl2", "catalyst", "PdCl2", e3, smiles="[Cl-].[Cl-].[Pd+2]", amounts=[fld("mass", qty(3.0, "mg"), e3), fld("amount", qty(0.015, "mmol"), e3), fld("catalyst_loading", qty(5, "mol%"), e3)]),
        participant("s2_6_dma", "solvent", "DMA", e3, name="N,N-dimethylacetamide", smiles="CC(=O)N(C)C", amounts=[fld("volume", qty(1, "mL"), e3)]),
        participant("s2_6_product", "product", "6", e3, name="2,2,4-triallyl-3-benzyl-5-butyl-2,5-dihydrofuran", amounts=[fld("isolated_mass", qty(76.8, "mg"), e3)]),
    ],
    [
        fld("temperature", "r.t.", e3), fld("time", qty(48, "h"), e3), fld("solvent", "DMA", e3), fld("atmosphere", None, e3),
        fld("operation", "Stirred at room temperature; completion monitored by TLC.", e3),
        fld("workup", "Added ether (60 mL); washed with 1% aqueous HCl, saturated aqueous NaHCO3, and brine; dried over anhydrous Na2SO4; evaporated.", e3),
        fld("purification", "Silica-gel chromatography: petroleum ether, then petroleum ether/ethyl acetate 100:1", e3),
    ],
    outcome_yield(76, e3, "s2_6_product", "isolated"),
    unresolved=["Atmosphere and product candidate SMILES are not established."],
))

records.append(record(
    "scheme2_silver_cyclization_2i_to_7", 3, "reported_experiment",
    [
        participant("s2_7_2i", "reactant", "2i", e3, name="4-allyl-5-benzyl-1,5,6-undecatrien-4-ol", smiles=smiles_2i,
                    amounts=[fld("mass", qty(58.9, "mg"), e3), fld("amount", qty(0.2, "mmol"), e3)]),
        participant("s2_7_agno3", "catalyst", "AgNO3", e3, smiles="[Ag+].[O-][N+](=O)[O-]", amounts=[fld("mass", qty(6.9, "mg"), e3), fld("amount", qty(0.04, "mmol"), e3), fld("catalyst_loading", qty(20, "mol%"), e3)]),
        participant("s2_7_ch2cl2", "solvent", "CH2Cl2", e3, smiles="ClCCl", amounts=[fld("volume", qty(2, "mL"), e3)]),
        participant("s2_7_product", "product", "7", e3, name="2,2-diallyl-3-benzyl-5-butyl-2,5-dihydrofuran", amounts=[fld("isolated_mass", qty(58.5, "mg"), e3)]),
    ],
    [
        fld("temperature", "r.t.", e3), fld("time", qty(11, "h"), e3), fld("solvent", "CH2Cl2", e3), fld("atmosphere", None, e3),
        fld("operation", "Stirred at room temperature; completion monitored by TLC.", e3),
        fld("workup", "Ether (10 mL) was added to quench; mixture was concentrated.", e3),
        fld("purification", "Silica-gel chromatography: petroleum ether, then petroleum ether/ethyl acetate 100:1", e3),
    ],
    outcome_yield(99, e3, "s2_7_product", "isolated"),
    evidence=list(dict.fromkeys(e3 + e4)),
    unresolved=["Atmosphere and product candidate SMILES are not established; characterization continues onto page 4."],
))

records.append(record(
    "scheme2_rcm_7_to_8", 4, "reported_experiment",
    [
        participant("s2_8_7", "reactant", "7", e4, name="2,2-diallyl-3-benzyl-5-butyl-2,5-dihydrofuran", amounts=[fld("mass", qty(41.8, "mg"), e4), fld("amount", qty(0.2, "mmol"), e4)]),
        participant("s2_8_grubbs2", "catalyst", "Grubbs II catalyst", e4, amounts=[fld("mass", qty(9.2, "mg"), e4), fld("amount", qty(0.01, "mmol"), e4), fld("catalyst_loading", qty(5, "mol%"), e4)]),
        participant("s2_8_ch2cl2", "solvent", "CH2Cl2", e4, smiles="ClCCl", amounts=[fld("volume", qty(4, "mL"), e4)]),
        participant("s2_8_product", "product", "8", e4, name="4-benzyl-2-(n-butyl)-1-oxaspiro[4.4]nona-3,7-diene", amounts=[fld("isolated_mass", qty(32.5, "mg"), e4)]),
    ],
    [
        fld("temperature", "reflux", e4), fld("time", qty(2, "h"), e4), fld("solvent", "CH2Cl2", e4), fld("atmosphere", "N2", e4),
        fld("operation", "Grubbs II catalyst was added to 7 in CH2Cl2 under N2; stirred under reflux and monitored by TLC.", e4),
        fld("workup", "Resulting solution was concentrated.", e4),
        fld("purification", "Flash silica-gel chromatography, petroleum ether/Et2O 100:1", e4),
    ],
    outcome_yield(86, e4, "s2_8_product", "isolated"),
    evidence=list(dict.fromkeys(e3 + e4)),
    unresolved=["The printed 41.8 mg/0.2 mmol substrate pair is internally inconsistent with the reported product mass/yield and is preserved without correction; product and catalyst structures remain unverified."],
))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
