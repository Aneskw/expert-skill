#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_384261d36d616986, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_384261d36d616986"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


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


def fld(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
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


def rec(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
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
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record requires source review; structures are not source-verified.",
                "Supporting Information was not explicitly supplied or associated.",
            ],
        },
    }


records = []

# Page 2 schemes and the page-1 graphical abstract are contextual records, not batch experiments.
e12 = ev(1) + ev(2)
records.append(rec(
    "current_hydration_general_scheme", "general_scheme", e12,
    [
        participant("generic_allenyl_sulfoxide_1", "reactant", "1 (generic 1,2-allenylic sulfoxide)", ev(2)),
        participant("acetic_acid", "solvent", "HOAc", ev(2), "acetic acid", "CC(=O)O"),
        participant("generic_z_alkenol_3", "product", "3 (generic 3-sulfinyl-2(Z)-alkenol)", ev(2)),
    ],
    [{"step_id": "generic_hydration", "participant_ids": ["generic_allenyl_sulfoxide_1", "acetic_acid"],
      "conditions": [fld("temperature", qty(100, "°C"), ev(2))]}],
    [],
    notes=["The lower arrow of Scheme 2 is a generic current-work hydration shown at 100 °C; optimized row-specific experiments are recorded separately."],
    unresolved=["Generic R groups prevent a fully specified structure.", "No scale, time, or yield is stated on this generic arrow."]
))
records.append(rec(
    "scheme1_prior_halohydroxylation_selenohydroxylation", "literature_example", ev(2),
    [
        participant("prior_allenyl_sulfoxide", "reactant", "generic 1,2-allenylic sulfoxide", ev(2)),
        participant("electrophile_e_plus", "reagent", "E+ (E = I, Br, Cl, PhSe)", ev(2)),
        participant("water", "reagent", "H2O", ev(2), "water", "O"),
        participant("prior_addition_product", "product", "generic halohydroxylation/selenohydroxylation product", ev(2)),
    ],
    [{"step_id": "cited_addition", "participant_ids": ["prior_allenyl_sulfoxide", "electrophile_e_plus", "water"],
      "conditions": [fld("temperature", "r.t.", ev(2)), fld("solvent", "unspecified solvent", ev(2))]}],
    [], notes=["Scheme 1 summarizes cited prior work (references 5a-d), not a new experiment in this paper."],
    unresolved=["Generic R groups and electrophile alternatives are not individual batch experiments."]
))
records.append(rec(
    "scheme2_prior_oxidative_hydroacetoxylation", "literature_example", ev(2),
    [
        participant("prior_sulfoxide_1", "reactant", "1 (generic 1,2-allenylic sulfoxide)", ev(2)),
        participant("hydrogen_peroxide", "reagent", "H2O2", ev(2), "hydrogen peroxide", "OO"),
        participant("prior_hoac", "solvent", "HOAc", ev(2), "acetic acid", "CC(=O)O"),
        participant("prior_acetate_2", "product", "2 (3-sulfonyl-2(Z)-alkenyl acetate)", ev(2)),
    ],
    [{"step_id": "cited_oxidative_hydroacetoxylation", "participant_ids": ["prior_sulfoxide_1", "hydrogen_peroxide", "prior_hoac"],
      "conditions": [fld("temperature", qty(100, "°C"), ev(2)), fld("time", qty(17, "h"), ev(2))]}],
    [], notes=["The upper arrow of Scheme 2 is the authors' 2009 cited work (reference 6), not a new batch in this paper."],
    unresolved=["Generic R groups and absent scale/yield prevent a batch-level reconstruction."]
))

# Table 1 optimization. Entry 1 is the same optimized 1a -> Z-3a batch shown in Table 2 entry 1 and the page-5 typical procedure.
table1 = [
    (1, "HOAc", 0.1, 60, 24, 85, None),
    (2, "TFA", 0.1, 60, 24, 46, None),
    (3, "HOAc-H2O = 1:1", 0.1, 60, 24, 7, None),
    (4, "CH3CN", 0.1, 60, 24, 53, None),
    (5, "CH3NO2", 0.1, 60, 24, 57, None),
    (6, "DMSO", 0.1, 60, 24, None, 96),
    (7, "HOAc", 0.1, 40, 24, 66, None),
    (8, "HOAc", 0.1, 80, 24, 41, None),
    (9, "HOAc", 0.1, 60, 12, 77, None),
    (10, "HOAc", 0.05, 60, 24, 86, None),
    (11, "HOAc", 0.2, 60, 24, 82, None),
]

