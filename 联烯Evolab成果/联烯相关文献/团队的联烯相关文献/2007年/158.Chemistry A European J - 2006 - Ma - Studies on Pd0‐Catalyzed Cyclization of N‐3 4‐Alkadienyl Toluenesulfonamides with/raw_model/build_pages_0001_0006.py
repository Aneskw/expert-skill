#!/usr/bin/env python3
"""Build evidence-linked machine records for PDF pages 1--6."""

from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_45c8b9340dcc6c98"
OUT = Path(__file__).resolve().parent
RUN = OUT.parent


def page_ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def make_record(
    rid,
    pages,
    kind,
    participants,
    conditions,
    outcomes,
    *,
    notes=(),
    unresolved=(),
    step=True,
):
    evidence = []
    for page in pages:
        for eid in page_ev(page):
            if eid not in evidence:
                evidence.append(eid)
    record = {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{
            "step_id": "step_1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if step else [],
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "Machine extraction requires chemical source review.",
                "No supporting-information file was explicitly associated.",
            ],
        },
    }
    return record


SMILES = {
    "6a": "Ic1ccccc1",
    "6b": "COc1ccc(I)cc1",
    "6c": "COC(=O)c1ccc(I)cc1",
    "6d": "Brc1ccc(I)cc1",
    "6e": "Cc1ccccc1I",
    "6f": "Cc1ccc(I)cc1",
    "6g": "Ic1cccc2ccccc12",
    "6h": "N#Cc1ccc(I)cc1",
    "6i": "CC(=O)c1ccc(I)cc1",
    "6j": "Brc1ccccc1",
    "6k": "COc1ccc(Br)cc1",
    "6l": "O=[N+]([O-])c1ccc(Br)cc1",
    "6m": "Ic1cccs1",
    "6n": "Brc1ccccn1",
    "6p": "CCCCC=CI",
    "6q": "O=[N+]([O-])c1ccc(I)cc1",
    "6r": "Ic1ccc(I)cc1",
    "iodobenzene": "Ic1ccccc1",
    "bromobenzene": "Brc1ccccc1",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "NaOH": "[Na+].[OH-]",
    "DMF": "CN(C)C=O",
    "toluene": "Cc1ccccc1",
    "MeOH": "CO",
    "CH2Cl2": "ClCCl",
    "CH3CN": "CC#N",
    "THF": "C1CCOC1",
    "1,4-dioxane": "O1CCOCC1",
    "Et3N": "CCN(CC)CC",
    "NaH": "[Na+].[H-]",
    "KOH": "[K+].[OH-]",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O",
}


records = []


