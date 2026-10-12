#!/usr/bin/env python3
"""Raw extraction specification for PDF pages 1--6; emits merge-ready records."""
import json
import re
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")
records = []


def ev(pages):
    out = []
    for page in pages:
        out += [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    return out


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def slug(value):
    value = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return value[:40] or "entity"


def participant(role, label, name=None, smiles=None, amounts=None, evidence=None):
    return {
        "entity_id": slug(label),
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [
            {"name": field_name, "fact": fact(value, evidence)}
            for field_name, value in (amounts or [])
        ],
    }


def add(rid, source_id, pages, parts, conditions=None, outcomes=None, notes=None,
        unresolved=None, kind="literature_example"):
    evidence = ev(pages)
    ps = [participant(*item, evidence=evidence) for item in parts]
    ids = {p["label"]["value"]: p["entity_id"] for p in ps}
    cond = list(conditions or [])
    if kind == "literature_example":
        if not any(n == "temperature" for n, _ in cond):
            cond.append(("temperature", None))
        if not any(n == "time" for n, _ in cond):
            cond.append(("time", None))
    out_fields = []
    supplied_yield = False
    for name, value, target in (outcomes or []):
        field = {"name": name, "fact": fact(value, evidence)}
        if target:
            field["target_entity_ids"] = [ids[target]]
        out_fields.append(field)
        supplied_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(x["name"] == "yield" for x in out_fields):
        products = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if products:
            missing["target_entity_ids"] = products
        out_fields.append(missing)
    if supplied_yield:
        out_fields.append({"name": "yield_measurement_basis", "fact": fact(None, evidence)})
    step_ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    steps = []
    if cond:
        steps = [{
            "step_id": "step1",
            "participant_ids": step_ids,
            "conditions": [{"name": n, "fact": fact(v, evidence)} for n, v in cond],
        }]
    records.append({
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": ps,
        "steps": steps,
        "outcomes": out_fields,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "This is a secondary review citation; the primary article and SI were not supplied.",
                "Complex or generic drawn structures require expert structure transcription; unverified SMILES remain null.",
            ],
        },
    })


def add_mechanism(rid, source_id, pages, sequence, conditions=None, notes=None):
    parts = []
    for i, label in enumerate(sequence):
        role = "reactant" if i == 0 else ("product" if i == len(sequence) - 1 else "unspecified_agent")
        parts.append((role, label, None, None, None))
    add(rid, source_id, pages, parts, conditions=conditions, notes=notes,
        unresolved=["The arrows depict a proposed pathway, not independently reported experimental operations."],
        kind="mechanism")


# Page 1 and the Scheme 2 continuation on page 2.
add("p0001_s01", "Scheme 1", [1], [
    ("reactant", "propadiene", "propadiene", "C=C=C", None),
    ("reactant", "alpha,beta-unsaturated cyclohexenone (R-variable)", None, None, None),
    ("product", "1", "methylene-cyclobutane-containing bicyclic product", None, None),
], conditions=[("operation", "irradiation (hν)")], notes=["Kakiuchi et al. prior-literature [2+2] cycloaddition; R is generic."])
add("p0001_s02_dabco", "Scheme 2 DABCO branch", [1, 2], [
    ("reactant", "electron-deficient allene (EWG = CO2Et or COMe)", None, None, None),
    ("reactant", "ArCH=NTs (2)", "N-tosylated imine", None, None),
    ("catalyst", "DABCO", "1,4-diazabicyclo[2.2.2]octane", "C1CN2CCN1CC2", [("catalyst_loading", {"number": 10, "unit": "mol%"})]),
    ("reagent", "4A molecular sieves", "4 Å molecular sieves", None, None),
    ("solvent", "benzene", "benzene", "c1ccccc1", None),
    ("product", "3", "azetidine derivative", None, None),
], notes=["Overall transformation shown above the proposed catalytic sequence."])
add("p0001_s02_dmap", "Scheme 2 DMAP branch", [1, 2], [
    ("reactant", "ethyl 2,3-butadienoate", None, "C=C=CC(=O)OCC", None),
    ("reactant", "ArCH=NTs", "N-tosylated imine", None, None),
    ("catalyst", "DMAP", "4-dimethylaminopyridine", "CN(C)c1ccncc1", None),
    ("product", "13", "dihydropyridine derivative", None, None),
], notes=["Overall DMAP-catalyzed branch; the review does not state loading, solvent, temperature, time, or yield in these pages."])
add_mechanism("p0002_s02_dabco_mechanism", "Scheme 2 DABCO mechanism", [1, 2],
              ["allene + DABCO", "4/5", "6", "7", "3"],
              notes=["Proposed nucleophilic addition, imine addition, cyclic conjugate addition, and DABCO elimination."])
