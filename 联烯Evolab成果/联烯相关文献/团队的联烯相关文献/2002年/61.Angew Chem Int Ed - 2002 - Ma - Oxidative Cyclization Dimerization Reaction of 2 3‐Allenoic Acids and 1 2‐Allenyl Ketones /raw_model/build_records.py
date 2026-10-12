#!/usr/bin/env python3
"""Build the source-derived machine extraction for PDF pages 1--4.

This is intentionally a machine submission: merge will quarantine every
record as needs_review and remove any self-certification.
"""
import json
from pathlib import Path

DOC = "doc_00ca2cd4c558966d"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"
EV2 = [P2T, P2I]
EV23 = [P2T, P2I, P3T, P3I]


def fact(value, evidence=EV2):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=EV2, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name=None, smiles=None, amounts=None, evidence=EV2):
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


def amount(name, number, unit, evidence=EV2, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return field(name, value, evidence)


def base_record(suffix, source_id, kind, evidence=EV2):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": [],
        "steps": [],
        "outcomes": [],
        "notes": [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": [],
        },
    }


SMILES = {
    "1a": "O=C(O)C(CCC)=C=Cc1ccccc1",
    "2a": "CC(=O)C=C=C",
    "2b": "CCCCC(=O)C=C=C",
    "2c": "O=C(Cc1ccccc1)C=C=C",
}

