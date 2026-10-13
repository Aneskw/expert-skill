#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0006.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0006.json"
DOC = "doc_e34a8fe7cb4f6494"


def ev(*pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return list(dict.fromkeys(out))


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


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def part(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, evidence),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
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
                "Machine-extracted chemistry requires expert source review.",
                "All candidate structures remain unverified.",
            ],
        },
    }


SMILES_1 = {
    "1a": "C=C=CC(O)CCCCCCCC",
    "1b": "C=C=CC(O)CCCCCCC",
    "1c": "C=C=CC(O)CCCCCC",
    "1d": "C=C=CC(O)CCCCC",
    "1e": "C=C=CC(O)CCc1ccccc1",
    "1f": "C=C=CC(O)Cc1ccccc1",
    "1g": "C=C=CC(O)C1CCCCC1",
    "1h": "C=C=CC(O)c1ccccc1",
    "1i": "C=C=CC(O)c1ccc(F)cc1",
    "1j": "C=C=CC(O)c1ccc(Cl)cc1",
    "1k": "C=C=CC(O)c1ccc(Br)cc1",
    "1l": "C=C=CC(O)c1cccc2ccccc12",
    "1m": "C=C=CC(O)c1ccccc1Cl",
    "1n": "C=C=CC(O)c1c(Cl)cccc1Cl",
    "1o": "C=C=CC(O)c1ccc(CC)cc1",
    "1p": "C=C=CC1(O)CCCCC1",
    "1q": "C=C=CC1(O)CCCC1",
    "1r": "C=C=CC(O)(C)c1ccccc1",
    "1s": "CCCCCCC=C=CC(O)C",
    "1t": "CCCCCC=C=CC(O)c1ccc(Cl)cc1",
    "1u": "OCC(C)=C=Cc1ccccc1",
}

SMILES_3 = {
    "3a": "O=C1OC(CCCCCCCC)C=C1CCl",
    "3b": "O=C1OC(CCCCCCC)C=C1CCl",
    "3c": "O=C1OC(CCCCCC)C=C1CCl",
    "3d": "O=C1OC(CCCCC)C=C1CCl",
    "3e": "O=C1OC(CCc2ccccc2)C=C1CCl",
    "3f": "O=C1OC(Cc2ccccc2)C=C1CCl",
    "3g": "O=C1OC(C2CCCCC2)C=C1CCl",
    "3h": "O=C1OC(c2ccccc2)C=C1CCl",
    "3i": "O=C1OC(c2ccc(F)cc2)C=C1CCl",
    "3j": "O=C1OC(c2ccc(Cl)cc2)C=C1CCl",
    "3k": "O=C1OC(c2ccc(Br)cc2)C=C1CCl",
    "3l": "O=C1OC(c2cccc3ccccc23)C=C1CCl",
    "3m": "O=C1OC(c2ccccc2Cl)C=C1CCl",
    "3n": "O=C1OC(c2c(Cl)cccc2Cl)C=C1CCl",
    "3o": "O=C1OC(c2ccc(CC)cc2)C=C1CCl",
    "3p": "O=C1OC2(CCCCC2)C=C1CCl",
    "3q": "O=C1OC2(CCCC2)C=C1CCl",
    "3r": "O=C1OC(C)(c2ccccc2)C=C1CCl",
}

R2 = {
    "2a": ("Ph", "C=C=CCC(O)c1ccccc1"),
    "2b": ("4-EtC6H4", "C=C=CCC(O)c1ccc(CC)cc1"),
    "2c": ("4-ClC6H4", "C=C=CCC(O)c1ccc(Cl)cc1"),
    "2d": ("2-ClC6H4", "C=C=CCC(O)c1ccccc1Cl"),
    "2e": ("4-BrC6H4", "C=C=CCC(O)c1ccc(Br)cc1"),
    "2f": ("4-i-PrC6H4", "C=C=CCC(O)c1ccc(C(C)C)cc1"),
    "2g": ("1-naphthyl", "C=C=CCC(O)c1cccc2ccccc12"),
    "2h": ("n-C8H17", "C=C=CCC(O)CCCCCCCC"),
    "2i": ("n-C5H11", "C=C=CCC(O)CCCCC"),
}

SMILES_4 = {
    "4a": "O=C1OC(c2ccccc2)CC=C1CCl",
    "4b": "O=C1OC(c2ccc(CC)cc2)CC=C1CCl",
    "4c": "O=C1OC(c2ccc(Cl)cc2)CC=C1CCl",
    "4d": "O=C1OC(c2ccccc2Cl)CC=C1CCl",
    "4e": "O=C1OC(c2ccc(Br)cc2)CC=C1CCl",
    "4f": "O=C1OC(c2ccc(C(C)C)cc2)CC=C1CCl",
    "4g": "O=C1OC(c2cccc3ccccc23)CC=C1CCl",
    "4h": "O=C1OC(CCCCCCCC)CC=C1CCl",
    "4i": "O=C1OC(CCCCC)CC=C1CCl",
}


def amount(name, number, unit, evidence):
    return fld(name, qty(number, unit), evidence)


