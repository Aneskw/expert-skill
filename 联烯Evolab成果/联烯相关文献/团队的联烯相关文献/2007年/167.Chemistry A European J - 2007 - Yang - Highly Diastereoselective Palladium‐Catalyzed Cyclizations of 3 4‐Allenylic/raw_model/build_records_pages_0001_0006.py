import json
from pathlib import Path

DOC = "doc_ea07b22f3f37e3c8"
BASE = Path(__file__).resolve().parents[1]


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return out


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def part(entity_id, role, label, name, evidence, smiles=None, amounts=()):
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


def missing_conditions():
    return [fld("atmosphere", None, ()), fld("workup", None, ()), fld("purification", None, ())]


def record(rid, kind, evidence, participants, conditions, outcomes, unresolved, notes=()):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
            "conditions": list(conditions),
        }],
        "outcomes": list(outcomes),
        "notes": [fact(n, evidence) for n in notes],
        "review": {"method": "model", "reviewer": None, "checked_fields": [], "unresolved": list(unresolved)},
    }


def amount(name, number, unit, evidence):
    return fld(name, qty(number, unit), evidence)


records = []
p2 = ev(2)

# Table 1: every optimization row remains independent.
table1 = [
    (1, "L1", "THF", "C1CCOC1", 69, 99, 88, "87:13"),
    (2, "L2", "THF", "C1CCOC1", 81, 98, 85, "95:5"),
    (3, "L3", "THF", "C1CCOC1", 83, 98, 99, "57:43"),
    (4, "L2", "DMF", "CN(C)C=O", 83, 97, 90, "86:14"),
    (5, "L2", "1,4-dioxane", "O1CCOCC1", 76, 99, 76, "93:7"),
]
for entry, ligand, solvent, solv_smiles, yld, trans_ee, cis_ee, dr in table1:
    e = p2
    participants = [
        part("substrate_1a", "reactant", "(R)-1a", "optically active allenylhydrazine 1a", e, amounts=[amount("amount", 0.2, "mmol", e)]),
        part("iodobenzene_2a", "reactant", "2a", "iodobenzene", e, "Ic1ccccc1", [amount("amount", 0.4, "mmol", e)]),
        part("product_3aa", "product", "3aa", "cis/trans pyrazolidine 3aa", e),
        part("pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", e, "[Pd+2].CC(=O)[O-].CC(=O)[O-]", [amount("catalyst_loading", 5, "mol%", e)]),
        part("ligand", "catalyst", ligand, f"chiral ligand {ligand}", e, amounts=[amount("ligand_loading", 10, "mol%", e)]),
        part("ag3po4", "reagent", "Ag3PO4", "silver phosphate", e, amounts=[amount("amount", 0.08, "mmol", e)]),
        part("solvent", "solvent", solvent, solvent, e, solv_smiles, [amount("volume", 2, "mL", e)]),
    ]
    conditions = [fld("temperature", qty(80, "°C"), e), fld("time", qty(10, "h"), e)] + missing_conditions()
    outcomes = [
        fld("isolated_yield", qty(yld, "%"), e, ["product_3aa"]),
        fld("yield_measurement_basis", "isolated yield", e, ["product_3aa"]),
        fld("trans_3R_5S_ee", qty(trans_ee, "%"), e, ["product_3aa"]),
        fld("cis_3R_5R_ee", qty(cis_ee, "%"), e, ["product_3aa"]),
        fld("diastereomeric_ratio_trans_to_cis", dr, e, ["product_3aa"]),
    ]
    records.append(record(f"table1_entry{entry}_3aa", "optimization_entry", e, participants, conditions, outcomes,
                          ["Atmosphere, workup, and purification are not reported for this optimization row.",
                           "Complex substrate, ligand, and product structures require independent structure review."]))


