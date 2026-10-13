#!/usr/bin/env python3
"""Build evidence-linked machine records for source PDF pages 1-6."""

import json
from pathlib import Path


DOC = "doc_4bdcd5de15645fe5"
OUT = Path(__file__).resolve().parent
CURRENT = OUT.parent


def ev(page, kind="text"):
    return f"{DOC}:page{page}:{kind}"


def page_evidence(*pages):
    result = []
    for page in pages:
        result.extend([ev(page, "text"), ev(page, "image")])
    return result


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number, unit, raw_text=None, **extra):
    value = {"number": number, "unit": unit}
    if raw_text is not None:
        value["raw_text"] = raw_text
    value.update(extra)
    return value


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
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants, conditions, outcomes, notes, unresolved):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
            "conditions": conditions,
        }],
        "outcomes": outcomes,
        "notes": [fact(note, evidence) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved,
        },
    }


records = []

# Table 1: each optimization row is independent. Page 1 prose explicitly discusses
# entries 1, 9, 10, and 11; the table itself is on page 2.
opt_rows = [
    (1, "NBS", 1.2, "CH3CN/H2O (10:1)", 10.5, 17, "82:18", 20, 0.3),
    (2, "NBS", 1.2, "1,4-dioxane/H2O (10:1)", 10.5, 39, "87:13", 27, 0.3),
    (3, "NBS", 1.2, "CH3NO2/H2O (10:1)", 10.5, "table dash (–)", "table dash (–)", 50, 0.3),
    (4, "NBS", 1.2, "CH2Cl2/H2O (10:1)", 17, 24, "63:37", 24, 0.3),
    (5, "NBS", 1.2, "1,4-dioxane/H2O (1:1)", 11.5, 64, "89:11", 0, 0.6),
    (6, "NBS", 1.2, "1,4-dioxane", 10, 20, "60:40", 41, 0.3),
    (7, "NBS", 1.2, "1,4-dioxane/H2O (1:10)", 18, 61, "90:10", 10, 0.3),
    (8, "NBS", 1.2, "H2O", 0.5, 20, "50:50", 0, 0.3),
    (9, "NBS", 1.5, "1,4-dioxane/H2O (1:1)", 10, 45, "91:9", 0, 0.3),
    (10, "NBS", 1.0, "1,4-dioxane/H2O (1:1)", 13, 71, "92:8", 0, 0.3),
    (11, "Br2", 1.0, "1,4-dioxane/H2O (1:1)", 0.8, 57, "68:32", 0, 0.3),
]

for entry, reagent, equiv, solvent, hours, combined, ratio, recovery, scale in opt_rows:
    pages = (1, 2) if entry in (1, 9, 10, 11) else (2,)
    evidence = page_evidence(*pages)
    rct = participant(
        "reactant_1a", "reactant", "1a", "4-phenyl-1,2-butadiene", evidence,
        "C=C=CCc1ccccc1",
        [field("amount", qty(scale, "mmol"), evidence)],
    )
    p2 = participant("product_2a", "product", "2a", "3-bromo-1-phenyl-3-buten-2-ol", evidence, "C=C(Br)C(O)Cc1ccccc1")
    p3 = participant("product_Z_3a", "product", "(Z)-3a", "(Z)-2-bromo-4-phenyl-2-buten-1-ol", evidence, "OCC(Br)=CCc1ccccc1")
    reagent_name = "N-bromosuccinimide" if reagent == "NBS" else "bromine"
    reagent_smiles = "O=C1CCC(=O)N1Br" if reagent == "NBS" else "BrBr"
    x = participant(
        "brominating_reagent", "reagent", reagent, reagent_name, evidence, reagent_smiles,
        [field("equivalents", qty(equiv, "equiv"), evidence)],
    )
    internal = participant("internal_standard", "unspecified_agent", "CH2Br2", "dibromomethane internal standard", evidence, "BrCBr")
    outcomes = [
        field(
            "combined_NMR_yield_2a_and_Z_3a",
            qty(combined, "%") if isinstance(combined, (int, float)) else combined,
            evidence,
            ["product_2a", "product_Z_3a"],
        ),
        field("product_ratio_2a_to_Z_3a", ratio, evidence, ["product_2a", "product_Z_3a"]),
        field("recovered_starting_material_yield", qty(recovery, "%"), evidence, ["reactant_1a"]),
        field("yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", evidence),
    ]
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", evidence,
        [rct, p2, p3, x, internal],
        [field("solvent", solvent, evidence), field("temperature", "r.t.", evidence), field("time", qty(hours, "h"), evidence)],
        outcomes,
        ["Table 1 optimization row; product structures are shown in the table header."],
        ["Exact solvent component volumes and workup are not reported for this optimization row.", "Supporting information was not provided or associated."],
    ))


