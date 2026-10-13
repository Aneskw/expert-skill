"""Build the source-derived machine records for PDF pages 1--6."""
import json
from pathlib import Path

DOC = "doc_4cb5cdc97ea07a54"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def facts(page, value):
    return {"value": value, "evidence_ids": ev(page) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def field(page, name, value, targets=None):
    item = {"name": name, "fact": facts(page, value)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def qty(number, unit, raw_text=None, qualifier=None):
    value = {"number": number, "unit": unit}
    if raw_text:
        value["raw_text"] = raw_text
    if qualifier:
        value["qualifier"] = qualifier
    return value


def part(page, entity_id, role, label, name=None, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": facts(page, label),
        "name": facts(page, name),
        "smiles": facts(page, smiles),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def amount(page, number, unit, name="amount"):
    return field(page, name, qty(number, unit))


def record(suffix, kind, pages, participants, conditions, outcomes, unresolved, notes=None):
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{"step_id": "reaction", "participant_ids": [p["entity_id"] for p in participants],
                   "conditions": conditions}],
        "outcomes": outcomes,
        "notes": notes or [],
        "review": {"method": "none", "reviewer": None, "checked_fields": [],
                   "unresolved": unresolved},
    }


records = []

# Table 1: solvent optimization. Page 1 prose and page 2 table describe the same rows.
t1 = [
    (1, "CH3CN", 0.6, 87, None),
    (2, "toluene", 1, 65, None),
    (3, "DCE", 1.5, 38, 45),
    (4, "THF", 1.5, 95, None),
    (5, "DMSO", 1, 66, None),
    (6, "DMF", 1, 66, None),
    (7, "CH3NO2", 16, 68, None),
    (8, "dioxane", 1.5, 84, None),
    (9, "MeOH", 1.5, None, None),
    (10, "HOAc", 1.5, None, None),
]
solvent_smiles = {"CH3CN": "CC#N", "toluene": "Cc1ccccc1", "DCE": "ClCCCl",
                  "THF": "C1CCOC1", "DMSO": "CS(C)=O", "DMF": "CN(C)C=O",
                  "CH3NO2": "C[N+](=O)[O-]", "dioxane": "O1CCOCC1",
                  "MeOH": "CO", "HOAc": "CC(=O)O"}
for entry, solvent, time_h, yield_pct, recovery in t1:
    pages = [1, 2]
    participants = [
        part(2, "reactant_1a", "reactant", "1a", "ethyl 2-acetyl-4,5-hexadienoate",
             [amount(2, 0.2, "mmol")]),
        part(2, "reactant_2a", "reactant", "2a", "propargylic carbonate 2a",
             [amount(2, 0.2, "mmol")]),
        part(2, "catalyst_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
             [amount(2, 5, "mol%")]),
        part(2, "additive_tbai", "reagent", "TBAI", "tetrabutylammonium iodide",
             [amount(2, 10, "mol%")]),
        part(2, "solvent", "solvent", solvent, solvent, [amount(2, 2, "mL", "volume")],
             solvent_smiles[solvent]),
        part(2, "product_3aa", "product", "3aa",
             "3-(ethoxycarbonyl)-2-methyl-5-(5-methyl-3-phenyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    ]
    conditions = [field(2, "time", qty(time_h, "h")), field(2, "temperature", qty(80, "°C")),
                  field(2, "solvent", solvent)]
    outcomes = []
    if yield_pct is not None:
        outcomes.append(field(2, "reported_yield_3aa", qty(yield_pct, "%"), ["product_3aa"]))
        basis = "1H NMR yield using dibromomethane as internal standard" if entry == 3 else "isolated yield"
        outcomes.append(field(2, "yield_measurement_basis", basis, ["product_3aa"]))
    else:
        outcomes.extend([field(2, "reaction_result", "complicated"),
                         field(2, "starting_material_consumption", "starting materials completely consumed")])
    if recovery is not None:
        outcomes.append(field(2, "recovered_starting_material_yield", qty(recovery, "%"), ["reactant_1a"]))
    if entry == 1:
        outcomes.append(field(1, "selectivity_observation",
                              "3aa was the only product; 4aa, 5aa, and 6aa were not observed",
                              ["product_3aa"]))
    records.append(record(f"table1_entry{entry}", "optimization_entry", pages, participants,
                          conditions, outcomes,
                          ["Reactant and product structures were not encoded from the drawings.",
                           "Supporting information was not explicitly supplied or associated."]))


# Scheme 2: phase-transfer/additive optimization. Four displayed rows are independent experiments.
scheme2 = [("tbai", "TBAI", "tetrabutylammonium iodide", 1.5, 95),
           ("tbab", "TBAB", "tetrabutylammonium bromide", 2, 71),
           ("tbac", "TBAC", "tetrabutylammonium chloride", 2, 66),
           ("none", None, None, 2.5, 76)]
for suffix, label, name, time_h, yield_pct in scheme2:
    participants = [
        part(2, "reactant_1a", "reactant", "1a", "ethyl 2-acetyl-4,5-hexadienoate",
             [amount(2, 1, "equiv", "equivalents"), amount(2, 0.2, "mmol")]),
        part(2, "reactant_2a", "reactant", "2a", "propargylic carbonate 2a",
             [amount(2, 1, "equiv", "equivalents"), amount(2, 0.2, "mmol")]),
        part(2, "catalyst_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
             [amount(2, 5, "mol%")]),
        part(2, "solvent_thf", "solvent", "THF", "tetrahydrofuran", smiles="C1CCOC1"),
        part(2, "product_3aa", "product", "3aa",
             "3-(ethoxycarbonyl)-2-methyl-5-(5-methyl-3-phenyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    ]
    if label:
        participants.insert(3, part(2, f"additive_{suffix}", "reagent", label, name,
                                    [amount(2, 10, "mol%")]))
    conditions = [field(2, "time", qty(time_h, "h")), field(2, "temperature", "reflux"),
                  field(2, "solvent", "THF")]
    outcomes = [field(2, "isolated_yield_3aa", qty(yield_pct, "%"), ["product_3aa"]),
                field(2, "yield_measurement_basis", "isolated yield", ["product_3aa"])]
    records.append(record(f"scheme2_{suffix}", "optimization_entry", [2], participants, conditions,
                          outcomes, ["Reactant and product structures were not encoded from the drawings.",
                                     "Supporting information was not explicitly supplied or associated."]))


# Table 2, reconciled with the matching detailed preparations in sections 4.2.1--4.2.13.
scope = [
    (1, "1a", 35, .19, "2a", 45, .21, 12, .010, 7, .019, 100, 59, 95, "3aa", 3, "reflux", "15:1 (eluent precooled at -20 °C)", "3-(ethoxycarbonyl)-2-methyl-5-(5-methyl-3-phenyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    (2, "1a", 33, .18, "2b", 28, .20, 12, .010, 7, .019, 43, 37, 82, "3ab", 3, "reflux", "20:1", "3-(ethoxycarbonyl)-2-methyl-5-(5-methyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    (3, "1a", 33, .18, "2c", 34, .19, 12, .010, 7, .019, 43, 39, 75, "3ac", 4, "reflux", "10:1", "3-(ethoxycarbonyl)-2-methyl-5-(5,5-pentamethylene-1,3,4-pentatrien-2-yl)-4,5-dihydrofuran"),
    (4, "1a", 31, .17, "2d", 31, .18, 13, .011, 9, .024, 65, 45, 96, "3ad", 4, qty(80, "°C"), "20:1", "3-(ethoxycarbonyl)-5-(5-ethyl-1,3,4-heptatrien-2-yl)-2-methyl-4,5-dihydrofuran"),
    (5, "1b", 41, .21, "2c", 43, .24, 13, .011, 9, .024, 40, 50, 79, "3bc", 4, "reflux", "20:1", "2-isopropyl-3-(methoxycarbonyl)-5-(5,5-pentamethylene-1,3,4-pentatrien-2-yl)-4,5-dihydrofuran"),
    (6, "1a", 36, .20, "2e", 40, .20, 12, .010, 8, .022, 50, 45, 74, "3ae", 4, "reflux", "10:1", "3-(ethoxycarbonyl)-2-methyl-5-(3-(methoxycarbonyl)-5-methyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    (7, "1a", 36, .20, "2f", 42, .21, 13, .011, 7, .019, 54, 51, 85, "3af", 4, "reflux", "20:1", "5-(3-butyl-5-methyl-1,3,4-hexatrien-2-yl)-3-(ethoxycarbonyl)-2-methyl-4,5-dihydrofuran"),
    (8, "1a", 35, .19, "2g", 56, .20, 12, .010, 8, .022, 70, 67, 89, "3ag", 4, "reflux", "20:1", "3-(ethoxycarbonyl)-2-methyl-5-(5-methyl-3-(tert-butyldimethylsilyloxy)methyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    (9, "1b", 38, .19, "2f", 40, .20, 12, .010, 7, .019, 60, 57, 92, "3bf", 4, "reflux", "20:1", "5-(3-butyl-5-methyl-1,3,4-hexatrien-2-yl)-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran"),
    (10, "1b", 37, .19, "2b", 27, .19, 12, .010, 7, .019, 28, 32, 65, "3bb", 4, "reflux", "20:1", "2-isopropyl-3-(methoxycarbonyl)-5-(5-methyl-1,3,4-hexatrien-2-yl)-4,5-dihydrofuran"),
    (11, "1c", 59, .21, "2d", 35, .21, 12, .010, 7, .019, 50, 59, 80, "3cd", 5, "reflux", "20:1", "5-benzyl-2-isopropyl-5-(5-ethyl-1,3,4-heptatrien-2-yl)-3-(methoxycarbonyl)-4,5-dihydrofuran"),
    (12, "1c", 61, .21, "2c", 37, .20, 12, .010, 7, .019, 75, 60, 75, "3cc", 5, "reflux", "20:1", "5-benzyl-2-isopropyl-3-(methoxycarbonyl)-5-(5,5-pentamethylene-1,3,4-pentatrien-2-yl)-4,5-dihydrofuran"),
    (13, "1d", 37, .22, "2d", 38, .22, 12, .010, 7, .019, 43, 48, 83, "3dd", 5, "reflux", "20:1", "5-(5-ethyl-1,3,4-heptatrien-2-yl)-2-methyl-3-(methoxycarbonyl)-4,5-dihydrofuran"),
]
for row in scope:
    (entry, r1, r1mg, r1mmol, r2, r2mg, r2mmol, pdmg, pdmmol, taim, taimmol,
     time_min, pmg, ypct, prod, detail_page, temperature, eluent, product_name) = row
    participants = [
        part(detail_page, "reactant_1", "reactant", r1, None,
             [amount(detail_page, r1mg, "mg", "mass"), amount(detail_page, r1mmol, "mmol")]),
        part(detail_page, "reactant_2", "reactant", r2, f"propargylic carbonate {r2}",
             [amount(detail_page, r2mg, "mg", "mass"), amount(detail_page, r2mmol, "mmol")]),
        part(detail_page, "catalyst_pd", "catalyst", "Pd(PPh3)4", "tetrakis(triphenylphosphine)palladium(0)",
             [amount(detail_page, pdmg, "mg", "mass"), amount(detail_page, pdmmol, "mmol")]),
        part(detail_page, "additive_tbai", "reagent", "TBAI", "tetrabutylammonium iodide",
             [amount(detail_page, taim, "mg", "mass"), amount(detail_page, taimmol, "mmol")]),
        part(detail_page, "solvent_thf", "solvent", "THF", "tetrahydrofuran",
             [amount(detail_page, 2, "mL", "volume")], "C1CCOC1"),
        part(detail_page, "product", "product", prod, product_name,
             [amount(detail_page, pmg, "mg", "mass")]),
    ]
    temperature_page = detail_page if entry == 4 else 2
    conditions = [field(2, "time", qty(time_min, "min")), field(temperature_page, "temperature", temperature),
                  field(detail_page, "solvent", "THF"), field(3, "atmosphere", "argon"),
                  field(detail_page, "purification", f"silica gel chromatography; petroleum ether/ethyl acetate {eluent}")]
    if entry == 1:
        conditions.extend([field(3, "operation", "reagents added sequentially to a flame-dried Schlenk tube"),
                           field(3, "workup", "solvent evaporated under vacuum after completion")])
    outcomes = [field(detail_page, f"isolated_yield_{prod}", qty(ypct, "%"), ["product"]),
                field(detail_page, "yield_measurement_basis", "isolated yield", ["product"])]
    records.append(record(f"table2_entry{entry}", "substrate_scope_entry", [2, detail_page] if detail_page != 2 else [2],
                          participants, conditions, outcomes,
                          ["Starting-material structures were not encoded from the drawings.",
                           "Supporting information was mentioned by the article but was not explicitly supplied or associated."]))


# Table 3, reconciled with sections 4.3.1--4.3.7.
pk = [
    (1, "3bb", 26, .099, 1, .0026, "7a", 26, 90, 5, qty(3, "h"), "4-(2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran-5-yl)-2-(isopropylidene)cyclopent-3-enone"),
    (2, "3cd", 46, .12, 1, .0026, "7b", 44, 89, 5, qty(3, "h"), "4-(5-benzyl-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran-5-yl)-2-(1-ethylpropylidene)cyclopent-3-enone"),
    (3, "3cc", 36, .092, 1, .0026, "7c", 37, 96, 5, {"number": 1, "unit": "h", "qualifier": "le", "raw_text": "within 1 h"}, "4-(5-benzyl-2-isopropyl-3-(methoxycarbonyl)-4,5-dihydrofuran-5-yl)-2-(1-cyclohexylidene)cyclopent-3-enone"),
    (4, "3ad", 28, .10, 1, .0026, "7d", 26, 84, 5, qty(3, "h"), "4-(3-(ethoxycarbonyl)-2-methyl-4,5-dihydrofuran-5-yl)-2-(1-ethylpropylidene)cyclopent-3-enone"),
    (5, "3af", 44, .14, 1, .0026, "7e", 34, 71, 5, {"number": 48, "unit": "h", "qualifier": "le", "raw_text": "complete within 48 h"}, "3-butyl-4-(3-(ethoxycarbonyl)-2-methyl-4,5-dihydrofuran-5-yl)-2-(isopropylidene)cyclopent-3-enone"),
    (6, "3aa", 32, .10, 1, .0026, "7f", 28, 81, 6, {"number": 48, "unit": "h", "qualifier": "le", "raw_text": "complete within 48 h"}, "4-(3-(ethoxycarbonyl)-2-methyl-4,5-dihydrofuran-5-yl)-2-(isopropylidene)-3-phenylcyclopent-3-enone"),
    (7, "3dd", 45, .17, 2, .0051, "7g", 44, 88, 6, qty(3, "h"), "2-(1-ethylpropylidene)-4-(2-methyl-3-(methoxycarbonyl)-4,5-dihydrofuran-5-yl)-cyclopent-3-enone"),
]
for entry, substrate, smg, smmol, catmg, catmmol, prod, pmg, ypct, page, time_value, product_name in pk:
    participants = [
        part(page, "substrate", "reactant", substrate, None,
             [amount(page, smg, "mg", "mass"), amount(page, smmol, "mmol")]),
        part(page, "carbon_monoxide", "reactant", "CO", "carbon monoxide", smiles="[C-]#[O+]"),
        part(page, "catalyst_rh", "catalyst", "[RhCl(CO)2]2", "dicarbonylchlororhodium(I) dimer",
             [amount(page, catmg, "mg", "mass"), amount(page, catmmol, "mmol")]),
        part(page, "solvent_dce", "solvent", "DCE", "1,2-dichloroethane",
             [amount(page, 2, "mL", "volume")], "ClCCCl"),
        part(page, "product", "product", prod, product_name, [amount(page, pmg, "mg", "mass")]),
    ]
    conditions = [field(3, "time", time_value), field(3, "temperature", "r.t."),
                  field(3, "atmosphere", "CO, 1 atm"), field(page, "solvent", "DCE")]
    if entry == 1:
        conditions.extend([field(5, "operation", "CO introduced by balloon; completion monitored by TLC"),
                           field(5, "workup", "solvent evaporated under vacuum"),
                           field(5, "purification", "flash chromatography on silica gel; petroleum ether/ethyl acetate 10:1")])
    outcomes = [field(page, f"isolated_yield_{prod}", qty(ypct, "%"), ["product"]),
                field(3, "yield_measurement_basis", "isolated yield", ["product"])]
    unresolved = ["Substrate and product structures were not encoded from the drawings."]
    if entry != 1:
        unresolved.append("Workup and purification are unstated for this abbreviated preparation.")
    unresolved.append("Supporting information was mentioned by the article but was not explicitly supplied or associated.")
    records.append(record(f"table3_entry{entry}", "substrate_scope_entry", [3, page] if page != 3 else [3],
                          participants, conditions, outcomes, unresolved))


assert len(records) == 34
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {OUT}")
