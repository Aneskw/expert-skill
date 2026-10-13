import json
from pathlib import Path

DOC = "doc_34a38cb1c5b4d3e7"
ROOT = Path(__file__).resolve().parents[1]


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


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
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(None, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(name, value, evidence):
    return field(name, value, evidence)


def record(suffix, kind, evidence, participants, conditions, outcomes, notes=None,
           unresolved=None, source_id=None):
    rid = f"{DOC}:{suffix}"
    return {
        "record_id": rid,
        "document_id": DOC,
        "source_reaction_id": source_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if conditions or participants else [],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record requires source review; structures are unverified."
            ],
        },
    }


records = []

# Table 1: each solvent/time row is an independent optimization experiment.
t1 = [
    (1, "CH2Cl2", 3.5, 41, None),
    (2, "CH3NO2", 1.2, 62, None),
    (3, "toluene", 30.2, 75, None),
    (4, "ethyl acetate", 30.4, 82, None),
    (5, "MeCN", 12, 82, None),
    (6, "MeCN/H2O = 40/1", 0.65, 92, None),
    (7, "MeCN/H2O = 20/1", 0.25, 96, None),
    (8, "MeCN/H2O = 10/1", 0.6, 87, None),
    (9, "MeCN/H2O = 5/1", 12, 80, None),
    (10, "MeCN/H2O = 20/1", 0.6, 84, "PhSeCl 1.2 equiv"),
    (11, "acetone/H2O = 20/1", 44.5, 0, "1a recovered 91%"),
    (12, "THF/H2O = 20/1", 16, 90, None),
    (13, "EtOH/H2O = 20/1", 28, 82, None),
    (14, "DMF/H2O = 20/1", 17, 85, None),
]
for entry, solvent, hours, yld, special in t1:
    e = ev(1, 2) if entry in (1, 2) else ev(2)
    phse_amounts = [amount("equivalents", qty(1.2 if entry == 10 else 1.5, "equiv"), e)]
    if entry != 10:
        phse_amounts.append(amount("amount", qty(0.3, "mmol"), e))
    ps = [
        participant("1a", "reactant", "1a", e, [amount("amount", qty(0.2, "mmol"), e)]),
        participant("phsecl", "reagent", "PhSeCl", e, phse_amounts, "Cl[Se]c1ccccc1"),
        participant("solvent", "solvent", solvent, e,
                    [amount("volume", qty(4.0, "mL"), e)] if "/H2O" not in solvent else []),
        participant("E-2a", "product", "E-2a", e),
    ]
    outcomes = [
        field("NMR_yield_E-2a", qty(yld, "%"), e, ["E-2a"]),
        field("yield_measurement_basis", "NMR yield based on 1a using CH2Br2 as internal standard", e),
    ]
    notes = []
    if special:
        notes.append(special)
    if entry == 11:
        outcomes.append(field("recovered_starting_material_yield", qty(91, "%"), e, ["1a"]))
        notes.append("No reaction was observed; 1a was recovered.")
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", e, ps,
        [field("temperature", "r.t.", e), field("time", qty(hours, "h"), e),
         field("solvent", solvent, e)], outcomes, notes,
        ["Water volume is not separately reported for mixed-solvent rows.",
         "Substrate and product structures require source verification."]
    ))

