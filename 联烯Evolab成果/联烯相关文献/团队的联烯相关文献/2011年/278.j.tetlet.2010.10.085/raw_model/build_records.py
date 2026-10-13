import json
from pathlib import Path

DOC = "doc_5dac7919a41781be"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, target=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if target:
        result["target_entity_ids"] = [target]
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def base_record(suffix, kind, evidence):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
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


solvents = {
    "MeCN": ("acetonitrile", "CC#N"),
    "DMSO": ("dimethyl sulfoxide", "CS(C)=O"),
    "DMA": ("N,N-dimethylacetamide", "CC(=O)N(C)C"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "Et2O": ("diethyl ether", "CCOCC"),
}

rf4 = "C(F)(F)C(F)(F)C(F)(F)C(F)(F)F"
rf6 = "C(F)(F)C(F)(F)C(F)(F)C(F)(F)C(F)(F)C(F)(F)F"
smiles_1a = f"c1ccccc1C=C=C(C)C(=O){rf4}"
smiles_2a = f"o1c(c2ccccc2)c(I)c(C)c1{rf4}"

records = []

# Scheme 1 is a proposed generic mechanism and follow-on coupling concept, not a batch experiment.
scheme = base_record("scheme1_electrophilic_cyclization_mechanism", "mechanism", [P1T, P1I, P2T, P2I])
scheme["participants"] = [
    participant("scheme1_allenyl_ketone_1", "reactant", "1", "generic 1,2-allenyl ketone", [P1T, P1I, P2T, P2I]),
    participant("scheme1_electrophile", "reagent", "X+", "generic electrophile", [P1T, P1I, P2T, P2I]),
    participant("scheme1_intermediate_M1", "product", "M1", "proposed cyclic cationic intermediate", [P1T, P1I, P2T, P2I]),
    participant("scheme1_furan_2", "product", "2", "generic substituted furan", [P1T, P1I, P2T, P2I]),
    participant("scheme1_dihydrofuranol_3", "product", "3", "generic 2-hydroxy-2,5-dihydrofuran", [P1T, P1I, P2T, P2I]),
    participant("scheme1_water", "reagent", "H2O", "water", [P1T, P1I, P2T, P2I], "O"),
]
scheme["steps"] = [
    {"step_id": "electrophile_addition", "participant_ids": ["scheme1_allenyl_ketone_1", "scheme1_electrophile", "scheme1_intermediate_M1"], "conditions": []},
    {"step_id": "r2_h_aromatization", "participant_ids": ["scheme1_intermediate_M1", "scheme1_furan_2"], "conditions": [field("branch_condition", "R2 = H; H+ release is depicted", [P1T, P1I, P2T, P2I])]},
    {"step_id": "r2_non_h_water_trapping", "participant_ids": ["scheme1_intermediate_M1", "scheme1_water", "scheme1_dihydrofuranol_3"], "conditions": [field("branch_condition", "R2 is not H; H2O attack and H+ release are depicted", [P1T, P1I, P2T, P2I])]},
    {"step_id": "generic_coupling_from_2", "participant_ids": ["scheme1_furan_2"], "conditions": [field("operation", "generic coupling replaces X by R", [P2T, P2I])]},
    {"step_id": "generic_coupling_from_3", "participant_ids": ["scheme1_dihydrofuranol_3"], "conditions": [field("operation", "generic coupling replaces X by R", [P2T, P2I])]},
]
scheme["notes"] = [fact("Conceptual mechanism/general route only; no yield or batch conditions are assigned.", [P1T, P1I, P2T, P2I])]
scheme["review"]["unresolved"] = ["Generic R groups and X are not complete molecular structures; SMILES are intentionally missing."]
records.append(scheme)


table1 = [
    (1, "MeCN", 0, "r.t.", 36, 93, 2, False),
    (2, "MeCN", 0, 40, 22, 95, 0, True),
    (3, "MeCN", 0, 60, 11, 93, 0, True),
    (4, "MeCN", 1, "r.t.", 36, 99, 0, False),
    (5, "MeCN", 5, "r.t.", 36, 81, 0, False),
    (6, "DMSO", 1, "r.t.", 32, 5, 1, False),
    (7, "DMA", 1, "r.t.", 32, 45, 0, False),
    (8, "THF", 1, "r.t.", 40, 17, 61, False),
    (9, "Et2O", 1, "r.t.", 40, 58, 18, False),
]

for entry, solvent_label, water_eq, temperature, hours, product_yield, recovery, byproduct in table1:
    evidence = [P2T, P2I]
    if entry <= 5:
        evidence = [P1T, P1I, P2T, P2I]
    rec = base_record(f"table1_entry{entry}", "optimization_entry", evidence)
    solvent_name, solvent_smiles = solvents[solvent_label]
    rec["participants"] = [
        participant("starting_1a", "reactant", "1a", "1-phenylbuta-1,2-dien-3-yl n-perfluorobutyl ketone", evidence, smiles_1a),
        participant("product_2a", "product", "2a", "n-perfluorobutyl-substituted iodofuran 2a", evidence, smiles_2a),
        participant("iodine", "reagent", "I2", "iodine", evidence, "II", [field("equivalents", quantity(2.0, "equiv"), evidence)]),
        participant("water", "reagent", "H2O", "water", evidence, "O", [field("equivalents", quantity(water_eq, "equiv"), evidence)]),
        participant("solvent", "solvent", solvent_label, solvent_name, evidence, solvent_smiles),
    ]
    temp_value = temperature if isinstance(temperature, str) else quantity(temperature, "°C")
    rec["steps"] = [{
        "step_id": "iodocyclization",
        "participant_ids": ["starting_1a", "iodine", "water", "solvent", "product_2a"],
        "conditions": [
            field("temperature", temp_value, evidence),
            field("time", quantity(hours, "h"), evidence),
        ],
    }]
    rec["outcomes"] = [
        field("nmr_yield", quantity(product_yield, "%"), evidence, "product_2a"),
        field("yield_measurement_basis", "1H NMR analysis with mesitylene as internal standard", [P2T, P2I], "product_2a"),
        field("recovered_starting_material_yield", quantity(recovery, "%"), evidence, "starting_1a"),
    ]
    if entry == 4:
        rec["outcomes"].append(field("parenthesized_reported_yield", quantity(93, "%", "(93)"), [P2T, P2I], "product_2a"))
        rec["review"]["unresolved"].append("The visible table does not define the basis of the parenthesized 93% value.")
    if byproduct:
        rec["notes"].append(fact("An unidentified byproduct was formed and could not be separated from 2a.", evidence))
    if entry == 1:
        rec["notes"].append(fact("The prose describes the MeCN as anhydrous.", [P1T, P1I]))
    rec["review"]["unresolved"] += [
        "No experimental workup or purification is present in the supplied main-text pages.",
        "Substrate and product SMILES are source-derived candidates and remain structurally unverified.",
    ]
    records.append(rec)


def allene_smiles(r1, r2, r3, rf):
    if (r1, r2) == ("Ph", "H"):
        left = "c1ccccc1C"
    elif (r1, r2) == ("n-Bu", "H"):
        left = "CCCCC"
    elif (r1, r2) == ("n-C7H15", "H"):
        left = "CCCCCCCC"
    elif (r1, r2) == ("Me", "Me"):
        left = "CC(C)"
    elif (r1, r2) == ("Ph", "Ph"):
        left = "c1ccccc1C(c2ccccc2)"
    elif r1 == "-(CH2)5-":
        return f"C1(CCCCC1)=C=C({substituent_smiles(r3)})C(=O){rf}"
    else:
        return None
    return f"{left}=C=C({substituent_smiles(r3)})C(=O){rf}"


def substituent_smiles(label):
    return {"Me": "C", "n-C3H7": "CCC", "Ph": "c1ccccc1"}[label]


def furan_smiles(r1, r3, rf):
    r1s = {"Ph": "c2ccccc2", "n-Bu": "CCCC", "n-C7H15": "CCCCCCC"}.get(r1)
    if not r1s:
        return None
    return f"o1c({r1s})c(I)c({substituent_smiles(r3)})c1{rf}"


def dihydrofuranol_smiles(r1, r2, r3, rf):
    r3s = substituent_smiles(r3)
    if r1 == "-(CH2)5-":
        return f"O1C2(CCCCC2)C(I)=C({r3s})C1(O){rf}"
    groups = {"Me": "C", "Ph": "c2ccccc2"}
    return f"O1C({groups[r1]})({groups[r2]})C(I)=C({r3s})C1(O){rf}"


table2 = [
    (1, "Ph", "H", "Me", "n-C4F9", "1a", "2a", 36, 93, 2.0, "r.t.", rf4, None, None),
    (2, "Ph", "H", "Me", "n-C6F13", "1b", "2b", 36, 91, 2.0, "r.t.", rf6, None, None),
    (3, "Ph", "H", "n-C3H7", "n-C4F9", "1c", "2c", 16, 91, 2.0, 60, rf4, None, 98),
    (4, "n-Bu", "H", "Me", "n-C4F9", "1d", "2d", 36, 60, 2.0, "r.t.", rf4, None, None),
    (5, "n-C7H15", "H", "Me", "n-C4F9", "1e", "2e", 36, 60, 2.0, "r.t.", rf4, None, None),
    (6, "n-Bu", "H", "Me", "n-C6F13", "1f", "2f", 24, 85, 4.0, "r.t.", rf6, None, None),
    (7, "n-C7H15", "H", "n-C3H7", "n-C4F9", "1g", "2g", 36, 70, 4.0, "r.t.", rf4, None, None),
    (8, "-(CH2)5-", "linked", "Me", "n-C4F9", "1h", "3h", 37, 75, 2.0, "r.t.", rf4, None, None),
    (9, "Me", "Me", "Ph", "n-C4F9", "1i", "3i", 35, 93, 2.0, "r.t.", rf4, None, None),
    (10, "Ph", "Ph", "n-C3H7", "n-C4F9", "1j", "3j", 35, 54, 2.0, "r.t.", rf4, 29, None),
    (11, "Ph", "Ph", "n-C3H7", "n-C4F9", "1j", "3j", 16, 88, 2.0, "r.t.", rf4, None, None),
]

for entry, r1, r2, r3, rf_label, start_label, product_label, hours, product_yield, iodine_eq, temperature, rf_smiles, recovery, purity in table2:
    evidence = [P1T, P1I, P2T, P2I]
    rec = base_record(f"table2_entry{entry}", "substrate_scope_entry", evidence)
    starting_smiles = allene_smiles(r1, r2, r3, rf_smiles)
    product_smiles = furan_smiles(r1, r3, rf_smiles) if r2 == "H" else dihydrofuranol_smiles(r1, r2, r3, rf_smiles)
    descriptor = f"R1={r1}, R2={r2}, R3={r3}, Rf={rf_label}"
    participants = [
        participant("starting_material", "reactant", start_label, f"1,2-allenyl perfluoroalkyl ketone ({descriptor})", evidence, starting_smiles),
        participant("product", "product", product_label, f"iodocyclization product {product_label} ({descriptor})", evidence, product_smiles),
        participant("iodine", "reagent", "I2", "iodine", evidence, "II", [field("equivalents", quantity(iodine_eq, "equiv"), evidence)]),
        participant("mecn", "solvent", "MeCN", "acetonitrile", evidence, "CC#N"),
    ]
    if entry == 11:
        participants.append(participant("water", "solvent", "H2O", "water", evidence, "O"))
    else:
        participants.append(participant("water", "reagent", "H2O", "water", evidence, "O", [field("equivalents", quantity(1.0, "equiv"), evidence)]))
    rec["participants"] = participants
    temp_value = temperature if isinstance(temperature, str) else quantity(temperature, "°C")
    conditions = [field("temperature", temp_value, evidence), field("time", quantity(hours, "h"), evidence)]
    if entry == 11:
        conditions.append(field("aqueous_solvent_composition", "MeCN/H2O = 20/1", evidence))
    rec["steps"] = [{
        "step_id": "iodocyclization",
        "participant_ids": [p["entity_id"] for p in participants] + ["product"],
        "conditions": conditions,
    }]
    # Avoid duplicate product in step participant IDs (product is already in participants list).
    rec["steps"][0]["participant_ids"] = list(dict.fromkeys(rec["steps"][0]["participant_ids"]))
    rec["outcomes"] = [
        field("reported_yield", quantity(product_yield, "%"), evidence, "product"),
        field("yield_measurement_basis", None, [], "product"),
    ]
    if recovery is not None:
        rec["outcomes"].append(field("recovered_starting_material_yield", quantity(recovery, "%"), evidence, "starting_material"))
    if purity is not None:
        rec["outcomes"].append(field("product_purity", quantity(purity, "%"), evidence, "product"))
    rec["review"]["unresolved"] = [
        "The visible table does not state the yield measurement basis.",
        "No experimental workup or purification is present in the supplied main-text pages.",
        "Substrate and product SMILES are source-derived candidates and remain structurally unverified.",
    ]
    if entry == 11:
        rec["review"]["unresolved"].append("The MeCN/H2O 20/1 ratio is preserved as printed; individual solvent volumes and a ratio basis are not stated.")
    records.append(rec)


output = Path(__file__).with_name("records_pages_0001_0003.json")
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {output}")
