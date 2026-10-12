#!/usr/bin/env python3
"""Build evidence-linked machine records for jo0163997 PDF pages 1-6."""
import json
from pathlib import Path

DOC = "doc_f03c4dfd3e9143ac"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0006.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def fld(name, value, evidence, targets=None):
    x = {"name": name, "fact": fact(value, evidence)}
    if targets is not None:
        x["target_entity_ids"] = targets
    return x


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id, "role": role,
        "label": fact(label, evidence), "name": fact(name, evidence),
        "smiles": fact(smiles, evidence), "smiles_parseable": None,
        "structure_verified": False, "amounts": amounts or [],
    }


def rec(suffix, page, kind, participants=None, steps=None, outcomes=None, notes=None,
        extra_evidence=None, unresolved=None):
    evidence = ev(page) + (extra_evidence or [])
    return {
        "record_id": f"{DOC}:{suffix}", "document_id": DOC,
        "source_reaction_id": suffix, "record_kind": kind, "status": "candidate",
        "completeness": "partial", "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [], "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved or [
                       "Machine extraction requires chemical source review.",
                       "No Supporting Information file was explicitly supplied or associated.",
                   ]},
    }


def amount(name, number, unit, evidence, raw=None):
    value = {"number": number, "unit": unit}
    if raw:
        value["raw_text"] = raw
    return fld(name, value, evidence)


records = []

# Page 2, Scheme 1: cited prior Pd(0) chemistry, not experiments newly reported here.
for path, product in [("path_a", "vinylic oxirane"), ("path_b", "2,5-dihydrofuran (not observed in cited work)")]:
    e = ev(2)
    records.append(rec(f"scheme1_{path}", 2, "literature_example", [
        part("allenol_1_generic", "reactant", "generic 2,3-allenol", e),
        part("rx_generic", "reactant", "R3X (aryl or vinyl halide)", e),
        part(f"product_{path}", "product", product, e),
        part("pd0", "catalyst", "Pd(0)", e),
    ], [{"step_id": "coupling_cyclization", "participant_ids": ["allenol_1_generic", "rx_generic", "pd0"],
         "conditions": []}], notes=["Scheme 1 summarizes cited prior work (ref. 18), not a new experiment in this paper."],
        unresolved=["Generic R-group structures do not support unique SMILES."]))

# Page 3, Scheme 3: eight reported starting-material preparations.
scheme3 = [
    ("2a", "R1=CH3; R2=n-C4H9; R3=R4=H", 92, "LiAlH4"),
    ("2b", "R1=R3=R4=H; R2=n-C4H9", 75, "LiAlH4"),
    ("2c", "R1=CH3; R2=Ph; R3=R4=H", 78, "DIBAL-H"),
    ("2d", "R1=CH3; R2=t-C4H9; R3=R4=H", 70, "LiAlH4"),
    ("2e", "R1=i-C3H7; R2=n-C4H9; R3=R4=H", 34, "LiAlH4"),
    ("2f", "R1=R3=R4=CH3; R2=H", 53, "LiAlH4"),
    ("2g", "R1=R2=R4=H; R3=n-C4H9", 74, "LiAlH4"),
    ("2h", "R1=CH3; R2=R3=R4=H", 54, "LiAlH4"),
]
for label, desc, yld, reductant in scheme3:
    e = ev(3)
    ps = [
        part(f"precursor_{label}", "reactant", f"propargylic alcohol precursor of {label}", e),
        part(f"orthoester_{label}", "reagent", "excess triethyl orthoacetate or triethyl orthopropionate", e),
        part(f"propionic_acid_{label}", "catalyst", "propionic acid", e, amounts=[fld("catalyst_loading", "catalytic amount", e)]),
        part(f"reductant_{label}", "reagent", reductant, e),
        part(f"thf_{label}", "solvent", "THF", e, smiles="C1CCOC1"),
        part(f"product_{label}", "product", label, e, name=f"3,4-allenol {label} ({desc})"),
    ]
    steps = [
        {"step_id": "ortho_claisen", "participant_ids": [f"precursor_{label}", f"orthoester_{label}", f"propionic_acid_{label}"],
         "conditions": [fld("temperature", {"minimum": 140, "maximum": 145, "unit": "°C", "raw_text": "140-145 °C"}, e)]},
        {"step_id": "reduction", "participant_ids": [f"reductant_{label}", f"thf_{label}"],
         "conditions": [fld("temperature", {"minimum": 0, "maximum": 25, "unit": "°C", "raw_text": "0-25 °C"}, e)]},
    ]
    records.append(rec(f"scheme3_{label}", 3, "substrate_scope_entry", ps, steps,
                       [fld("reported_yield", {"number": yld, "unit": "%"}, e, [f"product_{label}"])],
                       notes=["Scheme 3 starting-material preparation; the orthoester identity and individual stage yields are not assigned."],
                       unresolved=["Generic precursor drawing and R-group mapping do not support unique precursor SMILES.",
                                   "Reaction time, workup, purification, and yield measurement basis are not reported in this region.",
                                   "No Supporting Information file was explicitly supplied or associated."]))


