import copy
import json
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
DOC = "doc_d5f73b0e7de4203e"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def q(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    return value


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, participant_ids, conditions):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": conditions,
    }


def record(suffix, evidence, participants, steps, outcomes, notes=None, unresolved=None,
           kind="reported_experiment"):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def get_participant(rec, entity_id):
    return next(p for p in rec["participants"] if p["entity_id"] == entity_id)


def add_evidence(rec, evidence):
    rec["evidence_ids"] = uniq(rec["evidence_ids"] + list(evidence))


dataset = json.loads((BASE / "dataset.json").read_text())
existing = {r["source_reaction_id"]: copy.deepcopy(r) for r in dataset["experiments"]}
records = []

# Page 7 completes the compound-specific 1a dimerization procedure. Preserve the
# Table 2 value (27%) and the detailed-procedure value (28%) as separate outcomes.
r = existing["table2_entry1_1a"]
add_evidence(r, ev(7))
get_participant(r, "p2_1a")["amounts"] = [field("isolated_product_mass", q(19, "mg"), ev(7))]
get_participant(r, "pepi2_1a")["amounts"] = [field("isolated_product_mass", q(9, "mg"), ev(7))]
r["outcomes"] += [
    field("detailed_procedure_isolated_yield", q(28, "%"), ev(7), ["p2_1a"]),
    field("detailed_procedure_isolated_yield", q(13, "%"), ev(7), ["pepi2_1a"]),
]
r["notes"].append(fact(
    "The compound-specific procedure reports 28% for 2a, whereas Table 2 reports 27%; both source values are retained.",
    ev(3) + ev(7),
))
r["review"]["unresolved"] = [
    "Table 2 reports 27% for 2a while the detailed page-7 procedure reports 28%; the source conflict is unresolved.",
    "Complex product structures and stereochemistry remain unverified; atmosphere is not reported.",
]
records.append(r)

# General Procedure III explicitly applies to 1f-1o. The exact 1f execution below
# overrides the nominal general-procedure scale, catalyst mass, and solvent volume.
table3_suffixes = [f"table3_entry{i}_{label}" for i, label in enumerate(
    ["1f", "1g", "1h", "1i", "1j", "1k", "1l", "1m", "1n"], 1
)]
for suffix in table3_suffixes + ["equation2_1o_to_3o"]:
    r = existing[suffix]
    add_evidence(r, ev(7))
    substrate_id = "substrate" if suffix.startswith("table3_") else "s1o"
    product_id = "product" if suffix.startswith("table3_") else "p3o"
    get_participant(r, substrate_id)["amounts"] = [field("amount", q(0.25, "mmol"), ev(7))]
    get_participant(r, "rhcat")["amounts"] = [
        field("catalyst_loading", q(5, "mol%"), ev(3)),
        field("mass", q(9, "mg"), ev(7)),
        field("amount", q(0.0125, "mmol"), ev(7)),
    ]
    toluene = get_participant(r, "toluene")
    toluene["label"] = fact("dry toluene", ev(7))
    toluene["amounts"] = [field("volume", q(6, "mL"), ev(7))]
    old_time = next(c for c in r["steps"][0]["conditions"] if c["name"] == "time")
    r["steps"] = [step("unimolecular_cyclization", [substrate_id, "rhcat", "toluene", product_id], [
        field("temperature", "reflux", ev(7)),
        old_time,
        field("atmosphere", "argon", ev(7)),
        field("operation", "reaction completion monitored by TLC (petroleum ether/ethyl acetate 10:1)", ev(7)),
        field("workup", "rotary evaporation", ev(7)),
        field("purification", "flash chromatography on silica gel (petroleum ether/ethyl ether 20:1)", ev(7)),
    ])]
    r["review"]["unresolved"] = [
        "Reflux is reported qualitatively without a numerical temperature.",
        "Complex substrate/product connectivity and stereochemistry remain unverified.",
    ]
    records.append(r)

