#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--6 of Gao et al."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DOC = "doc_a5dd7894e70ecebe"


def evidence(*pages: int) -> list[str]:
    ids: list[str] = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, evs: list[str]):
    return {
        "value": value,
        "evidence_ids": list(evs),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number: float, unit: str, raw_text: str | None = None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def field(name: str, value, evs: list[str], targets: list[str] | None = None):
    item = {"name": name, "fact": fact(value, evs)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(
    entity_id: str,
    role: str,
    label: str | None,
    evs: list[str],
    *,
    name: str | None = None,
    smiles: str | None = None,
    amounts: list[tuple[str, object]] | None = None,
):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evs),
        "name": fact(name, evs),
        "smiles": fact(smiles, evs),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evs) for n, v in (amounts or [])],
    }


def record(
    suffix: str,
    kind: str,
    evs: list[str],
    participants: list[dict],
    conditions: list[dict],
    outcomes: list[dict],
    *,
    notes: list[str] | None = None,
    unresolved: list[str] | None = None,
):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evs),
        "participants": participants,
        "steps": [
            {
                "step_id": "reaction",
                "participant_ids": [p["entity_id"] for p in participants],
                "conditions": conditions,
            }
        ],
        "outcomes": outcomes,
        "notes": [fact(n, evs) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved
            or [
                "Machine-extracted record requires source review.",
                "Candidate structures are not source-verified.",
            ],
        },
    }


SMILES_1A = "C=C=C(CCCCCC)C(O)c1ccccc1"
SMILES_2A = "C=C=C(CCCCCC)C(=O)c1ccccc1"


def base_pair(evs: list[str], substrate_amount=qty(0.3, "mmol")):
    return [
        participant(
            "substrate_1a",
            "reactant",
            "1a",
            evs,
            name="2-hexyl-1-phenylbuta-2,3-dien-1-ol",
            smiles=SMILES_1A,
            amounts=[("amount", substrate_amount)],
        ),
        participant(
            "product_2a",
            "product",
            "2a",
            evs,
            name="2-hexyl-1-phenylbuta-2,3-dien-1-one",
            smiles=SMILES_2A,
        ),
    ]


def add_common(
    parts: list[dict],
    evs: list[str],
    *,
    copper="CuCl",
    copper_loading=20,
    phen_loading=20,
    dbad_loading=20,
    base="K2CO3",
    base_amount=qty(2.0, "equiv"),
    solvent="toluene",
    solvent_volume=qty(3, "mL"),
    atmosphere="O2",
):
    parts.extend(
        [
            participant("copper", "catalyst", copper, evs, amounts=[("amount", qty(copper_loading, "mol%"))]),
            participant("phen", "reagent", "phen", evs, name="1,10-phenanthroline", amounts=[("amount", qty(phen_loading, "mol%"))]),
            participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("amount", qty(dbad_loading, "mol%"))]),
            participant("base", "reagent", base, evs, amounts=[("amount", base_amount)]),
            participant("solvent", "solvent", solvent, evs, amounts=[("volume", solvent_volume)]),
            participant("oxidant", "reagent", atmosphere, evs, name="molecular oxygen" if atmosphere == "O2" else atmosphere, smiles="O=O" if atmosphere == "O2" else None),
        ]
    )
    return parts


records: list[dict] = []


