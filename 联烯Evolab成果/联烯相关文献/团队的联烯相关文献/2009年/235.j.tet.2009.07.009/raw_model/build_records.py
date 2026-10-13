#!/usr/bin/env python3
"""Build source-derived machine records for PDF pages 1--6 (doc_1cbf5a93b96a7964)."""
import json
from pathlib import Path

DOC = "doc_1cbf5a93b96a7964"
BASE = Path(__file__).resolve().parent


def ev(*pages):
    out = []
    for page in pages:
        out += [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]
    return out


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
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, evidence, amounts=(), name=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, evidence),
        "smiles": fact(None, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(n, v, evidence) for n, v in amounts],
    }


def record(suffix, kind, evidence, participants, conditions, outcomes, notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "needs_review",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants if p["role"] != "product"],
            "conditions": conditions,
        }] if conditions else [],
        "outcomes": outcomes,
        "notes": [fact(n, evidence) for n in notes],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "Machine-extracted record requires source review; all structures remain unverified.",
                "No supporting-information file was explicitly associated.",
            ],
        },
    }


records = []

# Table 1: synthesis of allenyl phosphine oxides. Detailed amounts visible on pp. 4--5
# are merged into the corresponding table row. Rows 1c and 1f remain table-only.
t1 = [
    (1, "1a", "2-phenylbut-3-yn-2-ol", "3-phenylbuta-1,2-dienyl diphenyl phosphine oxide", 63, 4,
     [("mass", qty(1.4643, "g")), ("amount", qty(10, "mmol"))],
     [("volume", qty(0.96, "mL")), ("mass", qty(0.94, "g")), ("amount", qty(11.9, "mmol"))],
     [("volume", qty(2.00, "mL")), ("mass", qty(2.41, "g")), ("amount", qty(10.9, "mmol"))],
     10, 11, [("mass", qty(2.0732, "g"))]),
    (2, "1b", "3-phenylpent-1-yn-3-ol", "3-phenylpenta-1,2-dienyl diphenyl phosphine oxide", 55, 4,
     [("mass", qty(1.6058, "g")), ("amount", qty(10, "mmol"))],
     [("volume", qty(0.96, "mL")), ("mass", qty(0.94, "g")), ("amount", qty(11.9, "mmol"))],
     [("volume", qty(2.00, "mL")), ("mass", qty(2.41, "g")), ("amount", qty(10.9, "mmol"))],
     10, 11, [("mass", qty(1.8842, "g"))]),
    (3, "1c", "corresponding propargylic alcohol (R1=H, R2=Ph, R3=Ph)", "allenyl phosphine oxide 1c", 54, None, [], [], [("equivalents", qty(1.1, "equiv"))], None, None, []),
    (4, "1d", "2-phenyloct-3-yn-2-ol", "2-phenylocta-2,3-dien-4-yl diphenyl phosphine oxide", 45, 4,
     [("mass", qty(1.6205, "g")), ("amount", qty(8, "mmol"))],
     [("volume", qty(0.78, "mL")), ("mass", qty(0.77, "g")), ("amount", qty(9.7, "mmol"))],
     [("volume", qty(1.60, "mL")), ("mass", qty(1.93, "g")), ("amount", qty(8.7, "mmol"))],
     10, 9, [("mass", qty(1.4010, "g"))]),
    (5, "1e", "2,4-diphenylbut-3-yn-2-ol", "1,3-diphenylbuta-1,2-dienyl diphenyl phosphine oxide", 51, 4,
     [("mass", qty(1.7846, "g")), ("amount", qty(8.0, "mmol"))],
     [("volume", qty(0.78, "mL")), ("mass", qty(0.77, "g")), ("amount", qty(9.7, "mmol"))],
     [("volume", qty(1.60, "mL")), ("mass", qty(1.93, "g")), ("amount", qty(8.7, "mmol"))],
     10, 9, [("mass", qty(1.6770, "g"))]),
    (6, "1f", "corresponding propargylic alcohol (R1=H, R2=H, R3=Ph)", "3-phenylpropa-1,2-dienyl diphenyl phosphine oxide", 75, None, [], [], [("equivalents", qty(1.1, "equiv"))], None, None, []),
    (7, "1g", "1-(4-nitrophenyl)prop-2-yn-1-ol", "3-(4-nitrophenyl)propa-1,2-dienyl diphenyl phosphine oxide", 69, 5,
     [("mass", qty(0.3549, "g")), ("amount", qty(2.0, "mmol"))],
     [("volume", qty(0.20, "mL")), ("mass", qty(0.20, "g")), ("amount", qty(2.5, "mmol"))],
     [("volume", qty(0.40, "mL")), ("mass", qty(0.48, "g")), ("amount", qty(2.2, "mmol"))],
     2.0, 2.5, [("mass", qty(0.4980, "g"))]),
    (8, "1h", "1-(4-fluorophenyl)prop-2-yn-1-ol", "3-(4-fluorophenyl)propa-1,2-dienyl diphenyl phosphine oxide", 58, 4,
     [("mass", qty(1.5085, "g")), ("amount", qty(10.0, "mmol"))],
     [("volume", qty(0.96, "mL")), ("mass", qty(0.94, "g")), ("amount", qty(11.9, "mmol"))],
     [("volume", qty(2.00, "mL")), ("mass", qty(2.41, "g")), ("amount", qty(10.9, "mmol"))],
     10, 11, [("mass", qty(1.9396, "g"))]),
    (9, "1i", "1-(4-chlorophenyl)prop-2-yn-1-ol", "3-(4-chlorophenyl)propa-1,2-dienyl diphenyl phosphine oxide", 52, 4,
     [("mass", qty(2.1640, "g")), ("amount", qty(13, "mmol"))],
     [("volume", qty(1.25, "mL")), ("mass", qty(1.23, "g")), ("amount", qty(15.6, "mmol"))],
     [("volume", qty(2.60, "mL")), ("mass", qty(3.13, "g")), ("amount", qty(14.2, "mmol"))],
     13, 14, [("mass", qty(2.3597, "g"))]),
    (10, "1j", "1-(3-chlorophenyl)prop-2-yn-1-ol", "3-(3-chlorophenyl)propa-1,2-dienyl diphenyl phosphine oxide", 68, (4, 5),
     [("mass", qty(1.3371, "g")), ("amount", qty(8.0, "mmol"))],
     [("volume", qty(0.75, "mL")), ("mass", qty(0.74, "g")), ("amount", qty(9.3, "mmol"))],
     [("volume", qty(1.60, "mL")), ("mass", qty(1.93, "g")), ("amount", qty(8.7, "mmol"))],
     8, 9, [("mass", qty(1.9008, "g"))]),
    (11, "1k", "1-(2-chlorophenyl)prop-2-yn-1-ol", "3-(2-chlorophenyl)propa-1,2-dienyl diphenyl phosphine oxide", 46, 5,
     [("mass", qty(2.1653, "g")), ("amount", qty(13, "mmol"))],
     [("volume", qty(1.25, "mL")), ("mass", qty(1.23, "g")), ("amount", qty(15.6, "mmol"))],
     [("volume", qty(2.60, "mL")), ("mass", qty(3.13, "g")), ("amount", qty(14.2, "mmol"))],
     13, 14, [("mass", qty(2.1188, "g"))]),
    (12, "1l", "1-(4-methylphenyl)prop-2-yn-1-ol", "3-(4-methylphenyl)propa-1,2-dienyl diphenyl phosphine oxide", 44, 5,
     [("mass", qty(1.3563, "g")), ("amount", qty(9.29, "mmol"))],
     [("volume", qty(0.90, "mL")), ("mass", qty(0.88, "g")), ("amount", qty(11.2, "mmol"))],
     [("volume", qty(1.90, "mL")), ("mass", qty(2.29, "g")), ("amount", qty(10.4, "mmol"))],
     10, 11, [("mass", qty(1.3399, "g"))]),
    (13, "1m", "1-phenylhept-2-yn-1-ol", "1-phenylhepta-1,2-dien-3-yl diphenyl phosphine oxide", 62, 5,
     [("mass", qty(1.8828, "g")), ("amount", qty(10, "mmol"))],
     [("volume", qty(0.96, "mL")), ("mass", qty(0.94, "g")), ("amount", qty(11.9, "mmol"))],
     [("volume", qty(2.00, "mL")), ("mass", qty(2.41, "g")), ("amount", qty(10.9, "mmol"))],
     10, 11, [("mass", qty(2.3002, "g"))]),
    (14, "1n", "1,3-diphenylprop-2-yn-1-ol", "1,3-diphenylpropa-1,2-dienyl diphenyl phosphine oxide", 54, 5,
     [("mass", qty(2.0776, "g")), ("amount", qty(10, "mmol"))],
     [("volume", qty(0.96, "mL")), ("mass", qty(0.94, "g")), ("amount", qty(11.9, "mmol"))],
     [("volume", qty(2.00, "mL")), ("mass", qty(2.41, "g")), ("amount", qty(10.9, "mmol"))],
     10, 12, [("mass", qty(2.1243, "g"))]),
    (15, "1o", "1-(4-methoxyphenyl)prop-2-yn-1-ol", "3-(4-methoxyphenyl)propa-1,2-dienyl diphenyl phosphine oxide", 20, 5,
     [("mass", qty(1.6253, "g")), ("amount", qty(10, "mmol"))],
     [("volume", qty(0.96, "mL")), ("mass", qty(0.94, "g")), ("amount", qty(11.9, "mmol"))],
     [("volume", qty(2.00, "mL")), ("mass", qty(2.41, "g")), ("amount", qty(10.9, "mmol"))],
     10, 11, [("mass", qty(0.6880, "g"))]),
]

