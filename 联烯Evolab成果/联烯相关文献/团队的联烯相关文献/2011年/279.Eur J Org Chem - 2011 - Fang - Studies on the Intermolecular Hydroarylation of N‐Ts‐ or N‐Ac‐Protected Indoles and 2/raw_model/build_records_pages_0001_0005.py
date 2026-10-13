#!/usr/bin/env python3
"""Build source-linked machine records for Fang, Fu, and Ma, EJOC 2011, PDF pages 1-5."""

import json
from pathlib import Path


DOC = "doc_3381a7d0616fcb9c"
OUT = Path(__file__).with_name("records_pages_0001_0005.json")


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, target=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = list(target)
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants=None, steps=None, outcomes=None, notes=None, unresolved=None, source_id=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id or rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(v, evidence) for v in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def missing_conditions():
    return [
        fld("atmosphere", None, []),
        fld("workup", None, []),
        fld("purification", None, []),
    ]


SMILES = {
    "1a": "Cc1ccc(S(=O)(=O)n2ccc3ccccc32)cc1",
    "1b": "CC(=O)n1ccc2ccccc21",
    "2h": "CCOC(=O)C(C)=C=Cc1ccccc1",
    "TFA": "O=C(O)C(F)(F)F",
    "CH2Cl2": "ClCCl",
    "CH3NO2": "C[N+](=O)[O-]",
    "CH3CN": "CC#N",
    "DMA": "CC(=O)N(C)C",
    "CH2Br2": "BrCBr",
}


records = []


# Page 1: four prior-literature arrows, kept distinct from the current paper's experiments.
p1 = [ev(1), ev(1, "text")]
records.append(record(
    "scheme1_literature_hydroarylation", "literature_example", p1,
    participants=[
        participant("lit_s1_arene", "reactant", "1,3,5-trimethoxybenzene", p1, smiles="COc1cc(OC)cc(OC)c1"),
        participant("lit_s1_allene", "reactant", "3-methylbuta-1,2-diene", p1, smiles="C=C=C(C)C"),
        participant("lit_s1_product", "product", "Scheme 1 hydroarylation product", p1),
        participant("lit_s1_au", "catalyst", "(4-ClC6H4O)3PAuCl", p1, amounts=[fld("catalyst_loading", {"number": 5, "unit": "mol%"}, p1)]),
        participant("lit_s1_agbf4", "catalyst", "AgBF4", p1, amounts=[fld("catalyst_loading", {"number": 5, "unit": "mol%"}, p1)]),
        participant("lit_s1_dcm", "solvent", "CH2Cl2", p1, smiles=SMILES["CH2Cl2"]),
    ],
    steps=[{"step_id": "hydroarylation", "participant_ids": ["lit_s1_arene", "lit_s1_allene", "lit_s1_au", "lit_s1_agbf4", "lit_s1_dcm"], "conditions": [fld("temperature", "r.t.", p1), fld("time", {"number": 2, "unit": "h"}, p1)] + missing_conditions()}],
    outcomes=[fld("reported_yield", {"number": 67, "unit": "%"}, p1, ["lit_s1_product"])],
    notes=["Scheme 1 is explicitly discussed as Gagné's prior gold(I)-catalyzed intermolecular hydroarylation, not as a new experiment of this paper."],
    unresolved=["Substrate and product stereochemical details were not encoded from the drawing; no scale, atmosphere, workup, or purification is stated."],
    source_id="Scheme 1 (prior literature)",
))