# Table 1: base screen, seven independent optimization experiments.
table1 = [
    (1, "K2CO3", 40, 59, "isolated", None, None),
    (2, "Na2CO3", 48, 22, "1H NMR using CH2Br2 as internal standard", 50, "1H NMR"),
    (3, "Cs2CO3", 35, 27, "isolated", 32, "column chromatography"),
    (4, "KHCO3", 45, 15, "1H NMR using CH2Br2 as internal standard", 53, "1H NMR"),
    (5, "KOH", 48, 39, "1H NMR using CH2Br2 as internal standard", 28, "1H NMR"),
    (6, "NEt3", 45, "NR", "1H NMR using CH2Br2 as internal standard", 70, "1H NMR"),
    (7, "DBU", 45, "NR", "1H NMR using CH2Br2 as internal standard", 72, "column chromatography"),
]
for entry, base, hours, yield_value, basis, recovery, recovery_basis in table1:
    evs = evidence(2)
    parts = base_pair(evs)
    base_amount = qty(1.0, "equiv") if entry == 1 else qty(2.0, "equiv")
    copper_loading = 15 if entry == 3 else 20
    if entry == 5:
        base_amount = qty(20, "mol%")
    add_common(parts, evs, copper_loading=copper_loading, base=base, base_amount=base_amount)
    if entry == 5:
        parts.append(participant("molecular_sieves", "reagent", "3 Å MS", evs, name="3 Å molecular sieves", amounts=[("mass", qty(100, "mg"))]))
    outcomes = [
        field("reported_product_yield", qty(yield_value, "%") if isinstance(yield_value, int) else yield_value, evs, ["product_2a"]),
        field("yield_measurement_basis", basis, evs, ["product_2a"]),
    ]
    if recovery is not None:
        outcomes += [
            field("recovered_starting_material_yield", qty(recovery, "%"), evs, ["substrate_1a"]),
            field("recovery_measurement_basis", recovery_basis, evs, ["substrate_1a"]),
        ]
    records.append(
        record(
            f"table1_entry{entry}",
            "optimization_entry",
            evs,
            parts,
            [
                field("temperature", "r.t.", evs),
                field("time", qty(hours, "h"), evs),
                field("atmosphere", "O2 (1 atm)", evs),
                field("workup", None, evs),
                field("purification", None, evs),
            ],
            outcomes,
            notes=["NR is retained as the source table marker and is not converted to numeric zero."] if yield_value == "NR" else [],
            unresolved=["Exact batch masses, workup, and purification are not reported in Table 1.", "Candidate substrate/product structures are not source-verified."],
        )
    )


# Table 2: solvent screen, five independent optimization experiments.
table2 = [
    (1, "toluene", 40, 59, "isolated", None),
    (2, "CH3CN", 48, "NR", None, 64),
    (3, "DCE", 47, 31, "1H NMR using CH2Br2 as internal standard", None),
    (4, "CHCl3", 47, 20, None, 78),
    (5, "DMF", 47, "NR", None, 76),
]
for entry, solvent, hours, yield_value, basis, recovery in table2:
    evs = evidence(2)
    parts = base_pair(evs)
    add_common(parts, evs, base_amount=qty(1.0, "equiv"), solvent=solvent)
    outcomes = [
        field("reported_product_yield", qty(yield_value, "%") if isinstance(yield_value, int) else yield_value, evs, ["product_2a"]),
        field("yield_measurement_basis", basis, evs, ["product_2a"]),
    ]
    if recovery is not None:
        outcomes += [
            field("recovered_starting_material_yield", qty(recovery, "%"), evs, ["substrate_1a"]),
            field("recovery_measurement_basis", "1H NMR", evs, ["substrate_1a"]),
        ]
    records.append(
        record(
            f"table2_entry{entry}",
            "optimization_entry",
            evs,
            parts,
            [field("temperature", "r.t.", evs), field("time", qty(hours, "h"), evs), field("atmosphere", "O2 (1 atm)", evs), field("workup", None, evs), field("purification", None, evs)],
            outcomes,
            notes=["NR is retained as the source table marker and is not converted to numeric zero."] if yield_value == "NR" else [],
            unresolved=["Exact batch masses, workup, and purification are not reported in Table 2.", "The product-yield measurement basis is absent where the row has no isolated/NMR footnote.", "Candidate substrate/product structures are not source-verified."],
        )
    )


