import json
from pathlib import Path

DOC = "doc_03ca6cf38d4f5d15"


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return out


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, target=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = list(target)
    return item


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in (amounts or [])],
    }


def record(rid, evidence, participants, conditions, outcomes, *, kind="reported_experiment", notes=None, unresolved=None):
    nonproducts = [p["entity_id"] for p in participants if p["role"] != "product"]
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": nonproducts,
            "conditions": [field(n, v, evidence) for n, v in conditions],
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting information was not explicitly provided or associated.",
                "Machine extraction requires chemical source review; structures remain unverified.",
            ],
        },
    }


def qty(number, unit, raw=None, **extra):
    value = {"number": number, "unit": unit}
    if raw:
        value["raw_text"] = raw
    value.update(extra)
    return value


records = []

# Scheme 3, with the detailed procedures on page 6 merged into the same records.
e = ev(1, 2, 6)
p = [
    part("ab", "reactant", "A/B (eta1-propargylic/eta1-allenylic Pd complexes, 1.7:1)", e,
         amounts=[("mass", qty(205, "mg")), ("amount", qty(0.25, "mmol"))]),
    part("zinc12a", "reactant", "(2Z)-ethoxycarbonylethenyl zinc iodide", e,
         amounts=[("volume", qty(0.5, "mL")), ("concentration", qty(1.0, "M", "ca. 1.0 M")), ("amount", qty(0.5, "mmol"))]),
    part("thf", "solvent", "THF", e, name="tetrahydrofuran", amounts=[("volume", qty(2, "mL"))]),
    part("prod", "product", "ethyl 6-phenylhex-5-yn-(2Z)-enoate", e,
         smiles="CCOC(=O)C=CCC#Cc1ccccc1", amounts=[("mass", qty(30, "mg"))]),
]
records.append(record("scheme3_alkenylzinc", e, p,
    [("reaction_temperature", "r.t."), ("reaction_time", qty(1, "h")),
     ("workup", "quenched with water; ether extraction; water wash; MgSO4 drying; rotary evaporation"),
     ("purification", "silica gel chromatography, hexane/ethyl acetate 100:1")],
    [field("yield", qty(57, "%"), e, ["prod"]), field("yield_measurement_basis", "isolated", e, ["prod"]),
     field("regioselectivity", "alkyne product exclusively", e, ["prod"])]))

e = ev(1, 2, 6)
p = [
    part("phI", "reactant", "phenyl iodide", e, name="iodobenzene", smiles="Ic1ccccc1",
         amounts=[("mass", qty(102, "mg")), ("amount", qty(0.5, "mmol"))]),
    part("nBuLi", "reagent", "n-BuLi", e, amounts=[("volume", qty(0.28, "mL")), ("amount", qty(0.56, "mmol")), ("concentration", qty(2, "M"))]),
    part("znbr2", "reagent", "ZnBr2", e, amounts=[("mass", qty(250, "mg")), ("amount", qty(1.1, "mmol"))]),
    part("ab", "reactant", "A/B (eta1-propargylic/eta1-allenylic Pd complexes)", e, amounts=[("mass", qty(519, "mg")), ("amount", qty(0.63, "mmol"))]),
    part("thf", "solvent", "THF", e, name="tetrahydrofuran", amounts=[("volume", qty(4, "mL", "2 mL + 2 mL"))]),
    part("prod", "product", "1,1-diphenylpropa-1,2-diene", e, smiles="C=C(c1ccccc1)c1ccccc1", amounts=[("mass", qty(58, "mg"))]),
]
records.append(record("scheme3_phenylzinc", e, p,
    [("atmosphere", "N2"), ("reaction_temperature", qty(-78, "°C")), ("reaction_time", qty(25, "min")),
     ("operation", "ZnBr2 added; held 5 min at -78 °C, warmed to r.t. for 15 min, then A/B added"),
     ("time_at_room_temperature", qty(1, "h")),
     ("workup", "quenched with water; ether extraction; water wash; MgSO4 drying; rotary evaporation"),
     ("purification", "silica gel chromatography, hexane")],
    [field("yield", qty(60, "%"), e, ["prod"]), field("yield_measurement_basis", "isolated", e, ["prod"]),
     field("regioselectivity", "allene product; 1,3-diphenyl-1-propyne 3–4% if any", e, ["prod"])],
    unresolved=["Supporting information was not explicitly associated.", "The phrase '3–4%, if any' is qualitative/uncertain and is retained without creating a second product yield."]))

