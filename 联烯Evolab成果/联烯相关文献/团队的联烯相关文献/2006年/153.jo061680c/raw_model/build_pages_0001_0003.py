#!/usr/bin/env python3
"""Build raw, evidence-linked extraction records for source PDF pages 1--3."""
import json
from pathlib import Path

DOC = "doc_51e51d934bac3530"
P1I, P1T = f"{DOC}:page1:image", f"{DOC}:page1:text"
P2I, P2T = f"{DOC}:page2:image", f"{DOC}:page2:text"
P3I, P3T = f"{DOC}:page3:image", f"{DOC}:page3:text"


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, ev, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def participant(entity_id, role, label, name, ev, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(smiles, ev) if smiles else fact(None, ev),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, ev, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(ev),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def base_compounds(ev, substrate_amount=None, phsecl_equiv=None, solvent_volume=None,
                   solvent_name="acetonitrile", include_products=True):
    parts = []
    sub_amounts = [] if substrate_amount is None else [field("amount", qty(substrate_amount, "mmol"), ev)]
    parts.append(participant(
        "substrate_1a", "reactant", "1a", "2,3-allenoate 1a (R1=n-C4H9, R2=CH3)", ev,
        "CCOC(=O)C(C)=C=CCCCC", sub_amounts,
    ))
    ph_amounts = [] if phsecl_equiv is None else [field("equivalents", qty(phsecl_equiv, "equiv"), ev)]
    parts.append(participant(
        "phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev,
        "Cl[Se]c1ccccc1", ph_amounts,
    ))
    solv_amounts = [] if solvent_volume is None else [field("volume", qty(solvent_volume, "mL"), ev)]
    parts.append(participant("mecn", "solvent", "CH3CN", solvent_name, ev, "CC#N", solv_amounts))
    if include_products:
        parts.extend([
            participant(
                "product_2a", "product", "2a",
                "ethyl 2-methyl-4-oxo-3-(phenylselanyl)oct-2(E)-enoate", ev,
                "CCOC(=O)C(C)=C([Se]c1ccccc1)C(=O)CCCC",
            ),
            participant(
                "product_3a", "product", "3a", "phenylseleno-substituted butenolide 3a", ev,
                "CCCCC1OC(=O)C(C)=C1[Se]c1ccccc1",
            ),
        ])
    return parts


def add_lithium_carbonate(parts, ev, equivalents=None, mass=None, amount=None):
    amounts = []
    if equivalents is not None:
        amounts.append(field("equivalents", qty(equivalents, "equiv"), ev))
    if mass is not None:
        amounts.append(field("mass", qty(mass, "mg"), ev))
    if amount is not None:
        amounts.append(field("amount", qty(amount, "mmol"), ev))
    parts.append(participant(
        "li2co3", "reagent", "Li2CO3", "lithium carbonate", ev,
        "[Li+].[Li+].[O-]C([O-])=O", amounts,
    ))


def add_water(parts, ev, equivalents):
    parts.append(participant(
        "water", "reagent", "H2O", "water", ev, "O",
        [field("equivalents", qty(equivalents, "equiv"), ev)],
    ))


records = []

# Page 1 graphical abstract: generic scope summary, not an extra reported experiment.
ev = [P1I, P1T]
parts = [
    participant("generic_allenoate", "reactant", "2,3-allenoate", "generic 2,3-allenoate (R1/R2 variable)", ev),
    participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev, "Cl[Se]c1ccccc1",
                [field("equivalents", qty(2.0, "equiv"), ev)]),
    participant("li2co3", "reagent", "Li2CO3", "lithium carbonate", ev,
                "[Li+].[Li+].[O-]C([O-])=O", [field("equivalents", qty(3.0, "equiv"), ev)]),
    participant("mecn", "solvent", "CH3CN", "acetonitrile", ev, "CC#N"),
    participant("generic_product_2", "product", "2", "generic 3-phenylseleno-4-oxo-2(E)-alkenoate", ev),
]
records.append(record(
    "graphical_abstract_general_scheme", "general_scheme", ev, parts,
    [{"step_id": "reaction", "participant_ids": ["generic_allenoate", "phsecl", "li2co3", "mecn"],
      "conditions": [field("temperature", "r.t.", ev), field("reaction_time", qty(1, "h"), ev)]}],
    [field("reported_yield_range", {"minimum": 63, "maximum": 93, "unit": "%", "raw_text": "63-93%"}, ev,
           ["generic_product_2"]), field("yield_measurement_basis", None, ev, ["generic_product_2"])],
    unresolved=["Generic R1/R2 structures are not expanded.", "The graphical abstract does not state the yield measurement basis."],
))

