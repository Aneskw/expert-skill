import json
from pathlib import Path

DOC = "doc_96bb7862efcf2053"
OUT = Path(__file__).with_name("records_pages_0001_0004.json")


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, raw_text=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    return value


def field(name, value, evidence, target=None):
    row = {"name": name, "fact": fact(value, evidence)}
    if target:
        row["target_entity_ids"] = list(target)
    return row


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(v, e) for v, e in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


P3 = [ev(3, "text"), ev(3)]
P2 = [ev(2, "text"), ev(2)]
P4 = [ev(4, "text"), ev(4)]


def amount(name, value, evidence):
    return field(name, value, evidence)


def common_1a(evidence, detailed=False):
    amounts = []
    if detailed:
        amounts = [
            amount("mass", qty(49.4, "mg"), P3),
            amount("amount", qty(0.29, "mmol"), P3),
            amount("nominal_reaction_scale", qty(0.3, "mmol"), P3),
        ]
    else:
        amounts = [amount("reaction_scale", qty(0.3, "mmol"), P3)]
    return participant(
        "1a", "reactant", "1a", "1,3,5-trimethoxybenzene", evidence,
        "COc1cc(OC)cc(OC)c1", amounts,
    )


def substrate_2a(evidence, detailed=False):
    amounts = [amount("equivalents", qty(1.2, "equiv"), P3)]
    if detailed:
        amounts = [
            amount("mass", qty(72.9, "mg"), P3),
            amount("amount", qty(0.36, "mmol"), P3),
            amount("equivalents", qty(1.2, "equiv"), P3),
        ]
    return participant(
        "2a", "reactant", "2a", "ethyl 2-methyl-4-phenylbuta-2,3-dienoate",
        evidence, "CCOC(=O)C(C)=C=Cc1ccccc1", amounts,
    )


def product_3a(evidence):
    return participant(
        "3a", "product", "(E)-3a",
        "ethyl (E)-2-methyl-4-phenyl-4-(2,4,6-trimethoxyphenyl)but-2-enoate",
        evidence,
        "CCOC(=O)/C(C)=C/C(c1ccccc1)c1c(OC)cc(OC)cc1OC",
    )


SOLVENTS = {
    "CH2Cl2": ("dichloromethane", "ClCCl"),
    "toluene": ("toluene", "Cc1ccccc1"),
    "DMA": ("N,N-dimethylacetamide", "CC(=O)N(C)C"),
    "TFA": ("trifluoroacetic acid", "O=C(O)C(F)(F)F"),
    "TCA": ("trichloroacetic acid", "O=C(O)C(Cl)(Cl)Cl"),
    "TfOH": ("trifluoromethanesulfonic acid", "OS(=O)(=O)C(F)(F)F"),
}


def solvent(entity_id, volume, evidence=P3):
    name, smiles = SOLVENTS[entity_id]
    amounts = [] if volume is None else [amount("volume", qty(volume, "mL"), evidence)]
    return participant(entity_id, "solvent", entity_id, name, evidence, smiles, amounts)


