#!/usr/bin/env python3
"""Build source-faithful machine records for doc_960bc2f9d5111dda, PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_960bc2f9d5111dda"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence, targets=None):
    x = {"name": name, "fact": fact(value, evidence)}
    if targets:
        x["target_entity_ids"] = list(targets)
    return x


def amt(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit, **extra}
    return fld(name, value, evidence)


SMILES = {
    "I2": "[I][I]", "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "Cs2CO3": "[Cs+].[Cs+].[O-]C([O-])=O", "NIS": "O=C1CCC(=O)N1I",
    "MeCN": "CC#N", "water": "O", "DMSO": "CS(C)=O",
    "toluene": "Cc1ccccc1", "CHCl3": "ClC(Cl)Cl", "CH2Cl2": "ClCCl",
    "DCE": "ClCCCl", "cyclohexane": "C1CCCCC1", "hexane": "CCCCCC",
    "THF": "C1CCOC1", "EtOH": "CCO", "pyridine": "n1ccccc1",
    "NaCN": "[Na+].[C-]#N", "NaOH": "[Na+].[OH-]", "LiAlH4": "[Li+].[AlH4-]",
    "EtCOOH": "CCC(=O)O", "triethyl_orthoacetate": "CC(OCC)(OCC)OCC",
    "TsCl": "Cc1ccc(S(=O)(=O)Cl)cc1", "BnOH": "OCC1=CC=CC=C1",
    "MeOH": "CO", "LiOH_hydrate": "[Li+].[OH-].O", "MeI": "CI",
    "Mg": "[Mg]", "nBuBr": "CCCCCBr", "CuCN": "[Cu]C#N",
    "LiBr": "[Li+].[Br-]", "MgCl2": "Cl[Mg]Cl", "DIPEA": "CCN(C(C)C)C(C)C",
    "propionyl_chloride": "CCC(=O)Cl", "EtCOCl": "CCC(=O)Cl",
    "DCC": "C(=NC1CCCCC1)=NC1CCCCC1", "DMAP": "CN(C)c1ccncc1",
    "Et2NH": "CCNCC", "propargyl_alcohol": "C#CCO", "CuI": "[Cu]I",
    "1a": "O=C(O)CCC=C=CCCCCCC",
}


def participant(entity_id, role, label, evidence, amounts=None, smiles_key=None, name=None):
    smiles = SMILES.get(smiles_key or label)
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


def record(rid, kind, evidence, participants, conditions, outcomes, notes=None, unresolved=None):
    if kind in {"reported_experiment", "optimization_entry", "substrate_scope_entry"}:
        present = {x[0] for x in conditions}
        for missing in ("temperature", "time", "atmosphere", "workup", "purification"):
            if missing not in present:
                conditions.append((missing, None))
    step_fields = [fld(name, value, evidence) for name, value in conditions]
    rec = {
        "record_id": f"{DOC}:{rid}", "document_id": DOC, "source_reaction_id": rid,
        "record_kind": kind, "status": "candidate", "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)), "participants": participants,
        "steps": [] if kind == "mechanism" else [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": step_fields,
        }],
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none", "reviewer": None, "checked_fields": [],
            "unresolved": (unresolved or []) + [
                "Machine-extracted chemistry and candidate structures require source review.",
                "No supporting-information file was supplied or explicitly associated.",
            ],
        },
    }
    return rec


def pset(substrate, product, evidence, reagents=(), solvent=None):
    ps = [participant("substrate", "reactant", substrate, evidence,
                      smiles_key=substrate if substrate in SMILES else None),
          participant("product", "product", product, evidence)]
    for i, (label, amount_fields) in enumerate(reagents, 1):
        ps.append(participant(f"reagent{i}", "reagent", label, evidence,
                              amounts=amount_fields, smiles_key=label))
    if solvent:
        label, amount_fields = solvent
        ps.append(participant("solvent", "solvent", label, evidence,
                              amounts=amount_fields, smiles_key=label))
    return ps


records = []

# Page 2, Table 1: thirteen independent optimization entries.
t1 = [
    (1, "MeCN", "r.t.", 40, "min", 92, "87:13", 2.0, None),
    (2, "MeCN/water (40:1)", -30, 19, "h", 73, "92:8", 2.0, None),
    (3, "DMSO", "r.t.", 48, "min", 80, "91:9", 2.0, None),
    (4, "toluene", "r.t.", 40, "min", 91, "97:3", 2.0, None),
    (5, "CHCl3", "r.t.", 35, "min", 89, "96:4", 2.0, None),
    (6, "CH2Cl2", "r.t.", 50, "min", 84, "96:4", 2.0, None),
    (7, "CH2Cl2", -20, 2.5, "h", 99, "97:3", 2.0, None),
    (8, "CH2Cl2", -20, 2.5, "h", 100, "95:5", 2.0, 2.0),
    (9, "DCE", "r.t.", 40, "min", 94, "97:3", 2.0, None),
    (10, "cyclohexane", "r.t.", 45, "min", 92, "98:2", 2.0, None),
    (11, "hexane", "r.t.", 30, "min", 70, "98:2", 2.0, None),
    (12, "cyclohexane", "r.t.", 50, "min", 92, "98:2", 1.5, None),
    (13, "cyclohexane", "r.t.", 35, "min", 92, "97:3", 1.2, None),
]
for entry, solvent, temp, ntime, tunit, yld, ratio, i2eq, k2eq in t1:
    e = ev(2)
    reagents = [("I2", [amt("equivalents", i2eq, "equiv", e)])]
    if k2eq is not None:
        reagents.append(("K2CO3", [amt("equivalents", k2eq, "equiv", e)]))
    ps = pset("1a", "2a", e, reagents, (solvent, []))
    outs = [fld("2a_NMR_yield", {"number": yld, "unit": "%"}, e, ["product"]),
            fld("2a_Z_E_ratio", ratio, e, ["product"]),
            fld("yield_measurement_basis", "400 MHz 1H NMR spectroscopy", e, ["product"])]
    if entry == 1:
        ps.append(participant("product_3a", "product", "7-membered lactone 3a", e))
        outs.append(fld("3a_formation", "not observed", e, ["product_3a"]))
    records.append(record(f"table1_entry{entry}", "optimization_entry", e, ps,
                          [("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}),
                           ("time", {"number": ntime, "unit": tunit})], outs,
                          unresolved=["Table 1 does not state scale, atmosphere, workup, or purification."]))

# Page 2, Table 2: ten scope rows.
t2 = [
    (1, "1a (R1=n-C6H13, R2=H, R3=H)", "2a", "A", 83, "98:2", "isolated"),
    (2, "1b (R1=n-C5H11, R2=H, R3=H)", "2b", "A", 85, "98:2", "isolated"),
    (3, "1c (R1=n-C4H9, R2=H, R3=H)", "2c", "A", 85, "97:3", "isolated"),
    (4, "1d (R1=CH3, R2=H, R3=H)", "2d", "A", 79, "98:2", "isolated"),
    (5, "1e (R1=C2H5, R2=H, R3=n-C4H9)", "2e", "A", 75, "99:1", "isolated"),
    (6, "1f (R1=H, R2=H, R3=n-C4H9)", "2f", "A", 19, "table dash (—)", "300 MHz 1H NMR"),
    (7, "1f (R1=H, R2=H, R3=n-C4H9)", "2f", "B", 87, "table dash (—)", "isolated"),
    (8, "1g (R1/R2=-(CH2)5-, R3=H)", "2g", "A", "trace", "table dash (—)", "300 MHz 1H NMR"),
    (9, "1g (R1/R2=-(CH2)5-, R3=H)", "2g", "B", 73, "table dash (—)", "isolated"),
    (10, "1h (R1=C2H5, R2=C2H5, R3=H)", "2h", "B", 88, "table dash (—)", "isolated"),
]
for entry, substrate, product, cond, yld, ratio, basis in t2:
    e = ev(2)
    reagents = [("I2", [amt("equivalents", 1.5, "equiv", e)])]
    if cond == "B":
        reagents.append(("K2CO3", [amt("equivalents", 1, "equiv", e)]))
    ps = pset(substrate, product, e, reagents, ("cyclohexane", []))
    yvalue = yld if isinstance(yld, str) else {"number": yld, "unit": "%"}
    records.append(record(f"table2_entry{entry}", "substrate_scope_entry", e, ps,
                          [("temperature", "r.t."), ("time", {"number": 1, "unit": "h"})],
                          [fld("reported_yield", yvalue, e, ["product"]),
                           fld("Z_E_ratio", ratio, e, ["product"]),
                           fld("yield_measurement_basis", basis, e, ["product"])],
                          unresolved=["Table 2 does not state reaction scale, atmosphere, workup, or purification."]))

# Scheme 1 route to optically active acids. Each drawn operation is a distinct stage.
scheme1_variants = [
    ("a", "(R)-(+)-4a (R=n-C6H13, 99% ee)", "ethyl (R)-undeca-3,4-dienoate", "(R)-(−)-5a", "(R)-(−)-6a", "(R)-(−)-1a", 35),
    ("b", "(R)-(+)-4b (R=n-C5H11, 97% ee)", "ethyl allenoate from 4b", "(R)-(−)-5b", "(R)-(−)-6b", "(R)-(−)-1b", 29),
]
for suffix, start, ester, alcohol, nitrile, acid, route_yield in scheme1_variants:
    e3 = ev(3)
    detailed = ev(5) + ev(6) if suffix == "a" else []
    e = list(dict.fromkeys(e3 + detailed))
    # a) Johnson-Claisen-type rearrangement to the allenoate.
    ps = pset(start, ester, e, [("triethyl_orthoacetate", []), ("EtCOOH", [])])
    cond = [("temperature", {"number": 130, "unit": "°C"}), ("time", {"number": 5, "unit": "h"}),
            ("operation", "Dean–Stark removal of ethanol and excess orthoester")]
    if suffix != "a": cond = [("temperature", None), ("time", None)]
    records.append(record(f"scheme1_{suffix}_4_to_allenoate", "reported_experiment", e, ps, cond,
                          [fld("stage_yield", None, e, ["product"])],
                          unresolved=["Scheme 1 gives no stage-specific yield for this operation."]))
    # b) Reduction to the allylic alcohol.
    ps = pset(ester, alcohol, e, [("LiAlH4", [])], ("THF", []))
    outs = [fld("combined_yield_from_propargylic_alcohol_to_alcohol",
                {"number": 50, "unit": "%"} if suffix == "a" else None, e, ["product"])]
    records.append(record(f"scheme1_{suffix}_allenoate_to_5", "reported_experiment", e, ps,
                          [("temperature", "ice-cold addition" if suffix == "a" else None),
                           ("time", {"number": 1.2, "unit": "h"} if suffix == "a" else None),
                           ("atmosphere", "N2" if suffix == "a" else None)], outs,
                          unresolved=["The stated yield for the 4a route is combined across the rearrangement and reduction."]))
    # c) Tosylation.
    ps = pset(alcohol, f"tosylate from {alcohol}", e, [("TsCl", [])], ("pyridine", []))
    records.append(record(f"scheme1_{suffix}_5_to_tosylate", "reported_experiment", e, ps,
                          [("temperature", {"minimum": 0, "maximum": 4, "unit": "°C", "raw_text": "0–4 °C"} if suffix == "a" else None),
                           ("time", {"number": 4, "unit": "h"} if suffix == "a" else None)],
                          [fld("stage_yield", None, e, ["product"])],
                          unresolved=["The tosylate was used without purification; no isolated stage yield is reported."]))
    # d) Cyanide substitution.
    ps = pset(f"tosylate from {alcohol}", nitrile, e, [("NaCN", [])], ("DMSO", []))
    outs = [fld("combined_yield_from_alcohol_to_nitrile",
                {"number": 66, "unit": "%"} if suffix == "a" else None, e, ["product"])]
    records.append(record(f"scheme1_{suffix}_tosylate_to_6", "reported_experiment", e, ps,
                          [("temperature", {"number": 20, "unit": "°C"} if suffix == "a" else None),
                           ("time", {"number": 25, "unit": "h"} if suffix == "a" else None)], outs,
                          unresolved=["The reported 66% value is combined from 5a through tosylation and cyanide substitution."] if suffix == "a" else ["No stage-specific yield is reported."]))
    # e) Nitrile hydrolysis.
    ps = pset(nitrile, acid, e, [("NaOH", [])], ("EtOH/water", []))
    outs = [fld("isolated_yield", {"number": 72, "unit": "%"} if suffix == "a" else None, e, ["product"]),
            fld("scheme_combined_route_yield", {"number": route_yield, "unit": "%"}, e, ["product"])]
    records.append(record(f"scheme1_{suffix}_6_to_1", "reported_experiment", e, ps,
                          [("temperature", {"number": 80, "unit": "°C"} if suffix == "a" else None),
                           ("time", {"number": 5, "unit": "h"} if suffix == "a" else None)], outs,
                          unresolved=["Scheme-level overall yield and the compound-specific hydrolysis yield refer to different scopes and are both retained."]))

# Scheme 2: four optically active iodolactonization experiments.
e23 = ev(2) + ev(3)
scheme2 = [
    ("i2_1a", "(R)-(−)-1a", "racemic (Z)-2a", "I2", 1.5, None, "cyclohexane", "r.t.", 74, "98:2", {"number": 0, "unit": "%"}),
    ("nis_cyclohexane_1b", "(R)-(−)-1b", "(S)-(Z)-2b and (R)-(E)-2b", "NIS", 2.0, 1.0, "cyclohexane", "r.t.", 80, "76:24", None),
    ("nis_ch2cl2_1a", "(R)-(−)-1a", "(S)-(Z)-2a and (R)-(E)-2a", "NIS", 2.0, 1.0, "CH2Cl2", -60, 86, "85:15", {"number": 99, "unit": "%"}),
    ("nis_ch2cl2_1b", "(R)-(−)-1b", "(S)-(Z)-2b and (R)-(E)-2b", "NIS", 2.0, 1.0, "CH2Cl2", -60, 91, "79:21", {"number": 98, "unit": "%"}),
]
for rid, sub, prod, iod, iod_eq, base_eq, solvent, temp, yld, ratio, ee in scheme2:
    reagents = [(iod, [amt("equivalents", iod_eq, "equiv", e23)])]
    if base_eq:
        reagents.append(("Cs2CO3", [amt("equivalents", base_eq, "equiv", e23)]))
    ps = pset(sub, prod, e23, reagents, (solvent, []))
    outs = [fld("reported_yield", {"number": yld, "unit": "%"}, e23, ["product"]),
            fld("Z_E_product_ratio", ratio, e23, ["product"])]
    if ee is not None: outs.append(fld("major_Z_isomer_ee", ee, e23, ["product"]))
    records.append(record(f"scheme2_{rid}", "reported_experiment", e23, ps,
                          [("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"})], outs,
                          unresolved=["Scheme 2 does not state duration, atmosphere, workup, purification, or yield basis."]))

# Scheme 3 is a proposed anti-iodolactonization pathway, not a reported run.
records.append(record("scheme3_anti_iodolactonization", "mechanism", ev(3), [], [], [],
                      notes=["Proposed anti iodolactonization of (R)-1a and (R)-1b with NIS via cationic allene-derived intermediates."],
                      unresolved=["Mechanistic intermediates and proton transfers are proposed, not independently observed experiments."]))

# Scheme 4: kinetic resolution of two Z/E mixtures.
for suffix, sub, prod, start_ratio, yld, ratio, ee in [
    ("2a", "(S)-(Z)-2a/(R)-(E)-2a mixture", "(S)-(+)-(Z)-2a", "85:15", 74, "99:1", 99),
    ("2b", "(S)-(Z)-2b/(R)-(E)-2b mixture", "(S)-(+)-(Z)-2b", "79:21", 63, "96:4", 98),
]:
    e = ev(3)
    eq_range = fld("equivalents", {"minimum": 0.35, "maximum": 0.45, "unit": "equiv", "raw_text": "0.35–0.45 equiv"}, e)
    loading_range = fld("catalyst_loading", {"minimum": 3.5, "maximum": 4.5, "unit": "mol%", "raw_text": "3.5–4.5 mol%"}, e)
    ps = pset(sub, prod, e,
              [("propargyl_alcohol", [eq_range]),
               ("CuI", [loading_range]),
               ("PdCl2(PPh3)2", [loading_range]),
               ("Et2NH", [eq_range])])
    records.append(record(f"scheme4_kinetic_resolution_{suffix}", "reported_experiment", e, ps,
                          [("starting_Z_E_ratio", start_ratio)],
                          [fld("isolated_yield", {"number": yld, "unit": "%"}, e, ["product"]),
                           fld("product_Z_E_ratio", ratio, e, ["product"]),
                           fld("product_ee", {"number": ee, "unit": "%"}, e, ["product"])],
                          unresolved=["Scheme 4 does not state solvent, temperature, duration, atmosphere, workup, purification, or yield basis."]))

# Page 3, Table 3.
t3 = [
    (1, "1i (R1=CH3, R2=CH3; substrate d.r. 2.0:1)", "trans-(Z)-2i", 82, "96:4", ">99:1"),
    (2, "1j (R1=CH3, R2=C2H5; substrate d.r. 2.2:1)", "trans-(Z)-2j", 78, "97:3", ">99:1"),
    (3, "1k (R1=CH3, R2=n-C3H7; substrate d.r. 2.2:1)", "trans-(Z)-2k", 82, "97:3", ">99:1"),
    (4, "1l (R1=n-C4H9, R2=CH3; substrate d.r. 3.1:1)", "trans-(Z)-2l", 76, "97:3", ">99:1"),
    (5, "1m (R1=n-C6H13, R2=n-C3H7; substrate d.r. 2.7:1)", "trans-(Z)-2m", 80, "97:3", ">99:1"),
]
for entry, sub, prod, yld, ratio, dr in t3:
    e = ev(3)
    ps = pset(sub, prod, e, [("I2", [amt("equivalents", 1.5, "equiv", e)])], ("cyclohexane", []))
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", e, ps,
                          [("temperature", "r.t."), ("time", {"number": 1, "unit": "h"})],
                          [fld("isolated_yield_after_flash_chromatography", {"number": yld, "unit": "%"}, e, ["product"]),
                           fld("crude_Z_E_ratio_by_1H_NMR", ratio, e, ["product"]),
                           fld("crude_product_dr_by_1H_NMR", dr, e, ["product"])],
                          unresolved=["Table 3 does not state scale, atmosphere, or workup."]))

# Scheme 5 route to (S)-1l and (S)-1m. The 1l route is enriched with page-6 detail.
e46 = ev(4) + ev(6)
scheme5_initial = [
    ("a", "7", "(3R,4R)-(−)-8a", "R1=CH3", 73),
    ("b", "7", "(3R,4R)-(−)-8b", "R1=n-C3H7", 53),
]
for suffix, sub, prod, variant, yld in scheme5_initial:
    e = e46 if suffix == "a" else ev(4)
    ps = pset(f"3-(trimethylsilyl)propiolaldehyde 7 ({variant})", prod, e,
              [("TMS-quinine", []), ("MgCl2", []), ("DIPEA", []),
               ("propionyl_chloride" if suffix == "a" else "acyl chloride", [])], ("CH2Cl2/diethyl ether", []))
    cond = [("temperature", {"number": -80, "unit": "°C"}), ("time", {"number": 14.5, "unit": "h"})] if suffix == "a" else []
    records.append(record(f"scheme5_7_to_8{suffix}", "reported_experiment", e, ps, cond,
                          [fld("isolated_yield", {"number": yld, "unit": "%"}, e, ["product"])],
                          unresolved=["The 8b preparation lacks compound-specific operational details on covered pages."] if suffix == "b" else []))

for suffix, sub, prod, grignard, yld in [
    ("a", "(3R,4R)-(−)-8a", "(Ra,R)-(+)-9a", "nBuMgBr", 83),
    ("b", "(3R,4R)-(−)-8b", "(Ra,R)-(−)-9b", "nC6H13MgBr", 83),
]:
    e = e46 if suffix == "a" else ev(4)
    ps = pset(sub, prod, e, [(grignard, []), ("CuCN", []), ("LiBr", [])], ("THF", []))
    yield_fields = [fld("detailed_batch_isolated_yield" if suffix == "a" else "reported_yield",
                        {"number": yld, "unit": "%"}, e, ["product"])]
    if suffix == "a":
        yield_fields.append(fld("scheme_reported_yield", {"number": 75, "unit": "%"}, e, ["product"]))
    records.append(record(f"scheme5_8{suffix}_to_9{suffix}", "reported_experiment", e, ps,
                          [("temperature", {"number": -78, "unit": "°C"}),
                           ("time", {"number": 20, "unit": "min"} if suffix == "a" else None)],
                          yield_fields,
                          unresolved=["Scheme 5 prints 75% for 9a, while the page-6 detailed batch reports 83%; the detailed batch value is retained here and the discrepancy remains unresolved."] if suffix == "a" else []))

# Detailed methylation/reduction sequence underlying Scheme 5's compressed 9a -> 10a arrow.
ps = pset("(Ra,R)-(+)-9a", "methyl (Ra,R)-2-methyl-5-(trimethylsilyl)nona-3,4-dienoate", e46,
          [("K2CO3", []), ("MeI", [])], ("DMF", []))
records.append(record("scheme5_9a_to_methyl_ester", "reported_experiment", e46, ps,
                      [("temperature", {"number": 10, "unit": "°C"}), ("time", {"number": 105, "unit": "min"})],
                      [fld("crude_yield", {"number": 91, "unit": "%"}, e46, ["product"])]))
ps = pset("methyl (Ra,R)-2-methyl-5-(trimethylsilyl)nona-3,4-dienoate", "(Ra,R)-(−)-10a", e46,
          [("LiAlH4", [])], ("THF", []))
records.append(record("scheme5_methyl_ester_to_10a", "reported_experiment", e46, ps,
                      [("temperature", None), ("time", None)],
                      [fld("isolated_yield", {"number": 93, "unit": "%"}, e46, ["product"]),
                       fld("scheme_combined_yield_from_9a_to_10a", {"number": 85, "unit": "%"}, e46, ["product"])],
                      unresolved=["The scheme compresses methylation and reduction into one 85% arrow; the detailed stage yield is 93% after a 91% methylation."]))
ps = pset("(Ra,R)-(−)-9b", "(Ra,R)-(−)-10b", ev(4), [("LiAlH4", [])], ("THF", []))
records.append(record("scheme5_9b_to_10b", "reported_experiment", ev(4), ps, [],
                      [fld("reported_yield", {"number": 70, "unit": "%"}, ev(4), ["product"])],
                      unresolved=["The covered source does not resolve whether the 70% value spans an unshown esterification as in the 9a route."]))

for suffix, alcohol, nitrile_tms, nitrile, acid, overall in [
    ("a", "(Ra,R)-(−)-10a", "(Ra,S)-3-methyl-6-trimethylsilyldeca-4,5-dienenitrile", "(S)-(−)-11a", "(S)-(+)-1l", 27),
    ("b", "(Ra,R)-(−)-10b", "TMS-protected nitrile from 10b", "(S)-11b", "(S)-(+)-1m", 17),
]:
    e = e46 if suffix == "a" else ev(4)
    tos = f"tosylate from {alcohol}"
    records.append(record(f"scheme5_10{suffix}_to_tosylate", "reported_experiment", e,
                          pset(alcohol, tos, e, [("TsCl", [])], ("pyridine", [])), [],
                          [fld("stage_yield", None, e, ["product"])],
                          unresolved=["No isolated tosylate yield is reported."]))
    records.append(record(f"scheme5_tosylate_to_tms_nitrile_{suffix}", "reported_experiment", e,
                          pset(tos, nitrile_tms, e, [("NaCN", [])], ("DMSO", [])), [],
                          [fld("stage_yield", None, e, ["product"])],
                          unresolved=["The TMS-protected nitrile was used without purification; no stage yield is reported."]))
    outs = [fld("combined_yield_from_10a_to_11a", {"number": 35, "unit": "%"}, e, ["product"]) if suffix == "a" else fld("stage_yield", None, e, ["product"])]
    records.append(record(f"scheme5_tms_nitrile_to_11{suffix}", "reported_experiment", e,
                          pset(nitrile_tms, nitrile, e, [("TBAF", [])], ("THF", [])),
                          [("temperature", {"number": 30, "unit": "°C"} if suffix == "a" else None),
                           ("time", {"number": 40, "unit": "min"} if suffix == "a" else None)], outs,
                          unresolved=["The 35% value is combined from 10a through tosylation, cyanide substitution, and desilylation."] if suffix == "a" else ["No stage-specific yield is reported."]))
    outs = [fld("isolated_yield", {"number": 77, "unit": "%"} if suffix == "a" else None, e, ["product"]),
            fld("combined_yield_from_10_to_acid", {"number": overall, "unit": "%"}, e, ["product"])]
    records.append(record(f"scheme5_11{suffix}_to_acid", "reported_experiment", e,
                          pset(nitrile, acid, e, [("NaOH", [])], ("EtOH/water", [])), [], outs,
                          unresolved=["The overall scheme yield spans multiple operations; individual hydrolysis yield is unavailable for 1m."] if suffix == "b" else []))

# Scheme 6: three chiral-center-controlled iodolactonizations under Conditions A.
for rid, sub, prod, yld, ratio in [
    ("s_1l", "(S)-(+)-1l (d.r. 1.2:1)", "(4S,5S)-(+)-(Z)-2l", 86, "98:2"),
    ("s_1m", "(S)-(+)-1m (d.r. 1.7:1)", "(4S,5S)-(+)-(Z)-2m", 72, "96:4"),
    ("r_1l", "(R)-(−)-1l (d.r. 1.2:1)", "(4R,5R)-(−)-(Z)-2l", 82, "97:3"),
]:
    e = ev(4) + ev(2)
    ps = pset(sub, prod, e, [("I2", [amt("equivalents", 1.5, "equiv", e)])], ("cyclohexane", []))
    records.append(record(f"scheme6_{rid}", "reported_experiment", e, ps,
                          [("temperature", "r.t."), ("time", {"number": 1, "unit": "h"})],
                          [fld("isolated_yield", {"number": yld, "unit": "%"}, e, ["product"]),
                           fld("Z_E_ratio", ratio, e, ["product"]),
                           fld("product_ee", {"number": 99, "unit": "%"}, e, ["product"])],
                          unresolved=["Scheme 6 does not state atmosphere, workup, purification, or yield basis beyond 'isolated' in prose."]))

# Scheme 7: route to (Ra,R)-1l and benzyl ester.
scheme7 = [
    ("7_to_8a", "7", "(3S,4S)-(+)-8a", [("TMS-quinidine", []), ("MgCl2", []), ("DIPEA", []), ("EtCOCl", [])], ("CH2Cl2", []), [], 62),
    ("8a_to_12a", "(3S,4S)-(+)-8a", "(3S,4S)-(−)-12a", [("TBAF", [])], ("THF", []), [], 51),
    ("12a_to_acid", "(3S,4S)-(−)-12a", "(Ra,S)-2-methylnona-3,4-dienoic acid", [("nC4H9MgBr", []), ("CuBr·Me2S", [])], ("THF", []), [("temperature", {"number": -78, "unit": "°C"})], 80),
    ("acid_to_10a", "(Ra,S)-2-methylnona-3,4-dienoic acid", "(Ra,S)-(−)-10a", [("LiAlH4", [])], ("THF", []), [("temperature", {"number": 0, "unit": "°C"})], 43),
    ("10a_to_tosylate", "(Ra,S)-(−)-10a", "tosylate from (Ra,S)-10a", [("TsCl", [])], ("pyridine", []), [], None),
    ("tosylate_to_11a", "tosylate from (Ra,S)-10a", "(S)-11a", [("NaCN", [])], ("DMSO", []), [], None),
    ("11a_to_1l", "(S)-11a", "(Ra,R)-(−)-1l", [("NaOH", [])], ("EtOH/water", []), [], 43),
    ("1l_to_13a", "(Ra,R)-(−)-1l", "benzyl (Ra,R)-(−)-13a", [("BnOH", []), ("DMAP", []), ("DCC", [])], ("CH2Cl2", []), [], 100),
]
for rid, sub, prod, reagents, solvent, cond, yld in scheme7:
    e = ev(4)
    outs = [fld("reported_yield", {"number": yld, "unit": "%"} if yld is not None else None, e, ["product"])]
    if rid == "11a_to_1l":
        outs[0]["name"] = "combined_yield_over_three_steps"
    if rid == "1l_to_13a":
        outs.append(fld("product_dr", "96:4", e, ["product"]))
    records.append(record(f"scheme7_{rid}", "reported_experiment", e,
                          pset(sub, prod, e, reagents, solvent), cond, outs,
                          unresolved=["The 43% value is a combined three-step yield."] if rid == "11a_to_1l" else ([] if yld is not None else ["No isolated stage yield is reported."])))

# Scheme 8: benzylation, preparative HPLC separation, and hydrolysis.
e468 = ev(4) + ev(6)
ps = pset("(R)-(−)-1l", "benzyl (R)-(−)-13a", e468,
          [("BnOH", []), ("DCC", []), ("DMAP", [])], ("CH2Cl2", []))
records.append(record("scheme8_benzylation_r_1l", "reported_experiment", e468, ps,
                      [("temperature", {"minimum": 0, "maximum": 28, "unit": "°C", "raw_text": "0–28 °C"}),
                       ("time", {"number": 10, "unit": "h"})],
                      [fld("isolated_yield", {"number": 89, "unit": "%"}, e468, ["product"]),
                       fld("scheme_product_dr", "1.1:1", e468, ["product"]),
                       fld("experimental_paragraph_product_dr", "1.2:1", e468, ["product"])],
                      unresolved=["Scheme 8 reports d.r. 1.1:1, while the page-6 paragraph reports 1.2:1; both are retained. "]))
ps = [participant("mixture", "reactant", "benzyl (R)-13a diastereomer mixture", e468),
      participant("peak1", "product", "(Sa,R)-(+)-13a, HPLC peak 1", e468),
      participant("peak2", "product", "(Ra,R)-(−)-13a, HPLC peak 2", e468)]
records.append(record("scheme8_preparative_hplc_separation", "reported_experiment", e468, ps,
                      [("operation", "CHIRALPAK IC preparative HPLC; hexane/ethyl acetate 98:2; rate 9 mL min−1"),
                       ("temperature", None), ("time", None)],
                      [fld("peak1_dr", ">99:1", e468, ["peak1"]), fld("peak2_dr", ">98:2", e468, ["peak2"])],
                      notes=["Peak 1 tR=13.7 and peak 2 tR=15.0; the displayed values lack an explicit time unit."],
                      unresolved=["The isolated quantities/yields of the separated peaks are not reported on covered pages."]))
ps = pset("(Sa,R)-(+)-13a", "(Sa,R)-(+)-1l", ev(4), [("LiOH_hydrate", [])], ("water/MeOH", []))
records.append(record("scheme8_hydrolysis_sa_r_13a", "reported_experiment", ev(4), ps,
                      [("temperature", {"number": 30, "unit": "°C"})],
                      [fld("isolated_yield", {"number": 67, "unit": "%"}, ev(4), ["product"])],
                      unresolved=["Scheme 8 does not state duration, atmosphere, workup, purification, or yield basis."]))

# Scheme 9: two allene-diastereomer experiments yielding the same stereoisomer.
for rid, sub, dr, yld in [
    ("sa_r_1l", "(Sa,R)-(+)-1l", "99:1", 80),
    ("ra_r_1l", "(Ra,R)-(−)-1l", "96:4", 77),
]:
    e = ev(5)
    ps = pset(f"{sub} (d.r. {dr})", "(4R,5R)-(−)-(Z)-2l", e, [("I2", [])], ("cyclohexane", []))
    records.append(record(f"scheme9_{rid}", "reported_experiment", e, ps,
                          [("temperature", "r.t."), ("time", {"number": 1, "unit": "h"})],
                          [fld("isolated_yield", {"number": yld, "unit": "%"}, e, ["product"]),
                           fld("Z_E_ratio", "97:3", e, ["product"]),
                           fld("product_ee", {"number": 99, "unit": "%"}, e, ["product"])],
                          unresolved=["Scheme 9 does not state iodine equivalents, atmosphere, workup, or purification."]))

# Page 5 detailed racemic 1a preparation: five distinct experimental stages.
e5 = ev(5)
ps = pset("nonyn-3-ol (4a)", "ethyl undeca-3,4-dienoate", e5,
          [("EtCOOH", [amt("mass", 0.99, "g", e5), amt("amount", 0.013, "mol", e5)]),
           ("triethyl_orthoacetate", [amt("volume", 30, "mL", e5), amt("mass", 26.28, "g", e5), amt("amount", 0.16, "mol", e5)])])
ps[0]["amounts"] = [amt("mass", 7.0010, "g", e5), amt("amount", 0.05, "mol", e5)]
records.append(record("prep_racemic_4a_to_allenoate", "reported_experiment", e5, ps,
                      [("temperature", {"number": 130, "unit": "°C"}), ("time", {"number": 5, "unit": "h"}),
                       ("operation", "Dean–Stark removal of ethanol and excess triethyl orthoacetate"),
                       ("purification", "silica-gel chromatography")],
                      [fld("product_mass", {"number": 9.8926, "unit": "g"}, e5, ["product"]),
                       fld("crude_yield", {"number": 94, "unit": "%"}, e5, ["product"])],
                      unresolved=["Atmosphere is not stated."]))

ps = pset("ethyl undeca-3,4-dienoate", "undeca-3,4-dien-1-ol (5a)", e5,
          [("LiAlH4", [amt("mass", 1.3310, "g", e5), amt("amount", 34.9, "mmol", e5)])],
          ("THF", [amt("volume", 50, "mL", e5)]))
ps[0]["amounts"] = [amt("mass", 5.6457, "g", e5), amt("amount", 26.9, "mmol", e5)]
records.append(record("prep_racemic_allenoate_to_5a", "reported_experiment", e5, ps,
                      [("temperature", "ice-cold addition"), ("time", {"number": 1.2, "unit": "h"}), ("atmosphere", "N2"),
                       ("workup", "slow water quench; ether extraction; water/brine washes; Na2SO4 drying"),
                       ("purification", "silica-gel chromatography")],
                      [fld("product_mass", {"number": 3.8973, "unit": "g"}, e5, ["product"]),
                       fld("isolated_yield", {"number": 86, "unit": "%"}, e5, ["product"])]))

ps = pset("5a", "tosylate from 5a", e5, [("TsCl", [amt("mass", 22.2, "g", e5), amt("amount", 0.12, "mol", e5)])],
          ("pyridine", [amt("volume", 50, "mL", e5)]))
ps[0]["amounts"] = [amt("mass", 6.5161, "g", e5), amt("amount", 0.039, "mol", e5)]
records.append(record("prep_racemic_5a_to_tosylate", "reported_experiment", e5, ps,
                      [("temperature", {"minimum": 0, "maximum": 4, "unit": "°C", "raw_text": "0–4 °C"}),
                       ("time", {"number": 4, "unit": "h"}),
                       ("workup", "ice/water quench; ether extraction; water/brine washes; Na2SO4 drying"),
                       ("purification", "none; used in the next step")],
                      [fld("stage_yield", None, e5, ["product"])]))

ps = pset("tosylate from 5a", "dodeca-4,5-dienenitrile (6a)", e5,
          [("NaCN", [amt("mass", 2.0526, "g", e5), amt("amount", 0.042, "mol", e5)])],
          ("DMSO", [amt("volume", 30, "mL", e5)]))
records.append(record("prep_racemic_tosylate_to_6a", "reported_experiment", e5, ps,
                      [("temperature", {"number": 20, "unit": "°C"}), ("time", {"number": 25, "unit": "h"}),
                       ("workup", "water quench; ether extraction; water/brine washes; Na2SO4 drying"),
                       ("purification", "silica-gel chromatography")],
                      [fld("product_mass", {"number": 5.0199, "unit": "g"}, e5, ["product"]),
                       fld("combined_yield_from_5a_to_6a", {"number": 73, "unit": "%"}, e5, ["product"])],
                      unresolved=["The 73% yield spans tosylation and cyanide substitution."]))

ps = pset("6a", "1a", e5, [("NaOH", [amt("mass", 4.0, "g", e5), amt("amount", 100, "mmol", e5)])],
          ("EtOH/water", [amt("EtOH_volume", 15, "mL", e5), amt("water_volume", 5.2, "mL", e5)]))
ps[0]["amounts"] = [amt("mass", 2.0040, "g", e5), amt("amount", 11.3, "mmol", e5)]
records.append(record("prep_racemic_6a_to_1a", "reported_experiment", e5, ps,
                      [("temperature", {"number": 80, "unit": "°C"}), ("time", {"number": 5, "unit": "h"}),
                       ("workup", "concentration; water addition; neutral extraction; acidification with 5% HCl to pH 1; ether extraction; washes and Na2SO4 drying"),
                       ("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 5:1")],
                      [fld("product_mass", {"number": 2.1065, "unit": "g"}, e5, ["product"]),
                       fld("isolated_yield", {"number": 95, "unit": "%"}, e5, ["product"])]))

# Page 6 derivatization used to determine the d.r. of (S)-1l.
e6 = ev(6)
ps = pset("(S)-(+)-1l", "benzyl (S)-(+)-13a", e6,
          [("BnOH", [amt("mass", 17.8, "mg", e6), amt("amount", 0.16, "mmol", e6)]),
           ("DMAP", [amt("mass", 5.1, "mg", e6), amt("amount", 0.04, "mmol", e6)]),
           ("DCC", [amt("mass", 14.4, "mg", e6), amt("amount", 0.07, "mmol", e6)])],
          ("CH2Cl2", [amt("volume", 1, "mL", e6)]))
ps[0]["amounts"] = [amt("mass", 9.8, "mg", e6), amt("amount", 0.05, "mmol", e6)]
records.append(record("page6_benzylation_s_1l", "reported_experiment", e6, ps, [],
                      [fld("product_mass", {"number": 12.0, "unit": "mg"}, e6, ["product"]),
                       fld("isolated_yield", {"number": 82, "unit": "%"}, e6, ["product"]),
                       fld("product_dr_by_HPLC", "1.2:1", e6, ["product"])],
                      unresolved=["The abbreviated paragraph does not state temperature, duration, atmosphere, workup, or purification."]))


# Coverage ledger, exactly pages 1-6, every region includes same-page image evidence.
ids = [r["record_id"] for r in records]
by_prefix = lambda prefixes: [x for x in ids if any(x.split(":", 1)[1].startswith(p) for p in prefixes)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "title, abstract, introduction, and opening Results and Discussion", "finding": "Opening MeCN result is the narrative form of Table 1 entry 1; abstract and cited prior-work summaries were not duplicated as experiments.", "evidence_ids": [f"{DOC}:page1:image", f"{DOC}:page1:text"]}
        ], "record_ids": [f"{DOC}:table1_entry1"], "unresolved": ["Abstract-level claims are not independent experiments; supporting information is mentioned but was not supplied or associated."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and reaction drawing", "finding": "Thirteen independent solvent/loading optimization entries extracted with NMR yields and Z/E ratios; K2CO3 and iodine footnote overrides applied row-wise.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "upper-right Table 2 and footnotes", "finding": "Ten independent substrate-scope entries extracted under Conditions A or B; trace and table dashes preserved, and NMR-yield exceptions retained.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]},
            {"region": "lower prose, Figures 1-2, and chiral-reaction discussion", "finding": "NOE and ORTEP figures support identities/selectivity but are not separate reactions; prose links to Scheme 2 chiral experiments on page 3.", "evidence_ids": [f"{DOC}:page2:image", f"{DOC}:page2:text"]}
        ], "record_ids": by_prefix(["table1_", "table2_", "scheme2_"]), "unresolved": ["Table 1/2 omit scale, atmosphere, workup, and purification; machine structures remain unverified."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "left-column Schemes 1-3", "finding": "Scheme 1 multi-step preparation split by operation and substrate; Scheme 2 split into four distinct iodolactonizations; Scheme 3 classified as proposed mechanism.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "upper-right Scheme 4", "finding": "Two substrate-specific Sonogashira kinetic-resolution records extracted with catalyst/loading ranges, recovered Z-product yields, Z/E ratios, and ee.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]},
            {"region": "middle-right Table 3 and footnotes", "finding": "Five independent 3-substituted allenoic-acid scope entries extracted with isolated yields, crude Z/E ratios, and product d.r.", "evidence_ids": [f"{DOC}:page3:image", f"{DOC}:page3:text"]}
        ], "record_ids": by_prefix(["scheme1_", "scheme2_", "scheme3_", "scheme4_", "table3_"]), "unresolved": ["Several schemes omit duration, scale, workup, purification, or yield basis; stereochemical structures remain candidates."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 5", "finding": "Preparation of (S)-1l and (S)-1m split into successive operations; the 1l route is linked to page-6 detailed batches rather than duplicated.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "lower-left Scheme 6", "finding": "Three optically active iodolactonizations extracted under Conditions A with yields, Z/E ratios, and ee.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]},
            {"region": "upper/right Scheme 7 and lower-right Scheme 8", "finding": "Route to (Ra,R)-1l and its benzyl ester split by operation; benzylation, preparative-HPLC separation, and hydrolysis in Scheme 8 retained as distinct records.", "evidence_ids": [f"{DOC}:page4:image", f"{DOC}:page4:text"]}
        ], "record_ids": by_prefix(["scheme5_", "scheme6_", "scheme7_", "scheme8_"]), "unresolved": ["Scheme 5's 9a yield conflicts with the page-6 detailed batch; Scheme 8 and page 6 disagree on the benzyl-ester d.r."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 9", "finding": "Two allene-diastereomer iodolactonizations extracted separately; both give the same (4R,5R)-(Z)-2l product with different yields.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "lower-left and right-column racemic 1a preparation", "finding": "Five successive stages extracted: rearrangement, reduction, tosylation, cyanide substitution, and nitrile hydrolysis; compound-specific quantities and operations retained.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]},
            {"region": "lower-right optically active 1a preparation beginning", "finding": "Details enrich Scheme 1 route records and continue onto page 6; they are not counted as duplicate experiments.", "evidence_ids": [f"{DOC}:page5:image", f"{DOC}:page5:text"]}
        ], "record_ids": by_prefix(["scheme9_", "prep_racemic_", "scheme1_a_"]), "unresolved": ["The optically active route reports a scheme-level overall yield and separate detailed stage/combined yields with different scopes."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "upper-left continuation of optically active 1a preparation", "finding": "R-6a hydrolysis details merged into the Scheme 1 route record rather than creating a duplicate.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "left and upper-right preparation of (S)-1l", "finding": "Detailed 8a, 9a, methyl-ester, 10a, tosylation, cyanide substitution, desilylation, and hydrolysis operations linked to Scheme 5 stage records.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]},
            {"region": "lower-right benzyl derivatizations and preparative-HPLC setup", "finding": "(S)-1l benzylation extracted as a separate analytical derivatization; (R)-1l benzylation and HPLC separation merged with Scheme 8.", "evidence_ids": [f"{DOC}:page6:image", f"{DOC}:page6:text"]}
        ], "record_ids": by_prefix(["scheme1_a_", "scheme5_", "page6_", "scheme8_"]), "unresolved": ["The preparative-HPLC characterization continues onto page 7, which is not claimed as covered; missing isolated peak quantities remain unresolved."]},
    ],
}

raw_path = OUT / "raw_model/records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2))
coverage_path = OUT / "coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2))

# Mark only the six covered page tasks attempted; pages 7-9 remain pending.
tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and any(task["evidence_id"] == f"{DOC}:page{p}:text" for p in range(1, 7)):
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2))

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage": str(coverage_path)}, ensure_ascii=False))