# Table 2 substrate scope. Page 6 details enrich entries 1 and 2 without creating duplicates.
t2 = [
    (1, "1a", "2a", "Ph", "H", "n-C5H11", 14, 91, None),
    (2, "1b", "2b", "H", "H", "Me", 12, 82, None),
    (3, "1c", "2c", "H", "H", "Ph", 28, 85, None),
    (4, "1d", "2d", "H", "Me", "Me", 19, 89, None),
    (5, "1e", "2e", "H", "n-Pr", "n-Pr", 18, 80, None),
    (6, "1f", "2f", "H", "(CH2)5", "cyclic", 10, 84, None),
    (7, "1g", "2g", "n-C4H9", "H", "H", 16, 67, None),
    (8, "1h", "2h", "Ph", "H", "H", 14, 80, None),
    (9, "1i", "2i", "Et", "H", "Me", 10, 90, None),
    (10, "1j", "2j", "Ph", "H", "Et", 5, 88, None),
    (11, "1k", "2k", "n-C4H9", "Me", "Me", 10, 65, None),
    (12, "1l", "2l", "H", "H", "i-Pr", 20, 76, ("3l", 7)),
    (13, "1m", "2m", "H", "H", "H", 16, 13, ("3m", 61.5)),
    (14, "1n", "2n", "H", "H", "Et", 20, 82.5, ("3n", 6)),
    (15, "1o", "2o", "H", "H", "n-C6H13", 30, 64, ("3o", 6)),
    (16, "1p", "2p", "H", "H", "Bn", 15, 64, ("3p", 14)),
]
for entry, substrate, product, r1, r2, r3, minutes, yld, byproduct in t2:
    pages = [2]
    if entry == 1:
        pages.append(6)
    if entry == 2:
        pages.append(6)
    if entry == 8:
        pages.extend([3, 4])
    e = ev(*pages)
    sub_amounts = [amount("amount", qty(0.3, "mmol"), e)]
    phse_amounts = [amount("amount", qty(0.45, "mmol"), e), amount("equivalents", qty(1.5, "equiv"), e)]
    if entry == 1:
        sub_amounts = [amount("mass", qty(77.7, "mg"), e), amount("amount", qty(0.2, "mmol"), e)]
        phse_amounts = [amount("mass", qty(58.1, "mg"), e), amount("amount", qty(0.3, "mmol"), e), amount("equivalents", qty(1.5, "equiv"), e)]
    if entry == 2:
        sub_amounts += [amount("mass", qty(77.0, "mg"), e)]
        phse_amounts += [amount("mass", qty(87.1, "mg"), e)]
    ps = [
        participant(substrate, "reactant", substrate, e, sub_amounts),
        participant("phsecl", "reagent", "PhSeCl", e, phse_amounts, "Cl[Se]c1ccccc1"),
        participant("mecn", "solvent", "MeCN", e, [amount("volume", qty(6.0 if entry != 1 else 4.0, "mL"), e)], "CC#N"),
        participant("water", "solvent", "H2O", e, [amount("volume", qty(0.3 if entry != 1 else 0.2, "mL"), e)], "O"),
        participant(f"E-{product}", "product", f"E-{product}", e),
    ]
    outcomes = [
        field(f"isolated_yield_E-{product}", qty(yld, "%"), e, [f"E-{product}"]),
        field("yield_measurement_basis", "isolated yield", e),
    ]
    if entry == 1:
        outcomes.append(field("isolated_product_mass", qty(102.3, "mg"), e, ["E-2a"]))
    if byproduct:
        bp, bpyld = byproduct
        ps.append(participant(f"Z-{bp}", "product", f"Z-{bp}", e))
        outcomes.append(field(f"isolated_yield_Z-{bp}", qty(bpyld, "%"), e, [f"Z-{bp}"]))
    notes = [f"Table substituents: R1={r1}, R2={r2}, R3={r3}."]
    if entry == 1:
        notes.append("General Procedure III workup: water quench, ether extraction, brine wash, Na2SO4 drying, evaporation, and silica chromatography (petroleum ether/ethyl acetate 3:1 to 2:1).")
    if entry == 8:
        notes.append("Figures 3 and the adjacent discussion report ESI-MS/MS [M+H]+ m/z 491 to daughter m/z 473 for E-2h.")
    records.append(record(
        f"table2_entry{entry}_{product}", "substrate_scope_entry", e, ps,
        [field("temperature", "r.t.", e), field("time", qty(minutes, "min"), e),
         field("solvent", "MeCN/H2O = 20/1", e)], outcomes, notes,
        ["SMILES for the allene substrate and selenium-containing products are not source-verified.",
         "Atmosphere is not reported for the scope experiment."]
    ))

# Scheme 1: sequential tosylation and chlorination are separate reported stages.
e = ev(2)
records.append(record(
    "scheme1_tosylation_E-2o_to_E-4o", "reported_experiment", e,
    [participant("E-2o", "reactant", "E-2o", e), participant("tscl", "reagent", "TsCl", e),
     participant("dmap", "reagent", "DMAP", e), participant("ch2cl2", "solvent", "CH2Cl2", e, smiles="ClCCl"),
     participant("E-4o", "product", "E-4o", e)],
    [field("temperature", qty(50, "°C"), e), field("time", None, e), field("solvent", "CH2Cl2", e)],
    [field("isolated_yield_E-4o", qty(86, "%"), e, ["E-4o"])],
    unresolved=["Scheme 1 does not report quantities, time, atmosphere, workup, or purification on page 2.", "Structures require review."]
))
records.append(record(
    "scheme1_chlorination_E-4o_to_E-3o", "reported_experiment", e,
    [participant("E-4o", "reactant", "E-4o", e), participant("licl", "reagent", "LiCl", e),
     participant("dmf", "solvent", "DMF", e, smiles="CN(C)C=O"), participant("E-3o", "product", "E-3o", e)],
    [field("temperature", qty(50, "°C"), e), field("time", None, e), field("solvent", "DMF", e)],
    [field("isolated_yield_E-3o", qty(60, "%"), e, ["E-3o"])],
    unresolved=["Scheme 1 does not report quantities, time, atmosphere, workup, or purification on page 2.", "Structures require review."]
))

