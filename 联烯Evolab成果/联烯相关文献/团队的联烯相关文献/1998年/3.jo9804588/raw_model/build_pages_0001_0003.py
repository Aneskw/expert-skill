#!/usr/bin/env python3
"""Build evidence-linked machine records for jo9804588 PDF pages 1-3."""

import json
from pathlib import Path


DOC = "doc_0f989d475a702a7c"
P1I = f"{DOC}:page1:image"
P1T = f"{DOC}:page1:text"
P2I = f"{DOC}:page2:image"
P2T = f"{DOC}:page2:text"
P3I = f"{DOC}:page3:image"
P3T = f"{DOC}:page3:text"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def record(suffix, source_id, kind, evidence_ids, participants, steps, outcomes,
           notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence_ids)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(v, ev) for v, ev in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def table1_record(entry, ph_i_eq, base, base_eq, solvent, additive, additive_eq,
                  temp_c, time_h, yield_value, isolated=False, pd_loading=10,
                  extra_evidence=()):
    ev = (P2I, P2T) + tuple(extra_evidence)
    pev = (P2I,)
    people = [
        participant("acid_4a", "reactant", "4a", "2,3-heptadienoic acid", pev),
        participant("phenyl_iodide", "reactant", "PhI", "phenyl iodide", pev,
                    (("equivalents", {"number": ph_i_eq, "unit": "equiv"}),)),
        participant("base", "reagent", base, base, pev,
                    (("equivalents", {"number": base_eq, "unit": "equiv"}),)),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", pev,
                    (("catalyst_loading_as_printed", f"{pd_loading}%"),)),
        participant("solvent", "solvent", solvent, solvent, pev),
        participant("product_5a", "product", "5a", "4-phenyl-5-(n-butyl)-2(5H)-furanone", pev),
    ]
    if additive:
        role = "catalyst" if entry == 12 and additive == "Ag2CO3" else "reagent"
        people.insert(-1, participant("additive", role, additive, additive, pev,
                                     (("equivalents", {"number": additive_eq, "unit": "equiv"}),)))
    conditions = [
        field("temperature", {"number": temp_c, "unit": "°C"}, pev),
        field("time", {"number": time_h, "unit": "h"}, pev),
        field("atmosphere", None),
    ]
    outcomes = [
        field("yield", yield_value, pev),
        field("yield_measurement_basis", "isolated yield" if isolated else "1H NMR yield using CH2Br2 as internal standard", pev),
    ]
    p1_rows = {
        1: "The expected product 5a was not observed under the tested condition.",
        4: "K2CO3/EtOH gave 5a in low yield.",
        7: "Ag2CO3 as base gave 5a with only 1.2 equivalents of PhI.",
    }
    notes = []
    if entry in p1_rows:
        notes.append((p1_rows[entry], (P1I, P1T)))
    unresolved = [
        "No supporting-information file was supplied; the main article alone does not establish omitted experimental details.",
        "Participant structures are retained as source names/labels with null SMILES and remain unverified.",
    ]
    if entry != 12:
        unresolved += [
            "Atmosphere, substrate charge, reaction concentration, workup, and purification are not reported for this optimization row.",
        ]
    return record(
        f"table1_entry{entry:02d}", f"Table 1 entry {entry}", "optimization_entry", ev,
        people, [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in people], "conditions": conditions}],
        outcomes, notes, unresolved,
    )


records = []

