#!/usr/bin/env python3
"""Build/augment machine-derived reaction records for PDF pages 7--12."""

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_50d01341363d3c76"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def unique(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def qty(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return field(name, value, evidence)


def participant(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def base_record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": unique(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-derived record requires expert chemical review.",
                "Participant connectivity and product stereochemistry remain unverified.",
            ],
        },
    }


def find_participant(record, label):
    return next(p for p in record["participants"] if p["label"]["value"] == label)


def set_amount(participant_obj, name, value, evidence):
    new_field = field(name, value, evidence)
    for index, old in enumerate(participant_obj["amounts"]):
        if old["name"] == name:
            participant_obj["amounts"][index] = new_field
            return
    participant_obj["amounts"].append(new_field)


def set_condition(record, name, value, evidence):
    conditions = record["steps"][0]["conditions"]
    new_field = field(name, value, evidence)
    for index, old in enumerate(conditions):
        if old["name"] == name:
            conditions[index] = new_field
            return
    conditions.append(new_field)


dataset = json.loads((OUT / "dataset.json").read_text())
existing = {record["record_id"]: record for record in dataset["experiments"]}
records = []


# Page 7: exact preparation of 2c, a compound-specific realization of the
# generic literature procedure shown on page 2.
e7 = ev(7)
rid = "preparation_2c_oxidation_1c"
parts = [
    participant("prep2c_1c", "reactant", "1c", "hepta-1,2-dien-3-yl phenyl sulfoxide", e7,
                [qty("mass", 441, "mg", e7), qty("amount", 2, "mmol", e7)],
                "C=C=C(CCCC)S(=O)c1ccccc1"),
    participant("prep2c_h2o2", "reagent", "30% H2O2", "30% hydrogen peroxide", e7,
                [qty("concentration", 30, "%", e7), qty("volume", 0.6, "mL", e7)], "OO"),
    participant("prep2c_acoh", "solvent", "AcOH", "acetic acid", e7,
                [qty("volume", 5, "mL", e7)], "CC(=O)O"),
    participant("prep2c_icewater", "reagent", "ice-water", "ice-water", e7,
                [qty("volume", 15, "mL", e7)]),
    participant("prep2c_chcl3", "solvent", "CHCl3", "chloroform", e7,
                [qty("extraction_volume_per_portion", 15, "mL", e7)], "ClC(Cl)Cl"),
    participant("prep2c_nahco3", "reagent", "sat. aq. NaHCO3", "saturated aqueous sodium bicarbonate", e7,
                [qty("wash_volume_per_portion", 15, "mL", e7)]),
    participant("prep2c_mgso4", "reagent", "MgSO4", "magnesium sulfate", e7),
    participant("prep2c_product", "product", "2c", "hepta-1,2-dien-3-yl phenyl sulfone", e7,
                smiles="C=C=C(CCCC)S(=O)(=O)c1ccccc1"),
]
records.append(base_record(
    rid, "reported_experiment", e7, parts,
    [{
        "step_id": "oxidation_and_isolation",
        "participant_ids": [p["entity_id"] for p in parts],
        "conditions": [
            field("temperature", {"number": 100, "unit": "°C"}, e7),
            field("time", {"number": 0.5, "unit": "h"}, e7),
            field("monitoring", "TLC to complete conversion", e7),
            field("atmosphere", None, []),
            field("workup", "quenched with ice-water; extracted with CHCl3 (4 × 15 mL); organic layer washed with saturated aqueous NaHCO3 (4 × 15 mL) and dried over MgSO4; solvent evaporated", e7),
            field("purification", "flash chromatography on silica gel with PE–Et2O 2:1", e7),
        ],
    }],
    [
        field("isolated_product_mass", {"number": 251, "unit": "mg"}, e7, ["prep2c_product"]),
        field("isolated_yield_2c", {"number": 53, "unit": "%"}, e7, ["prep2c_product"]),
        field("yield_measurement_basis", "isolated after flash chromatography", e7),
    ],
    unresolved=[
        "Atmosphere is not reported.",
        "The candidate 1c/2c structures are machine interpretations and remain unverified.",
    ],
))


