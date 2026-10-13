#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOC = "doc_8c906cf4ee850185"
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"

P1T, P1I = f"{DOC}:page1:text", f"{DOC}:page1:image"
P2T, P2I = f"{DOC}:page2:text", f"{DOC}:page2:image"
P3T, P3I = f"{DOC}:page3:text", f"{DOC}:page3:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def field(name, value, evidence=(), targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts),
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes=(), unresolved=()):
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
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def missing_conditions(include_time=False, include_temp=False):
    fields = []
    if include_temp:
        fields.append(field("temperature", None))
    if include_time:
        fields.append(field("time", None))
    fields.extend([
        field("atmosphere", None),
        field("workup", None),
        field("purification", None),
    ])
    return fields


def selectfluor(evidence, equiv=None, mass=None, amount=None):
    amounts = []
    if equiv is not None:
        amounts.append(field("equivalents", qty(equiv, "equiv"), evidence))
    if mass is not None:
        amounts.append(field("mass", qty(mass, "mg"), evidence))
    if amount is not None:
        amounts.append(field("amount", qty(amount, "mmol"), evidence))
    return participant(
        "selectfluor_1", "reagent", "1", evidence,
        "Selectfluor (F-TEDA-BF4)", None, amounts,
    )


def water(evidence, role="reagent", equiv=None, volume=None):
    amounts = []
    if equiv is not None:
        amounts.append(field("equivalents", qty(equiv, "equiv"), evidence))
    if volume is not None:
        amounts.append(field("volume", qty(volume[0], volume[1]), evidence))
    return participant("water", role, "H2O", evidence, "water", "O", amounts)


def substrate_2a(evidence, mass=None, amount=None):
    amounts = []
    if mass is not None:
        amounts.append(field("mass", qty(mass, "mg"), evidence))
    if amount is not None:
        amounts.append(field("amount", qty(amount, "mmol"), evidence))
    return participant(
        "substrate_2a", "reactant", "2a", evidence,
        "2,4-dimethyl-4-phenyl-2,3-butadienoic acid",
        "O=C(O)C(C)=C=C(C)c1ccccc1",
        amounts,
    )


def product_3a(evidence, mass=None):
    amounts = []
    if mass is not None:
        amounts.append(field("mass", qty(mass, "mg"), evidence))
    return participant(
        "product_3a", "product", "3a", evidence,
        "4-fluoro-3,5-dimethyl-5-phenyl-2(5H)-furanone",
        "CC1=C(F)C(C)(c2ccccc2)OC1=O", amounts,
    )


records = []

# Page-1 graphical abstract: a generic summary, not an individual execution.
ev = [P1T, P1I]
records.append(record(
    "graphical_abstract_general_scheme", "general_scheme", ev,
    [
        participant("generic_allenoic_acid", "reactant", "generic 2,3-allenoic acid", ev,
                    "R-substituted 2,3-allenoic acid"),
        selectfluor(ev),
        participant("generic_fluorobutenolide", "product", "generic beta-fluorobutenolide", ev,
                    "R-substituted beta-fluorobutenolide"),
    ],
    [{"step_id": "summary", "participant_ids": ["generic_allenoic_acid", "selectfluor_1", "generic_fluorobutenolide"],
      "conditions": [
          field("temperature", {"minimum": 80, "maximum": 100, "unit": "°C", "raw_text": "80-100 °C"}, ev),
          field("condition_A", "MeCN with 10 equiv H2O", ev),
          field("condition_B", "H2O", ev),
      ]}],
    [field("summary_reported_yield_range", {"minimum": 49, "maximum": 96, "unit": "%", "raw_text": "49-96%"}, ev,
           ["generic_fluorobutenolide"])],
    ["Graphical-abstract range summarizes later scope entries and is not a row-level experiment."],
    ["Generic R-group structures cannot be assigned complete constitutional SMILES.",
     "Time, atmosphere, workup, purification, and yield measurement basis are not given in the summary arrow."],
))

