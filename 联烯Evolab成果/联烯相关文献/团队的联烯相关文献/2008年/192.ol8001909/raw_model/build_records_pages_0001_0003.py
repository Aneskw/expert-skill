from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/records_pages_0001_0003.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0001_0003.json"
TASKS = ROOT / "runs/current/tasks.json"
DOC = "doc_8c3e8ad28aeff2c7"
P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


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
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, steps, outcomes, *, notes=None, unresolved=None):
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
            "unresolved": unresolved or [],
        },
    }


def step(step_id, participants, conditions):
    return {"step_id": step_id, "participant_ids": participants, "conditions": conditions}


def amount(name, value, evidence):
    return field(name, value, evidence)


records = []

# Page 1 graphical abstract: a family-level summary, not a row-level experiment.
records.append(record(
    "graphical_abstract_general_scheme",
    "general_scheme",
    P1,
    [
        participant("ga_allene", "reactant", "generic 1-aryl-3-alkylpropadiene", P1),
        participant("ga_lda", "reagent", "LDA", P1, name="lithium diisopropylamide",
                    amounts=[amount("equivalents", qty(2, "equiv"), P1)]),
        participant("ga_znbr2", "reagent", "ZnBr2", P1, name="zinc bromide", smiles="[Br-].[Br-].[Zn+2]"),
        participant("ga_ri", "reactant", "RI (R = aryl or alkenyl)", P1),
        participant("ga_pd", "catalyst", "Pd(PPh3)4", P1,
                    amounts=[amount("catalyst_loading", qty(5, "mol%"), P1)]),
        participant("ga_product", "product", "generic trisubstituted allene", P1),
    ],
    [step("summary", ["ga_allene", "ga_lda", "ga_znbr2", "ga_ri", "ga_pd", "ga_product"], [])],
    [
        field("reported_yield_range", {"minimum": 56, "maximum": 92, "unit": "%", "raw_text": "56-92%"}, P1, ["ga_product"]),
        field("reported_regioselectivity", "up to >99:1", P1, ["ga_product"]),
    ],
    notes=["Graphical abstract summarizes the later optimization/scope chemistry and is not an additional executed experiment."],
    unresolved=["Generic Ar, Alkyl, and R groups do not define a single molecular structure.", "Time, temperature, scale, atmosphere, workup, purification, and yield basis are absent from this summary."],
))


substrates = {
    "1a": ("1a", "1-phenyl-1,2-octadiene; Ar = Ph, R1 = n-C5H11", "CCCCCC=C=Cc1ccccc1"),
    "1b": ("1b", "1-phenyl-1,2-nonadiene; Ar = Ph, R1 = n-C6H13", "CCCCCCC=C=Cc1ccccc1"),
    "1c": ("1c", "1-(4-methoxyphenyl)-1,2-nonadiene; R1 = n-C6H13", "CCCCCCC=C=Cc1ccc(OC)cc1"),
    "1d": ("1d", "1-(4-methylphenyl)-1,2-nonadiene; R1 = n-C6H13", "CCCCCCC=C=Cc1ccc(C)cc1"),
}

iodides = {
    "2a": ("2a", "methyl 4-iodobenzoate (p-MeO2CC6H4I)", "COC(=O)c1ccc(I)cc1"),
    "2b": ("2b", "1-bromo-4-iodobenzene", "Brc1ccc(I)cc1"),
    "2c": ("2c", "1-fluoro-4-iodobenzene", "Fc1ccc(I)cc1"),
    "2d": ("2d", "4-iodobenzonitrile", "N#Cc1ccc(I)cc1"),
    "2e": ("2e", "iodobenzene", "Ic1ccccc1"),
    "2f": ("2f", "4-iodoanisole", "COc1ccc(I)cc1"),
    "2g": ("2g", "1-iodo-3-methylbenzene", "Cc1cccc(I)c1"),
    "2h": ("2h", "1-iodonaphthalene", "Ic1cccc2ccccc12"),
    "2i": ("2i", "printed (E)-n-BuCH=CH2 alkenyl iodide substituent", None),
    "2j": ("2j", "printed (E)-C6H4CH=CH2 alkenyl iodide substituent", None),
    "2k": ("2k", "printed (E)-C6H13CH=CH2 alkenyl iodide substituent", None),
}