scope = {
    "a": dict(entry=1, r1="Bn", r2="H", react="buta-2,3-dienylbenzene", p2="3-bromo-1-phenyl-3-buten-2-ol", p3="(Z)-2-bromo-4-phenyl-2-buten-1-ol", time=16, nmr=72, ratio="91:9", y2=63, y3=4, page=3, mmol=10.0, rmass=1300.4, nbsmass=1780.2, diox=20.0, water=20.0, p2mass=1416.6, p3mass=93.0, s1="C=C=CCc1ccccc1", s2="C=C(Br)C(O)Cc1ccccc1", s3="OCC(Br)=CCc1ccccc1"),
    "b": dict(entry=2, r1="n-C10H21", r2="H", react="trideca-1,2-diene", p2="2-bromo-1-tridecen-3-ol", p3="(Z)-2-bromo-2-tridecen-1-ol", time=17, nmr=86, ratio="94:6", y2=68, y3=5, page=4, mmol=5.0, rmass=900.9, nbsmass=895.6, diox=10.0, water=10.0, p2mass=963.2, p3mass=61.8, s1="C=C=CCCCCCCCCCC", s2="C=C(Br)C(O)CCCCCCCCCC", s3="OCC(Br)=CCCCCCCCCCC"),
    "c": dict(entry=3, r1="n-C8H17", r2="H", react="undeca-1,2-diene", p2="2-bromo-1-undecen-3-ol", p3="(Z)-2-bromo-2-undecen-1-ol", time=19, nmr=74, ratio="96:4", y2=62, y3=5, page=4, mmol=5.0, rmass=760.1, nbsmass=895.6, diox=10.0, water=10.0, p2mass=772.1, p3mass=58.6, s1="C=C=CCCCCCCCC", s2="C=C(Br)C(O)CCCCCCCC", s3="OCC(Br)=CCCCCCCCC"),
    "d": dict(entry=4, r1="n-C7H15", r2="H", react="deca-1,2-diene", p2="2-bromo-1-decen-3-ol", p3="(Z)-2-bromo-2-decen-1-ol", time=22, nmr=90, ratio="94:6", y2=82, y3=5, page=4, mmol=2.0, rmass=276.1, nbsmass=358.3, diox=7.0, water=7.0, p2mass=385.8, p3mass=25.3, s1="C=C=CCCCCCCC", s2="C=C(Br)C(O)CCCCCCC", s3="OCC(Br)=CCCCCCCC"),
    "e": dict(entry=5, r1="n-C6H13", r2="H", react="nona-1,2-diene", p2="2-bromo-1-nonen-3-ol", p3="(Z)-2-bromo-2-nonen-1-ol", time=16, nmr=85, ratio="93:7", y2=69, y3=4, page=4, mmol=5.0, rmass=621.0, nbsmass=895.3, diox=10.0, water=10.0, p2mass=766.5, p3mass=44.9, s1="C=C=CCCCCCC", s2="C=C(Br)C(O)CCCCCC", s3="OCC(Br)=CCCCCCC"),
    "f": dict(entry=6, r1="c-C6H11", r2="H", react="propa-1,2-dienylcyclohexane", p2="2-bromo-1-cyclohexyl-2-propen-1-ol", p3="(Z)-2-bromo-3-cyclohexyl-2-propen-1-ol", time=17, nmr=65, ratio="89:11", y2=58, y3=3, page=4, extra_page=5, mmol=5.0, rmass=611.1, nbsmass=895.5, diox=10.0, water=10.0, p2mass=632.3, p3mass=31.1, s1="C=C=CC1CCCCC1", s2="C=C(Br)C(O)C1CCCCC1", s3="OCC(Br)=CC1CCCCC1"),
    "g": dict(entry=7, r1="Ph", r2="H", react="propa-1,2-dienylbenzene", p2="2-bromo-1-phenyl-2-propen-1-ol", p3="(Z)-2-bromo-3-phenyl-2-propen-1-ol", time=16, nmr=74, ratio="78:22", y2=59, y3=9, page=5, mmol=2.0, rmass=232.2, nbsmass=358.4, diox=7.0, water=7.0, p2mass=251.3, p3mass=39.2, s1="C=C=Cc1ccccc1", s2="C=C(Br)C(O)c1ccccc1", s3="OCC(Br)=Cc1ccccc1"),
    "h": dict(entry=8, r1="Et", r2="Ph", react="penta-1,2-dien-3-ylbenzene", p2="2-bromo-3-phenyl-1-penten-3-ol", p3="(E)-2-bromo-3-phenyl-2-penten-1-ol", time=23, nmr=76, ratio="88:12", y2=65, y3=8, page=5, mmol=2.0, rmass=288.0, nbsmass=358.4, diox=7.0, water=7.0, p2mass=311.9, p3mass=39.3, s1="C=C=C(CC)c1ccccc1", s2="C=C(Br)C(O)(CC)c1ccccc1", s3="OCC(Br)=C(CC)c1ccccc1"),
    "i": dict(entry=9, r1="n-C4H9", r2="Ph", react="hepta-1,2-dien-3-ylbenzene", p2="2-bromo-3-phenyl-1-hepten-3-ol", p3="(E)-2-bromo-3-phenyl-2-hepten-1-ol", time=17.5, nmr=89, ratio="85:15", y2=63, y3=11, page=5, mmol=5.0, rmass=861.1, nbsmass=895.1, diox=10.0, water=10.0, p2mass=845.4, p3mass=151.8, s1="C=C=C(CCCC)c1ccccc1", s2="C=C(Br)C(O)(CCCC)c1ccccc1", s3="OCC(Br)=C(CCCC)c1ccccc1"),
    "j": dict(entry=10, r1="n-C6H13", r2="Ph", react="nona-1,2-dien-3-ylbenzene", p2="2-bromo-3-phenyl-1-nonen-3-ol", p3="(E)-2-bromo-3-phenyl-2-nonen-1-ol", time=20, nmr=76, ratio="87:13", y2=64, y3=10, page=5, extra_page=6, mmol=2.0, rmass=399.0, nbsmass=358.2, diox=7.0, water=7.0, p2mass=376.1, p3mass=60.1, s1="C=C=C(CCCCCC)c1ccccc1", s2="C=C(Br)C(O)(CCCCCC)c1ccccc1", s3="OCC(Br)=C(CCCCCC)c1ccccc1"),
    "k": dict(entry=11, r1="allyl", r2="Ph", react="hexa-1,2,5-trien-3-ylbenzene", p2="2-bromo-3-phenyl-1,5-hexadien-3-ol", p3="(E)-2-bromo-3-phenyl-2,5-hexadien-1-ol", time=12, nmr=76, ratio="88:12", y2=60, y3=7, page=6, mmol=2.0, rmass=15.1, nbsmass=357.5, diox=6.8, water=6.8, p2mass=306.5, p3mass=36.4, s1="C=C=C(CC=C)c1ccccc1", s2="C=C(Br)C(O)(CC=C)c1ccccc1", s3="OCC(Br)=C(CC=C)c1ccccc1"),
}

