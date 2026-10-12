#!/usr/bin/env python3
"""Build source-linked review-reaction records for PDF pages 19--24."""
import json
import re
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
OUT = Path(__file__).with_name("records_pages_0019_0024.json")
records = []


def ev(pages):
    ids = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def slug(value):
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()[:36] or "entity"


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
        "amounts": [
            {"name": name, "fact": fact(value, evidence)} for name, value in amounts
        ],
    }


def add(rid, source_id, pages, parts, conditions=None, outcomes=None, notes=None,
        unresolved=None, kind="literature_example"):
    evidence = ev(pages)
    ps = [participant(i, spec, evidence) for i, spec in enumerate(parts, 1)]
    ids = {p["label"]["value"]: p["entity_id"] for p in ps}
    conds = list(conditions or [])
    if kind == "literature_example":
        if not any(name == "temperature" for name, _ in conds):
            conds.append(("temperature", None))
        if not any(name == "time" for name, _ in conds):
            conds.append(("time", None))
    output_fields = []
    supplied_yield = False
    for name, value, targets in outcomes or []:
        field = {"name": name, "fact": fact(value, evidence)}
        if targets:
            if isinstance(targets, str):
                targets = [targets]
            field["target_entity_ids"] = [ids[target] for target in targets]
        output_fields.append(field)
        supplied_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(x["name"] == "yield" for x in output_fields):
        products = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if products:
            missing["target_entity_ids"] = products
        output_fields.append(missing)
    if supplied_yield:
        output_fields.append({"name": "yield_measurement_basis", "fact": fact(None, evidence)})
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
            "conditions": [
                {"name": name, "fact": fact(value, evidence)} for name, value in conds
            ],
        }] if conds else [],
        "outcomes": output_fields,
        "notes": [fact(note, evidence) for note in notes or []],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "Secondary-review example: the cited primary article and supporting information were not supplied.",
                "Generic or complex drawings remain label-only; all candidate structures are unverified.",
            ],
        },
    }
    records.append(record)
    return record


def mechanism(rid, source_id, pages, sequence, conditions=None, notes=None):
    parts = []
    for i, label in enumerate(sequence):
        role = "reactant" if i == 0 else ("product" if i == len(sequence) - 1 else "unspecified_agent")
        parts.append(P(role, label))
    return add(
        rid, source_id, pages, parts, conditions=conditions, notes=notes,
        unresolved=["The arrows are a proposed pathway, not independently reported experimental operations."],
        kind="mechanism",
    )


def set_steps(record, step_specs):
    evidence = record["evidence_ids"]
    ids = {p["label"]["value"]: p["entity_id"] for p in record["participants"]}
    record["steps"] = []
    for index, (labels, conditions) in enumerate(step_specs, 1):
        record["steps"].append({
            "step_id": f"step{index}",
            "participant_ids": [ids[label] for label in labels],
            "conditions": [
                {"name": name, "fact": fact(value, evidence)} for name, value in conditions
            ],
        })


