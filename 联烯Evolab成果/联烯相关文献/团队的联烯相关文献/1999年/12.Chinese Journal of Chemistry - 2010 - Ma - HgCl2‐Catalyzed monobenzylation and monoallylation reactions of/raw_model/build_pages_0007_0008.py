#!/usr/bin/env python3
"""Build page-7/8 updates for the HgCl2 monolithiation paper.

The detailed preparations on page 7 and the control procedure on page 8
continue experiments already represented in dataset.json.  This script emits
replacement records with the same IDs so the existing merge tool updates them
without creating cross-page duplicates.
"""
import copy
import json
from pathlib import Path


DOC = "doc_aef3035bf01be80f"
HERE = Path(__file__).resolve().parent
DATASET = HERE.parent / "dataset.json"
OUT_RECORDS = HERE / "records_pages_0007_0008.json"
OUT_COVERAGE = HERE.parent / "coverage" / "pages_0007_0008.json"


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def unique(items):
    return list(dict.fromkeys(items))


data = json.loads(DATASET.read_text())
indexed = {record["record_id"]: copy.deepcopy(record) for record in data["experiments"]}


def get(suffix):
    return indexed[f"{DOC}:{suffix}"]


def participant(record, suffix):
    wanted = f"{record['record_id'].split(':', 1)[1]}_{suffix}"
    return next(p for p in record["participants"] if p["entity_id"] == wanted)


def set_amounts(p, values, evidence):
    p["amounts"] = [field(name, value, evidence) for name, value in values]


def add_note(record, value, evidence):
    if not any(note.get("value") == value for note in record["notes"]):
        record["notes"].append(fact(value, evidence))


page7 = ev(7)
page8 = ev(8)
updates = []