def cyclization_participants(e, substrate_label, substrate_name, substrate_mass, substrate_mmol,
                             halide_label, halide_name, halide_smiles, halide_mass, halide_mmol,
                             product_label, product_name, product_mass, solvent="THF", solvent_smiles="C1CCOC1",
                             ag_mass=34):
    return [
        part("substrate", "reactant", substrate_label, substrate_name, e, amounts=[amount("mass", substrate_mass, "mg", e), amount("amount", substrate_mmol, "mmol", e)]),
        part("organic_halide", "reactant", halide_label, halide_name, e, halide_smiles, [amount("mass", halide_mass, "mg", e), amount("amount", halide_mmol, "mmol", e)]),
        part("product", "product", product_label, product_name, e),
        part("pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", e, "[Pd+2].CC(=O)[O-].CC(=O)[O-]", [amount("catalyst_loading", 5, "mol%", e)]),
        part("bn_box", "catalyst", "(R,R)-Bn-Box", "(R,R)-2,2'-isopropylidenebis(4-benzyl-2-oxazoline)", e, amounts=[amount("ligand_loading", 10, "mol%", e)]),
        part("ag3po4", "reagent", "Ag3PO4", "silver phosphate", e, amounts=[amount("mass", ag_mass, "mg", e), amount("amount", 0.08, "mmol", e)]),
        part("solvent", "solvent", solvent, solvent, e, solvent_smiles,
             [amount("catalyst_solution_volume", 1, "mL", e), amount("reaction_solution_volume", 1, "mL", e)]),
    ]


