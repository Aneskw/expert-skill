#!/usr/bin/env python3
"""Build evidence-linked records for ol006639p, original PDF pages 1-3."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs/current"
DOC = "doc_f58881a5665e6040"
RAW = RUN / "raw_model/records_pages_0001_0003.json"
COVERAGE = RUN / "coverage/pages_0001_0003.json"


def evidence(*pages: int) -> list[str]:
    ids: list[str] = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return ids


def fact(value, ev: list[str]):
    return {
        "value": value,
        "evidence_ids": [] if value is None else ev,
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name: str, value, ev: list[str]):
    return {"name": name, "fact": fact(value, ev)}


def participant(
    entity_id: str,
    role: str,
    label,
    name,
    ev: list[str],
    amounts: list[tuple[str, object]] | None = None,
):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev),
        "smiles": fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(k, v, ev) for k, v in (amounts or [])],
    }


COMMON_UNRESOLVED = [
    "No Supporting Information file is supplied or explicitly associated; the main text announces a typical procedure and analytical data, but these details remain unavailable.",
    "Structures are conveyed by drawings and labels; all SMILES remain null and unverified.",
]


def record(
    rid: str,
    kind: str,
    pages: tuple[int, ...],
    participants: list[dict],
    conditions: list[tuple[str, object]],
    outcomes: list[tuple[str, object]],
    notes: list[object],
    unresolved: list[str],
):
    ev = evidence(*pages)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": ev,
        "participants": participants,
        "steps": [
            {
                "step_id": "step1",
                "participant_ids": [p["entity_id"] for p in participants],
                "conditions": [field(k, v, ev) for k, v in conditions],
            }
        ],
        "outcomes": [field(k, v, ev) for k, v in outcomes],
        "notes": [fact(v, ev) for v in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved + COMMON_UNRESOLVED,
        },
    }


records: list[dict] = []

# The graphical abstract and Table 2 header are repeated generic presentations of
# the current chemistry; they are one generic transformation, not an experiment.
ev12 = evidence(1, 2)
records.append(
    record(
        "generic_iodohydroxylation",
        "general_scheme",
        (1, 2),
        [
            participant("generic_1", "reactant", "1", "allenyl phenyl sulfoxide family", ev12),
            participant("generic_i2", "reagent", "I2", "iodine", ev12),
            participant("generic_h2o", "reagent", "H2O", "water", ev12),
            participant("generic_2", "product", "2", "(E)-2-iodo-3-hydroxy-1-alkenyl phenyl sulfoxide family", ev12),
        ],
        [("medium", "aqueous MeCN"), ("additive", "LiOAc shown in Table 2 template")],
        [
            ("product_geometry", "E"),
            ("reported_regioselectivity", "excellent"),
            ("reported_stereoselectivity", "excellent"),
            ("reported_yield_assessment", "high or excellent")
        ],
        ["Generic R1/R2/R3 transformation; individual Table 2 rows are separate records."],
        ["Generic scheme does not state a unique scale, iodine loading, time, or isolated yield."],
    )
)

ev1 = evidence(1)
records.append(
    record(
        "scheme1_halohydroxylation_concept",
        "general_scheme",
        (1,),
        [
            participant("scheme1_alkene_or_allene", "reactant", "alkene/allene", "generic carbon-carbon unsaturated substrate", ev1),
            participant("scheme1_x2", "reagent", "X2", "halogen", ev1),
            participant("scheme1_h2o", "reagent", "H2O", "water", ev1),
            participant("scheme1_product", "product", "halohydrin products", "generic halohydroxylation products", ev1),
        ],
        [],
        [("conceptual_result", "Scheme contrasts ordinary alkene halohydroxylation with multiple possible regio- and stereoisomeric allene products")],
        ["Conceptual Scheme 1; no specific substrate, conditions, or yield are reported."],
        ["The generic allene product structures contain unresolved R groups and X identity."],
    )
)

ev12 = evidence(1, 2)
records.append(
    record(
        "scheme2_initial_1a_discovery",
        "reported_experiment",
        (1, 2),
        [
            participant("s2_1a", "reactant", "1a", "(1,2-propadienylsulfinyl)benzene", ev12),
            participant("s2_i2", "reagent", "I2", "iodine", ev12),
            participant("s2_hoac", "solvent", "HOAc", "acetic acid", ev12),
            participant("s2_h2o", "reagent", "H2O", "water", ev12),
            participant("s2_e2a", "product", "E-2a", "(E)-3-(phenylsulfinyl)-2-iodopropenol", ev12),
            participant("s2_3a", "product", "3A", "possible diiodide 3A", ev12),
            participant("s2_3b", "product", "3B", "possible diiodide 3B", ev12),
        ],
        [("stage_1_medium", "HOAc"), ("stage_1_temperature", {"number": -60, "unit": "°C"}), ("stage_2_operation", "H2O addition/quench shown after the first arrow")],
        [
            ("E-2a_yield", "low; numerical yield not reported"),
            ("E-2a_regioselectivity", "excellent"),
            ("E-2a_stereoselectivity", "excellent"),
            ("3A_observed", False),
            ("3B_observed", False),
            ("E-2a_configuration_assignment", "unambiguously established by X-ray diffraction")
        ],
        ["The page-1 discovery prose continues into Scheme 2 on page 2 and is represented once."],
        ["Iodine amount, reaction time, scale, workup, purification, and exact numerical yield are not reported in the supplied main text."],
    )
)


table1 = [
    # entry, I2 equiv, additive, time h, temperature, product yield, recovered 1a
    (1, 1.0, None, 5, "rt", 49, 34),
    (2, 2.0, None, 4, "rt", 66, 0),
    (3, 2.0, "K2CO3", 4, "rt", 3.9, 84),
    (4, 1.5, "LiOAc", 4, 55, 62, 29),
    (5, 2.0, "NaHCO3", 2.5, 65, 64, 0),
    (6, 2.0, "LiOAc", 5, "rt", 69, 18),
    (7, 2.0, "LiOAc", 0.2, 55, 60, 0),
    (8, 2.4, "LiOAc", 1, 55, 96, 0),
]

for entry, i2eq, additive, time_h, temp, yield_pct, recovered_pct in table1:
    ev = evidence(2)
    parts = [
        participant("t1_1a", "reactant", "1a", "(1,2-propadienylsulfinyl)benzene", ev, [("amount", {"number": 1, "unit": "mmol"})]),
        participant("t1_i2", "reagent", "I2", "iodine", ev, [("equivalents", {"number": i2eq, "unit": "equiv"})]),
        participant("t1_solvent", "solvent", "MeCN-H2O", "aqueous acetonitrile", ev),
        participant("t1_e2a", "product", "E-2a", "(E)-3-(phenylsulfinyl)-2-iodopropenol", ev),
    ]
    if additive:
        parts.insert(2, participant("t1_additive", "reagent", additive, additive, ev))
    cond = [
        ("time", {"number": time_h, "unit": "h"}),
        ("temperature", temp if temp == "rt" else {"number": temp, "unit": "°C"}),
        ("MeCN_volume", {"number": 2, "unit": "mL"}),
    ]
    if entry == 7:
        cond.append(("water_amount", {"number": 4.0, "unit": "equiv"}))
    else:
        cond.append(("water_volume", {"number": 0.3, "unit": "mL"}))
    outs = [
        ("E-2a_isolated_yield", {"number": yield_pct, "unit": "%"}),
        ("recovered_1a", {"number": recovered_pct, "unit": "%"}),
    ]
    notes = ["Table 1 isolated yield is based on 1a."]
    unresolved = ["Additive amount, atmosphere, concentration, workup, purification, and isolated mass are not reported in the supplied main text."]
    if entry == 2:
        notes.append("The prose reports some byproducts of low polarity.")
    if entry == 6:
        notes.append("The prose describes exclusive formation of E-2a under this row, with 18% starting material recovered.")
    if entry == 8:
        outs.append(("prose_reported_I2_equivalents", {"number": 2.0, "unit": "equiv"}))
        notes.append("Table 1 prints 2.4 equiv I2, whereas adjacent prose states 2.0 equiv for the 55 °C, 1 h, 96% result.")
        unresolved.append("Source conflict: Table 1 entry 8 prints 2.4 equiv I2 while prose reports 2.0 equiv; both values are retained.")
    records.append(
        record(
            f"table1_entry{entry}",
            "optimization_entry",
            (2,),
            parts,
            cond,
            outs,
            notes,
            unresolved,
        )
    )


table2 = [
    # entry, substrate, product, R1, R2, R3, I2 eq, time h, yield, temperature
    (1, "1a", "E-2a", "H", "H", "H", 2.4, 1, 96, 55),
    (2, "1b", "E-2b", "Ph", "H", "H", 1.6, 2.2, 79, "rt"),
    (3, "1c", "E-2c", "n-Bu", "H", "H", 1.6, 1.5, 82, "rt"),
    (4, "1d", "E-2d", "H", "H", "t-Bu", 1.2, 3.2, 87, "rt"),
    (5, "1e", "E-2e", "H", "Me", "Me", 1.2, 0.5, 87, "rt"),
    (6, "1f", "E-2f", "H", "(CH2)5", "(CH2)5; joined to R2", 1.2, 0.3, 74, "rt"),
    (7, "1g", "E-2g", "n-Bu", "Me", "Me", 1.2, 1.3, 88, "rt"),
]

for entry, substrate, product, r1, r2, r3, i2eq, time_h, yield_pct, temp in table2:
    ev = evidence(2)
    parts = [
        participant("t2_substrate", "reactant", substrate, f"allenyl phenyl sulfoxide {substrate}", ev, [("amount", {"number": 0.5, "unit": "mmol"})]),
        participant("t2_i2", "reagent", "I2", "iodine", ev, [("equivalents", {"number": i2eq, "unit": "equiv"})]),
        participant("t2_lioac", "reagent", "LiOAc", "lithium acetate", ev, [("amount", {"number": 1, "unit": "mmol"})]),
        participant("t2_solvent", "solvent", "MeCN-H2O (7:1 v/v)", "aqueous acetonitrile", ev, [("total_volume", {"number": 1, "unit": "mL"})]),
        participant("t2_product", "product", product, f"(E)-iodohydroxylation product {product}", ev),
    ]
    outs = [("isolated_yield", {"number": yield_pct, "unit": "%"}), ("product_geometry", "E")]
    notes = [{"R1": r1, "R2": r2, "R3": r3}, "Isolated yield of E-2 is based on substrate 1."]
    unresolved = ["Atmosphere, concentration, workup, purification, isolated mass, and numerical regio-/stereoselectivity are not reported in the supplied main text."]
    if entry == 1:
        unresolved.append("This row matches Table 1 entry 8 in time, temperature, iodine loading printed in the table, and yield, but Table 2 specifies a 0.5 mmol scale while Table 1 specifies 1 mmol; retained as a separate scope run.")
    if entry == 4:
        outs.extend([
            ("starting_material_de", "93:7"),
            ("product_de", "93:7"),
            ("product_de_measurement", "1H NMR spectra and HPLC"),
        ])
    records.append(
        record(
            f"table2_entry{entry}",
            "substrate_scope_entry",
            (2,),
            parts,
            [
                ("time", {"number": time_h, "unit": "h"}),
                ("temperature", "room temperature" if temp == "rt" else {"number": temp, "unit": "°C"}),
                ("solvent_ratio", "MeCN:H2O = 7:1 v/v"),
            ],
            outs,
            notes,
            unresolved,
        )
    )


ev3 = evidence(3)
records.append(
    record(
        "scheme3_diiodination_12_decadiene",
        "reported_experiment",
        (3,),
        [
            participant("s3_decadiene", "reactant", "C7H15-substituted terminal allene", "1,2-decadiene", ev3),
            participant("s3_i2", "reagent", "I2", "iodine", ev3),
            participant("s3_h2o", "reagent", "H2O", "water", ev3),
            participant("s3_lioac", "reagent", "LiOAc", "lithium acetate", ev3),
            participant("s3_mecn", "solvent", "aqueous MeCN", "aqueous acetonitrile", ev3),
            participant("s3_product", "product", "diiodination product", "1,2-diiodo-2-decene", ev3),
        ],
        [("temperature", "room temperature"), ("time", {"number": 1, "unit": "h"})],
        [("configurational_isomer_ratio", "88:12")],
        ["Under the iodohydroxylation conditions, the non-sulfinyl allene gives the diiodination product."],
        ["Reagent amounts, scale, exact aqueous-MeCN composition, yield, yield basis, workup, purification, and absolute configuration of the 88:12 isomers are not reported."],
    )
)

records.append(
    record(
        "scheme3_allenoate_unidentified_mixture",
        "reported_experiment",
        (3,),
        [
            participant("s3_allenoate", "reactant", "C6H13/CO2C2H5-substituted allene", "ethyl allenoate substrate shown in Scheme 3", ev3),
            participant("s3b_i2", "reagent", "I2", "iodine", ev3),
            participant("s3b_h2o", "reagent", "H2O", "water", ev3),
            participant("s3b_lioac", "reagent", "LiOAc", "lithium acetate", ev3),
            participant("s3b_mecn", "solvent", "aqueous MeCN", "aqueous acetonitrile", ev3),
            participant("s3b_products", "product", "unidentified mixture", "unidentified product mixture", ev3),
        ],
        [("temperature", "room temperature"), ("time", {"number": 1, "unit": "h"})],
        [("result", "unidentified mixture")],
        ["Scheme 3 lower-row comparison; no discrete product identity is assigned."],
        ["Exact substrate systematic name/structure, reagent amounts, scale, aqueous-MeCN composition, component identities, yields, workup, and purification are not reported."],
    )
)


RAW.parent.mkdir(parents=True, exist_ok=True)
RAW.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "graphical abstract and abstract",
                    "finding": "Generic current-paper iodohydroxylation of allenyl phenyl sulfoxides to (E)-2-iodo-3-hydroxy-1-alkenyl sulfoxides; this is a general scheme, not an individual run.",
                    "evidence_ids": evidence(1),
                },
                {
                    "region": "Scheme 1 and adjacent introductory prose",
                    "finding": "Conceptual alkene/allene halohydroxylation scheme illustrating the regio-/stereoselectivity challenge; no specific experiment or yield.",
                    "evidence_ids": evidence(1),
                },
                {
                    "region": "right-column discovery prose continuing to page 2",
                    "finding": "Current-paper initial reaction of 1a with iodine gives E-2a in qualitatively low yield with excellent selectivity; merged with Scheme 2 rather than duplicated.",
                    "evidence_ids": evidence(1),
                },
            ],
            "record_ids": [
                f"{DOC}:generic_iodohydroxylation",
                f"{DOC}:scheme1_halohydroxylation_concept",
                f"{DOC}:scheme2_initial_1a_discovery",
            ],
            "unresolved": [
                "The graphical abstract is generic and supplies no unique scale, time, iodine loading, or row-specific yield.",
                "The discovery experiment's numerical yield and most operating details are absent from the supplied main text.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 2 and continuation prose",
                    "finding": "Initial 1a/iodine experiment in HOAc at -60 °C followed by water gives E-2a; possible diiodides 3A and 3B were not observed, and E-2a was assigned by X-ray diffraction.",
                    "evidence_ids": evidence(2),
                },
                {
                    "region": "Table 1, footnotes, and surrounding optimization discussion",
                    "finding": "Eight distinct optimization rows extracted, including low-yield/base effects, recovered starting material, the four-equivalent-water override, and the entry-8 table/prose iodine-equivalent conflict.",
                    "evidence_ids": evidence(2),
                },
                {
                    "region": "Table 2, footnotes, and scope discussion",
                    "finding": "Seven distinct substrate-scope rows extracted; entry 4 retains the 93:7 starting-material and product diastereomeric ratios determined by 1H NMR and HPLC.",
                    "evidence_ids": evidence(2),
                },
            ],
            "record_ids": [
                f"{DOC}:generic_iodohydroxylation",
                f"{DOC}:scheme2_initial_1a_discovery",
                *[f"{DOC}:table1_entry{i}" for i in range(1, 9)],
                *[f"{DOC}:table2_entry{i}" for i in range(1, 8)],
            ],
            "unresolved": [
                "Table 1 entry 8 prints 2.4 equivalents I2, while adjacent prose reports 2.0 equivalents for the 55 °C/1 h/96% experiment.",
                "Table 2 entry 1 closely matches Table 1 entry 8 but specifies a different scale; it is retained separately rather than assumed to be the same run.",
                "No row-specific workup, purification, isolated mass, atmosphere, or concentration is available without SI.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "Scheme 3 upper arrow and preceding prose",
                    "finding": "Non-sulfinyl 1,2-decadiene forms 1,2-diiodo-2-decene under LiOAc/aqueous MeCN at room temperature for 1 h with configurational isomer ratio 88:12.",
                    "evidence_ids": evidence(3),
                },
                {
                    "region": "Scheme 3 lower arrow",
                    "finding": "The C6H13/CO2Et-substituted allene gives an unidentified mixture under the same displayed medium, temperature, and time.",
                    "evidence_ids": evidence(3),
                },
                {
                    "region": "conclusion and Supporting Information notice",
                    "finding": "No additional current experiment or mechanism is depicted; the article announces typical procedures and analytical data online, but no SI is supplied or associated in this pilot.",
                    "evidence_ids": evidence(3),
                },
            ],
            "record_ids": [
                f"{DOC}:scheme3_diiodination_12_decadiene",
                f"{DOC}:scheme3_allenoate_unidentified_mixture",
            ],
            "unresolved": [
                "Scheme 3 gives no numerical yields or reagent amounts.",
                "The lower-row product mixture is unidentified and its components cannot be represented structurally.",
                "The announced Supporting Information is not supplied or explicitly associated.",
            ],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {
        f"{DOC}:page1:text", f"{DOC}:page2:text", f"{DOC}:page3:text"
    }:
        task["state"] = "attempted"
        task["reason"] = "Original page image and page text inspected; records and coverage ledger generated."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(RAW), "coverage": str(COVERAGE)}, ensure_ascii=False))