add_mechanism("p0002_s02_dmap_mechanism", "Scheme 2 DMAP mechanism", [1, 2],
              ["ethyl allenoate + DMAP", "4a", "6a", "7a/8", "9", "10", "11", "12", "13"],
              notes=["Proposed double 1,2-addition/H+ transfer, cyclic conjugate addition, and eliminations."])

# Page 2: Schemes 3 and 4.
add("p0002_s03_alkene_scope", "Scheme 3 alkene row", [2], [
    ("reactant", "14", "4-vinylidene-2-oxazolidinone", None, None),
    ("reactant", "alkene (R1/R2 variable)", None, None, None),
    ("product", "15", "cyclobutane derivative", None, None),
], outcomes=[("yield", {"minimum": 55, "maximum": 98, "unit": "%", "raw_text": "55–98%"}, "15")],
    notes=["Aggregate substrate-scope range; individual alkene-to-yield mapping is not printed on this review page."])
for suffix, substituent, value in [("co2me", "R = CO2Me", 51), ("ph", "R = Ph", 61)]:
    add(f"p0002_s03_alkyne_{suffix}", f"Scheme 3 alkyne row {substituent}", [2], [
        ("reactant", "14", "4-vinylidene-2-oxazolidinone", None, None),
        ("reactant", f"alkyne ({substituent})", None, None, None),
        ("product", f"16 ({substituent})", "cyclobutene derivative", None, None),
    ], outcomes=[("yield", {"number": value, "unit": "%"}, f"16 ({substituent})")])

scheme4 = {
    "17A": [("R1=CH2TMS; R2=H", 80), ("R1=H; R2=Ph", 30), ("R1=OTIPS; R2=Ph", 73)],
    "17B": [("R1=Ph", 70), ("R1=CH2TMS", 90), ("R1=OTIPS", 70)],
    "17C": [("R1=Ph", 65), ("R1=OTIPS", 86), ("R1=OMe", 70)],
}
for family, rows in scheme4.items():
    for idx, (subs, value) in enumerate(rows, 1):
        add(f"p0002_s04_{family.lower()}_{idx}", f"Scheme 4 {family} row {idx}", [2], [
            ("reactant", "14", "4-vinylidene-2-oxazolidinone", None, None),
            ("reactant", f"{family} ({subs})", "1,4-diene", None, None),
            ("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", None),
            ("product", f"18{family[-1]} ({subs})", "[2+2] cycloaddition product", None, None),
        ], conditions=[("temperature", "heat")], outcomes=[("yield", {"number": value, "unit": "%"}, f"18{family[-1]} ({subs})")])

# Scheme 5 begins in page-2 prose and is drawn on page 3.
add("p0002_p0003_s05", "Scheme 5 overall", [2, 3], [
    ("reactant", "14", "4-vinylidene-1,3-oxazolidin-2-one", None, None),
    ("reactant", "19", "enol ether", None, None),
    ("product", "22", "bicyclic tetrahydropyridine derivative", None, None),
], notes=["The review offers two alternative proposed pathways; no conditions or yield are printed here."])
add_mechanism("p0003_s05_mechanism", "Scheme 5 proposed pathways", [2, 3],
              ["14 + 19", "20", "Z-21/E-21 or 23", "22"],
              notes=["Alternative 1,3-Ts shift/zwitterion and Diels–Alder routes are depicted."])

# Page 3: Schemes 6--11.
for idx, (partner, product) in enumerate([("25", "26"), ("27", "28")], 1):
    add(f"p0003_s06_row{idx}", f"Scheme 6 row {idx}", [3], [
        ("reactant", "24", "propadienyl sulfone", None, None),
        ("reactant", partner, "alkene", None, None),
        ("product", product, "[2+2] cycloaddition product", None, None),
    ], notes=["The two rows show different allene C=C bond participation."])
