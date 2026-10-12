#!/usr/bin/env python3
"""Build evidence-linked machine records for source.pdf pages 1--6."""
import json
from pathlib import Path

DOC = "doc_6b8369a38afea515"
OUT = Path(__file__).with_name("extracted_records_pages_0001_0006.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {"value": value, "evidence_ids": list(evidence) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


SMILES = {
    "diethyl malonate": "CCOC(=O)CC(=O)OCC",
    "potassium carbonate": "[K+].[K+].[O-]C([O-])=O",
    "sodium carbonate": "[Na+].[Na+].[O-]C([O-])=O",
    "acetone": "CC(=O)C", "ethanol": "CCO", "acetonitrile": "CC#N",
    "dichloromethane": "ClCCl", "DMF": "CN(C)C=O", "THF": "C1CCOC1",
    "diethyl ether": "CCOCC", "triethylamine": "CCN(CC)CC",
    "DMSO": "CS(C)=O", "oxalyl chloride": "O=C(Cl)C(=O)Cl",
    "1-bromohexane": "CCCCCCBr", "potassium iodide": "[K+].[I-]",
    "bromine": "BrBr", "triphenylphosphine": "P(c1ccccc1)(c1ccccc1)c1ccccc1",
    "stannous chloride": "Cl[Sn]Cl", "sodium iodide": "[Na+].[I-]",
    "nonanal": "CCCCCCCCC=O", "magnesium": "[Mg]", "mercuric chloride": "Cl[Hg]Cl",
    "heptanal": "CCCCCCC=O", "propargyl bromide": "C#CCBr",
    "n-butyllithium": "[Li]CCCC", "N,N-dimethylacetamide": "CC(=O)N(C)C",
}


def participant(entity_id, role, evidence, label=None, name=None, amounts=None, smiles=None):
    if smiles is None and name in SMILES:
        smiles = SMILES[name]
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


def qty(name, number, unit, evidence, raw=None):
    value = {"number": number, "unit": unit}
    if raw:
        value["raw_text"] = raw
    return field(name, value, evidence)


def rec(suffix, source_id, kind, evidence, participants, steps, outcomes=None,
        notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}", "document_id": DOC,
        "source_reaction_id": source_id, "record_kind": kind,
        "status": "candidate", "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)), "participants": participants,
        "steps": steps, "outcomes": outcomes or [], "notes": notes or [],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved or [
                       "Supporting information was not supplied or explicitly associated.",
                       "Machine-extracted structures and source assignments require review."]},
    }


ALLENE_NAMES = {
    "1a": "3-butylpenta-3,4-dien-2-one", "1b": "3-ethylpenta-3,4-dien-2-one",
    "1c": "3-hexylpenta-3,4-dien-2-one", "1d": "3-allylpenta-3,4-dien-2-one",
    "1e": "3-benzylpenta-3,4-dien-2-one", "1f": "3-pentyldodeca-1,2-dien-4-one",
    "1g": "5-methylhexa-3,4-dien-2-one", "1h": "2-methylundeca-2,3-dien-5-one",
    "1i": "dodeca-3,4-dien-2-one", "1j": "nona-3,4-dien-2-one",
    "1k": "octadeca-9,10-dien-8-one", "1l": "3-butyldeca-3,4-dien-2-one",
    "1s": "octa-1,2-dien-4-one", "1t": "nona-1,2-dien-4-one",
    "1u": "deca-1,2-dien-4-one", "1v": "dodeca-1,2-dien-4-one",
    "1w": "penta-3,4-dien-2-one", "1x": "1-phenylbuta-2,3-dien-1-one",
    "1y": "1-phenylpenta-3,4-dien-2-one",
}


records = []

# Scheme 1 is a generic reaction network, not an individual reported experiment.
records.append(rec(
    "scheme1_generic_network", "Scheme 1", "general_scheme", ev(2),
    [participant("generic_allene_1", "reactant", ev(2), "1", "generic 1,2-allenic ketone"),
     participant("malonate_2", "reactant", ev(2), "2", "diethyl malonate"),
     participant("generic_3", "product", ev(2), "3", "unmigrated beta,gamma-unsaturated enone"),
     participant("generic_4", "product", ev(2), "4", "double-bond-migrated enone"),
     participant("generic_6", "product", ev(2), "6", "alpha-pyrone")],
    [{"step_id": "generic_addition_migration_lactonization",
      "participant_ids": ["generic_allene_1", "malonate_2", "generic_3", "generic_4", "generic_6"],
      "conditions": [field("base", "base", ev(2)), field("solvent", "solvent", ev(2))]}],
    notes=[fact("Generic network only; intermediates 3/4/5 and pyrone 6 are alternatives or successive stages.", ev(2))],
    unresolved=["Scheme 1 uses R groups and does not define a single experimental substrate or condition."]
))