# Scheme 1: present work preliminary reaction and explicitly cited prior work.
parts = base_compounds(ev, phsecl_equiv=2.0)
records.append(record(
    "scheme1_mechcn_preliminary", "reported_experiment", ev, parts,
    [{"step_id": "reaction", "participant_ids": ["substrate_1a", "phsecl", "mecn"], "conditions": []}],
    [field("reported_yield_2a", qty(55, "%"), ev, ["product_2a"]),
     field("reported_yield_3a", qty(17, "%"), ev, ["product_3a"]),
     field("yield_measurement_basis", None, ev, ["product_2a", "product_3a"])],
    unresolved=["Reaction time, temperature, atmosphere, scale, and yield measurement basis are not stated in Scheme 1."],
))
parts = base_compounds(ev, phsecl_equiv=2.0, include_products=False)
parts[2]["name"] = fact("acetonitrile/water (10:1)", ev)
parts.append(participant("product_3a", "product", "3a", "phenylseleno-substituted butenolide 3a", ev,
                         "CCCCC1OC(=O)C(C)=C1[Se]c1ccccc1"))
records.append(record(
    "scheme1_ref7_aqueous", "literature_example", ev, parts,
    [{"step_id": "reaction", "participant_ids": ["substrate_1a", "phsecl", "mecn"],
      "conditions": [field("solvent_ratio", "CH3CN/H2O = 10:1", ev)]}],
    [field("reported_yield_3a", qty(100, "%"), ev, ["product_3a"]),
     field("yield_measurement_basis", None, ev, ["product_3a"])],
    notes=["Scheme 1 labels this transformation as ref. 7; it is prior literature, not a new experiment in this paper."],
    unresolved=["Reaction time, temperature, atmosphere, scale, and yield measurement basis are not stated."],
))


