#!/usr/bin/env python3
"""Build evidence-linked machine records and the page 1-6 coverage ledger."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/pages_0001_0006_records.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
DOC = "doc_486fee074f5afc44"


def ev(*pages):
    return [eid for p in pages for eid in (f"{DOC}:page{p}:text", f"{DOC}:page{p}:image")]


def fact(value, evidence=()):
    return {"value": value, "evidence_ids": list(evidence),
            "verification": "missing" if value is None else "unreviewed"}


def fld(name, value, evidence=(), targets=()):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def q(number, unit, raw_text=None):
    result = {"number": number, "unit": unit}
    if raw_text is not None:
        result["raw_text"] = raw_text
    return result


def part(eid, role, label, name, evidence, smiles=None, amounts=()):
    return {
        "entity_id": eid, "role": role,
        "label": fact(label, evidence), "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles is not None else ()),
        "smiles_parseable": None, "structure_verified": False,
        "amounts": list(amounts),
    }


def rec(rid, source, kind, evidence, participants, steps, outcomes,
        notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}", "document_id": DOC,
        "source_reaction_id": source, "record_kind": kind,
        "status": "candidate", "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants, "steps": steps, "outcomes": outcomes,
        "notes": list(notes),
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": list(unresolved)},
    }


def mass_amount(mass, mmol, evidence):
    return [fld("mass", q(mass, "mg"), evidence),
            fld("amount", q(mmol, "mmol"), evidence)]


records = []
p1 = ev(1)
records.append(rec(
    "scheme1_generic_electrophilic_addition", "Scheme 1", "general_scheme", p1,
    [
        part("allene", "reactant", "generic substituted allene", None, p1),
        part("electrophile", "reagent", "E+", "generic electrophile", p1),
        part("nucleophile", "reagent", "Nu-", "generic nucleophile", p1),
        part("products", "product", "four generic regio-/stereoisomer classes", None, p1),
    ],
    [{"step_id": "electrophilic_addition_then_capture",
      "participant_ids": ["allene", "electrophile", "nucleophile", "products"],
      "conditions": [fld("operation", "1) E+; 2) Nu-", p1)]}],
    [],
    unresolved=["Generic R/E/Nu groups are not fully specified; no experiment-specific quantities, yield, or unique structures are reported."],
))
records.append(rec(
    "scheme2_generic_halohydroxylation_alkoxylation", "Scheme 2", "mechanism", p1,
    [
        part("allene", "reactant", "RY-substituted allene", None, p1),
        part("halogen", "reagent", "X+", "generic halogen electrophile", p1),
        part("hydroxide", "reagent", "OH-", "hydroxide/water-derived nucleophile", p1),
        part("alkoxide", "reagent", "RO-", "generic alkoxide", p1),
        part("halohydrin", "product", "Z-halohydroxylation product", None, p1),
        part("ether", "product", "Z-haloalkoxylation product", None, p1),
    ],
    [
        {"step_id": "halogen_addition", "participant_ids": ["allene", "halogen"],
         "conditions": [fld("operation", "proposed cyclic/cationic intermediate", p1)]},
        {"step_id": "nucleophile_capture",
         "participant_ids": ["hydroxide", "alkoxide", "halohydrin", "ether"],
         "conditions": [fld("operation", "generic OH- versus RO- capture pathways", p1)]},
    ],
    [],
    unresolved=["Mechanistic/generic scheme only; R, Y, X, and RO are not fully specified and no experiment-specific outcome is assigned."],
))

SMILES = {
    "1a": "C=C=C[Se]c1ccccc1", "1b": "C=C=CSc1ccccc1",
    "1c": "C=C=C[Se]Cc1ccccc1",
    "2a": r"CCOC/C(I)=C\\[Se]c1ccccc1",
    "2b": r"CC(C)COC/C(I)=C\\[Se]c1ccccc1",
    "2c": r"CCCCCOC/C(I)=C\\[Se]c1ccccc1",
    "2d": r"C1CCCCC1OC/C(I)=C\\[Se]c1ccccc1",
    "2e": r"c1ccccc1COC/C(I)=C\\[Se]c1ccccc1",
    "2f": r"CCOC/C(I)=C\\[Se]Cc1ccccc1",
    "2g": r"CCOC/C(I)=C\\Sc1ccccc1",
    "2h": r"C#CC(C)OC/C(I)=C\\[Se]c1ccccc1",
    "2i": r"CCCCC#CCOC/C(I)=C\\[Se]c1ccccc1",
    "2j": r"C=CCOC/C(I)=C\\[Se]c1ccccc1",
    "2k": r"C=CCOC/C(I)=C\\Sc1ccccc1",
    "2m": r"C#CCOC/C(I)=C\\[Se]c1ccccc1",
    "2n": r"C=CCOC/C(I)=C\\[Se]Cc1ccccc1",
    "2o": r"C#CCOC/C(I)=C\\[Se]Cc1ccccc1",
}
SUBSTRATES = {
    "1a": "1,2-propadienyl phenyl selenide",
    "1b": "1,2-propadienyl phenyl sulfide",
    "1c": "1,2-propadienyl benzyl selenide",
}
ALCOHOLS = {
    "ethanol": ("EtOH", "CCO"), "isobutanol": ("i-butanol", "CC(C)CO"),
    "pentan-1-ol": ("pentanol", "CCCCCO"),
    "cyclohexanol": ("cyclohexanol", "OC1CCCCC1"),
    "benzyl alcohol": ("BnOH", "OCC1=CC=CC=C1"),
    "but-3-yn-2-ol": ("but-3-yn-2-ol", "C#CC(C)O"),
    "hept-2-yn-1-ol": ("hept-2-yn-1-ol", "CCCCC#CCO"),
    "allyl alcohol": ("allyl alcohol", "C=CCO"),
    "prop-2-yn-1-ol": ("prop-2-ynol", "C#CCO"),
}

# rid, source, product, substrate, alcohol, pages, substrate mass/mmol,
# iodine mass/mmol, MeCN mL, alcohol mL, product mg, yield, time, temp,
# basis, name, extra unresolved
iodo = [
("table1_entry5_product_2a","Table 1 entry 5 / Table 2 entry 1 / section 3.1.1","2a","1a","ethanol",(2,3),50.4,.26,128.3,.51,5,.25,64.7,68,1,"r.t.","isolated yield","(Z)-3-ethoxy-2-iodopropenyl phenyl selenide",["Table 1 footnote rounds the charge to 0.25 mmol 1a and 0.5 mmol I2, while section 3.1.1 reports 0.26 mmol and 0.51 mmol; detailed values are structured and the discrepancy is retained."]),
("scope_product_2b","Table 2 entry 2 / section 3.1.2","2b","1a","isobutanol",(2,3,4),51.5,.26,123.6,.49,5,.25,65.4,63,1,"r.t.","isolated yield","(Z)-3-isobutoxy-2-iodopropenyl phenyl selenide",[]),
("scope_product_2c","Table 2 entry 3 / section 3.1.3","2c","1a","pentan-1-ol",(2,4),52.4,.27,130.3,.51,5,.25,83.1,76,1,"r.t.","isolated yield","(Z)-3-pentoxy-2-iodopropenyl phenyl selenide",[]),
("scope_product_2d","Table 2 entry 4 / section 3.1.4","2d","1a","cyclohexanol",(2,4),47.2,.25,131.4,.5,5,.3,81.5,80,1,"r.t.","isolated yield","(Z)-3-cyclohexoxy-2-iodopropenyl phenyl selenide",[]),
("scope_product_2e","Table 2 entry 5 / section 3.1.5","2e","1a","benzyl alcohol",(2,4),47.1,.25,132.4,.5,5,.3,79.5,77,1,"r.t.","isolated yield","(Z)-3-benzoxy-2-iodopropenyl phenyl selenide",[]),
("scope_product_2f","Table 2 entry 6 / section 3.1.6","2f","1c","ethanol",(2,4),52.9,.26,128.3,.5,5,.25,61.0,64,1,"r.t.","isolated yield","(Z)-3-ethoxy-2-iodopropenyl benzyl selenide",[]),
("scope_product_2g","Table 2 entry 7 / section 3.1.7","2g","1b","ethanol",(2,4),74.6,.50,259.4,1.02,8,.4,79.0,49,1,"r.t.","isolated yield","(Z)-3-ethoxy-2-iodopropenyl phenyl sulfide",[]),
("scheme3_product_2h","Scheme 3 / section 3.1.8","2h","1a","but-3-yn-2-ol",(2,4),49.1,.25,131.7,.51,5,.25,60.1,61,None,None,None,"(Z)-3-(but-3-yn-2-yloxy)-2-iodopropenyl phenyl selenide",[]),
("scheme3_product_2i","Scheme 3 / section 3.1.9","2i","1a","hept-2-yn-1-ol",(2,4),47.1,.25,127.1,.50,5,.25,61.2,58,None,None,None,"(Z)-3-(hept-2-ynoxy)-2-iodopropenyl phenyl selenide",[]),
("scheme3_product_2j","Scheme 3 / section 3.1.10","2j","1a","allyl alcohol",(2,4,5),98.8,.51,255.0,1.00,8,.4,121.5,63,None,None,None,"(Z)-3-allyloxy-2-iodopropenyl phenyl selenide",[]),
("scheme3_product_2k","Scheme 3 / section 3.1.11","2k","1b","allyl alcohol",(2,5),82.1,.55,255.5,1.01,8,.4,74.4,40,None,None,None,"(Z)-3-allyloxy-2-iodopropenyl phenyl sulfide",[]),
("scheme3_product_2m","Scheme 3 / section 3.1.12","2m","1a","prop-2-yn-1-ol",(2,5),53.8,.28,129.8,.51,5,.25,53.1,51,None,None,None,"(Z)-3-(prop-2-ynoxy)-2-iodopropenyl phenyl selenide",[]),
("scheme4_product_2n","Scheme 4 / section 3.1.13","2n","1c","allyl alcohol",(3,5),87.1,.42,222.1,.87,8,4,49.8,30,None,None,None,"(Z)-3-allyloxy-2-iodopropenyl benzyl selenide",["Section 3.1.13 prints 8 mL MeCN and 4 mL allyl alcohol while also printing a 20:1 ratio; these values are internally inconsistent and are preserved without correction."]),
("scheme4_product_2o","Scheme 4 / section 3.1.14","2o","1c","prop-2-yn-1-ol",(3,5),86.1,.41,205.2,.81,8,.4,41.1,26,None,None,None,"(Z)-3-(prop-2-ynoxy)-2-iodopropenyl benzyl selenide",[]),
]

for row in iodo:
    (rid, source, product, substrate, alcohol, pages, smass, smmol, imass,
     immol, mecn, avol, pmass, yld, hours, temp, basis, pname, extra) = row
    evidence = ev(*pages)
    alabel, asmiles = ALCOHOLS[alcohol]
    participants = [
        part("substrate","reactant",substrate,SUBSTRATES[substrate],evidence,SMILES[substrate],mass_amount(smass,smmol,evidence)),
        part("iodine","reagent","I2","iodine",evidence,"II",mass_amount(imass,immol,evidence)),
        part("alcohol","reactant",alabel,alcohol,evidence,asmiles,[fld("volume",q(avol,"mL"),evidence)]),
        part("acetonitrile","solvent","MeCN","acetonitrile",evidence,"CC#N",[fld("volume",q(mecn,"mL"),evidence)]),
        part("product","product",product,pname,evidence,SMILES[product],[fld("mass",q(pmass,"mg"),evidence)]),
    ]
    conditions = [fld("solvent","MeCN/alcohol",evidence),fld("MeCN/alcohol ratio","20:1",evidence),
                  fld("time",q(hours,"h"),evidence) if hours is not None else fld("time",None),
                  fld("temperature",temp,evidence) if temp is not None else fld("temperature",None)]
    unresolved = ["Candidate SMILES are machine interpretations of named/drawn structures and remain unverified.",
                  "No supporting information was explicitly associated with this source."]
    if hours is None or temp is None:
        unresolved.append("Reaction time and/or temperature are not explicitly stated for this individual example on the inspected pages.")
    if basis is None:
        unresolved.append("Yield measurement basis is not explicitly stated for this individual example.")
    unresolved.extend(extra)
    records.append(rec(
        rid, source, "optimization_entry" if product == "2a" else "substrate_scope_entry",
        evidence, participants,
        [{"step_id":"iodoalkoxylation","participant_ids":[p["entity_id"] for p in participants],"conditions":conditions}],
        [fld("yield",q(yld,"%"),evidence,["product"]),
         fld("yield_measurement_basis",basis,evidence if basis else (),["product"])],
        notes=[fact("Product physical state: liquid.",evidence)],
        unresolved=unresolved,
    ))

# Table 1 optimization rows other than entry 5, which is merged with detailed 2a.
p2 = ev(2)
optimization = [
    (1,"1:1",1.5,59,"r.t.",2.0,.5),
    (2,"4:1",1.5,50,"r.t.",2.0,.5),
    (3,"9:1",1.0,55,"r.t.",2.0,.5),
    (4,"27:1",1.5,17,"r.t.",2.0,.5),
    (6,"20:1",2.5,48,q(0,"°C"),2.0,.5),
    (7,"20:1",1.0,45,q(30,"°C"),2.0,.5),
    (8,"20:1",1.0,54,"r.t.",1.5,None),
    (9,"20:1",1.0,54,"r.t.",3.0,None),
]
for entry, ratio, hours, yld, temp, iequiv, immol in optimization:
    iamounts = [fld("equivalents",q(iequiv,"equiv"),p2)]
    if immol is not None:
        iamounts.insert(0,fld("amount",q(immol,"mmol"),p2))
    participants = [
        part("substrate","reactant","1a",SUBSTRATES["1a"],p2,SMILES["1a"],[fld("amount",q(.25,"mmol"),p2)]),
        part("iodine","reagent","I2","iodine",p2,"II",iamounts),
        part("ethanol","reactant","EtOH","ethanol",p2,"CCO",[fld("volume",q(.25,"mL"),p2)]),
        part("acetonitrile","solvent","MeCN","acetonitrile",p2,"CC#N"),
        part("product","product","2a","(Z)-3-ethoxy-2-iodopropenyl phenyl selenide",p2,SMILES["2a"]),
    ]
    records.append(rec(
        f"table1_entry{entry}",f"Table 1 entry {entry}","optimization_entry",p2,participants,
        [{"step_id":"iodoethoxylation","participant_ids":[p["entity_id"] for p in participants],
          "conditions":[fld("MeCN/EtOH ratio",ratio,p2),fld("time",q(hours,"h"),p2),fld("temperature",temp,p2)]}],
        [fld("yield",q(yld,"%"),p2,["product"]),fld("yield_measurement_basis","isolated yield",p2,["product"])],
        unresolved=["Candidate SMILES are machine interpretations of the source drawing and remain unverified.",
                    "No supporting information was explicitly associated with this source."],
    ))


def cp(eid, role, label, name, evidence, smiles=None, mass=None, mmol=None,
       volume=None, molpct=None, concentration=None):
    amounts = []
    if mass is not None: amounts.append(fld("mass",q(mass,"mg"),evidence))
    if mmol is not None: amounts.append(fld("amount",q(mmol,"mmol"),evidence))
    if volume is not None: amounts.append(fld("volume",q(volume,"mL"),evidence))
    if molpct is not None: amounts.append(fld("catalyst_loading",q(molpct,"mol%"),evidence))
    if concentration is not None: amounts.append(fld("concentration",q(concentration,"M"),evidence))
    return part(eid,role,label,name,evidence,smiles,amounts)


PRODUCT_SMILES = {
    "3aa":r"CCOC/C(c1ccccc1)=C\\[Se]c1ccccc1",
    "3ab":r"CCOC/C(c1ccc(OC)cc1)=C\\[Se]c1ccccc1",
    "3ac":r"CCOC/C(c1ccc(C)cc1)=C\\[Se]c1ccccc1",
    "3ad":r"CCOC/C(c1ccc(C(C)=O)cc1)=C\\[Se]c1ccccc1",
    "3ae":r"CCOC/C(C#Cc1ccccc1)=C\\[Se]c1ccccc1",
    "3af":r"CCOC/C(CCCC)=C\\[Se]c1ccccc1",
}

# product, source, pages, 2a mass/mmol, boronic name/label/smiles/mass/mmol,
# catalyst mass/mol%, time, product mass, yield, product name, atmosphere, basis, conflict
suzuki = [
("3aa","Table 3 entry 1 / section 3.1.15",(3,5),100.6,.27,"phenylboronic acid","PhB(OH)2","OB(O)c1ccccc1",60.6,.51,14.7,5,22.5,68.5,79,"(E)-3-ethoxy-2-phenylpropenyl phenyl selenide","N2","product obtained after column chromatography",False),
("3ab","Table 3 entry 2 / section 3.1.16",(3,5),88.9,.24,"4-methoxyphenylboronic acid","4-MeOC6H4B(OH)2","COc1ccc(B(O)O)cc1",72.6,.48,15.1,5,17.5,64.2,76,"(E)-3-ethoxy-2-(4-methoxyphenyl)propenyl phenyl selenide",None,None,False),
("3ac","Table 3 entry 3 / section 3.1.17",(3,5),88.3,.24,"4-methylphenylboronic acid","4-MeC6H4B(OH)2","Cc1ccc(B(O)O)cc1",66.3,.49,18.4,6,17.5,59.9,75,"(E)-3-ethoxy-2-(4-methylphenyl)propenyl phenyl selenide",None,None,True),
("3ad","Table 3 entry 4 / section 3.1.18",(3,5,6),96.9,.26,"4-acetylphenylboronic acid","4-MeCOC6H4B(OH)2","CC(=O)c1ccc(B(O)O)cc1",86.4,.53,21.6,6,22.5,36.9,39,"(E)-3-ethoxy-2-(4-acetylphenyl)propenyl phenyl selenide",None,None,True),
]
for row in suzuki:
    (product, source, pages, rmass, rmmol, bname, blabel, bsmiles, bmass,
     bmmol, cmass, cmolpct, hours, pmass, yld, pname, atmosphere, basis, conflict) = row
    evidence = ev(*pages)
    participants = [
        cp("reactant_2a","reactant","2a","(Z)-3-ethoxy-2-iodopropenyl phenyl selenide",evidence,SMILES["2a"],rmass,rmmol),
        cp("boronic_acid","reactant",blabel,bname,evidence,bsmiles,bmass,bmmol),
        cp("pd_catalyst","catalyst","Pd(PPh3)4","tetrakis(triphenylphosphine)palladium",evidence,None,cmass,molpct=cmolpct),
        cp("methanol","solvent","CH3OH","methanol",evidence,"CO",volume=.1),
        cp("sodium_carbonate","reagent","Na2CO3","sodium carbonate",evidence,"[Na+].[Na+].[O-]C([O-])=O",volume=.3,concentration=2),
        cp("toluene","solvent","toluene","toluene",evidence,"Cc1ccccc1",volume=2),
        cp("product","product",product,pname,evidence,PRODUCT_SMILES[product],mass=pmass),
    ]
    conditions = [fld("temperature",q(100,"°C"),evidence),fld("operation","reflux",evidence),
                  fld("time",q(hours,"h"),evidence),
                  fld("atmosphere",atmosphere,evidence if atmosphere else ())]
    unresolved = ["Candidate SMILES are machine interpretations of named/drawn structures and remain unverified.",
                  "No supporting information was explicitly associated with this source."]
    if basis is None:
        unresolved.append("Yield measurement basis and individual workup/purification are not explicitly stated for this example.")
    if conflict:
        unresolved.append("Table 3 scheme prints 5 mol% Pd(PPh3)4, whereas the detailed example reports 6 mol%; the detailed loading is structured and the conflict retained.")
    records.append(rec(
        f"table3_product_{product}",source,"substrate_scope_entry",evidence,participants,
        [{"step_id":"suzuki_coupling","participant_ids":[p["entity_id"] for p in participants],"conditions":conditions}],
        [fld("yield",q(yld,"%"),evidence,["product"]),fld("yield_measurement_basis",basis,evidence if basis else (),["product"])],
        unresolved=unresolved,
    ))

# Sonogashira experiment 3ae.
evidence = ev(3,6)
participants = [
    cp("reactant_2a","reactant","2a","(Z)-3-ethoxy-2-iodopropenyl phenyl selenide",evidence,SMILES["2a"],87.3,.24),
    cp("phenylacetylene","reactant","PhCCH","phenylacetylene",evidence,"C#Cc1ccccc1",38.9,.38),
    cp("diethylamine","reagent","Et2NH","diethylamine",evidence,"CCNCC",21.1,.289),
    cp("cui","catalyst","CuI","copper(I) iodide",evidence,"[Cu]I",5.7,molpct=10),
    cp("pd_catalyst","catalyst","PdCl2(PPh3)2","bis(triphenylphosphine)palladium(II) dichloride",evidence,None,8.6,molpct=5),
    cp("acetonitrile","solvent","CH3CN","acetonitrile",evidence,"CC#N",volume=2.5),
    cp("product","product","3ae","(E)-3-ethoxy-2-(phenylethynyl)propenyl phenyl selenide",evidence,PRODUCT_SMILES["3ae"],mass=53.7),
]
records.append(rec(
    "scheme5_product_3ae","Scheme 5 / section 3.1.19","reported_experiment",evidence,participants,
    [{"step_id":"sonogashira_coupling","participant_ids":[p["entity_id"] for p in participants],
      "conditions":[fld("temperature","r.t.",evidence),fld("atmosphere","N2",evidence),fld("time",q(24,"h"),evidence),
                    fld("operation","monitored by TLC",evidence),
                    fld("purification","column chromatography on silica gel; petroleum ether/ethyl acetate 200:1",evidence)]}],
    [fld("yield",q(66,"%"),evidence,["product"]),
     fld("yield_measurement_basis","product obtained after column chromatography",evidence,["product"])],
    unresolved=["Candidate SMILES are machine interpretations of named/drawn structures and remain unverified.",
                "No supporting information was explicitly associated with this source."],
))

# Two-stage in-situ organozinc preparation and Negishi experiment 3af.
evidence = ev(3,6)
participants = [
    cp("zinc_bromide","reagent","ZnBr2","anhydrous zinc bromide",evidence,"Br[Zn]Br",145.4,.65),
    cp("n_butyllithium","reagent","n-C4H9Li","n-butyllithium",evidence,"[Li]CCCC",volume=.18,concentration=2.88),
    cp("hexane","solvent","hexane","hexane",evidence,"CCCCCC"),
    cp("thf","solvent","THF","tetrahydrofuran",evidence,"C1CCOC1",volume=3.0),
    cp("pd_catalyst","catalyst","Pd(PPh3)4","tetrakis(triphenylphosphine)palladium",evidence,None,20.2,molpct=8),
    cp("reactant_2a","reactant","2a","(Z)-3-ethoxy-2-iodopropenyl phenyl selenide",evidence,SMILES["2a"],79.0,.22),
    cp("product","product","3af","(E)-3-ethoxy-2-butylpropenyl phenyl selenide",evidence,PRODUCT_SMILES["3af"],mass=39.8),
]
records.append(rec(
    "scheme5_product_3af","Scheme 5 / section 3.1.20","reported_experiment",evidence,participants,
    [
        {"step_id":"organozinc_preparation","participant_ids":["zinc_bromide","n_butyllithium","hexane","thf"],
         "conditions":[fld("temperature",q(0,"°C"),evidence),fld("time",q(10,"min"),evidence),
                       fld("operation","n-C4H9Li added dropwise to ZnBr2 in THF",evidence)]},
        {"step_id":"negishi_coupling","participant_ids":["pd_catalyst","reactant_2a","thf","product"],
         "conditions":[fld("temperature",q(0,"°C"),evidence),fld("time",q(21.5,"h"),evidence),
                       fld("operation","monitored by TLC",evidence),fld("purification","column chromatography on silica gel",evidence)]},
    ],
    [fld("yield",q(62,"%"),evidence,["product"]),
     fld("yield_measurement_basis","product obtained after column chromatography",evidence,["product"])],
    notes=[fact("Scheme 5 denotes n-C4H9ZnBr; section 3.1.20 describes its in-situ preparation from ZnBr2 and n-C4H9Li.",evidence)],
    unresolved=["Candidate SMILES are machine interpretations of named/drawn structures and remain unverified.",
                "No supporting information was explicitly associated with this source.",
                "The detailed text does not explicitly state that the entire coupling stage remained at 0 °C; Scheme 5 prints 0 °C on the coupling arrow."],
))


def ids_for_page(page):
    marker = f":page{page}:"
    return [r["record_id"] for r in records if any(marker in eid for eid in r["evidence_ids"])]


pages = [
{
"page":1,"state":"attempted",
"regions":[
{"region":"title, abstract, and introduction columns","finding":"Article context and claims only; cited prior halohydroxylation work lacks experiment-level details for this paper.","evidence_ids":ev(1)},
{"region":"lower-left Scheme 1","finding":"Generic electrophilic addition/regio-stereochemical outcome scheme; classified as a general scheme, not a reported experiment.","evidence_ids":ev(1)},
{"region":"lower-right Scheme 2","finding":"Generic/proposed OH versus OR nucleophile-capture network; classified as mechanism, not a reported experiment.","evidence_ids":ev(1)}],
"record_ids":ids_for_page(1),
"unresolved":["Generic R, E, Nu, X, and Y groups do not permit unique structures or experiment-specific conditions."]},
{
"page":2,"state":"attempted",
"regions":[
{"region":"upper-left Table 1 including reaction drawing and footnotes a-f","finding":"Nine iodoethoxylation optimization rows inspected individually; entry 5 is merged with the detailed 2a procedure and the other eight remain independent records.","evidence_ids":ev(2)},
{"region":"middle-left Table 2 including reaction drawing and footnotes","finding":"Seven alcohol/substrate scope rows 2a-2g; each is merged with its matching detailed procedure rather than duplicated.","evidence_ids":ev(2)},
{"region":"right-column results/discussion","finding":"Narrative reports high Z selectivity, NOE assignment for 2a, and downstream couplings; no narrative-only experiment was added.","evidence_ids":ev(2)},
{"region":"lower-right Scheme 3","finding":"Five visible products 2h, 2i, 2j, 2k, and 2m; each is linked to its detailed procedure. No 2l arrow is present.","evidence_ids":ev(2)}],
"record_ids":ids_for_page(2),
"unresolved":["Scheme 3 omits reaction time, temperature, and yield basis; these remain missing for 2h, 2i, 2j, 2k, and 2m."]},
{
"page":3,"state":"attempted",
"regions":[
{"region":"upper Scheme 4","finding":"Two benzyl-selenide iodoalkoxylations to 2n and 2o at 30% and 26%, merged with sections 3.1.13 and 3.1.14.","evidence_ids":ev(3)},
{"region":"middle Table 3 including shared arrow conditions","finding":"Four row-specific Suzuki couplings to 3aa-3ad, linked to detailed examples.","evidence_ids":ev(3)},
{"region":"middle-lower Scheme 5","finding":"One Sonogashira arrow to 3ae and one Negishi arrow to 3af; each retained separately.","evidence_ids":ev(3)},
{"region":"lower experimental section 3.1 through 3.1.2","finding":"Typical 2a procedure and detailed 2a/2b quantities; 2a is merged with Table 1 entry 5 and Table 2 entry 1.","evidence_ids":ev(3)}],
"record_ids":ids_for_page(3),
"unresolved":["Detailed 2b characterization continues on page 4 and is represented by one cross-page record."]},
{
"page":4,"state":"attempted",
"regions":[
{"region":"top continuation of section 3.1.2","finding":"Continuation of 2b characterization only; no new experiment.","evidence_ids":ev(4)},
{"region":"sections 3.1.3-3.1.7","finding":"Detailed quantities and outcomes for 2c-2g, merged with matching Table 2 rows.","evidence_ids":ev(4)},
{"region":"sections 3.1.8-3.1.10","finding":"Detailed quantities/outcomes for 2h and 2i and the beginning of 2j; each matched to Scheme 3.","evidence_ids":ev(4)}],
"record_ids":ids_for_page(4),
"unresolved":["Sections do not restate all reaction times/temperatures; only values explicitly supplied by matching table rows are structured."]},
{
"page":5,"state":"attempted",
"regions":[
{"region":"top continuation of section 3.1.10 and sections 3.1.11-3.1.14","finding":"Completion of 2j characterization and detailed examples 2k, 2m, 2n, and 2o; matched to Schemes 3 and 4.","evidence_ids":ev(5)},
{"region":"sections 3.1.15-3.1.18","finding":"Detailed Suzuki examples 3aa-3ad; page ends after the 3ad preparation sentence, whose characterization continues on page 6.","evidence_ids":ev(5)}],
"record_ids":ids_for_page(5),
"unresolved":["Section 3.1.13 prints 8 mL MeCN plus 4 mL allyl alcohol and also 20:1; no correction was inferred.","The visible numbering skips 2l; no record was fabricated."]},
{
"page":6,"state":"attempted",
"regions":[
{"region":"upper-left continuation of section 3.1.18","finding":"3ad characterization continuation only; merged into the 3ad record.","evidence_ids":ev(6)},
{"region":"section 3.1.19","finding":"Full Sonogashira procedure to 3ae with loadings, N2, room temperature, 24 h, chromatography, product mass, and 66% yield.","evidence_ids":ev(6)},
{"region":"section 3.1.20","finding":"Two-stage in-situ organozinc preparation and Negishi coupling to 3af with explicit quantities, 0 °C, 10 min and 21.5 h stages, product mass, and 62% yield.","evidence_ids":ev(6)},
{"region":"acknowledgements and references","finding":"No current-paper reaction experiment; references are citations only.","evidence_ids":ev(6)}],
"record_ids":ids_for_page(6),
"unresolved":["For 3af, the text and Scheme 5 do not make the full second-stage temperature history completely explicit."]},
]

OUT.write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n")
COVERAGE.parent.mkdir(parents=True,exist_ok=True)
COVERAGE.write_text(json.dumps({"document_id":DOC,"semantic_accuracy_verified":False,"pages":pages},ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"records":len(records),"record_file":str(OUT),"coverage_file":str(COVERAGE)},ensure_ascii=False))