for rid, title, intramolecular in [
    ("scheme2_intramolecular_iodoarylation", "Scheme 2 upper intramolecular iodoarylation", True),
    ("scheme2_intermolecular_iodoarylation", "Scheme 2 lower intermolecular iodoarylation", False),
]:
    ps = [
        participant(f"{rid}_substrate", "reactant", "generic allene substrate with R groups" if not intramolecular else "generic tethered aryl-allene substrate", p1),
        participant(f"{rid}_product", "product", "generic iodoarylation product", p1),
        participant(f"{rid}_ipy", "reagent", "IPy2BF4", p1, amounts=[fld("equivalents", {"number": 1, "unit": "equiv"}, p1)] if intramolecular else []),
        participant(f"{rid}_hbf4", "reagent", "HBF4", p1, amounts=[fld("equivalents", {"number": 1, "unit": "equiv"}, p1)] if intramolecular else []),
        participant(f"{rid}_dcm", "solvent", "CH2Cl2", p1, smiles=SMILES["CH2Cl2"]),
    ]
    if not intramolecular:
        ps.insert(1, participant(f"{rid}_arh", "reactant", "Ar-H", p1))
    cond = [fld("temperature", {"number": -90, "unit": "°C"}, p1)] if intramolecular else []
    cond += [fld("time", None, [])] + missing_conditions()
    records.append(record(
        rid, "literature_example", p1, participants=ps,
        steps=[{"step_id": "iodoarylation", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": cond}],
        notes=[f"{title}; cited as Barluenga's prior work and represented with generic R/Ar groups."],
        unresolved=["Generic R/Ar structures, reaction time, yield, atmosphere, workup, and purification are not specified in the displayed scheme."],
        source_id=title,
    ))

records.append(record(
    "scheme3_literature_pd_hydroarylation", "literature_example", p1,
    participants=[
        participant("lit_s3_arene", "reactant", "1,3,5-trimethoxybenzene", p1, smiles="COc1cc(OC)cc(OC)c1"),
        participant("lit_s3_allenoate", "reactant", "generic ethyl 2-substituted 4-phenylbuta-2,3-dienoate", p1),
        participant("lit_s3_product", "product", "generic Pd-catalyzed hydroarylation product", p1),
        participant("lit_s3_pd", "catalyst", "PdCl2(MeCN)2", p1, amounts=[fld("catalyst_loading", {"number": 5, "unit": "mol%"}, p1)]),
        participant("lit_s3_dma", "solvent", "DMA", p1, smiles=SMILES["DMA"]),
        participant("lit_s3_tfa", "reagent", "TFA", p1, smiles=SMILES["TFA"]),
    ],
    steps=[{"step_id": "hydroarylation", "participant_ids": ["lit_s3_arene", "lit_s3_allenoate", "lit_s3_pd", "lit_s3_dma", "lit_s3_tfa"], "conditions": [fld("solvent_ratio", "DMA/TFA = 1:4", p1), fld("temperature", {"number": 40, "unit": "°C"}, p1), fld("time", {"number": 15, "unit": "h"}, p1)] + missing_conditions()}],
    notes=["Scheme 3 is the authors' previously reported Pd-catalyzed hydroarylation and is not a new experiment in this paper."],
    unresolved=["The scheme uses generic R and does not state reaction scale, yield, atmosphere, workup, or purification."],
    source_id="Scheme 3 (prior literature)",
))


def table1_record(entry, solvent, additive, temp, time_h, nmr_yield, ratio, isolated=None, recovery=None, extra_evidence=None, extra_notes=None):
    evidence = [ev(2), ev(2, "text")] + (extra_evidence or [])
    major = "Z3h" if int(ratio.split(":")[0]) >= int(ratio.split(":")[1]) else "E3h"
    ps = [
        participant("1a", "reactant", "1a", evidence, "N-tosylindole", SMILES["1a"], [fld("amount", {"number": 0.3, "unit": "mmol"}, evidence)]),
        participant("2h", "reactant", "2h", evidence, "ethyl 2-methyl-4-phenylbuta-2,3-dienoate", SMILES["2h"], [fld("equivalents", {"number": 1.2, "unit": "equiv"}, evidence)]),
        participant("Z3h", "product", "(Z)-3h", evidence),
        participant("E3h", "product", "(E)-3h", evidence),
        participant("TFA", "reagent", "TFA", evidence, "trifluoroacetic acid", SMILES["TFA"], [fld("volume", {"number": 1.2 if solvent != "TFA" else 1.5, "unit": "mL"}, evidence)]),
    ]
    if solvent != "TFA":
        ps.append(participant("cosolvent", "solvent", solvent, evidence, smiles=SMILES.get(solvent), amounts=[fld("volume", {"number": 0.3, "unit": "mL"}, evidence)]))
    if additive != "–":
        ps.append(participant("additive", "catalyst", additive, evidence))
    participant_ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    outcomes = [
        fld("main_product_nmr_yield", {"number": nmr_yield, "unit": "%"}, evidence, [major]),
        fld("Z/E_selectivity", {"ratio": ratio, "order": "Z/E"}, evidence),
        fld("nmr_yield_and_selectivity_measurement_basis", "1H NMR spectroscopy with CH2Br2 as internal standard", evidence),
    ]
    if entry == 1:
        outcomes.append(fld("E_isomer_nmr_yield", {"number": 9, "unit": "%"}, evidence, ["E3h"]))
    if isolated is not None:
        outcomes += [fld("isolated_yield", {"number": isolated, "unit": "%"}, evidence, [major]), fld("isolated_yield_measurement_basis", "isolated yield reported parenthetically", evidence)]
    if recovery is not None:
        outcomes.append(fld("recovered_starting_material_yield", {"number": recovery, "unit": "%"}, evidence, ["1a"]))
    notes = [f"Table 1 entry {entry}; the table reports yield of the main isomer and Z/E selectivity."] + (extra_notes or [])
    unresolved = ["Catalyst/additive loading is not stated." if additive != "–" else "No catalyst/additive was used (table dash).", "Atmosphere, workup, and purification are not stated in the main-text table; SI was not associated.", "Product structures are retained by source labels; candidate product SMILES were not encoded because alkene stereochemistry requires source-level review."]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence, participants=ps,
        steps=[{"step_id": "TFA_promoted_hydroarylation", "participant_ids": participant_ids, "conditions": [fld("temperature", {"number": temp, "unit": "°C"}, evidence), fld("time", {"number": time_h, "unit": "h"}, evidence), fld("solvent", solvent if solvent == "TFA" else f"{solvent}/TFA", evidence)] + missing_conditions()}],
        outcomes=outcomes, notes=notes, unresolved=unresolved,
        source_id=f"Table 1 entry {entry}" + (" / Table 2 entry 8" if entry == 9 else " / Table 3 entry 5" if entry == 11 else ""),
    ))


