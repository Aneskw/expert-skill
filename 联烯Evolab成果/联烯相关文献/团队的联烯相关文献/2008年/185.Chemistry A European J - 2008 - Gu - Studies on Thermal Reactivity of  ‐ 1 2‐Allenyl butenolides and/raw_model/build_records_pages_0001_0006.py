import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_efbb5564c1bec50d"


def evidence(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, ev, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, ev, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name is not None else fact(None, []),
        "smiles": fact(smiles, ev) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def record(suffix, kind, pages, participants, conditions=None, outcomes=None,
           notes=None, unresolved=None, source_id=None):
    ev = []
    for page in pages:
        ev.extend(evidence(page))
    ev = list(dict.fromkeys(ev))
    conditions = conditions or []
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants,
        "steps": ([{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if conditions else []),
        "outcomes": outcomes or [],
        "notes": [fact(text, ev) for text in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []


def add_nonexperimental(suffix, kind, page, summary, unresolved):
    ev = evidence(page)
    records.append(record(
        suffix, kind, [page], [], notes=[summary], unresolved=unresolved,
    ))


# Pages 1–2: cited prior work and proposed pathways.
add_nonexperimental(
    "scheme1_vitamin_d_17h_shift_literature", "literature_example", 1,
    "Scheme 1 reproduces a cited vitamin-D-type 1,7-hydrogen-shift stereochemical example from Hoeger et al.",
    ["The cited experiment's quantities, conditions, yields, and complete structures are not supplied on page 1."],
)
add_nonexperimental(
    "scheme2_vinylallene_15h_shift_literature", "literature_example", 1,
    "Scheme 2 reproduces cited vinylallene pericyclic chemistry and shows two stereochemical products after thermal 1,5-H shift.",
    ["The page gives no row-level procedure or yield for the cited work."],
)

ev2 = evidence(2)
records.append(record(
    "scheme3_backvall_allene_ene_literature", "literature_example", [2],
    [
        participant("scheme3_substrate", "reactant", "Backvall allene–ene substrate", ev2),
        participant("scheme3_major", "product", "major Alder–ene product", ev2),
        participant("scheme3_minor", "product", "minor product", ev2),
        participant("dmf", "solvent", "DMF", ev2, name="N,N-dimethylformamide", smiles="CN(C)C=O"),
    ],
    conditions=[field("solvent", "DMF", ev2), field("temperature", q(120, "°C"), ev2), field("reaction_time", q(24, "h"), ev2)],
    outcomes=[
        field("reported_yield", q(84, "%"), ev2, ["scheme3_major", "scheme3_minor"]),
        field("product_ratio", "90:10", ev2, ["scheme3_major", "scheme3_minor"]),
    ],
    unresolved=["This is cited prior work; scale, atmosphere, workup, purification, and yield basis are absent."],
))
records.append(record(
    "scheme4_prior_pi_bond_migration", "literature_example", [2],
    [
        participant("scheme4_allenoic_acid", "reactant", "2,3-allenoic acid substrate (E = CO2Me)", ev2),
        participant("scheme4_alkyne", "reactant", "methyl propiolate (E = CO2Me)", ev2, name="dimethyl acetylenedicarboxylate", smiles="COC(=O)C#CC(=O)OC"),
        participant("scheme4_product_a", "product", "previously reported migration product A", ev2),
        participant("scheme4_product_b", "product", "previously reported migration product B", ev2),
        participant("scheme4_pd", "catalyst", "Pd(OAc)2", ev2),
        participant("scheme4_sc", "catalyst", "Sc(OTf)3", ev2),
        participant("scheme4_bf3", "reagent", "BF3·Et2O", ev2),
        participant("scheme4_solvent", "solvent", "CCl3Me", ev2, name="1,1,1-trichloroethane", smiles="CC(Cl)(Cl)Cl"),
    ],
    conditions=[field("solvent", "CCl3Me", ev2), field("temperature", q(35, "°C"), ev2), field("reaction_time", None, ev2)],
    outcomes=[field("reported_yield", None, ev2, ["scheme4_product_a", "scheme4_product_b"])],
    unresolved=["This is explicitly prior work; catalyst loadings, time, product ratio, yield, and operational details are not printed."],
))
add_nonexperimental(
    "scheme4_double_17h_shift_mechanism", "mechanism", 2,
    "Scheme 4 proposes π-bond migration through intermediates A and B via two 1,7-hydrogen shifts.",
    ["The intermediates are proposed and were not treated as separately executed experiments."],
)


# Scheme 5: preparation of starting beta-allenylfuranones 1a–t.
scheme5_rows = [
    ("1a", "alpha-naphthyl", "H", "nPr", "Et", "Et", 71),
    ("1b", "Ph", "H", "iBu", "Me", "Me", 38),
    ("1c", "Ph", "H", "iBu", "Et", "Et", 49),
    ("1d", "Ph", "H", "Bn", "Me", "Me", 39),
    ("1e", "Ph", "H", "CH2CH(CH2)2 (cyclopropylmethyl)", "Me", "Me", 45),
    ("1f", "Ph", "H", "allyl", "Et", "Et", 72),
    ("1g", "Ph", "H", "allyl", "Me", "Me", 60),
    ("1h", "Ph", "H", "allyl", "-(CH2)5-", "-(CH2)5-", 63),
    ("1i", "Me", "Me", "allyl", "Et", "Et", 83),
    ("1j", "Me", "Me", "allyl", "Et", "Me", 66),
    ("1k", "Me", "Me", "allyl", "Me", "Ph", 79),
    ("1l", "alpha-naphthyl", "H", "allyl", "Et", "Et", 80),
    ("1m", "alpha-naphthyl", "H", "allyl", "Me", "Me", 63),
    ("1n", "4-BrC6H4", "H", "allyl", "Et", "Et", 59),
    ("1o", "4-BrC6H4", "H", "allyl", "Me", "Me", 46),
    ("1p", "Et", "H", "allyl", "Et", "Et", 72),
    ("1q", "Et", "H", "allyl", "-(CH2)5-", "-(CH2)5-", 58),
    ("1r", "Ph", "H", "allyl", "-(CH2)4-", "-(CH2)4-", 43),
    ("1s", "Me", "Me", "allyl", "-(CH2)4-", "-(CH2)4-", 73),
    ("1t", "4-BrC6H4", "H", "allyl", "-(CH2)4-", "-(CH2)4-", 44),
]
for label, r1, r2, r3, r4, r5, yield_value in scheme5_rows:
    rid = f"scheme5_prepare_{label}"
    product_id = f"product_{label}"
    participants = [
        participant(f"allenoic_acid_{label}", "reactant", f"2,3-allenoic acid for {label} (R1={r1}, R2={r2}, R3={r3})", ev2),
        participant(f"propargyl_carbonate_{label}", "reactant", f"propargyl carbonate for {label} (R4={r4}, R5={r5})", ev2),
        participant("pd_oac2", "catalyst", "Pd(OAc)2", ev2, amounts=[field("catalyst_loading", q(5, "mol%"), ev2)]),
        participant("tfp", "catalyst", "TFP", ev2, name="tri-2-furylphosphine", amounts=[field("catalyst_loading", q(10, "mol%"), ev2)]),
        participant("k2co3", "reagent", "K2CO3", ev2, amounts=[field("equivalents", q(1, "equiv"), ev2)]),
        participant("dmso", "solvent", "DMSO", ev2, name="dimethyl sulfoxide", smiles="CS(C)=O"),
        participant(product_id, "product", f"beta-allenylfuranone {label} (R1={r1}, R2={r2}, R3={r3}, R4={r4}, R5={r5})", ev2),
    ]
    records.append(record(
        rid, "substrate_scope_entry", [2], participants,
        conditions=[field("solvent", "DMSO", ev2), field("temperature", None, ev2), field("reaction_time", None, ev2), field("atmosphere", None, ev2)],
        outcomes=[field("reported_yield", q(yield_value, "%"), ev2, [product_id]), field("yield_measurement_basis", None, ev2, [product_id])],
        unresolved=["Scheme 5 omits scale, temperature, time, atmosphere, workup, purification, and yield basis.", "R-group connectivity and product stereochemistry remain unverified."],
    ))


# Scheme 6: Negishi preparation of 2a–d.
scheme6_rows = [("2a", "H", 64), ("2b", "Me", 81), ("2c", "nBu", 81), ("2d", "Ph", 56)]
for label, rgroup, yield_value in scheme6_rows:
    product_id = f"product_{label}"
    participants = [
        participant(f"enone_halide_{label}", "reactant", f"2-allyl-3-(I or OTf)cyclohex-2-enone precursor for {label} (R={rgroup})", ev2),
        participant("allenyl_zinc", "reactant", "allenylic zinc reagent", ev2),
        participant("pd_pph3_2cl2", "catalyst", "Pd(PPh3)2Cl2", ev2, amounts=[field("catalyst_loading", {"minimum": 2, "maximum": 5, "unit": "mol%", "raw_text": "2–5 mol%"}, ev2)]),
        participant("thf", "solvent", "THF", ev2, name="tetrahydrofuran", smiles="C1CCOC1"),
        participant(product_id, "product", f"2-allyl-3-allenylcyclohex-2-enone {label} (R={rgroup})", ev2),
    ]
    records.append(record(
        f"scheme6_prepare_{label}", "substrate_scope_entry", [2], participants,
        conditions=[field("solvent", "THF", ev2), field("temperature", None, ev2), field("reaction_time", None, ev2), field("atmosphere", None, ev2)],
        outcomes=[field("reported_yield", q(yield_value, "%"), ev2, [product_id]), field("yield_measurement_basis", None, ev2, [product_id])],
        unresolved=["Scheme 6 omits scale, time, temperature, atmosphere, workup, purification, and yield basis.", "The precursor leaving group is presented generically as I or OTf."],
    ))


# Scheme 7 reported thermal isomerization and its proposed hydrogen-shift sequence.
records.append(record(
    "scheme7_1a_to_3a_isomers", "reported_experiment", [2, 3],
    [
        participant("substrate_1a", "reactant", "beta-allenylfuranone 1a", ev2),
        participant("product_ee_3a", "product", "(E,E)-3a", ev2),
        participant("product_ez_3a", "product", "(E,Z)-3a", ev2),
        participant("xylene", "solvent", "xylene", ev2),
    ],
    conditions=[field("solvent", "xylene", ev2), field("temperature", "reflux", ev2), field("reaction_time", q(6, "h"), ev2), field("atmosphere", None, ev2)],
    outcomes=[
        field("isolated_yield_ee_3a", q(29, "%"), ev2, ["product_ee_3a"]),
        field("isolated_yield_ez_3a", q(7, "%"), ev2, ["product_ez_3a"]),
        field("yield_measurement_basis", "isolated", ev2, ["product_ee_3a", "product_ez_3a"]),
    ],
    notes=["Unidentified products were also formed; Figure 1 on page 3 is an ORTEP of (E,Z)-3a."],
    unresolved=["Scale, atmosphere, workup, purification, and unidentified-product identities are not given within pages 1–6."],
))
add_nonexperimental(
    "scheme7_15h_then_17h_mechanism", "mechanism", 2,
    "Scheme 7 proposes 1a to conformers 4a/4b/4c by 1,5-H shift, followed by 1,7-H shift to the two 3a stereoisomers.",
    ["Intermediates 4a–c are mechanistic structures, not isolated reaction records."],
)


def thermal_record(suffix, pages, substrate, products, temp, time, yields, solvent="xylene", atmosphere=None, notes=None, unresolved=None, outcomes_extra=None):
    ev = []
    for page in pages:
        ev += evidence(page)
    parts = [participant(f"substrate_{substrate}", "reactant", substrate, ev)]
    for product in products:
        parts.append(participant(f"product_{product}", "product", product, ev))
    parts.append(participant("xylene", "solvent", solvent, ev))
    outs = []
    for product, value in zip(products, yields):
        outs.append(field(f"reported_yield_{product}", value, ev, [f"product_{product}"]))
    outs += outcomes_extra or []
    records.append(record(
        suffix, "reported_experiment", pages, parts,
        conditions=[field("solvent", solvent, ev), field("temperature", temp, ev), field("reaction_time", time, ev), field("atmosphere", atmosphere, ev)],
        outcomes=outs,
        notes=notes,
        unresolved=unresolved or ["Scale, workup, purification, and yield basis are not fully reported within pages 1–6."],
    ))


ev3 = evidence(3)
thermal_record("scheme8_1b_to_e3b", [3], "1b", ["(E)-3b"], "reflux", q(3.5, "h"), [q(72, "%")])
thermal_record(
    "scheme8_1c_to_e3c", [3], "1c", ["(E)-3c"], "reflux", q(6, "h"), [q(66, "%")],
    outcomes_extra=[field("recovered_starting_material_yield", q(10, "%"), ev3, ["substrate_1c"])],
)
thermal_record(
    "scheme9_1d_to_5d", [3], "1d", ["5d"], q(200, "°C"), q(5, "h"), [q(70, "%")],
    notes=["Reaction conducted in xylene in a sealed screw-cap Schlenk tube; trans/cis = 1.9:1."],
    outcomes_extra=[field("trans_cis_ratio", "1.9:1", ev3, ["product_5d"])],
)
thermal_record(
    "scheme10_1e_to_5e", [3, 4], "1e", ["5e"], "reflux", q(5, "h"), [q(74, "%")],
    notes=["No triene 3e was formed according to the page-3 discussion; Scheme 10 attributes 5e formation to 6pi electrocyclization."],
    outcomes_extra=[field("trans_cis_ratio", "1.6:1", evidence(4), ["product_5e"]), field("triene_3e_result", "not formed", ev3)],
)

ev4 = evidence(4)
thermal_record(
    "scheme11_1f_to_6f", [4], "1f", ["6f"], q(100, "°C"), q(6, "h"), [q(89, "%")],
    outcomes_extra=[field("yield_measurement_basis", "isolated", ev4, ["product_6f"])],
)


# Table 1, one record per substrate row.
table1_rows = [
    (1, "1g", "Ph", "H", "Me", "Me", 84, 7),
    (2, "1h", "Ph", "H", "-(CH2)5-", "-(CH2)5-", 80, 6),
    (3, "1i", "Me", "Me", "Et", "Et", 83, 6),
    (4, "1j", "Me", "Me", "Me", "Et", 74, 6),
    (5, "1k", "Me", "Me", "Ph", "Me", 48, 6),
    (6, "1l", "alpha-naphthyl", "H", "Et", "Et", 97, 6),
    (7, "1m", "alpha-naphthyl", "H", "Me", "Me", 87, 6),
    (8, "1n", "p-BrC6H4", "H", "Et", "Et", 95, 6),
    (9, "1o", "p-BrC6H4", "H", "Me", "Me", 84, 6),
    (10, "1p", "Et", "H", "Et", "Et", 84, 6),
    (11, "1q", "Et", "H", "-(CH2)5-", "-(CH2)5-", 89, 6),
]
for entry, substrate, r1, r2, r3, r4, yield_value, hours in table1_rows:
    product = "6" + substrate[1:]
    sid = f"substrate_{substrate}"
    pid = f"product_{product}"
    parts = [
        participant(sid, "reactant", f"{substrate} (R1={r1}, R2={r2}, R3={r3}, R4={r4})", ev4, amounts=[field("reaction_scale", {"minimum": 0.15, "maximum": 0.25, "unit": "mmol", "raw_text": "0.15–0.25 mmol"}, ev4)]),
        participant(pid, "product", product, ev4),
        participant("xylene", "solvent", "xylene", ev4, amounts=[field("volume", q(4, "mL"), ev4)]),
    ]
    records.append(record(
        f"table1_entry{entry}_{substrate}", "substrate_scope_entry", [4], parts,
        conditions=[field("solvent", "xylene", ev4), field("temperature", q(100, "°C"), ev4), field("reaction_time", q(hours, "h"), ev4), field("atmosphere", "argon", ev4)],
        outcomes=[field("reported_yield", q(yield_value, "%"), ev4, [pid]), field("yield_measurement_basis", None, ev4, [pid])],
        unresolved=["Table 1 omits workup, purification, and yield measurement basis; complex structures and stereochemistry remain unverified."],
    ))


# Scheme 12, three independent cycloisomerizations with Diels–Alder coproducts.
scheme12_rows = [
    ("1r", "R1=Ph, R2=H", "6r", 67, "7r", 12, "1:1"),
    ("1s", "R1=R2=Me", "6s", 74, "7s", 14, None),
    ("1t", "R1=4-BrC6H4, R2=H", "6t", 66, "7t", 11, "1:1"),
]
for substrate, subdesc, p6, y6, p7, y7, dr in scheme12_rows:
    extra = []
    if dr:
        extra.append(field("diastereomer_ratio", dr, ev4, [f"product_{p7}"]))
    thermal_record(
        f"scheme12_{substrate}_to_{p6}_{p7}", [4], f"{substrate} ({subdesc})", [p6, p7], q(100, "°C"), q(6, "h"), [q(y6, "%"), q(y7, "%")],
        outcomes_extra=extra,
    )


# Page 5 prose / page 6 drawings: trapping and cycloisomerization experiments.
ev56 = evidence(5) + evidence(6)
records.append(record(
    "scheme13_2a_dimerization", "reported_experiment", [4, 6],
    [
        participant("substrate_2a", "reactant", "2a", ev56),
        participant("product_8aa", "product", "8aa", ev56),
        participant("product_8ab", "product", "8ab", ev56),
        participant("xylene", "solvent", "xylene", ev56),
    ],
    conditions=[field("solvent", "xylene", ev56), field("temperature", q(80, "°C"), ev56), field("reaction_time", q(3, "h"), ev56), field("atmosphere", None, ev56)],
    outcomes=[field("combined_reported_yield", q(81, "%"), evidence(6), ["product_8aa", "product_8ab"]), field("product_ratio", "8aa:8ab = 1:1.3", evidence(6), ["product_8aa", "product_8ab"]), field("yield_measurement_basis", None, ev56, ["product_8aa", "product_8ab"])],
    notes=["The products are described as intermolecular Diels–Alder products of two molecules of possible intermediate 9a."],
    unresolved=["Scale, atmosphere, workup, purification, individual product yields, and yield basis are absent within pages 1–6."],
))
records.append(record(
    "scheme13_bromination_8ab", "reported_experiment", [4, 6],
    [
        participant("substrate_8ab", "reactant", "8ab", ev56),
        participant("br2", "reagent", "Br2", ev56, smiles="BrBr"),
        participant("ch2cl2", "solvent", "CH2Cl2", ev56, name="dichloromethane", smiles="ClCCl"),
        participant("product_10aba", "product", "10aba", ev56),
        participant("product_10abb", "product", "10abb", ev56),
    ],
    conditions=[field("solvent", "CH2Cl2", ev56), field("temperature", None, ev56), field("reaction_time", q(15, "min"), ev56), field("atmosphere", None, ev56)],
    outcomes=[field("combined_reported_yield", q(96, "%"), evidence(6), ["product_10aba", "product_10abb"]), field("product_ratio", "10aba:10abb = 1.5:1", evidence(6), ["product_10aba", "product_10abb"]), field("yield_measurement_basis", None, ev56, ["product_10aba", "product_10abb"])],
    unresolved=["Scale, bromine amount, temperature, atmosphere, workup, purification, individual product yields, and yield basis are absent within pages 1–6."],
))
add_nonexperimental(
    "scheme14_alternative_cycloisomerization_pathway", "mechanism", 6,
    "Scheme 14 proposes [2+2] allene–ene cycloaddition to 11, 1,5-H shift to 12, and electrocyclic rearrangement to 5.",
    ["The pathway is explicitly proposed; intermediates 11 and 12 were not treated as executed experiments."],
)


traps = [
    ("13a", "maleic anhydride", "O=C1OC(=O)C=C1", "14aa", 24, 49),
    ("13b", "N-ethylmaleimide", "CCN1C(=O)C=CC1=O", "14ab", 72, 77),
    ("13c", "N-phenylmaleimide", "O=C1C=CC(=O)N1c2ccccc2", "14ac", 36, 91),
    ("13d", "dimethyl acetylenedicarboxylate", "COC(=O)C#CC(=O)OC", "14ad", 34, 52),
]
for trap, trap_name, trap_smiles, product, hours, yield_value in traps:
    ev6 = evidence(6)
    records.append(record(
        f"scheme15_2a_{trap}_to_{product}", "substrate_scope_entry", [5, 6],
        [
            participant("substrate_2a", "reactant", "2a", ev6),
            participant(f"reactant_{trap}", "reactant", trap, ev6, name=trap_name, smiles=trap_smiles),
            participant(f"product_{product}", "product", product, ev6),
            participant("xylene", "solvent", "xylene", ev6),
        ],
        conditions=[field("solvent", "xylene", ev6), field("temperature", q(55, "°C"), ev6), field("reaction_time", q(hours, "h"), ev6), field("atmosphere", None, ev6)],
        outcomes=[field("reported_yield", q(yield_value, "%"), ev6, [f"product_{product}"]), field("yield_measurement_basis", None, ev6, [f"product_{product}"])],
        notes=["The page-4/5 prose states that trapping products 14 were formed as a single diastereomer / highly stereoselectively."],
        unresolved=["Scale, atmosphere, workup, purification, exact selectivity value, and yield basis are absent within pages 1–6."],
    ))


scheme16_rows = [
    ("2b", "R=Me", [("15b", 56)]),
    ("2c", "R=nBu", [("15c", 57), ("9c", 8)]),
    ("2d", "R=Ph", [("15d", 77)]),
]
for substrate, desc, products in scheme16_rows:
    thermal_record(
        f"scheme16_{substrate}_cycloisomerization", [5, 6], f"{substrate} ({desc})",
        [p for p, _ in products], q(90, "°C"), q(2, "h"), [q(y, "%") for _, y in products],
    )

ev6 = evidence(6)
records.append(record(
    "scheme17_16_to_9e", "reported_experiment", [5, 6],
    [
        participant("substrate_16", "reactant", "16", ev6),
        participant("triethyl_orthoacetate", "reactant", "CH3C(OEt)3", ev6, name="triethyl orthoacetate", smiles="CC(OCC)(OCC)OCC"),
        participant("product_9e", "product", "9e", ev6),
        participant("xylene", "solvent", "xylene", ev6),
    ],
    conditions=[field("solvent", "xylene", ev6), field("temperature", q(140, "°C"), ev6), field("reaction_time", None, ev6), field("atmosphere", None, ev6)],
    outcomes=[field("reported_yield", q(41, "%"), ev6, ["product_9e"]), field("yield_measurement_basis", None, ev6, ["product_9e"])],
    notes=["The text describes 2e as generated in situ by a Claisen-type rearrangement and 9e as the tricyclic product instead of an eight-membered ring."],
    unresolved=["Scale, reagent loading, duration, atmosphere, workup, purification, yield basis, and any intermediate-2e yield are absent within pages 1–6."],
))
records.append(record(
    "scheme18_15b_13b_to_14bb", "reported_experiment", [5, 6],
    [
        participant("substrate_15b", "reactant", "15b", ev6),
        participant("reactant_13b", "reactant", "13b", ev6, name="N-ethylmaleimide", smiles="CCN1C(=O)C=CC1=O"),
        participant("product_14bb", "product", "14bb", ev6),
        participant("xylene", "solvent", "xylene", ev6),
    ],
    conditions=[field("solvent", "xylene", ev6), field("temperature", q(55, "°C"), ev6), field("reaction_time", q(24, "h"), ev6), field("atmosphere", None, ev6)],
    outcomes=[field("reported_yield", q(53, "%"), ev6, ["product_14bb"]), field("recovered_starting_material_yield", q(28, "%"), ev6, ["substrate_15b"]), field("yield_measurement_basis", None, ev6, ["product_14bb"])],
    unresolved=["Scale, atmosphere, workup, purification, and yield/recovery bases are absent within pages 1–6."],
))


# Mechanistic-probe syntheses and isotope experiments explicitly described in page-5/6 prose.
ev5 = evidence(5)
records.append(record(
    "d5_allyl_mesylate_24_synthesis", "reported_experiment", [5],
    [participant("product_d5_24", "product", "[D5]-24-(allyl), fully deuterated allyl mesylate", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d5_24"])],
    notes=["The synthesis is stated to follow procedures established by Lebeau et al.; Scheme 20 and detailed procedure lie beyond page 6."],
    unresolved=["Reactants, quantities, solvent, conditions, operations, and yield are not stated on page 5."],
))
records.append(record(
    "d5_25_cui_coupling", "reported_experiment", [5],
    [participant("d5_24", "reactant", "[D5]-24-(allyl)", ev5), participant("phenyl_propynol", "reactant", "1-phenylprop-2-yn-1-ol", ev5), participant("cui", "catalyst", "CuI", ev5), participant("product_d5_25", "product", "[D5]-25-(allyl)", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d5_25"])],
    unresolved=["Page 5 omits quantities, solvent, temperature, time, atmosphere, workup, purification, and yield."],
))
records.append(record(
    "d5_26_palladium_carbonylation", "reported_experiment", [5],
    [participant("d5_25", "reactant", "[D5]-25-(allyl)", ev5), participant("co", "reagent", "CO", ev5, smiles="[C-]#[O+]"), participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev5), participant("product_d5_26", "product", "2,3-allenoic acid [D5]-26-(allyl)", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", "CO atmosphere", ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d5_26"])],
    unresolved=["Page 5 omits quantities, solvent, temperature, time, workup, purification, CO pressure, and yield."],
))
records.append(record(
    "d5_1g_cross_coupling", "reported_experiment", [5],
    [participant("d5_26", "reactant", "[D5]-26-(allyl)", ev5), participant("methyl_propargyl_carbonate", "reactant", "methyl 2-methylbut-3-yn-2-yl carbonate", ev5), participant("product_d5_1g", "product", "[D5]-1g-(allyl)", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d5_1g"]), field("allenyl_center_deuterium_content", q(93, "%"), ev5, ["product_d5_1g"])],
    unresolved=["Page 5 omits catalyst identity/loading, quantities, solvent, temperature, time, atmosphere, workup, purification, and yield."],
))
records.append(record(
    "d5_1g_cycloisomerization", "reported_experiment", [5],
    [participant("substrate_d5_1g", "reactant", "[D5]-1g-(allyl)", ev5), participant("product_d5_6g", "product", "[D5]-6g", ev5), participant("xylene", "solvent", "xylene", ev5)],
    conditions=[field("solvent", "xylene", ev5), field("temperature", q(110, "°C"), ev5), field("reaction_time", q(6, "h"), ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", q(64, "%"), ev5, ["product_d5_6g"]), field("deuterium_incorporation_at_4_position", q(82, "%"), ev5, ["product_d5_6g"]), field("approximate_deuterium_incorporation_in_two_methyl_groups", q(3, "%", qualifier="approx", raw_text="~3%"), ev5, ["product_d5_6g"]), field("yield_measurement_basis", None, ev5, ["product_d5_6g"])],
    notes=["The authors interpret the change from 93% D at the precursor allenyl-center carbon to 82% D at product C4 as about 18% deuterium loss."],
    unresolved=["Scale, atmosphere, workup, purification, and yield basis are absent within pages 1–6."],
))
records.append(record(
    "d6_27_synthesis", "reported_experiment", [5],
    [participant("ethynylmagnesium_bromide", "reactant", "ethynylmagnesium bromide", ev5), participant("acetone_d6", "reactant", "CD3COCD3", ev5), participant("product_d6_27", "product", "[D6]-27-(CD3)2-H(D)", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d6_27"])],
    unresolved=["Page 5 omits quantities, solvent, temperature, time, atmosphere, workup, purification, yield, and exact terminal-H/D composition."],
))
records.append(record(
    "d6_28_carbonate_synthesis", "reported_experiment", [5],
    [participant("d6_27", "reactant", "[D6]-27-(CD3)2-H(D)", ev5), participant("product_d6_28_hd", "product", "propargyl carbonate [D6]-28-(CD3)2-H(D)", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d6_28_hd"])],
    notes=["The 1H NMR spectrum is said to show partial deuteration at the terminal alkyne."],
    unresolved=["Carbonylating reagent, quantities, solvent, conditions, operations, yield, and terminal D fraction are not stated on page 5."],
))
records.append(record(
    "d6_28_terminal_h_d_exchange", "reported_experiment", [5],
    [participant("d6_28_hd", "reactant", "[D6]-28-(CD3)2-H(D)", ev5), participant("nbuli", "reagent", "nBuLi", ev5), participant("water", "reagent", "water", ev5, smiles="O"), participant("thf", "solvent", "THF", ev5, smiles="C1CCOC1"), participant("product_d6_28", "product", "[D6]-28-(CD3)2", ev5)],
    conditions=[field("solvent", "THF", ev5), field("temperature", q(-78, "°C"), ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5), field("operation", "nBuLi treatment followed by quenching with water at -78 °C", ev5)],
    outcomes=[field("reported_yield", None, ev5, ["product_d6_28"])],
    unresolved=["Quantities, reaction time, atmosphere, workup, purification, yield, and final isotope fraction are absent on page 5."],
))
records.append(record(
    "d6_1g_cross_coupling", "reported_experiment", [5],
    [participant("allenoic_acid_allyl_ph", "reactant", "2-allyl-4-phenylbuta-2,3-dienoic acid", ev5), participant("d6_28", "reactant", "[D6]-28-(CD3)2", ev5), participant("pd_catalyst_unspecified", "catalyst", "palladium catalyst (identity not stated in page-5 prose)", ev5), participant("product_d6_1g", "product", "[D6]-1g-(CD3)2", ev5)],
    conditions=[field("temperature", None, ev5), field("reaction_time", None, ev5), field("atmosphere", None, ev5)],
    outcomes=[field("reported_yield", q(54, "%"), ev5, ["product_d6_1g"]), field("deuterium_content", q(95, "%"), ev5, ["product_d6_1g"]), field("yield_measurement_basis", None, ev5, ["product_d6_1g"])],
    unresolved=["Page 5 omits exact catalyst, quantities, solvent, temperature, time, atmosphere, workup, purification, and yield basis."],
))
records.append(record(
    "d6_1g_cycloisomerization", "reported_experiment", [5, 6],
    [participant("substrate_d6_1g", "reactant", "[D6]-1g-(CD3)2", ev56), participant("product_d6_6g", "product", "[D6]-6g", ev56), participant("xylene", "solvent", "xylene", ev56)],
    conditions=[field("solvent", "xylene", ev56), field("temperature", q(110, "°C"), ev56), field("reaction_time", q(6, "h"), ev56), field("atmosphere", None, ev56)],
    outcomes=[field("reported_yield", q(73, "%"), ev56, ["product_d6_6g"]), field("deuterium_incorporation_at_4_position", q(60, "%"), ev56, ["product_d6_6g"]), field("methyl_group_deuterium_content_after_reaction", q(85, "%"), evidence(6), ["product_d6_6g"]), field("yield_measurement_basis", None, ev56, ["product_d6_6g"])],
    notes=["The substrate methyl-group deuterium content is reported to drop from 95% to 85%."],
    unresolved=["Scale, atmosphere, workup, purification, and yield basis are absent within pages 1–6."],
))
add_nonexperimental(
    "scheme24_isotope_supported_pathway", "mechanism", 6,
    "Page-6 prose proposes 1,5-H shift of 1A to 18A/20A, 8pi electrocyclization of 18A to 6A, and 20A/18A interconversion through 29A by sequential 1,7-H shifts, supported by the deuterium-labeling results.",
    ["Scheme 24 itself is printed on page 7; this record cites only the page-6 prose and does not claim page-7 coverage."],
)


# Coverage ledger for exactly pages 1–6.
by_page = {page: [] for page in range(1, 7)}
for item in records:
    for eid in item["evidence_ids"]:
        for page in range(1, 7):
            if eid.startswith(f"{DOC}:page{page}:"):
                by_page[page].append(item["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, Schemes 1–2", "finding": "No present-paper row-level experiment; Schemes 1–2 are cited prior-work examples and the abstract is a summary of later chemistry.", "evidence_ids": evidence(1)},
                {"region": "supporting-information availability statement", "finding": "Online availability is stated, but no SI file is supplied or explicitly associated; no SI facts were imported.", "evidence_ids": evidence(1)},
            ],
            "record_ids": list(dict.fromkeys(by_page[1])),
            "unresolved": ["The cited prior-work procedures and full structure assignments are not available from page 1.", "Machine semantic accuracy and structures remain unverified."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 3", "finding": "One cited Backvall intramolecular allene–ene example classified as literature, with 120 °C/24 h/84% and 90:10 shown.", "evidence_ids": evidence(2)},
                {"region": "middle-left Scheme 4", "finding": "One cited prior π-bond-migration reaction and its proposed double-1,7-H-shift pathway classified separately.", "evidence_ids": evidence(2)},
                {"region": "lower-left Scheme 5", "finding": "Twenty independent beta-allenylfuranone starting-material preparations (1a–t) extracted row by row with shared catalysts/base/solvent and row yields.", "evidence_ids": evidence(2)},
                {"region": "upper-right Scheme 6", "finding": "Four independent Negishi preparations of 2a–d extracted.", "evidence_ids": evidence(2)},
                {"region": "lower-right Scheme 7", "finding": "Thermal 1a isomerization extracted once; the proposed 1,5-H/1,7-H sequence is a separate mechanism record.", "evidence_ids": evidence(2)},
            ],
            "record_ids": list(dict.fromkeys(by_page[2])),
            "unresolved": ["Schemes 5–6 omit most operational details and yield bases.", "Generic R-group structures and complex product stereochemistry remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Figure 1 and upper-left prose", "finding": "ORTEP of (E,Z)-3a linked to Scheme 7; no duplicate reaction created.", "evidence_ids": evidence(3)},
                {"region": "lower-left Scheme 8", "finding": "Independent thermal reactions of 1b and 1c extracted; the 10% recovery for 1c remains recovery, not product yield.", "evidence_ids": evidence(3)},
                {"region": "upper-right Scheme 9", "finding": "Sealed 200 °C conversion of 1d to 5d extracted with yield and trans/cis ratio.", "evidence_ids": evidence(3)},
                {"region": "right-column Figure 2 and Scheme-10 discussion", "finding": "ORTEP structures are characterization; the 1e-to-5e reaction continues onto page 4 and is linked cross-page.", "evidence_ids": evidence(3)},
            ],
            "record_ids": list(dict.fromkeys(by_page[3])),
            "unresolved": ["Several procedures omit scale, atmosphere, workup, purification, and yield basis."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 10", "finding": "Thermal 1e-to-5e electrocyclization extracted with reflux/5 h/74% and trans/cis 1.6:1; nonformation of 3e retained qualitatively.", "evidence_ids": evidence(4)},
                {"region": "middle-left Scheme 11", "finding": "Thermal 1f-to-6f cycloisomerization extracted with 100 °C/6 h/89% isolated yield.", "evidence_ids": evidence(4)},
                {"region": "lower-left Table 1 and footnotes", "finding": "All 11 substrate-scope rows extracted independently; argon, 0.15–0.25 mmol, 4 mL xylene, 100 °C/6 h apply to each row, with the 7 h footnote only on entry 1.", "evidence_ids": evidence(4)},
                {"region": "upper-right Scheme 12 and Figure 3", "finding": "Three independent 1r/1s/1t reactions extracted with separate 6 and 7 product yields; Figure 3 is characterization of 7s.", "evidence_ids": evidence(4)},
                {"region": "lower-right cyclohexenone discussion", "finding": "Narrative facts for 2a dimerization, 8ab bromination, and proposed Scheme 14 were linked to the page-6 records rather than duplicated.", "evidence_ids": evidence(4)},
            ],
            "record_ids": list(dict.fromkeys(by_page[4])),
            "unresolved": ["Table 1 does not state yield basis or workup/purification.", "The exact Scheme-12 dr for 7s is not printed in the arrow row."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "left-column Figure 4 and trapping/cycloisomerization prose", "finding": "ORTEP figures are characterization; prose facts for 13d trapping, 2b–d cycloisomerization, 16-to-9e, and 15b/13b trapping were merged with page-6 arrows.", "evidence_ids": evidence(5)},
                {"region": "right-column deuterium-labeling prose", "finding": "The stated [D5] and [D6] precursor syntheses and cycloisomerization probes were extracted as partial present-paper experiments with isotope outcomes preserved.", "evidence_ids": evidence(5)},
            ],
            "record_ids": list(dict.fromkeys(by_page[5])),
            "unresolved": ["Schemes 19–23 and detailed procedures lie after page 6; only facts explicit in page-5 prose were used.", "Several isotope-synthesis stages lack quantities, times, yields, and operational details on this page."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 13", "finding": "2a dimerization and subsequent 8ab bromination extracted as two experiments with combined yields and product ratios.", "evidence_ids": evidence(6)},
                {"region": "middle-left Scheme 14", "finding": "Alternative [2+2]/1,5-H/electrocyclic pathway classified as mechanism.", "evidence_ids": evidence(6)},
                {"region": "lower-left trapping arrows for 13a–d", "finding": "Four independent 2a trapping experiments extracted with row-specific time and yield.", "evidence_ids": evidence(6)},
                {"region": "center-right Schemes 16–18", "finding": "Three 2b–d cycloisomerizations, the 16-to-9e reaction, and the 15b/13b trapping experiment extracted independently; 28% recovered 15b remains recovery.", "evidence_ids": evidence(6)},
                {"region": "right-column Scheme-24 prose and lower-left isotope result", "finding": "Proposed isotope-supported hydrogen-shift pathway classified as mechanism; [D6]-6g isotope outcome linked to its page-5 experiment.", "evidence_ids": evidence(6)},
            ],
            "record_ids": list(dict.fromkeys(by_page[6])),
            "unresolved": ["Scheme 24 drawing is on page 7 and is not claimed as covered; only page-6 prose was recorded.", "Most scheme arrows omit scale, atmosphere, workup, purification, and yield basis."],
        },
    ],
}


raw_path = OUT / "raw_model/records_pages_0001_0006.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(OUT / "coverage/pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["task_id"] == f"{DOC}:page{page}:text" for page in range(1, 7)):
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
