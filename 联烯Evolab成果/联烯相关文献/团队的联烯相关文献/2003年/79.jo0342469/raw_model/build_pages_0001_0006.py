#!/usr/bin/env python3
"""Build evidence-linked machine records for jo0342469 PDF pages 1-6."""
import json
from pathlib import Path

DOC = "doc_70cf3d194c2f126f"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0006.json")


def ev(*pages):
    ids = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


KNOWN_SMILES = {
    "allyl bromide": "C=CCBr", "3-chloro-1-butene": "C=CCCCl",
    "3-chloro-2-methyl-1-propene": "C=C(C)CCl", "1-chloro-2-butene": "CC=CCCl",
    "DMA": "CC(=O)N(C)C", "DMF": "CN(C)C=O", "acetonitrile": "CC#N",
    "THF": "C1CCOC1", "acetone": "CC(C)=O", "diethyl ether": "CCOCC",
    "methanol": "CO", "ethanol": "CCO", "dichloromethane": "ClCCl",
    "PdCl2": "[Cl-].[Cl-].[Pd+2]", "Pd(OAc)2": "CC(=O)[O-].CC(=O)[O-].[Pd+2]",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O", "LiOH": "[Li+].[OH-]",
    "NaOH": "[Na+].[OH-]", "KOH": "[K+].[OH-]", "NaHCO3": "[Na+].OC([O-])=O",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O", "K3PO4": "[K+].[K+].[K+].[O-]P([O-])([O-])=O",
    "p-toluenesulfonamide": "CC1=CC=C(C=C1)S(=O)(=O)N", "phthalimide": "O=C1NC(=O)C2=CC=CC=C12",
    "triphenylphosphine": "P(C1=CC=CC=C1)(C1=CC=CC=C1)C1=CC=CC=C1",
    "triethylamine": "CCN(CC)CC", "hydrazine": "NN", "tosyl chloride": "CC1=CC=C(C=C1)S(=O)(=O)Cl",
    "pyridine": "N1=CC=CC=C1", "phosphorus tribromide": "P(Br)(Br)Br",
    "zinc chloride": "[Cl-].[Cl-].[Zn+2]", "diisopropylamine": "CC(C)NC(C)C",
    "n-butyllithium": "[Li]CCCC", "diazomethane": "[N-]=[N+]=C",
    "vinyl acetate": "C=COC(C)=O", "methyl iodide": "CI", "sodium periodate": "[Na+].[O-]I(=O)(=O)=O",
    "lithium aluminium hydride": "[Li+].[AlH4-]", "sodium hydride": "[Na+].[H-]",
}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def participant(entity_id, role, label, evidence, name=None, amounts=None, smiles=None):
    chemical_name = name or (label if label in KNOWN_SMILES else None)
    candidate = smiles if smiles is not None else KNOWN_SMILES.get(chemical_name)
    return {
        "entity_id": entity_id, "role": role,
        "label": fact(label, evidence), "name": fact(chemical_name, evidence),
        "smiles": fact(candidate, evidence), "smiles_parseable": None,
        "structure_verified": False, "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}", "document_id": DOC, "source_reaction_id": suffix,
        "record_kind": kind, "status": "candidate", "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)), "participants": participants,
        "steps": steps, "outcomes": outcomes or [], "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved or ["Machine extraction requires source review; structures are unverified."]},
    }


def step(step_id, ids, evidence, time=None, temp=None, solvent=None, operation=None):
    conditions = []
    if time is not None:
        conditions.append(field("time", time, evidence))
    if temp is not None:
        conditions.append(field("temperature", temp, evidence))
    if solvent is not None:
        conditions.append(field("solvent", solvent, evidence))
    if operation is not None:
        conditions.append(field("operation", operation, evidence))
    return {"step_id": step_id, "participant_ids": ids, "conditions": conditions}


records = []

# Page 2 equations: prior work and conceptual proposal are not reported experiments in this paper.
e2 = ev(2)
records.append(record("eq1_prior_allenol_cyclization", "literature_example", e2,
    [participant("eq1_allenol", "reactant", "generic allenic alcohol", e2),
     participant("eq1_halide", "reactant", "generic allylic halide", e2),
     participant("eq1_pdcl2", "catalyst", "PdCl2", e2, amounts=[field("amount", qty(5, "mol%"), e2)]),
     participant("eq1_dma", "solvent", "DMA", e2),
     participant("eq1_product", "product", "4-(2'-alkenyl)-2,5-dihydrofuran", e2)],
    [step("reaction", ["eq1_allenol", "eq1_halide", "eq1_pdcl2", "eq1_dma"], e2,
          temp="r.t.", solvent="DMA")],
    notes=["Prior work cited as reference 13; no experiment-specific yield is reported here."],
    unresolved=["Generic R groups and allylic halide are not fully specified; yield and time are missing."]))
records.append(record("eq2_proposed_amino_allene_cyclization", "general_scheme", e2,
    [participant("eq2_amino_allene", "reactant", "generic amino allene", e2),
     participant("eq2_halide", "reactant", "generic allylic halide", e2),
     participant("eq2_product", "product", "generic 3-allyl-2,5-dihydropyrrole", e2)],
    [step("conceptual_arrow", ["eq2_amino_allene", "eq2_halide"], e2, operation="proposed transformation")],
    notes=["Equation 2 is posed with a question mark and is not an experiment."],
    unresolved=["Conditions, structures, yield, time, and temperature are not specified in the conceptual equation."]))

