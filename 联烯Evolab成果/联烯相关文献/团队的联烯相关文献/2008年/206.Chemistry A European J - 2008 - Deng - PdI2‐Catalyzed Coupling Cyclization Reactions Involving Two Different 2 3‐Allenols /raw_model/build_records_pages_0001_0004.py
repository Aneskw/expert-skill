#!/usr/bin/env python3
"""Build evidence-linked machine records for doc_32fa8a6b83b4754e, PDF pages 1–4."""

import json
from pathlib import Path


DOC = "doc_32fa8a6b83b4754e"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0004.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0004.json"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


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


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
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


def record(suffix, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record requires source review.",
                "Candidate structures are unverified.",
            ],
        },
    }


ALLENOL_1 = {
    "1a": ("2-substituted 2,3-allenol 1a (R1=nBu, R2=Et)", "C=C=C(CCCC)C(O)CC"),
    "1b": ("2-substituted 2,3-allenol 1b (R1=nBu, R2=Me)", "C=C=C(CCCC)C(O)C"),
    "1c": ("2-substituted 2,3-allenol 1c (R1=nBu, R2=Ph)", "C=C=C(CCCC)C(O)c1ccccc1"),
    "1d": ("2-substituted 2,3-allenol 1d (R1=Ph, R2=nBu)", "C=C=C(c1ccccc1)C(O)CCCC"),
    "1e": ("2-substituted 2,3-allenol 1e (R1=allyl, R2=Me)", "C=C=C(CC=C)C(O)C"),
    "1f": ("2-substituted 2,3-allenol 1f (R1=CO2Me, R2=p-tolyl)", "C=C=C(C(=O)OC)C(O)c1ccc(C)cc1"),
    "1g": ("2-substituted 2,3-allenol 1g (R1=nBu, R2=p-NO2C6H4)", "C=C=C(CCCC)C(O)c1ccc([N+](=O)[O-])cc1"),
    "1h": ("2-substituted 2,3-allenol 1h (R1=nBu, R2=o-ClC6H4)", "C=C=C(CCCC)C(O)c1ccccc1Cl"),
    "1i": ("2-substituted 2,3-allenol 1i (R1=CO2Me, R2=Et)", "C=C=C(C(=O)OC)C(O)CC"),
    "1j": ("2-substituted 2,3-allenol 1j (R1=CO2Me, R2=nC5H11)", "C=C=C(C(=O)OC)C(O)CCCCC"),
}

ALLENOL_2 = {
    "2a": ("buta-2,3-dienol 2a (R3=H, R4=H)", "OCC=C=C"),
    "2b": ("2,3-allenol 2b (R3=Et, R4=Et)", "C=C=CC(O)(CC)CC"),
    "2c": ("cyclic 2,3-allenol 2c (R3/R4=(CH2)5)", "C=C=CC1(O)CCCCC1"),
    "2d": ("secondary 2,3-allenol 2d (R3=nHex)", "C=C=CC(O)CCCCCC"),
    "2e": ("secondary 2,3-allenol 2e (R3=Bn)", "C=C=CC(O)Cc1ccccc1"),
    "2f": ("secondary 2,3-allenol 2f (R3=Ph)", "C=C=CC(O)c1ccccc1"),
}

