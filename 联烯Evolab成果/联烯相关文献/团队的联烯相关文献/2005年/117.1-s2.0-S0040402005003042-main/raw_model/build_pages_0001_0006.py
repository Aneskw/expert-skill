#!/usr/bin/env python3
"""Build source-derived machine records and coverage for PDF pages 1--6.

This is an extraction artifact, not a source-review certification.  The merge
tool will quarantine all records as needs_review and all facts as unreviewed.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_77c72f16fe1e869a"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def uniq(values):
    return list(dict.fromkeys(values))


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    out = {"name": name, "fact": fact(value, evidence)}
    if targets:
        out["target_entity_ids"] = list(targets)
    return out


def qty(number, unit, **extra):
    out = {"number": number, "unit": unit}
    out.update(extra)
    return out


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence if name is not None else []),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": list(amounts or []),
    }


def record(suffix, kind, evidence, participants, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": uniq(evidence),
        "participants": participants,
        "steps": list(steps or []),
        "outcomes": list(outcomes or []),
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []),
        },
    }


SMILES = {
    "1a": "C=C=C(Cc1ccccc1)C(=O)C",
    "1b": "C=C=C(CC=C)C(=O)C",
    "1c": "C=C=C(CCCC)C(=O)C",
    "1d": "C=C=C(c1ccccc1)C(=O)Cc1ccccc1",
    "1e": "C=C=CC(=O)CCCCCCCC",
    "1f": "C=C=CC(=O)CCCCCCC",
    # 1g is deliberately omitted: Table 2 prints R3=H/R4=H, while the
    # reported mass and product name imply an allenic methyl ketone.
    "1h": "CCCCC=C=CC(=O)C",
    "1i": "CCCCCCCC=C=CC(=O)C",
    "1j": "CCCCCCCC=C=CC(=O)CCCCCCC",
    "4a": "CCOC(=O)C(C)C(=O)OCC",
    "4b": "C=CCC(C(=O)OCC)C(=O)OCC",
    "4c": "CCOC(=O)C(Cc1ccccc1)C(=O)OCC",
    "4d": "C=CCC(C#N)C#N",
    "5aa": "CC(=O)C(Cc1ccccc1)C(=C)C(C)(C(=O)OCC)C(=O)OCC",
    "5ab": "CC(=O)C(Cc1ccccc1)C(=C)C(CC=C)(C(=O)OCC)C(=O)OCC",
    "5ac": "CC(=O)C(Cc1ccccc1)C(=C)C(Cc1ccccc1)(C(=O)OCC)C(=O)OCC",
    "5ba": "CC(=O)C(CC=C)C(=C)C(C)(C(=O)OCC)C(=O)OCC",
    "5bb": "CC(=O)C(CC=C)C(=C)C(CC=C)(C(=O)OCC)C(=O)OCC",
    "5bc": "CC(=O)C(CC=C)C(=C)C(Cc1ccccc1)(C(=O)OCC)C(=O)OCC",
    "5ca": "CC(=O)C(CCCC)C(=C)C(C)(C(=O)OCC)C(=O)OCC",
    "5da": "O=C(CC1=CC=CC=C1)C(c1ccccc1)C(=C)C(C)(C(=O)OCC)C(=O)OCC",
    "5ea": "C=C(C(C)(C(=O)OCC)C(=O)OCC)CC(=O)CCCCCCCC",
    "5fa": "C=C(C(C)(C(=O)OCC)C(=O)OCC)CC(=O)CCCCCCC",
    "5ga": "C=C(C(C)(C(=O)OCC)C(=O)OCC)CC(=O)C",
    "5ha": "CC(=O)CC(=CCCCC)C(C)(C(=O)OCC)C(=O)OCC",
    "5ia": "CC(=O)CC(=CCCCCCCC)C(C)(C(=O)OCC)C(=O)OCC",
    "5ja": "CCCCCCCC(=O)CC(=CCCCCCCC)C(C)(C(=O)OCC)C(=O)OCC",
    "5ad": "CC(=O)C(Cc1ccccc1)C(=C)C(CC=C)(C#N)C#N",
    "5bd": "CC(=O)C(CC=C)C(=C)C(CC=C)(C#N)C#N",
    "5cd": "CC(=O)C(CCCC)C(=C)C(CC=C)(C#N)C#N",
    "acetone": "CC(=O)C",
    "DMF": "CN(C)C=O",
    "EtOH": "CCO",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "NEt3": "CCN(CC)CC",
    "pyridine": "n1ccccc1",
    "DABCO": "C1CN2CCN1CC2",
    "NaOAc": "CC(=O)[O-].[Na+]",
    "NaOEt": "CC[O-].[Na+]",
    "NaOH": "[OH-].[Na+]",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O",
    "DBU": "C1CCC2=NCCCN2CC1",
    "t-BuOK": "CC(C)(C)[O-].[K+]",
}


NAMES = {
    "1a": "2-benzyl-1,2-propadienyl methyl ketone",
    "1b": "alpha-allyl-1,2-allenic methyl ketone",
    "1c": "alpha-n-butyl-1,2-allenic methyl ketone",
    "1d": "alpha-phenyl-1,2-allenic benzyl ketone",
    "1e": "1,2-allenic n-octyl ketone",
    "1f": "1,2-allenic n-heptyl ketone",
    "1g": "1,2-allenic ketone 1g",
    "1h": "gamma-n-butyl-1,2-allenic methyl ketone",
    "1i": "gamma-n-heptyl-1,2-allenic methyl ketone",
    "1j": "gamma-n-heptyl-1,2-allenic n-heptyl ketone",
    "4a": "diethyl 2-methylmalonate",
    "4b": "diethyl 2-allylmalonate",
    "4c": "diethyl 2-benzylmalonate",
    "4d": "2-allylmalononitrile",
    "5aa": "3-benzyl-4-(1',1'-bis(ethoxycarbonyl)ethyl)-4-penten-2-one",
    "5ab": "3-benzyl-4-methylene-5,5-bis(ethoxycarbonyl)-7-octen-2-one",
    "5ac": "3-benzyl-4-(1',1'-bis(ethoxycarbonyl)-2'-phenylethyl)-4-penten-2-one",
    "5ba": "3-(1'-methylene-2',2'-bis(ethoxycarbonyl)propyl)-5-hexen-2-one",
    "5bb": "3-allyl-4-methylene-5-bis(ethoxycarbonyl)-7-octen-2-one",
    "5bc": "3-(1'-methylene-2',2'-bis(ethoxycarbonyl)-3'-phenylpropyl)-5-hexen-2-one",
    "5ca": "3-butyl-4-(1',1'-bis(ethoxycarbonyl)ethyl)-4-penten-2-one",
    "5da": "1,3-diphenyl-4-(1',1'-bis(ethoxycarbonyl)ethyl)-4-penten-2-one",
    "5ea": "2-(1',1'-bis(ethoxycarbonyl)ethyl)-1-dodecen-4-one",
    "5fa": "2-(1',1'-bis(ethoxycarbonyl)ethyl)-1-undecen-4-one",
    "5ga": "4-(1',1'-bis(ethoxycarbonyl)ethyl)-4-penten-2-one",
    "5ha": "(E)-4-(1',1'-bis(ethoxycarbonyl)ethyl)-4-nonen-2-one",
    "5ia": "(E)-4-(1',1'-bis(ethoxycarbonyl)ethyl)-4-dodecen-2-one",
    "5ja": "(E)-10-(1',1'-bis(ethoxycarbonyl)ethyl)-10-octadecen-8-one",
    "5ad": "3-benzyl-4-methylene-5,5-biscyano-7-octen-2-one",
    "5bd": "3-allyl-4-methylene-5,5-biscyano-7-octen-2-one",
    "5cd": "3-butyl-4-methylene-5,5-biscyano-7-octen-2-one",
}


def chemical(label, role, evidence, *, amounts=None, name=None, smiles="AUTO"):
    if name is None:
        name = NAMES.get(label)
    if smiles == "AUTO":
        smiles = SMILES.get(label)
    return participant(label.replace("-", "_"), role, label, evidence,
                       name=name, smiles=smiles, amounts=amounts)


def unknown_amount(name="amount"):
    return [field(name, None)]


records = []

# Page 1: authors' prior generic work; structures are generic R-group drawings.
records.append(record(
    "scheme1_prior_work", "literature_example", ev(1),
    [
        participant("scheme1_1", "reactant", "1", ev(1), name="generic 1,2-allenic ketone", smiles=None),
        participant("scheme1_malonate", "reactant", "diethyl malonate", ev(1),
                    name="diethyl malonate", smiles="CCOC(=O)CC(=O)OCC"),
        participant("scheme1_2", "product", "2", ev(1), name="generic beta,gamma-unsaturated enone 2", smiles=None),
        participant("scheme1_3", "product", "3", ev(1), name="generic alpha,beta-unsaturated enone 3", smiles=None),
        participant("scheme1_6", "product", "6", ev(1), name="generic lactone 6", smiles=None),
    ],
    notes=[
        "Scheme 1 summarizes the authors' previous work: substitution controls formation of 2, 3, or a mixture, and the scheme also depicts formation of 6.",
        "Generic R-group structures are not expanded to SMILES.",
    ],
    unresolved=[
        "Prior-literature scheme only; individual experimental conditions and yields are not reported on page 1.",
        "The relation of the right-hand arrow to each generic branch cannot be resolved as a discrete experiment from this page.",
    ],
))

# Page 2, Scheme 2: proposed generic transformation, not a discrete experiment.
records.append(record(
    "scheme2_proposed_general", "general_scheme", ev(2),
    [
        participant("scheme2_1", "reactant", "1", ev(2), name="generic 1,2-allenic ketone", smiles=None),
        participant("scheme2_4", "reactant", "4", ev(2), name="generic 2-substituted diethyl malonate", smiles=None),
        participant("scheme2_5", "product", "5", ev(2), name="generic beta,gamma-unsaturated enone", smiles=None),
        participant("scheme2_base", "unspecified_agent", "base", ev(2), name=None, smiles=None),
        participant("scheme2_solvent", "solvent", "solvent", ev(2), name=None, smiles=None),
    ],
    notes=["Scheme 2 is a proposed reaction class with unspecified base and solvent, not an individual reported experiment."],
    unresolved=["Generic R groups, base, solvent, quantities, time, temperature, and yield are unspecified."],
))


def opt_record(suffix, evidence, solvent_label, solvent_name, solvent_smiles,
               base_label, base_name, base_smiles, base_amount,
               time_value, temperature, yield_value, recovered=None,
               detailed=None, notes=None):
    detailed = detailed or {}
    all_ev = uniq(evidence + detailed.get("evidence", []))
    p1_amounts = detailed.get("1a_amounts", unknown_amount())
    p4_amounts = detailed.get("4a_amounts", unknown_amount())
    product_amounts = []
    participants = [
        chemical("1a", "reactant", all_ev, amounts=p1_amounts),
        chemical("4a", "reactant", all_ev, amounts=p4_amounts),
        chemical(base_label, "catalyst" if base_label == "t-BuOK" else "reagent", evidence,
                 amounts=[field("equivalents", base_amount, evidence)] if base_amount and base_amount.get("unit") == "equiv" else
                         ([field("catalyst_loading", base_amount, evidence)] if base_amount else unknown_amount()),
                 name=base_name, smiles=base_smiles),
        chemical(solvent_label, "solvent", evidence,
                 amounts=detailed.get("solvent_amounts", unknown_amount("volume")),
                 name=solvent_name, smiles=solvent_smiles),
        chemical("5aa", "product", all_ev, amounts=product_amounts),
    ]
    conditions = [
        field("time", time_value, evidence),
        field("temperature", temperature, evidence),
        field("atmosphere", None),
    ]
    steps = [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants[:-1]], "conditions": conditions}]
    if detailed:
        steps.append({
            "step_id": "isolation",
            "participant_ids": ["5aa"],
            "conditions": [
                field("operation", "solvent evaporated after reaction", ev(4)),
                field("purification", "silica gel chromatography; petroleum ether/ethyl acetate 10:1", ev(4)),
            ],
        })
    else:
        steps.append({
            "step_id": "workup_and_isolation",
            "participant_ids": ["5aa"],
            "conditions": [field("workup", None), field("purification", None)],
        })
    outcomes = [field("yield", yield_value, evidence, ["5aa"])]
    if yield_value not in ("no reaction", "NR"):
        outcomes.append(field(
            "yield_measurement_basis",
            "isolated after silica gel chromatography" if detailed else None,
            ev(4) if detailed else None,
            ["5aa"],
        ))
    if detailed.get("product_mass"):
        outcomes.append(field("product_mass", detailed["product_mass"], detailed["evidence"], ["5aa"]))
    if recovered is not None:
        outcomes.append(field("recovered_starting_material", recovered, evidence, ["1a"]))
    unresolved = ["Supporting-information association is unestablished.", "Atmosphere is not reported."]
    if not detailed:
        unresolved += ["Reactant and solvent quantities are not reported for this optimization row.",
                       "Workup, purification, and yield measurement basis are not reported for this row."]
    return record(suffix, "optimization_entry", all_ev, participants, steps, outcomes,
                  notes=notes, unresolved=unresolved)


# Scheme 3 solvent screen: common 10 mol% K2CO3 and 11.5 h are printed over the arrow.
scheme3_rows = [
    ("acetone", "acetone", SMILES["acetone"], "reflux", 44, qty(30, "%")),
    ("DMF", "N,N-dimethylformamide", SMILES["DMF"], qty(80, "°C"), 27, None),
    ("EtOH", "ethanol", SMILES["EtOH"], qty(80, "°C"), 9, None),
]
for i, (solv, solv_name, solv_smiles, temp, yld, recovered) in enumerate(scheme3_rows, 1):
    records.append(opt_record(
        f"scheme3_solvent_entry{i}", ev(2), solv, solv_name, solv_smiles,
        "K2CO3", "potassium carbonate", SMILES["K2CO3"], qty(10, "mol%"),
        qty(11.5, "h"), temp, qty(yld, "%"), recovered,
        notes=["Scheme 3 solvent-screen row under 10 mol% K2CO3."],
    ))


table1_rows = [
    (1, "K2CO3", "potassium carbonate", qty(11.5, "h"), "reflux", qty(75, "%"), None),
    (2, "NEt3", "triethylamine", qty(12, "h"), "reflux", "no reaction", None),
    (3, "pyridine", "pyridine", qty(12, "h"), "reflux", "no reaction", None),
    (4, "DABCO", "1,4-diazabicyclo[2.2.2]octane", qty(12, "h"), "reflux", "no reaction", None),
    (5, "NaOAc", "sodium acetate", qty(12.5, "h"), "reflux", qty(5, "%"), qty(53, "%")),
    (6, "NaOEt", "sodium ethoxide", qty(12.5, "h"), "reflux", qty(4, "%"), qty(49, "%")),
    (7, "NaOH", "sodium hydroxide", qty(12.5, "h"), "reflux", qty(52, "%"), None),
    (8, "Cs2CO3", "cesium carbonate", qty(1, "h"), "reflux", qty(78, "%"), None),
    (9, "DBU", "1,8-diazabicyclo[5.4.0]undec-7-ene", qty(10, "min"), "r.t.", qty(80, "%"), None),
    (10, "t-BuOK", "potassium tert-butoxide", qty(10, "min"), "r.t.", qty(82, "%"), None),
]
for idx, base, base_name, time_value, temp, yld, recovered in table1_rows:
    detailed = None
    base_amount = qty(1, "equiv")
    if idx == 10:
        base_amount = qty(10, "mol%")
        detailed = {
            "evidence": ev(4),
            "1a_amounts": [field("mass", qty(202, "mg"), ev(4)), field("amount", qty(1.2, "mmol"), ev(4))],
            "4a_amounts": [field("mass", qty(174, "mg"), ev(4)), field("amount", qty(1.0, "mmol"), ev(4))],
            "solvent_amounts": [field("volume", qty(2, "mL"), ev(4))],
            "product_mass": qty(282, "mg"),
        }
    rec = opt_record(
        f"table1_entry{idx:02d}", ev(2), "acetone", "acetone", SMILES["acetone"],
        base, base_name, SMILES[base], base_amount, time_value, temp, yld, recovered,
        detailed=detailed,
        notes=["Table 1 base-screen entry; the table header supplies acetone and, except entry 10, 1 equivalent of base."],
    )
    if idx == 10:
        # Replace the catalyst loading-only amount with the exact mass and mmol from section 2.1.1.
        bp = next(p for p in rec["participants"] if p["entity_id"] == "t_BuOK")
        bp["amounts"] += [field("mass", qty(12, "mg"), ev(4)), field("amount", qty(0.1, "mmol"), ev(4))]
    records.append(rec)


DETAIL = {
    "5ab": (4, "1a", 172, 1.0, "4b", 200, 1.0, 11, 0.1, 316, 85),
    "5ac": (4, "1a", 172, 1.0, "4c", 250, 1.0, 11, 0.1, 342, 81),
    "5ba": (5, "1b", 122, 1.0, "4a", 174, 1.0, 11, 0.1, 309, 83),
    "5bb": (5, "1b", 122, 1.0, "4b", 200, 1.0, 11, 0.1, 251, 78),
    "5bc": (5, "1b", 122, 1.0, "4c", 250, 1.0, 11, 0.1, 283, 76),
    "5ca": (5, "1c", 138, 1.0, "4a", 174, 1.0, 112, 1.0, 259, 83),
    "5da": (5, "1d", 234, 1.0, "4a", 209, 1.2, 11.0, 0.1, 261, 64),
    "5ea": (6, "1e", 180, 1.0, "4a", 174, 1.0, 11.0, 0.1, 234, 66),
    "5fa": (6, "1f", 166, 1.0, "4a", 174, 1.0, 11, 0.1, 211, 62),
    "5ga": (6, "1g", 82, 1.0, "4a", 209, 1.2, 11.0, 0.1, 113, 44),
    "5ha": (6, "1h", 138, 1.0, "4a", 209, 1.2, 12.0, 0.1, 153, 49),
    "5ia": (6, "1i", 180, 1.0, "4a", 174, 1.0, 11.0, 0.1, 207, 59),
    "5ja": (6, "1j", 264, 1.0, "4a", 174, 1.0, 11, 0.1, 232, 53),
}


def scope_record(suffix, page3_evidence, start_label, malonate_label, product_label,
                 yield_value, catalyst_loading, detailed_key=None, *, kind="substrate_scope_entry",
                 extra_notes=None, stereo_note=None):
    detail = DETAIL.get(detailed_key or product_label)
    detail_ev = ev(detail[0]) if detail else []
    all_ev = uniq(page3_evidence + ev(4) + detail_ev)
    if detail:
        _, _, smass, samount, _, mmass, mamount, bmass, bamount, pmass, _ = detail
        start_amounts = [field("mass", qty(smass, "mg"), detail_ev), field("amount", qty(samount, "mmol"), detail_ev)]
        mal_amounts = [field("mass", qty(mmass, "mg"), detail_ev), field("amount", qty(mamount, "mmol"), detail_ev)]
        base_amounts = [field("catalyst_loading", catalyst_loading, page3_evidence),
                        field("mass", qty(bmass, "mg"), detail_ev), field("amount", qty(bamount, "mmol"), detail_ev)]
    else:
        start_amounts = unknown_amount()
        mal_amounts = unknown_amount()
        base_amounts = [field("catalyst_loading", catalyst_loading, page3_evidence)]
    participants = [
        chemical(start_label, "reactant", all_ev, amounts=start_amounts),
        chemical(malonate_label, "reactant", all_ev, amounts=mal_amounts),
        chemical("t-BuOK", "catalyst", all_ev, name="potassium tert-butoxide", smiles=SMILES["t-BuOK"], amounts=base_amounts),
        chemical("acetone", "solvent", all_ev, name="acetone", smiles=SMILES["acetone"],
                 amounts=[field("volume", qty(2, "mL"), detail_ev)] if detail else unknown_amount("volume")),
        chemical(product_label, "product", all_ev),
    ]
    steps = [{
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in participants[:-1]],
        "conditions": [field("time", qty(10, "min"), page3_evidence), field("temperature", "r.t.", page3_evidence), field("atmosphere", None)],
    }, {
        "step_id": "isolation",
        "participant_ids": [product_label],
        "conditions": [
            field("operation", "solvent evaporated after reaction", ev(4)),
            field("purification", "silica gel chromatography; petroleum ether/ethyl acetate 10:1", ev(4)),
        ],
    }]
    outcomes = [field("yield", yield_value, page3_evidence, [product_label])]
    if detail:
        outcomes += [
            field("product_mass", qty(detail[9], "mg"), detail_ev, [product_label]),
            field("yield_measurement_basis", "isolated after silica gel chromatography", uniq(ev(4) + detail_ev), [product_label]),
        ]
    else:
        outcomes.append(field("yield_measurement_basis", None, None, [product_label]))
    notes = list(extra_notes or [])
    if stereo_note:
        notes.append(stereo_note)
    unresolved = ["Supporting-information association is unestablished.", "Atmosphere is not reported."]
    if not detail:
        unresolved += ["Exact reactant/catalyst masses, mmol values, and solvent volume are not reported in the inspected pages.",
                       "Yield measurement basis is not reported in the inspected pages."]
    if start_label == "1g":
        unresolved.append("Table 2 prints R3=H and R4=H for 1g, but section 2.1.11 reports 82 mg/mmol and a methyl-ketone product; the starting structure is therefore left without SMILES.")
    return record(suffix, kind, all_ev, participants, steps, outcomes, notes=notes, unresolved=unresolved)


table2_rows = [
    (1, "1a", "4b", "5ab", qty(85, "%"), qty(10, "mol%")),
    (2, "1a", "4c", "5ac", qty(81, "%"), qty(10, "mol%")),
    (3, "1b", "4a", "5ba", qty(83, "%"), qty(10, "mol%")),
    (4, "1b", "4b", "5bb", qty(78, "%"), qty(10, "mol%")),
    (5, "1b", "4c", "5bc", qty(76, "%"), qty(10, "mol%")),
    (6, "1c", "4a", "5ca", "trace", qty(10, "mol%")),
    (7, "1c", "4a", "5ca", qty(83, "%"), qty(100, "mol%")),
    (8, "1d", "4a", "5da", qty(64, "%"), qty(10, "mol%")),
    (9, "1e", "4a", "5ea", qty(66, "%"), qty(10, "mol%")),
    (10, "1f", "4a", "5fa", qty(62, "%"), qty(10, "mol%")),
    (11, "1g", "4a", "5ga", qty(44, "%"), qty(10, "mol%")),
]
for idx, start, mal, prod, yld, loading in table2_rows:
    detail_key = None if idx == 6 else prod
    records.append(scope_record(
        f"table2_entry{idx:02d}", ev(3), start, mal, prod, yld, loading, detail_key,
        extra_notes=["Table 2 row; entry 7 footnote overrides the standard catalyst loading with 100 mol% t-BuOK."] if idx == 7 else ["Table 2 substrate-scope row."],
    ))


for prod, start, yld in [("5ha", "1h", 49), ("5ia", "1i", 59), ("5ja", "1j", 53)]:
    records.append(scope_record(
        f"scheme4_{prod}", ev(3), start, "4a", prod, qty(yld, "%"), qty(10, "mol%"), prod,
        extra_notes=["Scheme 4 substrate-scope row."],
        stereo_note="The paper reports the E product as the sole product; E assignment is stated to be based on 1H-1H NOESY (Figure 1).",
    ))


for prod, start, yld in [("5ad", "1a", 65), ("5bd", "1b", 63), ("5cd", "1c", 79)]:
    records.append(scope_record(
        f"scheme5_{prod}", ev(3), start, "4d", prod, qty(yld, "%"), qty(10, "mol%"), None,
        extra_notes=["Scheme 5 substrate-scope row. The printed table header says 'yield of 7 (%)' although the products are labeled 5ad, 5bd, and 5cd."],
    ))


failed_labels = [
    ("allyl_acetoacetone", "2-allyl-substituted acetoacetone"),
    ("ethyl_nitroacetate", "nitroacetic acid ethyl ester"),
    ("ethyl_benzenesulfonylacetate", "benzenesulfonylacetic acid ethyl ester"),
]
for suffix, label in failed_labels:
    p = participant("active_methylene_compound", "reactant", label, ev(3), name=label, smiles=None,
                    amounts=unknown_amount())
    records.append(record(
        f"failed_{suffix}", "substrate_scope_entry", ev(3), [p],
        steps=[{
            "step_id": "treatment",
            "participant_ids": ["active_methylene_compound"],
            "conditions": [
                field("operation", "treated similarly to the Scheme 5 transformation", ev(3)),
                field("time", None), field("temperature", None), field("solvent", None),
            ],
        }],
        outcomes=[field("reaction_result", "complicated reaction observed", ev(3))],
        notes=["The prose groups three alternative active-methylene compounds and reports complicated reactions."],
        unresolved=[
            "The accompanying allenic-ketone partner is not identified for this failed observation.",
            "The phrase 'treated similarly' does not establish exact quantities, time, temperature, or solvent for this individual compound.",
            "No product identity or yield is reported.",
            "Supporting-information association is unestablished.",
        ],
    ))


records.append(record(
    "scheme6_mechanism", "mechanism", uniq(ev(3) + ev(4)),
    [
        participant("scheme6_4", "reactant", "4", ev(3), name="generic substituted malonate", smiles=None),
        participant("scheme6_base", "unspecified_agent", "base", ev(3), name=None, smiles=None),
        participant("scheme6_8", "unspecified_agent", "8", ev(3), name="proposed malonate anion", smiles=None),
        participant("scheme6_1", "reactant", "1", ev(3), name="generic 1,2-allenic ketone", smiles=None),
        participant("scheme6_9", "unspecified_agent", "9", ev(3), name="proposed addition intermediate", smiles=None),
        participant("scheme6_5", "product", "5", ev(3), name="generic beta,gamma-unsaturated enone", smiles=None),
        participant("scheme6_tBuOH", "unspecified_agent", "t-BuOH", ev(3), name="tert-butanol", smiles="CC(C)(C)O"),
    ],
    notes=[
        "Scheme 6 is a proposed catalytic rationale: base generates anion 8, addition gives intermediate 9, and proton transfer affords 5 while regenerating 8.",
        "This mechanism is not treated as a discrete reported experiment.",
    ],
    unresolved=["Generic R groups and E substituents are not expanded; mechanistic intermediates are proposed rather than experimentally isolated here."],
))


assert len(records) == 36, len(records)
assert len({r["record_id"] for r in records}) == len(records)


ids = {r["source_reaction_id"]: r["record_id"] for r in records}
page2_ids = [ids["scheme2_proposed_general"]] + [ids[f"scheme3_solvent_entry{i}"] for i in range(1, 4)] + [ids[f"table1_entry{i:02d}"] for i in range(1, 11)]
page3_ids = [ids[f"table2_entry{i:02d}"] for i in range(1, 12)] + [ids[f"scheme4_{p}"] for p in ("5ha", "5ia", "5ja")] + [ids[f"scheme5_{p}"] for p in ("5ad", "5bd", "5cd")] + [ids[f"failed_{s}"] for s, _ in failed_labels] + [ids["scheme6_mechanism"]]
page4_ids = [ids["table1_entry10"]] + [ids[f"table2_entry{i:02d}"] for i in range(1, 12)] + [ids[f"scheme4_{p}"] for p in ("5ha", "5ia", "5ja")] + [ids[f"scheme5_{p}"] for p in ("5ad", "5bd", "5cd")] + [ids["scheme6_mechanism"]]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction columns", "finding": "Article overview and prior-work discussion; no discrete current-paper experiment is reported in this region.", "evidence_ids": ev(1)},
                {"region": "Scheme 1 at page bottom", "finding": "Generic summary of the authors' previous work, classified as a literature example rather than a current reported experiment.", "evidence_ids": ev(1)},
            ],
            "record_ids": [ids["scheme1_prior_work"]],
            "unresolved": ["Scheme 1 uses generic R groups and gives no individual conditions or yields."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 2", "finding": "Generic proposed transformation with unspecified base and solvent; recorded as a general scheme.", "evidence_ids": ev(2)},
                {"region": "middle-left Scheme 3 solvent table", "finding": "Three distinct solvent-screen experiments under 10 mol% K2CO3 for 11.5 h; acetone footnote reports 30% recovered 1a.", "evidence_ids": ev(2)},
                {"region": "bottom Table 1 and footnotes", "finding": "Ten distinct base-screen experiments, including three no-reaction rows, two low-yield rows with recovered-starting-material footnotes, and the 10 mol% t-BuOK exception.", "evidence_ids": ev(2)},
                {"region": "right-column discussion", "finding": "Narrative confirms Table 1 outcomes and introduces the Table 2 substrate scope; duplicate statements were merged with their table rows.", "evidence_ids": ev(2)},
            ],
            "record_ids": page2_ids,
            "unresolved": ["Scheme 3 and most Table 1 rows do not state reactant/solvent quantities, workup, purification, atmosphere, or yield basis."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top Table 2", "finding": "Eleven substrate-scope rows extracted separately; entry 6 is trace and entry 7 uses the 100 mol% t-BuOK footnote.", "evidence_ids": ev(3)},
                {"region": "lower-left Scheme 4", "finding": "Three gamma-substituted allene scope rows yielding E-5ha, E-5ia, and E-5ja as sole reported products.", "evidence_ids": ev(3)},
                {"region": "Figure 1", "finding": "NOE characterization evidence for E-5ja; linked to the Scheme 4 record and not counted as a new reaction.", "evidence_ids": ev(3)},
                {"region": "middle-right Scheme 5", "finding": "Three malononitrile scope rows extracted separately; printed header/product numbering mismatch retained in notes.", "evidence_ids": ev(3)},
                {"region": "right-column failed-substrate prose", "finding": "Three alternative active-methylene compounds reported to give complicated reactions; recorded separately with unidentified allene partner and no invented products.", "evidence_ids": ev(3)},
                {"region": "lower-right Scheme 6", "finding": "Proposed catalytic mechanism, classified as mechanism and not as an experiment.", "evidence_ids": ev(3)},
            ],
            "record_ids": page3_ids,
            "unresolved": [
                "The failed-substrate sentence does not identify the allenic-ketone partner or exact conditions.",
                "Table 2's printed 1g substituent assignment conflicts with section 2.1.11 mass/product implications.",
                "Scheme 5's header says 'yield of 7 (%)' while products are labeled 5ad/5bd/5cd.",
            ],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left mechanism summary", "finding": "Textual explanation of Scheme 6; merged into the mechanism record rather than counted again.", "evidence_ids": ev(4)},
                {"region": "section 2.1 general procedure", "finding": "General reaction scale/range, 10 mol% t-BuOK, 2 mL acetone, room temperature, usual 10 min duration, evaporation, and silica chromatography conditions for the 5-series.", "evidence_ids": ev(4)},
                {"region": "sections 2.1.1-2.1.3", "finding": "Detailed 5aa, 5ab, and 5ac experiments; merged into Table 1 entry 10 and Table 2 entries 1-2.", "evidence_ids": ev(4)},
            ],
            "record_ids": page4_ids,
            "unresolved": ["The general procedure says reactions usually complete within 10 min; exact individual completion time is taken from the matching page-2/page-3 table where explicitly printed.", "Atmosphere is not reported."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "sections 2.1.4-2.1.8", "finding": "Detailed experiments for 5ba, 5bb, 5bc, 5ca, and 5da; merged with Table 2 entries 3, 4, 5, 7, and 8.", "evidence_ids": ev(5)},
                {"region": "section 2.1.9 heading", "finding": "5ea section heading only; its procedure continues on page 6 and is assigned there.", "evidence_ids": ev(5)},
            ],
            "record_ids": [ids[f"table2_entry{i:02d}"] for i in (3, 4, 5, 7, 8)],
            "unresolved": ["The printed 5ba mass/yield combination (309 mg, 83%) is preserved without arithmetic correction despite appearing inconsistent with the printed molecular formula."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "sections 2.1.9-2.1.11", "finding": "Detailed experiments for 5ea, 5fa, and 5ga; merged with Table 2 entries 9-11.", "evidence_ids": ev(6)},
                {"region": "sections 2.1.12-2.1.14", "finding": "Detailed experiments for E-5ha, E-5ia, and E-5ja; merged with the three Scheme 4 rows.", "evidence_ids": ev(6)},
            ],
            "record_ids": [ids[f"table2_entry{i:02d}"] for i in (9, 10, 11)] + [ids[f"scheme4_{p}"] for p in ("5ha", "5ia", "5ja")],
            "unresolved": ["The 1g structure conflict is retained; its candidate SMILES is null.", "Atmosphere is not reported."],
        },
    ],
}


raw_path = RUN / "raw_model" / "extracted_records_pages_0001_0006.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(RUN / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only the six user-scoped page tasks attempted.  Later pages remain pending.
tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page", 1)[1].split(":", 1)[0])
    if 1 <= page <= 6:
        task["state"] = "attempted"
        task["reason"] = "Page image and page text inspected; see coverage/pages_0001_0006.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]], "raw": str(raw_path)}, ensure_ascii=False))