# Scheme 1 generic variants 1b-c; 2a is recorded below from the detailed experiment.
records.append(record("scheme1_1bc_to_2bc", "general_scheme", e2,
    [participant("s1_1bc", "reactant", "alpha-allenols 1b-c", e2),
     participant("s1_pbr3", "reagent", "phosphorus tribromide", e2),
     participant("s1_pyridine", "reagent", "pyridine", e2),
     participant("s1_ether", "solvent", "diethyl ether", e2),
     participant("s1_k2co3", "reagent", "K2CO3", e2),
     participant("s1_tsnh2", "reactant", "p-toluenesulfonamide", e2),
     participant("s1_acetone", "solvent", "acetone", e2),
     participant("s1_2bc", "product", "alpha-amino allenes 2b-c", e2)],
    [step("i_bromination", ["s1_1bc", "s1_pbr3", "s1_pyridine", "s1_ether"], e2,
          temp=qty(-30, "°C"), solvent="diethyl ether", operation="warm from -30 °C to reflux"),
     step("ii_amination", ["s1_k2co3", "s1_tsnh2", "s1_acetone"], e2, temp="reflux", solvent="acetone")],
    unresolved=["Scheme groups 1b-c/2b-c are generic variants; individual quantities, times, yields, and intermediate identities are not reported on page 2."]))

# Scheme 3 generic preparations not otherwise detailed in pages 1-6.
records.append(record("scheme3_1e_l_to_2e_l", "general_scheme", e2,
    [participant("s3_1e_l", "reactant", "allenols 1e-l", e2),
     participant("s3_phthalimide_a", "reagent", "phthalimide", e2), participant("s3_dead_a", "reagent", "DEAD", e2),
     participant("s3_pph3_a", "reagent", "triphenylphosphine", e2), participant("s3_thf_a", "solvent", "THF", e2),
     participant("s3_hydrazine_a", "reagent", "hydrazine hydrate", e2), participant("s3_etoh_a", "solvent", "ethanol", e2),
     participant("s3_et3n_a", "reagent", "triethylamine", e2), participant("s3_pgcl_a", "reagent", "PGCl", e2),
     participant("s3_dcm_a", "solvent", "dichloromethane", e2), participant("s3_2e_l", "product", "alpha-amino allenes 2e-l", e2)],
    [step("i_mitsunobu", ["s3_1e_l", "s3_phthalimide_a", "s3_dead_a", "s3_pph3_a", "s3_thf_a"], e2, temp=qty(0, "°C"), solvent="THF", operation="warm to r.t."),
     step("ii_hydrazinolysis", ["s3_hydrazine_a", "s3_etoh_a"], e2, temp="reflux", solvent="ethanol"),
     step("iii_protection", ["s3_et3n_a", "s3_pgcl_a", "s3_dcm_a"], e2, temp=qty(0, "°C"), solvent="dichloromethane", operation="warm to r.t.")],
    unresolved=["The scheme covers variants 2e-l; individual reagent quantities, times, yields, and structures are not given here."]))
records.append(record("scheme3_5a_to_6b_d", "general_scheme", e2,
    [participant("s3_5a", "reactant", "phthalimide 5a", e2), participant("s3_hydrazine_b", "reagent", "hydrazine hydrate", e2),
     participant("s3_etoh_b", "solvent", "ethanol", e2), participant("s3_et3n_b", "reagent", "triethylamine", e2),
     participant("s3_pgcl_b", "reagent", "PGCl (NsCl, AcCl, or BzCl)", e2), participant("s3_dcm_b", "solvent", "dichloromethane", e2),
     participant("s3_6bd", "product", "beta-amino allenes 6b-d", e2)],
    [step("ii_hydrazinolysis", ["s3_5a", "s3_hydrazine_b", "s3_etoh_b"], e2, temp="reflux", solvent="ethanol"),
     step("iii_protection", ["s3_et3n_b", "s3_pgcl_b", "s3_dcm_b"], e2, temp=qty(0, "°C"), solvent="dichloromethane", operation="warm to r.t.")],
    unresolved=["Scheme variants 6b-d differ by protecting group; individual quantities, times, and yields are not reported on page 2."]))
records.append(record("scheme3_4b_l_to_6e_l", "general_scheme", e2,
    [participant("s3_4bl", "reactant", "beta-allenols 4b-l", e2), participant("s3_phthalimide_c", "reagent", "phthalimide", e2),
     participant("s3_dead_c", "reagent", "DEAD", e2), participant("s3_pph3_c", "reagent", "triphenylphosphine", e2),
     participant("s3_thf_c", "solvent", "THF", e2), participant("s3_hydrazine_c", "reagent", "hydrazine hydrate", e2),
     participant("s3_etoh_c", "solvent", "ethanol", e2), participant("s3_et3n_c", "reagent", "triethylamine", e2),
     participant("s3_tscl_c", "reagent", "tosyl chloride", e2), participant("s3_dcm_c", "solvent", "dichloromethane", e2),
     participant("s3_6el", "product", "beta-amino allenes 6e-l", e2)],
    [step("i_mitsunobu", ["s3_4bl", "s3_phthalimide_c", "s3_dead_c", "s3_pph3_c", "s3_thf_c"], e2, temp=qty(0, "°C"), solvent="THF", operation="warm to r.t."),
     step("ii_hydrazinolysis", ["s3_hydrazine_c", "s3_etoh_c"], e2, temp="reflux", solvent="ethanol"),
     step("iii_tosylation", ["s3_et3n_c", "s3_tscl_c", "s3_dcm_c"], e2, temp=qty(0, "°C"), solvent="dichloromethane", operation="warm to r.t.")],
    unresolved=["Scheme variants 6e-l have generic R groups; individual quantities, times, and yields are not reported on page 2."]))


