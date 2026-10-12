#!/usr/bin/env python3
"""Build source-linked reaction records and coverage for PDF pages 25--30."""
import json
import re
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
OUT = Path(__file__).with_name("records_pages_0025_0030.json")
records = []


def ev(pages):
    return [item for page in pages for item in (
        f"{DOC}:page{page}:text", f"{DOC}:page{page}:image")]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def slug(value):
    return re.sub(r"[^A-Za-z0-9]+", "_", str(value)).strip("_").lower()[:36] or "entity"


def P(role, label, name=None, smiles=None, amounts=None):
    return role, label, name, smiles, amounts or []


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def participant(index, spec, evidence):
    role, label, name, smiles, amounts = spec
    return {
        "entity_id": f"p{index}_{slug(label)}",
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [{"name": key, "fact": fact(value, evidence)} for key, value in amounts],
    }


def add(rid, source_id, pages, parts, conditions=None, outcomes=None, notes=None,
        unresolved=None, kind="literature_example"):
    evidence = ev(pages)
    ps = [participant(i, spec, evidence) for i, spec in enumerate(parts, 1)]
    label_ids = {p["label"]["value"]: p["entity_id"] for p in ps}
    conds = list(conditions or [])
    if kind == "literature_example":
        if not any(name == "temperature" for name, _ in conds):
            conds.append(("temperature", None))
        if not any(name == "time" for name, _ in conds):
            conds.append(("time", None))
    out_fields = []
    has_yield = False
    for name, value, targets in outcomes or []:
        field = {"name": name, "fact": fact(value, evidence)}
        if targets:
            if isinstance(targets, str):
                targets = [targets]
            field["target_entity_ids"] = [label_ids[target] for target in targets]
        out_fields.append(field)
        has_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(x["name"] == "yield" for x in out_fields):
        products = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if products:
            missing["target_entity_ids"] = products
        out_fields.append(missing)
    if has_yield:
        out_fields.append({"name": "yield_measurement_basis", "fact": fact(None, evidence)})
    step_ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    record = {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": ps,
        "steps": [{
            "step_id": "step1",
            "participant_ids": step_ids,
            "conditions": [{"name": name, "fact": fact(value, evidence)} for name, value in conds],
        }] if conds else [],
        "outcomes": out_fields,
        "notes": [fact(note, evidence) for note in notes or []],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "Secondary-review example: the cited primary article and its SI were not supplied.",
                "Complex or generic drawings remain label-only; all structures are unverified.",
            ],
        },
    }
    records.append(record)
    return record


def mechanism(rid, source_id, pages, sequence, conditions=None, notes=None, unresolved=None):
    parts = []
    for i, label in enumerate(sequence):
        role = "reactant" if i == 0 else ("product" if i == len(sequence) - 1 else "unspecified_agent")
        parts.append(P(role, label))
    return add(rid, source_id, pages, parts, conditions=conditions, notes=notes,
               unresolved=(unresolved or []) + [
                   "The arrows depict a proposed pathway, not independently reported experimental operations."
               ], kind="mechanism")


def set_steps(record, specs):
    evidence = record["evidence_ids"]
    ids = {p["label"]["value"]: p["entity_id"] for p in record["participants"]}
    record["steps"] = []
    for i, (labels, conditions) in enumerate(specs, 1):
        record["steps"].append({
            "step_id": f"step{i}",
            "participant_ids": [ids[label] for label in labels],
            "conditions": [{"name": name, "fact": fact(value, evidence)} for name, value in conditions],
        })


# Page 25: Schemes 115--119.
add("p0024_s115_text_only", "Scheme 115 substrate 557 scope", [24, 25], [
    P("reactant", "557 (R1/R2/X scope)", "1,2,7-triene"),
    P("catalyst", "[Rh(CO)2Cl]2"), P("unspecified_agent", "P(O-o-tol)3"),
    P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "559", "2-vinylic alkylidenecyclopentane"),
], conditions=[("temperature", q(110, "°C")), ("Rh_to_P_ratio", "1:2")],
    outcomes=[("yield", qr(28, 97, "%", "28–97%"), "559")],
    notes=["Scope: R1′=Me or H, or R1′/R1′=(CH2)5; R2=H, Ph, or TMS; X=C(CO2Me)2, NTs, N-Bn, or O."])
add("p0025_s115_560", "Scheme 115 substrate 560", [25], [
    P("reactant", "560", "1,2,7-triene"), P("catalyst", "[Rh(CO)2Cl]2"),
    P("unspecified_agent", "P(O-o-tol)3"), P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "561", "cyclized diene"),
], conditions=[("temperature", q(110, "°C"))], outcomes=[
    ("yield", q(78, "%"), "561"), ("E_Z_ratio", "2.6:1", "561")],
    notes=["The arrow is marked ibid relative to 557."])
add("p0025_s115_562", "Scheme 115 substrate 562", [25], [
    P("reactant", "562", "1,2,8-triene"),
    P("catalyst", "[Rh(CO)2Cl]2", amounts=[("catalyst_loading", q(20, "mol%"))]),
    P("unspecified_agent", "P(O-o-tol)3"), P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "563", "six-membered-ring cyclization product"),
], conditions=[("temperature", q(110, "°C"))], outcomes=[("yield", q(83, "%"), "563")],
    notes=["The arrow is marked ibid except for the printed 20 mol% catalyst loading."])
for suffix, ar, yld, ratio in [("otol", "Ar=o-tol", 87, "1.5:1"), ("obiphenyl", "Ar=o-PhC6H4", 91, "8.3:1")]:
    product = f"565 ({ar})"
    add(f"p0025_s115_564_{suffix}", f"Scheme 115 substrate 564 {ar}", [25], [
        P("reactant", f"564 ({ar})", "1,2,7-triene"), P("catalyst", "[RhCl(COD)]2"),
        P("unspecified_agent", f"P(OAr)3 ({ar})", "phosphite ligand"),
        P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"), P("product", product),
    ], conditions=[("temperature", q(110, "°C"))], outcomes=[
        ("yield", q(yld, "%"), product), ("E_Z_ratio", ratio, product)])

add("p0024_s116_text_only", "Scheme 116 scope", [24, 25], [
    P("reactant", "566 (R1/R2/R3/Ar scope)", "disubstituted alkene-allene"),
    P("catalyst", "[Rh(COD)Cl]2"), P("unspecified_agent", "P(OAr)3 (Ar=o-tol or o-C6H4C6H5)"),
    P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "567", "1,2-bis(vinylic)cyclopentane"),
    P("product", "alkylidene constitutional isomer (not formed)"),
], conditions=[("temperature", q(110, "°C")), ("operation", "reflux")], outcomes=[
    ("yield", qr(90, 93, "%", "90–93%"), "567"),
    ("cis_trans_ratio", "2.8:1 to 3:1", "567"),
    ("reaction_result", "not formed", "alkylidene constitutional isomer (not formed)"),
], notes=["The negative result is reported qualitatively; it is not converted to a numerical zero yield."])