for letter, row in scope.items():
    pages = [2, row["page"]]
    if row.get("extra_page"):
        pages.append(row["extra_page"])
    evidence = page_evidence(*dict.fromkeys(pages))
    rid = f"table2_entry{row['entry']}_{letter}"
    reactant = participant(
        f"reactant_1{letter}", "reactant", f"1{letter}", row["react"], evidence, row["s1"],
        [field("mass", qty(row["rmass"], "mg"), evidence), field("amount", qty(row["mmol"], "mmol"), evidence)],
    )
    product2 = participant(f"product_2{letter}", "product", f"2{letter}", row["p2"], evidence, row["s2"])
    prefix = "(Z)-" if letter in "abcdefg" else "(E)-"
    product3 = participant(f"product_3{letter}", "product", f"{prefix}3{letter}", row["p3"], evidence, row["s3"])
    nbs = participant(
        "reagent_nbs", "reagent", "NBS", "N-bromosuccinimide", evidence, "O=C1CCC(=O)N1Br",
        [field("mass", qty(row["nbsmass"], "mg"), evidence), field("amount", qty(row["mmol"], "mmol"), evidence), field("equivalents", qty(1.0, "equiv"), evidence)],
    )
    dioxane = participant("solvent_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", evidence, "O1CCOCC1", [field("volume", qty(row["diox"], "mL"), evidence)])
    water = participant("solvent_water", "solvent", "H2O", "water", evidence, "O", [field("volume", qty(row["water"], "mL"), evidence)])
    internal = participant("internal_standard", "unspecified_agent", "CH2Br2", "dibromomethane internal standard", evidence, "BrCBr")
    outcomes = [
        field("combined_NMR_yield_2_and_3", qty(row["nmr"], "%"), evidence, [product2["entity_id"], product3["entity_id"]]),
        field("product_ratio_2_to_3", row["ratio"], evidence, [product2["entity_id"], product3["entity_id"]]),
        field("isolated_yield_2", qty(row["y2"], "%"), evidence, [product2["entity_id"]]),
        field("isolated_product_2_mass", qty(row["p2mass"], "mg"), evidence, [product2["entity_id"]]),
        field("isolated_yield_3", qty(row["y3"], "%"), evidence, [product3["entity_id"]]),
        field("isolated_product_3_mass", qty(row["p3mass"], "mg"), evidence, [product3["entity_id"]]),
        field("NMR_yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", evidence),
    ]
    notes = [f"Table 2 reports R1={row['r1']} and R2={row['r2']}; the detailed preparation says the compound pair was prepared according to the typical procedure."]
    unresolved = ["Supporting information was mentioned by the article but was not provided or associated; NOE assignments were not independently checked."]
    if letter == "a":
        outcomes.append(field("NMR_yield_2a_detailed_batch", qty(65, "%"), page_evidence(3), [product2["entity_id"]]))
        notes.append("The detailed batch gives 65% NMR yield specifically for 2a and a 91:9 ratio; this is consistent with the table's 72% combined yield after including the minor regioisomer, but the combined value is not restated in the paragraph.")
    if letter == "k":
        unresolved.append("The source visibly reports 15.1 mg together with 2.0 mmol for 1k; these quantities are internally inconsistent and are preserved without correction.")
    records.append(record(
        rid, "substrate_scope_entry", evidence,
        [reactant, product2, product3, nbs, dioxane, water, internal],
        [field("solvent", "1,4-dioxane/H2O (1:1)", evidence), field("temperature", "r.t.", evidence), field("time", qty(row["time"], "h"), evidence), field("purification", "silica-gel chromatography; eluent ratios reported in the detailed paragraph", evidence)],
        outcomes, notes, unresolved,
    ))