# Scheme 1: two explicitly described unsuccessful present-paper experiments.
scheme_ev = [P1T, P1I, P2T, P2I]
for rid, sub_label, sub_name, sub_smiles, result in [
    ("scheme1_4phenyl3butenoic_acid", "4-phenyl-3-butenoic acid", "4-phenyl-3-butenoic acid",
     "O=C(O)CC=Cc1ccccc1", "complicated mixture"),
    ("scheme1_3undecynoic_acid", "3-undecynoic acid", "3-undecynoic acid",
     "CCCCCCCC#CCC(=O)O", "no fluorinated products"),
]:
    parts = [
        participant("substrate", "reactant", sub_label, scheme_ev, sub_name, sub_smiles),
        selectfluor(scheme_ev),
        participant("mecn", "solvent", "MeCN", scheme_ev, "acetonitrile", "CC#N"),
        water(scheme_ev, equiv=10),
    ]
    records.append(record(
        rid, "reported_experiment", scheme_ev, parts,
        [{"step_id": "fluorination_attempt", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("temperature", qty(90, "°C"), scheme_ev), field("time", None),
                         field("atmosphere", None), field("workup", None), field("purification", None)]}],
        [field("reaction_outcome", result, scheme_ev)],
        ["Scheme 1 reports a present-paper screening attempt, not a cited literature reaction."],
        ["Selectfluor loading, duration, atmosphere, workup, purification, and analytical criterion are not reported.",
         "No discrete product identity or yield is reported."],
    ))


# Table 1 optimization entries.
table1 = [
    # entry, solvent label, solvent name, smiles, water equiv, selectfluor equiv, temp, result, byproducts
    (1, "EtOH", "ethanol", "CCO", None, 2.0, 80, "no reaction", False),
    (2, "EtOH/H2O = 20:1", "ethanol/water 20:1", None, None, 2.0, 80, 50, True),
    (3, "DMA", "N,N-dimethylacetamide", "CC(=O)N(C)C", 10, 2.0, 80, 63, False),
    (4, "CH3NO2", "nitromethane", "C[N+](=O)[O-]", 10, 2.0, 90, 69, False),
    (5, "DMF", "N,N-dimethylformamide", "CN(C)C=O", 10, 2.0, 80, 76, False),
    (6, "CH3CN", "acetonitrile", "CC#N", 10, 2.0, 90, 85, False),
    (7, "CH3CN", "acetonitrile", "CC#N", None, 2.0, 90, 71, False),
    (8, "CH3CN", "acetonitrile", "CC#N", 10, 1.1, 90, 86, False),
    (9, "H2O", "water", "O", None, 1.1, 90, 78, False),
]

for entry, solv_label, solv_name, solv_smiles, water_eq, sel_eq, temp, result, byproducts in table1:
    tev = [P2T, P2I]
    if entry <= 6:
        tev = [P1T, P1I, P2T, P2I]
    parts = [substrate_2a(tev), selectfluor(tev, sel_eq), product_3a(tev)]
    if entry == 2:
        parts.extend([
            participant("ethanol", "solvent", "EtOH", tev, "ethanol", "CCO"),
            water(tev, role="solvent"),
        ])
    elif entry == 9:
        parts.append(water(tev, role="solvent"))
    else:
        parts.append(participant("solvent", "solvent", solv_label, tev, solv_name, solv_smiles))
        if water_eq is not None:
            parts.append(water(tev, equiv=water_eq))
    outcomes = []
    if isinstance(result, (int, float)):
        outcomes.extend([
            field("product_NMR_yield", qty(result, "%"), tev, ["product_3a"]),
            field("yield_measurement_basis", "NMR", tev, ["product_3a"]),
        ])
    else:
        outcomes.append(field("reaction_outcome", result, tev, ["product_3a"]))
    if byproducts:
        outcomes.append(field("byproduct_outcome", "byproducts were also formed", tev))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", tev, parts,
        [{"step_id": "lactonization", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [field("time", qty(10, "h"), tev), field("temperature", qty(temp, "°C"), tev)]
                        + missing_conditions()}],
        outcomes,
        [f"Table 1 entry {entry}; footnote-c 90 °C override applied only where marked."],
        ["Substrate scale, atmosphere, workup, and purification are not reported for this optimization row."],
    ))