add("p0003_s07", "Scheme 7", [3], [
    ("reactant", "p-methylphenyl-1,2-propadienyl sulfone", None, None, None),
    ("reactant", "29", "enol ether", None, None),
    ("solvent", "CH2Cl2", "dichloromethane", "ClCCl", None),
    ("product", "30", "[2+2] cycloadduct", None, None),
], conditions=[("pressure", "15 kbar")], outcomes=[("yield", {"minimum": 44, "maximum": 74, "unit": "%", "raw_text": "44–74%"}, "30")],
    notes=["Scope uses room temperature or 50 °C; substrate-to-temperature mapping is unresolved on the review page."])
for substrate, product in [("31", "32"), ("33", "34")]:
    add(f"p0003_s08_{substrate}", f"Scheme 8 {substrate}", [3], [
        ("reactant", substrate, "allene-tethered alpha,beta-unsaturated cyclic enone", None, None),
        ("product", product, "tricyclic [2+2] product", None, None),
    ], conditions=[("operation", "irradiation (hν)")])
add("p0003_s09_35", "Scheme 9 substrate 35", [3], [
    ("reactant", "35", "optically active allenyl silane-enone", None, None),
    ("product", "36", "photocycloadduct", None, None),
], conditions=[("operation", "UV lamp irradiation")], outcomes=[
    ("yield", {"minimum": 67, "maximum": 86, "unit": "%", "raw_text": "67–86%"}, "36"),
    ("enantiomeric_excess", {"minimum": 76, "maximum": 92, "unit": "%", "raw_text": "76–92% ee"}, "36"),
])
for suffix, x, y, ee in [("o", "O", 90, ">99%"), ("s", "S", 80, "89%")]:
    add(f"p0003_s09_37_{suffix}", f"Scheme 9 substrate 37 X={x}", [3], [
        ("reactant", f"37 (X={x})", "optically active allenyl silane-enone", None, None),
        ("product", f"38 (X={x})", "photocycloadduct", None, None),
    ], conditions=[("operation", "photoinduced cycloaddition")], outcomes=[
        ("yield", {"number": y, "unit": "%"}, f"38 (X={x})"),
        ("enantiomeric_excess", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ee} if x == "O" else {"number": 89, "unit": "%", "raw_text": ee}, f"38 (X={x})"),
    ], notes=["The starting material is shown as an E/Z mixture of approximately 2–1.5:1; exact assignment by row is not resolved."])
add("p0003_s10_39", "Scheme 10 substrate 39", [3], [
    ("reactant", "39", "1,2-allenyl sulfone-alkene", None, None),
    ("solvent", "benzene", "benzene", "c1ccccc1", None),
    ("product", "40", "[2+2] cycloadduct", None, None),
], conditions=[("temperature", {"number": 80, "unit": "°C"})], outcomes=[("yield", {"minimum": 80, "maximum": 98, "unit": "%", "raw_text": "80–98%"}, "40")])
add("p0003_s10_41", "Scheme 10 substrate 41", [3], [
    ("reactant", "41", "1,2-allenyl sulfone-alkene", None, None),
    ("reagent", "Bu3N", "tributylamine", "CCCN(CCC)CCC", None),
    ("product", "42", "cycloadduct", None, None),
], conditions=[("temperature", "heat")])
add("p0003_s10_43", "Scheme 10 substrate 43", [3], [
    ("reactant", "43", "1,2,7,9-tetraene", None, None),
    ("product", "44", "[2+2] product", None, None),
    ("product", "45", "[4+2] product", None, None),
], conditions=[("temperature", "heat")], outcomes=[
    ("product_ratio_44_to_45", "1:2", None),
], notes=["The scheme reports a product ratio, not individual isolated yields."])
for rgroup, value in [("R=CO2CH3", 80), ("R=SO2Ph", 81)]:
    add(f"p0003_s11_{slug(rgroup)}", f"Scheme 11 {rgroup}", [3], [
        ("reactant", f"46 ({rgroup})", "1,2,8-trienyl sulfone", None, None),
        ("product", f"48 ({rgroup})", "3-methylenecyclooctene product", None, None),
    ], conditions=[("temperature", "heat")], outcomes=[("yield", {"number": value, "unit": "%"}, f"48 ({rgroup})")])