# Scheme 1 entries 1l and 1m, with the detailed batches on page 6.
extra_scope = {
    "l": dict(react="1,1-diphenylpropa-1,2-diene", p2="2-bromo-1,1-diphenyl-2-propen-1-ol", p3="2-bromo-3,3-diphenyl-2-propen-1-ol", time=13, y2=37, y3=20, mmol=1.0, rmass=192.4, nbsmass=178.3, diox=3.4, water=3.4, p2mass=105.9, p3mass=56.6, s1="C=C=C(c1ccccc1)c2ccccc2", s2="C=C(Br)C(O)(c1ccccc1)c2ccccc2", s3="OCC(Br)=C(c1ccccc1)c2ccccc2"),
    "m": dict(react="3-butylhepta-1,2-diene", p2="5-(1-bromovinyl)nonan-5-ol", p3="2-bromo-3-n-butyl-2-hepten-1-ol", time=25, y2=40, y3=22, mmol=0.6, rmass=90.9, nbsmass=106.9, diox=2.0, water=2.0, p2mass=60.0, p3mass=33.2, s1="C=C=C(CCCC)CCCC", s2="C=C(Br)C(O)(CCCC)CCCC", s3="OCC(Br)=C(CCCC)CCCC"),
}

for letter, row in extra_scope.items():
    evidence = page_evidence(2, 6)
    rct = participant(f"reactant_1{letter}", "reactant", f"1{letter}", row["react"], evidence, row["s1"], [field("mass", qty(row["rmass"], "mg"), evidence), field("amount", qty(row["mmol"], "mmol"), evidence)])
    p2 = participant(f"product_2{letter}", "product", f"2{letter}", row["p2"], evidence, row["s2"])
    p3 = participant(f"product_3{letter}", "product", f"3{letter}", row["p3"], evidence, row["s3"])
    nbs = participant("reagent_nbs", "reagent", "NBS", "N-bromosuccinimide", evidence, "O=C1CCC(=O)N1Br", [field("mass", qty(row["nbsmass"], "mg"), evidence), field("amount", qty(row["mmol"], "mmol"), evidence)])
    diox = participant("solvent_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", evidence, "O1CCOCC1", [field("volume", qty(row["diox"], "mL"), evidence)])
    water = participant("solvent_water", "solvent", "H2O", "water", evidence, "O", [field("volume", qty(row["water"], "mL"), evidence)])
    records.append(record(
        f"scheme1_scope_1{letter}", "substrate_scope_entry", evidence,
        [rct, p2, p3, nbs, diox, water],
        [field("solvent", "1,4-dioxane/H2O (1:1)", evidence), field("temperature", "r.t.", evidence), field("time", qty(row["time"], "h"), evidence), field("purification", "silica-gel chromatography", evidence)],
        [field("isolated_yield_2", qty(row["y2"], "%"), evidence, [p2["entity_id"]]), field("isolated_product_2_mass", qty(row["p2mass"], "mg"), evidence, [p2["entity_id"]]), field("isolated_yield_3", qty(row["y3"], "%"), evidence, [p3["entity_id"]]), field("isolated_product_3_mass", qty(row["p3mass"], "mg"), evidence, [p3["entity_id"]]), field("yield_measurement_basis", "isolated yield", evidence)],
        ["Scheme 1 substrate-scope experiment; the detailed batch appears on page 6."],
        ["No combined NMR yield or 2/3 ratio is reported for this experiment.", "Supporting information was not provided or associated."],
    ))