# Table 3 optimization. Entry 6 is the same batch summarized as Table 4 entry 1.
t3 = [
    (1, "20/1", "r.t.", 0.50, 64, "90/10"),
    (2, "10/1", "r.t.", 0.37, 76, "91/9"),
    (3, "5/1", "r.t.", 0.60, 84, "94/6"),
    (4, "2/1", "r.t.", 13.4, 89, "97/3"),
    (5, "1/1", "r.t.", 65.7, 77, "98/2"),
    (6, "2/1", qty(70, "°C"), 0.57, 82, "97/3"),
]
for entry, ratio, temp, hours, yld, selectivity in t3:
    e = ev(3)
    ps = [participant("1l", "reactant", "1l", e),
          participant("phsecl", "reagent", "PhSeCl", e, [amount("equivalents", qty(1.5, "equiv"), e)], "Cl[Se]c1ccccc1"),
          participant("mecn_water", "solvent", f"MeCN/H2O = {ratio}", e),
          participant("E-2l", "product", "E-2l", e), participant("Z-3l", "product", "Z-3l", e)]
    conditions = [field("temperature", temp, e), field("time", qty(hours, "h"), e), field("solvent", f"MeCN/H2O = {ratio}", e)]
    notes = []
    suffix = f"table3_entry{entry}"
    if entry == 6:
        conditions.append(field("time_reported_in_table4", qty(34, "min"), e))
        notes.append("The same batch is repeated as Table 4 entry 1; it is not duplicated as a second experiment.")
        suffix = "table3_entry6_table4_entry1"
    records.append(record(
        suffix, "optimization_entry", e, ps, conditions,
        [field("NMR_yield_E-2l", qty(yld, "%"), e, ["E-2l"]),
         field("E-2l_to_Z-3l_ratio", selectivity, e, ["E-2l", "Z-3l"]),
         field("yield_measurement_basis", "NMR yield based on 1l using CH2Br2 as internal standard", e),
         field("ratio_measurement_basis", "1H NMR analysis of crude product", e)], notes,
        ["Participant quantities and workup are absent from Table 3.", "Structures require review."]
    ))

# Table 4 entries 2-5 (entry 1 already merged above).
t4 = [
    (2, "1m", "2m", "3m", "H", 540, 52.5, "79/21", "1/1"),
    (3, "1n", "2n", "3n", "Et", 21, 78, ">99/1", "2/1"),
    (4, "1o", "2o", "3o", "n-C6H13", 70, 74, "98/2", "1/1"),
    (5, "1p", "2p", "3p", "Bn", 105, 77, "96.5/3.5", "2/1"),
]
for entry, substrate, prod, bp, r3, minutes, yld, ratio, solvent_ratio in t4:
    e = ev(3)
    ps = [participant(substrate, "reactant", substrate, e),
          participant("phsecl", "reagent", "PhSeCl", e, [amount("equivalents", qty(1.5, "equiv"), e)], "Cl[Se]c1ccccc1"),
          participant("solvent", "solvent", f"MeCN/H2O = {solvent_ratio}", e),
          participant(f"E-{prod}", "product", f"E-{prod}", e), participant(f"Z-{bp}", "product", f"Z-{bp}", e)]
    records.append(record(
        f"table4_entry{entry}_{prod}", "substrate_scope_entry", e, ps,
        [field("temperature", qty(70, "°C"), e), field("time", qty(minutes, "min"), e),
         field("solvent", f"MeCN/H2O = {solvent_ratio}", e)],
        [field(f"isolated_yield_E-{prod}", qty(yld, "%"), e, [f"E-{prod}"]),
         field(f"E-{prod}_to_Z-{bp}_ratio", ratio, e, [f"E-{prod}", f"Z-{bp}"]),
         field("yield_measurement_basis", "isolated yield", e),
         field("ratio_measurement_basis", "1H NMR analysis of crude product", e)],
        [f"Table substituent R3={r3}."],
        ["Participant quantities and workup are absent from Table 4.", "Structures require review."]
    ))

