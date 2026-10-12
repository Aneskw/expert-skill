#!/usr/bin/env python3
"""Enrich existing jo0163997 experiment records from PDF pages 7-9.

The specific experimental paragraphs repeat experiments already represented by
Table 2, Table 3, Schemes 4/5/8/10, eq 2, and eq 5.  This script therefore
updates those record IDs rather than creating duplicate experiments.
"""
import copy
import json
from pathlib import Path


DOC = "doc_f03c4dfd3e9143ac"
BASE = Path(__file__).resolve().parents[1]
DATASET = BASE / "dataset.json"
OUT = Path(__file__).with_name("extracted_records_pages_0007_0009.json")
COVERAGE = BASE / "coverage" / "pages_0007_0009.json"
TASKS = BASE / "tasks.json"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets is not None:
        item["target_entity_ids"] = list(targets)
    return item


def quantity(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def extend_unique(items, additions):
    for item in additions:
        if item not in items:
            items.append(item)


def add_page_evidence(record, *pages):
    for page in pages:
        extend_unique(record["evidence_ids"], ev(page))


def set_specific_amounts(entity, mass_g, amount_mmol, evidence):
    entity["amounts"] = [
        quantity("mass", mass_g, "g", evidence),
        quantity("amount", amount_mmol, "mmol", evidence),
    ]


def set_product(entity, name, mass_value, mass_unit, evidence):
    entity["name"] = fact(name, evidence)
    entity["amounts"] = [quantity("mass", mass_value, mass_unit, evidence)]


def remove_nominal_catalyst_amount(record, catalyst_id):
    catalyst = participant(record, catalyst_id)
    catalyst["amounts"] = [
        item for item in catalyst["amounts"]
        if item["name"] != "amount"
    ]


def extend_outcome(record, name, evidence):
    item = next(o for o in record["outcomes"] if o["name"] == name)
    extend_unique(item["fact"]["evidence_ids"], evidence)


def upsert_outcome(record, name, value, evidence, targets):
    matches = [o for o in record["outcomes"] if o["name"] == name]
    item = field(name, value, evidence, targets)
    if matches:
        first = record["outcomes"].index(matches[0])
        record["outcomes"] = [o for o in record["outcomes"] if o["name"] != name]
        record["outcomes"].insert(first, item)
    else:
        record["outcomes"].append(item)


def add_note(record, value, evidence):
    if not any(n["value"] == value for n in record["notes"]):
        record["notes"].append(fact(value, evidence))


def replace_unresolved(record, remove_contains=(), add=()):
    record["review"]["unresolved"] = [
        text for text in record["review"]["unresolved"]
        if not any(fragment in text for fragment in remove_contains)
    ]
    extend_unique(record["review"]["unresolved"], list(add))


def add_workup(record, evidence, chromatography=True):
    additions = [
        ("ether", "reagent", "ether"),
        ("brine", "reagent", "brine"),
        ("sodium_sulfate", "reagent", "anhydrous sodium sulfate"),
    ]
    existing = {p["entity_id"] for p in record["participants"]}
    for entity_id, role, label in additions:
        if entity_id in existing:
            continue
        record["participants"].append({
            "entity_id": entity_id,
            "role": role,
            "label": fact(label, evidence),
            "name": fact(None, evidence),
            "smiles": fact(None, evidence),
            "smiles_parseable": None,
            "structure_verified": False,
            "amounts": [],
        })
    step_ids = {s["step_id"] for s in record["steps"]}
    if "workup" not in step_ids:
        record["steps"].append({
            "step_id": "workup",
            "participant_ids": ["ether", "brine", "sodium_sulfate"],
            "conditions": [field(
                "workup",
                "ether added; washed with brine three times; dried over anhydrous sodium sulfate",
                evidence,
            )],
        })
    if chromatography and "purification" not in step_ids:
        record["steps"].append({
            "step_id": "purification",
            "participant_ids": [],
            "conditions": [field(
                "purification",
                "silica-gel column chromatography (petroleum ether/ether 40:1)",
                evidence,
            )],
        })


data = json.loads(DATASET.read_text())
records_by_id = {r["record_id"]: r for r in data["experiments"]}
selected = []


def take(suffix):
    record = copy.deepcopy(records_by_id[f"{DOC}:{suffix}"])
    selected.append(record)
    return record


# Specific experimental paragraphs corresponding to Table 2 entries 3-17.
table2 = {
    3: (7, 0.143, 0.82, 0.482, 3.98, 0.107, "3-Benzyl-2-methyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    4: (7, 0.145, 0.80, 0.647, 5.35, 0.144, "2,3-Dibutyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    5: (7, 0.173, 0.86, 0.528, 4.36, 0.168, "3-Butyl-2-phenyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    6: (7, 0.111, 0.67, 0.410, 3.39, 0.088, "2-Butyl-3,4-bis(2′-propenyl)-2,5-dihydrofuran"),
    7: (7, 0.104, 0.56, 0.361, 2.98, 0.069, "2-Butyl-3-(methoxycarbonyl)-4-(2′-propenyl)-2,5-dihydrofuran"),
    8: (7, 0.126, 0.62, 0.400, 3.30, 0.102, "2-Butyl-3-phenyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    9: (7, 0.145, 0.65, 0.450, 3.72, 0.103, "2,3-Diphenyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    10: (7, 0.070, 0.40, 0.262, 2.16, 0.074, "2,2-Dimethyl-3-phenyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    11: (7, 0.077, 0.50, 0.302, 2.50, 0.055, "3-Butyl-2,2-dimethyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    12: (7, 0.098, 0.61, 0.354, 2.92, 0.077, "3-Benzyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    13: (7, 0.170, 1.01, 0.597, 4.93, 0.152, "2-Hexyl-4-methyl-3-(2′-propenyl)-2,5-dihydrofuran"),
    14: (7, 0.148, 0.96, 0.595, 4.92, 0.060, "2-Hexyl-3-(2′-propenyl)-2,5-dihydrofuran"),
    15: (7, 0.104, 0.68, 0.403, 3.33, 0.075, "5-Butyl-2,2-dimethyl-4-(2′-propenyl)-2,5-dihydrofuran"),
    16: (7, 0.096, 0.50, 0.313, 2.59, 0.080, "2-Butyl-3-(2′-propenyl)-1-oxaspiro[4.5]dec-3-ene"),
    17: (8, 0.065, 0.34, 0.226, 1.87, 0.054, "2-Butyl-4-(2′-propenyl)-1-oxaspiro[4.5]dec-3-ene"),
}
for entry, (page, s_mass, s_mmol, a_mass, a_mmol, p_mass, product_name) in table2.items():
    evidence = ev(page)
    record = take(f"table2_entry_{entry:02d}")
    add_page_evidence(record, page)
    if entry == 16:
        add_page_evidence(record, 8)  # characterization continues on page 8
    set_specific_amounts(participant(record, "substrate"), s_mass, s_mmol, evidence)
    set_specific_amounts(participant(record, "allyl_bromide_3a"), a_mass, a_mmol, evidence)
    set_product(participant(record, "product"), product_name, p_mass, "g", evidence)
    remove_nominal_catalyst_amount(record, "pdcl2")
    if entry == 7:
        upsert_outcome(
            record,
            "specific_example_isolated_yield",
            {"number": 54, "unit": "%"},
            evidence,
            ["product"],
        )
        add_note(record, "Table 2 reports 55%, whereas the specific experimental paragraph reports 54%; both source values are retained.", evidence)
        replace_unresolved(record, add=["Table 2 and the specific experimental paragraph disagree on the 4g isolated yield (55% versus 54%)."])
    else:
        extend_outcome(record, "isolated_yield", evidence)
    add_note(record, "Specific experimental scale replaces the nominal 1 mmol/5 mmol table scale for reactant quantities; catalyst mass is not reported.", evidence)


# Page 8: Scheme 4 entry for 1r.
e8 = ev(8)
record = take("scheme4_1r")
add_page_evidence(record, 8)
set_specific_amounts(participant(record, "allenol_1r"), 0.087, 0.69, e8)
set_specific_amounts(participant(record, "allyl_bromide_3a"), 0.433, 3.58, e8)
set_product(participant(record, "product_4r"), "2-Butyl-4-(2′-propenyl)-2,5-dihydrofuran", 5, "mg", e8)
extend_outcome(record, "isolated_yield", e8)

# Page 8: the 1s/3a run gives two separately quantified products.
record = take("scheme4_1s_5equiv")
add_page_evidence(record, 8)
set_specific_amounts(participant(record, "allenol_1s"), 0.133, 0.96, e8)
set_specific_amounts(participant(record, "allyl_bromide_3a"), 0.595, 4.92, e8)
set_product(participant(record, "product_4s"), "3-(2′-Propenyl)-1-oxaspiro[4.5]dec-3-ene", 0.007, "g", e8)
set_product(participant(record, "product_5s"), "3-(1-cyclohexylidenemethylvinyl)-1-oxaspiro[4.5]dec-3-ene", 0.081, "g", e8)
extend_outcome(record, "product_4s_yield", e8)
extend_outcome(record, "product_5s_yield", e8)

# Page 8: Scheme 5 specific examples.
scheme5 = {
    "3b": (0.069, 0.40, 0.385, 1.95, 0.086, "2,2-Dimethyl-3-phenyl-4-(2′-phenyl-2′-propenyl)-2,5-dihydrofuran"),
    "3c": (0.070, 0.40, 0.412, 2.06, 0.084, "4-(2′-Bromo-2′-propenyl)-2,2-dimethyl-3-phenyl-2,5-dihydrofuran"),
    "3d": (0.060, 0.34, 0.345, 1.95, 0.068, "2,2-Dimethyl-4-(2′-butyl-2′-propenyl)-3-phenyl-2,5-dihydrofuran"),
}
for reagent, (s_mass, s_mmol, r_mass, r_mmol, p_mass, product_name) in scheme5.items():
    record = take(f"scheme5_{reagent}")
    add_page_evidence(record, 8)
    set_specific_amounts(participant(record, "allenol_1j"), s_mass, s_mmol, e8)
    set_specific_amounts(participant(record, "allylic_bromide"), r_mass, r_mmol, e8)
    set_product(participant(record, "product"), product_name, p_mass, "g", e8)
    extend_outcome(record, "isolated_yield", e8)

# Page 8: Table 3 entries 1-7. Entry 7 characterization continues on page 9.
table3 = {
    1: (0.155, 1.01, 0.621, 5.13, 0.122, "4-Butyl-5-methyl-3-propenyl-5,6-dihydro-2H-pyran"),
    2: (0.077, 0.55, 0.336, 2.78, 0.060, "4-Butyl-3-propenyl-5,6-dihydro-2H-pyran"),
    3: (0.180, 1.03, 0.622, 5.14, 0.172, "5-Methyl-4-phenyl-3-propenyl-5,6-dihydro-2H-pyran"),
    4: (0.151, 0.98, 0.594, 4.91, 0.092, "4-tert-Butyl-5-methyl-3-propenyl-5,6-dihydro-2H-pyran"),
    5: (0.181, 0.99, 0.605, 5.00, 0.192, "4-Butyl-3-propenyl-2-isopropyl-5,6-dihydro-2H-pyran"),
    6: (0.125, 0.99, 0.603, 4.98, 0.106, "3-Propenyl-2,2,5-trimethyl-5,6-dihydro-2H-pyran"),
    7: (0.082, 0.59, 0.386, 3.19, 0.036, "2-Butyl-3-propenyl-5,6-dihydro-2H-pyran"),
}
for entry, (s_mass, s_mmol, a_mass, a_mmol, p_mass, product_name) in table3.items():
    record = take(f"table3_entry_{entry:02d}")
    add_page_evidence(record, 8)
    if entry == 7:
        add_page_evidence(record, 9)
    set_specific_amounts(participant(record, "substrate"), s_mass, s_mmol, e8)
    set_specific_amounts(participant(record, "allyl_bromide_3a"), a_mass, a_mmol, e8)
    set_product(participant(record, "product"), product_name, p_mass, "g", e8)
    remove_nominal_catalyst_amount(record, "pdcl2")
    extend_outcome(record, "isolated_yield", e8)
    if entry == 7:
        extend_outcome(record, "starting_material_recovered", e8)
    add_note(record, "Specific experimental scale replaces the nominal 1 mmol/5 mmol table scale for reactant quantities; catalyst mass is not reported.", e8)


# Page 9: four PdCl2 experiments from Scheme 8 have full specific scales.
e9 = ev(9)
scheme8 = {
    "scheme8_1a_3e_pdcl2": (0.096, 0.69, 0.317, 3.50, 0.084, "4aa", "(E and Z)-4-(2′-butenyl)-3-butyl-2-methyl-2,5-dihydrofuran", "4ab", "3-Butyl-2-methyl-4-(1′-methyl-2′-propenyl)-2,5-dihydrofuran"),
    "scheme8_1a_3f_pdcl2": (0.219, 1.56, 0.693, 7.65, 0.060, "4aa", "(E and Z)-4-(2′-butenyl)-3-butyl-2-methyl-2,5-dihydrofuran", "4ab", "3-Butyl-2-methyl-4-(1′-methyl-2′-propenyl)-2,5-dihydrofuran"),
    "scheme8_1j_3e": (0.070, 0.40, 0.184, 2.03, 0.063, "4ja", "(E and Z)-4-(2′-butenyl)-2,2-dimethyl-3-phenyl-2,5-dihydrofuran", "4jb", "2,2-Dimethyl-4-(1′-methyl-2′-propenyl)-3-phenyl-2,5-dihydrofuran"),
    "scheme8_1j_3f": (0.131, 0.75, 0.345, 3.81, 0.055, "4ja", "(E and Z)-4-(2′-butenyl)-2,2-dimethyl-3-phenyl-2,5-dihydrofuran", "4jb", "2,2-Dimethyl-4-(1′-methyl-2′-propenyl)-3-phenyl-2,5-dihydrofuran"),
}
for suffix, (s_mass, s_mmol, r_mass, r_mmol, mixture_mass, label_a, name_a, label_b, name_b) in scheme8.items():
    record = take(suffix)
    add_page_evidence(record, 9)
    set_specific_amounts(participant(record, "substrate"), s_mass, s_mmol, e9)
    set_specific_amounts(participant(record, "allylic_chloride"), r_mass, r_mmol, e9)
    product_a = participant(record, "product_a")
    product_b = participant(record, "product_b")
    assert product_a["label"]["value"] == label_a and product_b["label"]["value"] == label_b
    product_a["name"] = fact(name_a, e9)
    product_b["name"] = fact(name_b, e9)
    extend_outcome(record, "combined_yield", e9)
    extend_outcome(record, "product_ratio", e9)
    upsert_outcome(
        record,
        "combined_product_mass",
        {"number": mixture_mass, "unit": "g"},
        e9,
        ["product_a", "product_b"],
    )
    add_note(record, "The specific paragraph reports a product-mixture mass; individual isomer masses are not reported.", e9)


# Page 9: detailed dimerization experiment for 5a.
record = take("eq2_dimerization_1a")
add_page_evidence(record, 9)
set_specific_amounts(participant(record, "allenol_1a"), 0.069, 0.49, e9)
pdcl2 = participant(record, "pdcl2")
pdcl2["amounts"] = [quantity("mass", 0.005, "g", e9), quantity("catalyst_loading", 5, "mol%", e9)]
participant(record, "dma")["amounts"] = [quantity("volume", 3, "mL", e9)]
set_product(participant(record, "product_5a"), "3-Butyl-4-(2′-ethylidene-1′-methylenehexyl)-2-methyl-2,5-dihydrofuran", 0.007, "g", e9)
extend_outcome(record, "isolated_yield", e9)
add_workup(record, e9)
add_note(record, "The stereochemistry of 5a was confirmed by 1H-1H NOESY spectra.", e9)
replace_unresolved(
    record,
    remove_contains=("Exact reactant/catalyst/solvent quantities",),
    add=("Product SMILES is not assigned from the name alone; no structure drawing occurs on page 9.",),
)


# Page 9: detailed stoichiometric pi-allylpalladium experiment.
record = take("scheme10_1j")
add_page_evidence(record, 9)
set_specific_amounts(participant(record, "allenol_1j"), 0.030, 0.17, e9)
dimer = participant(record, "allylpalladium_dimer")
dimer["amounts"] = [
    quantity("mass", 0.063, "g", e9),
    quantity("amount", 0.17, "mmol", e9),
    quantity("equivalents", 1, "equiv", e9),
]
participant(record, "dma")["amounts"] = [quantity("volume", 1.2, "mL", e9)]
participant(record, "product_11")["name"] = fact("2,2-Dimethyl-3-phenyl-2,5-dihydrofuran", e9)
participant(record, "product_4j")["name"] = fact("2,2-Dimethyl-3-phenyl-4-(2′-propenyl)-2,5-dihydrofuran", e9)
extend_outcome(record, "combined_yield", e9)
extend_outcome(record, "product_ratio", e9)
upsert_outcome(record, "combined_product_mass", {"number": 0.010, "unit": "g"}, e9, ["product_11", "product_4j"])
upsert_outcome(record, "yield_measurement_basis", "isolated mixture after silica-gel chromatography", e9, ["product_11", "product_4j"])
add_workup(record, e9)
replace_unresolved(record, remove_contains=("does not state whether 33%",))


# Page 9: detailed 1s/4-bromo-1,2-butadiene experiment.
record = take("eq5_1s_3g")
add_page_evidence(record, 9)
set_specific_amounts(participant(record, "allenol_1s"), 0.042, 0.30, e9)
bromoallene = participant(record, "bromoallene_3g")
bromoallene["amounts"] = [
    quantity("mass", 0.206, "g", e9),
    quantity("amount", 1.55, "mmol", e9),
    quantity("equivalents", 5, "equiv", e9),
]
pdcl2 = participant(record, "pdcl2")
pdcl2["amounts"] = [quantity("mass", 0.003, "g", e9), quantity("catalyst_loading", 5, "mol%", e9)]
participant(record, "dma")["amounts"] = [quantity("volume", 2, "mL", e9)]
participant(record, "product_13")["name"] = fact("3-(1′-Methylenepropenyl)-1-oxaspiro[4.5]dec-3-ene", e9)
participant(record, "product_5s")["name"] = fact("3-(1-cyclohexylidenemethylvinyl)-1-oxaspiro[4.5]dec-3-ene", e9)
extend_outcome(record, "combined_yield", e9)
extend_outcome(record, "product_ratio", e9)
upsert_outcome(record, "combined_product_mass", {"number": 0.032, "unit": "g"}, e9, ["product_13", "product_5s"])
upsert_outcome(record, "yield_measurement_basis", "isolated mixture after silica-gel chromatography", e9, ["product_13", "product_5s"])
add_workup(record, e9)
replace_unresolved(record, remove_contains=("does not state whether 55%",))


# Machine records remain candidates here; merge will quarantine them as needs_review.
for record in selected:
    record["status"] = "candidate"
    record["completeness"] = "partial"
    record["review"]["method"] = "none"
    record["review"]["reviewer"] = None
    record["review"]["checked_fields"] = []

OUT.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of the 4b characterization paragraph",
                    "finding": "Characterization only; it continues the already represented 1b/3a experiment and does not define a new reaction run.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "two-column Experimental Section, examples (3)-(16), products 4c-4p",
                    "finding": "Fourteen specific executions corresponding to Table 2 entries 3-16 were checked row by row. Reactant/product masses, mmol values, product names, and isolated product masses were merged into the existing records. The 4g paragraph reports 54%, while Table 2 reports 55%; both were retained.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": [f"{DOC}:table2_entry_{n:02d}" for n in range(2, 17)],
            "unresolved": [
                "The specific examples do not restate catalyst mass, DMA volume, workup, or chromatography conditions; the shared general procedure is separate on page 6.",
                "Product SMILES were not generated from names alone because no structure drawings occur on this page.",
                "Table 2 and the specific experimental paragraph disagree on the 4g isolated yield (55% versus 54%).",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of 4p, followed by examples (17)-(22)",
                    "finding": "The 4p characterization continuation was linked to its existing record. Six specific experiments for 4q, 4r, the 4s/5s two-product run, and 4t-4v were merged into existing Table 2/Scheme 4/Scheme 5 records with exact quantities and product-specific masses/yields.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "right column examples (23)-(29), products 6a-6g",
                    "finding": "Seven specific Table 3 executions were checked individually and enriched with exact substrate/allyl-bromide quantities and isolated product masses. The 6g row retains 33% recovered 2g; its characterization continues onto page 9.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": [
                f"{DOC}:table2_entry_16", f"{DOC}:table2_entry_17",
                f"{DOC}:scheme4_1r", f"{DOC}:scheme4_1s_5equiv",
                f"{DOC}:scheme5_3b", f"{DOC}:scheme5_3c", f"{DOC}:scheme5_3d",
                *[f"{DOC}:table3_entry_{n:02d}" for n in range(1, 8)],
            ],
            "unresolved": [
                "The specific examples do not restate catalyst mass or DMA volume; catalyst loading and solvent identity remain from the shared conditions.",
                "No individual masses are reported for the two products 4s and 5s beyond the explicit 0.007 g and 0.081 g values; no unreported side products were inferred.",
                "Product SMILES were not generated from names alone because no structure drawings occur on this page.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of example (29), product 6g",
                    "finding": "Characterization only; linked to Table 3 entry 7 and not counted as a new experiment.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "left column examples (30)-(33), 4aa/4ab and 4ja/4jb mixtures",
                    "finding": "Four distinct PdCl2 experiments were merged into the existing Scheme 8 records. Exact reagent scales, combined product masses, combined yields, and product ratios were retained. The two Pd2(dba)3 rows from Scheme 8 are not repeated on this page and were not modified.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "bottom-left and upper/middle-right detailed procedures for 5a, 11/4j, and 13/5s",
                    "finding": "Three detailed experiments were merged into existing eq 2, Scheme 10, and eq 5 records with exact quantities, DMA volumes, workup, silica-gel chromatography, product-mixture masses, yields, and ratios.",
                    "evidence_ids": ev(9),
                },
                {
                    "region": "lower-right acknowledgment and Supporting Information statement",
                    "finding": "No reaction experiment. The article states that spectra are available online, but no SI file was supplied or explicitly associated in this workspace; no SI evidence was imported.",
                    "evidence_ids": ev(9),
                },
            ],
            "record_ids": [
                f"{DOC}:table3_entry_07",
                f"{DOC}:scheme8_1a_3e_pdcl2", f"{DOC}:scheme8_1a_3f_pdcl2",
                f"{DOC}:scheme8_1j_3e", f"{DOC}:scheme8_1j_3f",
                f"{DOC}:eq2_dimerization_1a", f"{DOC}:scheme10_1j", f"{DOC}:eq5_1s_3g",
            ],
            "unresolved": [
                "The E/Z composition within 4aa and 4ja is not unambiguously quantified in the specific paragraphs and remains unresolved.",
                "Individual isomer masses are not reported for the 4aa/4ab, 4ja/4jb, 11/4j, or 13/5s mixtures.",
                "The online Supporting Information mentioned by the paper was not provided and remains unassociated.",
                "Product SMILES were not generated from names alone because no structure drawings occur on this page.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["evidence_id"] in {f"{DOC}:page{p}:text" for p in (7, 8, 9)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task["evidence_id"].replace(":text", ":image")
        task["reason"] = "Original page image inspected; coverage recorded in coverage/pages_0007_0009.json."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"output": str(OUT), "records": len(selected), "coverage": str(COVERAGE)}, ensure_ascii=False))
