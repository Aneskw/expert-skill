#!/usr/bin/env python3
"""Build evidence-linked machine records for ja9904888 PDF pages 1-2."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current"
DOC = "doc_a5e08f86282a9d0c"
P1T = f"{DOC}:page1:text"
P1I = f"{DOC}:page1:image"
P2T = f"{DOC}:page2:text"
P2I = f"{DOC}:page2:image"


def fact(value, evidence=()):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence=()):
    return {"name": name, "fact": fact(value, evidence)}


def participant(entity_id, role, label, evidence, name=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None),
        "smiles": fact(None),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(evidence),
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [],
        },
    }


def missing_operation_fields():
    return [
        field("atmosphere", None),
        field("concentration", None),
        field("workup", None),
        field("purification", None),
    ]


records = []

# Scheme 1: two explicitly cited prior reactions, the current question, and its
# generic branching intermediate are not current-paper experimental runs.
records.append(record(
    "scheme1_prior_ag_cyclization", "literature_example", [P1I, P1T],
    participants=[
        participant("s1ag_allenol", "reactant", "generic 2,3-allenol (R1)", [P1I]),
        participant("s1ag_ag", "catalyst", "Ag+", [P1I]),
        participant("s1ag_product", "product", "generic 2,5-dihydrofuran derivative", [P1I]),
    ],
    notes=["Scheme 1 top arrow is attributed to references 4 and 5."],
    unresolved=["Generic R1 structure and literature-specific operating details are not supplied here."],
))
records.append(record(
    "scheme1_prior_pd_elimination", "literature_example", [P1I, P1T],
    participants=[
        participant("s1pd_allenol", "reactant", "generic 2,3-allenol (R1)", [P1I]),
        participant("s1pd_halide", "reactant", "R2X", [P1I]),
        participant("s1pd_pd", "catalyst", "Pd(0)", [P1I]),
        participant("s1pd_product", "product", "generic beta-R2-alpha,beta-unsaturated ketone", [P1I]),
    ],
    notes=["Scheme 1 middle arrow is attributed to reference 6 and described as insertion-beta-elimination."],
    unresolved=["Generic R groups, halide identity, loading, solvent, temperature, time, and yield are not supplied here."],
))
records.append(record(
    "scheme1_current_product_question", "general_scheme", [P1I, P1T],
    participants=[
        participant("s1q_allenol", "reactant", "generic 2,3-allenol (R1)", [P1I]),
        participant("s1q_halide", "reactant", "R2X", [P1I]),
        participant("s1q_pd", "catalyst", "Pd(0)", [P1I]),
        participant("s1q_dhf", "product", "possible 2,4-disubstituted 2,5-dihydrofuran", [P1I]),
        participant("s1q_epoxide", "product", "possible 2,3-disubstituted vinylic oxirane", [P1I]),
    ],
    notes=["The question mark and alternative products make this a problem-defining generic scheme, not an observed run."],
    unresolved=["No yield, substrate identity, or operating details apply to this generic question."],
))
records.append(record(
    "scheme1_candidate_branching_intermediate", "mechanism", [P1I, P1T],
    participants=[
        participant("s1m_intermediate", "unspecified_agent", "generic cationic Pd intermediate with pathways a, b, and c", [P1I]),
    ],
    notes=["Pathway a is beta-elimination; pathways b and c depict alternative oxygen attack directions."],
    unresolved=["The intermediate is schematic and is not reported as directly observed."],
))


scheme2_rows = [
    (1, "CH3CN", True, "reflux", 18, 67, "isolated", "18:1", None),
    (2, "CH3CN", False, "reflux", 18, 62, "300 MHz 1H NMR of crude; CH2Br2 internal standard", "14:1", None),
    (3, "CH3CN", True, 65, 18, 33, "300 MHz 1H NMR of crude; CH2Br2 internal standard", "15:1", 23),
    (4, "CH3CN", False, 65, 18, 32, "300 MHz 1H NMR of crude; CH2Br2 internal standard", "20:1", 18),
    (5, "DMF", False, 55, 14, 71, "isolated", "30:1", None),
]
for entry, solvent, silver, temp, hours, yld, basis, dr, recovered in scheme2_rows:
    ev = [P1I, P1T]
    ps = [
        participant(f"s2e{entry}_1a", "reactant", "1a", ev, "1,2-octadien-4-ol"),
        participant(f"s2e{entry}_2a", "reactant", "2a", ev, "iodobenzene (PhI)"),
        participant(f"s2e{entry}_k2co3", "reagent", "K2CO3", ev),
        participant(
            f"s2e{entry}_pd", "catalyst", "Pd(PPh3)4", ev,
            amounts=[field("catalyst loading", {"number": 5, "unit": "mol%"}, ev)],
        ),
        participant(f"s2e{entry}_solvent", "solvent", solvent, ev),
        participant(f"s2e{entry}_3a", "product", "3a", ev, "major trans-2-(1-phenylethenyl)-3-(n-butyl)oxirane"),
        participant(f"s2e{entry}_3ap", "product", "3a'", ev, "minor diastereomer of 3a"),
    ]
    if silver:
        ps.insert(3, participant(f"s2e{entry}_ag2co3", "reagent", "Ag2CO3", ev))
    step_fields = [
        field("temperature", temp if isinstance(temp, str) else {"number": temp, "unit": "°C"}, ev),
        field("time", {"number": hours, "unit": "h"}, ev),
    ] + missing_operation_fields()
    outcomes = [
        field("combined yield of 3a and 3a'", {"number": yld, "unit": "%"}, ev),
        field("yield measurement basis", basis, ev),
        field("diastereomer ratio 3a/3a'", dr, ev),
    ]
    if recovered is not None:
        outcomes.append(field("recovered 1a", {"number": recovered, "unit": "%"}, ev))
    notes = []
    if entry == 5:
        notes.append("Scheme 2 footnote e defines entry 5 as conditions A.")
    records.append(record(
        f"scheme2_entry_{entry}", "optimization_entry", ev, ps,
        [{"step_id": "cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": step_fields}],
        outcomes, notes,
        ["Participant charge amounts, concentration, atmosphere, workup, and purification are absent because the cited SI is not supplied."],
    ))


table1_rows = [
    (1, "n-C4H9", "Ph", 55, 14, "3a", 71, "96/4", None),
    (2, "n-C4H9", "p-MeO-C6H4", 52, 16, "3b", 71, "97/3", None),
    (3, "n-C4H9", "p-Me-C6H4", 53, 16, "3c", 70, "97/3", None),
    (4, "n-C4H9", "E-2-Ph-ethenyl", 54, 24, "3d", 65, "92/8", "minor isomer isolated by silica-gel chromatography"),
    (5, "n-C4H9", "naphthyl", 64, 48, "3e", 76, "96/4", "major relative configuration established as trans by NOESY"),
    (6, "Ph", "p-Me-C6H4", 52, 16, "3f", 55, "95/5", None),
    (7, "Ph", "p-MeO-C6H4", 53, 16, "3g", 66, "92/8", "minor isomer isolated by silica-gel chromatography"),
    (8, "n-C7H15", "p-Me-C6H4", 54, 16, "3h", 88, "97/3", None),
    (9, "n-C7H15", "p-MeO-C6H4", 52, 14, "3i", 81, "99/1", None),
    (10, "n-C7H15", "p-Br-C6H4", 56, 48, "3j", 80, "98/2", "C-I reacted while aryl C-Br remained intact"),
    (11, "n-C8H17", "E-1-hexenyl", 54, 20, "3k", 59, None, "cis isomer not observed"),
    (12, "n-C8H17", "p-Me-C6H4", 54, 16, "3l", 95, "97/3", "diastereomer data also confirmed by HPLC"),
    (13, "n-C8H17", "p-MeO-C6H4", 54, 16, "3m", 83, "98/2", "diastereomer data also confirmed by HPLC"),
    (14, "n-C8H17", "Ph", 58, 18, "3n", 78, "98/2", None),
    (15, "n-C8H17", "p-Br-C6H4", 56, 18, "3o", 46, "99/1", "diastereomer ratio determined from 400 MHz 1H NMR; C-I reacted while aryl C-Br remained intact"),
]
for entry, r1, r2, temp, hours, product, yld, dr, row_note in table1_rows:
    ev = [P1I, P1T, P2I, P2T]
    ps = [
        participant(f"t1e{entry}_allenol", "reactant", f"2,3-allenol 1 (R1={r1})", [P2I]),
        participant(f"t1e{entry}_iodide", "reactant", f"organoiodide 2 (R2={r2})", [P2I]),
        participant(f"t1e{entry}_k2co3", "reagent", "K2CO3", [P1I, P1T]),
        participant(
            f"t1e{entry}_pd", "catalyst", "Pd(PPh3)4", [P1I, P1T],
            amounts=[field("catalyst loading", {"number": 5, "unit": "mol%"}, [P1I])],
        ),
        participant(f"t1e{entry}_dmf", "solvent", "DMF", [P1I, P1T]),
        participant(f"t1e{entry}_product", "product", product, [P2I], f"vinylic oxirane {product} (R1={r1}, R2={r2})"),
    ]
    conditions = [
        field("condition set", "conditions A (base/catalyst/solvent inherited from Scheme 2 entry 5; row temperature and time override)", ev),
        field("temperature", {"number": temp, "unit": "°C"}, [P2I, P2T]),
        field("time", {"number": hours, "unit": "h"}, [P2I, P2T]),
    ] + missing_operation_fields()
    outcomes = [
        field("yield", {"number": yld, "unit": "%"}, [P2I, P2T]),
        field("yield measurement basis", None),
    ]
    if dr is None:
        outcomes.extend([
            field("diastereomer ratio", None),
            field("diastereoselectivity observation", "cis isomer not observed", [P2I, P2T]),
        ])
    else:
        outcomes.append(field("diastereomer ratio (major/minor)", dr, [P2I, P2T]))
        outcomes.append(field("dr measurement", "300 MHz 1H NMR of crude before separation" if entry != 15 else "400 MHz 1H NMR", [P2I, P2T]))
    notes = [row_note] if row_note else []
    records.append(record(
        f"table1_entry_{entry}", "substrate_scope_entry", ev, ps,
        [{"step_id": "insertion_cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        outcomes, notes,
        ["Yield basis, reagent equivalents, substrate charges, atmosphere, concentration, workup, and purification are not reported in the supplied main text."],
    ))


# Scheme 3 preparative sequence. Each arrow has its own reported yield and is
# retained as a distinct partial record.
prep_specs = [
    (
        1,
        [("ketone", "reactant", "1-undecyn-3-one", "1-undecyn-3-one"),
         ("chiral_al", "reagent", "chiral lithium aluminum hydride complex shown in Scheme 3", None),
         ("alcohol", "product", "(R)-1-undecyn-3-ol", "(R)-1-undecyn-3-ol")],
        [], 95,
        ["Identity of the reagent's OR group, solvent, temperature, time, charge amounts, product ee, workup, and purification are not specified in the supplied main text."],
    ),
    (
        2,
        [("alcohol", "reactant", "(R)-1-undecyn-3-ol", "(R)-1-undecyn-3-ol"),
         ("nbuli", "reagent", "n-BuLi", None),
         ("paraform", "reagent", "(CH2O)n", "paraformaldehyde"),
         ("diol", "product", "HOCH2-C≡C-CH(OH)-n-C8H17 (stereochemistry as drawn)", "chiral homopropargylic diol shown in Scheme 3")],
        [], 91,
        ["Solvent, temperature, time, charge amounts, workup, purification, and product ee are not specified."],
    ),
    (
        3,
        [("diol", "reactant", "HOCH2-C≡C-CH(OH)-n-C8H17 (stereochemistry as drawn)", "chiral homopropargylic diol shown in Scheme 3"),
         ("tsoh", "catalyst", "TsOH", None),
         ("dhp", "reagent", "DHP", "3,4-dihydro-2H-pyran"),
         ("thp", "product", "THPO-CH2-C≡C-CH(OH)-n-C8H17 (stereochemistry as drawn)", "THP-protected chiral propargylic alcohol")],
        [("TsOH loading", {"number": 10, "unit": "mol%"}), ("DHP amount", {"number": 1.1, "unit": "equiv"})], 78,
        ["Solvent, temperature, time, substrate charge, workup, purification, and product ee are not specified."],
    ),
    (
        4,
        [("thp", "reactant", "THPO-CH2-C≡C-CH(OH)-n-C8H17 (stereochemistry as drawn)", "THP-protected chiral propargylic alcohol"),
         ("lah", "reagent", "LiAlH4", "lithium aluminum hydride"),
         ("allenol", "product", "(R)-1b", "(R)-1,2-dodecadien-4-ol")],
        [], 61,
        ["Solvent, temperature, time, charge amounts, workup, purification, and product ee are not specified for this arrow."],
    ),
]
for idx, plist, special, yld, unresolved in prep_specs:
    ev = [P2I, P2T]
    ps = [participant(f"s3p{idx}_{eid}", role, label, ev, name) for eid, role, label, name in plist]
    for label, value in special:
        target = "s3p3_tsoh" if label.startswith("TsOH") else "s3p3_dhp"
        for p in ps:
            if p["entity_id"] == target:
                p["amounts"].append(field(label, value, ev))
    records.append(record(
        f"scheme3_preparation_step_{idx}", "reported_experiment", ev, ps,
        [{"step_id": f"preparation_step_{idx}", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": missing_operation_fields()}],
        [field("yield", {"number": yld, "unit": "%"}, [P2I]), field("yield measurement basis", None)],
        ["Scheme 3 reports this transformation as one arrow in the preparation of chiral allenol (R)-1b."], unresolved,
    ))


chiral_rows = [
    ("3k", "(1E)-hexenyl iodide", 98, 52, 98),
    ("3l", "p-iodotoluene", 95, 85, 96),
    ("3m", "p-iodoanisole", 98, 74, 97.5),
]
for product, iodide, input_ee, yld, product_ee in chiral_rows:
    ev = [P1I, P1T, P2I, P2T]
    ps = [
        participant(
            f"s3{product}_allenol", "reactant", "(R)-1b", [P2I, P2T], "(R)-1,2-dodecadien-4-ol",
            amounts=[field("enantiomeric excess", {"number": input_ee, "unit": "%"}, [P2I])],
        ),
        participant(f"s3{product}_iodide", "reactant", iodide, [P2I, P2T]),
        participant(f"s3{product}_k2co3", "reagent", "K2CO3", [P1I, P1T]),
        participant(
            f"s3{product}_pd", "catalyst", "Pd(PPh3)4", [P1I, P1T],
            amounts=[field("catalyst loading", {"number": 5, "unit": "mol%"}, [P1I])],
        ),
        participant(f"s3{product}_dmf", "solvent", "DMF", [P1I, P1T]),
        participant(f"s3{product}_product", "product", f"(R,R)-{product}", [P2I, P2T], f"chiral vinylic oxirane (R,R)-{product}"),
    ]
    conditions = [
        field("condition set", "conditions A as defined by Scheme 2 entry 5", ev),
        field("temperature", {"number": 55, "unit": "°C"}, [P1I, P1T]),
        field("time", {"number": 14, "unit": "h"}, [P1I, P1T]),
    ] + missing_operation_fields()
    records.append(record(
        f"scheme3_chiral_{product}", "reported_experiment", ev, ps,
        [{"step_id": "asymmetric_substrate_cyclization", "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"], "conditions": conditions}],
        [
            field("yield", {"number": yld, "unit": "%"}, [P2I]),
            field("yield measurement basis", None),
            field("product enantiomeric excess", {"number": product_ee, "unit": "%"}, [P2I, P2T]),
            field("ee measurement", "HPLC with CHIRALPAK AD column (0.46 cm x 25 cm)", [P2T]),
        ],
        ["This chiral run is distinct from the same product label in Table 1 because Scheme 3 reports a different yield and explicit substrate/product ee."],
        ["Substrate and reagent charges, concentration, atmosphere, workup, purification, and yield basis are absent because SI was not supplied."],
    ))


record_path = OUT / "raw_model/records_pages_0001_0002.json"
record_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

page1_ids = [r["record_id"] for r in records if P1I in r["evidence_ids"]]
page2_ids = [r["record_id"] for r in records if P2I in r["evidence_ids"]]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "upper-right Scheme 1 and pathways a-c", "finding": "Two explicitly cited prior-work arrows, one current generic product-space question, and one unobserved branching Pd-intermediate mechanism were classified separately.", "evidence_ids": [P1I, P1T]},
                {"region": "middle-right Scheme 2 reaction and five-row condition table", "finding": "Five distinct optimization experiments for 1a plus PhI were extracted row by row, including Ag2CO3 presence/absence, solvent, temperature, time, combined yield, dr, recovered starting material, and conditions A designation.", "evidence_ids": [P1I, P1T]},
                {"region": "left and lower-right article prose", "finding": "Prose links the first trials to Scheme 2, identifies the major 3e configuration as trans by NOESY, and states the p-bromoiodobenzene chemoselectivity later tabulated on page 2; cited background was not treated as current experiments.", "evidence_ids": [P1I, P1T]},
                {"region": "Scheme 2 footnotes", "finding": "NMR versus isolated-yield basis, recovered 1a percentages, and the conditions A definition were applied only to their corresponding rows.", "evidence_ids": [P1I, P1T]},
            ],
            "record_ids": page1_ids,
            "unresolved": [
                "Scheme 1 uses generic R groups and its candidate Pd intermediate is not directly observed.",
                "Scheme 2 omits reagent quantities, substrate charges, atmosphere, concentration, workup, and purification in the supplied main text.",
                "No SI file is supplied or explicitly associated, although the paper states that SI exists.",
            ],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 generic arrow and entries 1-15", "finding": "Fifteen substrate-scope rows were extracted separately with R1/R2 labels, row temperature/time, product label, yield, and dr or the explicit cis-not-observed result.", "evidence_ids": [P2I, P2T]},
                {"region": "Table 1 footnotes", "finding": "Crude-NMR dr method, separable-minor exceptions, cis-not-observed result, HPLC confirmations, and the 400 MHz override were attached only to the applicable rows.", "evidence_ids": [P2I, P2T]},
                {"region": "upper-right Scheme 3 preparative sequence", "finding": "Four successive arrows preparing (R)-1b were recorded independently with the displayed reagents and yields; omitted operating details remain missing.", "evidence_ids": [P2I, P2T]},
                {"region": "middle-right Scheme 3 chiral cyclizations", "finding": "Three current-paper chiral cyclizations to (R,R)-3k, -3l, and -3m were recorded separately from Table 1 because the displayed yields and ee data differ.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-left prose and footnote 11", "finding": "Prose confirms the Scheme 3 identities; the CHIRALPAK AD HPLC method was retained as the ee measurement method rather than a reaction condition.", "evidence_ids": [P2I, P2T]},
                {"region": "lower-right Supporting Information notice", "finding": "The article states that experimental details and spectra for 3a-o exist in SI, but no SI file is supplied in this pilot, so no association was inferred.", "evidence_ids": [P2I, P2T]},
            ],
            "record_ids": page2_ids,
            "unresolved": [
                "Table 1 and Scheme 3 do not state the yield measurement basis.",
                "Most row-specific charges, concentration, atmosphere, workup, purification, and isolated masses are unavailable without SI.",
                "Structures encoded only by drawings or generic R groups have null SMILES and remain unverified.",
                "The exact OR substituent in the depicted chiral aluminum reagent is not identified in the main-text scheme.",
            ],
        },
    ],
}
(OUT / "coverage/pages_0001_0002.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "page1_record_links": len(page1_ids), "page2_record_links": len(page2_ids)}, ensure_ascii=False))