# Table 3: ligand screen. L-A = phen; L-B = 2,2'-bipyridine.
ligand_rows = [
    (1, [("L-A", "1,10-phenanthroline", 20)], 40, 61, None),
    (2, [("L-B", "2,2'-bipyridine", 20)], 46, 43, 52),
    (3, [("ligand-1", "4,7-diphenyl-1,10-phenanthroline", 20)], 14.5, 66, None),
    (4, [("ligand-1", "2,9-dimethyl-4,7-diphenyl-1,10-phenanthroline", 20)], 45, "NR", 87),
    (5, [("ligand-1", "iPr-Pybox", 20)], 24, "NR", 82),
    (6, [("ligand-1", "4,7-diphenyl-1,10-phenanthroline", 10), ("L-B", "2,2'-bipyridine", 10)], 45.5, 82, None),
    (7, [("L-A", "1,10-phenanthroline", 17.5), ("L-B", "2,2'-bipyridine", 2.5)], 40, 79, None),
    (8, [("L-A", "1,10-phenanthroline", 15.0), ("L-B", "2,2'-bipyridine", 5.0)], 40, 65, None),
    (9, [("L-A", "1,10-phenanthroline", 12.5), ("L-B", "2,2'-bipyridine", 7.5)], 40, 82, None),
    (10, [("L-A", "1,10-phenanthroline", 10.0), ("L-B", "2,2'-bipyridine", 10.0)], 42, 83, None),
    (11, [("L-A", "1,10-phenanthroline", 7.5), ("L-B", "2,2'-bipyridine", 12.5)], 42, 78, None),
    (12, [("L-A", "1,10-phenanthroline", 5.0), ("L-B", "2,2'-bipyridine", 15.0)], 40, 73, None),
    (13, [("L-A", "1,10-phenanthroline", 2.5), ("L-B", "2,2'-bipyridine", 17.5)], 40, 68, None),
    (14, [("L-A", "1,10-phenanthroline", 5.0), ("NMI", "N-methylimidazole", 7.0)], 35, 17, 52),
]
for entry, ligands, hours, yield_value, recovery in ligand_rows:
    evs = evidence(3)
    scale = qty(0.5, "mmol") if entry == 14 else qty(0.3, "mmol")
    parts = base_pair(evs, scale)
    if entry == 14:
        parts.extend(
            [
                participant("copper", "catalyst", "CuCl", evs, amounts=[("amount", qty(5, "mol%"))]),
                participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("amount", qty(5, "mol%"))]),
                participant("base", "reagent", "t-BuOK", evs, amounts=[("amount", qty(5, "mol%"))]),
                participant("solvent", "solvent", "C6H5F", evs, name="fluorobenzene", amounts=[("volume", qty(5, "mL"))]),
                participant("oxidant", "reagent", "O2", evs, name="molecular oxygen", smiles="O=O"),
            ]
        )
    else:
        parts.extend(
            [
                participant("copper", "catalyst", "CuCl", evs, amounts=[("amount", qty(20, "mol%"))]),
                participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("amount", qty(20, "mol%"))]),
                participant("base", "reagent", "K2CO3", evs, amounts=[("equivalents", qty(1.0, "equiv"))]),
                participant("solvent", "solvent", "toluene", evs, amounts=[("volume", qty(3, "mL"))]),
                participant("oxidant", "reagent", "O2", evs, name="molecular oxygen", smiles="O=O"),
            ]
        )
    for index, (label, name, loading) in enumerate(ligands, 1):
        parts.append(participant(f"ligand_{index}", "reagent", label, evs, name=name, amounts=[("amount", qty(loading, "mol%"))]))
    outcomes = [
        field("reported_product_yield", qty(yield_value, "%") if isinstance(yield_value, int) else yield_value, evs, ["product_2a"]),
        field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", evs, ["product_2a"]),
    ]
    if recovery is not None:
        outcomes += [field("recovered_starting_material_yield", qty(recovery, "%"), evs, ["substrate_1a"]), field("recovery_measurement_basis", "1H NMR", evs, ["substrate_1a"])]
    records.append(
        record(
            f"table3_entry{entry}",
            "optimization_entry",
            evs,
            parts,
            [field("temperature", qty(70, "°C") if entry == 14 else "r.t.", evs), field("time", qty(hours, "h"), evs), field("atmosphere", "O2 (1 atm)", evs), field("workup", None, evs), field("purification", None, evs)],
            outcomes,
            notes=["NR is retained as the source table marker and is not converted to numeric zero."] if yield_value == "NR" else [],
            unresolved=["Exact batch masses, workup, and purification are not reported in Table 3.", "Ligand structure candidates were not encoded from drawings; ligand names/labels are retained.", "Candidate substrate/product structures are not source-verified."],
        )
    )