def std_participants(substrate_code, iodide_code, product_code, evidence, iodide_mmol=0.4, product_smiles=None):
    slabel, sname, ssmiles = substrates[substrate_code]
    ilabel, iname, ismiles = iodides[iodide_code]
    return [
        participant("allene", "reactant", slabel, evidence, name=sname, smiles=ssmiles,
                    amounts=[amount("amount", qty(0.5, "mmol"), evidence)]),
        participant("iodide", "reactant", ilabel, evidence, name=iname, smiles=ismiles,
                    amounts=[amount("amount", qty(iodide_mmol, "mmol"), evidence)]),
        participant("lda", "reagent", "LDA", evidence, name="lithium diisopropylamide",
                    amounts=[amount("amount", qty(1.0, "mmol"), evidence), amount("equivalents", qty(2.0, "equiv"), evidence)]),
        participant("znbr2", "reagent", "ZnBr2", evidence, name="zinc bromide", smiles="[Br-].[Br-].[Zn+2]",
                    amounts=[amount("amount", qty(2.0, "mmol"), evidence), amount("equivalents", qty(4.0, "equiv"), evidence)]),
        participant("pd", "catalyst", "Pd(PPh3)4", evidence,
                    amounts=[amount("amount", qty(0.020, "mmol"), evidence), amount("catalyst_loading", qty(5, "mol%"), evidence)]),
        participant("product", "product", product_code, evidence, name=f"trisubstituted allene {product_code}", smiles=product_smiles),
    ]


def scope_steps(evidence, cold_overnight=False):
    coupling_conditions = [
        field("temperature", qty(0, "°C") if cold_overnight else "r.t.", evidence),
        field("time", "overnight" if cold_overnight else None, evidence),
    ]
    return [
        step("lithiation", ["allene", "lda"], [
            field("thermal_program", "-78 °C to r.t.", evidence),
            field("time", qty(1, "h"), evidence),
        ]),
        step("transmetalation", ["allene", "znbr2"], [
            field("temperature", "r.t.", evidence),
            field("time", qty(20, "min"), evidence),
        ]),
        step("negishi_coupling", ["allene", "iodide", "pd", "product"], coupling_conditions),
    ]


# Table 1 entry 1 and Table 2 entry 4 are the same printed substrate/iodide/condition.
merged_evidence = P2
parts = std_participants("1a", "2d", "3ad", merged_evidence, product_smiles="CCCCCC(c1ccc(C#N)cc1)=C=Cc1ccccc1")
parts.append(participant("regioisomer", "product", "4ad", merged_evidence, name="propargylic regioisomer 4ad"))
records.append(record(
    "table1_entry1_table2_entry4_3ad",
    "optimization_entry",
    merged_evidence,
    parts,
    [
        step("lithiation", ["allene", "lda"], [field("solvent", "THF", P2), field("thermal_program", "-78 °C to 24 °C", P2), field("time", qty(1, "h"), P2)]),
        step("transmetalation", ["allene", "znbr2"], [field("temperature", "r.t.", P2), field("time", qty(20, "min"), P2)]),
        step("negishi_coupling", ["allene", "iodide", "pd", "product", "regioisomer"], [field("temperature", "r.t.", P2), field("time", qty(2, "h"), P2)]),
    ],
    [
        field("table1_nmr_yield_3ad", qty(84, "%"), P2, ["product"]),
        field("table1_yield_measurement_basis", "NMR using dibromomethane as internal standard, based on iodide", P2),
        field("crude_3ad_to_4ad_ratio", ">98:2", P2, ["product", "regioisomer"]),
        field("ratio_measurement_basis", "NMR analysis of crude products", P2),
        field("table2_isolated_yield_3ad", qty(68, "%"), P2, ["product"]),
        field("table2_yield_measurement_basis", "isolated yield based on iodide", P2),
    ],
    notes=["The identical optimized 1a/2d condition appears as Table 1 entry 1 and Table 2 entry 4; both measurement-specific yields are retained."],
    unresolved=["The paper does not explicitly say whether the two table appearances are the same physical execution or repeated runs.", "Atmosphere, workup, and purification are not reported in the main text."],
))


