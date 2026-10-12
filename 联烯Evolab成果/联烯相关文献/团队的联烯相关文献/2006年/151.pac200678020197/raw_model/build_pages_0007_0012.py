"""Build source-linked machine extraction records for original PDF pages 7--12.

The source is a review article. Specific cited reactions are therefore classified
as literature examples, generic transformations as general schemes, and proposed
paths as mechanisms. Machine merge will quarantine every record for review.
"""
from __future__ import annotations

import json
from pathlib import Path


DOC = "doc_3f267ff48aec9258"
BASE = Path(__file__).resolve().parents[1]


def ev(*pages: int) -> list[str]:
    out: list[str] = []
    for page in pages:
        out.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return out


def fact(value, evidence=None):
    return {
        "value": value,
        "evidence_ids": list(evidence or []),
        "verification": "missing" if value is None else "unreviewed",
    }


def field(name, value, evidence=None, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


SMILES = {
    "PhI": "Ic1ccccc1",
    "(i-Pr)2NEt": "CCN(C(C)C)C(C)C",
    "PPh3": "c1ccc(P(c2ccccc2)c2ccccc2)cc1",
    "toluene": "Cc1ccccc1",
    "allyl bromide": "C=CCBr",
    "DMA": "CC(=O)N(C)C",
    "n-C3H7I": "CCCI",
    "KI": "[K+].[I-]",
    "benzoquinone": "O=C1C=CC(=O)C=C1",
    "MeCN": "CC#N",
    "TFA": "O=C(O)C(F)(F)F",
}


def participant(entity_id, role, label, evidence, *, name=None, smiles=None, amounts=None):
    if smiles is None:
        smiles = SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(smiles, evidence) if smiles else fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def qty(name, value, evidence):
    return field(name, value, evidence)


def record(suffix, kind, pages, participants, *, conditions=None, outcomes=None,
           notes=None, unresolved=None, steps=None):
    evidence = ev(*pages)
    if steps is None:
        steps = [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions or [],
        }]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(note, evidence) for note in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


records = []

# Scheme 11, first reaction: optically active acid S-35 directly to butenolide.
e = ev(7)
p = [
    participant("s11a_35", "reactant", "S-35", e,
                name="optically active 2-methyl-4-phenyl-2,3-butadienoic acid",
                smiles="CC(=C=Cc1ccccc1)C(=O)O"),
    participant("s11a_phi", "reactant", "PhI", e, name="iodobenzene"),
    participant("s11a_pd", "catalyst", "Pd2(dba)3·CHCl3", e,
                amounts=[qty("catalyst_loading", {"number": 2.5, "unit": "mol%"}, e)]),
    participant("s11a_pph3", "reagent", "PPh3", e,
                amounts=[qty("loading", {"number": 10, "unit": "mol%"}, e)]),
    participant("s11a_dipea", "reagent", "(i-Pr)2NEt", e,
                name="N,N-diisopropylethylamine"),
    participant("s11a_tol", "solvent", "toluene", e),
    participant("s11a_36", "product", "S-(+)-36", e,
                name="optically active butenolide S-(+)-36"),
]
records.append(record(
    "scheme11_direct_acid_s35", "literature_example", [7], p,
    conditions=[field("solvent", "toluene", e),
                field("temperature", {"number": 0, "unit": "°C"}, e),
                field("time", None)],
    outcomes=[field("starting_material_ee", {"number": 97, "unit": "%"}, e, ["s11a_35"]),
              field("yield", {"number": 49, "unit": "%"}, e, ["s11a_36"]),
              field("product_ee", {"number": 23, "unit": "%"}, e, ["s11a_36"]),
              field("yield_measurement_basis", None, targets=["s11a_36"])],
    notes=["Scheme 11 is cited to reference 16; the skeletal SMILES for S-35 does not encode its axial stereochemistry."],
    unresolved=["Reaction time, reagent amounts, yield measurement basis, workup, purification, and stereochemical SMILES are absent or unresolved."],
))