# Page 19: complete the cross-page Scheme 88--90 records from page 18.
add("p0018_s88_422", "Scheme 88 compound 422", [18, 19], [
    P("reactant", "422", "4-hydroxycoumarin"),
    P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None,
      [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "423", "bis(propen-2-yl)propenylation product"),
], conditions=[("temperature", q(80, "°C"))])
add("p0018_s88_423", "Scheme 88 cyclization of 423", [18, 19], [
    P("reactant", "423", "bis(propen-2-yl)propenylation product"),
    P("product", "424", "tricyclic product"),
], outcomes=[("yield", q(34, "%"), "424")])
add("p0018_s88_425", "Scheme 88 compound 425", [18, 19], [
    P("reactant", "425", "dimethyl 3-oxoglutarate"),
    P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None,
      [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "426", "bis(propen-2-yl)propenylation product"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", q(89, "%"), "426")],
    notes=["The arrow is marked ibid relative to the 422 reaction."])
scheme88_rows = [
    ("p0018_s88_427", "X=Y=Ac", 90),
    ("p0019_s88_427_ac_co2me", "X=Ac; Y=CO2Me", 92),
    ("p0019_s88_427_cyclic", "X,Y=cyclic ketal-like dicarbonyl group drawn", 61),
    ("p0019_s88_427_so2ph", "X=Y=SO2Ph", 47),
]
for rid, subs, yld in scheme88_rows:
    product = f"428 ({subs})"
    add(rid, f"Scheme 88 compound 427 {subs}", [18, 19], [
        P("reactant", f"427 ({subs})", "methylene pronucleophile"),
        P("reactant", "propadiene", "propadiene", "C=C=C"),
        P("catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", None,
          [("catalyst_loading", q(5, "mol%"))]),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("product", product, "bis(propen-2-yl)propenylation product"),
    ], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", q(yld, "%"), product)],
        notes=["The arrow is marked ibid relative to the 422 reaction."],
        unresolved=["The compact cyclic X,Y drawing is retained as a visual label rather than transcribed to a structure."] if "cyclic" in subs else None)
mechanism("p0018_s89_mechanism", "Scheme 89 proposed Pd pathways", [18, 19],
          ["Pd(0) + two propadienes", "417a / pi-allyl PdX", "429 / 431", "430 / 432"],
          notes=["The review presents oxidative-addition/double-reductive-elimination and hydropalladation/carbopalladation alternatives."])
add("p0018_s90_text_only", "Scheme 90 dimeric cyclometalation scope", [18, 19], [
    P("reactant", "433 (R1/R2 scope; two molecules)", "2,3-allenol"),
    P("catalyst", "CpRu(MeCN)3PF6", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "Cu(OAc)2", "copper(II) acetate", None, [("amount", q(10, "mol%"))]),
    P("reagent", "i-Pr2NEt", "diisopropylethylamine", None, [("amount", q(3, "equiv"))]),
    P("reagent", "HOAc", "acetic acid", "CC(=O)O", [("amount", q(1.5, "equiv"))]),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "437", "5-acetoxy-3-methylenealk-5-en-1,7-diol"),
], outcomes=[("yield", qr(62, 73, "%", "62–73%"), "437")],
    notes=["Scope: R1=R2=C3H7-n, C5H11, or Ph; R1=Me/R2=Ph; or R1,R2=(CH2)4."])
mechanism("p0019_s90_mechanism", "Scheme 90 proposed Ru pathway", [19],
          ["433", "434", "435", "436", "437"],
          notes=["The depicted sequence is cyclometalation, reductive elimination, and intramolecular protonolysis of a C-Ru bond."])

add("p0019_s91", "Scheme 91 scope", [19], [
    P("reactant", "allene (R/tether scope)"), P("reactant", "CO2", "carbon dioxide", "O=C=O"),
    P("reactant", "ArCHO", "aromatic aldehyde"), P("unspecified_agent", "Ni(COD)2"),
    P("reagent", "PPTS", "pyridinium p-toluenesulfonate"),
    P("product", "442", "cis-alpha-methylene-gamma-butyrolactone"),
], outcomes=[("yield", qr(46, 73, "%", "46–73%"), "442")],
    notes=["R/tether scope includes (CH2)3OBn, (CH2)2OBn, (CH2)2Ph, imide tethers (n=2 or 3), and a cyclohexyl tether."])
mechanism("p0019_s91_mechanism", "Scheme 91 proposed cyclometalation/lactonization", [19],
          ["allene + CO2", "438 / 439 / 440", "441", "442"],
          notes=["Aldehyde addition precedes PPTS-promoted lactonization."])
scheme92 = add("p0019_s92", "Scheme 92 scope", [19], [
    P("reactant", "443 (R scope)", "1-(trimethylsilyl)-1,2-allene"),
    P("reactant", "CO2", "carbon dioxide", "O=C=O"),
    P("unspecified_agent", "Ni(COD)2"),
    P("reagent", "DBU", "1,8-diazabicyclo[5.4.0]undec-7-ene", None, [("amount", q(2, "equiv"))]),
    P("solvent", "THF or toluene"),
    P("reagent", "R1R2SiH (Ph3SiH, PhMe2SiH, or Ph2MeSiH)"),
    P("reagent", "H3O+", "aqueous acid"), P("reagent", "CH2N2", "diazomethane", "C=[N+]=[N-]"),
    P("product", "445", "2-(trimethylsilylmethyl)-2(E)-alkenoate"),
], outcomes=[("yield", qr(45, 78, "%", "45–78%"), "445")],
    notes=["The review states that Et3SiH gives a lower yield; no separate numerical row is shown."],
    unresolved=["The amount of Ni(COD)2 and the CO2 pressure are not printed."])
set_steps(scheme92, [
    (["443 (R scope)", "CO2", "Ni(COD)2", "DBU", "THF or toluene"], [("temperature", None), ("time", None)]),
    (["R1R2SiH (Ph3SiH, PhMe2SiH, or Ph2MeSiH)"], [("temperature", q(40, "°C"))]),
    (["H3O+"], [("operation", "acid treatment")]),
    (["CH2N2"], [("operation", "methylation after workup")]),
])
add("p0019_s92_electrocarboxylation", "Scheme 92 prose-only electrocarboxylation", [19], [
    P("reactant", "allene"), P("reactant", "CO2", "carbon dioxide", "O=C=O"),
    P("catalyst", "Ni(II) catalyst (unspecified)"),
    P("product", "unsaturated carboxylic acids"),
], outcomes=[("selectivity", "poor selectivity", "unsaturated carboxylic acids")],
    unresolved=["Catalyst identity, electrochemical setup, conditions, product mapping, and yield are not given on this review page."])

# Scheme 93 prose starts on page 19 and the drawings are on page 20.
for n_value, yld in [(0, 60), (1, 50)]:
    product = f"447 (n={n_value})"
    add(f"p0020_s93_446_n{n_value}", f"Scheme 93 substrate 446 n={n_value}", [19, 20], [
        P("reactant", f"446 (n={n_value})", "allene-alkyne"),
        P("reagent", "Fe(CO)4(NMe3)"), P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("product", product, "Pauson-Khand-type product"),
    ], conditions=[("temperature", "r.t."), ("operation", "hν irradiation")],
        outcomes=[("yield", q(yld, "%"), product)])
add("p0020_s93_448", "Scheme 93 substrate 448", [19, 20], [
    P("reactant", "448", "3-methylthio-1,2-nonadien-8-yne"), P("reagent", "Fe(CO)4(NMe3)"),
    P("product", "449", "5/7-fused bicyclic product"), P("product", "450", "pi-allyl iron complex"),
], conditions=[("operation", "hν irradiation")], outcomes=[
    ("yield", q(15, "%"), "449"), ("yield", q(32, "%"), "450"),
])
add("p0020_s93_450", "Scheme 93 conversion of 450", [19, 20], [
    P("reactant", "450", "pi-allyl iron complex"), P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "449", "5/7-fused bicyclic product"),
], conditions=[("temperature", "reflux")])

