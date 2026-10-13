import json
from pathlib import Path


DOC = "doc_a041da967eb86093"
P1 = [f"{DOC}:page1:image", f"{DOC}:page1:text"]
P2 = [f"{DOC}:page2:image", f"{DOC}:page2:text"]
P3 = [f"{DOC}:page3:image", f"{DOC}:page3:text"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []

# Page 1: the abstract arrow is a generic reaction class, not an individual experiment.
generic_participants = [
    participant("generic_allene_1", "reactant", "generic monoester of a 1,2-allenyl phosphonic acid (R1/R2/R3)", P1),
    participant("generic_alkene", "reactant", "generic alkene (R4/R5)", P1),
    participant("generic_product_2", "product", "generic 4-(1-Z-alkenyl)-2-ethoxy-2,5-dihydro[1,2]oxaphosphole 2-oxide", P1),
    participant("pd_catalyst_generic", "catalyst", "Pd (cat.)", P1),
    participant("cah2_generic", "reagent", "CaH2", P1, amounts=[field("reported_loading", "cat.", P1)]),
    participant("nai_generic", "reagent", "NaI", P1, amounts=[field("reported_loading", "cat.", P1)]),
    participant("oxygen_generic", "reagent", "O2", P1, smiles="O=O"),
    participant("bq_generic", "reagent", "benzoquinone (BQ)", P1, smiles="O=C1C=CC(=O)C=C1", amounts=[amount("equivalents", 1, "equiv", P1)]),
]
records.append(record(
    "page1_abstract_general_scheme", "general_scheme", P1, generic_participants,
    [{"step_id": "generic_cyclization_heck", "participant_ids": [p["entity_id"] for p in generic_participants if p["role"] != "product"],
      "conditions": [
          field("operation", "Pd-catalyzed cyclization-Heck reaction; oxidizing system shown as CaH2(cat.)/NaI(cat.)/O2 or BQ (1 equiv)", P1),
          field("temperature", None), field("time", None),
      ]}],
    [],
    [("Abstract reports regio- and stereoselective formation of the depicted product class and regeneration of Pd(II) from Pd(0).", P1)],
    ["Generic R-group scheme is not an individual experiment.", "Temperature, time, exact Pd identity/loading, and specific structures are not supplied in this arrow."],
))

# Page 2 Scheme 1: explicitly proposed mechanism, retained separately from experiments.
mech_parts = [
    participant("mechanism_I", "reactant", "generic allene I", P2),
    participant("mechanism_II", "unspecified_agent", "cyclic palladium intermediate II", P2),
    participant("mechanism_III", "unspecified_agent", "alkene-insertion intermediate III", P2),
    participant("mechanism_IV", "product", "generic cyclization-Heck product IV", P2),
    participant("mechanism_pdii", "catalyst", "Pd(II)", P2),
    participant("mechanism_oxidant", "reagent", "oxidant", P2),
]
records.append(record(
    "page2_scheme1_proposed_mechanism", "mechanism", P2, mech_parts,
    [
        {"step_id": "endo_cyclic_nucleopalladation", "participant_ids": ["mechanism_I", "mechanism_pdii"], "conditions": [field("operation", "endo-mode cyclic nucleopalladation to intermediate II", P2)]},
        {"step_id": "alkene_insertion", "participant_ids": ["mechanism_II"], "conditions": [field("operation", "alkene inserts into the C-Pd bond to form intermediate III", P2)]},
        {"step_id": "beta_h_elimination", "participant_ids": ["mechanism_III"], "conditions": [field("operation", "beta-H elimination affords product IV and a palladium hydride species", P2)]},
        {"step_id": "pd_reoxidation", "participant_ids": ["mechanism_pdii", "mechanism_oxidant"], "conditions": [field("operation", "Pd(0) is reoxidized to catalytically active Pd(II)", P2)]},
    ],
    [],
    [("Scheme 1 is titled a proposed catalytic cycle and is not a reported experiment.", P2)],
    ["All structures are generic and the oxidant is not specified within Scheme 1."],
))


def allene_1a(evidence, amount_value=None):
    amounts = [amount("equivalents", amount_value, "equiv", evidence)] if amount_value is not None else []
    return participant(
        "allene_1a", "reactant", "1a", evidence,
        name="ethyl (2-methylocta-2,3-dien-4-yl)phosphonic acid",
        smiles="CCOP(=O)(O)C(CCCC)=C=C(C)C", amounts=amounts,
    )


def acrylonitrile(evidence, amount_value=None):
    amounts = [amount("equivalents", amount_value, "equiv", evidence)] if amount_value is not None else []
    return participant("acrylonitrile", "reactant", "acrylonitrile", evidence, smiles="C=CC#N", amounts=amounts)


# Page 2 Scheme 2: distinct reported experiment preceding the optimization table.
scheme2_parts = [
    allene_1a(P2), acrylonitrile(P2),
    participant("cucl2", "reagent", "CuCl2", P2, smiles="[Cl-].[Cl-].[Cu+2]", amounts=[amount("equivalents", 4, "equiv", P2)]),
    participant("k2co3", "reagent", "K2CO3", P2, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[amount("equivalents", 4, "equiv", P2)]),
    participant("pdcl2_phcn2", "catalyst", "PdCl2(PhCN)2", P2, amounts=[amount("catalyst_loading", 5, "mol%", P2)]),
    participant("dmf", "solvent", "DMF", P2, smiles="CN(C)C=O"),
    participant("product_3a", "product", "chlorocyclization product 3a", P2),
    participant("product_E2a", "product", "E-2a", P2),
]
records.append(record(
    "scheme2_cucl2_k2co3", "reported_experiment", P2, scheme2_parts,
    [{"step_id": "scheme2_reaction", "participant_ids": [p["entity_id"] for p in scheme2_parts if p["role"] != "product"],
      "conditions": [field("temperature", {"number": 60, "unit": "°C"}, P2), field("solvent", "DMF", P2), field("time", None), field("atmosphere", None), field("workup", None), field("purification", None)]}],
    [
        field("reported_yield_3a", {"number": 34, "unit": "%"}, P2, ["product_3a"]),
        field("reported_yield_E_2a", {"number": 14, "unit": "%"}, P2, ["product_E2a"]),
        field("yield_measurement_basis", None),
    ],
    [("The prose describes a significant amount of 3a and 14% 2a; Scheme 2 labels 3a as 34% and E-2a as 14%.", P2)],
    ["Reaction time, atmosphere, workup, purification, yield measurement basis, and product SMILES are not reported here."],
))


TABLE1_ROWS = [
    (1, "NaI", 49, 7, "c"),
    (2, "NaI", 70, 4, None),
    (3, "NaI", 16, 2, "c"),
    (4, "NaI", 9, "trace", "d"),
    (5, "NaI", 70, 7, "e"),
    (6, "NaI", 41, 10, "d"),
    (7, "NaI", 9, 1, "f"),
    (8, "table dash (–)", 27, 7, None),
    (9, "BQ", 35, 6, "g"),
    (10, "CuCl2", 38, 17, None),
    (11, "KI", 34, 4, None),
    (12, "n-BuI", 46, 4, None),
    (13, "NaBr", 34, 6, None),
    (14, "NaCl", 9, 2, None),
]

OX_SMILES = {
    "NaI": "[Na+].[I-]", "BQ": "O=C1C=CC(=O)C=C1", "CuCl2": "[Cl-].[Cl-].[Cu+2]",
    "KI": "[K+].[I-]", "n-BuI": "CCCCI", "NaBr": "[Na+].[Br-]", "NaCl": "[Na+].[Cl-]",
}


for entry, oxidant_label, e_yield, z_yield, footnote in TABLE1_ROWS:
    ev = P2 + P3
    parts = [
        allene_1a(P2), acrylonitrile(P2),
        participant("pdcl2_phcn2", "catalyst", "PdCl2(PhCN)2", P2, amounts=[amount("catalyst_loading", 5, "mol%", P2)]),
        participant("dmf", "solvent", "DMF", P2, smiles="CN(C)C=O"),
        participant("product_E2a", "product", "E-2a", P2),
        participant("product_Z2a", "product", "Z-2a", P2),
        participant("product_4a", "product", "cycloisomerization product 4a", ev),
    ]
    if entry == 5:
        parts.append(participant("nah", "reagent", "NaH", P2, amounts=[amount("equivalents", 0.05, "equiv", P2)]))
    else:
        cah2_value = 0.5 if footnote == "c" else 1 if footnote == "d" else 0.05
        cah2_unit = "equiv" if footnote in ("c", "d") else "equiv"
        # The common header says 5 mol%; 0.05 equiv preserves the same explicit loading without converting units.
        if footnote not in ("c", "d"):
            parts.append(participant("cah2", "reagent", "CaH2", P2, amounts=[amount("catalyst_loading", 5, "mol%", P2)]))
        else:
            parts.append(participant("cah2", "reagent", "CaH2", P2, amounts=[amount("equivalents", cah2_value, cah2_unit, P2)]))
    if oxidant_label != "table dash (–)":
        parts.append(participant(
            "oxidant_or_halide", "reagent", "benzoquinone (BQ)" if oxidant_label == "BQ" else oxidant_label, P2,
            smiles=OX_SMILES.get(oxidant_label), amounts=[amount("equivalents", 0.2, "equiv", P2)],
        ))
    atmosphere = "Ar" if footnote == "f" else "air"
    apparatus = "without a CaCl2 drying tube" if entry in (5, 6) else ("with a CaCl2 drying tube" if atmosphere == "air" else None)
    step_conditions = [
        field("temperature", {"number": 60, "unit": "°C"}, P2),
        field("time", {"number": 24, "unit": "h"}, P2),
        field("solvent", "DMF", P2),
        field("atmosphere", atmosphere, ev if entry == 6 else P2),
        field("apparatus", apparatus, ev if apparatus else None) if apparatus is not None else field("apparatus", None),
        field("workup", None), field("purification", None),
    ]
    outcomes = [
        field("NMR_yield_E_2a", {"number": e_yield, "unit": "%"}, P2, ["product_E2a"]),
        field("NMR_yield_Z_2a", z_yield if z_yield == "trace" else {"number": z_yield, "unit": "%"}, P2, ["product_Z2a"]),
        field("yield_measurement_basis", "1H NMR analysis with CH2Br2 as internal standard", P2, ["product_E2a", "product_Z2a"]),
        field("formation_of_4a", {"number": 2, "unit": "%", "qualifier": "lt", "raw_text": "less than 2%, if any"}, P3, ["product_4a"]),
    ]
    if entry == 1:
        outcomes.append(field("E_Z_ratio", "7:1", P2, ["product_E2a", "product_Z2a"]))
    notes = []
    if entry == 8:
        notes.append(("Table 1 prints a dash in the oxidant column; the prose identifies entry 8 as conducted in the absence of NaI.", ev))
    unresolved = [
        "Amounts of 1a and acrylonitrile are not reported in the main-text table.",
        "Workup, purification, and product SMILES are unavailable without explicitly supplied supporting information.",
    ]
    if entry == 6:
        notes.append(("The prose assigns entry 6 to reaction in air without a drying tube; Table 1 also marks footnote d, whose CaH2 loading is structured in participants.", ev))
        unresolved.append("Entry 6's no-drying-tube condition is stated in prose rather than its table footnote; retained with both page-2 and page-3 evidence.")
    records.append(record(
        f"table1_entry{entry:02d}", "optimization_entry", ev, parts,
        [{"step_id": "cyclization_heck", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": step_conditions}],
        outcomes, notes, unresolved,
    ))


ALKENES = {
    "methyl acrylate": "C=CC(=O)OC",
    "ethyl acrylate": "C=CC(=O)OCC",
    "styrene": "C=Cc1ccccc1",
    "methyl methacrylate": "C=C(C)C(=O)OC",
    "acrylamide": "C=CC(N)=O",
}

TABLE2_ROWS = [
    (1, "1a (R1=n-Bu, R2=Me, R3=Me)", "methyl acrylate", "A", 88, "2b", ">99:1"),
    (2, "1a (R1=n-Bu, R2=Me, R3=Me)", "ethyl acrylate", "A", 84, "2c", ">99:1"),
    (3, "1a (R1=n-Bu, R2=Me, R3=Me)", "styrene", "A", 52, "2d", "only the signal of the E-isomer was identified in the 1H NMR spectrum"),
    (4, "1a (R1=n-Bu, R2=Me, R3=Me)", "styrene", "B", 85, "2d", "only the signal of the E-isomer was identified in the 1H NMR spectrum"),
    (5, "1e (R1=n-Bu, R2/R3=-(CH2)4-)", "methyl acrylate", "A", 69, "2e", ">99:1"),
    (6, "1f (R1=Me, R2/R3=-(CH2)5-)", "methyl acrylate", "A", 79, "2f", ">99:1"),
    (7, "1g (R1=Bn, R2=Me, R3=Me)", "methyl acrylate", "A", 75, "2g", "only the signal of the E-isomer was identified in the 1H NMR spectrum"),
    (8, "1h (R1=n-C6H13, R2=Et, R3=Et)", "methyl acrylate", "A", 85, "2h", ">99:1"),
    (9, "1a (R1=n-Bu, R2=Me, R3=Me)", "methyl methacrylate", "B", 61, "2i", ">99:1"),
    (10, "1a (R1=n-Bu, R2=Me, R3=Me)", "acrylamide", "B", 86, "2j", ">99:1"),
    (11, "1k (R1=n-Hept, R2=H, R3=Me)", "ethyl acrylate", "B", 63, "2k", "55:1"),
    (12, "1k (R1=n-Hept, R2=H, R3=Me)", "styrene", "B", 63, "2l", "only the signal of the E-isomer was identified in the 1H NMR spectrum"),
    (13, "1m (R1=n-Bu, R2=H, R3=H)", "ethyl acrylate", "B", 46, "2m", ">99:1"),
    (14, "1m (R1=n-Bu, R2=H, R3=H)", "acrylamide", "B", 48, "2n", "only the signal of the E-isomer was identified in the 1H NMR spectrum"),
    (15, "1o (R1=H, R2/R3=-(CH2)5-)", "ethyl acrylate", "B", 61, "2o", ">99:1"),
    (16, "1o (R1=H, R2/R3=-(CH2)5-)", "acrylamide", "B", 34, "2p", "only the signal of the E-isomer was identified in the 1H NMR spectrum"),
]


for entry, substrate_label, alkene_name, condition, table_yield, product_label, ez_value in TABLE2_ROWS:
    substrate_smiles = "CCOP(=O)(O)C(CCCC)=C=C(C)C" if substrate_label.startswith("1a ") else None
    parts = [
        participant("allene_substrate", "reactant", substrate_label, P3, smiles=substrate_smiles, amounts=[amount("equivalents", 1, "equiv", P3)]),
        participant("alkene", "reactant", alkene_name, P3, smiles=ALKENES[alkene_name], amounts=[amount("equivalents", 5, "equiv", P3)]),
        participant("pdcl2_phcn2", "catalyst", "PdCl2(PhCN)2", P3, amounts=[amount("catalyst_loading", 5, "mol%", P3)]),
        participant("dmf", "solvent", "DMF", P3, smiles="CN(C)C=O"),
        participant("major_product", "product", f"E-{product_label}", P3),
    ]
    if condition == "A":
        parts += [
            participant("nai", "reagent", "NaI", P3, smiles="[Na+].[I-]", amounts=[amount("equivalents", 0.2, "equiv", P3)]),
            participant("cah2", "reagent", "CaH2", P3, amounts=[amount("catalyst_loading", 5, "mol%", P3)]),
        ]
        temperature = 100 if entry == 3 else 60
        time_value = {"number": 24, "unit": "h"}
        atmosphere_value = "air"
        apparatus_value = "CaCl2 drying tube"
    else:
        parts.append(participant("bq", "reagent", "benzoquinone (BQ)", P3, smiles="O=C1C=CC(=O)C=C1", amounts=[amount("equivalents", 1, "equiv", P3)]))
        temperature = 60
        time_value = "overnight"
        atmosphere_value = None
        apparatus_value = None
    if entry == 3:
        parts.append(participant("byproduct_4a", "product", "cycloisomerization product 4a", P3))
    step_conditions = [
        field("temperature", {"number": temperature, "unit": "°C"}, P3),
        field("time", time_value, P3), field("solvent", "DMF", P3),
        field("atmosphere", atmosphere_value, P3 if atmosphere_value is not None else None),
        field("apparatus", apparatus_value, P3 if apparatus_value is not None else None),
        field("workup", None), field("purification", None),
    ]
    outcomes = [
        field("table_isolated_yield", {"number": table_yield, "unit": "%"}, P3, ["major_product"]),
        field("yield_measurement_basis", "isolated yield", P3, ["major_product"]),
        field("E_Z_ratio", ez_value, P3, ["major_product"]),
    ]
    unresolved = [
        "Workup, purification, and product SMILES are unavailable without explicitly supplied supporting information.",
        "E/Z values are from crude-product 1H NMR; no independently verified stereochemical structure is assigned.",
    ]
    notes = []
    if entry == 3:
        outcomes.append(field("isolated_yield_4a", {"number": 25, "unit": "%"}, P3, ["byproduct_4a"]))
    if entry == 9:
        outcomes.append(field("prose_reported_yield", {"number": 64, "unit": "%"}, P3, ["major_product"]))
        notes.append(("Table 2 gives 61% for 2i, while the prose on the same page states 64%.", P3))
        unresolved.append("Source-internal yield conflict for 2i: Table 2 = 61%; prose = 64%.")
    if entry == 10:
        outcomes.append(field("prose_reported_yield", {"number": 66, "unit": "%"}, P3, ["major_product"]))
        notes.append(("Table 2 gives 86% for 2j, while the prose on the same page states 66%.", P3))
        unresolved.append("Source-internal yield conflict for 2j: Table 2 = 86%; prose = 66%.")
    records.append(record(
        f"table2_entry{entry:02d}", "substrate_scope_entry", P3, parts,
        [{"step_id": "cyclization_heck", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": step_conditions}],
        outcomes, notes, unresolved,
    ))


out = Path(__file__).with_name("records_pages_0001_0004.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
