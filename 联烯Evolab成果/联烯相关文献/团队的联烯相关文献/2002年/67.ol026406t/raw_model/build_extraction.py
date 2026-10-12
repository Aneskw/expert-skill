#!/usr/bin/env python3
"""Build the evidence-linked raw extraction for PDF pages 1--4."""

import json
from pathlib import Path


DOC = "doc_cf66d76f4a06f108"
E = {
    page: [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    for page in range(1, 5)
}


def fact(value, evidence_ids=None):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids or []) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence_ids=None, targets=None):
    result = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, evidence_ids, *, label=None, name=None,
                smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids if label is not None else []),
        "name": fact(name, evidence_ids if name is not None else []),
        "smiles": fact(smiles, evidence_ids if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, source_reaction_id, kind, evidence_ids, participants,
           steps, outcomes, unresolved, notes=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_reaction_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence_ids)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, evs) for value, evs in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


SUBSTRATE_SMILES = {
    "1a": "C=C=C(CCCC)C(C)CNS(=O)(=O)c1ccc(C)cc1",
    "1b": "C=C=CC(C)CNS(=O)(=O)c1ccc(C)cc1",
    "1c": "C=C=C(CCCC)C(CCC)CNS(=O)(=O)c1ccc(C)cc1",
    "1d": "C=C=C(CCCC)CCNS(=O)(=O)c1ccc(C)cc1",
    "1e": "C=C=C(C(C)(C)C)CCNS(=O)(=O)c1ccc(C)cc1",
    "1f": "C=C=C(C(C)(C)C)C(C)CNS(=O)(=O)c1ccc(C)cc1",
    "1a-Ns": "C=C=C(CCCC)C(C)CNS(=O)(=O)c1ccc([N+](=O)[O-])cc1",
    "1a-Bz": "C=C=C(CCCC)C(C)CNC(=O)c1ccccc1",
}

HALIDES = {
    "PhI": ("iodobenzene", "Ic1ccccc1"),
    "p-MeOC6H4I": ("1-iodo-4-methoxybenzene", "COc1ccc(I)cc1"),
    "p-MeO2CC6H4I": ("methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1"),
    "p-BrC6H4I": ("1-bromo-4-iodobenzene", "Brc1ccc(I)cc1"),
    "o-MeC6H4I": ("2-iodotoluene", "Cc1ccccc1I"),
    "p-MeC6H4I": ("4-iodotoluene", "Cc1ccc(I)cc1"),
    "1-iodonaphthalene": ("1-iodonaphthalene", "Ic1cccc2ccccc12"),
    "2-iodothiophene": ("2-iodothiophene", "Ic1cccs1"),
    "2-bromopyridine": ("2-bromopyridine", "Brc1ccccn1"),
    "(E)-1-iodohex-1-ene": ("(E)-1-iodohex-1-ene", "CCCC/C=C/I"),
}


def common_participants(substrate, partner, row_evidence, condition_evidence,
                        *, full_scale):
    partner_name, partner_smiles = HALIDES[partner]
    substrate_amounts = []
    partner_amounts = [field("equivalents", {"number": 1.5, "unit": "equiv"}, row_evidence)]
    base_amounts = [field("equivalents", {"number": 4, "unit": "equiv"}, condition_evidence)]
    solvent_amounts = []
    if full_scale:
        substrate_amounts.append(field("reaction_scale", {"number": 0.3, "unit": "mmol"}, condition_evidence))
        partner_amounts.append(field("amount", {"number": 0.45, "unit": "mmol"}, condition_evidence))
        base_amounts.append(field("amount", {"number": 1.2, "unit": "mmol"}, condition_evidence))
        solvent_amounts.append(field("volume", {"number": 2, "unit": "mL"}, condition_evidence))
    return [
        participant(
            f"substrate_{substrate}", "reactant", row_evidence,
            label=substrate, name=f"beta-amino allene {substrate}",
            smiles=SUBSTRATE_SMILES[substrate], amounts=substrate_amounts,
        ),
        participant(
            "organic_halide", "reactant", row_evidence,
            label=partner, name=partner_name, smiles=partner_smiles,
            amounts=partner_amounts,
        ),
        participant(
            "potassium_carbonate", "reagent", condition_evidence,
            label="K2CO3", name="potassium carbonate",
            smiles="[K+].[K+].[O-]C([O-])=O", amounts=base_amounts,
        ),
        participant(
            "palladium_catalyst", "catalyst", condition_evidence,
            label="Pd(PPh3)4", name="tetrakis(triphenylphosphine)palladium(0)",
            amounts=[field("catalyst_loading", {"number": 5, "unit": "mol%"}, condition_evidence)],
        ),
        participant(
            "dmf", "solvent", condition_evidence,
            label="DMF", name="N,N-dimethylformamide", smiles="CN(C)C=O",
            amounts=solvent_amounts,
        ),
    ]