def table1_record(entry, catalyst, solvent, time_h, result, flags=()):
    e = ev(3)
    allyl_label = "allyl chloride" if "allyl_chloride" in flags else "3a"
    allyl_name = "allyl chloride" if "allyl_chloride" in flags else "allyl bromide"
    allyl_smiles = "C=CCCl" if "allyl_chloride" in flags else "C=CCBr"
    cat_loading = 1 if "cat_1" in flags else 2.5 if "cat_2.5" in flags else 5
    allyl_amounts = ([amount("equivalents", 2.5, "equiv", e)] if "allyl_2.5" in flags
                     else [amount("amount", 5, "mmol", e), amount("equivalents", 5, "equiv", e)])
    ps = [
        part("allenol_1a", "reactant", "1a", e, name="3-(n-butyl)-3,4-pentadien-2-ol", smiles="C=C=C(CCCC)C(O)C",
             amounts=[amount("amount", 1, "mmol", e)]),
        part("allylic_halide", "reactant", allyl_label, e, name=allyl_name, smiles=allyl_smiles, amounts=allyl_amounts),
        part("catalyst", "catalyst", catalyst, e, amounts=[amount("catalyst_loading", cat_loading, "mol%", e)]),
        part("solvent", "solvent", solvent, e, amounts=[amount("volume", 6, "mL", e)]),
        part("product_4a", "product", "4a", e, name="3-butyl-2-methyl-4-(2-propenyl)-2,5-dihydrofuran",
             smiles="O1C(C)C(CCCC)=C(CC=C)C1"),
    ]
    if "bases" in flags:
        ps += [
            part("k2co3", "reagent", "K2CO3", e, amounts=[amount("loading", 120, "mol%", e)]),
            part("ag2co3", "unspecified_agent", "Ag2CO3", e, amounts=[amount("loading", 5, "mol%", e)]),
        ]
    elif "k2co3" in flags:
        ps.append(part("k2co3", "reagent", "K2CO3", e, amounts=[amount("loading", 120, "mol%", e)]))
    steps = []
    ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    if "two_stage" in flags:
        steps = [
            {"step_id": "stage_1", "participant_ids": ids, "conditions": [fld("temperature", "r.t.", e), amount("time", 25, "h", e)]},
            {"step_id": "stage_2", "participant_ids": ids, "conditions": [fld("temperature", {"minimum": 50, "maximum": 60, "unit": "°C", "raw_text": "50-60 °C"}, e), amount("time", 24, "h", e)]},
        ]
    else:
        cond = [fld("temperature", "r.t.", e), amount("time", time_h, "h", e)]
        if "air_after_17" in flags:
            cond += [fld("atmosphere", "N2 for 17 h, then exposed to air", e)]
        steps = [{"step_id": "reaction", "participant_ids": ids, "conditions": cond}]
    if result == "NR":
        outs = [fld("reaction_result", "NR", e, ["product_4a"])]
    elif result == "trace":
        outs = [fld("isolated_yield", "trace", e, ["product_4a"])]
    else:
        outs = [fld("isolated_yield", {"number": result, "unit": "%"}, e, ["product_4a"])]
    outs.append(fld("yield_measurement_basis", "isolated yield based on allenol 1a", e, ["product_4a"]))
    return rec(f"table1_entry_{entry:02d}", 3, "optimization_entry", ps, steps, outs,
               notes=[f"Table 1 entry {entry}; distinct condition row."],
               unresolved=["Product structure candidate is machine-transcribed and unverified.",
                           "Workup and purification are not specified in Table 1.",
                           "No Supporting Information file was explicitly supplied or associated."])