def table_coupling(suffix, kind, evidence, substrate, product_yields, catalyst, loading, solvent, time,
                   base=None, base_equiv=None, temperature="r.t.", substrate_amount=None,
                   allyl_equiv=5, extra_outcomes=None, extra_notes=None, unresolved=None, steps_override=None):
    ps = [participant(f"{suffix}_substrate", "reactant", substrate, evidence,
                      amounts=([field("amount", substrate_amount, evidence)] if substrate_amount else [])),
          participant(f"{suffix}_allyl", "reactant", "allyl bromide", evidence,
                      amounts=[field("amount", qty(allyl_equiv, "equiv"), evidence)]),
          participant(f"{suffix}_cat", "catalyst", catalyst, evidence,
                      amounts=[field("amount", qty(loading, "mol%"), evidence)]),
          participant(f"{suffix}_solv", "solvent", solvent, evidence)]
    if base:
        ps.append(participant(f"{suffix}_base", "reagent", base, evidence,
                              amounts=[field("amount", qty(base_equiv, "equiv"), evidence)] if base_equiv else []))
    outcomes = []
    product_ids = []
    for label, value in product_yields:
        pid = f"{suffix}_{label}"
        product_ids.append(pid)
        ps.append(participant(pid, "product", label, evidence))
        if value is not None:
            outcomes.append(field("isolated_yield", qty(value, "%"), evidence, [pid]))
    if any(value is not None for _, value in product_yields):
        outcomes.append(field("yield_measurement_basis", "isolated yield based on substrate", evidence, product_ids))
    outcomes.extend(extra_outcomes or [])
    ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    steps = steps_override or [step("reaction", ids, evidence, time=qty(time, "h") if isinstance(time, (int, float)) else time,
                                    temp=temperature, solvent=solvent)]
    return record(suffix, kind, evidence, ps, steps, outcomes, extra_notes,
                  unresolved or ["Structures are represented by source labels and remain unverified; no SI was supplied."])


# Page 3 Table 1: every optimization row is independent.
e3 = ev(3)
t1 = [
    (1, "PdCl2", 5, None, None, "DMA", 4, 61, 0),
    (2, "PdCl2", 5, "K2CO3", 1.5, "DMA", 23, 44, 17),
    (3, "PdCl2(PhCN)2", 5, None, None, "acetonitrile", 4, 44, 0),
    (4, "PdCl2(PhCN)2", 10, "K2CO3", 1.5, "acetonitrile", 16, 45, 0),
    (5, "Pd(OAc)2", 5, None, None, "DMA", 4, 83, 0),
    (6, "PdCl2(PhCN)2", 5, None, None, "DMA", 4, 83, 0),
]
for row, cat, loading, base, beq, solv, hours, y7, y8 in t1:
    records.append(table_coupling(f"table1_entry_{row:02d}", "optimization_entry", e3, "2a",
        [("7a", y7), ("8a", y8)], cat, loading, solv, hours, base, beq))

# Page 3 Table 2: substrate scope, including staged heating and footnotes.
t2 = [
    (1,"2b","7b",15,91,"PdCl2(PhCN)2",5),(2,"2b","7b",15,95,"PdCl2",5),
    (3,"2d","7d",44,85,"PdCl2",5),(4,"2e","7e",12,83,"PdCl2",5),
    (5,"2f","7f",5,96,"PdCl2",5),(6,"2g","7g",3,85,"PdCl2",5),
    (7,"2h","7h",3,75,"PdCl2",5),(8,"2i","7i",3,81,"PdCl2",5),
    (9,"2j","7j",2,98,"PdCl2",5),(10,"2k","7k",131,18,"PdCl2",5),
    (11,"2l","7l",120,12,"PdCl2",5),(12,"(S)-2m","(S)-7m",2,92,"PdCl2",5),
    (13,"(R)-2n","(R)-7n",3,88,"PdCl2",5),
]
for row, sub, prod, hours, yld, cat, loading in t2:
    suffix=f"table2_entry_{row:02d}"
    extra=[]; notes=[]; unres=None; override=None
    evidence=e3
    if row == 3:
        extra.append(field("trans_cis_ratio", "96:4", e3, [f"{suffix}_{prod}"]))
        notes.append("The trans/cis assignment is reported as based on an oxypalladation mechanism and is therefore tentative.")
    if row == 10:
        extra.append(field("recovered_starting_material", qty(48,"%"), e3, [f"{suffix}_substrate"]))
        override=[step("stage_1", [], e3, time=qty(60,"h"), temp="r.t.", solvent="DMA"),
                  step("stage_2", [], e3, time=qty(35,"h"), temp=qty(50,"°C"), solvent="DMA"),
                  step("stage_3", [], e3, time=qty(36,"h"), temp=qty(70,"°C"), solvent="DMA")]
    if row == 11:
        override=[step("reported_total", [], e3, time=qty(120,"h"), solvent="DMA"),
                  step("stage_1", [], e3, time=qty(48,"h"), temp="r.t.", solvent="DMA"),
                  step("stage_2", [], e3, time=qty(36,"h"), temp=qty(50,"°C"), solvent="DMA")]
        unres=["Table reports 120 h, while the visible footnote specifies only 48 h at r.t. plus 36 h at 50 °C; the remaining 36 h condition is absent.",
               "Structures are represented by source labels and remain unverified; no SI was supplied."]
    if row in (12,13):
        evidence=ev(3,5)
        start_ee=86.6 if row==12 else 78
        prod_ee=86.4 if row==12 else 76
        extra.append(field("product_ee", qty(prod_ee,"%"), evidence, [f"{suffix}_{prod}"]))
        notes.append(f"Scheme 5 reports starting-material ee {start_ee}% and product ee {prod_ee}%.")
        unres=["Page 4 prose states 88% and 92%, respectively, whereas Table 2 and Scheme 5 give 92% for (S)-7m and 88% for (R)-7n; table/scheme values are retained.",
               "Absolute configurations are reported as tentatively assigned; structures remain unverified and no SI was supplied."]
    rec=table_coupling(suffix,"substrate_scope_entry",evidence,sub,[(prod,yld)],cat,loading,"DMA",hours,
                       extra_outcomes=extra,extra_notes=notes,unresolved=unres,steps_override=override)
    if row in (12,13):
        rec["participants"][0]["amounts"].append(field("enantiomeric_excess", qty(86.6 if row==12 else 78,"%"), evidence))
    if override:
        reactant_ids=[p["entity_id"] for p in rec["participants"] if p["role"] != "product"]
        for s in rec["steps"]: s["participant_ids"]=reactant_ids
    records.append(rec)