# Replace the general-procedure quantities for 1f with its compound-specific values.
r = next(x for x in records if x["source_reaction_id"] == "table3_entry1_1f")
get_participant(r, "substrate")["name"] = fact(
    "3'-phenylprop-2'-ynyl 2-benzyl-4-methylpenta-2,3-dienoate", ev(7)
)
get_participant(r, "substrate")["amounts"] = [
    field("mass", q(64, "mg"), ev(7)),
    field("amount", q(0.20, "mmol"), ev(7)),
]
get_participant(r, "rhcat")["amounts"] = [
    field("catalyst_loading", q(5, "mol%"), ev(3)),
    field("mass", q(7, "mg"), ev(7)),
    field("amount", q(0.01, "mmol"), ev(7)),
]
get_participant(r, "toluene")["amounts"] = [field("volume", q(5, "mL"), ev(7))]
get_participant(r, "product")["amounts"] = [field("isolated_product_mass", q(43, "mg"), ev(7))]
r["notes"].append(fact("Some starting material remained; no numerical recovery was reported.", ev(7)))

# The 4p trapping experiment is described by Scheme 4 and an exact procedure that
# begins on page 7 and whose characterization continues onto page 8.
r = existing["scheme4_1p_trapping_with_3_methoxyprop_1_yne"]
add_evidence(r, ev(7) + ev(8))
get_participant(r, "s1p")["amounts"] = [
    field("mass", q(46, "mg"), ev(7)), field("amount", q(0.15, "mmol"), ev(7))
]
get_participant(r, "trap")["amounts"] = [
    field("mass", q(110, "mg"), ev(7)), field("amount", q(1.57, "mmol"), ev(7))
]
get_participant(r, "rhcat")["amounts"] = [
    field("catalyst_loading", q(5, "mol%"), ev(4)),
    field("mass", q(6, "mg"), ev(7)), field("amount", q(0.0087, "mmol"), ev(7)),
]
toluene = get_participant(r, "toluene")
toluene["label"] = fact("dry toluene", ev(7))
toluene["amounts"] = [field("volume", q(3.6, "mL"), ev(7))]
get_participant(r, "p4p")["amounts"] = [field("isolated_product_mass", q(28, "mg"), ev(7))]
r["steps"] = [step("cyclization_trapping_aromatization",
    ["s1p", "trap", "rhcat", "toluene", "p4p"], [
        field("scheme_temperature", "reflux", ev(4)),
        field("scheme_time", q(12, "h"), ev(4)),
        field("detailed_procedure_temperature", q(110, "°C"), ev(7)),
        field("detailed_procedure_time", q(10, "h"), ev(7)),
        field("operation", "heated in a reaction tube with a screw cap", ev(7)),
    ])]
r["outcomes"] = [
    field("isolated_yield", q(50, "%"), ev(7), ["p4p"]),
    field("yield_measurement_basis", "isolated", ev(7), ["p4p"]),
]
r["review"]["unresolved"] = [
    "Scheme 4 reports reflux for 12 h, whereas the detailed procedure reports 110 °C for 10 h; both are retained.",
    "Atmosphere, workup, purification, and complex structures are not reported or remain unverified.",
]
records.append(r)

