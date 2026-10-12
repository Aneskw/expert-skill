import json
from pathlib import Path

DOC = "doc_cda73facc6ef4831"
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "raw_model" / "pages_0001_0005_records.json"
COVERAGE = BASE / "coverage" / "pages_0001_0005.json"


def evid(page, include_text=True):
    ids = [f"{DOC}:page{page}:image"]
    if include_text:
        ids.insert(0, f"{DOC}:page{page}:text")
    return ids


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence_ids, target=None):
    result = {"name": name, "fact": fact(value, evidence_ids)}
    if target:
        result["target_entity_ids"] = list(target)
    return result


def participant(entity_id, role, label, evidence_ids, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids) if name else fact(None, []),
        "smiles": fact(smiles, evidence_ids) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence_ids, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence_ids)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(n, evidence_ids) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def q(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


def thermal(label, time_h, yield_pct, smiles=None, extra_evidence=None, detailed=False):
    ev = evid(2) + (extra_evidence or [])
    substrate = f"substrate_{label}"
    product = f"product_7{label[-1]}"
    ps = [
        participant(substrate, "reactant", label, ev, smiles=smiles),
        participant(product, "product", f"7{label[-1]}", ev),
        participant("solvent_xylene", "solvent", "xylene", ev, name="xylene"),
    ]
    conditions = [
        field("substrate_concentration", q(0.04, "M", "0.04 M"), evid(2)),
        field("temperature", "reflux", evid(2)),
        field("time", q(time_h, "h", f"{time_h} h"), evid(2)),
    ]
    steps = [{"step_id": "thermal_cycloaddition", "participant_ids": [substrate, "solvent_xylene"], "conditions": conditions}]
    outcomes = [
        field("isolated_yield", q(yield_pct, "%", f"{yield_pct}%"), evid(2), [product]),
        field("yield_measurement_basis", "isolated product", evid(2), [product]),
    ]
    notes = ["Table 1 reports a thermal intramolecular [2+2] cycloaddition to a bicyclo[5.2.0] product."]
    unresolved = [
        "No explicitly associated supporting information was supplied; additional experimental details may be absent.",
        "The substrate/product drawing requires independent structure review; a missing SMILES is intentional where exact machine transcription was not reliable.",
    ]
    if detailed:
        pe = evid(3)
        for p in ps:
            if p["entity_id"] == substrate:
                p["amounts"] = [field("mass", q(145, "mg", "145 mg"), pe), field("amount", q(0.53, "mmol", "0.53 mmol"), pe)]
            elif p["entity_id"] == product:
                p["amounts"] = [field("mass", q(62, "mg", "62 mg"), pe)]
            elif p["entity_id"] == "solvent_xylene":
                p["amounts"] = [field("volume", q(12, "mL", "12 mL"), pe)]
        steps[0]["conditions"].append(field("atmosphere", "Ar", pe))
        steps[0]["conditions"].append(field("solvent", "dry xylene", pe))
        steps += [
            {"step_id": "reaction_monitoring_and_concentration", "participant_ids": [], "conditions": [
                field("operation", "Reaction completion checked by TLC (petroleum ether/ethyl acetate 5:1), followed by rotary evaporation.", pe)
            ]},
            {"step_id": "purification", "participant_ids": [product], "conditions": [
                field("purification", "Flash chromatography on silica gel (petroleum ether/diethyl ether 20:1).", pe)
            ]},
        ]
        notes.append("General procedure I identifies 7a as a liquid and supplies characterization data, retained in the source but not transcribed as reaction conditions.")
    return record(
        f"thermal_{label}_to_7{label[-1]}", f"Table1-{label}", "substrate_scope_entry", ev,
        ps, steps, outcomes, notes, unresolved,
    )


def standard_pd_participants(ev, catalyst_loading=5):
    return [
        participant("catalyst_pdpph3_4", "catalyst", "[Pd(PPh3)4]", ev, name="tetrakis(triphenylphosphine)palladium(0)", amounts=[field("catalyst_loading", q(catalyst_loading, "mol%", f"{catalyst_loading} mol%"), ev)]),
        participant("base_k2co3", "reagent", "K2CO3", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", q(4, "equiv", "4 equiv"), ev)]),
        participant("additive_nbu4ni", "reagent", "nBu4NI", ev, name="tetrabutylammonium iodide", smiles="CCCC[N+](CCCC)(CCCC)CCCC.[I-]", amounts=[field("equivalents", q(2, "equiv", "2 equiv"), ev)]),
        participant("solvent_toluene", "solvent", "toluene", ev, name="toluene", smiles="Cc1ccccc1"),
    ]


def optimization(entry, catalyst_loading, base, additive, solvent, time_h, outcome):
    ev = evid(1) + evid(2)
    ps = [
        participant("substrate_6a", "reactant", "6a", ev, smiles="C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1"),
        participant("target_product_8a", "product", "8a", ev),
        participant("catalyst_pdpph3_4", "catalyst", "[Pd(PPh3)4]", ev, name="tetrakis(triphenylphosphine)palladium(0)", amounts=[field("catalyst_loading", q(catalyst_loading, "mol%", f"{catalyst_loading} mol%"), evid(2))]),
    ]
    step_ids = ["substrate_6a", "catalyst_pdpph3_4"]
    if base:
        ps.append(participant("base_k2co3", "reagent", "K2CO3", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("equivalents", q(4, "equiv", "4 equiv"), evid(2))]))
        step_ids.append("base_k2co3")
    if additive:
        ps.append(participant("additive_nbu4ni", "reagent", "nBu4NI", ev, name="tetrabutylammonium iodide", smiles="CCCC[N+](CCCC)(CCCC)CCCC.[I-]", amounts=[field("equivalents", q(2, "equiv", "2 equiv"), evid(2))]))
        step_ids.append("additive_nbu4ni")
    solvent_id = f"solvent_{solvent}"
    solvent_smiles = "Cc1ccccc1" if solvent == "toluene" else None
    ps.append(participant(solvent_id, "solvent", solvent, ev, name=solvent, smiles=solvent_smiles))
    step_ids.append(solvent_id)
    steps = [{"step_id": "pd_cycloaddition_screen", "participant_ids": step_ids, "conditions": [
        field("temperature", {"minimum": 80, "maximum": 85, "unit": "°C", "raw_text": "80–85 °C"}, evid(2)),
        field("time", q(time_h, "h", f"{time_h} h"), evid(2)),
    ]}]
    basis = None
    if outcome == "trace":
        basis = "trace amount determined by 1H NMR analysis of the crude reaction mixture"
    elif isinstance(outcome, int):
        basis = "isolated product"
    outcomes = [field("yield", q(outcome, "%", f"{outcome}%") if isinstance(outcome, int) else outcome, evid(2), ["target_product_8a"])]
    if basis:
        outcomes.append(field("yield_measurement_basis", basis, evid(1) + evid(2), ["target_product_8a"]))
    notes = []
    if not base:
        notes.append("Table 2 explicitly reports no added base for this entry.")
    if not additive:
        notes.append("Table 2 explicitly reports no added additive for this entry.")
    unresolved = [
        "No explicitly associated supporting information was supplied.",
        "Exact substrate scale and workup are not reported for this optimization entry." if entry != 4 else "The product drawing requires independent structure review; SMILES was not assigned.",
    ]
    extra_ev = []
    if entry == 4:
        extra_ev = evid(3) + evid(4)
        ev += extra_ev
        # Merge the duplicate Table 3 6a row and General procedure II into this optimization experiment.
        for p in ps:
            if p["entity_id"] == "substrate_6a":
                p["amounts"] = [field("mass", q(140, "mg", "140 mg"), evid(4)), field("amount", q(0.51, "mmol", "0.51 mmol"), evid(4))]
            elif p["entity_id"] == "catalyst_pdpph3_4":
                p["amounts"] += [field("mass", q(27, "mg", "27 mg"), evid(4)), field("amount", q(0.023, "mmol", "0.023 mmol"), evid(4))]
            elif p["entity_id"] == "base_k2co3":
                p["amounts"] += [field("mass", q(281, "mg", "281 mg"), evid(4)), field("amount", q(2.04, "mmol", "2.04 mmol"), evid(4))]
            elif p["entity_id"] == "additive_nbu4ni":
                p["amounts"] += [field("mass", q(369, "mg", "369 mg"), evid(4)), field("amount", q(1, "mmol", "1 mmol"), evid(4))]
            elif p["entity_id"] == "solvent_toluene":
                p["amounts"] = [field("volume", q(5, "mL", "5 mL"), evid(4))]
        ps[1]["amounts"] = [field("mass", q(82, "mg", "82 mg"), evid(4))]
        steps[0]["conditions"].append(field("operation", "K2CO3 and nBu4NI were added to a stirred solution of 6a and [Pd(PPh3)4] in dry toluene.", evid(4)))
        steps += [
            {"step_id": "reaction_monitoring_and_concentration", "participant_ids": [], "conditions": [field("operation", "Reaction completion checked by TLC (petroleum ether/ethyl acetate 5:1), followed by rotary evaporation.", evid(4))]},
            {"step_id": "purification", "participant_ids": ["target_product_8a"], "conditions": [field("purification", "Flash chromatography on silica gel (petroleum ether/diethyl ether 20:1).", evid(4))]},
        ]
        notes.append("Table 2 entry 4, Table 3 row 6a, and General procedure II report the same 6a→8a experiment and are represented once with combined evidence.")
    return record(
        f"pd_optimization_entry_{entry}", f"Table2-entry{entry}", "optimization_entry", ev,
        ps, steps, outcomes, notes, unresolved,
    )


def pd_scope(label, product, time_h, yield_pct, substrate_smiles=None, catalyst_loading=5, ee=None):
    ev = evid(3)
    sid = f"substrate_{label}"
    pid = f"product_{product}"
    ps = [participant(sid, "reactant", label, ev, smiles=substrate_smiles), participant(pid, "product", product, ev)] + standard_pd_participants(ev, catalyst_loading)
    steps = [{"step_id": "pd_cycloaddition", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [
        field("temperature", {"minimum": 80, "maximum": 85, "unit": "°C", "raw_text": "80–85 °C"}, ev),
        field("time", q(time_h, "h", f"{time_h} h"), ev),
    ]}]
    outcomes = [field("isolated_yield", q(yield_pct, "%", f"{yield_pct}%"), ev, [pid]), field("yield_measurement_basis", "isolated product", ev, [pid])]
    if ee is not None:
        outcomes.append(field("enantiomeric_excess", {"number": ee, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, ev, [pid]))
    return record(
        f"pd_scope_{label}_to_{product}", f"Table3-{label}", "substrate_scope_entry", ev,
        ps, steps, outcomes,
        ["Table 3 reports an intramolecular Pd(0)-catalyzed [2+2] cycloaddition to a bicyclo[3.2.0] product."],
        ["No explicitly associated supporting information was supplied; substrate scale, workup, and purification are missing for this scope entry.", "Substrate/product structures require independent review; missing product SMILES is intentional."],
    )


def failed_scope(label):
    ev = evid(1)
    sid = f"substrate_{label}"
    pid = f"expected_product_8{label[-1]}"
    ps = [participant(sid, "reactant", label, ev), participant(pid, "product", f"8{label[-1]} (expected)", ev)]
    return record(
        f"pd_failed_{label}", f"prose-failed-{label}", "substrate_scope_entry", ev,
        ps,
        [{"step_id": "pd_cycloaddition_attempt", "participant_ids": [sid], "conditions": [
            field("operation", "Attempted under the optimized Pd(0)-catalyzed [2+2] cycloaddition context described in the prose.", ev),
            field("time", None, []), field("temperature", None, []),
        ]}],
        [field("expected_product_formation", "not obtained", ev, [pid]), field("other_regioisomers", "not observed", ev, [pid])],
        ["The authors suggest steric effects and possible polymerization as explanations; these are interpretations, not measured outcomes."],
        ["Exact conditions, reaction time, analytical basis, conversion, and isolated material are not individually reported for this failed substrate.", "The substrate and expected-product structures are cited only by labels in this record; SMILES is intentionally missing pending review."],
    )


def diels_alder():
    ev = evid(3) + evid(4)
    ps = [
        participant("reactant_8n", "reactant", "8n", ev, amounts=[field("mass", q(13, "mg", "13 mg"), evid(4)), field("amount", q(0.055, "mmol", "0.055 mmol"), evid(4))]),
        participant("reactant_npm", "reactant", "N-phenylmaleimide", ev, name="N-phenylmaleimide", smiles="O=C1C=CC(=O)N1c1ccccc1", amounts=[field("mass", q(19, "mg", "19 mg"), evid(4)), field("amount", q(0.11, "mmol", "0.11 mmol"), evid(4)), field("equivalents", q(2, "equiv", "2 equiv"), evid(4))]),
        participant("solvent_toluene", "solvent", "toluene", ev, name="toluene", smiles="Cc1ccccc1", amounts=[field("volume", q(2, "mL", "2 mL"), evid(4))]),
        participant("product_9na", "product", "9na", ev),
        participant("product_9nb", "product", "9nb", ev),
    ]
    return record(
        "diels_alder_8n_npm_to_9n", "Scheme2-GeneralProcedure-DA", "reported_experiment", ev,
        ps,
        [{"step_id": "diels_alder", "participant_ids": ["reactant_8n", "reactant_npm", "solvent_toluene"], "conditions": [field("solvent", "dry toluene", evid(4)), field("temperature", "reflux", ev), field("time", q(8, "h", "8 h"), evid(4)), field("atmosphere", "Ar", evid(4))]}],
        [
            field("combined_isolated_yield", q(100, "%", "100%"), ev, ["product_9na", "product_9nb"]),
            field("product_ratio_9na_to_9nb", "100:3", ev, ["product_9na", "product_9nb"]),
            field("selectivity_measurement_basis", "determined by 300 MHz 1H NMR analysis", ev, ["product_9na", "product_9nb"]),
            field("product_mass", q(24, "mg", "24 mg"), evid(4), ["product_9na", "product_9nb"]),
        ],
        ["The isolated material is reported collectively as product 9n, comprising major isomer 9na and minor isomer 9nb."],
        ["No explicitly associated supporting information was supplied; workup and purification operations are not reported in the provided main text.", "Exact stereochemical SMILES for 8n, 9na, and 9nb were not assigned and require independent structure review."],
    )


records = []

thermal_rows = [
    ("6a", 24, 43, "C=C=CCN(CC=C=C)S(=O)(=O)c1ccc(C)cc1", evid(3), True),
    ("6b", 3, 61, "C=C=CCC(CC=C=C)(S(=O)(=O)c1ccccc1)S(=O)(=O)c1ccccc1", None, False),
    ("6c", 46, 38, "C=C=CCC(CC=C=C)(C(=O)OCC)C(=O)OCC", None, False),
    ("6d", 8, 61, "C=C=CCC(CC=C=C)(S(=O)(=O)c1ccccc1)C(=O)OC", None, False),
    ("6e", 1.5, 69, None, None, False),
    ("6f", 1, 74, None, None, False),
    ("6g", 10, 56, None, None, False),
    ("6h", 24, 70, None, None, False),
    ("6i", 6, 69, None, None, False),
    ("6j", 5, 70, None, None, False),
    ("6k", 0.5, 78, None, None, False),
]
for row in thermal_rows:
    records.append(thermal(*row))

records += [
    optimization(1, 10, False, False, "toluene", 8, "n.r."),
    optimization(2, 10, True, False, "xylene", 4, "trace"),
    optimization(3, 10, False, True, "xylene", 10, "n.r."),
    optimization(4, 5, True, True, "toluene", 4, 59),
    pd_scope("6b", "8b", 4, 62, "C=C=CCC(CC=C=C)(S(=O)(=O)c1ccccc1)S(=O)(=O)c1ccccc1"),
    pd_scope("6c", "8c", 19, 45, "C=C=CCC(CC=C=C)(C(=O)OCC)C(=O)OCC"),
    pd_scope("6l", "8l", 8, 54),
    pd_scope("(S)-6m", "8m", 5, 66, "C=C=CCN(CC=C=C)[C@@H](C(=O)OCC)C(C)C", catalyst_loading=10, ee=99),
]

for label in ["6e", "6f", "6g", "6h", "6i", "6j", "6k"]:
    records.append(failed_scope(label))

records.append(diels_alder())

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [r["record_id"] for r in records]
by_prefix = lambda prefix: [x for x in ids if f":{prefix}" in x]
thermal_ids = by_prefix("thermal_")
opt_ids = by_prefix("pd_optimization_")
scope_ids = by_prefix("pd_scope_")
fail_ids = by_prefix("pd_failed_")
da_ids = by_prefix("diels_alder_")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1, lower-left", "finding": "General regioselectivity map: literature allenenes/allenynes are prior work; bisallene 6→7/8/9 is a general outcome map, not a row-level experiment.", "evidence_ids": evid(1)},
                {"region": "right-column optimization discussion", "finding": "Prose describes Table 2 entries: no reaction without K2CO3/nBu4NI, trace with K2CO3 only, no reaction with nBu4NI only, and an optimized productive entry.", "evidence_ids": evid(1)},
                {"region": "right-column substrate-scope discussion", "finding": "Explicit failed outcomes for 6e–6k: expected 8e–8k not obtained; other regioisomers not observed.", "evidence_ids": evid(1)},
            ],
            "record_ids": opt_ids + fail_ids,
            "unresolved": ["Scheme 1 uses generic X and cannot support fully specified molecule structures.", "Failure attempts 6e–6k lack row-specific time, conversion, analytical basis, and isolated-material details."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1, upper page", "finding": "Eleven thermal [2+2] substrate-scope rows (6a–6k), with row-specific time and isolated yield under xylene (0.04 M), reflux.", "evidence_ids": evid(2)},
                {"region": "Figure 1, lower-left", "finding": "ORTEP structure of 7e; structural confirmation only, not a separate reaction experiment.", "evidence_ids": evid(2)},
                {"region": "Table 2, lower-right", "finding": "Four Pd(0) optimization entries, including two no-reaction results and one trace result; entry 4 is the same 6a→8a experiment repeated in Table 3/procedure II.", "evidence_ids": evid(2)},
            ],
            "record_ids": thermal_ids + opt_ids,
            "unresolved": ["Most Table 1 rows provide no substrate scale, atmosphere, workup, or purification details in the supplied main text.", "Xylene is not given as a specific isomer, so no single solvent SMILES was assigned."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Figure 2, upper-left", "finding": "ORTEP structure of 8a; structural/stereochemical confirmation, not a separate experiment.", "evidence_ids": evid(3)},
                {"region": "Table 3, left-center", "finding": "Five Pd-catalyzed scope rows. The 6a row duplicates Table 2 entry 4; independent records are retained for 6b, 6c, 6l, and (S)-6m.", "evidence_ids": evid(3)},
                {"region": "Scheme 2, upper-right", "finding": "Diels–Alder reaction 8n + N-phenylmaleimide → 9na/9nb, 100% combined yield, ratio 100:3 by 300 MHz 1H NMR.", "evidence_ids": evid(3)},
                {"region": "Figure 3 and Scheme 3, right-center", "finding": "ORTEP of 9na and proposed Pd working model 10→11→8m; the latter is mechanism, not a reported experiment.", "evidence_ids": evid(3)},
                {"region": "Experimental Section, lower-right", "finding": "General procedure I supplies exact scale, Ar atmosphere, monitoring, workup, purification, mass, and yield for thermal 6a→7a; merged with Table 1 row 6a.", "evidence_ids": evid(3)},
            ],
            "record_ids": [thermal_ids[0], opt_ids[3]] + scope_ids + da_ids,
            "unresolved": ["Table 3 scope rows other than 6a do not state scale, atmosphere, workup, or purification.", "Exact product SMILES and stereochemistry remain unverified machine interpretations."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "General procedure II, upper-left", "finding": "Exact quantities, 80–85 °C/4 h conditions, TLC, evaporation, chromatography, product mass and 59% yield for 6a→8a; merged with Table 2 entry 4/Table 3 row 6a.", "evidence_ids": evid(4)},
                {"region": "Diels–Alder procedure, mid-left", "finding": "Exact quantities, dry toluene volume, reflux under Ar for 8 h, 24 mg/100% product and 9na/9nb 100:3 for 8n + N-phenylmaleimide.", "evidence_ids": evid(4)},
                {"region": "lower page and right column", "finding": "Characterization, bibliographic references, and crystal data; no additional independent reaction experiment.", "evidence_ids": evid(4)},
            ],
            "record_ids": [opt_ids[3]] + da_ids,
            "unresolved": ["Diels–Alder workup and purification operations are not stated in the supplied main text.", "No supporting-information PDF was explicitly provided or associated."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left references and notes 13–15", "finding": "References plus crystallographic data/CCDC identifiers for 7e, 8a, and 9na; no reaction arrow, conditions table, or independent synthesis experiment.", "evidence_ids": evid(5)},
                {"region": "remaining page", "finding": "Blank publication page area; no chemical experiment content.", "evidence_ids": evid(5)},
            ],
            "record_ids": [],
            "unresolved": ["Crystallographic data support identity/structure but do not supply reaction conditions and were not converted into reaction records."],
        },
    ],
}

COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "record_file": str(OUT), "coverage_file": str(COVERAGE)}, ensure_ascii=False))