add("p0025_s117_568", "Scheme 117 substrate 568", [25], [
    P("reactant", "568", "1,2,7-triene"), P("catalyst", "[RhCl(CO)2]2"),
    P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"), P("product", "569", "4-alkylidenecycloheptene"),
], conditions=[("temperature", "reflux"), ("atmosphere", "CO, 1 atm")],
    outcomes=[("yield", q(80, "%"), "569")])
add("p0025_s117_570", "Scheme 117 substrate 570 scope", [25], [
    P("reactant", "570 (X/R1/R2/R3 scope)", "allene-alkene"),
    P("catalyst", "[Rh(CO)2Cl]2", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "DCE or toluene"), P("product", "571", "4-alkylidenecycloheptene"),
], conditions=[("temperature", q(90, "°C"))], outcomes=[("yield", qr(40, 95, "%", "40–95%"), "571")],
    notes=["Scope: X=NTs, NBz, NCBz, or O; R1=alkyl, H, or Ph; R2=alkyl, H, or t-Bu; R3=H, alkyl, or i-Pr."])
mechanism("p0025_s118", "Scheme 118 deuterium-labeling mechanism", [25],
          ["572", "573", "574", "575"],
          notes=["Proposed allylic C–H cleavage, endo-mode insertion, and reductive elimination; D labels are retained by the scheme labels."])