for entry, solvent, concentration, temp, hours, nmr_yield, recovery in table1:
    evidence = ev(3)
    if entry == 1:
        evidence += ev(5)
    sid = "table1_entry1_table2_entry1_z3a" if entry == 1 else f"table1_entry{entry}"
    parts = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    "3,3-pentamethylenepropadienyl phenyl sulfoxide",
                    "O=S(c1ccccc1)C=C=C1CCCCC1",
                    [fld("amount", qty(0.3, "mmol"), evidence)]),
    ]
    solvent_id = "reaction_solvent"
    parts.append(participant(solvent_id, "solvent", solvent, evidence,
                             {"HOAc": "acetic acid", "TFA": "trifluoroacetic acid", "CH3CN": "acetonitrile",
                              "CH3NO2": "nitromethane", "DMSO": "dimethyl sulfoxide"}.get(solvent),
                             {"HOAc": "CC(=O)O", "TFA": "O=C(O)C(F)(F)F", "CH3CN": "CC#N",
                              "CH3NO2": "C[N+](=O)[O-]", "DMSO": "CS(C)=O"}.get(solvent),
                             [fld("volume", qty(3.0, "mL"), evidence)]))
    if entry in (4, 5, 6):
        parts.append(participant("added_hoac", "reagent", "HOAc", evidence, "acetic acid", "CC(=O)O",
                                 [fld("equivalents", qty(1, "equiv"), evidence)]))
    product_ids = []
    if entry != 6:
        product_ids = ["product_z3a"]
        parts.append(participant("product_z3a", "product", "Z-3a", evidence,
                                 "1-[(Z)-2-(phenylsulfinylethenyl)]-1-cyclohexanol",
                                 "O=S(c1ccccc1)/C=C\\C1(O)CCCCC1"))
    conds = [fld("temperature", qty(temp, "°C"), evidence), fld("time", qty(hours, "h"), evidence),
             fld("concentration", qty(concentration, "M"), evidence)]
    if entry == 1:
        conds.append(fld("operation", "stirred vigorously and monitored by TLC", ev(5)))
    outcomes = []
    if nmr_yield is not None:
        outcomes.append(fld("nmr_yield", qty(nmr_yield, "%"), evidence, product_ids))
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", qty(recovery, "%"), evidence, ["substrate_1a"]))
    if entry == 1:
        outcomes += [
            fld("isolated_yield", qty(87, "%"), evidence, product_ids),
            fld("product_mass", qty(64.9, "mg"), ev(5), product_ids),
        ]
    steps = [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts if p["role"] != "product"], "conditions": conds}]
    if entry == 1:
        parts += [
            participant("sat_naHCO3", "reagent", "saturated aqueous NaHCO3", ev(5), "sodium bicarbonate", "O=C([O-])O.[Na+]",
                        [fld("volume", qty(10, "mL"), ev(5))]),
            participant("diethyl_ether", "solvent", "diethyl ether", ev(5), "diethyl ether", "CCOCC",
                        [fld("volume_per_extraction", qty(15, "mL"), ev(5))]),
            participant("sodium_sulfate", "reagent", "anhydrous Na2SO4", ev(5), "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
        ]
        steps.append({"step_id": "workup_and_purification", "participant_ids": ["sat_naHCO3", "diethyl_ether", "sodium_sulfate", "product_z3a"],
                      "conditions": [fld("workup", "quenched with saturated aqueous NaHCO3; extracted with diethyl ether three times; washed with saturated aqueous NaHCO3; dried over anhydrous Na2SO4; filtered and evaporated", ev(5)),
                                     fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate = 1:1", ev(5))]})
    records.append(rec(sid, "optimization_entry", evidence, parts, steps, outcomes,
                       notes=["Table 1 optimization row." if entry != 1 else "This record reconciles Table 1 entry 1, Table 2 entry 1, and the Z-3a typical procedure as one experiment."],
                       unresolved=["Supporting Information was not explicitly associated; structure candidates remain unverified."] +
                                  (["No product yield is reported; only recovery of 1a is explicit."] if entry == 6 else [])))

# Table 2 scope entries 2-18; row 1 was reconciled above.
scope = {
    2: ("1b", "Ph/H/-(CH2)4-", "Z-3b", 53, None, 60, 24, 0.30, 3.0),
    3: ("1c", "Ph/H/n-C6H13/H", "Z-3c", 65, "1.66:1 (isolated-yield basis)", 60, 24, 0.30, 3.0),
    4: ("1d", "Ph/H/n-C5H11/H", "Z-3d", 66, "1.21:1 (isolated-yield basis)", 60, 24, 0.30, 3.0),
    5: ("1e", "p-BrC6H4/H/n-C5H11/H", "Z-3e", 74, "2.06:1 (isolated-yield basis)", 60, 24, 0.29, 3.0),
    6: ("1f", "p-O2NC6H4/H/n-C5H11/H", "Z-3f", 70, "2.13:1 (isolated-yield basis)", 60, 24, 0.32, 3.0),
    7: ("1g", "Ph/n-C4H9/CH3/CH3", "Z-3g", 87, None, "r.t.", 24, 0.20, 2.0),
    8: ("1h", "Ph/Ph/C2H5/C2H5", "Z-3h", 81, None, "r.t.", 24, 0.30, 3.0),
    9: ("1i", "p-BrC6H4/H/Me/H", "Z-3i", 76, "1.94:1 (1H NMR basis)", 60, 24, 0.30, 3.0),
    10: ("1j", "Ph/n-C4H9/H/H", "Z-3j", 58, None, 60, 24, 0.30, 3.0),
    11: ("1k", "Ph/Ph/H/H", "Z-3k", 51, None, 60, 24, 0.30, 3.0),
    12: ("1l", "Ph/allyl/H/H", "Z-3l", 64, None, 60, 24, 0.30, 3.0),
    13: ("1m", "Ph/H/CH3/CH3", "Z-3m", 58, None, 60, 24, 0.30, 3.0),
    14: ("1n", "Ph/H/C2H5/C2H5", "Z-3n", 76, None, 60, 24, 0.30, 3.0),
    15: ("1o", "Ph/H/C3H7/C3H7", "Z-3o", 71, None, 60, 24, 0.30, 3.0),
    16: ("1p", "Ph/H/C4H9/C4H9", "Z-3p", 69, None, 60, 24, 0.30, 3.0),
    17: ("1q", "Ph/H/Ph/Me", "Z-3q", 48, "1.43:1 (isolated-yield basis)", 60, 24, 0.30, 3.0),
    18: ("1r", "p-BrC6H4/Et/Me/H", "Z-3r", 68, "1.62:1 (isolated-yield basis)", 60, 24, 0.30, 3.0),
}

names = {
    2: "1-[(Z)-2-(phenylsulfinylethenyl)]-1-cyclopentanol",
    3: "1-(phenylsulfinyl)non-1(Z)-en-3-ol",
    4: "1-(phenylsulfinyl)oct-1(Z)-en-3-ol",
    5: "1-(p-bromophenylsulfinyl)oct-1(Z)-en-3-ol",
    6: "1-(p-nitrophenylsulfinyl)oct-1(Z)-en-3-ol",
    7: "2-methyl-4-(phenylsulfinyl)oct-3(Z)-en-2-ol",
    8: "3-ethyl-1-phenyl-1-(phenylsulfinyl)pent-1(Z)-en-3-ol",
    9: "4-(p-bromophenylsulfinyl)but-3(Z)-en-2-ol",
    10: "3-(phenylsulfinyl)hept-2(Z)-en-1-ol",
}
smiles = {
    2: "O=S(c1ccccc1)/C=C\\C1(O)CCCC1",
    3: "O=S(c1ccccc1)/C=C\\C(O)CCCCCC",
    4: "O=S(c1ccccc1)/C=C\\C(O)CCCCC",
    5: "O=S(c1ccc(Br)cc1)/C=C\\C(O)CCCCC",
    6: "O=S(c1ccc([N+](=O)[O-])cc1)/C=C\\C(O)CCCCC",
    7: "CCCC/C(=C\\C(O)(C)C)S(=O)c1ccccc1",
    8: "O=S(c1ccccc1)/C(c1ccccc1)=C\\C(O)(CC)CC",
    9: "CC(O)/C=C\\S(=O)c1ccc(Br)cc1",
    10: "CCCC/C(=C\\CO)S(=O)c1ccccc1",
}
substrate_smiles = {
    4: "O=S(c1ccccc1)C=C=CCCCCC",
    5: "O=S(c1ccc(Br)cc1)C=C=CCCCCC",
    6: "O=S(c1ccc([N+](=O)[O-])cc1)C=C=CCCCCC",
    8: "O=S(c1ccccc1)C(c1ccccc1)=C=C(CC)CC",
}
product_masses = {
    2: [("product", 37.4)],
    3: [("less_polar", 19.3), ("more_polar", 32.1)],
    4: [("less_polar", 22.8), ("more_polar", 27.5)],
    5: [("less_polar", 23.5), ("more_polar", 48.4)],
    6: [("less_polar", 20.8), ("more_polar", 44.4)],
    7: [("product", 46.2)],
    8: [("product", 76.4)],
    9: [("product", 62.7)],
    10: [("product", 41.7)],
}
purification = {
    2: "petroleum ether/ethyl acetate = 2:1",
    3: "petroleum ether/ethyl acetate = 2:1",
    4: "petroleum ether/ethyl acetate = 1:1",
    5: "petroleum ether/ethyl acetate = 1:2",
    6: "petroleum ether/ethyl acetate = 1:2",
    7: "petroleum ether/ethyl acetate = 2:1",
    8: "petroleum ether/ethyl acetate = 4:1",
    9: "petroleum ether/ethyl acetate = 1:1",
    10: "petroleum ether/ethyl acetate = 2:1 (printed as 2/:1)",
}

for entry, (substrate, rvals, product, yield_pct, dr, temp, hours, mmol, ml) in scope.items():
    pages = [3]
    if entry in (2, 3, 4):
        pages.append(5)
    if 4 <= entry <= 10:
        pages.append(6)
    if entry <= 10 and 5 not in pages:
        pages.append(5)  # shared Z-3a typical workup explicitly invoked for following compounds
    evidence = sum((ev(p) for p in pages), [])
    product_specs = product_masses.get(entry, [("product", None)])
    product_ids = []
    parts = [participant("substrate", "reactant", substrate, evidence,
                         f"1,2-allenylic sulfoxide {substrate}; R1/R2/R3/R4 = {rvals}",
                         substrate_smiles.get(entry), [fld("amount", qty(mmol, "mmol"), evidence)])]
    for tag, _mass in product_specs:
        pid = "product" if tag == "product" else f"product_{tag}"
        product_ids.append(pid)
        suffix_name = "" if tag == "product" else f" ({tag.replace('_', ' ')} diastereomer)"
        parts.append(participant(pid, "product", product if tag == "product" else f"{product}, {tag.replace('_', ' ')} isomer",
                                 evidence, (names.get(entry) + suffix_name) if names.get(entry) else None,
                                 smiles.get(entry)))
    parts.append(participant("hoac", "solvent", "HOAc", evidence, "acetic acid", "CC(=O)O",
                             [fld("volume", qty(ml, "mL"), evidence)]))
    if entry <= 10:
        parts += [
            participant("workup_bicarbonate", "reagent", "saturated aqueous NaHCO3", ev(5), "sodium bicarbonate", "O=C([O-])O.[Na+]"),
            participant("workup_ether", "solvent", "diethyl ether", ev(5), "diethyl ether", "CCOCC"),
            participant("drying_sodium_sulfate", "reagent", "anhydrous Na2SO4", ev(5), "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
        ]
    tvalue = temp if isinstance(temp, str) else qty(temp, "°C")
    steps = [{"step_id": "hydration", "participant_ids": ["substrate", "hoac"],
              "conditions": [fld("temperature", tvalue, evidence), fld("time", qty(hours, "h"), evidence)]}]
    if entry in purification:
        steps.append({"step_id": "isolation", "participant_ids": ["workup_bicarbonate", "workup_ether", "drying_sodium_sulfate"] + product_ids,
                      "conditions": [fld("workup", "quenched/washed with saturated aqueous NaHCO3, extracted with diethyl ether, dried over anhydrous Na2SO4, filtered and evaporated according to the Z-3a typical procedure", ev(5)),
                                     fld("purification", "silica-gel chromatography, " + purification[entry], evidence)]})
    outcomes = [fld("isolated_yield", qty(yield_pct, "%"), evidence, product_ids)]
    if dr:
        outcomes.append(fld("diastereomer_ratio", dr, evidence, product_ids))
    for (tag, mass_value), pid in zip(product_specs, product_ids):
        if mass_value is not None:
            outcomes.append(fld(f"{tag}_product_mass", qty(mass_value, "mg"), evidence, [pid]))
    unresolved = ["Supporting Information was not explicitly associated; structure candidates remain unverified."]
    if entry >= 11:
        unresolved.append("Only the table row is within pages 1-6; exact batch workup, product mass, and characterization are not stated in the covered pages.")
    if entry == 10:
        unresolved.append("The characterization paragraph continues onto page 7; only the batch facts visible on page 6 were used.")
    records.append(rec(f"table2_entry{entry}_{product.lower()}", "substrate_scope_entry", evidence,
                       parts, steps, outcomes, notes=[f"Table 2 entry {entry}; R1/R2/R3/R4 = {rvals}."], unresolved=unresolved))

# Isotopic labeling experiment, equation 1.
records.append(rec(
    "eq1_deuterium_labeling_z3h_d", "reported_experiment", ev(3),
    [
        participant("substrate_1h", "reactant", "1h", ev(3), "1-phenyl-3-ethyl-1,2-pentadienyl phenyl sulfoxide",
                    "O=S(c1ccccc1)C(c1ccccc1)=C=C(CC)CC"),
        participant("doac", "solvent", "DOAc", ev(3), "deuterated acetic acid", "[2H]OC(C)=O"),
        participant("d2o", "reagent", "D2O", ev(3), "deuterium oxide", "[2H]O[2H]",
                    [fld("equivalents", qty(1, "equiv"), ev(3))]),
        participant("product_z3h_d", "product", "d-(Z)-3h", ev(3), "2-deuterium-3-ethyl-1-phenyl-1-(phenylsulfinyl)pent-1(Z)-en-3-ol"),
    ],
    [{"step_id": "deuterium_labeling", "participant_ids": ["substrate_1h", "doac", "d2o"],
      "conditions": [fld("temperature", qty(60, "°C"), ev(3)), fld("time", qty(24, "h"), ev(3))]}],
    [fld("isolated_yield", qty(78, "%"), ev(3), ["product_z3h_d"]),
     fld("deuterium_incorporation", qty(97, "%"), ev(3), ["product_z3h_d"])],
    notes=["The text assigns deuterium incorporation to the center carbon atom of the allene-derived framework."],
    unresolved=["Covered pages do not state the batch scale or solvent volume.", "Candidate isotopologue structure is not source-verified."]
))

# Table 3: optically active substrates. Entry 1 is reconciled with Scheme 3 on page 3.
table3 = [
    (1, "(R)-1d", "Ph/H/H/n-C5H11", 98.5, 68, [97.6, 96.5], "1.20:1", "Z-3d"),
    (2, "(R)-1c", "Ph/H/H/n-C6H13", 99.0, 65, [98.9, 98.6], None, "Z-3c"),
    (3, "(R)-1r", "p-BrC6H4/Et/H/Me", 95.1, 74, [95.5, 94.1], None, "Z-3r"),
]
for entry, substrate, rvals, input_ee, yield_pct, output_ees, dr, product in table3:
    evidence = ev(4) + (ev(3) if entry == 1 else [])
    parts = [
        participant("chiral_substrate", "reactant", substrate, evidence,
                    f"optically active 1,2-allenylic sulfoxide; R1/R2/R3/R4 = {rvals}"),
        participant("hoac", "solvent", "HOAc", evidence, "acetic acid", "CC(=O)O"),
        participant("product_isomer_1", "product", f"{product}, diastereomer 1", evidence),
        participant("product_isomer_2", "product", f"{product}, diastereomer 2", evidence),
    ]
    outcomes = [
        fld("starting_material_ee", qty(input_ee, "%"), evidence, ["chiral_substrate"]),
        fld("combined_isolated_yield", qty(yield_pct, "%"), evidence, ["product_isomer_1", "product_isomer_2"]),
        fld("product_isomer_1_ee", qty(output_ees[0], "%"), evidence, ["product_isomer_1"]),
        fld("product_isomer_2_ee", qty(output_ees[1], "%"), evidence, ["product_isomer_2"]),
    ]
    if dr:
        outcomes.append(fld("diastereomer_ratio", dr, evidence, ["product_isomer_1", "product_isomer_2"]))
    notes = ["Table 3 states that ee values refer only to axial allene chirality or the carbon-center chirality."]
    if entry == 1:
        notes.append("Scheme 3 assigns the products as (Rs,3R)-(Z)-3d and (Ss,3R)-(Z)-3d by X-ray diffraction.")
    records.append(rec(f"table3_entry{entry}_{substrate.lower().replace('(', '').replace(')', '')}", "substrate_scope_entry", evidence,
                       parts,
                       [{"step_id": "enantiospecific_hydration", "participant_ids": ["chiral_substrate", "hoac"],
                         "conditions": [fld("temperature", qty(60, "°C"), evidence), fld("time", qty(24, "h"), evidence)]}],
                       outcomes, notes=notes,
                       unresolved=["Table 3 does not provide exact scale, solvent volume, workup, or purification on the covered pages.",
                                   "Stereochemical structures remain machine-unverified."]))

# Proposed mechanism, merged with the graphical abstract rather than treated as an experiment.
records.append(rec(
    "scheme4_proposed_hydration_mechanism", "mechanism", ev(1) + ev(4),
    [
        participant("chiral_allenyl_sulfoxide", "reactant", "(R)-1d (generic R1 at sulfur in Scheme 4)", ev(4)),
        participant("proton", "reagent", "H+", ev(4), "proton", "[H+]"),
        participant("water", "reagent", "H2O", ev(4), "water", "O"),
        participant("cyclic_intermediate_4", "unspecified_agent", "4 (proposed cyclic precursor)", ev(4)),
        participant("cyclic_intermediate_5", "unspecified_agent", "5 (proposed five-membered cyclic intermediate)", ev(4)),
        participant("z3d_product", "product", "(R)-(Z)-3d", ev(4)),
    ],
    [{"step_id": "proposed_sequence", "participant_ids": ["chiral_allenyl_sulfoxide", "proton", "water", "cyclic_intermediate_4", "cyclic_intermediate_5"],
      "conditions": [fld("operation", "proton addition, neighboring sulfinyl-oxygen participation, then water attack at sulfur and S-O cleavage", ev(4))]}],
    [], notes=["Scheme 4 is explicitly proposed as a possible mechanism and is not a batch experiment."],
    unresolved=["Intermediates 4 and 5 are proposed and generic; no yields or lifetimes are reported."]
))

# Precursor syntheses on pages 4-5. The abbreviated examples explicitly invoke the page-4 typical procedure.
precursors = [
    {
        "suffix": "synthesis_r_1d", "page": 4, "label": "(R)-(-)-1d", "name": "(R)-1,2-octadienyl phenyl sulfoxide",
        "start": "(R)-oct-1-yn-3-ol", "start_smiles": "C#C[C@@H](O)CCCCC", "start_mass": 0.4586, "start_mmol": 3.6,
        "base_ml": 0.50, "base_mass": 0.363, "base_mmol": 3.6,
        "sulfenyl": "phenylsulfenyl chloride", "sulfenyl_smiles": "ClSc1ccccc1", "sulf_mass": 0.6093, "sulf_mmol": 4.2,
        "dcm_main": 15, "dcm_add": 3, "mei_ml": 0.05, "mei_mass": 0.1140, "mei_mmol": 0.8,
        "product_smiles": "O=S(c1ccccc1)C=C=CCCCCC", "product_mass": 0.6764, "yield": 79, "ee": 98.5, "chrom": "5:1",
    },
    {
        "suffix": "synthesis_1e", "page": 5, "label": "1e", "name": "1,2-octadienyl 4-bromophenyl sulfoxide",
        "start": "oct-1-yn-3-ol", "start_smiles": "C#CC(O)CCCCC", "start_mass": 0.5053, "start_mmol": 4.0,
        "base_ml": 0.56, "base_mass": 0.4066, "base_mmol": 4.0,
        "sulfenyl": "4-bromophenylsulfenyl chloride", "sulfenyl_smiles": "ClSc1ccc(Br)cc1", "sulf_mass": 0.9465, "sulf_mmol": 4.2,
        "dcm_main": 15, "dcm_add": 2, "mei_ml": 0.05, "mei_mass": 0.1140, "mei_mmol": 0.80,
        "product_smiles": "O=S(c1ccc(Br)cc1)C=C=CCCCCC", "product_mass": 0.7558, "yield": 60, "ee": None, "chrom": "5:1",
    },
    {
        "suffix": "synthesis_1f", "page": 5, "label": "1f", "name": "1,2-octadienyl 4-nitrophenyl sulfoxide",
        "start": "oct-1-yn-3-ol", "start_smiles": "C#CC(O)CCCCC", "start_mass": 0.6298, "start_mmol": 5.0,
        "base_ml": 0.70, "base_mass": 0.5082, "base_mmol": 5.0,
        "sulfenyl": "4-nitrophenylsulfenyl chloride", "sulfenyl_smiles": "ClSc1ccc([N+](=O)[O-])cc1", "sulf_mass": 0.9944, "sulf_mmol": 5.3,
        "dcm_main": 20, "dcm_add": 5, "mei_ml": 0.07, "mei_mass": 0.1596, "mei_mmol": 1.1,
        "product_smiles": "O=S(c1ccc([N+](=O)[O-])cc1)C=C=CCCCCC", "product_mass": 0.8006, "yield": 57, "ee": None, "chrom": "5:1",
    },
    {
        "suffix": "synthesis_1h", "page": 5, "label": "1h", "name": "1-phenyl-3-ethyl-1,2-pentadienyl phenyl sulfoxide",
        "start": "3-ethyl-1-phenylpent-1-yn-3-ol", "start_smiles": "CCC(O)(CC)C#Cc1ccccc1", "start_mass": 0.9432, "start_mmol": 5.0,
        "base_ml": 0.70, "base_mass": 0.5082, "base_mmol": 5.0,
        "sulfenyl": "phenylsulfenyl chloride", "sulfenyl_smiles": "ClSc1ccccc1", "sulf_mass": 0.7634, "sulf_mmol": 5.3,
        "dcm_main": 15, "dcm_add": 2, "mei_ml": 0.07, "mei_mass": 0.1596, "mei_mmol": 1.1,
        "product_smiles": "O=S(c1ccccc1)C(c1ccccc1)=C=C(CC)CC", "product_mass": 0.7135, "yield": 48, "ee": None, "chrom": "7.5:1",
    },
]

for row in precursors:
    evidence = ev(row["page"]) + (ev(4) if row["page"] == 5 else []) + (ev(3) if row["suffix"] == "synthesis_r_1d" else [])
    workup_amounts_water = [fld("volume", qty(20, "mL"), ev(4))] if row["page"] == 4 else []
    workup_amounts_ether = [fld("volume_per_extraction", qty(20, "mL"), ev(4))] if row["page"] == 4 else []
    parts = [
        participant("propargylic_alcohol", "reactant", row["start"], evidence, row["start"], row["start_smiles"],
                    [fld("mass", qty(row["start_mass"], "g"), evidence), fld("amount", qty(row["start_mmol"], "mmol"), evidence)]),
        participant("triethylamine", "reagent", "Et3N", evidence, "triethylamine", "CCN(CC)CC",
                    [fld("volume", qty(row["base_ml"], "mL"), evidence), fld("mass", qty(row["base_mass"], "g"), evidence), fld("amount", qty(row["base_mmol"], "mmol"), evidence)]),
        participant("methylene_chloride", "solvent", "methylene chloride", evidence, "dichloromethane", "ClCCl",
                    [fld("initial_volume", qty(row["dcm_main"], "mL"), evidence), fld("addition_solution_volume", qty(row["dcm_add"], "mL"), evidence)]),
        participant("sulfenyl_chloride", "reagent", row["sulfenyl"], evidence, row["sulfenyl"], row["sulfenyl_smiles"],
                    [fld("mass", qty(row["sulf_mass"], "g"), evidence), fld("amount", qty(row["sulf_mmol"], "mmol"), evidence)]),
        participant("methyl_iodide", "reagent", "CH3I", evidence, "methyl iodide", "CI",
                    [fld("volume", qty(row["mei_ml"], "mL"), evidence), fld("mass", qty(row["mei_mass"], "g"), evidence), fld("amount", qty(row["mei_mmol"], "mmol"), evidence)]),
        participant("workup_water", "reagent", "water", evidence, "water", "O", workup_amounts_water),
        participant("workup_ether", "solvent", "diethyl ether", evidence, "diethyl ether", "CCOCC", workup_amounts_ether),
        participant("drying_sodium_sulfate", "reagent", "anhydrous Na2SO4", evidence, "sodium sulfate", "[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
        participant("product", "product", row["label"], evidence, row["name"], row["product_smiles"]),
    ]
    steps = [
        {"step_id": "low_temperature_rearrangement", "participant_ids": ["propargylic_alcohol", "triethylamine", "methylene_chloride", "sulfenyl_chloride"],
         "conditions": [fld("atmosphere", "N2", evidence), fld("temperature", qty(-67, "°C"), evidence),
                        fld("addition_time", qty(20, "min"), evidence), fld("post_addition_time", qty(15, "min"), evidence),
                        fld("operation", "sulfenyl chloride solution added dropwise; reaction monitored by TLC", evidence)]},
        {"step_id": "quench_and_warm", "participant_ids": ["methyl_iodide"],
         "conditions": [fld("operation", "quenched with methyl iodide and allowed to warm to room temperature", evidence)]},
        {"step_id": "isolation", "participant_ids": ["workup_water", "workup_ether", "drying_sodium_sulfate", "product"],
         "conditions": [fld("workup", "water addition, phase separation, ether extraction, Na2SO4 drying, filtration and evaporation according to the typical procedure", evidence),
                        fld("purification", f"silica-gel chromatography, petroleum ether/ethyl acetate = {row['chrom']}", evidence)]},
    ]
    outcomes = [fld("isolated_yield", qty(row["yield"], "%"), evidence, ["product"]),
                fld("product_mass", qty(row["product_mass"], "g"), evidence, ["product"])]
    if row["ee"] is not None:
        outcomes.append(fld("product_ee", qty(row["ee"], "%"), evidence, ["product"]))
    if row["suffix"] == "synthesis_r_1d":
        outcomes.append(fld("sulfoxide_diastereomer_ratio", "1.91:1", ev(3), ["product"]))
    unresolved = ["Supporting Information was not explicitly associated; candidate connectivity/stereochemistry remains unverified."]
    if row["page"] == 5:
        unresolved.append("The page-5 paragraph invokes the page-4 typical procedure; inherited timing, atmosphere, and workup are linked to both pages.")
    records.append(rec(row["suffix"], "reported_experiment", evidence, parts, steps, outcomes,
                       notes=["Density values are present in the source but are not required to reconstruct the explicitly reported masses and volumes."],
                       unresolved=unresolved))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


ids = {r["record_id"] for r in records}
page3_table1 = [f"{DOC}:table1_entry{i}" for i in range(2, 12)] + [f"{DOC}:table1_entry1_table2_entry1_z3a"]
page3_table2 = [f"{DOC}:table1_entry1_table2_entry1_z3a"] + [f"{DOC}:table2_entry{i}_{scope[i][2].lower()}" for i in range(2, 19)]
page4_table3 = [f"{DOC}:table3_entry{i}_{table3[i-1][1].lower().replace('(', '').replace(')', '')}" for i in range(1, 4)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "full-page journal cover and central graphical abstract", "finding": "Cover graphic depicts the generic HOAc hydration and a proposed cyclic mechanism; linked to the general-scheme and mechanism records, not counted as a batch experiment.", "evidence_ids": ev(1)}
        ], "record_ids": [f"{DOC}:current_hydration_general_scheme", f"{DOC}:scheme4_proposed_hydration_mechanism"],
         "unresolved": ["The cover uses generic R1 and omits scale, duration, and yield."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "left column Scheme 1", "finding": "Generic halohydroxylation/selenohydroxylation is explicitly cited prior work and classified as a literature example.", "evidence_ids": ev(2)},
            {"region": "right column Scheme 2", "finding": "Upper oxidative hydroacetoxylation arrow is cited 2009 work; lower HOAc arrow is the generic current hydration and is classified separately from batch rows.", "evidence_ids": ev(2)},
            {"region": "lower-right Results and discussion prose", "finding": "Narrative defines the Table 1 solvent, temperature, time, and concentration screen; independent rows are extracted from page 3.", "evidence_ids": ev(2)}
        ], "record_ids": [f"{DOC}:scheme1_prior_halohydroxylation_selenohydroxylation", f"{DOC}:scheme2_prior_oxidative_hydroacetoxylation", f"{DOC}:current_hydration_general_scheme"],
         "unresolved": ["Schemes 1 and 2 are generic and do not state batch scales or yields."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and footnotes", "finding": "Eleven optimization rows checked; entry 1 reconciled with Table 2 entry 1 and the page-5 Z-3a procedure, while entries 2-11 remain distinct condition rows. HOAc footnote additions and 96% recovery are structured.", "evidence_ids": ev(3)},
            {"region": "middle/lower-left Table 2 and footnotes", "finding": "Eighteen substrate-scope rows checked one by one; row-specific yields, diastereomer ratios, room-temperature overrides, and ratio measurement bases retained.", "evidence_ids": ev(3)},
            {"region": "upper-right equation 1", "finding": "Separate DOAc/D2O labeling experiment gives d-(Z)-3h in 78% yield with 97% D incorporation.", "evidence_ids": ev(3)},
            {"region": "middle-right Scheme 3 and Fig. 1", "finding": "Optically active (R)-1d hydration is reconciled with Table 3 entry 1; two X-ray-assigned diastereomers are products, and Fig. 1 is characterization rather than a new experiment.", "evidence_ids": ev(3)}
        ], "record_ids": list(dict.fromkeys(page3_table1 + page3_table2 + [f"{DOC}:eq1_deuterium_labeling_z3h_d", f"{DOC}:table3_entry1_r-1d"])),
         "unresolved": ["Table structures and stereochemical assignments remain machine-unverified; SI was not associated."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-left Table 3", "finding": "Three optically active substrate rows extracted with input ee, combined yield, and two product ee values per row.", "evidence_ids": ev(4)},
            {"region": "middle-left Fig. 2", "finding": "ORTEP image supports the second Z-3d diastereomer assignment but is not an independent reaction.", "evidence_ids": ev(4)},
            {"region": "lower-left Scheme 4", "finding": "Proposed five-membered cyclic mechanism classified as mechanism, with no experimental yield attached.", "evidence_ids": ev(4)},
            {"region": "right-column experimental section, synthesis of (R)-1d", "finding": "Full low-temperature precursor preparation extracted with quantities, staged operations, workup, 79% isolated yield, and 98.5% ee.", "evidence_ids": ev(4)}
        ], "record_ids": page4_table3 + [f"{DOC}:scheme4_proposed_hydration_mechanism", f"{DOC}:synthesis_r_1d"],
         "unresolved": ["Absolute/axial stereochemical structures are not source-verified as SMILES; SI is unassociated."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "left column precursor syntheses 1e, 1f, and 1h", "finding": "Three abbreviated precursor preparations extracted and linked to the page-4 typical procedure; exact reactant/reagent amounts, solvent volumes, product masses, and isolated yields retained.", "evidence_ids": ev(5)},
            {"region": "lower-left/right hydration typical procedure for Z-3a", "finding": "Detailed Z-3a batch merged with Table 1 entry 1 and Table 2 entry 1, including workup, chromatography, 64.9 mg product, and 87% isolated yield.", "evidence_ids": ev(5)},
            {"region": "right column Z-3b and Z-3c procedures", "finding": "Table 2 entries 2 and 3 enriched with exact scale, solvent, product masses, purification, and yield; two Z-3c polar isomers remain separate product entities.", "evidence_ids": ev(5)},
            {"region": "bottom-right start of Z-3d procedure", "finding": "Visible Z-3d reaction conditions linked to Table 2 entry 4; its outcome continues on page 6.", "evidence_ids": ev(5)}
        ], "record_ids": [f"{DOC}:synthesis_1e", f"{DOC}:synthesis_1f", f"{DOC}:synthesis_1h", f"{DOC}:table1_entry1_table2_entry1_z3a"] + [f"{DOC}:table2_entry{i}_{scope[i][2].lower()}" for i in range(2, 11)],
         "unresolved": ["Abbreviated precursor procedures inherit operations from the explicitly referenced typical procedure; their candidate structures remain unverified."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "upper-left continuation of Z-3d", "finding": "Two isomer masses and 66% combined isolated yield merged into Table 2 entry 4.", "evidence_ids": ev(6)},
            {"region": "left column Z-3e and Z-3f", "finding": "Detailed scope batches merged into Table 2 entries 5 and 6 with scale, solvent, paired isomer masses, purification, yields, and table diastereomer ratios.", "evidence_ids": ev(6)},
            {"region": "right column Z-3g, Z-3h, and Z-3i", "finding": "Detailed scope batches merged into Table 2 entries 7-9; room-temperature conditions for 3g/3h and the 1H-NMR-based 3i ratio are preserved.", "evidence_ids": ev(6)},
            {"region": "bottom-right start of Z-3j", "finding": "Visible batch facts for Table 2 entry 10 include scale, HOAc volume, 60 °C/24 h, purification, 41.7 mg, and 58%; characterization continues on page 7 and is not claimed covered.", "evidence_ids": ev(6)}
        ], "record_ids": [f"{DOC}:table2_entry{i}_{scope[i][2].lower()}" for i in range(4, 11)],
         "unresolved": ["Z-3j characterization continues onto page 7; it was not imported or claimed as covered.", "Spectral data were observed but not atom-by-atom interpreted."]},
    ],
}

assert len(records) == 40, len(records)
assert len(ids) == len(records)
assert len(coverage["pages"]) == 6
assert [p["page"] for p in coverage["pages"]] == [1, 2, 3, 4, 5, 6]
assert all(p["regions"] for p in coverage["pages"])
assert all(rid in ids for p in coverage["pages"] for rid in p["record_ids"])
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 7)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; records and coverage ledger generated for this pass."
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "output": str(OUT)}, ensure_ascii=False))