add_mechanism("p0003_s11_mechanism", "Scheme 11 diradical pathway", [3], ["46", "47", "48"],
              conditions=[("temperature", "heat")], notes=["Proposed diradical formation followed by transannular hydrogen abstraction."])

# Page 4: Schemes 12--17.
add("p0004_s12_oxidation", "Scheme 12 oxidation branch", [4], [
    ("reactant", "49A", "alkene-allenyl sulfoxide", None, None),
    ("reagent", "oxone", "Oxone", None, None),
    ("reagent", "Et3N", "triethylamine", "CCN(CC)CC", None),
    ("solvent", "benzene", "benzene", "c1ccccc1", None),
    ("product", "51", "oxidized [2+2] cycloaddition product", None, None),
], conditions=[("temperature", {"number": 60, "unit": "°C"}), ("operation", "oxidation followed by heating/reflux")],
    outcomes=[("yield", {"number": 82, "unit": "%"}, "51")],
    unresolved=["The prose and scheme annotations for n and labels 49A/49B/51 are internally difficult to reconcile; preserve the printed labels pending primary-source review."])
add("p0004_s12_no_oxidation", "Scheme 12 unoxidized branch", [4], [
    ("reactant", "49A", "alkene-allenyl sulfoxide", None, None),
    ("solvent", "benzene", "benzene", "c1ccccc1", None),
    ("product", "52", "sulfoxide [2+2] cycloaddition product", None, None),
], conditions=[("temperature", {"number": 60, "unit": "°C"}), ("operation", "heating without oxidation")], outcomes=[("yield", {"number": 86, "unit": "%"}, "52")])
for substrate, rows in [("53", [("R=H", 40), ("R=Me", 56), ("R=Ph", 58)]), ("54", [("R=Me", 60), ("R=Ph", 34)])]:
    for idx, (subs, value) in enumerate(rows, 1):
        product = f"Scheme 13 product from {substrate} ({subs})"
        add(f"p0004_s13_{substrate}_{idx}", f"Scheme 13 {substrate} row {idx}", [4], [
            ("reactant", f"{substrate} ({subs})", "beta-lactam-tethered alkene-alpha-allenol", None, None),
            ("solvent", "toluene", "toluene", "Cc1ccccc1", None),
            ("product", product, "polycyclic lactam", None, None),
        ], conditions=[("temperature", {"number": 220, "unit": "°C"}), ("operation", "sealed tube")], outcomes=[
            ("yield", {"number": value, "unit": "%"}, product),
            ("diastereomer_ratio", "100:0", product),
        ])
add("p0004_s14", "Scheme 14", [4], [
    ("reactant", "55", "electron-deficient allene", None, None),
    ("catalyst", "Ni(PPh3)4", "tetrakis(triphenylphosphine)nickel(0)", None, [("catalyst_loading", {"number": 10, "unit": "mol%"})]),
    ("solvent", "toluene", "toluene", "Cc1ccccc1", None),
    ("product", "56", "1,2-bis(alkylidene)cyclobutane", None, None),
], outcomes=[("yield", {"minimum": 33, "maximum": 81, "unit": "%", "raw_text": "33–81%"}, "56")],
    notes=["Aggregate EWG scope: n-C6F13, CO2Et, CON(Me)Ph, COR, and SO2Ph."])
add("p0004_s15_57", "Scheme 15 compound 57", [4], [
    ("reactant", "57", "1,2,4,5-hexatetraene", None, None),
    ("product", "58", "3,4-bis(methylene)cyclobutene", None, None),
], conditions=[("temperature", "heat")])
add("p0004_s15_59", "Scheme 15 compound 59", [4], [
    ("reactant", "59", "2,3,5,6-octatetraene", None, None),
    ("product", "60", "3,4-bis(alkylidene)cyclobutene", None, None),
], conditions=[("operation", "distillation")])
add("p0004_s15_61", "Scheme 15 compound 61", [4], [
    ("reactant", "61", "substituted vinyl allene", None, None),
    ("product", "62", "alkylidenecyclobutene", None, None),
], conditions=[("temperature", {"number": 360, "unit": "°C"})], outcomes=[("equilibrium_ratio_61_to_62", "19:81", None)])
add("p0004_s16_cyclization", "Scheme 16 cyclization", [4], [
    ("reactant", "63", "trimethylsilyl-substituted vinyl allene", None, None),
    ("solvent", "PhCH3", "toluene", "Cc1ccccc1", None),
    ("product", "64", "silylated alkylidenecyclobutene", None, None),
], conditions=[("temperature", {"number": 145, "unit": "°C"}), ("time", {"number": 3, "unit": "h"})], outcomes=[("yield", {"minimum": 85, "maximum": 99, "unit": "%", "raw_text": "85–99%"}, "64")],
    notes=["Scope shown for R1 = H or Me and R2 = TMS, n-C6H13, or Ph."])
