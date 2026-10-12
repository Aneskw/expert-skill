#!/usr/bin/env python3
"""Build evidence-linked records and coverage for PDF pages 19-23."""

import json
from pathlib import Path


DOC = "doc_eb61b148fa9cdbba"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/extracted_records_pages_0019_0023.json"
COVERAGE = ROOT / "runs/current/coverage/pages_0019_0023.json"


def evid(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def all_evid(pages):
    return [evidence_id for page in pages for evidence_id in evid(page)]


def fact(value, evidence_ids):
    return {
        "value": value,
        "evidence_ids": list(evidence_ids) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def fld(name, value, evidence_ids, targets=None):
    item = {"name": name, "fact": fact(value, evidence_ids)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, smiles=None, amounts=None, name=None, evidence_ids=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence_ids),
        "name": fact(name, evidence_ids) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence_ids) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(field_name, value, evidence_ids) for field_name, value in (amounts or [])],
    }


def record(sid, pages, kind, participants, conditions=None, outcomes=None, notes=None,
           unresolved=None, add_missing=True, step_specs=None):
    evidence_ids = all_evid(pages)
    conditions = list(conditions or [])
    outcomes = list(outcomes or [])
    if add_missing and kind == "literature_example":
        if not any(name == "temperature" for name, _ in conditions):
            conditions.append(("temperature", None))
        if not any(name == "time" for name, _ in conditions):
            conditions.append(("time", None))
        if not any("yield" in name for name, _, _ in outcomes):
            outcomes.append(("yield", None, None))

    participant_records = [part(*participant[:6], evidence_ids=evidence_ids) for participant in participants]
    if step_specs is not None:
        steps = [
            {
                "step_id": step_id,
                "participant_ids": list(participant_ids),
                "conditions": [fld(name, value, evidence_ids) for name, value in step_conditions],
            }
            for step_id, participant_ids, step_conditions in step_specs
        ]
    elif kind in ("mechanism", "general_scheme"):
        steps = []
    else:
        steps = [{
            "step_id": "step1",
            "participant_ids": [participant[0] for participant in participants],
            "conditions": [fld(name, value, evidence_ids) for name, value in conditions],
        }]

    if kind == "literature_example":
        default_unresolved = [
            "Prior-literature example summarized by this review; it is not a new experiment reported by the review authors.",
            "No explicitly associated supporting information was supplied.",
            "The reviewed pages do not provide a complete original experimental procedure, workup, purification, or yield basis.",
        ]
    else:
        default_unresolved = [
            "Generic or mechanistic drawing; it is not an individual reported experiment.",
            "Generic substituents and/or transient radicals prevent a fully specified structure assignment.",
        ]

    return {
        "record_id": f"{DOC}:{sid}",
        "document_id": DOC,
        "source_reaction_id": sid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence_ids,
        "participants": participant_records,
        "steps": steps,
        "outcomes": [fld(name, value, evidence_ids, targets) for name, value, targets in outcomes],
        "notes": [fact(note, evidence_ids) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": default_unresolved + list(unresolved or []),
        },
    }


R = []

# Page 19: thermal allene addition/polymerization and selenium-substituted allene dimerization.
R.append(record("p19_scheme40_substituted_allene_dimerization_mechanism", [19], "mechanism", [
    ("substituted_allene", "reactant", "stereodefined substituted allene shown in Scheme 40", None, None, None),
    ("biradical", "unspecified_agent", "head-to-head bis(allyl) biradical intermediate", None, None, None),
    ("cyclobutane", "product", "cyclobutane allene dimer shown in Scheme 40", None, None, None),
], notes=["Scheme 40 proposes thermal dimerization through a bis-radical intermediate; no isolated yield is printed."], add_missing=False))

