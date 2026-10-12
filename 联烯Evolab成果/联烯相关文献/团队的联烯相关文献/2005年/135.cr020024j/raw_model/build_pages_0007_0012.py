#!/usr/bin/env python3
"""Source-linked extraction specification for review PDF pages 7--12."""
import json
import re
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
OUT = Path(__file__).with_name("records_pages_0007_0012.json")
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
    return (re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()[:36]
            or "entity")


def P(role, label, name=None, smiles=None, amounts=None):
    return role, label, name, smiles, amounts or []


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
            {"name": field_name, "fact": fact(value, evidence)}
            for field_name, value in amounts
        ],
    }


def add(rid, source_id, pages, parts, conditions=None, outcomes=None, notes=None,
        unresolved=None, kind="literature_example"):
    evidence = ev(pages)
    ps = [participant(i, item, evidence) for i, item in enumerate(parts, 1)]
    ids = {p["label"]["value"]: p["entity_id"] for p in ps}
    cond = list(conditions or [])
    if kind == "literature_example":
        if not any(name == "temperature" for name, _ in cond):
            cond.append(("temperature", None))
        if not any(name == "time" for name, _ in cond):
            cond.append(("time", None))
    out_fields = []
    supplied_yield = False
    for name, value, targets in (outcomes or []):
        field = {"name": name, "fact": fact(value, evidence)}
        if targets:
            if isinstance(targets, str):
                targets = [targets]
            field["target_entity_ids"] = [ids[target] for target in targets]
        out_fields.append(field)
        supplied_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(
            field["name"] == "yield" for field in out_fields):
        products = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if products:
            missing["target_entity_ids"] = products
        out_fields.append(missing)
    if supplied_yield:
        out_fields.append({
            "name": "yield_measurement_basis",
            "fact": fact(None, evidence),
        })
    step_ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    steps = []
    if cond:
        steps.append({
            "step_id": "step1",
            "participant_ids": step_ids,
            "conditions": [
                {"name": name, "fact": fact(value, evidence)}
                for name, value in cond
            ],
        })
    record = {
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
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "This is a secondary review citation; the primary article and SI were not supplied.",
                "Complex or generic drawn structures require expert transcription; unverified SMILES remain null.",
            ],
        },
    }
    records.append(record)
    return record


def mechanism(rid, source_id, pages, sequence, conditions=None, notes=None,
              unresolved=None):
    parts = []
    for i, label in enumerate(sequence):
        role = "reactant" if i == 0 else (
            "product" if i == len(sequence) - 1 else "unspecified_agent")
        parts.append(P(role, label))
    add(
        rid, source_id, pages, parts, conditions=conditions, notes=notes,
        unresolved=(unresolved or []) + [
            "The arrows depict a proposed pathway, not independently reported experimental operations."
        ],
        kind="mechanism",
    )


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit,
            "raw_text": raw_text}


# Page 7: Schemes 30--33.
add("p0007_s30", "Scheme 30 overall", [7], [
    P("reactant", "119", "alkenyl chromium carbene complex"),
    P("reactant", "1,1-disubstituted allene (R2/R3 scope)"),
    P("unspecified_agent", "Ni(COD)2", "bis(1,5-cyclooctadiene)nickel(0)"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "124", "4-alkylidenecyclopentenyl methyl ether"),
], conditions=[("temperature", q(25, "°C"))])
mechanism("p0007_s30_mechanism", "Scheme 30 proposed pathway", [7],
          ["119 + allene", "122", "123", "124"],
          conditions=[("temperature", q(25, "°C"))],
          notes=["The review proposes Cr–Ni exchange, allylic rearrangement, and reductive elimination."])

add("p0007_s31", "Scheme 31 overall", [7], [
    P("reactant", "119", "alkenyl chromium carbene complex"),
    P("reactant", "1,1-disubstituted allene (R2/R3 scope)"),
    P("catalyst", "[Rh(naphthalene)(COD)]SbF6",
      amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "126", "3-methylenecyclopentenyl methyl ether"),
], conditions=[("temperature", q(25, "°C"))])
mechanism("p0007_s31_mechanism", "Scheme 31 proposed pathway", [7],
          ["119 + allene", "organometal fragments", "125", "126"],
          conditions=[("temperature", q(25, "°C"))],
          notes=["The review depicts a possible [4+2] cycloaddition followed by reductive elimination."])