# Page 1: cited prior chemistry and the authors' earlier report.
ev = page_ev(1)
records.append(make_record(
    "page1_scheme1_prior_carbopalladation_mechanism", [1], "mechanism",
    [
        participant("amino_allene", "reactant", "generic amino allene", ev),
        participant("r4pdx", "unspecified_agent", "R4PdX", ev),
        participant("pi_allylpalladium", "unspecified_agent", "pi-allylic palladium intermediate", ev),
        participant("azetidine", "product", "generic azetidine", ev),
        participant("tetrahydropyridine", "product", "generic tetrahydropyridine", ev),
    ], [], [],
    notes=("Scheme 1 summarizes cited prior coupling-cyclization pathways, not a new experiment in this paper.",),
    unresolved=("Generic R groups prevent complete structure assignment.", "No numerical conditions or outcomes are shown."),
))
records.append(make_record(
    "page1_scheme2_prior_five_membered_cyclization", [1], "literature_example",
    [
        participant("substrate", "reactant", "generic 3-substituted beta-amino allene", ev),
        participant("organic_halide", "reactant", "R4X", ev, amounts=[field("equivalents", qty(1.5, "equiv"), ev)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", ev, amounts=[field("catalyst_loading", qty(5, "mol%"), ev)]),
        participant("base", "reagent", "K2CO3", ev, smiles=SMILES["K2CO3"], amounts=[field("equivalents", qty(4, "equiv"), ev)]),
        participant("solvent", "solvent", "DMF", ev, smiles=SMILES["DMF"]),
        participant("product", "product", "generic 2,3-dihydropyrrole", ev),
    ], [field("temperature", qty(70, "°C"), ev)], [],
    notes=("Scheme 2 is explicitly described as the authors' previously reported result (reference 8).",),
    unresolved=("Generic substituents prevent full structure assignment.", "Reaction time and yield are not shown."),
))


# Page 2: starting-material preparation scheme, Scheme 3, and the Scheme 4 comparison.
ev = page_ev(2)
records.append(make_record(
    "page2_table1_general_starting_material_preparation", [2], "general_scheme",
    [
        participant("propargylic_alcohols", "reactant", "propargylic alcohols 1a-g, 1j-u", ev),
        participant("allenoates", "product", "3,4-allenoates 2a-g, 2j-u", ev),
        participant("allenols", "product", "3,4-allenols 3a-g, 3j-u", ev),
        participant("allenyl_amides", "product", "3,4-allenyl amides 4a-z", ev),
        participant("lialh4", "reagent", "LiAlH4", ev, smiles="[Li+].[AlH4-]"),
        participant("phthalimide", "reagent", "phthalimide", ev, smiles="O=C1NC(=O)c2ccccc21"),
        participant("dead", "reagent", "DEAD", ev, smiles="CCOC(=O)N=NC(=O)OCC"),
        participant("pph3", "reagent", "PPh3", ev, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1"),
        participant("hydrazine_hydrate", "reagent", "N2H4.H2O", ev),
        participant("triethylamine", "reagent", "NEt3", ev, smiles=SMILES["Et3N"]),
        participant("r4cl", "reagent", "R4Cl", ev),
    ], [
        field("step_1_temperature", qty(140, "°C"), ev),
        field("step_2_initial_temperature", qty(0, "°C"), ev),
        field("step_2_warm_to", "r.t.", ev),
        field("step_3_initial_temperature", qty(0, "°C"), ev),
        field("step_3_warm_to", "r.t.", ev),
        field("step_4_temperature", "reflux", ev),
        field("step_5_initial_temperature", qty(0, "°C"), ev),
        field("step_5_warm_to", "r.t.", ev),
    ], [],
    notes=("Table 1 rows define substituent identities for compounds 4a-z; they do not report row-specific reactions or yields and were not inflated into separate experiments.",),
    unresolved=("The general scheme does not give row-specific quantities, times, yields, workups, or purifications.", "R-group structures are generic."),
))

for substrate, product in [("3v", "5v"), ("3w", "trans-5w")]:
    rid = f"page2_scheme3_{substrate}_to_{product.replace('-', '_')}"
    records.append(make_record(
        rid, [2], "reported_experiment",
        [
            participant("substrate", "reactant", substrate, ev),
            participant("phthalimide", "reagent", "phthalimide", ev, smiles="O=C1NC(=O)c2ccccc21"),
            participant("dead", "reagent", "DEAD", ev, smiles="CCOC(=O)N=NC(=O)OCC"),
            participant("pph3", "reagent", "PPh3", ev, smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1"),
            participant("hydrazine_hydrate", "reagent", "N2H4.H2O", ev),
            participant("triethylamine", "reagent", "NEt3", ev, smiles=SMILES["Et3N"]),
            participant("tosyl_chloride", "reagent", "TsCl", ev, smiles="Cc1ccc(S(=O)(=O)Cl)cc1"),
            participant("product", "product", product, ev),
        ], [
            field("step_1_initial_temperature", qty(0, "°C"), ev),
            field("step_1_warm_to", "r.t.", ev),
            field("step_2_temperature", "reflux", ev),
            field("step_3_initial_temperature", qty(0, "°C"), ev),
            field("step_3_warm_to", "r.t.", ev),
        ], [],
        notes=("The source states that this substrate directly gave the cycloisomerization product during the Mitsunobu amination sequence.",),
        unresolved=("No numerical yield, quantities, times, workup, or purification are reported on the covered page.", "Product connectivity and stereochemistry remain machine-unverified."),
    ))

records.append(make_record(
    "page2_scheme4_prior_unsubstituted_amino_allene", [2], "literature_example",
    [
        participant("substrate", "reactant", "N-(2-methyl-3,4-pentadienyl)toluenesulfonamide", ev),
        participant("halide", "reactant", "iodobenzene 6a", ev, smiles=SMILES["6a"], amounts=[field("equivalents", qty(1.5, "equiv"), ev)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", ev, amounts=[field("catalyst_loading", qty(5, "mol%"), ev)]),
        participant("base", "reagent", "K2CO3", ev, smiles=SMILES["K2CO3"], amounts=[field("equivalents", qty(4, "equiv"), ev)]),
        participant("solvent", "solvent", "DMF", ev, smiles=SMILES["DMF"]),
        participant("azetidine_product", "product", "trans four-membered product", ev),
        participant("tetrahydropyridine_product", "product", "six-membered product", ev),
    ], [field("temperature", qty(70, "°C"), ev), field("time", qty(16, "h"), ev)], [
        field("combined_reported_yield", qty(66, "%"), ev, ["azetidine_product", "tetrahydropyridine_product"]),
        field("four_to_six_membered_product_ratio", "4:96", ev, ["azetidine_product", "tetrahydropyridine_product"]),
    ],
    notes=("This comparison is attributed to references 4 and 5, not claimed as a new experiment in the present paper.",),
    unresolved=("Yield measurement basis and detailed experimental procedure are not reported on the covered page.",),
))


def a_participants(evidence, substrate, halide_label, products, *, table2=False):
    halide_name = "iodobenzene" if halide_label == "6a" else halide_label
    parts = [
        participant("substrate", "reactant", substrate, evidence, amounts=[field("amount", qty(0.30, "mmol"), evidence)]),
        participant("halide", "reactant", halide_name, evidence, smiles=SMILES.get(halide_label), amounts=[field("amount", qty(0.45, "mmol"), evidence)]),
        participant("base", "reagent", "K2CO3", evidence, smiles=SMILES["K2CO3"], amounts=[field("amount", qty(1.20, "mmol"), evidence)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", evidence, amounts=[field("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("solvent", "solvent", "DMF", evidence, smiles=SMILES["DMF"]),
    ]
    for entity, label in products:
        parts.append(participant(entity, "product", label, evidence))
    return parts


# Table 2; entry 1 also cites its Scheme 4 rendering on page 2.
table2 = [
    (1, "4a", 7.5, 78, "7aa", None, None),
    (2, "4b", 8, 55, "7ba", 10, "8ba"),
    (3, "4c", 12, 66, "7ca", 11, "8ca"),
    (4, "4d", 42, 77, "7da", 6, "8da"),
    (5, "4e", 16, 76, "7ea", 0, None),
    (6, "4f", 48, 65, "7fa", 0, None),
    (7, "4g", 24, 74, "7ga", 0, None),
    (8, "4h", 5, 55, "7ha", 0, None),
]
for entry, substrate, time, y7, p7, y8, p8 in table2:
    pages = [2, 3] if entry == 1 else [3]
    evs = sum((page_ev(p) for p in pages), [])
    products = [("product7", p7)]
    if p8:
        products.append(("product8", p8))
    parts = a_participants(evs, substrate, "6a", products)
    outcomes = [field("isolated_yield_7", qty(y7, "%"), evs, ["product7"]), field("yield_measurement_basis", "isolated", evs)]
    if p8:
        outcomes.append(field("isolated_yield_8", qty(y8, "%"), evs, ["product8"]))
    elif entry == 1:
        outcomes.append(field("other_isomers_isolated_yield", qty(3, "%", qualifier="lt", raw_text="<3%"), evs))
    else:
        outcomes.append(field("isolated_yield_8", qty(0, "%"), evs))
    records.append(make_record(
        f"table2_entry_{entry}", pages, "substrate_scope_entry", parts,
        [field("temperature", qty(70, "°C"), evs), field("time", qty(time, "h"), evs)], outcomes,
        unresolved=("No solvent volume, workup, or purification is reported in Table 2.", "Substrate and product structures remain machine-unverified.", "No SI file was explicitly associated."),
    ))


# Page 3: Scheme 5, Eq. 1, and generic failed substrate classes.
ev = page_ev(3)
parts = a_participants(ev, "4j", "6a", [("product", "9ja")])
records.append(make_record(
    "page3_scheme5_4j_to_9ja", [3], "reported_experiment", parts,
    [field("temperature", qty(70, "°C"), ev), field("time", qty(15, "h"), ev)],
    [field("reported_yield", qty(14, "%"), ev, ["product"])],
    notes=("The source reports 9ja instead of the anticipated product 7ja.",),
    unresolved=("Yield measurement basis, workup, and purification are not reported here.", "Structures remain machine-unverified."),
))
records.append(make_record(
    "page3_scheme5_proposed_heck_path", [3], "mechanism",
    [participant("substrate", "reactant", "4j", ev), participant("intermediate", "unspecified_agent", "anticipated 7ja", ev), participant("halide", "reactant", "PhI", ev, smiles=SMILES["6a"]), participant("palladium", "catalyst", "Pd", ev), participant("product", "product", "9ja", ev)],
    [], [], notes=("Scheme 5 depicts a coupling-cyclization/Heck pathway through 7ja; the text does not report 7ja as an isolated product.",),
    unresolved=("The depicted pathway is mechanistic and its intermediate was not reported as isolated.",),
))
parts = a_participants(ev, "4i", "6a", [("product", "trans-11ia")])
records.append(make_record(
    "page3_equation1_4i_to_11ia", [3], "reported_experiment", parts,
    [field("temperature", qty(70, "°C"), ev), field("time", qty(48, "h"), ev)],
    [field("reported_yield", qty(19, "%"), ev, ["product"]), field("relative_configuration", "trans", ev, ["product"])],
    unresolved=("Yield measurement basis, workup, and purification are not reported here.", "The trans product structure remains machine-unverified."),
))
for rid, halide in [("page3_failed_1_alkynyl_halides", "1-alkynyl halides"), ("page3_failed_aryl_chlorides", "aryl chlorides")]:
    records.append(make_record(
        rid, [3], "reported_experiment",
        [participant("allenyl_amide", "reactant", "3,4-allenyl amide (unspecified)", ev), participant("halide", "reactant", halide, ev), participant("expected_product", "product", "expected coupling-cyclization product", ev)],
        [], [field("expected_product_formation", "not formed", ev, ["expected_product"])],
        notes=("The source reports failure for this substrate class without identifying a specific row or substrate.",),
        unresolved=("Exact substrates, quantities, conditions, and analytical detection limit are not given.",),
    ))


# Table 3 substrate scope.
table3 = [
    (1, "4a", "6b", "p-MeOC6H4I (6b)", 5.5, 79, "7ab", 0, None, None),
    (2, "4a", "6c", "p-MeO2CC6H4I (6c)", 24, 73, "7ac", 0, None, None),
    (3, "4a", "6d", "p-BrC6H4I (6d)", 10, 82, "7ad", 0, None, None),
    (4, "4a", "6e", "o-MeC6H4I (6e)", 10, 84, "7ae", 0, None, None),
    (5, "4a", "6f", "p-MeC6H4I (6f)", 8, 83, "7af", 0, None, None),
    (6, "4a", "6g", "1-iodonaphthalene (6g)", 12, 80, "7ag", 0, None, None),
    (7, "4b", "6b", "p-MeOC6H4I (6b)", 5.5, 68, "7bb", None, "8bb", "86:14"),
    (8, "4b", "6c", "p-MeO2CC6H4I (6c)", 10, 77, "7bc", None, "8bc", "86:15"),
    (9, "4f", "6b", "p-MeOC6H4I (6b)", 60, 77, "7fb", 0, None, None),
    (10, "4f", "6c", "p-MeO2CC6H4I (6c)", 96, 45, "7fc", 0, None, None),
    (11, "4d", "6h", "p-NCC6H4I (6h)", 60, 61, "7dh", 0, None, None),
    (12, "4d", "6i", "p-CH3COC6H4I (6i)", 52, 77, "7di", 0, None, None),
    (13, "4d", "6j", "PhBr (6j)", 16, 64, "7da", 10, "8da", None),
    (14, "4d", "6j_ortho_cl", "o-ClC6H4Br (printed 6j)", 58, 80, "7dj", 0, None, None),
    (15, "4d", "6k", "p-MeOC6H4Br (6k)", 36, 63, "7dk", 0, None, None),
    (16, "4d", "6l", "p-NO2C6H4Br (6l)", 30, 55, "7dl", 0, None, None),
    (17, "4a", "6m", "2-iodothiophene (6m)", 36, 68, "7am", 0, None, None),
    (18, "4a", "6n", "2-bromopyridine (6n)", 12, 68, "7an", 0, None, None),
]
for entry, substrate, halide_code, halide_name, time, y7, p7, y8, p8, ratio in table3:
    evs = page_ev(4)
    products = [("product7", p7)] + ([("product8", p8)] if p8 else [])
    parts = a_participants(evs, substrate, halide_code, products)
    parts[1]["label"] = fact(halide_name, evs)
    if halide_code == "6j_ortho_cl":
        parts[1]["smiles"] = fact("Brc1ccccc1Cl", evs)
    outcomes = []
    if ratio:
        outcomes += [field("combined_reported_yield", qty(y7, "%"), evs, ["product7", "product8"]), field("product_7_to_8_ratio_by_1H_NMR", ratio, evs, ["product7", "product8"])]
    else:
        outcomes.append(field("reported_yield_7", qty(y7, "%"), evs, ["product7"]))
        if p8:
            outcomes.append(field("reported_yield_8", qty(y8, "%"), evs, ["product8"]))
        else:
            outcomes.append(field("reported_yield_8", qty(0, "%"), evs))
    notes = []
    unresolved = ["Yield measurement basis, workup, and purification are not specified in Table 3.", "Structures remain machine-unverified.", "No SI file was explicitly associated."]
    if entry == 8:
        notes.append("The printed product ratio is 86:15, which sums to 101; it is preserved without correction.")
        unresolved.append("The source's 86:15 ratio requires review.")
    if entry == 14:
        notes.append("The source prints label 6j for both PhBr and o-ClC6H4Br; the duplicated label is preserved in the reactant text.")
        unresolved.append("The duplicated halide label 6j requires source review.")
    records.append(make_record(f"table3_entry_{entry}", [4], "substrate_scope_entry", parts, [field("temperature", qty(70, "°C"), evs), field("time", qty(time, "h"), evs)], outcomes, notes=notes, unresolved=unresolved))


def solvent_smiles(name):
    return SMILES.get(name)


# Table 4 optimization. Entries 15 and 21 are repeated in Table 5; merge that evidence below.
table4 = [
    (1, "K2CO3", 70, "DMF", 20, 84, 61, 3, 0),
    (2, "K2CO3", 70, "MeOH", 100, 76, 65, 0, 0),
    (3, "K2CO3", 70, "CH2Cl2", 100, 64, 73, 7, "trace"),
    (4, "K2CO3", 70, "CH3CN", 100, 68, 71, 7, 0),
    (5, "K2CO3", 70, "1,4-dioxane", 100, 67, 81, 8, 0),
    (6, "K2CO3", 70, "THF", 100, 58, 89, 6, 0),
    (7, "Et3N", 70, "Et3N", 100, 5, ">99:1", 0, 91),
    (8, "K2CO3", 70, "toluene", 100, 57, 90, 15, 0),
    (9, "K2CO3", 50, "toluene", 100, 68, 91, 11, 0),
    (10, "Et3N", 50, "toluene", 100, 3, ">99:1", 0, 81),
    (11, "NaH", 50, "toluene", 100, 28, 97, 7, 0),
    (12, "KOH", 50, "toluene", 100, 42, 92, 39, 0),
    (13, "Cs2CO3", 50, "toluene", 100, 48, 89, 6, 15),
    (14, "NaOH", 50, "toluene", 100, 53, 95, 6, 23),
    (15, "NaOH", 80, "toluene", 100, 41, 97, 12, 0),
    (16, "NaOH", 30, "toluene", 100, 48, 81, 17, 0),
    (17, "NaOH", 80, "DMF", 48, 43, 89, 0, 0),
    (18, "NaOH", 80, "toluene/DMF 1:1", 48, 57, 70, 0, 0),
    (19, "NaOH", 80, "toluene/DMF 5:1", 48, 51, 79, 0, 0),
    (20, "NaOH", 80, "toluene/DMF 10:1", 48, 59, 87, "trace", 0),
    (21, "NaOH", 80, "toluene/DMF 20:1", 48, 50, 95, 3, 0),
]
for entry, base, temp, solvent, time, y10, de10, y11, recovered in table4:
    pages = [4]
    if entry == 15:
        pages.append(3)
    if entry in (15, 21):
        pages.append(5)
    evs = sum((page_ev(p) for p in pages), [])
    parts = [
        participant("substrate", "reactant", "4k", evs, amounts=[field("amount", qty(0.30, "mmol"), evs)]),
        participant("halide", "reactant", "iodobenzene 6a", evs, smiles=SMILES["6a"], amounts=[field("amount", qty(0.45, "mmol"), evs)]),
        participant("base", "reagent", base, evs, smiles=SMILES.get(base), amounts=[field("amount", qty(1.20, "mmol"), evs)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", evs, amounts=[field("catalyst_loading", qty(5, "mol%"), evs)]),
        participant("solvent", "solvent", solvent, evs, smiles=solvent_smiles(solvent)),
        participant("product10", "product", "10ka", evs),
        participant("product11", "product", "11ka", evs),
    ]
    outcomes = [
        field("reported_yield_10ka", qty(y10, "%"), evs, ["product10"]),
        field("reported_yield_11ka", y11 if isinstance(y11, str) else qty(y11, "%"), evs, ["product11"]),
        field("recovered_starting_material_yield", recovered if isinstance(recovered, str) else qty(recovered, "%"), evs, ["substrate"]),
    ]
    if isinstance(de10, str):
        outcomes.append(field("diastereomeric_ratio_10ka", de10, evs, ["product10"]))
    else:
        outcomes.append(field("de_10ka", qty(de10, "%"), evs, ["product10"]))
    notes = []
    unresolved = ["Table 4 does not report solvent volume, workup, purification, or yield basis.", "Structures remain machine-unverified.", "No SI file was explicitly associated."]
    conditions = [field("temperature", qty(temp, "°C"), evs), field("time", qty(time, "h"), evs)]
    if entry == 1:
        notes.append("Page 3 prose gives 60% de for this experiment, while Table 4 prints 61%; the table value is retained as the structured outcome.")
        unresolved.append("The 60% versus 61% de discrepancy requires source review.")
    if entry == 15:
        outcomes += [field("de_11ka", qty(100, "%"), page_ev(3), ["product11"]), field("product_11ka_isomer", "trans-Z only", evs, ["product11"])]
        notes.append("Table 5 repeats the same substrate, conditions-B label, yields, and selectivities, but its shared reaction arrow prints 48 h whereas Table 4 prints 100 h.")
        conditions.append(field("conflicting_time_from_table5_shared_arrow", qty(48, "h"), page_ev(5)))
        unresolved.append("Table 4/Table 5 time conflict (100 h versus shared 48 h arrow) requires review; the repeated result was merged, not duplicated.")
    if entry == 21:
        notes.append("Table 5 entry 2 repeats this conditions-C experiment and is merged with the Table 4 row.")
    records.append(make_record(f"table4_entry_{entry}", pages, "optimization_entry", parts, conditions, outcomes, notes=notes, unresolved=unresolved))


# Page 5 Scheme 6 actual reaction and mechanism, plus Eq. 2.
ev = page_ev(5)
def condition_b_participants(substrate, halide_label, products, evidence):
    return [
        participant("substrate", "reactant", substrate, evidence),
        participant("halide", "reactant", halide_label, evidence, smiles=SMILES.get(halide_label.split()[0], SMILES.get(halide_label))),
        participant("base", "reagent", "NaOH", evidence, smiles=SMILES["NaOH"], amounts=[field("equivalents", qty(4, "equiv"), evidence)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", evidence, amounts=[field("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("solvent", "solvent", "toluene", evidence, smiles=SMILES["toluene"]),
    ] + [participant(entity, "product", label, evidence) for entity, label in products]

records.append(make_record(
    "page5_scheme6_4u_to_12", [5], "reported_experiment",
    condition_b_participants("4u", "iodobenzene 6a", [("product", "12")], ev),
    [field("temperature", qty(80, "°C"), ev), field("time", None, ev)],
    [field("reported_yield", qty(38, "%"), ev, ["product"])],
    notes=("Product 12 is described as the major carbopalladation-beta-elimination product.",),
    unresolved=("Reaction time, scale, workup, purification, yield basis, and side-product identities are not reported here.", "Structures remain machine-unverified."),
))
records.append(make_record(
    "page5_scheme6_beta_h_elimination_mechanism", [5], "mechanism",
    [participant("substrate", "reactant", "4u", ev), participant("organopalladium", "unspecified_agent", "depicted organopalladium intermediate", ev), participant("product", "product", "12", ev)],
    [], [], notes=("The source proposes beta-H elimination from a benzylic organopalladium intermediate.",),
    unresolved=("The organopalladium intermediate is proposed rather than isolated.",),
))
records.append(make_record(
    "page5_equation2_13_to_14", [5], "reported_experiment",
    condition_b_participants("13", "iodobenzene 6a", [("product", "14")], ev),
    [field("temperature", qty(80, "°C"), ev), field("time", None, ev)],
    [field("reported_yield", qty(21, "%"), ev, ["product"]), field("diastereomeric_ratio", ">99:1", ev, ["product"])],
    unresolved=("Reaction time, scale, workup, purification, and yield basis are not reported here.", "Structures remain machine-unverified."),
))


# Tables 5 and 6 share a compact record builder.
def bc_record(rid, page, substrate, halide_code, halide_name, condition, product10, y10, de10, product11, y11, de11, *, note=None):
    evs = page_ev(page)
    solvent = "toluene" if condition == "B" else "toluene/DMF 20:1"
    parts = [
        participant("substrate", "reactant", substrate, evs, amounts=[field("amount", qty(0.30, "mmol"), evs)]),
        participant("halide", "reactant", halide_name, evs, smiles=SMILES.get(halide_code), amounts=[field("amount", qty(0.45, "mmol"), evs)]),
        participant("base", "reagent", "NaOH", evs, smiles=SMILES["NaOH"], amounts=[field("amount", qty(1.20, "mmol"), evs), field("equivalents", qty(4, "equiv"), evs)]),
        participant("catalyst", "catalyst", "Pd(PPh3)4", evs, amounts=[field("catalyst_loading", qty(5, "mol%"), evs)]),
        participant("solvent", "solvent", solvent, evs, smiles=SMILES.get(solvent), amounts=[field("volume", qty(2.0, "mL"), evs)]),
        participant("product10", "product", product10, evs),
        participant("product11", "product", product11, evs),
    ]
    outcomes = [field("reported_yield_10", y10 if isinstance(y10, str) else qty(y10, "%"), evs, ["product10"]), field("reported_yield_11", y11 if isinstance(y11, str) else qty(y11, "%"), evs, ["product11"])]
    if de10 is not None:
        outcomes.append(field("diastereomeric_ratio_10" if isinstance(de10, str) else "de_10", de10 if isinstance(de10, str) else qty(de10, "%"), evs, ["product10"]))
    if de11 is not None:
        outcomes.append(field("diastereomeric_ratio_11" if isinstance(de11, str) else "de_11", de11 if isinstance(de11, str) else qty(de11, "%"), evs, ["product11"]))
    notes = [note] if note else []
    unresolved = ["Workup, purification, and yield measurement basis are not reported in the table.", "Structures remain machine-unverified.", "No SI file was explicitly associated."]
    if condition == "C":
        unresolved.append("The 20:1 toluene/DMF ratio is reported, but component-specific volumes are not given.")
    return make_record(rid, [page], "substrate_scope_entry", parts, [field("temperature", qty(80, "°C"), evs), field("time", qty(48, "h"), evs), field("solvent", solvent, evs)], outcomes, notes=notes, unresolved=unresolved)


table5 = [
    (3, "4l", "B", "10la", 42, 96, "11la", 4, ">99:1"),
    (4, "4l", "C", "10la", 61, 86, "11la", 3, 62),
    (5, "4m", "B", "10ma", 35, 95, "11ma", 9, ">99:1"),
    (6, "4m", "C", "10ma", 45, 88, "11ma", 3, None),
    (7, "4n", "B", "10na", 63, 86, "11na", "trace", None),
    (8, "4q", "B", "10qa", 36, 90, "11qa", 13, ">99:1"),
    (9, "4q", "C", "10qa", 56, 82, "11qa", 7, 71),
    (10, "4r", "B", "10ra", 37, 89, "11ra", 17, ">99:1"),
    (11, "4r", "C", "10ra", 58, 88, "11ra", 6, 84),
    (12, "4s", "B", "10sa", 7, ">99:1", "11sa", 12, ">99:1"),
    (13, "4t", "B", "10ta", 5, ">99:1", "11ta", 8, ">99:1"),
    (14, "4t", "C", "10ta", 7, ">99:1", "11ta", 7, ">99:1"),
    (15, "4v", "B", "10va", 38, ">99:1", "11va", "trace", None),
    (16, "4v", "C", "10va", 39, ">99:1", "11va", "trace", None),
    (17, "4w", "B", "10wa", 15, ">99:1", "11wa", "trace", None),
    (18, "4x", "B", "10xa", 41, 93, "11xa", "trace", None),
    (19, "4x", "C", "10xa", 49, ">99:1", "11xa", "trace", None),
    (20, "4y", "B", "10ya", 21, 88, "11ya", 4, 86),
    (21, "4y", "C", "10ya", 32, 84, "11ya", 5, 89),
    (22, "4z", "B", "10za", "trace", None, "11za", 30, ">99:1"),
]
for row in table5:
    entry, substrate, cond, p10, y10, de10, p11, y11, de11 = row
    note = "Footnote c states that product 11ma was a mixture of three isomers; no single de value is assigned." if entry == 6 else None
    records.append(bc_record(f"table5_entry_{entry}", 5, substrate, "6a", "iodobenzene 6a", cond, p10, y10, de10, p11, y11, de11, note=note))


table6 = [
    (1, "6j", "bromobenzene 6j", "B", "10la", 12, 94, "11la", 2, ">99:1"),
    (2, "6b", "p-MeOC6H4I 6b", "B", "10lb", 40, 92, "11lb", 5, 94),
    (3, "6b", "p-MeOC6H4I 6b", "C", "10lb", 55, 85, "11lb", 4, 64),
    (4, "6f", "p-MeC6H4I 6f", "B", "10lf", 46, 92, "11lf", 7, 89),
    (5, "6f", "p-MeC6H4I 6f", "C", "10lf", 50, 88, "11lf", 2, 72),
    (6, "6q", "p-NO2C6H4I 6q", "B", "10lq", 14, ">99:1", "11lq", "trace", None),
    (7, "6i", "p-CH3COC6H4I 6i", "B", "10li", 24, 85, "11li", "trace", None),
    (8, "6i", "p-CH3COC6H4I 6i", "C", "10li", 60, 73, "11li", "trace", None),
    (9, "6h", "p-NCC6H4I 6h", "B", "10lh", 28, 88, "11lh", "trace", None),
    (10, "6h", "p-NCC6H4I 6h", "C", "10lh", 62, 77, "11lh", "trace", None),
    (11, "6g", "1-iodonaphthalene 6g", "B", "10lg", 19, 76, "11lg", "trace", None),
    (12, "6g", "1-iodonaphthalene 6g", "C", "10lg", 31, 61, "11lg", "trace", None),
    (13, "6m", "2-iodothiophene 6m", "B", "10lm", 37, 89, "11lg", 5, ">99:1"),
    (14, "6m", "2-iodothiophene 6m", "C", "10lm", 61, 68, "11lm", 6, ">99:1"),
    (15, "6p", "(E)-1-hexenyl iodide 6p", "B", "10lp", 29, 95, "11lp", "trace", None),
    (16, "6p", "(E)-1-hexenyl iodide 6p", "C", "10lp", 53, 90, "11lp", "trace", None),
]
for row in table6:
    entry, hcode, hname, cond, p10, y10, de10, p11, y11, de11 = row
    note = "Table 6 prints product label 11lg in entry 13 although the corresponding 2-iodothiophene labels are otherwise lm; the printed label is preserved." if entry == 13 else None
    records.append(bc_record(f"table6_entry_{entry}", 6, "4l", hcode, hname, cond, p10, y10, de10, p11, y11, de11, note=note))


# Scheme 7 and page-6 experimental procedures.
ev = page_ev(6)
for rid, halide_code, halide_name, products in [
    ("page6_scheme7_4q_with_6q", "6q", "p-NO2C6H4I 6q", [("product10", "10qq", 32, 89), ("product11", "11qq", 14, ">99:1")]),
    ("page6_scheme7_4q_with_6r", "6r", "1,4-diiodobenzene 6r", [("product", "15", 35, 88)]),
]:
    parts = condition_b_participants("4q", halide_name, [(entity, label) for entity, label, _, _ in products], ev)
    parts[1]["smiles"] = fact(SMILES[halide_code], ev)
    outcomes = []
    for entity, label, yld, de in products:
        outcomes.append(field(f"reported_yield_{label}", qty(yld, "%"), ev, [entity]))
        if isinstance(de, str):
            outcomes.append(field(f"diastereomeric_ratio_{label}", de, ev, [entity]))
        else:
            outcomes.append(field(f"de_{label}", qty(de, "%"), ev, [entity]))
    records.append(make_record(
        rid, [6], "reported_experiment", parts,
        [field("temperature", qty(80, "°C"), ev), field("time", None, ev)], outcomes,
        unresolved=("Conditions B do not specify reaction time, scale, workup, purification, or yield basis for Scheme 7.", "Structures and stereochemistry remain machine-unverified."),
    ))

records.append(make_record(
    "page6_procedure1_ethyl_allenoate_2c", [6], "reported_experiment",
    [
        participant("alcohol", "reactant", "2-butyn-1-ol 1c", ev, smiles="CC#CCO", amounts=[field("mass", qty(2.969, "g"), ev), field("amount", qty(42.4, "mmol"), ev)]),
        participant("orthoester", "reactant", "triethyl orthopropionate", ev, smiles="CCC(OCC)(OCC)OCC", amounts=[field("volume", qty(30, "mL"), ev), field("mass", qty(26.4, "g"), ev), field("amount", qty(150, "mmol"), ev)]),
        participant("acid", "catalyst", "propanoic acid", ev, smiles="CCC(=O)O"),
        participant("product", "product", "ethyl 2,3-dimethylpenta-3,4-dienoate 2c", ev, smiles="CCOC(=O)C(C)C(C)=C=C", amounts=[field("mass", qty(2.960, "g"), ev)]),
    ], [
        field("temperature", qty(140, "°C"), ev), field("time", qty(3, "h"), ev),
        field("purification", "flash chromatography on silica gel; petroleum ether/Et2O 3:1", ev),
    ], [field("isolated_yield", qty(64, "%"), ev, ["product"]), field("yield_measurement_basis", "isolated product mass after flash chromatography", ev)],
    unresolved=("The catalytic propanoic-acid quantity is not specified.", "Candidate structures remain machine-unverified.", "No SI file was explicitly associated."),
))

records.append(make_record(
    "page6_procedure2_allenol_3d", [6], "reported_experiment",
    [
        participant("allenoate", "reactant", "2-methyl-3-(n-heptyl)penta-3,4-dienoate 2d", ev, smiles="CCOC(=O)C(C)C(CCCCCCC)=C=C", amounts=[field("mass", qty(3.820, "g"), ev), field("amount", qty(16.0, "mmol"), ev)]),
        participant("lialh4", "reagent", "LiAlH4", ev, smiles="[Li+].[AlH4-]", amounts=[field("mass", qty(0.734, "g"), ev), field("amount", qty(19.3, "mmol"), ev)]),
        participant("thf_substrate", "solvent", "THF (substrate solution)", ev, smiles=SMILES["THF"], amounts=[field("volume", qty(30, "mL"), ev)]),
        participant("thf_reagent", "solvent", "THF (LiAlH4 suspension)", ev, smiles=SMILES["THF"], amounts=[field("volume", qty(30, "mL"), ev)]),
        participant("product", "product", "2-methyl-3-(n-heptyl)penta-3,4-dienol 3d", ev, smiles="OCC(C)C(CCCCCCC)=C=C", amounts=[field("mass", qty(1.909, "g"), ev)]),
    ], [
        field("initial_temperature", "ice bath", ev), field("temperature_program", "ice bath to r.t.", ev), field("time", "until complete by TLC", ev),
        field("workup", "water quench; filtration; Et2O wash three times; brine wash three times; Na2SO4 drying; evaporation", ev),
        field("purification", "flash chromatography on silica gel; petroleum ether/Et2O 5:1 to 1:1", ev),
    ], [field("isolated_yield", qty(61, "%"), ev, ["product"]), field("yield_measurement_basis", "isolated product mass after flash chromatography", ev)],
    unresolved=("No numerical reaction time is reported.", "Candidate structures remain machine-unverified.", "No SI file was explicitly associated."),
))

records.append(make_record(
    "page6_partial_procedure_allenol_3w", [6], "reported_experiment",
    [
        participant("substrate", "reactant", "3-butyl-2-methylpenta-3,4-dienol 3a", ev, amounts=[field("mass", qty(1.766, "g"), ev), field("amount", qty(11.5, "mmol"), ev)]),
        participant("dess_martin", "reagent", "Dess-Martin reagent", ev, amounts=[field("mass", qty(7.302, "g"), ev), field("amount", qty(17.2, "mmol"), ev)]),
        participant("solvent_substrate", "solvent", "CH2Cl2 (substrate solution)", ev, smiles=SMILES["CH2Cl2"], amounts=[field("volume", qty(10, "mL"), ev)]),
        participant("solvent_reagent", "solvent", "CH2Cl2 (Dess-Martin solution)", ev, smiles=SMILES["CH2Cl2"], amounts=[field("volume", qty(25, "mL"), ev)]),
        participant("product", "product", "5-butyl-4-methylocta-5,6-dien-3-ol 3w", ev),
    ], [
        field("temperature", "r.t.", ev), field("time", "until complete by TLC", ev),
        field("partial_workup", "quenched and washed with saturated aqueous Na2S2O3; subsequent procedure continues on page 7", ev),
    ], [field("reported_yield", None, ev, ["product"])],
    notes=("Only the portion printed on PDF page 6 was extracted; the procedure continues onto page 7 outside this session's claimed coverage.",),
    unresolved=("The oxidation/Grignard sequence, final isolation, purification, and yield continue beyond page 6 and are not covered here.", "Product connectivity remains machine-unverified."),
))


# Coverage ledger: direct page-local records only; cross-page evidence is still retained in records.
ids = lambda *suffixes: [f"{DOC}:{s}" for s in suffixes]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1 and adjacent introduction", "finding": "Cited prior carbopalladation/pi-allylpalladium pathway; classified as mechanism, not a new experiment.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "Scheme 2 and preceding paragraph", "finding": "Authors' earlier reported generic five-membered coupling-cyclization; classified as literature example.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "title, abstract, author and SI notice", "finding": "Article metadata and scope only; the SI availability notice was not treated as an attached SI file.", "evidence_ids": [f"{DOC}:page1:image"]},
            ],
            "record_ids": ids("page1_scheme1_prior_carbopalladation_mechanism", "page1_scheme2_prior_five_membered_cyclization"),
            "unresolved": ["Generic R-group structures and omitted numerical outcomes cannot be completed from this page."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 and preparation arrows", "finding": "Starting-material inventory plus one multistage general preparation scheme; rows contain substituent definitions, not row-specific outcomes.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Scheme 3", "finding": "Two reported cycloisomerization outcomes from substrates 3v and 3w; no numerical yields shown.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Scheme 4 and surrounding prose", "finding": "Table 2 entry 1 is repeated here and merged; lower comparison is cited prior literature with 66% combined yield and 4:96 product ratio.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "Figure 1", "finding": "X-ray structure of trans-5w; structural evidence only, not an additional experiment.", "evidence_ids": [f"{DOC}:page2:image"]},
            ],
            "record_ids": ids("page2_table1_general_starting_material_preparation", "page2_scheme3_3v_to_5v", "page2_scheme3_3w_to_trans_5w", "page2_scheme4_prior_unsubstituted_amino_allene", "table2_entry_1"),
            "unresolved": ["Scheme 3 lacks yields and detailed quantities/times.", "Table 1 does not provide row-specific experimental results."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Table 2 and footnotes", "finding": "Eight independent iodobenzene substrate-scope rows with isolated product yields; entry 1 merged with Scheme 4.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Scheme 5", "finding": "One reported 4j-to-9ja experiment and a separately classified proposed coupling-cyclization/Heck path.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Equation 1", "finding": "Reported 4i-to-trans-11ia experiment (48 h, 19%).", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "scope and failure prose", "finding": "Generic failures for 1-alkynyl halides and aryl chlorides preserved as partial negative records.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "Table 4 discussion", "finding": "Conditions-B result corresponds to Table 4 entry 15; evidence merged with that row and its prose-only de value retained.", "evidence_ids": [f"{DOC}:page3:image"]},
            ],
            "record_ids": ids(*( [f"table2_entry_{i}" for i in range(1,9)] + ["page3_scheme5_4j_to_9ja", "page3_scheme5_proposed_heck_path", "page3_equation1_4i_to_11ia", "page3_failed_1_alkynyl_halides", "page3_failed_aryl_chlorides", "table4_entry_15"] )),
            "unresolved": ["Failure statements do not identify exact substrates or detection limits.", "Some scope structures and stereochemistry remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Table 3 and footnotes", "finding": "Eighteen independent organic-halide scope rows extracted, including combined-yield/ratio rows and printed label/ratio anomalies.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "Table 4 and footnotes", "finding": "Twenty-one independent optimization rows extracted with base, solvent, temperature, time, product yields/de, and recovered 4k.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "right-column scope discussion", "finding": "Narrative context for Tables 5–6, Scheme 6, and Eq. 2; no extra duplicate records created.", "evidence_ids": [f"{DOC}:page4:image"]},
            ],
            "record_ids": ids(*( [f"table3_entry_{i}" for i in range(1,19)] + [f"table4_entry_{i}" for i in range(1,22)] )),
            "unresolved": ["Table 3 entry 8 prints 86:15; Table 3 reuses label 6j for two different halides.", "Table 4 prose/table de discrepancy and missing yield bases require review."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "Figures 2 and 3", "finding": "X-ray/NOE stereochemical evidence for 10ka/11ka; not additional experiments.", "evidence_ids": [f"{DOC}:page5:image"]},
                {"region": "Scheme 6", "finding": "Reported 4u beta-H-elimination product 12 and a separately classified proposed mechanism.", "evidence_ids": [f"{DOC}:page5:image"]},
                {"region": "Equation 2", "finding": "Reported cyclization of 13 to 14 (21%, de >99:1).", "evidence_ids": [f"{DOC}:page5:image"]},
                {"region": "Table 5 and footnotes", "finding": "Twenty-two displayed rows reviewed; entries 1 and 2 were merged with repeated Table 4 results, leaving twenty new row records.", "evidence_ids": [f"{DOC}:page5:image"]},
                {"region": "conclusion", "finding": "Summary only; no additional reaction records.", "evidence_ids": [f"{DOC}:page5:image"]},
            ],
            "record_ids": ids(*( ["table4_entry_15", "table4_entry_21"] + [f"table5_entry_{i}" for i in range(3,23)] + ["page5_scheme6_4u_to_12", "page5_scheme6_beta_h_elimination_mechanism", "page5_equation2_13_to_14"] )),
            "unresolved": ["Table 4/Table 5 report a 100 h versus shared 48 h duration conflict for the repeated conditions-B result.", "Table 5 entry 6 gives a three-isomer mixture without a de value."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "Table 6 and footnotes", "finding": "Sixteen independent organic-halide/condition rows extracted with product-specific yields and selectivities.", "evidence_ids": [f"{DOC}:page6:image"]},
                {"region": "Scheme 7", "finding": "Two reported experiments: 4q with 6q gives 10qq/11qq; 4q with 1,4-diiodobenzene gives double-cyclization product 15.", "evidence_ids": [f"{DOC}:page6:image"]},
                {"region": "general methods", "finding": "Global nitrogen/dry-solvent/anhydrous statement and analytical conventions inspected; not turned into a standalone reaction.", "evidence_ids": [f"{DOC}:page6:image"]},
                {"region": "Typical procedures I and II", "finding": "Exact preparations of allenoate 2c and allenol 3d extracted with quantities, conditions, workup/purification, and isolated yields.", "evidence_ids": [f"{DOC}:page6:image"]},
                {"region": "beginning of 3w procedure", "finding": "Partial Dess-Martin/Grignard-sequence record retained; the printed procedure continues on page 7 outside claimed coverage.", "evidence_ids": [f"{DOC}:page6:image"]},
            ],
            "record_ids": ids(*( [f"table6_entry_{i}" for i in range(1,17)] + ["page6_scheme7_4q_with_6q", "page6_scheme7_4q_with_6r", "page6_procedure1_ethyl_allenoate_2c", "page6_procedure2_allenol_3d", "page6_partial_procedure_allenol_3w"] )),
            "unresolved": ["Table 6 entry 13 prints 11lg rather than the expected lm label.", "Scheme 7 omits time and detailed procedures.", "The 3w procedure continues beyond page 6 and remains incomplete."],
        },
    ],
}


records_path = OUT / "pages_0001_0006_records.json"
coverage_path = RUN / "coverage" / "pages_0001_0006.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_path": str(records_path), "coverage_path": str(coverage_path)}, ensure_ascii=False))