# Page 2 Table 1: every optimization row is separate.
table1 = [
    (1, 2.5, "air", 45, 0.2, 4, 29, 5, "85:15", None),
    (2, 2.5, "air", "r.t.", 0.2, 4, 64, 15, "81:19", None),
    (3, 2.5, "air", -35, 0.2, 4, 61, 36, "63:37", None),
    (4, 2.5, "N2", "r.t.", 0.2, 4, 31, 17, "65:35", None),
    (5, 2.5, "N2", "r.t.", 0.2, 4, 54, 15, "78:22", 0.5),
    (6, 2.5, "N2", "r.t.", 0.2, 4, 62, 16, "79:21", 1.0),
    (7, 2.5, "O2", "r.t.", 0.2, 4, 42, 5, "89:11", None),
    (8, 2.0, "air", "r.t.", 0.2, 4, 55, 17, "76:24", None),
    (9, 3.0, "air", "r.t.", 0.2, 4, 61, 4, "94:6", None),
    (10, 3.5, "air", "r.t.", 0.2, 4, 62, 4, "94:6", None),
    (11, 2.5, "air", "r.t.", 0.8, 4, 15, 19, "44:56", None),
    (12, 3.0, "air", "r.t.", 0.2, 6, 71, 4, "95:5", None),
    (13, 3.0, "air", "r.t.", 0.2, 16, 72, 3, "96:4", None),
]
ev2 = [P2I, P2T]
for entry, ph_eq, atm, temp, sub_mmol, volume, y2, y3, ratio, water_eq in table1:
    parts = base_compounds(ev2, sub_mmol, ph_eq, volume, "acetonitrile (distilled once from CaH2)")
    if water_eq is not None:
        add_water(parts, ev2, water_eq)
    if entry in (12, 13):
        parts.append(participant("mesitylene", "unspecified_agent", "mesitylene", "mesitylene (1H NMR internal standard)",
                                 ev2, "Cc1cc(C)cc(C)c1"))
    ids = ["substrate_1a", "phsecl", "mecn"] + (["water"] if water_eq is not None else [])
    conditions = [field("atmosphere", "open air" if atm == "air" else
                        ("N2 (air carefully removed)" if atm == "N2" else "O2"), ev2),
                  field("temperature", temp if isinstance(temp, str) else qty(temp, "°C"), ev2),
                  field("reaction_time", qty(1, "h"), ev2)]
    basis = "1H NMR yield using mesitylene as internal standard" if entry in (12, 13) else "isolated yield"
    records.append(record(
        f"table1_entry{entry:02d}", "optimization_entry", ev2, parts,
        [{"step_id": "reaction", "participant_ids": ids, "conditions": conditions}],
        [field("yield_2a", qty(y2, "%"), ev2, ["product_2a"]),
         field("yield_3a", qty(y3, "%"), ev2, ["product_3a"]),
         field("product_ratio_2a_to_3a", ratio, ev2, ["product_2a", "product_3a"]),
         field("yield_measurement_basis", basis, ev2, ["product_2a", "product_3a"])],
        unresolved=["Workup and purification are not reported for this optimization row."],
    ))


# Page 2 Table 2.
additives = {
    "Na2CO3": ("sodium carbonate", "[Na+].[Na+].[O-]C([O-])=O"),
    "K2CO3": ("potassium carbonate", "[K+].[K+].[O-]C([O-])=O"),
    "Cs2CO3": ("cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O"),
    "LiOH": ("lithium hydroxide", "[Li+].[OH-]"),
    "LiOAc": ("lithium acetate", "[Li+].CC(=O)[O-]"),
    "Li2CO3": ("lithium carbonate", "[Li+].[Li+].[O-]C([O-])=O"),
}
table2 = [
    (1, 3.0, "Na2CO3", 3.0, 80, 5, "94:6"),
    (2, 3.0, "K2CO3", 3.0, 80, 11, "88:12"),
    (3, 3.0, "Cs2CO3", 3.0, 79, 5, "94:6"),
    (4, 3.0, "LiOH", 3.0, 84, 6, "93:7"),
    (5, 3.0, "LiOAc", 3.0, 87, 4, "95:5"),
    (6, 3.0, "Li2CO3", 3.0, 87, 3, "97:3"),
    (7, 2.0, "Li2CO3", 3.0, 84, 3, "97:3"),
    (8, 1.5, "Li2CO3", 3.0, 67, 3, "94:6"),
    (9, 2.0, "Li2CO3", 2.5, 82, 5, "94:6"),
]
for entry, ph_eq, additive, add_eq, y2, y3, ratio in table2:
    parts = base_compounds(ev2, 0.2, ph_eq, 6)
    add_name, add_smiles = additives[additive]
    parts.append(participant("additive", "reagent", additive, add_name, ev2, add_smiles,
                             [field("equivalents", qty(add_eq, "equiv"), ev2)]))
    parts.append(participant("mesitylene", "unspecified_agent", "mesitylene", "mesitylene (1H NMR internal standard)",
                             ev2, "Cc1cc(C)cc(C)c1"))
    records.append(record(
        f"table2_entry{entry:02d}", "optimization_entry", ev2, parts,
        [{"step_id": "reaction", "participant_ids": ["substrate_1a", "phsecl", "additive", "mecn"],
          "conditions": [field("atmosphere", "open air", ev2), field("temperature", "r.t.", ev2),
                         field("reaction_time", qty(1, "h"), ev2)]}],
        [field("nmr_yield_2a", qty(y2, "%"), ev2, ["product_2a"]),
         field("nmr_yield_3a", qty(y3, "%"), ev2, ["product_3a"]),
         field("product_ratio_2a_to_3a", ratio, ev2, ["product_2a", "product_3a"]),
         field("yield_measurement_basis", "1H NMR analysis using mesitylene as internal standard", ev2,
               ["product_2a", "product_3a"])],
        unresolved=["Workup and purification are not reported for this optimization row."],
    ))