def experimental_step(participants, time_h, row_evidence, condition_evidence,
                      *, temperature=True, solvent="DMF"):
    conditions = []
    if time_h is None:
        conditions.append(field("reaction_time", None))
    elif isinstance(time_h, dict):
        conditions.append(field("reaction_time", time_h, row_evidence))
    else:
        conditions.append(field("reaction_time", {"number": time_h, "unit": "h"}, row_evidence))
    if temperature:
        conditions.append(field("reaction_temperature", {"number": 70, "unit": "°C"}, condition_evidence))
    else:
        conditions.append(field("reaction_temperature", None))
    if solvent is not None:
        conditions.append(field("solvent", solvent, condition_evidence))
    return [{
        "step_id": "coupling_cyclization",
        "participant_ids": [p["entity_id"] for p in participants],
        "conditions": conditions,
    }]


records = []

# Page 1: summary arrow and mechanistic/prior-work Scheme 1 are classified,
# not treated as individual reported experiments.
general_participants = [
    participant("generic_amino_allene", "reactant", E[1], label="generic beta-amino allene"),
    participant("generic_organic_halide", "reactant", E[1], label="R4X", amounts=[
        field("equivalents", {"number": 1.5, "unit": "equiv"}, E[1])
    ]),
    participant("palladium_catalyst", "catalyst", E[1], label="Pd(PPh3)4", amounts=[
        field("catalyst_loading", {"number": 5, "unit": "mol%"}, E[1])
    ]),
    participant("potassium_carbonate", "reagent", E[1], label="K2CO3", amounts=[
        field("equivalents", {"number": 4, "unit": "equiv"}, E[1])
    ]),
    participant("dmf", "solvent", E[1], label="DMF", name="N,N-dimethylformamide", smiles="CN(C)C=O"),
    participant("generic_five_membered_product", "product", E[1], label="generic five-membered N-heterocycle"),
]
records.append(record(
    "page1_abstract_general_scheme", "Abstract graphical summary", "general_scheme", E[1],
    general_participants,
    [{"step_id": "summary_coupling_cyclization",
      "participant_ids": [p["entity_id"] for p in general_participants],
      "conditions": [field("reaction_temperature", {"number": 70, "unit": "°C"}, E[1]),
                     field("solvent", "DMF", E[1])]}],
    [],
    ["Graphical abstract is a generic R-group summary, not an individual experiment.",
     "Generic structures are not expanded to SMILES; time and yield are not reported in this region."],
))

mechanism_participants = [
    participant("generic_amino_allene", "reactant", E[1], label="generic beta-amino allene"),
    participant("organopalladium_partner", "unspecified_agent", E[1], label="R4PdX"),
    participant("pi_allyl_palladium_intermediate", "unspecified_agent", E[1], label="pi-allyl palladium intermediate"),
    participant("path_a_product", "product", E[1], label="four-membered N-heterocycle (path a)"),
    participant("path_b_product", "product", E[1], label="six-membered N-heterocycle (path b)"),
]
records.append(record(
    "page1_scheme1_mechanism", "Scheme 1", "mechanism", E[1], mechanism_participants,
    [
        {"step_id": "carbopalladation", "participant_ids": ["generic_amino_allene", "organopalladium_partner", "pi_allyl_palladium_intermediate"], "conditions": []},
        {"step_id": "intramolecular_nucleophilic_attack_paths", "participant_ids": ["pi_allyl_palladium_intermediate", "path_a_product", "path_b_product"], "conditions": []},
    ],
    [],
    ["Scheme 1 is a generic mechanistic/prior-work schematic with R groups, not a current-paper experiment.",
     "No quantitative conditions or outcome are assigned."],
))