add("p0025_s119", "Scheme 119 overall", [25], [
    P("reactant", "576", "2-alkenamide-allene"), P("reagent", "MeLi", "methyllithium", "[Li]C"),
    P("reagent", "ZnCl2", "zinc chloride", "[Cl-].[Cl-].[Zn+2]"),
    P("catalyst", "Ni(COD)2", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("reagent", "Ti(O-i-Pr)4", "titanium tetraisopropoxide"),
    P("product", "579", "5/5-fused bicyclic product"),
], outcomes=[("yield", q(57, "%"), "579"), ("diastereomer_ratio", "98:2", "579")])
mechanism("p0025_s119_mechanism", "Scheme 119 proposed Ni pathway", [25],
          ["576", "577", "578", "579"],
          notes=["The review assigns cyclometalation, transmetalation, and reductive elimination."])


# Page 26: Schemes 120--124.
add("p0026_s120_580", "Scheme 120 coordination of 580", [26], [
    P("reactant", "580", "vinylic allene"), P("reagent", "RhCl(PPh3)3", "Wilkinson catalyst"),
    P("solvent", "C6H6", "benzene", "c1ccccc1"),
    P("product", "exo-581", "eta4-diene rhodium complex"), P("product", "endo-582", "eta4-diene rhodium complex"),
], conditions=[("temperature", "r.t."), ("time", q(20, "h"))])
add("p0026_s120_582", "Scheme 120 carbonylation of 582", [26], [
    P("reactant", "endo-582", "eta4-diene rhodium complex"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"), P("product", "585", "2-alkylidene-3-cyclopentenone"),
], conditions=[("temperature", "r.t."), ("time", q(5, "h")), ("atmosphere", "CO, 1 atm")])
mechanism("p0026_s120_582_mechanism", "Scheme 120 carbonylation pathway", [26],
          ["endo-582 + CO", "583", "584", "585"],
          notes=["The depicted sequence is cyclometalation, CO insertion, and reductive elimination."])
add("p0026_s120_586", "Scheme 120 vinylic-allene scope", [26], [
    P("reactant", "586 (R1–R5 scope)", "vinylic allene"),
    P("catalyst", "[Rh(COD)(MeCN)2]PF6 or [Rh(COD)2]PF6/dppe or [Rh(COD)dppb]BF4"),
    P("solvent", "CH2Cl2 or toluene"), P("product", "587", "alkylidenecyclopentenone"),
], outcomes=[("yield", qr(78, 99, "%", "78–99%"), "587")],
    notes=["Catalyst/solvent choices and R1–R5 scope are aggregate and are not mapped to individual yields on this review page."],
    unresolved=["The alternative catalyst and solvent combinations cannot be assigned row-by-row from the review scheme."])

add("p0026_s121_588", "Scheme 121 isolation of 588", [26], [
    P("reactant", "vinylic allene precursor to 588"), P("reagent", "RhCl(PPh3)3", "Wilkinson catalyst"),
    P("solvent", "benzene", "benzene", "c1ccccc1"), P("product", "588", "rhodacyclic complex"),
], conditions=[("temperature", "r.t."), ("time", q(24, "h"))], outcomes=[("yield", q(92, "%"), "588")])
add("p0026_s121_589", "Scheme 121 carbonylation of 588", [26], [
    P("reactant", "588", "rhodacyclic complex"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"), P("product", "589", "carbonylated rhodium complex"),
], conditions=[("temperature", "r.t."), ("time", q(18, "h"))], outcomes=[("yield", q(96, "%"), "589")])
add("p0026_s121_590", "Scheme 121 reductive elimination from 589", [26], [
    P("reactant", "589", "carbonylated rhodium complex"), P("product", "590", "5-alkylidenecyclopent-2-enone"),
])
add("p0026_s121_591", "Scheme 121 asymmetric carbonylation of 591", [26], [
    P("reactant", "591", "vinylic allene"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "[Rh(R,R)-Me-Duphos(COD)]PF6"), P("solvent", "DME", "1,2-dimethoxyethane", "COCCOC"),
    P("product", "592", "enantioenriched cyclopentenone"),
], conditions=[("temperature", qr(55, 60, "°C", "55–60 °C")), ("time", qr(6, 20, "h", "6–20 h")),
               ("atmosphere", "CO, 5 atm")], outcomes=[
    ("yield", qr(87, 99, "%", "87–99%"), "592"),
    ("enantiomeric_excess", qr(75, 78, "%", "75–78% ee"), "592")])
for suffix, rgroup, yld, ee_value in [("et", "R=Et", 93, 92.0), ("ibu", "R=i-Bu", 96, 91.5), ("benzyl", "R=CH2Ph", 94, 95.0)]:
    product = f"594 ({rgroup})"
    add(f"p0026_s121_593_{suffix}", f"Scheme 121 substrate 593 {rgroup}", [26], [
        P("reactant", f"593 ({rgroup})", "ester-substituted vinylic allene"),
        P("catalyst", "[Rh(COD)2]PF6"), P("unspecified_agent", "(R,R)-Me-Duphos"),
        P("solvent", "DME", "1,2-dimethoxyethane", "COCCOC"), P("product", product),
    ], conditions=[("temperature", q(10, "°C")), ("time", qr(24, 90, "h", "24–90 h"))], outcomes=[
        ("yield", q(yld, "%"), product), ("enantiomeric_excess", q(ee_value, "%", raw_text=f"{ee_value}% ee"), product)])

add("p0026_s122_595", "Scheme 122 formation of 595", [26], [
    P("reactant", "vinylic allene precursor to 595"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Pd(PPh3)4", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "595", "nine-membered-ring ketone"),
], conditions=[("temperature", q(30, "°C")), ("time", q(43, "h"))], outcomes=[("yield", q(87, "%"), "595")])
add("p0026_s122_596_597", "Scheme 122 competing products 596 and 597", [26], [
    P("reactant", "vinylic allene precursor to 596/597"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Pd(PPh3)4", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "596", "nine-membered-ring ketone"), P("product", "597", "competing ketone"),
], conditions=[("temperature", q(20, "°C")), ("time", q(22, "h"))], outcomes=[
    ("yield", q(77, "%"), "596"), ("yield", q(6, "%"), "597")], notes=["The arrow is marked ibid relative to 595."])

add("p0026_s123_598", "Scheme 123 diene scope", [26], [
    P("reactant", "598 (R1/R2/R3 scope)", "vinylic allene"), P("reactant", "1,3-diene"),
    P("catalyst", "Pd(PPh3)4", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "cis-599", "six-membered cycloadduct"),
], conditions=[("temperature", "r.t.")], outcomes=[("yield", qr(85, 98, "%", "85–98%"), "cis-599")])
add("p0026_s123_601", "Scheme 123 asymmetric cycloaddition", [26], [
    P("reactant", "dimethyl-substituted vinylic allene (R1/R2 scope)"), P("reactant", "1,3-diene"),
    P("catalyst", "Pd2(dba)3·CHCl3", amounts=[("catalyst_loading", q(2.5, "mol%"))]),
    P("unspecified_agent", "chiral monophosphine 600", amounts=[("ligand_loading", q(6, "mol%"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"), P("product", "601", "enantioenriched six-membered cycloadduct"),
], conditions=[("temperature", "r.t.")], outcomes=[
    ("yield", qr(63, 89, "%", "63–89%"), "601"),
    ("enantiomeric_excess", qr(52, 83, "%", "52–83% ee"), "601")])
add("p0026_s123_602", "Scheme 123 terminal-alkyne scope", [26], [
    P("reactant", "vinylic allene (R1–R4 scope)"), P("reactant", "terminal alkyne (R5 scope)"),
    P("catalyst", "[Rh(COD)2]OTf", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("unspecified_agent", "P[OCH(CF3)2]3", amounts=[("ligand_loading", q(10, "mol%"))]),
    P("solvent", "DME", "1,2-dimethoxyethane", "COCCOC"), P("product", "602", "polysubstituted arene"),
], conditions=[("temperature", q(50, "°C")), ("time", q(24, "h"))],
    outcomes=[("yield", qr(15, 94, "%", "15–94%"), "602")])
for suffix, subs, yld in [
    ("tetramethyl", "R1=R2=R3=R4=Me", 79),
    ("ditbu", "R1=R4=t-Bu; R2=R3=Me", 72),
    ("diphenyl", "R1=R4=Ph; R2=R3=Me", 81),
]:
    product = f"604 ({subs})"
    add(f"p0026_s124_{suffix}", f"Scheme 124 {subs}", [26], [
        P("reactant", f"603 ({subs})", "conjugated bisallene"),
        P("catalyst", "Fe(CO)5", amounts=[("catalyst_loading", q(10, "mol%"))]),
        P("unspecified_agent", "CO or Fe2(CO)9"), P("product", product, "2,5-bis(alkylidene)cyclopent-3-enone"),
    ], outcomes=[("yield", q(yld, "%"), product)],
        unresolved=["The review lists CO or Fe2(CO)9 as alternatives without mapping the option to each substrate row."])


# Page 27: Schemes 125--129.
add("p0027_s125", "Scheme 125 scope", [27], [
    P("reactant", "605 (R1–R5 scope)", "1,2-allenyl cyclopropane"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "trans-IrCl(CO)(PPh3)2", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "xylene"), P("product", "606", "2-alkylidene-3-cyclohexenone"),
], conditions=[("temperature", qr(130, 140, "°C", "130–140 °C"))],
    outcomes=[("yield", qr(28, 83, "%", "28–83%"), "606")])
for suffix, subs, yld, ratio in [
    ("npr", "R1=n-Pr; R2=CO2Bn", 98, ">99:1"),
    ("ph_ester", "R1=Ph; R2=CO2Me", 98, "92:8"),
    ("ph_h", "R1=Ph; R2=H", 78, "3:97"),
]:
    add(f"p0027_s126_{suffix}", f"Scheme 126 {subs}", [27], [
        P("reactant", f"607 ({subs})", "allenylcyclopropane"),
        P("catalyst", "RhCl(PPh3)3 or [Rh(COD)2]BF4 or [Rh(PPh3)4]BF4 or [Rh(COD)(PPh3)2]BF4"),
        P("solvent", "benzene", "benzene", "c1ccccc1"), P("product", f"608 ({subs})"), P("product", f"609 ({subs})"),
    ], conditions=[("temperature", "reflux")], outcomes=[
        ("yield", q(yld, "%"), [f"608 ({subs})", f"609 ({subs})"]),
        ("product_ratio_608_to_609", ratio, [f"608 ({subs})", f"609 ({subs})"])],
        unresolved=["The alternative rhodium catalysts are not mapped to individual scope rows in the review scheme."])

for suffix, rgroup, catalyst_loading, solvent, temp, concentration, yld, ratio in [
    ("h", "R=H", 5, "DCE", 90, 0.003, 83, ">20:1"),
    ("me", "R=Me", 10, "toluene", 110, 0.01, 90, ">10:1"),
]:
    add(f"p0027_s127_610_{suffix}", f"Scheme 127 substrate 610 {rgroup}", [27], [
        P("reactant", f"610 ({rgroup})", "allene-vinyl cyclopropane"),
        P("catalyst", "[Rh(CO)2Cl]2", amounts=[("catalyst_loading", q(catalyst_loading, "mol%"))]),
        P("solvent", solvent), P("product", f"611 ({rgroup})", "major cis-5/7-fused product"),
        P("product", f"612 ({rgroup})", "minor product"),
    ], conditions=[("temperature", q(temp, "°C")), ("concentration", q(concentration, "M"))], outcomes=[
        ("yield", q(yld, "%"), [f"611 ({rgroup})", f"612 ({rgroup})"]),
        ("product_ratio_611_to_612", ratio, [f"611 ({rgroup})", f"612 ({rgroup})"])])
for suffix, subs, yld in [
    ("carbon_me", "X=CHCO2Me; R1=R2=Me", 93),
    ("carbon_tbu", "X=CHCO2Me; R1=H; R2=t-Bu", 91),
    ("nts", "X=N-Ts; R1=R2=H", 90),
]:
    product = f"614 ({subs})"
    add(f"p0027_s127_613_{suffix}", f"Scheme 127 substrate 613 {subs}", [27], [
        P("reactant", f"613 ({subs})", "allene-vinyl cyclopropane"),
        P("catalyst", "[Rh(CO)2Cl]2", amounts=[("catalyst_loading", q(5, "mol%"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "cis-5/7-fused product"),
    ], conditions=[("temperature", q(100, "°C")), ("concentration", q(0.01, "M"))], outcomes=[("yield", q(yld, "%"), product)])
add("p0027_s127_615", "Scheme 127 substrate 615", [27], [
    P("reactant", "615", "allene-vinyl cyclopropane"),
    P("catalyst", "RhCl(PPh3)3", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "AgOTf", "silver triflate", amounts=[("amount", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "616", "cis-5/7-fused product"),
], conditions=[("temperature", q(100, "°C")), ("concentration", q(0.01, "M"))], outcomes=[("yield", q(70, "%"), "616")])
add("p0027_s127_617", "Scheme 127 chirality transfer", [27], [
    P("reactant", "617", "enantioenriched allene-vinyl cyclopropane"),
    P("catalyst", "RhCl(PPh3)3", amounts=[("catalyst_loading", q(1, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "618", "enantioenriched cis-5/7-fused product"),
], conditions=[("temperature", q(100, "°C"))], outcomes=[
    ("starting_material_enantiomeric_excess", q(91, "%", raw_text="91% ee"), "617"),
    ("enantiomeric_excess", q(92, "%", raw_text="92% ee"), "618")])

add("p0027_s128_619", "Scheme 128 cyclization to 620", [27], [
    P("reactant", "619", "dictamnol precursor"),
    P("catalyst", "[Rh(CO)2Cl]2", amounts=[("catalyst_loading", q(2.5, "mol%"))]),
    P("solvent", "DCE", "1,2-dichloroethane", "ClCCCl"), P("product", "620", "5/7-fused bicyclic intermediate"),
], conditions=[("temperature", q(80, "°C")), ("time", q(7, "h")), ("concentration", q(0.025, "M"))],
    outcomes=[("yield", q(76, "%"), "620")])
add("p0027_s128_620", "Scheme 128 oxidation/isomerization", [27], [
    P("reactant", "620", "dictamnol intermediate"), P("reagent", "[O]", "oxidant not specified"),
    P("product", "621", "oxidized/isomerized intermediate"),
], conditions=[("operation", "oxidation and isomerization")],
    unresolved=["The oxidant, conditions, and yield are not specified in the review scheme."])
add("p0027_s128_621", "Scheme 128 methylmagnesium bromide addition", [27], [
    P("reactant", "621", "dictamnol intermediate"), P("reagent", "MeMgBr", "methylmagnesium bromide"),
    P("product", "622A", "dictamnol diastereomer"), P("product", "622B", "(+)-dictamnol"),
], outcomes=[("product_ratio_622A_to_622B", "1:1", ["622A", "622B"])])
add("p0027_s128_623", "Scheme 128 cyclization to 624", [27], [
    P("reactant", "623", "aphanamol precursor"),
    P("catalyst", "[Rh(CO)2Cl]2", amounts=[("catalyst_loading", q(0.5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "624", "5/7-fused bicyclic intermediate"),
], conditions=[("temperature", q(110, "°C"))], outcomes=[("yield", q(93, "%"), "624")])
add("p0027_s128_624", "Scheme 128 DDQ oxidation", [27], [
    P("reactant", "624", "aphanamol intermediate"), P("reagent", "DDQ", "2,3-dichloro-5,6-dicyano-1,4-benzoquinone"),
    P("solvent", "CH2Cl2/H2O (10:1)"), P("product", "625", "oxidized aphanamol intermediate"),
], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(87, "%"), "625")])
add("p0027_s128_625", "Scheme 128 ozonolysis", [27], [
    P("reactant", "625", "aphanamol intermediate"), P("reagent", "O3", "ozone", "[O-][O+]=O"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"), P("reagent", "Me2S", "dimethyl sulfide", "CSC"),
    P("product", "626", "ozonolysis product"),
], conditions=[("temperature", q(-78, "°C")), ("operation", "ozonolysis followed by dimethyl sulfide workup")],
    outcomes=[("yield", q(61, "%"), "626")])
add("p0027_s128_626", "Scheme 128 reduction to (+)-aphanamol", [27], [
    P("reactant", "626", "aphanamol precursor"), P("reagent", "NaBH4", "sodium borohydride", "[Na+].[BH4-]"),
    P("reagent", "CeCl3·7H2O", "cerium(III) chloride heptahydrate"),
    P("solvent", "MeOH", "methanol", "CO"), P("product", "627", "(+)-aphanamol"),
], conditions=[("temperature", q(0, "°C"))], outcomes=[("yield", q(97, "%"), "627")])

add("p0027_s129_628", "Scheme 129 allenyl-ketone scope", [27], [
    P("reactant", "628 (R1/R2 scope)", "1,2-allenyl ketone"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Fe(CO)5", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "629", "lactone"),
], conditions=[("CO_concentration", q(64, "mM"))], outcomes=[
    ("yield", qr(54, 89, "%", "54–89%"), "629"), ("E_Z_ratio", "83:17 to 86:14", "629")])
add("p0027_s129_630", "Scheme 129 allenyl-imine scope", [27], [
    P("reactant", "630 (R1/R2 scope)", "1,2-allenyl imine"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Fe(CO)5", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "631", "lactam"),
], conditions=[("CO_concentration", q(64, "mM"))], outcomes=[
    ("yield", qr(62, 72, "%", "62–72%"), "631"), ("E_Z_ratio", "90:10 to 93:7", "631")])


# Page 28: Schemes 130--133.
add("p0028_s130_632", "Scheme 130 substrate 632 scope", [28], [
    P("reactant", "632 (n/X/R scope)", "5,6- or 6,7-alkadienyl aldehyde or ketone"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Ru3(CO)12", amounts=[("catalyst_loading", q(1, "mol%"))]),
    P("product", "635", "cis-fused alpha-methylene-gamma-butyrolactone"),
], conditions=[("temperature", q(120, "°C")), ("atmosphere", "CO, 20 atm")],
    outcomes=[("yield", qr(48, 82, "%", "48–82%"), "635")],
    notes=["Scope: n=1 or 2; X=NTs, NBoc, C(CO2Et)2, or O; R=H or Me."])
mechanism("p0028_s130_632_mechanism", "Scheme 130 proposed Ru carbonylation", [28],
          ["632", "633", "634", "635"],
          conditions=[("temperature", q(120, "°C")), ("atmosphere", "CO, 20 atm")])
add("p0028_s130_636", "Scheme 130 hydrazone 636", [28], [
    P("reactant", "636", "alkadienyl hydrazone"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Ru3(CO)12", amounts=[("catalyst_loading", q(1, "mol%"))]),
    P("product", "637", "cis-fused alpha-methylene-gamma-lactam"),
], conditions=[("temperature", q(120, "°C")), ("atmosphere", "CO, 20 atm")],
    outcomes=[("yield", q(53, "%"), "637")], notes=["The arrow is marked ibid relative to 632."])

add("p0028_s131_638", "Scheme 131 substrate 638 scope", [28], [
    P("reactant", "638 (X/R1 scope)", "allene-carbonyl substrate"),
    P("reagent", "R2Zn reagent (R2^2Zn or R2Li/ZnCl2)"),
    P("catalyst", "Ni(COD)2"), P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "642", "cis-2-vinylic five-membered cyclic alcohol"),
], conditions=[("temperature", q(0, "°C")), ("time", qr(10, 120, "min", "10 min–2 h"))],
    notes=["Scope: X=NTs, C(CO2Et)2, or CH2; R1=H, Me, or Et; R2=Me, Et, n-Bu, or Ph."])
mechanism("p0028_s131_638_mechanism", "Scheme 131 proposed Ni/organozinc pathway", [28],
          ["638", "639", "640", "641", "642"],
          conditions=[("temperature", q(0, "°C"))], notes=["The last operation is aqueous protonolysis."])
add("p0028_s131_643", "Scheme 131 substrate 643 scope", [28], [
    P("reactant", "643 (X/R1 scope)", "allene-carbonyl substrate"), P("reagent", "organozinc reagent (R2=Me or Et)"),
    P("catalyst", "Ni(COD)2", amounts=[("catalyst_loading", qr(10, 20, "mol%", "10–20 mol%"))]),
    P("solvent", "THF or ether"), P("product", "644", "cis-cyclic alcohol"),
], conditions=[("temperature", q(0, "°C"))], outcomes=[
    ("yield", qr(52, 77, "%", "52–77%"), "644"),
    ("diastereomer_ratio", "75:25 to >97:3", "644"),
    ("Z_E_ratio", "80:20 to 97:3 (R1=Ph)", "644")])

add("p0028_s132_645", "Scheme 132 cyclization to 646", [28], [
    P("reactant", "645", "testudinariol precursor"),
    P("catalyst", "Ni(COD)2", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("reagent", "Me2Zn", "dimethylzinc"), P("reagent", "Ti(O-i-Pr)4", "titanium tetraisopropoxide"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "646", "cyclized alcohol"),
], conditions=[("temperature", q(0, "°C"))], outcomes=[("yield", q(62, "%"), "646")])
add("p0028_s132_646_protection", "Scheme 132 TIPS protection", [28], [
    P("reactant", "646", "cyclized alcohol"), P("reagent", "TIPSOTf", "triisopropylsilyl triflate"),
    P("reagent", "2,6-lutidine", "2,6-dimethylpyridine", "Cc1cccc(C)n1"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"), P("product", "TIPS-protected 646 intermediate"),
], conditions=[("temperature", q(0, "°C"))], outcomes=[("yield", q(95, "%"), "TIPS-protected 646 intermediate")])
record = add("p0028_s132_647", "Scheme 132 conversion to 647", [28], [
    P("reactant", "TIPS-protected 646 intermediate"), P("reagent", "Li", "lithium", "[Li]"),
    P("reagent", "NH3", "ammonia", "N"), P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("reagent", "PPh3", "triphenylphosphine"), P("reagent", "imidazole", "imidazole", "c1ncc[nH]1"),
    P("reagent", "I2", "iodine", "II"), P("product", "647", "iodide testudinariol intermediate"),
], conditions=[("operation", "two-stage reduction/iodination sequence")], outcomes=[("yield", q(91, "%"), "647")])
set_steps(record, [
    (["TIPS-protected 646 intermediate", "Li", "NH3", "THF"], [("temperature", q(-78, "°C"))]),
    (["PPh3", "imidazole", "I2"], [("temperature", qr(0, 25, "°C", "0 °C to rt"))]),
])
add("p0028_s132_648", "Scheme 132 organolithium coupling", [28], [
    P("reactant", "647", "iodide testudinariol intermediate"),
    P("reactant", "dibromobis(trimethylsilyl)diene reagent (drawn)"),
    P("reagent", "s-BuLi", "sec-butyllithium"), P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "648", "coupled testudinariol intermediate"),
], conditions=[("temperature", qr(-78, 25, "°C", "−78 °C to rt")),
               ("operation", "organolithium generation at −78 °C followed by coupling")],
    outcomes=[("yield", q(38, "%"), "648")],
    unresolved=["The compact convergent-arrow layout does not label the lithiated reagent separately; its drawn precursor is retained textually."])
record = add("p0028_s132_649", "Scheme 132 conversion to (+)-testudinariol A", [28], [
    P("reactant", "648", "testudinariol precursor"), P("reagent", "Et2AlCl", "diethylaluminum chloride"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"), P("reagent", "Bu4NF", "tetrabutylammonium fluoride"),
    P("product", "649", "(+)-testudinariol A"),
], conditions=[("operation", "Lewis-acid treatment followed by fluoride deprotection")],
    outcomes=[("yield", q(55, "%"), "649")])
set_steps(record, [
    (["648", "Et2AlCl", "CH2Cl2"], [("temperature", qr(-78, 25, "°C", "−78 °C to rt"))]),
    (["Bu4NF"], [("temperature", "r.t.")]),
])

add("p0028_s133_650", "Scheme 133 substrate 650", [28], [
    P("reactant", "650", "1,2,7-triene"), P("catalyst", "RuCl(H)(CO)(PPh3)3", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "655", "vinyl cyclopentene"),
], conditions=[("temperature", "reflux")])
mechanism("p0028_s133_650_mechanism", "Scheme 133 proposed Ru hydrometalation cascade", [28],
          ["650", "651", "652", "653", "654", "655"], conditions=[("temperature", "reflux")])
for suffix, ar, yld, ratio in [("phenyl", "Ar=Ph", 71, "11:1"), ("thienyl", "Ar=2-thienyl", 64, "6.4:1")]:
    product = f"657 ({ar})"
    add(f"p0028_s133_656_{suffix}", f"Scheme 133 ether 656 {ar}", [28], [
        P("reactant", f"656 ({ar})", "allene-alkene ether"),
        P("catalyst", "RuCl(H)(CO)(PPh3)3", amounts=[("catalyst_loading", q(5, "mol%"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "1,4-diene"),
    ], conditions=[("temperature", "reflux")], outcomes=[
        ("yield", q(yld, "%"), product), ("trans_cis_ratio", ratio, product)],
        notes=["The arrow is marked ibid relative to 650."])


# Page 29: Schemes 134--138.
add("p0029_s134", "Scheme 134 scope", [29], [
    P("reactant", "allene (R1/R2 scope)"), P("reactant", "R3CHO", "aldehyde"),
    P("catalyst", "PdCl2(PPh3)2", amounts=[("catalyst_loading", None)]), P("reagent", "HCl-SnCl2"),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"), P("product", "658", "homoallylic alcohol"),
], conditions=[("temperature", "r.t."), ("catalyst_loading", None)],
    outcomes=[("yield", qr(45, 95, "%", "45–95%"), "658")],
    notes=["The arrow literally prints '2–5 mmol% PdCl2(PPh3)2'; the unsupported/ambiguous loading unit is retained here and not normalized to mol%."],
    unresolved=["The printed catalyst-loading unit 'mmol%' is ambiguous; no numerical catalyst loading is asserted."])
for suffix, rgroup, yld, ratio in [
    ("nbu", "R=n-Bu", 87, "92:8"), ("cyclohexyl", "R=cyclohexyl", 61, "94:6"),
    ("tbu", "R=t-Bu", 81, "99:1"), ("ph", "R=Ph", 87, "99:1"),
]:
    product = f"659A ({rgroup})"
    add(f"p0029_s135_659a_{suffix}", f"Scheme 135 hydrophosphorylation {rgroup}", [29], [
        P("reactant", f"monosubstituted allene ({rgroup})"), P("reactant", "cyclic phosphonate reagent (drawn)"),
        P("catalyst", "PdMe2(dppf)", amounts=[("catalyst_loading", None)]),
        P("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1"), P("product", product, "E-allylic phosphonate"),
    ], conditions=[("temperature", q(100, "°C")), ("catalyst_loading", None)], outcomes=[
        ("yield", q(yld, "%"), product), ("E_Z_ratio", ratio, product)],
        notes=["The scheme literally prints '3–5 mmol% PdMe2(dppf)'; the ambiguous unit is not normalized."],
        unresolved=["The printed catalyst-loading unit 'mmol%' is ambiguous."])
add("p0029_s135_659b", "Scheme 135 1,1-disubstituted allene scope", [29], [
    P("reactant", "1,1-disubstituted allene (R,R=Ph/Ph, Me/Me, or (CH2)5)"),
    P("reactant", "cyclic phosphonate reagent (drawn)"),
    P("catalyst", "PdMe2(dppf)", amounts=[("catalyst_loading", None)]),
    P("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1"), P("product", "659B", "allylic phosphonate"),
], conditions=[("temperature", qr(80, 100, "°C", "80–100 °C")), ("catalyst_loading", None)],
    outcomes=[("yield", qr(66, 92, "%", "66–92%"), "659B")],
    notes=["The arrow is marked ibid and inherits the literally printed, ambiguous '3–5 mmol%' catalyst notation."],
    unresolved=["The printed catalyst-loading unit 'mmol%' is ambiguous."])
add("p0029_s135_660", "Scheme 135 hydrosulfination scope", [29], [
    P("reactant", "allene (R=aryl, n-C7H15, or t-Bu)"), P("reactant", "TsNHNH2", "p-toluenesulfonyl hydrazide"),
    P("catalyst", "Pd(OAc)2", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "dppf", amounts=[("ligand_loading", q(10, "mol%"))]),
    P("reagent", "HOAc", "acetic acid", "CC(=O)O", [("amount", q(1.0, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "E-660", "linear allylic sulfone"),
], conditions=[("temperature", q(70, "°C"))], outcomes=[("yield", qr(44, 84, "%", "44–84%"), "E-660")],
    notes=["The review prose refers to E-670, whereas the scheme label is E-660; the scheme label is retained."])

for suffix, rgroup, yld, ee_value in [
    ("me", "R=Me", 25, 99), ("isobutyl", "R=i-PrCH2", 61, 88), ("allyl", "R=allyl", 82, 96),
    ("benzyl", "R=Bn", 90, 91), ("furfuryl", "R=2-C4H3OCH2", 81, 94), ("hydroxyl", "R=HO", 63, 82),
]:
    product = f"662 ({rgroup})"
    add(f"p0029_s136_{suffix}", f"Scheme 136 pronucleophile 661 {rgroup}", [29], [
        P("reactant", "propadienyl benzyl ether"), P("reactant", f"661 ({rgroup})", "pronucleophile"),
        P("catalyst", "[eta3-C3H5PdCl]2", amounts=[("catalyst_loading", q(1, "mol%"))]),
        P("reagent", "KOtBu", "potassium tert-butoxide", "CC(C)(C)[O-].[K+]", [("amount", q(5, "mol%"))]),
        P("unspecified_agent", "chiral ligand 663", amounts=[("ligand_loading", q(5, "mol%"))]),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", product, "enantioenriched allylation product"),
    ], conditions=[("temperature", q(80, "°C"))], outcomes=[
        ("yield", q(yld, "%"), product), ("enantiomeric_excess", q(ee_value, "%", raw_text=f"{ee_value}% ee"), product)])

for suffix, allene, hydride, product, yld in [
    ("sn_propadiene", "propadiene", "Ph3SnH", "664 (Y=Sn)", 40),
    ("ge_propadiene", "propadiene", "Ph3GeH", "664 (Y=Ge)", 88),
    ("ge_tridecadiene", "1,2-tridecadiene", "Ph3GeH", "665", 53),
    ("sn_silyl", "PhMe2SiCH=C=CH2", "Ph3SnH", "666", 40),
    ("sn_phenyl", "phenylallene", "Ph3SnH", "667", 100),
    ("ge_internal", "trideca-6,7-diene", "Ph3GeH", "668", 79),
]:
    add(f"p0029_s137_{suffix}", f"Scheme 137 {allene} with {hydride}", [29], [
        P("reactant", allene), P("reagent", hydride), P("catalyst", "Pd(PPh3)4"), P("product", product, "organotin/germanium addition product"),
    ], outcomes=[("yield", q(yld, "%"), product)],
        notes=["The prose reports low regioselectivity for the silyl-substituted allene case; only the labeled product is target-linked." ] if suffix == "sn_silyl" else None)

for suffix, subs, thiol, yld in [
    ("gemdimethyl", "R1=R2=Me", "RSH (aryl or alkyl)", qr(73, 94, "%", "73–94%")),
    ("methoxy", "R1=H; R2=OMe", "PhSH", q(83, "%")),
    ("hexyl", "R1=H; R2=C6H13", "PhSH", q(80, "%")),
    ("ester", "R1=H; R2=CO2Et", "PhSH", q(88, "%")),
]:
    product = f"669 ({subs})"
    add(f"p0029_s138_{suffix}", f"Scheme 138 {subs}", [29], [
        P("reactant", f"allene ({subs})"), P("reactant", thiol), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
        P("catalyst", "Pd(OAc)2/4 PPh3"), P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("product", product, "thiocarbonylation product"),
    ], conditions=[("temperature", q(100, "°C")), ("pressure", "CO, 400 psi")], outcomes=[("yield", yld, product)])
add("p0029_s138_670", "Scheme 138 cyclic-allene example", [29], [
    P("reactant", "cyclic allene (drawn)"), P("reactant", "PhSH", "thiophenol", "Sc1ccccc1"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"), P("catalyst", "Pd(OAc)2/4 PPh3"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "670", "cyclic thiocarbonylation product"),
], conditions=[("temperature", q(100, "°C")), ("pressure", "CO, 400 psi")], notes=["The arrow is marked ibid."])


# Page 30: Schemes 139--143 and the prose-only lead to Scheme 144.
record = add("p0030_s139", "Scheme 139 hydroboration/oxidation scope", [30], [
    P("reactant", "671 (R scope)", "chiral allene"), P("reagent", "9-BBN", "9-borabicyclo[3.3.1]nonane"),
    P("unspecified_agent", "672", "in-situ allylic borane"), P("reagent", "H2O2", "hydrogen peroxide", "OO"),
    P("reagent", "NaOH", "sodium hydroxide", "[Na+].[OH-]"),
    P("product", "673", "allylic alcohol diastereomer"), P("product", "674", "allylic alcohol diastereomer"),
], conditions=[("operation", "hydroboration followed by oxidative workup")], outcomes=[
    ("yield", qr(66, 82, "%", "66–82%"), ["673", "674"]),
    ("product_ratio_673_to_674", "5:1 to 18:1", ["673", "674"])],
    notes=["Scope: R=Me, n-C3H7, n-C4H9, n-C5H11, or (CH2)2OBn; the R=Me row is reported as 6:1."])
set_steps(record, [
    (["671 (R scope)", "9-BBN"], [("operation", "hydroboration to 672")]),
    (["672", "H2O2", "NaOH"], [("operation", "oxidation")]),
])
add("p0030_s140_575", "Scheme 140 allenol carbonylation", [30], [
    P("reactant", "575 (n=1 or 2)", "alpha- or beta-allenyl alcohol"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Ru3(CO)12", amounts=[("catalyst_loading", q(1, "mol%"))]),
    P("reagent", "NEt3", "triethylamine", "CCN(CC)CC"),
    P("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1"), P("product", "576", "alpha,beta-unsaturated lactone"),
], conditions=[("temperature", q(100, "°C")), ("atmosphere", "CO, 10 atm")],
    outcomes=[("yield", qr(91, 99, "%", "91–99%"), "576")])
add("p0030_s140_577", "Scheme 140 allenylamine carbonylation", [30], [
    P("reactant", "577 (n/R/X scope)", "alpha- or beta-allenylamine"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Ru3(CO)12", amounts=[("catalyst_loading", q(1, "mol%"))]),
    P("reagent", "Et3N", "triethylamine", "CCN(CC)CC", [("amount", q(1.5, "equiv"))]),
    P("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1"), P("product", "578", "alpha,beta-unsaturated lactam"),
], conditions=[("temperature", q(100, "°C")), ("atmosphere", "CO, 20 atm")],
    outcomes=[("yield", qr(54, 95, "%", "54–95%"), "578")],
    notes=["Scope: n=0 or 1; R=alkyl or aryl; X=Ts, Bn, or Mts."])
mechanism("p0030_s140_mechanism", "Scheme 140 proposed Ru carbonylation cycle", [30],
          ["577", "579", "580", "581", "578"],
          conditions=[("temperature", q(100, "°C")), ("atmosphere", "CO")])
add("p0030_s141", "Scheme 141 double cyclic hydroamination", [30], [
    P("reactant", "682", "1-(3′-butenyl)-4,5-allenylamine"),
    P("catalyst", "Cp*2SmCH(TMS)2", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("product", "683", "bicyclic amine"),
], conditions=[("temperature", q(45, "°C"))], outcomes=[("yield", q(80, "%"), "683")])

add("p0030_s142_684", "Scheme 142 alkoxyallene amidopalladation scope", [30], [
    P("reactant", "684 (PG scope)", "alkenyl carbamate/sulfonamide"), P("reactant", "ROCH=C=CH2 (R=Bn, Me, or Ph)", "alkoxyallene"),
    P("catalyst", "Pd(OAc)2", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("unspecified_agent", "dppp", amounts=[("ligand_loading", q(5, "mol%"))]),
    P("reagent", "Et3N or DBU"), P("product", "685", "cyclic amidopalladation product"),
], conditions=[("temperature", None), ("room_temperature_option", "r.t."),
               ("heated_temperature_option", q(60, "°C"))],
    outcomes=[("yield", qr(52, 85, "%", "52–85%"), "685")],
    unresolved=["Base and temperature alternatives are not mapped to individual protecting-group/substrate rows."])
add("p0030_s142_686", "Scheme 142 cyclic-amide scope", [30], [
    P("reactant", "686 (n=1, 2, or 3; R=H or propargyl)", "cyclic amide"),
    P("reactant", "benzyloxyallene"), P("catalyst", "Pd(OAc)2 (cat.)"), P("unspecified_agent", "dppp (cat.)"),
    P("reagent", "DBU"), P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "687", "bicyclic amidopalladation product"),
], conditions=[("temperature", q(60, "°C"))], outcomes=[("yield", qr(14, 77, "%", "14–77%"), "687")],
    unresolved=["Catalyst and ligand loadings are printed only as 'cat.' and are not inferred."])
add("p0030_s142_688", "Scheme 142 alcohol 688", [30], [
    P("reactant", "688", "alcohol"), P("reactant", "propadienyl methyl ether"),
    P("catalyst", "Pd(OAc)2", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "Et3N", "triethylamine", "CCN(CC)CC", [("amount", q(1.5, "equiv", raw_text="1.5×"))]),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "689", "acetal"),
], conditions=[("temperature", "reflux")], outcomes=[("yield", q(98, "%"), "689")])
for suffix, n_value, yld in [("n0", 0, 96), ("n1", 1, 89)]:
    product = f"691 (n={n_value})"
    add(f"p0030_s142_690_{suffix}", f"Scheme 142 alcohol 690 n={n_value}", [30], [
        P("reactant", f"690 (n={n_value})", "alcohol"), P("reactant", "propadienyl methyl ether"),
        P("catalyst", "Pd(OAc)2", amounts=[("catalyst_loading", q(5, "mol%"))]),
        P("reagent", "Et3N", "triethylamine", "CCN(CC)CC", [("amount", q(1.5, "equiv", raw_text="1.5×"))]),
        P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", product, "cyclic acetal"),
    ], conditions=[("temperature", "reflux")], outcomes=[("yield", q(yld, "%"), product)],
        notes=["The arrow is marked ibid relative to 688."])

add("p0030_s143_692", "Scheme 143 halopalladation scope", [30], [
    P("reactant", "692 (R1/R2 scope)", "2,3-allenyl acetate"),
    P("catalyst", "Pd(OAc)2", amounts=[("catalyst_loading", q(1.5, "mol%"))]),
    P("reagent", "LiBr", "lithium bromide", "[Li+].[Br-]", [("amount", q(2.5, "equiv"))]),
    P("solvent", "HOAc-acetone (1:1) or HOAc"), P("product", "693", "2-bromo-1(Z),3(E)-diene"),
], conditions=[("temperature", q(40, "°C"))],
    unresolved=["The two solvent choices are not mapped to individual substrate rows."])
mechanism("p0030_s143_692_mechanism", "Scheme 143 proposed halopalladation", [30],
          ["692", "694", "693"], conditions=[("temperature", q(40, "°C"))],
          notes=["The review attributes stereochemistry to a syn-syn intermediate and beta-acetoxy elimination."])
add("p0030_s143_695", "Scheme 143 allene racemization scope", [30], [
    P("reactant", "695 (R1/R2/R3 scope)", "optically active allene"),
    P("catalyst", "Pd(OAc)2", amounts=[("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "LiBr", "lithium bromide", "[Li+].[Br-]", [("amount", q(10, "mol%"))]),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "ent-695", "racemized/inverted allene"),
], conditions=[("temperature", q(50, "°C")), ("time", None),
               ("shortest_reported_time", q(1, "min", qualifier="lt", raw_text="<1 min")),
               ("longest_reported_time", q(3.3, "h"))],
    notes=["Scope: R1=Ph, Me, CH2OBn, or C5H11; R2=CH2Me, CH2OH, CH2OAc, or C5H11; R3=Me, H, CH(OAc)C7H15, NHBoc, or CH2CO2Et."])
add("p0030_s144_text_only", "Scheme 144 text-only overall reaction", [30], [
    P("reactant", "696", "allene-tethered enol silyl ether"),
    P("catalyst", "W(CO)6", "tungsten hexacarbonyl", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("product", "693 (label in page-30 prose)", "endo-cyclization product"),
], notes=["Only the page-30 prose was inspected; the Scheme 144 drawing is on page 31 and is outside this batch."],
    unresolved=["The product number 693 is retained from the extracted page-30 prose and may conflict with Scheme 143; page 31 was not claimed as covered."])
mechanism("p0030_s144_text_mechanism", "Scheme 144 prose-only proposed pathway", [30],
          ["696", "W(CO)5THF-activated allene", "699", "693 (label in page-30 prose)"],
          notes=["The prose proposes terminal-allene activation, endo carbon-nucleophile attack, and protonolysis."],
          unresolved=["The Scheme 144 drawing on page 31 was not inspected in this six-page batch."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

regions = {
    25: [
        ("左栏上部 Scheme 115", "引用工作：557范围、560、562及564的两个配体行分别记录；与第24页引入文字合并证据。"),
        ("左栏下部 Scheme 116", "引用工作及失败结果：566仅形成567；另一构造异构体明确标注Not formed。"),
        ("右栏 Scheme 117–119", "引用工作与机理：CO条件下七元环化、氘标记机理以及Ni介导576→579反应和提议路径。"),
    ],
    26: [
        ("左栏 Scheme 120–121", "引用工作/配位实验/机理：580配位、582羰基化、586范围、588/589分步及不对称羰基化逐箭头记录。"),
        ("右栏 Scheme 122–123", "引用工作：两个[4+4+1]行、二烯环加成、不对称行和端炔芳构化范围。"),
        ("右栏下部 Scheme 124", "引用工作：603的三个取代行逐行记录；CO或Fe2(CO)9选项映射保留未决。"),
    ],
    27: [
        ("左栏 Scheme 125–126", "引用工作：Ir催化605范围及607三行的608/609产物比；催化剂选项无法逐行映射。"),
        ("左栏下部至右栏上部 Scheme 127", "引用工作：610两行、613三行、615以及617手性转移分别记录。"),
        ("右栏 Scheme 128", "引用工作/合成序列：dictamnol与aphanamol的每条箭头单独编码，缺失试剂或收率保持missing。"),
        ("右栏下部 Scheme 129", "引用工作：allenyl ketone和imine两类Fe(CO)5/CO范围及E/Z范围。"),
    ],
    28: [
        ("左栏 Scheme 130–131", "引用工作与机理：Ru羰基化两行、Ni/organozinc范围及提议中间体分开。"),
        ("右栏上部 Scheme 132", "引用工作/全合成序列：645→646、保护、还原/碘化、汇聚偶联与脱保护按阶段记录；紧凑汇聚箭头保留未决。"),
        ("右栏下部 Scheme 133", "引用工作与机理：650 hydrometalation级联及656两个Ar行的收率和trans/cis。"),
    ],
    29: [
        ("左栏 Scheme 134–136", "引用工作/逐行范围：658范围、659A四行、659B、E-660及661六行；原图mmol%单位不作臆测换算。"),
        ("右栏 Scheme 137", "引用工作：六个hydrostannation/hydrogermylation箭头逐项记录。"),
        ("右栏下部 Scheme 138", "引用工作：669四行和循环联烯670；400 psi作为原文条件保存。"),
    ],
    30: [
        ("左栏 Scheme 139–140", "引用工作/分步操作与机理：671 hydroboration/oxidation、allenol/allenylamine羰基化及Ru路径。"),
        ("左栏下部 Scheme 141", "引用工作：Cp*2Sm催化双重环化氢胺化生成683。"),
        ("右栏 Scheme 142–143", "引用工作与机理：amidopalladation/oxypalladation各行、卤钯化范围与消旋范围。"),
        ("页底 Scheme 144引入正文", "仅按第30页正文建立text-only总体反应和提议路径；第31页图未检查且不声称覆盖。"),
    ],
}
unresolved = {
    25: ["Scheme 115/116的范围为综述汇总，未给出逐底物条件和测定基础。", "所有实例均为二手综述引用；原始论文及SI未提供。"],
    26: ["Scheme 120的催化剂/溶剂选项和Scheme 124的CO/Fe2(CO)9选项未逐行映射。", "多处收率为汇总范围，测定基础缺失。"],
    27: ["Scheme 126的多个Rh催化剂无法对应到每一行。", "Scheme 128的[O]/isomerization箭头缺具体试剂、条件和收率。"],
    28: ["Scheme 132汇聚箭头中的未编号有机锂物种无法从综述图可靠命名，保留绘图标签。", "Scheme 131若干范围缺收率或逐底物映射。"],
    29: ["Schemes 134–135印作mmol%的催化剂负载单位含义不明确，未换算为mol%。", "Scheme 137的低区域选择性副产物未给出可分配收率。"],
    30: ["Scheme 142的碱/温度选项未逐底物映射，若干催化剂仅标cat.。", "Scheme 144图位于第31页；仅编码第30页正文，产物编号冲突保留待核。"],
}
coverage_pages = []
for page in range(25, 31):
    image_id = f"{DOC}:page{page}:image"
    coverage_pages.append({
        "page": page,
        "state": "attempted",
        "regions": [{
            "region": region, "finding": finding,
            "evidence_ids": [image_id, f"{DOC}:page{page}:text"],
        } for region, finding in regions[page]],
        "record_ids": [r["record_id"] for r in records if image_id in r["evidence_ids"]],
        "unresolved": unresolved[page],
    })
coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": coverage_pages}
coverage_path = BASE / "coverage" / "pages_0025_0030.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    for page in range(25, 31):
        if task.get("evidence_id") == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(coverage_path)}, ensure_ascii=False))
