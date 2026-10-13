import json
from pathlib import Path


DOC = "doc_a10bd7ae7a17f1c1"
OUT = Path(__file__).resolve().parent
RUN = OUT.parent

P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"
P3T = f"{DOC}:page3:text"
P3I = f"{DOC}:page3:image"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, evidence, label=None, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(value, ev) for value, ev in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


def missing_operational_fields():
    return [
        field("reaction_scale", None, []),
        field("atmosphere", None, []),
        field("workup", None, []),
        field("purification", None, []),
    ]


SOLVENTS = {
    "Toluene": ("toluene", "Cc1ccccc1"),
    "CH2Cl2": ("dichloromethane", "ClCCl"),
    "CH3CN": ("acetonitrile", "CC#N"),
    "Xylenes": ("xylenes", None),
    "DCE": ("1,2-dichloroethane", "ClCCCl"),
    "THF": ("tetrahydrofuran", "C1CCOC1"),
}


CATALYST_NAMES = {
    "PtCl4": "platinum(IV) chloride",
    "AgBF4": "silver tetrafluoroborate",
    "AuCl(PPh3)": "chlorotriphenylphosphinegold(I)",
    "PtCl2": "platinum(II) chloride",
}


SMILES_1A = "CCCCCC=C=CC(O)c1cc2ccccc2n1CC"
SMILES_3A = "CCn1c2ccccc2c2cccc(CCCCC)c21"


def table1_record(entry, catalyst, loading, solvent, time_h, nmr_yield=None,
                  isolated_yield=None, recovery=None, product_marker=None, extra=None):
    ev = [P1T, P1I, P2T, P2I]
    catalyst_id = f"t1e{entry}_catalyst"
    solvent_id = f"t1e{entry}_solvent"
    p = [
        participant(f"t1e{entry}_1a", "reactant", ev, "1a",
                    "1-(1-ethyl-1H-indol-2-yl)nona-2,3-dien-1-ol", SMILES_1A),
        participant(f"t1e{entry}_3a", "product", ev, "3a",
                    "9-ethyl-4-pentyl-9H-carbazole", SMILES_3A),
        participant(catalyst_id, "catalyst", ev, catalyst, CATALYST_NAMES[catalyst], None,
                    [field("catalyst_loading", {"number": loading, "unit": "mol%"}, ev)]),
        participant(solvent_id, "solvent", ev, solvent, SOLVENTS[solvent][0], SOLVENTS[solvent][1]),
        participant(f"t1e{entry}_internal_standard", "unspecified_agent", ev, "CH2Br2",
                    "dibromomethane (1H NMR internal standard)", "BrCBr"),
    ]
    step_ids = [f"t1e{entry}_1a", catalyst_id, solvent_id]
    notes = []
    if extra:
        p.extend(extra.get("participants", []))
        step_ids.extend(extra.get("step_ids", []))
        notes.extend(extra.get("notes", []))
    conditions = [
        field("solvent", solvent, ev),
        field("temperature", "r.t.", ev),
        field("time", {"number": time_h, "unit": "h"}, ev),
        *missing_operational_fields(),
    ]
    outcomes = []
    product_id = f"t1e{entry}_3a"
    if nmr_yield is not None:
        outcomes.append(field("1H_NMR_yield", {"number": nmr_yield, "unit": "%"}, ev, [product_id]))
    if product_marker is not None:
        outcomes.append(field("reported_product_yield", product_marker, ev, [product_id]))
    if isolated_yield is not None:
        outcomes.append(field("isolated_yield", {"number": isolated_yield, "unit": "%"}, ev, [product_id]))
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, ev,
                              [f"t1e{entry}_1a"]))
    outcomes.append(field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", ev,
                          [product_id]))
    unresolved = [
        "Reaction scale, atmosphere, workup, and purification are not reported in the supplied main-text pages.",
        "No supporting-information PDF was supplied or associated.",
        "Candidate SMILES for 1a and 3a are unverified against an independently reviewed structure source.",
    ]
    if entry == 3:
        unresolved.append("The table dash is preserved and not interpreted as zero or not detected; the prose only says the catalyst was inactive.")
    if entry == 4:
        unresolved.append("The prose qualifies the <7% result as 'if any' and reports rapid decomposition of 1a.")
    return record(f"table1_entry{entry}", "optimization_entry", ev, p,
                  [{"step_id": "cyclization", "participant_ids": step_ids, "conditions": conditions}],
                  outcomes, notes, unresolved)