def optimization_record(entry, solvent_ids, recovery, product_yield, temp=40,
                        additive=None, additive_loading=None, merged_3a=False):
    evidence = P3[:]
    if entry in (1, 3, 4, 5, 6, 7, 8, 9):
        evidence += P2
    if merged_3a:
        evidence += P4
    participants = [common_1a(P3, merged_3a), substrate_2a(P3, merged_3a), product_3a(P3 + P4 if merged_3a else P3)]
    for sid in solvent_ids:
        volume = None if entry == 3 else (0.3 if sid in {"CH2Cl2", "toluene", "DMA"} else 1.2)
        participants.append(solvent(sid, volume))
    if additive:
        label, name, role = additive
        amounts = [amount("equivalents" if additive_loading[1] == "equiv" else "catalyst_loading",
                          qty(additive_loading[0], additive_loading[1]), P3)]
        participants.append(participant("additive", role, label, name, P3, None, amounts))
    participants.append(participant(
        "ch2br2_standard", "unspecified_agent", "CH2Br2", "dibromomethane internal standard",
        P3, "BrCBr",
    ))
    reaction_ids = [p["entity_id"] for p in participants if p["entity_id"] not in {"3a", "ch2br2_standard"}]
    steps = [{
        "step_id": "reaction",
        "participant_ids": reaction_ids,
        "conditions": [
            field("temperature", qty(temp, "°C"), P3),
            field("time", qty(15, "h"), P3),
            field("operation", "stirred; general optimization conditions", P3),
        ],
    }, {
        "step_id": "nmr_analysis",
        "participant_ids": ["ch2br2_standard"],
        "conditions": [field("operation", "1H NMR analysis with CH2Br2 as internal standard", P3)],
    }]
    outcomes = [
        field("recovered_starting_material_yield", qty(recovery, "%"), P3, ["1a"]),
        field("recovery_measurement_basis", "1H NMR", P3, ["1a"]),
        field("NMR_yield_of_3a", product_yield, P3, ["3a"]),
        field("NMR_yield_measurement_basis", "1H NMR with CH2Br2 internal standard", P3, ["3a"]),
    ]
    notes = []
    unresolved = [
        "Supporting information was not explicitly associated with this dataset.",
        "Structures are machine candidates and remain unverified against SI characterization.",
    ]
    if entry == 3:
        unresolved.append("Table 1 lists pure TFA but its common footnote still describes acid plus co-solvent volumes; total TFA volume was not inferred.")
    if merged_3a:
        # Replace generic quantities/operations with the detailed batch while retaining the row outcomes.
        cat = participant(
            "pdcl2_mecn2", "catalyst", "[PdCl2(MeCN)2]", "bis(acetonitrile)palladium(II) dichloride",
            P3, None,
            [amount("mass", qty(3.5, "mg"), P3), amount("amount", qty(0.013, "mmol"), P3),
             amount("catalyst_loading", qty(5, "mol%"), P3)],
        )
        participants = [p for p in participants if p["entity_id"] != "additive"]
        participants.insert(3, cat)
        reaction_ids = [p["entity_id"] for p in participants if p["entity_id"] not in {"3a", "ch2br2_standard"}]
        steps[0] = {
            "step_id": "reaction",
            "participant_ids": reaction_ids,
            "conditions": [
                field("operation", "1a, [PdCl2(MeCN)2], and DMA were added sequentially; 2a was added, followed by rinsing with TFA", P3),
                field("temperature", qty(40, "°C"), P3),
                field("time", qty(15, "h"), P3),
                field("operation", "stirred and monitored by TLC", P3),
            ],
        }
        steps.append({
            "step_id": "workup_and_purification",
            "participant_ids": ["3a"],
            "conditions": [
                field("workup", "quenched with 10 mL saturated aqueous NaHCO3; extracted with diethyl ether (15 mL × 3); washed with saturated aqueous NaHCO3; dried over anhydrous Na2SO4; filtered and evaporated", P3 + P4),
                field("purification", "silica gel chromatography, petroleum ether/ethyl acetate 7.5:1", P4),
            ],
        })
        outcomes += [
            field("isolated_yield", qty(64, "%"), P3 + P4, ["3a"]),
            field("isolated_product_mass", qty(69.6, "mg"), P4, ["3a"]),
            field("isolated_yield_measurement_basis", "isolated", P3 + P4, ["3a"]),
            field("double_bond_configuration", "E", P2 + P3, ["3a"]),
        ]
        notes += [
            ("Table 1 entry 9, Table 2 entry 1, Figure 1, and the Experimental Section describe the same 3a result and are represented once.", P2 + P3 + P4),
            ("White solid; melting point 90–92 °C; full NMR, IR, MS, and elemental analysis are reported on page 4.", P4),
        ]
    return record(
        f"table1_entry{entry}" if not merged_3a else "table1_entry9_table2_entry1_3a",
        "optimization_entry", evidence, participants, steps, outcomes, notes, unresolved,
    )