add("p0007_s32_ni", "Scheme 32 Ni-mediated branch", [7], [
    P("reactant", "alkenyl chromium carbene complex (R2=H; R1 scope)"),
    P("reactant", "3-methyl-1,2-butadiene (two molecules)"),
    P("unspecified_agent", "Ni(COD)2"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"),
    P("reagent", "SiO2", "silica"),
    P("product", "127", "3,4-bis(alkylidene)cycloheptanone"),
], conditions=[("temperature", qr(-10, 25, "°C", "−10 °C to rt")),
               ("operation", "Ni-mediated reaction followed by silica treatment")],
    outcomes=[("yield", qr(40, 56, "%", "40–56%"), "127")],
    notes=["The printed R1 scope is Ph, 4-MeOC6H4, n-Bu, and 2-furanyl."])
add("p0007_s32_rh", "Scheme 32 Rh-catalyzed branch", [7], [
    P("reactant", "alkenyl chromium carbene complex (R1 scope)"),
    P("reactant", "allene (R3/R4 scope; two molecules)"),
    P("catalyst", "[Rh(COD)Cl]2", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "128", "3,5-bis(alkylidene)cycloheptene"),
], conditions=[("temperature", "r.t.")],
    outcomes=[("yield", qr(50, 71, "%", "50–71%"), "128")])
add("p0007_s32_protonolysis", "Scheme 32 protonolysis", [7], [
    P("reactant", "128", "3,5-bis(alkylidene)cycloheptene"),
    P("reagent", "HCl", "hydrochloric acid", "Cl",
      [("concentration", q(2, "M"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "129", "2,4-bis(alkylidene)cycloheptanone"),
], conditions=[("temperature", "r.t.")],
    outcomes=[("yield", q(95, "%", qualifier="gt", raw_text=">95%"), "129")])

add("p0007_s33_inter_scope", "Scheme 33 intermolecular Ti-imido scope", [7], [
    P("reactant", "allene (R=H, Ph, or C6H13)"),
    P("reactant", "ArNH2", "arylamine"),
    P("catalyst", "Cp(ArNH)PyTi=NAr",
      amounts=[("catalyst_loading", qr(7, 10, "mol%", "7–10 mol%"))]),
    P("solvent", "C7H8", "toluene", "Cc1ccccc1"),
    P("product", "130", "enamine"),
], conditions=[("temperature", q(90, "°C"))],
    outcomes=[("yield", qr(85, 96, "%", "85–96%"), "130")])
add("p0007_s33_cyclononadiene", "Scheme 33 cyclic allene example", [7], [
    P("reactant", "131", "1,2-cyclononadiene"),
    P("reactant", "2,6-dimethylaniline"),
    P("catalyst", "Cp(ArNH)PyTi=NAr",
      amounts=[("catalyst_loading", qr(7, 10, "mol%", "7–10 mol%"))]),
    P("solvent", "C7H8", "toluene", "Cc1ccccc1"),
    P("product", "132", "cyclic imine"),
], conditions=[("temperature", q(90, "°C"))],
    outcomes=[("yield", q(70, "%"), "132")],
    notes=["The scheme marks these conditions as ibid relative to the preceding row."])
add("p0007_s33_cp2time2", "Scheme 33 Cp2TiMe2 branch", [7], [
    P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("reactant", "RNH2 (printed R scope)"),
    P("catalyst", "Cp2TiMe2", amounts=[("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "C6D6", "benzene-d6"),
    P("product", "133", "imine"),
], conditions=[("temperature", q(90, "°C"))],
    outcomes=[("yield", qr(25, 90, "%", "25–90%"), "133")],
    notes=["The review prints a broad alkyl/aryl R scope without row-resolved yields."])
add("p0007_s33_intramolecular", "Scheme 33 intramolecular hydroamination", [7], [
    P("reactant", "134", "allene-tethered arylamine"),
    P("catalyst", "Ti(NMe2)4-derived catalyst (drawn)"),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "135", "cyclic imine"),
], conditions=[("temperature", q(75, "°C"))],
    notes=["The aryl group scope and tether length are generic; no row-resolved yields are printed."])
mechanism("p0007_s33_mechanism", "Scheme 33 proposed Ti-imido cycle", [7],
          ["136 + propadiene", "137", "138", "enamine + 136"],
          notes=["Proposed [2+2] addition, protonolysis with ArNH2, and beta-H elimination."])

# Scheme 34 starts in page-7 prose and is drawn on page 8.
add("p0007_p0008_s34_complexation", "Scheme 34 metallocycle formation", [7, 8], [
    P("reactant", "139", "(EBTHI)(THF)Zr=NAr complex"),
    P("reactant", "allene (R scope)"),
    P("product", "140", "beta-methylenemetallocycle"),
])
kinetic_rows = [
    ("c3h5", "R1=R2=C3H5", 59, {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee (R)"}),
    ("ph_me", "R1=Ph; R2=Me", 61, {"number": 94, "unit": "%", "raw_text": "94% ee (R)"}),
    ("ph_et", "R1=Ph; R2=Et", 53, {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee (R)"}),
    ("ph_ph", "R1=R2=Ph", 50, {"number": 98, "unit": "%", "qualifier": "gt", "raw_text": ">98% ee (R)"}),
    ("cyclic", "R1,R2=(CH2)6", 54, {"number": 78, "unit": "%", "raw_text": "78% ee (R)"}),
]
for suffix, substituents, yld, ee in kinetic_rows:
    add(f"p0008_s34_resolution_{suffix}", f"Scheme 34 kinetic resolution {substituents}", [7, 8], [
        P("reactant", f"141 ({substituents})", "racemic allene"),
        P("reagent", "(S,S)-139", "enantiopure zirconium imido complex"),
        P("product", f"R-141 ({substituents})", "recovered enantioenriched allene"),
    ], conditions=[("temperature", "r.t.")], outcomes=[
        ("yield", q(yld, "%"), f"R-141 ({substituents})"),
        ("enantiomeric_excess", ee, f"R-141 ({substituents})"),
    ], unresolved=["For the first row, the small printed substituent formula is retained as C3H5 pending primary-source confirmation."] if suffix == "c3h5" else None)
for suffix, allene in [("nonadiene", "4,5-nonadiene (R=n-C3H7)"),
                       ("cyclononadiene", "1,2-cyclononadiene (R,R=(CH2)6)")]:
    add(f"p0008_s34_142_{suffix}", f"Scheme 34 formation of 142 from {allene}", [7, 8], [
        P("reactant", "(S,S)-139", "enantiopure zirconium imido complex"),
        P("reactant", allene),
        P("product", f"(S,S,R)-142 ({suffix})", "beta-methylenemetallocycle"),
    ], conditions=[("operation", "excess allene removed in vacuo after reaction")],
        unresolved=["The prose describes the allene amount qualitatively as slightly more than two equivalents; no exact amount is assigned."])
add("p0008_s34_displacement", "Scheme 34 propadiene displacement", [7, 8], [
    P("reactant", "(S,S,R)-142", "beta-methylenemetallocycle"),
    P("reagent", "propadiene", "propadiene", "C=C=C", [("amount", q(10, "equiv"))]),
    P("product", "(S,S)-143", "propadiene-derived zirconium complex"),
    P("product", "(S)-4,5-nonadiene", "enantioenriched allene"),
], conditions=[("temperature", q(23, "°C"))])

# Page 8: Schemes 35--37.
mechanism("p0008_s35_mechanism", "Scheme 35 proposed inversion pathways", [8],
          ["144", "145", "146 / 147↔148↔149"],
          notes=["The review presents beta-H elimination/hydrometalation and allylic rearrangement as alternatives."])
add("p0008_s36_r_h", "Scheme 36 R=H branch", [8], [
    P("reactant", "150 (R=H)", "alkene-allene"),
    P("product", "151", "intramolecular [4+2] cycloadduct"),
])
add("p0008_s36_r_substituted", "Scheme 36 R is not H branch", [8], [
    P("reactant", "150 (R is not H)", "alkene-allene"),
    P("product", "153", "rearranged intramolecular [2+2] product"),
], notes=["Cyclobutane 152 is depicted before a [3,3] rearrangement to 153."])
mechanism("p0008_s36_rearrangement", "Scheme 36 [2+2]/[3,3] branch", [8],
          ["150 (R is not H)", "152", "153"])
add("p0008_s37_154_r2_h", "Scheme 37 ester 154 R2=H", [8], [
    P("reactant", "154 (R2=H; R1/R3 scope)", "ester-tethered alkene-allene"),
    P("product", "155", "intramolecular [4+2] cycloadduct"),
], conditions=[("temperature", "heat")])
add("p0008_s37_154_r2_me", "Scheme 37 ester 154 R2=Me", [8], [
    P("reactant", "154 (R2=Me; R1/R3 scope)", "ester-tethered alkene-allene"),
    P("product", "156", "intramolecular [2+2] cycloadduct"),
], conditions=[("temperature", "heat")])
add("p0008_s37_157_r_h", "Scheme 37 sulfone 157 R=H", [8], [
    P("reactant", "157 (R=H)", "sulfone-tethered alkene-allene"),
    P("product", "158A", "intramolecular [4+2] cycloadduct"),
], conditions=[("temperature", "heat")])
add("p0008_s37_157_r_me", "Scheme 37 sulfone 157 R=Me", [8], [
    P("reactant", "157 (R=Me)", "sulfone-tethered alkene-allene"),
    P("product", "159", "intramolecular [2+2] cycloadduct"),
    P("product", "158B", "competing cycloadduct"),
], conditions=[("temperature", "heat")], outcomes=[
    ("yield", q(44, "%"), "159"),
    ("yield", q(24, "%"), "158B"),
])

# Page 9: Schemes 38--43.
add("p0009_s38_160", "Scheme 38 intermolecular step", [8, 9], [
    P("reactant", "160", "2,3-allenoate"),
    P("reactant", "cyclopentadiene", "cyclopentadiene", "C1C=CC=C1"),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "161", "endo [4+2] cycloadduct"),
], conditions=[("temperature", q(80, "°C")), ("time", q(3, "h"))],
    outcomes=[("yield", q(93, "%"), "161")])
add("p0009_s38_162", "Scheme 38 intramolecular step", [8, 9], [
    P("reactant", "162", "1,3-diene-allene"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "163", "bridged tetracyclic product"),
], conditions=[("temperature", q(160, "°C")), ("time", q(2, "h"))],
    outcomes=[("yield", q(74, "%"), "163")],
    unresolved=["The intervening conversion of 161 to 162 is summarized only as several steps and is not reconstructed."])
add("p0009_s39", "Scheme 39", [8, 9], [
    P("reactant", "164", "1-fluoropropadienyl phosphonate"),
    P("reactant", "cyclopentadiene", "cyclopentadiene", "C1C=CC=C1"),
    P("product", "165", "endo [4+2] cycloadduct"),
], conditions=[("temperature", "r.t."), ("time", q(48, "h"))],
    outcomes=[("yield", q(78, "%"), "165")])
add("p0009_s40", "Scheme 40", [9], [
    P("reactant", "166", "substituted furan"),
    P("reactant", "167", "allenyl alcohol"),
    P("product", "168", "eleutherobin-aglycone carbon-framework intermediate"),
])

for substrate, products, temperature, duration, yields in [
    ("169", ["171", "172", "173"], q(120, "°C"), q(14, "h"), [15, 28, 22]),
    ("169", ["171", "172", "173"], q(120, "°C"), q(4, "d"), [14, 58, 0]),
    ("174", ["175", "176", "177"], q(120, "°C"), q(14, "h"), [15, 28, 22]),
    ("174", ["175", "176", "177"], q(140, "°C"), q(4, "d"), [14, 58, 0]),
]:
    tag = f"{substrate}_{duration['number']}{duration['unit']}_{temperature['number']}c"
    parts = [
        P("reactant", substrate, "2-(silyloxy)-1,3-alkadiene"),
        P("reactant", "170", "ethyl 2-methyl-2,3-butadienoate"),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    ] + [P("product", product) for product in products]
    add(f"p0009_s41_{tag.lower()}", f"Scheme 41 {substrate}, {duration['number']} {duration['unit']}", [9], parts,
        conditions=[("temperature", temperature), ("time", duration), ("operation", "sealed tube")],
        outcomes=[("yield", q(value, "%"), product) for product, value in zip(products, yields)])
add("p0009_s41_178", "Scheme 41 formal-synthesis step", [9], [
    P("reactant", "178", "diene-allene precursor"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "179", "dysidiolide-synthesis intermediate"),
], conditions=[("temperature", "heat"), ("operation", "sealed tube")],
    outcomes=[("yield", q(30, "%"), "179")])

add("p0009_s42_180", "Scheme 42 substrate 180", [9], [
    P("reactant", "180 (X=heteroatom-containing tether)", "furan-tethered 1,2-allenyl sulfone"),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "181", "intramolecular [4+2] cycloadduct"),
], conditions=[("temperature", "heat")])
add("p0009_s42_182", "Scheme 42 substrate 182", [9], [
    P("reactant", "182 (R scope)", "furan-tethered 1,2-allenyl sulfone"),
    P("product", "184 (R1=H or Ac; R=H or Me)", "rearranged cycloadduct"),
], notes=["The scheme depicts intermediate 183 but prints no reagents, temperature, time, or yield."])
mechanism("p0009_s42_182_pathway", "Scheme 42 pathway from 182", [9],
          ["182", "183", "184"])

add("p0009_s43_185", "Scheme 43 substrate 185", [9], [
    P("reactant", "185 (X scope)", "diene-allene"),
    P("catalyst", "[Rh(COD)Cl]2"),
    P("unspecified_agent", "P(O-o-BiPh2)3", "phosphite ligand"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "186", "intramolecular [4+2] cycloadduct"),
], outcomes=[("yield", qr(94, 98, "%", "94–98%"), "186")])
add("p0009_s43_187", "Scheme 43 substrate 187", [9], [
    P("reactant", "187", "diene-allene"),
    P("catalyst", "Rh(CH2=CH2)2Cl"),
    P("unspecified_agent", "P[OCH(CF3)2]3", "phosphite ligand"),
    P("solvent", "PhCH3", "toluene", "Cc1ccccc1"),
    P("product", "188", "intramolecular [4+2] cycloadduct"),
], conditions=[("temperature", q(60, "°C"))],
    outcomes=[("yield", q(77, "%"), "188")])
s43_rows = [
    ("hh_a", "R1=R2=H", "P[OCH(CF3)(o-MeOC6H4)]3", "190", 87, "91:9"),
    ("hh_b", "R1=R2=H", "AgO2CCF3 + P[OCH(CF3)-2,6-(CH3)2C6H3]3", "190", 69, "5:95"),
    ("me_h", "R1=Me; R2=H", "P[OCH(CF3)(o-MeOC6H4)]3", "190", 87, "100:0"),
    ("h_me", "R1=H; R2=Me", "P[OCH(CF3)2]3", "191", 89, None),
]
for suffix, subs, ligand, product, yld, ratio in s43_rows:
    outcomes = [("yield", q(yld, "%"), product)]
    if ratio:
        outcomes.append(("trans_cis_ratio", ratio, product))
    add(f"p0009_s43_189_{suffix}", f"Scheme 43 substrate 189 {subs}", [9], [
        P("reactant", f"189 ({subs}; E=CO2Me)", "diene-allene"),
        P("catalyst", "Rh(CH2=CH2)2Cl"),
        P("unspecified_agent", ligand, "printed ligand/additive entry"),
        P("solvent", "PhCH3", "toluene", "Cc1ccccc1"),
        P("product", product, "intramolecular cycloaddition product"),
    ], conditions=[("temperature", qr(60, 80, "°C", "60–80 °C"))], outcomes=outcomes,
        unresolved=["The compact ligand/additive formula is preserved textually and requires primary-source confirmation."])

# Page 10: Schemes 44--48.
add("p0010_s44_reflux", "Scheme 44 reflux branch", [9, 10], [
    P("reactant", "192 (R1 scope)", "1-aryl-4-phenyl-1-azadiene"),
    P("reactant", "193 (R2 scope)", "2,3-allenoate"),
    P("solvent", "PhH", "benzene", "c1ccccc1"),
    P("product", "194", "six-membered cycloadduct"),
], conditions=[("temperature", "reflux")],
    outcomes=[("yield", qr(78, 97, "%", "78–97%"), "194")])
add("p0010_s44_room_temperature", "Scheme 44 room-temperature branch", [9, 10], [
    P("reactant", "192 (R1 scope)", "1-aryl-4-phenyl-1-azadiene"),
    P("reactant", "193 (R2 scope)", "2,3-allenoate"),
    P("solvent", "dry PhH", "dry benzene", "c1ccccc1"),
    P("product", "194", "six-membered cycloadduct"),
    P("product", "195", "azetidine [2+2] cycloadduct"),
], conditions=[("temperature", "r.t."),
               ("time", qr(45, 65, "d", "45–65 days"))],
    notes=["The review reports a mixture but gives no product ratio or branch yield."])
mechanism("p0010_s44_mechanism", "Scheme 44 proposed pathway", [9, 10],
          ["192 + 193", "196", "197", "198 / 199", "194 / 200"],
          notes=["Alternative intramolecular 1,2- and 1,4-addition branches are labeled a and b."])

add("p0010_s45", "Scheme 45 overall", [10], [
    P("reactant", "201", "2-phenyl-4-(dimethylamino)-1-thia-3-azabuta-1,3-diene"),
    P("reactant", "202 (R1/R2/R3 scope)", "2,3-allenoate"),
    P("product", "204 (R3=H)", "6-alkylidene-1,3-thiazine"),
], conditions=[("temperature", "heat")])
mechanism("p0010_s45_pathway", "Scheme 45 depicted sequence", [10],
          ["201 + 202", "203", "204"], conditions=[("temperature", "heat")])

s46_rows = [
    ("h_ch2", "R=H; X=CH2", 42), ("me_ch2", "R=Me; X=CH2", 40),
    ("h_nme", "R=H; X=NMe", 52), ("me_nme", "R=Me; X=NMe", 62),
    ("h_o", "R=H; X=O", 41), ("me_o", "R=Me; X=O", 40),
]
for suffix, subs, yld in s46_rows:
    add(f"p0010_s46_205_{suffix}", f"Scheme 46 allenamide 205 {subs}", [10], [
        P("reactant", f"205 ({subs})", "allenamide"),
        P("reactant", f"alpha,beta-unsaturated enal/enone ({subs})"),
        P("catalyst", "ZnCl2", "zinc chloride", "[Cl-].[Cl-].[Zn+2]",
          [("catalyst_loading", q(10, "mol%"))]),
        P("solvent", "MeCN", "acetonitrile", "CC#N"),
        P("product", f"206 ({subs})", "dihydropyran derivative"),
    ], conditions=[("temperature", qr(60, 80, "°C", "60–80 °C"))],
        outcomes=[("yield", q(yld, "%"), f"206 ({subs})")])
add("p0010_s46_207_scope", "Scheme 46 chiral allenamide 207 scope", [10], [
    P("reactant", "207", "optically active allenamide"),
    P("reactant", "208 (R=aryl, methyl, or H)", "vinyl ketone or propenal"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"),
    P("product", "209", "chiral dihydropyran derivative"),
], conditions=[("temperature", qr(80, 120, "°C", "80–120 °C")),
               ("additional_printed_condition", "r.t., dry PhH (assignment unresolved)")],
    outcomes=[
        ("yield", qr(19, 85, "%", "19–85%"), "209"),
        ("diastereomer_ratio", "63:37 to >=96:4", "209"),
    ], unresolved=["The figure also prints 'r.t., dry PhH'; its stage relative to MeCN at 80–120 °C is not unambiguous on this review page."])

s47_rows = [
    ("maleic", "maleic anhydride", "211", 75),
    ("tcne", "TCNE", "212", 35),
    ("ethyl_acrylate", "ethyl acrylate", "213", 76),
    ("dimethyl_fumarate", "dimethyl fumarate", "214", 20),
]
for suffix, partner, product, yld in s47_rows:
    add(f"p0010_s47_210_{suffix}", f"Scheme 47 compound 210 with {partner}", [10], [
        P("reactant", "210", "3,4,6-trienoate"),
        P("reactant", partner),
        P("product", product, "[4+2] cycloadduct"),
    ], outcomes=[("yield", q(yld, "%"), product)])
for suffix, subs, yld in [
    ("tbu_me_h", "R1=t-Bu; R2=Me; R3=H", 57),
    ("me_me_me", "R1=R2=R3=Me", 58),
]:
    add(f"p0010_s47_215_{suffix}", f"Scheme 47 compound 215 {subs}", [10], [
        P("reactant", f"215 ({subs})", "3,4,6-trienoate"),
        P("reactant", "maleic anhydride"),
        P("product", f"216 ({subs})", "[4+2] cycloadduct"),
    ], outcomes=[("yield", q(yld, "%"), f"216 ({subs})")])

add("p0010_s48", "Scheme 48 overall", [10], [
    P("reactant", "217", "2,4,5-trienyl alcohol"),
    P("reactant", "TCNE", "tetracyanoethylene", "N#CC(C#N)=C(C#N)C#N"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "219", "bicyclic iminolactone"),
], conditions=[("temperature", q(25, "°C"))])
mechanism("p0010_s48_pathway", "Scheme 48 cycloaddition/cyclization", [10],
          ["217 + TCNE", "218", "219"], conditions=[("temperature", q(25, "°C"))])

# Page 11: Schemes 49--54.
add("p0011_s49_220", "Scheme 49 aldehyde scope", [10, 11], [
    P("reactant", "220 (R1=Me or Ph)", "vinylic allene"),
    P("reactant", "aldehyde (R2=alkyl or Ph)"),
    P("catalyst", "BF3·OEt2", "boron trifluoride diethyl etherate"),
    P("product", "221", "fused hetero-Diels–Alder product"),
], outcomes=[
    ("yield", qr(36, 70, "%", "36–70%"), "221"),
    ("cis_trans_ratio", "64:36 to 75:25", "221"),
])
add("p0011_s49_222", "Scheme 49 imine example", [10, 11], [
    P("reactant", "222", "vinylic allene"),
    P("reactant", "N-benzyl benzaldimine"),
    P("catalyst", "BF3·OEt2", "boron trifluoride diethyl etherate"),
    P("product", "223", "hetero-Diels–Alder product"),
], outcomes=[("yield", q(67, "%"), "223")])
add("p0011_s49_224", "Scheme 49 intramolecular scope", [10, 11], [
    P("reactant", "224 (R/X/n scope)", "aldehyde-tethered vinylic allene"),
    P("product", "225", "fused tricyclic product"),
])
add("p0011_s50", "Scheme 50", [11], [
    P("reactant", "226 (R1=H or Ar)", "2-substituted buta-2,3-dienoate"),
    P("reactant", "227 (R2 scope)", "N-tosyl imine"),
    P("catalyst", "PBu3", "tributylphosphine", "CCCCP(CCCC)CCCC",
      [("catalyst_loading", q(20, "mol%"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "228", "tetrahydropyridine"),
], conditions=[("temperature", "r.t.")], outcomes=[
    ("yield", qr(82, 99, "%", "82–99%"), "228"),
    ("diastereomer_ratio", "83:17 to 98:2", "228"),
])
mechanism("p0011_s51_mechanism", "Scheme 51 proposed PBu3 cycle", [11],
          ["226 + PBu3", "229", "230", "231A/231B", "232", "233", "228"],
          notes=["The review depicts sequential imine addition, proton transfers, cyclic conjugate addition, and phosphine release."])

add("p0011_s52", "Scheme 52", [11], [
    P("reactant", "234", "allene-bearing oxime precursor"),
    P("reagent", "PhNCO", "phenyl isocyanate", "O=C=Nc1ccccc1"),
    P("reagent", "Et3N", "triethylamine", "CCN(CC)CC"),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "235", "intramolecular nitrile-oxide [3+2] cycloadduct"),
], conditions=[("temperature", "reflux")],
    outcomes=[("yield", q(40, "%"), "235")])
add("p0011_s53_overall", "Scheme 53 overall", [11], [
    P("reactant", "236", "alkyne-nitrone precursor"),
    P("reagent", "base (unspecified)"),
    P("product", "242", "fused cyclization product"),
], conditions=[("temperature", "r.t.")])
mechanism("p0011_s53_mechanism", "Scheme 53 proposed cascade", [11],
          ["236", "237", "238", "239", "240", "241", "242"],
          conditions=[("temperature", "r.t.")],
          notes=["The review proposes nitrone formation, N–O homolysis, radical recombination, [4+3] cycloaddition, and a 1,5-H shift."])
add("p0011_s54_overall", "Scheme 54 overall", [11], [
    P("reactant", "243", "o-allenyloxy benzaldehyde"),
    P("reagent", "PhNHOH", "N-phenylhydroxylamine"),
    P("product", "245", "intramolecular nitrone-allene [3+2] cycloadduct"),
])
mechanism("p0011_s54_pathway", "Scheme 54 nitrone formation/cycloaddition", [11],
          ["243 + PhNHOH", "244", "245"])

# Page 12: Schemes 55--60 and two text-only continuations.
mechanism("p0012_s55_mechanism", "Scheme 55 proposed phosphine [3+2] cycle", [11, 12],
          ["246 + PR3", "247", "248", "249", "250", "251"],
          notes=["The scheme is a generic catalytic mechanism; EWG and EWG1 are unexpanded variables."])

s56_rows = [
    ("hh", "R1=R2=H", 17, 49),
    ("me_h", "R1=Me; R2=H", 38, 0),
    ("h_ph", "R1=H; R2=Ph", 78, 0),
]
for suffix, subs, y252, y253 in s56_rows:
    add(f"p0012_s56_{suffix}", f"Scheme 56 {subs}", [12], [
        P("reactant", f"allenoate ({subs})", "ethyl 2,3-alkadienoate"),
        P("reactant", "chiral activated alkene (drawn)"),
        P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
          [("catalyst_loading", q(10, "mol%"))]),
        P("solvent", "benzene", "benzene", "c1ccccc1"),
        P("product", f"252 ({subs})", "cyclic amino-acid derivative"),
        P("product", f"253 ({subs})", "regioisomeric cyclic amino-acid derivative"),
    ], conditions=[("temperature", "r.t.")], outcomes=[
        ("yield", q(y252, "%"), f"252 ({subs})"),
        ("yield", q(y253, "%"), f"253 ({subs})"),
    ])
add("p0012_s57", "Scheme 57 scope", [12], [
    P("reactant", "254 (printed cyclic enone scope)", "cyclic alpha-methylene ketone"),
    P("reactant", "tert-butyl butadienoate"),
    P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
      [("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "255", "major spirocyclic product"),
    P("product", "256", "minor spirocyclic product"),
], conditions=[("temperature", "reflux")], outcomes=[
    ("yield", qr(63, 99, "%", "63–99%"), ["255", "256"]),
    ("product_ratio_255_to_256", "74:26 to 95:5", ["255", "256"]),
], notes=["The yield and product-ratio ranges are aggregate scope values without row-resolved mapping."])

add("p0012_s58_cycloaddition", "Scheme 58 key [3+2] cycloaddition", [12], [
    P("reactant", "254a", "2-methylenecyclohexanone"),
    P("reactant", "tert-butyl butadienoate"),
    P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
      [("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "255a", "enantioenriched spirocycle"),
], conditions=[("temperature", "reflux")], outcomes=[
    ("yield", q(60, "%"), "255a"),
    ("enantiomeric_excess", q(94, "%", raw_text="94% ee"), "255a"),
])
add("p0012_s58_hydrogenation", "Scheme 58 hydrogenation", [12], [
    P("reactant", "255a", "enantioenriched spirocycle"),
    P("catalyst", "Pd/C", "palladium on carbon",
      amounts=[("catalyst_weight_fraction", q(5, "%", raw_text="5% w/w"))]),
    P("reagent", "H2", "hydrogen", "[H][H]"),
    P("solvent", "MeOH", "methanol", "CO"),
    P("product", "257B", "hydrogenation diastereomer"),
    P("product", "257A", "hydrogenation diastereomer"),
], conditions=[("temperature", "r.t."), ("atmosphere", "H2, 1 atm")], outcomes=[
    ("yield", q(99, "%"), ["257B", "257A"]),
    ("product_ratio_257B_to_257A", "13:87", ["257B", "257A"]),
])
add("p0012_s58_hydrolysis", "Scheme 58 acid treatment", [12], [
    P("reactant", "257A", "major hydrogenation diastereomer"),
    P("catalyst", "H2SO4 (cat.)", "sulfuric acid"),
    P("solvent", "MeOH", "methanol", "CO"),
    P("product", "258", "methyl ester ketone"),
], conditions=[("temperature", "reflux")],
    outcomes=[("yield", q(93, "%"), "258")])
add("p0012_s58_cyclopropanation", "Scheme 58 cyclopropanation", [12], [
    P("reactant", "258", "methyl ester ketone"),
    P("reagent", "Zn", "zinc", "[Zn]"),
    P("reagent", "CH2I2", "diiodomethane", "ICI"),
    P("reagent", "TiCl4", "titanium tetrachloride"),
    P("solvent", "CH2Cl2/THF", "dichloromethane/tetrahydrofuran"),
    P("product", "259", "methylenated/cyclopropanated intermediate"),
], outcomes=[("yield", q(82, "%"), "259")])
final = add("p0012_s58_hinesol", "Scheme 58 conversion to (−)-hinesol", [12], [
    P("reactant", "259", "hinesol precursor"),
    P("reagent", "p-TsOH", "p-toluenesulfonic acid"),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("reagent", "MeMgI", "methylmagnesium iodide"),
    P("solvent", "Et2O", "diethyl ether", "CCOCC"),
    P("product", "260", "(−)-hinesol"),
], conditions=[("operation", "sequential acid treatment then MeMgI addition")],
    outcomes=[("yield", q(87, "%"), "260")])
evidence = ev([12])
ids = {p["label"]["value"]: p["entity_id"] for p in final["participants"]}
final["steps"] = [
    {"step_id": "step1", "participant_ids": [ids["259"], ids["p-TsOH"], ids["benzene"]],
     "conditions": [{"name": "temperature", "fact": fact("reflux", evidence)}]},
    {"step_id": "step2", "participant_ids": [ids["MeMgI"], ids["Et2O"]],
     "conditions": [
         {"name": "temperature", "fact": fact(q(0, "°C"), evidence)},
         {"name": "warm_to", "fact": fact("r.t.", evidence)},
     ]},
]

s59_261 = [("co2et", "EWG=CO2Et", 68), ("come", "EWG=COMe", 84),
           ("coph", "EWG=COPh", 70)]
for suffix, ewg, yld in s59_261:
    add(f"p0012_s59_261_{suffix}", f"Scheme 59 compound 261 {ewg}", [12], [
        P("reactant", f"electron-deficient allene ({ewg})"),
        P("reactant", "261", "2-hydroxycyclohexanone"),
        P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
          [("catalyst_loading", q(10, "mol%"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", f"262 ({ewg})", "dihydrofuran"),
    ], conditions=[("temperature", qr(70, 110, "°C", "70–110 °C"))],
        outcomes=[("yield", q(yld, "%"), f"262 ({ewg})")])
for suffix, rgroup, yld in [("me", "R=Me", 60), ("oet", "R=OEt", 77)]:
    add(f"p0012_s59_263_{suffix}", f"Scheme 59 compound 263 {rgroup}", [12], [
        P("reactant", "electron-deficient allene (EWG variable)"),
        P("reactant", f"263 ({rgroup})", "1,3-dicarbonyl compound"),
        P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
          [("catalyst_loading", q(10, "mol%"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", f"264 ({rgroup})", "dihydrofuran"),
    ], conditions=[("temperature", qr(70, 110, "°C", "70–110 °C"))],
        outcomes=[("yield", q(yld, "%"), f"264 ({rgroup})")],
        notes=["The arrow is marked ibid, so the preceding Scheme 59 catalyst, solvent, and temperature range are applied."])
mechanism("p0012_s60_mechanism", "Scheme 60 proposed gamma-addition cycle", [12],
          ["electron-deficient allene + PPh3", "247a / 266", "267", "268", "269", "270", "262 or 264"],
          notes=["The nucleophile is represented generically as HNu–NuH and EWG is unexpanded."])

add("p0012_s61_text_only", "Scheme 61 text-only introduction", [12], [
    P("reactant", "thiobenzamide"),
    P("reactant", "2,3-alkadienoate"),
    P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
      [("catalyst_loading", q(10, "mol%"))]),
    P("product", "271", "thiazoline"),
], unresolved=["Scheme 61 itself is on the following page and was outside this six-page image batch; only the page-12 prose is encoded."])
add("p0012_s62_text_only", "Scheme 62 text-only precursor formation", [12], [
    P("reactant", "272", "4-acetoxy-2-alkynoate"),
    P("reagent", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1"),
    P("product", "273", "2-acyl-2,3-alkadienoate"),
], unresolved=["Scheme 62 is on the following page; downstream partners, conditions, and outcomes are not reconstructed from the page-12 lead-in."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