PRODUCTS = {
    "3a": ("3-butyl-2-ethyl-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran (3a)", "O1C(CC)C(CCCC)=C(C(=C)C=C)C1"),
    "3b": ("3-butyl-2-methyl-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran (3b)", "O1C(C)C(CCCC)=C(C(=C)C=C)C1"),
    "3c": ("2-phenyl-3-butyl-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran (3c)", "O1C(c2ccccc2)C(CCCC)=C(C(=C)C=C)C1"),
    "3d": ("3-phenyl-2-butyl-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran (3d)", "O1C(CCCC)C(c2ccccc2)=C(C(=C)C=C)C1"),
    "3e": ("3-allyl-2-methyl-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran (3e)", "O1C(C)C(CC=C)=C(C(=C)C=C)C1"),
    "3f": ("methyl 2-(p-tolyl)-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran-3-carboxylate (3f)", "O1C(c2ccc(C)cc2)C(C(=O)OC)=C(C(=C)C=C)C1"),
    "3g": ("3-butyl-2-(p-nitrophenyl)-4-(1',3'-butadien-2'-yl)-2,5-dihydrofuran (3g)", "O1C(c2ccc([N+](=O)[O-])cc2)C(CCCC)=C(C(=C)C=C)C1"),
    "3h": ("dihydrofuran 3h from 1g and 2b", "O1C(c2ccc([N+](=O)[O-])cc2)C(CCCC)=C(C(=C)C=C(CC)CC)C1"),
    "3i": ("dihydrofuran 3i from 1g and cyclic allenol 2c", "O1C(c2ccc([N+](=O)[O-])cc2)C(CCCC)=C(C(=C)C=C2CCCCC2)C1"),
    "3j": ("(E)-dihydrofuran 3j from 1b and 2e", "O1C(C)C(CCCC)=C(C(=C)C=CCc2ccccc2)C1"),
    "3k": ("(E)-dihydrofuran 3k from 1c and 2e", "O1C(c2ccccc2)C(CCCC)=C(C(=C)C=CCc2ccccc2)C1"),
    "3l": ("(E)-dihydrofuran 3l from 1g and 2d", "O1C(c2ccc([N+](=O)[O-])cc2)C(CCCC)=C(C(=C)C=CCCCCCC)C1"),
    "3m": ("(E)-dihydrofuran 3m from 1g and 2e", "O1C(c2ccc([N+](=O)[O-])cc2)C(CCCC)=C(C(=C)C=CCc2ccccc2)C1"),
    "3n": ("(E)-dihydrofuran 3n from 1g and 2f", "O1C(c2ccc([N+](=O)[O-])cc2)C(CCCC)=C(C(=C)C=Cc2ccccc2)C1"),
    "3o": ("(E)-dihydrofuran 3o from 1h and 2e", "O1C(c2ccccc2Cl)C(CCCC)=C(C(=C)C=CCc2ccccc2)C1"),
    "3p": ("methyl (E)-dihydrofuran-3-carboxylate 3p from 1i and 2d", "O1C(CC)C(C(=O)OC)=C(C(=C)C=CCCCCCC)C1"),
    "3q": ("methyl (E)-dihydrofuran-3-carboxylate 3q from 1i and 2e", "O1C(CC)C(C(=O)OC)=C(C(=C)C=CCc2ccccc2)C1"),
    "3r": ("methyl (E)-dihydrofuran-3-carboxylate 3r from 1j and 2e", "O1C(CCCCC)C(C(=O)OC)=C(C(=C)C=CCc2ccccc2)C1"),
    "3s": ("(E)-dihydrofuran 3s from 1d and 2e", "O1C(CCCC)C(c2ccccc2)=C(C(=C)C=CCc2ccccc2)C1"),
}