# Table 2 scope entries and their condition definitions.
scope = [
    (1, "Ph", "Me", "Me", "2a", "3a", "A", 81, "isolated", None),
    (2, "Ph", "Me", "Me", "2a", "3a", "B", 75, "isolated", None),
    (3, "Ph", "Et", "n-Pr", "2b", "3b", "A", 81, "isolated", None),
    (4, "Ph", "Et", "n-Pr", "2b", "3b", "B", 59, "isolated", None),
    (5, "Ph", "Et", "Me", "2c", "3c", "B", 86, "isolated", None),
    (6, "Ph", "Ph", "Me", "2d", "3d", "A", 96, "isolated", None),
    (7, "Ph", "Ph", "n-Pr", "2e", "3e", "A", 94, "isolated", None),
    (8, "Ph", "Me", "H", "2f", "3f", "A", 61, "isolated", None),
    (9, "Ph", "Me", "H", "2f", "3f", "B", 70, "isolated", None),
    (10, "Ph", "Ph", "H", "2g", "3g", "A", 65, "isolated", None),
    (11, "Ph", "H", "n-Pr", "2h", "3h", "A", 39, "isolated", {"select": 1.5}),
    (12, "Ph", "H", "n-Pr", "2h", "3h", "B", 9, "NMR", {"recovery": 52}),
    (13, "Ph", "H", "n-Pr", "2h", "3h", "A", 49, "isolated", {"select": 1.5, "temp": 100, "time": 18, "screw": True}),
    (14, "Ph", "H", "Me", "2i", "3i", "B", 19, "isolated", None),
    (15, "Ph", "H", "Me", "2i", "3i", "A", 64, "isolated", {"select": 1.5, "temp": 95, "screw": True}),
    (16, "(CH2)4", "(CH2)4", "Me", "2j", "3j", "A", 53, "isolated", None),
    (17, "(CH2)4", "(CH2)4", "Me", "2j", "3j", "B", 34, "isolated", {"select": 1.2}),
]