# Detailed DIBAL-H reduction of 3f to 11f.
r = existing["scheme6_dibal_reduction_3f_to_11f"]
add_evidence(r, ev(8))
get_participant(r, "s3f")["name"] = fact(
    "(Z)-3-benzyl-5-benzylidene-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one", ev(8)
)
get_participant(r, "s3f")["amounts"] = [
    field("mass", q(50, "mg"), ev(8)), field("amount", q(0.16, "mmol"), ev(8))
]
get_participant(r, "dibal")["label"] = fact("DIBAL-H (1 M in toluene)", ev(8))
get_participant(r, "dibal")["amounts"] = [
    field("concentration", q(1, "M"), ev(8)), field("volume", q(0.64, "mL"), ev(8))
]
get_participant(r, "p11f")["name"] = fact(
    "(Z)-3-benzyl-5-benzylidene-4-(prop-1-en-2-yl)-5,6-dihydro-2H-pyran-2-ol", ev(8)
)
get_participant(r, "p11f")["amounts"] = [field("isolated_product_mass", q(55, "mg"), ev(8))]
r["participants"][2:2] = [
    participant("thf", "solvent", "dry THF", ev(8), smiles="C1CCOC1",
                amounts=[field("volume", q(1, "mL"), ev(8))]),
    participant("sat_nacl", "reagent", "saturated NaCl", ev(8)),
    participant("ether", "solvent", "ether", ev(8), name="diethyl ether", smiles="CCOCC"),
    participant("na2so4", "reagent", "Na2SO4", ev(8)),
]
r["steps"] = [step("carbonyl_reduction",
    ["s3f", "dibal", "thf", "sat_nacl", "ether", "na2so4", "p11f"], [
        field("temperature", q(-78, "°C"), ev(8)),
        field("addition_time", q(5, "min"), ev(8)),
        field("operation", "DIBAL-H solution was added to the substrate solution", ev(8)),
        field("workup", "quenched with saturated NaCl; extracted with ether; dried over Na2SO4; filtered and evaporated", ev(8)),
        field("purification", "column chromatography on silica gel", ev(8)),
    ])]
r["outcomes"] = [
    field("scheme_reported_yield", "quantitative", ev(6), ["p11f"]),
    field("detailed_isolated_yield", q(100, "%"), ev(8), ["p11f"]),
    field("yield_measurement_basis", "isolated", ev(8), ["p11f"]),
]
r["review"]["unresolved"] = [
    "Atmosphere and complex structures are not independently verified.",
]
records.append(r)

# Detailed regioselective hydrogenation of 3f to 12f.
r = existing["scheme6_hydrogenation_3f_to_12f"]
add_evidence(r, ev(8))
get_participant(r, "s3f")["name"] = fact(
    "(Z)-3-benzyl-5-benzylidene-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one", ev(8)
)
get_participant(r, "s3f")["amounts"] = [
    field("mass", q(47, "mg"), ev(8)), field("amount", q(0.15, "mmol"), ev(8))
]
get_participant(r, "pdc")["amounts"] = [field("mass", q(5, "mg"), ev(8))]
get_participant(r, "p12f")["amounts"] = [field("isolated_product_mass", q(42, "mg"), ev(8))]
r["participants"].insert(3, participant(
    "methanol", "solvent", "CH3OH", ev(8), name="methanol", smiles="CO",
    amounts=[field("volume", q(1, "mL"), ev(8))]
))
r["steps"] = [step("selective_hydrogenation",
    ["s3f", "pdc", "h2", "methanol", "p12f"], [
        field("atmosphere", "1 atm H2", ev(8)),
        field("temperature", "room temperature", ev(8)),
        field("time", q(5, "h"), ev(8)),
        field("workup", "evaporation", ev(8)),
        field("purification", "column chromatography on silica gel", ev(8)),
    ])]
r["outcomes"] = [
    field("isolated_yield", q(88, "%"), ev(8), ["p12f"]),
    field("yield_measurement_basis", "isolated", ev(8), ["p12f"]),
]
r["review"]["unresolved"] = [
    "Complex substrate/product structures and product stereochemistry remain unverified.",
]
records.append(r)

