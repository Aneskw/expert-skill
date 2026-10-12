#!/usr/bin/env python3
"""Build source-linked review-reaction records and coverage for PDF pages 13--18."""
import json
import re
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
OUT = Path(__file__).with_name("records_pages_0013_0018.json")
records = []


def ev(pages):
    out = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return out


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def slug(value):
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()[:32] or "entity"


def P(role, label, name=None, smiles=None, amounts=None):
    return role, label, name, smiles, amounts or []


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


def participant(index, spec, evidence):
    role, label, name, smiles, amounts = spec
    return {
        "entity_id": f"p{index}_{slug(label)}",
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [
            {"name": name, "fact": fact(value, evidence)} for name, value in amounts
        ],
    }


def add(rid, source_id, pages, parts, conditions=None, outcomes=None, notes=None,
        unresolved=None, kind="literature_example"):
    evidence = ev(pages)
    ps = [participant(i, spec, evidence) for i, spec in enumerate(parts, 1)]
    label_ids = {p["label"]["value"]: p["entity_id"] for p in ps}
    conds = list(conditions or [])
    if kind == "literature_example":
        if not any(name == "temperature" for name, _ in conds):
            conds.append(("temperature", None))
        if not any(name == "time" for name, _ in conds):
            conds.append(("time", None))
    outcome_fields = []
    supplied_yield = False
    for name, value, targets in outcomes or []:
        field = {"name": name, "fact": fact(value, evidence)}
        if targets:
            if isinstance(targets, str):
                targets = [targets]
            field["target_entity_ids"] = [label_ids[target] for target in targets]
        outcome_fields.append(field)
        supplied_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(
            field["name"] == "yield" for field in outcome_fields):
        products = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if products:
            missing["target_entity_ids"] = products
        outcome_fields.append(missing)
    if supplied_yield:
        outcome_fields.append({
            "name": "yield_measurement_basis", "fact": fact(None, evidence)
        })
    step_ids = [p["entity_id"] for p in ps if p["role"] != "product"]
    record = {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": ps,
        "steps": [{
            "step_id": "step1",
            "participant_ids": step_ids,
            "conditions": [
                {"name": name, "fact": fact(value, evidence)} for name, value in conds
            ],
        }] if conds else [],
        "outcomes": outcome_fields,
        "notes": [fact(note, evidence) for note in notes or []],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "Secondary-review example: the cited primary article and its SI were not supplied.",
                "Complex or generic drawings remain label-only unless a full unambiguous structure was available; all structures are unverified.",
            ],
        },
    }
    records.append(record)
    return record


def mechanism(rid, source_id, pages, sequence, conditions=None, notes=None):
    parts = []
    for i, label in enumerate(sequence):
        role = "reactant" if i == 0 else ("product" if i == len(sequence) - 1 else "unspecified_agent")
        parts.append(P(role, label))
    return add(
        rid, source_id, pages, parts, conditions=conditions, notes=notes,
        unresolved=["The arrows are a proposed pathway, not independently reported experimental operations."],
        kind="mechanism",
    )


def set_steps(record, step_specs):
    evidence = record["evidence_ids"]
    ids = {p["label"]["value"]: p["entity_id"] for p in record["participants"]}
    record["steps"] = []
    for index, (labels, conditions) in enumerate(step_specs, 1):
        record["steps"].append({
            "step_id": f"step{index}",
            "participant_ids": [ids[label] for label in labels],
            "conditions": [
                {"name": name, "fact": fact(value, evidence)} for name, value in conditions
            ],
        })


# Page 13. Scheme 61 completes two records introduced textually on page 12.
for suffix, r_group, yld, ratio, rid in [
    ("h", "R=H", 54, None, "p0012_s61_text_only"),
    ("me", "R=Me", 28, "cis/trans = 1:3", "p0013_s61_r_me"),
]:
    product = f"271 ({r_group})"
    outcomes = [("yield", q(yld, "%"), product)]
    if ratio:
        outcomes.append(("cis_trans_ratio", ratio, product))
    add(rid, f"Scheme 61 {r_group}", [12, 13], [
        P("reactant", f"ethyl 2,3-alkadienoate ({r_group})"),
        P("reactant", "PhCSNH2", "thiobenzamide", "NC(=S)c1ccccc1"),
        P("catalyst", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1",
          [("catalyst_loading", q(10, "mol%"))]),
        P("product", product, "thiazoline 271"),
    ], outcomes=outcomes)

add("p0012_s62_text_only", "Scheme 62 overall", [12, 13], [
    P("reactant", "272 (R1/R2 variable)", "4-acetoxy-2-alkynoate"),
    P("reagent", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c1ccccc1)c1ccccc1"),
    P("product", "276", "dihydrofuran product"),
], outcomes=[("yield", qr(60, 86, "%", "60–86%"), "276")],
    notes=["The depicted 2-acyl-2,3-alkadienoate 273 is formed in situ before cyclization."])
mechanism("p0013_s62_mechanism", "Scheme 62 proposed phosphine sequence", [13],
          ["272 + PPh3", "273", "274", "275", "276"],
          notes=["The drawing includes phosphine addition, cyclic intermediates, and phosphine release."])

for suffix, x_group, mode, product, yld in [
    ("x_o", "X=O", "[3+2], decarbonylation", "278", qr(72, 74, "%", "72–74%")),
    ("x_nar", "X=N-Ar", "[4+3]", "279", qr(55, 64, "%", "55–64%")),
]:
    add(f"p0013_s63_277_{suffix}", f"Scheme 63 substrate 277 {x_group}", [13], [
        P("reactant", f"277 ({x_group})", "coumarin-derived acceptor"),
        P("reactant", "247b", "phosphonium allenoate intermediate"),
        P("product", product, "polycyclic cycloaddition product"),
    ], conditions=[("operation", mode)], outcomes=[("yield", yld, product)])
add("p0013_s63_280", "Scheme 63 substrate 280", [13], [
    P("reactant", "280", "tropone"),
    P("reactant", "247c (R1/R2 variable)", "phosphonium allene intermediate"),
    P("solvent", "dry benzene", "benzene", "c1ccccc1"),
    P("product", "281", "[8+2] cycloadduct"),
    P("product", "282 (minor; R1=OEt)", "minor bicyclic product"),
], conditions=[("temperature", "r.t."), ("operation", "[8+2] cycloaddition")], outcomes=[
    ("yield", qr(70, 95, "%", "70–95%"), "281"),
    ("yield", None, "282 (minor; R1=OEt)"),
])

