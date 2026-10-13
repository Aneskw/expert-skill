#!/usr/bin/env python3
"""Generate evidence-linked machine records for PDF pages 1--6.

This is a session artifact, not a chemistry rule or reusable extraction tool.
"""
import json
from pathlib import Path

DOC = "doc_5728b702b8559e95"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(evidence)) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
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


def qty(name, number, unit, evidence, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return field(name, value, evidence)


def rec(suffix, kind, evidence, participants, steps, outcomes, notes=None, unresolved=None):
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
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting information was not supplied or explicitly associated.",
                "Machine-extracted structures and chemical roles require expert review.",
            ],
        },
    }


records = []

# Equation (1) is explicitly cited prior work (ref. 5), not a new experiment.
e = ev(1)
parts = [
    participant("eq1_start", "reactant", "generic N-propargyl amide (R1)", None, e),
    participant("eq1_product", "product", "generic N-(buta-2,3-dienyl) amide (R1)", None, e),
    participant("eq1_cubr", "catalyst", "CuBr", "copper(I) bromide", e,
                amounts=[qty("equivalents", 0.3, "equiv", e)]),
    participant("eq1_formaldehyde", "reactant", "(HCHO)n", "paraformaldehyde", e,
                amounts=[qty("equivalents", 2.0, "equiv", e)]),
    participant("eq1_dipa", "reagent", "i-Pr2NH", "diisopropylamine", e,
                amounts=[qty("equivalents", 2.0, "equiv", e)]),
    participant("eq1_dioxane", "solvent", "dioxane", "dioxane", e),
]
records.append(rec(
    "eq1_ref5_literature_example", "literature_example", e, parts,
    [{"step_id": "literature_step", "participant_ids": [p["entity_id"] for p in parts],
      "conditions": [qty("temperature", 100, "°C", e)]}],
    [field("reported_yield_range", {"minimum": 4, "maximum": 55, "unit": "%", "raw_text": "4–55%"}, e,
           ["eq1_product"])],
    notes=["The arrow is presented as Hashmi et al. ref. 5 prior work and is not an experiment newly reported in this paper."],
    unresolved=["Generic R1 structures are not fully specified.", "Reaction time is not shown in equation (1)."]
))


table1 = [
    (1, "1a", "Ph", "benzamide", 9, 85, 3, "c1ccccc1", 158.4, 54.9, 75.9, 146.4, "5:1"),
    (2, "1b", "p-FC6H4", "4-fluorobenzamide", 11.5, 90, 4, "c1ccc(F)cc1", 177.3, 54.9, 75.1, 171.6, "5:1"),
    (3, "1c", "p-ClC6H4", "4-chlorobenzamide", 4.5, 80, 4, "c1ccc(Cl)cc1", 193.3, 54.8, 74.7, 165.0, "5:1"),
    (4, "1d", "p-BrC6H4", "4-bromobenzamide", 5.5, 90, 4, "c1ccc(Br)cc1", 237.8, 54.7, 75.4, 225.9, "5:1"),
    (5, "1e", "p-MeO2CC6H4", "4-carbomethoxybenzamide", 24, 81, 4, "c1ccc(C(=O)OC)cc1", 217.2, 54.4, 75.3, 187.3, "3:1"),
    (6, "1f", "p-MeC6H4", "4-methylbenzamide", 6, 66, 4, "c1ccc(C)cc1", 173.8, 55.1, 75.6, 124.3, "5:1"),
    (7, "1g", "p-MeOC6H4", "4-methoxybenzamide", 1.2, 76, 5, "c1ccc(OC)cc1", 188.7, 54.8, 75.3, 153.3, "3:1"),
    (8, "1h", "n-C4H9", "pentanamide", 2.7, 73, 5, "CCCC", 140.0, 54.6, 75.5, 111.7, "5:1"),
    (9, "1i", "Bn", "2-phenylacetamide", 2.7, 65, 5, "Cc1ccccc1", 172.8, 54.8, 74.9, 121.7, "5:1"),
    (10, "1j", "2-furyl", "furan-2-carboxamide", 9.7, 82, 5, "c1ccoc1", 150.0, 54.4, 75.3, 133.8, "3:1"),
]