# Scheme 2 axial-to-central chirality-transfer experiments.
scheme2 = [
    ("S-1b", "S-E-2b", 99, "20/1", "r.t.", 12, 86, 99),
    ("S-1j", "S-E-2j", 99, "20/1", "r.t.", 8, 94, 99),
    ("R-1o", "R-E-2o", 97, "2/1", qty(70, "°C"), 30, 79, 97),
]
for substrate, product, input_ee, solvent_ratio, temp, minutes, yld, product_ee in scheme2:
    e = ev(3)
    ps = [participant(substrate, "reactant", substrate, e),
          participant("phsecl", "reagent", "PhSeCl", e, [amount("equivalents", qty(1.5, "equiv"), e)], "Cl[Se]c1ccccc1"),
          participant("solvent", "solvent", f"CH3CN/H2O = {solvent_ratio}", e),
          participant(product, "product", product, e)]
    records.append(record(
        f"scheme2_{substrate}_to_{product}", "reported_experiment", e, ps,
        [field("temperature", temp, e), field("time", qty(minutes, "min"), e),
         field("solvent", f"CH3CN/H2O = {solvent_ratio}", e)],
        [field("starting_material_ee", qty(input_ee, "%"), e, [substrate]),
         field(f"isolated_yield_{product}", qty(yld, "%"), e, [product]),
         field("product_ee", qty(product_ee, "%"), e, [product])],
        unresolved=["Participant quantities other than 1.5 equiv PhSeCl are absent from Scheme 2.", "Absolute structures and stereochemical drawings require review."]
    ))

# Scheme 3 isotope-labeling experiments.
scheme3 = [
    ("1h", "E-2h*", 45, 84, 94.5, [3, 4, 5]),
    ("1c", "E-2c*", 37, 85, 88.4, [3, 5]),
    ("1e", "E-2e*", 41, None, 69.5, [3, 5]),
]
for substrate, product, minutes, yld, incorporation, pages in scheme3:
    e = ev(*pages)
    ps = [participant(substrate, "reactant", substrate, e),
          participant("phsecl", "reagent", "PhSeCl", e, [amount("equivalents", qty(1.5, "equiv"), e)], "Cl[Se]c1ccccc1"),
          participant("mecn_h218o", "solvent", "CH3CN/H2-18O = 20/1", e),
          participant(product, "product", product, e)]
    outcomes = [field("oxygen_18_incorporation", qty(incorporation, "%"), e, [product])]
    if yld is not None:
        outcomes.insert(0, field(f"isolated_yield_{product}", qty(yld, "%"), e, [product]))
    notes = []
    if product == "E-2h*":
        notes.append("Figure 4 and page-3 discussion report ESI-MS/MS precursor m/z 493 and daughter m/z 475.")
    records.append(record(
        f"scheme3_{substrate}_to_{product}", "reported_experiment", e, ps,
        [field("temperature", "r.t.", e), field("time", qty(minutes, "min"), e),
         field("solvent", "CH3CN/H2-18O = 20/1", e)], outcomes, notes,
        ["Participant amounts and workup are absent from Scheme 3.",
         "The page-5 scheme does not display a product yield for E-2e*; it remains missing." if yld is None else "Labeled structure requires review."]
    ))

# Starting-material preparations visible on pages 4-6.
def prep_record(suffix, pages, procedure, substrate, product, reagents, solvent_label,
                time_value, temp_values, product_mass, yld, notes=None, unresolved=None):
    e = ev(*pages)
    ps = [participant("starting_alcohol", "reactant", substrate, e, reagents.pop(0)),
          participant("triethylamine", "reagent", "Et3N", e, reagents.pop(0), "CCN(CC)CC"),
          participant("ph2pcl", "reagent", "Ph2PCl", e, reagents.pop(0), "ClP(c1ccccc1)c1ccccc1"),
          participant("solvent", "solvent", solvent_label, e, reagents.pop(0)),
          participant(product, "product", product, e)]
    conditions = [field("procedure", procedure, e), field("time", time_value, e), field("solvent", solvent_label, e)]
    conditions.extend(field(name, value, e) for name, value in temp_values)
    outcomes = [field(f"isolated_yield_{product}", qty(yld, "%"), e, [product]),
                field("isolated_product_mass", qty(product_mass, "g"), e, [product])]
    return record(suffix, "reported_experiment", e, ps, conditions, outcomes, notes,
                  unresolved or ["Product and starting-alcohol structures require review.", "Atmosphere is not reported."])