# Page 20: Schemes 94--97.
add("p0020_s94_451", "Scheme 94 substrate 451", [20], [
    P("reactant", "451", "TMS-substituted allene-alkyne cobalt complex"),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("reagent", "air"), P("product", "452", "5/6-fused bicyclic enone"),
    P("product", "453", "5/5-fused bicyclic product"),
], conditions=[("temperature", q(40, "°C")), ("time", q(27, "h"))], outcomes=[
    ("yield", q(60, "%"), ["452", "453"]),
    ("product_ratio_452_to_453", "45:55", ["452", "453"]),
    ("E_Z_ratio_for_453", "10:1", "453"),
])
add("p0020_s94_454", "Scheme 94 substrate 454", [20], [
    P("reactant", "454", "TMS-substituted allene-alkyne"),
    P("reagent", "Cp2ZrCl2/n-BuLi"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("product", "452", "5/6-fused bicyclic enone"), P("product", "453", "E-5/5-fused bicyclic product"),
], conditions=[("time", q(2, "h")), ("operation", "1) zirconocene/n-BuLi; 2) CO")], outcomes=[
    ("yield", q(48, "%"), ["452", "453"]),
    ("product_ratio_452_to_453", "5:95", ["452", "453"]),
    ("stereochemical_result", "453 formed as E only", "453"),
])
add("p0020_s95", "Scheme 95", [20], [
    P("reactant", "455 (95% ee)", "optically active allene-alkyne"),
    P("reagent", "Cp2ZrCl2"), P("reagent", "n-BuLi"), P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("product", "E-(S)-456", "optically active bicyclic enone"),
], conditions=[("time", q(2, "h"))], outcomes=[
    ("yield", q(39, "%"), "E-(S)-456"), ("enantiomeric_excess", q(85, "%", raw_text="85% ee"), "E-(S)-456"),
], notes=["The reaction arrow prints a CO pressure of 20 psi; pressure is retained as source text because psi is not an allowed structured quantity unit."])
add("p0020_s96", "Scheme 96 overall", [20], [
    P("reactant", "457 (R variable)", "5,6-alkadienyne"), P("catalyst", "CpCo(CO)2"),
    P("solvent", "xylenes"), P("product", "463", "cyclohexadiene derivative"),
], conditions=[("temperature", "heat"), ("operation", "hν irradiation"), ("time", q(3, "h"))])
mechanism("p0020_s96_mechanism", "Scheme 96 proposed Co pathway", [20],
          ["457", "458", "459", "460", "461", "462", "463"],
          notes=["The review proposes allylic C-H activation, hydrometalation, a second C-H activation, double-bond migration, and reductive elimination."])
scheme97 = [
    ("nc7_h", "R1=n-C7H15; R2=H", 75), ("ph_h", "R1=Ph; R2=H", 70),
    ("nc7_tms", "R1=n-C7H15; R2=TMS", 75), ("h_tms", "R1=H; R2=TMS", 68),
]
for suffix, subs, yld in scheme97:
    product = f"465 ({subs})"
    add(f"p0020_s97_464_{suffix}", f"Scheme 97 compound 464 {subs}", [20], [
        P("reactant", f"464 ({subs})", "allene-alkyne"), P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"),
        P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", product, "5/5-fused bicyclic ketone"),
    ], conditions=[("temperature", q(100, "°C"))], outcomes=[("yield", q(yld, "%"), product)])
add("p0020_s97_466", "Scheme 97 optically active substrate 466", [20], [
    P("reactant", "466 (95% ee)", "optically active allene-alkyne"),
    P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"), P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "467", "bicyclic ketone diastereomer"),
    P("product", "468", "bicyclic ketone diastereomer"),
], conditions=[("temperature", q(98, "°C"))], outcomes=[
    ("yield", q(80, "%"), ["467", "468"]), ("product_ratio_467_to_468", "8:1", ["467", "468"]),
    ("enantiomeric_excess", q(95, "%", raw_text="95% ee"), "467"),
    ("enantiomeric_excess", q(63, "%", raw_text="63% ee"), "468"),
])

# Scheme 98 is introduced on page 20 and drawn on page 21.
for suffix, substrate, product, yld in [
    ("469", "469", "470", 60), ("471", "471", "472", 42), ("473", "473", "474", 66),
]:
    add(f"p0021_s98_{suffix}", f"Scheme 98 substrate {substrate}", [20, 21], [
        P("reactant", substrate, "allene-alkyne"), P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"),
        P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", product, "bicyclic enone"),
    ], conditions=[("temperature", q(100, "°C")), ("atmosphere", "Ar")], outcomes=[("yield", q(yld, "%"), product)],
        notes=["The 471 arrow is marked ibid relative to 469."] if substrate == "471" else None)
for suffix, subs, ratio, yld in [
    ("n1_h", "n=1; R=H", "7:1", 73), ("n1_tms", "n=1; R=TMS", "100:0", 50),
    ("n2_h", "n=2; R=H", "6:1", 62),
]:
    add(f"p0021_s98_475_{suffix}", f"Scheme 98 substrate 475 {subs}", [20, 21], [
        P("reactant", f"475 ({subs})", "allene-alkyne"), P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"),
        P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", f"476 ({subs})", "5/6-fused bicyclic enone"), P("product", f"477 ({subs})", "5/5-fused bicyclic enone"),
    ], conditions=[("temperature", q(100, "°C")), ("atmosphere", "Ar")], outcomes=[
        ("yield", q(yld, "%"), [f"476 ({subs})", f"477 ({subs})"]),
        ("product_ratio_476_to_477", ratio, [f"476 ({subs})", f"477 ({subs})"]),
    ], notes=["The arrow is marked ibid relative to the preceding Mo(CO)6/DMSO/toluene/Ar conditions."])
for suffix, subs, yld in [("me", "R1=Me", 59), ("cyclohexyl", "R1,R1=(CH2)5", 58)]:
    product = f"479 ({subs})"
    add(f"p0021_s98_478_{suffix}", f"Scheme 98 substrate 478 {subs}", [20, 21], [
        P("reactant", f"478 ({subs})", "1,1,3-trisubstituted allene-alkyne"),
        P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"), P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "5/5-fused bicyclic enone"),
    ], conditions=[("temperature", q(100, "°C")), ("atmosphere", "Ar")], outcomes=[("yield", q(yld, "%"), product)])

# Page 21: Schemes 99--101.
add("p0021_s99_480", "Scheme 99 Pauson-Khand step", [21], [
    P("reactant", "480", "allene-alkyne prostaglandin precursor"), P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "481", "bicyclic enone"),
], conditions=[("temperature", q(110, "°C")), ("time", q(10, "min"))], outcomes=[("yield", q(69, "%"), "481")])
add("p0021_s99_481", "Scheme 99 unannotated conversion", [21], [
    P("reactant", "481", "bicyclic enone"), P("product", "482", "hydroxymethylacylfulvene precursor"),
], unresolved=["The review shows a downward multi-arrow conversion but supplies no reagents, conditions, time, or yield."])
add("p0021_s99_482", "Scheme 99 formaldehyde step", [21], [
    P("reactant", "482", "hydroxymethylacylfulvene precursor"), P("reactant", "formaldehyde", "formaldehyde", "C=O"),
    P("reagent", "H+", "acid"), P("product", "483", "hydroxymethylacylfulvene"),
])
for suffix, subs, yld in [("h_tms", "R1=H; R2=TMS", 59), ("ph_tms", "R1=Ph; R2=TMS", 55), ("h_h", "R1=R2=H", 50)]:
    product = f"485 ({subs})"
    add(f"p0021_s100_{suffix}", f"Scheme 100 allenamide-alkyne {subs}", [21], [
        P("reactant", f"484 ({subs})", "allenamide-alkyne"),
        P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl", None, [("amount", q(1.2, "equiv"))]),
        P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", product, "5/5-fused bicyclic ketone"),
    ], conditions=[("temperature", "heat")], outcomes=[("yield", q(yld, "%"), product)])