# Table 4: Cu(I) source screen.
for entry, copper, hours, yield_number in [(1, "CuBr", 40, 68), (2, "CuI", 40, 49), (3, "CuCN", 41, 45)]:
    evs = evidence(4)
    parts = base_pair(evs, None)
    parts.extend(
        [
            participant("copper", "catalyst", copper, evs, amounts=[("amount", qty(20, "mol%"))]),
            participant("phen", "reagent", "phen", evs, name="1,10-phenanthroline", amounts=[("amount", qty(10, "mol%"))]),
            participant("bpy", "reagent", "bpy", evs, name="2,2'-bipyridine", amounts=[("amount", qty(10, "mol%"))]),
            participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("amount", qty(20, "mol%"))]),
            participant("base", "reagent", "K2CO3", evs, amounts=[("equivalents", qty(1.0, "equiv"))]),
            participant("solvent", "solvent", "toluene", evs),
            participant("oxidant", "reagent", "O2", evs, name="molecular oxygen", smiles="O=O"),
        ]
    )
    records.append(
        record(
            f"table4_entry{entry}",
            "optimization_entry",
            evs,
            parts,
            [field("temperature", "r.t.", evs), field("time", qty(hours, "h"), evs), field("atmosphere", "O2 (1 atm)", evs), field("solvent_volume", None, evs), field("workup", None, evs), field("purification", None, evs)],
            [field("isolated_yield", qty(yield_number, "%"), evs, ["product_2a"]), field("yield_measurement_basis", "isolated", evs, ["product_2a"])],
            unresolved=["Reaction scale, solvent volume, exact batch masses, workup, and purification are not reported in Table 4.", "Candidate substrate/product structures are not source-verified."],
        )
    )


scope = {
    1: dict(sub="1a", prod="2a", sub_name="2-hexyl-1-phenylbuta-2,3-dien-1-ol", prod_name="2-hexyl-1-phenylbuta-2,3-dien-1-one", sub_smiles=SMILES_1A, prod_smiles=SMILES_2A, time=10, y=86, page=5, masses=(5.5, 4.7, 5.9, 20.6, 13.7, 69.6, 59.3), eluent="petroleum ether/diethyl ether = 30:1"),
    2: dict(sub="1b", prod="2b", sub_name="2-propyl-1-(4-ethylphenyl)buta-2,3-dien-1-ol", prod_name="2-propyl-1-(4-ethylphenyl)buta-2,3-dien-1-one", sub_smiles="C=C=C(CCC)C(O)c1ccc(CC)cc1", prod_smiles="C=C=C(CCC)C(=O)c1ccc(CC)cc1", time=10, y=83, page=5, masses=(5.3, 4.6, 5.9, 20.8, 13.7, 64.7, 53.0), eluent=None),
    3: dict(sub="1c", prod="2c", sub_name="2-propyl-1-(4-bromophenyl)buta-2,3-dien-1-ol", prod_name="2-propyl-1-(4-bromophenyl)buta-2,3-dien-1-one", sub_smiles="C=C=C(CCC)C(O)c1ccc(Br)cc1", prod_smiles="C=C=C(CCC)C(=O)c1ccc(Br)cc1", time=6, y=80, page=5, masses=(5.4, 4.6, 5.9, 20.6, 13.8, 80.3, 64.1), eluent=None),
    4: dict(sub="1d", prod="2d", sub_name="2-hexyl-1-(4-chlorophenyl)buta-2,3-dien-1-ol", prod_name="2-hexyl-1-(4-chlorophenyl)buta-2,3-dien-1-one", sub_smiles="C=C=C(CCCCCC)C(O)c1ccc(Cl)cc1", prod_smiles="C=C=C(CCCCCC)C(=O)c1ccc(Cl)cc1", time=6, y=78, page=6, masses=(5.5, 4.8, 6.0, 20.9, 13.8, 79.6, 62.0), eluent=None),
    5: dict(sub="1e", prod="2e", sub_name="2-hexyl-1-(4-nitrophenyl)buta-2,3-dien-1-ol", prod_name="2-hexyl-1-(4-nitrophenyl)buta-2,3-dien-1-one", sub_smiles="C=C=C(CCCCCC)C(O)c1ccc([N+](=O)[O-])cc1", prod_smiles="C=C=C(CCCCCC)C(=O)c1ccc([N+](=O)[O-])cc1", time=6, y=63, page=6, masses=(5.5, 4.7, 5.9, 20.8, 13.9, 82.7, 51.4), eluent="petroleum ether/diethyl ether = 20:1"),
    6: dict(sub="1f", prod="2f", sub_name="2-hexyl-1-(3-furanyl)buta-2,3-dien-1-ol", prod_name="2-hexyl-1-(3-furanyl)buta-2,3-dien-1-one", sub_smiles=None, prod_smiles=None, time=11, y=61, page=6, masses=(5.4, 4.8, 6.2, 21.3, 13.6, 66.2, 40.4), eluent=None),
    7: dict(sub="1g", prod="2g", sub_name="2-pentyl-1-(3-thienyl)buta-2,3-dien-1-ol", prod_name="2-pentyl-1-(3-thienyl)buta-2,3-dien-1-one", sub_smiles=None, prod_smiles=None, time=8.5, y=73, page=6, masses=(5.5, 4.8, 5.9, 20.9, 13.7, 66.4, 48.3), eluent="petroleum ether/diethyl ether = 50:1"),
    8: dict(sub="1h", prod="2h", sub_name="2-methyl-1-(1-naphthyl)buta-2,3-dien-1-ol", prod_name="2-methyl-1-(1-naphthyl)buta-2,3-dien-1-one", sub_smiles="C=C=C(C)C(O)c1cccc2ccccc12", prod_smiles="C=C=C(C)C(=O)c1cccc2ccccc12", time=11, y=74, page=6, masses=(5.5, 4.8, 6.2, 21.4, 13.5, 63.6, 47.2), eluent=None),
    9: dict(sub="1i", prod="2i", sub_name="2-allyl-1-phenylbuta-2,3-dien-1-ol", prod_name="2-allyl-1-phenylbuta-2,3-dien-1-one", sub_smiles="C=C=C(CC=C)C(O)c1ccccc1", prod_smiles="C=C=C(CC=C)C(=O)c1ccccc1", time=11, y=75, page=6, masses=(5.4, 4.6, 6.1, 21.5, 13.7, 55.1, 41.1), eluent="petroleum ether/diethyl ether = 40:1"),
    10: dict(sub="1j", prod="2j", sub_name="allenol 1j (R1=Ph, R2=Bu, R3=n-C5H11)", prod_name="allenic ketone 2j (R1=Ph, R2=Bu, R3=n-C5H11)", sub_smiles=None, prod_smiles=None, time=11, y=91, page=None, masses=None, eluent=None),
}