def add_scheme2_record(suffix, substrate, time_h, products, yield_pct, ratio=None,
                       other_isomers=False):
    ps = common_participants(substrate, "PhI", E[2], E[2], full_scale=False)
    product_ids = []
    for entity_id, label, name in products:
        ps.append(participant(entity_id, "product", E[2], label=label, name=name))
        product_ids.append(entity_id)
    outcomes = [field("yield", {"number": yield_pct, "unit": "%"}, E[2], product_ids)]
    if ratio:
        outcomes.append(field("product_ratio", ratio, E[2], product_ids))
    if other_isomers:
        ps.append(participant("other_isomers", "product", E[2], label="other isomers, if any"))
        outcomes.append(field(
            "other_isomers_percentage",
            {"number": 3, "unit": "%", "qualifier": "lt", "raw_text": "less than 3%"},
            E[2], ["other_isomers"],
        ))
    outcomes.append(field("yield_measurement_basis", None))
    records.append(record(
        suffix, "Scheme 2", "reported_experiment", E[2], ps,
        experimental_step(ps, time_h, E[2], E[2]), outcomes,
        ["Supporting information was not supplied or explicitly associated.",
         "Yield measurement basis, atmosphere, workup, and purification are not stated on the inspected page.",
         "Product SMILES require independent structure curation from the drawings."],
    ))


add_scheme2_record(
    "scheme2_1a_phi_7p5h", "1a", 7.5,
    [("product_2a", "2a", "five-membered 2,3-dihydropyrrole product 2a")], 78,
    other_isomers=True,
)
for suffix, time_h, ratio, yield_pct in [
    ("scheme2_1b_phi_40min", {"number": 40, "unit": "min"}, "75:25", 71),
    ("scheme2_1b_phi_4h", 4, "23:77", 63),
    ("scheme2_1b_phi_16h", 16, "4:96", 66),
]:
    add_scheme2_record(
        suffix, "1b", time_h,
        [("product_3b", "trans-3b", "four-membered product trans-3b"),
         ("product_4b", "4b", "six-membered product 4b")],
        yield_pct, ratio=ratio,
    )


TABLE1 = [
    (1, "1a", "p-MeOC6H4I", 5.5, 79, "2b"),
    (2, "1a", "p-MeO2CC6H4I", 24, 73, "2c"),
    (3, "1a", "p-BrC6H4I", 10, 82, "2d"),
    (4, "1a", "o-MeC6H4I", 10, 84, "2e"),
    (5, "1a", "p-MeC6H4I", 8, 83, "2f"),
    (6, "1a", "1-iodonaphthalene", 12, 80, "2g"),
    (7, "1a", "2-iodothiophene", 36, 68, "2h"),
    (8, "1a", "2-bromopyridine", 12, 68, "2i"),
    (9, "1c", "PhI", 24, 74, "2j"),
]
for entry, substrate, halide, time_h, yield_pct, product_label in TABLE1:
    ps = common_participants(substrate, halide, E[2], E[2], full_scale=True)
    ps.append(participant(
        f"product_{product_label}", "product", E[2], label=product_label,
        name=f"corresponding 2,3-dihydropyrrole product {product_label}",
    ))
    notes = []
    if entry == 3:
        notes.append(("Only the carbon-iodine bond was cleaved; the carbon-bromine bond remained intact.", E[2]))
    records.append(record(
        f"table1_entry{entry}_{product_label}", f"Table 1 entry {entry}", "substrate_scope_entry", E[2], ps,
        experimental_step(ps, time_h, E[2], E[2]),
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, E[2], [f"product_{product_label}"]),
         field("yield_measurement_basis", "isolated yield based on beta-amino allene 1", E[2], [f"product_{product_label}"])],
        ["Supporting information was not supplied or explicitly associated.",
         "Atmosphere, workup, purification, and product SMILES are not established from the inspected pages."],
        notes=notes,
    ))