# Page 3 Table 3 optimization.
t3 = [
    (1,"PdCl2",5,None,None,"DMA",40,None,None,76),(2,"PdCl2(PhCN)2",5,None,None,"DMA",40,None,None,78),
    (3,"PdCl2",5,"K2CO3",2,"DMA",6.5,0,67,None),(4,"PdCl2(PhCN)2",10,"K2CO3",1.5,"DMA",12,5,59,None),
    (5,"PdCl2(PhCN)2",10,"K2CO3",1.5,"DMF",13.5,0,55,None),(6,"PdCl2(PhCN)2",10,"K2CO3",1.5,"acetone",24,32,11,None),
    (7,"PdCl2(PhCN)2",10,"K2CO3",1.5,"acetonitrile",12,39,4,None),(8,"PdCl2(PhCN)2",10,"K2CO3",1.5,"THF",12,39,22,None),
    (9,"PdCl2(PhCN)2",10,"LiOH",1.5,"THF",72,12,28,None),(10,"PdCl2(PhCN)2",10,"NaOH",1.5,"THF",60,11,49,None),
    (11,"PdCl2(PhCN)2",10,"KOH",1.5,"THF",50,8,25,None),(12,"PdCl2(PhCN)2",10,"Ba(OH)2",1.5,"THF",72,6,0,41),
    (13,"PdCl2(PhCN)2",10,"NaHCO3",1.5,"THF",72,18,25,None),(14,"PdCl2(PhCN)2",10,"Cs2CO3",1.5,"THF",72,19,27,None),
    (15,"PdCl2(PhCN)2",10,"K3PO4",1.5,"THF",72,33,12,None),
]
for row,cat,loading,base,beq,solv,hours,y7,y8,recovery in t3:
    suffix=f"table3_entry_{row:02d}"; extra=[]; notes=[]
    if recovery is not None:
        extra.append(field("recovered_starting_material", qty(recovery,"%"), e3, [f"{suffix}_substrate"]))
    if row in (1,2):
        extra.append(field("reaction_result", "no reaction", e3))
        notes.append("Product-yield cells are reported as NR rather than numeric zero.")
    records.append(table_coupling(suffix,"optimization_entry",e3,"2c",[("7c",y7),("8c",y8)],cat,loading,solv,hours,
                                  base,beq,extra_outcomes=extra,extra_notes=notes))

# Page 4 Scheme 4: three allylic-halide experiments.
e4=ev(4)
scheme4=[
    ("scheme4_3_chloro_1_butene","3-chloro-1-butene",18,[('7o',83)],[("E_Z_ratio","1:1",['scheme4_3_chloro_1_butene_7o'])]),
    ("scheme4_3_chloro_2_methyl_1_propene","3-chloro-2-methyl-1-propene",45,[('7p',68)],[]),
    ("scheme4_1_chloro_2_butene","1-chloro-2-butene",40,[('7q',None),('7o',None)],[("combined_isolated_yield",qty(24,"%"),['scheme4_1_chloro_2_butene_7q','scheme4_1_chloro_2_butene_7o']),("product_ratio","64:36",['scheme4_1_chloro_2_butene_7q','scheme4_1_chloro_2_butene_7o'])]),
]
for suffix,halide,hours,prods,extras in scheme4:
    ps=[participant(f"{suffix}_2b","reactant","2b",e4),participant(f"{suffix}_halide","reactant",halide,e4,amounts=[field("amount",qty(5,"equiv"),e4)]),
        participant(f"{suffix}_pdcl2","catalyst","PdCl2",e4,amounts=[field("amount",qty(5,"mol%"),e4)]),participant(f"{suffix}_dma","solvent","DMA",e4)]
    outcomes=[]; targets=[]
    for label,yld in prods:
        pid=f"{suffix}_{label}";targets.append(pid);ps.append(participant(pid,"product",label,e4))
        if yld is not None: outcomes.append(field("isolated_yield",qty(yld,"%"),e4,[pid]))
    for name,value,tg in extras: outcomes.append(field(name,value,e4,tg))
    if suffix!="scheme4_1_chloro_2_butene": outcomes.append(field("yield_measurement_basis","isolated yield based on 2b",e4,targets))
    else: outcomes.append(field("yield_measurement_basis","combined isolated yield based on 2b",e4,targets))
    records.append(record(suffix,"substrate_scope_entry",e4,ps,[step("reaction",[p["entity_id"] for p in ps if p["role"]!="product"],e4,time=qty(hours,"h"),temp="r.t.",solvent="DMA")],outcomes,
                          unresolved=["Product structures are taken only as source labels and remain unverified; no SI was supplied."]))