for idx, label, r1, amide_name, time_h, yield_pct, detail_page, rfrag, substrate_mg, cui_mg, pf_mg, product_mg, eluent in table1:
    e = ev(1) + ev(detail_page) + (ev(3) if idx == 2 else [])
    start_smiles = f"C#CCNC(=O){rfrag}"
    product_smiles = f"C=C=CCNC(=O){rfrag}"
    start_id, product_id = f"t1e{idx}_start", f"t1e{idx}_product"
    parts = [
        participant(start_id, "reactant", f"N-propargyl {amide_name}", None, e, start_smiles,
                    [qty("amount", 1.0, "mmol", e), qty("mass", substrate_mg, "mg", ev(detail_page))]),
        participant(product_id, "product", label, f"N-(buta-2,3-dienyl) {amide_name}", e, product_smiles,
                    [qty("mass", product_mg, "mg", ev(detail_page))]),
        participant(f"t1e{idx}_cui", "catalyst", "CuI", "copper(I) iodide", e, "[Cu]I",
                    [qty("amount", 0.5, "mmol", e), qty("mass", cui_mg, "mg", ev(detail_page))]),
        participant(f"t1e{idx}_pf", "reactant", "(HCHO)n", "paraformaldehyde", e, None,
                    [qty("amount", 2.5, "mmol", e), qty("mass", pf_mg, "mg", ev(detail_page))]),
        participant(f"t1e{idx}_cy2nh", "reagent", "Cy2NH", "dicyclohexylamine", e, None,
                    [qty("amount", 1.8, "mmol", e), qty("mass", 326.4, "mg", ev(detail_page)),
                     qty("volume", 0.36, "mL", ev(detail_page)), field("density", "0.916 g mL−1", ev(detail_page))]),
        participant(f"t1e{idx}_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", e, "O1CCOCC1",
                    [qty("volume", 2.0, "mL", e)]),
    ]
    step = {"step_id": "allene_formation", "participant_ids": [p["entity_id"] for p in parts],
            "conditions": [qty("temperature", 100, "°C", e), qty("time", time_h, "h", e),
                           field("purification", f"silica gel chromatography; petroleum ether/ethyl acetate {eluent}", ev(detail_page))]}
    records.append(rec(
        f"table1_entry{idx}_{label}", "substrate_scope_entry", e, parts, [step],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, e, [product_id]),
         field("yield_measurement_basis", "isolated product", e, [product_id])],
        notes=[f"Table 1 R1 = {r1}; the detailed preparation on PDF page {detail_page} was merged with the same table row."],
        unresolved=["Supporting information was not supplied or explicitly associated.",
                    "Candidate SMILES were transcribed from the displayed structures and remain unverified."]
    ))