records = []
records.append(table1_record(1, "PtCl4", 5, "Toluene", 1, nmr_yield=65))
records.append(table1_record(2, "AgBF4", 20, "Toluene", 3, nmr_yield=13))
records.append(table1_record(3, "AuCl(PPh3)", 10, "Toluene", 10,
                             recovery=92, product_marker="table dash (–)"))
agotf = participant("t1e4_AgOTf", "reagent", [P1T, P1I, P2T, P2I], "AgOTf",
                    "silver trifluoromethanesulfonate", None,
                    [field("reagent_loading", {"number": 10, "unit": "mol%"}, [P1T, P1I, P2T, P2I])])
records.append(table1_record(
    4, "AuCl(PPh3)", 10, "Toluene", 4,
    product_marker={"number": 7, "unit": "%", "qualifier": "lt", "raw_text": "<7%"},
    extra={
        "participants": [agotf],
        "step_ids": ["t1e4_AgOTf"],
        "notes": [("AgOTf (10 mol%) was added; 1a decomposed quickly and the product yield was <7%, if any.", [P1T, P1I, P2T, P2I])],
    },
))
records.append(table1_record(5, "PtCl2", 5, "Toluene", 2, nmr_yield=90, isolated_yield=83))
records.append(table1_record(6, "PtCl2", 5, "CH2Cl2", 3, nmr_yield=80))
records.append(table1_record(7, "PtCl2", 5, "CH3CN", 3, nmr_yield=20))
records.append(table1_record(8, "PtCl2", 5, "Xylenes", 3, nmr_yield=67))
records.append(table1_record(9, "PtCl2", 5, "DCE", 3, nmr_yield=82))
records.append(table1_record(10, "PtCl2", 5, "THF", 3, nmr_yield=38))
records.append(table1_record(11, "PtCl2", 2, "Toluene", 5, nmr_yield=79, isolated_yield=74))


TABLE2 = [
    (1, "1a", "3a", "Et", "H", "H", "n-C5H11", "H", 2, 83),
    (2, "1b", "3b", "Et", "H", "H", "Me", "H", 2, 86),
    (3, "1c", "3c", "Et", "Me", "H", "n-C6H13", "H", 2, 81),
    (4, "1d", "3d", "Et", "H", "H", "n-C6H13", "5-Me", 2, 75),
    (5, "1e", "3e", "Et", "H", "H", "n-C6H13", "5-OMe", 3, 75),
    (6, "1f", "3f", "Et", "H", "H", "Bn", "H", 5, 50),
    (7, "1g", "3g", "Et", "H", "Ph", "H", "H", 4, 70),
    (8, "1h", "3h", "Et", "H", "n-C4H9", "H", "H", 3, 74),
    (9, "1i", "3i", "Me", "H", "Ph", "H", "H", 4, 81),
    (10, "1j", "3j", "Me", "H", "n-C4H9", "H", "H", 4, 71),
    (11, "1k", "3k", "Et", "H", "allyl", "H", "H", 3, 74),
    (12, "1l", "3l", "Et", "H", "Ph", "H", "5-Me", 17, 70),
    (13, "1m", "3m", "Ph", "H", "Ph", "H", "H", 19, 78),
    (14, "1n", "3n", "Et", "H", "COOMe", "H", "H", 36, 67),
    (15, "1o", "3o", "Et", "H", "CONMe2", "H", "H", 24, 83),
    (16, "1p", "3p", "Et", "H", "CH2OH", "H", "H", 23, 64),
    (17, "1q", "3q", "Et", "H", "CH2OH", "H", "4-Me", 20, 81),
    (18, "1r", "3r", "Et", "H", "CH2OH", "H", "7-Me", 21, 68),
    (19, "1s", "3s", "Et", "H", "H", "H", "H", 4, 70),
]