for entry, row in scope.items():
    detail_page = row["page"]
    evs = evidence(4, detail_page) if detail_page else evidence(4)
    masses = row["masses"]
    sub_amounts = [("amount", qty(0.3, "mmol"))]
    if masses:
        sub_amounts.insert(0, ("mass", qty(masses[5], "mg")))
    parts = [
        participant("substrate", "reactant", row["sub"], evs, name=row["sub_name"], smiles=row["sub_smiles"], amounts=sub_amounts),
        participant("product", "product", row["prod"], evs, name=row["prod_name"], smiles=row["prod_smiles"], amounts=[("mass", qty(masses[6], "mg"))] if masses else []),
        participant("phen", "reagent", "phen", evs, name="1,10-phenanthroline", amounts=[("mass", qty(masses[0], "mg")), ("amount", qty(0.03, "mmol"))] if masses else [("amount", qty(10, "mol%"))]),
        participant("bpy", "reagent", "bpy", evs, name="2,2'-bipyridine", amounts=[("mass", qty(masses[1], "mg")), ("amount", qty(0.03, "mmol"))] if masses else [("amount", qty(10, "mol%"))]),
        participant("cucl", "catalyst", "CuCl", evs, amounts=[("mass", qty(masses[2], "mg")), ("amount", qty(0.06, "mmol"))] if masses else [("amount", qty(20, "mol%"))]),
        participant("k2co3", "reagent", "K2CO3", evs, amounts=[("mass", qty(masses[3], "mg")), ("amount", qty(0.15, "mmol"))] if masses else [("equivalents", qty(0.5, "equiv"))]),
        participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("mass", qty(masses[4], "mg")), ("amount", qty(0.06, "mmol"))] if masses else [("amount", qty(20, "mol%"))]),
        participant("toluene", "solvent", "dry toluene" if masses else "toluene", evs, amounts=[("initial_volume", qty(1.5, "mL")), ("substrate_solution_volume", qty(1.5, "mL"))] if masses else [("volume", qty(3, "mL"))]),
        participant("air", "reagent", "air", evs, name="compressed air"),
    ]
    conditions = [
        field("temperature", qty(35, "°C"), evs),
        field("time", qty(row["time"], "h"), evs),
        field("atmosphere", "air", evs),
        field("pressure", "300 psi", evs),
    ]
    if entry == 1:
        conditions.extend(
            [
                field("catalyst_prestir_temperature", "r.t.", evs),
                field("catalyst_prestir_time", qty(0.5, "h"), evs),
                field("workup", "Carefully release pressure; filter through a short silica-gel column (100–140 mesh), wash with diethyl ether, and evaporate solvent.", evs),
                field("purification", "Flash chromatography on silica gel; petroleum ether/diethyl ether = 30:1.", evs),
            ]
        )
    else:
        conditions.extend([field("workup", None, evs), field("purification", row["eluent"], evs)])
    outcomes = [field("isolated_yield", qty(row["y"], "%"), evs, ["product"]), field("yield_measurement_basis", "isolated", evs, ["product"])]
    notes = []
    if entry == 8:
        outcomes.append(field("product_purity_by_1H_NMR", qty(95, "%"), evs, ["product"]))
        notes.append("An unknown substance could not be separated by column chromatography; product purity was 95% by 1H NMR using mesitylene as internal standard.")
    records.append(
        record(
            f"table5_entry{entry}_{row['sub']}_to_{row['prod']}",
            "substrate_scope_entry",
            evs,
            parts,
            conditions,
            outcomes,
            notes=notes,
            unresolved=["Supporting Information was mentioned but not supplied or explicitly associated.", "Candidate structures are not source-verified.", "Abbreviated product paragraphs do not restate workup/purification unless captured explicitly."] if entry != 1 else ["Supporting Information was mentioned but not supplied or explicitly associated.", "Candidate structures are not source-verified."],
        )
    )


