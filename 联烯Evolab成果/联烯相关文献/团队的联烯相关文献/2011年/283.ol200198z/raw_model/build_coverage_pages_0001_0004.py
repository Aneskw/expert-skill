#!/usr/bin/env python3
"""Write the visual coverage ledger for PDF pages 1-4."""
import json
from pathlib import Path

DOC = "doc_f2387aac509ba979"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "runs/current/coverage/pages_0001_0004.json"


def rid(suffix):
    return f"{DOC}:{suffix}"


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


t1 = [rid(f"table1_entry{i}") for i in range(1, 12)]
t2 = [rid(x) for x in [
    "table2_entry1_2a", "table2_entry2_2b", "table2_entry3_2c", "table2_entry4_2d",
    "table2_entry5_2e", "table2_entry6_2e", "table2_entry7_2e", "table2_entry8_2f",
    "table2_entry9_2g", "table2_entry10_2h", "table2_entry11_2i", "table2_entry12_2j",
]]
au = [rid("scheme3_au_ref16_1a"), rid("scheme3_au_ref16_1e"), rid("scheme3_au_ref16_1i")]
p4 = [rid(x) for x in [
    "scheme4_eq5_1k_E2k", "scheme4_eq6_1l_E2l", "scheme4_eq7_1m_E2m",
    "scheme5_1n", "scheme5_1o_toluene_120C", "scheme5_1o_trimethylbenzene_160C",
    "scheme6_hydrolysis_E5", "scheme6_iodination_E6", "scheme6_diels_alder_product7",
]]

coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 1,
            "state": "attempted",
            "regions": [
                {"region": "title and graphical abstract in the upper and middle page", "finding": "The generic Rh(I)-catalyzed allene-to-diene transformation, two alternative catalyst systems, 120 °C, maximum 92% yield, and E/Z claim were captured as a general scheme rather than an individual batch experiment.", "evidence_ids": ev(1)},
                {"region": "abstract and introduction below the graphical abstract", "finding": "Contains scope claims and background/prior-art discussion; no additional experiment specific enough to duplicate as a current-paper batch was found on this page.", "evidence_ids": ev(1)},
            ],
            "record_ids": [rid("graphical_abstract_general_rearrangement")],
            "unresolved": ["The graphical abstract uses generic R groups and does not identify which catalyst alternative applies to an individual substrate.", "No SI file was explicitly associated."],
        },
        {
            "page": 2,
            "state": "attempted",
            "regions": [
                {"region": "left-column Scheme 1, equations 1-3", "finding": "Three cited prior-work transformations were retained as literature examples with their visible yields/product ratios; they were not classified as experiments newly reported by this paper.", "evidence_ids": ev(2)},
                {"region": "right-column Scheme 2", "finding": "The Rh coordination/oxametalation/beta-elimination cycle and favored trans-4 rationale were captured as a proposed mechanism, without assigning an experimental yield to intermediates.", "evidence_ids": ev(2)},
                {"region": "lower-right optimization narrative", "finding": "The prose corroborates Table 1 entries 1-11, including the two no-reaction cases, catalyst-loading changes, and ligand additives; the independent row records are anchored primarily to the full table on page 3 and cross-linked here rather than duplicated.", "evidence_ids": ev(2)},
                {"region": "upper prose and references", "finding": "Discussion of earlier transition-metal rearrangements and references is contextual prior art; no further current-paper experiment was created.", "evidence_ids": ev(2)},
            ],
            "record_ids": [rid("scheme1_eq1_prior_propargylic_rearrangement"), rid("scheme1_eq2_prior_pivalate_migration"), rid("scheme1_eq3_prior_au_allenyl_isomerization"), rid("scheme2_proposed_rh_mechanism")] + t1,
            "unresolved": ["Scheme 1 uses generic R groups and omits most operating conditions.", "Mechanistic intermediates are proposed and not structure-verified."],
        },
        {
            "page": 3,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Table 1 and footnotes", "finding": "All eleven optimization rows were extracted independently, including NMR yields, E/Z ratios where present, recovered 1a, scale/volume overrides, PPh3 or PMe3 additives, and the 81% isolated yield footnote for entry 10.", "evidence_ids": ev(3)},
                {"region": "upper-right Table 2 and footnotes", "finding": "All twelve substrate-scope rows were extracted independently under Conditions A or B, including times, isolated yields, E/Z ratios, and the 4 mmol/1 mol% catalyst override for entry 7.", "evidence_ids": ev(3)},
                {"region": "lower-right Scheme 3 comparison table", "finding": "The Rh values duplicate Table 2 entries 1, 6, and 11 and were not duplicated. The three Au columns explicitly marked protocol ref. 16 were retained as literature-example records, with yield, selectivity, and recovery kept distinct.", "evidence_ids": ev(3)},
                {"region": "lower-right Scheme 3 equation 4", "finding": "Heating the 59/41 E-2e/Z-2e mixture with 2 mol% Rh(CO)(PPh3)2Cl in toluene at 120 °C for 5 h was extracted separately, giving a final 64/36 ratio; no yield was reported.", "evidence_ids": ev(3)},
                {"region": "lower-left and lower-right prose", "finding": "Narrative scope and comparison statements were reconciled with Table 2 and Scheme 3 and were not converted into duplicate experiments.", "evidence_ids": ev(3)},
            ],
            "record_ids": t1 + t2 + au + [rid("scheme3_eq4_EZ_heating_test")],
            "unresolved": ["Table rows omit atmosphere, workup and purification.", "Table 2 entry 7 does not make explicit whether the 6 mL solvent volume was scaled with the 4 mmol batch.", "The Au comparison is classified as cited literature because the figure explicitly marks protocol ref. 16."],
        },
        {
            "page": 4,
            "state": "attempted",
            "regions": [
                {"region": "upper-left Scheme 4 equations 5-7", "finding": "Three distinct scope experiments were extracted for p-nitrobenzoate 1k, carbonate 1l, and sterically hindered acetate 1m; catalyst/ligand loadings, time, temperature, yield, and reported E/Z values were preserved.", "evidence_ids": ev(4)},
                {"region": "middle-left Figure 1", "finding": "ORTEP drawing is characterization evidence for E-2k, not a separate reaction; it is linked to the Scheme 4 equation 5 record.", "evidence_ids": ev(4)},
                {"region": "upper-right Scheme 5", "finding": "The 1n arrow and both condition rows for 1o were extracted as three experiments. Combined product yield, stereoisomer ratio, and starting-material recovery remain separate outcomes.", "evidence_ids": ev(4)},
                {"region": "middle-right Scheme 6", "finding": "The hydrolysis, NIS iodination, and DMAD Diels-Alder arrows from E-2e were extracted as three independent experiments, including all explicit equivalents, catalyst/additive loading, solvents, temperatures, times, and yields.", "evidence_ids": ev(4)},
                {"region": "lower-page prose, summary, acknowledgments, SI notice and references", "finding": "Prose corroborates Scheme 5 and 6 products and yields. The SI notice states availability but no SI file was supplied or explicitly associated, so no SI-only details were imported.", "evidence_ids": ev(4)},
            ],
            "record_ids": p4,
            "unresolved": ["Most schemes omit reaction scale, solvent volume, yield measurement basis, atmosphere, workup and purification.", "Several depicted structures and all stereochemical assignments remain machine-unverified.", "Supporting Information was mentioned but not explicitly provided/associated."],
        },
    ],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT.relative_to(ROOT)), "pages": len(coverage["pages"]), "regions": sum(len(p["regions"]) for p in coverage["pages"])}, ensure_ascii=False))