table1_record(1, "CH3NO2", "–", 40, 8.5, 47, "84:16", 44)
table1_record(2, "CH3CN", "–", 40, 10, 59, "91:9")
table1_record(3, "DMA", "–", 40, 48, 38, "90:10", recovery=31)
table1_record(4, "CH2Cl2", "–", 40, 2.5, 69, "92:8")
table1_record(5, "TFA", "–", 40, 2.5, 69, "92:8", 66)
table1_record(6, "TFA", "Pd(OAc)2", 40, 6, 52, "90:10", recovery=9)
table1_record(7, "TFA", "PdCl2(MeCN)2", 40, 6, 59, "95:5", recovery=9)
table1_record(8, "TFA", "PdCl2(PPh3)3", 40, 6, 61, "90:10", recovery=3)
table1_record(9, "TFA", "–", 10, 13, 64, "94:6", 64, extra_notes=["The same condition/result is repeated as Table 2 entry 8 and is represented once."])
table1_record(10, "TFA", "–", 60, 24, 47, "13:87", 51)
table1_record(11, "TFA", "–", 80, 11, 54, "4:96", 58, recovery=5, extra_evidence=[ev(3), ev(3, "text")], extra_notes=["The same experiment is repeated as Table 3 entry 5; Table 3 adds 5% recovery of 1a."])