def table2_record(row):
    entry, substrate, product, r1, r2, r3, r4, r5, time_h, yield_pct = row
    ev = [P1T, P1I, P2T, P2I]
    notes = [
        ({"R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5}, ev),
        ("The table depicts PtCl2-catalyzed conversion of the allenol template 1 to the carbazole template 3.", ev),
    ]
    if entry in (5, 6, 13):
        ev += [P3T, P3I]
        notes.append(("The authors state that the result in this Table 2 entry was reproduced by Mr Guobi Chai.", [P3T, P3I]))
    if entry == 7:
        ev += [P3T, P3I]
        notes.append(("Product 3g was further confirmed by X-ray diffraction; CCDC 713481 is cited.", [P1T, P1I, P3T, P3I]))
    sub_id = f"t2e{entry}_{substrate}"
    prod_id = f"t2e{entry}_{product}"
    cat_id = f"t2e{entry}_PtCl2"
    solv_id = f"t2e{entry}_toluene"
    sub_name = "1-(1-ethyl-1H-indol-2-yl)nona-2,3-dien-1-ol" if entry == 1 else None
    prod_name = "9-ethyl-4-pentyl-9H-carbazole" if entry == 1 else None
    p = [
        participant(sub_id, "reactant", ev, substrate, sub_name, SMILES_1A if entry == 1 else None),
        participant(prod_id, "product", ev, product, prod_name, SMILES_3A if entry == 1 else None),
        participant(cat_id, "catalyst", ev, "PtCl2", "platinum(II) chloride", None,
                    [field("catalyst_loading", {"number": 5, "unit": "mol%"}, ev)]),
        participant(solv_id, "solvent", ev, "toluene", "toluene", "Cc1ccccc1"),
    ]
    conditions = [
        field("solvent", "toluene", ev),
        field("temperature", "r.t.", ev),
        field("time", {"number": time_h, "unit": "h"}, ev),
        *missing_operational_fields(),
    ]
    outcomes = [
        field("isolated_yield", {"number": yield_pct, "unit": "%"}, ev, [prod_id]),
        field("yield_measurement_basis", "isolated yield", ev, [prod_id]),
    ]
    unresolved = [
        "Reaction scale, atmosphere, workup, and purification are not reported in the supplied main-text pages.",
        "No supporting-information PDF was supplied or associated, despite the main text stating that ESI exists.",
        "The row-specific substrate and product drawings are defined by an R-group template; SMILES are left missing except for explicitly named 1a/3a.",
    ]
    return record(f"table2_entry{entry}", "substrate_scope_entry", ev, p,
                  [{"step_id": "cyclization", "participant_ids": [sub_id, cat_id, solv_id], "conditions": conditions}],
                  outcomes, notes, unresolved)


records.extend(table2_record(row) for row in TABLE2)


scheme1_prior_ev = [P1T, P1I]
records.append(record(
    "scheme1_prior_interolecular_route",
    "literature_example",
    scheme1_prior_ev,
    [
        participant("s1prior_indole", "reactant", scheme1_prior_ev, "generic indole", None, None),
        participant("s1prior_beta_allenol", "reactant", scheme1_prior_ev, "generic beta-allenol", None, None),
        participant("s1prior_product", "product", scheme1_prior_ev,
                    "indole derivative bearing a saturated six-membered cyclic ether at C3", None, None),
        participant("s1prior_PtCl4", "catalyst", scheme1_prior_ev, "PtCl4", "platinum(IV) chloride", None,
                    [field("catalyst_loading", {"number": 5, "unit": "mol%"}, scheme1_prior_ev)]),
        participant("s1prior_THF", "solvent", scheme1_prior_ev, "THF", "tetrahydrofuran", "C1CCOC1"),
    ],
    [{"step_id": "prior_literature_cyclization",
      "participant_ids": ["s1prior_indole", "s1prior_beta_allenol", "s1prior_PtCl4", "s1prior_THF"],
      "conditions": [field("solvent", "THF", scheme1_prior_ev), field("temperature", "r.t.", scheme1_prior_ev),
                     field("time", None, []), *missing_operational_fields()]}],
    [field("reported_yield", None, [], ["s1prior_product"])],
    [("Scheme 1 upper arrow is explicitly presented as the authors' recently reported prior work (reference 7), not a new experiment in this paper.", scheme1_prior_ev)],
    ["Generic R groups prevent a unique structure assignment.", "Time, yield, scale, workup, and purification are not reported in Scheme 1."],
))


scheme1_current_ev = [P1T, P1I]
records.append(record(
    "scheme1_current_generic_cyclization",
    "general_scheme",
    scheme1_current_ev,
    [
        participant("s1current_1", "reactant", scheme1_current_ev, "1", "generic 1-(indol-2-yl)-2,3-allenol", None),
        participant("s1current_3", "product", scheme1_current_ev, "3", "generic carbazole product", None),
        participant("s1current_PtCl4", "catalyst", scheme1_current_ev, "PtCl4", "platinum(IV) chloride", None,
                    [field("catalyst_loading", {"number": 5, "unit": "mol%"}, scheme1_current_ev)]),
        participant("s1current_THF", "solvent", scheme1_current_ev, "THF", "tetrahydrofuran", "C1CCOC1"),
    ],
    [{"step_id": "generic_cyclization",
      "participant_ids": ["s1current_1", "s1current_PtCl4", "s1current_THF"],
      "conditions": [field("solvent", "THF", scheme1_current_ev), field("temperature", "r.t.", scheme1_current_ev),
                     field("time", None, []), *missing_operational_fields()]}],
    [field("reported_yield", None, [], ["s1current_3"])],
    [("Bracketed structure 2 is the envisioned polycyclic product; the text states that carbazole 3 was formed instead.", scheme1_current_ev)],
    ["This is a generic scheme, not an independently quantified experimental row.",
     "The lower Scheme 1 arrow shows PtCl4/THF, whereas the surrounding prose and Table 1 discuss the initial PtCl4 experiment in toluene; the generic arrow was not silently substituted with the table condition.",
     "Generic R groups prevent unique structures; time, yield, scale, workup, and purification are missing."],
))


mechanism_ev = [P1T, P1I, P2T, P2I]
records.append(record(
    "scheme2_proposed_mechanism",
    "mechanism",
    mechanism_ev,
    [
        participant("mech_1", "reactant", mechanism_ev, "1", "generic 1-(indol-2-yl)-2,3-allenol", None),
        participant("mech_3", "product", mechanism_ev, "3", "generic carbazole", None),
        participant("mech_PtCl2", "catalyst", mechanism_ev, "PtCl2", "platinum(II) chloride", None),
        participant("mech_4", "unspecified_agent", mechanism_ev, "4", "proposed PtCl2-allene complex", None),
        participant("mech_5", "unspecified_agent", mechanism_ev, "5", "proposed cyclized organoplatinum intermediate", None),
        participant("mech_6", "unspecified_agent", mechanism_ev, "6", "proposed protonated alcohol intermediate", None),
        participant("mech_7", "unspecified_agent", mechanism_ev, "7", "proposed cyclic vinylic platinum carbene", None),
        participant("mech_HCl", "unspecified_agent", mechanism_ev, "HCl", "hydrogen chloride", "Cl"),
        participant("mech_water", "product", mechanism_ev, "H2O", "water", "O"),
    ],
    [
        {"step_id": "allene_coordination_and_cyclization",
         "participant_ids": ["mech_1", "mech_PtCl2", "mech_4", "mech_5"],
         "conditions": [field("operation", "allene coordination followed by intramolecular attack of indolyl C3", mechanism_ev)]},
        {"step_id": "protonation_and_water_elimination",
         "participant_ids": ["mech_5", "mech_6", "mech_7", "mech_HCl", "mech_water"],
         "conditions": [field("operation", "hydroxyl protonation followed by elimination of H2O", mechanism_ev)]},
        {"step_id": "one_two_hydrogen_shift",
         "participant_ids": ["mech_7", "mech_3", "mech_PtCl2"],
         "conditions": [field("operation", "1,2-H shift to form 3 and regenerate PtCl2", mechanism_ev)]},
    ],
    [],
    [("Scheme 2 is explicitly labeled a proposed mechanism and does not report separate isolated intermediates or yields.", mechanism_ev)],
    ["Intermediate structures and elementary steps are proposed rather than experimentally isolated or quantified."],
))


raw_path = OUT / "records_pages_0001_0003.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")


t1_ids = [f"{DOC}:table1_entry{i}" for i in range(1, 12)]
t2_ids = [f"{DOC}:table2_entry{i}" for i in range(1, 20)]
scheme_ids = [
    f"{DOC}:scheme1_prior_interolecular_route",
    f"{DOC}:scheme1_current_generic_cyclization",
    f"{DOC}:scheme2_proposed_mechanism",
]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, abstract, and two-column Results and Discussion prose",
                    "finding": "The prose identifies the Pt-catalyzed allenol-to-carbazole transformation, narrates Table 1 optimization outcomes, summarizes Table 2 scope, and states that ESI exists; no SI file was supplied or associated.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "lower-right Scheme 1",
                    "finding": "The upper arrow is cited prior work and is classified as a literature example; the lower arrow is a generic current-paper transformation to carbazole 3, while bracketed 2 is described as the envisioned rather than observed product.",
                    "evidence_ids": [P1I, P1T],
                },
                {
                    "region": "right-column proposed-mechanism discussion above Scheme 1",
                    "finding": "Text proposes intermediates 4–7, water loss, a cyclic vinylic platinum carbene, and a 1,2-H shift; these are classified as mechanism content, not separate experiments.",
                    "evidence_ids": [P1I, P1T, P2I, P2T],
                },
            ],
            "record_ids": t1_ids + t2_ids + scheme_ids,
            "unresolved": [
                "The supplied main paper points to ESI for procedures and characterization, but no SI was explicitly provided; operational details remain missing.",
                "The lower Scheme 1 arrow shows PtCl4/THF while the prose/Table 1 initial PtCl4 experiment uses toluene; both source statements are retained in their own record contexts.",
                "Most Table 2 compounds are defined through an R-group template and were not assigned SMILES without independent structure review.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Table 1 including reaction drawing and footnotes",
                    "finding": "Eleven distinct optimization experiments were extracted row by row. Visual review confirms entry 6 is 3 h and 80% (not the OCR-joined '38 0'); entry 3 retains the table dash plus 92% recovered 1a; entry 4 includes 10 mol% AgOTf; parenthesized values in entries 5 and 11 are isolated yields.",
                    "evidence_ids": [P2I, P2T, P1I, P1T],
                },
                {
                    "region": "upper-right Fig. 1 and middle-right Scheme 2",
                    "finding": "Fig. 1 is an ORTEP representation of 3g and not a reaction. Scheme 2 is a proposed catalytic mechanism and is represented by one mechanism record rather than by isolated experimental intermediates.",
                    "evidence_ids": [P2I, P2T, P1I, P1T],
                },
                {
                    "region": "lower half Table 2 including generic arrow and all rows",
                    "finding": "Nineteen substrate-scope rows were extracted independently with row-specific R1–R5 assignments, 5 mol% PtCl2, toluene, room temperature, reaction time, and isolated yield linked to the row product.",
                    "evidence_ids": [P2I, P2T, P1I, P1T],
                },
            ],
            "record_ids": t1_ids + t2_ids + [f"{DOC}:scheme2_proposed_mechanism"],
            "unresolved": [
                "Reaction scale, atmosphere, workup, and purification are absent from the supplied main-text page.",
                "The table does not provide unique machine-readable structures for most R-group-defined rows; these remain unverified and without SMILES.",
            ],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "top-left conclusion continuation and acknowledgements",
                    "finding": "No new reaction row is introduced. The authors state that Table 2 entries 5, 6, and 13 were reproduced; this is linked as supplemental evidence to those existing records rather than counted as new experiments.",
                    "evidence_ids": [P3I, P3T],
                },
                {
                    "region": "two-column Notes and references",
                    "finding": "The page consists mainly of cited prior literature and is not converted into experiments of the current paper. Footnote 13 supplies crystal data for 3g/CCDC 713481 and is linked as characterization context to Table 2 entry 7, not as a reaction outcome.",
                    "evidence_ids": [P3I, P3T],
                },
            ],
            "record_ids": [
                f"{DOC}:table2_entry5",
                f"{DOC}:table2_entry6",
                f"{DOC}:table2_entry7",
                f"{DOC}:table2_entry13",
            ],
            "unresolved": [
                "The reproduced experiments are not accompanied by separate batch conditions or measurements on this page.",
                "Cited papers were not treated as source documents, so their experimental details remain outside this extraction.",
            ],
        },
    ],
}
coverage_dir = RUN / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0001_0003.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")


tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {P1T, P2T, P3T}:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text reviewed; records and coverage ledger generated, with unresolved source omissions retained."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")


print(json.dumps({"records": len(records), "raw_records": str(raw_path), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