# Add exact page-7--11 preparations to existing Conditions-A records.  These
# are the same experiments as Table 4/Table 5 rows and are replaced, not
# duplicated.
conditions_a_details = {
    "optimized_2a_3a_conditions_A": dict(pages=[7], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3a", boronic_mass=62, boronic_mmol=0.51, pd_mass=30, pd_mmol=0.026, product="(E)-4aa", product_mass=44,
        product_name="phenyl (E)-2-phenylprop-1-en-1-yl sulfone", purification="flash chromatography on silica gel with PE–Et2O 20:1"),
    "table4_entry2_4ab": dict(pages=[7, 8], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3b", boronic_mass=69, boronic_mmol=0.51, pd_mass=29, pd_mmol=0.025, product="(E)-4ab", product_mass=42,
        product_name="phenyl (E)-2-(4-tolyl)prop-1-en-1-yl sulfone"),
    "table4_entry3_4ac": dict(pages=[8], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3c", boronic_mass=76, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-4ac", product_mass=25,
        product_name="(E)-2-(3-methoxyphenyl)prop-1-en-1-yl phenyl sulfone"),
    "table4_entry4_4ad": dict(pages=[8], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3d", boronic_mass=77, boronic_mmol=0.51, pd_mass=30, pd_mmol=0.026, product="(E)-4ad", product_mass=56,
        product_name="(E)-2-(4-methoxyphenyl)prop-1-en-1-yl phenyl sulfone"),
    "table4_entry5_4ae": dict(pages=[8, 9], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3e", boronic_mass=84, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-4ae", product_mass=50,
        product_name="(E)-2-(3-nitrophenyl)prop-1-en-1-yl phenyl sulfone"),
    "table4_entry6_4af": dict(pages=[9], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3f", boronic_mass=82, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-4af", product_mass=60,
        product_name="(E)-2-(3-acetylphenyl)prop-1-en-1-yl phenyl sulfone"),
    "table4_entry7_4ag": dict(pages=[9], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3g", boronic_mass=82, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-4ag", product_mass=60,
        product_name="(E)-2-(4-acetylphenyl)prop-1-en-1-yl phenyl sulfone"),
    "table4_entry8_4ah": dict(pages=[9], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3h", boronic_mass=87, boronic_mmol=0.51, pd_mass=29, pd_mmol=0.025, product="(E)-4ah", product_mass=56,
        product_name="(E)-2-(1-naphthyl)prop-1-en-1-yl phenyl sulfone"),
    "table4_entry9_4ai": dict(pages=[9], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3i", boronic_mass=72, boronic_mmol=0.51, pd_mass=30, pd_mmol=0.026, product="(E)-4ai", product_mass=50,
        product_name="(1E,3E)-2-methylnona-1,3-dien-1-yl phenyl sulfone"),
    "table4_entry10_4aj": dict(pages=[9], allene="2a", allene_mass=45, allene_mmol=0.25,
        boronic="3j", boronic_mass=77, boronic_mmol=0.49, pd_mass=29, pd_mmol=0.025, product="(E)-4aj", product_mass=37,
        product_name="(1E,3E)-2-methyl-4-phenylbuta-1,3-dien-1-yl phenyl sulfone"),
    "table4_entry11_4ba": dict(pages=[9, 10], allene="2b", allene_mass=49, allene_mmol=0.25,
        boronic="3a", boronic_mass=61, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-4ba", product_mass=34,
        product_name="phenyl (E)-3-phenylbut-2-en-2-yl sulfone"),
    "table4_entry12_4ca": dict(pages=[10], allene="2c", allene_mass=59, allene_mmol=0.25,
        boronic="3a", boronic_mass=61, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-4ca", product_mass=43,
        product_name="phenyl (E)-2-phenylhept-2-en-3-yl sulfone"),
    "table5_entry1_6aa": dict(pages=[10], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3a", boronic_mass=61, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-6aa", product_mass=30,
        product_name="phenyl (E)-2-phenylprop-1-en-1-yl sulfoxide"),
    "table5_entry2_6ab": dict(pages=[10], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3b", boronic_mass=69, boronic_mmol=0.51, pd_mass=29, pd_mmol=0.025, product="(E)-6ab", product_mass=37,
        product_name="phenyl (E)-2-(4-tolyl)prop-1-en-1-yl sulfoxide"),
    "table5_entry3_6ac": dict(pages=[10], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3c", boronic_mass=76, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-6ac", product_mass=41,
        product_name="(E)-2-(3-methoxyphenyl)prop-1-en-1-yl phenyl sulfoxide"),
    "table5_entry4_6ad": dict(pages=[10], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3d", boronic_mass=76, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-6ad", product_mass=35,
        product_name="(E)-2-(4-methoxyphenyl)prop-1-en-1-yl phenyl sulfoxide"),
    "table5_entry5_6ae": dict(pages=[10], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3e", boronic_mass=85, boronic_mmol=0.51, pd_mass=29, pd_mmol=0.025, product="(E)-6ae", product_mass=35,
        product_name="(E)-2-(3-nitrophenyl)prop-1-en-1-yl phenyl sulfoxide"),
    "table5_entry6_6ag": dict(pages=[11], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3g", boronic_mass=83, boronic_mmol=0.51, pd_mass=29, pd_mmol=0.025, product="(E)-6ag", product_mass=34,
        product_name="(E)-2-(4-acetylphenyl)prop-1-en-1-yl phenyl sulfoxide"),
    "table5_entry7_6ah": dict(pages=[11], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3h", boronic_mass=86, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-6ah", product_mass=30,
        product_name="(E)-2-(1-naphthyl)prop-1-en-1-yl phenyl sulfoxide", pretreatment="3h should be recrystallized from H2O immediately before use"),
    "table5_entry8_6ak": dict(pages=[11], allene="1a", allene_mass=41, allene_mmol=0.25,
        boronic="3k", boronic_mass=64, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-6ak", product_mass=33,
        product_name="(1E,3E)-2-methylocta-1,3-dien-1-yl phenyl sulfoxide", identity_note="The heading and ratios identify 6ak, but the isolation sentence prints (E)-6al."),
    "table5_entry9_6aj": dict(pages=[11], allene="1a", allene_mass=40, allene_mmol=0.24,
        boronic="3j", boronic_mass=78, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product="(E)-6aj", product_mass=31,
        product_name="(1E,3E)-2-methyl-4-phenylbuta-1,3-dien-1-yl phenyl sulfoxide"),
}