table2_rows = [
    (1, "1a", "2a", "4-FC6H4", "Me", 28, 12, "89:11", 71, "(Z)-3a", 1.2, None),
    (2, "1a", "2b", "4-ClC6H4", "Me", 20, 12, "94:6", 62, "(Z)-3b", 1.2, None),
    (3, "1a", "2c", "3-ClC6H4", "Me", 60, 12, "86:14", 48, "(Z)-3c", 1.2, None),
    (4, "1a", "2d", "4-BrC6H4", "Me", 40, 15, "96:4", 58, "(Z)-3d", 1.2, None),
    (5, "1a", "2e", "4-MeOC6H4", "Me", 5, 0.5, "81:19", 68, "(Z)-3e", 1.5, None),
    (6, "1a", "2f", "4-MeC6H4", "Me", -10, 5.5, "91:9", 73, "(Z)-3f", 1.5, None),
    (7, "1a", "2g", "alpha-naphthyl", "Me", 5, 2.5, "95:5", 78, "(Z)-3g", 1.5, "CCDC-800855; crystal data on page 5 support the Z assignment"),
    # Entry 8 is the same experiment as Table 1 entry 9 and is not duplicated here.
    (9, "1a", "2h", "C6H5", "Me", 10, 22, "95:5", 70, "(Z)-3h", None, "large-scale: 1a 4 mmol and 2h 4.8 mmol"),
    (10, "1a", "2i", "C6H5", "Et", 10, 24, "90:10", 59, "(Z)-3i", 1.2, None),
    (11, "1a", "2j", "C6H5", "Allyl", 40, 15, None, 42, "(Z)-3j", 1.2, "E/Z ratio could not be determined by NMR spectroscopy"),
    (12, "1a", "2k", "C4H9", "Me", 60, 10, None, None, None, 1.2, "no reaction; 1a recovered in 45% yield and 2k decomposed"),
    (13, "1b", "2a", "4-FC6H4", "Me", 20, 10, "90:10", 57, "(Z)-3k", 1.2, None),
    (14, "1b", "2h", "C6H5", "Me", 10, 15, "96:4", 61, "(Z)-3l", 1.2, None),
]


def indole_part(label, evidence, amount):
    return participant(label, "reactant", label, evidence, "N-tosylindole" if label == "1a" else "N-acetylindole", SMILES[label], [fld("amount", amount, evidence)])


for entry, indole, allene, r2, r3, temp, time_h, ratio, isolated, product, equiv, comment in table2_rows:
    evidence = [ev(2), ev(2, "text")]
    if entry == 7:
        evidence += [ev(3), ev(3, "text"), ev(5), ev(5, "text")]
    indole_amount = {"number": 4, "unit": "mmol"} if entry == 9 else {"number": 0.3, "unit": "mmol"}
    allene_amounts = [fld("amount", {"number": 4.8, "unit": "mmol"}, evidence)] if entry == 9 else [fld("equivalents", {"number": equiv, "unit": "equiv"}, evidence)]
    ps = [
        indole_part(indole, evidence, indole_amount),
        participant(allene, "reactant", allene, evidence, f"2,3-allenoate; R2={r2}, R3={r3}", SMILES["2h"] if allene == "2h" else None, allene_amounts),
        participant("TFA", "reagent", "TFA", evidence, "trifluoroacetic acid", SMILES["TFA"], [fld("volume", {"number": 1.5, "unit": "mL"}, evidence)]),
    ]
    if product:
        ps.append(participant("product", "product", product, evidence))
    outcomes = []
    if ratio is not None:
        outcomes.append(fld("Z/E_selectivity", {"ratio": ratio, "order": "Z/E"}, evidence))
        outcomes.append(fld("selectivity_measurement_basis", "1H NMR spectroscopy with CH2Br2 as internal standard", evidence))
    elif entry == 11:
        outcomes.append(fld("Z/E_selectivity", "not determined by NMR spectroscopy", evidence))
    if isolated is not None:
        outcomes += [fld("isolated_yield", {"number": isolated, "unit": "%"}, evidence, ["product"]), fld("yield_measurement_basis", "isolated yield", evidence)]
    if entry == 12:
        outcomes += [fld("reaction_outcome", "no reaction; 2k decomposed under the reaction conditions", evidence), fld("recovered_starting_material_yield", {"number": 45, "unit": "%"}, evidence, [indole])]
    notes = [f"Table 2 entry {entry}; R2={r2}, R3={r3}."]
    if comment:
        notes.append(comment)
    unresolved = ["Atmosphere, workup, and purification are not stated in the main-text table; SI was not associated.", "The product/allenoate structure is retained by table label and R-group description; no complete stereochemical product SMILES was assigned."]
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, participants=ps,
        steps=[{"step_id": "TFA_promoted_hydroarylation", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": [fld("temperature", {"number": temp, "unit": "°C"}, evidence), fld("time", {"number": time_h, "unit": "h"}, evidence), fld("solvent", "TFA", evidence)] + missing_conditions()}],
        outcomes=outcomes, notes=notes, unresolved=unresolved, source_id=f"Table 2 entry {entry}",
    ))