t1 = [
    (1, "Pd(OAc)2", "MeCN", 25, "NR", ("bases", "two_stage", "allyl_2.5")),
    (2, "PdCl2", "MeCN", 46, "NR", ("bases", "allyl_2.5")),
    (3, "PdCl2(PhCN)2", "MeCN", 46, "NR", ("bases", "allyl_2.5")),
    (4, "PdCl2(MeCN)2", "THF", 1, 16, ()),
    (5, "PdCl2(MeCN)2", "DMF", 25, 69, ()),
    (6, "Pd(OAc)2", "DMF", 17, 67, ()),
    (7, "[(pi-C3H5)PdCl]2", "DMF", 49.5, 48, ()),
    (8, "PdCl2", "DMF", 14, 63, ()),
    (9, "PdCl2", "DMF", 12, 51, ("allyl_chloride",)),
    (10, "PdCl2", "CH3COOH", 11.5, 19, ()),
    (11, "PdCl2", "DMSO", 12, "trace", ()),
    (12, "PdCl2", "PhMe", 13, 27, ()),
    (13, "PdCl2", "DMA", 12, 74, ()),
    (14, "PdCl2", "DMA", 35, 65, ("cat_1",)),
    (15, "PdCl2", "DMA", 5, 60, ("k2co3",)),
    (16, "Pd2(dba)3.CHCl3", "DMA", 46, 67, ("cat_2.5",)),
    (17, "Pd(PPh3)4", "DMA", 17, "NR", ()),
    (18, "Pd(PPh3)4", "DMA", 72, 72, ("air_after_17",)),
]
records += [table1_record(*row) for row in t1]

# Page 3 prose: two lower-allyl-bromide trials and the no-halide dimerization (eq 2).
for equiv, yld in [(1, 36), (2, 54)]:
    e = ev(3)
    ps = [
        part("allenol_1a", "reactant", "1a", e),
        part("allyl_bromide_3a", "reactant", "3a", e, name="allyl bromide", smiles="C=CCBr",
             amounts=[amount("equivalents", equiv, "equiv", e)]),
        part("pdcl2", "catalyst", "PdCl2", e, amounts=[amount("catalyst_loading", 5, "mol%", e)]),
        part("dma", "solvent", "DMA", e), part("product_4a", "product", "4a", e),
        part("byproduct_5a", "product", "5a", e),
    ]
    records.append(rec(f"prose_allyl_loading_{equiv}equiv", 3, "optimization_entry", ps,
                       [{"step_id": "reaction", "participant_ids": ["allenol_1a", "allyl_bromide_3a", "pdcl2", "dma"],
                         "conditions": [fld("temperature", "r.t.", e), fld("time", None, e)]}],
                       [fld("isolated_yield", {"number": yld, "unit": "%"}, e, ["product_4a"]),
                        fld("byproduct_observation", "significant amount; not quantified", e, ["byproduct_5a"])],
                       unresolved=["Reaction time and 5a amount are not reported in this prose comparison.",
                                   "No Supporting Information file was explicitly supplied or associated."]))