# Scheme 5 lithiation/transmetalation/coupling scope. Z-2a, Z-2b, E-2a and Z-2c gain page-6 procedure evidence.
scheme5 = [
    ("scheme5_Z2a", (2, 6), "ethyl (Z)-3-iodo-2-propenoate", "Z-2a", "ethyl 6-(trimethylsilyl)hex-5-yn-(2Z)-enoate", 0, 2, 96, "ZnBr2"),
    ("scheme5_Z2b", (2, 6), "methyl (Z)-3-iodo-2-propenoate", "Z-2b", "methyl 6-(trimethylsilyl)hex-5-yn-(2Z)-enoate", 0, 2.75, 66, "ZnBr2"),
    ("scheme5_E2a", (2, 6), "ethyl (E)-3-iodo-2-propenoate", "E-2a", "ethyl 6-(trimethylsilyl)hex-5-yn-(2E)-enoate", 0, 1.17, 94, "ZnBr2"),
    ("scheme5_Z2c", (2, 6), "ethyl (Z)-3-iodo-2-propenoate", "Z-2c", "ethyl 6-(trimethylsilyl)-4-propylhex-5-yn-(2Z)-enoate", 20, 12, 60, "ZnBr2"),
    ("scheme5_E2c", (2,), "ethyl (E)-3-iodo-2-propenoate", "E-2c", "ethyl 6-(trimethylsilyl)-4-propylhex-5-yn-(2E)-enoate", 11, 2.17, 58, "ZnI2"),
]
for rid, pages, iodide, label, product_name, temp, hours, yld, zinc in scheme5:
    e = ev(*pages)
    starting = "1-(trimethylsilyl)hex-1-yne (3)" if label.endswith("2c") else "1-(trimethylsilyl)prop-1-yne (1)"
    p = [
        part("alkyne", "reactant", starting, e), part("nbuli", "reagent", "n-BuLi", e),
        part("zinc", "reagent", zinc, e), part("iodide", "reactant", iodide, e),
        part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]),
        part("thf", "solvent", "THF", e), part("prod", "product", label, e, name=product_name),
    ]
    records.append(record(rid, e, p,
        [("lithiation_temperature", qty(-78, "°C")), ("reaction_temperature", qty(temp, "°C")), ("reaction_time", qty(hours, "h"))],
        [field("yield", qty(yld, "%"), e, ["prod"]), field("yield_measurement_basis", "isolated", e, ["prod"]),
         field("stereochemical_outcome", "alkene configuration retained", e, ["prod"])],
        kind="substrate_scope_entry",
        unresolved=["Supporting information was not explicitly associated.", "Amounts/workup are incomplete for abbreviated scope entries; any page-6 details are only used where explicitly present.", "Product connectivity is represented by source label/name; structure not verified."]))

