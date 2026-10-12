#!/usr/bin/env python3
"""Build evidence-linked machine extraction records for jo025967v PDF pages 1-4."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0001_0004.json"
DOC = "doc_6645a563174b27a7"


def eid(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


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


def amount(name, number, unit, evidence, **extra):
    value = {"number": number, "unit": unit, **extra}
    return field(name, value, evidence)


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, ()),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, ()),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence, participants, steps, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes,
        "notes": [fact(x, evidence) for x in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


COMMON_UNRESOLVED = [
    "Supporting Information is mentioned but was not supplied or explicitly associated.",
    "Machine-extracted structures and role assignments require independent source review.",
]


records = []

# Scheme 1 rows share the page-3 general procedure and are distinct product examples.
scheme1_rows = [
    ("1a", "R1=n-Bu, R2=H, R3=Bn", 42, "N-benzyl octa-2,3-dienamide", "CCCCC=C=CC(=O)NCc1ccccc1"),
    ("1e", "R1=R2=Me, R3=Bn", 85, "allenamide 1e", None),
    ("1f", "R1=R2=Me, R3=n-Bu", 84, "allenamide 1f", None),
    ("1g", "R1=R2=Me, R3=H", 77, "allenamide 1g", None),
]
for label, subs, yld, product_name, product_smiles in scheme1_rows:
    ev = [eid(1), eid(1, "text"), eid(3), eid(3, "text")]
    ps = [
        participant("allenyl_bromide", "reactant", f"1,2-allenyl bromide precursor for {label}", ev,
                    name=f"1,2-allenyl bromide ({subs})", amounts=[amount("amount", 27.8, "mmol", ev)]),
        participant("amine", "reactant", "R3NH2", ev, name=f"amine for {label} ({subs})"),
        participant("carbon_monoxide", "reagent", "CO", ev, name="carbon monoxide", smiles="[C-]#[O+]"),
        participant("triethylamine", "reagent", "Et3N", ev, name="triethylamine", smiles="CCN(CC)CC",
                    amounts=[amount("amount", 30.6, "mmol", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, name="tetrakis(triphenylphosphine)palladium(0)",
                    amounts=[amount("amount", 0.28, "mmol", ev)]),
        participant("thf", "solvent", "THF", ev, name="tetrahydrofuran", smiles="C1CCOC1",
                    amounts=[amount("volume", 50, "mL", ev)]),
        participant("product", "product", label, ev, name=f"{product_name} ({subs})", smiles=product_smiles),
    ]
    steps = [{
        "step_id": "carbonylation",
        "participant_ids": [p["entity_id"] for p in ps],
        "conditions": [
            field("carbon_monoxide_pressure", "25 atm", ev),
            field("temperature", "r.t.", ev),
            amount("time", 2, "h", ev),
            field("workup", "Release CO; quench with water; add CH2Cl2; separate; wash organic phase with 1 N HCl and brine; evaporate.", ev),
            field("purification", "flash chromatography on silica gel", ev),
        ],
    }]
    records.append(record(
        f"scheme1_{label}", f"Scheme 1 {label}", "substrate_scope_entry", ev, ps, steps,
        [field("yield", {"number": yld, "unit": "%"}, ev, ["product"]),
         field("yield_measurement_basis", "product isolated after flash chromatography; the scheme does not separately define the yield basis", ev, ["product"])],
        [f"Scheme 1 substituent assignment: {subs}.", "CO pressure is retained verbatim because atm is not a supported structured quantity unit."],
        COMMON_UNRESOLVED + (["Product structure was not converted from the R-group drawing to SMILES."] if product_smiles is None else []),
    ))

# Scheme 2 / detailed two-stage preparation of 1b.
ev = [eid(1), eid(1, "text"), eid(3), eid(3, "text")]
ps = [
    participant("acid", "reactant", "4-cyclohexylbuta-2,3-dienoic acid", ev,
                name="4-cyclohexylbuta-2,3-dienoic acid", smiles="O=C(O)C=C=CC1CCCCC1",
                amounts=[amount("mass", 833, "mg", ev), amount("amount", 5, "mmol", ev)]),
    participant("thionyl_chloride", "reagent", "SOCl2", ev, name="thionyl chloride", smiles="O=S(Cl)Cl",
                amounts=[amount("volume", 1, "mL", ev), amount("amount", 14, "mmol", ev)]),
    participant("acid_chloride", "unspecified_agent", "4-cyclohexylbuta-2,3-dienoyl chloride", ev,
                name="4-cyclohexylbuta-2,3-dienoyl chloride", smiles="O=C(Cl)C=C=CC1CCCCC1"),
    participant("benzylamine", "reactant", "BnNH2", ev, name="benzylamine", smiles="NCc1ccccc1",
                amounts=[amount("volume", 0.6, "mL", ev), amount("amount", 5.5, "mmol", ev)]),
    participant("triethylamine", "reagent", "Et3N", ev, name="triethylamine", smiles="CCN(CC)CC",
                amounts=[amount("volume", 0.78, "mL", ev), amount("amount", 5.5, "mmol", ev)]),
    participant("ether", "solvent", "dry ether", ev, name="diethyl ether", smiles="CCOCC",
                amounts=[amount("acid_chloride_solution_volume", 10, "mL", ev), amount("reaction_solvent_volume", 20, "mL", ev)]),
    participant("product", "product", "1b", ev, name="N-benzyl 4-cyclohexylbuta-2,3-dienamide", smiles="O=C(NCc1ccccc1)C=C=CC1CCCCC1"),
]
steps = [
    {"step_id": "acid_chloride_formation", "participant_ids": ["acid", "thionyl_chloride", "acid_chloride", "ether"],
     "conditions": [field("temperature", "r.t.", ev), amount("time", 30, "min", ev),
                    field("operation", "Remove excess SOCl2 under reduced pressure; dissolve the acid chloride in dry ether.", ev)]},
    {"step_id": "aminolysis", "participant_ids": ["acid_chloride", "benzylamine", "triethylamine", "ether", "product"],
     "conditions": [field("temperature", "r.t.", ev), amount("time", 3, "h", ev),
                    field("operation", "Add the acid chloride solution dropwise to benzylamine/Et3N in dry ether; filter precipitate and evaporate solvent.", ev),
                    field("purification", "flash chromatography on silica gel", ev)]},
]
records.append(record(
    "scheme2_1b", "Scheme 2 / synthesis of 1b", "reported_experiment", ev, ps, steps,
    [field("product_mass", {"number": 732, "unit": "mg"}, ev, ["product"]),
     field("yield", {"number": 57, "unit": "%"}, ev, ["product"]),
     field("yield_measurement_basis", "isolated after flash chromatography", ev, ["product"])],
    ["The acid chloride is generated in situ and carried into the second stage; no intermediate yield is stated."],
    COMMON_UNRESOLVED,
))

# Scheme 3 rows share the page-3 DCC/DMAP amidation procedure.
scheme3_rows = [
    ("1c", "R1,R2=(CH2)5; R3=n-Pr", 74, "N-benzyl 3-cyclohexylidene-2-propylacrylamide"),
    ("1d", "R1=R2=Me; R3=Bn", 55, "allenamide 1d"),
    ("1h", "R1=R2=R3=Me", 45, "allenamide 1h"),
]
for label, subs, yld, pname in scheme3_rows:
    ev = [eid(1), eid(1, "text"), eid(3), eid(3, "text")]
    ps = [
        participant("allenoic_acid", "reactant", f"allenoic acid precursor for {label}", ev,
                    name=f"allenoic acid ({subs})", amounts=[amount("amount", 5.25, "mmol", ev)]),
        participant("benzylamine", "reactant", "BnNH2", ev, name="benzylamine", smiles="NCc1ccccc1",
                    amounts=[amount("amount", 5.8, "mmol", ev)]),
        participant("dcc", "reagent", "DCC", ev, name="dicyclohexylcarbodiimide", smiles="C1CCC(CC1)N=C=NC2CCCCC2",
                    amounts=[amount("amount", 5.5, "mmol", ev)]),
        participant("dmap", "catalyst", "DMAP", ev, name="4-(dimethylamino)pyridine", smiles="CN(C)c1ccncc1",
                    amounts=[amount("amount", 0.26, "mmol", ev)]),
        participant("dcm", "solvent", "dry CH2Cl2", ev, name="dichloromethane", smiles="ClCCl",
                    amounts=[amount("initial_volume", 10, "mL", ev), amount("dcc_dmap_solution_volume", 5, "mL", ev), amount("amine_solution_volume", 5, "mL", ev)]),
        participant("product", "product", label, ev, name=f"{pname} ({subs})"),
    ]
    records.append(record(
        f"scheme3_{label}", f"Scheme 3 {label}", "substrate_scope_entry", ev, ps,
        [{"step_id": "dcc_dmap_amidation", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
            field("addition_temperature", {"number": -30, "unit": "°C"}, ev),
            field("temperature", "r.t.", ev), amount("time", 6, "h", ev),
            field("operation", "Sequentially add DCC/DMAP solution and benzylamine solution; remove precipitate by filtration and evaporate.", ev),
            field("purification", "flash chromatography on silica gel", ev),
        ]}],
        [field("yield", {"number": yld, "unit": "%"}, ev, ["product"]),
         field("yield_measurement_basis", "product isolated after flash chromatography; the scheme does not separately define the yield basis", ev, ["product"])],
        [f"Scheme 3 substituent assignment: {subs}."],
        COMMON_UNRESOLVED + ["Product structure was not converted from the R-group drawing to SMILES."],
    ))


def detailed_lactam(label, substrate_label, substrate_name, substrate_smiles, substrate_mass, substrate_mmol,
                     base_mass, base_mmol, solvent_label, solvent_name, solvent_smiles, solvent_volume,
                     ph_i_volume, ph_i_mmol, catalyst_mass, catalyst_mmol, time_h, product_name,
                     product_smiles, product_mass, yld, tbab=None):
    pages = [1, 3, 4] if label == "3a" else [1, 4]
    ev = []
    for p in pages:
        ev += [eid(p), eid(p, "text")]
    ps = [
        participant("substrate", "reactant", substrate_label, ev, name=substrate_name, smiles=substrate_smiles,
                    amounts=[amount("mass", substrate_mass, "mg", ev), amount("amount", substrate_mmol, "mmol", ev)]),
        participant("iodobenzene", "reactant", "PhI (2a)", ev, name="iodobenzene", smiles="Ic1ccccc1",
                    amounts=[amount("volume", ph_i_volume, "uL", ev), amount("amount", ph_i_mmol, "mmol", ev), amount("equivalents", 1.5, "equiv", ev)]),
        participant("potassium_carbonate", "reagent", "K2CO3", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O",
                    amounts=[amount("mass", base_mass, "mg", ev), amount("amount", base_mmol, "mmol", ev), amount("equivalents", 2, "equiv", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, name="tetrakis(triphenylphosphine)palladium(0)",
                    amounts=[amount("mass", catalyst_mass, "mg", ev), amount("amount", catalyst_mmol, "mmol", ev), amount("catalyst_loading", 5, "mol%", ev)]),
        participant("solvent", "solvent", solvent_label, ev, name=solvent_name, smiles=solvent_smiles,
                    amounts=[amount("volume", solvent_volume, "mL", ev)]),
        participant("product", "product", label, ev, name=product_name, smiles=product_smiles),
    ]
    if tbab:
        ps.insert(4, participant("tbab", "reagent", "TBAB", ev, name="tetra-n-butylammonium bromide",
                                 smiles="[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
                                 amounts=[amount("mass", tbab[0], "mg", ev), amount("amount", tbab[1], "mmol", ev)]))
    if label == "3a":
        ps += [
            participant("water", "reagent", "water", ev, name="water", smiles="O"),
            participant("ether_workup", "solvent", "ether", ev, name="diethyl ether", smiles="CCOCC"),
            participant("brine", "reagent", "brine", ev, name="brine"),
            participant("sodium_sulfate", "reagent", "anhydrous sodium sulfate", ev, name="sodium sulfate", smiles="[Na+].[Na+].[O-]S(=O)(=O)[O-]"),
        ]
    steps = [{"step_id": "coupling_cyclization_hydroxylation", "participant_ids": [p["entity_id"] for p in ps[:6 if not tbab else 7]],
              "conditions": [field("atmosphere", "Ar", ev), amount("temperature", 70, "°C", ev), amount("time", time_h, "h", ev)]}]
    if label == "3a":
        steps.append({"step_id": "workup_purification", "participant_ids": ["product", "water", "ether_workup", "brine", "sodium_sulfate"],
                      "conditions": [field("workup", "Add water; extract with ether; wash organic layer with brine; dry over anhydrous sodium sulfate; evaporate.", ev),
                                     field("purification", "flash chromatography on silica gel", ev)]})
    return record(
        f"scheme4_{label}", f"Scheme 4 / synthesis of {label}", "reported_experiment", ev, ps, steps,
        [field("product_mass", {"number": product_mass, "unit": "mg"}, ev, ["product"]),
         field("yield", {"number": yld, "unit": "%"}, ev, ["product"]),
         field("yield_measurement_basis", "isolated after flash chromatography" if label == "3a" else None, ev, ["product"])],
        ["The article describes coupling-lactamization followed by gamma-hydroxylation, but does not state a separate hydroxylation reagent in this procedure."],
        COMMON_UNRESOLVED + ["Separate hydroxylation-stage conditions are not reported."] + (["The workup/purification basis for the reported yield is not stated."] if label == "3b" else []),
    )


records.append(detailed_lactam(
    "3a", "1a", "N-benzyl octa-2,3-dienamide", "CCCCC=C=CC(=O)NCc1ccccc1", 80, 0.35,
    97, 0.70, "DMF", "N,N-dimethylformamide", "CN(C)C=O", 2, 60, 0.53, 20, 0.017, 9,
    "1-benzyl-5-butyl-5-hydroxy-4-phenylpyrrol-2(5H)-one", "O=C1C=C(c2ccccc2)C(O)(CCCC)N1Cc1ccccc1", 50, 45,
))
records.append(detailed_lactam(
    "3b", "1b", "N-benzyl 4-cyclohexylbuta-2,3-dienamide", "O=C(NCc1ccccc1)C=C=CC1CCCCC1", 77, 0.30,
    83, 0.60, "toluene", "toluene", "Cc1ccccc1", 2, 52, 0.45, 17, 0.015, 30,
    "1-benzyl-5-cyclohexyl-5-hydroxy-4-phenylpyrrol-2(5H)-one", "O=C1C=C(c2ccccc2)C(O)(C2CCCCC2)N1Cc1ccccc1", 50, 48,
    tbab=(5, 0.016),
))

# Table 1: optimization rows. Entry 7 is also Table 2 entry 1 and the detailed 4a procedure.
table1 = [
    (1, "A", 5, 10, 4, 1.3, "toluene", 18.5, "h", 99),
    (2, "B", None, 10, 4, 1.3, "toluene", 18, "h", 99),
    (3, "B", None, None, 4, 1.3, "CH3CN", 17, "h", 92),
    (4, "B", None, None, 4, 1.3, "THF", 17, "h", 88),
    (5, "B", None, None, 4, 1.3, "DMF", 17, "h", 92),
    (6, "C", None, 5, 2, 1.1, "toluene", 4, "d", 67),
    (7, "B", None, 5, 2, 1.1, "toluene", 47, "h", 95),
]
solvents = {
    "toluene": ("toluene", "Cc1ccccc1"), "CH3CN": ("acetonitrile", "CC#N"),
    "THF": ("tetrahydrofuran", "C1CCOC1"), "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
}
for entry, catalyst_code, ag, tbab, k2co3, phi_eq, solv, time_n, time_u, yld in table1:
    ev = [eid(2), eid(2, "text")]
    if entry == 7:
        ev += [eid(4), eid(4, "text")]
    ps = [
        participant("substrate", "reactant", "1c", ev, name="N-benzyl 3-cyclohexylidene-2-propylacrylamide",
                    amounts=[amount("amount", 0.25, "mmol", ev)] if entry == 7 else []),
        participant("iodobenzene", "reactant", "PhI (2a)", ev, name="iodobenzene", smiles="Ic1ccccc1",
                    amounts=([amount("volume", 32, "uL", ev), amount("amount", 0.28, "mmol", ev)] if entry == 7 else []) + [amount("equivalents", phi_eq, "equiv", ev)]),
        participant("potassium_carbonate", "reagent", "K2CO3", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O",
                    amounts=([amount("mass", 68, "mg", ev), amount("amount", 0.49, "mmol", ev)] if entry == 7 else []) + [amount("equivalents", k2co3, "equiv", ev)]),
        participant("solvent", "solvent", solv, ev, name=solvents[solv][0], smiles=solvents[solv][1],
                    amounts=[amount("volume", 2, "mL", ev)] if entry == 7 else []),
        participant("product", "product", "4a", ev, name="N-benzyl (4-phenyl-3-propyl-1-oxa-spiro[4,5]dec-3-enylidene) amine"),
    ]
    if catalyst_code == "A":
        ps += [
            participant("pd2_dba3_chcl3", "catalyst", "Pd2(dba)3·CHCl3", ev, name="tris(dibenzylideneacetone)dipalladium chloroform adduct",
                        amounts=[amount("catalyst_loading", 2.5, "mol%", ev)]),
            participant("pph3", "reagent", "PPh3", ev, name="triphenylphosphine", smiles="P(c1ccccc1)(c1ccccc1)c1ccccc1",
                        amounts=[amount("loading", 10, "mol%", ev)]),
        ]
    elif catalyst_code == "B":
        loading = 1 if entry == 7 else 5
        extra = [amount("mass", 3, "mg", ev), amount("amount", 0.0026, "mmol", ev)] if entry == 7 else []
        ps.append(participant("catalyst", "catalyst", "Pd(PPh3)4", ev, name="tetrakis(triphenylphosphine)palladium(0)",
                              amounts=extra + [amount("catalyst_loading", loading, "mol%", ev)]))
    else:
        ps.append(participant("catalyst", "catalyst", "cyclic palladium complex 5 (C)", ev,
                              name="cyclic palladium complex 5", amounts=[amount("catalyst_loading", 1, "mol%", ev)]))
    if ag is not None:
        ps.append(participant("silver_carbonate", "reagent", "Ag2CO3", ev, name="silver carbonate", smiles="[Ag+].[Ag+].[O-]C([O-])=O",
                              amounts=[amount("loading", ag, "mol%", ev)]))
    if tbab is not None:
        tbab_amounts = [amount("mass", 4, "mg", ev), amount("amount", 0.012, "mmol", ev)] if entry == 7 else []
        ps.append(participant("tbab", "reagent", "TBAB", ev, name="tetra-n-butylammonium bromide", smiles="[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
                              amounts=tbab_amounts + [amount("loading", tbab, "mol%", ev)]))
    temp = "reflux" if entry == 4 else {"number": 70, "unit": "°C"}
    conditions = [field("temperature", temp, ev), amount("time", time_n, time_u, ev)]
    if entry == 7:
        conditions += [field("atmosphere", "Ar", ev), field("purification", "evaporation followed by flash chromatography on silica gel", ev)]
    source_id = f"Table 1 entry {entry}"
    if entry == 7:
        source_id += " / Table 2 entry 1 / typical procedure for 4a"
    outcomes = [field("yield", {"number": yld, "unit": "%"}, ev, ["product"]),
                field("yield_measurement_basis", "isolated after flash chromatography" if entry == 7 else None, ev, ["product"])]
    if entry == 7:
        outcomes.insert(0, field("product_mass", {"number": 84, "unit": "mg"}, ev, ["product"]))
    notes = ["Table 1 caption says reaction of 1a, while the depicted substrate and surrounding prose identify substrate 1c; 1c is retained and the discrepancy is unresolved."]
    if entry == 4:
        notes.append("Footnote b assigns reflux to the THF row, overriding the 70 °C condition printed over the common arrow.")
    if entry == 7:
        notes.append("This row is the same 1c/PhI -> 4a experiment reported as Table 2 entry 1 and in the detailed typical procedure; evidence is merged into one record.")
    records.append(record(
        f"table1_entry_{entry}", source_id, "optimization_entry", ev, ps,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in ps], "conditions": conditions}],
        outcomes, notes,
        COMMON_UNRESOLVED + (["Yield measurement basis is not stated for this optimization row."] if entry != 7 else []) +
        ["Product 4a structure was not converted to SMILES because the exocyclic imine/spiro connectivity requires independent structure review."],
    ))

# Table 2 entries 2-18; entry 1 is represented by Table 1 entry 7 above.
table2 = [
    (2, "1c", "R1,R2=(CH2)5; R3=n-Pr; R4=Bn", "p-MeC6H4 (2b)", "4-iodotoluene", "Cc1ccc(I)cc1", 47, 95, "4b", False),
    (3, "1c", "R1,R2=(CH2)5; R3=n-Pr; R4=Bn", "p-MeOC6H4 (2c)", "4-iodoanisole", "COc1ccc(I)cc1", 65, 95, "4c", False),
    (4, "1c", "R1,R2=(CH2)5; R3=n-Pr; R4=Bn", "p-NO2C6H4 (2d)", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", 72, 94, "4d", False),
    (5, "1c", "R1,R2=(CH2)5; R3=n-Pr; R4=Bn", "p-MeO2CC6H4 (2d)", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 44, 100, "4e", False),
    (6, "1d", "R1=R2=Me; R3=Bn; R4=Bn", "Ph (2a)", "iodobenzene", "Ic1ccccc1", 65, 96, "4f", False),
    (7, "1d", "R1=R2=Me; R3=Bn; R4=Bn", "p-MeC6H4 (2b)", "4-iodotoluene", "Cc1ccc(I)cc1", 48, 92, "4g", False),
    (8, "1d", "R1=R2=Me; R3=Bn; R4=Bn", "p-MeOC6H4 (2c)", "4-iodoanisole", "COc1ccc(I)cc1", 65, 93, "4h", False),
    (9, "1d", "R1=R2=Me; R3=Bn; R4=Bn", "p-NO2C6H4 (2d)", "1-iodo-4-nitrobenzene", "O=[N+]([O-])c1ccc(I)cc1", 72, 94, "4i", False),
    (10, "1d", "R1=R2=Me; R3=Bn; R4=Bn", "p-MeO2CC6H4 (2d)", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 72, 96, "4j", False),
    (11, "1e", "R1=R2=Me; R3=H; R4=Bn", "Ph (2a)", "iodobenzene", "Ic1ccccc1", 22, 90, "4k", False),
    (12, "1f", "R1=R2=Me; R3=H; R4=Bu", "Ph (2a)", "iodobenzene", "Ic1ccccc1", 24, 91, "4l", False),
    (13, "1g", "R1=R2=Me; R3=H; R4=H", "p-MeC6H4 (2b)", "4-iodotoluene", "Cc1ccc(I)cc1", 22, 94, "4m", False),
    (14, "1g", "R1=R2=Me; R3=H; R4=H", "p-MeOC6H4 (2c)", "4-iodoanisole", "COc1ccc(I)cc1", 22, 93, "4n", False),
    (15, "1g", "R1=R2=Me; R3=H; R4=H", "p-MeO2CC6H4 (2d)", "methyl 4-iodobenzoate", "COC(=O)c1ccc(I)cc1", 22, 90, "4o", False),
    (16, "1h", "R1=R2=Me; R3=Me; R4=Bn", "(E)-1-hexenyl", "(E)-1-hexenyl iodide", None, 17, 75, "4p", True),
    (17, "1h", "R1=R2=Me; R3=Me; R4=Bn", "(Z)-2-MeO2CCH=CH", "(Z)-methyl 3-iodoacrylate", None, 20, 99, "4q", True),
    (18, "1h", "R1=R2=Me; R3=Me; R4=Bn", "(E)-2-MeO2CCH=CH", "(E)-methyl 3-iodoacrylate", None, 20, 99, "4r", True),
]
for entry, substrate, subs, e_label, e_name, e_smiles, time_h, yld, product_label, special in table2:
    ev = [eid(2), eid(2, "text"), eid(3), eid(3, "text")] if special else [eid(2), eid(2, "text")]
    electrophile_eq = 1.5 if special else 1.1
    catalyst_loading = 5 if special else 1
    ps = [
        participant("substrate", "reactant", substrate, ev, name=f"2,3-allenamide {substrate} ({subs})",
                    amounts=[amount("amount", 0.25, "mmol", ev)]),
        participant("organic_iodide", "reactant", e_label, ev, name=e_name, smiles=e_smiles,
                    amounts=[amount("equivalents", electrophile_eq, "equiv", ev)]),
        participant("pd_pph3_4", "catalyst", "Pd(PPh3)4", ev, name="tetrakis(triphenylphosphine)palladium(0)",
                    amounts=[amount("catalyst_loading", catalyst_loading, "mol%", ev)]),
        participant("tbab", "reagent", "TBAB", ev, name="tetra-n-butylammonium bromide", smiles="[Br-].CCCC[N+](CCCC)(CCCC)CCCC",
                    amounts=[amount("loading", 5, "mol%", ev)]),
        participant("potassium_carbonate", "reagent", "K2CO3", ev, name="potassium carbonate", smiles="[K+].[K+].[O-]C([O-])=O",
                    amounts=[amount("equivalents", 2, "equiv", ev)]),
        participant("toluene", "solvent", "toluene", ev, name="toluene", smiles="Cc1ccccc1",
                    amounts=[amount("volume", 2, "mL", ev)]),
        participant("product", "product", product_label, ev, name=f"iminolactone {product_label} from {substrate} and {e_name}"),
    ]
    outcomes = [
        field("yield", {"number": yld, "unit": "%"}, ev, ["product"]),
        field("yield_measurement_basis", None, ev, ["product"]),
    ]
    if special:
        outcomes.append(field("alkene_stereochemical_outcome", "configuration of the C=C bond in the 1-alkenyl iodide remained intact", ev, ["product"]))
    notes = [f"Table 2 substituent assignment: {subs}."]
    if entry in (5, 10, 15):
        notes.append("The printed table uses label 2d for p-MeO2CC6H4, the same label also printed for p-NO2C6H4; the label collision is preserved without correction.")
    if special:
        notes.append("Footnote b overrides the common catalyst and organic-iodide loadings; both values are structured on their participants.")
    records.append(record(
        f"table2_entry_{entry}", f"Table 2 entry {entry}", "substrate_scope_entry", ev, ps,
        [{"step_id": "coupling_cyclization", "participant_ids": [p["entity_id"] for p in ps], "conditions": [
            amount("temperature", 70, "°C", ev), amount("time", time_h, "h", ev),
        ]}], outcomes, notes,
        COMMON_UNRESOLVED + ["Yield measurement basis is not stated in Table 2.", "Product structure was not converted from the generic R-group product drawing to SMILES."] +
        (["Exact alkenyl iodide SMILES was withheld pending independent E/Z structure review."] if special else []),
    ))

# Scheme 5 is a proposed mechanism, not a reported experiment.
ev = [eid(3), eid(3, "text")]
ps = [
    participant("organopalladium", "unspecified_agent", "R5PdI", ev, name="organic palladium iodide species"),
    participant("allenamide", "reactant", "generic 2,3-allenamide", ev, name="generic R-group 2,3-allenamide"),
    participant("lactam_branch", "product", "gamma-hydroxy-gamma-lactam branch product", ev, name="generic gamma-hydroxy-gamma-lactam"),
    participant("iminolactone_branch", "product", "iminolactone branch product", ev, name="generic iminolactone"),
]
records.append(record(
    "scheme5_mechanism", "Scheme 5", "mechanism", ev, ps, [], [],
    ["Proposed sequence: carbopalladation to a pi-allyl palladium intermediate; N-attack when R2=H gives the lactam branch; O-attack when R1/R2 are not H followed by base-mediated loss of H+ gives the iminolactone branch."],
    ["Scheme 5 is mechanistic and does not report a separate experimental yield.", "Generic R groups and intermediates are not converted to SMILES."],
))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT.relative_to(ROOT))}, ensure_ascii=False))