for entry, label, alcohol, product_name, yld, detail_page, alc_amt, pyr_amt, pcl_amt, ether_ml, dcm_ml, prod_amt in t1:
    pages = [1]
    if isinstance(detail_page, tuple):
        pages += list(detail_page)
    elif detail_page:
        pages.append(detail_page)
    evidence = ev(*pages)
    participants = [
        participant("alcohol", "reactant", alcohol, evidence, alc_amt),
        participant("ph2pcl", "reagent", "diphenylphosphinous chloride (Ph2PCl)", evidence, pcl_amt),
        participant("pyridine", "reagent", "pyridine", evidence, pyr_amt),
        participant("ether", "solvent", "diethyl ether", evidence, [("volume", qty(ether_ml, "mL"))] if ether_ml else []),
        participant("dcm", "solvent", "dichloromethane", evidence, [("volume", qty(dcm_ml, "mL"))] if dcm_ml else []),
        participant("product", "product", label, evidence, prod_amt, product_name),
    ]
    conditions = []
    if entry == 7:
        conditions += [field("temperature", qty(-40, "°C"), evidence), field("addition_time", qty(20, "min"), evidence), field("reaction_time", qty(11, "h"), evidence)]
    elif entry == 1:
        conditions += [field("initial_temperature", qty(0, "°C"), evidence), field("warm_to", "r.t.", evidence), field("addition_time", qty(1, "h"), evidence), field("time_at_0_C", qty(1, "h"), evidence), field("time_at_room_temperature", qty(7, "h"), evidence)]
    elif entry == 14:
        conditions += [field("initial_temperature", qty(0, "°C"), evidence), field("warm_to", "r.t.", evidence), field("reaction_time", qty(13, "h"), evidence)]
    else:
        conditions += [field("initial_temperature", qty(0, "°C"), evidence), field("warm_to", "r.t.", evidence), field("reaction_time", None, evidence)]
    if detail_page:
        conditions += [
            field("workup", "poured onto crushed ice; aqueous phase extracted with dichloromethane; combined organic phase washed with brine and dried over anhydrous Na2SO4", evidence),
            field("purification", "silica-gel chromatography", evidence),
        ]
    records.append(record(
        f"table1_entry{entry}", "substrate_scope_entry", evidence, participants, conditions,
        [field("isolated_yield", qty(yld, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence, ["product"])],
        unresolved=[
            "Machine-extracted structures are represented by source labels/names; SMILES remain unverified and unset.",
            "No supporting-information file was explicitly associated.",
            "The cited prior procedure is not imported as source evidence; abbreviated rows omit any details not restated in this paper.",
        ] + (["Reaction duration is not stated for this abbreviated preparation."] if entry not in (1, 7, 14) else []),
    ))


def fluor_participants(substrate, product, evidence, scale=0.2, sf_mmol=0.3, sf_equiv=1.5, solvents=(), water=None, sf_mass=None, substrate_mass=None, product_mass=None, second_product=None):
    parts = [participant("substrate", "reactant", substrate, evidence,
                         ([('mass', qty(substrate_mass, 'mg'))] if substrate_mass is not None else []) + [('amount', qty(scale, 'mmol'))])]
    sf_amounts = ([('mass', qty(sf_mass, 'mg'))] if sf_mass is not None else []) + [('amount', qty(sf_mmol, 'mmol')), ('equivalents', qty(sf_equiv, 'equiv'))]
    parts.append(participant("selectfluor", "reagent", "Selectfluor", evidence, sf_amounts))
    for i, (label, volume) in enumerate(solvents):
        parts.append(participant(f"solvent{i+1}", "solvent", label, evidence, [('volume', qty(volume, 'mL'))] if volume is not None else []))
    if water:
        parts.append(participant("water", "reagent", "water", evidence, water))
    parts.append(participant("product", "product", product, evidence, ([('mass', qty(product_mass, 'mg'))] if product_mass is not None else [])))
    if second_product:
        parts.append(participant("product2", "product", second_product, evidence))
    return parts


# Table 2 optimization. Page 6 adds full procedures to entries 1, 7 and 8.
t2 = [
    (1, "10/1", 80, 2.0, 80, "92/8", None),
    (2, "5/1", 80, 1.5, 85, "91/9", None),
    (3, "3/1", 80, 4.0, 83, "92/8", None),
    (4, "0/1", 80, 51.0, 57, "95/5", None),
    (5, "10/1", 60, 6.0, 78, "91/9", None),
    (6, "10/1", 40, 10.0, 81, "90/10", None),
    (7, "1/0", 80, 2.0, 71, ">99/1", 66),
    (8, "1/0", 80, 2.0, 66, ">99/1", 64),
]
for entry, ratio, temp, hours, nmr, selectivity, isolated in t2:
    evidence = ev(2, 5, 6) if entry == 7 else (ev(2, 6) if entry in (1, 8) else ev(2))
    if entry == 1:
        parts = fluor_participants("1a", "E-2a", evidence, solvents=[("MeCN", 2.0)], water=[("volume", qty(0.2, "mL"))], sf_mass=105.7, substrate_mass=67.8, second_product="E-3a")
        parts[-2]["amounts"].append(field("mass", qty(45.1, "mg"), evidence))
        parts[-1]["amounts"].append(field("mass", qty(3.9, "mg"), evidence))
    elif entry == 7:
        parts = fluor_participants("1a", "E-2a", evidence, solvents=[("commercial MeCN (without prior treatment)", 2.3)], sf_mass=106.3, substrate_mass=66.9, product_mass=48.9, second_product="E-3a")
    elif entry == 8:
        parts = fluor_participants("1a", "E-2a", evidence, solvents=[("anhydrous MeCN", 2.25)], water=[("mass", qty(24.5, "mg")), ("amount", qty(1.4, "mmol")), ("equivalents", qty(7.0, "equiv"))], sf_mass=111.6, substrate_mass=66.0, product_mass=47.2, second_product="E-3a")
    else:
        solvents = [("water", 2.3)] if ratio == "0/1" else [("MeCN", None), ("water", None)]
        parts = fluor_participants("1a", "E-2a", evidence, solvents=solvents, second_product="E-3a")
    cond = [field("temperature", qty(temp, "°C"), evidence), field("reaction_time", qty(hours, "h"), evidence), field("solvent_ratio_MeCN_to_H2O", ratio, evidence)]
    if entry == 8:
        cond.append(field("atmosphere", "nitrogen", evidence))
    if entry in (1, 7, 8):
        cond += [field("workup", "quenched with water, extracted with diethyl ether, washed with brine, dried over anhydrous Na2SO4", evidence), field("purification", "flash chromatography on silica gel", evidence)]
    outs = [
        field("combined_NMR_yield_E-2a_and_E-3a", qty(nmr, "%"), evidence, ["product", "product2"]),
        field("yield_measurement_basis", "NMR based on 1a using CH2Br2 as internal standard", evidence, ["product", "product2"]),
        field("product_ratio_E-2a_to_E-3a", selectivity, evidence, ["product", "product2"]),
    ]
    if isolated is not None:
        outs += [field("isolated_yield_E-2a", qty(isolated, "%"), evidence, ["product"])]
    if entry == 1:
        outs += [field("isolated_yield_E-2a_detailed_batch", qty(60, "%"), evidence, ["product"]), field("isolated_yield_E-3a_detailed_batch", qty(5.5, "%"), evidence, ["product2"])]
    records.append(record(f"table2_entry{entry}", "optimization_entry", evidence, parts, cond, outs,
                          unresolved=["All structures remain unverified; labels are retained from the source.", "No supporting-information file was explicitly associated."] + (["Exact individual solvent volumes are not stated for this table row."] if entry in (2, 3, 5, 6) else [])))


# Table 3 scope: rows remain distinct from Table 2 because the table specifies a different reaction scale.
t3 = [
    (1, "1a", "E-2a", "A", 2.0, 66, 0.3, 0.45, 3.5, None, None, None, None),
    (2, "1a", "E-2a", "B", 2.0, 64, 0.2, 0.3, 2.25, None, None, None, None),
    (3, "1b", "E-2b", "A", 3.0, 62, 0.3, 0.45, 3.5, 103.9, 159.4, 70.9, None),
    (4, "1b", "E-2b", "B", 3.0, 70, 0.2, 0.3, 2.25, 69.1, 111.7, 53.8, 26.4),
    (5, "1c", "E-2c", "A", 2.0, 78, 0.2, 0.3, 2.3, 77.8, 107.5, 66.4, None),
    (6, "1c", "E-2c", "B", 3.0, 85, 0.2, 0.3, 2.25, 79.0, 112.5, 73.3, 25.3),
    (7, "1d", "E-2d", "A", 15.0, 66, 0.3, 0.45, 3.5, 115.8, 168.2, 83.1, None),
    (8, "1d", "E-2d", "B", 14.0, 74, 0.2, 0.3, 2.25, 76.9, 112.1, 62.1, 25.7),
    (9, "1e", "E-2e", "A", 12.0, 70, 0.3, 0.45, 3.5, 122.1, 160.1, 92.6, None),
    (10, "1e", "E-2e", "B", 16.0, 75, 0.2, 0.3, 2.25, None, None, None, None),
]
for entry, substrate, product, mode, hours, yld, scale, sfmmol, mecn, smass, sfmass, pmass, watermass in t3:
    evidence = ev(2, 6) if entry in range(3, 10) else ev(2)
    water = None
    if mode == "B":
        water = [("equivalents", qty(7.0, "equiv")), ("amount", qty(1.4, "mmol"))]
        if watermass is not None:
            water.insert(0, ("mass", qty(watermass, "mg")))
    parts = fluor_participants(substrate, product, evidence, scale, sfmmol, 1.5,
                               [("commercial MeCN" if mode == "A" else "anhydrous MeCN", mecn)], water,
                               sfmass, smass, pmass)
    cond = [field("temperature", qty(80, "°C"), evidence), field("reaction_time", qty(hours, "h"), evidence), field("condition_set", mode, evidence)]
    if mode == "B":
        cond.append(field("atmosphere", "nitrogen", evidence))
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", evidence, parts, cond,
                          [field("isolated_yield", qty(yld, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence, ["product"])],
                          unresolved=["All structures remain unverified; labels are retained from the source.", "No supporting-information file was explicitly associated."] + (["Detailed batch quantities are not restated within covered pages."] if entry in (1, 2, 10) else [])))