# Table 1. Each row is a separate scope experiment under the shared header conditions.
table1 = [
    (1, "Ph", "o-methylphenyl iodide", 26, 5.5, "2 (alkyne)", 0, "6a", 85, "0/100"),
    (2, "Me3Si", "o-methylphenyl iodide", {"minimum": 0, "maximum": 20, "unit": "°C", "raw_text": "0–20 °C"}, 5.5, "2d", 52, "6 (allene)", 0, "100/0"),
    (3, "Me3Si", "phenyl iodide", 28, 2.25, "2e", 24, "6b", 23, "51/49"),
    (4, "Me3Si", "1-naphthyl iodide", 26, 13.5, "2f", 41, "6c", 17, "71/29"),
    (5, "TBS", "1-naphthyl iodide", 31, 15.5, "2g", 52, "6 (allene)", 0, "100/0"),
]
for row, rgroup, arx, temp, hours, p2, y2, p6, y6, ratio in table1:
    e = ev(2, 3) if row in (2, 3, 4, 5) else ev(2, 3)
    tval = temp if isinstance(temp, dict) else qty(temp, "°C")
    p = [
        part("alkyne", "reactant", f"R-C#C-CH3 (R={rgroup})", e), part("arx", "reactant", arx, e),
        part("nbuli", "reagent", "n-BuLi", e), part("znbr2", "reagent", "ZnBr2", e),
        part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]),
        part("thf", "solvent", "THF", e), part("prod2", "product", p2, e), part("prod6", "product", p6, e),
    ]
    records.append(record(f"table1_entry{row}", e, p,
        [("lithiation_temperature", qty(-78, "°C")), ("reaction_temperature", tval), ("reaction_time", qty(hours, "h"))],
        [field("yield_2", qty(y2, "%", "-(0)" if y2 == 0 else None), e, ["prod2"]),
         field("yield_6", qty(y6, "%", "-(0)" if y6 == 0 else None), e, ["prod6"]),
         field("product_ratio_2_to_6", ratio, e, ["prod2", "prod6"]),
         field("yield_measurement_basis", "reported table yield; isolation basis not stated in table", e, ["prod2", "prod6"])],
        kind="substrate_scope_entry",
        unresolved=["Supporting information was not explicitly associated.", "Table product drawings were transcribed by label; SMILES omitted pending structure review."]))

# Table 2. Carbonate/zinc-reagent labels preserve source identity without expanding uncertain generic structures.
table2 = [
    (1, "11a", "12a", 50, 0.75, [("Z-2a", 44)], None),
    (2, "11a", "12b", 55, 1, [("E-2i", 60)], None),
    (3, "11a", "12c", 45, 2.75, [("2j (Z/E mixture)", 63)], "Z/E=4/5"),
    (4, "11b", "12a", 50, 0.75, [("Z-2h", 58)], None),
    (5, "11b", "12b", 60, 2, [("E-2k", 63)], None),
    (6, "11b", "12d", 55, 0.9, [("2h (Z/E mixture)", 40)], "Z/E=5/6"),
    (7, "11c", "12a", 50, 0.5, [("Z-2l", 55), ("E-6d", 18)], None),
    (8, "11c", "12b", 50, 1.25, [("E-2m", 44)], None),
    (9, "11d", "12a", 50, 2.5, [("Z-2c", 35)], None),
    (10, "11d", "12b", 55, 11.5, [], None),
]
carbonate_names = {"11a": "methyl 3-(trimethylsilyl)prop-2-ynyl carbonate", "11b": "methyl 3-phenylprop-2-ynyl carbonate", "11c": "methyl 2-heptynyl carbonate", "11d": "methyl 1-(trimethylsilyl)hex-1-yn-3-yl carbonate"}
for row, c, z, temp, hours, products, ratio in table2:
    pages = (4, 5) if row == 4 else (4, 5) if row in (2, 3, 5, 6, 7, 8) else (4,)
    e = ev(*pages)
    p = [part("carbonate", "reactant", c, e, name=carbonate_names[c]), part("zinc", "reactant", z, e),
         part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]), part("thf", "solvent", "THF", e)]
    outs = []
    for i, (label, yld) in enumerate(products, 1):
        eid = f"prod{i}"
        p.append(part(eid, "product", label, e))
        outs.append(field("yield", qty(yld, "%"), e, [eid]))
        outs.append(field("yield_measurement_basis", "reported table yield; isolation basis not stated in table", e, [eid]))
    if ratio:
        outs.append(field("stereoisomer_ratio", ratio, e, ["prod1"]))
    if not products:
        outs.append(field("result", "no product reported (both product columns shown as dash)", e))
    unresolved = ["Supporting information was not explicitly associated.", "Table structures were transcribed by labels; SMILES omitted pending source review."]
    if row == 4:
        unresolved.append("Source-internal temperature conflict: Table 2 entry 4 reports 50 °C, while the cross-page prose reports 55 °C for the 58% sole-product experiment.")
    records.append(record(f"table2_entry{row}", e, p,
        [("reaction_temperature", qty(temp, "°C")), ("reaction_time", qty(hours, "h"))], outs,
        kind="substrate_scope_entry", unresolved=unresolved))