records = []
records.extend([
    optimization_record(1, ["CH2Cl2", "TFA"], 30, qty(31, "%")),
    optimization_record(2, ["toluene", "TFA"], 47, qty(29, "%")),
    optimization_record(3, ["TFA"], 35, qty(40, "%")),
    optimization_record(4, ["DMA", "TFA"], 32, qty(53, "%")),
    optimization_record(5, ["DMA", "TCA"], 36, qty(34, "%"), temp=60),
    optimization_record(6, ["DMA", "TfOH"], 29, "complex mixture"),
    optimization_record(7, ["DMA", "TFA"], 30, qty(43, "%"),
                        additive=("BF3·Et2O", "boron trifluoride diethyl etherate", "unspecified_agent"),
                        additive_loading=(1.0, "equiv")),
    optimization_record(8, ["DMA", "TFA"], 27, qty(41, "%"),
                        additive=("Sc(OTf)3", "scandium triflate", "unspecified_agent"),
                        additive_loading=(5, "mol%")),
    optimization_record(9, ["DMA", "TFA"], 0, qty(61, "%"),
                        additive=("[PdCl2(MeCN)2]", "bis(acetonitrile)palladium(II) dichloride", "catalyst"),
                        additive_loading=(5, "mol%"), merged_3a=True),
    optimization_record(10, ["DMA", "TFA"], 28, qty(46, "%"),
                        additive=("[Pd(OCOCF3)2]2", "palladium(II) trifluoroacetate dimer", "unspecified_agent"),
                        additive_loading=(5, "mol%")),
])


SCOPE = {
    2: ("2b", "ethyl 2-ethyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(CC)=C=Cc1ccccc1", "Ph", "Et", "(E)-3b", 40),
    3: ("2c", "ethyl 2-benzyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(Cc1ccccc1)=C=Cc1ccccc1", "Ph", "Bn", "(E)-3c", 50),
    4: ("2d", "ethyl 2-allyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(CC=C)=C=Cc1ccccc1", "Ph", "allyl", "(E)-3d", 37),
    5: ("2e", "ethyl 2-methyl-4-(naphthalen-1-yl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1cccc2ccccc12", "alpha-naphthyl", "Me", "(E)-3e", 69),
    6: ("2f", "ethyl 2-methyl-4-(4-methylphenyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccc(C)cc1", "p-MeC6H4", "Me", "(E)-3f", 61),
    7: ("2g", "ethyl 2-methyl-4-(4-methoxyphenyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccc(OC)cc1", "p-MeOC6H4", "Me", "(E)-3g", 38),
    8: ("2h", "ethyl 2-methyl-4-(4-fluorophenyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccc(F)cc1", "p-FC6H4", "Me", "(E)-3h", 70),
    9: ("2i", "ethyl 2-methyl-4-(4-chlorophenyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccc(Cl)cc1", "p-ClC6H4", "Me", "(E)-3i", 52),
    10: ("2j", "ethyl 2-methyl-4-(4-bromophenyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccc(Br)cc1", "p-BrC6H4", "Me", "(E)-3j", 51),
}