e = ev(3)
records.append(rec("eq2_dimerization_1a", 3, "reported_experiment", [
    part("allenol_1a", "reactant", "1a", e),
    part("pdcl2", "catalyst", "PdCl2", e, amounts=[amount("catalyst_loading", 5, "mol%", e)]),
    part("dma", "solvent", "DMA", e), part("product_5a", "product", "5a", e),
], [{"step_id": "reaction", "participant_ids": ["allenol_1a", "pdcl2", "dma"],
     "conditions": [fld("temperature", "r.t.", e), amount("time", 24, "h", e)]}],
    [fld("isolated_yield", {"number": 11, "unit": "%"}, e, ["product_5a"])],
    notes=["Reaction conducted in the absence of allylic halide."],
    unresolved=["Exact reactant/catalyst/solvent quantities are not shown in eq 2.",
                "Product structure candidate is not encoded as SMILES.",
                "No Supporting Information file was explicitly supplied or associated."]))


def scope_record(table, entry, substrate, substituents, time_h, yld, product, page=4, recovered=None):
    e = ev(page)
    is_t2 = table == 2
    sub_amt = 1
    allyl_amt = 5
    extra = []
    if table == 2 and entry == 1:
        sub_amt, allyl_amt = 0.75, 3.80
        extra = ev(6)
    elif table == 2 and entry == 2:
        sub_amt, allyl_amt = 1.00, 5.18
        extra = ev(6)
    evidence = e + extra
    ps = [
        part("substrate", "reactant", substrate, evidence, name=f"{'2,3' if is_t2 else '3,4'}-allenol {substrate} ({substituents})",
             amounts=[amount("amount", sub_amt, "mmol", evidence)]),
        part("allyl_bromide_3a", "reactant", "3a", evidence, name="allyl bromide", smiles="C=CCBr",
             amounts=[amount("amount", allyl_amt, "mmol", evidence)]),
        part("pdcl2", "catalyst", "PdCl2", evidence, amounts=[amount("amount", 0.05, "mmol", e), amount("catalyst_loading", 5, "mol%", e)]),
        part("dma", "solvent", "DMA", evidence, amounts=[amount("volume", 6, "mL", e)]),
        part("product", "product", product, evidence),
    ]
    if table == 2 and entry == 1:
        ps[-1]["name"] = fact("3-butyl-2-methyl-4-(2-propenyl)-2,5-dihydrofuran", evidence)
        ps[-1]["smiles"] = fact("O1C(C)C(CCCC)=C(CC=C)C1", evidence)
        ps[-1]["amounts"] = [amount("mass", 0.102, "g", ev(6))]
        ps[0]["amounts"].append(amount("mass", 0.105, "g", ev(6)))
        ps[1]["amounts"].append(amount("mass", 0.460, "g", ev(6)))
    elif table == 2 and entry == 2:
        ps[-1]["name"] = fact("2,3-dimethyl-4-(2-propenyl)-2,5-dihydrofuran", evidence)
        ps[-1]["amounts"] = [amount("mass", 0.098, "g", ev(6))]
        ps[0]["amounts"].append(amount("mass", 0.098, "g", ev(6)))
        ps[1]["amounts"].append(amount("mass", 0.627, "g", ev(6)))
    outs = [fld("isolated_yield", {"number": yld, "unit": "%"}, e, ["product"]),
            fld("yield_measurement_basis", f"isolated yield based on {substrate}", e, ["product"])]
    if recovered is not None:
        outs.append(fld("starting_material_recovered", {"number": recovered, "unit": "%"}, e, ["substrate"]))
    return rec(f"table{table}_entry_{entry:02d}", page, "substrate_scope_entry", ps,
               [{"step_id": "reaction", "participant_ids": ["substrate", "allyl_bromide_3a", "pdcl2", "dma"],
                 "conditions": [fld("temperature", "r.t.", e), amount("time", time_h, "h", e)]}], outs,
               notes=[f"Table {table} entry {entry}; nominal table scale is 1 mmol substrate and 5 mmol allyl bromide."
                      + (" Specific experimental scale from page 6 supersedes the nominal scale for this record." if extra else "")],
               extra_evidence=extra,
               unresolved=["SMILES is omitted for structures encoded only by generic R-group drawings unless separately named.",
                           "Individual workup and purification details are absent; page 6 gives only the shared general procedure.",
                           "No Supporting Information file was explicitly supplied or associated."])