def generic_starting_record(scheme, label, descriptors, page=2):
    evidence = ev(page)
    product_name = ALLENE_NAMES.get(label, f"1,2-allenic ketone {label} ({descriptors})")
    ps = [participant("starting_materials", "reactant", evidence, None,
                      f"scheme {scheme} precursor(s); {descriptors}"),
          participant("product", "product", evidence, label, product_name)]
    conditions = [field("operation", f"preparation route shown in Scheme {scheme}", evidence)]
    return rec(f"scheme{scheme}_{label}", f"Scheme {scheme}, {label}",
               "substrate_scope_entry", evidence, ps,
               [{"step_id": "scheme_route", "participant_ids": ["starting_materials", "product"],
                 "conditions": conditions}],
               unresolved=["Supporting information was not supplied or explicitly associated.",
                           "The scheme is a route summary; detailed quantities and yields are absent on this page.",
                           "The precursor drawing/R-group expansion was not converted to a verified SMILES."])


scheme_variants = {
    2: {"1a": "R3=n-C4H9", "1b": "R3=Et", "1c": "R3=n-C6H13",
        "1d": "R3=allyl", "1e": "R3=Bn", "1w": "R3=H"},
    3: {"1f": "n-C5H11-substituted alkynyl bromide and nonanal; Swern oxidation"},
    4: {"1g": "R4=Me", "1h": "R4=n-C6H13"},
    5: {"1i": "R1=n-C7H15, R4=Me", "1j": "R1=n-C4H9, R4=Me",
        "1k": "R1=n-C7H15, R4=n-C7H15"},
    6: {"1l": "R3=n-C4H9, R4=Me", "1m": "R3=n-C4H9, R4=n-C7H15",
        "1n": "R3=n-C4H9, R4=Ph", "1o": "R3=n-C4H9, R4=Tolyl",
        "1p": "R3=n-C5H11, R4=Me", "1q": "R3=n-C5H11, R4=n-C7H15",
        "1r": "R3=n-C5H11, R4=Ph"},
    7: {"1s": "R4=n-C4H9", "1t": "R4=n-C5H11", "1u": "R4=n-C6H13",
        "1v": "R4=n-C8H17"},
    8: {"1x": "R4=Ph", "1y": "R4=Bn"},
}
for scheme, variants in scheme_variants.items():
    for label, descriptors in variants.items():
        records.append(generic_starting_record(scheme, label, descriptors, 3 if scheme == 8 else 2))


def allene_part(label, evidence, role="reactant", descriptors=None):
    return participant("allene", role, evidence, label,
                       ALLENE_NAMES.get(label, f"1,2-allenic ketone {label} ({descriptors or 'substituents in table'})"))


def malonate_part(evidence):
    return participant("malonate", "reactant", evidence, "2", "diethyl malonate")


def catalyst_part(name, evidence, value):
    return participant("catalyst", "catalyst", evidence, None, name,
                       [field("loading", value, evidence)])


def solvent_part(name, evidence):
    return participant("solvent", "solvent", evidence, None, name)


def table_record(suffix, source_id, page, label, descriptors, solvent, temp, time,
                 products, yields, kind="substrate_scope_entry", catalyst="potassium carbonate",
                 loading=None, selectivity=None, ratio_basis=None, extra_notes=None):
    evidence = ev(page)
    ps = [allene_part(label, evidence, descriptors=descriptors), malonate_part(evidence)]
    if loading is not None:
        ps.append(catalyst_part(catalyst, evidence, loading))
    else:
        ps.append(participant("catalyst", "catalyst", evidence, None, catalyst))
    ps.append(solvent_part(solvent, evidence))
    for product_label, product_name in products:
        ps.append(participant(f"product_{product_label}", "product", evidence,
                              product_label, product_name))
    conditions = [field("solvent", solvent, evidence), field("temperature", temp, evidence),
                  field("time", time, evidence)]
    outcomes = []
    for target, value in yields:
        outcomes.append(field("yield", value, evidence, [f"product_{target}"]))
    if selectivity:
        outcomes.append(field(selectivity[0], selectivity[1], evidence,
                              [f"product_{p[0]}" for p in products]))
    if ratio_basis:
        outcomes.append(field("selectivity_measurement_basis", ratio_basis, evidence,
                              [f"product_{p[0]}" for p in products]))
    unresolved = ["Supporting information was not supplied or explicitly associated.",
                  "The table does not state the yield measurement basis.",
                  "Product and substrate drawings/R-group expansions were not assigned verified SMILES."]
    return rec(suffix, source_id, kind, evidence, ps,
               [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps],
                 "conditions": conditions}], outcomes,
               notes=[fact(x, evidence) for x in (extra_notes or [])], unresolved=unresolved)