for suffix, detail in conditions_a_details.items():
    record = copy.deepcopy(existing[f"{DOC}:{suffix}"])
    evidence = unique(sum((ev(page) for page in detail["pages"]), []))
    record["evidence_ids"] = unique(record["evidence_ids"] + evidence)
    allene = find_participant(record, detail["allene"])
    set_amount(allene, "mass", {"number": detail["allene_mass"], "unit": "mg"}, evidence)
    set_amount(allene, "amount", {"number": detail["allene_mmol"], "unit": "mmol"}, evidence)
    boronic = find_participant(record, detail["boronic"])
    set_amount(boronic, "mass", {"number": detail["boronic_mass"], "unit": "mg"}, evidence)
    set_amount(boronic, "amount", {"number": detail["boronic_mmol"], "unit": "mmol"}, evidence)
    pd = find_participant(record, "Pd(PPh3)4")
    set_amount(pd, "mass", {"number": detail["pd_mass"], "unit": "mg"}, evidence)
    set_amount(pd, "amount", {"number": detail["pd_mmol"], "unit": "mmol"}, evidence)
    acoh = find_participant(record, "AcOH")
    set_amount(acoh, "volume", {"number": 14, "unit": "uL"}, evidence)
    set_amount(acoh, "amount", {"number": 0.24, "unit": "mmol"}, evidence)
    solvent = next(p for p in record["participants"] if p["role"] == "solvent" and p["label"]["value"] == "THF")
    set_amount(solvent, "volume", {"number": 3, "unit": "mL"}, evidence)
    product = find_participant(record, detail["product"])
    product["name"] = fact(detail["product_name"], evidence)
    set_condition(record, "workup", "solvent evaporation; filtration through a pad of silica gel; evaporation to dryness; crude mixture analyzed by 1H NMR", evidence)
    set_condition(record, "purification", detail.get("purification", "flash chromatography on silica gel"), evidence)
    if detail.get("pretreatment"):
        set_condition(record, "reactant_pretreatment", detail["pretreatment"], evidence)
    record["outcomes"].append(field("isolated_product_mass", {"number": detail["product_mass"], "unit": "mg"}, evidence, [product["entity_id"]]))
    if detail.get("identity_note"):
        record["notes"].append(fact(detail["identity_note"], evidence))
    unresolved = ["Complex product/regioisomer structures and stereochemical SMILES remain unverified."]
    if detail.get("identity_note"):
        unresolved.append("The page-11 isolation sentence has an unresolved 6ak/6al product-code conflict.")
    record["review"]["unresolved"] = unresolved
    records.append(record)


