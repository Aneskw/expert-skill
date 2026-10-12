"""Build page-1--6 evidence-linked machine records for Xu, Li and Ma (2002).

This is a source transcription aid, not a chemistry-certification step.  The merge
tool will quarantine all records as needs_review and all facts as unreviewed.
"""
import json
from pathlib import Path


DOC = "doc_f83285164919129a"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(*pages):
    ids = []
    for page in pages:
        ids += [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    return ids


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def rec(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
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
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "No explicitly associated supporting information was provided.",
                "Machine-transcribed record requires independent source review.",
            ],
        },
    }


def q(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


names = {
    "1a": "3-(n-butyl)penta-3,4-dien-2-ol",
    "1b": "3-(n-propyl)penta-3,4-dien-2-ol",
    "1c": "3-(n-pentyl)penta-3,4-dien-2-ol",
    "1d": "3-(n-hexyl)penta-3,4-dien-2-ol",
    "1e": "3-(n-heptyl)penta-3,4-dien-2-ol",
    "1f": "3-benzylpenta-3,4-dien-2-ol",
    "1g": "3-(2-phenylethyl)penta-3,4-dien-2-ol",
    "1h": "3-allylpenta-3,4-dien-2-ol",
    "1i": "4-(n-butyl)hexa-4,5-dien-3-ol",
    "1j": "4-(n-propyl)hexa-4,5-dien-3-ol",
    "1k": "4-(n-pentyl)hexa-4,5-dien-3-ol",
    "1l": "4-(n-heptyl)hexa-4,5-dien-3-ol",
}
allenol_smiles = {
    "1a": "C=C=C(CCCC)C(O)C",
    "1b": "C=C=C(CCC)C(O)C",
    "1c": "C=C=C(CCCCC)C(O)C",
    "1d": "C=C=C(CCCCCC)C(O)C",
    "1e": "C=C=C(CCCCCCC)C(O)C",
    "1f": "C=C=C(Cc1ccccc1)C(O)C",
    "1g": "C=C=C(CCc1ccccc1)C(O)C",
    "1h": "C=C=C(CC=C)C(O)C",
    "1i": "C=C=C(CCCC)C(O)CC",
    "1j": "C=C=C(CCC)C(O)CC",
    "1k": "C=C=C(CCCCC)C(O)CC",
    "1l": "C=C=C(CCCCCCC)C(O)CC",
}
precursors = {
    "1a": ("1-bromohept-2-yne", "BrCC#CCCCC"),
    "1b": ("1-bromohex-2-yne", "BrCC#CCCC"),
    "1c": ("1-bromooct-2-yne", "BrCC#CCCCCC"),
    "1d": ("1-bromonon-2-yne", "BrCC#CCCCCCC"),
    "1e": ("1-bromodec-2-yne", "BrCC#CCCCCCCC"),
    "1g": ("1-bromo-5-phenylpent-2-yne", "BrCC#CCCc1ccccc1"),
    "1h": ("6-bromohex-1-en-4-yne", "C=CCC#CCBr"),
    "1i": ("1-bromohept-2-yne", "BrCC#CCCCC"),
    "1j": ("1-bromohex-2-yne", "BrCC#CCCC"),
    "1k": ("1-bromodec-2-yne", "BrCC#CCCCCCCC"),
    "1l": ("1-bromodec-2-yne", "BrCC#CCCCCCCC"),
}


def acetate_smiles(label):
    return allenol_smiles[label].replace("C(O)", "C(OC(=O)C)")


records = []

# Page 4 individual preparations of racemic 1a-e and 1g-l; Scheme 1 on page 2
# supplies the explicitly depicted shared SnCl2/NaI/DMF/0 C conditions.
synth_rows = {
    "1a": (3.90, 22.5, "acetaldehyde", "CC=O", 2.20, 50.0, 1.63, 50),
    "1b": (6.78, 42.4, "acetaldehyde", "CC=O", 3.70, 84.8, 2.41, 45),
    "1c": (11.1, 59.0, "acetaldehyde", "CC=O", 5.20, 118.0, 7.20, 79),
    "1d": (4.06, 20.0, "acetaldehyde", "CC=O", 1.76, 40.0, 2.16, 64),
    "1e": (6.48, 30.0, "acetaldehyde", "CC=O", 2.64, 60.0, 3.70, 67),
    "1g": (4.01, 18.0, "acetaldehyde", "CC=O", 3.70, 84.8, 2.03, 60),
    "1h": (3.18, 20.0, "acetaldehyde", "CC=O", 1.76, 40.0, 1.10, 44),
    "1i": (6.68, 38.4, "acetaldehyde", "CC=O", 3.38, 76.8, 3.68, 62),
    "1j": (6.90, 43.2, "propionaldehyde", "CCC=O", 2.01, 34.6, 4.10, 67),
    "1k": (7.10, 37.5, "propionaldehyde", "CCC=O", 1.74, 30.0, 3.40, 68),
    "1l": (7.08, 37.5, "propionaldehyde", "CCC=O", 1.74, 30.0, 3.40, 68),
}
for label, row in synth_rows.items():
    evidence = ev(2, 4)
    pmass, pmmol, aldehyde, aldehyde_smiles, amass, ammol, product_mass, product_yield = row
    precursor_name, precursor_smiles = precursors[label]
    ps = [
        part("propargylic_bromide", "reactant", precursor_name, precursor_name, evidence,
             precursor_smiles, [fld("mass", q(pmass, "g"), evidence), fld("amount", q(pmmol, "mmol"), evidence)]),
        part("aldehyde", "reactant", aldehyde, aldehyde, evidence, aldehyde_smiles,
             [fld("mass", q(amass, "g"), evidence), fld("amount", q(ammol, "mmol"), evidence)]),
        part("sncl2", "reagent", "SnCl2", "tin(II) chloride", evidence, "[Cl-].[Cl-].[Sn+2]"),
        part("nai", "reagent", "NaI", "sodium iodide", evidence, "[Na+].[I-]"),
        part("dmf", "solvent", "DMF", "N,N-dimethylformamide", evidence, "CN(C)C=O"),
        part("product", "product", f"rac-{label}", f"racemic {names[label]}", evidence,
             allenol_smiles[label], [fld("isolated_mass", q(product_mass, "g"), evidence)]),
    ]
    conditions = [fld("temperature", q(0, "°C"), evidence)]
    unresolved = [
        "No explicitly associated supporting information was provided.",
        "The individual paragraph does not repeat reaction time or SnCl2/NaI/DMF quantities; only the depicted shared Scheme 1 conditions are structured.",
        "The proposed SMILES is an unverified connectivity candidate and does not certify stereochemistry.",
    ]
    if label == "1a":
        ps[2]["amounts"] = [fld("mass", q(4.70, "g"), evidence), fld("amount", q(25.0, "mmol"), evidence)]
        ps[3]["amounts"] = [fld("mass", q(3.75, "g"), evidence), fld("amount", q(25.0, "mmol"), evidence)]
        ps[4]["amounts"] = [fld("volume", q(50, "mL"), evidence)]
        conditions = [
            fld("initial_temperature", "room temperature", evidence),
            fld("initial_time", q(1, "h"), evidence),
            fld("temperature", q(0, "°C"), evidence),
            fld("time", q(12, "h"), evidence),
            fld("workup", "quenched with water; extracted with diethyl ether; organic layers washed with water and dried over anhydrous MgSO4", evidence),
            fld("purification", "flash chromatography on silica gel, petroleum ether/diethyl ether 20:1", evidence),
        ]
        unresolved = [
            "No explicitly associated supporting information was provided.",
            "The proposed SMILES is an unverified connectivity candidate and does not certify stereochemistry.",
        ]
    if label == "1i":
        unresolved.append("The source calls the aldehyde acetaldehyde although product 1i is named as the ethyl-substituted hexa-4,5-dien-3-ol; the inconsistency is preserved.")
    if label == "1k":
        unresolved.append("The source names 1-bromodec-2-yne for pentyl product 1k, which is internally inconsistent with the stated product label; no correction was inferred.")
    records.append(rec(
        f"synthesis_racemic_{label}", "reported_experiment", evidence, ps,
        [{"step_id": "reaction_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
        [fld("isolated_yield", q(product_yield, "%"), evidence, ["product"]),
         fld("yield_measurement_basis", "isolated after chromatography" if label == "1a" else "reported afforded yield; individual purification not restated", evidence, ["product"])],
        unresolved=unresolved,
    ))

# The distinct LiAlH4 reduction giving racemic 1f.
evidence = ev(2, 4)
ps = [
    part("ketone", "reactant", "3-benzylpenta-3,4-dien-2-one", "3-benzylpenta-3,4-dien-2-one", evidence,
         "C=C=C(Cc1ccccc1)C(C)=O", [fld("mass", q(1.60, "g"), evidence), fld("amount", q(9.30, "mmol"), evidence)]),
    part("lialh4", "reagent", "LiAlH4", "lithium aluminium hydride", evidence, "[Li+].[AlH4-]",
         [fld("mass", q(0.38, "g"), evidence), fld("amount", q(10.0, "mmol"), evidence)]),
    part("thf", "solvent", "THF", "tetrahydrofuran", evidence, "C1CCOC1", [fld("volume", q(40, "mL"), evidence)]),
    part("product", "product", "rac-1f", "racemic 3-benzylpenta-3,4-dien-2-ol", evidence,
         allenol_smiles["1f"], [fld("isolated_mass", q(1.17, "g"), evidence)]),
]
records.append(rec(
    "synthesis_racemic_1f", "reported_experiment", evidence, ps,
    [{"step_id": "reduction_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
        fld("operation", "ketone solution added dropwise to LiAlH4 suspension with ice-bath cooling", evidence),
        fld("temperature", q(0, "°C"), evidence), fld("time", q(20, "min"), evidence),
        fld("workup", "excess LiAlH4 decomposed dropwise with water; filtered; solid washed with diethyl ether; organic phases washed with brine and dried over anhydrous Na2SO4", evidence),
        fld("purification", "flash chromatography on silica gel, petroleum ether (30-60 °C)/diethyl ether 8:1", evidence),
    ]}],
    [fld("isolated_yield", q(72, "%"), evidence, ["product"]), fld("yield_measurement_basis", "isolated after flash chromatography", evidence, ["product"])],
    unresolved=["No explicitly associated supporting information was provided.", "The proposed SMILES is an unverified connectivity candidate and does not certify stereochemistry."],
))


def kinetic_participants(label, evidence, substrate_mass, enzyme_mass=70, vinyl_volume=5, product_masses=(None, None), catalyst="Novozym-435"):
    alcohol_mass, acetate_mass = product_masses
    product_alcohol_amounts = [] if alcohol_mass is None else [fld("isolated_mass", q(alcohol_mass, "mg"), evidence)]
    product_acetate_amounts = [] if acetate_mass is None else [fld("isolated_mass", q(acetate_mass, "mg"), evidence)]
    return [
        part("racemic_alcohol", "reactant", label, f"racemic {names[label]}", evidence, allenol_smiles[label], [fld("mass", q(substrate_mass, "mg"), evidence)]),
        part("vinyl_acetate", "reactant", "vinyl acetate", "vinyl acetate", evidence, "C=COC(=O)C", [fld("volume", q(vinyl_volume, "mL"), evidence)]),
        part("enzyme", "catalyst", catalyst, catalyst, evidence, None, [fld("mass", q(enzyme_mass, "mg"), evidence)]),
        part("alcohol_product", "product", f"(S)-(-)-{label}", f"(S)-(-)-{names[label]}", evidence, allenol_smiles[label], product_alcohol_amounts),
        part("acetate_product", "product", f"(R)-(+)-2{label[-1]}", f"(R)-(+)-{names[label].replace('-ol', '-yl acetate')}", evidence, acetate_smiles(label), product_acetate_amounts),
    ]


# Table 1 enzyme screening; entry 7 is the same 96 h 1a experiment represented
# below as the first substrate-scope entry, so only entries 1-6 are added here.
screen = [
    (1, "Novozym 871 L", None, None, None, None),
    (2, "Lipolase", None, None, None, None),
    (3, "CCL", 40, 9, 17, 22),
    (4, "Lipase AY", 24, 1, 35, 38),
    (5, "Lipase PS", 34, 39, 20, 96),
    (6, "Lipase AK", 26, 99, 39, 79),
]
for entry, enzyme, ay, aee, ey, eee in screen:
    evidence = ev(2)
    if ay is None:
        ps = kinetic_participants("1a", evidence, 100, 70, 5, catalyst=enzyme)[:3]
        outcomes = [fld("reaction_result", "no reaction", evidence)]
    else:
        ps = kinetic_participants("1a", evidence, 100, 70, 5, catalyst=enzyme)
        outcomes = [
            fld("alcohol_isolated_yield", q(ay, "%"), evidence, ["alcohol_product"]),
            fld("alcohol_ee", q(aee, "%"), evidence, ["alcohol_product"]),
            fld("acetate_isolated_yield", q(ey, "%"), evidence, ["acetate_product"]),
            fld("acetate_ee", q(eee, "%"), evidence, ["acetate_product"]),
            fld("yield_measurement_basis", "isolated yield based on 1a", evidence, ["alcohol_product", "acetate_product"]),
        ]
    records.append(rec(
        f"table1_entry_{entry}_enzyme_screen", "optimization_entry", evidence, ps,
        [{"step_id": "kinetic_resolution", "participant_ids": [p["entity_id"] for p in ps], "conditions": [fld("temperature", q(30, "°C"), evidence), fld("time", q(4, "d"), evidence)]}],
        outcomes,
        unresolved=["No explicitly associated supporting information was provided.", "Product structures, where present, are unverified connectivity candidates; allene stereochemistry is not certified by SMILES."],
    ))

# Table 2 scope rows merged with the corresponding experimental paragraphs on
# pages 4-6.  Row 1 also merges Table 1 entry 7 (4 d = 96 h).
scope = {
    "1a": (96, 39, 99.0, 31, 98.9, 100, 39, 40, (2, 4)),
    "1b": (72, 36, 99.7, 36, 95.4, 101, 36, 48, (2, 4)),
    "1c": (100, 41, 99.5, 39, 99.0, 101, 41, 50, (2, 4)),
    "1d": (82.5, 40, 99.1, 31, 99.1, 100, 40, 39, (2, 4, 5)),
    "1e": (82.5, 45, 99.0, 49, 99.2, 100, 45, 60, (2, 5)),
    "1f": (72, 42, 95.9, 45, 99.2, 100, 42, 55, (2, 5)),
    "1g": (82.5, 50, 98.6, 44, 94.3, 100, 50, 54, (2, 5)),
    "1h": (82.5, 31, 99.7, 38, 98.8, 100, 31, 51, (2, 5)),
    "1i": (102, 49, 99.0, 43, 99.5, 101, 49, 55, (2, 5)),
    "1j": (74, 45, 99.7, 37, 96.4, 101, 45, 48, (2, 5, 6)),
    "1k": (84, 39, 99.4, 38, 99.7, 101, 39, 48, (2, 6)),
    "1l": (102, 49, 99.7, 47, 99.4, 102, 49, 58, (2, 6)),
}
for label, row in scope.items():
    t, ay, aee, ey, eee, input_mass, amass, emass, pages = row
    evidence = ev(*pages)
    ps = kinetic_participants(label, evidence, input_mass, 70, 5, (amass, emass))
    notes = []
    if label in {"1i", "1j", "1k", "1l"}:
        notes.append("The alcohol ee was reported as determined after conversion to the corresponding acetate.")
    scope_outcomes = [
        fld("alcohol_isolated_yield", q(ay, "%"), evidence, ["alcohol_product"]),
        fld("alcohol_ee", q(aee, "%"), evidence, ["alcohol_product"]),
        fld("acetate_isolated_yield", q(ey, "%"), evidence, ["acetate_product"]),
        fld("acetate_ee", q(eee, "%"), evidence, ["acetate_product"]),
        fld("yield_measurement_basis", "isolated yield based on starting alcohol", evidence, ["alcohol_product", "acetate_product"]),
        fld("ee_measurement_basis", "GC or HPLC; compound-specific analytical method given in the experimental paragraph", evidence, ["alcohol_product", "acetate_product"]),
    ]
    if label == "1a":
        scope_outcomes.append(fld("alcohol_minor_enantiomer_table1", "opposite enantiomer not detected by GC", evidence, ["alcohol_product"]))
    records.append(rec(
        f"kinetic_resolution_{label}_30c", "substrate_scope_entry", evidence, ps,
        [{"step_id": "kinetic_resolution", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
            fld("temperature", q(30, "°C"), evidence), fld("time", q(t, "h"), evidence),
            fld("workup", "filtered; solvent evaporated" if label == "1a" else None, evidence),
            fld("purification", "flash chromatography on silica gel, petroleum ether/diethyl ether 40:1 to 10:1" if label == "1a" else None, evidence),
        ]}],
        scope_outcomes,
        notes=notes,
        unresolved=["No explicitly associated supporting information was provided.", "SMILES are unverified connectivity candidates and do not certify the assigned axial configurations."],
    ))

# Explicit 10 g-scale demonstration, separate from the 100 mg scope experiment.
evidence = ev(2)
ps = kinetic_participants("1a", evidence, 10005, 7000, 500, (None, None))
ps[0]["amounts"].append(fld("amount", q(71, "mmol"), evidence))
ps[3]["amounts"] = [fld("isolated_mass_prose", q(4.622, "g"), evidence), fld("isolated_mass_equation", q(4.662, "g"), evidence)]
ps[4]["amounts"] = [fld("isolated_mass", q(5.723, "g"), evidence)]
records.append(rec(
    "kinetic_resolution_1a_10g_scale", "reported_experiment", evidence, ps,
    [{"step_id": "kinetic_resolution_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
        fld("temperature", q(30, "°C"), evidence), fld("time", q(47, "h"), evidence),
        fld("workup", "filtered; solids washed with diethyl ether; combined filtrate and washings concentrated", evidence),
        fld("purification", "flash chromatography on silica gel (12 cm x 6.5 cm), petroleum ether/diethyl ether 20:1 (300 mL) to 10:1 (400 mL) to 5:1 (350 mL) to 3:1 (500 mL); elution completed in 55 min", evidence),
    ]}],
    [
        fld("alcohol_isolated_yield", q(46, "%"), evidence, ["alcohol_product"]),
        fld("alcohol_minor_enantiomer", "(R)-isomer not detected by GC", evidence, ["alcohol_product"]),
        fld("acetate_isolated_yield", q(44, "%"), evidence, ["acetate_product"]),
        fld("acetate_ee", q(98.7, "%"), evidence, ["acetate_product"]),
        fld("yield_measurement_basis", "isolated after flash chromatography", evidence, ["alcohol_product", "acetate_product"]),
    ],
    unresolved=["No explicitly associated supporting information was provided.", "The prose reports 4.622 g alcohol whereas Equation (1) prints 4.662 g; both source values are retained.", "SMILES are unverified connectivity candidates and do not certify axial configurations."],
))


