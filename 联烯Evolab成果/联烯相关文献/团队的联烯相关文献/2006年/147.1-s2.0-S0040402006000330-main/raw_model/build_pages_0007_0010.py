#!/usr/bin/env python3
"""Enrich existing experiment records with source evidence from PDF pages 7-10."""

import copy
import json
from pathlib import Path


DOC = "doc_5fa965aae5d3692a"
HERE = Path(__file__).resolve().parent
RUN = HERE.parent
DATASET = RUN / "dataset.json"
OUT = HERE / "pages_0007_0010_records.json"
COVERAGE = RUN / "coverage" / "pages_0007_0010.json"


def evid(*pages):
    return [item for page in pages for item in (
        f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"
    )]


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(dict.fromkeys(ev)),
        "verification": "missing" if value is None else "unreviewed",
    }


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def rng(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


data = json.loads(DATASET.read_text())
all_records = {r["record_id"]: r for r in data["experiments"]}

suffixes = [
    "table2_entry3_12c", "table2_entry4_12d", "table2_entry5_12e", "table2_entry6_12f",
    "table3_entry2_13b", "table3_entry3_13c", "table3_entry4_13d", "table3_entry5_13e",
    "table3_entry6_13f", "table3_entry7_13g", "scheme3_13l_13lprime",
    "table3_entry8_13h", "table3_entry9_13i", "table3_entry10_13j", "table3_entry11_13k",
    "scheme4_cyclobutyl_14", "scheme4_cyclohexyl_15",
]
records = []
for suffix in suffixes:
    rid = f"{DOC}:{suffix}"
    if rid not in all_records:
        raise RuntimeError(f"Expected existing record is missing: {rid}")
    rec = copy.deepcopy(all_records[rid])
    rec["status"] = "candidate"
    rec["review"]["method"] = "none"
    rec["review"]["reviewer"] = None
    rec["review"]["checked_fields"] = []
    records.append(rec)

by_suffix = {r["record_id"].split(":", 1)[1]: r for r in records}


def rec(suffix):
    return by_suffix[suffix]


def participant(record, entity_id):
    return next(p for p in record["participants"] if p["entity_id"] == entity_id)


def add_record_evidence(record, pages):
    record["evidence_ids"] = list(dict.fromkeys(record["evidence_ids"] + evid(*pages)))


def add_amount(record, entity_id, name, value, pages):
    p = participant(record, entity_id)
    candidate = {"name": name, "fact": fact(value, evid(*pages))}
    def same(item):
        return (
            item["name"] == name
            and item["fact"]["value"] == value
            and set(item["fact"]["evidence_ids"]) == set(evid(*pages))
        )
    if not any(same(x) for x in p["amounts"]):
        p["amounts"].append(candidate)


def set_product(record, entity_id, name, smiles, pages):
    p = participant(record, entity_id)
    p["name"] = fact(name, evid(*pages))
    if smiles is not None:
        p["smiles"] = fact(smiles, evid(*pages))
    p["structure_verified"] = False


def set_yield_basis(record, product_ids, pages):
    record["outcomes"] = [o for o in record["outcomes"] if o["name"] != "yield_measurement_basis"]
    record["outcomes"].append({
        "name": "yield_measurement_basis",
        "fact": fact("isolated product; recovered mass and percentage are reported", evid(*pages)),
        "target_entity_ids": list(product_ids),
    })


def add_yield_evidence(record, pages):
    page_evidence = evid(*pages)
    for outcome in record["outcomes"]:
        if "yield" in outcome["name"] and outcome["name"] != "yield_measurement_basis":
            outcome["fact"]["evidence_ids"] = list(dict.fromkeys(
                outcome["fact"]["evidence_ids"] + page_evidence
            ))


def add_outcome(record, name, value, product_ids, pages):
    item = {
        "name": name,
        "fact": fact(value, evid(*pages)),
        "target_entity_ids": list(product_ids),
    }
    def same(existing):
        return (
            existing["name"] == name
            and existing["fact"]["value"] == value
            and set(existing["fact"]["evidence_ids"]) == set(evid(*pages))
            and existing.get("target_entity_ids", []) == list(product_ids)
        )
    if not any(same(x) for x in record["outcomes"]):
        record["outcomes"].append(item)


def keep_unresolved(record, fragments_to_remove):
    record["review"]["unresolved"] = [
        text for text in record["review"]["unresolved"]
        if not any(fragment in text for fragment in fragments_to_remove)
    ]


def enrich_table2(suffix, entry, product_name, product_smiles, page, values, mp=None):
    r = rec(suffix)
    prefix = f"t2e{entry}"
    add_record_evidence(r, [page])
    for entity_end, name, value in values:
        add_amount(r, prefix + entity_end, name, value, [page])
    set_product(r, prefix + "_prod", product_name, product_smiles, [page])
    add_yield_evidence(r, [page])
    set_yield_basis(r, [prefix + "_prod"], [page])
    if mp:
        add_outcome(r, "melting_point", rng(mp[0], mp[1], "°C", f"{mp[0]}-{mp[1]} °C"), [prefix + "_prod"], [page])
    keep_unresolved(r, ["Transmetallation and cross-coupling durations"])
    if not any("Cross-coupling completion time is not numerically reported" in text for text in r["review"]["unresolved"]):
        r["review"]["unresolved"].append("Cross-coupling completion time is not numerically reported in the detailed paragraph.")


common_t2 = [
    ("_nbu", "volume", qty(0.30, "mL")),
    ("_nbu", "amount", qty(0.48, "mmol")),
    ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")),
    ("_znbr2", "amount", qty(0.80, "mmol")),
]
enrich_table2(
    "table2_entry3_12c", 3,
    "1-phenyl-1-(4'-methoxyphenyl)-3-methylbuta-1,2-diene",
    "CC(C)=C=C(c1ccccc1)c1ccc(OC)cc1", 7,
    [("_sub", "mass", qty(58, "mg")), ("_sub", "amount", qty(0.40, "mmol"))] + common_t2 + [
        ("_pd", "mass", qty(16, "mg")), ("_electrophile", "mass", qty(63, "mg")),
        ("_electrophile", "amount", qty(0.27, "mmol")), ("_prod", "mass", qty(48, "mg")),
    ], mp=(45, 46),
)
enrich_table2(
    "table2_entry4_12d", 4,
    "1-phenyl-1-(4'-methoxycarbonylphenyl)-3-methylbuta-1,2-diene",
    "CC(C)=C=C(c1ccccc1)c1ccc(C(=O)OC)cc1", 7,
    [("_sub", "mass", qty(58, "mg")), ("_sub", "amount", qty(0.40, "mmol"))] + common_t2 + [
        ("_pd", "mass", qty(8, "mg")), ("_electrophile", "mass", qty(35, "mg")),
        ("_electrophile", "amount", qty(0.13, "mmol")), ("_prod", "mass", qty(33, "mg")),
    ],
)
enrich_table2(
    "table2_entry5_12e", 5,
    "1-phenyl-1-(2'-methylphenyl)-3-methylbuta-1,2-diene",
    "CC(C)=C=C(c1ccccc1)c1ccccc1C", 7,
    [("_sub", "mass", qty(57, "mg")), ("_sub", "amount", qty(0.40, "mmol"))] + common_t2 + [
        ("_pd", "mass", qty(16, "mg")), ("_electrophile", "volume", qty(34, "uL")),
        ("_electrophile", "amount", qty(0.27, "mmol")), ("_prod", "mass", qty(25, "mg")),
    ],
)
enrich_table2(
    "table2_entry6_12f", 6,
    "1-phenyl-1-(E-methoxycarbonylethenyl)-3-methylbuta-1,2-diene",
    "CC(C)=C=C(c1ccccc1)/C=C/C(=O)OC", 7,
    [("_sub", "mass", qty(58, "mg")), ("_sub", "amount", qty(0.40, "mmol"))] + common_t2 + [
        ("_pd", "mass", qty(16, "mg")), ("_electrophile", "mass", qty(57, "mg")),
        ("_electrophile", "amount", qty(0.27, "mmol")), ("_prod", "mass", qty(23, "mg")),
    ],
)


def enrich_table3(suffix, entry, product_name, pages, values, mp=None):
    r = rec(suffix)
    prefix = f"t3e{entry}"
    add_record_evidence(r, pages)
    for entity_end, name, value in values:
        add_amount(r, prefix + entity_end, name, value, pages)
    set_product(r, prefix + "_prod", product_name, participant(r, prefix + "_prod")["smiles"]["value"], pages)
    add_yield_evidence(r, pages)
    set_yield_basis(r, [prefix + "_prod"], pages)
    if mp:
        add_outcome(r, "melting_point", rng(mp[0], mp[1], "°C", f"{mp[0]}-{mp[1]} °C"), [prefix + "_prod"], pages)


enrich_table3("table3_entry2_13b", 2, "1-(phenylethynyl)-1-(1'-naphthyl)cyclopropane", [7], [
    ("_sub", "mass", qty(56, "mg")), ("_sub", "amount", qty(0.39, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.47, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")),
    ("_pd", "mass", qty(15, "mg")), ("_electrophile", "volume", qty(38, "uL")),
    ("_electrophile", "amount", qty(0.26, "mmol")), ("_prod", "mass", qty(19, "mg")),
])
enrich_table3("table3_entry3_13c", 3, "1-(phenylethynyl)-1-(2'-methylphenyl)cyclopropane", [7, 8], [
    ("_sub", "mass", qty(56, "mg")), ("_sub", "amount", qty(0.39, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.47, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")),
    ("_pd", "mass", qty(15, "mg")), ("_electrophile", "volume", qty(33, "uL")),
    ("_electrophile", "amount", qty(0.26, "mmol")), ("_prod", "mass", qty(15, "mg")),
])
enrich_table3("table3_entry4_13d", 4, "1-(phenylethynyl)-1-(4'-methoxycarbonylphenyl)cyclopropane", [8], [
    ("_sub", "mass", qty(56, "mg")), ("_sub", "amount", qty(0.39, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.47, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(178, "mg")), ("_znbr2", "amount", qty(0.79, "mmol")),
    ("_pd", "mass", qty(8, "mg")), ("_electrophile", "mass", qty(34, "mg")),
    ("_electrophile", "amount", qty(0.13, "mmol")), ("_prod", "mass", qty(35, "mg")),
], mp=(79, 81))
enrich_table3("table3_entry5_13e", 5, "1-(phenylethynyl)-1-(4'-cyanophenyl)cyclopropane", [8], [
    ("_sub", "mass", qty(56, "mg")), ("_sub", "amount", qty(0.39, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.47, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")),
    ("_pd", "mass", qty(8, "mg")), ("_electrophile", "mass", qty(31, "mg")),
    ("_electrophile", "amount", qty(0.13, "mmol")), ("_prod", "mass", qty(29, "mg")),
])
enrich_table3("table3_entry6_13f", 6, "1-(phenylethynyl)-1-(4'-methoxyphenyl)cyclopropane", [8], [
    ("_sub", "mass", qty(57, "mg")), ("_sub", "amount", qty(0.40, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.48, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")),
    ("_pd", "mass", qty(15, "mg")), ("_electrophile", "mass", qty(63, "mg")),
    ("_electrophile", "amount", qty(0.27, "mmol")), ("_prod", "mass", qty(22, "mg")),
])
enrich_table3("table3_entry7_13g", 7, "1-(phenylethynyl)-1-(E-methoxycarbonylethenyl)cyclopropane", [8], [
    ("_sub", "mass", qty(56, "mg")), ("_sub", "amount", qty(0.39, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.47, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(178, "mg")), ("_znbr2", "amount", qty(0.79, "mmol")),
    ("_pd", "mass", qty(15, "mg")), ("_electrophile", "mass", qty(55, "mg")),
    ("_electrophile", "amount", qty(0.26, "mmol")), ("_prod", "mass", qty(20, "mg")),
], mp=(80, 81))


# The Scheme 3 experiment is detailed on page 8 and its second product continues on page 9.
r = rec("scheme3_13l_13lprime")
add_record_evidence(r, [8, 9])
for entity_id, name, value in [
    ("s3_4a", "mass", qty(64, "mg")), ("s3_4a", "amount", qty(0.45, "mmol")),
    ("s3_nbu", "volume", qty(0.34, "mL")), ("s3_nbu", "amount", qty(0.54, "mmol")), ("s3_nbu", "concentration", qty(1.6, "M")),
    ("s3_zn", "mass", qty(203, "mg")), ("s3_zn", "amount", qty(0.90, "mmol")),
    ("s3_pd", "mass", qty(26, "mg")), ("s3_diiodo", "mass", qty(74, "mg")), ("s3_diiodo", "amount", qty(0.23, "mmol")),
    ("s3_13l", "mass", qty(45, "mg")), ("s3_13lp", "mass", qty(15, "mg")),
]:
    add_amount(r, entity_id, name, value, [8, 9])
set_product(r, "s3_13l", "1-(phenylethynyl)-1-(4'-iodophenyl)cyclopropane", participant(r, "s3_13l")["smiles"]["value"], [8, 9])
set_product(r, "s3_13lp", "1,4-bis(1'-phenylethynyl-1'-cyclopropyl)benzene", "c1cc(C2(CC2)C#Cc2ccccc2)ccc1C1(CC1)C#Cc1ccccc1", [8, 9])
add_yield_evidence(r, [8, 9])
set_yield_basis(r, ["s3_13l", "s3_13lp"], [8, 9])
add_outcome(r, "melting_point", rng(97, 100, "°C", "97-100 °C"), ["s3_13lp"], [9])
keep_unresolved(r, ["yield basis are not reported"])


enrich_table3("table3_entry8_13h", 8, "1-(phenylethynyl)-1-(4'-bromophenyl)cyclopropane", [9], [
    ("_sub", "mass", qty(66, "mg")), ("_sub", "amount", qty(0.46, "mmol")),
    ("_nbu", "volume", qty(0.35, "mL")), ("_nbu", "amount", qty(0.56, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(203, "mg")), ("_znbr2", "amount", qty(0.90, "mmol")),
    ("_pd", "mass", qty(18, "mg")), ("_electrophile", "mass", qty(87, "mg")),
    ("_electrophile", "amount", qty(0.31, "mmol")), ("_prod", "mass", qty(59, "mg")),
])
enrich_table3("table3_entry9_13i", 9, "1-(phenylethynyl)-1-(4'-chlorophenyl)cyclopropane", [9], [
    ("_sub", "mass", qty(65, "mg")), ("_sub", "amount", qty(0.46, "mmol")),
    ("_nbu", "volume", qty(0.34, "mL")), ("_nbu", "amount", qty(0.55, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(203, "mg")), ("_znbr2", "amount", qty(0.90, "mmol")),
    ("_pd", "mass", qty(18, "mg")), ("_electrophile", "mass", qty(73, "mg")),
    ("_electrophile", "amount", qty(0.31, "mmol")), ("_prod", "mass", qty(43, "mg")),
])
enrich_table3("table3_entry10_13j", 10, "1-(p-phenylphenyl)ethynyl-1-(4'-cyanophenyl)cyclopropane", [9], [
    ("_sub", "mass", qty(87, "mg")), ("_sub", "amount", qty(0.40, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.48, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")),
    ("_pd", "mass", qty(12, "mg")), ("_electrophile", "mass", qty(46, "mg")),
    ("_electrophile", "amount", qty(0.20, "mmol")), ("_prod", "mass", qty(45, "mg")),
], mp=(118, 119))
enrich_table3("table3_entry11_13k", 11, "1-(p-phenylphenyl)ethynyl-1-(4'-methoxycarbonylphenyl)cyclopropane", [9], [
    ("_sub", "mass", qty(87, "mg")), ("_sub", "amount", qty(0.40, "mmol")),
    ("_nbu", "volume", qty(0.30, "mL")), ("_nbu", "amount", qty(0.48, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_znbr2", "mass", qty(180, "mg")), ("_znbr2", "amount", qty(0.80, "mmol")),
    ("_pd", "mass", qty(8, "mg")), ("_electrophile", "mass", qty(38, "mg")),
    ("_electrophile", "amount", qty(0.13, "mmol")), ("_prod", "mass", qty(26, "mg")),
], mp=(156, 156))


def enrich_scheme4(suffix, prefix, pages, product_name, values, mp):
    r = rec(suffix)
    add_record_evidence(r, pages)
    for entity_end, name, value in values:
        add_amount(r, prefix + entity_end, name, value, pages)
    set_product(r, prefix + "_prod", product_name, participant(r, prefix + "_prod")["smiles"]["value"], pages)
    add_yield_evidence(r, pages)
    set_yield_basis(r, [prefix + "_prod"], pages)
    add_outcome(r, "melting_point", rng(mp[0], mp[1], "°C", f"{mp[0]}-{mp[1]} °C"), [prefix + "_prod"], pages)
    keep_unresolved(r, ["yield basis are not reported"])


enrich_scheme4("scheme4_cyclobutyl_14", "scheme4_cyclobutyl_14", [9, 10], "2,2-diphenyl vinylidenecyclobutane", [
    ("_sub", "mass", qty(79, "mg")), ("_sub", "amount", qty(0.50, "mmol")),
    ("_nbu", "volume", qty(0.94, "mL")), ("_nbu", "amount", qty(1.51, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_zn", "mass", qty(340, "mg")), ("_zn", "amount", qty(1.51, "mmol")),
    ("_pd", "mass", qty(29, "mg")), ("_phi", "volume", qty(169, "uL")),
    ("_phi", "amount", qty(1.51, "mmol")), ("_prod", "mass", qty(64, "mg")),
], (54, 55))
enrich_scheme4("scheme4_cyclohexyl_15", "scheme4_cyclohexyl_15", [10], "2,2-diphenyl vinylidenecyclohexane", [
    ("_sub", "mass", qty(94, "mg")), ("_sub", "amount", qty(0.51, "mmol")),
    ("_nbu", "volume", qty(0.95, "mL")), ("_nbu", "amount", qty(1.52, "mmol")), ("_nbu", "concentration", qty(1.6, "M")),
    ("_zn", "mass", qty(343, "mg")), ("_zn", "amount", qty(1.52, "mmol")),
    ("_pd", "mass", qty(29, "mg")), ("_phi", "volume", qty(171, "uL")),
    ("_phi", "amount", qty(1.52, "mmol")), ("_prod", "mass", qty(59, "mg")),
], (97, 98))


def ids(*items):
    return [f"{DOC}:{item}" for item in items]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "left column sections 3.2.2.3-3.2.2.5", "finding": "Detailed reported preparations of allenes 12c, 12d and 12e; each is merged with its existing Table 2 scope record.", "evidence_ids": evid(7)},
                {"region": "right column sections 3.2.2.6-3.2.2.7", "finding": "Detailed reported preparations of allene 12f and cyclopropyl alkyne 13b; merged with existing scope records.", "evidence_ids": evid(7)},
                {"region": "right-column bottom, section 3.2.2.8 beginning", "finding": "The 13c experiment begins here and continues on page 8; one cross-page record is retained.", "evidence_ids": evid(7)},
            ],
            "record_ids": ids("table2_entry3_12c", "table2_entry4_12d", "table2_entry5_12e", "table2_entry6_12f", "table3_entry2_13b", "table3_entry3_13c"),
            "unresolved": ["The derivative paragraphs inherit the section 3.2.2 typical procedure; no numeric cross-coupling completion time is stated."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of section 3.2.2.8", "finding": "Characterization continuation for 13c; not a separate experiment.", "evidence_ids": evid(8)},
                {"region": "sections 3.2.2.9-3.2.2.12", "finding": "Detailed reported preparations of 13d, 13e, 13f and 13g; merged with existing Table 3 rows.", "evidence_ids": evid(8)},
                {"region": "section 3.2.2.13", "finding": "One reported 1,4-diiodobenzene experiment produces 13l and 13l' with product-specific yields; the 13l' characterization continues on page 9.", "evidence_ids": evid(8)},
            ],
            "record_ids": ids("table3_entry3_13c", "table3_entry4_13d", "table3_entry5_13e", "table3_entry6_13f", "table3_entry7_13g", "scheme3_13l_13lprime"),
            "unresolved": ["The derivative paragraphs do not state a numeric reaction-completion time after palladium/electrophile addition."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of section 3.2.2.13", "finding": "Characterization and melting point for coproduct 13l'; retained within the page 8 experiment.", "evidence_ids": evid(9)},
                {"region": "sections 3.2.2.14-3.2.2.17", "finding": "Detailed reported preparations of 13h, 13i, 13j and 13k; merged with existing Table 3 rows.", "evidence_ids": evid(9)},
                {"region": "section 3.2.2.18 beginning", "finding": "The reported preparation of allene 14 begins here and its characterization continues on page 10; one cross-page record is retained.", "evidence_ids": evid(9)},
            ],
            "record_ids": ids("scheme3_13l_13lprime", "table3_entry8_13h", "table3_entry9_13i", "table3_entry10_13j", "table3_entry11_13k", "scheme4_cyclobutyl_14"),
            "unresolved": ["Numeric completion times for the cross-coupling stages are not stated in these derivative paragraphs."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "top-left continuation of section 3.2.2.18", "finding": "Characterization continuation for allene 14; not a separate experiment.", "evidence_ids": evid(10)},
                {"region": "section 3.2.2.19", "finding": "Detailed reported preparation of allene 15; merged with existing Scheme 4 record.", "evidence_ids": evid(10)},
                {"region": "acknowledgements and references 1-12", "finding": "Funding acknowledgements and cited prior literature; no additional experiment from the present paper is created from this region.", "evidence_ids": evid(10)},
            ],
            "record_ids": ids("scheme4_cyclobutyl_14", "scheme4_cyclohexyl_15"),
            "unresolved": ["The 14 and 15 derivative paragraphs report no numeric completion time for the transmetallation/cross-coupling stages; references were not treated as current-paper experiments."],
        },
    ],
}


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
COVERAGE.parent.mkdir(parents=True, exist_ok=True)
COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = RUN / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and task.get("evidence_id") in {f"{DOC}:page{page}:text" for page in range(7, 11)}:
        task["state"] = "attempted"
        task["reason"] = "Original page image inspected; regions and linked records are documented in coverage/pages_0007_0010.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "records_file": str(OUT),
    "coverage_file": str(COVERAGE),
    "tasks_updated": 4,
}, ensure_ascii=False))