gram = [
    ("1a", 3, "benzamide", "c1ccccc1", 10.0, 1.6097, 5.0, 0.5491, 25.0, 0.7519, 18.0, 3.264, 3.6, 20.0, 14.5, 1.3945, 80),
    ("1e", 4, "4-carbomethoxybenzamide", "c1ccc(C(=O)OC)cc1", 14.6, 3.166, 7.6, 0.830, 37.5, 1.126, 27.0, 4.9, 5.3, 40.0, 22, 2.5644, 76),
    ("1j", 5, "furan-2-carboxamide", "c1ccoc1", 15.0, 2.2610, 7.5, 0.8370, 37.5, 1.1340, 27.0, 4.8548, 5.3, 40.0, 16, 1.7809, 72),
]
for label, detail_page, amide_name, rfrag, scale_mmol, start_g, cui_mmol, cui_g, pf_mmol, pf_g, cy_mmol, cy_g, cy_ml, dioxane_ml, time_h, product_g, yield_pct in gram:
    e = ev(2) + ev(detail_page)
    sid, pid = f"gram_{label}_start", f"gram_{label}_product"
    parts = [
        participant(sid, "reactant", f"N-propargyl {amide_name}", None, e, f"C#CCNC(=O){rfrag}",
                    [qty("amount", scale_mmol, "mmol", ev(detail_page)), qty("mass", start_g, "g", ev(detail_page))]),
        participant(pid, "product", label, f"N-(buta-2,3-dienyl) {amide_name}", e, f"C=C=CCNC(=O){rfrag}",
                    [qty("mass", product_g, "g", ev(detail_page))]),
        participant(f"gram_{label}_cui", "catalyst", "CuI", "copper(I) iodide", e, "[Cu]I",
                    [qty("amount", cui_mmol, "mmol", ev(detail_page)), qty("mass", cui_g, "g", ev(detail_page))]),
        participant(f"gram_{label}_pf", "reactant", "(HCHO)n", "paraformaldehyde", e, None,
                    [qty("amount", pf_mmol, "mmol", ev(detail_page)), qty("mass", pf_g, "g", ev(detail_page))]),
        participant(f"gram_{label}_cy2nh", "reagent", "Cy2NH", "dicyclohexylamine", e, None,
                    [qty("amount", cy_mmol, "mmol", ev(detail_page)), qty("mass", cy_g, "g", ev(detail_page)), qty("volume", cy_ml, "mL", ev(detail_page))]),
        participant(f"gram_{label}_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", e, "O1CCOCC1",
                    [qty("volume", dioxane_ml, "mL", ev(detail_page))]),
    ]
    unresolved = ["Supporting information was not supplied or explicitly associated.",
                  "Candidate SMILES remain unverified against an independent structure review."]
    notes = ["Scheme 1 and the detailed gram-scale paragraph describe the same batch and were merged."]
    if label == "1e":
        notes.append("Scheme 1 rounds the starting-material scale to 15 mmol; the detailed paragraph reports 14.6 mmol and is retained as the batch amount.")
        unresolved.append("The source gives CuI as 0.830 g, 7.6 mmol; this apparent mass/amount inconsistency is preserved verbatim for review.")
    records.append(rec(
        f"scheme1_gram_scale_{label}", "reported_experiment", e, parts,
        [{"step_id": "gram_scale_allene_formation", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [qty("temperature", 100, "°C", e), qty("time", time_h, "h", e)]}],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, e, [pid]),
         field("yield_measurement_basis", "isolated product", e, [pid])], notes=notes, unresolved=unresolved
    ))


table2 = [
    (1, "DMF", 2, "KOtBu", 0, None),
    (2, "DMF", 37, "Li2CO3", 34, 23),
    (3, "DMF", 10.3, "Na2CO3", 74, None),
    (4, "DMF", 3, "K2CO3", 90, None),
    (5, "DMF", 10.3, "Cs2CO3", 87, None),
    (6, "DMSO", 5.3, "K2CO3", 82, None),
    (7, "DCE", 19, "K2CO3", 23, 62),
    (8, "DMA", 7.5, "K2CO3", 89, None),
    (9, "CH3CN", 24, "K2CO3", 88, None),
    (10, "toluene", 46, "K2CO3", 85, None),
    (11, "dioxane", 46, "K2CO3", 84, None),
]
solvent_smiles = {"DMF": "CN(C)C=O", "DMSO": "CS(C)=O", "DCE": "ClCCCl", "DMA": "CC(=O)N(C)C", "CH3CN": "CC#N", "toluene": "Cc1ccccc1", "dioxane": "O1CCOCC1"}
for idx, solvent, time_h, base, yield_pct, recovery_pct in table2:
    e = ev(2)
    sid, iid, pid = f"t2e{idx}_1a", f"t2e{idx}_2a", f"t2e{idx}_3aa"
    parts = [
        participant(sid, "reactant", "1a", "N-(buta-2,3-dienyl) benzamide", e, "C=C=CCNC(=O)c1ccccc1", [qty("amount", 0.2, "mmol", e)]),
        participant(iid, "reactant", "2a", "iodobenzene", e, "Ic1ccccc1", [qty("amount", 0.24, "mmol", e)]),
        participant(pid, "product", "3aa", "2-phenyl-5-(1-phenylvinyl)-4,5-dihydrooxazole", e, "C=C(c1ccccc1)C1CN=C(c2ccccc2)O1"),
        participant(f"t2e{idx}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e, None, [qty("catalyst_loading", 5, "mol%", e)]),
        participant(f"t2e{idx}_base", "reagent", base, base, e, None, [qty("equivalents", 2, "equiv", e)]),
        participant(f"t2e{idx}_solvent", "solvent", solvent, solvent, e, solvent_smiles[solvent], [qty("volume", 2, "mL", e)]),
        participant(f"t2e{idx}_mesitylene", "unspecified_agent", "mesitylene", "mesitylene (NMR internal standard)", e, "Cc1cc(C)cc(C)c1"),
    ]
    outcomes = [field("nmr_yield", {"number": yield_pct, "unit": "%"}, e, [pid]),
                field("yield_measurement_basis", "NMR using mesitylene as internal standard", e, [pid])]
    if recovery_pct is not None:
        outcomes.append(field("recovered_starting_material_yield", {"number": recovery_pct, "unit": "%"}, e, [sid]))
    notes = []
    if idx == 1:
        notes.append("The prose describes the KOtBu reaction as complicated; Table 2 reports 0% 3aa by NMR.")
    records.append(rec(
        f"table2_entry{idx}", "optimization_entry", e, parts,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [qty("temperature", 80, "°C", e), qty("time", time_h, "h", e)]}],
        outcomes, notes=notes,
        unresolved=["Supporting information was not supplied or explicitly associated.",
                    "Table-only optimization row; workup and isolated-product details are not reported here."]
    ))