table3_rows = [
    (1, "1a", "2b", "4-ClC6H4", 60, 12, "92:8", 66, "(E)-3b", 1.2, None),
    (2, "1a", "2e", "4-MeOC6H4", 40, 15, "98:2", 59, "(E)-3e", 1.5, None),
    (3, "1a", "2f", "4-MeC6H4", 40, 12, "93:7", 65, "(E)-3f", 1.5, None),
    (4, "1a", "2g", "alpha-naphthyl", 80, 3, "78:22", 55, "(E)-3g", 1.5, "CCDC-800854; crystal data on page 5 support the E assignment"),
    # Entry 5 is merged into Table 1 entry 11.
    (6, "1b", "2e", "4-MeOC6H4", 40, 20, "88:12", 52, "(E)-3m", 1.5, None),
]

for entry, indole, allene, r2, temp, time_h, ratio, isolated, product, equiv, comment in table3_rows:
    evidence = [ev(3), ev(3, "text")]
    if entry == 4:
        evidence += [ev(5), ev(5, "text")]
    ps = [
        indole_part(indole, evidence, {"number": 0.3, "unit": "mmol"}),
        participant(allene, "reactant", allene, evidence, f"2,3-allenoate; R2={r2}, R3=Me", None, [fld("equivalents", {"number": equiv, "unit": "equiv"}, evidence)]),
        participant("TFA", "reagent", "TFA", evidence, "trifluoroacetic acid", SMILES["TFA"], [fld("volume", {"number": 1.5, "unit": "mL"}, evidence)]),
        participant("product", "product", product, evidence),
    ]
    records.append(record(
        f"table3_entry{entry}", "substrate_scope_entry", evidence, participants=ps,
        steps=[{"step_id": "TFA_promoted_hydroarylation", "participant_ids": [indole, allene, "TFA"], "conditions": [fld("temperature", {"number": temp, "unit": "°C"}, evidence), fld("time", {"number": time_h, "unit": "h"}, evidence), fld("solvent", "TFA", evidence)] + missing_conditions()}],
        outcomes=[fld("E/Z_selectivity", {"ratio": ratio, "order": "E/Z"}, evidence), fld("selectivity_measurement_basis", "1H NMR spectroscopy with CH2Br2 as internal standard", evidence), fld("isolated_yield", {"number": isolated, "unit": "%"}, evidence, ["product"]), fld("yield_measurement_basis", "isolated yield", evidence)],
        notes=[f"Table 3 entry {entry}; R2={r2}."] + ([comment] if comment else []),
        unresolved=["Atmosphere, workup, and purification are not stated in the main-text table; SI was not associated.", "Product/allenoate structures are retained by labels and R-group descriptions; complete stereochemical SMILES were not assigned."],
        source_id=f"Table 3 entry {entry}",
    ))


table4_rows = [
    (1, "1c", "5-Me", 10, 11, "8:92", 58, "(Z)-3n", None),
    (2, "1c", "5-Me", 60, 20, "96:4", 56, "(E)-3n", None),
    (3, "1d", "5-Br", 10, 12, "7:93", 70, "(Z)-3o", 6),
    (4, "1d", "5-Br", 60, 20, "77:23", 53, "(E)-3o", 8),
    (5, "1e", "5-OMe", 40, 12.5, "9:91", 52, "(Z)-3p", None),
]