SOLVENTS = {
    "CH2Cl2": ("dichloromethane", "ClCCl"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "acetone": ("acetone", "CC(=O)C"),
    "DMA": ("N,N-dimethylacetamide", "CC(=O)N(C)C"),
    "methanol": ("methanol", "CO"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "CH3CN": ("acetonitrile", "CC#N"),
}


def substrate(label, substituents, entity_id="reactant_1", evidence=EV2, precise=False):
    name = f"2,3-allenoic acid {label} ({substituents})"
    return participant(entity_id, "reactant", label, name, SMILES.get(label) if precise else None,
                       evidence=evidence)


def ketone(label, r4, entity_id="reactant_2", evidence=EV2):
    name = f"1,2-allenyl ketone {label} (R4={r4})"
    return participant(entity_id, "reactant", label, name, SMILES.get(label), evidence=evidence)


def catalyst(evidence=EV2, mass=None):
    amounts = [amount("catalyst_loading", 5, "mol%", evidence)]
    if mass is not None:
        amounts.insert(0, amount("mass", mass, "mg", evidence))
    return participant("catalyst", "catalyst", "[PdCl2(MeCN)2]",
                       "bis(acetonitrile)palladium(II) dichloride", None, amounts, evidence)


def solvent(label, volume=3, evidence=EV2):
    name, smiles = SOLVENTS[label]
    amounts = [amount("solvent_volume", volume, "mL", evidence)] if volume is not None else []
    return participant("solvent", "solvent", label, name, smiles, amounts, evidence)


records = []

# Table 1 rows other than entry 11. Entry 11 is merged below with Table 2
# entry 1 and the typical procedure because they report the same experiment.
table1 = [
    (1, 5, "CH2Cl2", 11, 23, {"number": 14, "unit": "%"}),
    (2, 5, "THF", 11, 14, {"number": 0, "unit": "%"}),
    (3, 5, "acetone", 11, 40, {"number": 0, "unit": "%"}),
    (4, 5, "DMA", 17.5, 76, {"number": 0, "unit": "%"}),
    (5, 5, "methanol", 12, 30, "trace"),
    (6, 5, "toluene", 16.5, 13, {"number": 18, "unit": "%"}),
    (7, 1, "CH3CN", 10, 27, {"number": 30, "unit": "%"}),
    (8, 2, "CH3CN", 22, 42, {"number": 30, "unit": "%"}),
    (9, 3, "CH3CN", 11.5, 57, {"number": 12, "unit": "%"}),
    (10, 4, "CH3CN", 11, 69, {"number": 6, "unit": "%"}),
]
for entry, equiv, solv, hours, y3, y4 in table1:
    rec = base_record(f"table1_entry{entry:02d}", f"Table 1 entry {entry}", "optimization_entry")
    p1 = substrate("1a", "R1=Ph, R2=n-C3H7, R3=H", precise=True)
    p1["amounts"] = [amount("amount", 0.25, "mmol")]
    p2 = ketone("2a", "CH3")
    p2["amounts"] = [amount("equivalents", equiv, "equiv")]
    if equiv == 5:
        p2["amounts"].insert(0, amount("amount", 1.25, "mmol"))
    prod3 = participant("product_3a", "product", "3a", "4-(3-furanyl)butenolide 3a")
    prod4 = participant("product_4a", "product", "4a", "cycloisomerization furanone 4a")
    rec["participants"] = [p1, p2, catalyst(), solvent(solv), prod3, prod4]
    rec["steps"] = [{
        "step_id": "reaction",
        "participant_ids": ["reactant_1", "reactant_2", "catalyst", "solvent"],
        "conditions": [
            field("solvent", solv),
            field("reaction_temperature", None),
            field("reaction_time", {"number": hours, "unit": "h"}),
        ],
    }]
    rec["outcomes"] = [
        field("yield_3a", {"number": y3, "unit": "%"}, targets=["product_3a"]),
        field("yield_4a", y4, targets=["product_4a"]),
        field("yield_measurement_basis", None),
    ]
    rec["review"]["unresolved"] = [
        "Reaction temperature is not stated in Table 1 or its footnote.",
        "The measurement basis for the tabulated yields is not stated.",
        "Product structures were not transcribed to SMILES and all attempted structures remain unverified.",
        "Supporting information was mentioned by the paper but was not explicitly supplied or associated.",
    ]
    records.append(rec)

# One merged record for Table 1 entry 11, Table 2 entry 1, Schemes 2/4,
# and the typical procedure. It also preserves the reported side-products.
rec = base_record("standard_1a_2a_3a", "Table 1 entry 11; Table 2 entry 1; typical procedure", "reported_experiment", EV23)
p1 = substrate("1a", "R1=Ph, R2=n-C3H7, R3=H", evidence=EV23, precise=True)
p1["amounts"] = [amount("mass", 50, "mg", EV23), amount("amount", 0.248, "mmol", EV23)]
p2 = ketone("2a", "CH3", evidence=EV23)
p2["amounts"] = [amount("mass", 103, "mg", EV23), amount("amount", 1.26, "mmol", EV23), amount("equivalents", 5, "equiv", EV2)]
products = [
    participant("product_3a", "product", "3a", "4-(3-furanyl)butenolide 3a", evidence=EV23),
    participant("product_4a", "product", "4a", "cycloisomerization furanone 4a", evidence=EV2),
    participant("product_5a", "product", "5a", "homodimerization product of 2a", evidence=EV2),
    participant("product_6a", "product", "6a", "4,5-dimethyleneocta-2,7-dione", evidence=EV23),
    participant("product_7a", "product", "7a", "C=C double-bond isomer 7a of 6a", evidence=EV23),
    participant("product_8a", "product", "8a", "C=C double-bond isomer 8a of 6a", evidence=EV23),
]
rec["participants"] = [p1, p2, catalyst(EV23, 3), solvent("CH3CN", 3, EV23)] + products
rec["steps"] = [
    {
        "step_id": "reaction",
        "participant_ids": ["reactant_1", "reactant_2", "catalyst", "solvent"],
        "conditions": [field("solvent", "CH3CN", EV23), field("reaction_temperature", "room temperature", EV23), field("reaction_time", {"number": 4, "unit": "h"}, EV23), field("operation", "stirred", EV23)],
    },
    {
        "step_id": "isolation",
        "participant_ids": ["product_3a"],
        "conditions": [field("workup", "evaporation", EV23), field("purification", "silica gel chromatography; petroleum ether/diethyl ether 3:1", EV23)],
    },
]
rec["outcomes"] = [
    field("yield_3a", {"number": 90, "unit": "%"}, EV23, ["product_3a"]),
    field("product_mass_3a", {"number": 63, "unit": "mg"}, EV23, ["product_3a"]),
    field("yield_measurement_basis_3a", "pure product after silica gel chromatography", EV23, ["product_3a"]),
    field("yield_4a", {"number": 0, "unit": "%"}, EV2, ["product_4a"]),
    field("yield_5a", {"number": 13, "unit": "%"}, EV2, ["product_5a"]),
    field("yield_measurement_basis_5a", "calculated from the initial amount of 2a used", EV2, ["product_5a"]),
    field("yield_6a", {"number": 4, "unit": "%"}, EV23, ["product_6a"]),
    field("yield_7a", {"number": 23, "unit": "%"}, EV23, ["product_7a"]),
    field("yield_8a", {"number": 13, "unit": "%"}, EV23, ["product_8a"]),
    field("yield_measurement_basis_6a_8a", "calculated based on 2a (penta-3,4-dienone) used", EV23, ["product_6a", "product_7a", "product_8a"]),
    field("appearance_3a", "white solid", EV23, ["product_3a"]),
    field("melting_point_3a", {"minimum": 84, "maximum": 85, "unit": "°C", "raw_text": "84–85 °C"}, EV23, ["product_3a"]),
]
rec["notes"] = [fact("3a was recrystallized/characterized with melting-point solvent ethyl acetate/hexane; NMR, MS, IR and elemental-analysis data are reported on page 3.", EV23)]
rec["review"]["unresolved"] = [
    "The depicted product structures 3a--8a were not transcribed to SMILES; structure assignments remain for chemical review.",
    "The paper reports side-product yields but does not give separate isolation operations for 5a--8a in the supplied pages.",
    "Supporting information was mentioned by the paper but was not explicitly supplied or associated.",
]
records.append(rec)

# Table 2 scope rows except entry 1, already merged above.
scope = [
    (2, "1b", "R1=Ph, R2=PhCH2, R3=H", "2a", "CH3", 92, "3b"),
    (3, "1c", "R1=Ph, R2=CH3, R3=Et", "2a", "CH3", 85, "3c"),
    (4, "1d", "R1=Ph, R2=Allyl, R3=H", "2a", "CH3", 61, "3d"),
    (5, "1e", "R1=alpha-naphthyl, R2=n-C3H7, R3=H", "2a", "CH3", 86, "3e"),
    (6, "1f", "R1=CH3, R2=PhCH2, R3=H", "2a", "CH3", 90, "3f"),
    (7, "1g", "R1=n-C7H15, R2=H, R3=H", "2a", "CH3", 69, "3g"),
    (8, "1a", "R1=Ph, R2=n-C3H7, R3=H", "2b", "n-C4H9", 84, "3h"),
    (9, "1c", "R1=Ph, R2=CH3, R3=Et", "2b", "n-C4H9", 86, "3i"),
    (10, "1g", "R1=n-C7H15, R2=H, R3=H", "2b", "n-C4H9", 69, "3j"),
    (11, "1a", "R1=Ph, R2=n-C3H7, R3=H", "2c", "PhCH2", 74, "3k"),
    (12, "1c", "R1=Ph, R2=CH3, R3=Et", "2c", "PhCH2", 84, "3l"),
    (13, "1g", "R1=n-C7H15, R2=H, R3=H", "2c", "PhCH2", 71, "3m"),
]
for entry, acid, subs, keto, r4, yld, product_label in scope:
    rec = base_record(f"table2_entry{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry")
    p1 = substrate(acid, subs, precise=(acid == "1a"))
    p1["amounts"] = [amount("amount", 0.25, "mmol")]
    p2 = ketone(keto, r4)
    p2["amounts"] = [amount("amount", 1.25, "mmol")]
    product = participant("product", "product", product_label, f"4-(3-furanyl)butenolide {product_label}")
    rec["participants"] = [p1, p2, catalyst(), solvent("CH3CN", 3), product]
    rec["steps"] = [{
        "step_id": "reaction",
        "participant_ids": ["reactant_1", "reactant_2", "catalyst", "solvent"],
        "conditions": [field("solvent", "CH3CN"), field("reaction_temperature", "RT"), field("reaction_time", {"number": 4, "unit": "h"})],
    }]
    rec["outcomes"] = [field("yield", {"number": yld, "unit": "%"}, targets=["product"]), field("yield_measurement_basis", None)]
    rec["review"]["unresolved"] = [
        "The measurement basis for the tabulated yield is not stated.",
        "R-group-defined structures other than directly attempted 1a/2a--2c and all product structures remain without verified SMILES.",
        "Supporting information was mentioned by the paper but was not explicitly supplied or associated.",
    ]
    records.append(rec)

# Scheme 3 control under argon.
rec = base_record("scheme3_argon_control", "Scheme 3 argon control", "reported_experiment")
rec["participants"] = [
    substrate("1a", "R1=Ph, R2=n-C3H7, R3=H", precise=True),
    ketone("2a", "CH3"),
    catalyst(),
    solvent("CH3CN", None),
    participant("product_3a", "product", "3a", "4-(3-furanyl)butenolide 3a"),
]
rec["steps"] = [{"step_id": "reaction", "participant_ids": ["reactant_1", "reactant_2", "catalyst", "solvent"], "conditions": [field("solvent", "CH3CN"), field("atmosphere", "Ar"), field("reaction_temperature", "RT"), field("reaction_time", {"number": 4, "unit": "h"})]}]
rec["outcomes"] = [field("yield_3a", {"number": 90, "unit": "%"}, targets=["product_3a"]), field("yield_measurement_basis", None)]
rec["review"]["unresolved"] = [
    "Reactant quantities, solvent volume, and yield measurement basis are not reported in Scheme 3.",
    "The product structure remains without a verified SMILES.",
    "Supporting information was not explicitly supplied or associated.",
]
records.append(rec)

# Scheme 3 inhibition control with K2CO3 and Bu4NBr.
rec = base_record("scheme3_k2co3_control", "Scheme 3 K2CO3 control", "reported_experiment")
k2co3 = participant("k2co3", "reagent", "K2CO3", "potassium carbonate", "[K+].[K+].[O-]C([O-])=O", [amount("equivalents", 1, "equiv")])
tbab = participant("tbab", "reagent", "Bu4NBr", "tetrabutylammonium bromide")
rec["participants"] = [
    substrate("1a", "R1=Ph, R2=n-C3H7, R3=H", precise=True),
    ketone("2a", "CH3"), catalyst(), solvent("CH3CN", None), tbab, k2co3,
    participant("product_3a", "product", "3a", "4-(3-furanyl)butenolide 3a"),
]
rec["steps"] = [{"step_id": "reaction", "participant_ids": ["reactant_1", "reactant_2", "catalyst", "solvent", "tbab", "k2co3"], "conditions": [field("solvent", "CH3CN"), field("reaction_temperature", "RT"), field("reaction_time", {"number": 11, "unit": "h"})]}]
rec["outcomes"] = [field("yield_3a", {"number": 0, "unit": "%"}, targets=["product_3a"]), field("yield_measurement_basis", None)]
rec["notes"] = [fact("The authors interpret inhibition by potassium carbonate as evidence that in-situ HCl may be important; this interpretation is mechanistic, not an added experimental fact.")]
rec["review"]["unresolved"] = [
    "The amount and exact role of Bu4NBr are not specified in Scheme 3.",
    "Reactant quantities, solvent volume, and yield measurement basis are not reported.",
    "The product structure remains without a verified SMILES.",
    "Supporting information was not explicitly supplied or associated.",
]
records.append(rec)

out = Path(__file__).with_name("extracted_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