# Page 2 Table 3 scope. Candidate SMILES encode connectivity but not reported E stereochemistry.
scope = [
    (1, "a", "n-C4H9", "CH3", 2.0, 1, "97:3", 77),
    (2, "b", "n-C4H9", "n-C3H7", 2.0, 48, None, 68),
    (3, "c", "n-C4H9", "Bn", 2.0, 48, "97:3", 67),
    (4, "d", "n-C7H15", "CH3", 2.0, 1, None, 67),
    (5, "e", "n-C7H15", "n-C3H7", 2.0, 1, None, 63),
    (6, "f", "Ph", "CH3", 2.0, 1, "97:3", 77),
    (7, "g", "Ph", "n-C3H7", 3.0, 1, ">99:1", 82),
    (8, "h", "Ph", "Bn", 2.0, 1, ">99:1", 77),
    (9, "i", "p-BrC6H4", "CH3", 2.0, 1, "97:3", 63),
    (10, "j", "p-BrC6H4", "n-C3H7", 3.0, 1, "99:1", 85),
    (11, "k", "alpha-naphthyl", "CH3", 3.0, 1, "98:2", 93),
    (12, "l", "alpha-naphthyl", "n-C3H7", 3.0, 1, "97:3", 89),
]
r1_sub = {"n-C4H9": "CCCC", "n-C7H15": "CCCCCCC", "Ph": "c1ccccc1",
          "p-BrC6H4": "c1ccc(Br)cc1", "alpha-naphthyl": "c1cccc2ccccc12"}
r2_sub = {"CH3": "C", "n-C3H7": "CCC", "Bn": "Cc1ccccc1"}
r1_prod = {"n-C4H9": "CCCC", "n-C7H15": "CCCCCCC", "Ph": "c2ccccc2",
           "p-BrC6H4": "c2ccc(Br)cc2", "alpha-naphthyl": "c2cccc3ccccc23"}