# Table 1: entries 1--6 are solvent/time optimization; 7--9 are substrate scope.
t1 = [
    (1, "1a", "R3=n-C4H9, R4=CH3", "acetonitrile", "r.t.", {"number": 16, "unit": "h"}, [("4a",48),("6a",25)]),
    (2, "1a", "R3=n-C4H9, R4=CH3", "dichloromethane", {"number":60,"unit":"°C"}, {"number":2.5,"unit":"d"}, [("4a",57),("6a",28)]),
    (3, "1a", "R3=n-C4H9, R4=CH3", "DMF", "r.t.", {"number":10,"unit":"h"}, [("4a",36),("6a",34)]),
    (4, "1a", "R3=n-C4H9, R4=CH3", "ethanol", "r.t.", {"number":24,"unit":"h"}, [("4a",65),("6a",27)]),
    (5, "1a", "R3=n-C4H9, R4=CH3", "DMF/dichloromethane (1:1)", "r.t.", {"number":4,"unit":"d"}, [("4a",47)]),
    (6, "1a", "R3=n-C4H9, R4=CH3", "acetone", {"number":60,"unit":"°C"}, {"number":8,"unit":"h"}, [("4a",57),("6a",3)]),
    (7, "1c", "R3=n-C6H13, R4=CH3", "acetone", "reflux", {"number":12,"unit":"h"}, [("4c",67),("6c",27)]),
    (8, "1e", "R3=Bn, R4=CH3", "acetone", "reflux", {"number":8,"unit":"h"}, [("4e",56)]),
    (9, "1f", "R3=n-C5H11, R4=n-C8H17", "acetone", "reflux", {"number":24,"unit":"h"}, [("4f",85)]),
]
for entry, label, desc, solvent, temp, time, ys in t1:
    products = [(p, f"reported product {p}") for p, _ in ys]
    yields = [(p, {"number": y, "unit": "%"}) for p, y in ys]
    records.append(table_record(f"table1_entry{entry:02d}", f"Table 1 entry {entry}", 3,
                                label, desc, solvent, temp, time, products, yields,
                                "optimization_entry" if entry <= 6 else "substrate_scope_entry",
                                loading={"number":10,"unit":"mol%"},
                                extra_notes=["Table 1 footnote a supplies DMF/CH2Cl2 (1:1) for entry 5."] if entry == 5 else None))


# Table 2.
t2 = [
    (1,"1g","R1=CH3, R2=CH3, R3=H, R4=CH3","acetone","reflux",9,"h",75,None),
    (2,"1g","R1=CH3, R2=CH3, R3=H, R4=CH3","DMF",55,11,"h",83,None),
    (3,"1h","R1=CH3, R2=CH3, R3=H, R4=n-C6H13","acetone","reflux",21,"h",58,None),
    (4,"1i","R1=n-C7H15, R2=H, R3=H, R4=CH3","acetone","reflux",12,"h",75,">99:1"),
    (5,"1j","R1=n-C4H9, R2=H, R3=H, R4=CH3","acetone","reflux",12,"h",81,"98:2"),
    (6,"1k","R1=n-C7H15, R2=H, R3=H, R4=n-C7H15","acetone","reflux",24,"h",58,"96:4"),
    (7,"1l","R1=n-C5H11, R2=H, R3=n-C4H9, R4=CH3","acetone",55,4,"d",84,">99:1"),
    (8,"1m","R1=n-C5H11, R2=H, R3=n-C4H9, R4=n-C7H15","acetone",55,2,"d",71,"95:5"),
    (9,"1n","R1=n-C5H11, R2=H, R3=n-C4H9, R4=Ph","acetone",55,3,"d",76,">99:1"),
    (10,"1o","R1=n-C5H11, R2=H, R3=n-C4H9, R4=Tolyl","acetone",60,2,"d",47,"98:2"),
    (11,"1p","R1=n-C5H11, R2=H, R3=n-C5H11, R4=CH3","acetone",55,2.5,"d",83,">99:1"),
    (12,"1q","R1=n-C5H11, R2=H, R3=n-C5H11, R4=n-C7H15","acetone",55,3,"d",78,">99:1"),
    (13,"1r","R1=n-C5H11, R2=H, R3=n-C5H11, R4=Ph","acetone",55,3,"d",75,">99:1"),
]
for row in t2:
    entry,label,desc,solvent,temp,tval,tunit,yld,ez=row
    product=label.replace("1","3",1)
    select=("E_to_Z_ratio",ez) if ez else None
    records.append(table_record(f"table2_entry{entry:02d}", f"Table 2 entry {entry}", 4,
                                label, desc, solvent,
                                temp if isinstance(temp,str) else {"number":temp,"unit":"°C"},
                                {"number":tval,"unit":tunit}, [(product,f"beta,gamma-unsaturated enone {product}")],
                                [(product,{"number":yld,"unit":"%"})],
                                loading={"number":10,"unit":"mol%"}, selectivity=select,
                                ratio_basis="determined by 1H NMR spectra" if ez else None,
                                extra_notes=["Table 2 footnote a changes the solvent from acetone to DMF."] if entry==2 else None))