def amount(name, number, unit, evidence, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return field(name, value, evidence)


def molecule(code, role, evidence, *, amounts=None, entity_id=None):
    source = ALLENOL_1 if code.startswith("1") else ALLENOL_2 if code.startswith("2") else PRODUCTS
    label, smiles = source[code]
    return participant(entity_id or code, role, code, evidence, name=label, smiles=smiles, amounts=amounts)


def common_agents(evidence, *, catalyst="PdI2", include_bf3=True, solvent="DMSO"):
    catalyst_smiles = {"PdI2": "[I-].[I-].[Pd+2]", "PdCl2": "[Cl-].[Cl-].[Pd+2]", "PdBr2": "[Br-].[Br-].[Pd+2]"}.get(catalyst)
    solvent_smiles = {
        "DMSO": "CS(C)=O", "HOAc": "CC(=O)O", "CH3NO2": "C[N+](=O)[O-]",
        "(CH2Cl)2": "ClCCCl", "CH3CN": "CC#N", "THF": "C1CCOC1",
        "N,N-dimethylacetamide": "CC(=O)N(C)C", "DMF": "CN(C)C=O", "DMPU": "CN1CCCN(C)C1=O",
    }.get(solvent)
    items = [participant("catalyst", "catalyst", catalyst, evidence, smiles=catalyst_smiles)]
    if include_bf3:
        items.append(participant("bf3_etherate", "reagent", "BF3·Et2O", evidence, name="boron trifluoride diethyl etherate", smiles="CCOCC.FB(F)F"))
    items.append(participant("solvent", "solvent", solvent, evidence, smiles=solvent_smiles))
    return items


records = []

# Page 1: generic reaction map, then discrete solvent-screening statements.
e1 = ev(1)
records.append(record(
    "scheme1_general_coupling", "general_scheme", e1,
    [
        participant("generic_allenol_1", "reactant", "2-substituted 2,3-allenol 1 (R groups)", e1),
        participant("generic_allenol_2", "reactant", "2-unsubstituted 2,3-allenol 2 (R groups)", e1),
        participant("generic_product_3", "product", "4-(1',3'-dien-2'-yl)-2,5-dihydrofuran 3 (R groups)", e1),
    ],
    [{"step_id": "generic_coupling_cyclization", "participant_ids": ["generic_allenol_1", "generic_allenol_2", "generic_product_3"], "conditions": []}],
    [],
    notes=["Scheme 1 is a generic present-paper reaction map, not an individual experimental run."],
    unresolved=["Generic R-group structures cannot be represented as complete standard SMILES."],
))

screening = [
    ("hoac", "HOAc", "not afforded"),
    ("nitromethane", "CH3NO2", "not afforded"),
    ("dce", "(CH2Cl)2", "not afforded"),
    ("acetonitrile", "CH3CN", "not afforded"),
    ("thf", "THF", "not afforded"),
    ("dma", "N,N-dimethylacetamide", {"minimum": 27, "maximum": 31, "unit": "%", "raw_text": "27–31%"}),
    ("dmf", "DMF", {"minimum": 27, "maximum": 31, "unit": "%", "raw_text": "27–31%"}),
    ("dmpu", "DMPU", {"minimum": 27, "maximum": 31, "unit": "%", "raw_text": "27–31%"}),
]
for slug, solvent, result in screening:
    records.append(record(
        f"optimization_solvent_{slug}", "optimization_entry", e1,
        [molecule("1a", "reactant", e1), molecule("2a", "reactant", e1), *common_agents(e1, include_bf3=False, solvent=solvent), molecule("3a", "product", e1)],
        [{"step_id": "solvent_screen", "participant_ids": ["1a", "2a", "catalyst", "solvent", "3a"], "conditions": []}],
        [field("reported_yield_3a", result, e1, ["3a"])],
        notes=["The page-1 prose groups the DMA, DMF, and DMPU results into a 27–31% range; it does not assign an exact value to each solvent."],
        unresolved=[
            "Catalyst loading, substrate quantities, temperature, duration, concentration, workup, purification, and yield basis are not stated in this page-1 sentence.",
            "For DMA/DMF/DMPU, only the shared 27–31% range is available; the individual yield is unresolved.",
        ],
    ))

# Page 2: explicit Scheme 2 cases and qualitative optimization comparisons.
e2 = ev(2)
scheme2_common = [
    molecule("1a", "reactant", e2, amounts=[amount("amount", 1.00, "mmol", e2)]),
    molecule("2a", "reactant", e2),
    participant("catalyst", "catalyst", "PdI2", e2, smiles="[I-].[I-].[Pd+2]", amounts=[amount("catalyst_loading", 5, "mol%", e2)]),
    participant("solvent", "solvent", "DMSO", e2, smiles="CS(C)=O"),
    molecule("3a", "product", e2),
]
records.append(record(
    "scheme2_dmso_without_bf3", "optimization_entry", e2,
    [
        scheme2_common[0],
        molecule("2a", "reactant", e2, amounts=[amount("equivalents", 2.0, "equiv", e2)]),
        *scheme2_common[2:],
    ],
    [{"step_id": "coupling_cyclization", "participant_ids": ["1a", "2a", "catalyst", "solvent", "3a"], "conditions": [
        field("temperature", {"number": 80, "unit": "°C"}, e2),
        field("time", {"number": 1.5, "unit": "h"}, e2),
        field("reaction_concentration", {"number": 0.2, "unit": "M"}, e2),
    ]}],
    [field("NMR_yield_3a", {"number": 46, "unit": "%"}, e2, ["3a"]), field("yield_measurement_basis", "NMR spectroscopy", e2, ["3a"])],
    unresolved=["Atmosphere, workup, purification, and NMR internal-standard details are not reported in the covered main-text pages."],
))

for slug, label, smiles in [
    ("scandium_triflate", "Sc(OTf)3", None),
    ("trifluoroacetic_acid", "trifluoroacetic acid", "O=C(O)C(F)(F)F"),
]:
    records.append(record(
        f"optimization_{slug}", "optimization_entry", e2,
        [molecule("1a", "reactant", e2), molecule("2a", "reactant", e2), participant("catalyst", "catalyst", "PdI2", e2, smiles="[I-].[I-].[Pd+2]"), participant("lewis_acid", "reagent", label, e2, smiles=smiles), participant("solvent", "solvent", "DMSO", e2, smiles="CS(C)=O"), molecule("3a", "product", e2)],
        [{"step_id": "lewis_acid_screen", "participant_ids": ["1a", "2a", "catalyst", "lewis_acid", "solvent", "3a"], "conditions": []}],
        [field("reported_yield_effect", "could further improve the yield", e2, ["3a"])],
        unresolved=["The covered main text does not report additive loading, exact yield, substrate ratio, temperature, duration, concentration, workup, purification, or yield basis for this Lewis-acid screen."],
    ))

records.append(record(
    "scheme2_bf3_optimized", "optimization_entry", e2,
    [
        molecule("1a", "reactant", e2, amounts=[amount("amount", 1.00, "mmol", e2)]),
        molecule("2a", "reactant", e2, amounts=[amount("equivalents", 1.1, "equiv", e2)]),
        participant("catalyst", "catalyst", "PdI2", e2, smiles="[I-].[I-].[Pd+2]", amounts=[amount("catalyst_loading", 5, "mol%", e2)]),
        participant("bf3_etherate", "reagent", "BF3·Et2O", e2, name="boron trifluoride diethyl etherate", smiles="CCOCC.FB(F)F", amounts=[amount("equivalents", 1.0, "equiv", e2)]),
        participant("solvent", "solvent", "DMSO", e2, smiles="CS(C)=O"),
        molecule("3a", "product", e2),
    ],
    [{"step_id": "coupling_cyclization", "participant_ids": ["1a", "2a", "catalyst", "bf3_etherate", "solvent", "3a"], "conditions": [
        field("temperature", {"number": 80, "unit": "°C"}, e2), field("time", {"number": 1.5, "unit": "h"}, e2), field("reaction_concentration", {"number": 0.2, "unit": "M"}, e2),
    ]}],
    [field("NMR_yield_3a", {"number": 63, "unit": "%"}, e2, ["3a"]), field("yield_measurement_basis", "NMR spectroscopy", e2, ["3a"])],
    unresolved=["Atmosphere, workup, purification, and NMR internal-standard details are not reported for this optimization entry."],
))

for catalyst in ("PdCl2", "PdBr2"):
    slug = catalyst.lower().replace("2", "2")
    records.append(record(
        f"optimization_catalyst_{slug}", "optimization_entry", e2,
        [molecule("1a", "reactant", e2), molecule("2a", "reactant", e2), *common_agents(e2, catalyst=catalyst, include_bf3=True, solvent="DMSO"), molecule("3a", "product", e2)],
        [{"step_id": "catalyst_comparison", "participant_ids": ["1a", "2a", "catalyst", "bf3_etherate", "solvent", "3a"], "conditions": []}],
        [field("reported_relative_result", "PdI2 gave the best results in the reported PdCl2/PdBr2/PdI2 comparison", e2, ["3a"])],
        unresolved=["The exact yield and the conditions specific to this catalyst-comparison run are not reported in the covered main text."],
    ))

# Page 2 Table 1: nine independent substrate-scope rows.
table1 = [
    (1, "1a", "2a", "3a", 57, 1.1, 1.5),
    (2, "1b", "2a", "3b", 61, 1.1, 1.0),
    (3, "1c", "2a", "3c", 78, 1.1, 1.0),
    (4, "1d", "2a", "3d", 70, 1.1, 1.0),
    (5, "1e", "2a", "3e", 49, 1.1, 1.0),
    (6, "1f", "2a", "3f", 55, 1.2, 1.0),
    (7, "1g", "2a", "3g", 70, 1.1, 1.0),
    (8, "1g", "2b", "3h", 50, 1.3, 1.0),
    (9, "1g", "2c", "3i", 57, 1.3, 1.5),
]
for entry, s1, s2, prod, yld, eq2, hours in table1:
    participants = [
        molecule(s1, "reactant", e2),
        molecule(s2, "reactant", e2, amounts=[amount("equivalents", eq2, "equiv", e2)]),
        participant("catalyst", "catalyst", "PdI2", e2, smiles="[I-].[I-].[Pd+2]", amounts=[amount("catalyst_loading", 5, "mol%", e2)]),
        participant("bf3_etherate", "reagent", "BF3·Et2O", e2, name="boron trifluoride diethyl etherate", smiles="CCOCC.FB(F)F", amounts=[amount("equivalents", 1.0, "equiv", e2)]),
        participant("solvent", "solvent", "DMSO", e2, smiles="CS(C)=O"),
        molecule(prod, "product", e2),
    ]
    evidence = list(e2)
    conditions = [field("temperature", {"number": 80, "unit": "°C"}, e2), field("time", {"number": hours, "unit": "h"}, e2), field("reaction_concentration", {"number": 0.2, "unit": "M"}, e2)]
    notes = [f"Table 1 entry {entry}; the allenol-2 loading and time include any row-specific footnote override."]
    unresolved = ["Atmosphere, workup, purification, and exact reactant-1 scale are not stated in Table 1.", "Candidate product structure is machine-derived from the table drawing and substituent labels and remains unverified."]
    if entry == 1:
        e3 = ev(3)
        evidence += e3
        # Replace participants with the detailed general-procedure quantities and operational reagents.
        participants = [
            molecule("1a", "reactant", evidence, amounts=[amount("mass", 154.7, "mg", e3), amount("amount", 1.00, "mmol", e3)]),
            molecule("2a", "reactant", evidence, amounts=[amount("mass", 77.9, "mg", e3), amount("amount", 1.11, "mmol", e3), amount("equivalents", 1.1, "equiv", e2)]),
            participant("catalyst", "catalyst", "PdI2", evidence, smiles="[I-].[I-].[Pd+2]", amounts=[amount("mass", 18.5, "mg", e3), amount("amount", 0.051, "mmol", e3), amount("catalyst_loading", 5, "mol%", evidence)]),
            participant("bf3_etherate", "reagent", "BF3·Et2O", evidence, name="boron trifluoride diethyl etherate", smiles="CCOCC.FB(F)F", amounts=[amount("volume", 127, "uL", e3), amount("mass", 142.2, "mg", e3), amount("amount", 1.0, "mmol", e3), amount("equivalents", 1.0, "equiv", e2), field("reported_density", "1.12 g mL^-1", e3)]),
            participant("solvent", "solvent", "DMSO", evidence, smiles="CS(C)=O", amounts=[amount("initial_volume", 2.5, "mL", e3), amount("added_volume", 2.5, "mL", e3)]),
            participant("water", "reagent", "water", e3, smiles="O", amounts=[amount("quench_volume", 10, "mL", e3)]),
            participant("diethyl_ether", "solvent", "Et2O", e3, smiles="CCOCC", amounts=[amount("extraction_volume", 25, "mL", e3), field("extraction_count", "3 portions", e3)]),
            participant("sodium_thiosulfate", "reagent", "saturated aqueous Na2S2O3", e3, smiles="[Na+].[Na+].[O-]S(=O)(=S)[O-]"),
            participant("brine", "reagent", "brine", e3),
            participant("sodium_sulfate", "reagent", "anhydrous Na2SO4", e3, smiles="[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
            participant("petroleum_ether", "solvent", "petroleum ether", e3),
            participant("ethyl_acetate", "solvent", "ethyl acetate", e3, smiles="CCOC(C)=O"),
            molecule("3a", "product", evidence),
        ]
        conditions = [
            field("temperature", {"number": 80, "unit": "°C"}, evidence), field("time", {"number": 1.5, "unit": "h"}, evidence), field("reaction_concentration", {"number": 0.2, "unit": "M"}, e2),
            field("operation", "BF3·Et2O, 1a, and 2.5 mL DMSO were added sequentially to PdI2 and 2a in 2.5 mL DMSO; completion was checked by TLC.", e3),
        ]
        notes = ["Table 1 entry 1 and the page-3 general preparation describe the same 3a experiment and are merged rather than duplicated."]
        unresolved = ["Atmosphere is not reported.", "The candidate structures remain unverified; characterization was not used to certify the structures."]
    step_ids = [p["entity_id"] for p in participants]
    steps = [{"step_id": "coupling_cyclization", "participant_ids": step_ids, "conditions": conditions}]
    if entry == 1:
        steps.append({"step_id": "workup_and_purification", "participant_ids": ["3a", "water", "diethyl_ether", "sodium_thiosulfate", "brine", "sodium_sulfate", "petroleum_ether", "ethyl_acetate"], "conditions": [
            field("workup", "Cool to room temperature; quench with water; extract with Et2O (3×25 mL); wash with saturated aqueous Na2S2O3 and brine; dry over anhydrous Na2SO4; evaporate.", ev(3)),
            field("purification", "Silica-gel column chromatography, petroleum ether/ethyl acetate 100:1.", ev(3)),
        ]})
    outcomes = [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, [prod]), field("yield_measurement_basis", "isolated yield", e2, [prod])]
    if entry == 1:
        outcomes += [field("product_mass", {"number": 118.6, "unit": "mg"}, ev(3), ["3a"]), field("physical_form", "oil", ev(3), ["3a"])]
    records.append(record(f"table1_entry{entry}_{prod}", "substrate_scope_entry", evidence, participants, steps, outcomes, notes=notes, unresolved=unresolved))

# Page 2 Table 2: ten independent E-selective substrate-scope rows.
table2 = [
    (1, "1b", "2e", "3j", 55, 1.3),
    (2, "1c", "2e", "3k", 62, 1.1),
    (3, "1g", "2d", "3l", 69, 1.1),
    (4, "1g", "2e", "3m", 81, 1.1),
    (5, "1g", "2f", "3n", 38, 1.1),
    (6, "1h", "2e", "3o", 65, 1.1),
    (7, "1i", "2d", "3p", 52, 1.1),
    (8, "1i", "2e", "3q", 52, 1.1),
    (9, "1j", "2e", "3r", 53, 1.1),
    (10, "1d", "2e", "3s", 48, 1.1),
]
for entry, s1, s2, prod, yld, eq2 in table2:
    participants = [
        molecule(s1, "reactant", e2), molecule(s2, "reactant", e2, amounts=[amount("equivalents", eq2, "equiv", e2)]),
        participant("catalyst", "catalyst", "PdI2", e2, smiles="[I-].[I-].[Pd+2]", amounts=[amount("catalyst_loading", 5, "mol%", e2)]),
        participant("bf3_etherate", "reagent", "BF3·Et2O", e2, name="boron trifluoride diethyl etherate", smiles="CCOCC.FB(F)F", amounts=[amount("equivalents", 1.0, "equiv", e2)]),
        participant("solvent", "solvent", "DMSO", e2, smiles="CS(C)=O"), molecule(prod, "product", e2),
    ]
    steps = [{"step_id": "stereoselective_coupling_cyclization", "participant_ids": [s1, s2, "catalyst", "bf3_etherate", "solvent", prod], "conditions": [
        field("temperature", {"number": 80, "unit": "°C"}, e2),
        field("time", {"minimum": 0.5, "maximum": 1.2, "unit": "h", "raw_text": "0.5–1.2 h"}, e2),
        field("reaction_concentration", {"number": 0.2, "unit": "M"}, e2),
    ]}]
    records.append(record(
        f"table2_entry{entry}_{prod}", "substrate_scope_entry", e2, participants, steps,
        [field("isolated_yield", {"number": yld, "unit": "%"}, e2, [prod]), field("yield_measurement_basis", "isolated yield", e2, [prod]), field("alkene_geometry", "E", e2, [prod])],
        notes=[f"Table 2 entry {entry}; the table reports product (E)-{prod}. The paper states that the assignment was based on the NOESY study of (E)-3p."],
        unresolved=["The row-specific reaction time within the reported 0.5–1.2 h range is not assigned.", "Atmosphere, workup, purification, and exact reaction scale are not reported in Table 2.", "Candidate product SMILES omits asserted alkene stereobonds and remains unverified."],
    ))

# Page 3 Scheme 3 and detailed optical-activity paragraphs: two separate enantioenriched-substrate experiments.
e3 = ev(3)
chiral_runs = [
    ("3b", "2a", 1.1, 58, 137.3, 0.98, 18.1, 0.050, 79.9, 1.14, 127, 1.0, 5.0, 108.4, "+26.4 (c=1.09 in CHCl3)"),
    ("3j", "2e", 1.3, 53, 56.0, 1.00, 7.2, 0.020, 86.8, 0.54, 51, 0.40, 2.0, 60.1, "+10.1 (c=0.64 in CHCl3)"),
]
for prod, s2, eq2, yld, s1mg, s1mmol, pdmg, pdmmol, s2mg, s2mmol, bfvol, bfmmol, dmsovol, prodmg, rotation in chiral_runs:
    suffix = f"scheme3_optically_active_{prod}"
    s1_label = "(S)-(−)-1b (>99% ee)"
    participants = [
        participant("s_1b", "reactant", s1_label, e3, name="enantioenriched 2,3-allenol (S)-1b", smiles=ALLENOL_1["1b"][1], amounts=[amount("mass", s1mg, "mg", e3), amount("amount", s1mmol, "mmol", e3)]),
        molecule(s2, "reactant", e3, amounts=[amount("mass", s2mg, "mg", e3), amount("amount", s2mmol, "mmol", e3), amount("equivalents", eq2, "equiv", e3)]),
        participant("catalyst", "catalyst", "PdI2", e3, smiles="[I-].[I-].[Pd+2]", amounts=[amount("mass", pdmg, "mg", e3), amount("amount", pdmmol, "mmol", e3), amount("catalyst_loading", 5, "mol%", e3)]),
        participant("bf3_etherate", "reagent", "BF3·Et2O", e3, name="boron trifluoride diethyl etherate", smiles="CCOCC.FB(F)F", amounts=[amount("volume", bfvol, "uL", e3), amount("amount", bfmmol, "mmol", e3), amount("equivalents", 1.0, "equiv", e3)]),
        participant("solvent", "solvent", "DMSO", e3, smiles="CS(C)=O", amounts=[amount("volume", dmsovol, "mL", e3)]),
        participant(f"chiral_{prod}", "product", f"{('(S)-(+)-3b' if prod == '3b' else '(E,S)-(+)-3j')} (>99% ee)", e3, name=PRODUCTS[prod][0], smiles=PRODUCTS[prod][1]),
    ]
    steps = [{"step_id": "enantiospecific_coupling_cyclization", "participant_ids": ["s_1b", s2, "catalyst", "bf3_etherate", "solvent", f"chiral_{prod}"], "conditions": [field("temperature", {"number": 80, "unit": "°C"}, e3)]}]
    outcomes = [
        field("isolated_yield", {"number": yld, "unit": "%"}, e3, [f"chiral_{prod}"]),
        field("yield_measurement_basis", "isolated yield", e3, [f"chiral_{prod}"]),
        field("product_mass", {"number": prodmg, "unit": "mg"}, e3, [f"chiral_{prod}"]),
        field("product_ee", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% ee"}, e3, [f"chiral_{prod}"]),
        field("optical_rotation", rotation, e3, [f"chiral_{prod}"]),
        field("physical_form", "oil", e3, [f"chiral_{prod}"]),
    ]
    if prod == "3j":
        outcomes.append(field("alkene_geometry", "E", e3, ["chiral_3j"]))
    unresolved = ["Reaction duration, atmosphere, workup, purification, and yield basis beyond the isolated product wording are not stated in the covered paragraph.", "Candidate SMILES omits the asserted absolute/alkene stereochemistry and remains unverified."]
    if prod == "3j":
        unresolved.append("The source explicitly reports 56.0 mg of (S)-1b as 1.00 mmol; this mass/amount pair is retained verbatim despite apparent inconsistency.")
    records.append(record(suffix, "reported_experiment", e3, participants, steps, outcomes, notes=["Scheme 3 and the corresponding page-3 detailed paragraph describe the same experiment and are merged."], unresolved=unresolved))

# Page 3 Scheme 4: proposed mechanism, not a reported experimental run.
mechanism_evidence = list(dict.fromkeys(e2 + e3))
records.append(record(
    "scheme4_proposed_mechanism", "mechanism", mechanism_evidence,
    [
        participant("generic_allenol_1", "reactant", "2-substituted 2,3-allenol 1", mechanism_evidence),
        participant("generic_allenol_2", "reactant", "2-unsubstituted 2,3-allenol 2", mechanism_evidence),
        participant("m1", "unspecified_agent", "2,5-dihydrofuranyl palladium intermediate M1", mechanism_evidence),
        participant("m2", "unspecified_agent", "π-allylic palladium intermediate M2", mechanism_evidence),
        participant("generic_product_3", "product", "dihydrofuran product 3", mechanism_evidence),
        participant("pdioh", "unspecified_agent", "PdI(OH)", mechanism_evidence),
        participant("hi", "unspecified_agent", "HI", mechanism_evidence),
        participant("pdi2", "catalyst", "PdI2", mechanism_evidence, smiles="[I-].[I-].[Pd+2]"),
    ],
    [
        {"step_id": "cyclic_oxypalladation", "participant_ids": ["generic_allenol_1", "m1"], "conditions": []},
        {"step_id": "regioselective_carbopalladation", "participant_ids": ["m1", "generic_allenol_2", "m2"], "conditions": []},
        {"step_id": "trans_beta_hydroxide_elimination", "participant_ids": ["m2", "generic_product_3", "pdioh"], "conditions": []},
        {"step_id": "catalyst_regeneration", "participant_ids": ["pdioh", "hi", "pdi2"], "conditions": []},
    ],
    [],
    notes=["Scheme 4 is explicitly labeled a possible mechanism; it is not counted as an experimental reaction result."],
    unresolved=["Generic R-group intermediates and organopalladium bonding are not encoded as verified SMILES.", "The mechanism is proposed rather than experimentally established in the covered pages."],
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction in the upper and middle page", "finding": "High-level claims and cited prior work were classified as narrative/literature context, not duplicated as present-paper experiments.", "evidence_ids": ev(1)},
                {"region": "lower-right Scheme 1", "finding": "Generic present-paper coupling–cyclization map classified as a general scheme with unresolved R groups.", "evidence_ids": ev(1)},
                {"region": "lower-right Results and Discussion prose", "finding": "Eight solvent-screening trials were separated: five solvents failed to afford 3a and three solvents gave only a shared 27–31% yield range.", "evidence_ids": ev(1)},
            ],
            "record_ids": [r["record_id"] for r in records if r["record_id"] == f"{DOC}:scheme1_general_coupling" or ":optimization_solvent_" in r["record_id"]],
            "unresolved": ["The individual DMA/DMF/DMPU yields are not assigned within the reported 27–31% range.", "The introduction cites prior reactions without experiment-level conditions; no literature-example records were fabricated from citation prose."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 2 and surrounding optimization prose", "finding": "The DMSO/no-BF3 46% NMR case and BF3-optimized 63% NMR case were separated; qualitative Sc(OTf)3/TFA and PdCl2/PdBr2 comparisons were retained with missing exact yields.", "evidence_ids": ev(2)},
                {"region": "middle Table 1 including reaction header and footnotes", "finding": "Nine independent substrate-scope rows extracted with isolated yields and row-specific time or allenol-2-equivalent overrides.", "evidence_ids": ev(2)},
                {"region": "lower Table 2 including reaction header and footnotes", "finding": "Ten independent E-selective substrate-scope rows extracted with isolated yields, the shared 0.5–1.2 h time range, and entry-1 1.3-equivalent override.", "evidence_ids": ev(2)},
                {"region": "upper-right proposed-mechanism prose and lower-left optical-activity discussion", "finding": "Mechanistic narrative was linked to Scheme 4 as a mechanism record; the two optically active experiments were linked to their page-3 scheme/procedures rather than duplicated.", "evidence_ids": ev(2)},
            ],
            "record_ids": [r["record_id"] for r in records if f"{DOC}:scheme2_" in r["record_id"] or f"{DOC}:optimization_scandium" in r["record_id"] or f"{DOC}:optimization_trifluoroacetic" in r["record_id"] or f"{DOC}:optimization_catalyst" in r["record_id"] or f"{DOC}:table1_" in r["record_id"] or f"{DOC}:table2_" in r["record_id"] or f"{DOC}:scheme3_" in r["record_id"] or f"{DOC}:scheme4_" in r["record_id"]],
            "unresolved": ["Sc(OTf)3, TFA, PdCl2, and PdBr2 comparison trials have no exact yields or complete conditions in the covered main text.", "Table 2 supplies only a shared 0.5–1.2 h range, not row-specific times.", "All drawn candidate structures remain unverified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 3", "finding": "Two enantioenriched-(S)-1b coupling experiments extracted and merged with their detailed paragraphs; product ee and isolated yields retained.", "evidence_ids": ev(3)},
                {"region": "middle-left Scheme 4", "finding": "Four-arrow oxypalladation/carbopalladation/beta-hydroxide-elimination/catalyst-regeneration proposal classified as mechanism, not experiment.", "evidence_ids": ev(3)},
                {"region": "lower-left Experimental Section and page-spanning 3a general procedure", "finding": "Starting-material preparations are citation-based and were not expanded; the complete 3a procedure was merged into Table 1 entry 1 with quantities, workup, purification, product mass, and yield.", "evidence_ids": ev(3)},
                {"region": "upper-right detailed optical-activity procedures", "finding": "Exact masses, amounts, catalyst loadings, solvent volumes, product masses, ee, optical rotations, and HPLC-condition narrative were localized; no new duplicate records were made.", "evidence_ids": ev(3)},
            ],
            "record_ids": [f"{DOC}:table1_entry1_3a", f"{DOC}:scheme3_optically_active_3b", f"{DOC}:scheme3_optically_active_3j", f"{DOC}:scheme4_proposed_mechanism"],
            "unresolved": ["The 3j paragraph explicitly pairs 56.0 mg of (S)-1b with 1.00 mmol; this apparent source inconsistency is preserved.", "The optical-activity procedures omit reaction time, atmosphere, workup, and purification.", "The 3a procedure omits atmosphere."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "both columns of the original page", "finding": "References and publication dates only; cited prior work was not converted into present-paper experiments because no experiment-specific arrows, conditions, or outcomes appear on this page.", "evidence_ids": ev(4)},
            ],
            "record_ids": [],
            "unresolved": ["No SI file was supplied or explicitly associated; the reference page does not establish an SI association."],
        },
    ],
}


OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "raw_records": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
