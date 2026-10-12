#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1-4 of doc_9731d6e58e54a267."""
import json
from pathlib import Path

DOC = "doc_9731d6e58e54a267"
OUT = Path(__file__).with_name("pages_0001_0004_records.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def quantity(number, unit, *, qualifier=None, raw_text=None):
    value = {"number": number, "unit": unit}
    if qualifier:
        value["qualifier"] = qualifier
    if raw_text:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, target=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if target:
        result["target_entity_ids"] = list(target)
    return result


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence) if label is not None else fact(None),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(text, note_ev) for text, note_ev in notes],
        "review": {
            "method": "model",
            "reviewer": "Codex machine extraction",
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


records = []

# Table 1 rows, merged with the matching detailed procedures on page 3.
table1 = [
    {
        "n": 1, "acid_label": "(S)-(+)-1b",
        "acid_name": "(S)-2-methyl-4-phenylbuta-2,3-dienoic acid",
        "acid_smiles": "CC(=C=Cc1ccccc1)C(=O)O", "acid_mass": 69, "acid_mmol": 0.4,
        "table_ee": (97.3, ">97.3%"), "procedure_ee": None,
        "product_label": "(R)-(+)-2a", "product_name": "(R)-3-methyl-5-phenylfuran-2(5H)-one",
        "product_smiles": "CC1=CC(c2ccccc2)OC1=O", "time": 2, "product_mass": 65,
        "yield": 94, "product_ee": 98.6, "purification": "flash chromatography (silica gel, PE–EtOAc 10:1)",
    },
    {
        "n": 2, "acid_label": "(R)-(−)-1b",
        "acid_name": "(R)-2-methyl-4-phenylbuta-2,3-dienoic acid",
        "acid_smiles": "CC(=C=Cc1ccccc1)C(=O)O", "acid_mass": 70, "acid_mmol": 0.4,
        "table_ee": (94.3, ">94.3%"), "procedure_ee": None,
        "product_label": "(S)-(−)-2a", "product_name": "(S)-3-methyl-5-phenylfuran-2(5H)-one",
        "product_smiles": "CC1=CC(c2ccccc2)OC1=O", "time": 2.5, "product_mass": 58,
        "yield": 83, "product_ee": 97.6, "purification": "flash chromatography (silica gel, PE–EtOAc 10:1)",
        "time_conflict": True,
    },
    {
        "n": 3, "acid_label": "(S)-(+)-1a",
        "acid_name": "(S)-2-propyl-4-phenylbuta-2,3-dienoic acid",
        "acid_smiles": "CCCC(=C=Cc1ccccc1)C(=O)O", "acid_mass": 82, "acid_mmol": 0.4,
        "table_ee": (97.4, ">97.4%"), "procedure_ee": (97.2, ">97.2%"),
        "product_label": "(R)-(+)-2b", "product_name": "(R)-5-phenyl-3-propylfuran-2(5H)-one",
        "product_smiles": "CCCC1=CC(c2ccccc2)OC1=O", "time": 3, "product_mass": 70,
        "yield": 85, "product_ee": 99.8, "purification": "flash chromatography (silica gel, PE–EtOAc 15:1)",
        "time_conflict": True,
    },
    {
        "n": 4, "acid_label": "(R)-(−)-1a",
        "acid_name": "(R)-2-propyl-4-phenylbuta-2,3-dienoic acid",
        "acid_smiles": "CCCC(=C=Cc1ccccc1)C(=O)O", "acid_mass": 81, "acid_mmol": 0.4,
        "table_ee": (97.2, ">97.2%"), "procedure_ee": (97.4, ">97.4%"),
        "product_label": "(S)-(−)-2b", "product_name": "(S)-5-phenyl-3-propylfuran-2(5H)-one",
        "product_smiles": "CCCC1=CC(c2ccccc2)OC1=O", "time": 2, "product_mass": 73,
        "yield": 90, "product_ee": 96.5, "purification": "flash chromatography (silica gel, PE–EtOAc 15:1)",
    },
]

for row in table1:
    e1, e3 = ev(1), ev(3)
    acid = f"t1e{row['n']}_acid"
    product = f"t1e{row['n']}_product"
    cucl = f"t1e{row['n']}_cucl"
    meoh = f"t1e{row['n']}_meoh"
    parts = [
        participant(acid, "reactant", row["acid_label"], row["acid_name"], row["acid_smiles"], e1 + e3, [
            field("mass", quantity(row["acid_mass"], "mg"), e3),
            field("amount", quantity(row["acid_mmol"], "mmol"), e3),
        ]),
        participant(cucl, "catalyst", "CuCl", "copper(I) chloride", "[Cu]Cl", e1 + e3, [
            field("mass", quantity(1.6, "mg"), e3),
            field("amount", quantity(0.016, "mmol"), e3),
            field("catalyst_loading", quantity(4, "mol%"), e1),
        ]),
        participant(meoh, "solvent", "MeOH", "methanol", "CO", e1 + e3, [
            field("volume", quantity(4, "mL"), e3),
        ]),
        participant(product, "product", row["product_label"], row["product_name"], row["product_smiles"], e1 + e3, [
            field("mass", quantity(row["product_mass"], "mg"), e3),
        ]),
    ]
    conditions = [
        field("atmosphere", "N2", e3),
        field("temperature", quantity(60, "°C"), e1 + e3),
        field("time", quantity(row["time"], "h"), e3),
        field("solvent", "MeOH", e1 + e3),
        field("operation", "stirred; solvent evaporated after reaction", e3),
        field("purification", row["purification"], e3),
    ]
    outcomes = [
        field("table_reactant_ee", quantity(row["table_ee"][0], "%", qualifier="gt", raw_text=row["table_ee"][1]), e1, [acid]),
        field("yield", quantity(row["yield"], "%"), e1 + e3, [product]),
        field("product_ee", quantity(row["product_ee"], "%"), e1 + e3, [product]),
        field("yield_measurement_basis", None, [], [product]),
    ]
    unresolved = [
        "No supporting information was explicitly provided or associated.",
        "Yield basis is not explicitly labeled for Table 1 or its detailed procedure.",
        "Candidate SMILES encode connectivity only; axial and product stereochemistry require source-structure verification.",
    ]
    notes = [("Absolute configurations of products are described by the authors as tentatively assigned on the basis of the X-ray study of 2e.", ev(2))]
    evidence = e1 + e3 + ev(2)
    if row["procedure_ee"]:
        outcomes.append(field("procedure_reactant_ee", quantity(row["procedure_ee"][0], "%", qualifier="gt", raw_text=row["procedure_ee"][1]), e3, [acid]))
        unresolved.append("Starting-material ee differs between Table 1 and the detailed procedure; both printed values are retained.")
    if row.get("time_conflict"):
        notes.append(("The Table 1 arrow prints a shared 2 h condition, while the detailed procedure prints a different reaction time.", e1 + e3))
        unresolved.append("Reaction time differs between the Table 1 shared arrow and the detailed procedure; the procedure value is structured as time.")
    records.append(record(
        f"table1_entry{row['n']}", f"Table 1 entry {row['n']} / detailed procedure {row['acid_label']}",
        "substrate_scope_entry", evidence, parts,
        [{"step_id": "cycloisomerization", "participant_ids": [acid, cucl, meoh, product], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


# Table 2 optimization entries 1-9. Entry 10 is merged with scope record 3a below.
opt_rows = [
    (1, 97.7, "MeOH", 2, quantity(70, "°C"), 3.6, 71, 4.3),
    (2, 97.7, "EtOH", 2, quantity(70, "°C"), 11, 73, 1),
    (3, 97.7, "EtOAc", 2, quantity(70, "°C"), 13.5, 80, 9),
    (4, 89.2, "THF", 2, quantity(60, "°C"), 12, 82, 81.9),
    (5, 89.2, "CH2Cl2", 2, "reflux", 4.5, 82, 87.5),
    (6, 89.2, "CH2Cl2", 2, quantity(30, "°C"), 4.5, 80, 90.1),
    (7, 89.2, "CH2Cl2", 2, quantity(0, "°C"), 5, 67, 88.5),
    (8, 89.2, "CH2Cl2", 1, quantity(0, "°C"), 10.5, 62, 88.6),
    (9, 89.2, "CH2Cl2", "10%", quantity(25, "°C"), 12, 34, 58.5),
]
solvent_names = {"MeOH": ("methanol", "CO"), "EtOH": ("ethanol", "CCO"), "EtOAc": ("ethyl acetate", "CCOC(C)=O"), "THF": ("tetrahydrofuran", "C1CCOC1"), "CH2Cl2": ("dichloromethane", "ClCCl")}
for n, ree, solvent, loading, temp, time, yld, pee in opt_rows:
    e2 = ev(2)
    salt, cucl, solv, product = (f"t2e{n}_salt3a", f"t2e{n}_cucl", f"t2e{n}_solvent", f"t2e{n}_product2a")
    if loading == "10%":
        cucl_amount = field("table_loading", quantity(10, "%", raw_text="10% printed in the CuCl (equiv) column"), e2)
        loading_issue = ["Table 2 entry 9 prints 10% in a column headed CuCl (equiv); the percentage basis is not specified and is not converted to mol%. "]
    else:
        cucl_amount = field("equivalents", quantity(loading, "equiv"), e2)
        loading_issue = []
    parts = [
        participant(salt, "reactant", "3a", "1:1 salt of (S)-2-methyl-4-phenylbuta-2,3-dienoic acid with L-(−)-cinchonidine", None, e2),
        participant(cucl, "unspecified_agent", "CuCl", "copper(I) chloride", "[Cu]Cl", e2, [cucl_amount]),
        participant(solv, "solvent", solvent, solvent_names[solvent][0], solvent_names[solvent][1], e2),
        participant(product, "product", "(R)-(+)-2a", "(R)-3-methyl-5-phenylfuran-2(5H)-one", "CC1=CC(c2ccccc2)OC1=O", e2),
    ]
    outcomes = [
        field("reactant_ee", quantity(ree, "%"), e2, [salt]),
        field("isolated_yield", quantity(yld, "%"), e2, [product]),
        field("yield_measurement_basis", "isolated yield", e2, [product]),
        field("product_ee", quantity(pee, "%"), e2, [product]),
    ]
    records.append(record(
        f"table2_entry{n}", f"Table 2 entry {n}", "optimization_entry", e2, parts,
        [{"step_id": "cyclization", "participant_ids": [salt, cucl, solv, product], "conditions": [
            field("solvent", solvent, e2), field("temperature", temp, e2), field("time", quantity(time, "h"), e2)
        ]}], outcomes,
        [("Reactant ee was determined after conversion of 3a into its ester; product ee was determined by chiral-column HPLC.", e2)],
        [
            "No supporting information was explicitly provided or associated.",
            "No entry-specific atmosphere, scale, workup, or purification is reported in Table 2.",
            "The role of CuCl is preserved as unspecified_agent because the table spans stoichiometric and percentage loadings.",
            "The composite chiral salt structure and stereochemical product SMILES require source-structure verification.",
        ] + loading_issue,
    ))


# Table 3 scope rows, merged with detailed procedures on pages 3-4.
scope = [
    {"id":"3a","acid":"(S)-2-methyl-4-phenylbuta-2,3-dienoic acid","amine":"L-(−)-cinchonidine","product":"(R)-(+)-2a","pname":"(R)-3-methyl-5-phenylfuran-2(5H)-one","ps":"CC1=CC(c2ccccc2)OC1=O","mass":117,"mmol":0.25,"cucl_mass":26,"cucl_mmol":0.26,"vol":8,"table_time":10,"proc_time":12,"y_mass":34,"yield":78,"table_ree":97.7,"proc_ree":97.7,"table_pee":97.1,"proc_pee":97.1,"page":3,"basis":"isolated yield"},
    {"id":"3b","acid":"(R)-2-methyl-4-phenylbuta-2,3-dienoic acid","amine":"D-(+)-α-(1-phenylethyl)amine","product":"(S)-(−)-2a","pname":"(S)-3-methyl-5-phenylfuran-2(5H)-one","ps":"CC1=CC(c2ccccc2)OC1=O","mass":60,"mmol":0.2,"cucl_mass":21,"cucl_mmol":0.21,"vol":2,"table_time":10,"proc_time":10,"y_mass":32,"yield":90,"table_ree":94.3,"proc_ree":94.3,"table_pee":97.3,"proc_pee":97.3,"page":3},
    {"id":"3c","acid":"(S)-2-propyl-4-phenylbuta-2,3-dienoic acid","amine":"L-(−)-(1-phenylethyl)amine","product":"(R)-(+)-2b","pname":"(R)-5-phenyl-3-propylfuran-2(5H)-one","ps":"CCCC1=CC(c2ccccc2)OC1=O","mass":100,"mmol":0.31,"cucl_mass":31,"cucl_mmol":0.31,"vol":3,"table_time":10,"proc_time":10,"y_mass":59,"yield":94,"table_ree":97.2,"proc_ree":97.2,"table_pee":99.9,"proc_pee":99.0,"page":3},
    {"id":"3d","acid":"(R)-2-propyl-4-phenylbuta-2,3-dienoic acid","amine":"D-(+)-α-(1-phenylethyl)amine","product":"(S)-(−)-2b","pname":"(S)-5-phenyl-3-propylfuran-2(5H)-one","ps":"CCCC1=CC(c2ccccc2)OC1=O","mass":100,"mmol":0.31,"cucl_mass":31,"cucl_mmol":0.31,"vol":3,"table_time":10,"proc_time":10,"y_mass":59,"yield":94,"table_ree":97.4,"proc_ree":97.4,"table_pee":99.1,"proc_pee":99.1,"page":3},
    {"id":"3e","acid":"(S)-2-allyl-4-phenylbuta-2,3-dienoic acid","amine":"L-(−)-(1-phenylethyl)amine","product":"(R)-(+)-2c","pname":"(R)-3-allyl-5-phenylfuran-2(5H)-one","ps":"C=CCC1=CC(c2ccccc2)OC1=O","mass":102,"mmol":0.31,"cucl_mass":31,"cucl_mmol":0.31,"vol":3,"table_time":10,"proc_time":10,"y_mass":61,"yield":96,"table_ree":97.6,"proc_ree":97.6,"table_pee":96.9,"proc_pee":96.9,"page":3},
    {"id":"3f","acid":"(R)-2-allyl-4-phenylbuta-2,3-dienoic acid","amine":"D-(+)-α-(1-phenylethyl)amine","product":"(S)-(−)-2c","pname":"(S)-3-allyl-5-phenylfuran-2(5H)-one","ps":"C=CCC1=CC(c2ccccc2)OC1=O","mass":103,"mmol":0.32,"cucl_mass":31,"cucl_mmol":0.31,"vol":3,"table_time":10,"proc_time":10,"y_mass":60,"yield":93,"table_ree":97.8,"proc_ree":97.8,"table_pee":98.5,"proc_pee":98.5,"page":3},
    {"id":"3g","acid":"(S)-2-methyl-4-(1-naphthyl)buta-2,3-dienoic acid","amine":"L-(−)-(1-phenylethyl)amine","product":"(R)-(+)-2d","pname":"(R)-3-methyl-5-(1-naphthyl)furan-2(5H)-one","ps":"CC1=CC(c2cccc3ccccc23)OC1=O","mass":87,"mmol":0.252,"cucl_mass":27,"cucl_mmol":0.27,"vol":3,"table_time":12.5,"proc_time":10,"y_mass":46,"yield":81,"table_ree":98.3,"proc_ree":98.3,"table_pee":98.2,"proc_pee":98.2,"page":3},
    {"id":"3h","acid":"(R)-2-methyl-4-(1-naphthyl)buta-2,3-dienoic acid","amine":"D-(+)-α-(1-phenylethyl)amine","product":"(S)-(−)-2d","pname":"(S)-3-methyl-5-(1-naphthyl)furan-2(5H)-one","ps":"CC1=CC(c2cccc3ccccc23)OC1=O","mass":140,"mmol":0.406,"cucl_mass":41,"cucl_mmol":0.41,"vol":4,"table_time":10,"proc_time":10,"y_mass":86,"yield":95,"table_ree":96.7,"proc_ree":96.7,"table_pee":99.3,"proc_pee":99.3,"page":3},
    {"id":"3i","acid":"(S)-4-(4-bromophenyl)-2-propylbuta-2,3-dienoic acid","amine":"L-(−)-cinchonidine (Table 3 base A)","product":"(R)-(+)-2e","pname":"(R)-5-(4-bromophenyl)-3-propylfuran-2(5H)-one","ps":"CCCC1=CC(c2ccc(Br)cc2)OC1=O","mass":115,"mmol":0.2,"cucl_mass":20,"cucl_mmol":0.2,"vol":2,"table_time":10,"proc_time":10,"y_mass":49,"yield":87,"table_ree":99.0,"proc_ree":97.9,"table_pee":98.0,"proc_pee":98.0,"page":4,"alt_amine":"D-(−)-(1-phenylethyl)amine (detailed procedure)"},
]

acid_smiles = {
    "3a":"CC(=C=Cc1ccccc1)C(=O)O", "3b":"CC(=C=Cc1ccccc1)C(=O)O",
    "3c":"CCCC(=C=Cc1ccccc1)C(=O)O", "3d":"CCCC(=C=Cc1ccccc1)C(=O)O",
    "3e":"C=CCC(=C=Cc1ccccc1)C(=O)O", "3f":"C=CCC(=C=Cc1ccccc1)C(=O)O",
    "3g":"CC(=C=Cc1cccc2ccccc12)C(=O)O", "3h":"CC(=C=Cc1cccc2ccccc12)C(=O)O",
    "3i":"CCCC(=C=Cc1ccc(Br)cc1)C(=O)O",
}

for entry_no, row in enumerate(scope, 1):
    e2, ep = ev(2), ev(row["page"])
    evidence = e2 + ep
    if row["id"] == "3a":
        evidence = ev(1) + evidence
    if row["id"] == "3i":
        evidence = e2 + ev(3) + ep
    salt, cucl, dcm, product = (f"{row['id']}_salt", f"{row['id']}_cucl", f"{row['id']}_dcm", f"{row['id']}_product")
    salt_name = f"1:1 salt of {row['acid']} with {row['amine']}"
    parts = [
        participant(salt, "reactant", row["id"], salt_name, None, e2 + ep, [
            field("mass", quantity(row["mass"], "mg"), ep),
            field("amount", quantity(row["mmol"], "mmol"), ep),
        ]),
        participant(cucl, "unspecified_agent", "CuCl", "copper(I) chloride", "[Cu]Cl", e2 + ep, [
            field("mass", quantity(row["cucl_mass"], "mg"), ep),
            field("amount", quantity(row["cucl_mmol"], "mmol"), ep),
            field("equivalents", quantity(1, "equiv"), ev(1) if row["id"] == "3a" else e2),
        ]),
        participant(dcm, "solvent", "CH2Cl2", "dichloromethane", "ClCCl", e2 + ep, [
            field("volume", quantity(row["vol"], "mL"), ep),
        ]),
        participant(product, "product", row["product"], row["pname"], row["ps"], e2 + ep, [
            field("mass", quantity(row["y_mass"], "mg"), ep),
        ]),
    ]
    if row.get("alt_amine"):
        parts.append(participant("3i_conflicting_amine", "unspecified_agent", None, row["alt_amine"], None, ep))
    conditions = [
        field("atmosphere", "N2", ep),
        field("solvent", "CH2Cl2", e2 + ep),
        field("procedure_temperature", "r.t.", ep),
        field("procedure_time", quantity(row["proc_time"], "h"), ep),
    ]
    if row["table_time"] != row["proc_time"]:
        conditions.append(field("table_time", quantity(row["table_time"], "h"), e2))
    if row["id"] == "3a":
        conditions.append(field("table_temperature", quantity(25, "°C"), ev(1) + e2))
    outcomes = [
        field("table_reactant_ee", quantity(row["table_ree"], "%", qualifier="gt", raw_text=f">{row['table_ree']}%"), e2, [salt]),
        field("procedure_reactant_ee", quantity(row["proc_ree"], "%", qualifier="gt", raw_text=f">{row['proc_ree']}%"), ep, [salt]),
        field("yield", quantity(row["yield"], "%"), e2 + ep, [product]),
        field("product_ee", quantity(row["proc_pee"], "%"), ep, [product]),
        field("yield_measurement_basis", row.get("basis"), e2 if row.get("basis") else [], [product]),
    ]
    if row["table_pee"] != row["proc_pee"]:
        outcomes.append(field("table_product_ee", quantity(row["table_pee"], "%"), e2, [product]))
    notes = [
        ("The starting material is explicitly described as a 1:1 acid–chiral amine salt.", e2),
        ("Absolute configurations of products are described by the authors as tentatively assigned on the basis of the X-ray study of 2e.", e2 + (ev(3) if row["id"] == "3i" else [])),
        (f"Connectivity candidate for the allenoic acid component: {acid_smiles[row['id']]}; the source charges the composite salt and the stereochemical structure is not independently verified.", e2 + ep),
    ]
    unresolved = [
        "No supporting information was explicitly provided or associated.",
        "No workup or purification is reported in the detailed salt procedure.",
        "CuCl is preserved as unspecified_agent because the paper describes stoichiometric CuCl as a mediator and the schema has no mediator role.",
        "The composite salt SMILES is left null; candidate product SMILES does not encode the reported absolute stereochemistry and remains unverified.",
    ]
    if not row.get("basis"):
        unresolved.append("Yield measurement basis is not explicitly stated for this Table 3 entry.")
    if row["table_time"] != row["proc_time"]:
        unresolved.append("Reaction time differs between Table 3 and the detailed procedure; both printed values are retained.")
    if row["table_pee"] != row["proc_pee"]:
        unresolved.append("Product ee differs between Table 3 and the detailed procedure; both printed values are retained.")
    if row["table_ree"] != row["proc_ree"]:
        unresolved.append("Starting-salt ee differs between Table 3 and the detailed procedure; both printed values are retained.")
    if row.get("alt_amine"):
        unresolved.append("For 3i, Table 3 base A denotes L-(−)-cinchonidine, but the detailed procedure names D-(−)-(1-phenylethyl)amine; both identities are retained without choosing one.")
    records.append(record(
        f"scope_{row['id']}", f"Table 3 entry {entry_no} / detailed procedure {row['id']}",
        "substrate_scope_entry", evidence, parts,
        [{"step_id": "cucl_mediated_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