t2 = [
    (1,"1a","R1=CH3; R2=H; R3=n-C4H9; R4=R5=H",18.5,76,"4a"),
    (2,"1b","R1=CH3; R2=H; R3=CH3; R4=R5=H",3.5,71,"4b"),
    (3,"1c","R1=CH3; R2=H; R3=CH2Ph; R4=R5=H",18.5,61,"4c"),
    (4,"1d","R1=n-C4H9; R2=H; R3=n-C4H9; R4=R5=H",10.5,81,"4d"),
    (5,"1e","R1=Ph; R2=H; R3=n-C4H9; R4=R5=H",21,81,"4e"),
    (6,"1f","R1=n-C4H9; R2=H; R3=C3H5; R4=R5=H",26,64,"4f"),
    (7,"1g","R1=n-C4H9; R2=H; R3=CO2CH3; R4=R5=H",7.5,55,"4g"),
    (8,"1h","R1=n-C4H9; R2=H; R3=Ph; R4=R5=H",14.5,68,"4h"),
    (9,"1i","R1=Ph; R2=H; R3=Ph; R4=R5=H",14.5,60,"4i"),
    (10,"1j","R1=R2=CH3; R3=Ph; R4=R5=H",9,86,"4j"),
    (11,"1k","R1=R2=CH3; R3=n-C4H9; R4=R5=H",23,57,"4k"),
    (12,"1l","R1=R2=H; R3=CH2Ph; R4=R5=H",10,63,"4l"),
    (13,"1m","R1=R2=R5=H; R3=CH3; R4=n-C6H13",5,72,"4m"),
    (14,"1n","R1=R2=R3=R5=H; R4=n-C6H13",38,32,"4n"),
    (15,"1o","R1=R2=CH3; R3=R5=H; R4=n-C4H9",12,57,"4o"),
    (16,"1p","R1,R2=(CH2)5; R3=R5=H; R4=n-C4H9",7,69,"4p"),
    (17,"1q","R1=n-C4H9; R2=R3=H; R4,R5=(CH2)5",14,69,"4q"),
]
records += [scope_record(2, *row) for row in t2]

t3 = [
    (1,"2a","R1=CH3; R2=n-C4H9; R3=R4=H",48,63,"6a",None),
    (2,"2b","R1=H; R2=n-C4H9; R3=R4=H",24,61,"6b",None),
    (3,"2c","R1=CH3; R2=Ph; R3=R4=H",34,78,"6c",None),
    (4,"2d","R1=CH3; R2=t-C4H9; R3=R4=H",22,48,"6d",None),
    (5,"2e","R1=H; R2=n-C4H9; R3=i-C3H7; R4=H",20,87,"6e",None),
    (6,"2f","R1=CH3; R2=H; R3=R4=CH3",12,64,"6f",None),
    (7,"2g","R1=R2=H; R3=n-C4H9; R4=H",96,34,"6g",33),
    (8,"2h","R1=CH3; R2=R3=R4=H",24,0,"6h",35),
]
records += [scope_record(3, entry, substrate, substituents, time_h, yld, product,
                         page=4, recovered=recovered)
            for entry, substrate, substituents, time_h, yld, product, recovered in t3]

# Page 4 Scheme 4: one 1r experiment and three distinct 1s loading rows.
e = ev(4)
records.append(rec("scheme4_1r", 4, "substrate_scope_entry", [
    part("allenol_1r", "reactant", "1r", e), part("allyl_bromide_3a", "reactant", "3a", e, amounts=[amount("equivalents", 5, "equiv", e)]),
    part("pdcl2", "catalyst", "PdCl2", e, amounts=[amount("catalyst_loading", 5, "mol%", e)]),
    part("dma", "solvent", "DMA", e), part("product_4r", "product", "4r", e),
    part("side_products", "product", "unstable side products", e),
], [{"step_id":"reaction","participant_ids":["allenol_1r","allyl_bromide_3a","pdcl2","dma"],
     "conditions":[fld("temperature","r.t.",e),amount("time",17,"h",e)]}],
    [fld("isolated_yield",{"number":4,"unit":"%"},e,["product_4r"]),
     fld("side_products_observed","yes; structures not determined",e,["side_products"])],
    unresolved=["Side products were too unstable for structural determination.","SMILES are not assigned from the scheme drawing.",
                "No Supporting Information file was explicitly supplied or associated."]))