def vals(evidence_pages, sub_mass, sub_mmol, et_vol, et_mass, et_mmol, p_vol, p_mass, p_mmol, solvent_vol):
    e = ev(*evidence_pages)
    return [
        [amount("mass", qty(sub_mass, "g"), e), amount("amount", qty(sub_mmol, "mmol"), e)],
        [amount("volume", qty(et_vol, "mL"), e), amount("mass", qty(et_mass, "g"), e), amount("amount", qty(et_mmol, "mmol"), e)],
        [amount("volume", qty(p_vol, "mL"), e), amount("mass", qty(p_mass, "g"), e), amount("amount", qty(p_mmol, "mmol"), e)],
        [amount("volume", qty(solvent_vol, "mL"), e)],
    ]


records.append(prep_record(
    "section4.1.1_prepare_1j", [4, 5], "General Procedure I", "1-phenylpent-1-yn-3-ol", "1j",
    vals([4, 5], 2.4336, 15, 2.10, 1.53, 15, 2.80, 3.36, 15, 45), "CH2Cl2",
    None, [("addition_temperature", qty(-64, "°C")), ("warm_to", "r.t."), ("addition_time", qty(30, "min"))],
    2.1617, 41,
    ["Ph2PCl was dissolved in 5 mL of the total 45 mL CH2Cl2. TLC used petroleum ether/ethyl acetate 1:1; water quench, CH2Cl2 extraction, brine wash, Na2SO4 drying, evaporation, and silica chromatography (CH2Cl2/ethyl acetate 10:1) were reported."],
    ["Reaction time after warming to room temperature is not stated; completion was monitored by TLC.", "Structures require review."]
))
records.append(prep_record(
    "section4.1.2_prepare_1e", [5], "General Procedure I", "3-propylhex-1-yn-3-ol", "1e",
    vals([5], 2.1020, 15, 2.10, 1.53, 15, 2.80, 3.36, 15, 45), "CH2Cl2",
    qty(30, "h"), [("addition_temperature", qty(-64, "°C")), ("warm_to", "r.t."), ("heat_to", "reflux"), ("heating_ramp_time", qty(30, "min"))],
    1.3731, 28
))
records.append(prep_record(
    "section4.1.3_prepare_1g", [5], "General Procedure I", "hept-2-yn-1-ol", "1g",
    vals([5], 1.6865, 15, 2.10, 1.53, 15, 2.75, 3.30, 15, 45), "CH2Cl2",
    qty(7.5, "h"), [], 2.6667, 60,
    unresolved=["The abbreviated paragraph invokes General Procedure I but does not restate the stage-specific temperature sequence.", "Structures require review."]
))
records.append(prep_record(
    "section4.1.4_prepare_1k", [5], "General Procedure I", "2-methyloct-3-yn-2-ol", "1k",
    vals([5], 2.0734, 15, 2.10, 1.53, 15, 2.80, 3.36, 15, 45), "CH2Cl2",
    qty(15, "h"), [], 2.1277, 44,
    unresolved=["The abbreviated paragraph invokes General Procedure I but does not restate the stage-specific temperature sequence.", "Structures require review."]
))
records.append(prep_record(
    "section4.1.5_prepare_1p", [5, 6], "General Procedure I", "4-phenylbut-1-yn-3-ol", "1p",
    vals([5, 6], 2.1919, 15, 2.20, 1.61, 15, 2.80, 3.36, 15, 45), "CH2Cl2",
    qty(12, "h"), [], 2.3521, 47,
    unresolved=["The abbreviated paragraph invokes General Procedure I but does not restate the stage-specific temperature sequence.", "Structures require review."]
))

