#!/usr/bin/env python3
"""Build source-linked candidate records for review-PDF pages 31--36."""

import json
import re
from pathlib import Path


DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
OUT = Path(__file__).with_name("records_pages_0031_0036.json")
records = []


def ev(pages):
    evidence = []
    for page in pages:
        evidence.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return evidence


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def slug(value):
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()[:34] or "entity"


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
            {"name": amount_name, "fact": fact(value, evidence)}
            for amount_name, value in amounts
        ],
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

    outcome_fields = []
    supplied_yield = False
    for name, value, targets in outcomes or []:
        field = {"name": name, "fact": fact(value, evidence)}
        if targets:
            if isinstance(targets, str):
                targets = [targets]
            field["target_entity_ids"] = [label_ids[target] for target in targets]
        outcome_fields.append(field)
        supplied_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(
            field["name"] == "yield" for field in outcome_fields):
        products = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if products:
            missing["target_entity_ids"] = products
        outcome_fields.append(missing)
    if supplied_yield:
        outcome_fields.append({
            "name": "yield_measurement_basis",
            "fact": fact(None, evidence),
        })

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
        "outcomes": outcome_fields,
        "notes": [fact(note, evidence) for note in notes or []],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "This is a secondary-review example; the cited primary article and SI were not supplied.",
                "Complex or generic drawn structures remain label-only; all structures are unverified.",
            ],
        },
    }
    records.append(record)
    return record


def mechanism(rid, source_id, pages, sequence, conditions=None, notes=None,
              unresolved=None):
    parts = []
    for index, label in enumerate(sequence):
        role = "reactant" if index == 0 else (
            "product" if index == len(sequence) - 1 else "unspecified_agent"
        )
        parts.append(P(role, label))
    return add(
        rid, source_id, pages, parts, conditions=conditions, notes=notes,
        unresolved=list(unresolved or []) + [
            "The arrows depict a proposed pathway, not independently reported experimental operations."
        ], kind="mechanism",
    )


def set_steps(record, specifications):
    evidence = record["evidence_ids"]
    ids = {p["label"]["value"]: p["entity_id"] for p in record["participants"]}
    record["steps"] = []
    for index, (labels, conditions) in enumerate(specifications, 1):
        record["steps"].append({
            "step_id": f"step{index}",
            "participant_ids": [ids[label] for label in labels],
            "conditions": [
                {"name": name, "fact": fact(value, evidence)} for name, value in conditions
            ],
        })


# ---------------------------------------------------------------------------
# Page 31: Schemes 144--149. Scheme 144 starts on page 30; replace the two
# earlier text-only candidates with the visually checked page-31 scheme.
# ---------------------------------------------------------------------------
scheme144 = add("p0030_s144_text_only", "Scheme 144, substrate 696", [31], [
    P("reactant", "696", "allene-enol silyl ether"),
    P("catalyst", "W(CO)6", "tungsten hexacarbonyl", None,
      [("catalyst_loading", q(10, "mol%"))]),
    P("reagent", "H2O", "water", "O"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "697", "endo-cyclization product"),
], conditions=[("temperature", q(40, "°C")), ("operation", "hν irradiation")],
    notes=["The page-31 scheme labels the product 697; the page-30 extracted text had OCR/transcription label 693."],
    unresolved=["The record replaces an earlier page-30 text-only candidate; page-31 image evidence controls the product label."])
scheme144["evidence_ids"] = ev([30, 31])
scheme144["review"]["unresolved"].append(
    "Page 30 supplies narrative context, while the corrected product label is read from the page-31 scheme."
)
mech144 = mechanism("p0030_s144_text_mechanism", "Scheme 144 proposed W pathway", [31],
                    ["696 + W(CO)5(THF)", "698", "699", "697"],
                    conditions=[("temperature", q(40, "°C")), ("operation", "hν irradiation")],
                    notes=["The final arrow shows H2O, loss of TBSOH, and loss of W(CO)5THF."])
mech144["evidence_ids"] = ev([30, 31])

for substrate, product, yld in [("700", "701", 74), ("702 (R=Me, n-Bu, or Ph)", "703", qr(51, 86, "%", "51–86%")),
                                ("704", "705", 84)]:
    value = q(yld, "%") if isinstance(yld, int) else yld
    add(f"p0031_s144_{slug(substrate)}", f"Scheme 144 substrate {substrate}", [31], [
        P("reactant", substrate, "allene-enol silyl ether"),
        P("catalyst", "W(CO)6", "tungsten hexacarbonyl", None,
          [("catalyst_loading", q(10, "mol%"))]),
        P("reagent", "H2O", "water", "O"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("product", product, "endo-cyclization product"),
    ], conditions=[("temperature", q(40, "°C")), ("operation", "hν irradiation; conditions marked ibid")],
        outcomes=[("yield", value, product)])
for r_group, yld in [("R=H", 74), ("R=Me", 78)]:
    product = f"707 ({r_group})"
    add(f"p0031_s144_706_{slug(r_group)}", f"Scheme 144 substrate 706 {r_group}", [31], [
        P("reactant", f"706 ({r_group})", "allene-enol silyl ether"),
        P("catalyst", "W(CO)6", "tungsten hexacarbonyl", None,
          [("catalyst_loading", q(10, "mol%"))]),
        P("reagent", "H2O", "water", "O"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("product", product, "endo-cyclization product"),
    ], conditions=[("temperature", q(40, "°C")), ("operation", "hν irradiation")],
        outcomes=[("yield", q(yld, "%"), product)])

for suffix, r_group, yld, ratio in [
    ("hexyl", "R=n-C6H13", 64, "Z only"),
    ("benzyl", "R=Bn", 42, "Z only"),
    ("ethyl", "R=Et", 58, "Z/E = 89:11"),
]:
    product = f"708 ({r_group})"
    add(f"p0031_s145_708_{suffix}", f"Scheme 145 monosubstituted allene {r_group}", [31], [
        P("reactant", f"monosubstituted allene ({r_group})"),
        P("reagent", "ClCO2Et", "ethyl chloroformate", "CCOC(=O)Cl", [("amount", q(5, "equiv"))]),
        P("catalyst", "RhCl(CO)(PPh3)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", product, "3-chloro-3(Z)-alkenoate"),
    ], conditions=[("temperature", q(110, "°C"))], outcomes=[
        ("yield", q(yld, "%"), product), ("stereoselectivity", ratio, product),
    ])
add("p0031_s145_709_scope", "Scheme 145 1,1-disubstituted-allene scope", [31], [
    P("reactant", "1,1-disubstituted allene (R=Me, n-C4H9, or R,R=(CH2)5)"),
    P("reagent", "ClCO2Et", "ethyl chloroformate", "CCOC(=O)Cl", [("amount", q(5, "equiv"))]),
    P("catalyst", "RhCl(CO)(PPh3)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "709", "chloroalkenoate"),
], conditions=[("temperature", q(110, "°C")), ("operation", "conditions marked ibid")],
    outcomes=[("yield", qr(40, 75, "%", "40–75%"), "709")])

add("p0031_s146_710", "Scheme 146 aryl-halide scope", [31], [
    P("reactant", "ArX (X=Br or I; printed aryl scope)"),
    P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C", [("amount", q(2, "equiv"))]),
    P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("unspecified_agent", "PPh3", "triphenylphosphine", None, [("amount", q(5, "mol%"))]),
    P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(2, "equiv"))]),
    P("solvent", "DMA", "dimethylacetamide", "CC(=O)N(C)C"),
    P("product", "710", "1,3-diene"),
], outcomes=[("yield", qr(60, 94, "%", "60–94%"), "710")],
    notes=["The scheme also prints alkenyl-bromide examples as scope partners without separate arrows or row-resolved results."])