# Table 3: combined yields of product-isomer pairs and their 3:4 ratios.
t3 = [
    (1,"1s","n-C4H9","acetone",55,55,"min",88,"2.9:1","potassium carbonate"),
    (2,"1t","n-C5H11","acetone",55,50,"min",89,"3.5:1","potassium carbonate"),
    (3,"1u","n-C6H13","acetone",55,50,"min",86,"3.7:1","potassium carbonate"),
    (4,"1v","n-C8H17","acetone",55,50,"min",74,"3.6:1","potassium carbonate"),
    (5,"1s","n-C4H9","dichloromethane",50,11,"h",66,"2.7:1","potassium carbonate"),
    (6,"1t","n-C5H11","dichloromethane",50,11,"h",66,"1.1:1","potassium carbonate"),
    (7,"1u","n-C6H13","dichloromethane",50,10,"h",69,"0.9:1","potassium carbonate"),
    (8,"1t","n-C5H11","acetone",55,8,"h",71,"3.5:1","sodium carbonate"),
]
for entry,label,r4,solvent,temp,tval,tunit,yld,ratio,cat in t3:
    suffix=label[1:]
    p3,p4=f"3{suffix}",f"4{suffix}"
    records.append(table_record(f"table3_entry{entry:02d}", f"Table 3 entry {entry}", 4,
                                label, f"R4={r4}", solvent, {"number":temp,"unit":"°C"},
                                {"number":tval,"unit":tunit},
                                [(p3,f"unmigrated enone {p3}"),(p4,f"migrated enone {p4}")],
                                [(p3,{"number":yld,"unit":"%"})],
                                "optimization_entry" if entry>=5 else "substrate_scope_entry",
                                catalyst=cat, loading={"number":10,"unit":"mol%"},
                                selectivity=("product_3_to_4_ratio",ratio),
                                ratio_basis="determined by 300 MHz 1H NMR spectra",
                                extra_notes=["The reported yield is combined for the 3/4 product mixture and targets both products despite its table placement."] +
                                            (["Table 3 footnote b replaces K2CO3 with 10 mol% Na2CO3."] if entry==8 else [])))
    records[-1]["outcomes"][0]["target_entity_ids"]=[f"product_{p3}",f"product_{p4}"]


# Explicit but underspecified failed selectivity screen in the page-3 prose.
failed_ev=ev(3)
failed_ps=[participant("allene_class","reactant",failed_ev,None,"unsubstituted propadienyl ketones 1s-v"),
           malonate_part(failed_ev)]
for i,name in enumerate(["potassium bicarbonate","potassium fluoride","potassium acetate",
                         "sodium bicarbonate","sodium acetate"]):
    failed_ps.append(participant(f"base_{i+1}","unspecified_agent",failed_ev,None,name))
for i,name in enumerate(["acetonitrile","dichloromethane","acetone"]):
    failed_ps.append(participant(f"screen_solvent_{i+1}","solvent",failed_ev,None,name))
records.append(rec("prose_failed_selectivity_screen", "page 3 failed selectivity screen", "unresolved",
                   failed_ev, failed_ps,
                   [{"step_id":"screen","participant_ids":[p["entity_id"] for p in failed_ps],
                     "conditions":[field("operation","weaker-base/solvent combinations screened",failed_ev)]}],
                   [field("selectivity_improvement","failed",failed_ev)],
                   unresolved=["The source does not enumerate which base/solvent pairings were tested or give individual conditions/results.",
                               "No individual experiment rows can be reconstructed without inventing combinations."]))


# Scheme 9 is explicitly mechanistic.
records.append(rec("scheme9_mechanism", "Scheme 9", "mechanism", ev(4),
                   [participant("generic_allene","reactant",ev(4),"1","generic allenic ketone"),
                    participant("nucleophile","reactant",ev(4),"NuH","diethyl malonate"),
                    participant("product_3","product",ev(4),"3","unmigrated enone"),
                    participant("product_4","product",ev(4),"4","migrated enone")],
                   [{"step_id":"proposed_pathway","participant_ids":["generic_allene","nucleophile","product_3","product_4"],
                     "conditions":[field("operation","proposed nucleophilic attack, alpha-protonation, and optional C=C migration",ev(4))]}],
                   unresolved=["Mechanistic proposal only; it is not an independent reported experiment."]))