# Table 1: distinct conditions remain distinct experiments.
table1_rows = [
    (1, 5, "K2CO3", 5, "DMF", None, None, 80, 7, {"number": 0, "unit": "%"}, False, 10, (P1I, P1T)),
    (2, 5, "K2CO3", 5, "DMF", "n-Bu4NCl", 0.1, 80, 16, {"number": 0, "unit": "%"}, False, 10, ()),
    (3, 5, "Et3N", 3, "CH3CN", None, None, 80, 16, {"number": 0, "unit": "%"}, False, 10, ()),
    (4, 5, "K2CO3", 5, "DMF", "EtOH", 10, 80, 16, {"number": 15, "unit": "%"}, True, 10, (P1I, P1T)),
    (5, 2, "K2CO3", 4, "CH3CN", None, None, 70, 7, {"number": 29, "unit": "%"}, False, 10, ()),
    (6, 5, "K2CO3", 4, "CH3CN", "EtOH", 10, 80, 7, {"number": 49, "unit": "%"}, False, 10, ()),
    (7, 1.2, "Ag2CO3", 1, "CH3CN", None, None, 70, 7, {"number": 53, "unit": "%"}, False, 10, (P1I, P1T)),
    (8, 1.2, "K2CO3", 4, "CH3CN", "Ag2CO3", 1, 70, 7, {"number": 65, "unit": "%"}, True, 10, ()),
    (9, 1.2, "K2CO3", 4, "CH3CN", "Ag2CO3", 0.1, 70, 7, {"number": 73, "unit": "%"}, True, 10, ()),
    (10, 1.2, "K2CO3", 4, "CH3CN", "Ag2CO3", 0.1, 70, 7, {"number": 47, "unit": "%"}, False, 2.5, ()),
    (11, 1.2, "K2CO3", 4, "CH3CN", "Ag2CO3", 0.1, 40, 7, {"number": 33, "unit": "%"}, False, 10, ()),
    (12, 1.2, "K2CO3", 4, "CH3CN", "Ag2CO3", 0.05, 70, 7, {"number": 79, "unit": "%"}, True, 5, (P3I, P3T)),
    (13, 1.2, "K2CO3", 4, "CH3CN", "HgCl2", 0.05, 70, 7, "<5%", False, 10, ()),
    (14, 1.2, "K2CO3", 4, "CH3CN", "Hg(OAc)2", 0.05, 70, 7, "<5%", False, 10, ()),
]
for row in table1_rows:
    records.append(table1_record(*row))

