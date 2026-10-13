#!/usr/bin/env python3
"""Build machine-derived reaction records for doc_a874ba53f4d2d306, PDF pages 1-5."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model"
DOC = "doc_a874ba53f4d2d306"


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return out


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def step(step_id, ids, conditions):
    return {"step_id": step_id, "participant_ids": ids, "conditions": conditions}


def record(rid, kind, evidence, participants, steps, outcomes, unresolved, notes=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


phenyl_sulfone = "S(=O)(=O)c1ccccc1"
substrate_smiles = {
    "1a": f"CC=C=C{phenyl_sulfone}",
    "1b": f"CCC=C=C{phenyl_sulfone}",
    "1c": f"CCCC=C=C{phenyl_sulfone}",
    "1d": f"CCCCC=C=C{phenyl_sulfone}",
    "1e": f"CCCCCC=C=C{phenyl_sulfone}",
    "1f": f"CCCCCCC=C=C{phenyl_sulfone}",
    "1g": f"c1ccccc1CC=C=C{phenyl_sulfone}",
}
product_names = {
    "2a": "3-bromo-4-(phenylsulfonyl)but-3(E)-en-2-ol",
    "2b": "2-bromo-1-(phenylsulfonyl)pent-1(E)-en-3-ol",
    "2c": "2-bromo-1-(phenylsulfonyl)hex-1(E)-en-3-ol",
    "2d": "2-bromo-1-(phenylsulfonyl)hept-1(E)-en-3-ol",
    "2e": "2-bromo-1-(phenylsulfonyl)oct-1(E)-en-3-ol",
    "2f": "2-bromo-1-(phenylsulfonyl)non-1(E)-en-3-ol",
    "2g": "3-bromo-1-phenyl-4-(phenylsulfonyl)but-3(E)-en-2-ol",
}
product_smiles = {
    "2a": f"CC(O)C(Br)=C{phenyl_sulfone}",
    "2b": f"CCC(O)C(Br)=C{phenyl_sulfone}",
    "2c": f"CCCC(O)C(Br)=C{phenyl_sulfone}",
    "2d": f"CCCCC(O)C(Br)=C{phenyl_sulfone}",
    "2e": f"CCCCCC(O)C(Br)=C{phenyl_sulfone}",
    "2f": f"CCCCCCC(O)C(Br)=C{phenyl_sulfone}",
    "2g": f"c1ccccc1CC(O)C(Br)=C{phenyl_sulfone}",
}

# Table 1 rows. Entry 7 is a distinct solvent/water condition for the same substrate/product.
table1 = [
    dict(rid="table1_entry1_1a_2a", sub="1a", prod="2a", smg=58.5, smmol=0.3,
         brvol=0.72, brmmol=0.36, breq=1.2, temp={"number": 0, "unit": "°C"},
         pmg=73.9, y=85, pages=(2, 3), typical=True),
    dict(rid="table1_entry2_1b_2b", sub="1b", prod="2b", smg=62.4, smmol=0.3,
         brvol=0.72, brmmol=0.36, breq=1.2, temp="r.t.", pmg=62.0, y=68, pages=(2, 3)),
    dict(rid="table1_entry3_1c_2c", sub="1c", prod="2c", smg=66.3, smmol=0.3,
         brvol=1.2, brmmol=0.6, breq=2.0, temp="r.t.", pmg=57.2, y=60, pages=(2, 3, 5)),
    dict(rid="table1_entry4_1d_2d", sub="1d", prod="2d", smg=71.5, smmol=0.3,
         brvol=1.2, brmmol=0.6, breq=2.0, temp="r.t.", pmg=62.8, y=63, pages=(2, 3)),
    dict(rid="table1_entry5_1e_2e", sub="1e", prod="2e", smg=73.8, smmol=0.3,
         brvol=0.72, brmmol=0.36, breq=1.2, temp="r.t.", pmg=64.0, y=63, pages=(2, 3)),
    dict(rid="table1_entry6_1f_2f", sub="1f", prod="2f", smg=79.3, smmol=0.3,
         brvol=1.2, brmmol=0.6, breq=1.5, temp="r.t.", pmg=62.6, y=58, pages=(2, 3),
         conflict="Table 1 reports 1.5 equiv Br2, while the experimental paragraph reports 0.6 mmol Br2 for 0.3 mmol 1f."),
    dict(rid="table1_entry7_1f_2f_mecnetoh", sub="1f", prod="2f", smg=80.0, smmol=0.3,
         brvol=1.2, brmmol=0.6, breq=1.5, temp="r.t.", pmg=58.5, y=53, pages=(2, 3),
         alt=True, conflict="Table 1 reports 1.5 equiv Br2, while the experimental paragraph reports 0.6 mmol Br2 for 0.3 mmol 1f."),
    dict(rid="table1_entry8_1g_2g", sub="1g", prod="2g", smg=80.8, smmol=0.3,
         brvol=1.2, brmmol=0.6, breq=2.0, temp="r.t.", pmg=77.5, y=71, pages=(2, 3)),
]

records = []
for row in table1:
    evidence = ev(*row["pages"])
    sub_id, prod_id = row["sub"], row["prod"]
    parts = [
        participant(sub_id, "reactant", sub_id, evidence,
                    name=f"1,2-allenyl phenyl sulfone {sub_id}", smiles=substrate_smiles[sub_id],
                    amounts=[qty("mass", {"number": row["smg"], "unit": "mg"}, evidence),
                             qty("amount", {"number": row["smmol"], "unit": "mmol"}, evidence)]),
        participant("br2", "reagent", "Br2", evidence, name="bromine", smiles="BrBr",
                    amounts=[qty("solution_volume", {"number": row["brvol"], "unit": "mL"}, evidence),
                             qty("concentration", {"number": 0.5, "unit": "M"}, evidence),
                             qty("amount", {"number": row["brmmol"], "unit": "mmol"}, evidence),
                             qty("table_equivalents", {"number": row["breq"], "unit": "equiv"}, ev(2))]),
        participant("mecn", "solvent", "MeCN", evidence, name="acetonitrile", smiles="CC#N",
                    amounts=[qty("volume", {"number": 3.3, "unit": "mL"}, evidence)] if row.get("typical") else []),
        participant("water", "reagent", "H2O", evidence, name="water", smiles="O",
                    amounts=[qty("treatment_volume", {"number": 6, "unit": "mL"}, evidence)] if row.get("typical") or row.get("alt") else []),
        participant(prod_id, "product", prod_id, evidence, name=product_names[prod_id],
                    smiles=product_smiles[prod_id], amounts=[]),
    ]
    if row.get("alt"):
        parts.insert(3, participant("etoh", "solvent", "EtOH", evidence, name="ethanol", smiles="CCO",
                                    amounts=[qty("volume", {"number": 0.1, "unit": "mL"}, evidence)]))
        parts[4]["amounts"] = [qty("initial_volume", {"number": 5.4, "unit": "uL"}, evidence),
                               qty("initial_mass", {"number": 5.4, "unit": "mg"}, evidence),
                               qty("initial_amount", {"number": 0.3, "unit": "mmol"}, evidence),
                               qty("initial_equivalents", {"number": 1.0, "unit": "equiv"}, evidence),
                               qty("treatment_volume", {"number": 6, "unit": "mL"}, evidence)]
        parts[2]["amounts"] = [qty("volume", {"number": 2.8, "unit": "mL"}, evidence)]
    ids = [p["entity_id"] for p in parts]
    conditions1 = [qty("temperature", row["temp"], evidence), qty("time", {"number": 0.5, "unit": "h"}, ev(2, 3))]
    if row.get("alt"):
        conditions1.append(qty("operation", "Water and ethanol were present before Br2 addition.", evidence))
    conditions2 = [qty("time", {"number": 0.5, "unit": "h"}, ev(2, 3)), qty("temperature", row["temp"], ev(2, 3))]
    if row.get("typical") or row.get("alt"):
        conditions2.extend([
            qty("workup", "extract with diethyl ether; wash with brine; dry over anhydrous Na2SO4; evaporate", evidence),
            qty("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 5:1", evidence),
        ])
    unresolved = [
        "Candidate substrate/product SMILES encode constitution only; the depicted alkene stereochemistry remains unverified.",
        "No supporting-information file was supplied or explicitly associated.",
    ]
    if not (row.get("typical") or row.get("alt")):
        unresolved.append("The abbreviated paragraph does not restate workup, purification, atmosphere, or yield measurement basis.")
    if row.get("conflict"):
        unresolved.append(row["conflict"])
    outcomes = [
        qty("reported_yield", {"number": row["y"], "unit": "%"}, evidence, [prod_id]),
        qty("product_mass", {"number": row["pmg"], "unit": "mg"}, evidence, [prod_id]),
        qty("product_geometry", "E", evidence, [prod_id]),
    ]
    if row.get("typical") or row.get("alt"):
        outcomes.append(qty("yield_measurement_basis", "isolated after chromatography", evidence, [prod_id]))
    records.append(record(row["rid"], "substrate_scope_entry", evidence, parts,
                          [step("bromination", ids, conditions1), step("water_treatment", ids, conditions2)],
                          outcomes, unresolved))

# Direct 1h -> 2h bromohydroxylation: Scheme/prose and experimental section disagree on yield.
e = ev(1, 2, 4)
parts = [
    participant("1h", "reactant", "1h", e, name="1,2-butadienyl p-bromophenyl sulfone",
                smiles="CC=C=CS(=O)(=O)c1ccc(Br)cc1",
                amounts=[qty("mass", {"number": 54.1, "unit": "mg"}, ev(4)), qty("amount", {"number": 0.2, "unit": "mmol"}, ev(4))]),
    participant("br2", "reagent", "Br2", e, name="bromine", smiles="BrBr",
                amounts=[qty("solution_volume", {"number": 0.48, "unit": "mL"}, ev(4)), qty("concentration", {"number": 0.5, "unit": "M"}, ev(4)), qty("amount", {"number": 0.24, "unit": "mmol"}, ev(4)), qty("equivalents", {"number": 1.2, "unit": "equiv"}, ev(1, 2))]),
    participant("mecn", "solvent", "MeCN", e, name="acetonitrile", smiles="CC#N"),
    participant("water", "reagent", "H2O", e, name="water", smiles="O"),
    participant("2h", "product", "2h", e, name="3-bromo-4-(4'-bromophenylsulfonyl)but-3(E)-en-2-ol",
                smiles="CC(O)C(Br)=CS(=O)(=O)c1ccc(Br)cc1"),
]
records.append(record(
    "scheme1_direct_1h_to_2h", "reported_experiment", e, parts,
    [step("bromohydroxylation", [p["entity_id"] for p in parts],
          [qty("temperature", {"number": 0, "unit": "°C"}, e), qty("time", {"number": 0.5, "unit": "h"}, ev(2)), qty("operation", "Br2 treatment in MeCN followed by H2O", e)])],
    [qty("scheme_reported_yield", {"number": 85, "unit": "%"}, ev(1, 2), ["2h"]),
     qty("experimental_section_yield", {"number": 73, "unit": "%"}, ev(4), ["2h"]),
     qty("product_mass", {"number": 53.4, "unit": "mg"}, ev(4), ["2h"]),
     qty("product_geometry", "E", e, ["2h"])],
    ["The results/discussion and Scheme 1 report 85% yield, whereas section 4.1.9 reports 73%; both are retained.",
     "Workup, purification, atmosphere, and yield measurement basis are not reported for this abbreviated preparation.",
     "Candidate constitutional SMILES does not independently verify the depicted E geometry.",
     "No supporting-information file was supplied or explicitly associated."]
))

# Table 2 substrate scope.
table2 = [
    dict(rid="table2_entry1_1i_4i", sub="1i", prod="4i", subname="3,3-disubstituted 1,2-allenyl phenyl sulfone 1i",
         prodname="E-(2-bromo-3-methylbuta-1,3-dienyl) phenyl sulfone", prodsmiles=f"C=C(C)C(Br)=C{phenyl_sulfone}",
         smg=62.1, smmol=0.3, mecn=2.8, etoh=0.1, water_ul=5.4, water_mg=5.4, water_mmol=0.3,
         brvol=1.2, brmmol=0.6, temp="r.t.", time={"number": 5, "unit": "min"}, pmg=65.3, table_y=76, exp_y=76,
         sel1=">99:1", sel3="table dash (–)", detailed=True),
    dict(rid="table2_entry2_1j_4j", sub="1j", prod="4j", subname="cyclic 3,3-disubstituted 1,2-allenyl phenyl sulfone 1j",
         prodname="E-1-phenylsulfonyl-2-bromo-2-cyclohexenylethene", prodsmiles=f"C1CCCC=C1C(Br)=C{phenyl_sulfone}",
         smg=49.1, smmol=0.2, mecn=None, etoh=0.0675, water_ul=3.6, water_mg=None, water_mmol=0.2,
         brvol=0.8, brmmol=0.4, temp={"number": -40, "unit": "°C"}, time=None, pmg=42.1, table_y=63, exp_y=65,
         sel1=">99:1", sel3=">99:1", detailed=False),
    dict(rid="table2_entry3_1k_4k", sub="1k", prod="4k", subname="3-phenyl-3-methyl-1,2-allenyl phenyl sulfone 1k",
         prodname="1-phenylsulfonyl-2-bromo-3-phenyl-1(E),3(E)-pentadiene", prodsmiles=f"CC=C(c1ccccc1)C(Br)=C{phenyl_sulfone}",
         smg=56.2, smmol=0.2, mecn=1.9, etoh=0.0675, water_ul=3.6, water_mg=3.6, water_mmol=0.2,
         brvol=0.8, brmmol=0.4, temp="r.t.", time=None, pmg=57.2, table_y=80, exp_y=80,
         sel1=">99:1", sel3=">99:1", detailed=True),
]
for row in table2:
    e = ev(2, 4)
    parts = [
        participant(row["sub"], "reactant", row["sub"], e, name=row["subname"],
                    amounts=[qty("mass", {"number": row["smg"], "unit": "mg"}, ev(4)), qty("amount", {"number": row["smmol"], "unit": "mmol"}, ev(4))]),
        participant("br2", "reagent", "Br2", e, name="bromine", smiles="BrBr",
                    amounts=[qty("solution_volume", {"number": row["brvol"], "unit": "mL"}, ev(4)), qty("concentration", {"number": 0.5, "unit": "M"}, ev(4)), qty("amount", {"number": row["brmmol"], "unit": "mmol"}, ev(4)), qty("equivalents", {"number": 2.0, "unit": "equiv"}, ev(2))]),
        participant("mecn", "solvent", "MeCN", e, name="acetonitrile", smiles="CC#N",
                    amounts=[qty("volume", {"number": row["mecn"], "unit": "mL"}, ev(4))] if row["mecn"] else []),
        participant("etoh", "solvent", "EtOH", e, name="ethanol", smiles="CCO",
                    amounts=[qty("volume", {"number": row["etoh"], "unit": "mL"}, ev(4))]),
        participant("water", "reagent", "H2O", e, name="water", smiles="O",
                    amounts=[qty("volume", {"number": row["water_ul"], "unit": "uL"}, ev(4)), qty("amount", {"number": row["water_mmol"], "unit": "mmol"}, ev(4)), qty("equivalents", {"number": 1.0, "unit": "equiv"}, ev(2))] + ([qty("mass", {"number": row["water_mg"], "unit": "mg"}, ev(4))] if row["water_mg"] else [])),
        participant(row["prod"], "product", row["prod"], e, name=row["prodname"], smiles=row["prodsmiles"]),
    ]
    cond = [qty("temperature", row["temp"], e)]
    if row["time"]:
        cond.append(qty("time", row["time"], ev(4)))
    if row["prod"] == "4i":
        cond += [qty("workup", "treat with water; extract with diethyl ether; wash with brine; dry over anhydrous Na2SO4; evaporate", ev(4)), qty("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", ev(4))]
    elif row["prod"] == "4k":
        cond += [qty("operation", "reaction mixture submitted directly to chromatography without workup", ev(4)), qty("purification", "silica-gel chromatography", ev(4))]
    outcomes = [
        qty("table_reported_yield", {"number": row["table_y"], "unit": "%"}, ev(2), [row["prod"]]),
        qty("experimental_section_yield", {"number": row["exp_y"], "unit": "%"}, ev(4), [row["prod"]]),
        qty("product_mass", {"number": row["pmg"], "unit": "mg"}, ev(4), [row["prod"]]),
        qty("C1_C2_E_Z_ratio", row["sel1"], ev(2), [row["prod"]]),
        qty("C3_C4_E_Z_ratio", row["sel3"], ev(2), [row["prod"]]),
    ]
    unresolved = [
        "Starting-material connectivity and product stereochemical SMILES remain unverified against the drawings.",
        "The experimental paragraph does not report atmosphere or yield measurement basis.",
        "No supporting-information file was supplied or explicitly associated.",
    ]
    if row["prod"] == "4j":
        unresolved += ["Table 2 reports 63% yield, whereas section 4.2.2 reports 65%; both are retained.", "Section 4.2.2 does not state reaction time, MeCN volume, workup, or purification."]
    elif row["prod"] == "4k":
        unresolved.append("Section 4.2.3 does not state reaction time.")
    records.append(record(row["rid"], "substrate_scope_entry", e, parts,
                          [step("bromination_elimination", [p["entity_id"] for p in parts], cond)], outcomes, unresolved))

# Isolation of 3h from 1h. Scheme and detailed experimental section differ in yield.
e = ev(1, 2, 4, 5)
parts = [
    participant("1h", "reactant", "1h", e, name="1,2-butadienyl p-bromophenyl sulfone",
                smiles="CC=C=CS(=O)(=O)c1ccc(Br)cc1",
                amounts=[qty("mass", {"number": 546, "unit": "mg"}, ev(4)), qty("amount", {"number": 2.0, "unit": "mmol"}, ev(4))]),
    participant("br2", "reagent", "Br2", e, name="bromine", smiles="BrBr",
                amounts=[qty("solution_volume", {"number": 8.0, "unit": "mL"}, ev(4)), qty("concentration", {"number": 0.5, "unit": "M"}, ev(4)), qty("amount", {"number": 4.0, "unit": "mmol"}, ev(4)), qty("equivalents", {"number": 2.0, "unit": "equiv"}, ev(1, 2))]),
    participant("mecn", "solvent", "anhydrous MeCN", e, name="anhydrous acetonitrile", smiles="CC#N",
                amounts=[qty("substrate_solution_volume", {"number": 4.0, "unit": "mL"}, ev(4))]),
    participant("3h", "product", "3h", e, name="five-membered bromosulfonium tribromide intermediate 3h"),
]
records.append(record(
    "scheme1_isolation_1h_to_3h", "reported_experiment", e, parts,
    [step("intermediate_formation", [p["entity_id"] for p in parts],
          [qty("temperature", "r.t.", ev(4)), qty("operation", "evaporate solvent; collect orange solid by filtration; wash with 3 x 10 mL anhydrous diethyl ether; dry under vacuum", ev(4)), qty("purification", "dissolve in anhydrous MeCN at 40 °C and recrystallize at 0 °C to obtain pure cis-3h", ev(4))])],
    [qty("scheme_reported_yield", {"number": 76, "unit": "%"}, ev(2), ["3h"]),
     qty("experimental_section_yield", {"number": 79, "unit": "%"}, ev(4), ["3h"]),
     qty("product_mass", {"number": 940.7, "unit": "mg"}, ev(4), ["3h"]),
     qty("cis_trans_ratio", "1:1", ev(2, 4), ["3h"])],
    ["Scheme 1 reports 76% yield, whereas section 4.3.1 reports 79%; both are retained.",
     "No isolated mass or yield is given for the recrystallized pure cis isomer.",
     "The ionic five-membered intermediate structure and bromine counterion connectivity are not encoded as SMILES.",
     "Reaction duration is not reported.",
     "No supporting-information file was supplied or explicitly associated."],
    notes=["The structure of cis-3h was established by X-ray diffraction; page 5 gives CCDC 614241 crystal data."]
))

# Hydrolysis of the isolated 3h mixture to 2h.
e = ev(2, 4)
parts = [
    participant("3h", "reactant", "3h", e, name="five-membered intermediate 3h (cis/trans 1:1)",
                amounts=[qty("mass", {"number": 118.6, "unit": "mg"}, ev(4)), qty("amount", {"number": 0.2, "unit": "mmol"}, ev(4))]),
    participant("mecn", "solvent", "MeCN", e, name="acetonitrile", smiles="CC#N",
                amounts=[qty("volume", {"number": 2.7, "unit": "mL"}, ev(4))]),
    participant("water", "reagent", "H2O", e, name="water", smiles="O",
                amounts=[qty("volume", {"number": 4.0, "unit": "mL"}, ev(4))]),
    participant("2h", "product", "2h", e, name="3-bromo-4-(4'-bromophenylsulfonyl)but-3(E)-en-2-ol",
                smiles="CC(O)C(Br)=CS(=O)(=O)c1ccc(Br)cc1"),
]
records.append(record(
    "scheme1_hydrolysis_3h_to_2h", "reported_experiment", e, parts,
    [step("hydrolysis", [p["entity_id"] for p in parts],
          [qty("temperature", {"number": 0, "unit": "°C"}, e), qty("time", {"number": 0.5, "unit": "h"}, e), qty("operation", "monitor by TLC", ev(4)), qty("workup", "extract with diethyl ether; wash with brine; dry over anhydrous Na2SO4; evaporate", ev(4)), qty("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 4:1", ev(4))])],
    [qty("isolated_yield", {"number": 63, "unit": "%"}, e, ["2h"]), qty("product_mass", {"number": 46.3, "unit": "mg"}, ev(4), ["2h"]), qty("product_geometry", "E", e, ["2h"]), qty("yield_measurement_basis", "isolated after chromatography", ev(4), ["2h"])],
    ["Reaction atmosphere is not reported.", "Candidate product constitutional SMILES does not independently verify E geometry.", "No supporting-information file was supplied or explicitly associated."]
))

assert len(records) == 14

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, introduction, and lower-right Results and discussion", "finding": "Abstract and introduction give high-level bromohydroxylation/bromination-elimination claims. The lower-right prose reports the 1h to 2h reaction at 85% and the 2-equiv Br2 isolation of 3h; these were linked to detailed cross-page records rather than duplicated.", "evidence_ids": ev(1)},
            ],
            "record_ids": [f"{DOC}:scheme1_direct_1h_to_2h", f"{DOC}:scheme1_isolation_1h_to_3h"],
            "unresolved": ["Page 1 does not provide complete procedures for either reaction.", "Background cited chemistry was not converted into present-paper experiments."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1", "finding": "Eight distinct bromohydroxylation conditions were extracted row by row, including the 0 °C footnote and the MeCN/EtOH plus 1-equiv-water override.", "evidence_ids": ev(2)},
                {"region": "upper-right Scheme 1", "finding": "Three executed transformations were distinguished: direct 1h to 2h, isolation of 3h, and hydrolysis of 3h to 2h. Scheme yields were preserved alongside conflicting detailed-section yields.", "evidence_ids": ev(2)},
                {"region": "center-left Figures 1 and 2", "finding": "ORTEP structures of 2c and cis-3h were linked as characterization evidence, not counted as additional reactions.", "evidence_ids": ev(2)},
                {"region": "center-right Table 2", "finding": "All three 3,3-disubstituted-allene bromination-elimination rows were extracted independently with selectivity values and the -40 °C row footnote.", "evidence_ids": ev(2)},
            ],
            "record_ids": [r["record_id"] for r in records],
            "unresolved": ["Table 1 and section 4.1 disagree on Br2 loading for both 1f entries.", "The Table 2 entry-2 yield conflicts with the experimental paragraph.", "Complex structures and stereochemistry remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "Experimental sections 4.1.1-4.1.8", "finding": "Exact substrate and Br2 quantities, product masses, and yields for Table 1 entries 1-8 were merged into the corresponding table rows; full workup/purification was retained only where explicitly printed.", "evidence_ids": ev(3)},
            ],
            "record_ids": [f"{DOC}:{row['rid']}" for row in table1],
            "unresolved": ["Abbreviated compound paragraphs generally omit atmosphere, workup, purification, and yield basis.", "The 2g paragraph continues analytically onto page 4, but its reaction quantities and yield are complete on page 3."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "Sections 4.1.9 and 4.2.1-4.2.3", "finding": "The 1h to 2h experiment and all three Table 2 preparations were captured with printed quantities, conditions, masses, yields, workup/purification where stated, and source conflicts.", "evidence_ids": ev(4)},
                {"region": "Sections 4.3.1-4.3.2", "finding": "Isolation/recrystallization of 3h and its separate water reaction to 2h were extracted as two distinct experiments.", "evidence_ids": ev(4)},
                {"region": "Supplementary data statement", "finding": "The paper states that supplementary data are online, but no SI file was supplied or explicitly associated; no SI-derived facts were inferred.", "evidence_ids": ev(4)},
            ],
            "record_ids": [f"{DOC}:scheme1_direct_1h_to_2h", f"{DOC}:table2_entry1_1i_4i", f"{DOC}:table2_entry2_1j_4j", f"{DOC}:table2_entry3_1k_4k", f"{DOC}:scheme1_isolation_1h_to_3h", f"{DOC}:scheme1_hydrolysis_3h_to_2h"],
            "unresolved": ["Several reaction times and atmospheres are not reported.", "Scheme and experimental-section yields conflict for 2h, 3h, and 4j."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "references and notes 1-18", "finding": "No new present-paper experiment appears. References were treated as citations; crystal data for 2c and cis-3h were linked to their existing records as characterization context.", "evidence_ids": ev(5)},
            ],
            "record_ids": [f"{DOC}:table1_entry3_1c_2c", f"{DOC}:scheme1_isolation_1h_to_3h"],
            "unresolved": ["Cited publications and deposited CCDC files were not supplied as associated sources and were not mined for experimental facts."],
        },
    ],
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0005.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
(ROOT / "runs/current/coverage").mkdir(parents=True, exist_ok=True)
(ROOT / "runs/current/coverage/pages_0001_0005.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{i}:text" for i in range(1, 6)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
