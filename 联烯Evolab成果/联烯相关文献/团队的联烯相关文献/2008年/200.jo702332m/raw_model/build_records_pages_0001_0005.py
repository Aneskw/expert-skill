#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0005.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0005.json"
DOC = "doc_265ba0d7ea151308"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def amount(name, value, evidence):
    return field(name, value, evidence)


SMILES = {
    "1a": "C=C=CC1(O)CCCCC1",
    "1b": "C=C=CC(O)(C)C",
    "1c": "C=C=CC(O)(CC)CC",
    "1d": "C=C=CC(O)(CCCC)CCCC",
    "1e": "C=C=C(CCCC)CO",
    "1f": "C=C=C(CCCCCCC)CO",
    "1g": "C=C=C(CCCC)C(O)C",
    "1h": "C=C=C(CCCC)C(O)CC",
    "1i": "C=C=C(c1ccccc1)C(O)CCCC",
    "1j": "C=C=C(C(=O)OC)C(O)CC",
    "1k": "C=C=C(CC=C)C(O)C",
    "PdCl2": "[Cl-].[Cl-].[Pd+2]",
    "PdBr2": "[Br-].[Br-].[Pd+2]",
    "PdI2": "[I-].[I-].[Pd+2]",
    "NaCl": "[Na+].[Cl-]",
    "LiCl": "[Li+].[Cl-]",
    "NaI": "[Na+].[I-]",
    "KI": "[K+].[I-]",
    "I2": "II",
    "CH3I": "CI",
    "DMA": "CC(=O)N(C)C",
    "THF": "C1CCOC1",
    "acetone": "CC(=O)C",
    "CH3CN": "CC#N",
    "Et2O": "CCOCC",
    "toluene": "Cc1ccccc1",
    "N-phenylmaleimide": "O=C1C=CC(=O)N1c1ccccc1",
    "CH2Br2": "BrCBr",
}


def chemical(entity_id, role, label, evidence, name=None, amounts=None, smiles_key=None):
    return participant(
        entity_id, role, label, evidence, name=name,
        smiles=SMILES.get(smiles_key or label), amounts=amounts,
    )


records = []

# Page-1 graphical summary: generic, not a row-level execution.
e1 = ev(1)
p = [
    participant("generic_allenol", "reactant", "generic 2,3-allenol", e1),
    participant("generic_product", "product", "generic 4-(1′,3′-dien-2′-yl)-2,5-dihydrofuran", e1),
    chemical("pdcl2", "catalyst", "PdCl2", e1, amounts=[amount("catalyst_loading", qty(5, "mol%"), e1)]),
    chemical("nai", "reagent", "NaI", e1, amounts=[amount("equivalents", qty(0.5, "equiv"), e1)]),
    chemical("dma", "solvent", "DMA", e1, name="N,N-dimethylacetamide"),
]
records.append(record(
    "graphical_summary_general_scheme", "general_scheme", e1, p,
    [{"step_id": "summary_arrow", "participant_ids": [x["entity_id"] for x in p], "conditions": [
        field("temperature", qty(80, "°C"), e1),
    ]}],
    [field("reported_scope_yield_range", rng(58, 92, "%", "58–92%"), e1, ["generic_product"])],
    notes=[fact("Graphical abstract summarizes the present reaction class and is not a single substrate-specific execution.", e1)],
    unresolved=["Generic R-group structures are not assigned compound-specific SMILES.", "Duration, scale, atmosphere, workup, purification, and yield basis are not specified in the summary arrow."],
))


def substrate_product(label_in, label_out, evidence):
    substrate = chemical(label_in, "reactant", label_in, evidence, smiles_key=label_in)
    product_name = "3-(1-cyclohexylidenemethylvinyl)-1-oxaspiro[4.5]dec-3-ene" if label_out == "2a" else None
    product = participant(label_out, "product", label_out, evidence, name=product_name)
    return substrate, product