r2_prod = {"CH3": "C", "n-C3H7": "CCC", "Bn": "Cc2ccccc2"}
for entry, letter, r1, r2, ph_eq, hours, ratio, isolated_yield in scope:
    label1, label2, label3 = f"1{letter}", f"2{letter}", f"3{letter}"
    sub_smiles = f"CCOC(=O)C({r2_sub[r2]})=C=C({r1_sub[r1]})"
    p2_smiles = f"CCOC(=O)C({r2_prod[r2]})=C([Se]c1ccccc1)C(=O){r1_prod[r1]}"
    p3_smiles = f"O=C1OC({r1_prod[r1]})C([Se]c4ccccc4)=C1{r2_prod[r2]}"
    row_ev = [P2I, P2T] + ([P3I, P3T] if entry == 1 else [])
    parts = [
        participant("substrate", "reactant", label1, f"2,3-allenoate {label1} (R1={r1}, R2={r2})", row_ev,
                    sub_smiles, [field("amount", qty(0.2, "mmol"), row_ev)]),
        participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", row_ev, "Cl[Se]c1ccccc1",
                    [field("equivalents", qty(ph_eq, "equiv"), row_ev)]),
        participant("li2co3", "reagent", "Li2CO3", "lithium carbonate", row_ev,
                    "[Li+].[Li+].[O-]C([O-])=O", [field("equivalents", qty(3.0, "equiv"), row_ev)]),
        participant("mecn", "solvent", "CH3CN", "acetonitrile", row_ev, "CC#N",
                    [field("volume", qty(6, "mL"), row_ev)]),
        participant("product_2", "product", label2,
                    f"3-phenylseleno-4-oxo-2(E)-alkenoate {label2} (R1={r1}, R2={r2})", row_ev, p2_smiles),
        participant("product_3", "product", label3, f"phenylseleno-substituted butenolide {label3}", row_ev, p3_smiles),
        participant("mesitylene", "unspecified_agent", "mesitylene", "mesitylene (1H NMR internal standard)",
                    row_ev, "Cc1cc(C)cc(C)c1"),
    ]
    conditions = [field("atmosphere", "open air", row_ev), field("temperature", "r.t.", row_ev),
                  field("reaction_time", qty(hours, "h"), row_ev)]
    outcomes = [
        field("isolated_yield_product_2", qty(isolated_yield, "%"), row_ev, ["product_2"]),
        field("yield_measurement_basis", "isolated yield", row_ev, ["product_2"]),
        field("butenolide_3_crude_formation", {"number": 4, "unit": "%", "qualifier": "lt", "raw_text": "less than 4%"},
              row_ev, ["product_3"]),
        field("byproduct_measurement_basis", "1H NMR analysis of the crude reaction mixture", row_ev, ["product_3"]),
    ]
    unresolved = ["Reactant mass and detailed workup/purification are not reported for this scope row.",
                  "Candidate SMILES do not encode the reported E geometry and remain unverified."]
    if ratio is None:
        outcomes.append(field("product_ratio_2_to_3", None, row_ev, ["product_2", "product_3"]))
        unresolved.append("The 2:3 ratio could not be determined because the 1H NMR signals overlapped.")
    else:
        outcomes.append(field("product_ratio_2_to_3", ratio, row_ev, ["product_2", "product_3"]))
        outcomes.append(field("ratio_measurement_basis", "1H NMR analysis using mesitylene as internal standard", row_ev,
                              ["product_2", "product_3"]))
    steps = [{"step_id": "reaction", "participant_ids": ["substrate", "phsecl", "li2co3", "mecn"],
              "conditions": conditions}]
    if entry == 1:
        # The page-3 typical procedure is the same 1a -> 2a scope experiment, so merge its details here.
        parts[0]["amounts"].append(field("mass", qty(35.6, "mg"), row_ev))
        parts[1]["amounts"].extend([field("mass", qty(79.3, "mg"), row_ev), field("amount", qty(0.41, "mmol"), row_ev)])
        parts[2]["amounts"].extend([field("mass", qty(45.0, "mg"), row_ev), field("amount", qty(0.61, "mmol"), row_ev)])
        parts[3]["amounts"] = [field("initial_volume", qty(5, "mL"), row_ev),
                               field("subsequent_volume", qty(1, "mL"), row_ev),
                               field("total_volume", qty(6, "mL"), row_ev)]
        steps = [
            {"step_id": "charge_reagents", "participant_ids": ["phsecl", "li2co3", "mecn"],
             "conditions": [field("operation", "Li2CO3 was added to a solution of PhSeCl in 5 mL MeCN", row_ev)]},
            {"step_id": "reaction", "participant_ids": ["substrate", "phsecl", "li2co3", "mecn"],
             "conditions": conditions + [field("operation", "1a and a further 1 mL MeCN were added; completion monitored by TLC", row_ev)]},
            {"step_id": "workup_and_purification", "participant_ids": ["product_2"],
             "conditions": [field("workup", "filtered through a short column of silica gel", row_ev),
                            field("operation", "crude product analyzed by 400 MHz 1H NMR", row_ev),
                            field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 40:1", row_ev)]},
        ]
        outcomes.extend([field("isolated_product_mass", qty(53.1, "mg"), row_ev, ["product_2"]),
                         field("physical_form", "liquid", row_ev, ["product_2"])])
        unresolved = ["The source does not explicitly quantify residual 3a in the isolated material.",
                      "Candidate SMILES do not encode the reported E geometry and remain unverified."]
    records.append(record(f"table3_entry{entry:02d}", "substrate_scope_entry", row_ev, parts, steps, outcomes,
                          unresolved=unresolved))


# Page 2 Scheme 2: distinct substrate 1m gives only lactone 3m.
parts = [
    participant("substrate_1m", "reactant", "1m", "2,4,4-trisubstituted 2,3-allenoate 1m", ev2),
    participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev2, "Cl[Se]c1ccccc1",
                [field("equivalents", qty(2.0, "equiv"), ev2)]),
    participant("li2co3", "reagent", "Li2CO3", "lithium carbonate", ev2,
                "[Li+].[Li+].[O-]C([O-])=O", [field("equivalents", qty(3.0, "equiv"), ev2)]),
    participant("mecn", "solvent", "CH3CN", "acetonitrile", ev2, "CC#N"),
    participant("product_3m", "product", "3m", "spiro phenylseleno-substituted butenolide 3m", ev2),
]
records.append(record(
    "scheme2_substrate_1m", "substrate_scope_entry", ev2, parts,
    [{"step_id": "reaction", "participant_ids": ["substrate_1m", "phsecl", "li2co3", "mecn"],
      "conditions": [field("temperature", "r.t.", ev2), field("reaction_time", qty(1, "h"), ev2)]}],
    [field("isolated_yield_3m", qty(88, "%"), ev2, ["product_3m"]),
     field("yield_measurement_basis", "isolated yield", ev2, ["product_3m"]),
     field("ketoenoate_2_formation", "not formed; only butenolide 3m was isolated", ev2)],
    unresolved=["Reaction scale, solvent volume, atmosphere, workup, and purification are not stated.",
                "The spiro structures of 1m and 3m were not converted to SMILES because ring connectivity/stereochemistry requires review."],
))


# Page 3 Table 4: each water-equivalent row is separate.
table4 = [(1, 0, 22, 7), (2, 1.0, 61, 11), (3, 1.5, 59, 20), (4, 2.5, 60, 25),
          (5, 10, 44, 44), (6, 50, 2, 91), (7, 111, 0, 94)]
ev3 = [P3I, P3T]
for entry, water_eq, y2, y3 in table4:
    parts = base_compounds(ev3, 0.2, 2.5, 4, "acetonitrile (double distilled from CaH2)")
    ids = ["substrate_1a", "phsecl", "mecn"]
    if water_eq:
        add_water(parts, ev3, water_eq)
        ids.append("water")
    conditions = [field("atmosphere", "N2", ev3), field("temperature", "r.t.", ev3),
                  field("reaction_time", qty(1, "h"), ev3)]
    if not water_eq:
        conditions.append(field("water_added", "none (0 equiv)", ev3))
    records.append(record(
        f"table4_entry{entry:02d}", "optimization_entry", ev3, parts,
        [{"step_id": "reaction", "participant_ids": ids, "conditions": conditions}],
        [field("isolated_yield_2a", qty(y2, "%"), ev3, ["product_2a"]),
         field("isolated_yield_3a", qty(y3, "%"), ev3, ["product_3a"]),
         field("yield_measurement_basis", "isolated yield", ev3, ["product_2a", "product_3a"])],
        unresolved=["Workup and purification are not reported for this optimization row."],
    ))


# Page 3: three distinct control experiments described in prose, all negative.
def control_part(entity_id, label, name, smiles, equivalents=None):
    amounts = [] if equivalents is None else [field("equivalents", qty(equivalents, "equiv"), ev3)]
    return participant(entity_id, "reagent", label, name, ev3, smiles, amounts)

for rid, extra_parts, participant_ids, note in [
    ("control_1_3a_phsecl", [control_part("phsecl", "PhSeCl", "phenylselenyl chloride", "Cl[Se]c1ccccc1")],
     ["substrate_3a", "phsecl", "mecn"], "Compound 3a was stable in a CH3CN solution of PhSeCl."),
    ("control_2_3a_phsecl_ethanol", [control_part("phsecl", "PhSeCl", "phenylselenyl chloride", "Cl[Se]c1ccccc1"),
                                      control_part("ethanol", "EtOH", "ethanol", "CCO", 1.5)],
     ["substrate_3a", "phsecl", "ethanol", "mecn"], "Compound 3a remained stable when EtOH was added; its amount is structured on the participant."),
    ("control_3_3a_ethanol_hcl", [control_part("ethanol", "EtOH", "ethanol", "CCO", 1.0),
                                  control_part("hcl", "HCl", "hydrogen chloride", "Cl", 1.0)],
     ["substrate_3a", "ethanol", "hcl", "mecn"], "No reaction occurred with EtOH and HCl; both amounts are structured on their participants."),
]:
    parts = [
        participant("substrate_3a", "reactant", "3a", "phenylseleno-substituted butenolide 3a", ev3,
                    "CCCCC1OC(=O)C(C)=C1[Se]c1ccccc1"),
        participant("mecn", "solvent", "CH3CN", "acetonitrile", ev3, "CC#N"),
    ] + extra_parts
    records.append(record(
        rid, "reported_experiment", ev3, parts,
        [{"step_id": "control_exposure", "participant_ids": participant_ids, "conditions": []}],
        [field("reaction_result", "no reaction / starting 3a stable", ev3, ["substrate_3a"])],
        notes=[note], unresolved=["Reagent amounts not shown remain unknown; reaction time and temperature are not reported."],
    ))


# Page 3 Scheme 3: proposed pathway, classified as mechanism rather than experiment.
parts = [
    participant("generic_1", "reactant", "1", "generic 2,3-allenoate 1 (R1/R2 variable)", ev3),
    participant("phsecl", "reagent", "PhSeCl", "phenylselenyl chloride", ev3, "Cl[Se]c1ccccc1"),
    participant("water", "reagent", "H2O", "water", ev3, "O"),
    participant("base", "unspecified_agent", "base", "base (Li2CO3 discussed in prose)", ev3),
    participant("intermediate_4", "unspecified_agent", "4", "seleniranium-like intermediate 4", ev3),
    participant("intermediate_5", "unspecified_agent", "5", "hydroxy intermediate 5", ev3),
    participant("intermediate_6", "unspecified_agent", "6", "selenate intermediate 6", ev3),
    participant("intermediate_7", "unspecified_agent", "7", "cyclization intermediate 7", ev3),
    participant("generic_2", "product", "2", "generic 3-phenylseleno-4-oxo-2(E)-alkenoate 2", ev3),
    participant("generic_3", "product", "3", "generic phenylseleno-substituted butenolide 3", ev3),
]
steps = [
    {"step_id": "electrophilic_addition", "participant_ids": ["generic_1", "phsecl", "intermediate_4"], "conditions": []},
    {"step_id": "ketoenoate_branch_hydration", "participant_ids": ["intermediate_4", "water", "base", "intermediate_5"], "conditions": []},
    {"step_id": "ketoenoate_branch_selenate", "participant_ids": ["intermediate_5", "phsecl", "base", "intermediate_6"], "conditions": []},
    {"step_id": "ketoenoate_branch_decomposition", "participant_ids": ["intermediate_6", "generic_2"],
     "conditions": [field("operation", "selenate decomposition (ref. 10); oxygen may promote elimination", ev3)]},
    {"step_id": "lactone_branch", "participant_ids": ["intermediate_4", "water", "intermediate_7", "generic_3"], "conditions": []},
]
records.append(record(
    "scheme3_proposed_mechanism", "mechanism", ev3, parts, steps, [],
    notes=["The authors present this as a rationale; intermediates 4-7 are proposed, not isolated experiments.",
           "Large amounts of water are proposed to stabilize charged intermediates and favor lactonization."],
    unresolved=["The real role of water is explicitly stated to remain under study.",
                "Generic R1/R2 intermediate structures and charges were not converted to SMILES."],
))


out = Path(__file__).with_name("pages_0001_0003_records.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(out), "records": len(records)}, ensure_ascii=False))
