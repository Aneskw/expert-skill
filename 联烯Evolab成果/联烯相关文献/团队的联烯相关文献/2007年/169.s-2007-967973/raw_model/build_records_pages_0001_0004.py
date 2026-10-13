import json
from pathlib import Path

DOC = "doc_1aa5ae0f9990e25c"
P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def missing_conditions(evidence, include_temp=False, include_time=False, include_solvent=False):
    fields = []
    if include_solvent:
        fields.append(field("solvent", None, evidence))
    if include_temp:
        fields.append(field("temperature", None, evidence))
    if include_time:
        fields.append(field("time", None, evidence))
    fields.extend([
        field("atmosphere", None, evidence),
        field("workup", None, evidence),
        field("purification", None, evidence),
    ])
    return fields


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


records = []

# Prose-only base screen. The source gives one collective isolated-yield range,
# not a value-to-base assignment; each condition is therefore kept independent
# and the ambiguity remains explicit.
base_rows = [
    ("naoh", "NaOH", "sodium hydroxide", "[Na+].[OH-]"),
    ("lioh", "LiOH", "lithium hydroxide", "[Li+].[OH-]"),
    ("koh", "KOH", "potassium hydroxide", "[K+].[OH-]"),
    ("cs2co3", "Cs2CO3", "cesium carbonate", "[Cs+].[Cs+].[O-]C([O-])=O"),
    ("k3ps4_3h2o", "K3PS4·3H2O", "tripotassium thiophosphate trihydrate", None),
]
for slug, label, name, smiles in base_rows:
    ev = [P1T, P1I]
    ps = [
        participant("substrate_1a", "reactant", "1a", "ethyl (hepta-1,2-dien-3-yl)phosphonate monoacid", ev, "C=C=C(CCCC)P(=O)(O)OCC"),
        participant("allyl_bromide", "reactant", "allyl bromide", "3-bromoprop-1-ene", ev, "C=CCBr"),
        participant("base", "reagent", label, name, ev, smiles),
        participant("pdcl2_pph3_2", "catalyst", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", ev),
        participant("product_2a", "product", "2a", "coupling-cyclization product 2a", ev),
    ]
    cond = missing_conditions(ev, include_temp=True, include_time=True, include_solvent=True)
    records.append(record(
        f"prose_base_screen_{slug}", f"page1_base_screen_{label}", "optimization_entry", ev, ps,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": cond}],
        [field("collective_isolated_yield_range_for_base_screen", {"minimum": 14, "maximum": 55, "unit": "%", "raw_text": "14–55%"}, ev, ["product_2a"]),
         field("yield_measurement_basis", "isolated", ev, ["product_2a"])],
        ["The paper reports the range collectively for five bases and does not assign an individual yield to this base."],
        ["Individual yield within the collectively reported range is not specified.", "Base loading, solvent, temperature, time, atmosphere, workup, and purification are not reported for this prose-only condition.", "Product structure is not independently verified."],
    ))


solvents = {
    "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
    "DMA": ("N,N-dimethylacetamide", "CC(=O)N(C)C"),
    "DMSO": ("dimethyl sulfoxide", "CS(C)=O"),
    "CH2Cl2": ("dichloromethane", "ClCCl"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
    "PhMe": ("toluene", "Cc1ccccc1"),
    "MeCN": ("acetonitrile", "CC#N"),
}

# Table 1. Entry 4 is also Table 2 entry 1 and receives both identities/evidence.
table1 = [
    (1, "DMF", {"number": 70, "unit": "°C"}, 48, 0),
    (2, "DMF", {"number": 70, "unit": "°C"}, 48, 55),
    (3, "DMF", {"number": 70, "unit": "°C"}, 3, 65),
    (4, "DMF", {"number": 80, "unit": "°C"}, 2, 72),
    (5, "DMF", {"number": 90, "unit": "°C"}, 1, 68),
    (6, "DMF", {"number": 80, "unit": "°C"}, 2, 66),
    (7, "DMA", {"number": 80, "unit": "°C"}, 2, 50),
    (8, "DMSO", {"number": 80, "unit": "°C"}, 2, 32),
    (9, "CH2Cl2", "reflux", 24, 61),
    (10, "THF", "reflux", 24, 58),
    (11, "PhMe", {"number": 80, "unit": "°C"}, 3, 26),
    (12, "MeCN", {"number": 80, "unit": "°C"}, 3, 31),
]
for entry, solvent_label, temperature, hours, yld in table1:
    ev = [P2T, P2I]
    if entry in (2, 3, 4, 6):
        ev = [P1T, P1I, P2T, P2I]
    catalyst_label = "PdCl2(PPh3)2" if entry in (1, 2) else "PdCl2(PhCN)2"
    catalyst_name = "bis(triphenylphosphine)palladium(II) dichloride" if entry in (1, 2) else "bis(benzonitrile)palladium(II) dichloride"
    catalyst_loading = 10 if entry == 1 else 5
    solvent_name, solvent_smiles = solvents[solvent_label]
    ps = [
        participant("substrate_1a", "reactant", "1a", "ethyl (hepta-1,2-dien-3-yl)phosphonate monoacid", ev, "C=C=C(CCCC)P(=O)(O)OCC"),
        participant("allyl_bromide", "reactant", "allyl bromide", "3-bromoprop-1-ene", ev, "C=CCBr"),
        participant("catalyst", "catalyst", catalyst_label, catalyst_name, ev, None, [amount("catalyst_loading", catalyst_loading, "mol%", ev)]),
        participant("solvent", "solvent", solvent_label, solvent_name, ev, solvent_smiles),
        participant("product_2a", "product", "2a", "coupling-cyclization product 2a", ev),
    ]
    if entry == 1:
        ps.append(participant("k2co3", "reagent", "K2CO3", "potassium carbonate", ev, "[K+].[K+].[O-]C([O-])=O", [amount("equivalents", 4, "equiv", ev)]))
        ps.append(participant("product_3a", "product", "3a", "O-allylation product 3a", ev))
    conditions = [
        field("solvent", solvent_label, ev), field("temperature", temperature, ev),
        field("time", {"number": hours, "unit": "h"}, ev),
        field("atmosphere", "air" if entry == 6 else ("N2" if entry == 4 else None), ev),
        field("workup", None, ev), field("purification", None, ev),
    ]
    outcomes = [
        field("reported_yield_2a", {"number": yld, "unit": "%"}, ev, ["product_2a"]),
        field("yield_measurement_basis_2a", "isolated" if entry == 4 else None, ev, ["product_2a"]),
    ]
    notes = []
    source_id = f"Table 1 entry {entry}"
    suffix = f"table1_entry{entry}_2a"
    if entry == 1:
        outcomes.extend([
            field("isolated_yield_3a", {"number": 23, "unit": "%"}, ev, ["product_3a"]),
            field("yield_measurement_basis_3a", "isolated", ev, ["product_3a"]),
        ])
        notes.append("Only O-allylation product 3a was isolated in this entry.")
    if entry == 4:
        source_id = "Table 1 entry 4 / Table 2 entry 1"
        suffix = "table1_entry4_table2_entry1_2a"
        notes.append("The identical standard-condition 1a-to-2a result is printed in both tables and is represented once.")
    unresolved = ["Exact reactant/product connectivity and stereochemistry require structure review.", "Workup and purification are not reported in the supplied main text; no SI is associated."]
    if entry not in (4,):
        unresolved.append("Atmosphere is not reported for this entry." if entry != 6 else "No unresolved atmosphere field; the entry explicitly states air.")
    if entry != 4:
        unresolved.append("Yield measurement basis for 2a is not explicitly stated for this row.")
    records.append(record(
        suffix, source_id, "optimization_entry", ev, ps,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        outcomes, notes, unresolved,
    ))


substrate_smiles = {
    "1b": "C=C=C(CC=C)P(=O)(O)OCC",
    "1c": "C=C=C(C(C)(C)C)P(=O)(O)OCC",
    "1d": "C=C=C(Cc1ccccc1)P(=O)(O)OCC",
    "1e": "CC(C)=C=CP(=O)(O)OCC",
    "1f": "CC(C)=C=C(CCCC)P(=O)(O)OCC",
    "1g": None,
    "1h": "CC(C)=C=C(CC=C)P(=O)(O)OCC",
    "1i": "CC(C)=C=C(CC(=C)C)P(=O)(O)OCC",
}
table2 = [
    (2, "Allyl", "H", "H", "1b", 1, 72, "2b"),
    (3, "t-Bu", "H", "H", "1c", 4, 52, "2c"),
    (4, "Bn", "H", "H", "1d", 1, 75, "2d"),
    (5, "H", "Me", "Me", "1e", 5, 42, "2e"),
    (6, "n-Bu", "Me", "Me", "1f", 2, 68, "2f"),
    (7, "n-Bu", "-(CH2)5-", "-(CH2)5-", "1g", 5, 67, "2g"),
    (8, "Allyl", "Me", "Me", "1h", 6, 47, "2h"),
    (9, "2-Methylallyl", "Me", "Me", "1i", 3, 56, "2i"),
]
for entry, r1, r2, r3, substrate_label, hours, yld, product_label in table2:
    ev = [P1T, P1I, P2T, P2I]
    ps = [
        participant("substrate", "reactant", substrate_label, f"1,2-allenyl phosphonic acid monoethyl ester ({r1=}, {r2=}, {r3=})", ev, substrate_smiles[substrate_label]),
        participant("allyl_bromide", "reactant", "allyl bromide", "3-bromoprop-1-ene", ev, "C=CCBr"),
        participant("catalyst", "catalyst", "PdCl2(PhCN)2", "bis(benzonitrile)palladium(II) dichloride", ev, None, [amount("catalyst_loading", 5, "mol%", ev)]),
        participant("solvent", "solvent", "DMF", "N,N-dimethylformamide", ev, "CN(C)C=O"),
        participant("product", "product", product_label, f"coupling-cyclization product {product_label}", ev),
    ]
    outcomes = [
        field(f"isolated_yield_{product_label}", {"number": yld, "unit": "%"}, ev, ["product"]),
        field(f"yield_measurement_basis_{product_label}", "isolated", ev, ["product"]),
    ]
    if entry == 8:
        ps.append(participant("byproduct_4h", "product", "4h", "cycloisomerization product 4h", ev))
        outcomes.extend([
            field("isolated_yield_4h", {"number": 12, "unit": "%"}, ev, ["byproduct_4h"]),
            field("yield_measurement_basis_4h", "isolated", ev, ["byproduct_4h"]),
        ])
    conditions = [
        field("solvent", "DMF", ev), field("temperature", {"number": 80, "unit": "°C"}, ev),
        field("time", {"number": hours, "unit": "h"}, ev), field("atmosphere", "N2", ev),
        field("workup", None, ev), field("purification", None, ev),
    ]
    records.append(record(
        f"table2_entry{entry}_{product_label}", f"Table 2 entry {entry}", "substrate_scope_entry", ev, ps,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        outcomes, [f"Table substituents are retained verbatim: R1={r1}, R2={r2}, R3={r3}."],
        ["Workup and purification are not reported in the supplied main text; no SI is associated.", "Complex product connectivity and stereochemistry remain unverified."] + (["The cyclic -(CH2)5- substrate structure candidate is left without SMILES pending source review."] if entry == 7 else []),
    ))


# Scheme 1, two independent arrows from 1f.
scheme1 = [
    ("2j", "2-methylallyl chloride", "2-methylprop-2-en-1-yl chloride", "C=C(C)CCl", 24, [("2j", 80)]),
    ("2k_4f", "3-chlorobut-1-ene", "3-chlorobut-1-ene", "C=CC(Cl)C", 36, [("2k", 59), ("4f", 37)]),
]
for suffix, halide_label, halide_name, halide_smiles, hours, product_yields in scheme1:
    ev = [P1T, P1I, P3T, P3I]
    ps = [
        participant("substrate_1f", "reactant", "1f", "1,2-allenyl phosphonic acid monoethyl ester 1f", ev, "CC(C)=C=C(CCCC)P(=O)(O)OCC"),
        participant("allylic_chloride", "reactant", halide_label, halide_name, ev, halide_smiles, [amount("equivalents", 5, "equiv", ev)]),
        participant("catalyst", "catalyst", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", ev, None, [amount("catalyst_loading", 5, "mol%", ev)]),
        participant("solvent", "solvent", "DMF", "N,N-dimethylformamide", ev, "CN(C)C=O"),
    ]
    for label, _ in product_yields:
        ps.append(participant(f"product_{label}", "product", label, f"reported product {label}", ev))
    outcomes = []
    for label, yld in product_yields:
        basis = "isolated" if label == "2k" else None
        outcomes.extend([
            field(f"reported_yield_{label}", {"number": yld, "unit": "%"}, ev, [f"product_{label}"]),
            field(f"yield_measurement_basis_{label}", basis, ev, [f"product_{label}"]),
        ])
    if suffix == "2k_4f":
        outcomes.append(field("z_e_ratio_2k", "Z/E = 1:1", ev, ["product_2k"]))
    conditions = [
        field("solvent", "DMF", ev), field("temperature", {"number": 80, "unit": "°C"}, ev),
        field("time", {"number": hours, "unit": "h"}, ev), field("atmosphere", None, ev),
        field("workup", None, ev), field("purification", None, ev),
    ]
    records.append(record(
        f"scheme1_{suffix}", f"Scheme 1 {suffix}", "reported_experiment", ev, ps,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        outcomes, [],
        ["Atmosphere, workup, and purification are not reported in the supplied main text; no SI is associated.", "Complex product connectivity and product stereochemistry remain unverified."] + (["Yield measurement basis is not explicit for 2j."] if suffix == "2j" else ["Yield measurement basis is not explicit for coproduct 4f."]),
    ))


# Scheme 2: three substitution cases, each a distinct tandem experiment.
scheme2 = [
    ("6b", "H", "H", "H", 68),
    ("6h", "Me", "Me", "H", 83),
    ("6i", "Me", "Me", "Me", 58),
]
for product_label, r1, r2, r3, yld in scheme2:
    ev = [P3T, P3I]
    ps = [
        participant("substrate_2", "reactant", f"2 ({r1=}, {r2=}, {r3=})", "3,4-diallyl-2,5-dihydro[1,2]oxaphosphole 2-oxide derivative", ev),
        participant("grubbs_ii", "catalyst", "Grubbs II catalyst", "second-generation Grubbs catalyst depicted in Scheme 2", ev, None, [amount("catalyst_loading", 5, "mol%", ev)]),
        participant("dcm", "solvent", "CH2Cl2", "dichloromethane", ev, "ClCCl"),
        participant("ddq", "reagent", "DDQ", "2,3-dichloro-5,6-dicyano-1,4-benzoquinone", ev, "N#CC1=C(Cl)C(=O)C(C#N)=C(Cl)C1=O", [amount("equivalents", 1.5, "equiv", ev)]),
        participant("toluene", "solvent", "toluene", "toluene", ev, "Cc1ccccc1"),
        participant("product", "product", product_label, f"1-ethoxy-1,3-dihydro[2,1]benzoxaphosphole 1-oxide derivative {product_label}", ev),
    ]
    if product_label == "6b":
        ps.append(participant("intermediate_5b", "product", "5b", "1-ethoxy-1,3,4,7-tetrahydro[2,1]benzoxaphosphole 1-oxide", ev))
    step1_ids = ["substrate_2", "grubbs_ii", "dcm"]
    step2_ids = ["ddq", "toluene"] + (["intermediate_5b"] if product_label == "6b" else [])
    steps = [
        {"step_id": "ring_closing_metathesis", "participant_ids": step1_ids, "conditions": [
            field("solvent", "CH2Cl2", ev), field("temperature", "reflux", ev),
            field("time", {"number": 1, "unit": "h"}, ev), field("operation", "evaporation after stage 1", ev),
            field("atmosphere", None, ev),
        ]},
        {"step_id": "ddq_oxidation", "participant_ids": step2_ids, "conditions": [
            field("solvent", "toluene", ev), field("temperature", {"number": 80, "unit": "°C"}, ev),
            field("time", "overnight", ev), field("atmosphere", None, ev),
            field("workup", None, ev), field("purification", None, ev),
        ]},
    ]
    outcomes = [
        field(f"reported_yield_{product_label}", {"number": yld, "unit": "%"}, ev, ["product"]),
        field(f"yield_measurement_basis_{product_label}", None, ev, ["product"]),
    ]
    if product_label == "6b":
        outcomes.append(field("qualitative_stage_1_yield_5b", "good yield", ev, ["intermediate_5b"]))
    records.append(record(
        f"scheme2_{product_label}", f"Scheme 2 {product_label}", "substrate_scope_entry", ev, ps, steps, outcomes,
        [f"Scheme 2 substitution assignment retained verbatim: R1={r1}, R2={r2}, R3={r3}."],
        ["Atmosphere, workup, purification, and final yield measurement basis are not reported.", "The qualitative duration 'overnight' is not converted to a numeric time.", "Complex substrate, intermediate, and product structures remain unverified."],
    ))


# The prose separately reports that 2b gives 5b in good yield in toluene.
ev = [P3T, P3I]
ps = [
    participant("substrate_2b", "reactant", "2b", "3,4-diallyl-2-ethoxy-2,5-dihydro[1,2]oxaphosphole 2-oxide", ev),
    participant("grubbs_ii", "catalyst", "Grubbs II catalyst", "second-generation Grubbs catalyst", ev),
    participant("toluene", "solvent", "toluene", "toluene", ev, "Cc1ccccc1"),
    participant("product_5b", "product", "5b", "1-ethoxy-1,3,4,7-tetrahydro[2,1]benzoxaphosphole 1-oxide", ev),
]
records.append(record(
    "prose_2b_to_5b_toluene", "page3 prose: 2b to 5b in toluene", "reported_experiment", ev, ps,
    [{"step_id": "ring_closing_metathesis", "participant_ids": ["substrate_2b", "grubbs_ii", "toluene"], "conditions": missing_conditions(ev, include_temp=True, include_time=True)}],
    [field("qualitative_yield_5b", "good yield", ev, ["product_5b"]), field("yield_measurement_basis_5b", None, ev, ["product_5b"])],
    ["The prose reports toluene as an alternative solvent; it does not provide a numerical yield or a complete procedure for this alternative."],
    ["Catalyst loading, temperature, time, atmosphere, workup, purification, and numerical yield are not stated for the toluene alternative.", "Complex substrate and product structures remain unverified."],
))


out = Path(__file__).with_name("records_pages_0001_0004.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(out)}, ensure_ascii=False))