def table2_record(entry, row):
    label, name, smiles, r1, r2, product_label, yld = row
    participants = [
        common_1a(P3),
        participant(label, "reactant", label, name, P3, smiles,
                    [amount("equivalents", qty(1.2, "equiv"), P3)]),
        participant(product_label, "product", product_label,
                    f"ethyl (E)-2-{r2}-4-{r1}-4-(2,4,6-trimethoxyphenyl)but-2-enoate",
                    P3, None),
        participant("pdcl2_mecn2", "catalyst", "[PdCl2(MeCN)2]", "bis(acetonitrile)palladium(II) dichloride",
                    P3, None, [amount("catalyst_loading", qty(5, "mol%"), P3)]),
        solvent("DMA", 0.3), solvent("TFA", 1.2),
    ]
    temperature = 60 if entry == 10 else 40
    time = 24 if entry == 10 else 15
    evidence = P3 + (P2 if entry == 10 else [])
    return record(
        f"table2_entry{entry}", "substrate_scope_entry", evidence, participants,
        [{"step_id": "reaction", "participant_ids": ["1a", label, "pdcl2_mecn2", "DMA", "TFA"],
          "conditions": [field("temperature", qty(temperature, "°C"), P3),
                         field("time", qty(time, "h"), P3),
                         field("operation", "stirred; entry 10 was monitored by TLC to 100% conversion of 1a" if entry == 10 else "standard conditions", P3)]}],
        [field("reported_yield", qty(yld, "%"), P3, [product_label]),
         field("yield_measurement_basis", None, (), [product_label]),
         field("double_bond_configuration", "E", P3, [product_label])],
        [(f"Table substituents: R1={r1}; R2={r2}.", P3)],
        ["Yield basis is not stated in the Table 2 caption or footnote.",
         "Product stereochemical SMILES was not assigned from the variable-substitution drawing.",
         "Supporting information was not explicitly associated with this dataset."],
    )


for entry, row in SCOPE.items():
    records.append(table2_record(entry, row))


records.append(record(
    "table2_entry11_failed", "substrate_scope_entry", P2 + P3,
    [common_1a(P3),
     participant("2k", "reactant", "2k", "ethyl 2-methyl-4-(n-butyl)buta-2,3-dienoate", P3,
                 "CCOC(=O)C(C)=C=CCCCC", [amount("equivalents", qty(1.2, "equiv"), P3)]),
     participant("pdcl2_mecn2", "catalyst", "[PdCl2(MeCN)2]", "bis(acetonitrile)palladium(II) dichloride", P3,
                 None, [amount("catalyst_loading", qty(5, "mol%"), P3)]),
     solvent("DMA", 0.3), solvent("TFA", 1.2)],
    [{"step_id": "reaction", "participant_ids": ["1a", "2k", "pdcl2_mecn2", "DMA", "TFA"],
      "conditions": [field("temperature", qty(40, "°C"), P3), field("time", qty(15, "h"), P3),
                     field("operation", "standard conditions", P3)]}],
    [field("reported_product_yield", "table dash (–)", P3),
     field("recovered_starting_material_yield", qty(96, "%"), P3, ["1a"]),
     field("recovery_measurement_basis", "1H NMR", P3, ["1a"])],
    [("2k decomposed under the reaction conditions; the table dash was preserved and was not converted to zero.", P2 + P3)],
    ["No product label or explicit product amount is reported.",
     "Supporting information was not explicitly associated with this dataset."],
))


SCHEME5 = [
    ("3k", "1b", "anisole", "COc1ccccc1", "2a", "ethyl 2-methyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccccc1", "Ph", 52),
    ("3l", "1b", "anisole", "COc1ccccc1", "2e", "ethyl 2-methyl-4-(naphthalen-1-yl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1cccc2ccccc12", "alpha-naphthyl", 58),
    ("3m", "1b", "anisole", "COc1ccccc1", "2h", "ethyl 2-methyl-4-(4-fluorophenyl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccc(F)cc1", "p-FC6H4", 50),
    ("3n", "1c", "phenol", "Oc1ccccc1", "2a", "ethyl 2-methyl-4-phenylbuta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1ccccc1", "Ph", 40),
    ("3o", "1c", "phenol", "Oc1ccccc1", "2e", "ethyl 2-methyl-4-(naphthalen-1-yl)buta-2,3-dienoate", "CCOC(=O)C(C)=C=Cc1cccc2ccccc12", "alpha-naphthyl", 58),
]