# General Procedure II preparations on page 6.
records.append(prep_record(
    "section4.2.1_prepare_1a", [6], "General Procedure II", "1-phenyloct-1-yn-3-ol", "1a",
    vals([6], 3.0038, 15, 3.3, 2.41, 22.5, 4.30, 5.18, 22.5, 60), "THF",
    None, [("addition_temperature", qty(-64, "°C")), ("warm_to", "r.t."), ("addition_time", qty(22, "min"))],
    4.1912, 73,
    ["Ph2PCl was dissolved in 10 mL of the total 60 mL THF. TLC used petroleum ether/ethyl acetate 1:1; water quench, Et2O extraction, brine wash, Na2SO4 drying, evaporation, and silica chromatography (petroleum ether/ethyl acetate 5:1 to 2:1) were reported."],
    ["Reaction time after warming to room temperature is not stated; completion was monitored by TLC.", "Structures require review."]
))
records.append(prep_record(
    "section4.2.2_prepare_S-1j", [6], "General Procedure II", "S-(-)-1-phenylpent-1-yn-3-ol (99% ee)", "S-(+)-1j",
    vals([6], 0.6390, 4.0, 0.83, 0.61, 6.0, 1.10, 1.32, 6.0, 25), "THF",
    qty(2.0, "h"), [], 0.6290, 46,
    ["Starting alcohol ee was 99%. HPLC and optical rotation conditions are reported, but the product ee is not explicitly stated in this paragraph."],
    ["Stage-specific temperature and workup are inherited only by reference to General Procedure II and are not restated.", "Product ee is not explicitly quantified in section 4.2.2.", "Structures require review."]
))
records.append(prep_record(
    "section4.2.3_prepare_1l", [6], "General Procedure II", "4-methylpent-1-yn-3-ol (95% purity, THF-contaminated)", "1l",
    vals([6], 2.0619, 20, 4.20, 3.07, 30, 5.50, 6.60, 30, 55.5), "THF",
    qty(12, "h"), [], 2.4698, 44,
    ["The starting alcohol mass was reported for material contaminated with THF at 95% purity."],
    ["Stage-specific temperature and workup are inherited only by reference to General Procedure II and are not restated.", "Structures require review."]
))
records.append(prep_record(
    "section4.2.4_prepare_1o", [6], "General Procedure II", "non-1-yn-3-ol", "1o",
    vals([6], 2.1046, 15, 3.20, 2.34, 22.5, 4.20, 5.04, 22.5, 45), "THF",
    qty(3.5, "h"), [], 3.0060, 62,
    unresolved=["Stage-specific temperature and workup are inherited only by reference to General Procedure II and are not restated.", "Structures require review."]
))
records.append(prep_record(
    "section4.2.5_prepare_R-1o", [6], "General Procedure II", "R-(+)-1-nonyn-3-ol (99% ee)", "R-(+)-1o",
    vals([6], 0.9757, 7.0, 1.45, 1.06, 10.5, 1.95, 2.34, 10.5, 25), "THF",
    qty(3.0, "h"), [], 1.2900, 57,
    ["Starting alcohol ee was 99%. HPLC and optical rotation data are reported; the paragraph does not explicitly state product ee."],
    ["Stage-specific temperature and workup are inherited only by reference to General Procedure II and are not restated.", "Product ee is not explicitly quantified in section 4.2.5.", "Structures require review."]
))

# Explicit alternative preparation noted to erode ee; kept separate from the GP II batch.
e = ev(6)
records.append(record(
    "section4.2_alternative_GP-I_R-1o", "reported_experiment", e,
    [participant("R-propargylic-alcohol", "reactant", "optically active propargylic alcohol (99% ee)", e),
     participant("R-1o", "product", "R-(+)-1o", e)],
    [field("procedure", "General Procedure I", e), field("time", None, e), field("temperature", None, e)],
    [field("starting_material_ee", qty(99, "%"), e, ["R-propargylic-alcohol"]),
     field("product_ee", qty(60, "%"), e, ["R-1o"])],
    ["This is an explicitly noted alternative outcome, distinct from the General Procedure II preparation."],
    ["Exact substrate quantities, time, temperature, yield, and workup are not reported for this comparison.", "Structures require review."]
))

# Proposed mechanisms are classified and are not counted as reported experiments.
e = ev(3, 5)
for suffix, description in [
    ("scheme4_proposed_mechanism", "Proposed selenohydroxylation mechanism through selenium intermediate 5 and five-membered cyclic intermediate 6, followed by H2-18O attack at phosphorus and P-O cleavage."),
    ("scheme5_chirality_transfer_rationale", "Proposed stereochemical rationale for axial-to-central chirality transfer via intermediates 5 and 6."),
]:
    records.append(record(
        suffix, "mechanism", e, [], [], [], [description],
        ["Mechanistic structures are generic R-group drawings and are not reported batch experiments."]
    ))

out = ROOT / "raw_model" / "records_pages_0001_0006.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "path": str(out)}, ensure_ascii=False))