# Table 4: sequential Michael addition/migration/lactonization.
t4 = [
    (1,"1a","R1=H,R2=H,R3=n-C4H9,R4=Me","acetone","reflux",48,"h",64,"6a","1 equiv"),
    (2,"1a","R1=H,R2=H,R3=n-C4H9,R4=Me","DMF",80,7,"h",55,"6a",None),
    (3,"1b","R1=H,R2=H,R3=n-Et,R4=Me","ethanol","reflux",12,"h",53,"6b",None),
    (4,"1b","R1=H,R2=H,R3=n-Et,R4=Me","DMF",80,12,"h",50,"6b",None),
    (5,"1b","R1=H,R2=H,R3=n-Et,R4=Me","acetone","reflux",20,"h",33,"6b",None),
    (6,"1c","R1=H,R2=H,R3=n-C6H13,R4=Me","acetone",55,3,"d",81,"6c",None),
    (7,"1d","R1=H,R2=H,R3=allyl,R4=Me","ethanol","reflux",15,"h",54,"6d",None),
    (8,"1d","R1=H,R2=H,R3=allyl,R4=Me","acetone","reflux",20,"h",90,"6d",None),
    (9,"1e","R1=H,R2=H,R3=Bn,R4=Me","acetone","reflux",21,"h",92,"6e",None),
    (10,"1e","R1=H,R2=H,R3=Bn,R4=Me","DMF",60,2.5,"h",90,"6e",None),
    (11,"1f","R1=H,R2=H,R3=n-C5H11,R4=n-C8H17","acetone","reflux",2,"d",56,"6f",None),
    (12,"1s","R1=H,R2=H,R3=H,R4=n-C4H9","acetone",55,9,"h",65,"6s",None),
    (13,"1u","R1=H,R2=H,R3=H,R4=n-C6H13","acetone",55,9,"h",63,"6u",None),
    (14,"1v","R1=H,R2=H,R3=H,R4=n-C8H17","acetone",55,9,"h",69,"6v",None),
    (15,"1w","R1=H,R2=H,R3=H,R4=Me","ethanol",60,1.5,"h",74,"6w",None),
    (16,"1x","R1=H,R2=H,R3=H,R4=Ph","acetone","reflux",4,"h",71,"6x",None),
    (17,"1x","R1=H,R2=H,R3=H,R4=Ph","ethanol","reflux",1.5,"h",56,"6x",None),
    (18,"1y","R1=H,R2=H,R3=H,R4=Bn","dichloromethane","reflux",40,"h",69,"6y",None),
]
for entry,label,desc,solvent,temp,tval,tunit,yld,prod,override in t4:
    loading={"number":1,"unit":"equiv"} if override else {"number":10,"unit":"mol%"}
    records.append(table_record(f"table4_entry{entry:02d}", f"Table 4 entry {entry}", 5,
                                label, desc, solvent,
                                temp if isinstance(temp,str) else {"number":temp,"unit":"°C"},
                                {"number":tval,"unit":tunit}, [(prod,f"alpha-pyrone {prod}")],
                                [(prod,{"number":yld,"unit":"%"})],
                                loading=loading,
                                extra_notes=["Table 4 footnote a overrides the header catalyst loading; the explicit replacement is structured in the catalyst participant amount."] if entry==1 else None))


# Scheme 10 contains two distinct solvent entries.
for solvent,yld in [("ethanol",38),("DMF",54)]:
    evidence=ev(5)
    records.append(table_record(f"scheme10_{solvent.lower()}", f"Scheme 10, {solvent}", 5,
                                "1j", "nona-3,4-dien-2-one", solvent,
                                {"number":80,"unit":"°C"}, None,
                                [("6j","alpha-pyrone 6j")], [("6j",{"number":yld,"unit":"%"})],
                                "optimization_entry", loading={"number":10,"unit":"mol%"},
                                extra_notes=["Reaction time is not reported in Scheme 10 or its adjacent prose."]))
    records[-1]["steps"][0]["conditions"][2]=field("time",None,evidence)


records.append(rec("scheme11_mechanism", "Scheme 11", "mechanism", ev(5),
                   [participant("generic_allene","reactant",ev(5),"1","generic allenic ketone"),
                    participant("malonate","reactant",ev(5),None,"diethyl malonate"),
                    participant("intermediate_3","product",ev(5),"3","unmigrated addition product"),
                    participant("intermediate_4","product",ev(5),"4","migrated enone"),
                    participant("pyrone_6","product",ev(5),"6","alpha-pyrone")],
                   [{"step_id":"proposed_sequence","participant_ids":["generic_allene","malonate","intermediate_3","intermediate_4","pyrone_6"],
                     "conditions":[field("operation","proposed addition, C=C migration, keto-ester cyclization",ev(5))]}],
                   notes=[fact("The pathway through intermediate 5 is explicitly crossed out in the scheme.",ev(5))],
                   unresolved=["Mechanistic proposal only; intermediates are not separate isolated experiments."]))


negative_ev=ev(5)
records.append(rec("prose_no_pyrone_1_3_disubstituted", "page 5 negative result", "unresolved",
                   negative_ev,
                   [participant("substrate_class","reactant",negative_ev,None,"1,3-disubstituted 1,2-allenyl ketone"),
                    malonate_part(negative_ev),
                    participant("pyrone_class","product",negative_ev,None,"alpha-pyrone")],
                   [{"step_id":"reported_attempt","participant_ids":["substrate_class","malonate","pyrone_class"],
                     "conditions":[field("operation","cyclization reaction examined",negative_ev)]}],
                   [field("product_formation","not formed",negative_ev,["pyrone_class"])],
                   unresolved=["The source gives a substrate class but no exact substrate label, quantities, solvent, temperature, or time for this negative result."]))


# General procedure on page 6.
gpev=ev(6)
gp_ps=[participant("allene","reactant",gpev,"1","1,2-allenic ketone",
                   [qty("amount",1.2,"mmol",gpev)]),
       participant("malonate","reactant",gpev,None,"diethyl malonate",
                   [qty("amount",1.0,"mmol",gpev)]),
       participant("catalyst","catalyst",gpev,None,"potassium carbonate",
                   [qty("mass",15.8,"mg",gpev),field("loading",{"number":10,"unit":"mol%"},gpev)]),
       participant("solvent","solvent",gpev,None,"acetone",[qty("volume",2,"mL",gpev)]),
       participant("products","product",gpev,"3/4/6","product 3, 4, 6, or a mixture")]