# Page 4 Table 4 beta-amino-allene scope.
t4=[
    (1,"6a","9a",12,91,"PdCl2","r.t.",None),(2,"6b","9b",24,77,"PdCl2","r.t.",None),
    (3,"6c","9c",20,45,"PdCl2","r.t.",None),(4,"6c","9c",24,47,"PdCl2(PhCN)2","r.t.",None),
    (5,"6d","9d",96,None,"PdCl2","r.t.","complex mixture"),(6,"6e","9e",5,76,"PdCl2","r.t.",None),
    (7,"6f","9f",96,46,"PdCl2","r.t.","34% recovered"),(8,"6f","9f",48,79,"PdCl2",{"minimum":50,"maximum":55,"unit":"°C","raw_text":"50-55 °C"},None),
    (9,"6g","9g",30,79,"PdCl2","r.t.",None),(10,"6h","9h",171,14,"PdCl2",None,"31% recovered"),
    (11,"6i","9i",4,80,"PdCl2","r.t.",None),(12,"6j","9j",17,97,"PdCl2","r.t.",None),
    (13,"6k","9k",25,32,"PdCl2","r.t.",None),(14,"6l","9l",4,67,"PdCl2","r.t.",None),
]
for row,sub,prod,hours,yld,cat,temp,special in t4:
    suffix=f"table4_entry_{row:02d}";extra=[];notes=[];override=None
    if special=="complex mixture":
        extra.append(field("reaction_result","complex mixture of unidentified products",e4));notes.append("No isolated yield for expected product 9d is reported.")
    if special and "recovered" in special:
        extra.append(field("recovered_starting_material",qty(int(special.split('%')[0]),"%"),e4,[f"{suffix}_substrate"]))
    if row==10:
        override=[step("stage_1",[],e4,time=qty(48,"h"),temp="r.t.",solvent="DMA"),step("stage_2",[],e4,time=qty(72,"h"),temp=qty(50,"°C"),solvent="DMA"),step("stage_3",[],e4,time=qty(51,"h"),temp=qty(70,"°C"),solvent="DMA")]
    rec=table_coupling(suffix,"substrate_scope_entry",e4,sub,[(prod,yld)],cat,5,"DMA",hours,
                       temperature=temp,substrate_amount=qty(0.50,"mmol"),extra_outcomes=extra,extra_notes=notes,steps_override=override)
    rec["participants"][1]["amounts"]=[field("amount",qty(5,"equiv"),e4)]
    rec["participants"][3]["amounts"]=[field("volume",qty(3,"mL"),e4)]
    if override:
        ids=[p["entity_id"] for p in rec["participants"] if p["role"]!="product"]
        for s in rec["steps"]:s["participant_ids"]=ids
    records.append(rec)

# Page 5 Scheme 5: seven precursor-preparation arrows. Final two coupling arrows enrich Table 2 entries 12-13 above.
e5=ev(5)
def scheme5_simple(suffix,start,product,yld,ee_value,rotation,stepspec,extra_evidence=None):
    evidence=list(dict.fromkeys(e5+(extra_evidence or [])))
    ps=[participant(f"{suffix}_start","reactant",start,evidence),participant(f"{suffix}_product","product",product,evidence)]
    steps=[]
    for i,(reagents,temp,solvent,operation) in enumerate(stepspec,1):
        ids=[f"{suffix}_start"]
        for j,name in enumerate(reagents,1):
            eid=f"{suffix}_r{i}_{j}";ps.append(participant(eid,"reagent",name,evidence));ids.append(eid)
        if solvent:
            sid=f"{suffix}_s{i}";ps.append(participant(sid,"solvent",solvent,evidence));ids.append(sid)
        steps.append(step(f"stage_{i}",ids,evidence,temp=temp,solvent=solvent,operation=operation))
    outcomes=[field("isolated_yield",qty(yld,"%"),evidence,[f"{suffix}_product"]),field("product_ee",qty(ee_value,"%"),evidence,[f"{suffix}_product"]),field("optical_rotation",rotation,evidence,[f"{suffix}_product"])]
    return record(suffix,"reported_experiment",evidence,ps,steps,outcomes,
                  unresolved=["Scheme-level route lacks complete quantities and times; stereostructures and absolute assignments remain unverified.","No SI was supplied."])

records.append(scheme5_simple("scheme5_16a_to_S18a","16a","(S)-18a",47,99.5,"[alpha]D -24.9°",[(["Novozym 435","vinyl acetate"],qty(70,"°C"),None,"kinetic resolution")]))
records.append(scheme5_simple("scheme5_16b_to_R17","16b","(R)-17",25,99.6,"[alpha]D +6.4°",[(["Novozym 435","vinyl acetate"],qty(70,"°C"),None,"kinetic resolution")]))
records.append(scheme5_simple("scheme5_R17_to_R18b","(R)-17","(R)-18b",66,99.5,"[alpha]D +1.9°",[(["TBDMSCl","imidazole"],None,"DMF","silylation"),(["n-butyllithium","methyl iodide"],None,None,"alkylation"),(["5% HF"],None,"acetonitrile","desilylation")]))
common_18_to_1=[(["sodium hydride","chloroacetic acid"],None,None,"ether formation"),(["LDA"],qty(-78,"°C"),"THF","rearrangement; warm to r.t."),(["sodium periodate"],None,"methanol","oxidation"),(["lithium aluminium hydride"],qty(0,"°C"),"THF","reduction")]
records.append(scheme5_simple("scheme5_S18a_to_S1m","(S)-18a","(S)-1m",32,86.1,"[alpha]D -4.7°",common_18_to_1))
records.append(scheme5_simple("scheme5_R18b_to_R1n","(R)-18b","(R)-1n",8,78,"[alpha]D -25.1°",common_18_to_1))

