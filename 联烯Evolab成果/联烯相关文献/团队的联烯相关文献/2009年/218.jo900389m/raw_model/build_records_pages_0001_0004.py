#!/usr/bin/env python3
"""Build evidence-linked machine records for jo900389m, original PDF pages 1--4."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_3ee0a1dafca7c6f2"


def ev(page: int, kind: str = "image") -> str:
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


SMILES = {
    "NaI": "[Na+].[I-]",
    "LiI": "[Li+].[I-]",
    "AgI": "[Ag+].[I-]",
    "CuI": "[Cu+].[I-]",
    "LiBr·H2O": "[Li+].[Br-].O",
    "Na2CO3": "[Na+].[Na+].[O-]C([O-])=O",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "acetone": "CC(=O)C",
    "CH3CN": "CC#N",
    "THF": "C1CCOC1",
    "CH3NO2": "C[N+](=O)[O-]",
    "dioxane": "O1CCOCC1",
    "DCE": "ClCCCl",
    "toluene": "Cc1ccccc1",
    "H2O": "O",
    "phenylboronic acid": "OB(O)c1ccccc1",
    "Et2Zn": "CC[Zn]CC",
    "1-hexyne": "CCCCC#C",
    "phenylacetylene": "C#Cc1ccccc1",
    "1a": "COC(=O)C1(C(=O)OC)C(CCCBr)=C1c1ccccc1",
    "1b": "COC(=O)C1(C(=O)OC)C(CCCCCBr)=C1",
}


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    candidate = smiles if smiles is not None else SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(candidate, evidence) if candidate else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def missing_conditions():
    return [
        field("atmosphere", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]


def record(suffix, kind, evidence, participants, conditions, outcomes, *, notes=None, unresolved=None):
    ids = [p["entity_id"] for p in participants]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{"step_id": "step1", "participant_ids": ids, "conditions": conditions}],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted chemistry and structure assignments require source review."
            ],
        },
    }


records = []

# Page 1: graphical abstract / generic present-paper scope, not a batch experiment.
e1 = [ev(1, "image"), ev(1, "text")]
records.append(record(
    "graphical_abstract_general_scope",
    "general_scheme",
    e1,
    [
        participant("scope_1", "reactant", "generic cyclopropene 1 (R groups, LG and m unresolved)", e1),
        participant("scope_mx", "reagent", "MX (X = I or Br)", e1),
        participant("scope_acetone", "solvent", "acetone", e1),
        participant("scope_2", "product", "generic (E)-haloalkylidene cyclic product 2", e1),
    ],
    [field("temperature", "reflux", e1)],
    [
        field("scope_yield_upper_bound", {"number": 96, "unit": "%", "qualifier": "le", "raw_text": "up to 96% yield"}, e1, ["scope_2"]),
        field("ring_size_scope", "m = 2–5 (4–7-membered cyclic products)", e1, ["scope_2"]),
        field("alkene_geometry", "E", e1, ["scope_2"]),
    ],
    notes=["Generic summary scheme; it is not an individual completed experiment."],
    unresolved=["Generic R1/R2/R3, leaving group, metal halide, loading, duration, scale, workup, and purification are not uniquely specified."],
))


# Page 2, Table 1: 11 independent condition-screening rows.
e2 = [ev(2, "image"), ev(2, "text")]
table1 = [
    (1, "NaI", "acetone", "reflux", 78, 1.5, 0.5, None),
    (2, "NaI", "acetone", "reflux", 70, 1.2, 0.5, None),
    (3, "NaI", "acetone", "reflux", 80, 1.5, None, None),
    (4, "AgI", "acetone", "reflux", 0, 1.5, None, 89),
    (5, "CuI", "acetone", "reflux", 0, 1.5, None, 83),
    (6, "LiI", "acetone", "reflux", 58, 1.5, None, None),
    (7, "NaI", "CH3CN", "reflux", 74, 1.5, None, None),
    (8, "NaI", "THF", "reflux", 74, 1.5, None, None),
    (9, "NaI", "CH3NO2", {"number": 80, "unit": "°C"}, 71, 1.5, None, None),
    (10, "NaI", "dioxane", {"number": 80, "unit": "°C"}, 73, 1.5, None, None),
    (11, "NaI", "DCE", {"number": 80, "unit": "°C"}, 67, 1.5, None, None),
]
for entry, mi, solvent, temperature, yld, equiv, carbonate, recovery in table1:
    evidence = list(e2)
    if entry == 3:
        evidence += [ev(3, "image"), ev(3, "text"), ev(4, "image"), ev(4, "text")]
    ps = [
        participant("t1_substrate_1a", "reactant", "1a", evidence, name="dimethyl 2-(3-bromopropyl)-3-phenylcycloprop-2-ene-1,1-dicarboxylate"),
        participant("t1_mi", "reagent", mi, evidence, amounts=[field("equivalents", {"number": equiv, "unit": "equiv"}, e2)]),
        participant("t1_solvent", "solvent", solvent, evidence),
        participant("t1_product_e2a", "product", "E-2a", evidence, name="(E)-iodobenzylidenecyclopentane derivative"),
        participant("t1_product_3a", "product", "3a (six-membered regioisomer)", evidence),
    ]
    if carbonate is not None:
        ps.append(participant("t1_na2co3", "reagent", "Na2CO3", evidence, amounts=[field("equivalents", {"number": carbonate, "unit": "equiv"}, e2)]))
    cond = [
        field("temperature", temperature, e2),
        field("time", {"number": 2, "unit": "d"}, e2),
    ] + missing_conditions()
    outcomes = [
        field("isolated_yield_E_2a", {"number": yld, "unit": "%"}, e2, ["t1_product_e2a"]),
        field("yield_measurement_basis", "isolated yield", e2, ["t1_product_e2a"]),
        field("formation_of_3a", "not observed", e2, ["t1_product_3a"]),
        field("alkene_geometry", "E", e2, ["t1_product_e2a"]),
    ]
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, e2, ["t1_substrate_1a"]))
    unresolved = ["Atmosphere is not stated."]
    notes = []
    if entry == 3:
        # Merge the page-3 complete batch and page-4 characterization into this same experiment.
        ps[0]["amounts"] += [
            field("mass", {"number": 54, "unit": "mg"}, [ev(3, "text")]),
            field("amount", {"number": 0.15, "unit": "mmol"}, [ev(3, "text")]),
        ]
        ps[1]["amounts"] += [
            field("mass", {"number": 35, "unit": "mg"}, [ev(3, "text")]),
            field("amount", {"number": 0.23, "unit": "mmol"}, [ev(3, "text")]),
        ]
        ps[2]["amounts"] += [field("volume", {"number": 3.0, "unit": "mL"}, [ev(3, "text")])]
        ps[3]["amounts"] += [field("mass", {"number": 49, "unit": "mg"}, [ev(3, "text")])]
        cond = [
            field("temperature", "reflux", [ev(2, "image"), ev(3, "text")]),
            field("time", {"number": 2, "unit": "d"}, [ev(2, "image"), ev(3, "text")]),
            field("operation", "NaI, 1.5 mL acetone, 1a, then 1.5 mL acetone were added sequentially; reaction monitored by TLC", [ev(3, "text")]),
            field("atmosphere", None, []),
            field("workup", "evaporation", [ev(3, "text")]),
            field("purification", "silica-gel column chromatography; petroleum ether/Et2O = 10:1", [ev(3, "text")]),
        ]
        notes = ["E-2a was isolated as a solid; characterization continues on page 4, including mp 90–91 °C and spectral/elemental data."]
        unresolved = ["Atmosphere is not stated; candidate substrate/product connectivity and E geometry require chemistry review."]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, ps, cond, outcomes,
        notes=notes,
        unresolved=unresolved,
    ))


# Page 2, Table 2: concentration/additive screen for seven-membered E-2b.
table2 = [
    (1, 1.5, None, 0.067, 18, 9),
    (2, 1.5, 0.6, 0.067, 16.5, 23),
    (3, 1.7, 0.7, 0.050, 20, 57),
    (4, 1.6, 0.6, 0.025, 20, 47),
]
for entry, nai_eq, carbonate_eq, concentration, hours, yld in table2:
    ps = [
        participant("t2_substrate_1b", "reactant", "1b", e2, name="5-(3,3-bis(methoxycarbonyl)cyclopropenyl)pentyl bromide"),
        participant("t2_nai", "reagent", "NaI", e2, amounts=[field("equivalents", {"number": nai_eq, "unit": "equiv"}, e2)]),
        participant("t2_acetone", "solvent", "acetone", e2),
        participant("t2_product_e2b", "product", "E-2b", e2, name="seven-membered (E)-iodomethylene product"),
    ]
    if carbonate_eq is not None:
        ps.append(participant("t2_na2co3", "reagent", "Na2CO3", e2, amounts=[field("equivalents", {"number": carbonate_eq, "unit": "equiv"}, e2)]))
    records.append(record(
        f"table2_entry{entry}", "optimization_entry", e2, ps,
        [
            field("substrate_concentration", {"number": concentration, "unit": "M"}, e2),
            field("temperature", "reflux", e2),
            field("time", {"number": hours, "unit": "h"}, e2),
        ] + missing_conditions(),
        [
            field("isolated_yield_E_2b", {"number": yld, "unit": "%"}, e2, ["t2_product_e2b"]),
            field("yield_measurement_basis", "isolated yield", e2, ["t2_product_e2b"]),
            field("alkene_geometry", "E", e2, ["t2_product_e2b"]),
        ],
        unresolved=["Reaction scale, acetone volume, atmosphere, workup, and purification are not stated."],
    ))


# Page 3, Table 3: each row reports separate with-carbonate and without-carbonate experiments.
e3 = [ev(3, "image"), ev(3, "text")]
table3 = [
    (1, "CO2Me", "CO2Me", 3, "1c", "NaI", 0.8, 81, 61, "E-2c", 2.4),
    (2, "CO2Me", "CO2Me", 3, "1c", "LiBr·H2O", 2.7, 96, 86, "E-2d", None),
    (3, "CH3CO", "CO2Et", 3, "1d", "NaI", 0.5, 82, 65, "E-2e", None),
    (4, "CH3CO", "CO2Et", 3, "1d", "LiBr·H2O", 1, 84, 87, "E-2f", None),
    (5, "CH3CO", "SO2Ph", 3, "1e", "NaI", 3, 76, 92, "E-2g", None),
    (6, "CH3CO", "SO2Ph", 3, "1e", "LiBr·H2O", 3, 77, 85, "E-2h", None),
    (7, "CO2Me", "SO2Ph", 3, "1f", "NaI", 4, 79, 75, "E-2i", None),
    (8, "CO2Me", "SO2Ph", 3, "1f", "LiBr·H2O", 16, 71, 81, "E-2j", 2.4),
    (9, "CO2Me", "CO2Me", 4, "1g", "NaI", 1, 69, 76, "E-2k", None),
    (10, "CO2Me", "CO2Me", 2, "1h", "NaI", 10, 22, 27, "E-2l", None),
]
for entry, r1, r2, m, substrate, mx, hours, with_yield, without_yield, product, exact_mx in table3:
    for carbonate_present, yld in ((True, with_yield), (False, without_yield)):
        suffix = "with_na2co3" if carbonate_present else "without_na2co3"
        loading = {"number": exact_mx, "unit": "equiv"} if exact_mx else {
            "minimum": 1.5, "maximum": 1.7, "unit": "equiv", "raw_text": "1.5–1.7 equiv"
        }
        ps = [
            participant("t3_substrate", "reactant", substrate, e3, name=f"mesylate scope substrate; R1={r1}, R2={r2}, m={m}"),
            participant("t3_mx", "reagent", mx, e3, amounts=[field("equivalents", loading, e3)]),
            participant("t3_acetone", "solvent", "acetone", e3),
            participant("t3_product", "product", product, e3, name=f"corresponding (E)-haloalkylidene cyclic product; R1={r1}, R2={r2}, m={m}"),
        ]
        if carbonate_present:
            ps.append(participant(
                "t3_na2co3", "reagent", "Na2CO3", e3,
                amounts=[field("equivalents", {"minimum": 0.5, "maximum": 0.8, "unit": "equiv", "raw_text": "0.5–0.8 equiv"}, e3)],
            ))
        records.append(record(
            f"table3_entry{entry}_{suffix}", "substrate_scope_entry", e3, ps,
            [field("temperature", "reflux", e3), field("time", {"number": hours, "unit": "h"}, e3)] + missing_conditions(),
            [
                field(f"isolated_yield_{product.replace('-', '_')}", {"number": yld, "unit": "%"}, e3, ["t3_product"]),
                field("yield_measurement_basis", "isolated yield", e3, ["t3_product"]),
                field("alkene_geometry", "E", e3, ["t3_product"]),
            ],
            notes=["Parenthesized Table 3 yield is a separate experiment carried out without Na2CO3."] if not carbonate_present else [],
            unresolved=[
                "Na2CO3 loading is reported only as the shared 0.5–0.8 equiv range." if carbonate_present else "Reaction scale is not stated.",
                "Atmosphere, workup, purification, and solvent volume are not stated.",
                "Substrate and product structures require chemistry review.",
            ],
        ))

# Table 3 footnote f: additional 1l case under marked row-9 conditions.
records.append(record(
    "table3_footnote_f_1l_to_e2k", "substrate_scope_entry", e3,
    [
        participant("t3f_substrate", "reactant", "1l", e3, name="bromide analogue used in the Table 3 footnote"),
        participant("t3f_nai", "reagent", "NaI", e3, amounts=[field("equivalents", {"minimum": 1.5, "maximum": 1.7, "unit": "equiv", "raw_text": "1.5–1.7 equiv"}, e3)]),
        participant("t3f_na2co3", "reagent", "Na2CO3", e3, amounts=[field("equivalents", {"number": 0.6, "unit": "equiv"}, e3)]),
        participant("t3f_acetone", "solvent", "acetone", e3),
        participant("t3f_product", "product", "E-2k", e3),
    ],
    [field("temperature", "reflux", e3), field("time", {"number": 1, "unit": "h"}, e3)] + missing_conditions(),
    [
        field("isolated_yield_E_2k", {"number": 78, "unit": "%"}, e3, ["t3f_product"]),
        field("yield_measurement_basis", "isolated yield", e3, ["t3f_product"]),
        field("alkene_geometry", "E", e3, ["t3f_product"]),
    ],
    unresolved=["Footnote f explicitly gives 1l, 0.6 equiv Na2CO3 and 78% E-2k; NaI loading and 1 h duration are inherited from its marked row 9 and require review."],
))


# Page 3, Scheme 1: three explicitly drawn substrate-specific reactions.
scheme1 = [
    ("1i", "ethyl-substituted cyclopropenylalkyl bromide, m=4", 1.6, 0.6, 35, "h", "E-2m", 77, 93),
    ("1j", "n-butyl-substituted cyclopropenylalkyl bromide, m=4", 1.5, 0.6, 6, "d", "E-2n", 79, None),
    ("1k", "p-tolyl-substituted cyclopropenylalkyl bromide, m=3", 1.7, None, 12, "h", "E-2o", 85, None),
]
for substrate, name, nai_eq, carbonate_eq, duration, unit, product, yld, purity in scheme1:
    ps = [
        participant("s1_substrate", "reactant", substrate, e3, name=name),
        participant("s1_nai", "reagent", "NaI", e3, amounts=[field("equivalents", {"number": nai_eq, "unit": "equiv"}, e3)]),
        participant("s1_acetone", "solvent", "acetone", e3),
        participant("s1_product", "product", product, e3),
    ]
    if carbonate_eq is not None:
        ps.append(participant("s1_na2co3", "reagent", "Na2CO3", e3, amounts=[field("equivalents", {"number": carbonate_eq, "unit": "equiv"}, e3)]))
    outcomes = [
        field(f"reported_yield_{product.replace('-', '_')}", {"number": yld, "unit": "%"}, e3, ["s1_product"]),
        field("yield_measurement_basis", None, [], ["s1_product"]),
        field("alkene_geometry", "E", e3, ["s1_product"]),
    ]
    if purity is not None:
        outcomes.append(field("product_purity", {"number": purity, "unit": "%"}, e3, ["s1_product"]))
    records.append(record(
        f"scheme1_{substrate}_to_{product.lower().replace('-', '')}", "reported_experiment", e3, ps,
        [field("temperature", "reflux", e3), field("time", {"number": duration, "unit": unit}, e3)] + missing_conditions(),
        outcomes,
        unresolved=["Yield basis, scale, atmosphere, workup, purification, and solvent volume are not stated; structures require review."],
    ))


# Page 3, Scheme 2: catalytic LiBr hydrate reactions.
scheme2 = [
    ("1a", "E-2p", 12, 78, None),
    ("1l", "E-2q", 10, 68, 0.6),
]
for substrate, product, hours, yld, carbonate_eq in scheme2:
    ps = [
        participant("s2_substrate", "reactant", substrate, e3),
        participant("s2_libr", "reagent", "LiBr·H2O", e3, amounts=[field("equivalents", {"number": 0.25, "unit": "equiv"}, e3)]),
        participant("s2_acetone", "solvent", "acetone", e3),
        participant("s2_product", "product", product, e3),
    ]
    if carbonate_eq is not None:
        ps.append(participant("s2_na2co3", "reagent", "Na2CO3", e3, amounts=[field("equivalents", {"number": carbonate_eq, "unit": "equiv"}, e3)]))
    records.append(record(
        f"scheme2_{substrate}_to_{product.lower().replace('-', '')}", "reported_experiment", e3, ps,
        [field("temperature", "reflux", e3), field("time", {"number": hours, "unit": "h"}, e3)] + missing_conditions(),
        [
            field(f"reported_yield_{product.replace('-', '_')}", {"number": yld, "unit": "%"}, e3, ["s2_product"]),
            field("yield_measurement_basis", None, [], ["s2_product"]),
            field("alkene_geometry", "E", e3, ["s2_product"]),
        ],
        unresolved=["Yield basis, scale, atmosphere, workup, purification, and solvent volume are not stated; structures require review."],
    ))


# Page 3, Scheme 3: four distinct downstream transformations of E-2c.
scheme3 = [
    ("diethylzinc coupling", "Et2Zn", "E-5a", 73, ["Pd(PPh3)4"], ["THF"]),
    ("Suzuki coupling", "phenylboronic acid", "E-4a", 76, ["Pd(PPh3)4", "Na2CO3"], ["toluene", "H2O"]),
    ("Sonogashira coupling with 1-hexyne", "1-hexyne", "E-6a", 84, ["PdCl2(PPh3)2", "CuI", "K2CO3"], ["CH3CN"]),
    ("Sonogashira coupling with phenylacetylene", "phenylacetylene", "E-6b", 94, ["PdCl2(PPh3)2", "CuI", "K2CO3"], ["CH3CN"]),
]
for label, partner, product, yld, agents, solvents in scheme3:
    ps = [
        participant("s3_e2c", "reactant", "E-2c", e3),
        participant("s3_partner", "reactant", partner, e3),
        participant("s3_product", "product", product, e3),
    ]
    for idx, agent in enumerate(agents, 1):
        role = "catalyst" if "Pd" in agent or agent == "CuI" else "reagent"
        ps.append(participant(f"s3_agent{idx}", role, agent, e3))
    for idx, solvent in enumerate(solvents, 1):
        ps.append(participant(f"s3_solvent{idx}", "solvent", solvent, e3))
    records.append(record(
        f"scheme3_{product.lower().replace('-', '')}", "reported_experiment", e3, ps,
        [field("temperature", None, []), field("time", None, [])] + missing_conditions(),
        [
            field(f"reported_yield_{product.replace('-', '_')}", {"number": yld, "unit": "%"}, e3, ["s3_product"]),
            field("yield_measurement_basis", None, [], ["s3_product"]),
            field("alkene_geometry", "E", e3, ["s3_product"]),
        ],
        notes=[label],
        unresolved=["Reagent/catalyst loadings, scale, time, temperature, yield basis, atmosphere, workup, and purification are not stated; product structure requires review."],
    ))


# Page 3, Scheme 4: explicitly proposed mechanism, not an observed batch.
records.append(record(
    "scheme4_plausible_mechanism", "mechanism", e3,
    [
        participant("mech_1", "reactant", "generic cyclopropene 1", e3),
        participant("mech_x", "reagent", "X− (I− or Br−)", e3),
        participant("mech_7", "unspecified_agent", "stereodefined carbanion 7", e3),
        participant("mech_2", "product", "generic E-2", e3),
    ],
    [field("operation", "regioselective X− attack at cyclopropene C1, followed by intramolecular nucleophilic substitution", e3)],
    [field("mechanistic_status", "plausible/proposed", e3, ["mech_7", "mech_2"])],
    notes=["Intermediate 7 is proposed, not reported as isolated or directly observed."],
    unresolved=["Generic R groups, leaving group, ring size, and exact intermediate structure are unresolved; mechanism is not experimentally verified here."],
))


# Coverage ledger and task states.
ids = [r["record_id"] for r in records]
def rid(suffix):
    return f"{DOC}:{suffix}"

page2_ids = [rid(f"table1_entry{i}") for i in range(1, 12)] + [rid(f"table2_entry{i}") for i in range(1, 5)]
page3_ids = (
    [rid("table1_entry3")]
    + [rid(f"table3_entry{i}_{suffix}") for i in range(1, 11) for suffix in ("with_na2co3", "without_na2co3")]
    + [rid("table3_footnote_f_1l_to_e2k")]
    + [r["record_id"] for r in records if any(token in r["source_reaction_id"] for token in ("scheme1_", "scheme2_", "scheme3_", "scheme4_"))]
)
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "left-column graphical abstract and abstract",
                    "finding": "Generic present-paper X−-triggered ring-opening/cyclization scope classified as a general scheme; not duplicated as a batch experiment.",
                    "evidence_ids": [ev(1, "image"), ev(1, "text")],
                },
                {
                    "region": "introduction and references across both columns",
                    "finding": "Background allene/cyclopropene discussion and citation-only prior work; no independent source-level experiment with complete arrow/conditions on this page.",
                    "evidence_ids": [ev(1, "image"), ev(1, "text")],
                },
            ],
            "record_ids": [rid("graphical_abstract_general_scope")],
            "unresolved": ["Generic R groups, exact MX loading, duration, and individual substrate identities are not specified in the graphical abstract."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 1 and footnotes",
                    "finding": "Eleven independent optimization entries extracted; carbonate and NaI footnotes applied row-wise, zero-yield AgI/CuI cases preserve recovered starting material.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
                {
                    "region": "upper-right Table 2 and footnotes",
                    "finding": "Four independent concentration/additive optimization entries extracted with NaI equivalents, substrate molarity, time, and isolated yield.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
                {
                    "region": "Results and Discussion prose below tables",
                    "finding": "Narrative results were linked to the corresponding table rows; X-ray identity statements were not counted as new reactions.",
                    "evidence_ids": [ev(2, "image"), ev(2, "text")],
                },
            ],
            "record_ids": page2_ids,
            "unresolved": ["Table rows omit atmosphere, workup, purification, and most reaction-scale/volume details; Table 2 does not give an exact reflux temperature."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 3 and footnotes",
                    "finding": "Each of ten rows was split into separate with-Na2CO3 and without-Na2CO3 experiments; the distinct footnote-f 1l experiment was also retained.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "left-column Scheme 1",
                    "finding": "Three substrate-specific NaI ring-opening/cyclization experiments (1i, 1j, 1k) extracted separately.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "upper-right Scheme 2",
                    "finding": "Two catalytic LiBr·H2O ring-opening/cyclization experiments extracted separately.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "middle-right Scheme 3",
                    "finding": "Four distinct synthetic-utility reactions of E-2c extracted: Et2Zn, Suzuki, and two Sonogashira couplings.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "lower-right Scheme 4 and mechanism prose",
                    "finding": "Plausible carbanion pathway classified as mechanism, not an observed experiment.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
                {
                    "region": "bottom-right general procedure for E-2a",
                    "finding": "Detailed quantities, TLC monitoring, evaporation, chromatography, mass, and 80% yield merged into Table 1 entry 3.",
                    "evidence_ids": [ev(3, "image"), ev(3, "text")],
                },
            ],
            "record_ids": list(dict.fromkeys(page3_ids)),
            "unresolved": ["Most schemes omit scale, yield basis, atmosphere, workup, and purification; Table 3 gives shared loading ranges rather than exact row values."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left continuation of E-2a experimental paragraph",
                    "finding": "Physical form and analytical characterization continue the Table 1 entry 3 batch; linked as evidence, not counted as another reaction.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text")],
                },
                {
                    "region": "top-right Supporting Information Available notice",
                    "finding": "The paper advertises SI, but no SI file was supplied or explicitly associated; no SI facts were inferred.",
                    "evidence_ids": [ev(4, "image"), ev(4, "text")],
                },
            ],
            "record_ids": [rid("table1_entry3")],
            "unresolved": ["SI association remains unestablished; page 4 adds characterization but no independent reaction experiment."],
        },
    ],
}

assert len(records) == 47, len(records)
assert len(ids) == len(set(ids))
assert [p["page"] for p in coverage["pages"]] == [1, 2, 3, 4]
assert all(p["regions"] for p in coverage["pages"])
assert all(rid_ in ids for p in coverage["pages"] for rid_ in p["record_ids"])

(OUT / "raw_model/records_pages_0001_0004.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)
(OUT / "coverage").mkdir(parents=True, exist_ok=True)
(OUT / "coverage/pages_0001_0004.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {ev(i, "text") for i in range(1, 5)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": 4, "output": str(OUT)}, ensure_ascii=False))