# Detailed NIS conversion of the TMS-bearing 3m to iodide 13m. Page 5 printed 3l;
# Scheme 7 and the detailed procedure print 3m, so the source conflict remains explicit.
r = existing["page5_nis_iodination_to_13m"]
add_evidence(r, ev(7) + ev(8))
silane = get_participant(r, "silane")
silane["label"] = fact("3m", ev(7) + ev(8))
silane["name"] = fact(
    "3-methyl-5-methylene-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one", ev(8)
)
silane["amounts"] = [
    field("mass", q(118, "mg"), ev(8)), field("amount", q(0.50, "mmol"), ev(8))
]
get_participant(r, "nis")["amounts"] = [
    field("mass", q(230, "mg"), ev(8)), field("amount", q(1.02, "mmol"), ev(8))
]
get_participant(r, "p13m")["name"] = fact(
    "(Z)-5-(iodomethylene)-3-methyl-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one", ev(8)
)
get_participant(r, "p13m")["amounts"] = [field("isolated_product_mass", q(128, "mg"), ev(8))]
r["participants"].insert(2, participant(
    "mecn", "solvent", "dry CH3CN", ev(8), name="acetonitrile", smiles="CC#N",
    amounts=[field("volume", q(4, "mL"), ev(8))]
))
r["steps"] = [step("iodination", ["silane", "nis", "mecn", "p13m"], [
    field("temperature", "reflux", ev(8)),
    field("time", q(10, "h"), ev(8)),
    field("workup", "evaporation", ev(8)),
    field("purification", "column chromatography on silica gel", ev(8)),
])]
r["outcomes"] = [
    field("isolated_yield", q(88, "%"), ev(8), ["p13m"]),
    field("yield_measurement_basis", "isolated", ev(8), ["p13m"]),
]
r["notes"] = [fact(
    "Page-5 prose labels the vinylic silane as 3l, while Scheme 7 and the detailed page-8 procedure label it 3m; the latter also supplies the explicit TMS-bearing context.",
    ev(5) + ev(7) + ev(8),
)]
r["review"]["unresolved"] = [
    "The source contains a 3l/3m starting-material label conflict; no silent correction is certified.",
    "Reflux is qualitative, atmosphere is not reported, and complex structures remain unverified.",
    "The printed HRMS found value (298.9809) differs from the calculated value (289.9804); analytical data are not otherwise structured here.",
]
records.append(r)


def coupling_record(suffix, product_label, product_name, substrate_mass, substrate_mmol,
                    partner, catalyst_participants, base_participant, solvent, conditions,
                    product_mass, product_yield, participant_ids, notes=None, unresolved=None):
    evidence = ev(7) + ev(8)
    parts = [
        participant("s13m", "reactant", "13m", evidence,
                    name="(Z)-5-(iodomethylene)-3-methyl-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one",
                    amounts=[field("mass", q(substrate_mass, "mg"), ev(8)),
                             field("amount", q(substrate_mmol, "mmol"), ev(8))]),
        partner,
        *catalyst_participants,
        base_participant,
        solvent,
        participant("product", "product", product_label, evidence, name=product_name,
                    amounts=[field("isolated_product_mass", q(product_mass, "mg"), ev(8))]),
    ]
    return record(
        suffix, evidence, parts,
        [step("coupling", participant_ids, conditions + [
            field("workup", "evaporation", ev(8)),
            field("purification", "column chromatography on silica gel", ev(8)),
        ])],
        [field("isolated_yield", q(product_yield, "%"), ev(8), ["product"]),
         field("yield_measurement_basis", "isolated", ev(8), ["product"])],
        notes=notes,
        unresolved=unresolved or ["Complex reactant/product structures and stereochemistry remain unverified."],
    )


records.append(coupling_record(
    "scheme7_suzuki_13m_to_14m", "14m",
    "(Z)-5-(m-methoxybenzylidene)-3-methyl-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one",
    44, 0.15,
    participant("boronic_acid", "reactant", "3-methoxyphenylboronic acid", ev(7) + ev(8),
                smiles="COc1cccc(B(O)O)c1",
                amounts=[field("mass", q(45, "mg"), ev(8)), field("amount", q(0.3, "mmol"), ev(8))]),
    [participant("pdpph34", "catalyst", "Pd(PPh3)4", ev(7) + ev(8),
                 amounts=[field("mass", q(9, "mg"), ev(8)), field("catalyst_loading", q(5, "mol%"), ev(7) + ev(8))])],
    participant("k3po4_3h2o", "reagent", "K3PO4·3H2O", ev(7) + ev(8),
                amounts=[field("mass", q(81, "mg"), ev(8)), field("amount", q(0.3, "mmol"), ev(8)),
                         field("equivalents", q(2, "equiv"), ev(7))]),
    participant("toluene", "solvent", "toluene", ev(7) + ev(8), smiles="Cc1ccccc1",
                amounts=[field("volume", q(2, "mL"), ev(8))]),
    [field("temperature", "reflux", ev(7) + ev(8)), field("time", q(10, "min"), ev(7) + ev(8)),
     field("atmosphere", "argon", ev(8))],
    34, 83,
    ["s13m", "boronic_acid", "pdpph34", "k3po4_3h2o", "toluene", "product"],
))