for tag, equiv, time_h, y4s, y5s in [("5equiv",5,4,4,65),("0.25equiv",0.25,10,"trace",73),("0equiv",0,48,"not reported",24)]:
    e = ev(4)
    ps = [part("allenol_1s","reactant","1s",e),
          part("allyl_bromide_3a","reactant","3a",e,amounts=[amount("equivalents",equiv,"equiv",e)]),
          part("pdcl2","catalyst","PdCl2",e,amounts=[amount("catalyst_loading",5,"mol%",e)]),
          part("dma","solvent","DMA",e), part("product_4s","product","4s",e), part("product_5s","product","5s",e)]
    outs = [fld("product_4s_yield", ({"number":y4s,"unit":"%"} if isinstance(y4s,(int,float)) else y4s), e,["product_4s"]),
            fld("product_5s_yield", {"number":y5s,"unit":"%"}, e,["product_5s"])]
    records.append(rec(f"scheme4_1s_{tag}",4,"optimization_entry",ps,
                       [{"step_id":"reaction","participant_ids":["allenol_1s","allyl_bromide_3a","pdcl2","dma"],
                         "conditions":[fld("temperature","r.t.",e),amount("time",time_h,"h",e)]}],outs,
                       notes=["At 0 equiv, allyl bromide was not added; the zero quantity is retained from Scheme 4."],
                       unresolved=["Yield measurement basis is not stated in Scheme 4.","SMILES are not assigned from the scheme drawing.",
                                   "No Supporting Information file was explicitly supplied or associated."]))

# Page 4 Scheme 5 plus the stated cinnamyl-bromide failure.
for reagent, rdesc, time_h, product, yld in [("3b","R=Ph",22.5,"4t",74),("3c","R=Br",19,"4u",71),("3d","R=n-C4H9",12.5,"4v",73)]:
    e=ev(4)
    records.append(rec(f"scheme5_{reagent}",4,"substrate_scope_entry",[
        part("allenol_1j","reactant","1j",e), part("allylic_bromide","reactant",reagent,e,name=f"2-substituted allylic bromide {reagent} ({rdesc})",amounts=[amount("equivalents",5,"equiv",e)]),
        part("pdcl2","catalyst","PdCl2",e,amounts=[amount("catalyst_loading",5,"mol%",e)]),part("dma","solvent","DMA",e),part("product","product",product,e)],
        [{"step_id":"reaction","participant_ids":["allenol_1j","allylic_bromide","pdcl2","dma"],"conditions":[fld("temperature","r.t.",e),amount("time",time_h,"h",e)]}],
        [fld("isolated_yield",{"number":yld,"unit":"%"},e,["product"])],
        unresolved=["SMILES are not assigned from the scheme drawing.","Workup/purification and yield basis are not shown here.",
                    "No Supporting Information file was explicitly supplied or associated."]))

e=ev(4)
records.append(rec("scheme5_cinnamyl_bromide_failure",4,"substrate_scope_entry",[
    part("allenol_1j","reactant","1j",e),part("cinnamyl_bromide","reactant","3-phenyl-2-propenyl bromide",e),
    part("pdcl2","catalyst","PdCl2",e,amounts=[amount("catalyst_loading",5,"mol%",e)]),part("dma","solvent","DMA",e),
    part("desired_product","product","desired cyclic product",e)],
    [{"step_id":"reaction","participant_ids":["allenol_1j","cinnamyl_bromide","pdcl2","dma"],"conditions":[fld("temperature","r.t.",e),fld("time",None,e)]}],
    [fld("reaction_result","complicated; no desired cyclic product isolated",e,["desired_product"])],
    unresolved=["Reaction time, quantities, and side-product identities are not reported.","No Supporting Information file was explicitly supplied or associated."]))