for product, allene in [("711", "substituted allene shown for product 711"),
                        ("712", "1-phenyl-1,2-butadiene or cyclohexylpropadiene")]:
    add(f"p0031_s146_{product}", f"Scheme 146 product {product}", [31], [
        P("reactant", "ArX (printed scope)"), P("reactant", allene),
        P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
        P("unspecified_agent", "PPh3", "triphenylphosphine", None, [("amount", q(5, "mol%"))]),
        P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(2, "equiv"))]),
        P("solvent", "DMA", "dimethylacetamide", "CC(=O)N(C)C"),
        P("product", product, "regioisomeric 1,3-diene product"),
    ], conditions=[("operation", "conditions marked ibid")],
        notes=["The review reports poor regioselectivity for these substituted-allene cases."])

add("p0031_s147", "Scheme 147 acylpalladation scope", [31], [
    P("reactant", "allene (R=H, aryl, or alkyl)"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("reactant", "R2R3NH (printed amine scope)"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "HOAc", "acetic acid", "CC(=O)O", [("amount", q(5, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "713", "alpha,beta-unsaturated E-enamide"),
], conditions=[("temperature", q(110, "°C"))], outcomes=[("yield", qr(51, 83, "%", "51–83%"), "713")])

add("p0031_s148", "Scheme 148 polymer-supported allene", [31], [
    P("reactant", "ArI"), P("reactant", "714", "polymer-supported allene"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("reactant", "piperidine", "piperidine", "C1CCNCC1"),
    P("reagent", "i-Pr2NEt", "N,N-diisopropylethylamine", "CCN(C(C)C)C(C)C"),
    P("catalyst", "Pd(OAc)2", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "P(2-furanyl)3", None, None, [("amount", q(20, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "715", "2-acyl allylic amine"),
], conditions=[("temperature", q(50, "°C")), ("atmosphere", "CO, 1 atm")])

add("p0031_s149_716", "Scheme 149 carbopalladation/allylic substitution", [31], [
    P("reactant", "ArI (printed aryl scope)"), P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("reactant", "terminal-alkene tosylamine (n=0, R=H; or n=1, R=CO2Me)"),
    P("catalyst", "Pd(OAc)2", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "PPh3", "triphenylphosphine", None, [("amount", q(20, "mol%"))]),
    P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(2, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "716", "diene"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", qr(70, 88, "%", "70–88%"), "716")])
add("p0031_s149_717", "Scheme 149 ring-closing metathesis", [31], [
    P("reactant", "716", "diene"), P("product", "717", "N-heterocycle"),
], conditions=[("operation", "ring-closing metathesis (RCM)")],
    outcomes=[("yield", qr(63, 94, "%", "63–94%"), "717")],
    unresolved=["The review scheme does not print the metathesis catalyst or the reaction temperature/time."])


# ---------------------------------------------------------------------------
# Page 32: Schemes 150--153.
# ---------------------------------------------------------------------------
add("p0032_s150_719", "Scheme 150 C-allylation", [32], [
    P("reactant", "ArI"), P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("reactant", "718", "4-hydroxycoumarin"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "Cs2CO3", "cesium carbonate", None, [("amount", q(2, "equiv"))]),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "719", "C-allylation product"),
], conditions=[("temperature", q(80, "°C"))])
add("p0032_s150_720", "Scheme 150 acid cyclization", [32], [
    P("reactant", "719", "C-allylation product"),
    P("catalyst", "TFA", "trifluoroacetic acid", "O=C(O)C(F)(F)F"),
    P("product", "720", "tricyclic product"),
])
overall721 = add("p0032_s150_721", "Scheme 150 4-hydroxy-2-quinolone process", [32], [
    P("reactant", "ArI"), P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("reactant", "721", "4-hydroxy-2-quinolone"),
    P("catalyst", "TFA", "trifluoroacetic acid", "O=C(O)C(F)(F)F"),
    P("solvent", "CHCl3", "chloroform", "ClC(Cl)Cl"),
    P("product", "723", "tricyclic quinolone product"),
], conditions=[("temperature", "r.t."), ("operation", "Pd-mediated allylation through 722, then TFA cyclization")],
    outcomes=[("yield", qr(35, 55, "%", "35–55%"), "723")],
    unresolved=["The preceding Pd-stage conditions are described only as a similar process and are not assigned by inference."])
set_steps(overall721, [
    (["ArI", "propadiene", "721"], [("operation", "formation of allylic-Pd-derived intermediate 722; exact conditions missing")]),
    (["TFA", "CHCl3"], [("temperature", "r.t.")]),
])

for suffix, r_group, yld, geometry in [
    ("h", "R=H", 90, None), ("co2me_trans", "R=CO2Me (trans precursor)", 92, "trans"),
    ("co2me_cis", "R=CO2Me (cis precursor)", 97, "cis"),
]:
    product = f"726 ({r_group})"
    add(f"p0032_s151_724_{suffix}", f"Scheme 151 substrate 724 {r_group}", [32], [
        P("reactant", f"724 ({r_group})", "iodoaryl-tethered amine"),
        P("reactant", "propadiene", "propadiene", "C=C=C"),
        P("catalyst", "Pd(OAc)2", None, None, [("catalyst_loading", q(10, "mol%"))]),
        P("unspecified_agent", "PPh3", "triphenylphosphine", None, [("amount", q(20, "mol%"))]),
        P("reagent", "Et4NCl", "tetraethylammonium chloride", None, [("amount", q(1, "equiv"))]),
        P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(2, "equiv"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "polycyclic indole product"),
    ], conditions=[("temperature", q(110, "°C")), ("time", q(16, "h")), ("pressure", "propadiene, 1 atm")],
        outcomes=[("yield", q(yld, "%"), product)] + ([] if geometry is None else [("precursor_geometry", geometry, product)]))
for suffix, ar_group, yld in [("phenyl", "Ar=phenyl", 73), ("pyridyl", "Ar=2-pyridyl", 55),
                              ("furyl", "Ar=2-furyl", 62), ("thienyl", "Ar=2-thienyl", 48)]:
    product = f"728 ({ar_group})"
    add(f"p0032_s151_727_{suffix}", f"Scheme 151 substrate 727 {ar_group}", [32], [
        P("reactant", f"727 ({ar_group})", "iodoaryl-tethered amine"),
        P("reactant", "propadiene", "propadiene", "C=C=C"),
        P("catalyst", "Pd(OAc)2", None, None, [("catalyst_loading", q(10, "mol%"))]),
        P("unspecified_agent", "PPh3", "triphenylphosphine", None, [("amount", q(20, "mol%"))]),
        P("reagent", "Et4NCl", "tetraethylammonium chloride", None, [("amount", q(1, "equiv"))]),
        P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(2, "equiv"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", product, "polycyclic indole product"),
    ], conditions=[("temperature", q(110, "°C")), ("time", q(16, "h")),
                   ("pressure", "propadiene, 1 atm"), ("operation", "conditions marked ibid")],
        outcomes=[("yield", q(yld, "%"), product)])

add("p0032_s152_729", "Scheme 152 o-iodophenol/o-iodoaniline scope", [32], [
    P("reactant", "2-iodophenol or 2-iodoaniline derivative (X=O or NTs)"),
    P("reactant", "propadiene (1 atm) or substituted allene"),
    P("reagent", "CO (1 atm)", "carbon monoxide", "[C-]#[O+]"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(2, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "729", "heterocyclic allylation product"),
], conditions=[("temperature", qr(45, 70, "°C", "45–70 °C")),
               ("time", qr(16, 72, "h", "16–72 h"))], outcomes=[("yield", qr(36, 99, "%", "36–99%"), "729")])
add("p0032_s152_731", "Scheme 152 sequential carbopalladation scope", [32], [
    P("reactant", "730 (X=O or NTs; Y printed scope)"),
    P("reactant", "allene (R=H, 1 bar; or R=Me, 4 equiv)"),
    P("catalyst", "Pd(OAc)2", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "P(2-furyl)3", None, None, [("amount", q(20, "mol%"))]),
    P("reagent", "K2CO3 or Cs2CO3", None, None, [("amount", q(3, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1", [("volume", q(5, "mL"))]),
    P("product", "731", "polyheterocyclic product"),
], conditions=[("temperature", q(110, "°C"))], outcomes=[("yield", qr(54, 72, "%", "54–72%"), "731")],
    unresolved=["The base and allene-pressure/equivalent options are not mapped to individual substrate rows in the review."])
add("p0032_s152_733", "Scheme 152 intramolecular carbopalladation/substitution", [32], [
    P("reactant", "732 (Y=N-R, O, or C(CO2Me)2)"),
    P("catalyst", "Pd(OAc)2", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "P(2-furyl)3", None, None, [("amount", q(20, "mol%"))]),
    P("reagent", "K2CO3, Ag2CO3, or Cs2CO3", None, None, [("amount", q(2, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "733", "tricyclic product"),
], conditions=[("temperature", q(50, "°C"))], outcomes=[("yield", qr(45, 63, "%", "45–63%"), "733")],
    unresolved=["The three base options are not mapped to individual substrate rows."])

add("p0032_s153_734", "Scheme 153 allylic silane/germane scope", [32], [
    P("reactant", "R1X (printed organic-halide scope)"), P("reactant", "allene"),
    P("reagent", "Bu3SnYMe3 (Y=Si or Ge)"),
    P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "734", "allylic silane or germane"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", qr(61, 92, "%", "61–92%"), "734"),
    ("Z_E_ratio", "80:20 to 98:2", "734"),
])
add("p0032_s153_734a", "Scheme 153 3-methyl-1,2-butadiene scope", [32], [
    P("reactant", "RX (aryl or alkenyl halide)"), P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"),
    P("reagent", "Bu3SnSiMe3"), P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "734A", "allylic silane"),
], conditions=[("temperature", q(80, "°C")), ("operation", "conditions marked ibid")],
    outcomes=[("yield", qr(61, 92, "%", "61–92%"), "734A")])
add("p0032_s153_735", "Scheme 153 allylic tin synthesis", [32], [
    P("reactant", "R1X"), P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"),
    P("reagent", "R3SnSnR3"), P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "735", "allylic tin"),
])
add("p0032_s153_736", "Scheme 153 Ni-catalyzed acylstannylation", [32], [
    P("reactant", "R1COSnR3^2"), P("reactant", "allene"),
    P("catalyst", "Ni(COD)2"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "736", "beta-organostannyl beta,gamma-unsaturated enone"),
])


# ---------------------------------------------------------------------------
# Page 33: Schemes 154--158. Schemes 159--161 start in prose and continue as
# drawings on page 34, so their records cite both pages below.
# ---------------------------------------------------------------------------
add("p0033_s154", "Scheme 154 acylboration scope", [33], [
    P("reactant", "R1COCl (printed acyl scope)"), P("reactant", "allene (R2/R3 scope)"),
    P("reagent", "diboronate (drawn)"),
    P("catalyst", "PdCl2(MeCN)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "E-737", "2-acylallylic boronate"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", qr(50, 92, "%", "50–92%"), "E-737"), ("E_Z_ratio", ">93:7", "E-737"),
])
add("p0033_s155", "Scheme 155 acyl/chloroformate silylation", [33], [
    P("reactant", "acyl chloride or chloroformate"), P("reactant", "substituted allene"),
    P("reagent", "Me3SiSiMe3", "hexamethyldisilane", "C[Si](C)(C)[Si](C)(C)C"),
    P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "738", "2-acyl allylic silane"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", qr(43, 88, "%", "43–88%"), "738"), ("E_Z_ratio", ">99:1", "738"),
])
add("p0033_s156_739", "Scheme 156 boronate coupling", [33], [
    P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"), P("reactant", "RX"),
    P("reagent", "ArB(OH)2", "arylboronic acid"),
    P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "CsF", "cesium fluoride", "[Cs+].[F-]"),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"), P("product", "739", "tetrasubstituted alkene"),
], conditions=[("temperature", q(70, "°C"))])
add("p0033_s156_740", "Scheme 156 alkenylzirconium coupling", [33], [
    P("reactant", "monosubstituted allene"), P("reactant", "R2I"), P("reagent", "1-alkenyl zirconium reagent"),
    P("catalyst", "NiCl2(PPh3)2", None, None, [("catalyst_loading", q(2.5, "mol%"))]),
    P("reagent", "Zn", "zinc", "[Zn]", [("amount", q(1.37, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "E-740", "1,4-diene"),
], conditions=[("temperature", q(50, "°C")), ("time", q(24, "h"))], outcomes=[
    ("yield", qr(37, 85, "%", "37–85%"), "E-740"), ("E_Z_ratio", ">94:6", "E-740"),
])

add("p0033_s157_742", "Scheme 157 aldehyde-tethered cyclization", [33], [
    P("reactant", "741 (R=H, Me, Ph, or 4-NO2C6H4; X=I or Br)"),
    P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("unspecified_agent", "drawn palladium complex", None, None, [("amount", q(2, "equiv"))]),
    P("reagent", "Cs2CO3", "cesium carbonate"), P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "742", "five-membered cyclic alcohol"),
], conditions=[("temperature", qr(80, 90, "°C", "80–90 °C"))],
    outcomes=[("yield", qr(70, 90, "%", "70–90%"), "742")],
    unresolved=["The stoichiometric drawn Pd complex is not assigned a catalyst role because the review prints 2 equivalents."])
add("p0033_s157_744", "Scheme 157 dehydration branch", [33], [
    P("reactant", "indandione-derived aryl halide (drawn)"), P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("unspecified_agent", "drawn palladium complex", None, None, [("amount", q(2, "equiv"))]),
    P("reagent", "Cs2CO3", "cesium carbonate"), P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "744", "dehydrated cyclic product"),
], conditions=[("temperature", q(90, "°C")), ("operation", "cyclization through 743 followed by dehydration; conditions marked ibid")],
    outcomes=[("yield", q(45, "%"), "744")])
mechanism("p0033_s157_744_pathway", "Scheme 157 pathway through 743", [33],
          ["indandione-derived substrate + propadiene", "743", "744"],
          conditions=[("temperature", q(90, "°C"))], notes=["The review states that 744 forms by further dehydration of 743."])
add("p0033_s157_746", "Scheme 157 six-membered-ring formation", [33], [
    P("reactant", "745"), P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("unspecified_agent", "drawn palladium complex", None, None, [("amount", q(2, "equiv"))]),
    P("reagent", "Cs2CO3", "cesium carbonate"), P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "746", "six-membered cyclic alcohol"),
], conditions=[("temperature", q(80, "°C")), ("time", q(18, "h")), ("operation", "conditions marked ibid")],
    outcomes=[("yield", q(34, "%"), "746")])

add("p0033_s158_747", "Scheme 158 allene/aldehyde/boronic-acid coupling", [33], [
    P("reactant", "4-methoxyphenylboronic acid"), P("reactant", "1,2-nonadiene"), P("reactant", "aldehyde (printed scope)"),
    P("catalyst", "drawn Pd dimer", None, None, [("catalyst_loading", q(2.5, "mol%"))]),
    P("unspecified_agent", "[HPPH(t-Bu)2]BF4", "phosphonium ligand precursor"),
    P("reagent", "CsF", "cesium fluoride", "[Cs+].[F-]"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "747", "homoallylic alcohol"),
], conditions=[("temperature", "r.t."), ("time", q(24, "h"))], outcomes=[
    ("yield", qr(46, 85, "%", "46–85%"), "747"), ("diastereomer_ratio", "1.9:1 to 32:1", "747"),
])
add("p0033_s158_748", "Scheme 158 allenoate lactone formation", [33], [
    P("reactant", "4-methoxyphenylboronic acid"), P("reactant", "ethyl 2,3-butadienoate", None, "C=C=CC(=O)OCC"),
    P("reactant", "aldehyde"), P("catalyst", "drawn Pd dimer", None, None, [("catalyst_loading", q(2.5, "mol%"))]),
    P("unspecified_agent", "PCy3", "tricyclohexylphosphine"), P("reagent", "CsF", "cesium fluoride", "[Cs+].[F-]"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "748", "six-membered lactone"),
], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(65, "%"), "748")])


# ---------------------------------------------------------------------------
# Pages 33--34: Schemes 159--161 cross the page boundary. Page 34 also has
# Schemes 162--164.
# ---------------------------------------------------------------------------
add("p0034_s159_749", "Scheme 159 substrate 749", [33, 34], [
    P("reactant", "749"), P("reactant", "ArI", None, None, [("amount", q(3, "equiv"))]),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(1.2, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "751", "benzocyclohexadione derivative"),
], conditions=[("temperature", "reflux")], outcomes=[("yield", qr(68, 92, "%", "68–92%"), "751")])
mechanism("p0034_s159_749_mechanism", "Scheme 159 ring expansion through 750", [33, 34],
          ["749 + ArI", "750", "751"], conditions=[("temperature", "reflux")])
for substrate, product, yld in [("752", "753", q(72, "%")), ("754", "755", qr(48, 81, "%", "48–81%")),
                                ("756 (R=Et or n-Pr) + ArI", "757", qr(57, 94, "%", "57–94%"))]:
    add(f"p0034_s159_{slug(substrate)}", f"Scheme 159 substrate {substrate}", [33, 34], [
        P("reactant", substrate), P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(5, "mol%"))]),
        P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(1.2, "equiv"))]),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", product, "ring-expanded product"),
    ], conditions=[("temperature", "reflux"), ("operation", "conditions marked ibid")], outcomes=[("yield", yld, product)])

add("p0034_s160", "Scheme 160 C-C cleavage", [33, 34], [
    P("reactant", "758", "3,4-allenol"), P("reactant", "ArI"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(3, "mol%"))]),
    P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(1.5, "equiv"))]),
    P("solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "760", "1,3-diene"), P("product", "RCHO", "aldehyde coproduct"),
])
mechanism("p0034_s160_mechanism", "Scheme 160 proposed C-C cleavage", [33, 34],
          ["758 + ArI", "759", "760 + RCHO"], notes=["The review proposes intermediate 759 before C-C bond cleavage."])

rec161 = add("p0034_s161", "Scheme 161 cobalt-mediated cyclization", [33, 34], [
    P("reactant", "761", "4,5-alkadienylamine"),
    P("reagent", "MeCOCo(CO)4", None, None, [("amount", q(1.1, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("reagent", "Et3N", "triethylamine", "CCN(CC)CC"), P("product", "763", "cyclized amine"),
], conditions=[("temperature", "r.t."), ("time", q(10, "min")), ("operation", "cobalt addition followed by Et3N")])
set_steps(rec161, [
    (["761", "MeCOCo(CO)4", "THF"], [("temperature", "r.t."), ("time", q(10, "min"))]),
    (["Et3N"], [("operation", "Et3N treatment")]),
])
mechanism("p0034_s161_mechanism", "Scheme 161 pi-allyl cobalt pathway", [33, 34],
          ["761 + MeCOCo(CO)4", "762", "763"], conditions=[("temperature", "r.t.")])

for suffix, r_group in [("phenethyl", "R=Ph(CH2)2"), ("cyclohexyl", "R=Cy"), ("methoxy", "R=OMe")]:
    product = f"765 ({r_group})"
    add(f"p0034_s162_{suffix}", f"Scheme 162 {r_group}", [34], [
        P("reactant", f"allene ({r_group})"), P("reagent", "764", "silylborane"),
        P("catalyst", "Pd(acac)2", None, None, [("catalyst_loading", q(2, "mol%"))]),
        P("unspecified_agent", "2,6-xylyl isocyanide", None, None, [("amount", q(8, "mol%"))]),
        P("solvent", "octane", "octane", "CCCCCCCC"), P("product", product, "allylic silane"),
    ], conditions=[("temperature", q(120, "°C")), ("time", q(2, "h"))],
        outcomes=[("regioselectivity", ">99:1", product)])
for suffix, r_group, byproduct in [("phenyl", "R=Ph", 6), ("tbu", "R=t-Bu", 14)]:
    minor = f"regioisomeric 765 byproduct ({r_group})"
    add(f"p0034_s162_{suffix}", f"Scheme 162 less-selective {r_group}", [34], [
        P("reactant", f"allene ({r_group})"), P("reagent", "764", "silylborane"),
        P("catalyst", "Pd(acac)2", None, None, [("catalyst_loading", q(2, "mol%"))]),
        P("unspecified_agent", "2,6-xylyl isocyanide", None, None, [("amount", q(8, "mol%"))]),
        P("solvent", "octane", "octane", "CCCCCCCC"),
        P("product", f"765 ({r_group})", "major allylic silane"), P("product", minor, "minor regioisomer"),
    ], conditions=[("temperature", q(120, "°C")), ("time", q(2, "h"))], outcomes=[
        ("yield", None, f"765 ({r_group})"), ("byproduct_percentage", q(byproduct, "%"), minor),
    ])
mechanism("p0034_s162_mechanism", "Scheme 162 proposed silylboration cycle", [34],
          ["Pd(0) + Si-B reagent + allene", "oxidative-addition complex", "boropalladation intermediate", "765 + Pd(0)"],
          notes=["The prose proposes Si-B oxidative addition, boropalladation, and reductive elimination."])

for suffix, r_group, yld in [("me", "R=Me", 88), ("ome", "R=OMe", 93), ("h", "R=H", 91)]:
    product = f"767 ({r_group})"
    add(f"p0034_s163_767_{suffix}", f"Scheme 163 product 767 {r_group}", [34], [
        P("reactant", f"allene ({r_group})"), P("reagent", "766", "silylborane"),
        P("catalyst", "Pd2(dba)2", None, None, [("catalyst_loading", q(2.5, "mol%"))]),
        P("unspecified_agent", "etpo", "P(OCH2)3CEt", None, [("amount", q(10, "mol%"))]),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", product, "allylic silane"),
    ], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", q(yld, "%"), product)])
add("p0034_s163_768", "Scheme 163 Pd/PPh3 branch", [34], [
    P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"), P("reagent", "766", "silylborane"),
    P("catalyst", "Pd2(dba)2", None, None, [("catalyst_loading", q(2.5, "mol%"))]),
    P("unspecified_agent", "PPh3", "triphenylphosphine", None, [("amount", q(10, "mol%"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "768", "allylic silane"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", q(90, "%", raw_text="90% by GC"), "768"), ("yield_measurement", "GC", "768"),
])
add("p0034_s163_769", "Scheme 163 Pt branch", [34], [
    P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"), P("reagent", "766", "silylborane"),
    P("catalyst", "Pt(CH2=CH2)(PPh3)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("product", "769", "regioisomeric allylic silane"),
], conditions=[("temperature", q(80, "°C")), ("time", q(3, "h"))], outcomes=[("yield", q(87, "%"), "769")])

add("p0034_s164", "Scheme 164 disilylation scope", [34], [
    P("reactant", "allene (R=H or Me)"), P("reagent", "(X3-mMemSi)2 (m=0–3; X=Me, OMe, or Cl)", "disilane"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(1, "mol%"))]),
    P("product", "770", "allylic silane with terminal C=C bond"),
])


# ---------------------------------------------------------------------------
# Page 35: Schemes 165--168. Scheme 169 begins in prose and is drawn on page 36.
# ---------------------------------------------------------------------------
add("p0035_s165_771", "Scheme 165 distannylation scope", [35], [
    P("reactant", "allene (R1=Me, Et, or Bu)"), P("reagent", "(R3Sn)2", "distannane"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(1, "mol%"))]),
    P("product", "771A", "2-stannyl-(E)-allylic tin"), P("product", "771B", "regioisomeric allylic tin"),
], conditions=[("temperature", qr(40, 60, "°C", "40–60 °C"))], outcomes=[
    ("yield", "high yield", ["771A", "771B"]), ("major_product", "771A usually major", ["771A", "771B"]),
])
add("p0035_s165_772", "Scheme 165 cyclic-allene distannylation", [35], [
    P("reactant", "cyclohexylidene allene (drawn)"), P("reagent", "(R3Sn)2", "distannane"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(1, "mol%"))]),
    P("product", "772", "distannylation product"),
], conditions=[("temperature", qr(40, 60, "°C", "40–60 °C")), ("operation", "conditions marked ibid")],
    outcomes=[("yield", q(100, "%"), "772")])
add("p0035_s165_773", "Scheme 165 phosphine-free silylstannylation", [35], [
    P("reactant", "monosubstituted allene (R1 variable)"), P("reagent", "Me3SiSnR3^2"),
    P("catalyst", "Pd(dba)2"), P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "773", "2-(trimethylsilyl)allylic tin"),
], conditions=[("temperature", "r.t."), ("time", q(8, "h"))])

add("p0035_s166_scope", "Scheme 166 diboration scope", [35], [
    P("reactant", "allene (R1=H or Me; R2=alkyl, aryl, or OPh)"), P("reagent", "774A or 774B", "diboron reagent"),
    P("catalyst", "3-iodo-2-methyl-2-cyclohexenone 775", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("catalyst", "Pd(dba)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "776", "allene diboration product"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", qr(52, 93, "%", "52–93%"), "776"), ("E_Z_ratio", "7:93 to 5:95", "776"),
])
add("p0035_s166_control", "Scheme 166 control/cross-addition study", [35], [
    P("reactant", "775", "3-iodo-2-methyl-2-cyclohexenone"),
    P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"), P("reagent", "774", "diboron reagent"),
    P("catalyst", "Pd(0)"), P("product", "777", "allylic boronate"), P("product", "778", "iodoboronate"),
])
mechanism("p0035_s166_mechanism", "Scheme 166 proposed catalytic cycle", [35],
          ["778 + Pd(0) + allene", "779", "780", "781", "776A + regenerated 778"],
          notes=["The review depicts B-I oxidative addition, allene insertion, transmetalation, and reductive elimination."])

add("p0035_s167", "Scheme 167 enantioselective diboration scope", [35], [
    P("reactant", "monosubstituted allene (printed R scope)"), P("reagent", "bis(pinacolato)diboron"),
    P("catalyst", "Pd2(dba)3", None, None, [("catalyst_loading", q(2.5, "mol%"))]),
    P("unspecified_agent", "chiral phosphonite ligand (drawn)", None, None, [("amount", q(6, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"), P("product", "782", "enantioenriched diboration product"),
], conditions=[("temperature", "r.t."), ("time", q(14, "h"))],
    unresolved=["The review page prints no row-resolved yield or enantiomeric excess for the listed R groups."])

for suffix, subs, y783, y784, geometry in [
    ("hhh", "R1=R2=R3=H", 92, 0, None),
    ("mmh", "R1=R2=Me; R3=H", None, 99, None),
    ("phhh", "R1=Ph; R2=R3=H", 91, 9, "E"),
    ("mhh", "R1=Me; R2=R3=H", 89, 0, "E"),
]:
    p783, p784 = f"783 ({subs})", f"784 ({subs})"
    outcomes = [
        ("yield", None if y783 is None else q(y783, "%"), p783),
        ("yield", q(y784, "%"), p784),
    ]
    if geometry:
        outcomes.append(("geometry", geometry, [p783, p784]))
    add(f"p0035_s168_table_{suffix}", f"Scheme 168 stannylcupration {subs}", [35], [
        P("reactant", f"allene ({subs})"), P("reagent", "(Bu3Sn)2CuLi"),
        P("reagent", "NH4Cl", "ammonium chloride", "[NH4+].[Cl-]"),
        P("product", p783, "vinylic stannane"), P("product", p784, "allylic stannane"),
    ], conditions=[("temperature", qr(-78, 0, "°C", "−78 °C to 0 °C"))], outcomes=outcomes,
        notes=["A printed dash for 783 is encoded as missing rather than zero."] if y783 is None else None)

for suffix, electrophile, e_group, yld in [
    ("meoh", "MeOH", "E=H", 100), ("accl", "CH3COCl", "E=Ac", 73), ("br2", "Br2", "E=Br", 42),
]:
    product = f"786 ({e_group})"
    add(f"p0035_s168_a_{suffix}", f"Scheme 168 conditions A {electrophile}", [35], [
        P("reactant", "propadiene", "propadiene", "C=C=C"), P("reagent", "(Bu3Sn)2CuLi"),
        P("reagent", electrophile), P("product", product, "allylic stannane"),
    ], conditions=[("temperature", q(-100, "°C")), ("operation", "stannylcupration, then quench at −100 °C (conditions A)")],
        outcomes=[("yield", q(yld, "%"), product)])
for suffix, electrophile, e_group, yld in [
    ("meoh", "MeOH", "E=H", 92), ("accl", "CH3COCl", "E=Ac", 84),
    ("epoxide", "ethylene oxide", "E=(CH2)2OH", 78), ("co2", "CO2", "E=CO2H", 49),
]:
    product = f"788 ({e_group})"
    add(f"p0035_s168_b_{suffix}", f"Scheme 168 conditions B {electrophile}", [35], [
        P("reactant", "propadiene", "propadiene", "C=C=C"), P("reagent", "(Bu3Sn)2CuLi"),
        P("reagent", electrophile), P("product", product, "vinylic stannane"),
    ], conditions=[("temperature", qr(-100, 0, "°C", "−100 °C for 1 h, warm to 0 °C over 1 h; quench at −100 °C")),
                   ("time", q(2, "h")), ("operation", "conditions B")], outcomes=[("yield", q(yld, "%"), product)])


# ---------------------------------------------------------------------------
# Pages 35--36: Schemes 169--170 span the boundary. Page 36 also contains
# Schemes 171--173 and text-only leads to Schemes 174--175 on page 37.
# ---------------------------------------------------------------------------
for suffix, electrophile, y789, y790 in [
    ("me", "MeI (E=Me)", 96, None), ("ac", "CH3COCl (E=Ac)", None, 80),
    ("br", "Br2 (E=Br)", None, 79),
]:
    p789, p790 = f"789 ({electrophile})", f"790 ({electrophile})"
    add(f"p0036_s169_prop_{suffix}", f"Scheme 169 propadiene {electrophile}", [35, 36], [
        P("reactant", "propadiene", "propadiene", "C=C=C"),
        P("reagent", "halide-free (Bu3Sn)2Cu reagent", None, None,
          [("preparation", "(Bu3Sn)2/BuLi and CuCN")]),
        P("reagent", electrophile), P("product", p789, "allylic stannane"), P("product", p790, "vinylic stannane"),
    ], conditions=[("temperature", qr(-78, 0, "°C", "−78 °C, then −78 °C to 0 °C"))], outcomes=[
        ("yield", None if y789 is None else q(y789, "%"), p789),
        ("yield", None if y790 is None else q(y790, "%"), p790),
    ], notes=["Blank table cells are encoded as missing, not zero."])
for suffix, electrophile, e_group, yld in [
    ("ac", "CH3COCl", "E=Ac", 99), ("me", "MeI", "E=Me", 81),
    ("epoxide", "ethylene oxide", "E=(CH2)2OH", 75),
]:
    product = f"791 ({e_group})"
    add(f"p0036_s169_methyl_{suffix}", f"Scheme 169 3-methylallene {electrophile}", [35, 36], [
        P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"),
        P("reagent", "halide-free (Bu3Sn)2Cu reagent"), P("reagent", electrophile),
        P("product", product, "allylic stannane"),
    ], conditions=[("temperature", qr(-78, 0, "°C", "−78 °C, then −78 °C to 0 °C")), ("operation", "conditions marked ibid")],
        outcomes=[("yield", q(yld, "%"), product)])
add("p0036_s169_mixed_cuprate", "Scheme 169 mixed silyl(stannyl)cuprate", [35, 36], [
    P("reactant", "allene (R=H or Me)"), P("reagent", "PhMe2Si(Bu3Sn)CuLi·LiCN"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reagent", "aqueous workup"),
    P("product", "allylic stannane from selective stannyl transfer", "allylic stannane"),
], outcomes=[("yield", q(99, "%"), "allylic stannane from selective stannyl transfer")])

rec793 = add("p0036_s170_793", "Scheme 170 epoxide trapping", [35, 36], [
    P("reactant", "allene (R=H or Ph)"), P("reagent", "(Bu3Sn)2CuLi"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reactant", "epoxide (drawn)"),
    P("product", "793", "4-(tributylstannyl)-4(E)-pentenol"),
], conditions=[("temperature", qr(-70, 0, "°C", "−70 °C then −70 °C to 0 °C")), ("time", q(1, "h"))],
    outcomes=[("yield", qr(78, 86, "%", "78–86%"), "793")])
set_steps(rec793, [
    (["allene (R=H or Ph)", "(Bu3Sn)2CuLi", "THF"], [("temperature", q(-70, "°C"))]),
    (["epoxide (drawn)"], [("temperature", qr(-70, 0, "°C", "−70 °C to 0 °C")), ("time", q(1, "h"))]),
])
add("p0036_s170_791", "Scheme 170 low-order cuprate, 3-methylallene", [36], [
    P("reactant", "3-methyl-1,2-butadiene", None, "C=C=C(C)C"), P("reagent", "(Bu3Sn)CuCNLi"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reagent", "NH4Cl/H2O"),
    P("product", "791 (R=Me, E=H)", "allylic stannane"),
], conditions=[("temperature", qr(-40, 0, "°C", "−40 °C then −40 °C to 0 °C"))],
    outcomes=[("yield", q(85, "%"), "791 (R=Me, E=H)")])
for suffix, electrophile, e_group, yld in [
    ("h", "NH4Cl/H2O", "E=H", 90), ("me", "MeI", "E=Me", 92), ("bz", "BnBr", "E=Bz", 59),
    ("come", "acetyl electrophile", "E=COMe", 67), ("coph", "benzoyl electrophile", "E=COPh", 52),
    ("cyclohexanone", "cyclohexanone", "E=cyclohexanol-derived", 71),
]:
    product = f"795 ({e_group})"
    add(f"p0036_s170_795_{suffix}", f"Scheme 170 propadiene {electrophile}", [36], [
        P("reactant", "propadiene", "propadiene", "C=C=C"), P("reagent", "(Bu3Sn)CuCNLi"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reagent", electrophile),
        P("product", product, "allylic stannane"),
    ], conditions=[("temperature", qr(-40, 0, "°C", "−40 °C then −40 °C to 0 °C"))],
        outcomes=[("yield", q(yld, "%"), product)])

for suffix, subs, yld, geometry in [
    ("hhh", "R1=R2=R3=H", 99, None), ("phhh", "R1=Ph; R2=R3=H", 91, "Z"),
    ("mhph", "R1=Me; R2=H; R3=Ph", 71, "Z"), ("mmph", "R1=R2=Me; R3=Ph", 96, None),
]:
    product = f"798 ({subs})"
    outs = [("yield", q(yld, "%"), product)]
    if geometry:
        outs.append(("geometry", geometry, product))
    add(f"p0036_s171_798_{suffix}", f"Scheme 171 vinylic silane {subs}", [36], [
        P("reactant", f"allene 796 ({subs})"), P("reagent", "(PhMe2Si)2CuLi 797"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reagent", "NH4Cl/H2O/MeOH"),
        P("product", product, "vinylic silane"),
    ], conditions=[("temperature", q(-78, "°C"))], outcomes=outs)
for suffix, subs, yld, ratio in [
    ("hme", "R1=H; R2=Me", 93, "E/Z = 3:1"), ("meh", "R1=Me; R2=H", 99, None),
    ("meme", "R1=R2=Me", 97, None),
]:
    product = f"799 ({subs})"
    outs = [("yield", q(yld, "%"), product)] + ([] if ratio is None else [("stereoselectivity", ratio, product)])
    add(f"p0036_s171_799_{suffix}", f"Scheme 171 allylic silane {subs}", [36], [
        P("reactant", f"1,1-disubstituted allene ({subs})"), P("reagent", "(PhMe2Si)2CuLi 797"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reagent", "NH4Cl/H2O/MeOH"),
        P("product", product, "allylic silane"),
    ], conditions=[("temperature", q(-78, "°C")), ("operation", "conditions marked ibid")], outcomes=outs)
add("p0036_s171_heptadiene_text", "Scheme 171 prose 1,2-heptadiene result", [36], [
    P("reactant", "1,2-heptadiene"), P("reagent", "(PhMe2Si)2CuLi"),
    P("product", "vinylic silane from 1,2-heptadiene"), P("product", "allylic silane from 1,2-heptadiene"),
], outcomes=[
    ("yield", q(78, "%"), "vinylic silane from 1,2-heptadiene"),
    ("yield", q(29, "%"), "allylic silane from 1,2-heptadiene"),
], notes=["The review reports 78% and 29% as printed; the values are not normalized or corrected."])

for precursor, product, suffix, rows in [
    ("800", "801", "allylic", [("MeI", "E=Me", 75), ("CH3COCl", "E=Ac", 73),
                                ("cyclohex-2-enone", "E=cyclohexenol-derived 1,2-addition", 83)]),
    ("802", "803", "vinylic", [("MeI", "E=Me", 92), ("CH3COCl", "E=Ac", 77),
                                ("cyclohex-2-enone", "E=cyclohexanone-derived 1,4-addition", 52)]),
]:
    for idx, (electrophile, e_group, yld) in enumerate(rows, 1):
        target = f"{product} ({e_group})"
        add(f"p0036_s172_{precursor}_{idx}", f"Scheme 172 {precursor} with {electrophile}", [36], [
            P("reactant", precursor, f"{suffix} cuprate"), P("reagent", electrophile),
            P("product", target, "electrophile-trapping product"),
        ], outcomes=[("yield", q(yld, "%"), target)])
add("p0036_s172_804", "Scheme 172 iodination", [36], [
    P("reactant", "800", "allylic cuprate"), P("reagent", "I2", "iodine", "II"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "804", "2-iodoallyl silane"),
], conditions=[("time", q(1, "h"))], outcomes=[("yield", q(90, "%"), "804")])
add("p0036_s172_805", "Scheme 172 chlorination", [36], [
    P("reactant", "800", "allylic cuprate"), P("reagent", "Cl2", "chlorine", "ClCl"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", "805", "vinylic silane"),
], conditions=[("time", q(1, "h"))], outcomes=[("yield", q(61, "%"), "805")])
add("p0036_s172_806", "Scheme 172 halide exchange", [36], [
    P("reactant", "805", "chlorinated vinylic silane"), P("reagent", "NaI", "sodium iodide", "[Na+].[I-]"),
    P("solvent", "acetone", "acetone", "CC(C)=O"), P("product", "806", "iodinated vinylic silane"),
], conditions=[("temperature", q(80, "°C")), ("time", q(4, "h"))], outcomes=[("yield", q(87, "%"), "806")])

add("p0036_s173_810", "Scheme 173 propadiene silylcupration", [36], [
    P("reactant", "propadiene", "propadiene", "C=C=C"), P("reagent", "(t-BuPh2Si)2CuLi 807"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("reagent", "NH4Cl/MeOH"),
    P("product", "810", "vinylic silane"),
], conditions=[("temperature", q(-78, "°C")), ("operation", "formation of 809, then quench")],
    outcomes=[("yield", q(97, "%"), "810")])
for substrate, product, yld, geometry in [
    ("811 (R1=R2=Me)", "812", 86, None), ("813 (R1=n-C4H9; R2=H)", "814", 95, "Z"),
]:
    outs = [("yield", q(yld, "%"), product)] + ([] if geometry is None else [("geometry", geometry, product)])
    add(f"p0036_s173_{slug(product)}", f"Scheme 173 substrate {substrate}", [36], [
        P("reactant", substrate), P("reagent", "(t-BuPh2Si)2CuLi 807 or t-BuPh2SiCuLiCN 808"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"), P("product", product, "allylic silane"),
    ], conditions=[("temperature", qr(-78, -40, "°C", "−78 or −40 °C")), ("operation", "conditions marked ibid")],
        outcomes=outs, unresolved=["The review does not map reagent 807 versus 808 to each displayed substrate row."])

add("p0036_s174_text_only", "Scheme 174 text-only boundary", [36], [
    P("reactant", "propadiene", "propadiene", "C=C=C"), P("reagent", "(PhMe2Si)CuLiCN"),
    P("unspecified_agent", "vinylic copper reagent 815"), P("reagent", "electrophile (not shown on page 36)"),
    P("product", "816/817", "allyl silane products"),
], conditions=[("temperature", q(-40, "°C"))],
    unresolved=["Scheme 174 is drawn on page 37, outside this batch; electrophile identities, individual products, and yields were not transcribed."])
add("p0036_s175_text_only", "Scheme 175 text-only stereospecificity statement", [36], [
    P("reactant", "stereochemically defined allene 818 or 820"),
    P("reagent", "silylcupration reagent (not shown on page 36)"),
    P("product", "stereospecific syn-addition product (Scheme 175)"),
], outcomes=[("stereochemical_result", "stereospecific syn-addition", "stereospecific syn-addition product (Scheme 175)")],
    unresolved=["Scheme 175 is drawn on page 37, outside this batch; structures, exact conditions, and yields were not transcribed."])


# Persist raw model records.
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


# Coverage ledger: exact requested pages, each tied only to evidence actually inspected.
regions = {
    31: [
        ("左栏上部 Scheme 144", "引用工作及提议机理：逐箭头核查696/700/702/704/706系列；图中产物697用于纠正先前文字OCR的693。"),
        ("左栏下部 Scheme 145", "引用工作：708三行按R拆分，709保留为无逐行映射的范围记录。"),
        ("右栏上中部 Scheme 146–148", "引用工作：芳基卤化物/联烯制二烯、酰基钯化及聚合物负载联烯四组分反应；缺失收率明确保留。"),
        ("右栏下部 Scheme 149", "引用工作：716形成与后续RCM成717为不同箭头、不同记录；RCM催化剂缺失。"),
    ],
    32: [
        ("左栏 Scheme 150–151", "引用工作：719→720分步，721支路保留未给出的上游Pd条件；724三行和727四行逐行记录。"),
        ("右栏上部 Scheme 152", "引用工作：729、731、733三套条件独立建档，未把可选碱/联烯条件强行逐底物分配。"),
        ("右栏下部 Scheme 153", "引用工作：734、734A、735及736四个箭头分别记录。"),
    ],
    33: [
        ("左栏 Scheme 154–156", "引用工作：酰基硼化、酰基硅化、739与740两类三组分偶联分别记录。"),
        ("右栏 Scheme 157–158", "引用工作及机理：742、744/743、746和747/748逐箭头记录；2当量绘制Pd络合物不自动标为催化剂。"),
        ("页底跨页正文", "引用工作引入Schemes 159–161；相应记录与第34页图合并证据，而非重复。"),
    ],
    34: [
        ("左栏 Scheme 159–161", "引用工作及提议机理：四个159底物分支、758裂解和761两步钴介导环化；与第33页正文合并。"),
        ("右栏 Scheme 162", "引用工作/机理：三条>99:1范围与Ph、t-Bu副产物百分比分开；催化循环单列机理。"),
        ("右栏 Scheme 163–164", "引用工作：767三行、Pd/PPh3与Pt两个区域异构分支及通式二硅化。"),
    ],
    35: [
        ("左栏 Scheme 165–167", "引用工作及机理：二锡化/硅锡化、776控制实验与催化循环、782不对称二硼化范围。"),
        ("右栏 Scheme 168表格", "引用工作：783/784四行、条件A三种淬灭和条件B四种淬灭逐行建档；横线保留missing，印刷0%保留为0%。"),
        ("页底 Scheme 169–170引入正文", "引用工作：与第36页图合并记录混合铜试剂选择性和环氧化物捕获，不重复建档。"),
    ],
    36: [
        ("左栏 Scheme 169–170", "引用工作：789/790三行、791三行、混合硅锡铜试剂、793、低阶铜试剂及795六种亲电试剂逐行记录。"),
        ("右栏上部 Scheme 171", "引用工作：798四行、799三行及正文1,2-heptadiene两个印刷收率均按原文保留。"),
        ("右栏中部 Scheme 172", "引用工作：800与802各三种亲电试剂、I2/Cl2及805→806独立记录。"),
        ("右栏下部 Scheme 173及页底正文", "引用工作：810/812/814；Schemes 174–175图在第37页，本批仅建立明确文字边界记录并保留缺失。"),
    ],
}
unresolved_by_page = {
    31: [
        "Scheme 144的页30文字提取曾写693，页31原图明确标697；以原图为准并保留冲突说明。",
        "Scheme 149后续RCM未给催化剂、温度和时间。",
    ],
    32: [
        "Scheme 150的721支路仅称similar process，未推断上游Pd条件。",
        "Schemes 152–153多为汇总范围，可选碱、压力和单底物收率未逐行映射。",
    ],
    33: [
        "Scheme 157的绘制Pd络合物印为2 equiv，角色保持unspecified_agent。",
        "Schemes 154–158为综述汇总，未提供原始实验步骤或SI。",
    ],
    34: [
        "Scheme 162对Ph和t-Bu只明确给出6%/14%区域异构副产物，未反推主产物百分比。",
        "Scheme 164未给温度、时间或收率。",
    ],
    35: [
        "Scheme 167未在本页列出逐底物收率或ee。",
        "Scheme 168表格空白/横线不解释为零；只有印刷0%才记录为0%。",
    ],
    36: [
        "Scheme 171正文印刷78%与29%合计超过100%，按原文保留，未归一化。",
        "Schemes 174–175的图位于第37页，超出本批范围；本页仅保留明确文字事实与缺失项。",
    ],
}
coverage_pages = []
for page in range(31, 37):
    image_id = f"{DOC}:page{page}:image"
    record_ids = [record["record_id"] for record in records if image_id in record["evidence_ids"]]
    coverage_pages.append({
        "page": page,
        "state": "attempted",
        "regions": [
            {
                "region": region,
                "finding": finding,
                "evidence_ids": [image_id, f"{DOC}:page{page}:text"],
            }
            for region, finding in regions[page]
        ],
        "record_ids": record_ids,
        "unresolved": unresolved_by_page[page],
    })
coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": coverage_pages}
coverage_path = BASE / "coverage" / "pages_0031_0036.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


# Mark only the requested tasks attempted and bind them to the inspected images.
tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    for page in range(31, 37):
        if task.get("evidence_id") == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "raw": str(OUT),
    "coverage": str(coverage_path),
    "pages": [31, 32, 33, 34, 35, 36],
}, ensure_ascii=False))
