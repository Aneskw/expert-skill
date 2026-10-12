#!/usr/bin/env python3
"""Build evidence-linked raw records for doc_59eb0b3e3b72ed1c, PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_59eb0b3e3b72ed1c"
BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "raw_model" / "extracted_records_pages_0001_0004.json"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


P1, P2, P3 = ev(1), ev(2), ev(3)


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, target=None, category=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if target:
        item["target_entity_ids"] = list(target)
    if category:
        item["category"] = category
    return item


def participant(entity_id, role, evidence, label=None, name=None, smiles=None, amounts=None):
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


def amount(name, number, unit, evidence):
    return field(name, {"number": number, "unit": unit}, evidence)


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


def base_1a(evidence, with_amount=True):
    amounts = [amount("amount", 0.5, "mmol", evidence)] if with_amount else []
    return participant(
        "1a", "reactant", evidence, "1a", "1,2-propadienyl phenyl sulfoxide",
        "O=S(c1ccccc1)C=C=C", amounts,
    )


def p_i2(evidence, equiv=None, mmol=None, mass=None):
    amounts = []
    if equiv is not None:
        amounts.append(amount("equivalents", equiv, "equiv", evidence))
    if mmol is not None:
        amounts.append(amount("amount", mmol, "mmol", evidence))
    if mass is not None:
        amounts.append(amount("mass", mass, "mg", evidence))
    return participant("iodine", "reagent", evidence, "I2", "iodine", "[I][I]", amounts)


def p_etoh(evidence, volume=0.3):
    return participant(
        "ethanol", "reagent", evidence, "EtOH", "ethanol", "CCO",
        [amount("volume", volume, "mL", evidence)],
    )


def p_mecn(evidence, volume=6):
    return participant(
        "acetonitrile", "solvent", evidence, "MeCN", "acetonitrile", "CC#N",
        [amount("volume", volume, "mL", evidence)],
    )


def p_4a(evidence, mass=None):
    amounts = [amount("mass", mass, "mg", evidence)] if mass is not None else []
    return participant(
        "4a", "product", evidence, "4a",
        "E-2-iodo-3-phenylsulfinyl-2-propen-1-ol",
        "O=S(c1ccccc1)C=C(I)CO", amounts,
    )


def p_5a(evidence):
    return participant(
        "5a", "product", evidence, "5a",
        "2-iodo-3-(phenylthio)-2-propen-1-ol",
        "c1ccccc1SC=C(I)CO", [],
    )


records = []

# Scheme 1 is a proposed cyclic-intermediate pathway, not an individual experiment.
records.append(record(
    "scheme1_mechanism", "Scheme 1", "mechanism", P1,
    [
        participant("scheme1_1", "reactant", P1, "1", "generic 1,2-allenylic sulfoxide", None),
        p_i2(P1),
        participant("scheme1_2", "unspecified_agent", P1, "2", "cyclic intermediate", None),
        participant("scheme1_3", "product", P1, "3", "generic iodohydroxylation product", None),
    ],
    [], [],
    ["Scheme 1 is presented as a stereochemical pathway through cyclic intermediate 2."],
    ["Generic R-group structures are not expanded to SMILES.", "The scheme is mechanistic and is not counted as a reported experiment."],
))


# Table 1. Entry 7 is linked to the 4a preparation and Table 2 entry 1.
table1 = [
    (1, 1.5, 0.1, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 1.3, 58, 6, 27),
    (2, 1.5, 0.2, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 2.5, 52, 10, 16),
    (3, 2.0, 0.1, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 1.3, 71, 5, 23),
    (4, 2.0, 0.2, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 1.3, 71, 4, 6),
    (5, 1.5, 3.0, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 2.0, 43, 17, 25),
    (6, 2.0, 0.25, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 1.6, 82, 11, 0),
    (7, 2.0, 0.3, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 1.3, 88, 13, 0),
    (8, 2.0, 0.25, {"number": 16, "unit": "°C"}, 1.6, 64, 31, 0),
    (9, 1.5, 0.6, {"number": 15, "unit": "°C"}, 2.0, 62, 25, 0),
    (10, 2.0, 0.25, {"number": 16, "unit": "°C"}, 1.6, 45, 46, 0),
    (11, 2.4, 0.3, {"number": 55, "unit": "°C"}, 1.0, 11, 0, 0),
    (12, 1.5, 0.0, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 2.0, 58, 14, 17),
    (13, 2.0, 0.0, {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, 2.0, 80, 0, 20),
]

for entry, i2eq, etoh_ml, temp, hours, y4, y5, recovered in table1:
    evidence = P2
    if entry in (1, 2, 7, 8, 9, 10, 12, 13):
        evidence = P1 + P2
    suffix = f"table1_entry{entry:02d}"
    source_id = f"Table 1 entry {entry}"
    if entry == 7:
        suffix = "table1_entry07_table2_entry01_4a"
        source_id = "Table 1 entry 7 / Table 2 entry 1 / 4a preparation"
    participants = [base_1a(evidence), p_i2(evidence, equiv=i2eq), p_mecn(evidence), p_4a(evidence), p_5a(evidence)]
    notes = []
    unresolved = ["Supporting information was not supplied or explicitly associated."]
    if etoh_ml > 0:
        participants.append(p_etoh(evidence, etoh_ml))
    else:
        notes.append("EtOH was absent in this table entry.")
    if entry == 13:
        participants.extend([
            participant("lithium_acetate_dihydrate", "unspecified_agent", evidence,
                        "LiOAc·2H2O", "lithium acetate dihydrate", None,
                        [amount("amount", 1.0, "mmol", evidence)]),
            participant("water", "solvent", evidence, "H2O", "water", "O", []),
        ])
        notes.append("The footnote specifies CH3CN/H2O = 7:1 and addition of LiOAc·2H2O.")
    if entry == 10:
        notes.append("The reaction was carried out under an atmosphere of N2.")
    if entry == 7:
        participants[0]["amounts"].append(amount("mass", 82.0, "mg", evidence))
        participants[1]["amounts"].extend([amount("amount", 1.0, "mmol", evidence), amount("mass", 254.0, "mg", evidence)])
        participants[3]["amounts"].append(amount("mass", 136.0, "mg", evidence))
        notes.append("Table 2 footnote c says direct chromatography without prior Na2S2O3, whereas the detailed 4a procedure reports water then saturated Na2S2O3 and a different eluent ratio.")
        unresolved.append("Conflicting 4a workup/purification descriptions were preserved without choosing one.")
    conditions = [
        field("temperature", temp, evidence),
        field("time", {"number": hours, "unit": "h"}, evidence),
    ]
    if entry == 10:
        conditions.append(field("atmosphere", "N2", evidence))
    if entry == 13:
        conditions.append(field("solvent", "CH3CN/H2O = 7:1", evidence))
    if entry == 7:
        conditions.extend([
            field("operation", "I2 was added to 1a in MeCN; after 5 min, EtOH in MeCN was added.", evidence),
            field("workup", "Source conflict: direct chromatography without Na2S2O3 in Table 2 footnote c; water/Na2S2O3 workup in the detailed procedure.", evidence),
            field("purification", "Silica gel chromatography; petroleum ether/ethyl acetate is reported as 3:1 in the footnote and 2:1 in the detailed procedure.", evidence),
        ])
    outcomes = [
        field("isolated_yield", {"number": y4, "unit": "%"}, evidence, ["4a"]),
        field("isolated_yield", {"number": y5, "unit": "%"}, evidence, ["5a"]),
        field("recovered_starting_material_percent", {"number": recovered, "unit": "%"}, evidence, ["1a"], "percentage"),
        field("yield_measurement_basis", "isolated yield", evidence),
    ]
    records.append(record(suffix, source_id, "optimization_entry", evidence, participants,
                          [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
                          outcomes, notes, unresolved))


# Table 2 scope rows 2-11; row 1 is already unified with Table 1 entry 7 above.
scope = {
    "b": dict(row=2, time=0.7, y=84, sub="1b", prod="4b", subname="1-(phenylsulfinyl)-1,2-heptadiene", prodname="E-2-iodo-1-phenylsulfinyl-1-hepten-3-ol", subsm="O=S(c1ccccc1)C=C=CCCCC", prodsm="O=S(c1ccccc1)C=C(I)C(O)CCCC", smass=66.0, smmol=0.3, imass=152.4, immol=0.6, pmass=91.4),
    "c": dict(row=3, time=0.5, y=82, sub="1c", prod="4c", subname="1-(phenylsulfinyl)-1,2-decadiene", prodname="E-2-iodo-1-phenylsulfinyl-1-decen-3-ol", subsm="O=S(c1ccccc1)C=C=CCCCCCCC", prodsm="O=S(c1ccccc1)C=C(I)C(O)CCCCCCC", smass=131.0, smmol=0.5, imass=254.0, immol=1.0, pmass=167.1),
    "d": dict(row=4, time=0.3, y=91, sub="1d", prod="4d", subname="3-ethyl-1-(phenylsulfinyl)-1,2-pentadiene", prodname="E-3-ethyl-2-iodo-1-phenylsulfinyl-1-penten-3-ol", subsm="O=S(c1ccccc1)C=C=C(CC)CC", prodsm="O=S(c1ccccc1)C=C(I)C(O)(CC)CC", smass=88.0, smmol=0.4, imass=203.2, immol=0.8, pmass=132.4),
    "e": dict(row=5, time=0.3, y=80, sub="1e", prod="4e", subname="3,5-dimethyl-1-(phenylsulfinyl)-1,2-hexadiene", prodname="E-2-iodo-3,5-dimethyl-1-phenylsulfinyl-1-hexen-3-ol", subsm="O=S(c1ccccc1)C=C=C(C)CC(C)C", prodsm="O=S(c1ccccc1)C=C(I)C(O)(C)CC(C)C", smass=93.6, smmol=0.4, imass=203.2, immol=0.8, pmass=121.5),
    "f": dict(row=6, time=0.3, y=94, sub="1f", prod="4f", subname="1-(phenylsulfinyl)vinylidenecyclohexane", prodname="E-1-[1-iodo-2-(phenylsulfinyl)vinyl]-1-cyclohexanol", subsm="O=S(c1ccccc1)C=C=C1CCCCC1", prodsm="O=S(c1ccccc1)C=C(I)C1(O)CCCCC1", smass=69.6, smmol=0.3, imass=152.4, immol=0.6, pmass=106.4),
    "g": dict(row=7, time=0.6, y=91, sub="1g", prod="4g", subname="3-methyl-1-(phenylsulfinyl)-1,2-pentadiene", prodname="E-2-iodo-3-methyl-1-phenylsulfinyl-1-penten-3-ol", subsm="O=S(c1ccccc1)C=C=C(C)CC", prodsm="O=S(c1ccccc1)C=C(I)C(O)(C)CC", smass=81.7, smmol=0.4, imass=203.2, immol=0.8, pmass=132.3),
    "h": dict(row=8, time=0.3, y=87, sub="1h", prod="4h", subname="3-methyl-1-(phenylsulfinyl)-1,2-butadiene", prodname="E-3-iodo-2-methyl-4-phenylsulfinyl-3-buten-2-ol", subsm="O=S(c1ccccc1)C=C=C(C)C", prodsm="O=S(c1ccccc1)C=C(I)C(O)(C)C", smass=76.8, smmol=0.4, imass=203.2, immol=0.8, pmass=117.2),
    "i": dict(row=9, time=1.0, y=74, sub="1i", prod="4i", subname="substituted 1,2-allenyl phenyl sulfoxide 1i", prodname="E-3-iodo-2-methyl-4-phenylsulfinyl-3-octen-2-ol", subsm=None, prodsm="CC(O)(C)C(I)=C(S(=O)c1ccccc1)CCCC", smass=74.4, smmol=0.3, imass=114.3, immol=0.45, pmass=85.7),
    "j": dict(row=10, time=1.0, y=58, sub="1j", prod="4j", subname="substituted 1,2-allenyl phenyl sulfoxide 1j", prodname="E-2-iodo-3-phenylsulfinyl-2-hepten-1-ol", subsm=None, prodsm="OCC(I)=C(S(=O)c1ccccc1)CCCC", smass=66.0, smmol=0.3, imass=152.4, immol=0.6, pmass=65.2),
    "k": dict(row=11, time=0.5, y=84, sub="1k", prod="4k", subname="3-methyl-1-(phenylsulfinyl)-1,2-hexadiene", prodname="E-2-iodo-3-methyl-1-phenylsulfinyl-1-hexen-3-ol", subsm="O=S(c1ccccc1)C=C=C(C)CCC", prodsm="O=S(c1ccccc1)C=C(I)C(O)(C)CCC", smass=88.2, smmol=0.4, imass=203.2, immol=0.8, pmass=127.1),
}

for letter, row in scope.items():
    evidence = P2 + P3
    sub = participant(row["sub"], "reactant", evidence, row["sub"], row["subname"], row["subsm"],
                      [amount("mass", row["smass"], "mg", evidence), amount("amount", row["smmol"], "mmol", evidence)])
    prod = participant(row["prod"], "product", evidence, row["prod"], row["prodname"], row["prodsm"],
                       [amount("mass", row["pmass"], "mg", evidence)])
    i2eq = row["immol"] / row["smmol"]
    participants = [sub, p_i2(evidence, equiv=i2eq, mmol=row["immol"], mass=row["imass"]), p_etoh(evidence), p_mecn(evidence), prod]
    temp = {"number": 0, "unit": "°C"} if letter == "f" else {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}
    conditions = [field("temperature", temp, evidence), field("time", {"number": row["time"], "unit": "h"}, evidence)]
    notes = ["The compound was prepared according to typical procedure A."]
    unresolved = ["Supporting information was not supplied or explicitly associated.", "The row-specific yield of sulfide byproduct 5 is not reported."]
    if letter == "f":
        conditions.extend([
            field("operation", "A solution of I2 in MeCN was added to 1f and EtOH in MeCN with stirring at 0 °C.", evidence),
            field("workup", "Quenched with water, treated with saturated aqueous Na2S2O3, extracted with dichloromethane, washed with NaCl, and dried over MgSO4.", evidence),
            field("purification", "Silica gel chromatography, petroleum ether/ethyl acetate = 3:1 v/v.", evidence),
        ])
    elif letter == "i":
        conditions.extend([
            field("workup", "The productive experiment was submitted directly to silica gel chromatography without prior Na2S2O3 treatment.", evidence),
            field("purification", "Silica gel chromatography, petroleum ether/ethyl acetate = 3:1 v/v.", evidence),
        ])
        notes.append("The detailed 1i experiment has a lower iodine loading than the generic Condition A default.")
        unresolved.append("The detailed 1i experiment reports 0.45 mmol I2 for 0.3 mmol 1i (1.5 equiv), while generic Condition A specifies 2 equiv; the detailed quantities were used for this row.")
    else:
        conditions.extend([
            field("workup", "Treated with Na2S2O3 before chromatography under typical procedure A.", evidence),
            field("purification", "Silica gel chromatography under typical procedure A.", evidence),
        ])
    records.append(record(
        f"table2_entry{row['row']:02d}_{row['prod']}", f"Table 2 entry {row['row']} / {row['prod']} preparation",
        "substrate_scope_entry", evidence, participants,
        [{"step_id": "reaction_and_isolation", "participant_ids": [p["entity_id"] for p in participants], "conditions": conditions}],
        [field("isolated_yield", {"number": row["y"], "unit": "%"}, evidence, [row["prod"]]), field("yield_measurement_basis", "isolated yield", evidence)],
        notes, unresolved,
    ))


# Table 2 entry 9 footnote reports a distinct failed workup experiment.
failure_evidence = P2 + P3
failure_parts = [
    participant("1i", "reactant", failure_evidence, "1i", "substituted 1,2-allenyl phenyl sulfoxide 1i", None,
                [amount("mass", 74.4, "mg", failure_evidence), amount("amount", 0.3, "mmol", failure_evidence)]),
    p_i2(failure_evidence, equiv=1.5, mmol=0.45, mass=114.3), p_etoh(failure_evidence), p_mecn(failure_evidence),
    participant("sodium_thiosulfate", "unspecified_agent", failure_evidence, "Na2S2O3", "sodium thiosulfate", None, []),
]
records.append(record(
    "table2_entry09_thiosulfate_failure", "Table 2 entry 9 footnote d Na2S2O3-treated control",
    "reported_experiment", failure_evidence, failure_parts,
    [{"step_id": "reaction_and_workup", "participant_ids": [p["entity_id"] for p in failure_parts], "conditions": [
        field("temperature", {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, failure_evidence),
        field("time", {"number": 1.0, "unit": "h"}, failure_evidence),
        field("workup", "The reaction mixture was treated with Na2S2O3.", failure_evidence),
    ]}],
    [field("observed_result", "only starting material 1i was obtained", failure_evidence, ["1i"])],
    ["This is a distinct failed control described in Table 2 footnote d, not the productive 74% row."],
    ["Recovery percentage and mass were not reported.", "No product yield was quantified for this control.", "Supporting information was not supplied or explicitly associated."],
))


# Table 3 alcohol variants.
alcohols = [
    (1, "benzyl_alcohol", "BnOH", "benzyl alcohol", "OCc1ccccc1", 88),
    (2, "isopropanol", "i-PrOH", "2-propanol", "CC(O)C", 85),
    (3, "n_pentanol", "n-C5H11OH", "1-pentanol", "CCCCCO", 86),
]
for entry, entity, label, name, smiles, yld in alcohols:
    evidence = P1 + P2
    parts = [
        base_1a(evidence), p_i2(evidence, mmol=1.2), p_mecn(evidence),
        participant(entity, "reagent", evidence, label, name, smiles, [amount("volume", 0.3, "mL", evidence)]),
        p_4a(evidence), p_5a(evidence),
    ]
    records.append(record(
        f"table3_entry{entry:02d}", f"Table 3 entry {entry}", "optimization_entry", evidence, parts,
        [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in parts], "conditions": [
            field("temperature", {"minimum": 0, "maximum": 5, "unit": "°C", "raw_text": "0–5 °C"}, evidence),
            field("time", {"number": 2.0, "unit": "h"}, evidence),
        ]}],
        [field("isolated_yield", {"number": yld, "unit": "%"}, evidence, ["4a"]), field("yield_measurement_basis", "isolated yield", evidence)],
        ["Across the Table 3 alcohol experiments, 5a is reported in a 3–9% yield range, but no row-specific 5a yield is assigned."],
        ["The row-specific yield of 5a is missing.", "The workup and purification for these alcohol variants are not reported in the table.", "Supporting information was not supplied or explicitly associated."],
    ))


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