# Table 1, page 2. Table 1 entry 6 is enriched later with the exact page-4 procedure.
table1 = [
    (1, "DMA", None, None, 24, "trace", "isolated", None),
    (2, "DMA", "NaCl", 0.5, 12, 22, "1H NMR with 1,3,5-trimethylbenzene internal standard", 10),
    (3, "DMA", "LiCl", 0.5, 12, 25, "1H NMR with 1,3,5-trimethylbenzene internal standard", None),
    (4, "DMA", "NaI", 0.1, 5, 42, "isolated", None),
    (5, "DMA", "NaI", 0.3, 5, 80, "isolated", None),
    (6, "DMA", "NaI", 0.5, 5, 86, "isolated", None),
    (7, "DMA", "NaI", 0.5, 21, 75, "1H NMR with 1,3,5-trimethylbenzene internal standard", 16),
    (8, "DMA", "NaI", 1.0, 5, 81, "isolated", None),
    (9, "DMA", "KI", 0.5, 5, 85, "isolated", None),
    (10, "DMA", "I2", 0.25, 0.5, 66, "isolated", None),
    (11, "DMA", "I2", 0.05, 3, 42, "isolated", None),
    (12, "DMA", "CH3I", 10, 1.5, 86, "isolated", None),
    (13, "THF", "NaI", 0.5, 17, 60, "1H NMR with 1,3,5-trimethylbenzene internal standard", 11),
    (14, "acetone", "NaI", 0.5, 17, 47, "1H NMR with 1,3,5-trimethylbenzene internal standard", 40),
    (15, "CH3CN", "NaI", 0.5, 17, 44, "1H NMR with 1,3,5-trimethylbenzene internal standard", 33),
]
e2 = ev(2)
for entry, solvent, additive, equivalents, hours, yld, basis, recovery in table1:
    evidence = e2 + (ev(3) if entry in (1, 6) else []) + (ev(4) if entry == 6 else []) + (ev(5) if entry == 6 else [])
    substrate, product = substrate_product("1a", "2a", evidence)
    catalyst_loading = 2 if entry == 7 else 5
    participants = [
        substrate, product,
        chemical("pdcl2", "catalyst", "PdCl2", evidence, amounts=[amount("catalyst_loading", qty(catalyst_loading, "mol%"), evidence)]),
        chemical(solvent.lower(), "solvent", solvent, evidence, name="N,N-dimethylacetamide" if solvent == "DMA" else None, smiles_key=solvent),
    ]
    if additive:
        participants.append(chemical(additive.lower(), "reagent", additive, evidence, amounts=[amount("equivalents", qty(equivalents, "equiv"), evidence)]))
    if entry == 2 or entry == 7 or entry >= 13:
        participants.append(participant("nmr_internal_standard", "reagent", "1,3,5-trimethylbenzene", evidence, smiles="Cc1cc(C)cc(C)c1"))
    conditions = [field("temperature", qty(80, "°C"), evidence), field("time", qty(hours, "h"), evidence)]
    outcomes = [field("reported_yield_2a", yld if isinstance(yld, str) else qty(yld, "%"), evidence, ["2a"]), field("yield_measurement_basis", basis, evidence, ["2a"])]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", qty(recovery, "%"), evidence, ["1a"]))
    notes = []
    if additive is None:
        notes.append(fact("No additive was used.", evidence))
    if entry == 6:
        notes.append(fact("The acknowledgment states that Table 2 entry 1 was reproduced by a group member.", ev(5)))
    unresolved = ["Atmosphere is not reported.", "Candidate structures remain machine-derived and unverified."]
    if entry != 6:
        unresolved.append("Workup and purification are not reported for this optimization row.")
    if entry == 6:
        # Exact typical procedure and workup from page 4.
        substrate["amounts"] = [amount("mass", qty(136.8, "mg"), ev(4)), amount("amount", qty(0.99, "mmol"), ev(4))]
        participants[2]["amounts"] += [amount("mass", qty(8.8, "mg"), ev(4)), amount("amount", qty(0.050, "mmol"), ev(4))]
        participants[3]["amounts"] = [amount("volume", qty(2, "mL"), ev(4))]
        nai = next(x for x in participants if x["entity_id"] == "nai")
        nai["amounts"] += [amount("mass", qty(75.1, "mg"), ev(4)), amount("amount", qty(0.50, "mmol"), ev(4))]
        product["amounts"] = [amount("isolated_mass", qty(109.3, "mg"), ev(4))]
        participants.extend([
            participant("water_quench", "reagent", "water", ev(4), smiles="O", amounts=[amount("volume", qty(10, "mL"), ev(4))]),
            chemical("ether_extract", "solvent", "Et2O", ev(4), name="diethyl ether", amounts=[amount("extraction_volume", qty(25, "mL"), ev(4))]),
            participant("sodium_thiosulfate_wash", "reagent", "saturated aqueous Na2S2O3", ev(4)),
            participant("brine_wash", "reagent", "brine", ev(4)),
            participant("drying_agent", "reagent", "anhydrous Na2SO4", ev(4)),
            participant("chromatography_eluent", "solvent", "petroleum ether/diethyl ether 20:1", ev(4)),
        ])
        conditions += [
            field("operation", "TLC monitoring to completion; cool to room temperature and quench with water", ev(4)),
            field("workup", "Extract with diethyl ether three times; wash combined organic layer with saturated aqueous Na2S2O3 and brine; dry over anhydrous Na2SO4; evaporate", ev(4)),
            field("purification", "Silica-gel column chromatography, petroleum ether/diethyl ether 20:1", ev(4)),
        ]
        unresolved = ["Atmosphere is not reported.", "The 1a and 2a candidate structures remain unverified."]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, participants,
        [{"step_id": "homodimeric_coupling_cyclization", "participant_ids": [x["entity_id"] for x in participants], "conditions": conditions}],
        outcomes, notes=notes, unresolved=unresolved,
    ))