# Remaining Table 1 optimization entries.
table1 = [
    (2, "LDA", 1.5, "-78 °C to 24 °C", 71, ">99:1"),
    (3, "LDA", 1.2, "-78 °C to 24 °C", 25, ">99:1"),
    (4, "LDA", 2.0, "-78 °C", 67, ">99:1"),
    (5, "n-BuLi", 2.0, "-78 °C to 24 °C", 88, "96:4"),
]
for entry, base_label, equiv, temp, yld, ratio in table1:
    base_id = "base"
    parts = [
        participant("allene", "reactant", "1a", P2, name=substrates["1a"][1], smiles=substrates["1a"][2]),
        participant("iodide", "reactant", "2d", P2, name=iodides["2d"][1], smiles=iodides["2d"][2], amounts=[amount("equivalents", qty(0.8, "equiv"), P2)]),
        participant(base_id, "reagent", base_label, P2, name="lithium diisopropylamide" if base_label == "LDA" else "n-butyllithium", amounts=[amount("equivalents", qty(equiv, "equiv"), P2)]),
        participant("znbr2", "reagent", "ZnBr2", P2, name="zinc bromide", smiles="[Br-].[Br-].[Zn+2]", amounts=[amount("equivalents", qty(4, "equiv"), P2)]),
        participant("pd", "catalyst", "Pd(PPh3)4", P2, amounts=[amount("catalyst_loading", qty(5, "mol%"), P2)]),
        participant("product", "product", "3ad", P2, name="1-phenyl-3-(4-cyanophenyl)octa-1,2-diene", smiles="CCCCCC(c1ccc(C#N)cc1)=C=Cc1ccccc1"),
        participant("regioisomer", "product", "4ad", P2, name="propargylic regioisomer 4ad"),
    ]
    if entry == 4:
        lith_conditions = [field("solvent", "THF", P2), field("temperature", qty(-78, "°C"), P2), field("time", qty(1, "h"), P2)]
        tm_conditions = [field("temperature", qty(-78, "°C"), P2), field("time", None, P2), field("subsequent_operation", "warm reaction mixture to room temperature", P2)]
    else:
        lith_conditions = [field("solvent", "THF", P2), field("thermal_program", temp, P2), field("time", qty(1, "h"), P2)]
        tm_conditions = [field("thermal_program", "then warm to room temperature", P2), field("time", None, P2)]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", P2, parts,
        [
            step("lithiation", ["allene", base_id], lith_conditions),
            step("transmetalation", ["allene", "znbr2"], tm_conditions),
            step("negishi_coupling", ["allene", "iodide", "pd", "product", "regioisomer"], [field("temperature", "r.t.", P2), field("time", qty(2, "h"), P2)]),
        ],
        [
            field("nmr_yield_3ad", qty(yld, "%"), P2, ["product"]),
            field("yield_measurement_basis", "NMR using dibromomethane as internal standard, based on iodide", P2),
            field("crude_3ad_to_4ad_ratio", ratio, P2, ["product", "regioisomer"]),
            field("ratio_measurement_basis", "NMR analysis of crude products", P2),
        ],
        unresolved=["Absolute scale, atmosphere, transmetalation duration, workup, and purification are not reported for this optimization row."],
    ))