for product_label, arene_label, arene_name, arene_smiles, allene_label, allene_name, allene_smiles, aryl, yld in SCHEME5:
    participants = [
        participant(arene_label, "reactant", arene_label, arene_name, P3, arene_smiles),
        participant(allene_label, "reactant", allene_label, allene_name, P3, allene_smiles),
        participant(product_label, "product", f"(E)-{product_label}",
                    f"ethyl (E)-4-{aryl}-4-(4-{'methoxy' if arene_label == '1b' else 'hydroxy'}phenyl)-2-methylbut-2-enoate",
                    P3, None),
        participant("pdcl2_mecn2", "catalyst", "[PdCl2(MeCN)2]", "bis(acetonitrile)palladium(II) dichloride", P3,
                    None, [amount("catalyst_loading", qty(5, "mol%"), P3)]),
        solvent("DMA", None), solvent("TFA", None),
    ]
    records.append(record(
        f"scheme5_{product_label}", "substrate_scope_entry", P2 + P3, participants,
        [{"step_id": "reaction", "participant_ids": [arene_label, allene_label, "pdcl2_mecn2", "DMA", "TFA"],
          "conditions": [field("temperature", qty(40, "°C"), P3), field("time", qty(15, "h"), P3),
                         field("solvent_ratio", "DMA/TFA 1:4 by volume", P3)]}],
        [field("reported_yield", qty(yld, "%"), P3, [product_label]),
         field("yield_measurement_basis", None, (), [product_label]),
         field("double_bond_configuration", "E", P3, [product_label])],
        [("Scheme 5 reports exclusive para C–H functionalization for anisole products; phenol products are also drawn para-substituted.", P2 + P3)],
        ["Reaction scale, individual solvent volumes, workup, purification, and yield basis are not stated in Scheme 5.",
         "Product stereochemical SMILES was not assigned from the scheme drawing.",
         "Supporting information was not explicitly associated with this dataset."],
    ))


# Prior-work arrows and conceptual schemes are retained but never treated as experiments from this paper.
for idx, (substrate, product, conditions) in enumerate([
    ("generic alkyne R–C≡C–EWG", "generic hydroarylation product", "Pd(OAc)2 or PtCl2/AgOAc; TFA/CH2Cl2"),
    ("generic alkynyl ketone R–C≡C–COMe", "generic hydroarylation product", "Pd(OAc)2 or PtCl2/AgOAc; TFA/CH2Cl2"),
    ("generic activated alkene", "generic hydroarylation product", "Pd(OAc)2 or PtCl2/AgOAc; TFA/CH2Cl2"),
], 1):
    evidence = [ev(1, "text"), ev(1)]
    records.append(record(
        f"scheme1_prior_arrow{idx}", "literature_example", evidence,
        [participant("arene", "reactant", "Ar–H", "generic arene", evidence),
         participant("unsaturated_partner", "reactant", substrate, substrate, evidence),
         participant("product", "product", product, product, evidence)],
        [{"step_id": "reported_prior_work", "participant_ids": ["arene", "unsaturated_partner"],
          "conditions": [field("operation", conditions, evidence)]}], [],
        [("Scheme 1 is explicitly captioned as work reported by Fujiwara.", evidence)],
        ["Generic R/Ar/EWG structures and alternative catalysts prevent assignment of a single fully specified batch."],
    ))