records.append(coupling_record(
    "scheme7_suzuki_13m_to_15m", "15m",
    "3-methyl-5-(Z)-(((E)-3-phenylvinyl)methylene)-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one",
    40, 0.14,
    participant("styrylboronic_acid", "reactant", "(E)-styrylboronic acid", ev(7) + ev(8),
                amounts=[field("mass", q(41, "mg"), ev(8)), field("amount", q(0.28, "mmol"), ev(8))]),
    [participant("pdpph34", "catalyst", "Pd(PPh3)4", ev(7) + ev(8),
                 amounts=[field("mass", q(8, "mg"), ev(8)), field("catalyst_loading", q(5, "mol%"), ev(7) + ev(8))])],
    participant("k3po4_3h2o", "reagent", "K3PO4·3H2O", ev(7) + ev(8),
                amounts=[field("mass", q(76, "mg"), ev(8)), field("amount", q(0.28, "mmol"), ev(8)),
                         field("equivalents", q(2, "equiv"), ev(7))]),
    participant("toluene", "solvent", "toluene", ev(7) + ev(8), smiles="Cc1ccccc1",
                amounts=[field("volume", q(2, "mL"), ev(8))]),
    [field("temperature", "reflux", ev(7) + ev(8)), field("time", q(0.5, "h"), ev(7) + ev(8)),
     field("atmosphere", "argon", ev(8))],
    52, 100,
    ["s13m", "styrylboronic_acid", "pdpph34", "k3po4_3h2o", "toluene", "product"],
))

records.append(coupling_record(
    "scheme7_sonogashira_13m_to_16m", "16m",
    "(Z)-3-methyl-5-(3-phenylprop-2-ynylidene)-4-(prop-1-en-2-yl)-5,6-dihydropyran-2-one",
    39, 0.14,
    participant("phenylacetylene", "reactant", "phenylacetylene", ev(7) + ev(8), smiles="C#Cc1ccccc1",
                amounts=[field("mass", q(32, "mg"), ev(8)), field("amount", q(0.3, "mmol"), ev(8))]),
    [participant("pdcl2_pph3_2", "catalyst", "PdCl2(PPh3)2", ev(7) + ev(8),
                 amounts=[field("mass", q(5, "mg"), ev(8)), field("catalyst_loading", q(5, "mol%"), ev(7) + ev(8))]),
     participant("cui", "catalyst", "CuI", ev(7) + ev(8),
                 amounts=[field("mass", q(4, "mg"), ev(8)), field("catalyst_loading", q(10, "mol%"), ev(7) + ev(8))])],
    participant("k2co3", "reagent", "K2CO3", ev(7) + ev(8), smiles="[K+].[K+].[O-]C([O-])=O",
                amounts=[field("mass", q(42, "mg"), ev(8)), field("amount", q(0.3, "mmol"), ev(8)),
                         field("equivalents", q(2, "equiv"), ev(7))]),
    participant("mecn", "solvent", "CH3CN", ev(7) + ev(8), name="acetonitrile", smiles="CC#N",
                amounts=[field("volume", q(2, "mL"), ev(8))]),
    [field("temperature", "room temperature", ev(7) + ev(8)), field("time", q(1, "h"), ev(7) + ev(8)),
     field("atmosphere", "argon", ev(8))],
    33, 93,
    ["s13m", "phenylacetylene", "pdcl2_pph3_2", "cui", "k2co3", "mecn", "product"],
))