# Table 2 scope, page 3. Entry 1 is identical to Table 1 entry 6 and is not duplicated.
e3 = ev(3)
table2 = [
    (2, "1b", "2b", 5, 66),
    (3, "1c", "2c", 4, 85),
    (4, "1d", "2d", 10, 92),
    (5, "1e", "2e", 12, 84),
    (6, "1f", "2f", 12, 87),
]
for entry, substrate_label, product_label, hours, yld in table2:
    evidence = e3 + (ev(5) if entry == 4 else [])
    substrate, product = substrate_product(substrate_label, product_label, evidence)
    participants = [
        substrate, product,
        chemical("pdcl2", "catalyst", "PdCl2", evidence, amounts=[amount("catalyst_loading", qty(5, "mol%"), evidence)]),
        chemical("nai", "reagent", "NaI", evidence, amounts=[amount("equivalents", qty(0.5, "equiv"), evidence)]),
        chemical("dma", "solvent", "DMA", evidence, name="N,N-dimethylacetamide"),
    ]
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "homodimeric_coupling_cyclization", "participant_ids": [x["entity_id"] for x in participants], "conditions": [field("temperature", qty(80, "°C"), evidence), field("time", qty(hours, "h"), evidence)]}],
        [field(f"isolated_yield_{product_label}", qty(yld, "%"), evidence, [product_label]), field("yield_measurement_basis", "isolated yield", evidence, [product_label])],
        notes=[fact("The acknowledgment states that Table 2 entry 4 was reproduced by a group member.", ev(5))] if entry == 4 else None,
        unresolved=["Absolute quantities, atmosphere, workup, and purification are not reported.", "Product connectivity and stereochemistry remain unverified."],
    ))


# Table 3 stereoselective scope.
table3 = [
    (1, "1g", "2g", 13, 83, "E/Z_ratio", "≥95:5"),
    (2, "1h", "2h", 14, 86, "E/Z_ratio", "≥96:4"),
    (3, "1i", "2i", 11, 75, "Z/E_ratio", ">99:1"),
    (4, "1j", "2j", 17, 58, "Z/E_ratio", "95:5"),
    (5, "1k", "2k", 1.5, 61, "E/Z_ratio", ">99:1"),
]
for entry, substrate_label, product_label, hours, yld, ratio_name, ratio in table3:
    evidence = e3 + (ev(5) if entry in (1, 4) else [])
    substrate, product = substrate_product(substrate_label, product_label, evidence)
    participants = [
        substrate, product,
        chemical("pdcl2", "catalyst", "PdCl2", evidence, amounts=[amount("catalyst_loading", qty(5, "mol%"), evidence)]),
        chemical("nai", "reagent", "NaI", evidence, amounts=[amount("equivalents", qty(0.5, "equiv"), evidence)]),
        chemical("dma", "solvent", "DMA", evidence, name="N,N-dimethylacetamide"),
    ]
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "stereoselective_homodimerization", "participant_ids": [x["entity_id"] for x in participants], "conditions": [field("temperature", qty(80, "°C"), evidence), field("time", qty(hours, "h"), evidence)]}],
        [
            field(f"isolated_yield_{product_label}", qty(yld, "%"), evidence, [product_label]),
            field("yield_measurement_basis", "isolated yield", evidence, [product_label]),
            field(ratio_name, ratio, evidence, [product_label]),
            field("selectivity_measurement_basis", "1H NMR analysis", evidence, [product_label]),
        ],
        notes=[fact(f"The acknowledgment states that Table 3 entry {entry} was reproduced by a group member.", ev(5))] if entry in (1, 4) else None,
        unresolved=["Absolute quantities, atmosphere, workup, and purification are not reported.", "Product connectivity and stereochemical SMILES remain unverified."],
    ))