# Two preliminary experiments described in prose before the final Table 2 entry 4 conditions.
for rid, temp, result in [
    ("carbonate11b_12a_room_temp_no_reaction", "r.t.", "reaction did not take place"),
    ("carbonate11b_12a_55C_mixed_products", qty(55, "°C"), "Z-2h plus ethyl 6-phenylhex-5-yn-3-enoate (double-bond migration product); yields not stated"),
]:
    e = ev(4)
    p = [part("carbonate", "reactant", "methyl 3-phenylprop-2-ynyl carbonate", e, amounts=[("amount", qty(0.5, "mmol"))]),
         part("zinc", "reactant", "(2Z)-ethoxycarbonylethenylzinc iodide (12a)", e, amounts=[("amount", qty(0.5, "mmol"))]),
         part("pd", "catalyst", "Pd(PPh3)4", e), part("thf", "solvent", "THF", e)]
    if "mixed" in rid:
        p.extend([part("prod1", "product", "ethyl 6-phenylhex-5-yn-(2Z)-enoate (Z-2h)", e), part("prod2", "product", "ethyl 6-phenylhex-5-yn-3-enoate", e)])
    records.append(record(rid, e, p, [("reaction_temperature", temp), ("reaction_time", None)],
        [field("result", result, e)], kind="optimization_entry",
        unresolved=["Reaction time and product yields were not reported in this prose description.", "Supporting information was not explicitly associated."]))

# Scheme 8: each starting-halide row is retained as an independent organozinc-preparation experiment.
scheme8 = [
    (1, "ethyl (Z)-3-iodopropenoate", "12a", 21, "Z/E=100/0", "determined by iodinolysis"),
    (2, "methyl 3-phenyl-3-iodopropenoate", "12b", 21, "Z/E=1.8/1", "determined by hydrolysis"),
    (3, "methyl 3-iodo-2-butenoate", "12c", 12, "Z/E=7.1/1", "determined by iodinolysis"),
    (4, "ethyl 3-iodopropenoate isomer mixture", "12d", 9, "Z/E=1/3.6", "determined by iodinolysis"),
]
for row, start, product, hours, ratio, method in scheme8:
    e = ev(4)
    p = [part("halide", "reactant", start, e), part("zn", "reagent", "Zn", e),
         part("dibromoethane", "reagent", "BrCH2CH2Br", e, name="1,2-dibromoethane"),
         part("tmscl", "reagent", "Me3SiCl", e, name="trimethylsilyl chloride"), part("thf", "solvent", "THF", e),
         part("organozinc", "product", product, e)]
    records.append(record(f"scheme8_entry{row}", e, p,
        [("reaction_temperature", qty(45, "°C")), ("reaction_time", qty(hours, "h"))],
        [field("stereoisomer_ratio", ratio, e, ["organozinc"]), field("configuration_determination", method, e, ["organozinc"])],
        unresolved=["Scheme 8 does not state reagent quantities in the inspected page region.", "Supporting information was not explicitly associated.", "Organozinc structures remain label-based and unverified."]))

