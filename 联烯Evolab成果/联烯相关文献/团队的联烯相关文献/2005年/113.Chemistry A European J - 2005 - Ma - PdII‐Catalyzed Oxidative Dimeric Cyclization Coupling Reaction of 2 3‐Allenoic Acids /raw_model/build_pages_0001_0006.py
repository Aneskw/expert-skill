#!/usr/bin/env python3
"""Build source-derived, unreviewed records for PDF pages 1--6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_88e84ce1468bbb92"


def ev(page: int, kind: str = "text") -> str:
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    ids = list(dict.fromkeys(evidence))
    return {"value": value, "evidence_ids": ids, "verification": "missing" if value is None else "unreviewed"}


def fld(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def qty(number, unit, raw_text=None, qualifier=None):
    result = {"number": number, "unit": unit}
    if raw_text is not None:
        result["raw_text"] = raw_text
    if qualifier is not None:
        result["qualifier"] = qualifier
    return result


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name is not None else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, source_id, kind, evidence, participants=None, steps=None, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": notes or [],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


SMILES = {
    "1a": "O=C(O)C(CCC)=C=Cc1ccccc1",
    "1b": "O=C(O)C(C)=C=Cc1ccccc1",
    "1c": "O=C(O)C(Cc1ccccc1)=C=Cc1ccccc1",
    "1d": "O=C(O)C(C)=C=Cc1cccc2ccccc12",
    "1e": "O=C(O)C(CCC)=C=Cc1cccc2ccccc12",
    "1f": "O=C(O)C(Cc1ccccc1)=C=CC",
    "1g": "O=C(O)C(C)=C=CCCCCCC",
    "1h": "O=C(O)C(C)=C=CC",
    "1i": "O=C(O)C(CCC)=C=CCCC",
    "1j": "O=C(O)C=C=CCCCCC",
    "1k": "O=C(O)C=C=CCCCCCCC",
    "1l": "O=C(O)C=C=CCCCCCCCC",
    "1m": "O=C(O)C(Cc1ccccc1)=C=C",
    "1n": "O=C(O)C=C=C",
    "1o": "O=C(O)C(CCC)=C=Cc1ccc(Br)cc1",
    "PdCl2": "[Cl-].[Cl-].[Pd+2]",
    "propyl iodide": "CCCI",
    "benzoquinone": "O=C1C=CC(=O)C=C1",
    "KI": "[K+].[I-]",
    "NaI": "[Na+].[I-]",
    "TBAI": "CCCC[N+](CCCC)(CCCC)CCCC.[I-]",
    "DMA": "CC(=O)N(C)C",
    "DMF": "CN(C)C=O",
    "THF": "C1CCOC1",
    "MeCN": "CC#N",
    "EtOH": "CCO",
}


SUBSTRATES = {
    "1a": "4-phenyl-2-propyl-2,3-butadienoic acid",
    "1b": "2-methyl-4-phenyl-2,3-butadienoic acid",
    "1c": "2-benzyl-4-phenyl-2,3-butadienoic acid",
    "1d": "2-methyl-4-(alpha-naphthyl)-2,3-butadienoic acid",
    "1e": "4-(alpha-naphthyl)-2-propyl-2,3-butadienoic acid",
    "1f": "2-benzylpenta-2,3-dienoic acid",
    "1g": "2-methyldeca-2,3-dienoic acid",
    "1h": "2-methylpenta-2,3-dienoic acid",
    "1i": "2-propylhepta-2,3-dienoic acid",
    "1j": "nona-2,3-dienoic acid",
    "1k": "undeca-2,3-dienoic acid",
    "1l": "dodeca-2,3-dienoic acid",
    "1m": "2-benzylbuta-2,3-dienoic acid",
    "1n": "buta-2,3-dienoic acid",
    "1o": "4-(4-bromophenyl)-2-propyl-2,3-butadienoic acid",
}


R_GROUPS = {
    "3a": ("c2ccccc2", "CCC"),
    "3b": ("c2ccccc2", "C"),
    "3c": ("c2ccccc2", "Cc2ccccc2"),
    "3d": ("c2cccc3ccccc23", "C"),
    "3e": ("c2cccc3ccccc23", "CCC"),
    "3f": ("C", "Cc2ccccc2"),
    "3g": ("CCCCCC", "C"),
    "3h": ("C", "C"),
    "3i": ("CCC", "CCC"),
    "3j": ("CCCCC", ""),
    "3k": ("CCCCCCC", ""),
    "3l": ("CCCCCCCC", ""),
    "3m": ("", "Cc2ccccc2"),
    "3n": ("", ""),
    "3o": ("c2ccc(Br)cc2", "CCC"),
}


PRODUCT_NAMES = {
    "3a": "3,3'-dipropyl-5,5'-diphenyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3b": "3,3'-dimethyl-5,5'-diphenyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3c": "3,3'-dibenzyl-5,5'-diphenyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3d": "3,3'-dimethyl-5,5'-di(alpha-naphthyl)-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3e": "3,3'-dipropyl-5,5'-di(alpha-naphthyl)-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3f": "3,3'-dibenzyl-5,5'-dimethyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3g": "3,3'-dimethyl-5,5'-dihexyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3h": "3,3',5,5'-tetramethyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3i": "3,3',5,5'-tetrapropyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3j": "5,5'-dipentyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3k": "5,5'-diheptyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3l": "5,5'-dioctyl-5H,5'H-[4,4']bifuranyl-2,2'-dione",
    "3m": "expected bibutenolide 3m",
    "3n": "expected bibutenolide 3n",
    "3o": "3,3'-dipropyl-5,5'-di(4-bromophenyl)-5H,5'H-[4,4']bifuranyl-2,2'-dione",
}


def product_smiles(label):
    r1, r2 = R_GROUPS[label]
    if not r1:
        return None
    if r2:
        return f"O=C1OC({r1})C(=C1{r2})-C4=C({r2})C(=O)OC4{r1}"
    return f"O=C1OC({r1})C(=C1)-C4=CC(=O)OC4{r1}"


def amounts(evidence, **values):
    fields = []
    for name, value in values.items():
        if value is not None:
            fields.append(fld(name, value, evidence))
    return fields


records = []

# Page 1: cited prior-work concept, not a current-paper experiment.
p1 = [ev(1, "image"), ev(1)]
records.append(record(
    "page1_scheme1_prior_work", "Scheme 1", "literature_example", p1,
    participants=[
        participant("scheme1_allene_a", "reactant", "functionalized allene A", "generic functionalized allene", None, p1),
        participant("scheme1_allene_b", "reactant", "functionalized allene B", "generic functionalized allene", None, p1),
        participant("scheme1_bicycle", "product", "Scheme 1 bicyclic product", "generic bicyclic coupling product", None, p1),
    ],
    notes=[fact("Prior transition-metal-catalyzed oxidative cyclization-dimerization work cited as reference 9; R/FG groups are generic.", p1)],
    unresolved=["Generic R/FG structures are not fully specified; SMILES are intentionally null.", "This is cited prior work, not a reported experiment of the current paper."],
))

# Page 2, Table 1: ten independent optimization rows.
table1 = [
    (1, "propyl iodide", 5, "DMA", {"number": 80, "unit": "°C"}, 10, 74),
    (2, "propyl iodide", 3, "DMA", {"number": 80, "unit": "°C"}, 6.5, 62),
    (3, "propyl iodide", 5, "THF", "reflux", 46, "trace"),
    (4, "propyl iodide", 5, "MeCN", "reflux", 16, 66),
    (5, "propyl iodide", 5, "EtOH", "reflux", 10, 42),
    (6, "TBAI", 1, "DMA", {"number": 80, "unit": "°C"}, 5, 62),
    (7, "NaI", 0.5, "DMA", {"number": 80, "unit": "°C"}, 5, 68),
    (8, "KI", 0.5, "DMA", {"number": 80, "unit": "°C"}, 5, 74),
    (9, "KI", 0.2, "DMA", {"number": 80, "unit": "°C"}, 5, 64),
    (10, "benzoquinone", 0.63, "DMF", {"number": 80, "unit": "°C"}, 2, 92),
]
p2 = [ev(2, "image"), ev(2)]
for entry, additive, equiv, solvent, temp, hours, yld in table1:
    substrate = participant("substrate_1a", "reactant", "1a", SUBSTRATES["1a"], SMILES["1a"], p2,
                              amounts(p2, reaction_scale=qty(0.25, "mmol")))
    add = participant("additive", "reagent", "2a" if additive == "propyl iodide" else additive, additive,
                      SMILES.get(additive), p2, amounts(p2, equivalents=qty(equiv, "equiv")))
    catalyst = participant("catalyst", "catalyst", "PdCl2", "palladium(II) chloride", SMILES["PdCl2"], p2,
                           amounts(p2, catalyst_loading=qty(5, "mol%")))
    solv = participant("solvent", "solvent", solvent, solvent, SMILES.get(solvent), p2)
    product = participant("product_3a", "product", "3a", PRODUCT_NAMES["3a"], product_smiles("3a"), p2)
    records.append(record(
        f"table1_entry_{entry:02d}", f"Table 1 entry {entry}", "optimization_entry", p2,
        participants=[substrate, add, catalyst, solv, product],
        steps=[{"step_id": "reaction", "participant_ids": ["substrate_1a", "additive", "catalyst", "solvent"], "conditions": [
            fld("solvent", solvent, p2), fld("temperature", temp, p2), fld("time", qty(hours, "h"), p2), fld("atmosphere", "air", p2)
        ]}],
        outcomes=[fld("isolated_yield", qty(yld, "%") if isinstance(yld, (int, float)) else yld, p2, ["product_3a"]),
                  fld("yield_measurement_basis", "isolated", p2, ["product_3a"])],
        notes=[fact(f"Optimization row {entry}; Table 1 footnote states all rows used 0.25 mmol of allenoic acid.", p2)],
        unresolved=["Supporting information was mentioned by the article but was not supplied or explicitly associated.", "Candidate molecular structures remain unverified."],
    ))

# Page 2: three mechanistic/control experiments, each a distinct arrow.
def add_control(suffix, source, atmosphere, time_h, additive_label, product_yield, recovery=None, second_product=None):
    parts = [
        participant("substrate_1a", "reactant", "1a", SUBSTRATES["1a"], SMILES["1a"], p2),
        participant("additive", "reagent", additive_label, additive_label if additive_label not in ("2b", "2c") else f"alkyl iodide {additive_label}",
                    SMILES.get("propyl iodide") if additive_label == "n-C3H7I" else None, p2,
                    amounts(p2, equivalents=qty(5, "equiv")) if suffix == "eq1_argon" else None),
        participant("catalyst", "catalyst", "PdCl2", "palladium(II) chloride", SMILES["PdCl2"], p2,
                    amounts(p2, catalyst_loading=qty(5, "mol%"))),
        participant("solvent", "solvent", "DMA", "N,N-dimethylacetamide", SMILES["DMA"], p2),
        participant("product_3a", "product", "3a", PRODUCT_NAMES["3a"], product_smiles("3a"), p2),
    ]
    outcomes = [fld("yield", qty(product_yield, "%"), p2, ["product_3a"])]
    if second_product:
        parts.append(participant("product_4a", "product", "4a", "cycloisomerization product 4a", None, p2))
        outcomes.append(fld("yield", qty(second_product, "%"), p2, ["product_4a"]))
    if recovery is not None:
        outcomes.append(fld("additive_recovery", qty(recovery, "%"), p2, ["additive"]))
    records.append(record(
        suffix, source, "reported_experiment", p2, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts if p["role"] not in ("product",)], "conditions": [
            fld("solvent", "DMA", p2), fld("temperature", qty(80, "°C"), p2), fld("time", qty(time_h, "h"), p2), fld("atmosphere", atmosphere, p2)
        ]}], outcomes,
        notes=[fact("No alkyl-iodide-derived product was detected in the crude reaction mixture." if recovery is not None else "Control experiment used an argon atmosphere.", p2)],
        unresolved=["Yield measurement basis and workup are not stated for this arrow.", "Alkyl iodide structure is retained by label only where the drawing was not converted to a verified SMILES.", "Supporting information was not provided."],
    ))


add_control("eq1_argon", "Equation 1", "argon", 4, "n-C3H7I", 26, second_product=12)
add_control("eq2_iodide_2b", "Equation 2", "air", 4.5, "2b", 72, recovery=94)
add_control("eq3_iodide_2c", "Equation 3", "air", 4, "2c", 56, recovery=95)


# Table 2 substrate-scope rows. Page 4 supplies the shared method definitions.
table2_rows = [
    (1,"1a","A",10,74,"1:1.87"),(2,"1a","B",5,75,"1:2.18"),(3,"1a","C",2,92,"1:1.65"),
    (4,"1b","A",4,64,"1:1.62"),(5,"1b","B",4,74,"1:1.66"),(6,"1b","C",2,96,"1:2.03"),
    (7,"1c","A",11.5,75,"1:1.53"),(8,"1c","B",11.5,"mixture",None),(9,"1c","C",2,94,"0.9:1"),
    (10,"1d","A",4,71,"1:1.28"),(11,"1d","C",2,92,"1:1.84"),
    (12,"1e","A",4.5,64,"1:1.43"),(13,"1e","B",6,65,"1:1.54"),(14,"1e","C",2,67,"1:1.33"),
    (15,"1f","A",3.5,72,"1.04:1"),(16,"1f","B",5,15,None),(17,"1f","C",2,36,None),
    (18,"1g","A",21,47,"1:1.87"),(19,"1g","B",17,11,"1.23:1"),(20,"1g","C",3.5,13,"1:1.84"),(21,"1g","D",2,"cycloisomerization_62",None),
    (22,"1h","A",20,43,"1:1.13"),(23,"1h","B",22.5,"mixture",None),(24,"1h","C",2,22,"1:2"),(25,"1h","D",11,20,"1:1.62"),
    (26,"1i","A",17,61,"1:1.59"),(27,"1i","B",2.5,25,"1:1.02"),(28,"1i","C",2,"cycloisomerization_8",None),(29,"1i","D",2.5,"mixture",None),
    (30,"1j","A",3,52,"1:1.67"),(31,"1j","B",15,"mixture",None),(32,"1j","C",2,46,"1:1.06"),(33,"1j","D",2,61,"1.19:1"),
    (34,"1k","A",6,49,"1:1"),(35,"1k","B",21,"mixture",None),(36,"1k","C",2,80,"1.06:1"),(37,"1k","D",2,83,"1:1.05"),
    (38,"1l","A",3,54,"1:1"),(39,"1l","B",2,32,"1:1.38"),(40,"1l","C",2,71,"1:1.06"),(41,"1l","D",2,73,"1:1.06"),
    (42,"1m","A",10.5,"mixture",None),(43,"1n","C",2,"NR",None),
]

sub_to_product = {f"1{x}": f"3{x}" for x in "abcdefghijklmno"}

# Exact examples override shared nominal quantities and add product masses.
detail = {
    18:(4,{"substrate_mass":qty(92,"mg"),"substrate_amount":qty(.51,"mmol"),"reagent_mass":qty(428,"mg"),"reagent_amount":qty(2.50,"mmol"),"catalyst_mass":qty(5,"mg"),"catalyst_amount":qty(.028,"mmol"),"solvent_volume":qty(5,"mL"),"product_mass":qty(43,"mg")}),
    19:(4,{"substrate_mass":qty(91,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(42,"mg"),"reagent_amount":qty(.25,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(3,"mL"),"product_mass":qty(10,"mg")}),
    20:(4,{"substrate_mass":qty(92,"mg"),"substrate_amount":qty(.51,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.30,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(12,"mg")}),
    22:(4,{"substrate_mass":qty(56,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(420,"mg"),"reagent_amount":qty(2.47,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(24,"mg")}),
    24:(4,{"substrate_mass":qty(56,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.30,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(12,"mg")}),
    25:(4,{"substrate_mass":qty(56,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.30,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(11,"mg")}),
    26:(5,{"substrate_mass":qty(84,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(425,"mg"),"reagent_amount":qty(2.50,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(51,"mg")}),
    27:(5,{"substrate_mass":qty(85,"mg"),"substrate_amount":qty(.51,"mmol"),"reagent_mass":qty(42,"mg"),"reagent_amount":qty(.25,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(21,"mg")}),
    30:(5,{"substrate_mass":qty(77,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(430,"mg"),"reagent_amount":qty(2.53,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(40,"mg")}),
    32:(5,{"substrate_mass":qty(78,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.30,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(35,"mg")}),
    33:(5,{"substrate_mass":qty(76,"mg"),"substrate_amount":qty(.49,"mmol"),"reagent_mass":qty(33,"mg"),"reagent_amount":qty(.31,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(46,"mg")}),
    34:(5,{"substrate_mass":qty(94,"mg"),"substrate_amount":qty(.52,"mmol"),"reagent_mass":qty(425,"mg"),"reagent_amount":qty(2.50,"mmol"),"catalyst_mass":qty(5,"mg"),"catalyst_amount":qty(.028,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(46,"mg")}),
    36:(5,{"substrate_mass":qty(91,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.15,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(72,"mg")}),
    37:(5,{"substrate_mass":qty(47,"mg"),"substrate_amount":qty(.26,"mmol"),"reagent_mass":qty(16,"mg"),"reagent_amount":qty(.15,"mmol"),"catalyst_mass":qty(2,"mg"),"catalyst_amount":qty(.011,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(39,"mg")}),
    38:(5,{"substrate_mass":qty(97,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(425,"mg"),"reagent_amount":qty(2.50,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(52,"mg")}),
    39:(5,{"substrate_mass":qty(97,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(44,"mg"),"reagent_amount":qty(.27,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(31,"mg")}),
    40:(5,{"substrate_mass":qty(97,"mg"),"substrate_amount":qty(.50,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.30,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(68,"mg")}),
    41:(5,{"substrate_mass":qty(96,"mg"),"substrate_amount":qty(.49,"mmol"),"reagent_mass":qty(32,"mg"),"reagent_amount":qty(.30,"mmol"),"catalyst_mass":qty(4,"mg"),"catalyst_amount":qty(.023,"mmol"),"solvent_volume":qty(2,"mL"),"product_mass":qty(70,"mg")}),
}


def method_components(method, evidence, exact=None):
    exact = exact or {}
    if method == "A":
        reagent_label, reagent_name, reagent_smiles, solvent = "2a", "propyl iodide", SMILES["propyl iodide"], "DMA"
        nominal = {"reagent_amount": qty(2.50,"mmol")}
        atmosphere = "air"
    elif method == "B":
        reagent_label, reagent_name, reagent_smiles, solvent = "KI", "potassium iodide", SMILES["KI"], "DMA"
        nominal = {"reagent_mass": qty(42,"mg"), "reagent_amount": qty(.25,"mmol")}
        atmosphere = "air"
    elif method == "C":
        reagent_label, reagent_name, reagent_smiles, solvent = "BQ", "benzoquinone", SMILES["benzoquinone"], "DMF"
        nominal = {"reagent_amount": qty(.30,"mmol")}
        atmosphere = None
    else:
        reagent_label, reagent_name, reagent_smiles, solvent = "BQ", "benzoquinone", SMILES["benzoquinone"], "DMA"
        nominal = {"reagent_amount": qty(.30,"mmol")}
        atmosphere = None
    vals = {"substrate_amount":qty(.50,"mmol"), **nominal, "catalyst_mass":qty(4,"mg"), "catalyst_amount":qty(.023,"mmol"), "solvent_volume":qty(2,"mL")}
    vals.update(exact)
    return reagent_label, reagent_name, reagent_smiles, solvent, atmosphere, vals


for entry, substrate_label, method, hours, result, dr in table2_rows:
    page_extra, exact = detail.get(entry, (None, {}))
    evidence = [ev(3,"image"),ev(3),ev(4,"image"),ev(4)]
    detail_ev = [ev(page_extra,"image"),ev(page_extra)] if page_extra else []
    evidence += detail_ev
    product_label = sub_to_product[substrate_label]
    reagent_label, reagent_name, reagent_smiles, solvent, atmosphere, vals = method_components(method, evidence, exact)
    sub_ev = detail_ev or [ev(3,"image"),ev(3)]
    substrate_amounts = amounts(sub_ev, reaction_scale=vals.get("substrate_amount"), mass=vals.get("substrate_mass"))
    reagent_amounts = amounts(detail_ev or [ev(4,"image"),ev(4)], mass=vals.get("reagent_mass"), amount=vals.get("reagent_amount"))
    catalyst_amounts = amounts(detail_ev or [ev(4,"image"),ev(4)], mass=vals.get("catalyst_mass"), amount=vals.get("catalyst_amount"))
    solvent_amounts = amounts(detail_ev or [ev(4,"image"),ev(4)], volume=vals.get("solvent_volume"))
    parts = [
        participant("substrate", "reactant", substrate_label, SUBSTRATES[substrate_label], SMILES[substrate_label], [ev(3,"image"),ev(3)], substrate_amounts),
        participant("oxidant_additive", "reagent", reagent_label, reagent_name, reagent_smiles, [ev(4,"image"),ev(4)], reagent_amounts),
        participant("catalyst", "catalyst", "PdCl2", "palladium(II) chloride", SMILES["PdCl2"], [ev(4,"image"),ev(4)], catalyst_amounts),
        participant("solvent", "solvent", solvent, solvent, SMILES[solvent], [ev(4,"image"),ev(4)], solvent_amounts),
        participant("target_product", "product", product_label, PRODUCT_NAMES[product_label], product_smiles(product_label), [ev(3,"image"),ev(3)]),
    ]
    outcomes = []
    notes = [fact(f"Table 2 entry {entry}; method {method}.", [ev(3,"image"),ev(3)])]
    if isinstance(result, (int, float)):
        outcomes.append(fld("yield", qty(result,"%"), [ev(3,"image"),ev(3)] + detail_ev, ["target_product"]))
        if vals.get("product_mass"):
            outcomes.append(fld("isolated_product_mass", vals["product_mass"], detail_ev, ["target_product"]))
    elif result.startswith("cycloisomerization_"):
        yld = int(result.rsplit("_",1)[1])
        parts.append(participant("cycloisomerization_product", "product", "cycloisomerization product", "cycloisomerization product", None, [ev(3,"image"),ev(3)]))
        outcomes.append(fld("isolated_yield", qty(yld,"%"), [ev(3,"image"),ev(3)], ["cycloisomerization_product"]))
        outcomes.append(fld("reaction_result", "cycloisomerization rather than target dimer", [ev(3,"image"),ev(3)], ["cycloisomerization_product"]))
    elif result == "mixture":
        outcomes.append(fld("reaction_result", "mixture", [ev(3,"image"),ev(3)], ["target_product"]))
    else:
        outcomes.append(fld("reaction_result", "NR", [ev(3,"image"),ev(3)], ["target_product"]))
    if dr:
        outcomes.append(fld("diastereomer_ratio_RstarSstar_to_RstarRstar", dr, [ev(3,"image"),ev(3)] + detail_ev, ["target_product"]))
    if entry == 38:
        parts.append(participant("side_product", "product", "5-octyl-5H-furan-2-one", "5-octyl-5H-furan-2-one", "O=C1OC(CCCCCCCC)C=C1", detail_ev))
        outcomes.append(fld("side_product_yield", qty(5,"%"), detail_ev, ["side_product"]))
        outcomes.append(fld("side_product_mass", qty(5,"mg"), detail_ev, ["side_product"]))
    condition_evidence = [ev(3,"image"),ev(3),ev(4,"image"),ev(4)]
    conditions = [fld("solvent", solvent, condition_evidence), fld("temperature", qty(80,"°C"), condition_evidence), fld("time", qty(hours,"h"), [ev(3,"image"),ev(3)] + detail_ev)]
    if atmosphere:
        conditions.append(fld("atmosphere", atmosphere, [ev(4,"image"),ev(4)]))
    if method == "A":
        conditions += [
            fld("workup", "diluted with diethyl ether, washed with water, dried over MgSO4, then evaporated", [ev(4,"image"),ev(4)]),
            fld("purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate eluent", [ev(4,"image"),ev(4)]),
        ]
    unresolved = ["Supporting information was not supplied or explicitly associated.", "All molecular structures are candidates and remain unverified."]
    if method in ("B","C","D"):
        unresolved.append("Workup and purification are not explicitly restated for this method in the supplied main text.")
    if atmosphere is None:
        unresolved.append("Atmosphere is not stated for this method.")
    if result in ("mixture","NR"):
        unresolved.append("No product identity/yield was reported beyond the qualitative table result.")
    if result.startswith("cycloisomerization_") if isinstance(result,str) else False:
        unresolved.append("The cycloisomerization product structure/label is not specified in the table footnote.")
    if entry == 36:
        unresolved.append("The detailed procedure prints 32 mg benzoquinone as 0.15 mmol; both printed values are preserved without correction despite their apparent inconsistency.")
    records.append(record(
        f"table2_entry_{entry:02d}", f"Table 2 entry {entry}", "substrate_scope_entry", evidence, parts,
        [{"step_id":"reaction","participant_ids":["substrate","oxidant_additive","catalyst","solvent"],"conditions":conditions}],
        outcomes, notes, unresolved,
    ))


# Table 3 and its detailed procedures on pages 5--6.
table3 = [
    (1,"1a","R-(-)",97,.63,"3a","R,R-(-)",88,">99",">99:1",5,qty(50,"mg"),qty(.248,"mmol"),qty(17,"mg"),qty(.157,"mmol"),qty(2,"mg"),qty(.011,"mmol"),qty(2,"mL"),qty(44,"mg")),
    (2,"1b","R-(-)",99,.58,"3b","R,R-(-)",100,"99","25:1",6,qty(44,"mg"),qty(.253,"mmol"),qty(16,"mg"),qty(.148,"mmol"),qty(2,"mg"),qty(.011,"mmol"),qty(2,"mL"),qty(44,"mg")),
    (3,"1d","S-(+)",98,.74,"3d","S,S-(+)",86,">99","20:1",6,qty(56,"mg"),qty(.25,"mmol"),qty(20,"mg"),qty(.189,"mmol"),qty(2,"mg"),qty(.011,"mmol"),qty(2,"mL"),qty(48,"mg")),
    (4,"1o","S-(+)",99,.67,"3o","S,S-(+)",94,"98","24:1",6,qty(35,"mg"),qty(.125,"mmol"),qty(9,"mg"),qty(.083,"mmol"),qty(1,"mg"),qty(.006,"mmol"),qty(1,"mL"),qty(33,"mg")),
]

for entry, sublab, subprefix, subee, bqeq, prodlab, prodprefix, yld, prodee, dr, detail_page, smass, samount, bmass, bamount, cmass, camount, svol, pmass in table3:
    evidence = [ev(4,"image"),ev(4),ev(detail_page,"image"),ev(detail_page)]
    if entry == 1:
        evidence += [ev(6,"image"),ev(6)]
    if entry == 4:
        evidence += [ev(2,"image"),ev(2)]
    sub = participant("substrate", "reactant", f"{subprefix}-{sublab}", f"{subprefix}-{SUBSTRATES[sublab]}", SMILES[sublab], evidence,
                      amounts(evidence, mass=smass, amount=samount, substrate_ee=qty(subee,"%")))
    bq = participant("benzoquinone", "reagent", "BQ", "benzoquinone", SMILES["benzoquinone"], evidence,
                     amounts(evidence, mass=bmass, amount=bamount, equivalents=qty(bqeq,"equiv")))
    catalyst = participant("catalyst", "catalyst", "PdCl2", "palladium(II) chloride", SMILES["PdCl2"], evidence,
                           amounts(evidence, mass=cmass, amount=camount, catalyst_loading=qty(5,"mol%")))
    solvent = participant("solvent", "solvent", "DMF", "N,N-dimethylformamide", SMILES["DMF"], evidence, amounts(evidence, volume=svol))
    product = participant("product", "product", f"{prodprefix}-{prodlab}", f"{prodprefix}-{PRODUCT_NAMES[prodlab]}", product_smiles(prodlab), evidence)
    eevalue = qty(int(prodee.replace(">","")), "%", raw_text=f"{prodee}%", qualifier="gt") if prodee.startswith(">") else qty(int(prodee), "%")
    outcomes = [
        fld("yield", qty(yld,"%"), evidence, ["product"]),
        fld("product_ee", eevalue, evidence, ["product"]),
        fld("diastereomer_ratio_RstarRstar_to_RstarSstar", dr, evidence, ["product"]),
        fld("isolated_product_mass", pmass, evidence, ["product"]),
    ]
    records.append(record(
        f"table3_entry_{entry:02d}", f"Table 3 entry {entry}", "substrate_scope_entry", evidence,
        [sub,bq,catalyst,solvent,product],
        [{"step_id":"reaction","participant_ids":["substrate","benzoquinone","catalyst","solvent"],"conditions":[
            fld("solvent","DMF",evidence),fld("temperature",qty(80,"°C"),evidence),fld("time",qty(2,"h"),evidence)
        ]}], outcomes,
        [fact("Diastereomer ratio was determined by 1H NMR; HPLC used an AD column at 0.7 mL min-1.", evidence)],
        ["Atmosphere, workup, and purification are not stated for Method C in the supplied main text.", "Axial/chiral stereochemistry is preserved in labels but not encoded in the non-stereochemical candidate SMILES.", "Supporting information was not supplied or explicitly associated."]
        + (["Table 3 gives 0.74 equiv BQ for entry 3, while the detailed procedure prints 0.189 mmol BQ for 0.25 mmol substrate; both source values are preserved without arithmetic correction."] if entry == 3 else []),
    ))


# Page 3 prose + page 4 Scheme 2: mechanism, not a reported experiment.
mech_ev = [ev(3,"image"),ev(3),ev(4,"image"),ev(4)]
records.append(record(
    "scheme2_proposed_mechanism", "Scheme 2", "mechanism", mech_ev,
    participants=[
        participant("substrate_1o", "reactant", "S-(+)-1o", f"S-(+)-{SUBSTRATES['1o']}", SMILES["1o"], mech_ev),
        participant("palladium_species", "catalyst", "PdII/Pd0", "palladium species", None, mech_ev),
        participant("intermediate_5o", "unspecified_agent", "5o", "oxypalladation intermediate 5o", None, mech_ev),
        participant("product_3o", "product", "(S,S)-(+)-3o", f"(S,S)-(+)-{PRODUCT_NAMES['3o']}", product_smiles("3o"), mech_ev),
        participant("oxidant", "reagent", "in-situ I2 or benzoquinone", "iodine or benzoquinone reoxidant", None, mech_ev),
    ],
    steps=[],
    notes=[fact("Proposed sequence: PdII coordination, double cyclic oxypalladation to 5o, reductive elimination to 3o and Pd0, then oxidation back to PdII.", mech_ev)],
    unresolved=["Scheme 2 is a proposed mechanism and is not an independently reported preparative experiment.", "Intermediate structures are not converted to verified SMILES."],
))


# Coverage ledger: exactly pages 1--6, every region cites that page's image.
all_ids = [r["record_id"] for r in records]
table2_ids = [f"{DOC}:table2_entry_{i:02d}" for i in range(1,44)]
table3_ids = [f"{DOC}:table3_entry_{i:02d}" for i in range(1,5)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page":1,"state":"attempted","regions":[
            {"region":"title, abstract, introduction, and lower-right Scheme 1","finding":"Article context plus a generic prior-literature oxidative cyclization-dimerization scheme; no current-paper experimental conditions on this page.","evidence_ids":[ev(1,"image")]},
        ],"record_ids":[f"{DOC}:page1_scheme1_prior_work"],"unresolved":["Scheme 1 contains generic R/FG groups and cannot support complete structures."]},
        {"page":2,"state":"attempted","regions":[
            {"region":"upper-left Table 1 and reaction scheme","finding":"Ten independent optimization entries for 1a to 3a, including reflux/trace and isolated-yield footnotes.","evidence_ids":[ev(2,"image")]},
            {"region":"lower-left Equation 1","finding":"Argon control giving 3a (26%) and 4a (12%).","evidence_ids":[ev(2,"image")]},
            {"region":"upper-right Equations 2 and 3","finding":"Two high-boiling alkyl-iodide recovery experiments, each retained as a separate reported experiment.","evidence_ids":[ev(2,"image")]},
            {"region":"lower-right Figure 1 and discussion","finding":"ORTEP/structure evidence for (S,S)-(+)-3o; linked to Table 3 entry 4, not treated as another reaction.","evidence_ids":[ev(2,"image")]},
        ],"record_ids":[f"{DOC}:table1_entry_{i:02d}" for i in range(1,11)]+[f"{DOC}:eq1_argon",f"{DOC}:eq2_iodide_2b",f"{DOC}:eq3_iodide_2c",f"{DOC}:table3_entry_04"],"unresolved":["Structures of alkyl iodides 2b and 2c were not converted to verified SMILES.","Yield bases for Equations 1--3 are not stated."]},
        {"page":3,"state":"attempted","regions":[
            {"region":"left-column Table 2, entries 1--43 and footnotes","finding":"Forty-three distinct substrate-scope rows, including mixtures, NR, and footnoted isolated cycloisomerization products.","evidence_ids":[ev(3,"image")]},
            {"region":"upper-right mechanistic discussion","finding":"Proposed catalytic cycle text supporting Scheme 2; classified as mechanism.","evidence_ids":[ev(3,"image")]},
            {"region":"right-column conclusion and start of Experimental Section","finding":"Conclusion contains no additional experimental arrow; Method A begins and continues on page 4.","evidence_ids":[ev(3,"image")]},
        ],"record_ids":table2_ids+[f"{DOC}:scheme2_proposed_mechanism"],"unresolved":["Table 2 mixture and NR rows do not identify products or quantitative yields.","Cycloisomerization product structures in footnotes b/c are not specified."]},
        {"page":4,"state":"attempted","regions":[
            {"region":"upper-left Table 3","finding":"Four optically active substrate-scope experiments with BQ equivalents, yield, product ee, and diastereomer ratio.","evidence_ids":[ev(4,"image")]},
            {"region":"middle-left Scheme 2","finding":"Proposed PdII/Pd0 mechanism; not treated as a preparative experiment.","evidence_ids":[ev(4,"image")]},
            {"region":"bottom-left and upper-right general Methods A--D","finding":"Shared quantities and conditions mapped onto the corresponding Table 2 rows; only Method A explicitly states workup/purification.","evidence_ids":[ev(4,"image")]},
            {"region":"right-column detailed procedures for 3g and 3h","finding":"Exact procedures merged into Table 2 entries 18--20, 22, 24, and 25 rather than duplicated.","evidence_ids":[ev(4,"image")]},
        ],"record_ids":table2_ids+table3_ids+[f"{DOC}:scheme2_proposed_mechanism"],"unresolved":["Atmosphere and workup/purification are not explicit for Methods C/D; no inference was made.","Analytical data for 3a--f are referred to supporting information of reference 11, which was not supplied."]},
        {"page":5,"state":"attempted","regions":[
            {"region":"left and upper-right detailed procedures for 3i--3l","finding":"Exact procedures merged into Table 2 entries 26, 27, 30, 32--34, and 36--41; Table 2 entry 37 read as 83% from the image and detailed procedure.","evidence_ids":[ev(5,"image")]},
            {"region":"lower-right Figure 2 and 3l structure","finding":"ORTEP/structure characterization for (R*,R*)-3l linked to the 3l records, not treated as another reaction.","evidence_ids":[ev(5,"image")]},
            {"region":"bottom-right start of chiral 3a Method C procedure","finding":"Beginning of Table 3 entry 1 detailed procedure; continuation and outcome are on page 6.","evidence_ids":[ev(5,"image")]},
        ],"record_ids":[f"{DOC}:table2_entry_{i:02d}" for i in [26,27,30,32,33,34,36,37,38,39,40,41]]+[f"{DOC}:table3_entry_01"],"unresolved":["Page 5 reports benzoquinone 32 mg as 0.15 mmol for 3k Method C; the printed quantity was preserved without correction."]},
        {"page":6,"state":"attempted","regions":[
            {"region":"upper-left continuation of chiral 3a procedure","finding":"Completion of Table 3 entry 1 with 44 mg, 88% yield, >99% ee, HPLC, and optical rotation.","evidence_ids":[ev(6,"image")]},
            {"region":"left-column chiral 3b, 3d, and 3o procedures","finding":"Detailed procedures and outcomes merged into Table 3 entries 2--4.","evidence_ids":[ev(6,"image")]},
            {"region":"right column references and crystallographic notes","finding":"No additional current-paper reaction experiments; crystallography supports 3l/3o assignments only.","evidence_ids":[ev(6,"image")]},
        ],"record_ids":table3_ids,"unresolved":["HPLC/optical-rotation characterization was retained only at summary level; full spectral characterization is outside the reaction-record schema."]},
    ],
}

assert len(records) == 62, len(records)
assert [p["page"] for p in coverage["pages"]] == [1,2,3,4,5,6]
assert all(p["regions"] for p in coverage["pages"])
assert set(all_ids) == {rid for p in coverage["pages"] for rid in p["record_ids"]}

raw_path = OUT / "raw_model/extracted_records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

coverage_path = OUT / "coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    page = int(task["evidence_id"].split(":page",1)[1].split(":",1)[0])
    if 1 <= page <= 6:
        task["state"] = "attempted"
        task["reason"] = "Original page image and extracted text inspected; findings mapped in coverage/pages_0001_0006.json."
        task["visual_evidence_id"] = ev(page,"image")
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records":len(records),"coverage_pages":[p["page"] for p in coverage["pages"]],"raw":str(raw_path),"coverage":str(coverage_path)},ensure_ascii=False))