add("p0021_s101_486", "Scheme 101 substrate 486 scope", [21], [
    P("reactant", "486 (R1/R2 scope)", "silicon-tethered allene-alkyne"),
    P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl", None, [("amount", q(1.2, "equiv"))]),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "487", "5/5-fused bicyclic ketone"),
], conditions=[("temperature", q(90, "°C"))], outcomes=[("yield", qr(36, 64, "%", "36–64%"), "487")],
    notes=["Scope: R1=alkyl or H; R2=H, alkyl, TMS, or Ph."])
add("p0021_s101_488", "Scheme 101 substrate 488", [21], [
    P("reactant", "488", "silicon-tethered allene-alkyne"), P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "E-489", "bicyclic enone isomer"), P("product", "Z-489", "bicyclic enone isomer"),
], conditions=[("temperature", q(100, "°C"))], outcomes=[("yield", q(38, "%"), ["E-489", "Z-489"])])
add("p0021_s101_489_resolution", "Scheme 101 printed E/Z-489 treatment", [21], [
    P("reactant", "E-489 + Z-489", "bicyclic enone mixture"),
    P("reagent", "(HSCH2)2CH2", "1,3-propanedithiol"), P("reagent", "BF3·OEt2", "boron trifluoride etherate"),
    P("product", "E-489 (printed product label)", "E-bicyclic enone"),
], outcomes=[("yield", q(64, "%"), "E-489 (printed product label)")],
    unresolved=["The review arrow returns to an E-489 label with an apparently unchanged enone drawing; the exact chemical operation requires the primary article."])
add("p0021_s101_490", "Scheme 101 reduction to E-490", [21], [
    P("reactant", "E-489", "bicyclic enone"), P("reagent", "DIBAL-H", "diisobutylaluminum hydride"),
    P("solvent", "Et2O", "diethyl ether", "CCOCC"), P("reagent", "15% NaOH workup", "sodium hydroxide"),
    P("product", "E-490", "allylic alcohol"),
], conditions=[("temperature", q(-78, "°C")), ("workup", "15% NaOH")])
add("p0021_s101_491", "Scheme 101 desilylation to E-491", [21], [
    P("reactant", "E-490", "silylated allylic alcohol"), P("reagent", "BTAF", "benzyltrimethylammonium fluoride"),
    P("solvent", "HMPA:THF (2:1)"), P("reagent", "buffer pH 7.38"),
    P("product", "E-491", "silanol/desilylation product"),
])
add("p0021_s101_492", "Scheme 101 conversion to prostaglandin 492", [21], [
    P("reactant", "E-491", "prostaglandin precursor"), P("product", "492", "15-deoxy-Delta12,14-prostaglandin J2"),
], unresolved=["The vertical arrow has no printed reagents, conditions, time, or yield on this review page."])

# Scheme 102 starts in page-21 prose and is drawn on page 22.
for suffix, subs, yld in [
    ("me_h", "R1=Me; R2=H", 64), ("me_bu", "R1=Me; R2=Bu", 75),
    ("me_ph", "R1=Me; R2=Ph", 51), ("c5_h", "R1=C5H11; R2=H", 55),
]:
    product = f"493 ({subs})"
    add(f"p0022_s102_486_{suffix}", f"Scheme 102 substrate 486 {subs}", [21, 22], [
        P("reactant", f"486 ({subs})", "silicon-tethered allene-alkyne"),
        P("catalyst", "[Rh(CO)2Cl]2", None, None, [("catalyst_loading", q(5, "mol%"))]),
        P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "5/6-fused bicyclic product"),
    ], conditions=[("temperature", q(90, "°C"))], outcomes=[("yield", q(yld, "%"), product)],
        notes=["The reaction arrow prints CO at 1 atm; pressure is retained as source text because atm is not an allowed structured quantity unit."])