TABLE2 = [
    (1, "1d", "PhI", 8, 65, [("2k_prime", "2k′", "five-membered exocyclic-alkene product 2k′"), ("2k", "2k", "2,3-dihydropyrrole product 2k")], "15:85", "determined by isolation"),
    (2, "1d", "p-MeOC6H4I", 5.5, 68, [("2l_prime", "2l′", "five-membered exocyclic-alkene product 2l′"), ("2l", "2l", "2,3-dihydropyrrole product 2l")], "14:86", "determined by 1H NMR spectra (300 MHz)"),
    (3, "1d", "p-MeO2CC6H4I", 10, 77, [("2m_prime", "2m′", "five-membered exocyclic-alkene product 2m′"), ("2m", "2m", "2,3-dihydropyrrole product 2m")], "15:85", "determined by 1H NMR spectra (300 MHz)"),
    (4, "1e", "PhI", 48, 65, [("2n", "2n", "2,3-dihydropyrrole product 2n")], None, None),
    (5, "1e", "p-MeOC6H4I", 60, 77, [("2o", "2o", "2,3-dihydropyrrole product 2o")], None, None),
    (6, "1e", "p-MeO2CC6H4I", 96, 45, [("2p", "2p", "2,3-dihydropyrrole product 2p")], None, None),
    (7, "1f", "PhI", 16, 76, [("2q", "2q", "2,3-dihydropyrrole product 2q")], None, None),
    (8, "1f", "(E)-1-iodohex-1-ene", 11, 62, [("2r", "2r", "2,3-dihydropyrrole product 2r")], None, None),
]
table2_condition_evidence = E[3] + E[2]
for entry, substrate, halide, time_h, yield_pct, products, ratio, ratio_basis in TABLE2:
    ps = common_participants(substrate, halide, E[3], table2_condition_evidence, full_scale=True)
    product_ids = []
    for short_id, label, name in products:
        entity_id = f"product_{short_id}"
        product_ids.append(entity_id)
        ps.append(participant(entity_id, "product", E[3], label=label, name=name))
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, E[3], product_ids),
        field("yield_measurement_basis", "isolated yield based on beta-amino allene 1", E[3], product_ids),
    ]
    if ratio:
        outcomes.extend([
            field("product_ratio", ratio, E[3], product_ids),
            field("ratio_measurement_basis", ratio_basis, E[3], product_ids),
        ])
    else:
        outcomes.append(field("regioselectivity", "2,3-dihydropyrrole product reported as the only product", E[3], product_ids))
    if entry == 6:
        outcomes.append(field(
            "recovered_starting_material_yield", {"number": 28, "unit": "%"},
            E[3], ["substrate_1e"],
        ))
    records.append(record(
        f"table2_entry{entry}_{products[-1][1]}", f"Table 2 entry {entry}", "substrate_scope_entry",
        E[3] + E[2], ps,
        experimental_step(ps, time_h, E[3], table2_condition_evidence), outcomes,
        ["Supporting information was not supplied or explicitly associated.",
         "Atmosphere, workup, purification, and product SMILES are not established from the inspected pages."],
    ))