scope_ids = []
for entry, r1, r2, r3, sublab, prodlab, cond, yld, basis, override in scope:
    rid = f"table2_entry{entry}_{prodlab}"
    scope_ids.append(f"{DOC}:{rid}")
    sev = [P2T, P2I]
    if entry in (1, 2):
        sev = [P2T, P2I, P3T, P3I]
    detailed = entry in (1, 2)
    subid = f"substrate_{sublab}"
    prodid = f"product_{prodlab}"
    if entry == 1:
        sub = substrate_2a(sev, 94.0, 0.5)
        prod = product_3a(sev, 83.1)
    elif entry == 2:
        sub = substrate_2a(sev, 56.5, 0.3)
        prod = product_3a(sev, 46.3)
    else:
        sub = participant(subid, "reactant", sublab, sev,
                          f"2,3-allenoic acid {sublab} (R1={r1}, R2={r2}, R3={r3})")
        prod = participant(prodid, "product", prodlab, sev,
                           f"beta-fluorobutenolide {prodlab}")

    select_eq = 1.1
    if override and "select" in override:
        select_eq = override["select"]
    sel_mass = 194.5 if entry == 1 else 116.8 if entry == 2 else None
    sel_amount = 0.55 if entry == 1 else 0.33 if entry == 2 else None
    parts = [sub, selectfluor(sev, select_eq, sel_mass, sel_amount), prod]
    if cond == "A":
        parts.append(participant("mecn", "solvent", "MeCN", sev, "acetonitrile", "CC#N",
                                 [field("volume", qty(5.0, "mL"), sev)] if entry == 1 else []))
        parts.append(water(sev, equiv=10, volume=(90, "uL") if entry == 1 else None))
        temp = 90
    else:
        parts.append(water(sev, role="solvent", volume=(3.0, "mL") if entry == 2 else None))
        temp = 90
    time = 10
    if override:
        temp = override.get("temp", temp)
        time = override.get("time", time)

    conds = [field("time", qty(time, "h"), sev), field("temperature", qty(temp, "°C"), sev)]
    if entry == 1:
        conds.append(field("detailed_procedure_temperature", qty(80, "°C"), sev))
    if override and override.get("screw"):
        conds.append(field("vessel", "reaction tube with a screw cap", sev))
    if detailed:
        conds.extend([
            field("monitoring", "TLC", sev),
            field("atmosphere", None),
        ])
        if entry == 1:
            conds.extend([
                field("workup", "quenched with 10 mL water; extracted with diethyl ether (30 mL then 25 mL twice); washed with brine; dried over anhydrous Na2SO4; evaporated", sev),
                field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", sev),
            ])
        else:
            conds.extend([
                field("workup", "extracted with diethyl ether (30 mL then 25 mL twice); washed with brine; dried over anhydrous Na2SO4; evaporated", sev),
                field("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", sev),
            ])
    else:
        conds.extend(missing_conditions())

    outcomes = [
        field("product_reported_yield", qty(yld, "%"), sev, [prodid]),
        field("yield_measurement_basis", basis, sev, [prodid]),
    ]
    if override and "recovery" in override:
        outcomes.append(field("recovered_starting_material_yield", qty(override["recovery"], "%"), sev, [subid]))
    notes = [f"Table 2 entry {entry}: R1={r1}, R2={r2}, R3={r3}; conditions {cond}."]
    unresolved = ["Product/substrate connectivity and stereochemistry are machine-unverified."]
    if cond == "A":
        unresolved.append("Condition A is defined by Table 1 entry 8 at 90 °C; the detailed 3a procedure reports 80 °C. The source conflict is retained.")
    if not detailed:
        unresolved.append("Atmosphere, workup, and purification are not reported for this abbreviated scope row.")
    if override and override.get("screw") and entry == 15:
        unresolved.append("The 95 °C footnote gives no row-specific duration; 10 h is retained from the defined condition A.")
    records.append(record(
        rid, "substrate_scope_entry", sev, parts,
        [{"step_id": "fluorolactonization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conds}],
        outcomes, notes, unresolved,
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

table1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 10)]
scheme_ids = [f"{DOC}:scheme1_4phenyl3butenoic_acid", f"{DOC}:scheme1_3undecynoic_acid"]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract and abstract, upper-left", "finding": "Generic fluorolactonization summary classified as a general scheme; it is not a row-level execution.", "evidence_ids": [P1I, P1T]},
                {"region": "results prose, upper-right", "finding": "Narrative evidence for the two Scheme 1 screening failures and Table 1 entries 1-6; linked to later page-2 records rather than duplicated.", "evidence_ids": [P1I, P1T]},
                {"region": "introduction and references", "finding": "Background fluorination/allene literature only; no additional present-paper experiment extracted.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": [f"{DOC}:graphical_abstract_general_scheme"] + scheme_ids + table1_ids[:6],
            "unresolved": ["The graphical-abstract R-group structures are generic.", "Background cited papers were not supplied as associated sources."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 1, upper-left", "finding": "Two present-paper screening attempts extracted independently: one complicated mixture and one no-fluorinated-products result.", "evidence_ids": [P2I, P2T]},
                {"region": "Table 1 and footnotes, left-center", "finding": "All nine optimization entries extracted independently with water/loading/temperature footnote handling and NMR-yield basis.", "evidence_ids": [P2I, P2T]},
                {"region": "Table 2 and footnotes, upper-right", "finding": "All 17 substrate-scope rows extracted independently; footnote overrides and recovered 2h are preserved.", "evidence_ids": [P2I, P2T]},
                {"region": "discussion and Experimental Section opening", "finding": "Conditions A/B definitions and the beginning of the exact conditions-A procedure were merged into corresponding rows; no duplicate records created.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": scheme_ids + table1_ids + scope_ids,
            "unresolved": ["Condition A is 90 °C in its defining Table 1 row but 80 °C in the detailed 3a procedure.", "Most scope structures remain machine-unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left column, completion of conditions-A procedure and 3a characterization", "finding": "Exact isolation, 81% yield, workup, purification, and product mass merged into Table 2 entry 1; characterization does not define a new reaction.", "evidence_ids": [P3I, P3T]},
                {"region": "left-to-right columns, conditions-B procedure", "finding": "Exact aqueous conditions-B execution and 75% isolated yield merged into Table 2 entry 2.", "evidence_ids": [P3I, P3T]},
                {"region": "acknowledgment and Supporting Information Available statement", "finding": "Reproduction note linked contextually; online SI availability is not treated as supplied SI.", "evidence_ids": [P3I, P3T]},
            ],
            "record_ids": [f"{DOC}:table2_entry1_3a", f"{DOC}:table2_entry2_3a"],
            "unresolved": ["No SI PDF was supplied or explicitly associated.", "Spectral characterization was not used to mark the machine SMILES as verified."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