for entry, indole, r1, temp, time_h, ratio, isolated, product, printed_recovery in table4_rows:
    evidence = [ev(4), ev(4, "text")]
    ps = [
        participant(indole, "reactant", indole, evidence, f"N-tosyl-{r1}-indole", None, [fld("amount", {"number": 0.3, "unit": "mmol"}, evidence)]),
        participant("2h", "reactant", "2h", evidence, "ethyl 2-methyl-4-phenylbuta-2,3-dienoate", SMILES["2h"], [fld("equivalents", {"number": 1.2, "unit": "equiv"}, evidence)]),
        participant("TFA", "reagent", "TFA", evidence, "trifluoroacetic acid", SMILES["TFA"], [fld("volume", {"number": 1.5, "unit": "mL"}, evidence)]),
        participant("product", "product", product, evidence),
    ]
    outcomes = [fld("E/Z_selectivity", {"ratio": ratio, "order": "E/Z"}, evidence), fld("selectivity_measurement_basis", "1H NMR spectroscopy with CH2Br2 as internal standard", evidence), fld("isolated_yield", {"number": isolated, "unit": "%"}, evidence, ["product"]), fld("yield_measurement_basis", "isolated yield", evidence)]
    unresolved = ["Atmosphere, workup, and purification are not stated in the main-text table; SI was not associated.", "Product structures are retained by source labels; complete stereochemical SMILES were not assigned."]
    notes = [f"Table 4 entry {entry}; indole substituent R1={r1}."]
    if printed_recovery is not None:
        ps.append(participant("printed_1a", "unspecified_agent", "1a (as printed in footnote)", evidence, "N-tosylindole", SMILES["1a"]))
        outcomes.append(fld("reported_recovered_1a_yield", {"number": printed_recovery, "unit": "%"}, evidence, ["printed_1a"]))
        notes.append(f"Footnote reports recovery of N-tosylindole 1a ({printed_recovery}%), although the row substrate is {indole}; the source discrepancy is preserved.")
        unresolved.append(f"Recovery footnote identity conflicts with the row substrate ({indole} versus printed 1a) and requires source/SI review.")
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", evidence, participants=ps,
        steps=[{"step_id": "TFA_promoted_hydroarylation", "participant_ids": [indole, "2h", "TFA"], "conditions": [fld("temperature", {"number": temp, "unit": "°C"}, evidence), fld("time", {"number": time_h, "unit": "h"}, evidence), fld("solvent", "TFA", evidence)] + missing_conditions()}],
        outcomes=outcomes, notes=notes, unresolved=unresolved, source_id=f"Table 4 entry {entry}",
    ))


p4 = [ev(4), ev(4, "text")]
records.append(record(
    "equation1_isomerization_Z3h_to_E3h", "reported_experiment", p4,
    participants=[
        participant("Z3h", "reactant", "(Z)-3h", p4),
        participant("E3h", "product", "(E)-3h", p4),
        participant("TFA", "reagent", "TFA", p4, "trifluoroacetic acid", SMILES["TFA"]),
    ],
    steps=[{"step_id": "isomerization", "participant_ids": ["Z3h", "TFA"], "conditions": [fld("temperature", {"number": 60, "unit": "°C"}, p4), fld("time", {"number": 48, "unit": "h"}, p4), fld("solvent", "TFA", p4)] + missing_conditions()}],
    outcomes=[fld("reported_yield", {"number": 41, "unit": "%"}, p4, ["E3h"]), fld("yield_measurement_basis", None, [])],
    notes=["Equation (1) tests isomerization of (Z)-3h in TFA; the text attributes the low yield partly to decomposition of 3h."],
    unresolved=["Reaction scale, TFA volume, yield measurement basis, atmosphere, workup, and purification are not stated in the main text; SI was not associated.", "Candidate stereochemical product SMILES was not assigned."],
    source_id="Equation (1)",
))

records.append(record(
    "scheme4_proposed_mechanism", "mechanism", p4,
    participants=[
        participant("generic_2h", "reactant", "2,3-allenoate represented as 2h-like substrate", p4),
        participant("M1", "unspecified_agent", "Z allylic carbocation M1", p4),
        participant("M2", "unspecified_agent", "E allylic carbocation M2", p4),
        participant("1a", "reactant", "N-tosylindole", p4, smiles=SMILES["1a"]),
        participant("E3", "product", "(E)-3", p4),
        participant("Z3", "product", "(Z)-3", p4),
    ],
    notes=["Scheme 4 is explicitly labeled a proposed mechanism: protonation at the allene center gives allylic carbocations M1/M2, followed by indole attack; higher temperature/time favors E product by isomerization."],
    unresolved=["This is a mechanistic proposal, not an independent batch experiment; arrows have no separate reported scales, times, or yields."],
    source_id="Scheme 4 proposed mechanism",
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