def common_main_participants(substrate, product, evidence, substrate_smiles, product_smiles,
                             solvent="CH3CN", pd=5, cu=5, et3n=2, bq=None,
                             exact=None, base="Et3N"):
    exact = exact or {}
    ps = [
        part(substrate, "reactant", substrate, evidence, smiles=substrate_smiles,
             amounts=[amount(k, n, u, evidence) for k, n, u in exact.get(substrate, [])]),
        part(product, "product", product, evidence, smiles=product_smiles,
             amounts=[amount(k, n, u, evidence) for k, n, u in exact.get(product, [])]),
        part("CuCl2", "reagent", "CuCl2", evidence, name="anhydrous copper(II) chloride",
             smiles="[Cl-].[Cl-].[Cu+2]", amounts=[amount("equivalents", cu, "equiv", evidence)] +
             [amount(k, n, u, evidence) for k, n, u in exact.get("CuCl2", [])]),
        part("PdCl2", "catalyst", "PdCl2", evidence, name="palladium(II) chloride",
             smiles="[Cl-].[Cl-].[Pd+2]", amounts=[amount("catalyst_loading", pd, "mol%", evidence)] +
             [amount(k, n, u, evidence) for k, n, u in exact.get("PdCl2", [])]),
        part("CO", "reagent", "CO", evidence, name="carbon monoxide", smiles="[C-]#[O+]"),
    ]
    if base == "Et3N" and et3n is not None:
        ps.append(part("Et3N", "reagent", "Et3N", evidence, name="triethylamine",
                       smiles="CCN(CC)CC", amounts=[amount("equivalents", et3n, "equiv", evidence)] +
                       [amount(k, n, u, evidence) for k, n, u in exact.get("Et3N", [])]))
    elif base == "NaOAc":
        ps.append(part("NaOAc", "reagent", "NaOAc", evidence, name="sodium acetate",
                       smiles="CC(=O)[O-].[Na+]", amounts=[amount("equivalents", et3n, "equiv", evidence)]))
    if bq is not None:
        ps.append(part("BQ", "reagent", "BQ", evidence, name="1,4-benzoquinone",
                       smiles="O=C1C=CC(=O)C=C1", amounts=[amount("equivalents", bq, "equiv", evidence)] +
                       [amount(k, n, u, evidence) for k, n, u in exact.get("BQ", [])]))
    solvent_smiles = {"CH3CN": "CC#N", "THF": "C1CCOC1", "dioxane": "O1CCOCC1",
                      "toluene": "Cc1ccccc1", "benzene": "c1ccccc1", "DMF": "CN(C)C=O",
                      "CH2Cl2": "ClCCl", "HOAc": "CC(=O)O", "Et3N": "CCN(CC)CC"}.get(solvent)
    ps.append(part(f"solvent_{solvent}", "solvent", solvent, evidence, smiles=solvent_smiles,
                   amounts=[amount(k, n, u, evidence) for k, n, u in exact.get("solvent", [])]))
    return ps


records = []

# Page 2: substrate preparations shown in Schemes 1-3.
scheme1 = [
    ("1a", "n-C8H17", "H", 76), ("1b", "n-C7H15", "H", 75),
    ("1c", "n-C6H13", "H", 67), ("1d", "n-C5H11", "H", 69),
    ("1e", "PhCH2CH2", "H", 68), ("1f", "PhCH2", "H", 69),
    ("1g", "cyclohexyl", "H", 65), ("1h", "Ph", "H", 67),
    ("1i", "4-FC6H4", "H", 60), ("1j", "4-ClC6H4", "H", 66),
    ("1k", "4-BrC6H4", "H", 65), ("1l", "1-naphthyl", "H", 72),
    ("1m", "2-ClC6H4", "H", 74), ("1n", "2,6-Cl2C6H3", "H", 58),
    ("1o", "4-EtC6H4", "H", 72), ("1p", "-(CH2)5-", None, 71),
    ("1q", "-(CH2)4-", None, 51), ("1r", "Ph", "Me", 52),
]
for label, r1, r2, yld in scheme1:
    e = ev(2)
    carbonyl = part(f"carbonyl_{label}", "reactant", f"carbonyl precursor for {label}", e,
                    name=f"carbonyl compound, R1={r1}, R2={r2 or 'ring closure'}")
    prod = part(label, "product", label, e, name=f"2,3-allenol {label}", smiles=SMILES_1[label])
    participants = [
        carbonyl,
        part("ethynyl_MgBr", "reagent", "HC≡CMgBr", e, name="ethynylmagnesium bromide"),
        part(f"propargyl_{label}", "reactant", f"propargylic alcohol precursor of {label}", e),
        part("paraformaldehyde", "reagent", "(HCHO)n", e, name="paraformaldehyde", smiles="C=O"),
        part("iPr2NH", "reagent", "i-Pr2NH", e, name="diisopropylamine", smiles="CC(C)NC(C)C"),
        part("CuBr", "catalyst", "CuBr", e, name="copper(I) bromide", smiles="[Cu]Br"),
        part("dioxane", "solvent", "dioxane", e, smiles="O1CCOCC1"), prod,
    ]
    steps = [
        {"step_id": "propargylic_alcohol_formation", "participant_ids": [carbonyl["entity_id"], "ethynyl_MgBr", f"propargyl_{label}"],
         "conditions": [fld("initial_temperature", qty(-20, "°C"), e), fld("operation", "warm from -20 °C to room temperature", e)]},
        {"step_id": "crabbe_homologation", "participant_ids": [f"propargyl_{label}", "paraformaldehyde", "iPr2NH", "CuBr", "dioxane", label],
         "conditions": [fld("temperature", "reflux", e)]},
    ]
    records.append(record(f"scheme1_{label}_preparation", "substrate_scope_entry", e, participants, steps,
                          [fld("reported_yield", qty(yld, "%"), e, [label])],
                          notes=["Scheme 1 reports the final allene yield; the individual carbonyl and propargylic structures are shown generically through R1/R2."],
                          unresolved=["Absolute quantities, durations, atmosphere, workup, purification, and yield basis are not reported on page 2.", "Intermediate connectivity and every candidate structure remain unverified."]))