scope_rows = [
    (1, "1a", "2a", 75, "3aa", 0.4, False, "CCCCCC(c1ccc(C(=O)OC)cc1)=C=Cc1ccccc1"),
    (2, "1a", "2b", 79, "3ab", 0.4, False, "CCCCCC(c1ccc(Br)cc1)=C=Cc1ccccc1"),
    (3, "1a", "2c", 73, "3ac", 0.4, False, "CCCCCC(c1ccc(F)cc1)=C=Cc1ccccc1"),
    # entry 4 is merged above
    (5, "1b", "2e", 92, "3be", 0.4, False, "CCCCCCC(c1ccccc1)=C=Cc1ccccc1"),
    (6, "1b", "2f", 79, "3bf", 0.4, False, "CCCCCCC(c1ccc(OC)cc1)=C=Cc1ccccc1"),
    (7, "1b", "2a", 86, "3ba", 0.4, False, "CCCCCCC(c1ccc(C(=O)OC)cc1)=C=Cc1ccccc1"),
    (8, "1b", "2b", 84, "3bb", 0.4, False, "CCCCCCC(c1ccc(Br)cc1)=C=Cc1ccccc1"),
    (9, "1b", "2g", 82, "3bg", 0.4, False, "CCCCCCC(c1cccc(C)c1)=C=Cc1ccccc1"),
    (10, "1b", "2h", 57, "3bh", 0.4, False, None),
    (11, "1b", "2i", 56, "3bi", 0.4, True, None),
    (12, "1a", "2j", 71, "3aj", 0.4, True, None),
    (13, "1a", "2k", 68, "3ak", 0.4, True, None),
    (14, "1c", "2a", 78, "3ca", 0.3, False, "CCCCCCC(c1ccc(C(=O)OC)cc1)=C=Cc1ccc(OC)cc1"),
    (15, "1c", "2f", 80, "3cf", 0.4, False, "CCCCCCC(c1ccc(OC)cc1)=C=Cc1ccc(OC)cc1"),
    (16, "1d", "2d", 81, "3dd", 0.2, False, "CCCCCCC(c1ccc(C#N)cc1)=C=Cc1ccc(C)cc1"),
]
for entry, substrate_code, iodide_code, yld, product_code, iodide_mmol, cold, product_smiles in scope_rows:
    parts = std_participants(substrate_code, iodide_code, product_code, P2, iodide_mmol, product_smiles)
    outcomes = [
        field("isolated_yield", qty(yld, "%"), P2, ["product"]),
        field("yield_measurement_basis", "isolated yield based on iodide", P2),
    ]
    unresolved = ["Atmosphere, workup, and purification are not reported."]
    if not cold:
        unresolved.append("The coupling duration is not stated for this row.")
    if entry == 14:
        outcomes.append(field("recovered_aryl_iodide_yield", qty(22, "%"), P2, ["iodide"]))
    if iodide_code in {"2i", "2j", "2k"}:
        unresolved.append("The compact printed alkenyl substituent formula requires expert review before assigning a constitutional SMILES.")
    records.append(record(
        f"table2_entry{entry}_{product_code}", "substrate_scope_entry", P2, parts,
        scope_steps(P2, cold), outcomes,
        unresolved=unresolved,
    ))


def deut_participants(base_label, base_equiv):
    return [
        participant("allene_d", "reactant", "1a-d", P3, name="1-deuterated-1-phenylocta-1,2-diene", amounts=[]),
        participant("base", "reagent", base_label, P3, name="lithium diisopropylamide" if base_label == "LDA" else "n-butyllithium", amounts=[amount("equivalents", qty(base_equiv, "equiv"), P3)]),
        participant("znbr2", "reagent", "ZnBr2", P3, name="zinc bromide", smiles="[Br-].[Br-].[Zn+2]", amounts=[amount("equivalents", qty(4, "equiv"), P2)]),
        participant("iodide", "reactant", "p-MeOC6H4I (2f)", P3, name="4-iodoanisole", smiles="COc1ccc(I)cc1", amounts=[amount("equivalents", qty(0.8, "equiv"), P2)]),
        participant("pd", "catalyst", "Pd(PPh3)4", P3, amounts=[amount("catalyst_loading", qty(5, "mol%"), P3)]),
        participant("product", "product", "3af-d", P3, name="deuterium-labeled trisubstituted allene 3af-d"),
    ]