# Scheme 1: distinct gram-scale experiment.
evs = evidence(4)
parts = [
    participant("substrate_1k", "reactant", "1k", evs, name="2-propyl-1-phenylbuta-2,3-dien-1-ol", smiles="C=C=C(CCC)C(O)c1ccccc1", amounts=[("mass", qty(1, "g", "1 g scale"))]),
    participant("product_2k", "product", "2k", evs, name="2-propyl-1-phenylbuta-2,3-dien-1-one", smiles="C=C=C(CCC)C(=O)c1ccccc1"),
    participant("cucl", "catalyst", "CuCl", evs, amounts=[("amount", qty(10, "mol%"))]),
    participant("phen", "reagent", "phen", evs, name="1,10-phenanthroline", amounts=[("amount", qty(5, "mol%"))]),
    participant("bpy", "reagent", "bpy", evs, name="2,2'-bipyridine", amounts=[("amount", qty(5, "mol%"))]),
    participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("amount", qty(10, "mol%"))]),
    participant("base", "reagent", "K2CO3", evs, amounts=[("equivalents", qty(0.5, "equiv"))]),
    participant("solvent", "solvent", "toluene", evs),
    participant("air", "reagent", "air", evs, name="compressed air"),
]
records.append(
    record(
        "scheme1_gram_scale_1k_to_2k",
        "reported_experiment",
        evs,
        parts,
        [field("temperature", qty(35, "°C"), evs), field("time", qty(12, "h"), evs), field("atmosphere", "air", evs), field("pressure", "300 psi", evs), field("solvent_volume", None, evs), field("workup", None, evs), field("purification", None, evs)],
        [field("reported_product_yield", qty(74, "%"), evs, ["product_2k"]), field("yield_measurement_basis", None, evs, ["product_2k"])],
        unresolved=["The page states a 1 g scale but omits exact mmol, solvent volume, product mass, yield basis, workup, and purification.", "Candidate structures are not source-verified."],
    )
)