scheme2_yields = {"2a": 34, "2b": 45, "2c": 44, "2d": 54, "2e": 43, "2f": 46, "2g": 47, "2h": 47, "2i": 47}
for label, yld in scheme2_yields.items():
    e = ev(2)
    r1, smi = R2[label]
    participants = [
        part(f"carbonyl_{label}", "reactant", f"carbonyl precursor for {label}", e, name=f"carbonyl compound, R1={r1}, R2=H"),
        part("allenyl_MgBr", "reagent", "allenyl-MgBr", e, name="allenylmagnesium bromide"),
        part(f"homo_propargyl_{label}", "reactant", f"alkynol precursor of {label}", e),
        part("paraformaldehyde", "reagent", "(HCHO)n", e, name="paraformaldehyde", smiles="C=O"),
        part("iPr2NH", "reagent", "i-Pr2NH", e, name="diisopropylamine", smiles="CC(C)NC(C)C"),
        part("CuBr", "catalyst", "CuBr", e, name="copper(I) bromide", smiles="[Cu]Br"),
        part("dioxane", "solvent", "dioxane", e, smiles="O1CCOCC1"),
        part(label, "product", label, e, name=f"3,4-allenol {label}", smiles=smi),
    ]
    steps = [
        {"step_id": "alkynol_formation", "participant_ids": [f"carbonyl_{label}", "allenyl_MgBr", f"homo_propargyl_{label}"],
         "conditions": [fld("initial_temperature", qty(-40, "°C"), e), fld("operation", "warm from -40 °C to room temperature", e)]},
        {"step_id": "crabbe_homologation", "participant_ids": [f"homo_propargyl_{label}", "paraformaldehyde", "iPr2NH", "CuBr", "dioxane", label],
         "conditions": [fld("temperature", "reflux", e)]},
    ]
    records.append(record(f"scheme2_{label}_preparation", "substrate_scope_entry", e, participants, steps,
                          [fld("reported_yield", qty(yld, "%"), e, [label])],
                          notes=["Scheme 2 reports the final allene yield; precursor structures are defined through the printed R groups."],
                          unresolved=["Absolute quantities, durations, atmosphere, workup, purification, and yield basis are missing.", "Intermediate and product structures remain unverified."]))

for label, r1, r2, yld in [("1s", "n-C6H13", "Me", None), ("1t", "n-C5H11", "4-ClC6H4", 75)]:
    e = ev(2)
    participants = [
        part(f"propargyl_bromide_{label}", "reactant", f"propargylic bromide for {label}", e, name=f"R1={r1}"),
        part(f"aldehyde_{label}", "reactant", f"aldehyde for {label}", e, name=f"R2CHO, R2={r2}"),
        part("SnCl2", "reagent", "SnCl2", e, name="tin(II) chloride", smiles="Cl[Sn]Cl"),
        part("NaI", "reagent", "NaI", e, name="sodium iodide", smiles="[Na+].[I-]"),
        part("DMF", "solvent", "DMF", e, smiles="CN(C)C=O"),
        part(label, "product", label, e, name=f"2,3-allenol {label}", smiles=SMILES_1[label]),
    ]
    outcomes = [fld("reported_yield", qty(yld, "%") if yld is not None else None, e, [label])]
    records.append(record(f"scheme3_{label}_preparation", "substrate_scope_entry", e, participants,
                          [{"step_id": "allenol_formation", "participant_ids": [p["entity_id"] for p in participants],
                            "conditions": [fld("temperature", qty(0, "°C"), e)]}], outcomes,
                          unresolved=["Absolute quantities, duration, atmosphere, workup, purification, and yield basis are missing; Scheme 3 prints no yield for 1s.", "Candidate structures remain unverified."]))

e = ev(2)
records.append(record("prose_1u_dibal_reduction", "reported_experiment", e,
                      [part("ethyl_allenoate_1u", "reactant", "ethyl 2-methyl-4-phenyl-2,3-butadienoate", e),
                       part("DIBAL-H", "reagent", "DIBAL-H", e, name="diisobutylaluminum hydride"),
                       part("1u", "product", "1u", e, name="2-methyl-4-phenylbuta-2,3-dienol", smiles=SMILES_1["1u"])],
                      [{"step_id": "reduction", "participant_ids": ["ethyl_allenoate_1u", "DIBAL-H", "1u"], "conditions": []}],
                      [fld("reported_yield", None, e, ["1u"])],
                      notes=["The paper states that 1u was prepared by DIBAL-H reduction and cites reference 22."],
                      unresolved=["No quantities, solvent, time, temperature, atmosphere, workup, purification, or yield are reported here.", "Candidate structures remain unverified."]))