prior_examples = [
    ("scheme2_widenhoefer", "Widenhoefer intramolecular allene hydroarylation", "2.5 mol% chiral AuCl complex; 5 mol% AgBF4; toluene", qty(-10, "°C"), qty(17, "h"), 88, ("ee", 92)),
    ("scheme2_ohno", "Ohno intramolecular hydroarylation of N-(1,2-allenyl)aniline", "AuI/AgOTf (1 mol%); dioxane or AcOH", "RT→reflux", None, {"minimum": 40, "maximum": 98, "unit": "%", "raw_text": "40–98%"}, None),
    ("scheme2_nelson", "Nelson intramolecular annulation of an enantioenriched allene with pyrrole", "5 mol% Ph3P–AuOTf", None, None, 92, None),
]
for suffix, title, condition_text, temperature, time_value, yld, extra in prior_examples:
    evidence = [ev(1, "text"), ev(1)]
    outcomes = [field("reported_yield", qty(yld, "%") if isinstance(yld, int) else yld, evidence, ["product"])]
    if extra:
        outcomes.append(field(extra[0], qty(extra[1], "%"), evidence, ["product"]))
    conditions = [field("operation", condition_text, evidence)]
    if temperature is not None:
        conditions.append(field("temperature", temperature, evidence))
    if time_value is not None:
        conditions.append(field("time", time_value, evidence))
    records.append(record(
        suffix, "literature_example", evidence,
        [participant("substrate", "reactant", title + " substrate", title + " substrate", evidence),
         participant("product", "product", title + " product", title + " product", evidence)],
        [{"step_id": "reported_prior_work", "participant_ids": ["substrate"], "conditions": conditions}], outcomes,
        [("Scheme 2 and adjacent prose identify this as previously reported gold(I)-catalyzed work.", evidence)],
        ["Compound identities are depicted but not named; no current-paper batch is represented."],
    ))


records.append(record(
    "scheme3_gagne_prior_work", "literature_example", P2,
    [participant("trimethoxybenzene", "reactant", "1,3,5-trimethoxybenzene", "1,3,5-trimethoxybenzene", P2, "COc1cc(OC)cc(OC)c1"),
     participant("allene", "reactant", "3-methylbuta-1,2-diene", "3-methylbuta-1,2-diene", P2, "CC(=C=C)C"),
     participant("product", "product", "Scheme 3 hydroarylation product", "prior-work hydroarylation product", P2),
     participant("gold_catalyst", "catalyst", "[(4-ClC6H4O)3PAuCl]", "aryl phosphite gold(I) chloride complex", P2,
                 None, [amount("catalyst_loading", qty(5, "mol%"), P2)]),
     participant("agbf4", "unspecified_agent", "AgBF4", "silver tetrafluoroborate", P2,
                 None, [amount("amount", qty(5, "mol%"), P2)]),
     participant("ch2cl2", "solvent", "CH2Cl2", "dichloromethane", P2, "ClCCl")],
    [{"step_id": "reported_prior_work", "participant_ids": ["trimethoxybenzene", "allene", "gold_catalyst", "agbf4", "ch2cl2"],
      "conditions": [field("temperature", "RT", P2), field("time", qty(2, "h"), P2)]}],
    [field("reported_yield", qty(67, "%"), P2, ["product"]), field("yield_measurement_basis", None, (), ["product"])],
    [("Scheme 3 is explicitly described as the recent intermolecular result by Gagné and is not a new experiment in this paper.", P2)],
    ["Yield basis and exact product name are not stated in the main-text scheme."],
))


records.append(record(
    "scheme4_carbopalladation_possibilities", "general_scheme", P2,
    notes=[("Scheme 4 enumerates eight possible regio-/stereochemical carbopalladation intermediates from a generic 2,3-allenoate and aryl–Pd species; it is a conceptual selectivity scheme, not an experimental batch.", P2)],
    unresolved=["Generic Ar/R substituents and intermediates were not converted into specific molecule records."],
))

records.append(record(
    "scheme6_proposed_mechanism", "mechanism", P3,
    notes=[("Proposed cycle: electrophilic palladation gives M1; allene/carbonyl coordination gives M2; syn insertion gives M3; protonation releases (E)-3 and regenerates Pd(II).", P3)],
    unresolved=["The proposed intermediates are mechanistic hypotheses, not isolated experimental products."],
))


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