# Table 4 solvent/loading/temperature screen for 1f.
t4 = [
    (1, "MeCN", 1.5, 80, 23.5, 58, None),
    (2, "MeCN/H2O=20/1", 1.5, 80, 24.0, 63, None),
    (3, "MeCN/H2O=10/1", 1.5, 80, 11.0, 68, None),
    (4, "MeCN/H2O=10/1", 3.0, 80, 11.5, 60, None),
    (5, "MeCN/H2O=5/1", 1.5, 80, 13.0, 40, None),
    (6, "DMF/H2O=10/1", 1.5, 80, 54.5, 32, None),
    (7, "MeNO2/H2O=10/1", 1.5, 80, 20.0, 88, 62),
    (8, "MeNO2/H2O=10/1", 1.2, 80, 24.0, 55, None),
    (9, "MeNO2/H2O=10/1", 1.5, 60, 33.0, 69, None),
]
for entry, solvent, sfeq, temp, hours, yld, isolated in t4:
    evidence = ev(2)
    sfmmol = round(0.2 * sfeq, 3)
    if "/" in solvent:
        component_text = solvent.split("=", 1)[0]
        solvent_parts = [(name, None) for name in component_text.split("/")]
    else:
        solvent_parts = [(solvent, 2.2)]
    parts = fluor_participants("1f", "E-2f", evidence, 0.2, sfmmol, sfeq, solvent_parts)
    outs = [field("NMR_yield_E-2f", qty(yld, "%"), evidence, ["product"]), field("yield_measurement_basis", "NMR based on 1f using CH2Br2 as internal standard", evidence, ["product"])]
    if isolated is not None:
        outs.append(field("isolated_yield_E-2f", qty(isolated, "%"), evidence, ["product"]))
    records.append(record(f"table4_entry{entry}", "optimization_entry", evidence, parts,
                          [field("temperature", qty(temp, "°C"), evidence), field("reaction_time", qty(hours, "h"), evidence), field("solvent_system", solvent, evidence), field("total_solvent_volume", qty(2.2, "mL"), evidence)], outs,
                          unresolved=["Individual component volumes of mixed solvents are not stated in the table.", "All structures remain unverified.", "No supporting-information file was explicitly associated."]))


