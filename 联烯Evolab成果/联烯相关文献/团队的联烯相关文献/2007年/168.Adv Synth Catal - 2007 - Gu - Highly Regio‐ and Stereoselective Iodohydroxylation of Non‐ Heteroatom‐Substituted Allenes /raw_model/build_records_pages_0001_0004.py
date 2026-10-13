#!/usr/bin/env python3
"""Build source-linked machine records for Gu et al., Adv. Synth. Catal. 2007, PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_b324560c10c6f9bc"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(page, kinds=("text", "image")):
    return [f"{DOC}:page{page}:{kind}" for kind in kinds]


P1, P2, P3, P4 = ev(1), ev(2), ev(3), ev(4)


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=(), targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(suffix, source_id, kind, evidence, participants=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": list(participants),
        "steps": list(steps),
        "outcomes": list(outcomes),
        "notes": [fact(note, note_ev) for note, note_ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def step(step_id, participant_ids, conditions):
    return {"step_id": step_id, "participant_ids": list(participant_ids), "conditions": list(conditions)}


records = []

# Page-1 cited prior work. These are deliberately literature_example records, not present-paper experiments.
records.append(record(
    "literature_phenylallene_bromination_meoh", "Introduction ref. 4, MeOH condition", "literature_example", P1,
    participants=[
        participant("lit4_phallene_meoh", "reactant", "phenylallene", P1, smiles="C=C=Cc1ccccc1"),
        participant("lit4_br2_meoh", "reagent", "Br2", P1, smiles="BrBr"),
        participant("lit4_meoh", "solvent", "MeOH", P1, smiles="CO"),
        participant("lit4_product_a", "product", "3-methoxy-3-phenyl-2-bromo-1-propene", P1),
        participant("lit4_product_b", "product", "1-methoxy-3-phenyl-2-bromo-2-propene", P1),
    ],
    outcomes=[field("product_ratio", "84:16", P1, ["lit4_product_a", "lit4_product_b"])],
    unresolved=["Cited prior-work procedure details and product structures were not supplied in this paper."],
))
records.append(record(
    "literature_phenylallene_bromination_nonpolar", "Introduction ref. 4, non-polar-solvent condition", "literature_example", P1,
    participants=[
        participant("lit4_phallene_nonpolar", "reactant", "phenylallene", P1, smiles="C=C=Cc1ccccc1"),
        participant("lit4_br2_nonpolar", "reagent", "Br2", P1, smiles="BrBr"),
        participant("lit4_nonpolar_solvent", "solvent", "CS2, CH2Cl2, etc.", P1),
        participant("lit4_dibromide", "product", "1-phenyl-2,3-dibromo-1-propene (Z/E mixture)", P1),
    ],
    outcomes=[field("reported_yield", {"number": 98, "unit": "%"}, P1, ["lit4_dibromide"]), field("stereoisomeric_result", "Z/E mixture", P1, ["lit4_dibromide"])],
    unresolved=["The Z/E ratio, exact non-polar solvent, and full procedure are not stated in the present paper."],
))
records.append(record(
    "literature_23pentadiene_iodomethoxylation", "Introduction ref. 5", "literature_example", P1,
    participants=[
        participant("lit5_pentadiene", "reactant", "2,3-pentadiene", P1, smiles="CC=C=CC"),
        participant("lit5_product", "product", "3-iodo-4-methoxy-2-pentene", P1),
    ],
    outcomes=[field("Z_E_ratio", "9:1", P1, ["lit5_product"])],
    unresolved=["The electrophile, solvent, yield, and procedure are not fully stated in the present paper."],
))
records.append(record(
    "literature_23pentadiene_methoxymercuration", "Introduction ref. 6", "literature_example", P1,
    participants=[participant("lit6_pentadiene", "reactant", "2,3-pentadiene", P1, smiles="CC=C=CC"), participant("lit6_products", "product", "methoxymercuration Z/E products", P1)],
    outcomes=[field("stereoisomeric_result", "mixture of Z/E isomers", P1, ["lit6_products"])],
    unresolved=["Product identities, ratio, yield, and conditions are not stated in the present paper."],
))
records.append(record(
    "literature_phenylallene_sulfenyl_chloride", "Introduction ref. 7", "literature_example", P1,
    participants=[
        participant("lit7_phallene", "reactant", "phenylallene", P1, smiles="C=C=Cc1ccccc1"),
        participant("lit7_reagent", "reagent", "2,4-dinitrobenzenesulfenyl chloride", P1),
        participant("lit7_product", "product", "3-phenyl-2-arylthio-2(Z)-propenyl chloride", P1),
    ],
    outcomes=[field("stereoselectivity", "Z product exclusively", P1, ["lit7_product"])],
    unresolved=["Yield and detailed conditions are not stated in the present paper."],
))
records.append(record(
    "literature_23pentadiene_iodine_azide", "Introduction ref. 8", "literature_example", P1,
    participants=[
        participant("lit8_pentadiene", "reactant", "2,3-pentadiene", P1, smiles="CC=C=CC"),
        participant("lit8_in3", "reagent", "IN3", P1),
        participant("lit8_acetonitrile", "solvent", "CH3CN", P1, smiles="CC#N"),
        participant("lit8_product", "product", "3-iodo-4-azido-2(Z)-pentene", P1),
    ],
    outcomes=[field("reported_yield", {"number": 80, "unit": "%"}, P1, ["lit8_product"]), field("stereoselectivity", "Z product exclusively", P1, ["lit8_product"])],
    unresolved=["Reaction time, temperature, atmosphere, and workup are not stated in the present paper."],
))

# Scheme 1 contains two generic mechanistic precedents; Scheme 2 is the proposed mechanism for this work.
records.append(record(
    "scheme1_sulfoxide_mechanism", "Scheme 1, upper pathway", "mechanism", P1 + P2,
    participants=[participant("scheme1_sulfoxide", "reactant", "generic 1,2-allenyl sulfoxide", P2), participant("scheme1_i2", "reagent", "I2", P2, smiles="II"), participant("scheme1_lioac", "reagent", "LiOAc", P2), participant("scheme1_acetonitrile", "solvent", "CH3CN", P2, name="acetonitrile", smiles="CC#N"), participant("scheme1_water", "solvent", "H2O", P2, name="water", smiles="O"), participant("scheme1_e_product", "product", "generic E-halohydroxylation product", P2)],
    notes=[("The paper attributes E selectivity to oxygen participation through five-membered intermediate B.", P1 + P2)],
    unresolved=["This is a generic prior-work mechanism, not a row-level experiment; R groups and experimental quantities are unspecified."],
))
records.append(record(
    "scheme1_sulfide_selenide_mechanism", "Scheme 1, lower pathway", "mechanism", P1 + P2,
    participants=[participant("scheme1_chalcogen_allene", "reactant", "generic sulfide- or selenide-substituted allene", P2), participant("scheme1_xplus", "reagent", "X+ electrophile", P2), participant("scheme1_water_lower", "reagent", "H2O", P2, smiles="O"), participant("scheme1_z_product", "product", "generic Z-halohydroxylation product", P2)],
    notes=[("The paper attributes Z selectivity to soft Lewis acid-base interaction between X+ and S or Se in intermediate D.", P1 + P2)],
    unresolved=["This is a generic prior-work mechanism, not a row-level experiment; X, R groups, and quantities are unspecified."],
))
records.append(record(
    "scheme2_proposed_iodohydroxylation_mechanism", "Scheme 2", "mechanism", P1 + P2,
    participants=[participant("scheme2_allene_1", "reactant", "generic furanone-substituted allene 1", P2), participant("scheme2_i2", "reagent", "I2", P2, smiles="II"), participant("scheme2_water", "reagent", "H2O", P2, smiles="O"), participant("scheme2_z2", "product", "generic Z-2 iodohydroxylation product", P2), participant("scheme2_e2", "product", "generic E-2 iodohydroxylation product (disfavored path)", P2)],
    notes=[
        ("The proposed favored path proceeds through iodonium-like intermediate 3 and trans attack of water to Z-2.", P1 + P2),
        ("The alternative path through 4 and 6 is depicted as sterically hindered and leads to E-2.", P1 + P2),
    ],
    unresolved=["Scheme 2 is a proposed generic mechanism; intermediates 3-6 are not isolated experiments and R groups are generic."],
))


solvent_info = {
    "CH3CN": ("acetonitrile", "CC#N"),
    "CH3NO2": ("nitromethane", "C[N+](=O)[O-]"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "CH2Cl2": ("dichloromethane", "ClCCl"),
}


def common_1a_participants(rec_prefix, evidence, solvent, iodine_equiv, include_z7=True):
    solvent_name, solvent_smiles = solvent_info[solvent]
    parts = [
        participant(f"{rec_prefix}_1a", "reactant", "1a", evidence, name="3-propyl-4-(3-methylbuta-1,2-dienyl)-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(CCC)=C1C=C=C(C)C", amounts=[field("reaction_scale", {"minimum": 0.15, "maximum": 0.25, "unit": "mmol", "raw_text": "0.15-0.25 mmol"}, P3)]),
        participant(f"{rec_prefix}_i2", "reagent", "I2", evidence, smiles="II", amounts=[field("equivalents", {"number": iodine_equiv, "unit": "equiv"}, P3)]),
        participant(f"{rec_prefix}_solvent", "solvent", solvent, evidence, name=solvent_name, smiles=solvent_smiles),
        participant(f"{rec_prefix}_water", "solvent", "H2O", evidence, name="water", smiles="O"),
        participant(f"{rec_prefix}_z2a", "product", "Z-2a", evidence, name="4-[3-hydroxy-2-iodo-3-methylbut-1(Z)-enyl]-3-propyl-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(CCC)=C1/C=C(\\I)C(O)(C)C"),
    ]
    if include_z7:
        parts.append(participant(f"{rec_prefix}_z7a", "product", "Z-7a", evidence, name="Ritter-type iodoamidation product"))
    return parts


table1 = [
    (1, "CH3CN", "5:1", 4.0, 1.0, 54, 13, "open air"),
    (2, "CH3CN", "5:1", 4.0, 1.0, 59, 4, "argon"),
    (3, "CH3NO2", "5:1", 4.0, 1.0, 71, "table dash (–)", "argon"),
    (4, "THF", "5:1", 4.0, 1.0, 69, "table dash (–)", "argon"),
    (5, "CH2Cl2", "5:1", 4.0, 4.0, 44, "table dash (–)", "argon"),
    (6, "CH3NO2", "5:1", 2.0, 1.0, 74, "table dash (–)", "argon"),
    # Entry 7 is emitted below together with Table 2 entry 1 and the detailed typical procedure.
    (8, "CH3NO2", "10:1", 1.5, 1.0, 72, "table dash (–)", "argon"),
    (9, "CH3NO2", "3:1", 1.5, 1.0, 69, "table dash (–)", "argon"),
]

for entry, solvent, ratio, equiv, hours, z2_yield, z7_value, atmosphere in table1:
    prefix = f"t1e{entry}"
    evidence = P3 + (P1 + P2 if entry == 1 else P2)
    parts = common_1a_participants(prefix, evidence, solvent, equiv)
    z2 = f"{prefix}_z2a"
    z7 = f"{prefix}_z7a"
    outcomes = [
        field("table_isolated_yield_Z_2a", {"number": z2_yield, "unit": "%"}, P3, [z2]),
        field("yield_measurement_basis", "isolated", P3, [z2]),
    ]
    if isinstance(z7_value, int):
        outcomes += [field("isolated_yield_Z_7a", {"number": z7_value, "unit": "%"}, P3, [z7]), field("yield_measurement_basis_Z_7a", "isolated", P3, [z7])]
    else:
        outcomes.append(field("Z_7a_table_source_marker", z7_value, P3, [z7]))
    unresolved = ["No supporting-information file was supplied or explicitly associated.", "Workup and purification are not stated for this optimization row.", "Complex participant structures remain machine-unverified."]
    if entry == 1:
        outcomes.append(field("narrative_yield_Z_2a", {"number": 51, "unit": "%"}, P2, [z2]))
        outcomes.append(field("stereoselectivity", "Z-2a was the only stereoisomer", P2, [z2]))
        unresolved.append("Source conflict: page-2 prose reports 51% Z-2a, while Table 1 entry 1 reports 54% isolated Z-2a.")
    if isinstance(z7_value, str):
        unresolved.append("The Table 1 dash for Z-7a is preserved as printed because the source does not define it as zero or not detected.")
    rec = record(
        f"table1_entry{entry}", f"Table 1 entry {entry}", "optimization_entry", evidence,
        participants=parts,
        steps=[step("reaction", [p["entity_id"] for p in parts[:4]], [
            field("solvent", f"{solvent}/H2O = {ratio}", P3),
            field("temperature", "r.t.", P3),
            field("atmosphere", atmosphere, P3),
            field("time", {"number": hours, "unit": "h"}, P3),
            field("workup", None),
            field("purification", None),
        ])],
        outcomes=outcomes,
        unresolved=unresolved,
    )
    records.append(rec)


# The identical optimized/scope experiment is reported as Table 1 entry 7, Table 2 entry 1, and the typical procedure.
merged_ev = P2 + P3 + P4
parts = [
    participant("merged_1a", "reactant", "1a", merged_ev, name="3-propyl-4-(3-methylbuta-1,2-dienyl)-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(CCC)=C1C=C=C(C)C", amounts=[field("mass", {"number": 63, "unit": "mg"}, P3), field("amount", {"number": 0.24, "unit": "mmol"}, P3)]),
    participant("merged_i2", "reagent", "I2", merged_ev, smiles="II", amounts=[field("mass", {"number": 90, "unit": "mg"}, P3), field("amount", {"number": 0.35, "unit": "mmol"}, P3), field("equivalents", {"number": 1.5, "unit": "equiv"}, P3)]),
    participant("merged_ch3no2", "solvent", "CH3NO2", merged_ev, name="nitromethane", smiles="C[N+](=O)[O-]", amounts=[field("volume", {"number": 4, "unit": "mL"}, P3)]),
    participant("merged_water", "solvent", "H2O", merged_ev, name="water", smiles="O", amounts=[field("volume", {"number": 0.8, "unit": "mL"}, P3)]),
    participant("merged_z2a", "product", "Z-2a", merged_ev, name="4-[3-hydroxy-2-iodo-3-methylbut-1(Z)-enyl]-3-propyl-5-phenyl-2(5H)-furanone", smiles="O=C1OC(c2ccccc2)C(CCC)=C1/C=C(\\I)C(O)(C)C"),
    participant("merged_na2s2o3", "reagent", "saturated aqueous Na2S2O3", P4),
    participant("merged_ether", "solvent", "ether", P4, name="diethyl ether", smiles="CCOCC"),
    participant("merged_wash_water", "solvent", "water wash", P4, name="water", smiles="O"),
    participant("merged_brine", "reagent", "brine", P4),
    participant("merged_na2so4", "reagent", "Na2SO4", P4, name="sodium sulfate", smiles="[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
    participant("merged_petroleum_ether", "solvent", "petroleum ether", P4),
    participant("merged_ethyl_acetate", "solvent", "ethyl acetate", P4, smiles="CCOC(C)=O"),
]
records.append(record(
    "table1_entry7_table2_entry1_typical_z2a", "Table 1 entry 7 / Table 2 entry 1 / Typical procedure", "reported_experiment", merged_ev,
    participants=parts,
    steps=[
        step("reaction", ["merged_1a", "merged_i2", "merged_ch3no2", "merged_water"], [field("solvent", "CH3NO2/H2O = 5:1", P3), field("atmosphere", "argon", P3), field("temperature", "room temperature", P3), field("time", {"number": 1, "unit": "h"}, P3)]),
        step("quench_and_extraction", ["merged_na2s2o3", "merged_ether"], [field("workup", "treated with saturated aqueous Na2S2O3, then extracted with ether", P4)]),
        step("washing_and_drying", ["merged_wash_water", "merged_brine", "merged_na2so4"], [field("workup", "organic layer washed with water and brine, then dried over Na2SO4", P4)]),
        step("evaporation", [], [field("operation", "evaporation", P4)]),
        step("flash_chromatography", ["merged_petroleum_ether", "merged_ethyl_acetate"], [field("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate = 10:1", P4)]),
    ],
    outcomes=[
        field("isolated_yield_Z_2a", {"number": 77, "unit": "%"}, P3 + P4, ["merged_z2a"]),
        field("product_mass", {"number": 75, "unit": "mg"}, P4, ["merged_z2a"]),
        field("yield_measurement_basis", "isolated after flash chromatography", P4, ["merged_z2a"]),
        field("product_physical_form", "oil", P4, ["merged_z2a"]),
        field("stereoselectivity", "Z-2a; only stereoisomer reported", P2 + P3, ["merged_z2a"]),
    ],
    notes=[("Page 4 reports 1H NMR, 13C NMR, ESI-MS, IR, and HRMS characterization for Z-2a.", P4)],
    unresolved=["No supporting-information file was supplied or explicitly associated.", "The candidate substrate/product SMILES and alkene stereochemical encoding remain machine-unverified."],
))


scope_rows = [
    # entry 1 is the merged record above
    (2, "Ph", "H", "Me", "Me", "Me", "1b", 12.5, 80, "Z-2b"),
    (3, "Ph", "H", "Et", "Me", "Me", "1c", 9.5, 78, "Z-2c"),
    (4, "Ph", "H", "i-C4H9", "Me", "Me", "1d", 4.0, 70, "Z-2d"),
    (5, "Ph", "H", "Allyl", "Me", "Me", "1e", 4.0, 70, "Z-2e"),
    (6, "Ph", "H", "Me", "Et", "Et", "1f", 51.0, 62, "Z-2f"),
    (7, "Ph", "Me", "H", "Me", "Me", "1g", 12.0, 76, "Z-2g"),
    (8, "Ph", "Et", "H", "Me", "Me", "1h", 1.0, 76, "Z-2h"),
    (9, "Ph", "Et", "Me", "Me", "Me", "1i", 4.0, 75, "Z-2i"),
    (10, "p-Br-C6H4", "H", "Allyl", "Me", "Me", "1j", 11.0, 49, "Z-2j"),
    (11, "Me", "Me", "Me", "Ph", "Me", "1k", 11.0, 61, "Z-2k"),
    (12, "Me", "Me", "Allyl", "Me", "Me", "1l", 11.0, 65, "Z-2l"),
]

for entry, r1, r2, r3, r4, r5, substrate_label, hours, yield_pct, product_label in scope_rows:
    prefix = f"t2e{entry}"
    entry_ev = P3 + (P2 if entry in (6, 11) else []) + (P4 if entry == 11 else [])
    iodine_equiv = 3.0 if entry == 6 else 1.5
    substrate_smiles = "O=C1OC(C)(C)C(C)=C1C=C=C(C)c1ccccc1" if entry == 11 else None
    product_smiles = "O=C1OC(C)(C)C(C)=C1/C=C(\\I)C(O)(C)c1ccccc1" if entry == 11 else None
    substrate = f"{prefix}_substrate"
    product = f"{prefix}_product"
    parts = [
        participant(substrate, "reactant", substrate_label, P3, name=f"Table 2 substrate with R1={r1}, R2={r2}, R3={r3}, R4={r4}, R5={r5}", smiles=substrate_smiles, amounts=[field("reaction_scale", {"minimum": 0.15, "maximum": 0.30, "unit": "mmol", "raw_text": "0.15-0.30 mmol"}, P3)]),
        participant(f"{prefix}_i2", "reagent", "I2", P3, smiles="II", amounts=[field("equivalents", {"number": iodine_equiv, "unit": "equiv"}, P3)]),
        participant(f"{prefix}_ch3no2", "solvent", "CH3NO2", P3, name="nitromethane", smiles="C[N+](=O)[O-]", amounts=[field("volume", {"number": 4, "unit": "mL"}, P3)]),
        participant(f"{prefix}_water", "solvent", "H2O", P3, name="water", smiles="O", amounts=[field("volume", {"number": 0.8, "unit": "mL"}, P3)]),
        participant(product, "product", product_label, P3, name=f"Z-2 product from {substrate_label} (R1={r1}, R2={r2}, R3={r3}, R4={r4}, R5={r5})", smiles=product_smiles),
    ]
    notes = []
    unresolved = ["No supporting-information file was supplied or explicitly associated.", "Workup and purification are not stated for this scope row.", "The Table 2 yield measurement basis is not explicitly stated.", "Complex participant connectivity and product stereochemistry remain machine-unverified."]
    if entry == 6:
        notes.append(("Table 2 footnote b overrides the common iodine loading; the row-specific value is stored on the I2 participant.", P3))
    if entry == 11:
        notes += [("The product assignment was further supported by NOE and X-ray diffraction studies of Z-2k.", P2 + P4), ("Page 4 reports crystal data and CCDC 642223 for Z-2k.", P4)]
        unresolved.append("The tentative 1k/Z-2k SMILES were generated from the table substituents and remain unverified despite the reported X-ray assignment.")
    records.append(record(
        f"table2_entry{entry}", f"Table 2 entry {entry}", "substrate_scope_entry", entry_ev,
        participants=parts,
        steps=[step("reaction", [p["entity_id"] for p in parts[:4]], [field("solvent", "CH3NO2/H2O = 5:1", P3), field("atmosphere", "argon", P3), field("temperature", "r.t.", P3), field("time", {"number": hours, "unit": "h"}, P3), field("workup", None), field("purification", None)])],
        outcomes=[field("reported_yield_Z_2", {"number": yield_pct, "unit": "%"}, P3, [product]), field("yield_measurement_basis", None, targets=[product])],
        notes=notes,
        unresolved=unresolved,
    ))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