def procedure_notes(group):
    if group == "aliphatic":
        return ["Typical Procedure I applies to 3a-g and 3p-r; petroleum ether/ethyl ether or ethyl acetate (10:1) was used for flash chromatography."]
    return ["Products 3h-o followed Typical Procedure I except for 0.5 h reaction time, direct evaporation before flash chromatography, and DCM/petroleum ether 5:1 eluent."]


def main_conditions(evidence, time_h, solvent="CH3CN", pressure="100 psi CO", temperature=True, extra=None):
    cs = []
    if temperature:
        cs.append(fld("temperature", {"minimum": 30, "maximum": 35, "unit": "°C", "raw_text": "30-35 °C"}, evidence))
    if time_h is not None:
        cs.append(fld("time", qty(time_h, "h"), evidence))
    if pressure is not None:
        cs.append(fld("CO_pressure", pressure, evidence))
        cs.append(fld("atmosphere", "CO", evidence))
    if extra:
        cs.extend(extra)
    return cs


# Tables 1 and 3; the exact Conditions-A row is represented once.
table1 = [
    (1, "dioxane", 18, False), (2, "toluene", 19, False), (3, "benzene", "trace", False),
    (4, "DMF", 0, False), (5, "CH2Cl2", 57, False), (6, "THF", 65, False),
    (8, "THF", 66, True), (9, "CH3CN", 70, True),
]
for entry, solvent, yld, has_bq in table1:
    e = ev(3)
    ps = common_main_participants("1a", "3a", e, SMILES_1["1a"], SMILES_3["3a"], solvent=solvent, bq=0.5 if has_bq else None)
    outcomes = [fld("isolated_yield", qty(yld, "%") if isinstance(yld, (int, float)) else yld, e, ["3a"]),
                fld("yield_measurement_basis", "isolated", e, ["3a"])]
    records.append(record(f"table1_entry{entry}", "optimization_entry", e, ps,
                          [{"step_id": "chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps],
                            "conditions": main_conditions(e, 1)}], outcomes,
                          unresolved=["Table 1 omits absolute quantities and compound-specific workup details.", "All candidate structures remain unverified."]))