records.append(rec("general_procedure_1_4_addition", "General procedure for K2CO3-catalyzed 1,4-addition", "general_scheme",
                   gpev,gp_ps,
                   [{"step_id":"reaction","participant_ids":[p["entity_id"] for p in gp_ps],
                     "conditions":[field("temperature",{"number":60,"unit":"°C"},gpev),
                                   field("operation","heat with stirring until TLC indicated completion",gpev)]},
                    {"step_id":"isolation","participant_ids":["products"],
                     "conditions":[field("workup","evaporate solvent",gpev),
                                   field("purification","silica gel chromatography; petroleum ether/ethyl acetate 10:1",gpev)]}],
                   unresolved=["General procedure covers alternative products 3, 4, 6, or mixtures and is not a single substrate experiment.",
                               "Supporting information was not supplied or explicitly associated."]))


def amounts(evidence, **items):
    result=[]
    for key,value in items.items():
        name,unit=key.rsplit("_",1)
        result.append(qty(name,value,unit,evidence))
    return result


def find_record(suffix):
    rid=f"{DOC}:{suffix}"
    return next(r for r in records if r["record_id"]==rid)


# Replace five scheme-summary records with their detailed page-6 procedures while retaining scheme evidence.
e26=ev(2)+ev(6)
r=find_record("scheme2_1c")
r["evidence_ids"]=e26
r["participants"]=[
    participant("acetoacetone","reactant",e26,None,"acetoacetone",amounts(e26,mass_g=10.0,amount_mol=0.1)),
    participant("bromohexane","reactant",e26,None,"1-bromohexane",amounts(e26,volume_mL=15.5,mass_g=18.2,amount_mol=0.11)),
    participant("k2co3","reagent",e26,None,"potassium carbonate",amounts(e26,mass_g=15.2,amount_mol=0.11)),
    participant("ki","reagent",e26,None,"potassium iodide",amounts(e26,mass_g=8.3,amount_mol=0.05)),
    participant("acetone","solvent",e26,None,"acetone",amounts(e26,volume_mL=50)),
    participant("pph3","reagent",e26,None,"triphenylphosphine",amounts(e26,mass_g=21.6,amount_mmol=83)),
    participant("br2","reagent",e26,None,"bromine",amounts(e26,mass_g=17.8,amount_mmol=80)),
    participant("ch2cl2","solvent",e26,None,"dichloromethane",amounts(e26,volume_mL=100)),
    participant("et3n","reagent",e26,None,"triethylamine",amounts(e26,mass_g=7.5,amount_mmol=75)),
    participant("mecn","solvent",e26,None,"acetonitrile",amounts(e26,volume_mL=100)),
    participant("product","product",e26,"1c",ALLENE_NAMES["1c"],[qty("mass",4.5,"g",e26)])]
r["steps"]=[
    {"step_id":"alkylation","participant_ids":["acetoacetone","bromohexane","k2co3","ki","acetone"],
     "conditions":[field("temperature","reflux",e26),field("time",{"number":43,"unit":"h"},e26)]},
    {"step_id":"bromination","participant_ids":["pph3","br2","ch2cl2"],
     "conditions":[field("temperature","ice-cold",e26),field("time","until evolution of hydrogen bromide ceased",e26)]},
    {"step_id":"elimination_and_isolation","participant_ids":["et3n","mecn","product"],
     "conditions":[field("temperature",{"number":80,"unit":"°C"},e26),field("time",{"number":23,"unit":"h"},e26),
                   field("workup","filter; wash with diluted HCl (2 x 30 mL) and saturated NaCl (2 x 50 mL); dry over MgSO4; evaporate",e26),
                   field("purification","silica gel chromatography, hexane/ether 100:1",e26)]}]
r["outcomes"]=[field("yield",{"number":36,"unit":"%"},e26,["product"])]
r["review"]["unresolved"]=["Supporting information was not supplied or explicitly associated.",
                            "The named acetoacetone/derived diketone wording is preserved from the source; structures remain unverified."]


e6=ev(6)
r=find_record("scheme3_1f"); r["evidence_ids"]=ev(2)+e6
r["participants"]=[
    participant("sncl2","reagent",e6,None,"stannous chloride",amounts(e6,mass_g=2.39,amount_mmol=12.6)),
    participant("bromoalkyne","reactant",e6,None,"1-bromooct-2-yne",amounts(e6,mass_g=1.8,amount_mmol=10.1)),
    participant("nai","reagent",e6,None,"sodium iodide",amounts(e6,mass_g=1.85,amount_mmol=12.4)),
    participant("dmf","solvent",e6,None,"DMF",amounts(e6,volume_mL=30)),
    participant("nonanal","reactant",e6,None,"nonanal",amounts(e6,mass_g=1.4,amount_mmol=9.9)),
    participant("crude_alcohol","reactant",e6,None,"crude allenic alcohol",amounts(e6,mass_g=1.04)),
    participant("oxalyl_chloride","reagent",e6,None,"oxalyl chloride",amounts(e6,volume_mL=0.7,amount_mmol=6.2)),
    participant("dmso","reagent",e6,None,"DMSO",amounts(e6,volume_mL=1.1,amount_mmol=12.4)),
    participant("ch2cl2","solvent",e6,None,"dichloromethane",amounts(e6,volume_mL=30)),
    participant("et3n","reagent",e6,None,"triethylamine",amounts(e6,volume_mL=6.0,amount_mmol=40)),
    participant("product","product",e6,"1f",ALLENE_NAMES["1f"],[qty("mass",0.84,"g",e6)])]