# Scheme 2 first arrow: 1n bromohydroxylation, detailed on page 6.
evidence = page_evidence(3, 6)
rct = participant("reactant_1n", "reactant", "1n", "1,1-diphenylbuta-1,2-diene", evidence, "CC=C=C(c1ccccc1)c2ccccc2", [field("mass", qty(123.3, "mg"), evidence), field("amount", qty(0.6, "mmol"), evidence)])
p2 = participant("product_2n", "product", "2n", "2-bromo-1,1-diphenyl-2-buten-1-ol", evidence, "CC=C(Br)C(O)(c1ccccc1)c2ccccc2")
p3 = participant("product_3n", "product", "3n", "3-bromo-4,4-diphenyl-3-buten-2-ol", evidence, "CC(O)C(Br)=C(c1ccccc1)c2ccccc2")
nbs = participant("reagent_nbs", "reagent", "NBS", "N-bromosuccinimide", evidence, "O=C1CCC(=O)N1Br", [field("mass", qty(106.7, "mg"), evidence), field("amount", qty(0.6, "mmol"), evidence), field("equivalents", qty(1.0, "equiv"), evidence)])
diox = participant("solvent_dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", evidence, "O1CCOCC1", [field("volume", qty(2.0, "mL"), evidence)])
water = participant("solvent_water", "solvent", "H2O", "water", evidence, "O", [field("volume", qty(2.0, "mL"), evidence)])
records.append(record(
    "scheme2_scope_1n", "substrate_scope_entry", evidence, [rct, p2, p3, nbs, diox, water],
    [field("solvent", "1,4-dioxane/H2O (1:1)", evidence), field("temperature", "r.t.", evidence), field("time", qty(26, "h"), evidence), field("purification", "silica-gel chromatography (petroleum ether/ethyl acetate, 40:1 to 10:1)", evidence)],
    [field("isolated_yield_2n", qty(21, "%"), evidence, ["product_2n"]), field("isolated_product_2n_mass", qty(37.2, "mg"), evidence, ["product_2n"]), field("Z_to_E_ratio_within_2n", "60:40", evidence, ["product_2n"]), field("isolated_yield_3n", qty(45, "%"), evidence, ["product_3n"]), field("isolated_product_3n_mass", qty(81.5, "mg"), evidence, ["product_3n"]), field("yield_measurement_basis", "isolated yield", evidence)],
    ["Scheme 2 and the page-6 detailed preparation describe the same 1n bromohydroxylation batch."],
    ["The isolated 2n is a Z/E mixture; structures of the individual isomers were not independently verified.", "Supporting information was not provided or associated."],
))


# Scheme 2 second arrow: selective elimination of the E component of 2n.
evidence = page_evidence(3)
rct = participant("reactant_2n_mixture", "reactant", "2n", "Z/E mixture of 2-bromo-1,1-diphenyl-2-buten-1-ol", evidence, "CC=C(Br)C(O)(c1ccccc1)c2ccccc2")
tbaf = participant("reagent_tbaf", "reagent", "TBAF", "tetrabutylammonium fluoride", evidence)
dmf = participant("solvent_dmf", "solvent", "DMF", "N,N-dimethylformamide", evidence, "CN(C)C=O")
p4n = participant("product_4n", "product", "4n", "1,1-diphenyl-2-butyn-1-ol", evidence, "CC#CC(O)(c1ccccc1)c2ccccc2")
pz = participant("product_Z_2n", "product", "(Z)-2n", "(Z)-2-bromo-1,1-diphenyl-2-buten-1-ol", evidence, "CC=C(Br)C(O)(c1ccccc1)c2ccccc2")
records.append(record(
    "scheme2_tbaf_2n", "reported_experiment", evidence, [rct, tbaf, dmf, p4n, pz],
    [field("solvent", "DMF", evidence), field("temperature", "r.t.", evidence), field("time", qty(24, "h"), evidence)],
    [field("isolated_yield_4n", qty(6, "%"), evidence, ["product_4n"]), field("isolated_yield_Z_2n", qty(51, "%"), evidence, ["product_Z_2n"]), field("yield_measurement_basis", "isolated yield", evidence)],
    ["The article describes highly selective elimination of the E isomer, leaving pure (Z)-2n; NOE support is said to be in the unavailable SI."],
    ["Exact TBAF amount, substrate amount, and workup are not stated on the covered page; the detailed procedure continues on page 7, which is outside the claimed coverage.", "The (Z) assignment was not independently checked because SI was not provided."],
))