# Table 3 exact-quantity optimization rows.  Entry 9 is also Table 4 entry 1.
table3 = [
    (1, 2.5, 100, 35, 30, 96, 37, "not detected", 32, 97.2),
    (2, 1.25, 100, 18, 30, 95, 32, "not detected", 35, 99.6),
    (3, 5, 100, 70, 40, 48, 40, "not detected", 45, 99.1),
    (4, 5, 100, 70, 50, 40, 40, "not detected", 43, 97.8),
    (5, 5, 100, 70, 60, 24.5, 36, "not detected", 39, "not detected"),
    (6, 1.25, 100, 18.5, 60, 23, 33, "not detected", 36, 96.2),
    (7, 3, 500, 46, 60, 24, 40, "not detected", 41, 96.0),
    (8, 1.5, 500, 23, 60, 24, 35, "not detected", 39, 95.6),
    (9, 1.5, 1000, 23, 60, 24, 36, "not detected", 39, 95.2),
]
for entry, vol, smass, emass, temp, time, ay, aee, ey, eee in table3:
    evidence = ev(3)
    ps = kinetic_participants("1a", evidence, smass, emass, vol)
    def ee_value(value):
        return "opposite enantiomer not detected by GC" if value == "not detected" else q(value, "%")
    rid = f"table3_entry_{entry}_optimization"
    if entry == 9:
        rid += "_table4_entry_1"
    records.append(rec(
        rid, "optimization_entry", evidence, ps,
        [{"step_id": "kinetic_resolution", "participant_ids": [p["entity_id"] for p in ps], "conditions": [fld("temperature", q(temp, "°C"), evidence), fld("time", q(time, "h"), evidence)]}],
        [fld("alcohol_isolated_yield", q(ay, "%"), evidence, ["alcohol_product"]), fld("alcohol_ee", ee_value(aee), evidence, ["alcohol_product"]),
         fld("acetate_isolated_yield", q(ey, "%"), evidence, ["acetate_product"]), fld("acetate_ee", ee_value(eee), evidence, ["acetate_product"])],
        unresolved=["No explicitly associated supporting information was provided.", "The footnote phrase 'opposite enantiomer was not detected by GC' is retained qualitatively and is not converted to 100% ee.", "Product SMILES are unverified connectivity candidates."],
    ))