# Scheme 1: two distinct enantioenriched starting-material experiments.
for tag, start_label, start_ee, product_prefix, hours, yld, product_ee in [
    ("r", "R-(+)-1g", 97, "R-2g", 4, 86, 97),
    ("s", "S-(-)-1g", 98, "S-2g", 9.5, 88, 99),
]:
    start = participant("1g_enriched", "reactant", start_label, e3, smiles=SMILES["1g"], amounts=[])
    eprod = participant("E_product", "product", f"(E)-{product_prefix}", e3)
    zprod = participant("Z_product", "product", f"(Z)-{product_prefix}", e3)
    participants = [
        start, eprod, zprod,
        chemical("pdcl2", "catalyst", "PdCl2", e3, amounts=[amount("catalyst_loading", qty(5, "mol%"), e3)]),
        chemical("nai", "reagent", "NaI", e3, amounts=[amount("equivalents", qty(0.5, "equiv"), e3)]),
        chemical("dma", "solvent", "DMA", e3, name="N,N-dimethylacetamide"),
    ]
    records.append(record(
        f"scheme1_{tag}_1g", "reported_experiment", e3, participants,
        [{"step_id": "enantioenriched_homodimerization", "participant_ids": [x["entity_id"] for x in participants], "conditions": [field("temperature", qty(80, "°C"), e3), field("time", qty(hours, "h"), e3)]}],
        [
            field("starting_material_ee", qty(start_ee, "%"), e3, ["1g_enriched"]),
            field("reported_combined_product_yield", qty(yld, "%"), e3, ["E_product", "Z_product"]),
            field("E_Z_ratio", "95:5", e3, ["E_product", "Z_product"]),
            field("E_product_ee", qty(product_ee, "%"), e3, ["E_product"]),
            field("Z_product_ee", qty(product_ee, "%"), e3, ["Z_product"]),
        ],
        notes=[fact("The source states that no racemization was observed under the standard conditions.", e3)],
        unresolved=["Yield measurement basis, absolute quantities, atmosphere, workup, and purification are not reported.", "Axial/central stereochemical structures remain unverified."],
    ))


# Scheme 2 controls. The PdCl2 control duplicates Table 1 entry 1; only PdBr2/PdI2 add records.
for catalyst, hours, yld in [("PdBr2", 16, 65), ("PdI2", 5, 90)]:
    substrate, product = substrate_product("1a", "2a", e3)
    participants = [
        substrate, product,
        chemical(catalyst.lower(), "catalyst", catalyst, e3, amounts=[amount("catalyst_loading", qty(5, "mol%"), e3)]),
        chemical("dma", "solvent", "DMA", e3, name="N,N-dimethylacetamide"),
    ]
    records.append(record(
        f"scheme2_{catalyst.lower()}_control", "reported_experiment", e3, participants,
        [{"step_id": "halide_catalyst_control", "participant_ids": [x["entity_id"] for x in participants], "conditions": [field("temperature", qty(80, "°C"), e3), field("time", qty(hours, "h"), e3)]}],
        [field("reported_yield_2a", qty(yld, "%"), e3, ["2a"])],
        notes=[fact("The control was conducted without NaI.", e3)],
        unresolved=["Yield measurement basis, absolute quantities, atmosphere, workup, and purification are not reported.", "The 1a and 2a structures remain unverified."],
    ))