# Detailed page-6 quantities are attached to the two Scheme-5 amination/tosylation records.
e56=ev(5,6)
def amination_record(suffix,start,product,start_data,pph3_data,phth_data,dead_data,hyd_data,product_mass,yld,ee_value,rotation,intermediate_mass):
    ps=[participant(f"{suffix}_start","reactant",start,e56,amounts=[field("mass",qty(start_data[0],"g"),e56),field("amount",qty(start_data[1],"mmol"),e56),field("enantiomeric_excess",qty(start_data[2],"%"),e56)]),
        participant(f"{suffix}_pph3","reagent","triphenylphosphine",e56,amounts=[field("mass",qty(pph3_data[0],"g"),e56),field("amount",qty(pph3_data[1],"mmol"),e56)]),
        participant(f"{suffix}_phth","reagent","phthalimide",e56,amounts=[field("mass",qty(phth_data[0],"g"),e56),field("amount",qty(phth_data[1],"mmol"),e56)]),
        participant(f"{suffix}_dead","reagent","DEAD",e56,amounts=[field("volume",qty(dead_data[0],"mL"),e56),field("amount",qty(dead_data[1],"mmol"),e56),field("concentration","40% in toluene",e56)]),
        participant(f"{suffix}_hyd","reagent","hydrazine hydrate",e56,amounts=[field("volume",qty(hyd_data[0],"mL"),e56),field("amount",qty(hyd_data[1],"mmol"),e56),field("concentration","85% purity",e56)]),
        participant(f"{suffix}_tscl","reagent","tosyl chloride",e56),participant(f"{suffix}_product","product",product,e56,amounts=[field("mass",qty(product_mass,"g"),e56)])]
    steps=[step("vii_mitsunobu",[f"{suffix}_start",f"{suffix}_pph3",f"{suffix}_phth",f"{suffix}_dead"],e56,temp=qty(0,"°C"),solvent="THF",operation="warm to r.t."),step("viii_hydrazinolysis",[f"{suffix}_hyd"],e56,temp="reflux",solvent="methanol"),step("ix_tosylation",[f"{suffix}_tscl"],e56,temp=qty(0,"°C"),solvent="dichloromethane",operation="warm to r.t.")]
    outcomes=[field("overall_isolated_yield",qty(yld,"%"),e56,[f"{suffix}_product"]),field("product_ee",qty(ee_value,"%"),e56,[f"{suffix}_product"]),field("optical_rotation",rotation,e56,[f"{suffix}_product"])]
    notes=[f"The corresponding phthalimide intermediate was isolated/reported as {intermediate_mass} g before hydrazinolysis and tosylation."]
    return record(suffix,"reported_experiment",e56,ps,steps,outcomes,notes,["Tosyl chloride and solvent quantities are not reported in the visible paragraph for these examples; structures remain unverified.","No SI was supplied."])

records.append(amination_record("scheme5_S1m_to_S2m","(S)-1m","(S)-2m",(1.203,8.6,86),(3.467,13.2),(1.328,8.9),(5.6,12.9),(0.96,16.6),1.628,65,86.6,"[alpha]D +17.4°",2.269))
records.append(amination_record("scheme5_R1n_to_R2n","(R)-1n","(R)-2n",(0.03,0.21,78),(0.090,0.34),(0.037,0.25),(0.14,0.32),(0.02,0.35),0.023,25,78,"[alpha]D -44°",0.044))

# Page 5 mechanisms are classified as mechanisms, not experiments.
records.append(record("scheme6_pdii_mechanism","mechanism",ev(4,5),
    [participant("m6_2","reactant","generic amino allene 2",ev(4,5)),participant("m6_pdcl2","catalyst","PdCl2",ev(4,5)),participant("m6_10","unspecified_agent","vinylpalladium intermediate 10",ev(4,5)),participant("m6_allylbr","reactant","allyl bromide",ev(4,5)),participant("m6_11","unspecified_agent","sigma-carbon-palladium intermediate 11",ev(4,5)),participant("m6_7","product","generic product 7",ev(4,5))],
    [step("aza_palladation",["m6_2","m6_pdcl2"],ev(4,5),operation="proposed intramolecular aza-palladation"),step("insertion",["m6_10","m6_allylbr"],ev(4,5),operation="proposed alkene insertion"),step("beta_elimination",["m6_11"],ev(4,5),operation="proposed beta-elimination")],
    notes=["Authors favor this Pd(II) pathway, but explicitly do not completely exclude Pd(0)."],
    unresolved=["Mechanistic proposal only; intermediates are not isolated experiments and generic structures remain unverified."]))
records.append(record("scheme7_pd0_mechanism","mechanism",ev(4,5),
    [participant("m7_2","reactant","generic amino allene 2",ev(4,5)),participant("m7_12","unspecified_agent","pi-allylpalladium intermediate 12",ev(4,5)),participant("m7_13","unspecified_agent","vinyl pi-allylpalladium intermediate 13",ev(4,5)),participant("m7_14","unspecified_agent","pi-allylpalladium intermediate 14",ev(4,5)),participant("m7_7","product","generic product 7",ev(4,5))],
    [step("pathway_a",["m7_2","m7_12"],ev(4,5),operation="proposed coordination, aza-palladation, and reductive elimination via 13"),step("pathway_b",["m7_2","m7_12"],ev(4,5),operation="proposed carbopalladation and nucleophilic substitution via 14")],
    notes=["Alternative Pd(0) pathways a and b are presented as less competitive mechanistic possibilities."],
    unresolved=["Mechanistic proposal only; intermediates are not isolated experiments and generic structures remain unverified."]))