BORONIC = {
    "3a": ("phenylboronic acid", "OB(O)c1ccccc1"),
    "3b": ("4-tolylboronic acid", "OB(O)c1ccc(C)cc1"),
    "3l": ("2-methoxyphenylboronic acid", "COc1ccccc1B(O)O"),
    "3d": ("4-methoxyphenylboronic acid", "COc1ccc(B(O)O)cc1"),
    "3e": ("3-nitrophenylboronic acid", "O=[N+]([O-])c1cccc(B(O)O)c1"),
    "3g": ("4-acetylphenylboronic acid", "CC(=O)c1ccc(B(O)O)cc1"),
    "3h": ("1-naphthylboronic acid", "OB(O)c1cccc2ccccc12"),
}


# Page 7, Table 7.  Rows with detailed procedures on pages 11--12 receive
# exact amounts and post-purification ratios; the remaining rows retain only
# the table-level facts.
table7 = [
    dict(entry=1, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3a", product="9aa", minor="10aa", yld=75, ratio="92:8", stereo=">99:1", time=9, page=11,
         allene_mass=38, boronic_mass=61, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=43, isolated_ratio="96:4", product_name="(E)-2-phenylundec-2-ene"),
    dict(entry=2, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3b", product="9ab", minor="10ab", yld=75, ratio="91:9", stereo=">99:1", time=9, page=11,
         allene_mass=38, boronic_mass=68, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=46, isolated_ratio="93:7", product_name="(E)-2-(4-tolyl)undec-2-ene"),
    dict(entry=3, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3l", product="9al", minor="10al", yld=66, ratio="91:9", stereo=">99:1", time=9, page=12,
         allene_mass=38, boronic_mass=76, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=43, isolated_ratio="91:9", product_name="(E)-2-(2-methoxyphenyl)undec-2-ene"),
    dict(entry=4, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3d", product="9ad", minor="10ad", yld=77, ratio="91:9", stereo=">99:1", time=9, page=12,
         allene_mass=38, boronic_mass=76, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=50, isolated_ratio="97:3", product_name="(E)-2-(4-methoxyphenyl)undec-2-ene"),
    dict(entry=5, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3e", product="9ae", minor="10ae", yld=67, ratio="89:11", stereo=">99:1", time=9, page=12,
         allene_mass=38, boronic_mass=84, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=46, isolated_ratio="93:7", product_name="(E)-2-(3-nitrophenyl)undec-2-ene"),
    dict(entry=6, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3g", product="9ag", minor="10ag", yld=62, ratio="93:7", stereo=">99:1", time=9, page=12,
         allene_mass=38, boronic_mass=82, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=42, isolated_ratio=None, product_name="(E)-2-(4-acetylphenyl)undec-2-ene", pure_main=True),
    dict(entry=7, r1="(CH2)7Me", allene="8a", allene_name="alkyl-substituted allene 8a (R1 = (CH2)7Me)", allene_smiles="C=C=CCCCCCCCC", boronic="3h", product="9ah", minor="10ah", yld=74, ratio="90:10", stereo=">99:1", time=9, page=12,
         allene_mass=38, boronic_mass=86, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=52, isolated_ratio="92:8", product_name="(E)-2-(1-naphthyl)undec-2-ene"),
    dict(entry=8, r1="(CH2)11Me", allene="8b", allene_name="alkyl-substituted allene 8b (R1 = (CH2)11Me)", allene_smiles="C=C=CCCCCCCCCCCCC", boronic="3a", product="9ba", minor="10ba", yld=50, ratio="92:8", stereo=">99:1", time=9, page=12,
         allene_mass=52, boronic_mass=61, boronic_mmol=0.50, pd_mass=29, pd_mmol=0.025, product_mass=36, isolated_ratio="93:7", product_name="(E)-2-phenylpentadec-2-ene"),
    dict(entry=9, r1="(CH2)15Me", allene="8c", allene_name="alkyl-substituted allene 8c (R1 = (CH2)15Me)", allene_smiles="C=C=CCCCCCCCCCCCCCCCC", boronic="3d", product="9cd", minor="10cd", yld=34, ratio="93:7", stereo=">99:1", time=9),
    dict(entry=10, r1="Cy", allene="8d", allene_name="alkyl-substituted allene 8d (R1 = Cy)", allene_smiles="C=C=CC1CCCCC1", boronic="3d", product="9dd", minor="10dd", yld=44, ratio="88:12", stereo=">99:1", time=9),
    dict(entry=11, r1="Bn", allene="8e", allene_name="alkyl-substituted allene 8e (R1 = Bn)", allene_smiles="C=C=CCc1ccccc1", boronic="3d", product="9ed", minor="10ed", yld=76, ratio=">93:7", stereo="95:5", time=6),
]