# Enrich the merged Table 1 entry 12 / Table 2 entry 1 / typical preparation of 5a.
merged = records[11]
merged["source_reaction_id"] = "Table 1 entry 12; Table 2 entry 1; typical preparation of 5a"
merged["evidence_ids"] = [P1I, P1T, P2I, P2T, P3I, P3T]
merged["participants"] = [
    participant("acid_4a", "reactant", "4a", "2,3-heptadienoic acid", (P3I, P3T),
                (("mass", {"number": 140, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"}), ("equivalents", {"number": 1, "unit": "equiv"}))),
    participant("phenyl_iodide", "reactant", "PhI", "phenyl iodide", (P2I, P3I, P3T),
                (("mass", {"number": 245, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"}), ("equivalents", {"number": 1.2, "unit": "equiv"}))),
    participant("potassium_carbonate", "reagent", "K2CO3", "potassium carbonate", (P2I, P3I, P3T),
                (("mass", {"number": 553, "unit": "mg"}), ("amount", {"number": 4.0, "unit": "mmol"}), ("equivalents", {"number": 4, "unit": "equiv"}))),
    participant("silver_carbonate", "catalyst", "Ag2CO3", "silver carbonate", (P2I, P3I, P3T),
                (("mass", {"number": 14, "unit": "mg"}), ("amount", {"number": 0.05, "unit": "mmol"}), ("equivalents", {"number": 0.05, "unit": "equiv"}))),
    participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", (P2I, P3I, P3T),
                (("mass", {"number": 58, "unit": "mg"}), ("amount", {"number": 0.05, "unit": "mmol"}), ("equivalents", {"number": 0.05, "unit": "equiv"}), ("catalyst_loading_as_printed", "5%"))),
    participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", (P2I, P3I, P3T),
                (("volume", {"number": 3, "unit": "mL"}),)),
    participant("product_5a", "product", "5a", "4-phenyl-5-(n-butyl)-2(5H)-furanone", (P2I, P3I, P3T),
                (("isolated_mass", {"number": 170, "unit": "mg"}),)),
]
merged["steps"] = [
    {
        "step_id": "reaction",
        "participant_ids": [p["entity_id"] for p in merged["participants"][:-1]],
        "conditions": [
            field("addition", "Pd(PPh3)4 was added to the other components in CH3CN", (P3I, P3T)),
            field("atmosphere", "Ar", (P3I, P3T)),
            field("temperature", {"number": 70, "unit": "°C"}, (P2I, P3I, P3T)),
            field("time", {"number": 7, "unit": "h"}, (P2I, P3I, P3T)),
            field("monitoring", "TLC", (P3I, P3T)),
        ],
    },
    {
        "step_id": "workup",
        "participant_ids": ["product_5a"],
        "conditions": [
            field("filtration", "filtered through a short column of silica gel", (P3I, P3T)),
            field("solvent_removal", "solvent evaporated", (P3I, P3T)),
        ],
    },
    {
        "step_id": "purification",
        "participant_ids": ["product_5a"],
        "conditions": [
            field("method", "flash chromatography on silica gel", (P3I, P3T)),
            field("eluent", "petroleum ether:ethyl acetate = 10:1", (P3I, P3T)),
        ],
    },
]
merged["outcomes"] = [
    field("yield", {"number": 79, "unit": "%"}, (P2I, P3I, P3T)),
    field("yield_measurement_basis", "isolated yield", (P2I, P3I, P3T)),
    field("physical_state", "liquid", (P3I, P3T)),
]
merged["notes"] = [
    fact("This record merges the same 5a experiment shown as Table 1 entry 12, Table 2 entry 1, and the detailed typical procedure.", (P2I, P3I, P3T)),
]
merged["review"]["unresolved"] = [
    "No supporting-information file was supplied; the cited spectra for 5a are unavailable in this pilot.",
    "Reaction concentration and isolated-product purity are not explicitly reported.",
    "Structures remain source-labelled with null SMILES and are unverified.",
]


scope_rows = [
    # entry, acid label/name, halide label/name, product label/name, yield, physical state, melting point, halide equiv
    (2, "4a", "2,3-heptadienoic acid", "p-MeC6H4I", "p-methylphenyl iodide", "5b", "4-(4'-methylphenyl)-5-(n-butyl)-2(5H)-furanone", 73, "liquid", None, 1.2),
    (3, "4a", "2,3-heptadienoic acid", "p-NO2C6H4Br", "p-nitrophenyl bromide", "5c", "4-(4'-nitrophenyl)-5-(n-butyl)-2(5H)-furanone", 64, "solid", "111-112 °C (n-hexane)", 1.5),
    (4, "4a", "2,3-heptadienoic acid", "1-bromonaphthalene", "1-bromonaphthalene", None, None, 0, None, None, 1.2),
    (5, "4a", "2,3-heptadienoic acid", "1-iodonaphthalene", "1-iodonaphthalene", "5d", "4-(1'-naphthyl)-5-(n-butyl)-2(5H)-furanone", 69, "liquid", None, 1.2),
    (6, "4b", "2,3-undecadienoic acid", "PhI", "phenyl iodide", "5e", "4-phenyl-5-(n-heptyl)-2(5H)-furanone", 77, "liquid", None, 1.2),
    (7, "4b", "2,3-undecadienoic acid", "p-NO2C6H4Br", "p-nitrophenyl bromide", "5f", "4-(4'-nitrophenyl)-5-(n-heptyl)-2(5H)-furanone", 63, "solid", "144-146 °C (n-hexane)", 1.5),
    (8, "4b", "2,3-undecadienoic acid", "1-iodonaphthalene", "1-iodonaphthalene", "5g", "4-(1'-naphthyl)-5-(n-heptyl)-2(5H)-furanone", 72, "liquid", None, 1.2),
    (9, "4a", "2,3-heptadienoic acid", "methyl (Z)-3-iodo-2-propenoate", "methyl (Z)-3-iodo-2-propenoate", "5h", "(Z)-4-(2'-methoxycarbonylvinyl)-5-(n-butyl)-2(5H)-furanone", 59, "liquid", None, 1.2),
]

for entry, acid_label, acid_name, halide_label, halide_name, product_label, product_name, yld, state, mp, halide_eq in scope_rows:
    ev = (P2I, P2T) if entry == 4 else (P2I, P2T, P3I, P3T)
    people = [
        participant("allenic_acid", "reactant", acid_label, acid_name, (P2I,),
                    (("equivalents", {"number": 1, "unit": "equiv"}),)),
        participant("organic_halide", "reactant", halide_label, halide_name, (P2I,),
                    (("equivalents", {"number": halide_eq, "unit": "equiv"}),)),
        participant("potassium_carbonate", "reagent", "K2CO3", "potassium carbonate", (P2I,),
                    (("equivalents", {"number": 4, "unit": "equiv"}),)),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", (P2I,),
                    (("equivalents", {"number": 0.05, "unit": "equiv"}),)),
        participant("silver_carbonate", "catalyst", "Ag2CO3", "silver carbonate", (P2I,),
                    (("equivalents", {"number": 0.05, "unit": "equiv"}),)),
        participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", (P2I,)),
    ]
    if product_label:
        people.append(participant("product", "product", product_label, product_name, (P2I, P3I, P3T)))
    outcomes = [
        field("yield", {"number": yld, "unit": "%"}, (P2I,)),
        field("yield_measurement_basis", "isolated yield", (P2I,)),
    ]
    if state:
        outcomes.append(field("physical_state", state, (P3I, P3T)))
    if mp:
        outcomes.append(field("melting_point", mp, (P3I, P3T)))
    notes = []
    if entry == 4:
        notes.append(("1-Bromonaphthalene was inert and did not afford 5d.", (P2I, P2T)))
    if entry == 9:
        outcomes.append(field("stereochemical_observation", "The alkene configuration remained intact; J = 12.6 Hz and a strong NOE was reported between the COOMe-connected olefinic protons.", (P2I, P2T, P3I, P3T)))
    unresolved = [
        "The article states that these compounds were prepared similarly, but row-specific charges, atmosphere, workup, and purification are not supplied.",
        "No supporting-information file was supplied; cited spectra are unavailable in this pilot.",
        "Structures remain source-labelled with null SMILES and are unverified.",
    ]
    records.append(record(
        f"table2_entry{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry", ev, people,
        [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in people],
            "conditions": [
                field("temperature", {"number": 70, "unit": "°C"}, (P2I,)),
                field("time", {"number": 7, "unit": "h"}, (P2I,)),
                field("atmosphere", None),
            ],
        }], outcomes, notes, unresolved,
    ))


mechanisms = [
    (
        "scheme1_mechanistic_rationale", "Scheme 1", (P1I, P1T),
        [
            participant("organic_halide_3", "reactant", "3", "R2X", (P1I,)),
            participant("pd0", "catalyst", "Pd(0)", "palladium(0)", (P1I,)),
            participant("carbopalladium_2", "unspecified_agent", "2", "R2PdX", (P1I,)),
            participant("allenic_acid", "reactant", "1,2-allenic carboxylic acid", "generic 1,2-allenic carboxylic acid", (P1I,)),
            participant("pi_allyl_pd_1", "unspecified_agent", "1", "pi-allyl palladium intermediate", (P1I, P1T)),
            participant("butenolide", "product", "butenolide", "generic substituted butenolide", (P1I,)),
        ],
        "Proposed sequence: oxidative addition gives R2PdX (2), allene insertion gives pi-allyl palladium intermediate 1, and oxygen-centred intramolecular nucleophilic substitution gives a butenolide.",
    ),
    (
        "scheme2_pd_cycle", "Scheme 2", (P2I, P2T),
        [
            participant("organic_halide", "reactant", "R2X", "generic organic halide", (P2I,)),
            participant("allenic_carboxylate", "reactant", "1,2-allenic carboxylate", "generic 1,2-allenic carboxylate", (P2I,)),
            participant("pd0", "catalyst", "Pd(0)", "palladium(0)", (P2I,)),
            participant("butenolide", "product", "butenolide", "generic substituted butenolide", (P2I,)),
        ],
        "Proposed Pd cycle: oxidative addition, intermolecular carbopalladation of the allene, and intramolecular allylic substitution regenerate Pd(0) and form the butenolide.",
    ),
    (
        "scheme3_ag_pd_cycle", "Scheme 3", (P3I, P3T),
        [
            participant("organic_halide", "reactant", "R2X", "generic organic halide", (P3I,)),
            participant("allenic_acid", "reactant", "1,2-allenic carboxylic acid", "generic 1,2-allenic carboxylic acid", (P3I,)),
            participant("pd0", "catalyst", "Pd(0)", "palladium(0)", (P3I,)),
            participant("ag_plus", "catalyst", "Ag+", "silver(I)", (P3I,)),
            participant("silver_butenolide", "unspecified_agent", "3-silver-2-butenolide", "generic 3-silver-2-butenolide intermediate", (P3I, P2T)),
            participant("butenolide", "product", "butenolide", "generic substituted butenolide", (P3I,)),
        ],
        "Alternative proposed cycle: Ag+ mediates cyclization to a 3-silver-2-butenolide; transmetalation with R2PdX and reductive elimination form product while Pd(0) and Ag+ are regenerated.",
    ),
]

for suffix, source_id, ev, people, description in mechanisms:
    records.append(record(
        suffix, source_id, "mechanism", ev, people,
        [{"step_id": "proposed_cycle", "participant_ids": [p["entity_id"] for p in people],
          "conditions": [field("mechanistic_description", description, ev)]}],
        [],
        (("This is a proposed mechanism, not an independently reported experimental run.", ev),),
        (
            "Generic R groups and intermediates are not complete molecular structures; SMILES are intentionally null.",
            "The proposed intermediates were not reported as isolated or directly observed in the supplied pages.",
        ),
    ))


out = Path(__file__).with_name("records_pages_0001_0003.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(out)}, ensure_ascii=False))