# Page 5 Scheme 8 mechanistic experiments.
scheme8=[
    ("scheme8_entry_01","bis(eta3-allyl)di-mu-chlorodipalladium",1,48,34,[('7b',45),('15',55)],None),
    ("scheme8_entry_02","bis(1-methyl-eta3-allyl)di-mu-chlorodipalladium",1,96,38,[('(E+Z)-7o',47),('15',53)],None),
    ("scheme8_entry_03","bis(eta3-allyl)di-mu-chlorodipalladium",1,32,75,[('(E+Z)-7o',67),('7b',6),('15',27)],("3-chloro-1-butene",20)),
]
for suffix,pd,peq,hours,yld,products,added in scheme8:
    ps=[participant(f"{suffix}_2b","reactant","2b",e5),participant(f"{suffix}_pd","reactant",pd,e5,amounts=[field("amount",qty(peq,"equiv"),e5)]),participant(f"{suffix}_dma","solvent","DMA",e5)]
    if added:ps.append(participant(f"{suffix}_added","reactant",added[0],e5,amounts=[field("amount",qty(added[1],"equiv"),e5)]))
    pids=[]
    for label,_ratio in products:
        pid=f"{suffix}_p{len(pids)+1}";pids.append(pid);ps.append(participant(pid,"product",label,e5))
    outcomes=[field("combined_isolated_yield",qty(yld,"%"),e5,pids),field("product_ratio",": ".join(str(x[1]) for x in products),e5,pids),field("yield_measurement_basis","combined isolated yield",e5,pids)]
    records.append(record(suffix,"reported_experiment",e5,ps,[step("reaction",[p["entity_id"] for p in ps if p["role"]!="product"],e5,time=qty(hours,"h"),temp=qty(25,"°C"),solvent="DMA")],outcomes,
                          notes=["Product-ratio order: "+" : ".join(x[0] for x in products)],unresolved=["Mixture component structures and stereoisomer distribution remain unverified; no SI was supplied."]))

# Page 6 detailed starting-material preparations (with page-2 scheme evidence where applicable).
e26=ev(2,6)
records.append(record("prep_2a_allenyl_bromide", "reported_experiment", e26,
    [participant("p2ab_1a","reactant","2-benzylbuta-2,3-dien-1-ol (1a)",e26,amounts=[field("mass",qty(3.205,"g"),e26),field("amount",qty(20.0,"mmol"),e26)]),participant("p2ab_pyr","reagent","pyridine",e26,amounts=[field("volume",qty(0.20,"mL"),e26)]),participant("p2ab_pbr3","reagent","phosphorus tribromide",e26,amounts=[field("volume",qty(0.75,"mL"),e26),field("amount",qty(7.97,"mmol"),e26)]),participant("p2ab_ether","solvent","diethyl ether",e26),participant("p2ab_product","product","2-benzylbuta-2,3-dienyl bromide",e26,amounts=[field("mass",qty(3.364,"g"),e26)])],
    [step("bromination",["p2ab_1a","p2ab_pyr","p2ab_pbr3","p2ab_ether"],e26,temp=qty(-30,"°C"),solvent="diethyl ether",operation="warm to reflux")],
    [field("isolated_yield",qty(75,"%"),e26,["p2ab_product"]),field("yield_measurement_basis","isolated yield",e26,["p2ab_product"])],
    unresolved=["Reaction time and detailed workup are not reported in the visible text; product structure remains unverified."]))
records.append(record("prep_2a", "reported_experiment", e26,
    [participant("p2a_bromide","reactant","2-benzylbuta-2,3-dienyl bromide",e26,amounts=[field("mass",qty(1.682,"g"),e26),field("amount",qty(7.54,"mmol"),e26)]),participant("p2a_k2co3","reagent","K2CO3",e26,amounts=[field("mass",qty(1.264,"g"),e26),field("amount",qty(9.16,"mmol"),e26)]),participant("p2a_tsnh2","reactant","p-toluenesulfonamide",e26,amounts=[field("mass",qty(5.665,"g"),e26),field("amount",qty(33.1,"mmol"),e26)]),participant("p2a_acetone","solvent","acetone",e26,amounts=[field("volume",qty(40,"mL"),e26)]),participant("p2a_product","product","2a",e26,amounts=[field("mass",qty(1.053,"g"),e26)])],
    [step("amination",["p2a_bromide","p2a_k2co3","p2a_tsnh2","p2a_acetone"],e26,time=qty(5,"h"),temp="reflux",solvent="acetone",operation="heat to reflux")],
    [field("isolated_yield",qty(45,"%"),e26,["p2a_product"]),field("yield_measurement_basis","isolated yield",e26,["p2a_product"]),field("workup","cool; add ether; wash with brine three times; dry over anhydrous sodium sulfate; evaporate",e26),field("purification","flash chromatography on silica gel, petroleum ether/ether 3:1",e26)],
    unresolved=["Atmosphere is not reported; structures remain unverified and no SI was supplied."]))