# Page 3 prose reports three solvent substitutions only qualitatively. Keep
# them as separate partial experiments without importing the Table 2 numeric
# time/yield/ratio into these unquantified variants.
SOLVENTS = [
    ("toluene", "toluene", "Cc1ccccc1"),
    ("1,4-dioxane", "1,4-dioxane", "O1CCOCC1"),
    ("acetonitrile", "CH3CN", "CC#N"),
]
for suffix, label, smiles in SOLVENTS:
    ps = [
        participant("substrate_1d", "reactant", E[3], label="1d", name="beta-amino allene 1d", smiles=SUBSTRATE_SMILES["1d"]),
        participant("organic_halide", "reactant", E[3], label="PhI", name="iodobenzene", smiles=HALIDES["PhI"][1]),
        participant("reaction_solvent", "solvent", E[3], label=label, name=suffix, smiles=smiles),
        participant("product_2k_prime", "product", E[3], label="2k′", name="five-membered exocyclic-alkene product 2k′"),
        participant("product_2k", "product", E[3], label="2k", name="2,3-dihydropyrrole product 2k"),
    ]
    records.append(record(
        f"prose_solvent_variant_{suffix.replace(',', '').replace('-', '_')}",
        f"Prose solvent variant: {label}", "reported_experiment", E[3], ps,
        experimental_step(ps, None, E[3], E[3], temperature=False, solvent=label),
        [field("reported_outcome", "similar results were obtained", E[3], ["product_2k_prime", "product_2k"]),
         field("yield", None, targets=["product_2k_prime", "product_2k"]),
         field("product_ratio", None, targets=["product_2k_prime", "product_2k"])],
        ["The exact time, temperature, yield, and product ratio are not reported for this solvent variant.",
         "The immediate antecedent links 'similar results' to the 1d/PhI product pair, but exact equivalence to Table 2 entry 1 must be reviewed.",
         "Catalyst/base quantities, atmosphere, workup, purification, and product SMILES are not stated for this variant.",
         "Supporting information was not supplied or explicitly associated."],
    ))


def add_scheme3_record(substrate, product_id, product_label, product_name, time_h,
                       yield_pct, only_product=False):
    ps = common_participants(substrate, "PhI", E[3], E[3] + E[2], full_scale=False)
    ps.append(participant(product_id, "product", E[3], label=product_label, name=product_name))
    outcomes = [
        field("yield", {"number": yield_pct, "unit": "%"}, E[3], [product_id]),
        field("yield_measurement_basis", None),
    ]
    if only_product:
        outcomes.append(field("selectivity", "reported as the only product", E[3], [product_id]))
    records.append(record(
        f"scheme3_{substrate}_phi", f"Scheme 3: {substrate}", "reported_experiment", E[3] + E[2], ps,
        experimental_step(ps, time_h, E[3], E[3] + E[2]), outcomes,
        ["Supporting information was not supplied or explicitly associated.",
         "Yield measurement basis, atmosphere, workup, purification, and product SMILES are not stated on the inspected pages."],
    ))


add_scheme3_record("1a-Ns", "product_2a_ns", "2a-Ns", "five-membered product 2a-Ns", 5, 55)
add_scheme3_record("1a-Bz", "product_3a_bz", "3a-Bz", "four-membered azetidine product 3a-Bz", 48, 19, only_product=True)


# Footnote 12 describes an experiment repeated by the authors, distinct from
# Scheme 2 substrate 1b. Exact operating conditions and yield are absent.
footnote_ps = [
    participant("simple_pentadienyl_sulfonamide", "reactant", E[3], label="simple N-(3,4-pentadienyl)sulfonamide"),
    participant("iodobenzene", "reactant", E[3], label="PhI", name="iodobenzene", smiles=HALIDES["PhI"][1]),
    participant("palladium_zero_catalyst", "catalyst", E[3], label="Pd(0) catalyst"),
    participant("four_membered_product", "product", E[3], label="four-membered product"),
    participant("six_membered_product", "product", E[3], label="six-membered product"),
]
records.append(record(
    "footnote12_repeated_pentadienyl_sulfonamide_phi", "Footnote 12", "reported_experiment", E[3],
    footnote_ps,
    [{"step_id": "palladium_catalyzed_coupling_cyclization",
      "participant_ids": [p["entity_id"] for p in footnote_ps],
      "conditions": [field("reaction_time", None), field("reaction_temperature", None)]}],
    [field("product_ratio", "79:21", E[3], ["four_membered_product", "six_membered_product"]),
     field("yield", None, targets=["four_membered_product", "six_membered_product"])],
    ["The footnote reports that the authors repeated this prior-literature reaction; it is retained as a current-paper reported experiment, not merged with Scheme 2 substrate 1b.",
     "Exact N-sulfonyl substituent, catalyst identity/loading, solvent, temperature, time, yield, atmosphere, workup, and purification are not stated in the footnote.",
     "Supporting information was not supplied or explicitly associated."],
))


output = Path(__file__).with_name("records.pages_0001_0004.json")
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(output), "records": len(records)}, ensure_ascii=False))