r1_info = {
    "1a": ("Ph", "N-(buta-2,3-dienyl) benzamide", "c1ccccc1"),
    "1b": ("4-FC6H4", "N-(buta-2,3-dienyl) 4-fluorobenzamide", "c1ccc(F)cc1"),
    "1c": ("4-ClC6H4", "N-(buta-2,3-dienyl) 4-chlorobenzamide", "c1ccc(Cl)cc1"),
    "1d": ("4-BrC6H4", "N-(buta-2,3-dienyl) 4-bromobenzamide", "c1ccc(Br)cc1"),
    "1e": ("4-MeO2CC6H4", "N-(buta-2,3-dienyl) 4-carbomethoxybenzamide", "c1ccc(C(=O)OC)cc1"),
    "1f": ("4-MeC6H4", "N-(buta-2,3-dienyl) 4-methylbenzamide", "c1ccc(C)cc1"),
    "1g": ("4-MeOC6H4", "N-(buta-2,3-dienyl) 4-methoxybenzamide", "c1ccc(OC)cc1"),
    "1h": ("nBu", "N-(buta-2,3-dienyl) pentanamide", "CCCC"),
    "1i": ("Bn", "N-(buta-2,3-dienyl) 2-phenylacetamide", "Cc1ccccc1"),
    "1j": ("2-furanyl", "N-(buta-2,3-dienyl) furan-2-carboxamide", "c1ccoc1"),
}
r2_info = {
    "2a": ("Ph", "iodobenzene", "Ic1ccccc1", "c1ccccc1"),
    "2b": ("4-MeOC6H4", "1-iodo-4-methoxybenzene", "COc1ccc(I)cc1", "c1ccc(OC)cc1"),
    "2c": ("4-MeC6H4", "1-iodo-4-methylbenzene", "Cc1ccc(I)cc1", "c1ccc(C)cc1"),
    "2d": ("4-BrC6H4", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1", "c1ccc(Br)cc1"),
    "2e": ("4-FC6H4", "1-fluoro-4-iodobenzene", "Fc1ccc(I)cc1", "c1ccc(F)cc1"),
    "2f": ("4-ClC6H4", "1-chloro-4-iodobenzene", "Clc1ccc(I)cc1", "c1ccc(Cl)cc1"),
    "2g": ("4-EtO2CC6H4", "ethyl 4-iodobenzoate", "CCOC(=O)c1ccc(I)cc1", "c1ccc(C(=O)OCC)cc1"),
    "2h": ("4-CH3COC6H4", "4-iodoacetophenone", "CC(=O)c1ccc(I)cc1", "c1ccc(C(=O)C)cc1"),
    "2i": ("4-O2NC6H4", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", "c1ccc([N+](=O)[O-])cc1"),
    "2j": ("4-NCC6H4", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1", "c1ccc(C#N)cc1"),
    "2k": ("4-PhC6H4", "4-iodobiphenyl", "Ic1ccc(-c2ccccc2)cc1", "c1ccc(-c2ccccc2)cc1"),
    "2l": ("3-MeC6H4", "1-iodo-3-methylbenzene", "Cc1cccc(I)c1", "c1cccc(C)c1"),
    "2m": ("3-FC6H4", "1-fluoro-3-iodobenzene", "Fc1cccc(I)c1", "c1cccc(F)c1"),
    "2n": ("2-MeC6H4", "1-iodo-2-methylbenzene", "Cc1ccccc1I", "c1ccccc1C"),
    "2o": ("3-thienyl", "3-iodothiophene", "Ic1ccsc1", None),
    "2p": ("N-tosyl-3-indolyl", "3-iodo-1-tosyl-1H-indole", None, None),
    "2q": ("(E)-PhCH=CH", "(E)-1-iodo-2-phenylethene", None, None),
    "2r": ("(E)-nBuCH=CH", "(E)-1-iodohex-1-ene", None, None),
}
table3 = [
    (1,"1a","2a",3,80,"3aa"),(2,"1a","2b",8,69,"3ab"),(3,"1a","2c",9,66,"3ac"),
    (4,"1a","2d",17.5,83,"3ad"),(5,"1a","2e",10,82,"3ae"),(6,"1a","2f",17,71,"3af"),
    (7,"1a","2g",9,91,"3ag"),(8,"1a","2h",45.5,63,"3ah"),(9,"1a","2i",24,82,"3ai"),
    (10,"1a","2j",22,88,"3aj"),(11,"1a","2k",5,77,"3ak"),(12,"1a","2l",6,79,"3al"),
    (13,"1a","2m",10,94,"3am"),(14,"1a","2n",28,66,"3an"),(15,"1a","2o",9,79,"3ao"),
    (16,"1a","2p",9.5,66,"3ap"),(17,"1a","2q",6.5,58,"3aq"),(18,"1a","2r",6.5,77,"3ar"),
    (19,"1b","2a",21,73,"3ba"),(20,"1c","2a",5,72,"3ca"),(21,"1d","2a",10,89,"3da"),
    (22,"1e","2a",10,86,"3ea"),(23,"1f","2a",5,87,"3fa"),(24,"1g","2a",9,76,"3ga"),
    (25,"1h","2a",8,53,"3ha"),(26,"1i","2a",6.4,52,"3ia"),(27,"1j","2a",22,71,"3ja"),
]

for idx, r1_label, r2_label, time_h, yield_pct, product_label in table3:
    e = ev(2)
    if idx == 1:
        e += ev(5) + ev(6)
    r1_text, r1_name, r1frag = r1_info[r1_label]
    r2_text, r2_name, r2_smiles, r2frag = r2_info[r2_label]
    sid, iid, pid = f"t3e{idx}_{r1_label}", f"t3e{idx}_{r2_label}", f"t3e{idx}_{product_label}"
    product_smiles = f"C=C({r2frag})C1CN=C({r1frag})O1" if r2frag else None
    product_name = f"2-({r1_text})-5-[1-({r2_text})vinyl]-4,5-dihydrooxazole"
    start_amounts = [qty("amount", 0.2, "mmol", ev(2))]
    iodide_amounts = [qty("amount", 0.24, "mmol", ev(2))]
    pd_amounts = [qty("catalyst_loading", 5, "mol%", ev(2))]
    product_amounts = []
    if idx == 1:
        start_amounts.append(qty("mass", 34.9, "mg", ev(5)))
        iodide_amounts.append(qty("mass", 49.7, "mg", ev(5)))
        pd_amounts += [qty("amount", 0.01, "mmol", ev(5)), qty("mass", 11.7, "mg", ev(5))]
        product_amounts.append(qty("mass", 40.3, "mg", ev(5)))
    parts = [
        participant(sid, "reactant", r1_label, r1_name, e, f"C=C=CCNC(=O){r1frag}", start_amounts),
        participant(iid, "reactant", r2_label, r2_name, e, r2_smiles, iodide_amounts),
        participant(pid, "product", product_label, product_name, e, product_smiles, product_amounts),
        participant(f"t3e{idx}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e, None, pd_amounts),
        participant(f"t3e{idx}_k2co3", "reagent", "K2CO3", "potassium carbonate", e, None,
                    [qty("equivalents", 2, "equiv", ev(2))] + ([qty("amount", 0.4, "mmol", ev(5)), qty("mass", 55.4, "mg", ev(5))] if idx == 1 else [])),
        participant(f"t3e{idx}_dmf", "solvent", "DMF", "N,N-dimethylformamide", e, "CN(C)C=O", [qty("volume", 2, "mL", ev(2))]),
    ]
    conditions = [qty("temperature", 80, "°C", e), qty("time", time_h, "h", ev(2))]
    if idx == 1:
        conditions += [field("atmosphere", "nitrogen", ev(5)),
                       field("workup", "diluted with diethyl ether; washed with water; dried over anhydrous Na2SO4; filtered and evaporated", ev(5)),
                       field("purification", "silica gel chromatography, petroleum ether/ethyl acetate 10:1", ev(5))]
    unresolved = ["Supporting information was not supplied or explicitly associated.",
                  "Product and participant candidate structures remain unverified."]
    if product_smiles is None:
        unresolved.append("Product SMILES is left null because the displayed substituent was not encoded with sufficient confidence.")
    records.append(rec(
        f"table3_entry{idx}_{product_label}", "substrate_scope_entry", e, parts,
        [{"step_id": "pd_coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts], "conditions": conditions}],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, e, [pid]),
         field("yield_measurement_basis", "isolated product", ev(2), [pid])],
        notes=["The Table 3 row is retained as a distinct experiment under the shared footnote conditions."],
        unresolved=unresolved
    ))


# Separate large-scale coupling/cyclization batches in equations (2) and (3).
scaleups = [
    ("eq2_gram_scale_3da", "1d", "N-(buta-2,3-dienyl) 4-bromobenzamide", "C=C=CCNC(=O)c1ccc(Br)cc1", 1.0086,
     "2a", "iodobenzene", "Ic1ccccc1", "3da", "2-(4-bromophenyl)-5-(1-phenylvinyl)-4,5-dihydrooxazole", "C=C(c1ccccc1)C1CN=C(c2ccc(Br)cc2)O1", 1.0, 12, 1.1476, 87),
    ("eq3_gram_scale_3ak", "1a", "N-(buta-2,3-dienyl) benzamide", "C=C=CCNC(=O)c1ccccc1", 1.3836,
     "2k", "4-iodobiphenyl", "Ic1ccc(-c2ccccc2)cc1", "3ak", "2-phenyl-5-[1-(4-biphenyl)vinyl]-4,5-dihydrooxazole", "C=C(c1ccc(-c2ccccc2)cc1)C1CN=C(c2ccccc2)O1", 0.1, 69, 2.0021, 77),
]
for suffix, slabel, sname, ssmiles, smass, ilabel, iname, ismiles, plabel, pname, psmiles, pd_loading, time_h, pmass, yield_pct in scaleups:
    e = ev(3)
    parts = [
        participant(f"{suffix}_start", "reactant", slabel, sname, e, ssmiles, [qty("mass", smass, "g", e)]),
        participant(f"{suffix}_iodide", "reactant", ilabel, iname, e, ismiles),
        participant(f"{suffix}_product", "product", plabel, pname, e, psmiles, [qty("mass", pmass, "g", e)]),
        participant(f"{suffix}_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)", e, None, [qty("catalyst_loading", pd_loading, "mol%", e)]),
        participant(f"{suffix}_base", "reagent", "K2CO3", "potassium carbonate", e),
        participant(f"{suffix}_dmf", "solvent", "DMF", "N,N-dimethylformamide", e, "CN(C)C=O"),
    ]
    records.append(rec(
        suffix, "reported_experiment", e, parts,
        [{"step_id": "scale_up_coupling_cyclization", "participant_ids": [p["entity_id"] for p in parts],
          "conditions": [qty("temperature", 80, "°C", e), qty("time", time_h, "h", e)]}],
        [field("isolated_yield", {"number": yield_pct, "unit": "%"}, e, [f"{suffix}_product"]),
         field("yield_measurement_basis", "isolated product", e, [f"{suffix}_product"])],
        notes=["Equation (2) or (3) is a separate scale-up batch, not the corresponding Table 3 row."],
        unresolved=["Supporting information was not supplied or explicitly associated.",
                    "The equation does not report all reactant/base/solvent quantities or workup details.",
                    "Candidate structures remain unverified."]
    ))


assert len(records) == 54, len(records)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