def oxygen_scheme_record(label: str, product: str, sub_name: str, prod_name: str, sub_smiles: str, prod_smiles: str, isolated: int, based_consumed: int):
    evs = evidence(4, 5)
    parts = [
        participant("substrate", "reactant", label, evs, name=sub_name, smiles=sub_smiles),
        participant("product", "product", product, evs, name=prod_name, smiles=prod_smiles),
        participant("cucl", "catalyst", "CuCl", evs, amounts=[("amount", qty(20, "mol%"))]),
        participant("phen", "reagent", "phen", evs, name="1,10-phenanthroline", amounts=[("amount", qty(12.5, "mol%"))]),
        participant("bpy", "reagent", "bpy", evs, name="2,2'-bipyridine", amounts=[("amount", qty(12.5, "mol%"))]),
        participant("dbad", "reagent", "DBAD", evs, name="di-tert-butyl azodicarboxylate", amounts=[("amount", qty(20, "mol%"))]),
        participant("base", "reagent", "K2CO3", evs, amounts=[("equivalents", qty(0.5, "equiv"))]),
        participant("solvent", "solvent", "toluene", evs),
        participant("oxygen", "reagent", "O2", evs, name="molecular oxygen", smiles="O=O"),
    ]
    return record(
        f"scheme2_{label}_to_{product}",
        "reported_experiment",
        evs,
        parts,
        [field("temperature", qty(60, "°C"), evs), field("time", qty(24, "h"), evs), field("atmosphere", "O2 (1 atm)", evs), field("reaction_scale", None, evs), field("solvent_volume", None, evs), field("workup", None, evs), field("purification", None, evs)],
        [
            field("conversion", qty(81, "%"), evs, ["substrate"]),
            field("isolated_yield", qty(isolated, "%"), evs, ["product"]),
            field("yield_measurement_basis", "isolated", evs, ["product"]),
            field("yield_based_on_starting_material_consumed", qty(based_consumed, "%"), evs, ["product"]),
        ],
        unresolved=["Reaction scale, solvent volume, exact batch masses, workup, and purification are absent from pages 4–5.", "Candidate structures are not source-verified."],
    )


records.append(oxygen_scheme_record("1l", "2l", "2-hexyl-1-butylbuta-2,3-dien-1-ol", "3-hexylocta-1,2-dien-4-one", "C=C=C(CCCCCC)C(O)CCCC", "C=C=C(CCCCCC)C(=O)CCCC", 58, 72))
records.append(oxygen_scheme_record("1m", "2m", "2-pentyl-1-(phenylethyl)buta-2,3-dien-1-ol", "4-pentyl-1-phenylhexa-4,5-dien-3-one", "C=C=C(CCCCC)C(O)CCc1ccccc1", "C=C=C(CCCCC)C(=O)CCc1ccccc1", 60, 74))


# Narrative comparison is a separate experiment because atmosphere/pressure and duration differ.
evs = evidence(4)
parts = [
    participant("substrate", "reactant", "1l", evs, name="2-hexyl-1-butylbuta-2,3-dien-1-ol", smiles="C=C=C(CCCCCC)C(O)CCCC"),
    participant("product", "product", "2l", evs, name="3-hexylocta-1,2-dien-4-one", smiles="C=C=C(CCCCCC)C(=O)CCCC"),
    participant("air", "reagent", "air", evs, name="compressed air"),
]
records.append(
    record(
        "prose_1l_high_pressure_air_comparison",
        "reported_experiment",
        evs,
        parts,
        [field("temperature", qty(60, "°C"), evs), field("time", qty(10, "h"), evs), field("atmosphere", "air", evs), field("pressure", "300 psi", evs), field("other_reaction_conditions", None, evs), field("workup", None, evs), field("purification", None, evs)],
        [field("reported_product_yield", qty(43, "%"), evs, ["product"]), field("yield_measurement_basis", "1H NMR", evs, ["product"]), field("conversion", qty(73, "%"), evs, ["substrate"])],
        unresolved=["The comparison sentence does not explicitly restate catalyst, ligands, DBAD, base, solvent, scale, workup, or purification; these were not inferred from Scheme 2.", "Candidate structures are not source-verified."],
    )
)


assert len(records) == 43, len(records)
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


def ids(prefix: str):
    return [r["record_id"] for r in records if r["source_reaction_id"].startswith(prefix)]


page_records = {
    1: [],
    2: ids("table1_") + ids("table2_"),
    3: ids("table3_"),
    4: ids("table4_") + ids("table5_") + ids("scheme1_") + ids("scheme2_") + ids("prose_1l_"),
    5: ids("scheme2_") + [f"{DOC}:table5_entry{i}_{scope[i]['sub']}_to_{scope[i]['prod']}" for i in (1, 2, 3)],
    6: [f"{DOC}:table5_entry{i}_{scope[i]['sub']}_to_{scope[i]['prod']}" for i in (4, 5, 6, 7, 8, 9)],
}