# Scheme 11 contains a distinct acid-to-1:1-salt arrow.
e = ev(7)
p = [
    participant("s11b_35", "reactant", "S-35", e,
                name="optically active 2-methyl-4-phenyl-2,3-butadienoic acid",
                smiles="CC(=C=Cc1ccccc1)C(=O)O"),
    participant("s11b_dipea", "reagent", "(i-Pr)2NEt", e,
                name="N,N-diisopropylethylamine"),
    participant("s11b_37", "product", "S-(+)-37", e,
                name="1:1 diisopropylethylammonium salt of S-35"),
]
records.append(record(
    "scheme11_salt_formation_s37", "literature_example", [7], p,
    conditions=[field("temperature", None), field("time", None), field("solvent", None)],
    outcomes=[field("salt_stoichiometry", "1:1", e, ["s11b_37"]),
              field("yield", None, targets=["s11b_37"])],
    notes=["The 1:1 value describes the isolated salt composition in the prose; it is not converted into an unsupported reagent-equivalent amount."],
    unresolved=["Preparation solvent, temperature, time, isolated yield, workup, and purification are not reported."],
))

# Scheme 11, second reaction: preformed salt S-(+)-37 to the same butenolide.
e = ev(7)
p = [
    participant("s11c_37", "reactant", "S-(+)-37", e,
                name="1:1 diisopropylethylammonium salt of S-35"),
    participant("s11c_phi", "reactant", "PhI", e, name="iodobenzene"),
    participant("s11c_pd", "catalyst", "Pd2(dba)3·CHCl3", e,
                amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s11c_pph3", "reagent", "PPh3", e,
                amounts=[qty("loading", {"number": 20, "unit": "mol%"}, e)]),
    participant("s11c_tol", "solvent", "toluene", e),
    participant("s11c_36", "product", "S-(+)-36", e,
                name="optically active butenolide S-(+)-36"),
]
records.append(record(
    "scheme11_preformed_salt_s37", "literature_example", [7], p,
    conditions=[field("solvent", "toluene", e),
                field("temperature", {"number": 5, "unit": "°C"}, e),
                field("time", {"number": 60, "unit": "h"}, e)],
    outcomes=[field("starting_material_ee", {"number": 97, "unit": "%"}, e, ["s11c_37"]),
              field("yield", {"number": 62, "unit": "%"}, e, ["s11c_36"]),
              field("product_ee", {"number": 91, "unit": "%"}, e, ["s11c_36"]),
              field("yield_measurement_basis", None, targets=["s11c_36"])],
    notes=["This is kept separate from the direct-acid experiment because catalyst loading, temperature, time, starting form, yield, and ee differ."],
    unresolved=["PhI amount, yield measurement basis, workup, purification, and complete stereochemical structures are not reported or verified."],
))

# Scheme 12: generic explanation of low versus high chirality transfer.
e = ev(7, 8)
p = [
    participant("s12_acid", "reactant", "generic optically active 2,3-allenoic acid", e),
    participant("s12_rx", "reactant", "R4X", e, name="generic organic halide"),
    participant("s12_salt", "reactant", "generic allenoate salt COOBH+", e),
    participant("s12_38", "product", "pi-allylpalladium intermediate 38", e),
    participant("s12_39", "product", "oxypalladation transition structure 39", e),
    participant("s12_40", "product", "2(5H)-furanonyl palladium intermediate 40", e),
]
records.append(record(
    "scheme12_chirality_transfer_mechanism", "mechanism", [7, 8], p,
    conditions=[field("operation", "acid path via pi-allylpalladium 38 may lose stereochemical information; salt path via 39 and 40 gives highly efficient chirality transfer", e)],
    outcomes=[field("acid_path_ee", "low ee", e), field("salt_path_ee", "high ee", e)],
    notes=["Scheme 12 is a proposed generic mechanistic comparison, not an independent isolated experiment."],
    unresolved=["R groups, X, B, palladium ligation, and quantitative conditions are generic or unspecified."],
))