# Scheme 9: three distinct carbonate/12 experiments, including the explicit failed reaction.
scheme9 = [
    ("scheme9_11e_12a", "11e", "12a (Z)", 55, 1.4, "E-6e", 70),
    ("scheme9_11e_12d", "11e", "12d (Z/E=1/3.6)", 55, 1.25, "E-6e", 55),
    ("scheme9_11f_12a_no_product", "11f", "12a (Z)", 50, 6, None, 0),
]
for rid, c, z, temp, hours, prod, yld in scheme9:
    e = ev(5)
    p = [part("carbonate", "reactant", c, e), part("zinc", "reactant", z, e),
         part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]), part("thf", "solvent", "THF", e)]
    if prod:
        p.append(part("prod", "product", prod, e, name="ethyl 4-(n-butyl)nona-(2E),4,5-trienoate"))
        outs = [field("yield", qty(yld, "%"), e, ["prod"]), field("yield_measurement_basis", "reported scheme yield", e, ["prod"])]
    else:
        outs = [field("yield", qty(0, "%"), e), field("result", "no product", e)]
    records.append(record(rid, e, p, [("reaction_temperature", qty(temp, "°C")), ("reaction_time", qty(hours, "h"))], outs,
        kind="substrate_scope_entry", unresolved=["Supporting information was not explicitly associated.", "Source labels 11e/11f/12 are retained because structures were not independently verified."]))

# Scheme 10: one reaction gives two products; the other uses the explicit 3.5 equiv Na2CO3 additive.
e = ev(5)
p = [part("carbonate", "reactant", "11g (methyl 2-heptynyl carbonate)", e),
     part("boronic", "reactant", "(2E)-phenylethenylboronic acid", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]),
     part("thf", "solvent", "THF", e), part("prod1", "product", "E-2o", e, name="1-phenylnona-4-yn-(1E)-ene"),
     part("prod2", "product", "E-6f", e, name="1-phenyl-4-(n-butyl)-(1E),3,4-pentatriene"),
     part("byproduct", "product", "13 (self-coupling product of phenylethenylboronic acid)", e)]
records.append(record("scheme10_11g_boronic", e, p,
    [("reaction_temperature", "reflux"), ("reaction_time", qty(4, "h"))],
    [field("yield", qty(49, "%"), e, ["prod1"]), field("yield", qty(29, "%"), e, ["prod2"]),
     field("byproduct_amount", "small amount; no numeric yield", e, ["byproduct"]), field("yield_measurement_basis", "isolated", e, ["prod1", "prod2"])],
    unresolved=["The yield of byproduct 13 is not stated.", "Supporting information was not explicitly associated."]))

e = ev(5)
p = [part("carbonate", "reactant", "11e", e), part("boronic", "reactant", "(2E)-phenylethenylboronic acid", e),
     part("base", "reagent", "Na2CO3", e, amounts=[("equivalents", qty(3.5, "equiv"))]),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]), part("thf", "solvent", "THF", e),
     part("prod", "product", "E-6g", e, name="3-(n-butyl)-1-phenyloct-(1E),3,4-triene")]
records.append(record("scheme10_11e_boronic", e, p,
    [("reaction_temperature", qty(55, "°C")), ("reaction_time", qty(2, "h"))],
    [field("yield", qty(60, "%"), e, ["prod"]), field("yield_measurement_basis", "reported isolated product", e, ["prod"]), field("regioselectivity", "sole product", e, ["prod"])],
    unresolved=["Supporting information was not explicitly associated.", "Structure remains label/name based and unverified."]))

# Equation (1), distinct acetate substrate experiment.
e = ev(5)
p = [part("acetate", "reactant", "3-phenylprop-2-ynyl acetate", e), part("zinc", "reactant", "12a", e),
     part("pd", "catalyst", "Pd(PPh3)4", e, amounts=[("catalyst_loading", qty(5, "mol%"))]), part("thf", "solvent", "THF", e),
     part("prod", "product", "Z-2h", e, name="ethyl 6-phenylhex-5-yn-(2Z)-enoate")]
records.append(record("equation1_propargyl_acetate_12a", e, p,
    [("reaction_temperature", qty(55, "°C")), ("reaction_time", qty(1.17, "h"))],
    [field("yield", qty(37, "%"), e, ["prod"]), field("yield_measurement_basis", "reported product yield", e, ["prod"])],
    kind="substrate_scope_entry", unresolved=["Supporting information was not explicitly associated.", "Reactant quantities are not shown in the inspected equation region."]))

out = Path(__file__).with_name("extracted_records_pages_0001_0006.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(out)}, ensure_ascii=False))
