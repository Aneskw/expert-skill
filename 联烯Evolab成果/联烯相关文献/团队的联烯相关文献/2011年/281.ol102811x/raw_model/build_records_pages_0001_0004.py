#!/usr/bin/env python3
"""Build source-linked machine records for PDF pages 1--4 of ol102811x."""
import json
from pathlib import Path

DOC = "doc_a86ec75fede7c9fe"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(*pages):
    return [f"{DOC}:page{p}:{kind}" for p in pages for kind in ("image", "text")]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, target=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = [target]
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(record_id, source_id, kind, evidence, participants, conditions, outcomes,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{record_id}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting Information was not supplied or explicitly associated; atmosphere, workup, purification, and omitted operational details remain missing.",
                "Complex bridged product structure is retained by source label/drawing with null SMILES pending chemical review.",
            ],
        },
    }


def amount(name, number, unit, evidence, raw_text=None):
    return field(name, qty(number, unit, raw_text), evidence)


def common_table1(evidence, catalyst, ligand, solvent, sieve, concentration, imine_equiv):
    participants = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    "dimethyl 2-(buta-2,3-dien-1-yl)malonate",
                    "C=C=CCC(C(=O)OC)C(=O)OC",
                    [amount("concentration", concentration, "M", evidence,
                            f"[1a] = {concentration} mmol/mL")]),
        participant("imine_2", "reactant", "2", evidence,
                    "o-iodobenzaldehyde N-tosyl imine",
                    "Cc1ccc(S(=O)(=O)N=Cc2ccccc2I)cc1",
                    [amount("equivalents", imine_equiv, "equiv", evidence)]),
        participant("product_3a", "product", "3a", evidence,
                    "aza-bridged benzo[a,d]cycloheptene 3a"),
        participant("base_k2co3", "reagent", "K2CO3", evidence,
                    "potassium carbonate", "[K+].[K+].[O-]C([O-])=O",
                    [amount("equivalents", 4, "equiv", evidence)]),
        participant("catalyst", "catalyst", catalyst, evidence, catalyst, None,
                    [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("solvent", "solvent", solvent, evidence, solvent,
                    {"dioxane": "O1CCOCC1", "toluene": "Cc1ccccc1", "MeCN": "CC#N"}[solvent]),
        participant("nmr_standard", "unspecified_agent", "CH2Br2", evidence,
                    "dibromomethane", "BrCBr"),
    ]
    if ligand:
        participants.append(participant("ligand", "reagent", ligand, evidence, ligand, None,
                                        [amount("ligand_loading", 10, "mol%", evidence)]))
    if sieve:
        participants.append(participant(
            "molecular_sieves", "reagent", "4 Å MS", evidence, "4 Å molecular sieves", None,
            [amount("mass_per_1_mL", sieve, "mg", evidence, f"{sieve} mg/mL"),
             amount("reference_volume", 1, "mL", evidence, f"{sieve} mg/mL")],
        ))
    return participants


records = []

# Table 1: ten distinct optimization rows. Entry 10 is reconciled with Table 2 entry 1 below.
table1 = [
    (1, "Pd(OAc)2", "PPh3", "dioxane", 10.5, 0, None, 0.033, 2.0),
    (2, "Pd(OAc)2", "PPh3", "toluene", 17.5, 17, None, 0.033, 2.0),
    (3, "Pd(OAc)2", "PPh3", "MeCN", 5.5, 38, None, 0.033, 2.0),
    (4, "Pd(OAc)2", "TFP", "MeCN", 3, 49, None, 0.033, 2.0),
    (5, "Pd(dba)2", "TFP", "MeCN", 47, 30, None, 0.033, 2.0),
    (6, "Pd(OAc)2", "TFP", "MeCN", 7.5, 62, 61.3, 0.033, 2.0),
    (7, "Pd(OAc)2", None, "MeCN", 3.5, 80, 61.3, 0.033, 2.0),
    (8, "Pd(OAc)2", None, "MeCN", 3.5, 80, 12.2, 0.033, 2.0),
    (9, "Pd(OAc)2", None, "MeCN", 3.5, 80, 12.2, 0.067, 2.0),
    (10, "Pd(OAc)2", None, "MeCN", 3.5, 80, 12.2, 0.067, 1.5),
]
for entry, catalyst, ligand, solvent, hours, nmr_yield, sieve, conc, imine_eq in table1:
    pages = (2, 3) if entry == 10 else (2,)
    evidence = ev(*pages)
    rid = "table1_entry10_table2_entry1" if entry == 10 else f"table1_entry{entry}"
    sid = "Table 1 entry 10 / Table 2 entry 1" if entry == 10 else f"Table 1 entry {entry}"
    outcomes = [
        field("reported_NMR_yield", qty(nmr_yield, "%"), ev(2), "product_3a"),
        field("yield_measurement_basis", "NMR using CH2Br2 as internal standard", ev(2), "product_3a"),
    ]
    if entry == 10:
        outcomes += [
            field("reported_isolated_yield", qty(77, "%"), evidence, "product_3a"),
            field("isolated_yield_measurement_basis", "isolated", evidence, "product_3a"),
        ]
    notes = ["Table 1 entry 1 is an unsuccessful condition: expected 3a was reported at 0% NMR yield."] if entry == 1 else []
    if entry == 10:
        notes.append("This is the same optimized 1a + 2 -> 3a batch repeated as Table 2 entry 1; it is not duplicated.")
    records.append(record(
        rid, sid, "optimization_entry", evidence,
        common_table1(evidence, catalyst, ligand, solvent, sieve, conc, imine_eq),
        [field("solvent", solvent, evidence),
         field("temperature", qty(80, "°C"), evidence),
         field("time", qty(hours, "h"), evidence)],
        outcomes, notes,
    ))


# Table 2 entries 2--5; entry 1 was merged into Table 1 entry 10.
table2 = [
    (2, "Ph", "1b", 7, 94, "3b"),
    (3, "Bn", "1c", 6.2, 95, "3c"),
    (4, "n-C4H9", "1d", 4, 94, "3d"),
    (5, "Allyl", "1e", 3, 91, "3e"),
]
for entry, r1, substrate_label, hours, isolated_yield, product_label in table2:
    evidence = ev(3)
    participants = [
        participant("substrate_1", "reactant", substrate_label, evidence,
                    f"2,3-allenyl malonate {substrate_label} (R1 = {r1})", None,
                    [amount("concentration", 0.067, "M", evidence, "[1] = 0.067 mmol/mL")]),
        participant("imine_2", "reactant", "2", evidence, "o-iodobenzaldehyde N-tosyl imine",
                    "Cc1ccc(S(=O)(=O)N=Cc2ccccc2I)cc1",
                    [amount("equivalents", 1.5, "equiv", evidence)]),
        participant("product_3", "product", product_label, evidence,
                    f"aza-bridged benzo[a,d]cycloheptene {product_label} (R1 = {r1})"),
        participant("catalyst", "catalyst", "Pd(OAc)2", evidence, "palladium(II) acetate", None,
                    [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("base", "reagent", "K2CO3", evidence, "potassium carbonate",
                    "[K+].[K+].[O-]C([O-])=O", [amount("equivalents", 4, "equiv", evidence)]),
        participant("molecular_sieves", "reagent", "4 Å MS", evidence, "4 Å molecular sieves", None,
                    [amount("mass_per_1_mL", 12.2, "mg", evidence, "12.2 mg/mL"),
                     amount("reference_volume", 1, "mL", evidence, "12.2 mg/mL")]),
        participant("solvent", "solvent", "MeCN", evidence, "acetonitrile", "CC#N"),
    ]
    records.append(record(
        f"table2_entry{entry}", f"Table 2 entry {entry}", "substrate_scope_entry", evidence,
        participants,
        [field("solvent", "MeCN", evidence), field("temperature", qty(80, "°C"), evidence),
         field("time", qty(hours, "h"), evidence)],
        [field("reported_isolated_yield", qty(isolated_yield, "%"), evidence, "product_3"),
         field("yield_measurement_basis", "isolated", evidence, "product_3"),
         field("product_selectivity", "only bridged product 3 observed by 1H NMR of the crude product", evidence, "product_3")],
        ["D-type, E-type, and bridged G products were reported as not formed."],
    ))


def common_table3(evidence, substrate_label, substrate_name, product_label):
    return [
        participant("allenol_4", "reactant", substrate_label, evidence, substrate_name),
        participant("aldehyde_5", "reactant", "5", evidence, "o-iodobenzaldehyde", "O=Cc1ccccc1I",
                    [amount("equivalents", 1, "equiv", evidence)]),
        participant("product_6", "product", product_label, evidence, f"oxa-bridged benzocycloheptane {product_label}"),
        participant("catalyst", "catalyst", "Pd(OAc)2", evidence, "palladium(II) acetate", None,
                    [amount("catalyst_loading", 5, "mol%", evidence)]),
        participant("ligand", "reagent", "TFP", evidence, "tri(2-furyl)phosphine", None,
                    [amount("ligand_loading", 10, "mol%", evidence)]),
        participant("base", "reagent", "K2CO3", evidence, "potassium carbonate",
                    "[K+].[K+].[O-]C([O-])=O", [amount("equivalents", 4, "equiv", evidence)]),
        participant("solvent", "solvent", "MeCN", evidence, "acetonitrile", "CC#N"),
    ]


# Two explicitly quantified ligand-control experiments in the page-3 prose.
for suffix, ligand_present, yield_value in (("without_tfp", False, 56), ("with_tfp", True, 70)):
    evidence = ev(3)
    participants = [
        participant("allenol_4a", "reactant", "4a", evidence, "2,3-butadien-1-ol 4a", "C=C=CCO"),
        participant("aldehyde_5", "reactant", "5", evidence, "o-iodobenzaldehyde", "O=Cc1ccccc1I"),
        participant("product_6a", "product", "6a", evidence, "oxa-bridged benzocycloheptane 6a"),
    ]
    if ligand_present:
        participants.append(participant("ligand", "reagent", "TFP", evidence, "tri(2-furyl)phosphine"))
    records.append(record(
        f"prose_control_{suffix}", f"page 3 prose control ({suffix.replace('_', ' ')})",
        "optimization_entry", evidence, participants,
        [field("solvent", None, evidence), field("temperature", None, evidence),
         field("time", None, evidence)],
        [field("reported_yield", qty(yield_value, "%"), evidence, "product_6a"),
         field("yield_measurement_basis", None, evidence, "product_6a")],
        ["The prose reports 70% with TFP versus 56% without TFP and states that 4 Å molecular sieves were not required."],
        [
            "Exact catalyst/base loadings, substrate ratio, solvent, temperature, time, and yield measurement basis are not restated for this control and were not inferred from Table 3.",
            "The molecular-sieve comparison is qualitative; no separate numerical outcome is given.",
            "Complex bridged product structure is retained by source label/drawing with null SMILES pending chemical review.",
        ],
    ))


# Table 3: ten racemic substrate-scope rows.
table3 = [
    (1, "H", "H", "4a", 4.5, 75, "6a"),
    (2, "H", "n-C7H15", "4b", 10.5, 73, "6b"),
    (3, "H", "Ph", "4c", 52.8, 87, "6c"),
    (4, "H", "Bn", "4d", 11, 68, "6d"),
    (5, "H", "allyl", "4e", 19, 66, "6e"),
    (6, "Ph", "H", "4f", 2.5, 92, "6f"),
    (7, "2-BrC6H4", "H", "4g", 13.5, 90, "6g"),
    (8, "2-MeOC6H4", "H", "4h", 21, 88, "6h"),
    (9, "n-C6H13", "H", "4i", 6, 90, "6i"),
    (10, "4-ClC6H4", "H", "4j", 6.5, 77, "6j"),
]
for entry, r1, r2, substrate_label, hours, isolated_yield, product_label in table3:
    evidence = ev(3)
    name = f"2,3-allenol {substrate_label} (R1 = {r1}; R2 = {r2})"
    participants = common_table3(evidence, substrate_label, name, product_label)
    participants[0]["amounts"] = [amount("concentration", 0.1, "M", evidence, "[4] = 0.1 mmol/mL")]
    if entry == 1:
        participants[0]["smiles"] = fact("C=C=CCO", evidence)
    outcomes = [
        field("reported_isolated_yield", qty(isolated_yield, "%"), evidence, "product_6"),
        field("yield_measurement_basis", "isolated", evidence, "product_6"),
    ]
    if entry >= 6:
        outcomes.append(field("diastereoselectivity", "one diastereomer observed by 1H NMR of the crude reaction mixture", evidence, "product_6"))
    records.append(record(
        f"table3_entry{entry}", f"Table 3 entry {entry}", "substrate_scope_entry", evidence,
        participants,
        [field("solvent", "MeCN", evidence), field("temperature", qty(80, "°C"), evidence),
         field("time", qty(hours, "h"), evidence)],
        outcomes,
        ["D-type, E-type, and bridged G products were reported as not formed in this scope."],
    ))


# Table 4: five enantioenriched substrate-scope rows.
table4 = [
    (1, "Ph", "(S)-4f", 2.5, 92, "(1R,9R,10R)-6f", 98.0),
    (2, "Ph", "(R)-4f", 2, 91, "(1S,9S,10S)-6f", 97.9),
    (3, "2-BrC6H4", "(S)-4g", 13.5, 91, "(1R,9R,10R)-6g", 99.8),
    (4, "n-C6H13", "(R)-4i", 6.5, 90, "(1S,9R,10R)-6i", 99.8),
    (5, "4-ClC6H4", "(S)-4j", 3.5, 84, "(1R,9R,10R)-6j", 99.8),
]
for entry, r_group, substrate_label, hours, isolated_yield, product_label, ee_value in table4:
    evidence = ev(4)
    participants = common_table3(
        evidence, substrate_label,
        f"optically active 2,3-allenol {substrate_label} (R = {r_group})", product_label,
    )
    participants[0]["amounts"] = [amount("concentration", 0.1, "M", evidence, "[4] = 0.1 mmol/mL")]
    records.append(record(
        f"table4_entry{entry}", f"Table 4 entry {entry}", "substrate_scope_entry", evidence,
        participants,
        [field("solvent", "MeCN", evidence), field("temperature", qty(80, "°C"), evidence),
         field("time", qty(hours, "h"), evidence)],
        [field("reported_isolated_yield", qty(isolated_yield, "%"), evidence, "product_6"),
         field("yield_measurement_basis", "isolated", evidence, "product_6"),
         field("product_ee", qty(ee_value, "%"), evidence, "product_6"),
         field("diastereoselectivity", "excellent de (qualitative; no numeric de reported)", evidence, "product_6")],
        ["The paper states that no reracemization occurred; exact substrate ee is not tabulated on this page."],
    ))


assert len(records) == 31
assert len({r["record_id"] for r in records}) == len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