# Scheme 3: four distinct transformations of 2a.
def scheme3_record(rid, product_id, product_label, product_name, product_smiles, reagents, conditions, hours, temperature, yield_value, unresolved=None):
    evidence = page_evidence(3)
    p2a = participant("reactant_2a", "reactant", "2a", "3-bromo-1-phenyl-3-buten-2-ol", evidence, "C=C(Br)C(O)Cc1ccccc1")
    product = participant(product_id, "product", product_label, product_name, evidence, product_smiles)
    parts = [p2a, product]
    for entity_id, role, label, name, smiles in reagents:
        parts.append(participant(entity_id, role, label, name, evidence, smiles))
    cond = [field("temperature", temperature, evidence), field("time", qty(hours, "h"), evidence)]
    cond.extend(field(name, value, evidence) for name, value in conditions)
    return record(
        rid, "reported_experiment", evidence, parts, cond,
        [field("isolated_yield", qty(yield_value, "%"), evidence, [product_id]), field("yield_measurement_basis", "isolated yield", evidence)],
        ["Independent product-derivatization arrow in Scheme 3."],
        (unresolved or []) + ["Exact quantities, full workup, and purification are not stated in Scheme 3 on the covered page; any detailed continuation outside page 6 was not imported."],
    )

records.append(scheme3_record(
    "scheme3_elimination_4a", "product_4a", "4a", "1-phenyl-3-butyn-2-ol", "C#CC(O)Cc1ccccc1",
    [("reagent_tbaf", "reagent", "TBAF", "tetrabutylammonium fluoride", None), ("solvent_dmf", "solvent", "DMF", "N,N-dimethylformamide", "CN(C)C=O")],
    [("solvent", "DMF")], 12, None, 58,
    ["Temperature is discrepant: Scheme 3 visibly reports 30 °C, while the detailed procedure beginning on page 6 says room temperature; both are retained in notes and the structured temperature is left missing."],
))
# Add the two source-specific temperature statements without collapsing the discrepancy.
for p in records[-1]["participants"]:
    if p["entity_id"] == "reactant_2a":
        p["amounts"] = [field("mass", qty(91.0, "mg"), page_evidence(6)), field("amount", qty(0.4, "mmol"), page_evidence(6))]
    elif p["entity_id"] == "reagent_tbaf":
        p["amounts"] = [field("volume", qty(1.2, "mL"), page_evidence(6)), field("concentration", qty(1.0, "M"), page_evidence(6)), field("amount", qty(1.2, "mmol"), page_evidence(6))]
    elif p["entity_id"] == "solvent_dmf":
        p["amounts"] = [field("volume", qty(4.0, "mL"), page_evidence(6))]
records[-1]["steps"][0]["conditions"].extend([
    field("scheme_temperature", qty(30, "°C"), page_evidence(3)),
    field("detailed_procedure_temperature", "r.t.", page_evidence(6)),
    field("operation", "TBAF was slowly added to the solution of 2a in DMF; completion was monitored by TLC", page_evidence(6)),
    field("workup", "diluted with diethyl ether (20 mL), quenched with saturated aqueous NH4Cl (5 mL), washed with water, and dried over anhydrous Na2SO4", page_evidence(6)),
    field("purification", "silica-gel chromatography (petroleum ether/ethyl acetate, 10:1)", page_evidence(6)),
])
records[-1]["evidence_ids"] = page_evidence(3, 6)
for p in records[-1]["participants"]:
    for key in ("label", "name", "smiles"):
        if p[key]["value"] is not None:
            p[key]["evidence_ids"] = page_evidence(3, 6)
records[-1]["outcomes"][0]["fact"]["evidence_ids"] = page_evidence(3, 6)
records[-1]["outcomes"].append(field("isolated_product_mass", qty(33.9, "mg"), page_evidence(6), ["product_4a"]))
records[-1]["notes"] = [fact("Scheme 3 reports 30 °C; the page-6 detailed procedure reports room temperature for the same 12 h, 58% conversion to 4a.", page_evidence(3, 6))]

records.append(scheme3_record(
    "scheme3_sonogashira_5a", "product_5a", "5a", "3-methylene-1,5-diphenyl-4-pentyn-2-ol", "C=C(C#Cc1ccccc1)C(O)Cc2ccccc2",
    [("ethynylbenzene", "reactant", "PhCCH", "ethynylbenzene", "C#Cc1ccccc1"), ("pd_catalyst", "catalyst", "PdCl2(PPh3)2", "bis(triphenylphosphine)palladium(II) dichloride", None), ("cui", "catalyst", "CuI", "copper(I) iodide", "[Cu]I"), ("nbutylamine", "reagent", "nBuNH2", "n-butylamine", "CCCCN"), ("benzene", "solvent", "benzene", "benzene", "c1ccccc1")],
    [("solvent", "benzene")], 14, "r.t.", 92,
))

