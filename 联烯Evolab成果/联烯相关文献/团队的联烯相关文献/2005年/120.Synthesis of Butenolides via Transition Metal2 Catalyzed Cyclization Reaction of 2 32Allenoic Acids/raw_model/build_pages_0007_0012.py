#!/usr/bin/env python3
"""Build evidence-linked machine records for visually inspected PDF pages 7--12."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/raw_model/pages_0007_0012_records.json"
COVERAGE_OUT = ROOT / "runs/current/coverage/pages_0007_0012.json"
TASKS_OUT = ROOT / "runs/current/tasks.json"
DOC = "doc_8f7c32b36ec71a95"


def ev(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return result


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def participant(entity_id, role, label, name, evidence, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence if smiles is not None else []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def missing_conditions(conditions):
    present = {item["name"] for item in conditions}
    return [
        field(name, None, [])
        for name in ("reaction_scale", "atmosphere", "workup", "purification")
        if name not in present
    ]


def experiment(suffix, source_id, evidence, participants, conditions, outcomes, citation, notes=None, unresolved=None):
    record_notes = [
        fact(f"The review assigns this reaction series to prior publication {citation}; classified as a literature example.", evidence),
        fact("Only information visible in the inspected main-text pages was retained; no supporting information was associated.", evidence),
    ]
    record_notes.extend(notes or [])
    pending = [
        "Reactant quantities, workup, and purification are not reported in the inspected page region.",
        "Complete source-verified substrate/product SMILES were not assigned where structures depend on a generic R-group scaffold or stereochemical drawing.",
        "Record is machine-extracted and requires independent chemical source review.",
    ]
    pending.extend(unresolved or [])
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": "literature_example",
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
        "participants": participants,
        "steps": [{
            "step_id": "reaction",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions + missing_conditions(conditions),
        }],
        "outcomes": outcomes,
        "notes": record_notes,
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": pending,
        },
    }


records = []

# Page 7 continues Table 4, whose generic arrow and shared conditions are on page 6.
table4 = [
    (1, "Ph", "n-C3H7", "1a", 10, "13a", 74, "1:1.87"),
    (2, "Ph", "CH3", "1b", 4, "13b", 64, "1:1.62"),
    (3, "Ph", "PhCH2", "1c", 11.5, "13c", 75, "1:1.53"),
    (4, "alpha-naphthyl", "CH3", "1d", 4, "13d", 71, "1:1.28"),
    (5, "alpha-naphthyl", "n-C3H7", "1e", 4.5, "13e", 64, "1:1.43"),
    (6, "CH3", "PhCH2", "1f", 3.5, "13f", 72, "1.04:1"),
]
e67 = ev(6, 7)
for entry, r1, r2, substrate, time_h, product, yld, ratio in table4:
    participants = [
        participant("substrate", "reactant", substrate, f"2,3-allenoic acid {substrate} (R1={r1}, R2={r2})", e67),
        participant("propyl_iodide", "unspecified_agent", "C3H7I", "C3H7I species shown on the Table 4 reaction arrow", e67),
        participant("product", "product", product, f"bi-butenolide {product}", e67),
        participant("pdcl2", "catalyst", "PdCl2", "palladium(II) chloride", e67, amounts=[field("amount", {"number": 5, "unit": "mol%"}, e67)]),
        participant("dma", "solvent", "DMA", "N,N-dimethylacetamide", e67, smiles="CC(=O)N(C)C"),
    ]
    outcomes = [
        field("yield", {"number": yld, "unit": "%"}, e67, ["product"]),
        field("diastereomer_ratio_R*S*_to_R*R*", ratio, e67, ["product"]),
        field("yield_measurement_basis", None, []),
    ]
    records.append(experiment(
        f"p07_table4_entry{entry:02d}", f"Table 4 entry {entry}", e67, participants,
        [field("solvent", "DMA", e67), field("temperature", {"number": 80, "unit": "°C"}, e67), field("reaction_time", {"number": time_h, "unit": "h"}, e67)],
        outcomes, "[10]",
        unresolved=["The exact isomer identity, role, and quantity of the C3H7I species printed on the shared Table 4 arrow are not stated; it remains an unspecified agent with null SMILES."],
    ))


# Page 7, Table 5: 22 rows under one shared PdCl2(MeCN)2/CH3CN/r.t./4 h header.
table5 = [
    (1, "Ph", "n-C3H7", "H", "1a", "CH3", "14a", "15a", 90),
    (2, "Ph", "CH3", "H", "1b", "CH3", "14a", "15b", 73),
    (3, "Ph", "PhCH2", "H", "1c", "CH3", "14a", "15c", 92),
    (4, "Ph", "allyl", "H", "1d", "CH3", "14a", "15d", 86),
    (5, "alpha-naphthyl", "CH3", "H", "1e", "CH3", "14a", "15e", 84),
    (6, "alpha-naphthyl", "n-C3H7", "H", "1f", "CH3", "14a", "15f", 86),
    (7, "CH3", "PhCH2", "H", "1g", "CH3", "14a", "15g", 90),
    (8, "Ph", "CH3", "Et", "1h", "CH3", "14a", "15h", 85),
    (9, "n-C7H15", "H", "H", "1i", "CH3", "14a", "15i", 69),
    (10, "4-Br-Ph", "n-C3H7", "H", "1j", "CH3", "14a", "15j", 70),
    (11, "Ph", "n-C3H7", "H", "1a", "n-C4H9", "14b", "15k", 84),
    (12, "Ph", "CH3", "H", "1b", "n-C4H9", "14b", "15l", 63),
    (13, "Ph", "allyl", "H", "1d", "n-C4H9", "14b", "15m", 66),
    (14, "alpha-naphthyl", "CH3", "H", "1e", "n-C4H9", "14b", "15n", 79),
    (15, "Ph", "CH3", "Et", "1h", "n-C4H9", "14b", "15o", 86),
    (16, "n-C7H15", "H", "H", "1i", "n-C4H9", "14b", "15p", 69),
    (17, "Ph", "n-C3H7", "H", "1a", "PhCH2", "14c", "15q", 74),
    (18, "Ph", "CH3", "H", "1b", "PhCH2", "14c", "15r", 86),
    (19, "Ph", "allyl", "H", "1d", "PhCH2", "14c", "15s", 82),
    (20, "alpha-naphthyl", "CH3", "H", "1e", "PhCH2", "14c", "15t", 90),
    (21, "Ph", "CH3", "Et", "1h", "PhCH2", "14c", "15u", 84),
    (22, "n-C7H15", "H", "H", "1i", "PhCH2", "14c", "15v", 71),
]
ketone_smiles = {
    "14a": "CC(=O)C=C=C",
    "14b": "CCCCC(=O)C=C=C",
    "14c": "O=C(Cc1ccccc1)C=C=C",
}
e7 = ev(7)
e7910 = ev(7, 9, 10)
for entry, r1, r2, r3, substrate, r4, ketone, product, yld in table5:
    evidence = e7910 if entry == 1 else (ev(7, 9) if entry == 10 else e7)
    participants = [
        participant("allenoic_acid", "reactant", substrate, f"2,3-allenoic acid {substrate} (R1={r1}, R2={r2}, R3={r3})", evidence),
        participant("allenyl_ketone", "reactant", ketone, f"1,2-allenyl ketone {ketone} (R4={r4})", evidence, smiles=ketone_smiles[ketone]),
        participant("product", "product", product, f"4-(3-furanyl)-2(5H)-furanone {product}", evidence),
        participant("pd_complex", "catalyst", "PdCl2(MeCN)2", "bis(acetonitrile)palladium(II) dichloride", evidence, amounts=[field("amount", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", evidence, smiles="CC#N"),
    ]
    outcomes = [field("yield", {"number": yld, "unit": "%"}, evidence, ["product"])]
    notes = []
    unresolved = ["The Table 5 yield measurement basis is not stated."]
    if entry == 1:
        participants.extend([
            participant("byproduct_16a", "product", "16a", "allenyl-ketone homodimerization product 16a", ev(9, 10)),
            participant("byproduct_17a", "product", "17a", "4,5-dimethyleneocta-2,7-dione 17a", ev(9, 10)),
            participant("byproduct_printed_16a", "product", "16a", "second drawn diketone isomer printed as 16a; prose identifies the corresponding isomer as 18a", ev(9, 10)),
            participant("byproduct_19a", "product", "19a", "diketone C=C isomer 19a", ev(9, 10)),
        ])
        outcomes.extend([
            field("byproduct_yield", {"number": 13, "unit": "%"}, ev(10), ["byproduct_16a"]),
            field("byproduct_yield", {"number": 6, "unit": "%"}, ev(10), ["byproduct_17a"]),
            field("byproduct_yield", {"number": 21, "unit": "%"}, ev(10), ["byproduct_printed_16a"]),
            field("byproduct_yield", {"number": 13, "unit": "%"}, ev(10), ["byproduct_19a"]),
            field("byproduct_yield_measurement_basis", "Yields are calculated based on penta-3,4-dien-2-one used.", ev(10), ["byproduct_16a", "byproduct_17a", "byproduct_printed_16a", "byproduct_19a"]),
        ])
        notes.append(fact("Scheme 4 expands the Table 5 entry 1 reaction with four byproduct drawings, so those observations are attached to the same standard-condition record rather than duplicated.", ev(7, 9, 10)))
        notes.append(fact("The lower-left 21% diketone is printed as 16a, while the surrounding prose names the three diketones 17a, 18a, and 19a; the discrepancy is preserved without silently relabeling it.", ev(9, 10)))
        unresolved.append("The source-label conflict for the 21% lower-left Scheme 4 byproduct (printed 16a versus prose 18a) requires source review.")
    if entry == 10:
        notes.append(fact("Scheme 3 reports that single-crystal X-ray analysis establishes compound 15j as the S configuration; this characterization evidence is linked to the matching Table 5 row rather than treated as a new reaction.", ev(9)))
    outcomes.append(field("yield_measurement_basis", None, []))
    records.append(experiment(
        f"p07_table5_entry{entry:02d}", f"Table 5 entry {entry}", evidence, participants,
        [field("solvent", "CH3CN", evidence), field("temperature", "r.t.", evidence), field("reaction_time", {"number": 4, "unit": "h"}, evidence)],
        outcomes, "[11]", notes=notes, unresolved=unresolved,
    ))


# Pages 8--9, Table 6: optically active allenoic acids; each row is a separate experiment.
table6 = [
    (1, 8, "S-(+)-1a", 98, "14a", "S-(+)-15a", 87, {"number": 95, "unit": "%"}),
    (2, 8, "R-(-)-1a", 97, "14b", "R-(-)-15k", 75, {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}),
    (3, 8, "R-(-)-1a", 97, "14c", "R-(-)-15q", 86, {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}),
    (4, 8, "R-(-)-1b", 99, "14a", "R-(-)-15b", 76, {"number": 97, "unit": "%"}),
    (5, 8, "R-(-)-1b", 99, "14b", "R-(-)-15l", 81, {"number": 99, "unit": "%"}),
    (6, 8, "R-(-)-1b", 99, "14c", "R-(-)-15r", 72, {"number": 96, "unit": "%"}),
    (7, 9, "S-(-)-1d", 98, "14a", "S-(+)-15d", 73, {"number": 97, "unit": "%"}),
    (8, 9, "S-(-)-1d", 98, "14b", "S-(+)-15m", 67, {"number": 99, "unit": "%"}),
    (9, 9, "S-(-)-1d", 98, "14c", "S-(+)-15s", 67, {"number": 98, "unit": "%"}),
    (10, 9, "S-(+)-1e", 98, "14a", "S-(-)-15e", 74, {"number": 97, "unit": "%"}),
    (11, 9, "S-(+)-1e", 98, "14b", "S-(-)-15n", 76, {"number": 99, "unit": "%"}),
    (12, 9, "S-(+)-1e", 98, "14c", "S-(-)-15t", 87, {"number": 99, "unit": "%", "qualifier": "gt", "raw_text": ">99%"}),
]
for entry, page, substrate, start_ee, ketone, product, yld, product_ee in table6:
    evidence = ev(8) if page == 8 else ev(8, 9)
    participants = [
        participant("allenoic_acid", "reactant", substrate, f"optically active 2,3-allenoic acid {substrate}", evidence),
        participant("allenyl_ketone", "reactant", ketone, f"1,2-allenyl ketone {ketone}", evidence, smiles=ketone_smiles[ketone]),
        participant("product", "product", product, f"optically active furanone {product}", evidence),
        participant("pd_complex", "catalyst", "PdCl2(MeCN)2", "bis(acetonitrile)palladium(II) dichloride", evidence, amounts=[field("amount", {"number": 5, "unit": "mol%"}, evidence)]),
        participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", evidence, smiles="CC#N"),
    ]
    outcomes = [
        field("starting_material_ee", {"number": start_ee, "unit": "%"}, evidence, ["allenoic_acid"]),
        field("yield", {"number": yld, "unit": "%"}, evidence, ["product"]),
        field("product_ee", product_ee, evidence, ["product"]),
        field("yield_measurement_basis", None, []),
    ]
    records.append(experiment(
        f"p{page:02d}_table6_entry{entry:02d}", f"Table 6 entry {entry}", evidence, participants,
        [field("solvent", "CH3CN", evidence), field("temperature", "r.t.", evidence), field("reaction_time", {"number": 4, "unit": "h"}, evidence)],
        outcomes, "[11]",
        unresolved=["Absolute/axial stereochemical SMILES were not assigned from the drawings; configuration labels, optical-rotation signs, and ee values are preserved as printed."],
    ))


# Page 9 prose and page 10 drawings: two distinct control experiments.
e910 = ev(9, 10)
base_control = [
    participant("allenoic_acid", "reactant", "1a", "4-phenyl-2-propyl-2,3-butadienoic acid 1a", e910),
    participant("allenyl_ketone", "reactant", "14a", "penta-3,4-dien-2-one 14a", e910, smiles=ketone_smiles["14a"]),
    participant("product", "product", "15a", "furanone 15a", e910),
    participant("pd_complex", "catalyst", "PdCl2(MeCN)2", "bis(acetonitrile)palladium(II) dichloride", e910, amounts=[field("amount", {"number": 5, "unit": "mol%"}, e910)]),
    participant("acetonitrile", "solvent", "CH3CN", "acetonitrile", e910, smiles="CC#N"),
]
records.append(experiment(
    "p10_eq6_argon_control", "Equation (6)", e910,
    base_control,
    [field("solvent", "CH3CN", e910), field("temperature", "r.t.", e910), field("reaction_time", {"number": 4, "unit": "h"}, e910), field("atmosphere", "Ar", e910)],
    [field("yield", {"number": 90, "unit": "%"}, e910, ["product"]), field("yield_measurement_basis", None, [])],
    "[11]", notes=[fact("The argon control is a distinct run from Table 5 entry 1 because the atmosphere is explicitly changed/tested.", e910)],
))

eq7_participants = list(base_control) + [
    participant("tbab", "reagent", "Bu4NBr", "tetrabutylammonium bromide", e910, smiles="CCCC[N+](CCCC)(CCCC)CCCC.[Br-]"),
    participant("potassium_carbonate", "reagent", "K2CO3", "potassium carbonate", e910, smiles="[K+].[K+].[O-]C([O-])=O", amounts=[field("amount", {"number": 1, "unit": "equiv"}, e910)]),
]
records.append(experiment(
    "p10_eq7_base_control", "Equation (7)", e910,
    eq7_participants,
    [field("solvent", "CH3CN", e910), field("temperature", "r.t.", e910), field("reaction_time", {"number": 11, "unit": "h"}, e910)],
    [field("yield", {"number": 0, "unit": "%"}, e910, ["product"]), field("yield_measurement_basis", None, [])],
    "[11]", notes=[fact("The source explicitly reports 0% 15a for the base-control run; the failed result is retained as a numeric zero rather than treated as missing. The carbonate amount is structured on its participant.", e910)],
    unresolved=["Bu4NBr is printed on the reaction arrow but its amount is not provided."],
))


# Pages 10--11, Scheme 5: explicitly proposed catalytic cycle, not an isolated experiment.
e1011 = ev(10, 11)
mechanism_participants = [
    participant("allenoic_acid", "reactant", "1a", "2,3-allenoic acid 1a", e1011),
    participant("allenyl_ketone", "reactant", "14a", "penta-3,4-dien-2-one 14a", e1011, smiles=ketone_smiles["14a"]),
    participant("additional_allenyl_ketone", "reactant", "14a", "two additional equivalents of penta-3,4-dien-2-one shown in the proposed cycle", e1011, smiles=ketone_smiles["14a"], amounts=[field("amount", {"number": 2, "unit": "equiv"}, e1011)]),
    participant("desired_product", "product", "15a", "furanone 15a", e1011),
    participant("diketone_products", "product", "17a + 18a + 19a", "proposed diketone products 17a, 18a, and 19a", e1011),
    participant("palladium_species", "catalyst", "LnPdCl2 / LxPd(0)", "proposed palladium catalyst states", e1011),
    participant("intermediate_20a", "unspecified_agent", "20a", "proposed double-oxypalladation intermediate 20a", e1011),
    participant("intermediates_21", "unspecified_agent", "21a / 21a'", "proposed cyclic palladium intermediates 21a and 21a'", e1011),
    participant("hcl", "unspecified_agent", "2 HCl", "two equivalents of in-situ generated hydrogen chloride shown in the proposed cycle", e1011, smiles="Cl", amounts=[field("amount", {"number": 2, "unit": "equiv"}, e1011)]),
]
records.append({
    "record_id": f"{DOC}:p11_scheme5_mechanism",
    "document_id": DOC,
    "source_reaction_id": "Scheme 5",
    "record_kind": "mechanism",
    "status": "candidate",
    "completeness": "partial",
    "evidence_ids": e1011,
    "participants": mechanism_participants,
    "steps": [{
        "step_id": "proposed_catalytic_cycle",
        "participant_ids": [p["entity_id"] for p in mechanism_participants],
        "conditions": [field("operation", "Proposed double oxypalladation, reductive elimination, Pd(0) cyclometalation, and protonation sequence.", e1011)],
    }],
    "outcomes": [],
    "notes": [
        fact("The figure is explicitly titled a proposed catalytic cycle and is not treated as an isolated experimental run.", e1011),
        fact("The accompanying prose says HCl is generated in situ and may protonate intermediates 21a/21a' to furnish 17a, 18a, and 19a.", e1011),
    ],
    "review": {
        "method": "none",
        "reviewer": None,
        "checked_fields": [],
        "unresolved": [
            "Ligand identities and complete organopalladium intermediate structures are not specified in the generic mechanism.",
            "Mechanistic arrows are proposals rather than independently isolated experimental stages.",
            "Record is machine-extracted and requires independent chemical source review.",
        ],
    },
})


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = [record["record_id"] for record in records]
prefix = f"{DOC}:"
table4_ids = [rid for rid in ids if ":p07_table4_" in rid]
table5_ids = [rid for rid in ids if ":p07_table5_" in rid]
table6_8_ids = [rid for rid in ids if ":p08_table6_" in rid]
table6_9_ids = [rid for rid in ids if ":p09_table6_" in rid]
eq_ids = [f"{prefix}p10_eq6_argon_control", f"{prefix}p10_eq7_base_control"]
mechanism_id = f"{prefix}p11_scheme5_mechanism"

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "Table 4 continuation, entries 1--6", "finding": "Combined with the page-6 shared arrow, six prior-work oxidative dimeric cyclizing-coupling rows were extracted independently with time, yield, and printed R*S*/R*R* ratio.", "evidence_ids": ev(7, 6)},
                {"region": "Table 5 generic arrow and shared conditions", "finding": "Prior-work [11] cross-coupling uses PdCl2(MeCN)2 5 mol% in CH3CN at r.t. for 4 h; the generic arrow was not counted as a separate experiment.", "evidence_ids": ev(7)},
                {"region": "Table 5 entries 1--22", "finding": "Twenty-two row-level literature examples were extracted; Table 5 entry 1 also carries the later Scheme 4 byproduct evidence rather than duplicating the standard-condition reaction.", "evidence_ids": ev(7)},
            ],
            "record_ids": table4_ids + table5_ids,
            "unresolved": ["Table 4 and Table 5 omit reactant quantities, workup, purification, and yield measurement basis; structures represented through generic R-group scaffolds retain null substrate/product SMILES."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "Table 5 discussion", "finding": "Narrative scope and mild-condition discussion only; no additional row or arrow beyond Table 5 was created.", "evidence_ids": ev(8)},
                {"region": "Table 6 header, generic arrow, and entries 1--6", "finding": "Six optically active prior-work rows were extracted separately with starting ee, product yield, and product ee under PdCl2(MeCN)2/CH3CN/r.t./4 h.", "evidence_ids": ev(8)},
            ],
            "record_ids": table6_8_ids,
            "unresolved": ["Absolute/axial stereochemical SMILES, reaction scale, workup, purification, and yield measurement basis are not established on this page."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "Table 6 continuation, entries 7--12", "finding": "Six additional optically active rows were extracted using the page-8 shared header, preserving the >99% ee bound in entry 12.", "evidence_ids": ev(9, 8)},
                {"region": "Scheme 3 X-ray structure", "finding": "Characterization evidence states compound 15j has S configuration; it is not a new reaction experiment and no standalone reaction record was fabricated.", "evidence_ids": ev(9)},
                {"region": "Control-experiment prose below Scheme 3", "finding": "The prose introduces the argon and K2CO3 controls drawn as Eq. (6)/(7) on page 10; both records merge page-9 text with page-10 image evidence.", "evidence_ids": ev(9, 10)},
            ],
            "record_ids": table6_9_ids + [f"{prefix}p07_table5_entry10"] + eq_ids,
            "unresolved": ["Scheme 3 gives crystallographic configuration but no crystallographic procedure; it was retained only as a coverage finding."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "Equations (6) and (7)", "finding": "Two distinct controls were extracted: Ar/4 h gives 15a in 90%, while 1 equiv K2CO3 with Bu4NBr/11 h gives 0% 15a.", "evidence_ids": ev(10, 9)},
                {"region": "Scheme 4 standard reaction and four byproduct drawings", "finding": "The standard 1a+14a reaction matches Table 5 entry 1 and was merged into that record; byproduct yields 13%, 6%, 21%, and 13% were added with the footnoted penta-3,4-dien-2-one basis.", "evidence_ids": ev(10, 9, 7)},
                {"region": "Scheme 4 lower-left byproduct label", "finding": "The drawing is printed as 16a at 21%, but surrounding prose calls the corresponding diketone isomer 18a; the source conflict is preserved explicitly.", "evidence_ids": ev(10)},
                {"region": "Mechanism discussion leading to Scheme 5", "finding": "Proposed mechanistic prose was linked to the Scheme 5 mechanism record and not promoted to an experimental reaction.", "evidence_ids": ev(10, 11)},
            ],
            "record_ids": eq_ids + [f"{prefix}p07_table5_entry01", mechanism_id],
            "unresolved": ["Bu4NBr quantity in Eq. (7) is not printed; the Scheme 4 21% byproduct label conflict requires source review."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "Scheme 5 proposed catalytic cycle", "finding": "A single mechanism record captures the proposed double-oxypalladation/reductive-elimination/cyclometalation/protonation network and its generic intermediates; it is not a reported experiment.", "evidence_ids": ev(11, 10)},
                {"region": "Conclusion, acknowledgement, and references", "finding": "Summary and bibliography only; cited papers [6], [8]--[11] explain why table rows are classified as prior-work literature examples, but no new experiment is created here.", "evidence_ids": ev(11)},
            ],
            "record_ids": [mechanism_id],
            "unresolved": ["Generic ligands and proposed organopalladium intermediates prevent complete source-verified structures."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "Chinese title, author profiles, abstract, and keywords", "finding": "The page summarizes the previously described Pd-catalyzed coupling and two allene dimerization classes but contains no new table row, reaction arrow, conditions, or experiment-specific outcome.", "evidence_ids": ev(12)},
            ],
            "record_ids": [],
            "unresolved": ["Abstract-level statements lack experiment-specific quantities and were not converted into duplicate reaction records."],
        },
    ],
}
COVERAGE_OUT.parent.mkdir(parents=True, exist_ok=True)
COVERAGE_OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks = json.loads(TASKS_OUT.read_text())
for task in tasks:
    if task.get("document_id") != DOC:
        continue
    try:
        page = int(task["task_id"].split(":page", 1)[1].split(":", 1)[0])
    except (IndexError, ValueError):
        continue
    if 7 <= page <= 12:
        task["state"] = "attempted"
        task["reason"] = "Original page image visually inspected; findings and unresolved limits are recorded in coverage/pages_0007_0012.json."
TASKS_OUT.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records_output": str(OUT.relative_to(ROOT)),
    "coverage_output": str(COVERAGE_OUT.relative_to(ROOT)),
    "records": len(records),
    "coverage_pages": [page["page"] for page in coverage["pages"]],
    "tasks_attempted": sum(task.get("state") == "attempted" for task in tasks),
}, ensure_ascii=False))