def region(page: int, name: str, finding: str):
    return {"region": name, "finding": finding, "evidence_ids": evidence(page)}


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                region(1, "title and abstract", "Broad method and scope claims only; no individual batch record was created."),
                region(1, "two-column introduction", "Prior oxidants and cited allene syntheses are literature context, not experiments newly reported in this paper."),
            ],
            "record_ids": [],
            "unresolved": ["No individual reaction drawing or table row appears on this page."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                region(2, "lower-left Table 1 and footnotes", "Seven base-screen rows extracted independently, including base/catalyst/MS footnote overrides, NR outcomes, isolated/NMR yields, and recovered 1a."),
                region(2, "upper-right Table 2 and footnotes", "Five solvent-screen rows extracted independently, preserving NR, distinct yield bases, and recovered 1a."),
                region(2, "Results and Discussion prose", "Narrative interpretations duplicate Table 1/2 results; cited Markó conditions were not added as a separate literature experiment."),
            ],
            "record_ids": page_records[2],
            "unresolved": ["Exact batch masses, workups, and purification details are absent; Table 2 entry 4 gives no product-yield measurement basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                region(3, "full-page Table 3 ligand screen", "Fourteen independent ligand-screen rows extracted; structures were read as ligand labels/names, row 14 footnote conditions override the table-wide conditions, and recovery is kept separate from product yield."),
                region(3, "bottom standard-condition prose", "The standard-condition summary is represented in the applicable Table 5 rows rather than duplicated as a standalone experiment."),
            ],
            "record_ids": page_records[3],
            "unresolved": ["Ligand drawings are not encoded as verified structures; exact batch masses, workup, and purification are absent."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                region(4, "middle-left Table 4", "Three Cu(I)-source optimization rows extracted independently with isolated yields."),
                region(4, "lower full-width Table 5", "Ten substrate-scope rows extracted independently; rows 1–9 are linked to detailed product paragraphs on pages 5–6 where visible."),
                region(4, "upper-right Scheme 1", "One distinct gram-scale 1k-to-2k experiment extracted with page-visible catalyst loadings, pressure, temperature, duration, and yield."),
                region(4, "right-column Scheme 2 discussion", "Two pure-oxygen experiments are linked to Scheme 2 on page 5; the separate high-pressure-air 1l comparison is retained as a third, condition-distinct record."),
            ],
            "record_ids": page_records[4],
            "unresolved": ["Scheme 1 omits exact mmol, solvent volume, product mass, yield basis, workup, and purification; the air-comparison sentence omits most other reaction conditions."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                region(5, "upper-left Scheme 2", "Two separate O2 (1 atm) oxidations, 1l-to-2l and 1m-to-2m, extracted with conversion, isolated yield, and yield based on consumed alcohol kept distinct."),
                region(5, "left-column starting-material methods", "References describe how starting allenols were prepared in earlier reports; no new preparation batch is supplied here."),
                region(5, "2a typical procedure spanning both columns", "Detailed 2a quantities, catalyst pre-stir, compressed-air reaction, workup, chromatography, product mass, and yield merged into Table 5 entry 1."),
                region(5, "right-column 2b and 2c paragraphs", "Detailed charges and isolated product masses/yields merged into Table 5 entries 2 and 3; characterization was not duplicated as a reaction."),
            ],
            "record_ids": page_records[5],
            "unresolved": ["Scheme 2 exact batch quantities/workups are not visible on pages 4–5; SI is mentioned later but was not supplied or associated."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                region(6, "left column 2d–2f", "Detailed charges and isolated product masses/yields merged into Table 5 entries 4–6; explicit 2e chromatography eluent retained."),
                region(6, "right column 2g–2i", "Detailed charges and isolated product masses/yields merged into Table 5 entries 7–9; explicit eluents and the 2h impurity/purity qualification retained."),
            ],
            "record_ids": page_records[6],
            "unresolved": ["Abbreviated product paragraphs do not restate every operation; complex heteroaryl structures remain without candidate SMILES where connectivity was not encoded confidently."],
        },
    ],
}

coverage_dir = ROOT / "runs/current/coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["task_id"] == f"{DOC}:page{page}:text" for page in range(1, 7)):
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; reaction records and coverage ledger generated for this pass."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