for run, base_label, base_equiv, temp, yld, deuterium in [
    (1, "LDA", 2.0, "-78 °C to r.t.", 94, 76),
    (2, "n-BuLi", 1.5, "-78 °C", 89, 99),
]:
    outcomes = [
        field("reported_yield", qty(yld, "%"), P3, ["product"]),
        field("product_deuterium_incorporation", qty(deuterium, "%"), P3, ["product"]),
        field("starting_material_deuterium_incorporation", {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99% D"}, P3, ["allene_d"]),
        field("yield_measurement_basis", None, P3),
    ]
    if run == 2:
        outcomes.append(field("regioisomeric_product", "not observed", P3, ["product"]))
    records.append(record(
        f"scheme1_deuterium_run{run}", "reported_experiment", P2 + P3,
        deut_participants(base_label, base_equiv),
        [
            step("lithiation", ["allene_d", "base"], [field("thermal_program", temp, P3), field("time", qty(1, "h"), P3)]),
            step("transmetalation", ["allene_d", "znbr2"], [field("temperature", "r.t.", P2), field("time", qty(20, "min"), P2)]),
            step("negishi_coupling", ["allene_d", "iodide", "pd", "product"], [field("temperature", "r.t.", P3), field("time", qty(2, "h"), P3)]),
        ],
        outcomes,
        notes=["The prose calls these the standard reaction conditions; standard ZnBr2 and iodide equivalents are therefore linked from Table 2."],
        unresolved=["Absolute scale, atmosphere, workup, purification, and yield basis are not reported.", "The deuterated substrate/product constitutional and isotopic SMILES remain unverified."],
    ))


records.append(record(
    "scheme2_proposed_lithiation_mechanism",
    "mechanism",
    P3,
    [
        participant("m_substrate", "reactant", "generic allene 1", P3),
        participant("m_lda", "reagent", "LDA", P3),
        participant("m_nbuli", "reagent", "n-BuLi", P3),
        participant("m_m1", "unspecified_agent", "allenyl lithium intermediate M1", P3),
        participant("m_m2", "unspecified_agent", "propargyl/allenyl lithium intermediate M2", P3),
        participant("m_5", "unspecified_agent", "alkyne derivative 5", P3),
        participant("m_product", "product", "generic trisubstituted allene 3", P3),
    ],
    [],
    [],
    notes=["Proposed path a invokes direct 3-lithiation plus minor 1-lithiation/1,3-lithium-hydrogen exchange; proposed path b invokes alkyne 5 and organozinc-mediated isomerization.", "The authors' control experiments exclude path b under the tested conditions."],
    unresolved=["This is a proposed mechanism, not a set of independently executed reaction steps.", "Generic R-group and organolithium/organozinc structures are not assigned verified SMILES."],
))


records.append(record(
    "prose_5a_nbutylzinc_control",
    "reported_experiment",
    P3,
    [
        participant("alkyne_5a", "reactant", "5a", P3, name="alkyne derivative 5a"),
        participant("nbuznbr", "reagent", "n-BuZnBr", P3, name="n-butylzinc bromide", amounts=[amount("equivalents", qty(2, "equiv"), P3)]),
        participant("thf", "solvent", "THF", P3, name="tetrahydrofuran", smiles="C1CCOC1"),
    ],
    [step("isomerization_control", ["alkyne_5a", "nbuznbr", "thf"], [field("temperature", "r.t.", P3), field("time", qty(4, "h"), P3)])],
    [field("isomerization_outcome", "no isomerization", P3, ["alkyne_5a"])],
    unresolved=["Absolute scale, solvent volume, atmosphere, workup, purification, and recovery amount are not reported."],
))


records.append(record(
    "scheme3_5a_organozinc_control",
    "reported_experiment",
    P3,
    [
        participant("allene_1c", "reactant", "1c", P3, name=substrates["1c"][1], smiles=substrates["1c"][2]),
        participant("alkyne_5a", "reactant", "5a", P3, name="alkyne derivative 5a"),
        participant("lda", "reagent", "LDA", P3, name="lithium diisopropylamide", amounts=[amount("equivalents", qty(2, "equiv"), P3)]),
        participant("znbr2", "reagent", "ZnBr2", P3, name="zinc bromide", smiles="[Br-].[Br-].[Zn+2]"),
        participant("thf", "solvent", "THF", P3, name="tetrahydrofuran", smiles="C1CCOC1"),
        participant("protonated_mix", "product", "protonated propargyl/1,2-allenyl zinc-species mixture", P3),
    ],
    [
        step("generate_organozinc", ["allene_1c", "lda", "znbr2"], [field("thermal_program", "-78 °C to r.t.; ZnBr2 at r.t.", P3), field("time", None, P3)]),
        step("challenge_with_5a", ["alkyne_5a", "thf", "protonated_mix"], [field("temperature", "r.t.", P3), field("time", "overnight", P3)]),
    ],
    [
        field("reaction_outcome", "no reaction", P3, ["alkyne_5a"]),
        field("recovered_5a_yield", qty(90, "%"), P3, ["alkyne_5a"]),
        field("recovery_measurement_basis", None, P3),
        field("isolated_material_identity", "protonated mixture of propargyl/1,2-allenyl zinc species", P3, ["protonated_mix"]),
    ],
    unresolved=["ZnBr2 amount, exact generation duration, absolute scale, atmosphere, workup, purification, and recovery basis are not reported.", "The isolated mixture is not resolved into individual compounds or structures."],
))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {
                    "region": "title, graphical abstract, abstract, and introduction across the original page",
                    "finding": "The graphical abstract is a family-level general scheme (56–92% summary yield; up to >99:1 regioselectivity), not a row-level experiment. The remaining page is abstract/introduction/background citations.",
                    "evidence_ids": P1,
                }
            ],
            "record_ids": [f"{DOC}:graphical_abstract_general_scheme"],
            "unresolved": ["Generic Ar/Alkyl/R structures and omitted operational details prevent a complete experiment record."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {
                    "region": "left-column Table 1 reaction arrow, five optimization rows, footnotes, and discussion",
                    "finding": "All five optimization rows were extracted; Table 1 entry 1 was evidence-merged with the identical Table 2 entry 4 condition while retaining its NMR yield and crude regioisomer ratio.",
                    "evidence_ids": P2,
                },
                {
                    "region": "upper-right Table 2 reaction arrow, sixteen scope rows, and footnotes",
                    "finding": "All sixteen scope rows were inventoried with common quantities and row-specific 0 °C/overnight, 0.3 mmol, 0.2 mmol, and 22% iodide-recovery exceptions.",
                    "evidence_ids": P2,
                },
                {
                    "region": "lower-page results prose and references",
                    "finding": "Narrative selectivity/scope statements were linked to the table records; cited prior work was not promoted to present-paper experiments.",
                    "evidence_ids": P2,
                },
            ],
            "record_ids": [r["record_id"] for r in records if r["record_id"].startswith(f"{DOC}:table")],
            "unresolved": ["Atmosphere, most coupling durations, workup, and purification are absent from the main paper.", "Compact alkenyl formulas for 2i–2k require expert structure review."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left Scheme 1 and adjacent deuterium-labeling discussion",
                    "finding": "Two distinct deuterium-labeling runs were extracted with base loading, temperature/time, yield, and product deuterium incorporation.",
                    "evidence_ids": P3,
                },
                {
                    "region": "lower-left Scheme 2 and mechanism discussion",
                    "finding": "The lithiation/1,3-exchange versus alkyne-isomerization pathways were classified as a proposed mechanism, not executed reaction stages.",
                    "evidence_ids": P3,
                },
                {
                    "region": "upper-right control-experiment prose and Scheme 3",
                    "finding": "Two independent negative controls were extracted: 5a with n-BuZnBr for 4 h (no isomerization) and 5a with organozinc species generated from 1c overnight (no reaction; 90% recovery).",
                    "evidence_ids": P3,
                },
                {
                    "region": "conclusion, acknowledgments, SI availability statement, and reference 9",
                    "finding": "No additional reaction row was created. The online SI statement does not establish an SI association in this workspace.",
                    "evidence_ids": P3,
                },
            ],
            "record_ids": [f"{DOC}:scheme1_deuterium_run1", f"{DOC}:scheme1_deuterium_run2", f"{DOC}:scheme2_proposed_lithiation_mechanism", f"{DOC}:prose_5a_nbutylzinc_control", f"{DOC}:scheme3_5a_organozinc_control"],
            "unresolved": ["No supplied SI; detailed procedures and spectroscopic data were not imported.", "Deuterated, organolithium, organozinc, and mixture structures remain unverified."],
        },
    ],
}
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page1:text", f"{DOC}:page2:text", f"{DOC}:page3:text"}:
        task["state"] = "attempted"
TASKS.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