# Scheme 13 has two explicitly tabulated temperature/time/result rows.
for suffix, temp, hours, yld, ee_value in [
    ("50c", 50, 16, 90, 93.5),
    ("25c", 25, 36.5, 80, 99.9),
]:
    e = ev(8, 9)
    p = [
        participant(f"s13_{suffix}_41", "reactant", "S-41", e,
                    name="optically active 2,3-allenoic acid S-41",
                    smiles="O=C(O)C(CCC)=C=Cc1ccccc1"),
        participant(f"s13_{suffix}_allylbr", "reactant", "allyl bromide", e),
        participant(f"s13_{suffix}_pdcl2", "catalyst", "PdCl2", e,
                    amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
        participant(f"s13_{suffix}_dma", "solvent", "DMA", e,
                    name="N,N-dimethylacetamide"),
        participant(f"s13_{suffix}_44", "product", "44", e,
                    name="allylated butenolide 44"),
    ]
    records.append(record(
        f"scheme13_s41_allyl_bromide_{suffix}", "literature_example", [8, 9], p,
        conditions=[field("solvent", "DMA", e),
                    field("temperature", {"number": temp, "unit": "°C"}, e),
                    field("time", {"number": hours, "unit": "h"}, e)],
        outcomes=[field("starting_material_ee", {"number": 97.7, "unit": "%", "qualifier": "gt", "raw_text": ">97.7% ee"}, e, [f"s13_{suffix}_41"]),
                  field("yield", {"number": yld, "unit": "%"}, e, [f"s13_{suffix}_44"]),
                  field("product_ee", {"number": ee_value, "unit": "%"}, e, [f"s13_{suffix}_44"]),
                  field("yield_measurement_basis", None, targets=[f"s13_{suffix}_44"])],
        notes=["Scheme 13 is cited to reference 17; its two temperature/time rows are retained as distinct literature examples."],
        unresolved=["Reactant quantities, yield basis, workup, purification, and stereochemical product structure are not reported or verified."],
    ))

# Scheme 13 lower drawing: oxypalladation/coupling mechanism.
e = ev(8, 9)
p = [
    participant("s13m_41", "reactant", "S-41", e),
    participant("s13m_allylbr", "reactant", "allyl bromide", e),
    participant("s13m_pdcl2", "catalyst", "PdCl2", e),
    participant("s13m_42", "product", "2(5H)-furanonyl palladium intermediate 42", e),
    participant("s13m_43", "product", "alkylpalladium intermediate 43", e),
    participant("s13m_44", "product", "44", e),
]
records.append(record(
    "scheme13_oxypalladation_mechanism", "mechanism", [8, 9], p,
    conditions=[field("operation", "oxypalladation of S-41 to 42, coupling with allyl bromide to 43, then dehalopalladation to 44", e)],
    notes=["The review proposes this pathway to explain efficient chirality transfer; intermediates 42 and 43 are not presented as isolated products."],
    unresolved=["X and palladium ligation are unspecified and intermediate structures are not independently verified."],
))

# Scheme 14 is a generic, deuterium-labelled mechanistic sequence.
e = ev(9)
p = [
    participant("s14_acid", "reactant", "generic 2,3-allenoic acid", e),
    participant("s14_bromide", "reactant", "deuterium-labeled omega-alkenyl dibromide", e),
    participant("s14_pdx2", "catalyst", "PdX2", e),
    participant("s14_45", "product", "furanonyl palladium intermediate 45", e),
    participant("s14_46", "product", "alkylpalladium intermediate 46", e),
    participant("s14_47", "product", "palladium hydride intermediate 47", e),
    participant("s14_48", "product", "alkylpalladium intermediate 48", e),
    participant("s14_49", "product", "coupling-cyclization product 49", e),
]
records.append(record(
    "scheme14_alkenyl_halide_mechanism", "mechanism", [9], p,
    conditions=[field("operation", "45 undergoes alkene insertion to 46, repeated dehydropalladation/hydropalladation through 47 and 48, then dehalopalladation to 49", e)],
    notes=["Scheme 14 is a generic mechanistic isotope-labeling depiction cited to reference 18, not a fully specified experiment."],
    unresolved=["R groups, X, ligand L, exact substrate identity, operating conditions, yield, and isolation status are unspecified."],
))

# Scheme 15 drawn alkyl-iodide protocol.
e = ev(10)
p = [
    participant("s15_acid", "reactant", "generic 2,3-allenoic acid", e),
    participant("s15_propyli", "reagent", "n-C3H7I", e, name="1-iodopropane",
                amounts=[qty("equivalents", {"number": 5, "unit": "equiv"}, e)]),
    participant("s15_pdcl2", "catalyst", "PdCl2", e,
                amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s15_dma", "solvent", "DMA", e, name="N,N-dimethylacetamide"),
    participant("s15_50", "product", "50", e, name="generic bisbutenolide 50"),
]
records.append(record(
    "scheme15_alkyl_iodide_protocol", "general_scheme", [10], p,
    conditions=[field("solvent", "DMA", e),
                field("temperature", {"number": 80, "unit": "°C"}, e),
                field("time", None)],
    outcomes=[field("yield", {"minimum": 64, "maximum": 75, "unit": "%", "raw_text": "64-75%"}, e, ["s15_50"]),
              field("generality", "best among the compared protocols", e, ["s15_50"]),
              field("yield_measurement_basis", None, targets=["s15_50"])],
    notes=["The prose proposes in-situ I2 formation from iodide and O2 in air as catalyst reoxidation; this mechanistic proposal is not promoted to an explicit atmosphere or reagent quantity."],
    unresolved=["Generic R groups, reaction time, yield basis, individual scope rows, and detailed operations are missing."],
))

# The prose reports two additional oxidant protocols without row-level details.
for suffix, label, outcome in [
    ("ki", "KI", "protocol reported; less general than the alkyl-iodide protocol"),
    ("benzoquinone", "benzoquinone", "highest yields among the compared protocols"),
]:
    e = ev(10)
    p = [
        participant(f"s15_{suffix}_acid", "reactant", "generic 2,3-allenoic acid", e),
        participant(f"s15_{suffix}_oxidant", "reagent", label, e),
        participant(f"s15_{suffix}_pd", "catalyst", "Pd(II) species", e),
        participant(f"s15_{suffix}_50", "product", "generic bisbutenolide 50", e),
    ]
    records.append(record(
        f"scheme15_{suffix}_oxidant_protocol", "general_scheme", [10], p,
        conditions=[field("temperature", None), field("time", None), field("solvent", None)],
        outcomes=[field("protocol_comparison", outcome, e, [f"s15_{suffix}_50"]),
                  field("yield", None, targets=[f"s15_{suffix}_50"])],
        notes=["This protocol is stated in prose and cited to reference 19; no separate arrow or numerical scope data are printed on this page."],
        unresolved=["Exact palladium catalyst, oxidant loading, solvent, temperature, time, substrate scope, and numerical yields are absent."],
    ))

# Scheme 16 generic double cyclization.
e = ev(10)
p = [
    participant("s16_acid", "reactant", "generic 2,3-allenoic acid", e),
    participant("s16_ketone", "reactant", "generic 1,2-allenyl ketone", e,
                amounts=[qty("equivalents", {"number": 5, "unit": "equiv"}, e)]),
    participant("s16_pd", "catalyst", "PdCl2(MeCN)2", e,
                amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s16_mecn", "solvent", "MeCN", e, name="acetonitrile"),
    participant("s16_51", "product", "51", e, name="generic beta-furanyl butenolide 51"),
]
records.append(record(
    "scheme16_allenyl_ketone_double_cyclization", "general_scheme", [10], p,
    conditions=[field("solvent", "MeCN", e), field("temperature", "rt", e),
                field("time", {"number": 4, "unit": "h"}, e)],
    outcomes=[field("yield", None, targets=["s16_51"])],
    notes=["The review cites reference 20 and says probe/X-ray studies revealed a double oxypalladation mechanism."],
    unresolved=["Generic substituents, individual yields, yield basis, exact room temperature, and scope rows are not printed."],
))

# Scheme 17 contains two additive conditions and product-specific results.
for suffix, additive, yld, ee_value in [
    ("no_tfa", None, 58, 36),
    ("tfa_0p8eq", "TFA", 62, 98),
]:
    e = ev(10, 11)
    p = [
        participant(f"s17_{suffix}_52", "reactant", "52", e,
                    name="optically active 2-methyl-4-phenyl-2,3-butadienoic acid 52",
                    smiles="CC(=C=Cc1ccccc1)C(=O)O"),
        participant(f"s17_{suffix}_54", "reactant", "54", e,
                    name="2,3-allenol 54"),
        participant(f"s17_{suffix}_pd", "catalyst", "PdCl2", e,
                    amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
        participant(f"s17_{suffix}_dma", "solvent", "DMA", e,
                    name="N,N-dimethylacetamide"),
    ]
    if additive:
        p.append(participant(f"s17_{suffix}_tfa", "reagent", "TFA", e,
                             name="trifluoroacetic acid",
                             amounts=[qty("equivalents", {"number": 0.8, "unit": "equiv"}, e)]))
    p.append(participant(f"s17_{suffix}_56", "product", "56", e,
                         name="beta-(1,3-dien-2-yl)butenolide 56"))
    product_id = f"s17_{suffix}_56"
    conditions = [field("solvent", "DMA", e),
                  field("temperature", {"number": 30, "unit": "°C"}, e),
                  field("time", None)]
    if additive is None:
        conditions.append(field("TFA_condition", "no TFA", e))
    records.append(record(
        f"scheme17_{suffix}", "literature_example", [10, 11], p,
        conditions=conditions,
        outcomes=[field("starting_material_ee", {"number": 98, "unit": "%"}, e, [f"s17_{suffix}_52"]),
                  field("yield", {"number": yld, "unit": "%"}, e, [product_id]),
                  field("product_ee", {"number": ee_value, "unit": "%"}, e, [product_id]),
                  field("yield_measurement_basis", None, targets=[product_id])],
        notes=["Scheme 17 is cited to reference 21; additive-free and 0.8-equivalent TFA conditions are separate records."],
        unresolved=["Reaction time, reactant amounts, yield basis, workup, purification, and stereochemical product structure are missing or unverified."],
    ))

# Scheme 17 central cycle is a proposed mechanism, not another experiment.
e = ev(10, 11)
p = [
    participant("s17m_52", "reactant", "52", e),
    participant("s17m_54", "reactant", "54", e),
    participant("s17m_pdx2", "catalyst", "PdX2", e),
    participant("s17m_53", "product", "furanonyl palladium intermediate 53", e),
    participant("s17m_55", "product", "hydroxy palladium intermediate 55", e),
    participant("s17m_56", "product", "56", e),
]
records.append(record(
    "scheme17_beta_elimination_mechanism", "mechanism", [10, 11], p,
    conditions=[field("operation", "oxypalladation of 52 to 53, addition of allenol 54 to 55, beta-elimination to 56, and palladium regeneration", e)],
    notes=["The prose proposes that TFA neutralizes in-situ generated hydroxide and thereby improves chirality transfer."],
    unresolved=["X, detailed ligand state, proton-transfer sequence, and structures of generic palladium species are not fully specified."],
))

# Scheme 18 specific bisallene cyclization.
e = ev(11)
p = [
    participant("s18_57", "reactant", "57", e, name="bisallene 57"),
    participant("s18_rh", "catalyst", "trans-RhCl(CO)(PPh3)2", e,
                amounts=[qty("catalyst_loading", {"number": 5, "unit": "mol%"}, e)]),
    participant("s18_tol", "solvent", "toluene", e),
    participant("s18_58", "product", "58", e, name="steroid-motif product 58"),
]
records.append(record(
    "scheme18_bisallene_cyclization", "literature_example", [11], p,
    conditions=[field("solvent", "toluene", e), field("temperature", "reflux", e),
                field("time", {"number": 2, "unit": "h"}, e)],
    outcomes=[field("yield", {"number": 69, "unit": "%"}, e, ["s18_58"]),
              field("yield_measurement_basis", None, targets=["s18_58"])],
    notes=["The review calls this a bimolecular cyclization and cites reference 22; substituent E is not defined on the inspected page."],
    unresolved=["Identity of E, stoichiometric interpretation of the bimolecular process, yield basis, workup, purification, and complete structures are unresolved."],
))

# Scheme 18 prose-only proposed cascade.
e = ev(11)
p = [
    participant("s18m_57", "reactant", "57", e),
    participant("s18m_58", "product", "58", e),
]
records.append(record(
    "scheme18_proposed_cascade", "mechanism", [11], p,
    conditions=[field("operation", "two cyclometallation-carbometallation events, pi-allyl metal formation, reductive elimination, then intramolecular Diels-Alder reaction", e)],
    notes=["The article explicitly says the mechanism is far from clear and presents these pathways only as proposals."],
    unresolved=["No intermediates, metal-ligation details, stereochemical sequence, or experimental support are specified on this page."],
))


records_path = Path(__file__).with_name("pages_0007_0012_records.json")
records_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

record_ids_by_page = {page: [] for page in range(7, 13)}
for item in records:
    for page in range(7, 13):
        if f"{DOC}:page{page}:image" in item["evidence_ids"]:
            record_ids_by_page[page].append(item["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {"region": "upper and middle: Scheme 11 and accompanying paragraph", "finding": "Three arrows/experiments were separated: direct S-35 coupling (49%, 23% ee), conversion to 1:1 salt S-(+)-37 with missing preparation conditions, and coupling of preformed S-(+)-37 (62%, 91% ee).", "evidence_ids": ev(7)},
                {"region": "bottom paragraph introducing Scheme 12", "finding": "Proposed explanation for loss versus retention of stereochemical information; the mechanism drawing continues on page 8.", "evidence_ids": ev(7)},
            ],
            "record_ids": record_ids_by_page[7],
            "unresolved": ["Scheme 11 omits several reagent amounts, the direct-acid reaction time, yield bases, workups, purifications, and fully verified stereochemical structures."],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {"region": "top and middle: Scheme 12", "finding": "Generic mechanistic comparison of acid and allenoate-salt paths through palladium species 38-40; not an independent experiment.", "evidence_ids": ev(8)},
                {"region": "bottom paragraph introducing Scheme 13", "finding": "Text reports PdCl2-catalyzed coupling-cyclization of S-41 with allyl bromide and attributes high chirality transfer to oxypalladation; exact rows and mechanism continue on page 9.", "evidence_ids": ev(8)},
            ],
            "record_ids": record_ids_by_page[8],
            "unresolved": ["Scheme 12 uses generic R/X/B/L labels; Scheme 13 quantitative rows require page 9 and no detailed workup is supplied."],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {"region": "top and middle: Scheme 13 reaction and two-row condition/result block", "finding": "Two distinct literature examples were recorded: 50 °C/16 h gives 44 in 90% and 93.5% ee; 25 °C/36.5 h gives 80% and 99.9% ee, both with 5 mol% PdCl2 in DMA.", "evidence_ids": ev(9)},
                {"region": "middle: Scheme 13 lower catalytic sequence", "finding": "Proposed oxypalladation/coupling pathway through intermediates 42 and 43, classified as mechanism rather than another experiment.", "evidence_ids": ev(9)},
                {"region": "bottom: Scheme 14", "finding": "Generic deuterium-labelled mechanism for coupling of 2,3-allenoic acids with an omega-alkenyl halide through species 45-48 to 49; no numerical conditions or yield.", "evidence_ids": ev(9)},
            ],
            "record_ids": record_ids_by_page[9],
            "unresolved": ["Scheme 13 lacks reactant quantities and yield basis; Scheme 14 has generic substituents/catalyst labels and no operating conditions."],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {"region": "top and upper middle: Scheme 15 and oxidant-protocol prose", "finding": "Generic alkyl-iodide protocol gives bisbutenolides 50 in 64-75%; prose-only KI and benzoquinone oxidant protocols were retained separately with missing numerical details.", "evidence_ids": ev(10)},
                {"region": "middle: Scheme 16", "finding": "Generic double cyclization of 2,3-allenoic acids with 5 equiv 1,2-allenyl ketones under 5 mol% PdCl2(MeCN)2 in MeCN at room temperature for 4 h; no yield shown.", "evidence_ids": ev(10)},
                {"region": "bottom paragraph introducing Scheme 17", "finding": "Text identifies allenoic-acid/allenol cyclization and distinguishes additive-free versus 0.8 equiv TFA conditions; structures and numerical results continue on page 11.", "evidence_ids": ev(10)},
            ],
            "record_ids": record_ids_by_page[10],
            "unresolved": ["Scheme 15 has no time or row-level scope; KI/benzoquinone protocols lack detailed conditions; Scheme 16 lacks yields; Scheme 17 lacks reaction time and workup."],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {"region": "top: Scheme 17", "finding": "Two condition lines were recorded separately: no TFA gives 56 in 58% and 36% ee, while 0.8 equiv TFA gives 62% and 98% ee under 5 mol% PdCl2 in DMA at 30 °C; the central cycle is a proposed mechanism.", "evidence_ids": ev(11)},
                {"region": "middle: Scheme 18", "finding": "Bisallene 57 cyclizes with 5 mol% trans-RhCl(CO)(PPh3)2 in refluxing toluene for 2 h to steroid motif 58 in 69%; a prose-only cascade is classified separately as an uncertain mechanism.", "evidence_ids": ev(11)},
                {"region": "lower: conclusion and acknowledgments", "finding": "No additional reaction arrows, tables, footnotes, or experimental records; conclusion and funding text only.", "evidence_ids": ev(11)},
            ],
            "record_ids": record_ids_by_page[11],
            "unresolved": ["Scheme 17 omits time and yield basis; Scheme 18 leaves substituent E undefined and gives no workup, purification, or yield basis; proposed mechanism is explicitly unclear."],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {"region": "entire page: references 1-22", "finding": "Bibliographic references only; no reaction arrow, table, figure, footnote condition, or new experimental result is shown.", "evidence_ids": ev(12)},
            ],
            "record_ids": [],
            "unresolved": ["Referenced primary papers were not supplied as source documents and were not used to fill missing experimental details."],
        },
    ],
}

coverage_dir = BASE / "coverage"
coverage_dir.mkdir(parents=True, exist_ok=True)
(coverage_dir / "pages_0007_0012.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
covered_task_ids = {f"{DOC}:page{page}:text" for page in range(7, 13)}
for task in tasks:
    if task.get("task_id") in covered_task_ids:
        task["state"] = "attempted"
        task["reason"] = "Page text and original rendered page image were inspected; see coverage/pages_0007_0012.json."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({
    "records": len(records),
    "records_path": str(records_path),
    "coverage_pages": len(coverage["pages"]),
}, ensure_ascii=False))