r["steps"]=[
    {"step_id":"allenic_alcohol_formation","participant_ids":["sncl2","bromoalkyne","nai","dmf","nonanal","crude_alcohol"],
     "conditions":[field("operation","stir at room temperature, then cool to 0 °C for the aldehyde stage",e6),
                   field("initial_stir_time",{"number":1,"unit":"h"},e6),
                   field("time_at_0_C",{"number":24,"unit":"h"},e6),
                   field("workup","quench with water; extract, dry, evaporate",e6),field("purification","flash chromatography, hexane/ether 15:1",e6)]},
    {"step_id":"swern_oxidation","participant_ids":["crude_alcohol","oxalyl_chloride","dmso","ch2cl2","et3n","product"],
     "conditions":[field("operation","conduct activation and oxidation at -78 °C, then warm to 0 °C",e6),
                   field("activation_time",{"number":5,"unit":"min"},e6),
                   field("time_at_minus_78_C",{"number":30,"unit":"min"},e6),
                   field("time_at_0_C",{"number":10,"unit":"min"},e6),
                   field("workup","dilute with ether; wash with 10% HCl; extract with ether; dry over MgSO4; evaporate",e6),
                   field("purification","flash chromatography, petroleum ether/ethyl acetate 100:1",e6)]}]
r["outcomes"]=[field("yield",{"number":82,"unit":"%"},e6,["product"])]
r["review"]["unresolved"]=["Supporting information was not supplied or explicitly associated.",
                            "The first-stage crude alcohol is reported by mass without an isolated yield."]


r=find_record("scheme5_1k"); r["evidence_ids"]=ev(2)+e6
r["participants"]=[
    participant("diene","reactant",e6,None,"deca-1,2-diene",amounts(e6,mass_g=4.4,amount_mmol=32)),
    participant("thf","solvent",e6,None,"THF",amounts(e6,volume_mL=100)),
    participant("nbuli","reagent",e6,None,"n-butyllithium",amounts(e6,concentration_M=2.5,volume_mL=12,amount_mmol=30)),
    participant("amide","reactant",e6,None,"N,N-dimethyl octamide",amounts(e6,mass_g=5.1,amount_mmol=30)),
    participant("product","product",e6,"1k",ALLENE_NAMES["1k"],[qty("mass",3.1,"g",e6)])]
r["steps"]=[{"step_id":"lithiation_and_acylation","participant_ids":["diene","thf","nbuli","amide","product"],
              "conditions":[field("operation","add n-BuLi at -70 °C, stir at -50 to -40 °C, then add amide at -78 °C",e6),
                            field("time_at_minus_50_to_minus_40_C",{"number":1,"unit":"h"},e6),
                            field("time_at_minus_78_C",{"number":2,"unit":"h"},e6),
                            field("workup","transfer into ice-cold aqueous 0.2 N HCl (200 mL); extract with ether; dry over MgSO4; evaporate",e6),
                            field("purification","flash chromatography, hexane/ether 40:1",e6)]}]
r["outcomes"]=[field("yield",{"number":39,"unit":"%"},e6,["product"])]
r["review"]["unresolved"]=["0.2 N HCl is preserved in the workup text because N is unsupported by the quantity schema.",
                            "Supporting information was not supplied or explicitly associated."]


r=find_record("scheme6_1l"); r["evidence_ids"]=ev(2)+e6
r["participants"]=[
    participant("enyne","reactant",e6,None,"oct-1-en-3-yne",amounts(e6,mass_g=1.1,amount_mmol=10)),
    participant("thf","solvent",e6,None,"THF",amounts(e6,volume_mL=70)),
    participant("nbuli","reagent",e6,None,"n-butyllithium",amounts(e6,concentration_M=2.5,volume_mL=4)),
    participant("amide","reactant",e6,None,"N,N-dimethylacetamide",amounts(e6,mass_g=5.1,amount_mmol=30)),
    participant("product","product",e6,"1l",ALLENE_NAMES["1l"],[qty("mass",3.2,"g",e6)])]
r["steps"]=[{"step_id":"lithiation_and_acylation","participant_ids":["enyne","thf","nbuli","amide","product"],
              "conditions":[field("atmosphere","argon",e6),
                            field("operation","add n-BuLi at -40 °C, stir at -25 °C, recool to -78 °C, then add amide",e6),
                            field("time_at_minus_25_C",{"number":0.5,"unit":"h"},e6),
                            field("time_after_amide_addition",{"number":2,"unit":"h"},e6),
                            field("workup","transfer to 400 mL of 0.2 N HCl; usual workup",e6),
                            field("purification","flash chromatography, hexane/ether 100:1",e6)]}]