# Table 1 entries 6-9: merge page-7 detailed preparation and characterization
# with the already extracted table rows on page 3.
details = {
    6: {
        "product4": "3,5-dimethyl-1-phenyl-5-hexen-1-yne",
        "product5": "2-methyl-4-phenyl-1,4,5-heptatriene",
        "substrate": [("mass", {"number": 130, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})],
        "halide": [("mass", {"number": 107, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"})],
        "masses": (66, 92),
    },
    7: {
        "product4": "3-(n-propyl)-1-phenyl-5-hexen-1-yne",
        "product5": "4-phenyl-1,4,5-nonatriene",
        "substrate": [("mass", {"number": 158, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})],
        "halide": [("mass", {"number": 145, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"})],
        "masses": (59, 105),
    },
    8: {
        "product4": "5-methyl-3-(n-propyl)-1-phenyl-5-hexen-1-yne",
        "product5": "2-methyl-4-phenyl-1,4,5-nonatriene",
        "substrate": [("mass", {"number": 128, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})],
        "halide": [("mass", {"number": 107, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"})],
        "masses": (68, 102),
    },
    9: {
        "product4": "1-phenyl-3-benzyl-1-hexyne",
        "product5": "1,4-diphenyl-1,4,5-heptatriene",
        "substrate": [("mass", {"number": 206, "unit": "mg"}), ("amount", {"number": 1.0, "unit": "mmol"})],
        "halide": [("mass", {"number": 145, "unit": "mg"}), ("amount", {"number": 1.2, "unit": "mmol"})],
        "masses": (69, 118),
    },
}

for row, detail in details.items():
    rec = get(f"table1_entry{row}")
    rec["status"] = "candidate"
    rec["evidence_ids"] = unique(rec["evidence_ids"] + page7 + (page8 if row == 9 else []))
    sub = participant(rec, "substrate")
    hg = participant(rec, "hgcl2")
    nb = participant(rec, "nbuli")
    halide = participant(rec, "allyl_halide")
    p4 = participant(rec, "product4")
    p5 = participant(rec, "product5")
    set_amounts(sub, detail["substrate"], page7)
    set_amounts(hg, [
        ("mass", {"number": 4, "unit": "mg"}),
        ("catalyst_loading", {"number": 1.5, "unit": "mol%"}),
    ], page7)
    set_amounts(nb, [
        ("concentration", {"number": 1.6, "unit": "mol/L"}),
        ("solution_volume", {"number": 0.63, "unit": "mL"}),
        ("amount", {"number": 1.0, "unit": "mmol"}),
    ], page7)
    set_amounts(halide, detail["halide"], page7)
    p4["name"] = fact(detail["product4"], page7)
    p5["name"] = fact(detail["product5"], page7)
    generated_outcomes = {
        f"isolated_mass_4{'fghi'[row - 6]}",
        f"isolated_mass_5{'fghi'[row - 6]}",
        "detailed_preparation_reported_yield_4i",
    }
    rec["outcomes"] = [item for item in rec["outcomes"] if item["name"] not in generated_outcomes]
    rec["outcomes"].extend([
        field(f"isolated_mass_4{'fghi'[row - 6]}", {"number": detail["masses"][0], "unit": "mg"}, page7),
        field(f"isolated_mass_5{'fghi'[row - 6]}", {"number": detail["masses"][1], "unit": "mg"}, page7),
    ])
    add_note(rec,
        "Page 7 supplies the compound heading, exact reagent charges, isolated masses, and characterization for this existing Table 1 experiment; it is merged rather than counted again.",
        page7,
    )
    rec["review"]["unresolved"] = [
        "Atmosphere, reaction concentration, row-specific solvent volume, workup, and purification are not restated for this individual run.",
        "No SI was supplied or explicitly associated; missing experimental details remain unavailable.",
        "Participant structures are retained as source labels/names; no SMILES has been verified.",
    ]
    if row == 7:
        add_note(rec,
            "Source conflict retained: the heading/products and Table 1 identify the n-propyl (1c) series, but the page-7 charge sentence visibly prints '1-phenyl-1-butyne (158 mg, 1.0 mmol)'.",
            page7,
        )
        rec["review"]["unresolved"].append(
            "The page-7 printed substrate name conflicts with the Table 1 identity, product heading, and 158 mg charge; it was not silently corrected."
        )
    if row == 8:
        add_note(rec,
            "Source conflict retained: the heading/products and Table 1 identify the n-propyl (1c) series, but the page-7 charge sentence visibly prints '1-phenyl-1-butyne (128 mg, 1.0 mmol)'.",
            page7,
        )
        rec["review"]["unresolved"].append(
            "The page-7 printed substrate name and 128 mg charge conflict with the Table 1 identity and n-propyl product heading; neither value was normalized."
        )
    if row == 9:
        rec["outcomes"].append(field("detailed_preparation_reported_yield_4i", {"number": 25, "unit": "%"}, page7))
        add_note(
            rec,
            "Source conflict retained: Table 1 reports 4i at 28%, whereas the page-7 detailed paragraph prints 69 mg (25%); both source values are recorded.",
            ev(3, 7),
        )
        add_note(
            rec,
            "The 5i characterization continues at the top of page 8; it is not a separate reaction run.",
            page8,
        )
        rec["review"]["unresolved"].append(
            "The 4i yield discrepancy (Table 1: 28%; detailed paragraph: 25%) is unresolved."
        )
    updates.append(rec)


# Page 8 gives the full procedure for the Scheme 4 no-coupling control.
rec = get("scheme4_allyl_bromide_control")
rec["status"] = "candidate"
rec["evidence_ids"] = unique(rec["evidence_ids"] + page8)
mercury = next(p for p in rec["participants"] if p["entity_id"] == "scheme4_control_mercury")
allyl = next(p for p in rec["participants"] if p["entity_id"] == "scheme4_control_allyl_bromide")
thf = next(p for p in rec["participants"] if p["entity_id"] == "scheme4_control_thf")
set_amounts(mercury, [
    ("mass", {"number": 20, "unit": "mg"}),
    ("amount", {"number": 0.05, "unit": "mmol"}),
], page8)
set_amounts(allyl, [
    ("mass", {"number": 7.3, "unit": "mg"}),
    ("amount", {"number": 0.06, "unit": "mmol"}),
], page8)
set_amounts(thf, [("volume", {"number": 5, "unit": "mL"})], page8)
rec["steps"] = [
    {
        "step_id": "coupling_attempt",
        "participant_ids": [mercury["entity_id"], allyl["entity_id"], thf["entity_id"]],
        "conditions": [
            field("allyl_bromide_addition_temperature", {"number": -78, "unit": "°C"}, page8),
            field("warming", "allowed to warm naturally to room temperature", page8),
            field("time_at_room_temperature", {"number": 10, "unit": "h"}, page8),
        ],
    },
    {
        "step_id": "workup_and_analysis",
        "participant_ids": [mercury["entity_id"], allyl["entity_id"], thf["entity_id"]],
        "conditions": [
            field("quench", "saturated NH4Cl", page8),
            field("extraction", "petroleum ether (60-90 °C)", page8),
            field("wash", "saturated NaCl", page8),
            field("drying", "MgSO4", page8),
            field("post_drying_operations", "filtering and solvent removal", page8),
            field("analysis", "crude product analyzed by 1H NMR", page8),
        ],
    },
]
rec["outcomes"] = [
    field("cross_coupling_products_4a_and_5a", "not detected", page8),
    field("recovered_organomercury_yield", {"number": 90, "unit": "%"}, page8),
    field("recovery_yield_measurement_basis", "1H NMR using CH2Br2 as internal standard", page8),
]
add_note(rec,
    "The page-8 heading says '3-phenyl-3-propargyl mercury bromide', while the procedure abbreviates the reactant as 'propargyl mercury bromide'; the previously retained source-local organomercury name remains unverified.",
    page8,
)
rec["review"]["unresolved"] = [
    "The organomercury reactant nomenclature is inconsistent across the heading, procedure, and earlier prose; its structure remains unverified and SMILES is null.",
    "Atmosphere, reaction concentration, extraction count/volumes, wash count/volume, and detection limit for 4a/5a are not reported.",
    "No chromatographic purification is reported; only crude-product 1H NMR analysis and NMR recovery yield are stated.",
    "No SI was supplied or explicitly associated.",
]
updates.append(rec)


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper section, continuation of monoallylation preparation (b): 4f/5f",
                    "finding": "Detailed charges and isolated masses/yields for existing Table 1 entry 6, followed by characterization; merged into the existing record.",
                    "evidence_ids": page7,
                },
                {
                    "region": "middle section (c): 4g/5g",
                    "finding": "Detailed charges and isolated masses/yields for existing Table 1 entry 7; the printed substrate name conflicts with the n-propyl heading/Table 1 and is retained as unresolved.",
                    "evidence_ids": page7,
                },
                {
                    "region": "lower-middle section (d): 4h/5h",
                    "finding": "Detailed charges and isolated masses/yields for existing Table 1 entry 8; the printed substrate name/mass conflicts with the n-propyl heading/Table 1 and is retained as unresolved.",
                    "evidence_ids": page7,
                },
                {
                    "region": "bottom section (e): 4i/5i",
                    "finding": "Detailed charges, masses, and yields for existing Table 1 entry 9; 4i is printed as 25% here versus 28% in Table 1, and 5i characterization continues on page 8.",
                    "evidence_ids": page7,
                },
            ],
            "record_ids": [f"{DOC}:table1_entry{i}" for i in range(6, 10)],
            "unresolved": [
                "Entries 7 and 8 contain visible substrate-identity/charge conflicts against their headings and Table 1.",
                "Entry 9 reports 4i at 25% in the detailed paragraph but 28% in Table 1.",
                "The individual procedures do not restate atmosphere, complete solvent details, workup, or purification.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "top two lines",
                    "finding": "Continuation of 5i characterization from page 7; not a new experiment.",
                    "evidence_ids": page8,
                },
                {
                    "region": "heading and procedure above References",
                    "finding": "Full current-paper no-coupling control: organomercury reagent plus allyl bromide in THF, -78 °C to room temperature, 10 h; no 4a/5a detected and 90% starting organomercury recovered by 1H NMR with CH2Br2 internal standard.",
                    "evidence_ids": page8,
                },
                {
                    "region": "References section",
                    "finding": "Bibliographic references only; no additional current-paper experiment instantiated.",
                    "evidence_ids": page8,
                },
            ],
            "record_ids": [
                f"{DOC}:table1_entry9",
                f"{DOC}:scheme4_allyl_bromide_control",
            ],
            "unresolved": [
                "The organomercury reagent name varies between the heading and procedure; structure remains unverified.",
                "The source gives no atmosphere, detection limit, or detailed extraction/wash volumes for the control.",
                "No SI is supplied or explicitly associated.",
            ],
        },
    ],
}

OUT_RECORDS.write_text(json.dumps(updates, ensure_ascii=False, indent=2) + "\n")
OUT_COVERAGE.parent.mkdir(parents=True, exist_ok=True)
OUT_COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({
    "updated_records": len(updates),
    "record_ids": [record["record_id"] for record in updates],
    "coverage_pages": [page["page"] for page in coverage["pages"]],
}, ensure_ascii=False))