# Table 5 aryl-substituent scope.
t5 = [
    (1, "1f", "E-2f", 1.5, 80, 20.0, 62, False),
    (2, "1g", "E-2g", 2.5, 80, 28.0, 33, False),
    (3, "1h", "E-2h", 1.5, 80, 10.0, 72, False),
    (4, "1i", "E-2i", 1.5, 80, 12.0, 56, False),
    (5, "1j", "E-2j", 2.0, 80, 24.0, 50, True),
    (6, "1k", "E-2k", 1.5, 80, 33.0, 56, False),
    (7, "1l", "E-2l", 1.5, 40, 25.0, 63, False),
    (8, "1m", "E-2m", 2.0, 80, 24.0, 59, True),
    (9, "1n", "E-2n", 1.5, 80, 12.5, 67, True),
]
for entry, substrate, product, sfeq, temp, hours, yld, recryst in t5:
    evidence = ev(3)
    sfmmol = round(0.3 * sfeq, 3)
    parts = fluor_participants(substrate, product, evidence, 0.3, sfmmol, sfeq,
                               [("nitromethane", 3.0)], [("volume", qty(0.3, "mL"))])
    cond = [field("temperature", qty(temp, "°C"), evidence), field("reaction_time", qty(hours, "h"), evidence), field("solvent_ratio_MeNO2_to_H2O", "10/1", evidence)]
    if recryst:
        cond.append(field("purification", "silica-gel chromatography followed by recrystallization", evidence))
    records.append(record(f"table5_entry{entry}", "substrate_scope_entry", evidence, parts, cond,
                          [field("isolated_yield", qty(yld, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence, ["product"])],
                          unresolved=["All structures remain unverified; labels are retained from the source.", "No supporting-information file was explicitly associated."] + (["The paper points to Supplementary data for detailed recrystallization information, but no SI was explicitly provided."] if recryst else [])))


# Table 6 loading screen for 1o. The combined isolated yield is assigned to both
# products unless the reported 0/100 ratio identifies E-4o alone.
t6 = [
    (1, 1.5, 80, 7.0, 38, "65/35", None),
    (2, 2.5, 80, 5.0, 41, "29/71", None),
    (3, 3.0, 80, 8.0, 43, "8/92", None),
    (4, 0.9, "r.t.", 8.0, 69, "97/3", 45),
    (5, 3.5, 80, 8.0, 25, "0/100", 14),
]
for entry, sfeq, temp, hours, nmr, ratio, isolated in t6:
    evidence = ev(3)
    parts = fluor_participants("1o", "E-2o", evidence, 0.3, round(0.3*sfeq, 3), sfeq,
                               [("nitromethane", 3.0)], [("volume", qty(0.3, "mL"))], second_product="E-4o")
    target = ["product", "product2"]
    outs = [field("combined_NMR_yield_E-2o_and_E-4o", qty(nmr, "%"), evidence, target), field("product_ratio_E-2o_to_E-4o", ratio, evidence, target), field("yield_measurement_basis", "NMR; ratio determined by 1H NMR after flash chromatography", evidence, target)]
    if isolated is not None:
        iso_targets = ["product2"] if ratio == "0/100" else target
        outs.append(field("isolated_yield", qty(isolated, "%"), evidence, iso_targets))
    records.append(record(f"table6_entry{entry}", "optimization_entry", evidence, parts,
                          [field("temperature", qty(temp, "°C") if isinstance(temp, (int, float)) else temp, evidence), field("reaction_time", qty(hours, "h"), evidence), field("solvent_ratio_MeNO2_to_H2O", "10/1", evidence), field("purification", "flash chromatography on silica gel; E-2o and E-4o not separable under the reported conditions", evidence)], outs,
                          unresolved=["All structures remain unverified.", "No supporting-information file was explicitly associated.", "The table reports combined yields because E-2o and E-4o could not generally be separated."]))


# Equation (1): fluorination of E-2o to E-4o is a separate experiment.
evidence = ev(3)
parts = fluor_participants("E-2o", "E-4o", evidence, 0.3, 0.66, 2.2,
                           [("nitromethane", 3.0)], [("volume", qty(0.3, "mL"))])
records.append(record("equation1_E-2o_to_E-4o", "reported_experiment", evidence, parts,
                      [field("temperature", qty(80, "°C"), evidence), field("reaction_time", qty(8.0, "h"), evidence), field("solvent_ratio_MeNO2_to_H2O", "10/1", evidence)],
                      [field("isolated_yield_E-4o", qty(20, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated", evidence, ["product"])],
                      unresolved=["The equation is source-supported, but full workup/purification details are not stated on covered pages.", "All structures remain unverified.", "No supporting-information file was explicitly associated."]))


# Scheme 1 is explicitly a proposed mechanism, not a reported batch experiment.
evidence = ev(3)
records.append({
    "record_id": f"{DOC}:scheme1_proposed_mechanism",
    "document_id": DOC,
    "source_reaction_id": "scheme1_proposed_mechanism",
    "record_kind": "mechanism",
    "status": "needs_review",
    "completeness": "partial",
    "evidence_ids": evidence,
    "participants": [],
    "steps": [],
    "outcomes": [],
    "notes": [fact("Proposed sequence: electrophilic fluorination gives fluorinium intermediate 3; neighboring phosphine-oxide oxygen participation gives cyclic intermediate 4; water attack and P-O cleavage affords E-2.", evidence)],
    "review": {"method": "model", "reviewer": None, "checked_fields": [], "unresolved": ["This is a proposed mechanism, not an independently reported experiment; generic R groups preclude fully specified structures."]},
})


out = BASE / "records_pages_0001_0006.json"
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "path": str(out)}, ensure_ascii=False))