r["outcomes"]=[field("yield",{"number":55,"unit":"%"},e6,["product"])]
r["review"]["unresolved"]=["The phrase 'usual workup' is not expanded.",
                            "0.2 N HCl is preserved as text because N is unsupported by the quantity schema.",
                            "Supporting information was not supplied or explicitly associated."]


r=find_record("scheme7_1u"); r["evidence_ids"]=ev(2)+e6
r["participants"]=[
    participant("mg","reagent",e6,None,"magnesium",amounts(e6,mass_g=3.6,amount_mol=0.15)),
    participant("ether","solvent",e6,None,"diethyl ether",amounts(e6,volume_mL=60)),
    participant("hgcl2","reagent",e6,None,"mercuric chloride",amounts(e6,mass_g=0.1)),
    participant("propargyl_bromide","reactant",e6,None,"propargyl bromide",amounts(e6,volume_mL=10.7,amount_mol=0.12)),
    participant("heptanal","reactant",e6,None,"heptanal",amounts(e6,volume_mL=16.0,amount_mol=0.11)),
    participant("alcohol","reactant",e6,None,"dec-1-yn-4-ol",amounts(e6,mass_g=15.9)),
    participant("alcohol_portion","reactant",e6,None,"above prepared alcohol",amounts(e6,mass_g=8.8,amount_mmol=57)),
    participant("dmp","reagent",e6,"DMP","Dess-Martin periodinane",amounts(e6,mass_g=29.5,amount_mmol=69)),
    participant("ch2cl2","solvent",e6,None,"dichloromethane",amounts(e6,volume_mL=500)),
    participant("product","product",e6,"1u",ALLENE_NAMES["1u"],[qty("mass",4.7,"g",e6)])]
r["steps"]=[
    {"step_id":"alcohol_formation","participant_ids":["mg","ether","hgcl2","propargyl_bromide","heptanal","alcohol"],
     "conditions":[field("operation","stir at room temperature, cool to 0 °C for propargyl bromide, cool to -40 °C for heptanal, then warm naturally to room temperature",e6),
                   field("initial_stir_time",{"number":2.5,"unit":"h"},e6),
                   field("time_after_propargyl_bromide",{"number":1,"unit":"h"},e6),
                   field("time_after_heptanal",{"number":1,"unit":"h"},e6),
                   field("workup","pour into NH4Cl solution; usual workup",e6),
                   field("purification","distillation at 99-100 °C/20 mmHg",e6)]},
    {"step_id":"dmp_oxidation","participant_ids":["alcohol_portion","dmp","ch2cl2","product"],
     "conditions":[field("time",{"number":2,"unit":"h"},e6),
                   field("workup","dilute with 500 mL ether; add to 200 mL of 1 N NaOH; usual workup",e6),
                   field("purification","flash chromatography, hexane/ethyl acetate 100:1",e6)]}]
r["outcomes"]=[field("stage_1_yield",{"number":93,"unit":"%"},e6,["alcohol"]),
               field("stage_2_yield",{"number":54,"unit":"%"},e6,["product"])]
r["review"]["unresolved"]=["The phrase 'usual workup' is not expanded.",
                            "NaOH normality and distillation pressure are preserved in text because N and mmHg are unsupported quantity units.",
                            "Supporting information was not supplied or explicitly associated."]


# Enrich Table 1 entry 6 with its matching page-6 specific experiment, without duplicating it.
r=find_record("table1_entry06")
r["evidence_ids"]=ev(3)+e6
r["participants"][0]["amounts"]=[qty("mass",169.7,"mg",e6),qty("amount",1.2,"mmol",e6)]
r["participants"][1]["amounts"]=[qty("mass",164.5,"mg",e6),qty("amount",1.0,"mmol",e6)]
r["participants"][2]["amounts"]=[qty("mass",16.7,"mg",e6),field("loading",{"number":10,"unit":"mol%"},ev(3)+e6)]
r["participants"][3]["amounts"]=[qty("volume",2,"mL",e6)]
for p in r["participants"]:
    if p["entity_id"]=="product_4a": p["amounts"]=[qty("mass",172.4,"mg",e6)]
    if p["entity_id"]=="product_6a": p["amounts"]=[qty("mass",9.1,"mg",e6)]
r["steps"]=[{"step_id":"reaction","participant_ids":[p["entity_id"] for p in r["participants"]],
              "conditions":[field("solvent","acetone",ev(3)+e6),field("temperature",{"number":60,"unit":"°C"},ev(3)+e6),
                            field("time",{"number":8,"unit":"h"},ev(3)),
                            field("operation","heat with stirring until TLC indicated completion",e6)]},
             {"step_id":"isolation","participant_ids":["product_4a","product_6a"],
              "conditions":[field("workup","evaporate solvent",e6),
                            field("purification","silica gel chromatography, petroleum ether/ethyl acetate 10:1",e6)]}]
r["review"]["unresolved"]=["Supporting information was not supplied or explicitly associated.",
                            "The product structures are shown/named but remain machine-unverified.",
                            "Analytical characterization continues onto page 7, outside this session's visual coverage."]


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