# Table 4 entries 2-21; entry 1 is already merged with Table 3 entry 9.  Compound
# units mL g^-1 and mg g^-1 are retained as raw source strings because the current
# controlled unit list does not include compound loading units.
table4 = [
    (2, "1b", 1.5, 23, 20, 30, 82.2, 38, 98.4),
    (3, "1b", 6, 92, 21.5, 31, 99.3, 43, 95.8),
    (4, "1b", 6, 92, 19, 34, 96.3, 41, 97.4),
    (5, "1c", 1.5, 23, 24, 41, 85.0, 40, 98.2),
    (6, "1c", 3, 46, 26, 41, "not detected", 48, 97.7),
    (7, "1d", 1.5, 23, 28, 43, 91.2, 43, 96.8),
    (8, "1d", 3, 46, 30, 41, 99.4, 43, 96.5),
    (9, "1d", 3, 46, 28, 45, "not detected", 51, 99.0),
    (10, "1e", 1.5, 23, 28, 50, 98.7, 50, 98.4),
    (11, "1f", 1.5, 23, 24, 48, 89.7, 31, 99.3),
    (12, "1f", 6, 92, 22, 38, "not detected", 41, 96.7),
    (13, "1h", 3, 46, 21, 35, 90.0, 34, 98.3),
    (14, "1i", 1.5, 23, 49, 60, 28.5, 24, 94.0),
    (15, "1i", 3, 46, 44.5, 52, 73.6, 36, 97.9),
    (16, "1i", 6, 92, 41, 54, 96.4, 41, 97.3),
    (17, "1j", 1.5, 23, 26, 58, 49.4, 30, 98.0),
    (18, "1j", 6, 92, 27, 44, 74.7, 38, 97.7),
    (19, "1k", 1.5, 23, 43, 39, 98.5, 45, 99.1),
    (20, "1l", 1.5, 23, 28, 31, 70.7, 40, 99.3),
    (21, "1l", 6, 92, 43, 48, 66.0, 38, 97.0),
]
for entry, label, conc, loading, time, ay, aee, ey, eee in table4:
    evidence = ev(3)
    ps = kinetic_participants(label, evidence, 1000, 0, 0)
    ps[1]["amounts"] = []
    ps[2]["amounts"] = [fld("loading", f"{loading} mg g^-1 substrate", evidence)]
    aee_value = "opposite enantiomer not detected by GC" if aee == "not detected" else q(aee, "%")
    records.append(rec(
        f"table4_entry_{entry}_loading_scope", "optimization_entry", evidence, ps,
        [{"step_id": "kinetic_resolution", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
            fld("temperature", q(60, "°C"), evidence), fld("time", q(time, "h"), evidence),
            fld("substrate_concentration", f"{conc} mL g^-1 (vinyl acetate volume per substrate mass)", evidence),
        ]}],
        [fld("alcohol_isolated_yield", q(ay, "%"), evidence, ["alcohol_product"]), fld("alcohol_ee", aee_value, evidence, ["alcohol_product"]),
         fld("acetate_isolated_yield", q(ey, "%"), evidence, ["acetate_product"]), fld("acetate_ee", q(eee, "%"), evidence, ["acetate_product"])],
        notes=["The prose describes Table 4 as typical results on a 1.0 g scale."],
        unresolved=["No explicitly associated supporting information was provided.", "Compound loading units mL g^-1 and mg g^-1 are preserved as raw source expressions rather than converted to unsupported units.", "The footnote 'opposite enantiomer was not detected by GC' is qualitative where applicable.", "Product SMILES are unverified connectivity candidates."],
    ))