# Schemes 3 and 4: proposed chemistry only.
e34 = ev(3) + ev(4)
records.append(record(
    "scheme3_possible_mechanism", "mechanism", e34,
    [
        participant("1g", "reactant", "1g", e34, smiles=SMILES["1g"]),
        participant("2g", "product", "2g", e34),
        chemical("pdcl2", "catalyst", "PdCl2", e34),
        chemical("nai", "reagent", "NaI", e34),
        participant("pdi2", "unspecified_agent", "PdI2", e34, smiles=SMILES["PdI2"]),
        participant("m1", "unspecified_agent", "M1", e34),
        participant("m2", "unspecified_agent", "M2", e34),
    ], [], [],
    notes=[fact("Proposed sequence: cyclic oxypalladation to M1, regioselective carbopalladation to M2, trans-beta-hydroxide elimination, and regeneration of PdI2.", e34)],
    unresolved=["This is a proposed catalytic mechanism, not a set of independently executed experiments.", "Intermediate connectivity and charges remain unverified."],
))
records.append(record(
    "scheme4_stereoselectivity_rationale", "mechanism", e34,
    [participant("m3", "unspecified_agent", "M3", e34), participant("m4", "unspecified_agent", "M4", e34), participant("e_isomer", "product", "E-isomer (major)", e34), participant("z_isomer", "product", "Z-isomer (minor)", e34)],
    [], [],
    notes=[fact("The authors propose that thermodynamically favored M3 gives the E isomer through trans-beta-hydroxide elimination; M4 gives the minor Z isomer.", e34)],
    unresolved=["This is a stereochemical rationale, not an independently executed experiment.", "Generic R-group structures and palladium intermediates remain unverified."],
))