add("p0004_s16_desilylation", "Scheme 16 desilylation", [4], [
    ("reactant", "64 (R1=Me, R2=Ph)", "silylated alkylidenecyclobutene", None, None),
    ("reagent", "Bu4NF", "tetrabutylammonium fluoride", None, None),
    ("solvent", "THF/H2O", "tetrahydrofuran/water", None, None),
    ("product", "62", "desilylated alkylidenecyclobutene", None, None),
], conditions=[("temperature", {"number": 70, "unit": "°C"})], outcomes=[("yield", {"number": 99, "unit": "%"}, "62")])
add("p0004_s17_65", "Scheme 17 compound 65", [4], [
    ("reactant", "65", "1,3-bis(vinylic) allene", None, None),
    ("solvent", "benzene-d6", "benzene-d6", None, None),
    ("product", "66", "alkylidenecyclobutene", None, None),
], conditions=[("temperature", {"minimum": 90, "maximum": 110, "unit": "°C", "raw_text": "90–110 °C"})], notes=["R = CH2OTBDMS, CH2OH, or CHO; the CHO case is slower."])
add("p0004_s17_67", "Scheme 17 compound 67", [4], [
    ("reactant", "67", "1,3-bis(vinylic) allene", None, None),
    ("product", "68", "alkylidenecyclobutene", None, None),
], conditions=[("temperature", {"number": 110, "unit": "°C"})])

# Page 5: Schemes 18--21.
add("p0005_s18", "Scheme 18", [4, 5], [
    ("reactant", "69", "enyne-allenyl phosphine oxide", None, None),
    ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
    ("product", "70 (X=H)", "aryl phosphine oxide", None, None),
    ("product", "70 (X=cyclohexadienyl)", "aryl phosphine oxide", None, None),
    ("product", "71", "homocoupling product", None, None),
], conditions=[("temperature", {"number": 37, "unit": "°C"}), ("time", {"number": 5, "unit": "h"})], outcomes=[
    ("yield", {"number": 32, "unit": "%"}, "70 (X=H)"),
    ("yield", {"number": 17, "unit": "%"}, "70 (X=cyclohexadienyl)"),
    ("yield", {"number": 4, "unit": "%"}, "71"),
], notes=["R is shown as CH2CH2OAc."])
add_mechanism("p0005_s18_mechanism", "Scheme 18 diradical", [4, 5], ["69", "72", "70/71"],
              conditions=[("temperature", {"number": 37, "unit": "°C"}), ("time", {"number": 5, "unit": "h"})])