# Table 2 rows, enriched with their exact experimental paragraphs on pages 4–6.
scope = [
    # entry, pages, substrate, mass/mmol, halide label/name/smiles/mass/mmol, product label/name/mass, temp, yields, ee trans/cis, dr, solvent
    (1, (2,3,4), "(R)-1a", "allenylhydrazine (R)-1a", 102, .21, "2a", "iodobenzene", "Ic1ccccc1", 50, .24, "3aa", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-(1-phenylethenyl)pyrazolidine", 96, 80, (81,), 99, 73, "94:6", "THF", "C1CCOC1"),
    (2, (2,4,5), "(R)-1a", "allenylhydrazine (R)-1a", 91, .19, "4-MeC6H4I", "4-iodotoluene", "Cc1ccc(I)cc1", 55, .25, "3ab", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[1-(4-methylphenyl)ethenyl]pyrazolidine", 87, 80, (81,), 99, 85, "92:8", "THF", "C1CCOC1"),
    (3, (2,5), "(R)-1a", "allenylhydrazine (R)-1a", 96, .20, "4-MeC6H4I", "4-iodotoluene", "Cc1ccc(I)cc1", 54, .25, "3ab", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[1-(4-methylphenyl)ethenyl]pyrazolidine", 91, 80, (80,), 99, 80, "93:7", "1,4-dioxane", "O1CCOCC1"),
    (4, (2,5), "(R)-1a", "allenylhydrazine (R)-1a", 94, .20, "4-MeOC6H4I", "4-iodoanisole", "COc1ccc(I)cc1", 58, .25, "3ac", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[1-(4-methoxyphenyl)ethenyl]pyrazolidine", 97, 80, (85,), 99, 85, "94:6", "THF", "C1CCOC1"),
    (5, (2,5), "(R)-1a", "allenylhydrazine (R)-1a", 98, .20, "4-MeO2CC6H4I", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 64, .24, "3ad", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[1-(4-methoxycarbonylphenyl)ethenyl]pyrazolidine", 101, 80, (83,81), 97, 81, "95:5", "THF", "C1CCOC1"),
    (6, (2,5), "(R)-1a", "allenylhydrazine (R)-1a", 94, .20, "(E)-n-C4H9C2H2I", "(E)-1-iodohex-1-ene", "CCCC/C=C/I", 56, .26, "3ae", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[(E)-1-methylenehept-2-enyl]pyrazolidine", 90, 80, (82,), 99, 83, "93:7", "THF", "C1CCOC1"),
    (7, (2,5), "(R)-1a", "allenylhydrazine (R)-1a", 101, .21, "2-iodothiophene", "2-iodothiophene", "Ic1cccs1", 53, .25, "3af", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[1-(2-thienyl)ethenyl]pyrazolidine", 78, 80, (67,66), 99, 79, "95:5", "THF", "C1CCOC1"),
    (8, (2,5), "(R)-1a", "allenylhydrazine (R)-1a", 99, .21, "4-BrC6H4I", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", 70, .25, "3ag/3ah", "3-acetyl-1,2-dibenzyloxycarbonyl-3-ethoxycarbonyl-5-[1-(4-bromophenyl)ethenyl]pyrazolidine", 112, 80, (86,), ">95", 85, "93:7", "THF", "C1CCOC1"),
    (9, (2,5), "(R)-1b", "allenylhydrazine (R)-1b", 99, .20, "2a", "iodobenzene", "Ic1ccccc1", 55, .26, "3ba", "1,2-dibenzyloxycarbonyl-3-butyryl-3-methoxycarbonyl-5-(1-phenylethenyl)pyrazolidine", 96, 70, (81,), 99, 83, "91:9", "THF", "C1CCOC1"),
    (10, (2,5,6), "(R)-1c", "allenylhydrazine (R)-1c", 98, .20, "2a", "iodobenzene", "Ic1ccccc1", 55, .26, "3ca", "1,2-dibenzyloxycarbonyl-3-isobutyryl-3-methoxycarbonyl-5-(1-phenylethenyl)pyrazolidine", 90, 70, (78,), 99, 81, "92:8", "THF", "C1CCOC1"),
]

for row in scope:
    (entry, pages, sublabel, subname, smass, smmol, hlabel, hname, hsmiles, hmass, hmmol,
     plabel, pname, pmass, temp, yields, trans_ee, cis_ee, dr, solvent, solv_smiles) = row
    e = ev(*pages)
    participants = cyclization_participants(e, sublabel, subname, smass, smmol, hlabel, hname, hsmiles,
                                             hmass, hmmol, plabel, pname, pmass, solvent, solv_smiles)
    participants[2]["amounts"] = [amount("isolated_product_mass", pmass, "mg", e)]
    conditions = [fld("temperature", qty(temp, "°C"), e), fld("time", qty(10, "h"), e),
                  fld("atmosphere", None, ()), fld("workup", "rotary evaporation", e),
                  fld("purification", "flash chromatography on silica gel (petroleum ether/ethyl acetate 5:1)", e)]
    outcomes = []
    if len(yields) == 1:
        outcomes.append(fld("isolated_yield", qty(yields[0], "%"), e, ["product"]))
    else:
        outcomes.append(fld("table_2_isolated_yield", qty(yields[0], "%"), ev(2), ["product"]))
        outcomes.append(fld("experimental_section_isolated_yield", qty(yields[1], "%"), ev(5), ["product"]))
    trans_value = qty(95, "%", qualifier="gt", raw_text=">95%") if trans_ee == ">95" else qty(trans_ee, "%")
    outcomes += [
        fld("yield_measurement_basis", "isolated yield", e, ["product"]),
        fld("major_trans_product_ee", trans_value, e, ["product"]),
        fld("minor_cis_product_ee", qty(cis_ee, "%"), e, ["product"]),
        fld("diastereomeric_ratio_trans_to_cis", dr, e, ["product"]),
    ]
    notes = ["The table calls the benzyl-substituted bisoxazoline ligand L2, while the experimental section calls the same named ligand L1."]
    unresolved = ["Complex allenylhydrazine and pyrazolidine structures and stereochemical SMILES require independent structure review.",
                  "Reaction atmosphere is not reported."]
    if entry in (5, 7):
        unresolved.append("The Table 2 and experimental-section isolated yields disagree; both source values are retained.")
    if entry == 8:
        notes.append("Table 2 labels the bromophenyl product 3ag; the experimental heading labels it 3ah and the sentence reporting formation prints 3af.")
        unresolved.append("Product code is internally inconsistent (3ag/3ah/3af); the named bromophenyl product is retained without choosing a code.")
    if entry == 4:
        notes.append("The experimental dr sentence prints one cis isomer as 1ac; the product heading and remaining text identify 3ac.")
    if entry == 1:
        outcomes.append(fld("table4_entry1_HPLC_peak_integrations", {
            "from_R_1a_total_percent": 98.87, "3R_5R_percent": 5.16, "3R_5S_percent": 93.71,
            "from_S_1a_total_percent": 1.13, "3S_5S_percent": 0.80, "3S_5R_percent": 0.33,
        }, ev(3), ["product"]))
        notes.append("Table 3 entry 1 and Table 4 entry 1 report the same reaction as Table 2 entry 1 and were merged as additional evidence and outcomes.")
    records.append(record(f"table2_entry{entry}_{plabel.replace('/', '_')}", "substrate_scope_entry", e,
                          participants, conditions, outcomes, unresolved, notes))


def control_record(entry, substrate_label, substrate_name, smass, ligand_label, ligand_name, agmass,
                   product_mass, yld, cis_ee, trans_ee, dr, pages, integration=None, narrative_trans_ee=None):
    e = ev(*pages)
    participants = [
        part("substrate", "reactant", substrate_label, substrate_name, e,
             amounts=[amount("mass", smass, "mg", e), amount("amount", .20, "mmol", e)]),
        part("iodobenzene", "reactant", "PhI", "iodobenzene", e, "Ic1ccccc1",
             [amount("mass", 50, "mg", e), amount("amount", .24, "mmol", e)]),
        part("cis_product", "product", "cis-3aa", "cis stereoisomer of 3aa", e),
        part("trans_product", "product", "trans-3aa", "trans stereoisomer of 3aa", e),
        part("pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", e, "[Pd+2].CC(=O)[O-].CC(=O)[O-]", [amount("catalyst_loading", 5, "mol%", e)]),
        part("ligand", "catalyst", ligand_label, ligand_name, e, amounts=[amount("ligand_loading", 10, "mol%", e)]),
        part("ag3po4", "reagent", "Ag3PO4", "silver phosphate", e,
             amounts=[amount("mass", agmass, "mg", e), amount("amount", .08, "mmol", e)]),
        part("thf", "solvent", "THF", "tetrahydrofuran", e, "C1CCOC1",
             [amount("catalyst_solution_volume", 1, "mL", e), amount("reaction_solution_volume", 1, "mL", e)]),
    ]
    conditions = [fld("temperature", qty(80, "°C"), e), fld("time", qty(10, "h"), e), fld("atmosphere", None, ()),
                  fld("workup", "rotary evaporation", e), fld("purification", "flash chromatography on silica gel", e)]
    outcomes = [
        fld("combined_isolated_yield", qty(yld, "%"), e, ["cis_product", "trans_product"]),
        fld("isolated_product_mixture_mass", qty(product_mass, "mg"), e, ["cis_product", "trans_product"]),
        fld("yield_measurement_basis", "isolated yield", e, ["cis_product", "trans_product"]),
        fld("cis_product_ee", qty(cis_ee, "%"), e, ["cis_product"]),
        fld("trans_product_ee", qty(trans_ee, "%"), e, ["trans_product"]),
        fld("diastereomeric_ratio_cis_to_trans", dr, e, ["cis_product", "trans_product"]),
    ]
    unresolved = ["Complex substrate and product structures require independent structure review.", "Reaction atmosphere is not reported."]
    notes = ["The experimental section gives the benzyl-substituted bisoxazoline name but contains inconsistent L1/L2 and configuration labels; the explicit ligand name/configuration and table row were retained."]
    if integration:
        outcomes.append(fld("table4_HPLC_peak_integrations", integration, ev(3), ["cis_product", "trans_product"]))
    if narrative_trans_ee is not None:
        outcomes.append(fld("narrative_trans_product_ee", qty(narrative_trans_ee, "%"), ev(3), ["trans_product"]))
        unresolved.append("Page 3 narrative and Table 3/experimental section disagree on the trans-product ee; both values are retained.")
    return record(f"table3_entry{entry}_3aa", "reported_experiment", e, participants, conditions, outcomes, unresolved, notes)


records.append(control_record(2, "(R)-1a", "allenylhydrazine (R)-1a", 96, "(S,S)-Bn-Box",
                              "(S,S)-2,2'-isopropylidenebis(4-benzyl-2-oxazoline)", 33, 90, 81, 97, 90, "65:35", (3,6)))
records.append(control_record(3, "(S)-1a", "allenylhydrazine (S)-1a", 98, "(R,R)-Bn-Box",
                              "(R,R)-2,2'-isopropylidenebis(4-benzyl-2-oxazoline)", 34, 91, 80, 99, 94, "61:39", (3,6),
                              integration={"from_R_1a_total_percent": 1.46, "3R_5R_percent": .36, "3R_5S_percent": 1.10,
                                           "from_S_1a_total_percent": 98.54, "3S_5S_percent": 60.56, "3S_5R_percent": 37.98},
                              narrative_trans_ee=92))
records.append(control_record(4, "(S)-1a", "allenylhydrazine (S)-1a", 96, "(S,S)-Bn-Box",
                              "(S,S)-2,2'-isopropylidenebis(4-benzyl-2-oxazoline)", 34, 95, 85, 85, 99, "6:94", (3,6)))


def prediction_test(rid, substrate_label, substrate_ee, smass, ph_mass, ag_mass, pmass, yld, dr,
                    cis_ee, trans_ee, actual_integration, predicted_integration, predicted_dr,
                    predicted_cis_ee, predicted_trans_ee, pages, note=None):
    e = ev(*pages)
    participants = [
        part("substrate", "reactant", substrate_label, "allenylhydrazine 1a", e,
             amounts=[amount("mass", smass, "mg", e), amount("amount", .20, "mmol", e), amount("starting_material_ee", substrate_ee, "%", e)]),
        part("iodobenzene", "reactant", "PhI", "iodobenzene", e, "Ic1ccccc1", [amount("mass", ph_mass, "mg", e), amount("amount", .4, "mmol", e)]),
        part("cis_product", "product", "cis-3aa", "cis stereoisomer of 3aa", e),
        part("trans_product", "product", "trans-3aa", "trans stereoisomer of 3aa", e),
        part("pd_oac2", "catalyst", "Pd(OAc)2", "palladium(II) acetate", e, "[Pd+2].CC(=O)[O-].CC(=O)[O-]", [amount("catalyst_loading", 5, "mol%", e)]),
        part("bn_box", "catalyst", "(R,R)-Bn-Box", "(R,R)-2,2'-isopropylidenebis(4-benzyl-2-oxazoline)", e, amounts=[amount("ligand_loading", 10, "mol%", e)]),
        part("ag3po4", "reagent", "Ag3PO4", "silver phosphate", e, amounts=[amount("mass", ag_mass, "mg", e), amount("amount", .08, "mmol", e)]),
        part("thf", "solvent", "THF", "tetrahydrofuran", e, "C1CCOC1", [amount("catalyst_solution_volume", 1, "mL", e), amount("reaction_solution_volume", 1, "mL", e)]),
    ]
    conditions = [fld("temperature", qty(80, "°C"), e), fld("time", qty(10, "h"), e), fld("atmosphere", None, ()),
                  fld("workup", "rotary evaporation", e), fld("purification", "flash chromatography on silica gel", e)]
    outcomes = [
        fld("combined_isolated_yield", qty(yld, "%"), e, ["cis_product", "trans_product"]),
        fld("isolated_product_mixture_mass", qty(pmass, "mg"), e, ["cis_product", "trans_product"]),
        fld("yield_measurement_basis", "isolated yield", e, ["cis_product", "trans_product"]),
        fld("actual_diastereomeric_ratio_cis_to_trans", dr, e, ["cis_product", "trans_product"]),
        fld("actual_cis_product_ee", qty(cis_ee, "%"), e, ["cis_product"]),
        fld("actual_trans_product_ee", qty(trans_ee, "%"), e, ["trans_product"]),
        fld("actual_HPLC_peak_integrations", actual_integration, ev(3), ["cis_product", "trans_product"]),
        fld("predicted_HPLC_peak_integrations", predicted_integration, ev(3), ["cis_product", "trans_product"]),
        fld("predicted_diastereomeric_ratio_cis_to_trans", predicted_dr, ev(4), ["cis_product", "trans_product"]),
        fld("predicted_cis_product_ee", qty(predicted_cis_ee, "%"), ev(4), ["cis_product"]),
        fld("predicted_trans_product_ee", qty(predicted_trans_ee, "%"), ev(4), ["trans_product"]),
    ]
    notes = ["Predicted Table 4 row and Scheme 1 values are retained separately from the subsequently measured values."]
    if note:
        notes.append(note)
    return record(rid, "reported_experiment", e, participants, conditions, outcomes,
                  ["Complex substrate and product structures require independent structure review.",
                   "Reaction atmosphere is not reported.",
                   "The experimental section contains inconsistent stereoisomer labels; product assignment needs source review."], notes)


records.append(prediction_test(
    "table4_entry4_rac_1a_actual", "rac-1a", 0, 96, 82, 34, 88, 79, "35:65", 86, 43,
    {"from_R_1a_total_percent": 49.00, "3R_5R_percent": 2.38, "3R_5S_percent": 46.62,
     "from_S_1a_total_percent": 51.00, "3S_5S_percent": 32.42, "3S_5R_percent": 18.58},
    {"from_R_1a_total_percent": 50.00, "3R_5R_percent": 2.61, "3R_5S_percent": 47.39,
     "from_S_1a_total_percent": 50.00, "3S_5S_percent": 30.73, "3S_5R_percent": 19.27},
    "33.3:66.7", 84, 42, (3,4,6),
    "Scheme 1 assigns the measured cis and trans products as cis-(3S,5S)-3aa and trans-(3R,5S)-3aa; page 6 headings are internally inconsistent."))
records.append(prediction_test(
    "table4_entry6_R_1a_84ee_actual", "(R)-1a", 84, 95, 84, 33, 93, 85, "9:91", 2.7, 95,
    {"from_R_1a_total_percent": 93.13, "3R_5R_percent": 4.82, "3R_5S_percent": 88.31,
     "from_S_1a_total_percent": 6.68, "3S_5S_percent": 4.56, "3S_5R_percent": 2.31},
    {"from_R_1a_total_percent": 92.00, "3R_5R_percent": 4.80, "3R_5S_percent": 87.20,
     "from_S_1a_total_percent": 8.00, "3S_5S_percent": 4.92, "3S_5R_percent": 3.08},
    "10.7:90.3", 1, 93, (3,4,6),
    "Scheme 1 prints the observed cis ee as -3% to indicate the opposite enantiomer direction; the experimental section reports 2.7% ee."))


# Preparations of the four optically active allenylhydrazines on page 4.
prep_specs = [
    ("prep_R_1a", "ethyl 2-(buta-2,3-dienyl)-3-oxobutanoate", "CCOC(=O)C(CC=C=C)C(C)=O", 1328, 7.2,
     "(S,S)-Ph-Box", 255, .78, 270, .75, 2999, 9.1, 60, "(R)-1a", 3373, 97, 98, True),
    ("prep_S_1a", "ethyl 2-(buta-2,3-dienyl)-3-oxobutanoate", "CCOC(=O)C(CC=C=C)C(C)=O", 258, 1.42,
     "(R,R)-Ph-Box", 54, None, 53, None, 663, 2.0, 12, "(S)-1a", 627, 92, 97.6, False),
    ("prep_R_1b", "methyl 2-(buta-2,3-dienyl)-3-oxohexanoate", "COC(=O)C(CC=C=C)C(=O)CCC", 409, 2.09,
     "(S,S)-Ph-Box", 73, None, 76, None, 884, 2.67, 20, "(R)-1b", 808, 78, 98, False),
    ("prep_R_1c", "methyl 2-(buta-2,3-dienyl)-4-methyl-3-oxopentanoate", "COC(=O)C(CC=C=C)C(=O)C(C)C", 490, 2.50,
     "(S,S)-Ph-Box", 88, None, 90, None, 994, 3.00, 20, "(R)-1c", 1107, 90, 98, False),
]
for rid, precursor_name, precursor_smiles, pmass, pmmol, ligand_label, lmass, lmmol, cmass, cmmol, dbmass, dbmmol, svol, product_label, product_mass, yld, ee_value, full in prep_specs:
    e = ev(4)
    ligand_amounts = [amount("mass", lmass, "mg", e), amount("ligand_loading", 10.4 if rid != "prep_R_1c" else 10.6, "mol%", e)]
    if lmmol is not None:
        ligand_amounts.append(amount("amount", lmmol, "mmol", e))
    catalyst_amounts = [amount("mass", cmass, "mg", e), amount("catalyst_loading", 10, "mol%", e)]
    if cmmol is not None:
        catalyst_amounts.append(amount("amount", cmmol, "mmol", e))
    participants = [
        part("precursor", "reactant", None, precursor_name, e, precursor_smiles, [amount("mass", pmass, "mg", e), amount("amount", pmmol, "mmol", e)]),
        part("dbad", "reactant", "DBAD", "dibenzyl azodicarboxylate", e, "O=C(OCc1ccccc1)N=NC(=O)OCc1ccccc1", [amount("mass", dbmass, "mg", e), amount("amount", dbmmol, "mmol", e)]),
        part("product", "product", product_label, f"optically active allenylhydrazine {product_label}", e, amounts=[amount("isolated_product_mass", product_mass, "mg", e)]),
        part("cu_otf2", "catalyst", "Cu(OTf)2", "copper(II) triflate", e, "[Cu+2].O=S(=O)([O-])C(F)(F)F.O=S(=O)([O-])C(F)(F)F", catalyst_amounts),
        part("ligand", "catalyst", ligand_label, f"{ligand_label} 2,2'-isopropylidenebis(4-phenyl-2-oxazoline)", e, amounts=ligand_amounts),
        part("dcm", "solvent", "CH2Cl2", "dichloromethane", e, "ClCCl", [amount("volume", svol, "mL", e)]),
    ]
    if full:
        rec = record(rid, "reported_experiment", e, participants,
                     [fld("addition_temperature", qty(0, "°C"), e), fld("reaction_temperature", qty(0, "°C"), e),
                      fld("time", qty(4, "h"), e), fld("atmosphere", None, ()),
                      fld("workup", "evaporation", e), fld("purification", "flash chromatography on silica gel (petroleum ether/ether 2:1)", e)],
                     [fld("isolated_yield", qty(yld, "%"), e, ["product"]), fld("yield_measurement_basis", "isolated after flash chromatography", e, ["product"]),
                      fld("product_ee", qty(ee_value, "%"), e, ["product"])],
                     ["Reaction atmosphere is not reported.", "Product structure and stereochemistry require independent structure review."],
                     ["The Cu(OTf)2/ligand solution was pre-stirred at room temperature for 1 h before the reactants were added at 0 °C."])
        rec["steps"].insert(0, {"step_id": "catalyst_preformation", "participant_ids": ["cu_otf2", "ligand", "dcm"],
                                "conditions": [fld("temperature", "room temperature", e), fld("time", qty(1, "h"), e)]})
    else:
        rec = record(rid, "reported_experiment", e, participants,
                     [fld("temperature", None, ()), fld("time", None, ()), fld("atmosphere", None, ()),
                      fld("workup", None, ()), fld("purification", None, ())],
                     [fld("isolated_yield", qty(yld, "%"), e, ["product"]), fld("yield_measurement_basis", "isolated yield", e, ["product"]),
                      fld("product_ee", qty(ee_value, "%"), e, ["product"])],
                     ["This compound-specific paragraph does not restate reaction time, temperature, atmosphere, workup, or purification.",
                      "Product structure and stereochemistry require independent structure review."])
    records.append(rec)


records_path = BASE / "raw_model" / "records_pages_0001_0006.json"
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
by_prefix = lambda prefix: [i for i in ids if prefix in i]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, and introduction", "finding": "No reaction arrow or experiment table; abstract summarizes the present Pd-catalyzed cyclizations and introduction cites prior work without enough row-level detail for present-paper experiment records.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            {"region": "supporting-information availability statement", "finding": "SI is mentioned as available online, but no SI file is supplied or explicitly associated; no SI facts were imported.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
        ], "record_ids": [], "unresolved": ["No supporting-information association is established."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "Table 1 and ligand drawings", "finding": "Five independent optimization experiments extracted, including solvent overrides and all yield/ee/dr values.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "Table 2 and common reaction arrow/footnotes", "finding": "All ten substrate-scope rows extracted independently; common catalyst, ligand, Ag3PO4, solvent, temperature, time, and footnote overrides applied only to their rows.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "discussion prose", "finding": "Narrative claims and standard-condition definition used as cross-page context, without creating duplicate experiments.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
        ], "record_ids": by_prefix("table1_") + by_prefix("table2_"), "unresolved": ["Complex drawn structures and ligand stereochemistry remain unverified."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "Table 3 and control-experiment discussion", "finding": "Table 3 entry 1 merged with Table 2 entry 1; entries 2–4 extracted as three distinct match/mismatch experiments.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "Table 4", "finding": "Measured HPLC integrations merged into their underlying experiments; predicted rows 3 and 5 retained as predicted outcomes of later measured entries 4 and 6, not promoted to experiments.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "narrative around Table 4", "finding": "No-racemization statement and prediction-versus-measurement discussion retained as context; conflicting narrative/table ee values preserved.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
        ], "record_ids": [i for i in ids if "table2_entry1_" in i or "table3_" in i or "table4_" in i], "unresolved": ["Page 3 narrative reports 92% ee for one trans product while Table 3 and page 6 report 94% ee."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "Scheme 1", "finding": "Two prediction/measurement comparisons mapped to the rac-1a and 84% ee (R)-1a experiments; predicted values kept separate from measured values.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "allenylhydrazine preparation paragraphs", "finding": "Four distinct preparations extracted for (R)-1a, (S)-1a, (R)-1b, and (R)-1c; only explicitly restated conditions assigned to each.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "general catalyst and pyrazolidine procedures plus 3aa/3ab paragraphs", "finding": "General conditions merged into applicable scope rows; exact 3aa and first 3ab experiment data merged with Table 2 rows rather than duplicated.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
        ], "record_ids": by_prefix("prep_") + [i for i in ids if "table2_entry1_" in i or "table2_entry2_" in i or "table4_" in i], "unresolved": ["The experimental section calls the named Bn-Box ligand L1, conflicting with the ligand numbering in Table 1/2."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "3ab dioxane experiment and 3ac–3af preparations", "finding": "Table 2 entries 3–7 enriched with exact masses, amounts, solvent volumes, isolated masses, yields, dr, and ee values.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "bromophenyl product and 3ba/3ca preparations", "finding": "Table 2 entries 8–10 enriched; code and yield discrepancies retained rather than silently resolved.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
        ], "record_ids": [i for i in ids if any(f"table2_entry{n}_" in i for n in range(2, 11))], "unresolved": ["Table 2 versus experimental yields conflict for entries 5 and 7.", "Bromophenyl product is variously labeled 3ag, 3ah, and 3af."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "continuation of 3ca characterization", "finding": "Continuation linked to Table 2 entry 10; no new reaction created.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "Table 3 entries 2–4 experimental paragraphs", "finding": "Exact control-experiment quantities, isolated masses/yields, dr, and chiral-HPLC ee results merged into the three Table 3 records.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "Table 4 entries 4 and 6 experimental paragraphs", "finding": "Actual rac-1a and 84% ee (R)-1a experiments merged with page 3 Table 4 and page 4 Scheme 1 evidence.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "acknowledgements and references", "finding": "No present-paper reaction experiment extracted from acknowledgements or cited literature.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
        ], "record_ids": [i for i in ids if "table2_entry10_" in i or "table3_" in i or "table4_" in i], "unresolved": ["Several stereoisomer labels and ligand labels in the experimental prose are internally inconsistent."]},
    ],
}
coverage_path = BASE / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"].endswith(":text"):
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
        if 1 <= page <= 6:
            task["state"] = "attempted"
            task["reason"] = "Original page image and page text inspected; records and page regions logged in coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"]), "record_file": str(records_path)}, ensure_ascii=False))