add("p0022_s102_494_mo", "Scheme 102 substrate 494 Mo branch", [22], [
    P("reactant", "494 (PG/R1/R2/R3 scope)", "allene-alkyne"), P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl"),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "495", "5/5-fused bicyclic ketone"),
], conditions=[("temperature", q(90, "°C"))], outcomes=[("yield", qr(72, 95, "%", "72–95%"), "495")])
add("p0022_s102_494_rh", "Scheme 102 substrate 494 Rh branch", [22], [
    P("reactant", "494 (PG/R1/R2/R3 scope)", "allene-alkyne"), P("catalyst", "[Rh(CO)2Cl]2"),
    P("unspecified_agent", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1"),
    P("unspecified_agent", "AgBF4", "silver tetrafluoroborate"), P("solvent", "DCE", "1,2-dichloroethane", "ClCCCl"),
    P("product", "496", "5/6-fused bicyclic ketone"),
], conditions=[("temperature", q(40, "°C"))], outcomes=[("yield", qr(72, 98, "%", "72–98%"), "496")])
add("p0022_s102_497", "Scheme 102 substrate 497", [22], [
    P("reactant", "497", "bis-allene/alkyne substrate"), P("catalyst", "[Rh(CO)2Cl]2", None, None,
      [("catalyst_loading", q(5, "mol%"))]), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "498", "polycyclic Pauson-Khand product"),
], conditions=[("temperature", "r.t."), ("time", q(18, "h"))], outcomes=[("yield", q(61, "%"), "498")],
    notes=["The reaction arrow prints CO at 1 atm; pressure is retained as source text because atm is not an allowed structured quantity unit."])

# Page 22: Schemes 103--105.
add("p0022_s103_499", "Scheme 103 substrate 499 scope", [22], [
    P("reactant", "499 (R1/R2/R3/R4 scope)", "1,2-allen-7-yne"),
    P("catalyst", "[Rh(CO)2Cl]2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "500", "5/6-fused bicyclic product"),
], outcomes=[("yield", qr(22, 88, "%", "22–88%"), "500")],
    notes=["The reaction arrow prints CO at 1 atm; pressure is retained as source text because atm is not an allowed structured quantity unit."])
for suffix, r_group, yld in [("tms", "R=TMS", 88), ("me", "R=Me", 47), ("ph", "R=Ph", 60)]:
    product = f"502 ({r_group})"
    add(f"p0022_s103_501_{suffix}", f"Scheme 103 substrate 501 {r_group}", [22], [
        P("reactant", f"501 ({r_group})", "1,2-allen-7-yne"),
        P("catalyst", "[Ir(COD)Cl]2", None, None, [("catalyst_loading", q(10, "mol%"))]),
        P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "5/6-fused bicyclic product"),
    ], outcomes=[("yield", q(yld, "%"), product)],
        notes=["The reaction arrow prints CO at 1 atm; pressure is retained as source text because atm is not an allowed structured quantity unit."])
add("p0022_s103_503_505", "Scheme 103 sulfone scope", [22], [
    P("reactant", "503 or 505 (R=H or Ph; E=CO2Me)", "1,2-allenyl sulfone-alkyne"),
    P("catalyst", "[RhCl(CO)2]2 or printed [RhCl(CO)(dppp)]2", None, None,
      [("catalyst_loading", q(2.5, "mol%"))]),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "504 or 506", "5/7-fused bicyclic enone"),
], outcomes=[("yield", qr(40, 84, "%", "40–84%"), "504 or 506")],
    notes=["The reaction arrow prints CO at 1 atm; pressure is retained as source text because atm is not an allowed structured quantity unit."],
    unresolved=["The compact second rhodium catalyst formula and substrate-to-catalyst/yield mapping require the primary paper."])