table3 = [
    ("1a", "3a", 1, 66), ("1b", "3b", 1, 65), ("1c", "3c", 1, 66),
    ("1d", "3d", 1, 69), ("1e", "3e", 1, 74), ("1f", "3f", 1, 70),
    ("1g", "3g", 1, 70), ("1h", "3h", 0.5, 62), ("1i", "3i", 0.5, 66),
    ("1j", "3j", 0.5, 67), ("1k", "3k", 0.5, 69), ("1l", "3l", 0.5, 70),
    ("1m", "3m", 0.5, 65), ("1n", "3n", 0.5, 66), ("1o", "3o", 0.5, 50),
    ("1p", "3p", 1, 59), ("1q", "3q", 1, 24), ("1r", "3r", 1, 42),
]
for idx, (sub, prod, tm, yld) in enumerate(table3, 1):
    pages = [3]
    if sub == "1a": pages.append(5)
    if sub == "1k": pages.extend([4, 5])
    if sub in {"1h", "1i", "1j", "1l", "1m", "1n", "1o"}: pages.append(5)
    e = ev(*pages)
    exact = {}
    if sub == "1a":
        exact = {
            "1a": [("mass", 92, "mg"), ("amount", 0.50, "mmol")],
            "CuCl2": [("mass", 336, "mg"), ("amount", 2.50, "mmol")],
            "PdCl2": [("mass", 5, "mg"), ("amount", 0.028, "mmol")],
            "Et3N": [("mass", 102, "mg"), ("amount", 1.01, "mmol")],
            "solvent": [("volume", 6, "mL")],
            "3a": [("isolated_product_mass", 82, "mg")],
        }
    ps = common_main_participants(sub, prod, e, SMILES_1[sub], SMILES_3[prod], exact=exact)
    conditions = main_conditions(e, tm)
    if sub == "1a":
        conditions += [fld("operation", "autoclave flushed three times with 150 psi CO, then charged to 100 psi CO", e),
                       fld("workup", "vent excess CO, dilute with Et2O, filter through a short silica-gel column, evaporate", e),
                       fld("purification", "flash chromatography on silica gel; petroleum ether/ethyl ether 10:1", e)]
    elif sub in {"1h", "1i", "1j", "1k", "1l", "1m", "1n", "1o"}:
        conditions += [fld("operation", "reaction mixture evaporated directly before flash chromatography", e),
                       fld("purification", "flash chromatography on silica gel; dichloromethane/petroleum ether 5:1", e)]
    else:
        conditions.append(fld("purification", "flash chromatography; petroleum ether/ethyl ether or ethyl acetate 10:1", e))
    evidence_note = []
    rid = f"table3_entry{idx}_{prod}"
    if sub == "1a":
        rid = "conditionsA_1a_to_3a"
        evidence_note.append("This record merges Table 1 entry 7, Table 3 entry 1, and Typical Procedure I because all report 1a to 3a under the same Conditions A with 66% isolated yield.")
    if sub == "1k":
        evidence_note.append("Table 3 entry 11 and Table 4 entry 5 both report DCM/PE 5:1 and 69%; they are represented once here with both evidence locations.")
    records.append(record(rid, "substrate_scope_entry", e, ps,
                          [{"step_id": "chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
                          [fld("isolated_yield", qty(yld, "%"), e, [prod]), fld("yield_measurement_basis", "isolated", e, [prod])],
                          notes=evidence_note + procedure_notes("aryl" if 8 <= idx <= 15 else "aliphatic"),
                          unresolved=["Atmosphere is defined by the CO operation, but other missing compound-specific quantities were not inferred.", "All candidate structures and stereochemical assignments remain unverified."]))

# Three explicitly failed Conditions-A substrates from the prose.
for sub in ["1s", "1t", "1u"]:
    e = ev(3)
    ps = common_main_participants(sub, f"expected_product_from_{sub}", e, SMILES_1[sub], None)
    records.append(record(f"failed_conditionsA_{sub}", "substrate_scope_entry", e, ps,
                          [{"step_id": "attempted_chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": main_conditions(e, None)}],
                          [fld("expected_product_result", "failed to undergo transformation", e, [f"expected_product_from_{sub}"]),
                           fld("starting_material_conversion", "starting material completely consumed", e, [sub])],
                          notes=["The three substrates are described collectively as 2-substituted, terminally substituted, or 2,4-disubstituted 2,3-allenols."],
                          unresolved=["Individual reaction duration, byproduct identities, workup, purification, and analytical basis are not reported.", "Expected-product structures remain unverified."]))

# Table 2 pressure/catalyst/base screen.
table2 = [(1, 3, 2, "100 psi", 60), (2, 10, 2, "100 psi", 63), (3, 5, 2, "1 atm (CO balloon)", 55),
          (4, 5, 2, "200 psi", 61), (5, 5, 1, "100 psi", 59), (6, 5, 3, "100 psi", 52)]
for entry, pd, baseeq, pressure, yld in table2:
    e = ev(3)
    ps = common_main_participants("1a", "3a", e, SMILES_1["1a"], SMILES_3["3a"], pd=pd, et3n=baseeq)
    records.append(record(f"table2_entry{entry}", "optimization_entry", e, ps,
                          [{"step_id": "chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps],
                            "conditions": main_conditions(e, 1, pressure=pressure)}],
                          [fld("isolated_yield", qty(yld, "%"), e, ["3a"]), fld("yield_measurement_basis", "isolated", e, ["3a"])],
                          unresolved=["Table 2 omits absolute quantities, workup, and purification.", "All candidate structures remain unverified."]))

# Table 4: five additional purification conditions; entry 5 is merged with Table 3 entry 11.
table4 = [(1, "1:1", 34, "filtered through a short silica-gel column before flash chromatography"),
          (2, "2:1", 53, "reaction mixture evaporated directly before flash chromatography"),
          (3, "3:1", 64, "reaction mixture evaporated directly before flash chromatography"),
          (4, "4:1", 68, "reaction mixture evaporated directly before flash chromatography"),
          (6, "6:1", 68, "reaction mixture evaporated directly before flash chromatography")]
for entry, ratio, yld, operation in table4:
    e = ev(4)
    ps = common_main_participants("1k", "3k", e, SMILES_1["1k"], SMILES_3["3k"])
    conditions = main_conditions(e, 0.5) + [fld("operation", operation, e),
                                            fld("purification", f"flash chromatography on silica gel; DCM/petroleum ether {ratio}", e)]
    records.append(record(f"table4_entry{entry}", "optimization_entry", e, ps,
                          [{"step_id": "reaction_and_isolation", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
                          [fld("isolated_yield", qty(yld, "%"), e, ["3k"]), fld("yield_measurement_basis", "isolated", e, ["3k"])],
                          unresolved=["Absolute quantities are not reported for these purification comparisons.", "All candidate structures remain unverified."]))


def table5_participants(entry, pd, base, baseeq, additive, addeq, solvent, evidence):
    ps = common_main_participants("2a", "4a", evidence, R2["2a"][1], SMILES_4["4a"], solvent=solvent,
                                  pd=pd, et3n=baseeq, bq=addeq if additive == "BQ" else None,
                                  base=base if base in {"Et3N", "NaOAc"} else None)
    # Entry 7 uses triethylamine as the solvent, not as a base.
    if solvent == "Et3N" and not any(p["entity_id"] == "solvent_Et3N" for p in ps):
        ps.append(part("solvent_Et3N", "solvent", "Et3N", evidence, smiles="CCN(CC)CC"))
    return ps


# Table 5; entry 10 is merged into Table 6 entry 1 below.
table5 = [
    (1, 10, "300 psi", None, None, None, None, "THF", 4, "complicated"),
    (2, 5, "100 psi", "Et3N", 2, None, None, "CH3CN", 1, 35),
    (3, 5, "60 psi", "NaOAc", 3, None, None, "CH3CN", 2, 35),
    (4, 10, "60 psi", "NaOAc", 3, None, None, "HOAc", 3, 33),
    (5, 10, "60 psi", "NaOAc", 3, None, None, "dioxane", 2, "NR"),
    (6, 10, "60 psi", "NaOAc", 3, None, None, "DMF", 2, 0),
    (7, 10, "60 psi", None, None, None, None, "Et3N", 2, "NR"),
    (8, 5, "100 psi", "Et3N", 2, None, None, "THF", 1, 48),
    (9, 5, "100 psi", "Et3N", 2, "BQ", 0.1, "THF", 1, 50),
    (11, 5, "100 psi", "Et3N", 2, "BQ", 1.0, "THF", 1, 53),
]
for entry, pd, pressure, base, baseeq, additive, addeq, solvent, tm, yld in table5:
    e = ev(4)
    ps = table5_participants(entry, pd, base, baseeq, additive, addeq, solvent, e)
    outcomes = []
    if isinstance(yld, (int, float)):
        outcomes += [fld("isolated_yield", qty(yld, "%"), e, ["4a"]), fld("yield_measurement_basis", "isolated", e, ["4a"])]
    else:
        outcomes.append(fld("reaction_result", yld, e, ["4a"]))
    if entry in {5, 7}:
        outcomes.append(fld("starting_material_recovery", "starting material not completely consumed", e, ["2a"]))
    if entry == 6:
        outcomes.append(fld("starting_material_conversion", "no starting material was left", e, ["2a"]))
    records.append(record(f"table5_entry{entry}", "optimization_entry", e, ps,
                          [{"step_id": "chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps],
                            "conditions": main_conditions(e, tm, pressure=pressure)}], outcomes,
                          unresolved=["Table 5 omits absolute quantities, workup, and purification; NR and complicated are preserved qualitatively.", "All candidate structures remain unverified."]))

# Table 6. Entry 1 also represents Table 5 entry 10; entry 4 includes the exact Typical Procedure II.
table6_yields = {"2a": 53, "2b": 46, "2c": 55, "2d": 54, "2e": 55, "2f": 43, "2g": 53, "2h": 30, "2i": 23}
for idx, (sub, yld) in enumerate(table6_yields.items(), 1):
    prod = f"4{sub[1:]}"
    pages = [4]
    if sub == "2d": pages.append(6)
    e = ev(*pages)
    exact = {}
    if sub == "2d":
        exact = {
            "2d": [("mass", 197, "mg"), ("amount", 1.01, "mmol")],
            "CuCl2": [("mass", 672, "mg"), ("amount", 5.00, "mmol")],
            "PdCl2": [("mass", 9, "mg"), ("amount", 0.051, "mmol")],
            "BQ": [("mass", 54, "mg"), ("amount", 0.50, "mmol")],
            "Et3N": [("mass", 202, "mg"), ("amount", 2.00, "mmol")],
            "solvent": [("volume", 12, "mL")],
            "4d": [("isolated_product_mass", 141, "mg")],
        }
    ps = common_main_participants(sub, prod, e, R2[sub][1], SMILES_4[prod], solvent="THF", bq=0.5, exact=exact)
    conditions = main_conditions(e, 1)
    if sub == "2d":
        conditions += [fld("operation", "autoclave flushed three times with 150 psi CO, then charged to 100 psi CO", e),
                       fld("workup", "vent excess CO, dilute with Et2O, filter through a short silica-gel column, evaporate", e),
                       fld("purification", "flash chromatography on silica gel; dichloromethane/petroleum ether 1:1", e)]
    rid = f"table6_entry{idx}_{prod}"
    notes = ["Table 6 scope entry under Conditions B."]
    if sub == "2a":
        rid = "conditionsB_2a_to_4a"
        notes.append("This record merges Table 5 entry 10 and Table 6 entry 1 because both report the same Conditions-B 2a-to-4a reaction and 53% isolated yield.")
    records.append(record(rid, "substrate_scope_entry", e, ps,
                          [{"step_id": "chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
                          [fld("isolated_yield", qty(yld, "%"), e, [prod]), fld("yield_measurement_basis", "isolated", e, [prod])],
                          notes=notes,
                          unresolved=["Except for 4d, compound-specific absolute quantities, workup, and purification are not restated.", "All candidate structures remain unverified."]))

# Table 7 enantioenriched scope; entry 1 is enriched with page-6 exact quantities.
table7 = [
    (1, "(R)-1a", "(R)-3a", ">99%", 70, 99, False),
    (2, "(S)-1a", "(S)-3a", "97%", 69, 97, False),
    (3, "(R)-1b", "(R)-3b", ">99%", 68, 99, False),
    (4, "(S)-1b", "(S)-3b", ">99%", 69, 99, False),
    (5, "(R)-1c", "(R)-3c", ">99%", 69, 99, False),
    (6, "(S)-1c", "(S)-3c", "96%", 69, 96, False),
    (7, "(R)-1d", "(R)-3d", ">99%", 64, 99, True),
    (8, "(S)-1d", "(S)-3d", "93%", 70, 93, False),
]
for entry, sub, prod, start_ee, yld, prod_ee, use_b in table7:
    base_sub = sub[-2:]
    base_prod = prod[-2:]
    pages = [5]
    if entry == 1: pages.append(6)
    e = ev(*pages)
    exact = {}
    if entry == 1:
        exact = {
            sub: [("mass", 182, "mg"), ("amount", 1.00, "mmol"), ("starting_material_ee", qty(99, "%", qualifier="gt", raw_text=">99%"), None)],
            "CuCl2": [("mass", 673, "mg"), ("amount", 5.01, "mmol")],
            "PdCl2": [("mass", 9, "mg"), ("amount", 0.051, "mmol")],
            "Et3N": [("mass", 202, "mg"), ("amount", 2.00, "mmol")],
            "solvent": [("volume", 12, "mL")],
            prod: [("isolated_product_mass", 172, "mg")],
        }
    # exact tuple handling for pre-structured ee.
    sub_amounts = []
    for item in exact.get(sub, []):
        if item[2] is None:
            sub_amounts.append(fld(item[0], item[1], e))
        else:
            sub_amounts.append(amount(item[0], item[1], item[2], e))
    exact2 = {k: v for k, v in exact.items() if k != sub}
    solvent = "THF" if use_b else "CH3CN"
    bq = 0.5 if use_b else None
    ps = common_main_participants(sub, prod, e, SMILES_1[base_sub], SMILES_3[base_prod], solvent=solvent, bq=bq, exact=exact2)
    ps[0]["amounts"] = sub_amounts or [fld("starting_material_ee", start_ee, e)]
    if not any(x["name"] == "starting_material_ee" for x in ps[0]["amounts"]):
        ps[0]["amounts"].append(fld("starting_material_ee", start_ee, e))
    conditions = main_conditions(e, 1)
    if entry == 1:
        conditions += [fld("operation", "following Typical Procedure I", e),
                       fld("workup", "vent excess CO, dilute with Et2O, filter through a short silica-gel column, evaporate", e),
                       fld("purification", "flash chromatography on silica gel", e)]
    outcomes = [fld("isolated_yield", qty(yld, "%"), e, [prod]),
                fld("yield_measurement_basis", "isolated", e, [prod]),
                fld("product_ee", qty(prod_ee, "%"), e, [prod]),
                fld("ee_measurement_basis", "HPLC", e, [prod])]
    notes = ["No racemization was observed according to the authors."]
    if use_b:
        notes.append("Table 7 footnote c states that entry 7 was carried out under Conditions B, despite the Conditions-A reaction header.")
    if entry == 1:
        notes += ["HPLC: Chiralcel OJ-H, n-hexane/i-PrOH 90:10, 0.7 mL/min, 214 nm; tR 12.5 min minor and 14.0 min major.",
                  "Specific rotation [alpha]D20 -32.9 (c 1.05, CHCl3)."]
    records.append(record(f"table7_entry{entry}_{prod.replace('(','').replace(')','')}", "substrate_scope_entry", e, ps,
                          [{"step_id": "enantioenriched_chlorocyclocarbonylation", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
                          outcomes, notes=notes,
                          unresolved=["Absolute configuration and every constitutional/stereochemical candidate remain machine-unverified.", "Compound-specific operational details are missing except for entry 1."]))

# Scheme 4 is a proposed catalytic mechanism, not a set of executed experiments.
e = ev(4, 5)
mech_parts = [
    part("allenol_1_or_2", "reactant", "1 or 2", e, name="2,3- or 3,4-allenol"),
    part("PdCl2", "catalyst", "PdCl2", e, smiles="[Cl-].[Cl-].[Pd+2]"),
    part("M1", "unspecified_agent", "M1", e, name="coordination complex"),
    part("M2", "unspecified_agent", "M2", e, name="cyclic vinylic chloropalladium intermediate"),
    part("CO", "reagent", "CO", e, smiles="[C-]#[O+]"),
    part("Et3N", "reagent", "Et3N", e, smiles="CCN(CC)CC"),
    part("M3", "unspecified_agent", "M3", e, name="five-membered metallocyclic intermediate"),
    part("M4", "unspecified_agent", "M4", e, name="six-membered metallocyclic intermediate"),
    part("3_or_4", "product", "3 or 4", e, name="chloromethyl lactone product"),
]
records.append(record("scheme4_proposed_mechanism", "mechanism", e, mech_parts,
                      [{"step_id": "coordination_and_chlorometalation", "participant_ids": ["allenol_1_or_2", "PdCl2", "M1", "M2"],
                        "conditions": [fld("operation", "selective terminal-double-bond coordination followed by regioselective chlorometalation", e)]},
                       {"step_id": "CO_insertion_and_reductive_elimination", "participant_ids": ["M2", "CO", "Et3N", "M3", "M4", "3_or_4"],
                        "conditions": [fld("operation", "CO coordination/insertion, HCl trapping by Et3N, and reductive elimination", e)]},
                       {"step_id": "catalyst_regeneration", "participant_ids": ["PdCl2"],
                        "conditions": [fld("operation", "Pd(0) is oxidized by oxidant to regenerate PdCl2", e)]}],
                      [], notes=["The authors explicitly present Scheme 4 as a rationale; M1-M4 are proposed intermediates."],
                      unresolved=["Mechanistic intermediate structures and the identity/contribution of the oxidant in each substrate class remain unverified."]))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [{
                "region": "full original page: title, graphical abstract, abstract, and introduction",
                "finding": "The graphical abstract is a generic summary of the later Conditions A/B chemistry and was not duplicated as a row-level experiment; no table or compound-specific procedure occurs on this page.",
                "evidence_ids": ev(1),
            }],
            "record_ids": [],
            "unresolved": ["Abstract-level generic structures do not define individual substrate identities or procedures."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1", "finding": "Two-stage carbonyl-to-propargylic-alcohol/Crabbe homologation series inventoried as 18 distinct starting-material preparations (1a-r).", "evidence_ids": ev(2)},
                {"region": "middle-right Scheme 2", "finding": "Two-stage carbonyl/allenylmagnesium-bromide and Crabbe homologation series inventoried as nine preparations (2a-i).", "evidence_ids": ev(2)},
                {"region": "lower-right Scheme 3 and preparation prose", "finding": "Two SnCl2/NaI allenol preparations (1s,t) and the prose-only DIBAL-H preparation of 1u were extracted; cited background reactions were not promoted to present-paper experiments.", "evidence_ids": ev(2)},
            ],
            "record_ids": [r["record_id"] for r in records if r["record_id"].startswith(f"{DOC}:scheme1_") or r["record_id"].startswith(f"{DOC}:scheme2_") or r["record_id"].startswith(f"{DOC}:scheme3_") or r["record_id"].endswith("prose_1u_dibal_reduction")],
            "unresolved": ["Scheme preparations omit many quantities and operations; 1s has no printed yield.", "The cited procedures and SI are not supplied or associated."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnote", "finding": "All nine solvent/additive optimization rows inventoried; Table 1 entry 7 is merged with Table 3 entry 1 and Typical Procedure I.", "evidence_ids": ev(3)},
                {"region": "upper-right Table 2 and footnote", "finding": "All six PdCl2/Et3N/CO-pressure optimization rows extracted, including the CO-balloon footnote.", "evidence_ids": ev(3)},
                {"region": "right-center Table 3 and footnote", "finding": "All 18 2,3-allenol scope rows extracted; original-image review establishes 24% for 3q. Three additional failed 1s-u cases in the prose were extracted separately.", "evidence_ids": ev(3)},
            ],
            "record_ids": [r["record_id"] for r in records if any(x in r["record_id"] for x in [":table1_", ":table2_", ":table3_", ":conditionsA_", ":failed_conditionsA_"])],
            "unresolved": ["Most rows omit absolute quantities and compound-specific workup; complex structures remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 4 and footnotes", "finding": "Six purification/eluent comparisons inventoried; entry 5 is merged with Table 3 entry 11 because both report the same 5:1 DCM/PE isolation and 69% yield.", "evidence_ids": ev(4)},
                {"region": "middle-left Table 5 and footnotes", "finding": "All 11 3,4-allenol optimization rows inventoried; original-image review establishes 35% in entries 2 and 3. Entry 10 is merged with Table 6 entry 1.", "evidence_ids": ev(4)},
                {"region": "upper-right Table 6", "finding": "All nine 3,4-allenol scope rows extracted; 4d is linked to its page-6 exact procedure.", "evidence_ids": ev(4)},
                {"region": "lower-right mechanistic discussion", "finding": "Opening discussion of proposed Scheme 4 linked to one mechanism record, not treated as an executed reaction.", "evidence_ids": ev(4)},
            ],
            "record_ids": [r["record_id"] for r in records if any(x in r["record_id"] for x in [":table4_", ":table5_", ":table6_", ":conditionsB_", ":scheme4_"]) or r["record_id"].endswith("table3_entry11_3k")],
            "unresolved": ["Table 5 NR/complicated results are qualitative; most Table 4-6 rows omit absolute quantities and workup."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 7 and footnotes", "finding": "All eight enantioenriched-substrate rows extracted with starting/product ee and isolated yields; entry 7's Conditions-B footnote is retained.", "evidence_ids": ev(5)},
                {"region": "upper-right Scheme 4", "finding": "Proposed M1-M4 catalytic pathway classified as a mechanism and not split into experiments.", "evidence_ids": ev(5)},
                {"region": "lower-right Typical Procedure I", "finding": "Exact 1a/CuCl2/PdCl2/MeCN/Et3N quantities, CO operations, workup, purification, product mass, and 66% isolated yield merged into the Conditions-A 1a-to-3a record; the 3h-o procedural exception is linked to those scope records.", "evidence_ids": ev(5)},
            ],
            "record_ids": [r["record_id"] for r in records if ":table7_" in r["record_id"] or r["record_id"].endswith("scheme4_proposed_mechanism") or r["record_id"].endswith("conditionsA_1a_to_3a") or any(r["record_id"].endswith(f"table3_entry{i}_3{x}") for i, x in zip(range(8,16), list("hijklmno")))],
            "unresolved": ["Only one enantioenriched case has exact quantities in the supplied main text; SI is mentioned but unassociated."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "left column Typical Procedure II", "finding": "Exact preparation of 4d merged into Table 6 entry 4 with quantities, CO operations, workup, purification, product mass, and 54% isolated yield.", "evidence_ids": ev(6)},
                {"region": "upper-right enantioenriched (5R)-3a procedure", "finding": "Exact (R)-1a preparation merged into Table 7 entry 1 with quantities, 172 mg/70% isolated yield, 99% ee, HPLC conditions, and optical rotation.", "evidence_ids": ev(6)},
                {"region": "lower-right SI availability statement", "finding": "The statement that SI is available online was recorded as availability only; no SI source was supplied or associated.", "evidence_ids": ev(6)},
            ],
            "record_ids": [f"{DOC}:table6_entry4_4d", f"{DOC}:table7_entry1_R-3a"],
            "unresolved": ["No SI PDF or CIF was supplied; missing external procedures and crystallographic files were not inferred."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