out = BASE / "raw_model" / "records_pages_0007_0008.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

rid = lambda suffix: f"{DOC}:{suffix}"
gp3_ids = [rid(x) for x in table3_suffixes + ["equation2_1o_to_3o"]]
scheme7_ids = [
    rid("page5_nis_iodination_to_13m"),
    rid("scheme7_suzuki_13m_to_14m"),
    rid("scheme7_suzuki_13m_to_15m"),
    rid("scheme7_sonogashira_13m_to_16m"),
]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper half, Scheme 7",
                    "finding": "Four present-paper transformations were inventoried: NIS conversion of 3m to 13m and three separate coupling reactions of 13m to 14m, 15m, and 16m. The 13m experiment updates an existing record; the three couplings are new records.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "lower-left continuation of 2a/epi-2a preparation and General Procedure III",
                    "finding": "The cross-page 1a dimerization was merged into Table 2 entry 1, retaining its 28% detailed-procedure yield alongside the table's 27%. General Procedure III quantities, argon, TLC, workup, and purification were merged into the existing 1f-1o cyclization records.",
                    "evidence_ids": ev(7),
                },
                {
                    "region": "lower-right exact 3f procedure and beginning of 4p mechanistic-study procedure",
                    "finding": "Exact 3f masses/scale and the exact 1p trapping quantities, 110 °C/10 h condition, product mass, and isolated yield were merged into existing records; 4p characterization continues on page 8.",
                    "evidence_ids": ev(7),
                },
            ],
            "record_ids": uniq([rid("table2_entry1_1a"), *scheme7_ids, *gp3_ids,
                                rid("scheme4_1p_trapping_with_3_methoxyprop_1_yne")]),
            "unresolved": [
                "Table 2 gives 27% 2a, while the detailed procedure gives 28%.",
                "Scheme 4 gives reflux/12 h for 4p, while the detailed procedure gives 110 °C/10 h.",
                "Complex structures and stereochemistry remain unverified.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of 4p characterization",
                    "finding": "Continuation of the same page-7 trapping experiment; analytical data support product identity but do not define another reaction.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "left column synthetic applications 1-3",
                    "finding": "Detailed DIBAL-H reduction to 11f, Pd/C-H2 hydrogenation to 12f, and NIS iodination to 13m were merged into their existing records with quantities, conditions, workup/purification, product masses, and isolated yields.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "lower-left and right column synthetic applications 4-6",
                    "finding": "Three distinct coupling experiments of 13m were extracted: Suzuki reactions yielding 14m and 15m, and a Sonogashira reaction yielding 16m.",
                    "evidence_ids": ev(8),
                },
                {
                    "region": "lower-right acknowledgments and Supporting Information Available statement",
                    "finding": "No additional reaction is present. SI availability is stated, but no SI file was supplied or explicitly associated, so no SI-derived facts were imported.",
                    "evidence_ids": ev(8),
                },
            ],
            "record_ids": uniq([
                rid("scheme4_1p_trapping_with_3_methoxyprop_1_yne"),
                rid("scheme6_dibal_reduction_3f_to_11f"),
                rid("scheme6_hydrogenation_3f_to_12f"),
                *scheme7_ids,
            ]),
            "unresolved": [
                "The page-5 prose labels the TMS substrate 3l, while Scheme 7 and the detailed procedure label it 3m.",
                "The 13m HRMS found/calculated values are inconsistent as printed.",
                "No supporting-information document is associated; complex structures and stereochemistry remain unverified.",
            ],
        },
    ],
}
(BASE / "coverage").mkdir(parents=True, exist_ok=True)
(BASE / "coverage" / "pages_0007_0008.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("task_id") in {
        f"{DOC}:page7:text", f"{DOC}:page8:text"
    }:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "updated_records": 15,
    "new_records": 3,
    "records_file": str(out),
    "coverage_pages": len(coverage["pages"]),
}, ensure_ascii=False))