table7_ids = []
for row in table7:
    rid = f"table7_entry{row['entry']}_{row['product']}"
    table7_ids.append(f"{DOC}:{rid}")
    evidence = e7 + (ev(row["page"]) if row.get("page") else [])
    bname, bsmiles = BORONIC[row["boronic"]]
    allene_amounts = [qty("amount", 0.25, "mmol", e7)]
    boronic_amounts = [qty("equivalents", 2.0, "equiv", e7)]
    pd_amounts = [qty("catalyst_loading", 10, "mol%", e7)]
    acoh_amounts = [qty("loading", 100, "mol%", e7)]
    solvent_amounts = [field("volume", None, [])]
    if row.get("page"):
        detail_ev = ev(row["page"])
        allene_amounts += [qty("mass", row["allene_mass"], "mg", detail_ev)]
        boronic_amounts += [qty("mass", row["boronic_mass"], "mg", detail_ev), qty("amount", row["boronic_mmol"], "mmol", detail_ev)]
        pd_amounts += [qty("mass", row["pd_mass"], "mg", detail_ev), qty("amount", row["pd_mmol"], "mmol", detail_ev)]
        acoh_amounts += [qty("volume", 14, "uL", detail_ev), qty("amount", 0.24, "mmol", detail_ev)]
        solvent_amounts = [qty("volume", 3, "mL", detail_ev)]
    prefix = rid
    parts = [
        participant(f"{prefix}_allene", "reactant", row["allene"], row["allene_name"], evidence, allene_amounts, row["allene_smiles"]),
        participant(f"{prefix}_boronic", "reactant", row["boronic"], bname, evidence, boronic_amounts, bsmiles),
        participant(f"{prefix}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence, pd_amounts),
        participant(f"{prefix}_acoh", "reagent", "AcOH", "acetic acid", evidence, acoh_amounts, "CC(=O)O"),
        participant(f"{prefix}_dioxane", "solvent", "dioxane", "1,4-dioxane", evidence, solvent_amounts, "C1COCCO1"),
        participant(f"{prefix}_e9", "product", f"(E)-{row['product']}", row.get("product_name", f"reported (E)-alkene {row['product']}"), evidence),
        participant(f"{prefix}_z9", "product", f"(Z)-{row['product']}", f"reported (Z)-alkene {row['product']}", evidence),
        participant(f"{prefix}_10", "product", row["minor"], f"reported regioisomer {row['minor']}", evidence),
    ]
    conditions = [
        field("temperature", "reflux", e7),
        field("time", {"number": row["time"], "unit": "h"}, e7),
        field("atmosphere", "N2", ev(6) if not row.get("page") else ev(row["page"])),
        field("workup", "solvent evaporated to dryness; crude mixture analyzed by 1H NMR" if row.get("page") else None, ev(row["page"]) if row.get("page") else []),
        field("purification", "flash chromatography on silica gel with petroleum ether" if row.get("page") else None, ev(row["page"]) if row.get("page") else []),
    ]
    outcomes = [
        field("combined_isolated_yield_9_and_10", {"number": row["yld"], "unit": "%"}, e7,
              [f"{prefix}_e9", f"{prefix}_z9", f"{prefix}_10"]),
        field("crude_regioisomer_ratio_9_to_10", row["ratio"], e7, [f"{prefix}_e9", f"{prefix}_z9", f"{prefix}_10"]),
        field("crude_stereoisomer_ratio_E_9_to_Z_9", row["stereo"], e7, [f"{prefix}_e9", f"{prefix}_z9"]),
        field("yield_measurement_basis", "isolated yield", e7),
        field("selectivity_measurement_basis", "1H NMR (300 MHz) analysis of the crude reaction mixture after evaporation", e7),
    ]
    unresolved = ["Reflux is qualitative because no numerical temperature is reported.", "Product/regioisomer structures and stereochemical SMILES remain unverified."]
    notes = []
    if row.get("page"):
        detail_ev = ev(row["page"])
        outcomes.append(field("isolated_product_mass", {"number": row["product_mass"], "unit": "mg"}, detail_ev,
                              [f"{prefix}_e9"] if row.get("pure_main") else [f"{prefix}_e9", f"{prefix}_10"]))
        if row.get("isolated_ratio"):
            outcomes.append(field("isolated_mixture_ratio_E_9_to_10", row["isolated_ratio"], detail_ev, [f"{prefix}_e9", f"{prefix}_10"]))
        if row.get("pure_main"):
            outcomes.append(field("detailed_paragraph_isolated_yield_E_9", {"number": row["yld"], "unit": "%"}, detail_ev, [f"{prefix}_e9"]))
            unresolved.append("Table 7 defines the yield as combined 9+10 and states that isomers could not be separated, whereas the page-12 paragraph says pure (E)-9ag was isolated; both claims are retained.")
    else:
        unresolved.append("Dioxane volume, workup, and purification are not reported on page 7 for this row.")
    records.append(base_record(rid, "substrate_scope_entry", evidence, parts,
                               [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
                               outcomes, notes=notes, unresolved=unresolved))


# Page 8, Table 8: eight independent aryl-allene scope entries.
e8 = ev(8)
table8 = [
    (1, "Ph", "11a", "3a", "12aa", 41, 5),
    (2, "Ph", "11a", "3b", "12ab", 73, 5),
    (3, "Ph", "11a", "3d", "12ad", 79, 5),
    (4, "Ph", "11a", "3g", "12ag", 44, 5),
    (5, "Ph", "11a", "3h", "12ah", 87, 5),
    (6, "4-MeOC6H4", "11b", "3d", "12bd", 60, 5),
    (7, "4-t-BuC6H4", "11c", "3d", "12cd", 66, 2),
    (8, "4-AcC6H4", "11d", "3d", "12dd", 62, 2),
]
table8_ids = []
for entry, ar, allene, boronic, product, yld, hours in table8:
    rid = f"table8_entry{entry}_{product}"
    table8_ids.append(f"{DOC}:{rid}")
    bname, bsmiles = BORONIC[boronic]
    prefix = rid
    parts = [
        participant(f"{prefix}_allene", "reactant", allene, f"aryl-substituted allene {allene} (Ar = {ar})", e8,
                    [qty("amount", 0.25, "mmol", e8)]),
        participant(f"{prefix}_boronic", "reactant", boronic, bname, e8,
                    [qty("equivalents", 2.0, "equiv", e8)], bsmiles),
        participant(f"{prefix}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e8,
                    [qty("catalyst_loading", 10, "mol%", e8)]),
        participant(f"{prefix}_acoh", "reagent", "AcOH", "acetic acid", e8,
                    [qty("loading", 100, "mol%", e8)], "CC(=O)O"),
        participant(f"{prefix}_dioxane", "solvent", "dioxane", "1,4-dioxane", e8,
                    [field("volume", None, [])], "C1COCCO1"),
        participant(f"{prefix}_e12", "product", f"(E)-{product}", f"reported (E)-alkene {product}", e8),
        participant(f"{prefix}_z12", "product", f"(Z)-{product}", f"reported (Z)-alkene {product}", e8),
        participant(f"{prefix}_13", "product", product.replace("12", "13", 1), f"reported regioisomer of {product}", e8),
    ]
    records.append(base_record(
        rid, "substrate_scope_entry", e8, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", "reflux", e8), field("time", {"number": hours, "unit": "h"}, e8),
            field("atmosphere", "N2", e8), field("workup", None, []), field("purification", None, []),
        ]}],
        [
            field("isolated_yield_E_12", {"number": yld, "unit": "%"}, e8, [f"{prefix}_e12"]),
            field("regioisomer_ratio_12_to_13", ">99:1", e8, [f"{prefix}_e12", f"{prefix}_z12", f"{prefix}_13"]),
            field("stereoisomer_ratio_E_12_to_Z_12", ">99:1", e8, [f"{prefix}_e12", f"{prefix}_z12"]),
            field("yield_measurement_basis", "isolated yield", e8),
            field("selectivity_measurement_basis", "1H NMR (300 MHz) analysis of the crude reaction mixture after evaporation", e8),
        ],
        unresolved=[
            "Dioxane volume, workup, and purification are not reported on page 8.",
            "Reflux is qualitative because no numerical temperature is reported.",
            "Product/regioisomer connectivity and stereochemical SMILES remain unverified.",
        ],
    ))