# Scheme 2 transformations are merged with the full procedures on page 6.
evidence = ev(3, 6)
ps = [
    part("allenol", "reactant", "(S)-1a", "(S)-(-)-3-(n-butyl)penta-3,4-dien-2-ol", evidence, allenol_smiles["1a"], [fld("mass", q(140, "mg"), evidence), fld("amount", q(1, "mmol"), evidence), fld("ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, evidence)]),
    part("agno3", "catalyst", "AgNO3", "silver nitrate", evidence, "[Ag+].[O-]N(=O)=O", [fld("mass", q(170, "mg"), evidence), fld("amount", q(1, "mmol"), evidence)]),
    part("acetone", "solvent", "acetone", "acetone", evidence, "CC(C)=O"),
    part("water", "solvent", "water", "water", evidence, "O"),
    part("product", "product", "(S)-3a", "3-butyl-2-methyl-2,5-dihydrofuran", evidence, None, [fld("isolated_mass", q(84, "mg"), evidence)]),
]
records.append(rec(
    "agno3_cycloisomerization_1a_to_3a", "reported_experiment", evidence, ps,
    [{"step_id": "cycloisomerization_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
        fld("solvent", "acetone/water 1:1, total 2 mL", evidence), fld("atmosphere", "nitrogen", evidence),
        fld("temperature", "reflux", evidence), fld("time", q(8, "h"), evidence),
        fld("workup", "quenched with brine (10 mL); extracted with diethyl ether (3 x 20 mL); extracts washed twice with brine and dried over Na2SO4", evidence),
        fld("purification", "flash chromatography on silica gel, petroleum ether/diethyl ether 100:1", evidence),
    ]}],
    [fld("isolated_yield", q(60, "%"), evidence, ["product"]), fld("product_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, evidence, ["product"]), fld("yield_measurement_basis", "isolated after flash chromatography", evidence, ["product"])],
    unresolved=["No explicitly associated supporting information was provided.", "The page-6 heading calls the product (R)-3-butyl-2-methyl-2,5-dihydrofuran while the compound label is (S)-3a; this source inconsistency is not resolved.", "The product structure and stereochemistry are left without SMILES pending source-aware structure review."],
))

evidence = ev(3, 6)
ps = [
    part("allenol", "reactant", "(S)-1a", "(S)-(-)-3-(n-butyl)penta-3,4-dien-2-ol", evidence, allenol_smiles["1a"], [fld("mass", q(140, "mg"), evidence), fld("amount", q(1, "mmol"), evidence), fld("ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, evidence)]),
    part("allyl_bromide", "reactant", "allyl bromide", "allyl bromide", evidence, "C=CCBr", [fld("amount", q(5, "mmol"), evidence)]),
    part("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", evidence, "Cl[Pd]Cl", [fld("mass", q(8.9, "mg"), evidence), fld("amount", q(0.05, "mmol"), evidence)]),
    part("dma", "solvent", "DMA", "N,N-dimethylacetamide", evidence, "CC(=O)N(C)C", [fld("volume", q(6, "mL"), evidence)]),
    part("product", "product", "(S)-4a", "(S)-4-allyl-3-butyl-2-methyl-2,5-dihydrofuran", evidence, None, [fld("isolated_mass", q(122, "mg"), evidence)]),
]
records.append(rec(
    "pdii_coupling_cyclization_1a_allyl_bromide", "reported_experiment", evidence, ps,
    [{"step_id": "coupling_cyclization_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
        fld("temperature", "room temperature", evidence), fld("time", "until complete by TLC", evidence),
        fld("workup", "diethyl ether added; mixture washed with brine three times and dried over anhydrous Na2SO4", evidence),
        fld("purification", "column chromatography on silica gel, petroleum ether/diethyl ether 100:1", evidence),
    ]}],
    [fld("isolated_yield", q(68, "%"), evidence, ["product"]), fld("product_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, evidence, ["product"]), fld("yield_measurement_basis", "isolated after column chromatography", evidence, ["product"])],
    unresolved=["No explicitly associated supporting information was provided.", "The reaction time is qualitative ('until complete by TLC').", "The product structure and stereochemistry are left without SMILES pending source-aware structure review."],
))

evidence = ev(3, 6)
ps = [
    part("allenol", "reactant", "(S)-1a", "(S)-(-)-3-(n-butyl)penta-3,4-dien-2-ol", evidence, allenol_smiles["1a"], [fld("mass", q(140, "mg"), evidence), fld("amount", q(1, "mmol"), evidence), fld("ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, evidence)]),
    part("iodobenzene", "reactant", "PhI", "iodobenzene", evidence, "Ic1ccccc1", [fld("mass", q(216, "mg"), evidence), fld("amount", q(1.06, "mmol"), evidence)]),
    part("pdp4", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", evidence, None, [fld("mass", q(58, "mg"), evidence), fld("amount", q(0.05, "mmol"), evidence)]),
    part("k2co3", "reagent", "K2CO3", "potassium carbonate", evidence, "[K+].[K+].[O-]C([O-])=O", [fld("mass", q(552, "mg"), evidence), fld("amount", q(4.01, "mmol"), evidence)]),
    part("dmf", "solvent", "DMF", "N,N-dimethylformamide", evidence, "CN(C)C=O", [fld("volume", q(4, "mL"), evidence)]),
    part("product", "product", "(S,S)-5a", "(S,S)-2-butyl-3-methyl-2-(1-phenylvinyl)oxirane", evidence, None, [fld("isolated_mass", q(127, "mg"), evidence)]),
]
records.append(rec(
    "pd0_coupling_cyclization_1a_iodobenzene", "reported_experiment", evidence, ps,
    [{"step_id": "coupling_cyclization_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
        fld("atmosphere", "argon", evidence), fld("temperature", {"minimum": 75, "maximum": 80, "unit": "°C", "raw_text": "75-80 °C"}, evidence), fld("time", q(18, "h"), evidence),
        fld("workup", "quenched with brine (10 mL); extracted with diethyl ether (3 x 20 mL); extracts washed twice with brine and dried over Na2SO4", evidence),
        fld("purification", "flash chromatography on silica gel, petroleum ether/diethyl ether 200:1", evidence),
    ]}],
    [fld("isolated_yield", q(59, "%"), evidence, ["product"]), fld("product_ee", q(99.4, "%"), evidence, ["product"]), fld("diastereomeric_ratio", "35:1", evidence, ["product"]), fld("yield_measurement_basis", "isolated after flash chromatography", evidence, ["product"])],
    unresolved=["No explicitly associated supporting information was provided.", "The product structure and stereochemistry are left without SMILES pending source-aware structure review."],
))

assert len(records) == 63, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