records.append(scheme3_record(
    "scheme3_suzuki_6a", "product_6a", "6a", "1,3-diphenyl-3-buten-2-ol", "C=C(c1ccccc1)C(O)Cc2ccccc2",
    [("phenylboronic_acid", "reactant", "PhB(OH)2", "phenylboronic acid", "OB(O)c1ccccc1"), ("palladium_acetate", "catalyst", "Pd(OAc)2", "palladium(II) acetate", "CC(=O)O[Pd]OC(C)=O"), ("triphenylphosphine", "reagent", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c2ccccc2)c3ccccc3"), ("potassium_phosphate", "reagent", "K3PO4", "tripotassium phosphate", "[K+].[K+].[K+].[O-]P([O-])([O-])=O"), ("dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1")],
    [("solvent", "1,4-dioxane")], 48, qty(110, "°C"), 70,
))

records.append(scheme3_record(
    "scheme3_suzuki_7a", "product_7a", "7a", "3-styryl-1-phenyl-3-buten-2-ol", "C=C(/C=C/c1ccccc1)C(O)Cc2ccccc2",
    [("styrylboronic_acid", "reactant", "styryl-B(OH)2", "styrylboronic acid", "OB(O)/C=C/c1ccccc1"), ("palladium_acetate", "catalyst", "Pd(OAc)2", "palladium(II) acetate", "CC(=O)O[Pd]OC(C)=O"), ("triphenylphosphine", "reagent", "PPh3", "triphenylphosphine", "P(c1ccccc1)(c2ccccc2)c3ccccc3"), ("potassium_phosphate", "reagent", "K3PO4", "tripotassium phosphate", "[K+].[K+].[K+].[O-]P([O-])([O-])=O"), ("water", "solvent", "H2O", "water", "O"), ("dioxane", "solvent", "1,4-dioxane", "1,4-dioxane", "O1CCOCC1")],
    [("solvent", "1,4-dioxane/H2O")], 6, qty(110, "°C"), 56,
))


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstract, and introduction", "finding": "Article identity and broad bromohydroxylation claim inspected. Prior chlorination, HBr-addition, and sulfenyl-chloride examples are cited literature, not experiments from this paper, and were not converted into current-study records.", "evidence_ids": page_evidence(1)},
                {"region": "right-column Results and Discussion", "finding": "Narrative cross-checks Table 1 entries 1, 9, 10, and 11 and identifies the adopted NBS/dioxane-water room-temperature conditions; these statements were linked to the corresponding table-row records rather than duplicated.", "evidence_ids": page_evidence(1)},
            ],
            "record_ids": [f"{DOC}:table1_entry{x}" for x in (1, 9, 10, 11)],
            "unresolved": ["No reaction drawings occur on page 1; exact row data are on page 2.", "The article mentions Supporting Information, but no SI file was provided or associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper half, Table 1 including header reaction and footnotes", "finding": "All 11 optimization rows were extracted independently, including entry 3 table dashes, product ratios, starting-material recovery, NMR basis, the 0.3 mmol default scale, and the entry-5 0.6 mmol override.", "evidence_ids": page_evidence(2)},
                {"region": "middle, Table 2 including generic structures and footnote", "finding": "All 11 Table 2 substrate-scope rows were extracted independently with time, combined NMR yield, 2/3 ratio, and product-specific isolated yields.", "evidence_ids": page_evidence(2)},
                {"region": "lower-right Scheme 1", "finding": "The 1l and 1m bromohydroxylation arrows were extracted as two additional substrate-scope experiments and reconciled with their detailed page-6 batches.", "evidence_ids": page_evidence(2)},
                {"region": "lower-left and lower-right discussion", "finding": "Selectivity interpretation and chromatography comments were used as context; the allyl substituent statement concerns chemoselectivity within Table 2 entry 11, not a separate failed experiment.", "evidence_ids": page_evidence(2)},
            ],
            "record_ids": [f"{DOC}:table1_entry{x}" for x in range(1, 12)] + [f"{DOC}:table2_entry{x}_{letter}" for x, letter in enumerate("abcdefghijk", 1)] + [f"{DOC}:scheme1_scope_1l", f"{DOC}:scheme1_scope_1m"],
            "unresolved": ["Generic Table 2 drawings and machine-derived candidate SMILES remain structure-unverified.", "No exact solvent volumes or workup are given for the optimization rows."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "top, Scheme 2 first arrow", "finding": "1n bromohydroxylation was extracted and merged with the page-6 detailed batch: 2n 21% as a Z/E 60:40 mixture and 3n 45%.", "evidence_ids": page_evidence(3)},
                {"region": "top, Scheme 2 second arrow", "finding": "The TBAF/DMF treatment of 2n was extracted as a distinct experiment giving 4n (6%) and recovered/enriched (Z)-2n (51%).", "evidence_ids": page_evidence(3)},
                {"region": "middle-left, Scheme 3", "finding": "Four independent 2a derivatization arrows were extracted: TBAF elimination to 4a, Sonogashira coupling to 5a, and two Suzuki couplings to 6a and 7a.", "evidence_ids": page_evidence(3)},
                {"region": "right-column Experimental Section", "finding": "The 10 mmol typical 1a/NBS batch, workup, NMR result, and product-specific isolated masses/yields were merged into Table 2 entry 1 rather than duplicated.", "evidence_ids": page_evidence(3)},
            ],
            "record_ids": [f"{DOC}:scheme2_scope_1n", f"{DOC}:scheme2_tbaf_2n", f"{DOC}:scheme3_elimination_4a", f"{DOC}:scheme3_sonogashira_5a", f"{DOC}:scheme3_suzuki_6a", f"{DOC}:scheme3_suzuki_7a", f"{DOC}:table2_entry1_a"],
            "unresolved": ["Scheme 3 reports 30 °C for the 4a elimination, whereas the page-6 detailed procedure says room temperature.", "NOE-based stereochemical assignments refer to unavailable SI and remain unverified."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation", "finding": "Only characterization of (Z)-3a continues from page 3; it was associated with the existing 1a batch and was not treated as a new reaction.", "evidence_ids": page_evidence(4)},
                {"region": "left and right columns, detailed preparations 1b-1f", "finding": "Detailed quantities, times, product masses, isolated yields, ratios, and chromatography eluents for Table 2 entries 2-6 were merged into their respective scope records; 1f characterization continues on page 5.", "evidence_ids": page_evidence(4)},
            ],
            "record_ids": [f"{DOC}:table2_entry1_a"] + [f"{DOC}:table2_entry{x}_{letter}" for x, letter in zip(range(2, 7), "bcdef")],
            "unresolved": ["The phrase 'prepared according to this procedure' imports the typical workflow conceptually, but operation-specific volumes not restated for each batch were not fabricated.", "Stereochemical structures remain machine candidates."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation", "finding": "Characterization of 2f and (Z)-3f continues; it supports the existing entry-6 batch and is not a new experiment.", "evidence_ids": page_evidence(5)},
                {"region": "detailed preparations 1g-1j", "finding": "Exact reactant/NBS quantities, solvent volumes, times, isolated masses/yields, regioisomer ratios, and purification descriptions for Table 2 entries 7-10 were merged into those four records; 2j characterization continues on page 6.", "evidence_ids": page_evidence(5)},
            ],
            "record_ids": [f"{DOC}:table2_entry6_f"] + [f"{DOC}:table2_entry{x}_{letter}" for x, letter in zip(range(7, 11), "ghij")],
            "unresolved": ["No separate experiment is created for analytical characterization blocks.", "NOE and full spectral verification were not possible without SI."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper-left continuation", "finding": "Analytical data for 2j/(E)-3j continue from page 5 and remain linked to Table 2 entry 10.", "evidence_ids": page_evidence(6)},
                {"region": "left column, detailed 1k and 1l preparations", "finding": "The 1k Table 2 batch and 1l Scheme 1 batch were extracted with reported quantities, times, masses, yields, ratios where given, and chromatography.", "evidence_ids": page_evidence(6)},
                {"region": "right column, detailed 1m and 1n preparations", "finding": "The 1m Scheme 1 and 1n Scheme 2 batches were extracted and reconciled with their graphical arrows.", "evidence_ids": page_evidence(6)},
                {"region": "bottom-right, beginning of 4a elimination procedure", "finding": "Visible quantities and 12 h room-temperature statement for TBAF elimination of 2a were linked to Scheme 3; the 58% outcome is shown in Scheme 3, while the paragraph continues onto page 7 outside the claimed range.", "evidence_ids": page_evidence(6)},
            ],
            "record_ids": [f"{DOC}:table2_entry10_j", f"{DOC}:table2_entry11_k", f"{DOC}:scheme1_scope_1l", f"{DOC}:scheme1_scope_1m", f"{DOC}:scheme2_scope_1n", f"{DOC}:scheme3_elimination_4a"],
            "unresolved": ["The source reports 15.1 mg and 2.0 mmol for 1k, an internal quantity inconsistency preserved verbatim.", "The 4a procedure continues on page 7; details beyond the visible page-6 portion were not used as covered evidence.", "Scheme 3/page-6 temperature discrepancy remains unresolved."],
        },
    ],
}


assert len(records) == 30, len(records)
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
coverage_path = CURRENT / "coverage" / "pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "records_path": str(OUT / 'records_pages_0001_0006.json'), "coverage_path": str(coverage_path)}, ensure_ascii=False))