# Page 5: proposed pathways are mechanism records, not reported experiments.
for n, title in [(6,"proposed Pd(II)-catalyzed pathway"),(7,"alternative Pd(0)-catalyzed pathways A and B"),(9,"proposed origin of major/minor regioisomers")]:
    records.append(rec(f"scheme{n}_mechanism",5,"mechanism",notes=[title,"Mechanistic arrows are not treated as independent experimental yield records."],
                       unresolved=["Proposed intermediates are generic R-group structures and have no unique SMILES."]))

# Page 5 Scheme 8: six independent regioselectivity experiments.
scheme8 = [
    ("1a_3e_pdcl2","1a","3e","R1=H; R2=CH3","PdCl2",5,"h",9,63,"4aa","4ab","98:2"),
    ("1a_3e_pd2dba3","1a","3e","R1=H; R2=CH3","Pd2(dba)3.CHCl3",2.5,"d",3,50,"4aa","4ab","98:2"),
    ("1a_3f_pdcl2","1a","3f","R1=CH3; R2=H","PdCl2",5,"h",21,21,"4aa","4ab","14:86"),
    ("1a_3f_pd2dba3","1a","3f","R1=CH3; R2=H","Pd2(dba)3.CHCl3",2.5,"d",7,22,"4aa","4ab","13:87"),
    ("1j_3e","1j","3e","R1=H; R2=CH3","PdCl2",5,"h",14,69,"4ja","4jb","89:11"),
    ("1j_3f","1j","3f","R1=CH3; R2=H","PdCl2",5,"h",40,34,"4ja","4jb","15:85"),
]
for suffix, substrate, reagent, desc, catalyst, loading, tunit, tnum, yld, major, minor, ratio in scheme8:
    e=ev(5)
    records.append(rec(f"scheme8_{suffix}",5,"optimization_entry",[
        part("substrate","reactant",substrate,e),part("allylic_chloride","reactant",reagent,e,name=f"allylic chloride {reagent} ({desc})"),
        part("catalyst","catalyst",catalyst,e,amounts=[amount("catalyst_loading",loading,"mol%",e)]),part("dma","solvent","DMA",e),
        part("product_a","product",major,e),part("product_b","product",minor,e)],
        [{"step_id":"reaction","participant_ids":["substrate","allylic_chloride","catalyst","dma"],"conditions":[fld("temperature","r.t.",e),amount("time",tnum,tunit,e)]}],
        [fld("combined_yield",{"number":yld,"unit":"%"},e,["product_a","product_b"]),
         fld("product_ratio",ratio,e,["product_a","product_b"])],
        unresolved=["Combined-yield measurement basis is not stated in Scheme 8.","E/Z composition within 4aa/4ja is not quantified.",
                    "SMILES are not assigned from the scheme drawing.","No Supporting Information file was explicitly supplied or associated."]))

# Page 6 Scheme 10: stoichiometric pi-allylpalladium chloride dimer tests.
e=ev(6)
records.append(rec("scheme10_1a",6,"reported_experiment",[
    part("allenol_1a","reactant","1a",e),part("allylpalladium_dimer","reagent","(pi-allyl)palladium chloride dimer",e,amounts=[amount("equivalents",1,"equiv",e)]),part("dma","solvent","DMA",e)],
    [{"step_id":"reaction","participant_ids":["allenol_1a","allylpalladium_dimer","dma"],"conditions":[fld("temperature","r.t.",e),amount("time",24,"h",e)]}],
    [fld("reaction_result","no cyclic product",e)],
    unresolved=["Amounts, concentration, and noncyclic products are not reported in Scheme 10.","No Supporting Information file was explicitly supplied or associated."]))