add("p0022_s104", "Scheme 104", [22], [
    P("reactant", "507", "guanacastepene-A precursor"),
    P("catalyst", "[Rh(CO)2Cl]2", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "508", "guanacastepene-A skeleton"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", q(65, "%"), "508")],
    notes=["The reaction arrow prints CO at 1 atm; pressure is retained as source text because atm is not an allowed structured quantity unit."])
add("p0022_s105", "Scheme 105", [22], [
    P("reactant", "509", "1,2-allen-6-yne"), P("catalyst", "Cp2Ti(CO)2", None, None,
      [("catalyst_loading", q(10, "mol%"))]), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "511", "Pauson-Khand product"),
], conditions=[("temperature", q(90, "°C"))], outcomes=[("yield", q(86, "%"), "511")],
    notes=["The reaction arrow prints a CO pressure of 18 psi; pressure is retained as source text because psi is not an allowed structured quantity unit."])
mechanism("p0022_s105_mechanism", "Scheme 105 titanacycle", [22], ["509", "510", "511"],
          conditions=[("temperature", q(90, "°C"))],
          notes=["The proposed sequence is drawn under CO at 18 psi; pressure remains source text because psi is not an allowed structured quantity unit."])

# Page 23: Schemes 106--109.
add("p0023_s106_512", "Scheme 106 substrate 512 scope", [22, 23], [
    P("reactant", "512 (X/R1/R2/R3 scope)", "allene-alkyne"),
    P("catalyst", "[Rh(CO)2Cl]2", None, None, [("catalyst_loading", q(2, "mol%"))]),
    P("solvent", "toluene or CH2Cl2 or DCE"), P("product", "513", "cyclometalation/beta-H-elimination product"),
], conditions=[("temperature_option_room_temperature", "r.t."),
               ("temperature_option_high", q(90, "°C")), ("atmosphere", "N2")], outcomes=[
    ("yield", qr(45, 93, "%", "45–93%"), "513"), ("E_Z_ratio", "2:1 to 6:1", "513"),
], notes=["Scope: X=CH(CO2Me)2, NTs, O, or CH2; R1=H/TMS/Me; R2=H/alkyl; R3=H/CH2OH."],
    unresolved=["Solvent and temperature options are not mapped to individual scope rows."])
mechanism("p0023_s106_512_mechanism", "Scheme 106 proposed pathway from 512", [22, 23],
          ["512", "514", "513"], notes=["The review attributes product formation to cyclometalation, beta-H elimination, and reductive elimination."])
add("p0023_s106_515", "Scheme 106 substrate 515", [22, 23], [
    P("reactant", "515 (R1/R2 scope)", "1,2-allenyl sulfone-alkyne"),
    P("catalyst", "[Rh(CO)2Cl]2", None, None, [("catalyst_loading", q(2, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "516", "cyclized product"),
], conditions=[("temperature", "reflux"), ("atmosphere", "N2")])
add("p0023_s106_517", "Scheme 106 substrate 517", [22, 23], [
    P("reactant", "517 (R1/R2 scope)", "tetrasubstituted 1,2-allenyl sulfone-alkyne"),
    P("catalyst", "[Rh(CO)2Cl]2", None, None, [("catalyst_loading", q(2, "mol%"))]),
    P("solvent", "xylene"), P("product", "519", "cyclobutene-fused product"),
], conditions=[("temperature", "reflux")], notes=["Intermediate 518 undergoes a further electrocyclization."])
mechanism("p0023_s106_517_mechanism", "Scheme 106 electrocyclization branch", [22, 23],
          ["517", "518", "519"], conditions=[("temperature", "xylene reflux")])
add("p0023_s107_521", "Scheme 107 product 521 scope", [22, 23], [
    P("reactant", "520 (R1/R2 scope)", "double allene-alkyne substrate"),
    P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl", None, [("amount", q(10, "equiv"))]),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O", [("amount", q(20, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "521", "tetracyclic product"),
], conditions=[("temperature", qr(53, 55, "°C", "53–55 °C")), ("time", q(48, "h")), ("atmosphere", "Ar")],
    outcomes=[("yield", qr(65, 70, "%", "65–70%"), "521")])
add("p0023_s107_522", "Scheme 107 product 522 scope", [22, 23], [
    P("reactant", "520 (R1/R2 scope)", "double allene-alkyne substrate"),
    P("reagent", "Mo(CO)6", "molybdenum hexacarbonyl", None, [("amount", q(2.2, "equiv"))]),
    P("reagent", "DMSO", "dimethyl sulfoxide", "CS(C)=O", [("amount", q(10, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "522", "tetracyclic product"),
], conditions=[("temperature", q(100, "°C")), ("atmosphere", "Ar")],
    outcomes=[("yield", qr(30, 40, "%", "30–40%"), "522")])
mechanism("p0023_s108_general", "Scheme 108 general Ti pathway", [22, 23],
          ["523", "524", "525"], notes=["R1=H or TMS; R2=alkyl or SiR3; Y=H or CH2OBn. Text reports about 80:20 Z/E for alkyl R2 and Z only for SiR3."])
add("p0023_s108_523a", "Scheme 108 optically active 523A", [22, 23], [
    P("reactant", "523A (<=83% ee)", "optically active 1,2-alkadien-7-yne"),
    P("reagent", "(eta2-propene)Ti(O-i-Pr)2"), P("reagent", "H+", "acid"),
    P("product", "525A", "optically active cyclized diene"),
], outcomes=[("yield", q(80, "%"), "525A"),
             ("enantiomeric_excess", qr(80, 83, "%", "80–83% ee"), "525A")])
step108 = add("p0023_s108_523b", "Scheme 108 optically active 523B", [22, 23], [
    P("reactant", "523B (<=86% ee)", "optically active 1,2-alkadien-7-yne"),
    P("reagent", "(eta2-propene)Ti(O-i-Pr)2"), P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("reagent", "H+", "acid"), P("product", "528", "optically active bicyclic enone"),
], outcomes=[("yield", q(68, "%"), "528"),
             ("enantiomeric_excess", q(86, "%", raw_text="86% ee"), "528")],
    notes=["Titanium intermediates 526 and 527 are depicted."])
set_steps(step108, [
    (["523B (<=86% ee)", "(eta2-propene)Ti(O-i-Pr)2"], [("temperature", None), ("time", None)]),
    (["CO"], [("operation", "carbonylation to 526/527")]),
    (["H+"], [("operation", "protonolysis")]),
])
add("p0023_s109_529", "Scheme 109 substrate 529 scope", [23], [
    P("reactant", "529 (R1/R2/R3 scope)", "1,2-alkadien-6-yne"),
    P("reagent", "(eta2-propene)Ti(O-i-Pr)2"), P("reactant", "R4CHO (R4=alkyl)", "aldehyde"),
    P("reagent", "H+", "acid"), P("product", "531", "alcoholic cyclization product"),
], conditions=[("temperature", q(-50, "°C")), ("operation", "1) aldehyde addition; 2) protonolysis")], outcomes=[
    ("yield", qr(40, 98, "%", "40–98%"), "531"), ("diastereomer_ratio", "74:26 to 98:2", "531"),
], notes=["Scope: R1=H or alkyl; R2=alkyl or TMS; R3=H; or R2=R3=H / R2=R3=Me."])
for suffix, carbonyl, yld, ee in [
    ("aldehyde", "R1=H; R2=C8H17; X=O", 84, 80),
    ("ketone", "R1=R2=Me; X=O", 88, 80),
    ("imine", "R1=Ph; R2=H; X=NPr", 71, 81),
]:
    product = f"533 ({carbonyl})"
    add(f"p0023_s109_532_{suffix}", f"Scheme 109 optically active 532 {carbonyl}", [23], [
        P("reactant", "532 (<=83% ee)", "optically active 1,2-alkadien-6-yne"),
        P("reagent", "(eta2-propene)Ti(O-i-Pr)2"), P("reactant", carbonyl, "carbonyl or imine partner"),
        P("product", product, "optically active alcohol/amine product"),
    ], outcomes=[("yield", q(yld, "%"), product),
                 ("enantiomeric_excess", q(ee, "%", raw_text=f"{ee}% ee"), product)])

# Page 24: Schemes 110--114 and prose-only introductions to Schemes 115--116.
for suffix, r_group, ratio, yld in [("c6h13", "R=C6H13", "95:5", 68), ("tms", "R=TMS", "96:4", 58)]:
    add(f"p0024_s110_534_{suffix}", f"Scheme 110 substrate 534 {r_group}", [24], [
        P("reactant", f"534 ({r_group})", "hydroxymethyl-substituted allene-alkyne"),
        P("reagent", "(eta2-propene)Ti(O-i-Pr)2"), P("reagent", "H+", "acid"),
        P("product", f"Z-535 ({r_group})", "alcoholic cyclization product"),
        P("product", f"E-535 ({r_group})", "alcoholic cyclization product"),
    ], outcomes=[("yield", q(yld, "%"), [f"Z-535 ({r_group})", f"E-535 ({r_group})"]),
                 ("Z_E_ratio", ratio, [f"Z-535 ({r_group})", f"E-535 ({r_group})"])])
add("p0024_s110_536", "Scheme 110 substrate 536 scope", [24], [
    P("reactant", "536 (R1/R2/X scope)", "5,6-alkadien-1-yne"),
    P("reagent", "(eta2-propene)Ti(O-i-Pr)2"), P("product", "537", "cross-conjugated triene"),
], outcomes=[("yield", qr(47, 79, "%", "47–79%"), "537")],
    notes=["Scope: R1=OTBS or H; R2=alkyl or TMS; X=OBn, OTBS, OAc, OCO2Et, or OMe."])
add("p0024_s111", "Scheme 111 scope", [24], [
    P("reactant", "538 (R/X/n scope)", "2-methyl-2,3-allen-8- or 9-yne"),
    P("catalyst", "RhCl(PPh3)3", "Wilkinson catalyst", None,
      [("catalyst_loading", qr(2, 10, "mol%", "2–10 mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "539", "cyclic ene-type product"),
], conditions=[("temperature", q(90, "°C"))], outcomes=[("yield", qr(41, 81, "%", "41–81%"), "539")],
    notes=["R=4-ClC6H4, 4-MeOC6H4, Ph, or Me; X=O, NTs, or C(CO2Et)2; n=1 or 2."])
for suffix, subs, yld in [("hh", "R1=R2=H", 75), ("me_h", "R1=Me; R2=H", 84), ("me_me", "R1=R2=Me", 71)]:
    product = f"541 ({subs})"
    add(f"p0024_s112_540_{suffix}", f"Scheme 112 substrate 540 {subs}", [24], [
        P("reactant", f"540 ({subs})", "allene-alkyne"), P("catalyst", "PtCl2", "platinum(II) chloride", None,
          [("catalyst_loading", q(5, "mol%"))]), P("solvent", "PhMe", "toluene", "Cc1ccccc1"),
        P("product", product, "3-allenylcyclohexene"),
    ], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(yld, "%"), product)])
for suffix, subs, yld in [
    ("ch2ome", "R=CH2OMe", 80), ("ketal", "R,R=cyclic acetonide group drawn", 70), ("co2me", "R=CO2Me", 60),
]:
    product = f"543 ({subs})"
    add(f"p0024_s112_542_{suffix}", f"Scheme 112 substrate 542 {subs}", [24], [
        P("reactant", f"542 ({subs})", "tetrasubstituted allene-alkyne"),
        P("catalyst", "PtCl2", "platinum(II) chloride", None, [("catalyst_loading", q(5, "mol%"))]),
        P("solvent", "PhMe", "toluene", "Cc1ccccc1"), P("product", product, "5/6-fused bicyclic product"),
    ], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(yld, "%"), product)],
        unresolved=["The cyclic R,R drawing is retained as a visual label."] if suffix == "ketal" else None)
add("p0024_s112_544", "Scheme 112 substrate 544", [24], [
    P("reactant", "544", "trisubstituted allene-alkyne"),
    P("catalyst", "PtCl2", "platinum(II) chloride", None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "PhMe", "toluene", "Cc1ccccc1"), P("product", "545", "2-vinyl-3-methylenecyclohexene"),
], conditions=[("temperature", q(40, "°C"))], outcomes=[("yield", q(54, "%"), "545")])
mechanism("p0024_s113_mechanism", "Scheme 113 proposed Pt pathways", [23, 24],
          ["546", "547", "548 / 549", "550 / 551 / 552", "553"],
          notes=["R3=CH2R4 gives 548; R3=H gives 549, then R1=H gives 550 while R1=Me gives 553 via 551 or 552."])
add("p0024_s114", "Scheme 114", [24], [
    P("reactant", "554", "alkylthio-substituted 1,2,6-triene"), P("reagent", "Fe(CO)4(NMe3)"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "555", "pi-allyl iron complex"),
    P("product", "556", "binuclear pi-allyl iron complex"),
], conditions=[("operation", "hν irradiation (100 W)")], outcomes=[
    ("yield", q(40, "%"), "555"), ("yield", q(15, "%"), "556"),
])
add("p0024_s115_text_only", "Scheme 115 prose-only Rh cyclization scope", [24], [
    P("reactant", "557 or 560", "1,2,7-triene"), P("catalyst", "[RhCl(COD)]2"),
    P("unspecified_agent", "P(O-o-PhC6H4)3 or P(O-o-tol)3", "phosphite ligand"),
    P("product", "559 or 561", "2-vinylic alkylidenecyclopentane"),
    P("product", "563", "six-membered-ring product"),
], outcomes=[("selectivity", "P(O-o-PhC6H4)3 gives a much higher E/Z ratio than P(O-o-tol)3", ["559 or 561", "563"])],
    unresolved=["Scheme 115 is on page 25, outside this batch; conditions, yields, and row mappings were not visually inspected."])
add("p0024_s116_text_only", "Scheme 116 prose-only disubstituted-alkene branch", [24], [
    P("reactant", "566", "disubstituted alkene-allene"), P("product", "567", "1,2-bis(vinylic)cyclopentane"),
], notes=["The prose attributes regioselectivity to the syn requirement of beta-H elimination."],
    unresolved=["Scheme 116 is on page 25, outside this batch; catalyst, conditions, yield, and substituent scope were not visually inspected."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

regions = {
    19: [
        ("左栏 Scheme 88–89", "引用工作：补全422、423、425及427四行逐箭头实验；Scheme 89仅为两条提议Pd路径。"),
        ("右栏上部 Scheme 90", "引用工作及机理：433二聚范围与434–436提议路径；脚注式当量均进入participants。"),
        ("右栏中部 Scheme 91–92", "引用工作：CO2/醛三组分内酯化、443逐步硅烷/酸/CH2N2处理及正文电羧化概述。"),
        ("右栏下部跨页正文", "Scheme 93说明始于本页、原图位于第20页；相应记录合并两页证据。"),
    ],
    20: [
        ("左栏 Scheme 93–95", "引用工作：446两行、448的双产物与450回流转化、451/454两条件及光学活性455。"),
        ("右栏 Scheme 96–97", "引用工作与机理：457的Co路径；464四行和466的467/468产物比及各自ee。"),
        ("页底跨页正文", "Scheme 98文字说明在本页、逐行图在第21页；记录合并两页证据。"),
    ],
    21: [
        ("左栏 Scheme 98", "引用工作/逐行范围：469、471、473、475三行及478两行分别记录条件、收率和区域异构体比。"),
        ("左栏下部 Scheme 99", "引用工作：480关键Pauson–Khand步骤、无注释481→482和482的酸/Formaldehyde步骤分开记录。"),
        ("右栏 Scheme 100–101", "引用工作：484三行、486范围及488到492多步序列；E/Z-489的二硫醇处理标签存在歧义并保留。"),
        ("右栏底部跨页正文", "Scheme 102的Rh条件说明跨至第22页原图，逐行记录使用两页证据。"),
    ],
    22: [
        ("左栏 Scheme 102", "引用工作：486四行Rh条件、494的Mo/Rh两支路及497单例。"),
        ("右栏 Scheme 103–105", "引用工作：499范围、501三行、503/505范围、507和509单例；510仅作提议中间体。"),
        ("页底跨页正文", "Scheme 106–108文字说明由本页引入，图与条件位于第23页；跨页合并证据。"),
    ],
    23: [
        ("左栏 Scheme 106–107", "引用工作：512范围、515/517支路与520两套不同Mo/DMSO当量和温度，未按相同产物合并。"),
        ("右栏 Scheme 108–109", "引用工作/机理：523一般Ti路径、523A/523B手性转移、529醛加成范围及532三行碳yl/亚胺结果。"),
        ("右栏底部跨页正文", "Scheme 113机理说明始于本页，原图在第24页；合并两页证据。"),
    ],
    24: [
        ("左栏 Scheme 110–112", "引用工作：534两行Z/E、536和538范围、540三行、542三行及544单例逐项记录。"),
        ("右栏 Scheme 113", "提议机理：546经547按R3/R1分支形成548、550或553，不作为独立实验。"),
        ("右栏 Scheme 114", "引用工作：554光化学生成555和556，两个产物收率分别关联。"),
        ("右栏下部正文 Scheme 115–116引入", "仅编码本页明确文字为text-only部分记录；图在第25页且未声称已查看。"),
    ],
}
unresolved = {
    19: ["Scheme 88的423形成未给收率，423→424未给条件；Scheme 90/91为汇总范围。", "Scheme 92未给Ni(COD)2用量和CO2压力；电羧化仅有定性低选择性描述。"],
    20: ["Scheme 93的450→449未给转化收率；Scheme 96未给产率。", "Scheme 94/97的总收率测定基础未说明。"],
    21: ["Scheme 99中481→482、482→483缺完整实验信息。", "Scheme 101的E/Z-489经1,3-丙二硫醇/BF3·OEt2后仍标E-489，化学操作需查原始论文；后续若干步无产率。"],
    22: ["Scheme 103的第二铑催化剂紧凑式及503/505对应关系需原文核对。", "Scheme 499范围和494两支路为汇总收率，缺逐底物映射。"],
    23: ["Scheme 106溶剂与温度选项未逐底物映射；515/517未给收率。", "Scheme 108的一般523范围无数值产率；所有光学纯度仍为综述二手值。"],
    24: ["Scheme 112的环状R,R基团未无歧义转写结构。", "Scheme 115–116图在第25页且未查看，本批次只保留第24页正文明确的信息。"],
}
coverage_pages = []
for page in range(19, 25):
    image_id = f"{DOC}:page{page}:image"
    record_ids = [r["record_id"] for r in records if image_id in r["evidence_ids"]]
    coverage_pages.append({
        "page": page,
        "state": "attempted",
        "regions": [
            {"region": region, "finding": finding,
             "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]}
            for region, finding in regions[page]
        ],
        "record_ids": record_ids,
        "unresolved": unresolved[page],
    })
coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": coverage_pages}
coverage_path = BASE / "coverage" / "pages_0019_0024.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    for page in range(19, 25):
        if task.get("evidence_id") == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records), "raw": str(OUT), "coverage": str(coverage_path),
    "coverage_pages": [p["page"] for p in coverage_pages],
}, ensure_ascii=False))
