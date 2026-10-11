#!/usr/bin/env python3
"""Build evidence-linked records for ol0055871, original PDF pages 1-4."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "runs" / "current"
DOC = "doc_a27377d6512eaf44"


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence):
    return {"name": name, "fact": fact(value, evidence)}


def part(entity_id, role, label, name, evidence, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(k, v, evidence) for k, v in amounts],
    }


def record(rid, kind, page, participants=(), conditions=(), outcomes=(), notes=(), unresolved=()):
    evidence = ev(page)
    participants = list(participants)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": ([{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": [fld(k, v, evidence) for k, v in conditions],
        }] if participants or conditions else []),
        "outcomes": [fld(k, v, evidence) for k, v in outcomes],
        "notes": [fact(v, evidence) for v in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved),
        },
    }


def common_missing():
    return [
        ("atmosphere", None),
        ("concentration", None),
        ("workup", None),
        ("purification", None),
    ]


records = []

# Page 1: current-paper graphical abstract and explicitly cited prior method.
e = ev(1)
records.append(record(
    "graphical_abstract_general_scheme", "general_scheme", 1,
    participants=[
        part("ga_allenyl_ketone", "reactant", "generic 1,2-allenyl ketone", "differently substituted 1,2-allenyl ketone", e),
        part("ga_allylic_bromide", "reactant", "generic allylic bromide", "allylic bromide", e),
        part("ga_product", "product", "generic 3-allylic polysubstituted furan", "3-allylic polysubstituted furan", e),
        part("ga_pd", "catalyst", "PdCl2(PhCN)2", "bis(benzonitrile)palladium(II) dichloride", e, [("loading", {"number": 5, "unit": "mol%"})]),
        part("ga_base", "reagent", "K2CO3", "potassium carbonate", e),
        part("ga_solvent", "solvent", "CH3CN", "acetonitrile", e),
    ],
    conditions=[("temperature", {"number": 25, "unit": "°C"}), ("time", None)] + common_missing(),
    outcomes=[("yield", None)],
    notes=["Graphical abstract/current-paper generic transformation; it is not an individual experimental run."],
    unresolved=["Generic R-group structures are not fully specified.", "Reaction time, scale, yield, workup, and purification are not reported in the graphical abstract."],
))
records.append(record(
    "scheme1_prior_work_generic", "literature_example", 1,
    participants=[
        part("s1_organic_halide", "reactant", "R3X", "generic organic halide or 3-iodo-2-propenoate", e),
        part("s1_allenyl_ketone", "reactant", "generic 1,2-allenyl ketone", "1,2-allenyl ketone", e),
        part("s1_product", "product", "generic polysubstituted furan", "polysubstituted furan", e),
        part("s1_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e, [("loading", {"number": 5, "unit": "mol%"})]),
        part("s1_base", "reagent", "Et3N", "triethylamine", e),
        part("s1_ag", "reagent", "Ag2CO3", "silver carbonate", e, [("loading", {"number": 10, "unit": "mol%"})]),
        part("s1_solvent", "solvent", "PhMe", "toluene", e),
    ],
    conditions=[("temperature", None), ("time", None)] + common_missing(),
    outcomes=[("yield", None)],
    notes=["Scheme 1 is described in the prose as the authors' recently demonstrated method and cites reference 8; it is prior work, not a current-paper experiment."],
    unresolved=["Generic R-group structures, scale, temperature, time, yield, workup, and purification are not reported on this page."],
))


# Page 2: Table 1, one record per optimization row.
table1 = [
    (1, "3a", "1/3", "Pd(OAc)2", False, 24, "Et3N", 13, "38/62", "1a", False),
    (2, "3a", "1/3", "Pd(OAc)2", True, 24, "K2CO3", 37, "89/11", "1a", False),
    (3, "3b", "1.5/1", "Pd(PPh3)4", True, 18, "Et3N", 40, "5/95", "3b", True),
    (4, "3b", "1.5/1", "Pd(OAc)2", True, 29, "K2CO3", 81, "96/4", "3b", False),
    (5, "3b", "1/1.2", "Pd(OAc)2", True, 20, "K2CO3", 62, "92/8", "1a", False),
    (6, "3b", "1/2", "PdCl2", True, 21, "K2CO3", 45, "98/2", "1a", False),
    (7, "3b", "1/2", "PdCl2(CH3CN)2", True, 20, "K2CO3", 62, "99/1", "1a", False),
    (8, "3b", "1/2", "PdCl2(PhCN)2", True, 17, "K2CO3", 71, "99/1", "1a", False),
    (9, "3b", "1/2", "PdCl2(CH3CN)2", False, 20, "K2CO3", 61, "99/1", "1a", False),
    (10, "3b", "1/2", "PdCl2(PhCN)2", False, 21, "K2CO3", 72, "99/1", "1a", False),
    (11, "3a", "1/3", "Pd(OAc)2", False, 24, "K2CO3", 46, "84/16", "1a", False),
    (12, "3b", "1/2", "PdCl2(PhCN)2", False, 21, None, 18, "96/4", "1a", False),
    (13, "3a", "1/3", "Pd(OAc)2", False, 21, None, 10, "82/18", "1a", False),
]
cat_names = {
    "Pd(OAc)2": "palladium(II) acetate",
    "Pd(PPh3)4": "tetrakis(triphenylphosphine)palladium(0)",
    "PdCl2": "palladium(II) chloride",
    "PdCl2(CH3CN)2": "bis(acetonitrile)palladium(II) dichloride",
    "PdCl2(PhCN)2": "bis(benzonitrile)palladium(II) dichloride",
}
for entry, halide, ratio, catalyst, has_ag, time_h, base, yld, product_ratio, yield_basis, special in table1:
    e = ev(2)
    p = [
        part(f"t1e{entry}_1a", "reactant", "1a", "3-butyl-3,4-pentadien-2-one", e, [("amount", {"number": 1.5 if special else 1, "unit": "mmol"})]),
        part(f"t1e{entry}_{halide}", "reactant", halide, "allyl chloride" if halide == "3a" else "allyl bromide", e,
             [("amount", {"number": 1, "unit": "mmol"})] if special else []),
        part(f"t1e{entry}_4a", "product", "4a", "cyclization-coupling product 4a", e),
        part(f"t1e{entry}_5a", "product", "5a", "cycloisomerization product 5a", e),
        part(f"t1e{entry}_pd", "catalyst", catalyst, cat_names[catalyst], e, [("loading", {"number": 5, "unit": "mol%"})]),
    ]
    if has_ag:
        p.append(part(f"t1e{entry}_ag", "reagent", "Ag2CO3", "silver carbonate", e,
                      [("loading", {"number": 10, "unit": "mol%"})] if special else [("loading", None)]))
    if base:
        p.append(part(f"t1e{entry}_base", "reagent", base, "triethylamine" if base == "Et3N" else "potassium carbonate", e,
                      [("amount", {"number": 2 if special else 1, "unit": "mmol"})]))
    p.append(part(f"t1e{entry}_solvent", "solvent", "toluene" if special else "MeCN", "toluene" if special else "acetonitrile", e,
                  [("volume", {"number": 4 if special else 2, "unit": "mL"})]))
    conditions = [
        ("molar_ratio_1a_to_3", ratio),
        ("temperature", {"number": 100, "unit": "°C"} if special else "room temperature; reaction drawing prints 25 °C"),
        ("time", {"number": time_h, "unit": "h"}),
        ("base", base if base else "none"),
    ] + common_missing()
    records.append(record(
        f"table1_entry{entry:02d}", "optimization_entry", 2,
        participants=p,
        conditions=conditions,
        outcomes=[
            ("combined_yield_4a_plus_5a", {"number": yld, "unit": "%"}),
            ("yield_measurement_basis", f"isolated yield based on {yield_basis}"),
            ("ratio_4a_to_5a", product_ratio),
            ("ratio_measurement_method", "1H NMR analysis"),
        ],
        notes=["Table 1 optimization row."],
        unresolved=[
            "Product structures were read from the reaction drawing but are not independently structure-verified.",
            "Atmosphere, concentration, workup, purification, and isolated masses are not reported in the main-text table.",
        ] + (["The amount/loading of Ag2CO3 is not reported for this row."] if has_ag and not special else []),
    ))


# Page 3: proposed Pd(II) pathway (Scheme 2).
e = ev(3)
records.append(record(
    "scheme2_proposed_pdii_pathway", "mechanism", 3,
    participants=[
        part("s2_substrate1", "reactant", "generic 1", "generic 1,2-allenyl ketone 1", e),
        part("s2_allyl_br", "reactant", "allyl bromide", "allyl bromide", e),
        part("s2_intermediate2", "unspecified_agent", "furanyl palladium species 2", "proposed furanyl palladium intermediate 2", e),
        part("s2_product", "product", "generic 3-allylic furan", "generic 3-allylic polysubstituted furan", e),
        part("s2_pdii", "catalyst", "Pd(II)", "palladium(II) catalyst", e),
        part("s2_base", "reagent", "Base", "unspecified base", e),
    ],
    conditions=[], outcomes=[],
    notes=["Scheme 2 is a proposed Pd(II)-based pathway through furanyl palladium species 2; it is not an observed standalone experiment."],
    unresolved=["The exact identities and structures of the generic substituents and organopalladium intermediate are not established as observed species."],
))


# Page 3: Table 2 substrate scope.
table2 = [
    (1, "n-Bu", "1a", "H", "Ph", "3c", 19, 78, "4b"),
    (2, "n-Bu", "1a", "Ph", "H", "3d", 23, 53, "4c"),
    (3, "Me", "1b", "H", "H", "3b", 19, 62, "4d"),
    (4, "Me", "1b", "Ph", "H", "3d", 20, 50, "4e"),
    (5, "Me", "1b", "H", "Ph", "3c", 20, 52, "4f"),
    (6, "allyl", "1c", "H", "H", "3b", 21, 52, "4g"),
    (7, "allyl", "1c", "Ph", "H", "3d", 22, 53, "4h"),
    (8, "allyl", "1c", "H", "Ph", "3c", 22, 70, "4i"),
]
substrate_names = {
    "1a": "3-butyl-3,4-pentadien-2-one",
    "1b": "1b (R = Me)",
    "1c": "3-allyl-3,4-pentadien-2-one",
}
halide_names = {
    "3b": "allyl bromide",
    "3c": "allylic bromide 3c (R1 = H, R2 = Ph)",
    "3d": "3-phenyl-2-propenyl bromide 3d (R1 = Ph, R2 = H)",
}
for entry, r, substrate, r1, r2, halide, time_h, yld, product in table2:
    e = ev(3)
    notes = [f"Table 2 row; allenyl-ketone substituent R = {r}; allylic-bromide substituents R1 = {r1}, R2 = {r2}."]
    if halide == "3d":
        notes.append("The prose states that coupling of 3d occurs exclusively at the nonsubstituted terminus and that its C=C configuration remains intact.")
    records.append(record(
        f"table2_entry{entry:02d}", "substrate_scope_entry", 3,
        participants=[
            part(f"t2e{entry}_{substrate}", "reactant", substrate, substrate_names[substrate], e, [("amount", {"number": 1.5, "unit": "mmol"})]),
            part(f"t2e{entry}_{halide}", "reactant", halide, halide_names[halide], e, [("amount", {"number": 1, "unit": "mmol"})]),
            part(f"t2e{entry}_{product}", "product", product, f"furan product {product}", e),
            part(f"t2e{entry}_pd", "catalyst", "PdCl2(PhCN)2", "bis(benzonitrile)palladium(II) dichloride", e, [("loading", {"number": 5, "unit": "mol%"})]),
            part(f"t2e{entry}_base", "reagent", "K2CO3", "potassium carbonate", e, [("amount", {"number": 1, "unit": "mmol"})]),
            part(f"t2e{entry}_solvent", "solvent", "MeCN", "acetonitrile", e, [("volume", {"number": 2, "unit": "mL"})]),
        ],
        conditions=[
            ("temperature", "room temperature; reaction drawing prints 25 °C"),
            ("time", {"number": time_h, "unit": "h"}),
        ] + common_missing(),
        outcomes=[
            ("isolated_yield", {"number": yld, "unit": "%"}),
            ("yield_basis", "isolated yield based on allylic bromide 3"),
        ],
        notes=notes,
        unresolved=["Exact structures and stereochemical descriptors are not independently structure-verified.", "Atmosphere, concentration, workup, purification, and isolated mass are not reported in the main-text table."],
    ))


# Page 3: Scheme 3 catalyst comparison (three distinct runs).
scheme3 = [
    (1, "Pd(PPh3)4", None, 0),
    (2, "PdCl2(PhCN)2", "PPh3", 0),
    (3, "Pd2(dba)3·CHCl3", None, 79),
]
scheme3_names = {
    "Pd(PPh3)4": "tetrakis(triphenylphosphine)palladium(0)",
    "PdCl2(PhCN)2": "bis(benzonitrile)palladium(II) dichloride",
    "Pd2(dba)3·CHCl3": "tris(dibenzylideneacetone)dipalladium chloroform adduct",
}
for entry, catalyst, ligand, yld in scheme3:
    e = ev(3)
    p = [
        part(f"s3e{entry}_1a", "reactant", "1a", "3-butyl-3,4-pentadien-2-one", e),
        part(f"s3e{entry}_3d", "reactant", "3d", "3-phenyl-2-propenyl bromide", e),
        part(f"s3e{entry}_4c", "product", "4c", "furan 4c", e),
        part(f"s3e{entry}_pd", "catalyst", catalyst, scheme3_names[catalyst], e, [("loading", {"number": 5, "unit": "mol%"})]),
        part(f"s3e{entry}_base", "reagent", "K2CO3", "potassium carbonate", e, [("amount", {"number": 1, "unit": "equiv"})]),
        part(f"s3e{entry}_solvent", "solvent", "CH3CN", "acetonitrile", e),
    ]
    if ligand:
        p.append(part(f"s3e{entry}_ligand", "reagent", ligand, "triphenylphosphine", e, [("loading", {"number": 20, "unit": "mol%"})]))
    records.append(record(
        f"scheme3_catalyst_row{entry}", "optimization_entry", 3,
        participants=p,
        conditions=[
            ("molar_ratio_1a_to_3d", "1.5/1"),
            ("temperature", {"number": 25, "unit": "°C"}),
            ("time", None),
        ] + common_missing(),
        outcomes=[("yield_of_4c", {"number": yld, "unit": "%"}), ("yield_measurement_basis", None)],
        notes=["Scheme 3 catalyst comparison row."],
        unresolved=["Reaction time, scale, solvent volume, atmosphere, concentration, workup, purification, isolated mass, and yield measurement basis are not reported."],
    ))


# Page 3: Table 3 solvent/ratio optimization.
table3 = [
    (1, "1/6", "CH3CN", 15, 58, "75/25"),
    (2, "1/6", "DMF", 15, 67, "81/19"),
    (3, "1/6", "toluene", 16, 66, "28/72"),
    (4, "1/6", "THF", 16, 58, "44/56"),
    (5, "1/10", "DMA", 22, 57, "90/10"),
    (6, "1/20", None, 22, 76, "51/49"),
    (7, "1/10", "DMF", 22, 65, "92/8"),
]
solvent_names = {
    "CH3CN": "acetonitrile", "DMF": "N,N-dimethylformamide", "toluene": "toluene",
    "THF": "tetrahydrofuran", "DMA": "N,N-dimethylacetamide",
}
for entry, ratio, solvent, time_h, yld, product_ratio in table3:
    e = ev(3)
    p = [
        part(f"t3e{entry}_1d", "reactant", "1d", "3,4-dodecadien-2-one", e, [("amount", {"number": 1, "unit": "mmol"})]),
        part(f"t3e{entry}_3b", "reactant", "3b", "allyl bromide", e),
        part(f"t3e{entry}_8", "product", "8", "allylated furan 8 (R = allyl)", e),
        part(f"t3e{entry}_9", "product", "9", "cycloisomerized furan 9 (R = H)", e),
        part(f"t3e{entry}_pd", "catalyst", "PdCl2(PhCN)2", "bis(benzonitrile)palladium(II) dichloride", e, [("loading", {"number": 5, "unit": "mol%"})]),
        part(f"t3e{entry}_base", "reagent", "K2CO3", "potassium carbonate", e, [("amount", {"number": 1, "unit": "mmol"})]),
    ]
    if solvent:
        p.append(part(f"t3e{entry}_solvent", "solvent", solvent, solvent_names[solvent], e, [("volume", {"number": 2, "unit": "mL"})]))
    records.append(record(
        f"table3_entry{entry:02d}", "optimization_entry", 3,
        participants=p,
        conditions=[
            ("molar_ratio_1d_to_3b", ratio),
            ("solvent", solvent),
            ("solvent_volume", {"number": 2, "unit": "mL"}),
            ("temperature", "room temperature; reaction drawing prints 25 °C"),
            ("time", {"number": time_h, "unit": "h"}),
        ] + common_missing(),
        outcomes=[
            ("isolated_combined_yield_8_plus_9", {"number": yld, "unit": "%"}),
            ("yield_basis", "isolated yield based on 1d"),
            ("ratio_8_to_9", product_ratio),
            ("ratio_measurement_method", "1H NMR analysis"),
        ],
        notes=["Table 3 optimization row."],
        unresolved=["The solvent cell is blank in Table 3 entry 6." if solvent is None else "Exact product structures are not independently structure-verified.", "Atmosphere, concentration, workup, purification, and isolated masses are not reported."],
    ))


# Page 4: proposed Pd(0) catalytic cycle.
e = ev(4)
records.append(record(
    "scheme4_proposed_pd0_cycle", "mechanism", 4,
    participants=[
        part("s4_allylic_bromide", "reactant", "generic allylic bromide", "allylic bromide", e),
        part("s4_allenyl_ketone", "reactant", "generic 1,2-allenyl ketone", "1,2-allenyl ketone", e),
        part("s4_pi_allyl6", "unspecified_agent", "π-allyl palladium species 6", "proposed π-allyl palladium species 6", e),
        part("s4_furanyl7", "unspecified_agent", "π-allyl 3-furanyl palladium species 7", "proposed π-allyl 3-furanyl palladium species 7", e),
        part("s4_product", "product", "generic 3-allylic furan", "3-allylic polysubstituted furan", e),
        part("s4_pd0", "catalyst", "Pd(0)", "palladium(0)", e),
    ],
    conditions=[], outcomes=[],
    notes=["Scheme 4 is a proposed Pd(0) catalytic cycle; intermediates 6 and 7 are not reported as isolated or directly observed."],
    unresolved=["Generic substituents and organopalladium intermediate structures remain unverified; the scheme supplies no independent experimental conditions or outcomes."],
))


raw_path = RUN / "raw_model" / "records_pages_0001_0004.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = {r["source_reaction_id"]: r["record_id"] for r in records}
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "graphical abstract reaction arrow", "finding": "Current-paper generic PdCl2(PhCN)2/K2CO3/CH3CN cyclization-coupling; classified as a general scheme, not an individual run.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
                {"region": "Scheme 1 and adjacent lower-right prose", "finding": "Generic Pd(PPh3)4/Ag2CO3 prior method explicitly attributed to reference 8; classified as literature_example.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]},
            ],
            "record_ids": [ids["graphical_abstract_general_scheme"], ids["scheme1_prior_work_generic"]],
            "unresolved": ["Generic R groups and drawing-derived structures are not structure-verified.", "No individual yield or complete procedure appears on page 1."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "Table 1 reaction drawing, entries 1-13, and footnotes a-e", "finding": "Thirteen distinct catalyst/base/halide/ratio optimization experiments, including low-yield and 0-dominant-product outcomes; each row was retained separately and footnote overrides were applied.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
                {"region": "body prose below Table 1", "finding": "Explains the current Pd(II) route and points to Table 1; no additional standalone experiment beyond the table rows.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            ],
            "record_ids": [ids[f"table1_entry{i:02d}"] for i in range(1, 14)],
            "unresolved": ["No detailed workup, purification, atmosphere, concentration, or isolated masses are supplied.", "Ag2CO3 loading is absent for Table 1 rows other than entry 3."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 2, upper left", "finding": "Proposed Pd(II) pathway through furanyl palladium species 2; classified as mechanism, not an experiment.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Table 2, left column", "finding": "Eight substrate-scope experiments, one per row, with isolated yields and common conditions.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Scheme 3, upper right", "finding": "Three distinct catalyst comparison runs: two 0% results and one 79% Pd2(dba)3·CHCl3 result.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "Table 3, lower right", "finding": "Seven solvent/stoichiometry optimization rows with isolated combined yield and 8/9 ratio.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
                {"region": "body prose surrounding schemes and tables", "finding": "Regioselectivity/stereoretention observations and catalyst comparison prose were linked to matching records; no duplicate runs were created.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            ],
            "record_ids": (
                [ids["scheme2_proposed_pdii_pathway"]]
                + [ids[f"table2_entry{i:02d}"] for i in range(1, 9)]
                + [ids[f"scheme3_catalyst_row{i}"] for i in range(1, 4)]
                + [ids[f"table3_entry{i:02d}"] for i in range(1, 8)]
            ),
            "unresolved": ["Scheme 3 does not report reaction times or yield measurement bases.", "The solvent cell for Table 3 entry 6 is blank.", "No detailed workup/purification is present, and all structures remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 4, upper half", "finding": "Proposed Pd(0) catalytic cycle with π-allyl species 6 and π-allyl 3-furanyl palladium species 7; classified as mechanism.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
                {"region": "conclusion and Supporting Information notice", "finding": "No additional experiment; the article says procedures/data are available as SI, but no SI is supplied or associated in this pilot.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            ],
            "record_ids": [ids["scheme4_proposed_pd0_cycle"]],
            "unresolved": ["Proposed intermediates are not observed species and their structures remain unverified.", "Supporting Information is mentioned but unavailable and must not be inferred or associated."],
        },
    ],
}
coverage_path = RUN / "coverage" / "pages_0001_0004.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{i}:text" for i in range(1, 5)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; records and coverage ledger generated for this page."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