records.append(record("prep_2d", "reported_experiment", e26,
    [participant("p2d_dipa","reactant","diisopropylamine",e26,amounts=[field("mass",qty(0.262,"g"),e26),field("amount",qty(2.59,"mmol"),e26)]),participant("p2d_nbli","reagent","n-butyllithium",e26,amounts=[field("volume",qty(1.30,"mL"),e26),field("concentration",qty(2.0,"M"),e26),field("amount",qty(2.60,"mmol"),e26)]),participant("p2d_3","reactant","propargylic ester 3",e26,amounts=[field("mass",qty(0.320,"g"),e26),field("amount",qty(0.88,"mmol"),e26)]),participant("p2d_zncl2","reagent","zinc chloride",e26,amounts=[field("mass",qty(0.154,"g"),e26),field("amount",qty(1.13,"mmol"),e26)]),participant("p2d_thf","solvent","THF",e26,amounts=[field("volume",qty(10,"mL"),e26)]),participant("p2d_ch2n2","reagent","diazomethane",e26),participant("p2d_ether","solvent","diethyl ether",e26),participant("p2d_product","product","2d",e26,amounts=[field("mass",qty(0.201,"g"),e26)])],
    [step("prepare_LDA",["p2d_dipa","p2d_nbli","p2d_thf"],e26,time=qty(30,"min"),temp=qty(0,"°C"),solvent="THF"),step("add_ester",["p2d_3"],e26,time=qty(10,"min"),temp=qty(-78,"°C"),solvent="THF"),step("add_zinc_chloride",["p2d_zncl2"],e26,time="overnight",temp="warm to r.t.",solvent="THF"),step("methylation",["p2d_ch2n2","p2d_ether"],e26,time=qty(10,"min"),temp=qty(-50,"°C"),solvent="diethyl ether")],
    [field("isolated_yield",qty(60,"%"),e26,["p2d_product"]),field("yield_measurement_basis","isolated yield",e26,["p2d_product"]),field("workup","dilute with ether; hydrolyze with 1 N HCl; extract with ether; dry over anhydrous sodium sulfate",e26),field("purification","flash chromatography on silica gel, petroleum ether/ether 2:1",e26)],
    unresolved=["Diazomethane amount is not reported; the stated THF total combines 3, 5, and 2 mL portions; structures remain unverified."]))

records.append(record("prep_5a", "reported_experiment", e26,
    [participant("p5a_4a","reactant","4a",e26,amounts=[field("mass",qty(1.542,"g"),e26),field("amount",qty(10.0,"mmol"),e26)]),participant("p5a_pph3","reagent","triphenylphosphine",e26,amounts=[field("mass",qty(3.932,"g"),e26),field("amount",qty(15.0,"mmol"),e26)]),participant("p5a_phth","reagent","phthalimide",e26,amounts=[field("mass",qty(1.471,"g"),e26),field("amount",qty(10.0,"mmol"),e26)]),participant("p5a_dead","reagent","DEAD",e26,amounts=[field("mass",qty(6.565,"g"),e26),field("concentration","40% in toluene",e26),field("amount",qty(15.0,"mmol"),e26)]),participant("p5a_thf","solvent","THF",e26,amounts=[field("volume",qty(40,"mL"),e26)]),participant("p5a_product","product","5a",e26,amounts=[field("mass",qty(2.573,"g"),e26)])],
    [step("mitsunobu_amination",["p5a_4a","p5a_pph3","p5a_phth","p5a_dead","p5a_thf"],e26,time="overnight",temp="ice bath to r.t.",solvent="THF",operation="DEAD added dropwise; warm to room temperature")],
    [field("isolated_yield",qty(91,"%"),e26,["p5a_product"]),field("yield_measurement_basis","isolated yield",e26,["p5a_product"]),field("purification","remove solvent; add ether; filter solid; evaporate; flash chromatography on silica gel",e26)],
    unresolved=["Chromatography eluent and atmosphere are not reported; structures remain unverified."]))

records.append(record("prep_6a", "reported_experiment", e26,
    [participant("p6a_5a","reactant","5a",e26,amounts=[field("mass",qty(1.270,"g"),e26),field("amount",qty(4.49,"mmol"),e26)]),participant("p6a_hyd","reagent","hydrazine hydrate",e26,amounts=[field("volume",qty(0.55,"mL"),e26),field("concentration","85% purity",e26),field("amount",qty(9.49,"mmol"),e26)]),participant("p6a_etoh","solvent","ethanol",e26,amounts=[field("volume",qty(20,"mL"),e26)]),participant("p6a_hcl","reagent","concentrated HCl",e26,amounts=[field("volume",qty(2,"mL"),e26)]),participant("p6a_naoh","reagent","NaOH",e26,amounts=[field("concentration",qty(1,"M"),e26)]),participant("p6a_et3n","reagent","triethylamine",e26,amounts=[field("volume",qty(0.70,"mL"),e26),field("amount",qty(5.06,"mmol"),e26)]),participant("p6a_tscl","reagent","tosyl chloride",e26,amounts=[field("mass",qty(0.855,"g"),e26),field("amount",qty(4.48,"mmol"),e26)]),participant("p6a_dcm","solvent","dichloromethane",e26,amounts=[field("volume",qty(20,"mL"),e26)]),participant("p6a_product","product","6a",e26,amounts=[field("mass",qty(1.018,"g"),e26)])],
    [step("hydrazinolysis",["p6a_5a","p6a_hyd","p6a_etoh"],e26,time=qty(1.5,"h"),temp="reflux",solvent="ethanol"),step("acid_base_workup",["p6a_hcl","p6a_naoh"],e26,temp="ice bath then ambient",operation="add HCl, filter, basify to pH >10, extract with ether"),step("tosylation",["p6a_et3n","p6a_tscl","p6a_dcm"],e26,time="overnight",temp="ice bath to r.t.",solvent="dichloromethane")],
    [field("isolated_yield",qty(74,"%"),e26,["p6a_product"]),field("yield_measurement_basis","isolated yield",e26,["p6a_product"]),field("workup","extract with ether (50 mL x 3), dry over anhydrous magnesium sulfate, concentrate",e26),field("purification","flash chromatography on silica gel",e26)],
    unresolved=["NaOH volume and chromatography eluent are not reported; structures remain unverified."]))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