R.append(record("p19_scheme41_allene_thermal_oligomerization_general", [19], "general_scheme", [
    ("allene", "reactant", "allene or substituted allene units shown in Scheme 41", None, None, None),
    ("allene_dimer", "product", "methylenecyclobutane dimer class", None, None, None),
    ("higher_oligomers", "product", "fused/spiro cyclic allene oligomer classes", None, None, None),
    ("tetramethylallene", "reactant", "1,1,3,3-tetramethylallene", "CC(C)=C=C(C)C", None, None),
    ("tetramethyl_products", "product", "multiple cyclobutane/cyclopropane dimer classes from tetramethylallene", None, None, None),
    ("biradical", "unspecified_agent", "tetramethylallene-derived 1,4-biradical", None, None, None),
], notes=[
    "Scheme 41 is a literature summary of several allene/allene thermal addition and oligomerization product classes, not one fully specified run.",
    "The lower network shows several closures of a tetramethylallene-derived biradical; no product distribution or conditions are assigned to individual arrows.",
], add_missing=False))

R.append(record("p19_scheme42_selenoallene_dimerization", [19], "literature_example", [
    ("selenoallene", "reactant", "1,3-diphenyl-1,3-bis(methylseleno)allene shown in Scheme 42", None, None, None),
    ("cyclobutane_intermediate", "product", "tetrameric methylseleno/phenyl cyclobutane intermediate shown in Scheme 42", None, None, None),
    ("dimethyl_diselenide", "product", "MeSeSeMe eliminated in the second stage", "C[Se][Se]C", None, None),
    ("dimer_product1", "product", "Scheme 42 cyclobutene dimer product, left", None, None, None),
    ("dimer_product2", "product", "Scheme 42 cyclobutene dimer product, right", None, None, None),
], outcomes=[], notes=["Scheme 42 reports dimerization followed by loss of MeSeSeMe to two depicted final products."],
    unresolved=["Temperature, time, solvent, product yields/distribution, and the isolation status of the bracketed intermediate are not stated."],
    step_specs=[
        ("step1_dimerization", ["selenoallene", "cyclobutane_intermediate"], []),
        ("step2_elimination", ["cyclobutane_intermediate", "dimethyl_diselenide", "dimer_product1", "dimer_product2"], []),
    ]))

# Page 20: enediyne cyclizations and a generic phosphine-oxide/1,4-CHD sequence.
R.append(record("p20_scheme43_enediyne_allene_cyclization_mechanism", [20], "mechanism", [
    ("enediyne_allene", "reactant", "allene-containing enediyne shown in Scheme 43", None, None, None),
    ("biradical1", "unspecified_agent", "aromatic 1,4-biradical intermediate", None, None, None),
    ("biradical2", "unspecified_agent", "cyclized fused-ring biradical intermediate", None, None, None),
    ("hydrogen_donor", "reagent", "H-donor", None, None, None),
    ("product", "product", "dimethyl-substituted fused bicyclic product", None, None, None),
], notes=["Scheme 43 proposes thermal radical cyclization followed by hydrogen donation."], add_missing=False))

R.append(record("p20_scheme44_phosphine_oxide_radical_cyclization_general", [20], "general_scheme", [
    ("enyne_alcohol", "reactant", "R1/R2/R3-substituted enediyne alcohol shown in Scheme 44", None, None, None),
    ("chlorodiphenylphosphine", "reagent", "PPh2Cl", "ClP(c1ccccc1)c1ccccc1", [("equivalents", {"number": 1.5, "unit": "equiv"})], None),
    ("triethylamine", "reagent", "NEt3", "CCN(CC)CC", [("equivalents", {"number": 2.0, "unit": "equiv"})], None),
    ("allenyl_phosphine_oxide", "product", "R1/R2/R3-substituted allenyl phosphine oxide intermediate", None, None, None),
    ("cyclohexadiene", "reagent", "1,4-cyclohexadiene (1,4-CHD)", "C1=CCC=CC1", [("concentration", {"number": 3.5, "unit": "M", "raw_text": "3.5 mol/L"})], None),
    ("benzene", "solvent", "PhH", "c1ccccc1", None, None),
    ("cyclized_product", "product", "R1/R2/R3-substituted fused bicyclic phosphine oxide", None, None, None),
], notes=["Scheme 44 is generic in R1/R2/R3; the first arrow forms an allenyl phosphine oxide and the second performs a 1,4-CHD-mediated cyclization for 12 h."],
    unresolved=["The first-stage time/temperature and the second-stage temperature and yields are not printed; variable R groups prevent a unique structure assignment."],
    add_missing=False,
    step_specs=[
        ("step1_allene_formation", ["enyne_alcohol", "chlorodiphenylphosphine", "triethylamine", "allenyl_phosphine_oxide"], []),
        ("step2_radical_cyclization", ["allenyl_phosphine_oxide", "cyclohexadiene", "benzene", "cyclized_product"], [("time", {"number": 12, "unit": "h"})]),
    ]))

