#!/usr/bin/env python3
"""Build source-faithful machine records for doc_024d1f8cc93b26a0 pages 1–4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = "doc_024d1f8cc93b26a0"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


P1, P2, P3, P4 = (ev(i) for i in range(1, 5))


def uniq(items):
    return list(dict.fromkeys(items))


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": uniq(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence=(), targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def qty(number, unit, **extra):
    result = {"number": number, "unit": unit}
    result.update(extra)
    return result


def rng(low, high, unit, raw_text):
    return {"minimum": low, "maximum": high, "unit": unit, "raw_text": raw_text}


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


def amount(name, value, evidence):
    return fld(name, value, evidence)


def missing_conditions(include_time=True, include_temperature=False):
    result = []
    if include_time:
        result.append(fld("time", None))
    if include_temperature:
        result.append(fld("temperature", None))
    result += [fld("atmosphere", None), fld("workup", None), fld("purification", None)]
    return result


def record(rid, kind, evidence, participants, conditions, outcomes, *, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


SMILES = {
    "1a": "O=C(NCc1ccccc1)C=C=C(C)C",
    "1b": "O=C(NCCCC)C=C=C(C)C",
    "1c": "O=C(NC(C)(C)C)C=C=C(C)C",
    "1d": "O=C(NC(C)C)C=C=C(C)C",
    "1e": "O=C(NCc1ccccc1)C=C=C(CC)CC",
    "1f": "O=C(NCCCC)C=C=C(CC)CC",
    "1g": "O=C(NCc1ccccc1)C=C=C(CCC)CCC",
    "1h": "O=C(NCCCC)C=C=C(CCC)CCC",
    "1i": "O=C(NCc1ccccc1)C=C=C(CCCC)CCCC",
    "1j": "O=C(NCc1ccccc1)C=C=C1CCCCC1",
    "1k": "O=C(NCc1ccccc1)C=C=C(C)CC",
    "1l": "O=C(NCc1ccccc1)C(C)=C=C(C)C",
    "1m": "O=C(NCc1ccccc1)C=C=C(c1ccccc1)CC",
    "2a": "CC1(C)OC(=NCC2=CC=CC=C2)C=C1C3=CC(=NCC4=CC=CC=C4)OC3(C)C",
    "2b": "CC1(C)OC(=NCCCC)C=C1C1=CC(=NCCCC)OC1(C)C",
    "2c": "CC1(C)OC(=NC(C)(C)C)C=C1C1=CC(=NC(C)(C)C)OC1(C)C",
    "2d": "CC1(C)OC(=NC(C)C)C=C1C1=CC(=NC(C)C)OC1(C)C",
    "2e": "CCC1(CC)OC(=NCC2=CC=CC=C2)C=C1C1=CC(=NCC2=CC=CC=C2)OC1(CC)CC",
    "2f": "CCC1(CC)OC(=NCCCC)C=C1C1=CC(=NCCCC)OC1(CC)CC",
    "2g": "CCCC1(CCC)OC(=NCC2=CC=CC=C2)C=C1C1=CC(=NCC2=CC=CC=C2)OC1(CCC)CCC",
    "2h": "CCCC1(CCC)OC(=NCCCC)C=C1C1=CC(=NCCCC)OC1(CCC)CCC",
    "2i": "CCCCC1(CCCC)OC(=NCC2=CC=CC=C2)C=C1C1=CC(=NCC2=CC=CC=C2)OC1(CCCC)CCCC",
    "2j": "C1CCC2(CC1)OC(=NCC1=CC=CC=C1)C=C2C1=CC(=NCC2=CC=CC=C2)OC12CCCCC2",
    "2k": "CCC1(C)OC(=NCC2=CC=CC=C2)C=C1C1=CC(=NCC2=CC=CC=C2)OC1(C)CC",
    "2l": "CC1(C)OC(=NCC2=CC=CC=C2)C(C)=C1C1=C(C)C(=NCC2=CC=CC=C2)OC1(C)C",
    "PdCl2": "[Cl-].[Cl-].[Pd+2]",
    "PdI2": "[I-].[I-].[Pd+2]",
    "NaI": "[Na+].[I-]",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "DMF": "CN(C)C=O",
    "DMA": "CC(=O)N(C)C",
    "DMSO": "CS(C)=O",
    "MeCN": "CC#N",
    "THF": "C1CCOC1",
    "DCE": "ClCCCl",
}


NAMES = {
    "1a": "N-benzyl 4-methylpenta-2,3-dienamide",
    "1b": "N-n-butyl 4-methylpenta-2,3-dienamide",
    "1c": "N-tert-butyl 4-methylpenta-2,3-dienamide",
    "1d": "N-isopropyl 4-methylpenta-2,3-dienamide",
    "1m": "N-benzyl 4-phenyl-2,3-hexadienamide",
}


SOLVENTS = {
    "DMF": "N,N-dimethylformamide",
    "DMA": "N,N-dimethylacetamide",
    "DMSO": "dimethyl sulfoxide",
    "MeCN": "acetonitrile",
    "THF": "tetrahydrofuran",
    "DCE": "1,2-dichloroethane",
}


def molecule(label, role, evidence, *, entity_id=None, amounts=(), name=None, smiles=None):
    key = label.removeprefix("Z-")
    return participant(
        entity_id or key,
        role,
        label,
        evidence,
        name=name or NAMES.get(key),
        smiles=smiles if smiles is not None else SMILES.get(key),
        amounts=amounts,
    )


def reagent(key, evidence, *, entity_id=None, amounts=()):
    names = {"PdCl2": "palladium(II) chloride", "PdI2": "palladium(II) iodide",
             "NaI": "sodium iodide", "K2CO3": "potassium carbonate"}
    return participant(entity_id or key, "catalyst" if key.startswith("Pd") else "reagent",
                       key, evidence, name=names.get(key), smiles=SMILES.get(key), amounts=amounts)


def solvent(key, evidence, volume=None):
    amounts = [amount("volume", volume, evidence)] if volume else []
    return participant(key, "solvent", key, evidence, name=SOLVENTS.get(key),
                       smiles=SMILES.get(key), amounts=amounts)


records = []


# Scheme 1: two generic prior-work pathways, not present-paper batches.
for attack, product_label, rid in [
    ("N-attack", "generic gamma-lactam product", "scheme1_n_attack_literature"),
    ("O-attack", "generic furanimine product", "scheme1_o_attack_literature"),
]:
    parts = [
        participant("generic_allenamide", "reactant", "generic 2,3-allenamide", P1),
        participant("generic_product", "product", product_label, P1),
    ]
    records.append(record(
        rid, "literature_example", P1, parts,
        [fld("operation", attack, P1)] + missing_conditions(True, True), [],
        notes=("Scheme 1 summarizes a cited, generic cyclization pathway rather than a present-paper experiment.",),
        unresolved=("Generic R groups, primary-paper conditions, scale, yield, workup, and purification are not supplied on this page.",),
    ))


# Table 1: ten independent optimization rows.
table1 = [
    (1, "PdCl2", None, None, "DMF", 12, 0, 58),
    (2, "PdCl2", "NaI", None, "DMF", 16, 29, 32),
    (3, "PdCl2", "NaI", "K2CO3", "DMF", 8, 77, 0),
    (4, "PdCl2", None, "K2CO3", "DMF", 12, 26, 0),
    (5, "PdI2", None, "K2CO3", "DMF", 12, 59, 0),
    (6, "PdCl2", "NaI", "K2CO3", "DMA", 14, 67, 0),
    (7, "PdCl2", "NaI", "K2CO3", "DMSO", 22, 46, 5),
    (8, "PdCl2", "NaI", "K2CO3", "MeCN", 22, 53, 4),
    (9, "PdCl2", "NaI", "K2CO3", "THF", 23, 15, 30),
    (10, "PdCl2", "NaI", "K2CO3", "DCE", 23, 9, 49),
]
for entry, pd, nai, base, solv, hours, product_yield, recovery in table1:
    substrate = molecule("1a", "reactant", P1, amounts=[amount("amount", qty(0.2, "mmol"), P1)])
    product = molecule("Z-2a", "product", P1)
    parts = [substrate, product, reagent(pd, P1, amounts=[amount("loading", qty(5, "mol%"), P1)])]
    if nai:
        parts.append(reagent("NaI", P1, amounts=[amount("loading", qty(50, "mol%"), P1)]))
    if base:
        parts.append(reagent("K2CO3", P1, amounts=[amount("equivalents", qty(1.0, "equiv"), P1)]))
    parts.append(solvent(solv, P1))
    outcomes = [
        fld("nmr_product_yield", qty(product_yield, "%"), P1, ["2a"]),
        fld("recovered_starting_material_yield", qty(recovery, "%"), P1, ["1a"]),
        fld("yield_measurement_basis", "1H NMR analysis with mesitylene as internal standard", P1, ["2a"]),
    ]
    conditions = [fld("solvent", solv, P1), fld("temperature", qty(80, "°C"), P1),
                  fld("time", qty(hours, "h"), P1)] + missing_conditions(False)
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", P1, parts, conditions, outcomes,
        unresolved=("Atmosphere, solvent volume, workup, and purification are not stated for the optimization row.",
                    "Candidate substrate/product connectivity and Z geometry require chemistry review."),
    ))


# Table 2 scope rows, merged with the corresponding compound-specific preparation paragraphs.
scope = [
    # entry, substrate, product, solvent, time, yield, substrate mg/mmol, Pd mg/mmol, NaI mg/mmol, K2CO3 mg/mmol, product mg, evidence pages
    (1, "1a", "2a", "DMF", 8, 68, 40.0, 0.20, 1.9, 0.011, 15.0, 0.10, 27.6, 0.20, 27.2, [2, 3]),
    (2, "1b", "2b", "DMF", 11, 66, 34.0, 0.20, 1.9, 0.011, 15.7, 0.10, 27.6, 0.20, 22.4, [2, 3]),
    (3, "1c", "2c", "DMA", 14, 65, 33.1, 0.20, 1.7, 0.010, 14.7, 0.10, 27.6, 0.20, 21.3, [2, 3]),
    (4, "1d", "2d", "DMA", 10, 73, 31.8, 0.21, 1.7, 0.010, 14.8, 0.10, 28.0, 0.20, 23.2, [2, 3]),
    (5, "1e", "2e", "DMA", 21, 58, 45.6, 0.20, 2.0, 0.011, 14.4, 0.10, 27.6, 0.20, 26.4, [2, 3]),
    (6, "1f", "2f", "DMA", 15, 66, 38.9, 0.20, 1.8, 0.010, 15.0, 0.10, 26.8, 0.19, 25.4, [2, 3]),
    (7, "1g", "2g", "DMA", 10, 72, 50.4, 0.20, 1.9, 0.011, 14.5, 0.10, 27.9, 0.20, 36.3, [2, 3, 4]),
    (8, "1h", "2h", "DMA", 28, 64, 43.6, 0.20, 1.9, 0.011, 15.6, 0.10, 27.3, 0.20, 27.8, [2, 4]),
    (9, "1i", "2i", "DMA", 14, 66, 56.3, 0.20, 1.8, 0.010, 14.5, 0.10, 27.4, 0.20, 37.0, [2, 4]),
    (10, "1j", "2j", "DMF", 14, 74, 48.4, 0.20, 1.7, 0.010, 15.2, 0.10, 26.8, 0.20, 35.7, [2, 4]),
    (11, "1k", "2k", "DMA", 14, 69, 43.9, 0.20, 1.8, 0.010, 14.9, 0.10, 27.3, 0.20, 30.3, [2, 4]),
    (12, "1l", "2l", "DMA", 14, 88, 43.3, 0.20, 1.8, 0.010, 15.1, 0.10, 28.4, 0.21, 38.1, [2, 4]),
]
for row in scope:
    (entry, sub, prod, solv, hours, percent, sub_mg, sub_mmol, pd_mg, pd_mmol,
     nai_mg, nai_mmol, base_mg, base_mmol, prod_mg, pages) = row
    evidence = uniq(sum((ev(p) for p in pages), []))
    parts = [
        molecule(sub, "reactant", evidence, amounts=[amount("mass", qty(sub_mg, "mg"), evidence),
                                                     amount("amount", qty(sub_mmol, "mmol"), evidence)]),
        molecule(f"Z-{prod}", "product", evidence),
        reagent("PdCl2", evidence, amounts=[amount("mass", qty(pd_mg, "mg"), evidence),
                                            amount("amount", qty(pd_mmol, "mmol"), evidence),
                                            amount("loading", qty(5, "mol%"), P2)]),
        reagent("NaI", evidence, amounts=[amount("mass", qty(nai_mg, "mg"), evidence),
                                          amount("amount", qty(nai_mmol, "mmol"), evidence),
                                          amount("loading", qty(50, "mol%"), P2)]),
        reagent("K2CO3", evidence, amounts=[amount("mass", qty(base_mg, "mg"), evidence),
                                            amount("amount", qty(base_mmol, "mmol"), evidence),
                                            amount("equivalents", qty(1.0, "equiv"), P2)]),
        solvent(solv, evidence, qty(2, "mL")),
    ]
    conditions = [fld("solvent", solv, evidence), fld("temperature", qty(80, "°C"), P2),
                  fld("time", qty(hours, "h"), P2), fld("atmosphere", None)]
    if entry == 1:
        conditions += [
            fld("operation", "K2CO3, PdCl2, NaI, 1a, and DMF were added sequentially to a reaction tube and heated with stirring; TLC monitoring was used.", P3),
            fld("workup", "Quenched with 10 mL H2O; extracted with ether (25 mL × 3); washed with brine; dried over anhydrous Na2SO4; filtered and evaporated.", P3),
            fld("purification", "Chromatography on neutral Al2O3 using petroleum ether/ethyl acetate 4:1.", P3),
        ]
    else:
        conditions += [fld("workup", None), fld("purification", None)]
    outcomes = [
        fld("isolated_product_yield", qty(percent, "%"), evidence, [prod]),
        fld("isolated_product_mass", qty(prod_mg, "mg"), evidence, [prod]),
        fld("yield_measurement_basis", "isolated yield", P2, [prod]),
    ]
    if entry == 11:
        outcomes.append(fld("diastereomer_ratio", "1:1 mixture of two diastereomers", P2, [prod]))
    unresolved = ["Atmosphere is not stated.", "Candidate connectivity and the source-assigned Z geometry remain unverified."]
    if entry != 1:
        unresolved.append("The abbreviated preparation does not restate workup or purification.")
    records.append(record(f"table2_entry{entry}_{prod}", "substrate_scope_entry", evidence,
                          parts, conditions, outcomes, unresolved=unresolved))


# Scheme 2: lower PdCl2 loading, two independent substrate-specific experiments.
evidence = uniq(P2 + P3)
parts = [
    molecule("1a", "reactant", evidence, amounts=[amount("mass", qty(40.3, "mg"), P3), amount("amount", qty(0.20, "mmol"), P3)]),
    molecule("Z-2a", "product", evidence),
    reagent("PdCl2", evidence, amounts=[amount("mass", qty(0.4, "mg"), P3), amount("amount", qty(0.002, "mmol"), P3), amount("loading", qty(1, "mol%"), P2)]),
    reagent("NaI", evidence, amounts=[amount("mass", qty(15.7, "mg"), P3), amount("amount", qty(0.10, "mmol"), P3), amount("loading", qty(50, "mol%"), P2)]),
    reagent("K2CO3", evidence, amounts=[amount("mass", qty(28.1, "mg"), P3), amount("amount", qty(0.20, "mmol"), P3), amount("equivalents", qty(1.0, "equiv"), P2)]),
    solvent("DMF", evidence, qty(2, "mL")),
]
records.append(record(
    "scheme2_1a_low_pd_loading", "reported_experiment", evidence, parts,
    [fld("solvent", "DMF", evidence), fld("temperature", qty(80, "°C"), P2), fld("time", qty(22.5, "h"), P2)] + missing_conditions(False),
    [fld("reported_product_yield", qty(60, "%"), evidence, ["2a"]), fld("product_mass", qty(23.9, "mg"), P3, ["2a"]), fld("yield_measurement_basis", None)],
    unresolved=("Yield basis, atmosphere, workup, and purification are not stated.", "Candidate connectivity and Z geometry remain unverified."),
))

parts = [
    molecule("1l", "reactant", P2), molecule("Z-2l", "product", P2),
    reagent("PdCl2", P2, amounts=[amount("loading", qty(1, "mol%"), P2)]),
    reagent("NaI", P2, amounts=[amount("loading", qty(50, "mol%"), P2)]),
    reagent("K2CO3", P2, amounts=[amount("equivalents", qty(1.0, "equiv"), P2)]),
    solvent("DMA", P2),
]
records.append(record(
    "scheme2_1l_low_pd_loading", "reported_experiment", P2, parts,
    [fld("solvent", "DMA", P2), fld("temperature", qty(80, "°C"), P2), fld("time", qty(21.5, "h"), P2)] + missing_conditions(False),
    [fld("reported_product_yield", qty(60, "%"), P2, ["2l"]), fld("yield_measurement_basis", None)],
    unresolved=("Reaction scale, yield basis, atmosphere, workup, and purification are not stated.", "Candidate connectivity and Z geometry remain unverified."),
))


# Scheme 3: three substrate-specific negative or failed outcomes.
parts = [
    molecule("1m", "reactant", P2), participant("expected_2m", "product", "expected homodimeric cyclization product of 1m", P2),
    reagent("PdCl2", P2), reagent("NaI", P2), reagent("K2CO3", P2),
    participant("solvent", "solvent", "DMF or DMA", P2),
]
records.append(record(
    "scheme3_1m_no_reaction", "reported_experiment", P2, parts,
    [fld("solvent", "DMF or DMA", P2), fld("temperature", qty(80, "°C"), P2)] + missing_conditions(True),
    [fld("expected_product_formation", "no reaction", P2, ["expected_2m"]),
     fld("recovered_starting_material_yield", rng(27, 32, "%", "27%–32% recovery"), P2, ["1m"])],
    unresolved=("The drawing combines DMF or DMA with a 27–32% recovery range; solvent-specific recoveries are not assigned.",
                "Catalyst/additive loadings, time, yield basis, atmosphere, workup, and purification are not stated."),
))

for label in ("1n", "1o"):
    parts = [
        participant(label, "reactant", label, P2, amounts=[amount("amount", qty(0.2, "mmol"), P2)]),
        participant(f"expected_2{label[-1]}", "product", f"expected homodimeric cyclization product of {label}", P2),
        reagent("PdCl2", P2, amounts=[amount("loading", qty(5, "mol%"), P2)]),
        reagent("NaI", P2, amounts=[amount("loading", qty(50, "mol%"), P2)]),
        reagent("K2CO3", P2, amounts=[amount("equivalents", qty(1.0, "equiv"), P2)]),
        solvent("DMF", P2),
    ]
    records.append(record(
        f"scheme3_{label}_no_expected_product", "reported_experiment", P2, parts,
        [fld("solvent", "DMF", P2), fld("temperature", qty(80, "°C"), P2)] + missing_conditions(True),
        [fld("expected_product_formation", "no expected products", P2, [f"expected_2{label[-1]}"]),
         fld("starting_material_conversion", "completely consumed", P2, [label]),
         fld("starting_material_recovery_observation", "no starting material remained", P2, [label])],
        unresolved=("Reaction time, atmosphere, workup, purification, side-product identities, and yield basis are not stated.",
                    "The substrate and expected product structures are not encoded because their drawings require chemistry review."),
    ))


# Scheme 4: explicitly proposed catalytic rationale.
evidence = uniq(P2 + P3)
parts = [
    participant("generic_allenamide", "reactant", "generic 2,3-allenamide", evidence),
    participant("M1", "unspecified_agent", "iminyl-lactonyl palladium(II) intermediate M1", evidence),
    participant("M2", "unspecified_agent", "bis(iminyl-lactonyl) palladium intermediate M2", evidence),
    participant("generic_Z2", "product", "generic Z-bis(furanimine) product", evidence),
    reagent("PdCl2", evidence), reagent("NaI", evidence), reagent("K2CO3", evidence),
    participant("Pd0", "catalyst", "Pd(0)", P3),
    participant("I2", "reagent", "in situ generated I2", P3, smiles="II"),
    participant("O2", "reagent", "O2 in air", P3, smiles="O=O"),
]
records.append(record(
    "scheme4_proposed_mechanism", "mechanism", evidence, parts,
    [fld("operation", "coordination and anti-oxypalladation to M1", evidence),
     fld("operation", "second oxypalladation to M2", evidence),
     fld("operation", "reductive elimination to Z-bis(furanimine) and Pd(0)", evidence),
     fld("operation", "Pd(0) oxidation to Pd(II) by in situ I2 and O2 in air", P3)],
    [fld("stereochemical_rationale", "Z selectivity at C=N is attributed to steric interaction between R3 and R4 in the E products", P3, ["generic_Z2"])],
    notes=("K2CO3 is proposed to increase the nucleophilicity of the amide functionality.",),
    unresolved=("The pathway is proposed rather than experimentally isolated or verified.",
                "Generic R groups and organopalladium coordination/connectivity are not encoded as SMILES."),
))


assert len(records) == 30
assert len({r["record_id"] for r in records}) == 30


def ids(prefixes):
    if isinstance(prefixes, str):
        prefixes = [prefixes]
    return [r["record_id"] for r in records if any(r["source_reaction_id"].startswith(p) for p in prefixes)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and Results opening", "finding": "Abstract and narrative summarize the present homodimerization and cited prior work; broad claims were not duplicated as batch experiments.", "evidence_ids": P1},
                {"region": "lower-left Scheme 1", "finding": "Two generic cited prior-work cyclization arrows (N-attack to gamma-lactam and O-attack to furanimine) classified as literature examples.", "evidence_ids": P1},
                {"region": "lower-right Table 1 and footnotes", "finding": "Ten independent optimization rows extracted with 0.2 mmol scale, 5 mol% Pd, 80 °C, row solvent/time, footnote NaI/K2CO3 loadings, NMR yields, and starting-material recoveries.", "evidence_ids": P1},
            ],
            "record_ids": ids(["scheme1_", "table1_"]),
            "unresolved": ["Scheme 1 generic structures and cited primary-paper conditions are not supplied.", "Table 1 omits solvent volume, atmosphere, workup, and purification."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 2 and footnotes", "finding": "Twelve independent substrate-scope rows extracted; the compound-specific paragraphs on pages 3–4 are merged into these records.", "evidence_ids": P2},
                {"region": "upper-right Scheme 2", "finding": "Two distinct 1 mol% PdCl2 experiments for 1a and 1l extracted; the 1a quantities on page 3 are merged into its record.", "evidence_ids": P2},
                {"region": "middle-right Scheme 3", "finding": "Three substrate-specific negative outcomes extracted: no reaction for 1m with 27–32% recovery, and no expected products with complete consumption for 1n and 1o.", "evidence_ids": P2},
                {"region": "lower-left Figure 1", "finding": "X-ray structure of 2e supports Table 2 entry 5 and is not an additional reaction.", "evidence_ids": P2},
                {"region": "lower-right proposed-rationale prose", "finding": "Prose introduces the Scheme 4 proposed catalytic pathway; linked to the page-3 mechanism record rather than treated as an experiment.", "evidence_ids": P2},
            ],
            "record_ids": ids(["table2_", "scheme2_", "scheme3_", "scheme4_"]),
            "unresolved": ["Scheme 3 omits reaction times and most operational details.", "The 1m drawing combines DMF or DMA with a 27–32% recovery range without solvent-specific assignment.", "Figure 1 supports identity but does not independently verify every candidate structure."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 4 and adjacent prose", "finding": "Proposed M1/M2 oxypalladation, reductive-elimination, and Pd reoxidation pathway classified as mechanism.", "evidence_ids": P3},
                {"region": "Experimental 4.1 general procedure and low-loading paragraph", "finding": "Complete 2a isolation procedure merged into Table 2 entry 1; the separate 1 mol% PdCl2/1a batch merged into Scheme 2's 1a record.", "evidence_ids": P3},
                {"region": "Experimental 4.2–4.7", "finding": "Exact quantities and product masses for 2b–2g merged into their Table 2 rows; the 2g paragraph continues onto page 4.", "evidence_ids": P3},
            ],
            "record_ids": ids(["table2_entry1_", "table2_entry2_", "table2_entry3_", "table2_entry4_", "table2_entry5_", "table2_entry6_", "table2_entry7_", "scheme2_1a", "scheme4_"]),
            "unresolved": ["Only the 2a general procedure states workup and purification; abbreviated preparations do not inherit them.", "Atmosphere is not stated.", "The proposed mechanism and source-assigned Z geometry remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Experimental 4.7 continuation and 4.8–4.12", "finding": "Exact quantities and product masses for 2g–2l merged into Table 2 entries 7–12; analytical data were treated as identity support, not new reactions.", "evidence_ids": P4},
                {"region": "Acknowledgements and Supplementary data notice", "finding": "The paper states that supplementary data are available online, but no SI file was supplied or explicitly associated; no SI content was inferred.", "evidence_ids": P4},
                {"region": "References and crystallographic note", "finding": "Citation list and crystal data for 2e contain no additional present-paper reaction batch.", "evidence_ids": P4},
            ],
            "record_ids": ids(["table2_entry7_", "table2_entry8_", "table2_entry9_", "table2_entry10_", "table2_entry11_", "table2_entry12_"]),
            "unresolved": ["Abbreviated preparations omit atmosphere, workup, and purification.", "SI association remains unestablished.", "Candidate structures and stereochemistry require chemistry review."],
        },
    ],
}


(ROOT / "raw_model" / "records_pages_0001_0004.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
(ROOT / "coverage" / "pages_0001_0004.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id", "").split(":")[-2] in {"page1", "page2", "page3", "page4"}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