records.append(rec("scheme10_1j",6,"reported_experiment",[
    part("allenol_1j","reactant","1j",e),part("allylpalladium_dimer","reagent","(pi-allyl)palladium chloride dimer",e,amounts=[amount("equivalents",1,"equiv",e)]),
    part("dma","solvent","DMA",e),part("product_11","product","11",e),part("product_4j","product","4j",e)],
    [{"step_id":"reaction","participant_ids":["allenol_1j","allylpalladium_dimer","dma"],"conditions":[fld("temperature","r.t.",e),amount("time",96,"h",e)]}],
    [fld("combined_yield",{"number":33,"unit":"%"},e,["product_11","product_4j"]),fld("product_ratio","11:4j = 92:8",e,["product_11","product_4j"])],
    unresolved=["Scheme 10 does not state whether 33% is isolated or analytical yield.","SMILES are not assigned from the scheme drawing.",
                "No Supporting Information file was explicitly supplied or associated."]))

# Page 6 Scheme 11 and eq 5.
records.append(rec("scheme11_mechanism",6,"mechanism",notes=["Proposed Pd(II)-catalyzed bimolecular cyclizative coupling pathway to product 5.",
                                                               "Mechanistic arrows are not treated as independent experimental yield records."],
                   unresolved=["Generic intermediates and R-group structures have no unique SMILES."]))

records.append(rec("eq5_1s_3g",6,"reported_experiment",[
    part("allenol_1s","reactant","1s",e),part("bromoallene_3g","reactant","3g",e,name="4-bromo-1,2-butadiene",amounts=[amount("equivalents",5,"equiv",e)]),
    part("pdcl2","catalyst","PdCl2",e,amounts=[amount("catalyst_loading",5,"mol%",e)]),part("dma","solvent","DMA",e),
    part("product_13","product","13",e),part("product_5s","product","5s",e)],
    [{"step_id":"reaction","participant_ids":["allenol_1s","bromoallene_3g","pdcl2","dma"],"conditions":[fld("temperature","r.t.",e),amount("time",9,"h",e)]}],
    [fld("combined_yield",{"number":55,"unit":"%"},e,["product_13","product_5s"]),fld("product_ratio","13:5s = 92:8",e,["product_13","product_5s"])],
    unresolved=["Equation 5 does not state whether 55% is isolated or analytical yield.","SMILES are not assigned from the scheme drawing.",
                "No Supporting Information file was explicitly supplied or associated."]))

# Page 6 shared experimental procedure, classified as general rather than a single run.
records.append(rec("general_procedure_cyclizative_coupling",6,"general_scheme",[
    part("allenol","reactant","allenol 1 or 2",e,amounts=[amount("amount",1,"mmol",e)]),
    part("allylic_halide","reactant","allylic halide 3",e,amounts=[amount("amount",5,"mmol",e)]),
    part("pdcl2","catalyst","PdCl2",e,amounts=[amount("catalyst_loading",5,"mol%",e)]),
    part("dma","solvent","DMA",e,amounts=[amount("volume",6,"mL",e)]),
    part("ether","reagent","ether",e),part("brine","reagent","brine",e),part("sodium_sulfate","reagent","anhydrous sodium sulfate",e),
], [
    {"step_id":"reaction","participant_ids":["allenol","allylic_halide","pdcl2","dma"],"conditions":[fld("temperature","r.t.",e),fld("time","until complete by TLC",e)]},
    {"step_id":"workup","participant_ids":["ether","brine","sodium_sulfate"],"conditions":[fld("workup","ether added; washed with brine three times; dried over anhydrous sodium sulfate",e)]},
    {"step_id":"purification","participant_ids":[],"conditions":[fld("purification","silica-gel column chromatography (petroleum ether/ether)",e)]},
], notes=["Shared procedure; not itself a unique experimental run or yield."],
    unresolved=["Reaction duration and chromatography solvent ratio depend on the individual example.","Generic structures have no unique SMILES.",
                "No Supporting Information file was explicitly supplied or associated."]))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
