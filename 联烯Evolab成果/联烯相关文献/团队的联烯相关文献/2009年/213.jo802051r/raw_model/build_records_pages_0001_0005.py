#!/usr/bin/env python3
"""Build evidence-linked machine records for jo802051r, PDF pages 1-5."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_a722ae5c33634d5f"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "Et3N": "CCN(CC)CC",
    "THF": "C1CCOC1",
    "P(OEt)2Cl": "CCOP(=O)(Cl)OCC",
    "NaOH": "[Na+].[OH-]",
    "H2O": "O",
    "MeOH": "CO",
    "DMF": "CN(C)C=O",
    "CH2Cl2": "ClCCl",
    "CH3CN": "CC#N",
    "toluene": "Cc1ccccc1",
    "EtOH": "CCO",
    "CuCl2": "[Cl-].[Cl-].[Cu+2]",
    "CuBr2": "[Br-].[Br-].[Cu+2]",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "2a": "CCCC[C](P(=O)(OCC)OCC)=C=C(C)C",
    "3a": "CCCC[C](P(=O)(O)OCC)=C=C(C)C",
    "3c": "C=CC[C](P(=O)(O)OCC)=C=C(C)C",
    "4a": "O=P1(OCC)OC(C)(C)C(Cl)=C1CCCC",
    "5a": "O=P1(OCC)OC(C)(C)C(Br)=C1CCCC",
    "6a": "O=P1(OCC)OC(C)(C)C(c2ccccc2)=C1CCCC",
}


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    structure = smiles if smiles is not None else SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(structure, evidence) if structure else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def missing_conditions():
    return [field("atmosphere", None), field("workup", None), field("purification", None)]


def record(suffix, kind, evidence, participants, conditions, outcomes, *, notes=None, unresolved=None):
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
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []


# Page 1: generic present-paper overview and a cited, generic prior-work equation.
e1 = ev(1)
records.append(record(
    "graphical_abstract_two_stage_scope", "general_scheme", e1,
    [
        participant("generic_allenyl_phosphonic_monoester", "reactant", "generic monoester of a 1,2-allenyl phosphonic acid", e1),
        participant("generic_halo_oxaphosphole", "product", "generic 4-halo-2,5-dihydro[1,2]oxaphosphole 2-oxide", e1),
        participant("generic_substituted_oxaphosphole", "product", "generic 4-substituted-2,5-dihydro[1,2]oxaphosphole 2-oxide", e1),
        participant("generic_cux2", "reagent", "CuX2 (X = Cl or Br)", e1),
        participant("dmf", "solvent", "DMF", e1),
        participant("generic_boronic_acid", "reactant", "RB(OH)2", e1),
        participant("pd_sphos", "catalyst", "PdCl2(Sphos)2", e1),
        participant("toluene", "solvent", "toluene", e1),
    ],
    [field("temperature", {"number": 60, "unit": "°C"}, e1), field("second_stage_temperature", "reflux", e1), field("time", None)] + missing_conditions(),
    [],
    notes=["Generic graphical summary with R groups and two arrows; it is not a batch-specific experiment."],
    unresolved=["Generic R groups and branch-specific quantities/times are not specified in the graphical abstract."],
))
records.append(record(
    "equation1_cited_electrophilic_cyclization", "literature_example", e1,
    [
        participant("generic_allenyl_phosphonic_acid", "reactant", "generic 1,2-allenyl phosphonic acid", e1),
        participant("generic_electrophile", "reagent", "E+ (E = H, Br, HgOAc, OH, ArSe, or RS)", e1),
        participant("generic_oxaphospholene", "product", "generic electrophile-substituted 1,2-oxaphosphol-3-ene", e1),
    ],
    [field("temperature", None), field("time", None)] + missing_conditions(), [],
    notes=["Equation 1 summarizes cited Macomber and related prior work, not a present-paper experiment."],
    unresolved=["Generic structures, quantities, conditions, and yields are not supplied on this page."],
))


# Page 2: cited prior-work sequence in equation 2.
e2 = ev(2)
records.append(record(
    "equation2_cited_halobutenolide_coupling", "literature_example", e2,
    [
        participant("generic_allenoate", "reactant", "generic 2,3-allenoic acid or ester", e2),
        participant("generic_cux2", "reagent", "CuX2 (X = Cl or Br)", e2),
        participant("generic_halobutenolide", "product", "generic beta-halobutenolide", e2),
        participant("generic_terminal_alkyne", "reactant", "R4C≡CH", e2),
        participant("pdcl2_pph3_2", "catalyst", "PdCl2(PPh3)2", e2),
        participant("cui", "catalyst", "CuI", e2),
        participant("generic_alkynyl_butenolide", "product", "generic beta-alkynylbutenolide", e2),
    ],
    [field("temperature", None), field("time", None)] + missing_conditions(), [],
    notes=["Equation 2 summarizes the authors' cited earlier halolactonization/coupling work."],
    unresolved=["No batch quantities, solvent, temperature, time, or yields are given in equation 2."],
))


# Table 1: each row has two distinct chemical operations, recorded separately.
table1 = [
    (1, "n-Bu", "Me", "Me", 72, 93, "a"),
    (2, "Bn", "Me", "Me", 51, 85, "b"),
    (3, "allyl", "Me", "Me", 98, 75, "c"),
    (4, "2-methylallyl", "Me", "Me", 81, 81, "c"),
    (5, "n-C6H13", "Et", "Et", 52, 82, "c"),
    (6, "n-Bu", "-(CH2)4-", "linked", 32, 66, "c"),
    (7, "n-Bu", "-(CH2)5-", "linked", 74, 55, "c"),
    (8, "Me", "-(CH2)5-", "linked", 80, 57, "c"),
    (9, "n-Bu", "Me", "Et", 96, 85, "c"),
    (10, "n-Bu", "H", "n-Pr", 78, 42, "c,d"),
    (11, "allyl", "H", "H", 73, 64, "b"),
    (12, "Me", "H", "H", 62, 69, "b"),
    (13, "n-Bu", "H", "H", 63, 99, "b"),
    (14, "H", "Me", "Me", 66, 99, "b"),
]


for entry, r1, r2, r3, y2, y3, foot in table1:
    label1, label2, label3 = f"1{chr(96+entry)}", f"2{chr(96+entry)}", f"3{chr(96+entry)}"
    rid_a = f"table1_entry{entry}_prepare_{label2}"
    evidence_a = e2 + (ev(4) if entry == 1 else [])
    pa = [
        participant("substrate", "reactant", label1, evidence_a),
        participant("product", "product", label2, evidence_a),
        participant("pcl_oet2", "reagent", "P(OEt)2Cl", evidence_a),
        participant("et3n", "reagent", "Et3N", evidence_a),
        participant("thf", "solvent", "THF", evidence_a),
    ]
    ca = [
        field("temperature_start", {"number": 0, "unit": "°C"}, e2),
        field("temperature_end", "reflux", e2),
        field("time", "overnight", e2),
        field("atmosphere", None), field("workup", None), field("purification", None),
    ]
    na = [f"Table 1 substituents: R1={r1}, R2={r2}, R3={r3}."]
    ua = ["Atmosphere is not stated."]
    if entry == 1:
        pa[0]["amounts"] += [field("mass", {"number": 4.255, "unit": "g"}, ev(4)), field("amount", {"number": 30.4, "unit": "mmol"}, ev(4))]
        pa[2]["amounts"] += [field("mass", {"number": 7.117, "unit": "g"}, ev(4)), field("amount", {"number": 45.5, "unit": "mmol"}, ev(4)), field("volume", {"number": 50, "unit": "mL"}, ev(4))]
        pa[3]["amounts"] += [field("volume", {"number": 6, "unit": "mL"}, ev(4)), field("mass", {"number": 4.32, "unit": "g"}, ev(4)), field("amount", {"number": 42.9, "unit": "mmol"}, ev(4))]
        pa[4]["amounts"] += [field("volume", {"number": 110, "unit": "mL"}, ev(4)), field("additional_volume", {"number": 50, "unit": "mL"}, ev(4))]
        ca = [
            field("addition_temperature", {"number": -78, "unit": "°C"}, ev(4)),
            field("warm_to", "r.t.", ev(4)),
            field("temperature", "reflux", ev(4)),
            field("time", None),
            field("operation", "P(OEt)2Cl solution added dropwise; conversion monitored by TLC; mixture filtered and solvent evaporated", ev(4)),
            field("atmosphere", None),
            field("workup", "filtration and solvent evaporation", ev(4)),
            field("purification", "flash chromatography on silica gel, petroleum ether/ether 1:1", ev(4)),
        ]
        na.append("The table's common 0 °C-to-reflux/overnight statement and the detailed -78 °C-to-reflux/TLC-endpoint procedure are both preserved.")
        ua.append("Table 1 and the detailed 2a procedure differ in starting temperature and duration description.")
    oa = [field("isolated_yield" if entry == 1 else "reported_yield", {"number": y2, "unit": "%"}, evidence_a, ["product"])]
    if entry == 1:
        oa += [field("product_mass", {"number": 5.699, "unit": "g"}, ev(4), ["product"]), field("yield_measurement_basis", "isolated after flash chromatography", ev(4), ["product"])]
    else:
        oa += [field("yield_measurement_basis", None, targets=["product"])]
    records.append(record(rid_a, "substrate_scope_entry", evidence_a, pa, ca, oa, notes=na, unresolved=ua))

    rid_b = f"table1_entry{entry}_hydrolysis_{label3}"
    evidence_b = e2 + (ev(4) if entry == 1 else []) + (ev(5) if entry == 3 else [])
    pb = [
        participant("substrate", "reactant", label2, evidence_b),
        participant("product", "product", label3, evidence_b),
        participant("naoh", "reagent", "NaOH", evidence_b),
    ]
    cb = []
    if foot == "a":
        pb.append(participant("water", "solvent", "H2O", evidence_b))
        cb += [field("temperature", "reflux", e2), field("time", "overnight", e2)]
    elif "b" in foot:
        pb.append(participant("water", "solvent", "H2O", evidence_b))
        cb += [field("temperature", {"number": 80, "unit": "°C"}, e2), field("time", "overnight", e2)]
    else:
        pb += [participant("water", "solvent", "H2O", evidence_b), participant("methanol", "solvent", "MeOH", evidence_b)]
        cb += [field("solvent_ratio", "H2O/MeOH 1:1", e2), field("temperature", "reflux", e2), field("time", None)]
    cb += missing_conditions()
    nb = [f"Table 1 substituents: R1={r1}, R2={r2}, R3={r3}; hydrolysis footnote={foot}."]
    ub = ["Atmosphere is not stated."]
    ob = [field("reported_yield", {"number": y3, "unit": "%"}, evidence_b, ["product"]), field("yield_measurement_basis", None, targets=["product"])]
    if entry == 10:
        ob.append(field("recovered_starting_material_yield", {"number": 55, "unit": "%"}, e2, ["substrate"]))
    if entry == 1:
        pb[0]["amounts"] += [field("mass", {"number": 12.566, "unit": "g"}, ev(4)), field("amount", {"number": 47.2, "unit": "mmol"}, ev(4))]
        pb[2]["amounts"] += [field("mass", {"number": 11.596, "unit": "g"}, ev(4)), field("amount", {"number": 289.9, "unit": "mmol"}, ev(4))]
        pb[3]["amounts"] += [field("volume", {"number": 300, "unit": "mL"}, ev(4))]
        cb = [field("temperature", "reflux", ev(4)), field("time", "overnight", ev(4)), field("atmosphere", None),
              field("workup", "ethyl acetate extraction; aqueous phase acidified with 1 N HCl and extracted with ether; water wash; Na2SO4 drying; evaporation", ev(4)),
              field("purification", "evaporation after extraction", ev(4))]
        ob = [field("isolated_yield", {"number": 93, "unit": "%"}, ev(4), ["product"]), field("product_mass", {"number": 10.227, "unit": "g"}, ev(4), ["product"]), field("yield_measurement_basis", "isolated after extraction and evaporation", ev(4), ["product"])]
    if entry == 3:
        pb[0]["amounts"] += [field("mass", {"number": 9.318, "unit": "g"}, ev(5)), field("amount", {"number": 38.8, "unit": "mmol"}, ev(5))]
        pb[2]["amounts"] += [field("mass", {"number": 9.644, "unit": "g"}, ev(5)), field("amount", {"number": 241.1, "unit": "mmol"}, ev(5))]
        pb[3]["amounts"] += [field("volume", {"number": 240, "unit": "mL"}, ev(5))]
        pb[4]["amounts"] += [field("volume", {"number": 240, "unit": "mL"}, ev(5))]
        cb = [field("solvent_ratio", "H2O/MeOH 1:1", e2), field("temperature", "reflux", ev(5)), field("time", {"number": 3, "unit": "d"}, ev(5)), field("atmosphere", None),
              field("workup", "ethyl acetate extraction; acidification with 1 N HCl; ether extraction; water wash; Na2SO4 drying; evaporation; repeat ether dilution/water wash/drying/evaporation", ev(5)),
              field("purification", "evaporation after repeated extraction/washing", ev(5))]
        ob = [field("isolated_yield", {"number": 75, "unit": "%"}, ev(5), ["product"]), field("product_mass", {"number": 6.284, "unit": "g"}, ev(5), ["product"]), field("yield_measurement_basis", "isolated and used directly for cyclization", ev(5), ["product"])]
        nb.append("The detailed 3c batch states 3 days; Table 1 footnote c gives reflux but no duration.")
    records.append(record(rid_b, "substrate_scope_entry", evidence_b, pb, cb, ob, notes=nb, unresolved=ub))


# Table 2: CuCl2 optimization. Entry 5 is the same experiment as Table 3 entry 1 and the detailed 4a batch.
table2 = [
    (1, 2, "DMF", 80, 48), (2, 3, "DMF", 80, 66), (3, 4, "DMF", 80, 75),
    (4, 5, "DMF", 80, 75), (5, 4, "DMF", 60, 88), (6, 4, "DMF", 100, 41),
    (7, 4, "DMF", 40, 81), (8, 4, "CH2Cl2", "reflux", 70),
    (9, 4, "THF", 60, 76), (10, 4, "CH3CN", 60, 69), (11, 4, "toluene", 60, 77),
]


for entry, cu_eq, solvent, temp, yld in table2:
    suffix = f"table2_entry{entry}_chlorocyclization_4a"
    evidence = e2
    if entry == 5:
        suffix = "table2_entry5_table3_entry1_chlorocyclization_4a"
        evidence = e2 + ev(3) + ev(5)
    ps = [participant("substrate", "reactant", "3a", evidence), participant("product", "product", "4a", evidence),
          participant("cucl2", "reagent", "CuCl2", evidence, amounts=[field("equivalents", {"number": cu_eq, "unit": "equiv"}, e2)]),
          participant("solvent", "solvent", solvent, evidence)]
    cs = [field("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}, e2), field("time", {"number": 12, "unit": "h"}, e2)] + missing_conditions()
    os = [field("reported_yield", {"number": yld, "unit": "%"}, e2, ["product"]), field("yield_measurement_basis", None, targets=["product"])]
    notes = []
    unresolved = ["Atmosphere is not stated."]
    if entry == 5:
        ps[0]["amounts"] += [field("mass", {"number": 69, "unit": "mg"}, ev(5)), field("amount", {"number": 0.30, "unit": "mmol"}, ev(5))]
        ps[2]["amounts"] += [field("mass", {"number": 162, "unit": "mg"}, ev(5)), field("amount", {"number": 1.2, "unit": "mmol"}, ev(5))]
        ps[3]["amounts"] += [field("volume", {"number": 2, "unit": "mL"}, ev(5))]
        cs = [field("temperature", {"number": 60, "unit": "°C"}, ev(3)+ev(5)), field("time", {"number": 12, "unit": "h"}, ev(3)+ev(5)), field("atmosphere", None),
              field("workup", "ether addition; three brine washes; Na2SO4 drying; evaporation", ev(5)),
              field("purification", "silica-gel column chromatography, petroleum ether/ether acetate 3:1", ev(5))]
        os = [field("isolated_yield", {"number": 88, "unit": "%"}, evidence, ["product"]), field("product_mass", {"number": 70, "unit": "mg"}, ev(5), ["product"]), field("yield_measurement_basis", "isolated after column chromatography", ev(5), ["product"])]
        notes.append("Table 2 entry 5, Table 3 entry 1, and typical procedure IV describe the same 3a/CuCl2/DMF/60 °C/12 h experiment and are merged.")
    records.append(record(suffix, "optimization_entry", evidence, ps, cs, os, notes=notes, unresolved=unresolved))


# Page 3 Table 3: scope. Entry 1 is already represented by Table 2 entry 5.
e3 = ev(3)
table3 = [
    (1,"3a","n-Bu","Me","Me","Cl",[88],"4a"), (2,"3a","n-Bu","Me","Me","Br",[84],"5a"),
    (3,"3b","Bn","Me","Me","Cl",[68],"4b"), (4,"3b","Bn","Me","Me","Br",[69],"5b"),
    (5,"3c","allyl","Me","Me","Cl",[77],"4c"), (6,"3c","allyl","Me","Me","Br",[82],"5c"),
    (7,"3d","2-methylallyl","Me","Me","Cl",[82],"4d"), (8,"3d","2-methylallyl","Me","Me","Br",[66],"5d"),
    (9,"3e","n-C6H13","Et","Et","Cl",[83],"4e"), (10,"3e","n-C6H13","Et","Et","Br",[80],"5e"),
    (11,"3f","n-Bu","-(CH2)4-","linked","Cl",[73],"4f"), (12,"3f","n-Bu","-(CH2)4-","linked","Br",[73],"5f"),
    (13,"3g","n-Bu","-(CH2)5-","linked","Cl",[84],"4g"), (14,"3g","n-Bu","-(CH2)5-","linked","Br",[76],"5g"),
    (15,"3h","Me","-(CH2)5-","linked","Cl",[73],"4h"), (16,"3h","Me","-(CH2)5-","linked","Br",[94],"5h"),
    (17,"3i","n-Bu","Me","Et","Cl",[38,23],"4i"), (18,"3i","n-Bu","Me","Et","Br",[36,26],"5i"),
    (19,"3j","n-Bu","n-Pr","H","Cl",[17,12],"4j"), (20,"3j","n-Bu","n-Pr","H","Br",[15,20],"5j"),
]


for entry, sub, r1, r2, r3, hal, yields, prod in table3:
    if entry == 1:
        continue
    evidence = e3 + (ev(5) if entry == 2 else [])
    reagent = "CuCl2" if hal == "Cl" else "CuBr2"
    ps = [participant("substrate", "reactant", sub, evidence)]
    targets = []
    if len(yields) == 1:
        ps.append(participant("product", "product", prod, evidence)); targets = ["product"]
    else:
        ps += [participant("product_d1", "product", f"{prod} diastereoisomer 1", evidence), participant("product_d2", "product", f"{prod} diastereoisomer 2", evidence)]
        targets = ["product_d1", "product_d2"]
    ps += [participant("cux2", "reagent", reagent, evidence, amounts=[field("equivalents", {"number": 4, "unit": "equiv"}, e3)]), participant("dmf", "solvent", "DMF", evidence)]
    cs = [field("temperature", {"number": 60, "unit": "°C"}, e3), field("time", {"number": 12, "unit": "h"}, e3)] + missing_conditions()
    os = []
    for i, yld in enumerate(yields):
        os.append(field("reported_yield" if len(yields)==1 else f"diastereoisomer_{i+1}_isolated_yield", {"number": yld, "unit": "%"}, e3, [targets[i] if len(yields)>1 else targets[0]]))
    os.append(field("yield_measurement_basis", "two diastereoisomers isolated" if len(yields)>1 else None, e3 if len(yields)>1 else None, targets if len(yields)>1 else ["product"]))
    notes = [f"Table 3 substituents: R1={r1}, R2={r2}, R3={r3}; X={hal}."]
    unresolved = ["Atmosphere is not stated."]
    if entry == 2:
        ps[0]["amounts"] += [field("mass", {"number": 71, "unit": "mg"}, ev(5)), field("amount", {"number": 0.31, "unit": "mmol"}, ev(5))]
        ps[-2]["amounts"] += [field("mass", {"number": 269, "unit": "mg"}, ev(5)), field("amount", {"number": 1.2, "unit": "mmol"}, ev(5))]
        ps[-1]["amounts"] += [field("volume", {"number": 2, "unit": "mL"}, ev(5))]
        cs = [field("temperature", {"number": 60, "unit": "°C"}, evidence), field("time", {"number": 12, "unit": "h"}, evidence), field("atmosphere", None),
              field("workup", "ether addition; three brine washes; Na2SO4 drying; evaporation", ev(5)),
              field("purification", "silica-gel column chromatography, petroleum ether/ether acetate 3:1", ev(5))]
        os = [field("isolated_yield", {"number": 84, "unit": "%"}, evidence, ["product"]), field("product_mass", {"number": 80, "unit": "mg"}, ev(5), ["product"]), field("yield_measurement_basis", "isolated after column chromatography", ev(5), ["product"])]
    records.append(record(f"table3_entry{entry}_{prod}", "substrate_scope_entry", evidence, ps, cs, os, notes=notes, unresolved=unresolved))


# Four present-paper negative substrate results stated below Table 3.
for sub, desc in [("3k","1-monosubstituted; R1=allyl, R2=H, R3=H"), ("3l","1-monosubstituted; R1=Me, R2=H, R3=H"), ("3m","1-monosubstituted; R1=n-Bu, R2=H, R3=H"), ("3n","3,3-disubstituted; R1=H, R2=Me, R3=Me")]:
    records.append(record(
        f"table3_no_reaction_{sub}", "substrate_scope_entry", e3,
        [participant("substrate", "reactant", sub, e3), participant("cux2", "unspecified_agent", "CuX2", e3), participant("dmf", "solvent", "DMF", e3)],
        [field("temperature", {"number": 60, "unit": "°C"}, e3), field("time", {"number": 12, "unit": "h"}, e3)] + missing_conditions(),
        [field("reaction_result", "no reaction observed", e3)],
        notes=[desc, "The prose reports no reaction with these substrates and refers generically to CuX2."],
        unresolved=["The source does not resolve the no-reaction statement into separate CuCl2 and CuBr2 trials; CuX2 role is left unspecified."],
    ))


# Scheme 1 mechanism.
records.append(record(
    "scheme1_proposed_halolactonization_mechanism", "mechanism", e3,
    [participant("generic_substrate_3", "reactant", "generic monoethyl 1,2-allenyl phosphonic acid 3", e3), participant("cux2", "reagent", "CuX2", e3),
     participant("m1", "unspecified_agent", "proposed organocopper intermediate M1", e3), participant("m2", "unspecified_agent", "proposed five-membered intermediate M2", e3),
     participant("generic_product", "product", "4 or 5", e3), participant("cux", "product", "CuX", e3)],
    [field("operation", "proposed oxy-metalation followed by C-X bond formation with another CuX2 molecule", e3), field("temperature", None), field("time", None)] + missing_conditions(),
    [], notes=["Scheme 1 is explicitly described as a plausible mechanism."],
    unresolved=["The organocopper intermediates and generic R groups are proposed and not independently verified."],
))


# Scheme 2 has two distinct condition lines.
for suffix, bor_eq, hours, yld in [("low_boronic_acid",1.5,24,53), ("higher_boronic_acid",2.5,10,89)]:
    records.append(record(
        f"scheme2_4a_to_6a_{suffix}", "reported_experiment", e3,
        [participant("substrate", "reactant", "4a", e3), participant("product", "product", "6a", e3),
         participant("boronic_acid", "reactant", "phenylboronic acid", e3, amounts=[field("equivalents", {"number": bor_eq, "unit": "equiv"}, e3)]),
         participant("catalyst", "catalyst", "PdCl2(Sphos)2", e3, amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, e3)]),
         participant("base", "reagent", "K3PO4·3H2O", e3, amounts=[field("equivalents", {"number": 2, "unit": "equiv"}, e3)]),
         participant("solvent", "solvent", "toluene", e3)],
        [field("temperature", "reflux", e3), field("time", {"number": hours, "unit": "h"}, e3)] + missing_conditions(),
        [field("reported_yield", {"number": yld, "unit": "%"}, e3, ["product"]), field("yield_measurement_basis", None, targets=["product"])],
        unresolved=["Reaction scale, atmosphere, workup, purification, and yield basis are not stated in Scheme 2."],
    ))


# Page 4 Table 4 optimization.
e4 = ev(4)
table4 = [
    (1,"Pd(PPh3)4",3,"Na2CO3",2,"toluene/EtOH 4:1","reflux",22,5),
    (2,"Pd(PPh3)4",3,"K3PO4·3H2O",2,"toluene",100,8,34),
    (3,"Pd(PPh3)4",3,"K3PO4·3H2O",1,"toluene",100,24,29),
    (4,"PdCl2(PPh3)2",3,"K3PO4·3H2O",2,"toluene",100,24,24),
    (5,"PdCl2(PhCN)2",3,"K3PO4·3H2O",2,"toluene",100,24,"trace"),
    (6,"PdCl2(Sphos)2",3,"K3PO4·3H2O",2,"toluene",100,2,84),
    (7,"PdCl2(Sphos)2",3,"K3PO4·3H2O",2,"toluene","reflux",1,89),
    (8,"PdCl2(Sphos)2",5,"K3PO4·3H2O",2,"toluene","reflux",1,96),
]


for entry, catalyst, loading, base, baseeq, solvent, temp, hours, yld in table4:
    evidence = e4 + (ev(5) if entry == 8 else [])
    ps = [participant("substrate", "reactant", "5a", evidence), participant("product", "product", "6a", evidence),
          participant("boronic_acid", "reactant", "phenylboronic acid", evidence, amounts=[field("equivalents", {"number": 1.5, "unit": "equiv"}, e4)]),
          participant("catalyst", "catalyst", catalyst, evidence, amounts=[field("catalyst_loading", {"number": loading, "unit": "mol%"}, e4)]),
          participant("base", "reagent", base, evidence, amounts=[field("equivalents", {"number": baseeq, "unit": "equiv"}, e4)]),
          participant("solvent", "solvent", solvent, evidence)]
    if entry == 1:
        ps[4]["amounts"].append(field("concentration", {"number": 2, "unit": "M"}, e4))
        ps.append(participant("side_product", "product", "7a cycloisomerization product", e4))
    cs = [field("temperature", temp if isinstance(temp,str) else {"number": temp,"unit":"°C"}, e4), field("time", {"number":hours,"unit":"h"}, e4)] + missing_conditions()
    os = [field("reported_yield", yld if isinstance(yld,str) else {"number":yld,"unit":"%"}, e4, ["product"]), field("yield_measurement_basis", None, targets=["product"])]
    if entry == 1:
        os.append(field("side_product_isolated_yield", {"number":9,"unit":"%"}, e4, ["side_product"]))
    notes=[]; unresolved=["Atmosphere is not stated."]
    if entry == 8:
        ps[0]["amounts"] += [field("mass", {"number":95,"unit":"mg"}, ev(5)), field("amount", {"number":0.31,"unit":"mmol"}, ev(5))]
        ps[2]["amounts"] += [field("mass", {"number":54,"unit":"mg"}, ev(5)), field("amount", {"number":0.45,"unit":"mmol"}, ev(5))]
        ps[3]["amounts"] += [field("mass", {"number":15,"unit":"mg"}, ev(5))]
        ps[4]["amounts"] += [field("mass", {"number":160,"unit":"mg"}, ev(5)), field("amount", {"number":0.60,"unit":"mmol"}, ev(5))]
        ps[5]["amounts"] += [field("volume", {"number":2,"unit":"mL"}, ev(5))]
        cs = [field("temperature","reflux", evidence), field("time", {"number":1,"unit":"h"}, e4), field("operation","completion monitored by TLC", ev(5)), field("atmosphere",None),
              field("workup","ether addition; three brine washes; Na2SO4 drying; evaporation", ev(5)),
              field("purification","silica-gel column chromatography, petroleum ether/ether acetate 3:2", ev(5))]
        os = [field("isolated_yield", {"number":96,"unit":"%"}, evidence,["product"]), field("product_mass", {"number":90,"unit":"mg"}, ev(5),["product"]), field("yield_measurement_basis","isolated after column chromatography",ev(5),["product"])]
        notes.append("Typical procedure VI is merged into Table 4 entry 8.")
    records.append(record(f"table4_entry{entry}_5a_to_6a", "optimization_entry", evidence, ps, cs, os, notes=notes, unresolved=unresolved))


# Table 5 substrate scope with phenylboronic acid.
table5 = [
    (1,"5b","Bn","Me","Me","Br",1.5,4,96,"6b"), (2,"5c","allyl","Me","Me","Br",1.5,7,80,"6c"),
    (3,"5e","n-C6H13","Et","Et","Br",1.5,1,77,"6e"), (4,"5g","n-Bu","-(CH2)5-","linked","Br",1.5,2,81,"6g"),
    (5,"5h","Me","-(CH2)5-","linked","Br",1.5,1,81,"6h"), (6,"4b","Bn","Me","Me","Cl",2.5,9,91,"6b"),
    (7,"4c","allyl","Me","Me","Cl",2.5,9,65,"6c"), (8,"4e","n-C6H13","Et","Et","Cl",2.5,9,73,"6e"),
    (9,"4f","n-Bu","-(CH2)5-","linked","Cl",2.5,1,73,"6f"), (10,"4h","Me","-(CH2)5-","linked","Cl",2.5,9,61,"6h"),
]
for entry, sub, r1, r2, r3, hal, beq, hours, yld, prod in table5:
    ps=[participant("substrate","reactant",sub,e4),participant("product","product",prod,e4),
        participant("boronic_acid","reactant","phenylboronic acid",e4,amounts=[field("equivalents",{"number":beq,"unit":"equiv"},e4)]),
        participant("catalyst","catalyst","PdCl2(Sphos)2",e4,amounts=[field("catalyst_loading",{"number":5,"unit":"mol%"},e4)]),
        participant("base","reagent","K3PO4·3H2O",e4,amounts=[field("equivalents",{"number":2,"unit":"equiv"},e4)])]
    notes=[f"Table 5 substituents: R1={r1}, R2={r2}, R3={r3}; X={hal}."]
    unresolved=["Solvent, reaction scale, atmosphere, workup, purification, and yield basis are not stated in Table 5."]
    if entry==9:
        unresolved.append("Table 5 entry 9 prints substrate 4f with a -(CH2)5- substituent pattern, whereas Table 3 assigns 4f to -(CH2)4-; the source inconsistency is not normalized.")
    records.append(record(f"table5_entry{entry}_{sub}_to_{prod}","substrate_scope_entry",e4,ps,
        [field("temperature","reflux",e4),field("time",{"number":hours,"unit":"h"},e4),field("solvent",None)]+missing_conditions(),
        [field("reported_yield",{"number":yld,"unit":"%"},e4,["product"]),field("yield_measurement_basis",None,targets=["product"])],notes=notes,unresolved=unresolved))


# Table 6 boronic-acid scope.
table6=[
    (1,"p-methylphenyl",1.5,1,91,"6o"),(2,"p-methoxyphenyl",1.5,1,71,"6p"),(3,"m-methoxyphenyl",1.5,2,66,"6q"),
    (4,"o-methoxyphenyl",1.5,2,93,"6r"),(5,"benzo[1,3]dioxol-5-yl",1.5,2,90,"6s"),(6,"m-nitrophenyl",2.5,20,69,"6t"),
    (7,"p-acetylphenyl",2.5,20,47,"6u"),(8,"cyclopropyl",2.5,64,84,"6v"),(9,"hex-1(E)-en-1-yl",2.5,48,90,"6w"),(10,"n-butyl",1.5,68,58,"6x"),
]
for entry, rgroup, beq, hours, yld, prod in table6:
    ps=[participant("substrate","reactant","5a",e4),participant("product","product",prod,e4),
        participant("boronic_acid","reactant",f"{rgroup}boronic acid",e4,amounts=[field("equivalents",{"number":beq,"unit":"equiv"},e4)]),
        participant("catalyst","catalyst","PdCl2(Sphos)2",e4,amounts=[field("catalyst_loading",{"number":5,"unit":"mol%"},e4)]),
        participant("base","reagent","K3PO4·3H2O",e4,amounts=[field("equivalents",{"number":2,"unit":"equiv"},e4)]),participant("solvent","solvent","toluene",e4)]
    records.append(record(f"table6_entry{entry}_5a_to_{prod}","substrate_scope_entry",e4,ps,
        [field("temperature","reflux",e4),field("time",{"number":hours,"unit":"h"},e4)]+missing_conditions(),
        [field("reported_yield",{"number":yld,"unit":"%"},e4,["product"]),field("yield_measurement_basis",None,targets=["product"])],
        notes=[f"Table 6 boronic-acid R group: {rgroup}."],unresolved=["Reaction scale, atmosphere, workup, purification, and yield basis are not stated in Table 6."]))


# Coverage ledger. All page image evidence was inspected at original detail.
ids = {r["source_reaction_id"]: r["record_id"] for r in records}
page1_ids = [ids["graphical_abstract_two_stage_scope"], ids["equation1_cited_electrophilic_cyclization"]]
page2_ids = [ids["equation2_cited_halobutenolide_coupling"]]
for entry, *_ in table1:
    page2_ids += [ids[f"table1_entry{entry}_prepare_2{chr(96+entry)}"], ids[f"table1_entry{entry}_hydrolysis_3{chr(96+entry)}"]]
for entry, *_ in table2:
    key = "table2_entry5_table3_entry1_chlorocyclization_4a" if entry == 5 else f"table2_entry{entry}_chlorocyclization_4a"
    page2_ids.append(ids[key])
page3_ids = [ids["table2_entry5_table3_entry1_chlorocyclization_4a"]]
page3_ids += [ids[f"table3_entry{x[0]}_{x[-1]}"] for x in table3 if x[0] != 1]
page3_ids += [ids[f"table3_no_reaction_{x}"] for x in ("3k","3l","3m","3n")]
page3_ids += [ids["scheme1_proposed_halolactonization_mechanism"], ids["scheme2_4a_to_6a_low_boronic_acid"], ids["scheme2_4a_to_6a_higher_boronic_acid"]]
page4_ids = [ids[f"table4_entry{x[0]}_5a_to_6a"] for x in table4]
page4_ids += [ids[f"table5_entry{x[0]}_{x[1]}_to_{x[-1]}"] for x in table5]
page4_ids += [ids[f"table6_entry{x[0]}_5a_to_{x[-1]}"] for x in table6]
page4_ids += [ids["table1_entry1_prepare_2a"], ids["table1_entry1_hydrolysis_3a"]]
page5_ids = [ids["table1_entry3_hydrolysis_3c"], ids["table2_entry5_table3_entry1_chlorocyclization_4a"], ids["table3_entry2_5a"], ids["table4_entry8_5a_to_6a"]]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page":1,"state":"attempted","regions":[
            {"region":"title/graphical abstract and abstract, center","finding":"Generic two-stage present-paper scope (CuX2 halolactonization then Suzuki coupling); classified as a general scheme, not a batch experiment.","evidence_ids":ev(1)},
            {"region":"introduction and equation 1, lower right","finding":"Generic electrophilic cyclization is explicitly attributed to cited prior work and classified as a literature example.","evidence_ids":ev(1)}],
         "record_ids":page1_ids,"unresolved":["Generic R groups and missing batch conditions prevent molecule-complete experiment records on page 1."]},
        {"page":2,"state":"attempted","regions":[
            {"region":"Table 1 and footnotes, upper half","finding":"Fourteen rows were split into 28 operation-level records: preparation of phosphonate 2 and hydrolysis to monoester 3; row-specific yields and footnote solvents/temperatures were applied.","evidence_ids":ev(2)},
            {"region":"equation 2 and surrounding prior-work prose, middle left","finding":"Generic halobutenolide/coupling sequence is cited prior work and classified as a literature example.","evidence_ids":ev(2)},
            {"region":"Table 2 and discussion, middle/right","finding":"Eleven independent CuCl2 optimization entries extracted; entry 5 is linked across Table 3 and the detailed page-5 procedure rather than duplicated.","evidence_ids":ev(2)}],
         "record_ids":page2_ids,"unresolved":["Most Table 1 rows and Table 2 rows omit atmosphere, detailed workup/purification, and explicit yield basis.","Table 1 common 0 °C-to-reflux/overnight statement conflicts in detail with the page-4 2a procedure's -78 °C addition and TLC endpoint."]},
        {"page":3,"state":"attempted","regions":[
            {"region":"Table 3 and footnote, upper left","finding":"Twenty halocyclization scope rows inspected; entry 1 merged with Table 2 entry 5, the other 19 retained independently, and dual yields in entries 17–20 linked to separate isolated diastereoisomers.","evidence_ids":ev(3)},
            {"region":"prose below Table 3, lower left","finding":"Four substrate-specific no-reaction results (3k–n) retained without inventing separate chloride/bromide trials.","evidence_ids":ev(3)},
            {"region":"Scheme 1, middle left","finding":"Oxy-metalation/C-X-bond pathway is explicitly proposed and classified as mechanism.","evidence_ids":ev(3)},
            {"region":"Scheme 2, lower left","finding":"Two independent 4a-to-6a coupling conditions extracted (1.5 equiv/24 h/53% and 2.5 equiv/10 h/89%).","evidence_ids":ev(3)},
            {"region":"Suzuki discussion and conclusion, right column","finding":"Narrative links Table 4–6 results; no extra duplicate experiment beyond the tables and Scheme 2.","evidence_ids":ev(3)}],
         "record_ids":page3_ids,"unresolved":["The no-reaction sentence uses generic CuX2 and does not distinguish CuCl2 from CuBr2 trials.","Most Table 3 and Scheme 2 records omit scale, atmosphere, workup, purification, and yield basis."]},
        {"page":4,"state":"attempted","regions":[
            {"region":"Table 4 and footnotes, upper half","finding":"Eight independent Suzuki optimization rows extracted; entry 1 includes both 6a (5%) and isolated cycloisomerization product 7a (9%).","evidence_ids":ev(4)},
            {"region":"Table 5, middle left","finding":"Ten phenylboronic-acid scope rows extracted with row times, yields, and footnote boronic-acid equivalents.","evidence_ids":ev(4)},
            {"region":"Table 6, middle right","finding":"Ten boronic-acid scope rows extracted with R groups, equivalents, times, and yields.","evidence_ids":ev(4)},
            {"region":"typical procedures I and II, lower half","finding":"Exact 2a and 3a batch quantities and operations merged into the corresponding Table 1 stage records.","evidence_ids":ev(4)}],
         "record_ids":page4_ids,"unresolved":["Table 5 entry 9 labels the substrate 4f while showing a -(CH2)5- pattern inconsistent with Table 3's 4f assignment.","Table 5 does not explicitly state solvent; most table rows omit atmosphere, workup, purification, scale, and yield basis."]},
        {"page":5,"state":"attempted","regions":[
            {"region":"typical procedure III for 3c, upper left","finding":"Detailed 2c hydrolysis batch merged into Table 1 entry 3 hydrolysis record, including 3-day reflux, quantities, workup, mass, and 75% yield.","evidence_ids":ev(5)},
            {"region":"typical procedures IV and V for 4a/5a, lower left to upper right","finding":"Detailed CuCl2 and CuBr2 halocyclizations merged into Table 2/Table 3 records rather than duplicated.","evidence_ids":ev(5)},
            {"region":"typical procedure VI for 6a, right column","finding":"Detailed Suzuki batch merged into Table 4 entry 8, including quantities, TLC endpoint, workup, product mass, and 96% isolated yield.","evidence_ids":ev(5)},
            {"region":"Supporting Information notice, lower right","finding":"The paper states SI availability, but no SI file was supplied or explicitly associated; association remains unestablished.","evidence_ids":ev(5)}],
         "record_ids":page5_ids,"unresolved":["Atmosphere is not stated for the detailed procedures.","Analytical characterization supports identity but is not treated as a separate reaction.","SI-only procedures and analytical data were not inferred."]},
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
    if task.get("document_id") == DOC and task.get("evidence_id", "").endswith(":text"):
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