add("p0013_s64_283", "Scheme 64 substrate 283", [13], [
    P("reactant", "283", "aldehyde-tethered allenoate"),
    P("reagent", "SmI2", "samarium(II) iodide", None, [("amount", q(2, "equiv"))]),
    P("reagent", "t-BuOH", "tert-butanol", "CC(C)(C)O", [("amount", q(2, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "284", "cyclized regioisomer"),
    P("product", "285", "cyclized regioisomer"),
], outcomes=[
    ("yield", q(66, "%"), ["284", "285"]),
    ("product_ratio_284_to_285", "2:1", ["284", "285"]),
])
add("p0013_s64_286_smi2", "Scheme 64 substrate 286, SmI2", [13], [
    P("reactant", "286 (n=1)", "aldehyde-tethered allenoate"),
    P("reagent", "SmI2", "samarium(II) iodide", None, [("amount", q(2, "equiv"))]),
    P("reagent", "t-BuOH", "tert-butanol", "CC(C)(C)O", [("amount", q(2, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "287", "cyclized diastereomer"),
    P("product", "288", "cyclized diastereomer"),
], outcomes=[
    ("yield", q(82, "%"), ["287", "288"]),
    ("diastereomer_ratio_287_to_288", "15:1", ["287", "288"]),
])
add("p0013_s64_286_tin", "Scheme 64 substrate 286, Bu3SnH/AIBN", [13], [
    P("reactant", "286 (n=1)", "aldehyde-tethered allenoate"),
    P("reagent", "Bu3SnH", "tributyltin hydride"),
    P("reagent", "AIBN", "2,2'-azobis(isobutyronitrile)", "N#CC(C)(C)N=NC(C)(C)C#N"),
    P("solvent", "benzene", "benzene", "c1ccccc1"),
    P("product", "287", "cyclized diastereomer"),
    P("product", "288", "cyclized diastereomer"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", q(37, "%"), ["287", "288"]),
    ("diastereomer_ratio_287_to_288", "5:1", ["287", "288"]),
])
add("p0013_s64_reduction", "Scheme 64 conjugate-reduction branch", [13], [
    P("reactant", "higher-homologue aldehyde-tethered allenoate 286"),
    P("reagent", "SmI2", "samarium(II) iodide", None, [("amount", q(2, "equiv"))]),
    P("solvent", "MeOH", "methanol", "CO"),
    P("product", "conjugate-reduction product (drawn)"),
], notes=["The review states that seven-membered-ring formation was less successful and conjugate reduction was the major pathway."],
    unresolved=["The n value and yield for the vertically drawn reduction branch are not printed unambiguously."])

add("p0013_s65", "Scheme 65 overall", [13], [
    P("reactant", "289", "1-siloxyalkyl iodide"),
    P("reactant", "propadienyl methyl ether", None, "COC=C=C"),
    P("reagent", "Sm", "samarium"),
    P("reagent", "HgCl2", "mercury(II) chloride", None,
      [("amount_relative_to_sm", q(0.2, "equiv"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "290", "trans-3-methoxymethylenetetrahydrofuran"),
], outcomes=[
    ("yield", q(78, "%"), "290"),
    ("diastereomer_ratio", "82:18", "290"),
])
mechanism("p0013_s65_mechanism", "Scheme 65 proposed carbonyl-ylide pathway", [13],
          ["289 + Sm/HgCl2", "291", "292", "293", "294", "290"],
          notes=["Intermediate 294 is the proposed nonstabilized carbonyl ylide formed by 1,3-elimination."])


# Page 14. Scheme 66 crosses from the page-13 discussion.
mechanism("p0014_s66_mechanism", "Scheme 66 proposed ketyl-radical pathways", [13, 14],
          ["ketone + propadienyl methyl ether + SmI2", "295", "296", "297 / 298", "299", "300"],
          notes=["Path A is H abstraction to 297; Path B includes a 1,5-H shift and radical cyclization to 300."])
add("p0014_s66_3_pentanone", "Scheme 66 3-pentanone example", [13, 14], [
    P("reactant", "3-pentanone", "3-pentanone", "CCC(=O)CC"),
    P("reactant", "propadienyl methyl ether", None, "COC=C=C"),
    P("reagent", "SmI2", "samarium(II) iodide"),
    P("reagent", "t-BuOH", "tert-butanol", "CC(C)(C)O"),
    P("product", "300A", "cyclic alcohol"),
    P("product", "297A", "homoallylic alcohol"),
], outcomes=[
    ("yield", q(8, "%"), "300A"),
    ("yield", q(44, "%"), "297A"),
    ("reported_selectivity_for_297A", "55:45", "297A"),
], unresolved=["The parenthesized 55:45 value is preserved without assigning an unstated stereochemical basis."])
add("p0014_s66_diphenylallene", "Scheme 66 cyclopentanone/1,3-diphenylallene", [13, 14], [
    P("reactant", "cyclopentanone", "cyclopentanone", "O=C1CCCC1"),
    P("reactant", "1,3-diphenylallene"),
    P("reagent", "SmI2", "samarium(II) iodide"),
    P("reagent", "HMPA", "hexamethylphosphoramide"),
    P("reagent", "t-BuOH", "tert-butanol", "CC(C)(C)O"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "301", "E-allylic alcohol"),
], conditions=[("temperature", "r.t."), ("time", q(16, "h"))],
    outcomes=[("yield", q(69, "%"), "301")])

for suffix, x, y, yld in [("tsbr", "Br", "Br", 75), ("tsi", "I", "Ts", 60)]:
    product = f"E-303 (X={x}, Y={y})"
    add(f"p0014_s67_302_{suffix}", f"Scheme 67 substrate 302, Ts{x}", [13, 14], [
        P("reactant", "302", "allenic alcohol"),
        P("reagent", f"Ts{x}", f"p-toluenesulfonyl {x}", None, [("amount", q(1.2, "equiv"))]),
        P("reagent", "AIBN", "2,2'-azobis(isobutyronitrile)", "N#CC(C)(C)N=NC(C)(C)C#N",
          [("initiator_loading", q(20, "mol%"))]),
        P("solvent", "toluene", "toluene", "Cc1ccccc1"),
        P("product", product, "radical addition product"),
    ], conditions=[("temperature", q(90, "°C")), ("time", q(3, "h"))],
        outcomes=[("yield", q(yld, "%"), product)])
add("p0014_s67_304", "Scheme 67 substrate 304", [13, 14], [
    P("reactant", "304", "allenic alcohol"),
    P("reagent", "TsBr", "p-toluenesulfonyl bromide", None, [("amount", q(1.2, "equiv"))]),
    P("reagent", "AIBN", "2,2'-azobis(isobutyronitrile)", "N#CC(C)(C)N=NC(C)(C)C#N",
      [("initiator_loading", q(20, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "305", "E-radical addition product"),
], conditions=[("temperature", q(90, "°C")), ("time", q(3, "h"))],
    outcomes=[("yield", q(67, "%"), "305")], notes=["The arrow is marked ibid relative to the preceding conditions."])
for suffix, x, yld in [("br", "Br", 72), ("i", "I", 70)]:
    product = f"307 (X={x})"
    add(f"p0014_s67_306_{suffix}", f"Scheme 67 substrate 306, Ts{x}", [13, 14], [
        P("reactant", "306", "4,5-hexadienol"),
        P("reagent", f"Ts{x}", f"p-toluenesulfonyl {x}", None, [("amount", q(1.2, "equiv"))]),
        P("product", product, "five-membered cyclization product"),
    ], outcomes=[("yield", q(yld, "%"), product)])
add("p0014_s67_308_tsi", "Scheme 67 substrate 308 with TsI", [13, 14], [
    P("reactant", "308", "5,6-heptadienol"),
    P("reagent", "TsI", "p-toluenesulfonyl iodide"),
    P("product", "309", "six-membered cyclization product"),
], outcomes=[("yield", q(53, "%"), "309")])
add("p0014_s67_308_tsbr", "Scheme 67 substrate 308 with TsBr", [13, 14], [
    P("reactant", "308", "5,6-heptadienol"),
    P("reagent", "TsBr", "p-toluenesulfonyl bromide"),
    P("product", "310", "eight-membered cyclic ether"),
    P("product", "311", "addition product"),
], outcomes=[
    ("yield", q(52, "%"), "310"),
    ("yield", q(33, "%"), "311"),
])

add("p0014_s68_addition", "Scheme 68 formation of E-313", [14], [
    P("reactant", "312 (n variable)", "N-allenyl sulfonamide"),
    P("reagent", "TsBr", "p-toluenesulfonyl bromide"),
    P("product", "E-313", "1:1 radical addition product"),
], notes=["The prose describes E-313 as highly stereoselective but gives no numeric yield or E/Z ratio."])
for suffix, n_value, product, yld in [
    ("n3", 3, "314 (m=0)", 76),
    ("n4", 4, "314 (m=1)", 78),
    ("n2", 2, "315", 63),
]:
    add(f"p0014_s68_cyclization_{suffix}", f"Scheme 68 cyclization n={n_value}", [14], [
        P("reactant", f"E-313 (n={n_value})", "radical addition product"),
        P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(1.2, "equiv"))]),
        P("product", product, "cyclic sulfonamide"),
    ], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(yld, "%"), product)])
add("p0014_s68_n1_no_cyclization", "Scheme 68 n=1 no-cyclization result", [14], [
    P("reactant", "E-313 (n=1)", "radical addition product"),
    P("reagent", "K2CO3", "potassium carbonate", None, [("amount", q(1.2, "equiv"))]),
], conditions=[("temperature", "r.t.")], outcomes=[("reaction_result", "no cyclization", None), ("yield", None, None)])
add("p0014_s68_tetraene_scope", "Scheme 68 tetraene scope", [14], [
    P("reactant", "1,2,7,8-tetraene (X=N-Ts, N-Ph, O, or CPh2)"),
    P("reagent", "TsX (Y=Br or SePh)"),
    P("reagent", "AIBN", "2,2'-azobis(isobutyronitrile)", "N#CC(C)(C)N=NC(C)(C)C#N"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "trans-1,2-vinylic five-membered product"),
], conditions=[("temperature", q(90, "°C"))],
    outcomes=[("yield", qr(48, 73, "%", "48–73%"), "trans-1,2-vinylic five-membered product")])

add("p0014_s69", "Scheme 69 overall", [14], [
    P("reactant", "316", "allene-containing xanthate"),
    P("reagent", "Bu3SnH", "tributyltin hydride"),
    P("reagent", "AIBN", "2,2'-azobis(isobutyronitrile)", "N#CC(C)(C)N=NC(C)(C)C#N"),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("product", "319", "polycyclic radical-cyclization product"),
], conditions=[("temperature", q(100, "°C"))], outcomes=[("yield", q(81, "%"), "319")])
mechanism("p0014_s69_mechanism", "Scheme 69 radical cascade", [14], ["316", "317", "318", "319"],
          conditions=[("temperature", q(100, "°C"))])
add("p0014_s70_epoxidation", "Scheme 70 epoxidation", [14], [
    P("reactant", "320", "1,3-di-tert-butylallene"),
    P("reagent", "ArCO3H", "peroxybenzoic acid"),
    P("product", "321", "allene monoxide"),
], conditions=[("temperature", q(25, "°C"))])
add("p0014_s70_rearrangement", "Scheme 70 thermal rearrangement", [14], [
    P("reactant", "321", "allene monoxide"),
    P("product", "322", "trans-2,3-di-tert-butylcyclopropanone"),
], conditions=[("temperature", q(100, "°C"))])


# Page 15. Scheme 71 has an internally ambiguous printed temperature line.
scheme71_unresolved = [
    "The arrow prints both '80 °C' and 'rt, 5 h'; the review does not make their stage relationship unambiguous, so temperature is retained as missing."
]
common71 = [
    P("reagent", "H2O2", "hydrogen peroxide", "OO"),
    P("catalyst", "PCWP", "cetylpyridinium peroxotungstophosphate", None,
      [("catalyst_loading", q(2, "mol%"))]),
    P("solvent", "EtOH/CH2Cl2 (6/4)", "ethanol/dichloromethane"),
]
for suffix, substrate, product, yld in [
    ("nc6h13", "monosubstituted allene (R=n-C6H13)", "alpha-ethoxy ketone (R=n-C6H13)", 66),
    ("cyclohexyl", "monosubstituted allene (R=cyclohexyl)", "alpha-ethoxy ketone (R=cyclohexyl)", 48),
]:
    add(f"p0015_s71_mono_{suffix}", f"Scheme 71 {suffix}", [14, 15],
        [P("reactant", substrate)] + common71 + [P("product", product)],
        conditions=[("temperature", None), ("time", q(5, "h"))],
        outcomes=[("yield", q(yld, "%"), product)],
        notes=["The source displays '80 °C' and 'rt, 5 h' together; the temperature-stage assignment is unresolved."],
        unresolved=scheme71_unresolved)
for suffix, r_group, y1, y2 in [("nc5h11", "R=n-C5H11", 20, 27), ("ph", "R=Ph", 8, 22)]:
    p1 = f"alpha-ethoxy ketone regioisomer A ({r_group})"
    p2 = f"alpha-ethoxy ketone regioisomer B ({r_group})"
    add(f"p0015_s71_disub_{suffix}", f"Scheme 71 1,3-disubstituted allene {r_group}", [14, 15],
        [P("reactant", f"1,3-disubstituted allene ({r_group})")] + common71 + [P("product", p1), P("product", p2)],
        conditions=[("temperature", None), ("time", q(5, "h"))],
        outcomes=[("yield", q(y1, "%"), p1), ("yield", q(y2, "%"), p2)],
        notes=["The arrow is marked ibid relative to the first Scheme 71 row.",
               "The source displays '80 °C' and 'rt, 5 h' together; the temperature-stage assignment is unresolved."],
        unresolved=scheme71_unresolved)
add("p0015_s71_unsym_terminal", "Scheme 71 unsymmetrical terminal allene", [14, 15],
    [P("reactant", "unsymmetrical terminal allene (drawn)")] + common71 + [
        P("product", "alpha-ethoxy ketone"), P("product", "carboxylic acid")],
    conditions=[("temperature", None), ("time", q(5, "h"))],
    outcomes=[("yield", q(20, "%"), "alpha-ethoxy ketone"), ("yield", q(17, "%"), "carboxylic acid")],
    notes=["The arrow is marked ibid.",
           "The source displays '80 °C' and 'rt, 5 h' together; the temperature-stage assignment is unresolved."],
    unresolved=scheme71_unresolved)
add("p0015_s71_internal", "Scheme 71 1,3-disubstituted internal allene", [14, 15],
    [P("reactant", "1,3-disubstituted internal allene (drawn)")] + common71 + [
        P("product", "alpha-ethoxy ketone (50%)"),
        P("product", "n-C5H11-substituted carboxylic acid"),
        P("product", "n-C6H13-substituted carboxylic acid")],
    conditions=[("temperature", None), ("time", q(5, "h"))],
    outcomes=[
        ("yield", q(50, "%"), "alpha-ethoxy ketone (50%)"),
        ("yield", q(18, "%"), "n-C5H11-substituted carboxylic acid"),
        ("yield", q(21, "%"), "n-C6H13-substituted carboxylic acid"),
    ], notes=["The arrow is marked ibid.",
              "The source displays '80 °C' and 'rt, 5 h' together; the temperature-stage assignment is unresolved."],
       unresolved=scheme71_unresolved)

add("p0015_s72_323", "Scheme 72 allene 323 scope", [15], [
    P("reactant", "323 (R=n-C4H9 or t-Bu)", "substituted allene"),
    P("reagent", "dimethyldioxirane", "dimethyldioxirane", "CC1(C)OO1"),
    P("product", "anti-325A", "anti bisepoxide"),
    P("product", "syn-325B", "syn bisepoxide"),
], outcomes=[("diastereomer_ratio_anti_to_syn", "9:1", ["anti-325A", "syn-325B"])],
    notes=["Monoepoxides 324A/324B are drawn as intermediates; no row-resolved yield is printed."])
add("p0015_s72_326", "Scheme 72 monosubstituted allene", [15], [
    P("reactant", "monosubstituted allene (R variable)"),
    P("reagent", "dimethyldioxirane", "dimethyldioxirane", "CC1(C)OO1"),
    P("product", "anti-327A", "anti bisepoxide"),
    P("product", "syn-327B", "syn bisepoxide"),
], outcomes=[
    ("yield", q(78, "%"), "anti-327A"),
    ("yield", q(22, "%"), "syn-327B"),
], notes=["Monoepoxide 326 is shown as an intermediate."])
for suffix, substrate, product, yld in [
    ("328", "2,4-dimethyl-2,3-pentadiene", "328", 44),
    ("329", "3-(n-butyl)-1,2-heptadiene", "329", 83),
]:
    add(f"p0015_s72_{suffix}", f"Scheme 72 product {product}", [15], [
        P("reactant", substrate),
        P("reagent", "dimethyldioxirane", "dimethyldioxirane", "CC1(C)OO1"),
        P("product", product, "bisepoxide"),
    ], outcomes=[("yield", q(yld, "%"), product)])

for suffix, r_group, yld in [("me", "R=Me", 90), ("et", "R=Et", 88), ("ibu", "R=i-Bu", 88)]:
    product = f"332 ({r_group})"
    add(f"p0015_s73_330_{suffix}", f"Scheme 73 substrate 330 {r_group}", [15], [
        P("reactant", f"330 ({r_group})", "2,3-allenyl acetate"),
        P("reagent", "m-CPBA", "meta-chloroperoxybenzoic acid"),
        P("product", product, "alpha,beta-unsaturated ketone"),
    ], outcomes=[("yield", q(yld, "%"), product)], notes=["Intermediate 331 is drawn."])
for substrate, product, yld in [("333", "334", 92), ("335", "336", 81)]:
    add(f"p0015_s73_{substrate}", f"Scheme 73 substrate {substrate}", [15], [
        P("reactant", substrate, "2,3-allenyl acetate"),
        P("reagent", "m-CPBA", "meta-chloroperoxybenzoic acid"),
        P("product", product, "alpha,beta-unsaturated ketone"),
    ], outcomes=[("yield", q(yld, "%"), product)])
add("p0015_s73_337_first", "Scheme 73 substrate 337 first oxidation", [15], [
    P("reactant", "337", "2,3-allenyl acetate"),
    P("reagent", "TBHP", "tert-butyl hydroperoxide", "CC(C)(C)OO"),
    P("catalyst", "VO(acac)2", "vanadyl acetylacetonate"),
    P("product", "338", "monoepoxidation product"),
], outcomes=[("yield", q(90, "%"), "338")])
add("p0015_s73_338_second", "Scheme 73 second oxidation/rearrangement", [15], [
    P("reactant", "338/339", "monoepoxide/rearranged intermediate"),
    P("reagent", "m-CPBA", "meta-chloroperoxybenzoic acid"),
    P("product", "342", "alpha,beta-unsaturated ketone"),
], notes=["Intermediates 340 and 341 are drawn; the final-step yield is not printed."])
mechanism("p0015_s73_mechanism", "Scheme 73 pathway from 337", [15],
          ["337", "338", "339", "340", "341", "342"])

add("p0015_s74_overall", "Scheme 74 photooxygenation", [15], [
    P("reactant", "cyclic allene 342 (n=2 or 6)"),
    P("reagent", "O2", "oxygen", "O=O"),
    P("catalyst", "tetraphenylporphyrin"),
    P("solvent", "CCl4", "carbon tetrachloride", "ClC(Cl)(Cl)Cl"),
    P("product", "348", "trione"),
    P("product", "349", "hydrated trione"),
], conditions=[("operation", "hν photooxygenation")], notes=["Product 349 is drawn as the hydration product of 348."])
mechanism("p0015_s74_mechanism", "Scheme 74 proposed photooxygenation pathway", [15],
          ["342 + singlet O2", "343", "344", "345", "346", "347", "348 / 349"],
          notes=["The review proposes O-O homolysis, triplet-O2 capture, H abstraction, dehydration, and hydration."])


# Page 16. Scheme 75 uses staged one-pot transformations.
add("p0016_s75_acetal_scope", "Scheme 75 acetal scope", [15, 16], [
    P("reactant", "methoxyallene", "methoxyallene", "COC=C=C"),
    P("reagent", "m-CPBA", "meta-chloroperoxybenzoic acid", None, [("amount", q(2, "equiv"))]),
    P("reagent", "TiI4", "titanium(IV) iodide", None, [("amount", q(2, "equiv"))]),
    P("reactant", "ArCH(OR)2 (Ar=Ph, 4-ClC6H4, or 4-MeC6H4; R=Me or Et)", "acetal"),
    P("unspecified_agent", "acid (3-chlorobenzoic, chloroacetic, or salicylic acid)", None, None,
      [("amount", q(0.5, "equiv"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "351", "beta-alkoxy-alpha-methoxy ketone"),
], conditions=[("temperature", qr(-78, -20, "°C", "−78 °C to −20 °C"))], outcomes=[
    ("yield", qr(56, 81, "%", "56–81%"), "351"),
    ("syn_anti_ratio", "68:32 to 78:22", "351"),
], notes=["Methoxyallene oxide 350 is the depicted in-situ intermediate."])
add("p0016_s75_aldehyde_scope", "Scheme 75 aldehyde scope", [15, 16], [
    P("reactant", "methoxyallene", "methoxyallene", "COC=C=C"),
    P("reagent", "m-CPBA", "meta-chloroperoxybenzoic acid", None, [("amount", q(2, "equiv"))]),
    P("unspecified_agent", "TiI4-Lewis acid", None, None, [("amount", q(3, "equiv"))]),
    P("reactant", "RCHO (R=aryl, (E)-PhCH=CH, Ph(CH2)2, c-hex, or t-Bu)", "aldehyde"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "352", "beta-hydroxy-alpha-methoxy ketone"),
], conditions=[("temperature", qr(-78, -20, "°C", "−78 °C to −20 °C"))], outcomes=[
    ("yield", qr(53, 78, "%", "53–78%"), "352"),
    ("anti_syn_ratio", "27:73 to 94:6", "352"),
], notes=["The scheme identifies Ti(O-i-Pr)4 as the Lewis acid component; intermediate 350 is drawn."],
    unresolved=["The compact label 'TiI4-Lewis acid (3.0 equiv)' does not unambiguously partition the 3.0 equivalents between TiI4 and Ti(O-i-Pr)4."])
for suffix, subs, yld in [
    ("hh", "R1=R2=H", 87), ("me_h", "R1=Me; R2=H", 92), ("me_me", "R1=R2=Me", 96),
]:
    product = f"354 ({subs})"
    add(f"p0016_s75_353_{suffix}", f"Scheme 75 allenoic acid 353 {subs}", [15, 16], [
        P("reactant", f"353 ({subs})", "allenoic acid"),
        P("reagent", "DMD", "dimethyldioxirane", "CC1(C)OO1"),
        P("solvent", "acetone", "acetone", "CC(C)=O"),
        P("product", product, "lactone"),
    ], outcomes=[("yield", q(yld, "%"), product)])
add("p0016_s75_355", "Scheme 75 allenoic acid 355", [15, 16], [
    P("reactant", "355 (R1/R2 variable)", "allenoic acid"),
    P("reagent", "DMD", "dimethyldioxirane", "CC1(C)OO1"),
    P("solvent", "acetone", "acetone", "CC(C)=O"),
    P("product", "356", "lactone"),
], outcomes=[("yield", q(52, "%"), "356")])

s76_rows = [
    ("ch2_o_hh_ph", "X=CH2; W=O; R1=R2=H; R3=Ph", 2.0, 40, ">95:5"),
    ("o_nme_mehph", "X=O; W=NMe; R1=Me; R2=H; R3=Ph", 2.0, 60, ">95:5"),
    ("ch2_nme_mehph", "X=CH2; W=NMe; R1=Me; R2=H; R3=Ph", 2.0, 83, "96:4"),
    ("o_o_hh_chph2", "X=O; W=O; R1=R2=H; R3=CHPh2", None, 74, ">95:5"),
    ("ch2_o_hh_chph2", "X=CH2; W=O; R1=R2=H; R3=CHPh2", None, 62, "93:7"),
    ("o_o_phph_ipr", "X=O; W=O; R1=R2=Ph; R3=i-Pr", None, 72, "94:6"),
]
for suffix, subs, zn_equiv, yld, ratio in s76_rows:
    parts = [
        P("reactant", f"357 ({subs})", "1-aminoallene"),
        P("reagent", "dimethyldioxirane", "dimethyldioxirane", "CC1(C)OO1",
          [("amount", qr(2, 3, "equiv", "2–3 equiv"))]),
        P("reactant", "furan or cyclopentadiene"),
    ]
    if zn_equiv is not None:
        parts.append(P("unspecified_agent", "ZnCl2", "zinc chloride", "[Cl-].[Cl-].[Zn+2]",
                       [("amount", q(zn_equiv, "equiv"))]))
    parts += [P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
              P("product", f"358/359 ({subs})", "[4+3] cycloadducts")]
    add(f"p0016_s76_{suffix}", f"Scheme 76 {subs}", [15, 16], parts,
        conditions=[("temperature", qr(-50, -40, "°C", "−40 °C to −50 °C")), ("time", q(8, "h"))],
        outcomes=[("yield", q(yld, "%"), f"358/359 ({subs})"),
                  ("reported_product_ratio", ratio, f"358/359 ({subs})")],
        unresolved=["The table's parenthesized ratio is preserved without expanding its abbreviated heading."])

mechanism("p0016_s77_inter_path", "Scheme 77 intermolecular [4+3] pathway", [16],
          ["357A", "360", "361", "362"], notes=["The incoming five-membered diene is furan or cyclopentadiene."])
for suffix, r_group, duration, yld in [("ph", "R=Ph", 30, 75), ("ipr", "R=i-Pr", 10, 65)]:
    product = f"364 ({r_group})"
    add(f"p0016_s77_363_{suffix}", f"Scheme 77 intramolecular {r_group}", [16], [
        P("reactant", f"363 ({r_group})", "tethered aminoallene"),
        P("reagent", "DMD", "dimethyldioxirane", "CC1(C)OO1",
          [("amount", qr(2, 5, "equiv", "2–5 equiv"))]),
        P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
        P("product", product, "intramolecular [4+3] cycloadduct"),
    ], conditions=[("temperature", q(-78, "°C")), ("time", q(duration, "min"))], outcomes=[
        ("yield", q(yld, "%"), product), ("diastereomer_ratio", "95:5", product),
    ])

add("p0016_s78", "Scheme 78 monoepisulfidation scope", [16], [
    P("reactant", "365 (R1/R2 scope)", "allene"),
    P("reagent", "366 (R=Me or Ph)", "thiirane"),
    P("catalyst", "Mo(O)L2 complex 368 or 369", None, None,
      [("catalyst_loading", qr(1, 10, "mol%", "1–10 mol%"))]),
    P("reagent", "Na2S4 and S8"),
    P("solvent", "CD3COCD3, CDCl3, or C6D6"),
    P("product", "367", "allene episulfide"),
], outcomes=[("yield", qr(36, 95, "%", "36–95%"), "367")])

first79 = add("p0016_s79_371", "Scheme 79 ammonia workup branch", [16], [
    P("reactant", "370", "iminium-activated allene"),
    P("reagent", "HCO2H", "formic acid", "O=CO"),
    P("reagent", "NH3 in MeOH", "ammonia in methanol", None, [("concentration", q(50, "%"))]),
    P("product", "371", "bridged ketone"),
], conditions=[("temperature", q(85, "°C"))], outcomes=[("yield", q(79, "%"), "371")])
set_steps(first79, [
    (["370", "HCO2H"], [("temperature", q(85, "°C"))]),
    (["NH3 in MeOH"], [("operation", "50% ammonia in methanol treatment")]),
])
add("p0016_s79_373", "Scheme 79 NaI branch", [16], [
    P("reactant", "370", "iminium-activated allene"),
    P("reagent", "NaI", "sodium iodide", "[Na+].[I-]"),
    P("reagent", "HCO2H", "formic acid", "O=CO"),
    P("product", "373", "iodinated bridged product"),
], conditions=[("temperature", q(85, "°C"))], outcomes=[("yield", q(42, "%"), "373")],
    notes=["Zwitterionic iminium 372 is drawn as the proposed intermediate."])
mechanism("p0016_s79_mechanism", "Scheme 79 nucleophilic-addition pathway", [16],
          ["370 + NaI/HCO2H", "372", "373"], conditions=[("temperature", q(85, "°C"))])


# Page 17. Scheme 80.
for n_value in [1, 4]:
    product = f"375 (n={n_value})"
    add(f"p0017_s80_374_n{n_value}", f"Scheme 80 alcohol nucleophile n={n_value}", [16, 17], [
        P("reactant", f"374 (n={n_value})", "hydroxy-1,2-allenyl sulfone"),
        P("reagent", "t-BuOK", "potassium tert-butoxide", "CC(C)(C)[O-].[K+]"),
        P("solvent", "t-BuOH", "tert-butanol", "CC(C)(C)O"),
        P("product", product, "cyclic ether"),
    ], conditions=[("temperature", "r.t.")])
add("p0017_s80_376_scope", "Scheme 80 carbon-nucleophile scope", [16, 17], [
    P("reactant", "376 (R=Me or Et; E=CO2Me, SO2Ph, CO2Et, or COPh; n=1 or 2)"),
    P("reagent", "t-BuOK", "potassium tert-butoxide", "CC(C)(C)[O-].[K+]"),
    P("solvent", "t-BuOH", "tert-butanol", "CC(C)(C)O"),
    P("product", "377", "carbocyclic product"),
], conditions=[("temperature", "r.t.")], notes=["The arrow is marked ibid relative to 374."])
for suffix, r1, solvent, yld in [("bz", "R1=Bz", "THF", 28), ("h", "R1=H", "t-BuOH", 37)]:
    product = f"379 ({r1})"
    add(f"p0017_s80_378_{suffix}", f"Scheme 80 amide nucleophile {r1}", [16, 17], [
        P("reactant", f"378 ({r1})", "amido-1,2-allenyl sulfone"),
        P("reagent", "t-BuOK", "potassium tert-butoxide", "CC(C)(C)[O-].[K+]"),
        P("solvent", solvent),
        P("product", product, "cyclic amine"),
    ], outcomes=[("yield", q(yld, "%"), product)])
add("p0017_s80_380_deprotection", "Scheme 80 substrate 380 deprotection", [16, 17], [
    P("reactant", "380", "Boc-protected amino-1,2-allenyl sulfone"),
    P("reagent", "TFA", "trifluoroacetic acid", "O=C(O)C(F)(F)F"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "deprotected 380 intermediate"),
], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(83, "%"), "deprotected 380 intermediate")])
add("p0017_s80_380_oxidation", "Scheme 80 substrate 380 oxidative cyclization", [16, 17], [
    P("reactant", "deprotected 380 intermediate"),
    P("catalyst", "Salcomine"),
    P("reagent", "O2", "oxygen", "O=O"),
    P("solvent", "MeOH", "methanol", "CO"),
    P("product", "381", "benzazepine product"),
], conditions=[("temperature", "r.t.")], outcomes=[("yield", q(77, "%"), "381")])

for suffix, r_group, yld in [("nc6h13", "R=n-C6H13", 69), ("ph", "R=Ph", 33), ("tms", "R=TMS", 40)]:
    product = f"E-383 ({r_group})"
    record = add(f"p0017_s81_383_{suffix}", f"Scheme 81 product E-383 {r_group}", [16, 17], [
        P("reactant", "4-octyne", "4-octyne"),
        P("reagent", "Co2(CO)8", "dicobalt octacarbonyl"),
        P("solvent", "pentane", "pentane", "CCCCC"),
        P("unspecified_agent", "382", "alkyne-dicobalt complex"),
        P("reactant", f"allene ({r_group})"),
        P("reagent", "NMMO", "N-methylmorpholine N-oxide"),
        P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
        P("product", product, "4-alkylidene-2-cyclopentenone"),
    ], outcomes=[("yield", q(yld, "%"), product)])
    set_steps(record, [
        (["4-octyne", "Co2(CO)8", "pentane"], [("temperature", qr(-100, -90, "°C", "−90 to −100 °C"))]),
        (["382", f"allene ({r_group})", "NMMO", "CH2Cl2"], [("temperature", qr(0, 20, "°C", "0–20 °C"))]),
    ])
add("p0017_s81_384", "Scheme 81 product 384", [16, 17], [
    P("reactant", "382", "4-octyne-dicobalt complex"),
    P("reactant", "3-methyl-1,2-butadiene"),
    P("reagent", "NMMO", "N-methylmorpholine N-oxide"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "384", "Pauson-Khand product"),
], conditions=[("temperature", qr(0, 20, "°C", "0–20 °C"))], outcomes=[("yield", q(61, "%"), "384")],
    notes=["The arrow is marked ibid relative to formation of E-383."])
add("p0017_s81_385", "Scheme 81 product E-385", [16, 17], [
    P("reactant", "382", "4-octyne-dicobalt complex"),
    P("reactant", "1,3-di-n-pentylallene"),
    P("reagent", "NMMO", "N-methylmorpholine N-oxide"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "E-385", "Pauson-Khand product"),
], conditions=[("temperature", qr(0, 20, "°C", "0–20 °C"))], outcomes=[("yield", q(66, "%"), "E-385")],
    notes=["The arrow is marked ibid relative to formation of E-383."])
for suffix, r_group, yld, ratio in [("c5h11", "R=C5H11", 54, "79:21"), ("ph", "R=Ph", 52, "75:25")]:
    product = f"386 ({r_group})"
    add(f"p0017_s81_386_{suffix}", f"Scheme 81 product 386 {r_group}", [16, 17], [
        P("reactant", f"alkyne-dicobalt complex ({r_group})"),
        P("reactant", "n-hexylallene"),
        P("reagent", "NMMO", "N-methylmorpholine N-oxide"),
        P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
        P("product", product, "Pauson-Khand product"),
    ], conditions=[("temperature", qr(0, 20, "°C", "0–20 °C"))], outcomes=[
        ("yield", q(yld, "%"), product), ("E_Z_ratio", ratio, product),
    ], notes=["The arrow is marked ibid."])
add("p0017_s81_387", "Scheme 81 cyclic-allene example", [16, 17], [
    P("reactant", "4-octyne-dicobalt complex"),
    P("reactant", "cyclic allene (drawn)"),
    P("reagent", "NMMO", "N-methylmorpholine N-oxide", None, [("amount", q(6, "equiv"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "387", "fused Pauson-Khand product"),
], conditions=[("temperature", qr(0, 20, "°C", "0–20 °C"))], outcomes=[("yield", q(56, "%"), "387")])

add("p0017_s82_388_scope", "Scheme 82 silyl-alkyne scope", [17], [
    P("reactant", "silyl alkyne-dicobalt complex (R1=H, Me, or TMS)"),
    P("reactant", "allene (R2 variable)"),
    P("reagent", "NMO", "N-methylmorpholine N-oxide", None, [("amount", q(6, "equiv"))]),
    P("solvent", "CH2Cl2 or CH2Cl2/THF (1:1)"),
    P("product", "388", "major Pauson-Khand regioisomer"),
    P("product", "389", "minor Pauson-Khand regioisomer"),
], conditions=[("temperature", None)], outcomes=[
    ("product_ratio_388_to_389", ">10:1", ["388", "389"]),
    ("E_Z_ratio", "70:30 to 83:17", "388"),
], notes=["The source gives alternative temperature programs, '0–20 °C' or '−78 to 20 °C', without row-resolved mapping."])
add("p0017_s82_nbu", "Scheme 82 prose n-Bu case", [17], [
    P("reactant", "silyl-alkyne/allene substrate (R1=n-Bu)"),
    P("product", "388 (R1=n-Bu)"),
], outcomes=[("E_Z_ratio", "100:0", "388 (R1=n-Bu)")],
    unresolved=["The compact prose does not fully map this R1 label onto the generic Scheme 82 drawings."])
add("p0017_s82_tbu_failure", "Scheme 82 prose t-Bu failure", [17], [
    P("reactant", "silyl-alkyne/allene substrate (R1=t-Bu)"),
], outcomes=[("reaction_result", "did not occur", None), ("yield", None, None)],
    unresolved=["The compact prose does not fully map this R1 label onto the generic Scheme 82 drawings."])
add("p0017_s82_390", "Scheme 82 allenamide scope", [17], [
    P("reactant", "390 (Z=Ar or Ts; R1=MeO, F, or H)", "allenamide"),
    P("reactant", "alkyne (R2=aryl or alkyl; R3=H or R2)", None, None,
      [("amount", q(1.5, "equiv"))]),
    P("reagent", "Co2(CO)8", "dicobalt octacarbonyl", None, [("amount", q(1.5, "equiv"))]),
    P("reagent", "NMO", "N-methylmorpholine N-oxide"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"),
    P("product", "E-391", "allenamide Pauson-Khand product"),
], outcomes=[("yield", qr(25, 85, "%", "25–85%"), "E-391")])
s82_fe_rows = [
    ("row1", "R1=Ph(CH2)3; R2=TMS; R3=Ph; R4=H", 58, 15),
    ("row2", "R1=Ph; R2=TMS; R3=Ph; R4=H", 54, 12),
    ("row3", "R1=Ph(CH2)3; R2=TMS; R3=Ph; R4=Ph", 60, None),
    ("row4", "R1=Ph(CH2)3; R2=TMS; R3=n-Bu; R4=H", 55, 6),
    ("row5", "R1=Ph(CH2)3; R2=TMS; R3=n-Pr; R4=n-Pr", 57, None),
]
for suffix, subs, y392, y393 in s82_fe_rows:
    outcomes = [("yield", q(y392, "%"), f"392 ({subs})"),
                ("yield", None if y393 is None else q(y393, "%"), f"393 ({subs})")]
    add(f"p0017_s82_fe_{suffix}", f"Scheme 82 Fe-mediated {subs}", [17], [
        P("reactant", f"allene ({subs})"), P("reactant", f"alkyne ({subs})"),
        P("reagent", "Fe(CO)4(NMe3)"),
        P("product", f"392 ({subs})", "cyclopent-2-enone regioisomer"),
        P("product", f"393 ({subs})", "cyclopent-2-enone regioisomer"),
    ], conditions=[("operation", "hν irradiation")], outcomes=outcomes,
        notes=["A dash is printed for product 393." ] if y393 is None else None)

add("p0017_s83_395", "Scheme 83 arene 395 scope", [17], [
    P("reactant", "allene (R1=alkyl or Ph)"),
    P("reactant", "methyl 2-alkynoate (R2=CO2Me or alkyl)", None, None, [("amount", q(2, "equiv"))]),
    P("catalyst", "Ni(dppe)Br2"), P("reagent", "Zn", "zinc", "[Zn]"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "395", "polysubstituted arene"),
], conditions=[("temperature", q(80, "°C")), ("time", q(8, "h"))],
    outcomes=[("yield", qr(69, 86, "%", "69–86%"), "395")])
add("p0017_s83_396", "Scheme 83 3-phenylpropynoate branch", [17], [
    P("reactant", "allene (R1 variable)"), P("reactant", "methyl 3-phenylpropynoate", None, None, [("amount", q(2, "equiv"))]),
    P("catalyst", "Ni(dppe)Br2"), P("reagent", "Zn", "zinc", "[Zn]"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "396", "polysubstituted arene"),
], conditions=[("temperature", q(80, "°C")), ("time", q(8, "h"))], notes=["The arrow is marked ibid."])
add("p0017_s83_397", "Scheme 83 tethered diyne scope", [17], [
    P("reactant", "1,6- or 1,7-alkadiynoate (X=(CH2)2, CH2, or O; R1=H or CO2Me)"),
    P("reactant", "allene (R2=aryl, alkyl, or cyclic alkyl)"),
    P("catalyst", "Ni(dppe)Br2"), P("reagent", "Zn", "zinc", "[Zn]"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"), P("product", "397", "benzocyclic product"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", qr(63, 90, "%", "63–90%"), "397")])


# Page 18. Scheme 84--87 plus prose-only leads to Schemes 88--90.
add("p0018_s84", "Scheme 84 overall", [18], [
    P("reactant", "398 (R1=H or Me)", "aryne precursor"),
    P("reactant", "allene (R2=H, alkyl, cyclic alkyl, or t-Bu)"),
    P("catalyst", "NiBr2(dppe)"), P("reagent", "Zn", "zinc", "[Zn]"),
    P("reagent", "CsF", "cesium fluoride", "[Cs+].[F-]"),
    P("solvent", "MeCN", "acetonitrile", "CC#N"),
    P("product", "402", "nonaromatic six-membered-ring product"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[("yield", qr(46, 67, "%", "46–67%"), "402")])
mechanism("p0018_s84_mechanism", "Scheme 84 proposed cyclometalation", [18],
          ["398", "399", "400", "401", "402"], conditions=[("temperature", q(80, "°C"))],
          notes=["Benzyne 399 is generated in situ; the drawing ends with reductive elimination."])

add("p0018_s85", "Scheme 85 scope", [18], [
    P("reactant", "403 (R1 scope)", "terminal allene"),
    P("reactant", "404 (R2=Me, Ph, or cyclohexyl)", "alpha,beta-unsaturated ketone"),
    P("catalyst", "CpRu(COD)Cl", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "CeCl3·7H2O", None, None, [("amount", q(15, "mol%"))]),
    P("unspecified_agent", "3-hexynol", None, None, [("amount", q(10, "mol%"))]),
    P("product", "407", "3-methylene-4-(E)-alkenyl ketone"),
], outcomes=[("yield", qr(53, 81, "%", "53–81%"), "407")])
mechanism("p0018_s85_mechanism", "Scheme 85 proposed Ru pathway", [18],
          ["403 + 404", "405", "406", "407"],
          notes=["The drawing labels beta-H elimination followed by reductive elimination."])

add("p0018_s86_408", "Scheme 86 allenol 408 scope", [18], [
    P("reactant", "408 (n=1 or 2)", "4,5- or 5,6-allenol"),
    P("reactant", "enone (R=Me or Ph)"),
    P("catalyst", "CpRu(COD)Cl or CpRu(NCMe)3PF6", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "CeCl3·7H2O", None, None, [("amount", q(15, "mol%"))]),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "409", "cyclic ether"),
], conditions=[("temperature", q(60, "°C"))], outcomes=[("yield", qr(70, 82, "%", "70–82%"), "409")])
add("p0018_s86_410", "Scheme 86 allenol 410 scope", [18], [
    P("reactant", "410 (m=1 or 2; n=1 or 2)", "cyclic allenol"),
    P("reactant", "enone (R=Me or cyclohexyl)"),
    P("catalyst", "CpRu(COD)Cl or CpRu(NCMe)3PF6", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "CeCl3·7H2O", None, None, [("amount", q(15, "mol%"))]),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "411", "fused cyclic ether"),
], conditions=[("temperature", q(60, "°C"))], outcomes=[("yield", qr(61, 73, "%", "61–73%"), "411")],
    notes=["The arrow is marked ibid relative to the 408 scope."])
add("p0018_s86_412", "Scheme 86 allenylamine 412 scope", [18], [
    P("reactant", "412 (n=1 or 2; Ar=Ph or p-MeOC6H4)", "allenylamine"),
    P("reactant", "enone (R=Me or Ph)"),
    P("catalyst", "CpRu(NCMe)3PF6", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "TiCl4 or MeAlCl2", None, None, [("amount", q(15, "mol%"))]),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "413", "pyrrolidine or piperidine"),
], conditions=[("condition_options", "TiCl4: 60 °C, 2 h; MeAlCl2: 40 °C, 1 h")],
    outcomes=[("yield", qr(70, 82, "%", "70–82%"), "413")],
    unresolved=["The review does not map each catalyst/additive option to each substrate row."])
add("p0018_s86_414", "Scheme 86 cyclic allenylamine 414 scope", [18], [
    P("reactant", "414 (m=1 or 2; n=1 or 2)", "cyclic allenylamine"),
    P("reactant", "enone (R=Me or Ph)"),
    P("catalyst", "CpRu(NCMe)3PF6", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("unspecified_agent", "TiCl4 or MeAlCl2", None, None, [("amount", q(15, "mol%"))]),
    P("solvent", "DMF", "dimethylformamide", "CN(C)C=O"),
    P("product", "415", "fused pyrrolidine or piperidine"),
], conditions=[("condition_options", "TiCl4: 60 °C, 2 h; MeAlCl2: 40 °C, 1 h")],
    notes=["The arrow is marked ibid relative to 412; no yield is printed for 415."],
    unresolved=["The review does not map each catalyst/additive option to each substrate row."])

add("p0018_s87", "Scheme 87 allene dimerization scope", [18], [
    P("reactant", "416 (R scope)", "allene", None, [("stoichiometry", q(2, "equiv"))]),
    P("catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)"),
    P("reagent", "HCO2H", "formic acid", "O=CO"),
    P("solvent", "DMF or toluene"),
    P("product", "420", "conjugated diene regioisomer"),
    P("product", "421", "conjugated diene regioisomer"),
], conditions=[("temperature", None)], outcomes=[
    ("yield", qr(39, 83, "%", "39–83%"), ["420", "421"]),
    ("product_ratio_420_to_421", "1:1", ["420", "421"]),
], notes=["The review prints a broad R-group scope; individual yield mappings are absent.",
          "The source reports temperatures from room temperature to 50 °C without row-resolved mapping."])
mechanism("p0018_s87_mechanism", "Scheme 87 proposed Pd dimerization", [18],
          ["416", "417", "418 / 419", "420 / 421"],
          notes=["The review proposes monoprotonolysis, CO2 elimination, and reductive elimination."])

add("p0018_s88_422", "Scheme 88 text-only 422 reaction", [18], [
    P("reactant", "422", "4-hydroxycoumarin"), P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("product", "423", "bis-propenylation product"),
], unresolved=["Scheme 88 is on the following page; only page-18 prose was used."])
add("p0018_s88_423", "Scheme 88 text-only cyclization of 423", [18], [
    P("reactant", "423", "bis-propenylation product"), P("product", "424", "tricyclic product"),
], unresolved=["Scheme 88 is on the following page; conditions and yield are unavailable in this page batch."])
for precursor, product in [("425", "426"), ("427", "428")]:
    add(f"p0018_s88_{precursor}", f"Scheme 88 text-only {precursor}", [18], [
        P("reactant", precursor, "methylene pronucleophile"),
        P("reactant", "propadiene", "propadiene", "C=C=C"),
        P("product", product, "bis-propenylation product"),
    ], unresolved=["Scheme 88 is on the following page; only page-18 prose was used."])
mechanism("p0018_s89_mechanism", "Scheme 89 prose-only proposed pathways", [18],
          ["two propadienes", "417", "429 / 431", "430", "432"],
          notes=["The prose proposes oxidative-addition/double-reductive-elimination and hydropalladation/carbopalladation alternatives."])
add("p0018_s90_text_only", "Scheme 90 text-only dimeric cyclometalation", [18], [
    P("reactant", "433", "2,3-allenol", None, [("stoichiometry", q(2, "equiv"))]),
    P("catalyst", "CpRu(MeCN)3PF6"),
    P("product", "437", "5-acetoxy-3-methylenealk-5-en-1,7-diol"),
], notes=["The prose attributes formation to cyclometalation, reductive elimination, and intramolecular protonolysis."],
    unresolved=["Scheme 90 is on a later page; conditions, intermediates, and yield are not visible in this page batch."])


# Persist raw records.
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Coverage ledger. Record IDs are derived from submitted records, including cross-page links.
regions = {
    13: [
        ("左栏上部 Scheme 61–62", "引用工作：Scheme 61按R=H/Me两行补全收率与cis/trans；Scheme 62记录272→276总体反应及273–275提议路径。"),
        ("左栏中下部 Scheme 63", "引用工作：277的[3+2]/[4+3]分支和280的[8+2]分支分别记录。"),
        ("右栏上部 Scheme 64", "引用工作：SmI2两行、Bu3SnH/AIBN对照和高同系物还原支路分开；保留产物比和不完整支路。"),
        ("右栏下部 Scheme 65与跨页正文", "引用工作及机理：289+丙二烯基甲醚生成290；Scheme 66–67说明跨至第14页并合并证据。"),
    ],
    14: [
        ("左栏上部 Scheme 66", "引用工作/机理：SmI2酮基自由基加成、1,5-H迁移分支及两个具体底物结果。"),
        ("左栏中下部 Scheme 67", "引用工作：302/304/306/308各箭头、TsBr/TsI分支及各产物收率逐项记录。"),
        ("右栏 Scheme 68–69", "引用工作与机理：E-313形成、n=1失败、n=2/3/4环化、四烯范围及316→319自由基级联。"),
        ("右栏下部 Scheme 70", "引用工作：320的25 °C环氧化和321的100 °C重排为连续但独立步骤。"),
    ],
    15: [
        ("左栏 Scheme 71", "引用工作/逐行范围：单取代、1,3-二取代及两个多产物氧化行；图中80 °C与rt, 5 h并列，阶段关系保留未决。"),
        ("左栏下部 Scheme 72", "引用工作：通式双环氧化选择性、单取代物分布以及328/329两个具体收率。"),
        ("右栏上部 Scheme 73", "引用工作/机理：330三行、333、335及337分步氧化，逐箭头记录。"),
        ("右栏中下部 Scheme 74", "引用工作与提议路径：环状联烯光氧化至348/349，机理中间体343–347单列。"),
    ],
    16: [
        ("左栏上部 Scheme 75", "引用工作：缩醛与醛两类范围、353三行及355一行，保留当量、温区、收率和选择性。"),
        ("左栏中部 Scheme 76", "引用工作/六行范围：逐行记录X/W/R取代、ZnCl2当量、收率和括号内产物比。"),
        ("左栏下部 Scheme 77", "提议分子间[4+3]路径及363的R=Ph/i-Pr两条分子内结果。"),
        ("右栏上部 Scheme 78–79", "引用工作：Mo催化单硫环氧化范围；370的氨处理与NaI分支及372提议中间体。"),
        ("右栏下部章节引言", "正文引入Scheme 80–81，具体图在第17页；相应跨页记录同时引用本页与第17页。"),
    ],
    17: [
        ("左栏上部 Scheme 80", "引用工作：374的n=1/4、376范围、378两溶剂结果及380两步序列分别记录。"),
        ("左栏中下部 Scheme 81", "引用工作/底物范围：E-383三行、384、E-385、386两行及387逐项记录。"),
        ("右栏上部 Scheme 82", "引用工作/逐行范围：388/389范围、n-Bu选择性、t-Bu失败、390范围及Fe介导五行。"),
        ("右栏下部 Scheme 83", "引用工作：395范围、396区域化学分支及397二炔范围。"),
    ],
    18: [
        ("左栏上部 Scheme 84", "引用工作与机理：原位苯炔399与联烯的Ni催化反应及400/401路径。"),
        ("左栏中下部 Scheme 85", "引用工作与机理：403+404总体范围和405/406的β-H消除/还原消除路径。"),
        ("右栏上部 Scheme 86", "引用工作/四个范围：408、410、412、414分别记录催化剂/添加剂、条件选项、收率或缺失值。"),
        ("右栏中部 Scheme 87", "引用工作与机理：416二聚生成420/421及417–419提议路径。"),
        ("页底 Scheme 88–90引入正文", "仅有正文的引用工作/机理引入；建立text-only部分记录并明确图、条件和收率位于后页而未在本批次核查。"),
    ],
}
unresolved = {
    13: ["Scheme 62为通式范围；Scheme 64竖直还原支路的n值和收率无法从本页可靠分配。", "全部为综述引用工作，未提供原始论文实验部分或SI。"],
    14: ["Scheme 66的55:45括号值测定对象未明；Scheme 67/68若干箭头缺完整条件和收率基础。"],
    15: ["Scheme 71同时印有80 °C与rt, 5 h，阶段归属不清；未擅自合并为单一温度。", "Scheme 72–74多为机理或范围汇总，缺逐底物条件/收率基础。"],
    16: ["Scheme 75下支路的TiI4/Lewis acid 3.0 equiv分配不清。", "Scheme 76括号内比值标题缩写不清，仅原样保留；Scheme 78为汇总范围。"],
    17: ["Scheme 82正文n-Bu/t-Bu的R1与紧凑通式映射需查原始论文。", "多处为汇总范围，单个底物的收率/条件映射和测定基础缺失。"],
    18: ["Scheme 86条件选项未逐底物映射。", "Scheme 88–90反应图位于后页，本批次只编码第18页明确正文，不声称核查后页图。"],
}
coverage_pages = []
for page in range(13, 19):
    image_id = f"{DOC}:page{page}:image"
    record_ids = [record["record_id"] for record in records if image_id in record["evidence_ids"]]
    coverage_pages.append({
        "page": page,
        "state": "attempted",
        "regions": [
            {"region": region, "finding": finding,
             "evidence_ids": [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]}
            for region, finding in regions[page]
        ],
        "record_ids": record_ids,
        "unresolved": unresolved[page],
    })
coverage = {"document_id": DOC, "semantic_accuracy_verified": False, "pages": coverage_pages}
coverage_path = BASE / "coverage" / "pages_0013_0018.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

# Mark only this page batch attempted and point each task to the image actually inspected.
tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    for page in range(13, 19):
        if task.get("evidence_id") == f"{DOC}:page{page}:text":
            task["state"] = "attempted"
            task["visual_evidence_id"] = f"{DOC}:page{page}:image"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "raw": str(OUT),
    "coverage": str(coverage_path),
    "coverage_pages": [p["page"] for p in coverage_pages],
}, ensure_ascii=False))