# Exact page coverage.  Each page has at least one region backed by its own
# original page-image evidence.
def rid(suffix):
    return f"{DOC}:{suffix}"


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 7, reaction drawing, 11 rows, and footnotes", "finding": "All 11 alkyl-allene substrate-scope rows extracted independently; the 6 h footnote applies only to entry 11, and combined yield/selectivity fields retain the table definitions.", "evidence_ids": ev(7)},
                {"region": "lower-left exact preparation of 2c", "finding": "One compound-specific oxidation/isolation experiment extracted with quantities, 100 °C/0.5 h, workup, chromatography, product mass, and 53% isolated yield.", "evidence_ids": ev(7)},
                {"region": "lower-center/right Conditions-A procedures", "finding": "The detailed 4aa procedure and 4ab preparation were merged into their existing Table 4 records rather than duplicated.", "evidence_ids": ev(7)},
            ],
            "record_ids": table7_ids + [rid("preparation_2c_oxidation_1c"), rid("optimized_2a_3a_conditions_A"), rid("table4_entry2_4ab")],
            "unresolved": ["Table 7 gives qualitative reflux temperatures.", "Table 7 entries 9–11 lack detailed workup/purification within pages 7–12.", "Complex product/regioisomer structures remain unverified."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "upper Table 8, reaction drawing, eight rows, and footnotes", "finding": "All eight aryl-allene scope rows extracted independently; the 2 h footnote applies only to entries 7–8.", "evidence_ids": ev(8)},
                {"region": "lower experimental paragraphs", "finding": "Continuation/characterization of 4ab and exact preparations of 4ac, 4ad, and 4ae were linked to existing Table 4 rows; no duplicate reactions were created.", "evidence_ids": ev(8)},
            ],
            "record_ids": table8_ids + [rid("table4_entry2_4ab"), rid("table4_entry3_4ac"), rid("table4_entry4_4ad"), rid("table4_entry5_4ae")],
            "unresolved": ["Table 8 omits dioxane volume, workup, and purification.", "Reflux temperatures are qualitative.", "Complex products remain structurally unverified."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "two-column experimental paragraphs", "finding": "Characterization continuation for 4ae and exact preparations of 4af, 4ag, 4ah, 4ai, 4aj, and 4ba were merged into their existing Table 4 rows.", "evidence_ids": ev(9)},
            ],
            "record_ids": [rid(x) for x in ["table4_entry5_4ae", "table4_entry6_4af", "table4_entry7_4ag", "table4_entry8_4ah", "table4_entry9_4ai", "table4_entry10_4aj", "table4_entry11_4ba"]],
            "unresolved": ["Product/regioisomer connectivity and stereochemical SMILES remain unverified."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "left and right experimental columns", "finding": "4ba characterization continuation and exact preparations of 4ca, 6aa, 6ab, 6ac, 6ad, and 6ae were merged into existing Table 4/Table 5 records.", "evidence_ids": ev(10)},
            ],
            "record_ids": [rid(x) for x in ["table4_entry11_4ba", "table4_entry12_4ca", "table5_entry1_6aa", "table5_entry2_6ab", "table5_entry3_6ac", "table5_entry4_6ad", "table5_entry5_6ae"]],
            "unresolved": ["Complex sulfone/sulfoxide product structures and stereochemistry remain unverified."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "upper/left sulfoxide experimental paragraphs", "finding": "Exact preparations of 6ag, 6ah, 6ak, and 6aj were merged into existing Table 5 rows; the immediate H2O recrystallization instruction for 3h was structured.", "evidence_ids": ev(11)},
                {"region": "right-column Conditions-B typical procedure and 9ab paragraph", "finding": "Detailed quantities, nitrogen/reflux procedure, evaporation, NMR analysis, flash chromatography, product masses, and post-purification ratios were merged into Table 7 entries 1 and 2.", "evidence_ids": ev(11)},
            ],
            "record_ids": [rid(x) for x in ["table5_entry6_6ag", "table5_entry7_6ah", "table5_entry8_6ak", "table5_entry9_6aj", "table7_entry1_9aa", "table7_entry2_9ab"]],
            "unresolved": ["The 6ak paragraph prints (E)-6al in the isolation sentence, conflicting with its heading and ratios.", "Reflux temperature remains qualitative.", "Complex structures remain unverified."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "two-column Conditions-B compound paragraphs", "finding": "Exact preparations for 9al, 9ad, 9ae, 9ag, 9ah, and 9ba were merged into Table 7 entries 3–8 with quantities, product masses, and isolated-mixture ratios where reported.", "evidence_ids": ev(12)},
            ],
            "record_ids": [rid(x) for x in ["table7_entry3_9al", "table7_entry4_9ad", "table7_entry5_9ae", "table7_entry6_9ag", "table7_entry7_9ah", "table7_entry8_9ba"]],
            "unresolved": ["Table 7 defines entry 6 as a combined 9ag+10ag yield under a general inseparability footnote, while the detailed paragraph says pure (E)-9ag was isolated.", "Reflux temperature remains qualitative.", "Complex product/regioisomer structures remain unverified."],
        },
    ],
}


raw_dir = OUT / "raw_model"
raw_dir.mkdir(parents=True, exist_ok=True)
(raw_dir / "records_pages_0007_0012.json").write_text(json.dumps(records, ensure_ascii=False, indent=2))
coverage_dir = OUT / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0007_0012.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id", "").endswith(":text"):
        page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
        if 7 <= page <= 12:
            task["state"] = "attempted"
            task["reason"] = "Original page image and text inspected; page-level extraction attempted for this session."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({
    "submitted_records": len(records),
    "new_records": 20,
    "replacements": len(records) - 20,
    "coverage_pages": [page["page"] for page in coverage["pages"]],
}, ensure_ascii=False, indent=2))