R.append(record("p20_scheme45_enediyne_allene_cascade_mechanism", [20], "mechanism", [
    ("tethered_enediyne_allene", "reactant", "R-substituted tethered enediyne/allene shown in Scheme 45", None, None, None),
    ("benzene", "solvent", "benzene", "c1ccccc1", None, None),
    ("radical_intermediates", "unspecified_agent", "successive aromatic and ring-closure radical intermediates", None, None, None),
    ("polycyclic_product", "product", "fused polycyclic product shown in Scheme 45", None, None, None),
], notes=["Scheme 45 depicts the proposed radical cascade under benzene reflux; it is a mechanism map rather than a discrete fully reported experiment."], add_missing=False))

# Page 21: Scheme 46, a cited synthetic application toward supinidine/heliotridine.
def scheme46_chalcogenation(code, n_value, product_id):
    return record(f"p21_scheme46_chalcogenation_{code}", [20, 21], "literature_example", [
        ("allenic_imide", "reactant", f"allene-tethered cyclic imide in Scheme 46; n = {n_value}", None, None, None),
        ("sodium_borohydride", "reagent", "NaBH4", "[BH4-].[Na+]", None, None),
        ("benzeneselenol", "reagent", "PhSeH", "[SeH]c1ccccc1", None, None),
        ("tosic_acid", "reagent", "TsOH", "Cc1ccc(S(=O)(=O)O)cc1", None, None),
        ("product", "product", f"intermediate {product_id}; n = {n_value}, X = Se", None, None, None),
    ], outcomes=[("reported_yield", {"number": 82, "unit": "%"}, ["product"])],
        notes=["Scheme 46 shows sequential (1) NaBH4 and (2) PhXH/TsOH; the product annotation specifies X = Se."],
        unresolved=["The 90%/99% values printed under the left starting-material family are not assigned to the displayed NaBH4/PhSeH arrow and are therefore not treated as this product yield."],
        step_specs=[
            ("step1_reduction", ["allenic_imide", "sodium_borohydride"], []),
            ("step2_selenation", ["allenic_imide", "benzeneselenol", "tosic_acid", "product"], []),
        ])


R.append(scheme46_chalcogenation("n2_to_57", 2, 57))
R.append(scheme46_chalcogenation("n1_to_58", 1, 58))

