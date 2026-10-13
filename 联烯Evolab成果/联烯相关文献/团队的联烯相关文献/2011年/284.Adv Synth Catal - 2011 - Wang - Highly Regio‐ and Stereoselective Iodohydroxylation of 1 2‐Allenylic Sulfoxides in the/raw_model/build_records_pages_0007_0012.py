"""Build/extend evidence-linked records from PDF pages 7--12.

The script deliberately updates existing page-1--6 records when the
experimental section describes the same batch.  Only four genuinely new
experiments are introduced.  All output remains machine extracted and is
intended for reaction_tools.py merge (therefore needs_review).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path


DOC = "doc_f68af135ec78d163"
BASE = Path(__file__).parents[1]
DATASET = BASE / "dataset.json"
OUT = Path(__file__).with_name("records_pages_0007_0012.json")


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


SMILES = {
    "Et3N": "CCN(CC)CC",
    "CH2Cl2": "ClCCl",
    "MeI": "CI",
    "H2O": "O",
    "MeCN": "CC#N",
    "BnSH": "SCC1=CC=CC=C1",
    "I2": "II",
    "Na2SO4": "[Na+].[Na+].[O-]S(=O)(=O)[O-]",
    "MgSO4": "[Mg+2].[O-]S(=O)(=O)[O-]",
    "m-CPBA": "OOC(=O)c1cccc(Cl)c1",
    "1-hexyne": "CCCCC#C",
    "DMSO": "CS(C)=O",
    "DME": "COCCOC",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "Na2CO3": "[Na+].[Na+].[O-]C([O-])=O",
    "undec-1-yn-3-ol": "C#CC(O)CCCCCCCC",
    "dodeca-1-yn-3-ol": "C#CC(O)CCCCCCCCC",
    "3-methylhex-1-yn-3-ol": "C#CC(O)(C)CCC",
    "1,2-undecadienyl phenyl sulfoxide (1i)": "O=S(c1ccccc1)C=C=CCCCCCCCC",
    "1,2-dodecadienyl phenyl sulfoxide (1j)": "O=S(c1ccccc1)C=C=CCCCCCCCCC",
    "3-methylhexa-1,2-dienyl phenyl sulfoxide (1r)": "O=S(c1ccccc1)C=C=C(C)CCC",
}


def participant(entity_id, role, label, evidence, amounts=None, smiles_key=None):
    smiles = SMILES.get(smiles_key or label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def empty_record(suffix, page, participants, steps, outcomes, notes=None, unresolved=None):
    evidence = ev(page)
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": "reported_experiment",
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": (unresolved or []) + [
                "Machine extraction requires source review; molecular structures are not independently verified.",
                "Supporting information was mentioned by the article but was not explicitly supplied or associated.",
            ],
        },
    }


data = json.loads(DATASET.read_text())
existing = {r["record_id"]: r for r in data["experiments"]}
updates = []


def get(suffix: str, pages: list[int]):
    rid = f"{DOC}:{suffix}"
    rec = copy.deepcopy(existing[rid])
    for page in pages:
        for evidence_id in ev(page):
            if evidence_id not in rec["evidence_ids"]:
                rec["evidence_ids"].append(evidence_id)
    return rec


def part(rec, entity_id):
    return next(p for p in rec["participants"] if p["entity_id"] == entity_id)


def add_part(rec, entity_id, role, label, evidence, smiles_key=None):
    current = next((p for p in rec["participants"] if p["entity_id"] == entity_id), None)
    if current is None:
        current = participant(entity_id, role, label, evidence, smiles_key=smiles_key)
        rec["participants"].append(current)
        for step in rec["steps"]:
            if entity_id not in step["participant_ids"]:
                step["participant_ids"].append(entity_id)
    return current


def amount(rec, entity_id, name, value, evidence):
    part(rec, entity_id)["amounts"].append(fld(name, value, evidence))


def condition(rec, name, value, evidence, step_id="reaction"):
    step = next(s for s in rec["steps"] if s["step_id"] == step_id)
    step["conditions"].append(fld(name, value, evidence))


def outcome(rec, name, value, evidence, targets=None):
    rec["outcomes"].append(fld(name, value, evidence, targets))


def note(rec, text, evidence):
    rec["notes"].append(fact(text, evidence))


def unresolved(rec, text):
    if text not in rec["review"]["unresolved"]:
        rec["review"]["unresolved"].append(text)


# Page 7: three starting-material preparations not represented in pages 1--6.
e7 = ev(7)

start_1i = [
    participant("undecynol", "reactant", "undec-1-yn-3-ol", e7,
                [fld("mass", qty(1.69, "g"), e7), fld("amount", qty(10, "mmol"), e7)]),
    participant("et3n", "reagent", "triethylamine", e7,
                [fld("volume", qty(1.70, "mL"), e7), fld("amount", qty(12, "mmol"), e7),
                 fld("mass", qty(1.22, "g"), e7)], "Et3N"),
    participant("sulfenyl_chloride", "reagent", "sulfenyl chloride (identity not further specified in the paragraph)", e7,
                [fld("mass", qty(1.74, "g"), e7), fld("amount", qty(12, "mmol"), e7)]),
    participant("methyl_iodide", "reagent", "methyl iodide", e7,
                [fld("volume", qty(0.1, "mL"), e7), fld("amount", qty(1.6, "mmol"), e7),
                 fld("mass", qty(0.23, "g"), e7)], "MeI"),
    participant("ch2cl2", "solvent", "CH2Cl2", e7, [fld("volume", qty(20, "mL"), e7)], "CH2Cl2"),
    participant("product_1i", "product", "1,2-undecadienyl phenyl sulfoxide (1i)", e7),
]
steps_1i = [
    {"step_id": "reaction", "participant_ids": [p["entity_id"] for p in start_1i], "conditions": [
        fld("initial_temperature", qty(-70, "°C"), e7),
        fld("sulfenyl_chloride_addition_time", qty(5, "min"), e7),
        fld("post_addition_stirring_time", qty(10, "min"), e7),
        fld("operation", "methyl iodide added after 10 min; mixture allowed to warm naturally to room temperature", e7),
    ]},
    {"step_id": "workup", "participant_ids": ["product_1i", "ch2cl2"], "conditions": [
        fld("workup", "quenched with 10 mL water; layers separated; aqueous layer extracted with 10 mL CH2Cl2; combined organics dried over anhydrous Na2SO4, filtered and evaporated", e7),
        fld("purification", "silica-gel chromatography, petroleum ether/ethyl acetate = 8/1", e7),
    ]},
]
updates.append(empty_record(
    "experimental_starting_material_1i", 7, start_1i, steps_1i,
    [fld("isolated_mass_1i", qty(1.68, "g"), e7, ["product_1i"]),
     fld("isolated_yield_1i", qty(61, "%"), e7, ["product_1i"])],
    notes=["Triethylamine density was reported as 0.72 g/mL; product was an oil."],
    unresolved=["The solvent and concentration of the sulfenyl chloride addition solution are not stated; room-temperature duration is not stated."],
))


def abbreviated_starting_record(suffix, product_label, alcohol_label, values, temperature, product_mass, product_yield):
    evidence = e7
    alcohol_mass, alcohol_mmol, et_vol, et_mmol, et_mass, sc_mass, sc_mmol, mei_vol, mei_mmol, mei_mass = values
    ps = [
        participant("propargylic_alcohol", "reactant", alcohol_label, evidence,
                    [fld("mass", qty(alcohol_mass, "g"), evidence), fld("amount", qty(alcohol_mmol, "mmol"), evidence)]),
        participant("et3n", "reagent", "triethylamine", evidence,
                    [fld("volume", qty(et_vol, "mL"), evidence), fld("amount", qty(et_mmol, "mmol"), evidence),
                     fld("mass", qty(et_mass, "g"), evidence)], "Et3N"),
        participant("sulfenyl_chloride", "reagent", "sulfenyl chloride (identity not further specified in the paragraph)", evidence,
                    [fld("mass", qty(sc_mass, "g"), evidence), fld("amount", qty(sc_mmol, "mmol"), evidence)]),
        participant("methyl_iodide", "reagent", "methyl iodide", evidence,
                    [fld("volume", qty(mei_vol, "mL"), evidence), fld("amount", qty(mei_mmol, "mmol"), evidence),
                     fld("mass", qty(mei_mass, "g"), evidence)], "MeI"),
        participant("product", "product", product_label, evidence),
    ]
    if suffix == "experimental_starting_material_1j":
        ps.append(participant("ch2cl2", "solvent", "CH2Cl2", evidence,
                              [fld("volume", qty(20, "mL"), evidence)], "CH2Cl2"))
    conds = []
    if temperature is not None:
        conds.append(fld("temperature", qty(temperature, "°C"), evidence))
    conds.append(fld("operation", "abbreviated preparation reported without a full step-by-step restatement", evidence))
    return empty_record(
        suffix, 7, ps,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps], "conditions": conds},
         {"step_id": "purification", "participant_ids": ["product"], "conditions": [
             fld("purification", "silica-gel chromatography, petroleum ether/ethyl acetate = 4/1", evidence)
         ]}],
        [fld("isolated_mass", qty(product_mass, "g"), evidence, ["product"]),
         fld("isolated_yield", qty(product_yield, "%"), evidence, ["product"])],
        notes=["Triethylamine density was reported as 0.72 g/mL; methyl iodide density was reported as 2.28 g/mL; product was an oil."],
        unresolved=["Duration, atmosphere and full workup are not restated in this abbreviated experiment."
                    + ("" if suffix.endswith("1j") else " Solvent and temperature are also not stated.")],
    )


updates.append(abbreviated_starting_record(
    "experimental_starting_material_1j", "1,2-dodecadienyl phenyl sulfoxide (1j)", "dodeca-1-yn-3-ol",
    (1.41, 7.7, 1.10, 7.8, 0.79, 0.92, 7.7, 0.4, 6.4, 0.91), -65, 1.29, 57,
))
updates.append(abbreviated_starting_record(
    "experimental_starting_material_1r", "3-methylhexa-1,2-dienyl phenyl sulfoxide (1r)", "3-methylhex-1-yn-3-ol",
    (3.73, 33, 4.2, 33, 3.02, 4.44, 30, 0.68, 10.9, 1.55), None, 3.10, 47,
))


# Detailed E-3a batch is the same experiment summarized in Eq. (1).
rec = get("eq1_1a_iodohydroxylation", [7])
amount(rec, "substrate_1a", "mass", qty(82.3, "mg"), e7)
amount(rec, "substrate_1a", "amount", qty(0.5, "mmol"), e7)
amount(rec, "iodine", "mass", qty(195.1, "mg"), e7)
amount(rec, "iodine", "amount", qty(0.77, "mmol"), e7)
amount(rec, "bnsh", "mass", qty(63.1, "mg"), e7)
amount(rec, "bnsh", "amount", qty(0.5, "mmol"), e7)
amount(rec, "mecn", "substrate_solution_volume", qty(4, "mL"), e7)
amount(rec, "mecn", "BnSH_solution_volume", qty(2, "mL"), e7)
eprod = add_part(rec, "product_E3a", "product", "E-3a", e7)
zprod = add_part(rec, "product_Z3a", "product", "Z-3a", e7)
condition(rec, "iodine_pretreatment_time", qty(5, "min"), e7)
condition(rec, "workup", "quenched with 6 mL water, then saturated aqueous Na2S2O3; extracted with CH2Cl2 (25 mL x 3), dried over anhydrous MgSO4, filtered and evaporated", e7)
condition(rec, "purification", "silica-gel chromatography, petroleum ether/ethyl acetate = 10/1 to 2/1", e7)
outcome(rec, "isolated_mass_E3a", qty(74.0, "mg"), e7, [eprod["entity_id"]])
outcome(rec, "isolated_yield_E3a", qty(51, "%"), e7, [eprod["entity_id"]])
outcome(rec, "isolated_mass_Z3a", qty(3.3, "mg"), e7, [zprod["entity_id"]])
outcome(rec, "isolated_yield_Z3a", qty(2, "%"), e7, [zprod["entity_id"]])
note(rec, "The experimental-section component yields (51% E plus 2% Z) reconcile with the 53% combined yield reported in Eq. (1).", e7)
updates.append(rec)


# Table 2 rows: detailed experimental paragraphs and byproduct yields.
mono = [
    # suffix, page, substrate mass, BnSH mass, E mass/yield, Z mass/yield, E4 mass/yield
    ("table2_entry2_1b", 7, 70.6, 50.8, 84.7, 70, 3.4, 3, 16.8, 13),
    ("table2_entry3_1c", 7, 76.7, 49.3, 98.9, 77, 5.7, 4, 16.7, 12),
    ("table2_entry4_1d", 8, 81.5, 50.1, 98.8, 75, 3.1, 2, 23.9, 17),
    ("table2_entry5_1e", 8, 88.8, 50.5, 93.7, 67, 2.0, 1, 15.9, 11),
    ("table2_entry6_1f", 8, 94.2, 50.7, 104.9, 72, None, None, 19.0, 12),
    ("table2_entry7_1g", 8, 98.6, 49.7, 121.3, 81, None, None, 27.1, 17),
    ("table2_entry8_1h", 8, 104.6, 50.3, 101.8, 65, None, None, 16.2, 10),
    ("table2_entry9_1i", 8, 109.6, 50.4, 114.6, 71, 2.1, 1, 9.4, 6),
    ("table2_entry10_1j", 8, 115.5, 49.3, 127.5, 77, 4.8, 3, 27.1, 16),
    ("table2_entry11_1k", 9, 96.5, 50.2, 109.3, 74, None, None, 13.6, 9),
]
for suffix, page, substrate_mass, bnsh_mass, e_mass, e_yield, z_mass, z_yield, e4_mass, e4_yield in mono:
    evidence = list(dict.fromkeys(ev(page) + e7))
    rec = get(suffix, [page, 7])
    amount(rec, "substrate", "mass", qty(substrate_mass, "mg"), ev(page))
    amount(rec, "bnsh", "mass", qty(bnsh_mass, "mg"), ev(page))
    amount(rec, "water", "volume", qty(14.5, "uL"), ev(page))
    amount(rec, "iodine", "solution_volume", qty(3.0, "mL"), ev(page))
    amount(rec, "iodine", "solution_concentration", qty(0.2, "M"), ev(page))
    e_part = part(rec, "product_E3")
    e4_part = add_part(rec, "product_E4", "product", "corresponding E-4 byproduct", ev(page))
    if z_mass is not None:
        z_part = add_part(rec, "product_Z3", "product", "corresponding Z-3 isomer", ev(page))
        outcome(rec, "isolated_mass_Z3", qty(z_mass, "mg"), ev(page), [z_part["entity_id"]])
        outcome(rec, "isolated_yield_Z3", qty(z_yield, "%"), ev(page), [z_part["entity_id"]])
    outcome(rec, "isolated_mass_E3", qty(e_mass, "mg"), ev(page), [e_part["entity_id"]])
    outcome(rec, "isolated_mass_E4", qty(e4_mass, "mg"), ev(page), [e4_part["entity_id"]])
    outcome(rec, "isolated_yield_E4", qty(e4_yield, "%"), ev(page), [e4_part["entity_id"]])
    note(rec, "This paragraph states that the compound was prepared according to the detailed E-3b procedure on page 7.", evidence)
    if suffix.endswith("1b"):
        condition(rec, "iodine_solution_addition_time", qty(4, "min"), e7)
        condition(rec, "post_addition_stirring_time", qty(30, "min"), e7)
        condition(rec, "workup_detail", "quenched with 6 mL water at -20 °C and saturated aqueous Na2S2O3 at 0 °C; extracted with CH2Cl2 (20 mL x 3), washed with brine and dried over anhydrous Na2SO4", e7)
        condition(rec, "purification", "filtration, evaporation and silica-gel chromatography, petroleum ether/ethyl acetate = 20/1 to 2/1", e7)
        note(rec, "The 4 min addition plus 30 min stirring explains the 34 min table duration.", e7)
    updates.append(rec)


# Detailed Table 3 entry 5 (E-3l/E-4l isolated-yield batch).
e9 = ev(9)
rec = get("table3_entry5", [9])
amount(rec, "substrate_1l", "mass", qty(92.1, "mg"), e9)
amount(rec, "bnsh", "mass", qty(50.4, "mg"), e9)
amount(rec, "water", "amount", qty(4, "mmol"), e9)
amount(rec, "water", "volume", qty(72, "uL"), e9)
amount(rec, "iodine", "amount", qty(0.48, "mmol"), e9)
amount(rec, "iodine", "solution_concentration", qty(0.267, "M"), e9)
condition(rec, "iodine_solution_addition_time", qty(1, "min"), e9)
condition(rec, "post_addition_stirring_time", qty(45, "min"), e9)
condition(rec, "workup_detail", "quenched sequentially with 6 mL water at -40 °C and saturated aqueous Na2S2O3 at 0 °C; extracted with CH2Cl2 (20 mL x 3), washed with brine and dried over anhydrous Na2SO4", e9)
condition(rec, "purification", "filtration, evaporation and silica-gel chromatography, petroleum ether/ethyl acetate = 40/1 to 3/1", e9)
outcome(rec, "isolated_mass_E3l", qty(95.3, "mg"), e9, ["product_E3l"])
outcome(rec, "isolated_mass_E4l", qty(35.6, "mg"), e9, ["product_E4l"])
note(rec, "The detailed procedure reports 1 min iodine addition followed by 45 min stirring; Table 3 reports 46 min total.", e9)
updates.append(rec)


# Table 4 rows: exact masses and E-4 byproduct yields, inheriting E-3l workup.
poly = [
    ("table4_entry1_1m", 9, 77.0, 50.0, 76.6, 60, 27.2, 20),
    ("table4_entry2_1n", 9, 88.6, 49.6, 99.9, 71, 15.1, 10),
    ("table4_entry3_1o", 9, 107.8, 50.5, 101.9, 64, 43.4, 26),
    ("table4_entry4_1p", 9, 92.6, 50.7, 96.4, 67, 42.5, 28),
    ("table4_entry5_1q", 9, 82.7, 50.3, 84.1, 63, 35.8, 25),
    ("table4_entry6_1r", 10, 89.0, 50.2, 96.5, 69, 41.0, 28),
    ("table4_entry7_1s", 10, 101.4, 50.4, 95.1, 62, 42.8, 27),
    ("table4_entry8_1t", 10, 99.4, 50.2, 99.7, 66, 28.7, 18),
]
for suffix, page, substrate_mass, bnsh_mass, e_mass, e_yield, e4_mass, e4_yield in poly:
    pages = [page, 9] if page == 10 or suffix.endswith("1r") else [page]
    rec = get(suffix, pages)
    ep = ev(page)
    amount(rec, "substrate", "mass", qty(substrate_mass, "mg"), ep)
    amount(rec, "bnsh", "mass", qty(bnsh_mass, "mg"), ep)
    amount(rec, "iodine", "solution_concentration", qty(0.2 if suffix.endswith("1o") else 0.267, "M"), ep)
    if suffix.endswith("1o"):
        # Entry 3 explicitly used the 3.0 mL, 0.2 M / 1.5 equiv override.
        amount(rec, "iodine", "solution_volume_detailed", qty(3.0, "mL"), ep)
    e4 = add_part(rec, "product_E4", "product", "corresponding E-4 byproduct", ep)
    outcome(rec, "isolated_mass_E3", qty(e_mass, "mg"), ep, ["product_E3"])
    outcome(rec, "isolated_mass_E4", qty(e4_mass, "mg"), ep, [e4["entity_id"]])
    outcome(rec, "isolated_yield_E4", qty(e4_yield, "%"), ep, [e4["entity_id"]])
    note(rec, "The paragraph reports this compound as prepared according to the detailed E-3l procedure on page 9.", list(dict.fromkeys(ep + e9)))
    updates.append(rec)


# Chiral E-3g batch (Eq. 3) with exact quantities and HPLC basis.
e10 = ev(10)
rec = get("eq3_chiral_1g_iodohydroxylation", [10])
amount(rec, "substrate_R1g", "mass", qty(99.5, "mg"), e10)
amount(rec, "substrate_R1g", "amount", qty(0.4, "mmol"), e10)
amount(rec, "bnsh", "mass", qty(48.8, "mg"), e10)
amount(rec, "bnsh", "amount", qty(0.4, "mmol"), e10)
amount(rec, "water", "amount", qty(0.8, "mmol"), e10)
amount(rec, "water", "volume", qty(14.5, "uL"), e10)
amount(rec, "iodine", "solution_volume", qty(3.0, "mL"), e10)
amount(rec, "iodine", "solution_concentration", qty(0.2, "M"), e10)
outcome(rec, "isolated_mass_RE3g", qty(117.4, "mg"), e10, ["product_RE3g"])
outcome(rec, "ee_measurement_basis", "HPLC, Chiralcel OD-H, hexane/i-PrOH = 95/5, 0.8 mL min-1, 254 nm", e10)
updates.append(rec)


# Detailed E-4f oxidation, same batch as Scheme 4.
rec = get("scheme4_E3f_oxidation_E4f", [10])
amount(rec, "substrate_E3f", "mass", qty(73.3, "mg"), e10)
amount(rec, "substrate_E3f", "amount", qty(0.2, "mmol"), e10)
amount(rec, "mcpba", "mass", qty(52.2, "mg"), e10)
amount(rec, "mcpba", "amount", qty(0.3, "mmol"), e10)
amount(rec, "ch2cl2", "mCPBA_solution_volume", qty(1, "mL"), e10)
amount(rec, "ch2cl2", "substrate_solution_volume", qty(1, "mL"), e10)
add_part(rec, "nahco3", "reagent", "saturated aqueous NaHCO3", e10)
amount(rec, "nahco3", "volume", qty(2, "mL"), e10)
condition(rec, "workup", "after 2 h, saturated aqueous NaHCO3 was added; layers separated; aqueous layer extracted with CH2Cl2 (10 mL x 3); combined organics dried over Na2SO4, filtered and evaporated", e10)
condition(rec, "purification", "flash chromatography, petroleum ether/ethyl acetate = 4/1", e10)
outcome(rec, "isolated_mass_E4f", qty(64.8, "mg"), e10, ["product_E4f"])
updates.append(rec)


# New racemic E-3g oxidation; it is distinct from the chiral Eq. (4) batch.
ps = [
    participant("substrate_E3g", "reactant", "E-3g", e10,
                [fld("mass", qty(75.6, "mg"), e10), fld("amount", qty(0.2, "mmol"), e10)]),
    participant("mcpba", "reagent", "m-CPBA", e10,
                [fld("mass", qty(51.9, "mg"), e10), fld("amount", qty(0.3, "mmol"), e10)], "m-CPBA"),
    participant("ch2cl2", "solvent", "CH2Cl2", e10, [fld("volume", qty(2, "mL"), e10)], "CH2Cl2"),
    participant("product_E4g", "product", "E-4g", e10),
]
updates.append(empty_record(
    "experimental_E3g_oxidation_E4g", 10, ps,
    [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
        fld("temperature", qty(0, "°C"), e10), fld("time", qty(1, "h"), e10), fld("solvent", "CH2Cl2", e10),
        fld("workup", "prepared according to the preceding E-4f oxidation procedure", e10),
    ]}],
    [fld("isolated_mass_E4g", qty(67.4, "mg"), e10, ["product_E4g"]),
     fld("isolated_yield_E4g", qty(86, "%"), e10, ["product_E4g"])],
    notes=["Product was reported as a white solid."],
    unresolved=["The abbreviated paragraph inherits workup and purification from E-4f but does not restate every operation."],
))


# Detailed chiral E-4g oxidation, same batch as Eq. (4).
rec = get("eq4_RE3g_oxidation", [10])
amount(rec, "substrate_RE3g", "mass", qty(75.9, "mg"), e10)
amount(rec, "substrate_RE3g", "amount", qty(0.2, "mmol"), e10)
amount(rec, "mcpba", "mass", qty(52.2, "mg"), e10)
amount(rec, "mcpba", "amount", qty(0.3, "mmol"), e10)
outcome(rec, "isolated_mass_RE4g", qty(65.8, "mg"), e10, ["product_RE4g"])
outcome(rec, "ee_measurement_basis", "HPLC, Chiralcel AD-H, hexane/i-PrOH = 95/5, 0.7 mL min-1, 254 nm", e10)
condition(rec, "workup", "prepared according to the preceding E-4f oxidation procedure", e10)
updates.append(rec)


# Sonogashira batch, spanning pages 10--11.
e11 = ev(11)
rec = get("scheme4_sonogashira_product6", [10, 11])
amount(rec, "substrate_E3f", "mass", qty(73.0, "mg"), e10)
amount(rec, "substrate_E3f", "amount", qty(0.2, "mmol"), e10)
amount(rec, "et3n", "volume", qty(0.8, "mL"), e10)
amount(rec, "hexyne", "mass", qty(33.2, "mg"), e10)
amount(rec, "hexyne", "amount", qty(0.4, "mmol"), e10)
amount(rec, "pd_cat", "mass", qty(7.1, "mg"), e10)
amount(rec, "pd_cat", "amount", qty(0.01, "mmol"), e10)
amount(rec, "cui", "mass", qty(7.6, "mg"), e10)
amount(rec, "cui", "amount_as_printed", qty(0.4, "mmol"), e10)
amount(rec, "dmso", "volume", qty(0.8, "mL"), e10)
condition(rec, "atmosphere", "nitrogen", e10)
condition(rec, "workup", "cooled to room temperature; 10 mL ethyl ether added; filtered and evaporated", e10)
condition(rec, "purification", "silica-gel chromatography, petroleum ether/ethyl acetate = 40/1", e10)
outcome(rec, "isolated_mass_product_6", qty(57.2, "mg"), e11, ["product_6"])
unresolved(rec, "The source prints CuI as 7.6 mg, 0.4 mmol; this apparent mass/amount inconsistency is preserved without correction.")
updates.append(rec)


# Suzuki batch on page 11.  Keep the scheme's r.t. statement and add the
# detailed procedure's 30 °C value rather than silently choosing one.
rec = get("scheme4_suzuki_product7", [11])
amount(rec, "substrate_E3f", "mass", qty(73.1, "mg"), e11)
amount(rec, "substrate_E3f", "amount", qty(0.2, "mmol"), e11)
amount(rec, "dme", "volume", qty(1, "mL"), e11)
amount(rec, "na2co3", "mass", qty(64.3, "mg"), e11)
amount(rec, "na2co3", "amount", qty(0.6, "mmol"), e11)
amount(rec, "water", "volume", qty(1, "mL"), e11)
amount(rec, "phenylboronic", "mass", qty(27.2, "mg"), e11)
amount(rec, "phenylboronic", "amount", qty(0.22, "mmol"), e11)
amount(rec, "pd_cat", "mass", qty(2.4, "mg"), e11)
amount(rec, "pd_cat", "amount", qty(0.01, "mmol"), e11)
condition(rec, "detailed_procedure_temperature", qty(30, "°C"), e11)
condition(rec, "atmosphere", "nitrogen", e11)
condition(rec, "workup", "after TLC completion, 5 mL ethyl ether was added; mixture filtered and evaporated", e11)
condition(rec, "purification", "silica-gel chromatography, petroleum ether/ethyl acetate = 20/1", e11)
outcome(rec, "isolated_mass_product_7", qty(37.6, "mg"), e11, ["product_7"])
unresolved(rec, "Scheme 4 reports room temperature, whereas the detailed procedure reports 30 °C; both source statements are retained.")
updates.append(rec)


# Detailed Table 5 entry 3 isomerization batch.
rec = get("table5_entry3", [11])
amount(rec, "substrate_E3a", "mass", qty(61.8, "mg"), e11)
amount(rec, "substrate_E3a", "amount", qty(0.21, "mmol"), e11)
amount(rec, "iodine", "mass", qty(82.4, "mg"), e11)
amount(rec, "iodine", "amount", qty(0.32, "mmol"), e11)
amount(rec, "mecn", "volume", qty(3, "mL"), e11)
z3a = add_part(rec, "product_Z3a", "product", "Z-3a", e11)
condition(rec, "workup", "quenched with 6 mL water, then saturated aqueous Na2S2O3; extracted with CH2Cl2 (25 mL x 3), washed with brine and dried over anhydrous MgSO4", e11)
condition(rec, "purification", "after evaporation and NMR ratio determination, silica-gel chromatography with petroleum ether/ethyl acetate = 10/1", e11)
outcome(rec, "isolated_mass_Z3a", qty(56.4, "mg"), e11, [z3a["entity_id"]])
outcome(rec, "isolated_yield_Z3a", qty(91, "%"), e11, [z3a["entity_id"]])
note(rec, "The section heading says isomerization of Z-3a, but the procedure explicitly starts from E-3a and affords Z-3a; the explicit procedure is retained.", e11)
updates.append(rec)


def dedupe(items):
    seen = set()
    result = []
    for item in items:
        key = json.dumps(item, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


for record in updates:
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"]))
    record["notes"] = dedupe(record["notes"])
    record["outcomes"] = dedupe(record["outcomes"])
    for p in record["participants"]:
        p["amounts"] = dedupe(p["amounts"])
    for s in record["steps"]:
        s["participant_ids"] = list(dict.fromkeys(s["participant_ids"]))
        s["conditions"] = dedupe(s["conditions"])


assert len(updates) == 30, len(updates)
assert len({r["record_id"] for r in updates}) == len(updates)
OUT.write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(updates), "new": 4, "updated": 26, "output": str(OUT)}, ensure_ascii=False))
