#!/usr/bin/env python3
"""Build evidence-linked review records for PDF pages 1-6."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_b414d70be6e70746"


def ev(page: int) -> list[str]:
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


SMILES = {
    "I2": "II",
    "Br2": "BrBr",
    "THF": "C1CCOC1",
    "DMSO": "CS(C)=O",
    "methanol": "CO",
    "toluene": "Cc1ccccc1",
    "allyl bromide": "C=CCBr",
    "NaI": "[Na+].[I-]",
    "LiOAc": "[Li+].CC(=O)[O-]",
    "water": "O",
    "NaH": "[Na+].[H-]",
    "KH": "[K+].[H-]",
    "DIBAL": None,
    "triethylamine": "CCN(CC)CC",
    "CuI": "[Cu]I",
    "cyclopentadiene": "C1=CCC=C1",
    "diazomethane": "C=[N+]=[N-]",
    "Et2NH": "CCNCC",
}


def participant(idx, role, label, evidence, amounts=None, smiles=None, name=None):
    if smiles is None:
        smiles = SMILES.get(label)
    return {
        "entity_id": f"e{idx}",
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [
            {"name": field_name, "fact": fact(value, evidence)}
            for field_name, value in (amounts or [])
        ],
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def rec(
    rid,
    pages,
    reactants,
    products,
    reagents=(),
    catalysts=(),
    solvents=(),
    conditions=(),
    outcomes=(),
    notes=(),
    kind="literature_example",
    extra_unresolved=(),
):
    evidence = []
    for page in pages:
        evidence.extend(ev(page))
    participants = []
    for role, items in (("reactant", reactants), ("product", products), ("reagent", reagents), ("catalyst", catalysts), ("solvent", solvents)):
        for item in items:
            if isinstance(item, str):
                label, amounts, smiles, name = item, [], None, None
            else:
                label = item[0]
                amounts = item[1] if len(item) > 1 else []
                smiles = item[2] if len(item) > 2 else None
                name = item[3] if len(item) > 3 else None
            participants.append(participant(len(participants) + 1, role, label, evidence, amounts, smiles, name))
    reactant_ids = [p["entity_id"] for p in participants if p["role"] == "reactant"]
    product_ids = [p["entity_id"] for p in participants if p["role"] == "product"]
    all_ids = [p["entity_id"] for p in participants]
    condition_fields = [field(name, value, evidence) for name, value in conditions]
    present = {x[0] for x in conditions}
    if "reaction_time" not in present:
        condition_fields.append(field("reaction_time", None, []))
    if "temperature" not in present:
        condition_fields.append(field("temperature", None, []))
    outcome_fields = []
    for item in outcomes:
        name, value = item[0], item[1]
        target_indices = item[2] if len(item) > 2 else tuple(range(len(products)))
        target_ids = [product_ids[i] for i in target_indices if i < len(product_ids)]
        outcome_fields.append(field(name, value, evidence, target_ids))
    if not any("yield" in item[0] for item in outcomes):
        outcome_fields.append(field("yield", None, [], product_ids))
    elif not any("measurement_basis" in item[0] for item in outcomes):
        outcome_fields.append(field("yield_measurement_basis", None, []))
    unresolved = [
        "This review summarizes cited literature; no external experimental procedure was imported.",
        "Generic or drawing-defined structures remain unverified and use null SMILES.",
        "Unreported scale, atmosphere, concentration, workup, purification, and isolated mass remain missing.",
        "No supporting-information file was supplied or associated.",
    ]
    unresolved.extend(extra_unresolved)
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": [{"step_id": "step1", "participant_ids": all_ids, "conditions": condition_fields}],
        "outcomes": outcome_fields,
        "notes": [fact(text, evidence) for text in notes],
        "review": {"method": "none", "reviewer": None, "checked_fields": [], "unresolved": unresolved},
    }


R = []

# Page 2: nucleophilic additions by amines/amides and alcohols/phenols.
R += [
    rec("p2_amine_aziridine_addition", [2], ["ethyl-substituted 1,2-allenic sulfoxide", "aziridine"],
        ["direct aziridine addition product", "double-bond-migrated aziridine adduct"],
        notes=["The review states that amine addition products can undergo hydrogen migration."]),
    rec("p2_ephedrine_tandem_cyclization", [2], ["generic 1,2-allenic sulfone", "ephedrine"],
        ["cyclic ephedrine-derived heterocycle"],
        notes=["Nucleophilic addition, double-bond rearrangement, and intramolecular O-cyclization retain the two ephedrine stereocenters."]),
    rec("p2_intramolecular_amide_addition", [2], ["amide-tethered 1,2-allenic sulfoxide"],
        ["indole-type intramolecular addition product"], notes=["Equation (1); intramolecular amide-nitrogen addition."]),
    rec("p2_alcohol_addition", [2], ["generic 1,2-allenic sulfone", "alcohol ROH"],
        ["vinyl ether addition product"], reagents=["sodium alkoxide RONa"],
        notes=["Equation (2); prolonged reaction can cause double-bond migration."]),
    rec("p2_vinyl_ether_double_bond_migration", [2], ["vinyl ether from alcohol addition to a 1,2-allenic sulfone"],
        ["double-bond-migrated vinyl ether"], conditions=[("reaction_time", "prolonged")],
        notes=["The review separately cites double-bond migration when the alcohol-addition reaction is allowed to proceed too long."]),
    rec("p2_allyl_alcohol_addition", [2], ["generic 1,2-allenic sulfone", "allylic alcohol"],
        ["allylic-ether addition intermediate"], reagents=["KH"], solvents=["THF"],
        conditions=[("temperature", {"number": 20, "unit": "°C"})], notes=["First arrow of Scheme 3."]),
    rec("p2_claisen_rearrangement", [2], ["Scheme 3 allylic-ether addition intermediate"],
        ["gamma,delta-unsaturated carbonyl compound"], solvents=["DMSO"],
        conditions=[("temperature", {"number": 135, "unit": "°C"})], notes=["Second arrow of Scheme 3; [3,3]-sigmatropic rearrangement."]),
    rec("p2_intramolecular_alcohol_addition", [2], ["hydroxy-tethered 1,2-allenic sulfoxide"],
        ["six-membered cyclic vinyl ether"], reagents=["NaH"], solvents=["THF"],
        notes=["Upper arrow of Scheme 4."]),
    rec("p2_intramolecular_phenol_addition", [2], ["phenol-tethered 1,2-allenic sulfoxide"],
        ["benzofuran-type cyclic product"], notes=["Lower arrow of Scheme 4."]),
]

# Page 3: carbon nucleophiles, carboxylate, hydroxylamine, and hydrohalogenation.
R += [
    rec("p3_malonate_addition", [3], ["generic 1,2-allenic sulfoxide", "sodium dimethyl malonate"],
        ["malonate-added allylic sulfoxide anion"], solvents=["THF"], conditions=[("temperature", "r.t.")],
        notes=["First arrow of Scheme 5."]),
    rec("p3_malonate_alkylation", [3], ["Scheme 5 malonate-added allylic sulfoxide anion", "alkyl halide R3X"],
        ["alkylated malonate-sulfoxide intermediate"], notes=["Second arrow of Scheme 5."]),
    rec("p3_phosphite_methanol_step", [3], ["Scheme 5 alkylated malonate-sulfoxide intermediate"],
        ["desulfinylated hydroxy-diene intermediate"], reagents=["trimethyl phosphite"], solvents=["methanol"],
        notes=["Third arrow of Scheme 5; exact transformation details are not stated in the review."],
        extra_unresolved=["The role and fate of trimethyl phosphite in this compact scheme require the cited paper."]),
    rec("p3_lactonization", [3], ["Scheme 5 hydroxy-diene intermediate"],
        ["beta-methylene-gamma-butyrolactone derivative"], notes=["Final arrow of Scheme 5; intramolecular lactonization."]),
    rec("p3_enamine_addition", [3], ["phenylsulfonylallene", "cyclopentanone-derived enamine"],
        ["unmigrated enamine addition product", "partly double-bond-migrated enamine product"],
        solvents=["toluene"], conditions=[("temperature", {"number": -50, "unit": "°C"})],
        notes=["Equation (3) gives two depicted products before base treatment."]),
    rec("p3_enamine_base_isomerization", [3], ["Equation (3) enamine-addition product mixture"],
        ["fully double-bond-migrated product"], reagents=["NaH"], conditions=[("temperature", {"number": 0, "unit": "°C"})],
        notes=["The review states that NaH affords entirely the migrated product."]),
    rec("p3_organocuprate_allylation", [3], ["p-tolylsulfonylallene"],
        ["allylated organocuprate-addition product"], reagents=["lithium trimethylcuprate", "allyl bromide"],
        conditions=[("operation", "organocuprate addition followed by trapping with allyl bromide")], notes=["Equation (4)."]),
    rec("p3_carboxylate_addition", [3], ["p-tolylsulfonylallene", "carboxylate anion RCOO-"],
        ["allylic enol ester"], solvents=["DMSO"], conditions=[("temperature", "r.t.")],
        notes=["Equation (5); the weakly basic system does not cause product double-bond migration."]),
    rec("p3_hydroxylamine_addition", [3], ["phenylsulfonylallene", "lithiated aryl hydroxylamine"],
        ["O-addition intermediate"], notes=["First arrow of Scheme 6."]),
    rec("p3_hydroxylamine_rearrangement", [3], ["Scheme 6 O-addition intermediate"],
        ["rearranged imine/sulfone-anion intermediate"], conditions=[("operation", "[3,3]-sigmatropic rearrangement")],
        notes=["Second arrow of Scheme 6; the drawn species is an intermediate, not an isolated product."]),
    rec("p3_hydroxylamine_cyclization", [3], ["Scheme 6 rearranged imine/sulfone-anion intermediate"],
        ["fused cyclic hydroxylamine-derived product"], notes=["Final arrow of Scheme 6; intramolecular nucleophilic addition."]),
    rec("p3_allenic_sulfone_hydrohalogenation", [3], ["generic 1,2-allenic sulfone", "halide salt MX"],
        ["generic beta,gamma-unsaturated alpha-halosulfone"], reagents=["acid H+"],
        conditions=[("temperature", "heated")], outcomes=[("family_yield", {"number": 70, "unit": "%", "qualifier": "gt", "raw_text": ">70%"})],
        notes=["Equation (6); X is Cl, Br, or I and M is Na or Li. Lithium salts are reported to react more readily than sodium salts."],
        extra_unresolved=["The three exact condition sets are not enumerated in this review page."]),
    rec("p3_allenic_sulfoxide_standard_hydrohalogenation_failure", [3], ["generic 1,2-allenic sulfoxide", "halide salt under acidic sulfone conditions"],
        [], outcomes=[("reaction_result", "no hydrohalogenation")], notes=["The review explicitly contrasts this failure with allenic sulfones."]),
    rec("p3_sulfoxide_AlX3_water_hydrohalogenation", [3], ["generic 1,2-allenic sulfoxide"],
        ["generic hydrohalogenated allenic-sulfoxide product"],
        reagents=[("AlX3 (X = Cl or Br)", [("equivalents", {"number": 0.5, "unit": "equiv"})]),
                  ("water", [("equivalents", {"number": 1.0, "unit": "equiv"})])],
        solvents=["THF"], conditions=[("temperature", "r.t.")], notes=["Upper arrow of Scheme 7."]),
    rec("p3_sulfoxide_AlCl3_NaI_water_hydroiodination", [3], ["phenylsulfinylallene"],
        ["iodohydrohalogenated allenic-sulfoxide product"],
        reagents=[("NaI", [("equivalents", {"number": 4.0, "unit": "equiv"})]),
                  ("AlCl3", [("equivalents", {"number": 0.5, "unit": "equiv"})]),
                  ("water", [("equivalents", {"number": 1.0, "unit": "equiv"})])],
        solvents=["THF"], conditions=[("temperature", "r.t.")],
        notes=["Lower arrow of Scheme 7; the review states that no hydrochlorination product forms."]),
    rec("p3_bulky_sulfoxide_hydrohalogenation_failure", [3], ["sterically hindered 1,2-allenic sulfoxide"],
        [], outcomes=[("reaction_result", "no hydrohalogenation")], notes=["Explicit substrate-limitation statement in the review prose."]),
    rec("p3_p4_sulfoxide_hydrohalogenation_family_context", [3, 4], ["1,2-allenic sulfoxide family under AlX3/water conditions"],
        ["hydrohalogenated sulfoxide family"], outcomes=[
            ("family_yield_range", {"minimum": 56, "maximum": 89, "unit": "%", "raw_text": "56%–89%"}),
            ("major_alkene_geometry", "Z-major"),
        ], notes=["The range applies to the family of preceding hydrohalogenation reactions and is not allocated to individual substrates."]),
]

# Page 4: electrophilic additions and Diels-Alder chemistry.
R += [
    rec("p4_allenic_sulfone_halogen_addition", [4], ["generic 1,2-allenic sulfone", "I2 or Br2"],
        ["beta,gamma-dihalogen addition product"], notes=["The prose attributes the iodine and bromine additions to Padwa; no row-specific conditions or yields are given."]),
    rec("p4_photoiodination", [4], ["phenylsulfinylallene", "I2"], ["1,2-diiodo addition product"],
        conditions=[("light_source", "250 W sunlamp")], notes=["Equation (7); irradiation is required for the sulfoxide iodination."]),
    rec("p4_bromination_hydrolysis", [4], ["gamma,gamma-dialkyl-substituted 1,2-allenic sulfoxide", "Br2"],
        ["hydroxybromination product"], reagents=["NaHCO3", "water"], solvents=["CCl4"],
        conditions=[("operation", "bromination followed by basic aqueous hydrolysis")], notes=["Equation (8); n = 0 or 1."]),
    rec("p4_iodohydroxylation", [4], ["generic 1,2-allenic sulfoxide", "I2"], ["E-hydroxyiodination product"],
        reagents=["LiOAc"], solvents=["MeCN-H2O (7:1)"], conditions=[("temperature", "r.t.")],
        outcomes=[("yield", {"number": 80, "unit": "%", "qualifier": "gt", "raw_text": ">80%"})],
        notes=["Equation (9); the review reports chemoselective, regioselective, and stereospecific reaction with inversion at sulfur."]),
    rec("p4_inter_DA_cyclopentadiene", [4], ["trichloromethylsulfinylallene", "cyclopentadiene"],
        ["Diels-Alder regioisomer 1", "Diels-Alder regioisomer 2"], notes=["Equation (10)."]),
    rec("p4_scheme8_DA", [4], ["1,2-dimethylenecyclohexane", "chloromethyl 1,2-allenic sulfoxide"],
        ["fused-ring Diels-Alder adduct"], conditions=[("temperature", {"number": 60, "unit": "°C"}), ("reaction_time", {"number": 3, "unit": "h"})],
        notes=["First arrow of Scheme 8."]),
    rec("p4_scheme8_ramberg_backlund", [4], ["Scheme 8 fused-ring sulfoxide adduct"],
        ["conjugated dimethylene fused-ring product"], reagents=["t-BuOK"], outcomes=[("yield", {"number": 57, "unit": "%"})],
        notes=["Second arrow of Scheme 8; Ramberg-Backlund elimination."]),
    rec("p4_scheme8_iterative_DA", [4], ["Scheme 8 conjugated dimethylene fused-ring product", "chloromethyl 1,2-allenic sulfoxide"],
        ["higher fused-polycycle product"], notes=["Final repeated-arrow portion of Scheme 8; the review describes iterative Diels-Alder/elimination construction."]),
    rec("p4_vinyl_allene_DA", [4], ["vinyl-substituted 1,2-allenic sulfoxide", "dimethyl triazolinedione"],
        ["vinyl-allene Diels-Alder adduct"], notes=["Equation (11); the substituted allene acts as the diene."]),
]

# Page 5: intramolecular Diels-Alder, dipolar, [2+2], and ene reactions.
R += [
    rec("p5_IMDA_180C", [5], ["tethered allenic sulfone substrate A"], ["fused bicyclic Diels-Alder product A"],
        conditions=[("temperature", {"number": 180, "unit": "°C"})], outcomes=[("yield", {"number": 30, "unit": "%"})], notes=["Upper row of Scheme 9."]),
    rec("p5_IMDA_80C", [5], ["tethered allenic sulfone substrate B"],
        ["fused bicyclic Diels-Alder product B1", "fused bicyclic Diels-Alder product B2"],
        conditions=[("temperature", {"number": 80, "unit": "°C"})], outcomes=[
            ("product_B1_yield", {"number": 54, "unit": "%"}, (0,)),
            ("product_B2_yield", {"number": 18, "unit": "%"}, (1,)),
        ], notes=["Lower row of Scheme 9."]),
    rec("p5_nitrone_dipolar_cycloaddition", [5], ["arylnitrone", "generic 1,2-allenic sulfoxide or sulfone"],
        ["1,3-dipolar cycloadduct"], notes=["First arrow of Scheme 10."]),
    rec("p5_nitrone_rearrangement", [5], ["Scheme 10 1,3-dipolar cycloadduct"], ["rearranged seven-membered intermediate"],
        conditions=[("operation", "[3,3]-rearrangement")], notes=["Second arrow of Scheme 10."]),
    rec("p5_nitrone_ring_contraction", [5], ["Scheme 10 rearranged intermediate"], ["indole derivative"],
        notes=["Final arrows of Scheme 10; the compact drawing omits operating details."]),
    rec("p5_diazomethane_cycloaddition", [5], ["phenylsulfonylallene", "diazomethane"], ["pyrazoline cycloadduct"],
        notes=["First arrow of Equation (12)."]),
    rec("p5_pyrazole_rearrangement", [5], ["Equation (12) pyrazoline cycloadduct"], ["pyrazole derivative"],
        outcomes=[("yield", {"number": 49, "unit": "%"})], notes=["Second arrow of Equation (12); double-bond migration."]),
    rec("p5_inter_2plus2", [5], ["methylenecyclohexane", "phenylsulfonylallene"],
        ["spirocyclobutane [2+2] product", "open-chain side product"], catalysts=["EtAlCl2"],
        outcomes=[("combined_yield", {"number": 25, "unit": "%"}, (0, 1)), ("product_ratio", "8:1", (0, 1))],
        notes=["Equation (13); the source describes the yield as low."]),
    rec("p5_intra_2plus2_generic", [5], ["tethered allenic sulfone with pendant alkene"], ["fused cyclobutane product"],
        notes=["Upper arrow of Scheme 11."]),
    rec("p5_intra_2plus2_thermal", [5], ["tethered cyclic allenic sulfone"],
        ["cyclobutane product", "rearranged bicyclic coproduct"], conditions=[("temperature", "heated")],
        outcomes=[("cyclobutane_product_yield", {"number": 27, "unit": "%"}, (0,))], notes=["Lower arrow of Scheme 11."]),
    rec("p5_intramolecular_ene", [5], ["homopropargylic alcohol bearing a remote alkene", "arylsulfinyl chloride"],
        ["intramolecular ene cyclization product"], outcomes=[("family_yield_range", {"minimum": 75, "maximum": 90, "unit": "%", "raw_text": "75%–90%"})],
        notes=["Equation (14); the bracketed species is a drawn intermediate, not an isolated record."]),
]

# Page 6: radical cyclization, rearrangement, and natural-product sequence.
R += [
    rec("p6_radical_cyclization", [6], ["iodo-tethered 1,2-allenic sulfoxide or sulfone"],
        ["four- to seven-membered cyclic alkene"], reagents=["Bu3SnH"], notes=["Equation (15); m = 1 or 2 and n = 1-4."]),
    rec("p6_1_5_hydrogen_shift", [6], ["gamma-alkenyl-substituted 1,2-allenic sulfoxide"],
        ["conjugated triene"], conditions=[("temperature", "heated")], notes=["Equation (16); [1,5]-hydrogen migration."]),
    rec("p6_sterpurene_stage1_coupling", [6], ["iodinated cyclobutene", "chiral enynol"],
        ["coupled enynol precursor"], catalysts=["Pd(PPh3)2Cl2", "CuI"], solvents=["Et2NH"],
        notes=["First arrow of Scheme 12."]),
    rec("p6_sterpurene_stage2_sulfinylation", [6], ["Scheme 12 coupled enynol precursor", "PhSCl"],
        ["chiral vinyl-homopropargyl allenic sulfoxide"], reagents=["triethylamine"],
        conditions=[("temperature", {"number": -78, "unit": "°C"})], notes=["Second arrow of Scheme 12."]),
    rec("p6_sterpurene_stage3_IMDA", [6], ["chiral Scheme 12 allenic sulfoxide"], ["stereospecific polycyclic Diels-Alder product"],
        conditions=[("operation", "intramolecular [4+2] cycloaddition")], notes=["Third arrow of Scheme 12; the review states the sulfinyl group is crucial."]),
    rec("p6_sterpurene_stage4_methyl_substitution", [6], ["Scheme 12 polycyclic sulfoxide"], ["methyl-substituted polycyclic intermediate"],
        reagents=["CH3MgBr"], catalysts=["Ni(dppp)Cl2"], solvents=["THF"], conditions=[("temperature", "reflux")],
        notes=["Fourth arrow of Scheme 12; methyl replaces the sulfinyl group."]),
    rec("p6_sterpurene_stage5_reduction", [6], ["Scheme 12 methyl-substituted polycyclic intermediate"], ["(+)-1-sterpurene"],
        reagents=["Na", "NH3", "t-BuOH"], conditions=[("temperature", {"number": -78, "unit": "°C"})],
        notes=["Final arrow of Scheme 12."]),
]


assert len(R) == 53, len(R)

page_records = {page: [] for page in range(1, 7)}
for record in R:
    for page in range(1, 7):
        if f"{DOC}:page{page}:image" in record["evidence_ids"]:
            page_records[page].append(record["record_id"])

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title, abstracts, keywords, and introductory prose", "finding": "Review framing and reactivity overview; no individual experiment is reported.", "evidence_ids": [f"{DOC}:page1:image"]},
                {"region": "Scheme 1 at lower right", "finding": "Orbital/structural illustration of allenic sulfoxide and sulfone, not a reaction arrow.", "evidence_ids": [f"{DOC}:page1:image"]},
            ],
            "record_ids": page_records[1],
            "unresolved": ["No reaction record was fabricated from the orbital illustration or introductory classification."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left column, amine/amide additions and Schemes 2 / equations (1)-(2)", "finding": "Cited nucleophilic-addition literature examples, including tandem cyclization and intramolecular amide addition.", "evidence_ids": [f"{DOC}:page2:image"]},
                {"region": "right column, Schemes 3-4", "finding": "Two-stage allylic-alcohol addition/rearrangement and two intramolecular O-addition examples.", "evidence_ids": [f"{DOC}:page2:image"]},
            ],
            "record_ids": page_records[2],
            "unresolved": ["No numerical yields, scales, or complete procedures are given for the page-2 examples."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "left column, Scheme 5 and equations (3)-(5)", "finding": "Cited carbon-nucleophile, organocuprate, enamine, and carboxylate reactions; Scheme 5 and equation (3) were split by successive arrows.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "right column, Scheme 6 and equation (6)", "finding": "Hydroxylamine addition/rearrangement/cyclization and generic allenic-sulfone hydrohalogenation.", "evidence_ids": [f"{DOC}:page3:image"]},
                {"region": "right-column lower Scheme 7 and prose", "finding": "Two AlX3/water hydrohalogenation arrows plus explicit ordinary-condition and sterically hindered sulfoxide failures.", "evidence_ids": [f"{DOC}:page3:image"]},
            ],
            "record_ids": page_records[3],
            "unresolved": ["The 56-89% range is family-level and is not allocated to either individual Scheme-7 arrow.", "The review says three sulfone hydrohalogenation condition sets were developed but does not enumerate them here."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "left column, equations (7)-(9)", "finding": "Electrophilic iodination, bromination/hydrolysis, and iodohydroxylation literature examples.", "evidence_ids": [f"{DOC}:page4:image"]},
                {"region": "right column, equation (10), Scheme 8, and equation (11)", "finding": "Intermolecular Diels-Alder examples and the iterative Diels-Alder/Ramberg-Backlund polycycle sequence.", "evidence_ids": [f"{DOC}:page4:image"]},
            ],
            "record_ids": page_records[4],
            "unresolved": ["Most page-4 arrows omit reaction scale, yield basis, workup, and purification."],
        },
        {
            "page": 5,
            "state": "attempted",
            "regions": [
                {"region": "upper left Scheme 9", "finding": "Two intramolecular Diels-Alder literature examples with explicit temperatures and yields.", "evidence_ids": [f"{DOC}:page5:image"]},
                {"region": "left middle Scheme 10 and equation (12)", "finding": "1,3-dipolar cycloaddition sequences split into successive cycloaddition/rearrangement/cyclization stages.", "evidence_ids": [f"{DOC}:page5:image"]},
                {"region": "right column equation (13), Scheme 11, and equation (14)", "finding": "Inter- and intramolecular [2+2] additions plus an intramolecular ene-reaction family.", "evidence_ids": [f"{DOC}:page5:image"]},
            ],
            "record_ids": page_records[5],
            "unresolved": ["For the lower Scheme-11 row, the printed 27% is attached only to the first depicted product; the coproduct yield is absent."],
        },
        {
            "page": 6,
            "state": "attempted",
            "regions": [
                {"region": "upper left equations (15)-(16)", "finding": "Intramolecular radical cyclization and [1,5]-hydrogen migration literature examples.", "evidence_ids": [f"{DOC}:page6:image"]},
                {"region": "left lower Scheme 12", "finding": "Five-stage cited synthesis of (+)-1-sterpurene, split arrow by arrow.", "evidence_ids": [f"{DOC}:page6:image"]},
                {"region": "right column references", "finding": "Bibliography only; no current-paper experiment was created from citations.", "evidence_ids": [f"{DOC}:page6:image"]},
            ],
            "record_ids": page_records[6],
            "unresolved": ["Scheme 12 omits stage yields, scales, and most operating details; these remain missing."],
        },
    ],
}

raw_path = OUT / "raw_model/records_pages_0001_0006.json"
raw_path.parent.mkdir(parents=True, exist_ok=True)
raw_path.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
coverage_path = OUT / "coverage/pages_0001_0006.json"
coverage_path.parent.mkdir(parents=True, exist_ok=True)
coverage_path.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = OUT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["document_id"] == DOC and task["task_id"] in {f"{DOC}:page{p}:text" for p in range(1, 7)}:
        task["state"] = "attempted"
        task["visual_evidence_id"] = task["visual_evidence_id"] or task["task_id"].replace(":text", ":image")
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(R), "coverage_pages": [p["page"] for p in coverage["pages"]]}, ensure_ascii=False))