R.append(record("p21_scheme46_radical_cyclization_58", [20, 21], "literature_example", [
    ("intermediate58", "reactant", "58, phenylseleno-substituted allene-tethered lactam", None, None, None),
    ("tributyltin_hydride", "reagent", "n-Bu3SnH", "CCCC[SnH](CCCC)CCCC", None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ("product59", "product", "59, methyl-substituted bicyclic lactam", None, None, None),
    ("product60", "product", "60, exomethylene bicyclic lactam", None, None, None),
], outcomes=[
    ("reported_yield", {"number": 52, "unit": "%"}, ["product59"]),
    ("reported_yield", {"number": 14, "unit": "%"}, ["product60"]),
], notes=["The two product-specific yields are printed beneath products 59 and 60."],
    unresolved=["Temperature, time, solvent, reagent amounts, and yield basis are not printed for this arrow."]))


def simple_lit(sid, participants, notes, unresolved=None, conditions=None, outcomes=None):
    R.append(record(sid, [20, 21], "literature_example", participants,
                    conditions=conditions, outcomes=outcomes, notes=[notes],
                    unresolved=unresolved or []))


simple_lit("p21_scheme46_60_to_61", [
    ("product60", "reactant", "60, exomethylene bicyclic lactam", None, None, None),
    ("phseococf3", "reagent", "PhSeOCOCF3", None, None, None),
    ("sodium_bicarbonate", "reagent", "NaHCO3", "O=C([O-])O.[Na+]", None, None),
    ("water", "reagent", "H2O", "O", None, None),
    ("hydrogen_peroxide", "reagent", "H2O2", "OO", None, None),
    ("acetic_anhydride", "reagent", "Ac2O", "CC(=O)OC(C)=O", None, None),
    ("triethylamine", "reagent", "Et3N", "CCN(CC)CC", None, None),
    ("dmap", "reagent", "DMAP", "CN(C)c1ccncc1", None, None),
    ("product61", "product", "61, functionalized bicyclic lactam (X = OH, OAc, or the depicted sulfur-containing derivative)", None, None, None),
], "Scheme 46 arrow a,b,c,d: PhSeOCOCF3; NaHCO3/H2O; H2O2; then Ac2O/Et3N/DMAP.",
    ["The exact X member(s) of compound family 61 generated by this sequence and all stage-specific conditions/yields are not stated."])

simple_lit("p21_scheme46_61_to_64", [
    ("product61", "reactant", "61, functionalized bicyclic lactam", None, None, None),
    ("lithium_aluminum_hydride", "reagent", "LiAlH4", "[Li+].[AlH4-]", None, None),
    ("product64", "product", "64, supinidine/heliotridine-related amino alcohol intermediate", None, None, None),
], "Scheme 46 arrow e: LiAlH4 reduction of 61 to 64.")

simple_lit("p21_scheme46_59_to_61", [
    ("product59", "reactant", "59, methyl-substituted bicyclic lactam", None, None, None),
    ("selenium_dioxide", "reagent", "SeO2", "O=[Se]=O", None, None),
    ("acetic_acid", "solvent", "AcOH", "CC(=O)O", None, None),
    ("product61", "product", "61, functionalized bicyclic lactam", None, None, None),
], "Scheme 46 arrow f: SeO2 in AcOH converts 59 to 61.")

simple_lit("p21_scheme46_59_to_62", [
    ("product59", "reactant", "59, methyl-substituted bicyclic lactam", None, None, None),
    ("osmium_tetroxide", "reagent", "OsO4", "O=[Os](=O)(=O)=O", None, None),
    ("trimethylamine_n_oxide", "reagent", "Me3NO", "C[N+](C)(C)[O-]", None, None),
    ("acetic_anhydride", "reagent", "Ac2O", "CC(=O)OC(C)=O", None, None),
    ("triethylamine", "reagent", "Et3N", "CCN(CC)CC", None, None),
    ("dmap", "reagent", "DMAP", "CN(C)c1ccncc1", None, None),
    ("product62", "product", "62, oxygenated bicyclic lactam (R = H or Ac as printed)", None, None, None),
], "Scheme 46 arrows g,d: OsO4/Me3NO followed by Ac2O/Et3N/DMAP gives 62.",
    ["The scheme prints R = H and R = Ac for 62 without assigning separate yields or conditions."])

simple_lit("p21_scheme46_62_to_63", [
    ("product62", "reactant", "62, oxygenated bicyclic lactam", None, None, None),
    ("sulfur_reagent", "reagent", "Ph2S[OC(CF3)2Ph]2", None, None, None),
    ("sodium_bicarbonate", "reagent", "NaHCO3", "O=C([O-])O.[Na+]", None, None),
    ("water", "reagent", "H2O", "O", None, None),
    ("methyl_chloride", "reagent", "MeCl", "CCl", None, None),
    ("triethylamine", "reagent", "Et3N", "CCN(CC)CC", None, None),
    ("product63", "product", "63, exomethylene bicyclic lactam (R = Ac/H/Me as printed)", None, None, None),
], "Scheme 46 arrows h,b,i: sulfur reagent; NaHCO3/H2O; then MeCl/Et3N gives 63.",
    ["The scheme prints R = Ac, H, and Me for 63 without assigning separate yields or conditions."])

simple_lit("p21_scheme46_63_to_61_acoh", [
    ("product63", "reactant", "63, exomethylene bicyclic lactam", None, None, None),
    ("acetic_acid", "reagent", "AcOH", "CC(=O)O", None, None),
    ("product61", "product", "61, functionalized bicyclic lactam", None, None, None),
], "Scheme 46 alternative arrow j: AcOH and heat convert 63 to 61.", conditions=[("temperature", "Δ")])

simple_lit("p21_scheme46_63_to_61_xanthate", [
    ("product63", "reactant", "63, exomethylene bicyclic lactam", None, None, None),
    ("sodium_hydride", "reagent", "NaH", "[H-].[Na+]", None, None),
    ("carbon_disulfide", "reagent", "CS2", "S=C=S", None, None),
    ("methyl_iodide", "reagent", "CH3I", "CI", None, None),
    ("product61", "product", "61, depicted sulfur-containing derivative of the bicyclic lactam", None, None, None),
], "Scheme 46 alternative arrow k: NaH, CS2, and CH3I convert 63 to the xanthate member of 61.")

# Page 21: Scheme 47, a cited route to (±)-alpha-chamigrene.
R.append(record("p21_scheme47_65_to_66", [20, 21], "literature_example", [
    ("compound65", "reactant", "65, nitro-substituted methylcyclohexene", None, None, None),
    ("methyl_butenal", "reactant", "Me2C=CHCHO", "CC(C)=CC=O", None, None),
    ("dbu", "reagent", "DBU", None, None, None),
    ("compound66", "product", "66, nitro aldehyde", None, None, None),
], outcomes=[("reported_yield", {"number": 25, "unit": "%"}, ["compound66"])],
    notes=["Scheme 47 first arrow; the printed 25% is associated with product 66."],
    unresolved=["Time, temperature, solvent, reagent amounts, and yield basis are not stated."]))

R.append(record("p21_scheme47_66_to_67", [20, 21], "literature_example", [
    ("compound66", "reactant", "66, nitro aldehyde", None, None, None),
    ("propargyl_bromide", "reagent", "propargyl bromide", "C#CCBr", None, None),
    ("aluminum", "reagent", "Al", "[Al]", None, None),
    ("mercuric_chloride", "reagent", "HgCl2", None, None, None),
    ("compound67", "product", "67, propargylic alcohol", None, None, None),
], outcomes=[("reported_yield", {"number": 85, "unit": "%"}, ["compound67"])],
    notes=["Scheme 47 second arrow; product 67 is drawn with unspecified alcohol stereochemistry."],
    unresolved=["Time, temperature, solvent, reagent amounts, diastereomeric composition, and yield basis are not stated."]))

R.append(record("p21_scheme47_67_to_68", [20, 21], "literature_example", [
    ("compound67", "reactant", "67, propargylic alcohol", None, None, None),
    ("chromium_trioxide", "reagent", "CrO3", "O=[Cr](=O)=O", None, None),
    ("compound68", "product", "68, allenyl ketone", None, None, None),
], outcomes=[("reported_yield", {"number": 81, "unit": "%"}, ["compound68"])],
    notes=["Scheme 47 third arrow oxidizes 67 to allenyl ketone 68."],
    unresolved=["Time, temperature, solvent, reagent amount, workup, and yield basis are not stated."]))

R.append(record("p21_scheme47_radical_cyclization_68", [20, 21, 22], "literature_example", [
    ("compound68", "reactant", "68, nitro-substituted allenyl ketone", None, None, None),
    ("tributyltin_hydride", "reagent", "Bu3SnH", "CCCC[SnH](CCCC)CCCC", None, None),
    ("aibn", "unspecified_agent", "AIBN", "N#CC(C)(C)N=NC(C)(C)C#N", None, None),
    ("benzene", "solvent", "PhH", "c1ccccc1", None, None),
    ("compound69", "product", "69, spirocyclic enone", None, None, None),
    ("compound70", "product", "70, nitro cyclization product with E-alkenyl ketone side chain", None, None, None),
    ("compound71", "product", "71, nitro cyclization product with allylic ketone side chain", None, None, None),
], outcomes=[], notes=["Scheme 47 gives three products 69-71; Scheme 48 on page 22 provides the proposed radical pathways for the same arrow."],
    unresolved=["No overall yield, product distribution, time, temperature, or reagent amounts are printed for the radical cyclization."]))

R.append(record("p21_scheme47_69_to_72", [20, 21], "literature_example", [
    ("compound69", "reactant", "69, spirocyclic enone", None, None, None),
    ("ethanedithiol", "reagent", "HSCH2CH2SH", "SCCS", None, None),
    ("tosic_acid", "reagent", "TsOH", "Cc1ccc(S(=O)(=O)O)cc1", None, None),
    ("acetic_acid", "solvent", "AcOH", "CC(=O)O", None, None),
    ("compound72", "product", "72, cyclic thioketal", None, None, None),
], outcomes=[("reported_yield", {"number": 65, "unit": "%"}, ["compound72"])],
    notes=["Scheme 47 converts 69 to thioketal 72 in 65% yield."],
    unresolved=["Time, temperature, reagent amounts, and yield basis are not stated."]))

R.append(record("p21_scheme47_72_to_alpha_chamigrene", [20, 21], "literature_example", [
    ("compound72", "reactant", "72, cyclic thioketal", None, None, None),
    ("alpha_chamigrene", "product", "(±)-alpha-chamigrene", None, None, None),
], outcomes=[], notes=["Scheme 47 shows a final unlabeled arrow from 72 to (±)-alpha-chamigrene."],
    unresolved=["The final transformation's reagents, conditions, number of operations, yield, and yield basis are not printed."]))

# Page 22: Scheme 48 is the proposed mechanism for the Scheme 47 radical cyclization.
R.append(record("p22_scheme48_chamigrene_intermediates_mechanism", [21, 22], "mechanism", [
    ("compound68", "reactant", "68, nitro-substituted allenyl ketone", None, None, None),
    ("tributyltin_radical", "unspecified_agent", "Bu3Sn radical", None, None, None),
    ("radical_intermediates", "unspecified_agent", "three radical-addition/cyclization pathways shown in Scheme 48", None, None, None),
    ("compound69", "product", "69, spirocyclic enone", None, None, None),
    ("compound70", "product", "70, nitro cyclization product", None, None, None),
    ("compound71", "product", "71, nitro cyclization product", None, None, None),
], notes=["Scheme 48 proposes three radical pathways leading to the products 69-71 shown in Scheme 47; transient tin-containing intermediates are not treated as isolated products."], add_missing=False))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")


def ids(prefixes):
    return [item["record_id"] for item in R if any(item["source_reaction_id"].startswith(prefix) for prefix in prefixes)]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 19,
            "state": "attempted",
            "regions": [
                {"region": "页上部 Scheme 40", "finding": "取代联烯热二聚的双自由基路径，分类为 mechanism；未给收率或完整条件。", "evidence_ids": evid(19)},
                {"region": "页中部 Scheme 41", "finding": "联烯/联烯及四甲基联烯热加成、二聚和高聚的通式/产物网络，作为一个 general_scheme 保存，不把可能的闭环箭头冒充独立实验。", "evidence_ids": evid(19)},
                {"region": "页下部 Scheme 42", "finding": "1,3-二芳基硒取代联烯的引用二聚实例；二聚与脱 MeSeSeMe 两阶段合并为同一跨步记录。", "evidence_ids": evid(19)},
            ],
            "record_ids": ids(["p19_"]),
            "unresolved": ["Schemes 40-42 均缺原始实验操作；Scheme 41 没有逐箭头条件、收率或产物比例；Scheme 42 的中间体是否分离未说明。"],
        },
        {
            "page": 20,
            "state": "attempted",
            "regions": [
                {"region": "页上部 Scheme 43", "finding": "联烯-烯炔热自由基成环及供氢终止路径，分类为 mechanism。", "evidence_ids": evid(20)},
                {"region": "页中部 Scheme 44", "finding": "R1/R2/R3 可变的两步通式；结构化 PPh2Cl 1.5 equiv、NEt3 2.0 equiv、1,4-CHD 3.5 mol/L、PhH 和 12 h。", "evidence_ids": evid(20)},
                {"region": "页下部 Scheme 45", "finding": "苯回流下的联烯-烯炔自由基串联成环机理，分类为 mechanism。", "evidence_ids": evid(20)},
                {"region": "第3节合成应用正文", "finding": "正文引出第21页 Scheme 46 和 47 的引用合成路线；与对应跨页记录合并证据，没有另建正文记录。", "evidence_ids": evid(20) + evid(21)},
            ],
            "record_ids": ids(["p20_", "p21_scheme46_", "p21_scheme47_"]),
            "unresolved": ["Scheme 44 第一阶段缺时间/温度、第二阶段缺温度，且两阶段均无收率；Schemes 43/45 仅为机理图。"],
        },
        {
            "page": 21,
            "state": "attempted",
            "regions": [
                {"region": "上半页 Scheme 46：57/58 与 58→59/60", "finding": "按 n=2、n=1 两行拆分 57/58 的 82%制备；58 的 Bu3SnH/AIBN 自由基环化保留 59（52%）与60（14%）的产物专属收率。", "evidence_ids": evid(21) + evid(20)},
                {"region": "中部 Scheme 46：59-64 转化网络", "finding": "逐箭头建立七条引用步骤；a-k 脚注中的所有明确试剂进入 participants，j/k 两种替代条件分开记录。", "evidence_ids": evid(21) + evid(20)},
                {"region": "下半页 Scheme 47：65→68", "finding": "按三条箭头分别记录 65→66（25%）、66→67（85%）和67→68（81%）。", "evidence_ids": evid(21) + evid(20)},
                {"region": "下半页 Scheme 47：68→69/70/71→72→目标物", "finding": "68 的自由基环化作为一条三产物记录；69→72（65%）及未标条件的72→(±)-α-Chamigrene 分别记录。", "evidence_ids": evid(21) + evid(20)},
            ],
            "record_ids": ids(["p21_"]) + ids(["p22_scheme48_"]),
            "unresolved": ["左上起始底物下的90%/99%没有对应制备箭头，未错误归入57/58收率；Scheme 46多数步骤缺收率/条件；68→69-71缺总收率和分布；最终72→目标物无试剂、条件或收率。"],
        },
        {
            "page": 22,
            "state": "attempted",
            "regions": [
                {"region": "页首 Scheme 48", "finding": "解释 Scheme 47 中 68 生成69-71的三条自由基路径，分类为 mechanism，并与第21页同一实验记录交叉关联。", "evidence_ids": evid(22) + evid(21)},
                {"region": "Scheme 48以下参考文献1-31", "finding": "仅为参考文献条目，不含本页独立实验箭头、表格或操作；未建立反应记录。", "evidence_ids": evid(22)},
            ],
            "record_ids": ids(["p22_"]) + [f"{DOC}:p21_scheme47_radical_cyclization_68"],
            "unresolved": ["Scheme 48 的瞬态自由基和含锡中间体未被报道为分离物；参考文献本身不提供可抽取的实验条件。"],
        },
        {
            "page": 23,
            "state": "attempted",
            "regions": [
                {"region": "整页参考文献32-56及稿件编号", "finding": "逐页查看确认仅含参考文献续表与稿件编号，无反应图、表、箭头、脚注实验或正文实验步骤。", "evidence_ids": evid(23)},
            ],
            "record_ids": [],
            "unresolved": ["参考文献条目未展开到原始论文全文，因而不据此推断实验条件或SI关联。"],
        },
    ],
}

COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = ROOT / "runs/current/tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    prefix = f"{DOC}:page"
    task_id = task.get("task_id", "")
    if not task_id.startswith(prefix) or not task_id.endswith(":text"):
        continue
    page = int(task_id[len(prefix):].split(":", 1)[0])
    if 19 <= page <= 23:
        task["state"] = "attempted"
        task["visual_evidence_id"] = f"{DOC}:page{page}:image"
        task["reason"] = "Original page image inspected; findings and unresolved issues are recorded in coverage/pages_0019_0023.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(R), "raw": str(OUT), "coverage": str(COVERAGE)}, ensure_ascii=False))