for suffix, reagent, rname, smiles, products in [
    ("chd", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", "74A + 74B"),
    ("cd3oh", "CD3OH", "methanol-d4", "[2H]OC([2H])([2H])[2H]", "75"),
    ("ccl4", "CCl4", "carbon tetrachloride", "C(Cl)(Cl)(Cl)Cl", "76 + 77"),
]:
    add(f"p0005_s19_73_{suffix}", f"Scheme 19 substrate 73 with {reagent}", [5], [
        ("reactant", "73 (R=H or TMS)", "6-alkyn-1,2,4-triene", None, None),
        ("reagent", reagent, rname, smiles, None),
        ("product", products, "benzene derivative(s)", None, None),
    ])
add("p0005_s19_78", "Scheme 19 substrate 78", [5], [
    ("reactant", "78", "1,2,4-trien-6-yne", None, None),
    ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
    ("product", "80", "Myers–Saito product", None, None),
], conditions=[("temperature", {"number": 80, "unit": "°C"})], outcomes=[("yield", {"number": 58, "unit": "%"}, "80")], notes=["Diradical 79 is depicted as a proposed intermediate."])
add("p0005_s19_81", "Scheme 19 substrate 81", [5], [
    ("reactant", "81", "1,2,4-trien-6-yne", None, None),
    ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
    ("product", "82", "polycyclic Myers–Saito product", None, None),
], conditions=[("temperature", {"number": 75, "unit": "°C"}), ("time", {"number": 1.5, "unit": "h"})])
add("p0005_s20", "Scheme 20", [5], [
    ("reactant", "83", "bis(allene)-alkyne", None, None),
    ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
    ("product", "86", "octacyclic product", None, None),
], conditions=[("temperature", {"number": 75, "unit": "°C"}), ("time", {"number": 1, "unit": "h"})])
add_mechanism("p0005_s20_mechanism", "Scheme 20 diradical cascade", [5], ["83", "84", "85", "86"],
              conditions=[("temperature", {"number": 75, "unit": "°C"}), ("time", {"number": 1, "unit": "h"})])
for suffix, r2, product in [("h", "R2=H", "89"), ("me", "R2=Me", "90")]:
    add(f"p0005_s21_87_{suffix}", f"Scheme 21 allene-enyne 87 {r2}", [5], [
        ("reactant", f"87 ({r2})", "allene-enyne", None, None),
        ("product", product, "Myers–Saito aromatization product", None, None),
    ])
add_mechanism("p0005_s21_87_mechanism", "Scheme 21 intermediate 88", [5], ["87", "88", "89 or 90"],
              notes=["Product branch is controlled by R2 (H versus Me)."])
add("p0005_s21_91_meoh", "Scheme 21 aza-Myers–Saito methanol branch", [5], [
    ("reactant", "91", "aza-allene-enyne", None, None),
    ("solvent", "MeOH", "methanol", "CO", None),
    ("product", "93", "pyridine derivative", None, None),
], conditions=[("temperature", {"number": 0, "unit": "°C"}), ("time", {"number": 14, "unit": "h"})])
add("p0005_s21_91_cdcl3", "Scheme 21 aza-Myers–Saito CDCl3 branch", [5], [
    ("reactant", "91", "aza-allene-enyne", None, None),
    ("solvent", "CDCl3", "chloroform-d", "[2H]C(Cl)(Cl)Cl", None),
    ("product", "92", "pyridine derivative", None, None),
], conditions=[("temperature", {"number": 10, "unit": "°C"}), ("time", {"number": 12, "unit": "h"})])

# Page 6: Schemes 22--29.
for substrate, intermediate, product, temp, value in [("94", "95", "96", 150, 45), ("97", "98", "99", 75, 80)]:
    add(f"p0006_s22_{substrate}", f"Scheme 22 substrate {substrate}", [5, 6], [
        ("reactant", substrate, "allene-enyne", None, None),
        ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
        ("solvent", "PhCl", "chlorobenzene", "Clc1ccccc1", None),
        ("product", product, "cyclized product", None, None),
    ], conditions=[("temperature", {"number": temp, "unit": "°C"})], outcomes=[("yield", {"number": value, "unit": "%"}, product)])
    add_mechanism(f"p0006_s22_{substrate}_mechanism", f"Scheme 22 intermediate {intermediate}", [5, 6], [substrate, intermediate, product],
                  conditions=[("temperature", {"number": temp, "unit": "°C"})])
add("p0006_s23", "Scheme 23", [6], [
    ("reactant", "100", "allene-enyne", None, None),
    ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
    ("solvent", "toluene", "toluene", "Cc1ccccc1", None),
    ("product", "101", "benzo[b]fluorene-core product", None, None),
], conditions=[("temperature", {"number": 105, "unit": "°C"})], outcomes=[("yield", {"number": 38, "unit": "%"}, "101")])
add("p0006_s24", "Scheme 24 overall", [5, 6], [
    ("reactant", "102", "3-(o-(1-alkynyl)phenyl)allenylphosphine oxide", None, None),
    ("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None),
    ("solvent", "toluene", "toluene", "Cc1ccccc1", None),
    ("product", "105", "Schmittel cyclization product", None, None),
], conditions=[("temperature", {"minimum": 60, "maximum": 70, "unit": "°C", "raw_text": "60–70 °C"})], outcomes=[("yield", {"number": 63, "unit": "%"}, "105")])
add_mechanism("p0006_s24_mechanism", "Scheme 24 benzofulvene diradical", [5, 6], ["102", "103", "104", "105"],
              conditions=[("temperature", {"minimum": 60, "maximum": 70, "unit": "°C", "raw_text": "60–70 °C"})], notes=["Final arrow is labeled [1,5-H]."])
for substrate, rgroup, temp, duration, product, value in [
    ("108", "R=H", 50, None, "111", 57),
    ("106", "R=t-Bu", 90, 40, "109", 34),
    ("107", "R=SiMe3", 90, 18, "110", 39),
]:
    parts = [("reactant", f"{substrate} ({rgroup})", "allene-enyne phosphine oxide", None, None)]
    if substrate != "108":
        parts.append(("reagent", "1,4-cyclohexadiene", "1,4-cyclohexadiene", "C1=CCC=CC1", None))
    parts.append(("product", product, "cyclization product", None, None))
    conditions = [("temperature", {"number": temp, "unit": "°C"})]
    if duration is not None:
        conditions.append(("time", {"number": duration, "unit": "h"}))
    add(f"p0006_s25_{substrate}", f"Scheme 25 substrate {substrate}", [6], parts,
        conditions=conditions, outcomes=[("yield", {"number": value, "unit": "%"}, product)])
for suffix, rgroup, value in [("tbu", "R=t-Bu", 76), ("h", "R=H", 50)]:
    add(f"p0006_s26_{suffix}", f"Scheme 26 {rgroup}", [6], [
        ("reactant", f"112 ({rgroup})", "diaryl allene-alkyne", None, None),
        ("product", f"114 ({rgroup})", "Schmittel product", None, None),
    ], outcomes=[("yield", {"number": value, "unit": "%"}, f"114 ({rgroup})")])
add_mechanism("p0006_s26_mechanism", "Scheme 26 diradical pathway", [6], ["112", "diradical intermediate", "113", "114"])
add("p0006_s27", "Scheme 27 overall", [6], [
    ("reactant", "115", "benzene-tethered allene-alkyne", None, None),
    ("product", "116", "tricyclic product", None, None),
], outcomes=[("yield", {"number": 62, "unit": "%"}, "116")])
add_mechanism("p0006_s27_mechanism", "Scheme 27 coupling pathway", [6], ["115", "1,4-diradical", "116"], notes=["The second arrow is labeled coupling."])
add("p0006_s28", "Scheme 28", [6], [
    ("reactant", "117", "1,1-difluoro-1,2-allen-7-yne", None, None),
    ("reagent", "Mo(CO)6", "molybdenum hexacarbonyl", None, None),
    ("solvent", "DMSO/toluene", "dimethyl sulfoxide/toluene", None, None),
    ("product", "118", "4,6-fused bicyclic product", None, None),
], conditions=[("temperature", {"number": 100, "unit": "°C"})], outcomes=[("yield", {"minimum": 75, "maximum": 92, "unit": "%", "raw_text": "75–92%"}, "118")], notes=["Scope: X = NTs or C(CO2Et)2; R = H, alkyl, or Ph."])
add("p0006_s29", "Scheme 29 overall", [6], [
    ("reactant", "119", "alkenyl chromium carbene complex", None, None),
    ("reactant", "1,1-disubstituted allene (R=Ph or Me)", None, None, None),
    ("solvent", "(CH2Cl)2", "1,2-dichloroethane", "ClCCCl", None),
    ("reagent", "SiO2", "silica", None, None),
    ("product", "121", "alpha,beta-unsaturated enone", None, None),
], conditions=[("temperature", {"number": 60, "unit": "°C"}), ("operation", "1) reaction in 1,2-dichloroethane; 2) silica treatment")], outcomes=[("yield", {"minimum": 70, "maximum": 80, "unit": "%", "raw_text": "70–80%"}, "121")])
add_mechanism("p0006_s29_mechanism", "Scheme 29 metallocarbene pathway", [6], ["119 + allene", "120", "121"],
              conditions=[("temperature", {"number": 60, "unit": "°C"})], notes=["Intermediate 120 undergoes retro-[2+2] cycloaddition."])

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