# Scheme 5 and its detailed page-4 procedure.
e45 = ev(4) + ev(5)
participants = [
    participant("2a", "reactant", "2a", e45, name="3-(1-cyclohexylidenemethylvinyl)-1-oxaspiro[4.5]dec-3-ene", amounts=[amount("mass", qty(387.8, "mg"), ev(4)), amount("amount", qty(1.5, "mmol"), ev(4))]),
    chemical("maleamide_3", "reactant", "3", e45, name="maleamide 3; N-phenylmaleimide structure shown", smiles_key="N-phenylmaleimide", amounts=[amount("mass", qty(519.3, "mg"), ev(4)), amount("amount", qty(3.0, "mmol"), ev(4)), amount("equivalents", qty(2, "equiv"), ev(4))]),
    participant("4aa", "product", "4aa", e45, name="major polycyclic Diels–Alder product", amounts=[amount("isolated_mass", qty(524.0, "mg"), ev(4))]),
    participant("4ab", "product", "4ab", e45, name="minor polycyclic Diels–Alder product", amounts=[amount("isolated_mass", qty(54.1, "mg"), ev(4))]),
    chemical("toluene", "solvent", "toluene", e45, amounts=[amount("volume", qty(15, "mL"), ev(4))]),
    chemical("ch2br2", "reagent", "CH2Br2", e45, name="dibromomethane internal standard", amounts=[amount("volume", qty(105, "uL"), ev(4)), amount("amount", qty(1.5, "mmol"), ev(4))]),
    participant("chromatography_eluent", "solvent", "petroleum ether/ethyl acetate 8:1", ev(4)),
]
records.append(record(
    "scheme5_diels_alder", "reported_experiment", e45, participants,
    [{"step_id": "diels_alder", "participant_ids": [x["entity_id"] for x in participants], "conditions": [
        field("temperature", qty(130, "°C"), ev(4)),
        field("operation", "reflux", ev(4)),
        field("time", qty(5, "h"), ev(4)),
        field("operation", "Monitor by TLC; cool to room temperature; evaporate; analyze crude mixture by 300 MHz 1H NMR with CH2Br2 internal standard", ev(4)),
        field("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate 8:1", ev(4)),
    ]}],
    [
        field("isolated_yield_4aa", qty(81, "%"), ev(4), ["4aa"]),
        field("isolated_yield_4ab", qty(8, "%"), ev(4), ["4ab"]),
        field("yield_measurement_basis", "isolated yield", ev(4), ["4aa", "4ab"]),
        field("4aa_4ab_ratio", "91:9", ev(4), ["4aa", "4ab"]),
        field("selectivity_measurement_basis", "300 MHz 1H NMR with CH2Br2 internal standard", ev(4), ["4aa", "4ab"]),
    ],
    notes=[fact("The major 4aa structure was further supported by X-ray diffraction; CCDC 651148 is cited, but no CIF is supplied in this workspace.", e45)],
    unresolved=["Reaction atmosphere is not reported.", "The printed procedure describes toluene reflux at 130 °C; the source wording is retained without correction.", "Product connectivity and relative stereochemistry remain unverified; the external CIF was not supplied."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

rid = lambda suffix: f"{DOC}:{suffix}"
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "center graphical abstract arrow", "finding": "Generic present-paper summary scheme with PdCl2/NaI/DMA/80 °C and a collective 58–92% scope range; classified as general_scheme rather than a single execution.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "title, abstract, and introduction", "finding": "Abstract-level claims and cited background reactions; no additional row-level present-paper experiment was created.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": [rid("graphical_summary_general_scheme")],
            "unresolved": ["Generic R-group structures and compound-specific yields are not supplied in the summary arrow."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Table 1 reaction arrow, rows 1–15, and footnotes", "finding": "Fifteen independent optimization conditions extracted with solvent/additive/time/yield, catalyst-loading exception, NMR-yield bases, and recovered-starting-material results.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "lower-right Results and Discussion prose", "finding": "Narrative interpretation of Table 1; facts were merged into table rows rather than duplicated.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "left column background methods and references", "finding": "Cited prior syntheses are literature context without row-level procedures on this page; no present-paper records were fabricated.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": [rid(f"table1_entry{i}") for i in range(1, 16)],
            "unresolved": ["Most optimization rows omit scale, atmosphere, workup, and purification.", "Complex structures remain machine-derived and unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top Scheme 1", "finding": "Two independent enantioenriched 1g homodimerizations extracted with times, yields, E/Z ratios, and starting/product ee values.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "middle-left Table 2", "finding": "Six scope rows inventoried; entry 1 is the same optimized 1a→2a execution as Table 1 entry 6 and was merged, while entries 2–6 remain independent.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "lower-left Table 3", "finding": "Five stereoselective scope rows extracted with isolated yields and the source-defined E/Z or Z/E ratios.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "middle-right Scheme 2 and mechanistic prose", "finding": "Three PdX2 controls inventoried; the PdCl2 case duplicates Table 1 entry 1, while PdBr2 and PdI2 are independent. Proposed Scheme 3/4 reasoning is classified as mechanism.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": [
                rid("scheme1_r_1g"), rid("scheme1_s_1g"), rid("table1_entry6"),
                *[rid(f"table2_entry{i}") for i in range(2, 7)],
                *[rid(f"table3_entry{i}") for i in range(1, 6)],
                rid("table1_entry1"), rid("scheme2_pdbr2_control"), rid("scheme2_pdi2_control"),
                rid("scheme3_possible_mechanism"), rid("scheme4_stereoselectivity_rationale"),
            ],
            "unresolved": ["Scheme/table scope rows generally omit absolute scale, atmosphere, workup, purification, and several yield bases.", "Product connectivity and stereochemical SMILES require expert review."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Schemes 3 and 4", "finding": "Proposed catalytic mechanism and stereoselectivity rationale classified as mechanism, not executed stepwise experiments.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "middle-left Scheme 5", "finding": "One Diels–Alder experiment extracted with separate 4aa/4ab yields and 91:9 ratio.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "lower-left and upper-right typical procedure for 2a", "finding": "Exact 1a/PdCl2/NaI/DMA quantities, 80 °C/5 h condition, workup, chromatography, product mass, and 86% isolated yield merged into Table 1 entry 6/Table 2 entry 1.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "right-column polycyclic-compound procedure and Figure 1", "finding": "Exact Diels–Alder quantities, operations, product masses/yields, and characterization linked to the Scheme 5 record; ORTEP is not a separate reaction.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            ],
            "record_ids": [rid("scheme3_possible_mechanism"), rid("scheme4_stereoselectivity_rationale"), rid("scheme5_diels_alder"), rid("table1_entry6")],
            "unresolved": ["Reaction atmospheres are not reported.", "The Diels–Alder procedure prints toluene reflux at 130 °C; this is retained verbatim.", "Product and intermediate structures remain unverified."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "top-left crystallographic-data continuation", "finding": "Continuation of 4aa crystal data and CCDC 651148; linked as characterization context, not a new reaction.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "acknowledgment and reproducibility statement", "finding": "The paper acknowledges reproduction of selected Table 2/3 entries; no new condition or independent result is supplied, so no duplicate experiment was created.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
                {"region": "Supporting Information Available statement", "finding": "Online SI availability is stated, but no SI file is supplied or explicitly associated in the workspace; no SI facts were imported.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            ],
            "record_ids": [rid("scheme5_diels_alder"), rid("table1_entry6"), rid("table2_entry4"), rid("table3_entry1"), rid("table3_entry4")],
            "unresolved": ["The external SI and CIF are not supplied or associated.", "Page 5 adds no independent reaction condition."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "record_file": str(OUT), "coverage_file": str(COVERAGE)}, ensure_ascii=False))
