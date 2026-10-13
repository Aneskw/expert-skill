import json
from pathlib import Path

DOC = "doc_1e29b02f2fac50bb"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def facts_ev(*pages):
    result = []
    for page in pages:
        result.extend(ev(page))
    return list(dict.fromkeys(result))


def fact(value, evidence):
    return {"value": value, "evidence_ids": evidence if value is not None else evidence,
            "verification": "unreviewed" if value is not None else "missing"}


def qty(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, evidence, targets=None):
    result = {"name": name, "fact": fact(value, evidence)}
    if targets:
        result["target_entity_ids"] = targets
    return result


def participant(entity_id, role, label, name, smiles, evidence, amounts=None):
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


def record(suffix, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants or [],
        "steps": steps or [],
        "outcomes": outcomes or [],
        "notes": [fact(n, evidence) for n in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Machine-extracted record requires chemical source review.",
                "No supporting-information file was explicitly associated with this dataset."
            ],
        },
    }


def common_1a(evidence, scale=1.0):
    return participant("1a", "reactant", "1a", "1-phenylprop-2-yn-1-ol",
                       "C#CC(O)c1ccccc1", evidence,
                       [field("amount", qty(scale, "mmol"), evidence)])


def butanal(evidence, equiv=1.4, detailed=False):
    amounts = [field("equivalents", qty(equiv, "equiv"), evidence)]
    if detailed:
        amounts += [field("amount", qty(1.61, "mmol"), evidence),
                    field("mass", qty(116.0, "mg"), evidence),
                    field("volume", qty(142, "uL"), evidence)]
    return participant("nPrCHO", "reactant", "n-PrCHO", "n-butanal", "CCCC=O",
                       evidence, amounts)


def cui(evidence, loading=10, mass=None, mmol=None):
    amounts = [field("catalyst_loading", qty(loading, "mol%"), evidence)]
    if mass is not None:
        amounts.append(field("mass", qty(mass, "mg"), evidence))
    if mmol is not None:
        amounts.append(field("amount", qty(mmol, "mmol"), evidence))
    return participant("CuI", "catalyst", "CuI", "copper(I) iodide", "[Cu]I",
                       evidence, amounts)


def nbu2nh(evidence, equiv=1.2, detailed=False, mmol=1.40, mass=181.4, volume=238):
    amounts = [field("equivalents", qty(equiv, "equiv"), evidence)]
    if detailed:
        amounts += [field("amount", qty(mmol, "mmol"), evidence),
                    field("mass", qty(mass, "mg"), evidence),
                    field("volume", qty(volume, "uL"), evidence)]
    return participant("nBu2NH", "reagent", "n-Bu2NH", "dibutylamine", "CCCCNCCCC",
                       evidence, amounts)


def product_2a(evidence):
    return participant("2a", "product", "2a", "1-phenylhepta-2,3-dien-1-ol",
                       "CCCC=C=CC(O)c1ccccc1", evidence)


def std_step(evidence, participant_ids, temp, time, solvent="dioxane", concentration=0.33,
             detailed=False):
    conditions = [field("solvent", solvent, evidence),
                  field("reaction_temperature", qty(temp, "°C"), evidence),
                  field("reaction_time", qty(time, "h"), evidence)]
    if concentration is not None:
        conditions.append(field("reaction_concentration", qty(concentration, "M"), evidence))
    if detailed:
        typical_ev = facts_ev(4)
        conditions += [field("atmosphere", "argon", typical_ev),
                       field("operation", "sealed screw-cap tube; stirred in an oil bath", typical_ev),
                       field("workup", "cooled to room temperature, filtered, and evaporated", typical_ev),
                       field("purification", "silica-gel column chromatography", typical_ev)]
    return [{"step_id": "reaction", "participant_ids": participant_ids, "conditions": conditions}]


records = []

# Page 1: generic/current route, two explicitly cited prior routes, and the nine Figure 1 screening trials.
e1 = facts_ev(1)
generic_parts = [
    participant("generic_alkyne", "reactant", "R-C≡CH", "generic terminal alkyne", None, e1),
    participant("generic_aldehyde", "reactant", "R'CHO", "generic aldehyde", None, e1),
    participant("generic_allene", "product", "R-C=C=CH-R'", "generic allene", None, e1),
    cui(e1, 10),
    participant("generic_dialkylamine", "reagent", "di(n-alkyl)amine", "dialkylamine matched to aldehyde", None, e1),
]
records.append(record("scheme1_current_general", "general_scheme", e1, generic_parts,
                      [{"step_id": "generic_transformation",
                        "participant_ids": [p["entity_id"] for p in generic_parts],
                        "conditions": []}],
                      notes=["Scheme 1 is a generic representation of the method reported in this paper."],
                      unresolved=["Generic R and R' groups do not define complete structures."]))

for suffix, aldehyde_label, catalyst_label, catalyst_amount, reagent_label, product_label in [
    ("scheme1_prior_paraformaldehyde", "(CH2O)n", "Cu(I)", 0.5, "R'2NH (R'=i-Pr or Cy)", "terminal allene"),
    ("scheme1_prior_aromatic_aldehyde", "ArCHO", "ZnI2", 0.8, "morpholine", "1,3-disubstituted allene"),
]:
    parts = [participant("alkyne", "reactant", "R-C≡CH", "generic terminal alkyne", None, e1),
             participant("aldehyde", "reactant", aldehyde_label, aldehyde_label, None, e1),
             participant("product", "product", product_label, product_label, None, e1),
             participant("catalyst", "unspecified_agent", catalyst_label, catalyst_label, None, e1,
                         [field("equivalents", qty(catalyst_amount, "equiv"), e1)]),
             participant("amine", "reagent", reagent_label, reagent_label, None, e1)]
    records.append(record(suffix, "literature_example", e1, parts,
                          [{"step_id": "cited_prior_route",
                            "participant_ids": [p["entity_id"] for p in parts], "conditions": []}],
                          notes=["Scheme 1 labels this arrow as a previous report; it is not a new experiment in this paper."],
                          unresolved=["Generic structures and operational details are not specified in Scheme 1."]))

figure1_amines = [
    ("A", "2-methylpiperazine", "CC1CNCCN1"),
    ("B", "imidazolidin-2-one", "O=C1NCCN1"),
    ("C", "N,N'-diisopropylethane-1,2-diamine", "CC(C)NCCNC(C)C"),
    ("D", "N,N'-dimethylpropane-1,3-diamine", "CNCCCNC"),
    ("E", "morpholine", "C1COCCN1"),
    ("F", "piperidine", "C1CCNCC1"),
    ("G", "pyrrolidine", "C1CCNC1"),
    ("H", "n-butylamine", "CCCCN"),
    ("I", "benzylamine", "NCC1=CC=CC=C1"),
]
for code, name, smiles in figure1_amines:
    parts = [common_1a(e1), butanal(e1, 1.4),
             participant("amine", "reagent", f"Figure 1 amine {code}", name, smiles, e1,
                         [field("equivalents", qty(1.2, "equiv"), e1)]),
             cui(e1, 10), product_2a(e1)]
    records.append(record(f"figure1_trial_{code.lower()}", "optimization_entry", e1, parts,
                          std_step(e1, [p["entity_id"] for p in parts[:-1]], 130, 11),
                          [field("reaction_result", "failed to promote the Table 1 reaction within 11 h", e1, ["2a"])],
                          unresolved=["Figure 1 gives a qualitative failure statement rather than a numerical yield.",
                                      "Amine names A-D are structure-based machine assignments and require review.",
                                      "No supporting-information file was explicitly associated with this dataset."]))

# Page 2: Tables 1-3, one independent record per row.
e2 = facts_ev(2)
table1 = [
    (1, "i-Pr2NH", "diisopropylamine", "CC(C)NC(C)C", 22, 31),
    (2, "Cy2NH", "dicyclohexylamine", "C1CCCCC1NC1CCCCC1", 20, 27),
    (3, "N-ethylisopropylamine", "N-ethylisopropylamine", "CCNC(C)C", 20, 38),
    (4, "2-methylpiperidine", "2-methylpiperidine", "CC1CCCCN1", 11, 20),
    (5, "n-Pr2NH", "dipropylamine", "CCCNCCC", 11, 56),
    (6, "n-Bu2NH", "dibutylamine", "CCCCNCCCC", 11, 70),
]
for entry, label, name, smiles, time, yld in table1:
    parts = [common_1a(e2), butanal(e2, 1.4),
             participant("amine", "reagent", label, name, smiles, e2,
                         [field("equivalents", qty(1.2, "equiv"), e2)]),
             cui(e2, 10), product_2a(e2),
             participant("internal_standard", "unspecified_agent", "CH2Br2", "dibromomethane", "BrCBr", e2)]
    outcomes = [field("reported_NMR_yield_2a", qty(yld, "%"), e2, ["2a"]),
                field("yield_measurement_basis", "NMR yield with CH2Br2 as internal standard", e2, ["2a"])]
    if entry == 1:
        outcomes.append(field("recovered_starting_material_yield", qty(16, "%"), e2, ["1a"]))
    records.append(record(f"table1_entry{entry}", "optimization_entry", e2, parts,
                          std_step(e2, [p["entity_id"] for p in parts[:4]], 130, time), outcomes))

table2 = [
    (1, "CuBr", 25, 58, 24), (2, "CuBr", 46, 40, 17),
    (3, "CuCl", 25, 43, 27), (4, "CuCN", 25, "table dash (–)", 70),
    (5, "CuBr2", 25, 55, 25), (6, "CuBr2", 46, 44, 10),
    (7, "Cu(OAc)2", 17, 2, 50), (8, "ZnCl2", 40, 52, 42),
    (9, "ZnI2", 40, 68, 18), (10, "Cu(OTf)2", 21, 19, 32),
    (11, "AgI", 21, "table dash (–)", 68),
]
for entry, catalyst, time, y2a, y3a in table2:
    parts = [common_1a(e2, 0.5), butanal(e2, 1.4), nbu2nh(e2, 1.2),
             participant("catalyst", "catalyst", catalyst, catalyst, None, e2,
                         [field("catalyst_loading", qty(10, "mol%"), e2)]),
             product_2a(e2),
             participant("3a", "product", "3a", "4-(N,N-dibutylamino)-1-phenylhept-2-yn-1-ol",
                         "CCCCN(CCCC)C(CCC)C#CC(O)c1ccccc1", e2),
             participant("internal_standard", "unspecified_agent", "1,3,5-trimethylbenzene",
                         "1,3,5-trimethylbenzene", "Cc1cc(C)cc(C)c1", e2)]
    outcomes = [field("reported_NMR_yield_2a", qty(y2a, "%") if isinstance(y2a, int) else y2a, e2, ["2a"]),
                field("reported_NMR_yield_3a", qty(y3a, "%"), e2, ["3a"]),
                field("yield_measurement_basis", "NMR yield using 1,3,5-trimethylbenzene as internal standard", e2,
                      ["2a", "3a"])]
    if entry == 11:
        outcomes.append(field("recovered_starting_material_yield", qty(10, "%"), e2, ["1a"]))
    records.append(record(f"table2_entry{entry}", "optimization_entry", e2, parts,
                          std_step(e2, [p["entity_id"] for p in parts[:4]], 130, time), outcomes,
                          unresolved=["Table 2 visibly reports the catalyst label as shown; entries 1/2 and 5/6 are distinct rows with different times.",
                                      "A table dash is preserved and not interpreted as zero.",
                                      "No supporting-information file was explicitly associated with this dataset."]))

solvent_smiles = {"dioxane": "O1CCOCC1", "DME": "COCCOC", "DMSO": "CS(C)=O",
                  "THF": "C1CCOC1", "DCE": "ClCCCl", "hexane": "CCCCCC",
                  "o-xylene": "Cc1ccccc1C"}
table3 = [
    (1, "dioxane", 11, 70, "table dash (–)"),
    (2, "DME", 22.5, 61, 14), (3, "DMSO", 13, {"number": 2, "unit": "%", "qualifier": "lt", "raw_text": "<2%"}, 46),
    (4, "THF", 17, 66, 9), (5, "DCE", 12, "complicated", "table dash (–)"),
    (6, "hexane", 13, 6, 79), (7, "o-xylene", 16, 59, "table dash (–)"),
]
for entry, solvent, time, y2a, y3a in table3:
    parts = [common_1a(e2), butanal(e2, 1.4), nbu2nh(e2, 1.2), cui(e2, 10),
             participant("solvent", "solvent", solvent, solvent, solvent_smiles[solvent], e2),
             product_2a(e2),
             participant("3a", "product", "3a", "4-(N,N-dibutylamino)-1-phenylhept-2-yn-1-ol",
                         "CCCCN(CCCC)C(CCC)C#CC(O)c1ccccc1", e2),
             participant("internal_standard", "unspecified_agent", "1,3,5-trimethylbenzene",
                         "1,3,5-trimethylbenzene", "Cc1cc(C)cc(C)c1", e2)]
    v2a = qty(y2a, "%") if isinstance(y2a, (int, float)) else y2a
    v3a = qty(y3a, "%") if isinstance(y3a, (int, float)) else y3a
    records.append(record(f"table3_entry{entry}", "optimization_entry", e2, parts,
                          std_step(e2, [p["entity_id"] for p in parts[:5]], 130, time, solvent=solvent),
                          [field("reported_NMR_yield_2a", v2a, e2, ["2a"]),
                           field("reported_NMR_yield_3a", v3a, e2, ["3a"]),
                           field("yield_measurement_basis", "NMR yield using 1,3,5-trimethylbenzene as internal standard",
                                 e2, ["2a", "3a"])],
                          unresolved=["The qualitative word 'complicated' and table dashes are preserved without numerical interpretation.",
                                      "No supporting-information file was explicitly associated with this dataset."]))

# Page 3 plus experimental evidence on pages 4-6: Table 4 scope entries.
table4 = [
    (1, "PhCH(OH)", "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", 10, 130, 12, 73, "2a", "1-phenylhepta-2,3-dien-1-ol", "CCCC=C=CC(O)c1ccccc1"),
    (2, "PhCH(OH)", "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", 10, 130, 13, 66, "2a", "1-phenylhepta-2,3-dien-1-ol", "CCCC=C=CC(O)c1ccccc1"),
    (3, "4-ClC6H4CH(OH)", "1b", "1-(4-chlorophenyl)prop-2-yn-1-ol", "C#CC(O)c1ccc(Cl)cc1", 10, 130, 12, 77, "2b", "1-(4-chlorophenyl)hepta-2,3-dien-1-ol", "CCCC=C=CC(O)c1ccc(Cl)cc1"),
    (4, "4-MeOC6H4CH(OH)", "1c", "1-(4-methoxyphenyl)prop-2-yn-1-ol", "COc1ccc(C(O)C#C)cc1", 10, 130, 12, 68, "2c", "1-(4-methoxyphenyl)hepta-2,3-dien-1-ol", "CCCC=C=CC(O)c1ccc(OC)cc1"),
    (5, "c-3,4-OCH2OC6H3CH(OH)", "1d", "1-(3,4-methylenedioxyphenyl)prop-2-yn-1-ol", "C#CC(O)c1ccc2OCOc2c1", 10, 130, 12, 74, "2d", "1-(3,4-methylenedioxyphenyl)hepta-2,3-dien-1-ol", "CCCC=C=CC(O)c1ccc2OCOc2c1"),
    (6, "n-C7H15CH(OH)", "1e", "1-decyn-3-ol", "C#CC(O)CCCCCCC", 10, 130, 36, 60, "2e", "tetradeca-4,5-dien-7-ol", "CCCC=C=CC(O)CCCCCCC"),
    (7, "n-C9H19CH(OH)", "1f", "1-dodecyn-3-ol", "C#CC(O)CCCCCCCCC", 10, 150, 18, 60, "2f", "hexadeca-4,5-dien-7-ol", "CCCC=C=CC(O)CCCCCCCCC"),
    (8, "c-CyCH(OH)", "1g", "1-cyclohexylprop-2-yn-1-ol", "C#CC(O)C1CCCCC1", 10, 150, 16, 64, "2g", "1-cyclohexylhepta-2,3-dien-1-ol", "CCCC=C=CC(O)C1CCCCC1"),
    (9, "c-(CH2)5C(OH)", "1h", "1-ethynylcyclohexan-1-ol", "C#CC1(O)CCCCC1", 10, 150, 21.5, 73, "2h", "1-(hexa-1,2-dienyl)cyclohexanol", "CCCC=C=CC1(O)CCCCC1"),
    (10, "4-MeC6H4CMe(OH)", "1i", "2-(p-tolyl)but-3-yn-2-ol", "C#CC(O)(C)c1ccc(C)cc1", 10, 150, 26, 72, "2i", "2-p-tolylocta-3,4-dien-2-ol", "CCCC=C=CC(O)(C)c1ccc(C)cc1"),
    (11, "n-C6H13CMe(OH)", "1j", "3-methyl-1-nonyn-3-ol", "C#CC(O)(C)CCCCCC", 10, 150, 26, 65, "2j", "7-methyltrideca-4,5-dien-7-ol", "CCCC=C=CC(O)(C)CCCCCC"),
    (12, "Ph2C(OH)", "1k", "1,1-diphenylprop-2-yn-1-ol", "C#CC(O)(c1ccccc1)c1ccccc1", 20, 150, 26, 59, "2k", "1,1-diphenylhepta-2,3-dien-1-ol", "CCCC=C=CC(O)(c1ccccc1)c1ccccc1"),
    (13, "4-EtC6H4CH(OH)CH2", "1l", "1-(4-ethylphenyl)but-3-yn-1-ol", "C#CCC(O)c1ccc(CC)cc1", 10, 150, 19, 62, "2l", "1-(4-ethylphenyl)octa-3,4-dien-1-ol", "CCCC=C=CCC(O)c1ccc(CC)cc1"),
    (14, "TsNHCH2", "1m", "N-tosylpropargylamine", "C#CCNS(=O)(=O)c1ccc(C)cc1", 20, 150, 46, 49, "2m", "N-tosyl(hepta-2,3-dienyl)amine", "CCCC=C=CCNS(=O)(=O)c1ccc(C)cc1"),
    (15, "n-C5H11CH(NHTs)", "1n", "N-tosyl(oct-1-yn-3-yl)amine", "C#CC(NS(=O)(=O)c1ccc(C)cc1)CCCCC", 20, 150, 41, 58, "2n", "N-tosyl(dodeca-4,5-dien-7-yl)amine", "CCCC=C=CC(NS(=O)(=O)c1ccc(C)cc1)CCCCC"),
    (16, "n-C7H15CH(NHTs)", "1o", "N-tosyl(dec-1-yn-3-yl)amine", "C#CC(NS(=O)(=O)c1ccc(C)cc1)CCCCCCC", 20, 150, 48, 54, "2o", "N-tosyl(tetradeca-4,5-dien-7-yl)amine", "CCCC=C=CC(NS(=O)(=O)c1ccc(C)cc1)CCCCCCC"),
    (17, "HO(CH2)9", "1p", "10-undecyn-1-ol", "C#CCCCCCCCCCO", 15, 150, 28, 54, "2p", "pentadeca-10,11-dien-1-ol", "CCCC=C=CCCCCCCCCCO"),
    (18, "BnOCH2", "1q", "1-benzyloxy-2-propyne", "C#CCOCc1ccccc1", 20, 150, 28, 55, "2q", "1-benzyloxyhepta-2,3-diene", "CCCC=C=CCOCc1ccccc1"),
    (19, "THPOCH2", "1r", "3-(tetrahydropyran-2-yloxy)-1-propyne", "C#CCOC1OCCCC1", 20, 150, 8.5, 40, "2r", "1-(tetrahydropyran-2-yloxy)hepta-2,3-diene", "CCCC=C=CCOC1OCCCC1"),
    (20, "n-C8H17", "1s", "1-decyne", "C#CCCCCCCC", 15, 150, 43, 66, "2s", "tetradeca-4,5-diene", "CCCC=C=CCCCCCCCC"),
]
detailed = {
    1: (4, 19.0, 0.10, 133.7, 1.01, 139.6),
    3: (4, 18.9, 0.099, 166.8, 1.00, 172.0),
    4: (5, 19.0, 0.10, 162.0, 1.00, 148.6),
    5: (5, 19.0, 0.10, 176.6, 1.00, 172.8),
    6: (5, 19.1, 0.10, 153.4, 0.99, 125.4),
    7: (5, 19.1, 0.10, 182.6, 1.00, 143.0),
    8: (6, 19.0, 0.10, 137.8, 1.00, 123.7),
    9: (6, 19.1, 0.10, 124.2, 1.00, 131.1),
    10: (6, 19.0, 0.10, 160.6, 1.00, 156.4),
    11: (6, 19.0, 0.10, 153.7, 1.00, 136.1),
    12: (6, 38.0, 0.10, 208.0, 1.00, None),
}
for entry, r_label, s_label, s_name, s_smiles, loading, temp, time, yld, p_label, p_name, p_smiles in table4:
    pages = [3]
    if entry in detailed:
        pages.append(detailed[entry][0])
    if entry == 4:
        pages.append(4)
    evidence = facts_ev(*sorted(set(pages)))
    detail = detailed.get(entry)
    if entry == 2:
        substrate_amounts = [field("amount", qty(8.0, "mmol"), facts_ev(3))]
    elif detail:
        substrate_amounts = [field("mass", qty(detail[3], "mg"), facts_ev(detail[0])),
                             field("amount", qty(detail[4], "mmol"), facts_ev(detail[0]))]
    else:
        substrate_amounts = [field("amount", qty(1.0, "mmol"), facts_ev(3))]
    substrate = participant(s_label, "reactant", s_label, s_name, s_smiles, evidence, substrate_amounts)
    product_amounts = []
    if detail and detail[5] is not None:
        product_amounts.append(field("mass", qty(detail[5], "mg"), facts_ev(detail[0])))
    product = participant(p_label, "product", p_label, p_name, p_smiles, evidence, product_amounts)
    if detail:
        cat = cui(evidence, loading, detail[1], detail[2])
        aldehyde = butanal(evidence, 1.6, True)
        amine = nbu2nh(evidence, 1.4, True)
    else:
        cat = cui(evidence, loading)
        aldehyde = butanal(evidence, 1.6)
        amine = nbu2nh(evidence, 1.4)
    solvent_amounts = []
    if entry == 2:
        solvent_amounts = [field("volume", qty(20, "mL"), facts_ev(3))]
    elif detail:
        solvent_amounts = [field("volume", qty(3, "mL"), facts_ev(detail[0]))]
    solvent = participant("dioxane", "solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", evidence, solvent_amounts)
    parts = [substrate, aldehyde, amine, cat, solvent, product]
    ops_detailed = detail is not None and entry != 12
    steps = std_step(evidence, [s_label, "nPrCHO", "nBu2NH", "CuI", "dioxane"], temp, time,
                     solvent="dioxane", detailed=ops_detailed)
    outcomes = [field("isolated_yield", qty(yld, "%"), facts_ev(3), [p_label]),
                field("yield_measurement_basis", "isolated yield", facts_ev(3), [p_label])]
    unresolved = ["No supporting-information file was explicitly associated with this dataset."]
    if entry not in detailed:
        unresolved.append("Only the Table 4 row was used within pages 1-6; operational workup and purification are not stated there.")
    if entry == 12:
        unresolved += ["The compound 2k paragraph continues on page 7, outside the claimed coverage range.",
                       "Page 6 prints CuI as 38.0 mg, 0.10 mmol while Table 4 gives 20 mol% for a 1 mmol substrate; the inconsistency is preserved."]
    if entry == 2:
        unresolved.append("The 8.0 mmol scale/20 mL dioxane footnote is structured; other scale-up operations occur outside pages 1-6.")
    records.append(record(f"table4_entry{entry}", "substrate_scope_entry", evidence, parts, steps,
                          outcomes, notes=[f"Table 4 R group: {r_label}."], unresolved=unresolved))

# Page 3 Scheme 2: three independent arrows.
e3 = facts_ev(3)
scheme2 = [
    ("paraformaldehyde", "paraformaldehyde", "(CH2O)n", None, "n-Bu2NH", "dibutylamine", "CCCCNCCCC", 130, 4.2, 67, "2t", "1-(4-chlorophenyl)buta-2,3-dien-1-ol", "C=C=CC(O)c1ccc(Cl)cc1"),
    ("propanal", "propanal", "EtCHO", "CCC=O", "n-Pr2NH", "dipropylamine", "CCCNCCC", 130, 11, 62, "2u", "1-(4-chlorophenyl)hexa-2,3-dien-1-ol", "CCC=C=CC(O)c1ccc(Cl)cc1"),
    ("isobutanal", "isobutanal", "i-PrCHO", "CC(C)C=O", "i-Bu2NH", "diisobutylamine", "CC(C)CNCC(C)C", 150, 11, 48, "2v", "1-(4-chlorophenyl)-5-methylhexa-2,3-dien-1-ol", "CC(C)C=C=CC(O)c1ccc(Cl)cc1"),
]
for key, aldehyde_name, aldehyde_label, aldehyde_smiles, am_label, am_name, am_smiles, temp, time, yld, p_label, p_name, p_smiles in scheme2:
    parts = [participant("1b", "reactant", "1b", "1-(4-chlorophenyl)prop-2-yn-1-ol", "C#CC(O)c1ccc(Cl)cc1", e3),
             participant("aldehyde", "reactant", aldehyde_label, aldehyde_name, aldehyde_smiles, e3),
             participant("amine", "reagent", am_label, am_name, am_smiles, e3), cui(e3, 10),
             participant("dioxane", "solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", e3),
             participant(p_label, "product", p_label, p_name, p_smiles, e3)]
    records.append(record(f"scheme2_{key}", "substrate_scope_entry", e3, parts,
                          std_step(e3, ["1b", "aldehyde", "amine", "CuI", "dioxane"], temp, time,
                                   concentration=None),
                          [field("isolated_yield", qty(yld, "%"), e3, [p_label]),
                           field("yield_measurement_basis", "isolated yield", e3, [p_label])],
                          unresolved=["Scheme 2 does not state substrate, aldehyde, amine, or solvent quantities on page 3.",
                                      "No supporting-information file was explicitly associated with this dataset."]))

# Equation 1: mismatched amine/aldehyde gives two product-specific yields.
parts = [common_1a(e3), participant("EtCHO", "reactant", "EtCHO", "propanal", "CCC=O", e3,
                                 [field("equivalents", qty(1.6, "equiv"), e3)]),
         nbu2nh(e3, 1.4), cui(e3, 10),
         participant("dioxane", "solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", e3),
         participant("eq1_R_Et", "product", "R=Et", "1-phenylhexa-2,3-dien-1-ol", "CCC=C=CC(O)c1ccccc1", e3),
         participant("eq1_R_nPr", "product", "R=propyl", "1-phenylhepta-2,3-dien-1-ol", "CCCC=C=CC(O)c1ccccc1", e3)]
records.append(record("equation1_mismatched_amine", "reported_experiment", e3, parts,
                      std_step(e3, ["1a", "EtCHO", "nBu2NH", "CuI", "dioxane"], 130, 12,
                               concentration=None),
                      [field("reported_yield_R_Et_product", qty(43, "%"), e3, ["eq1_R_Et"]),
                       field("reported_yield_R_nPr_product", qty(12, "%"), e3, ["eq1_R_nPr"])],
                      notes=["The paper attributes the n-propyl allene to butanal generated from hydrolysis of an in-situ imine."],
                      unresolved=["The yield measurement basis is not explicitly stated next to Equation 1.",
                                  "No supporting-information file was explicitly associated with this dataset."]))

# Table 5: common diisobutylamine scope, including footnote-b contaminant and entry-5 loading override.
table5 = [
    (1, "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", "Et", "propanal", "CCC=O", 130, 18, 49, "2w", "1-phenylhexa-2,3-dien-1-ol", "CCC=C=CC(O)c1ccccc1"),
    (2, "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", "Cy", "cyclohexanecarbaldehyde", "O=CC1CCCCC1", 130, 18, 39, "2x", "4-cyclohexyl-1-phenylbuta-2,3-dien-1-ol", "C1CCCCC1C=C=CC(O)c1ccccc1"),
    (3, "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", "n-C5H11", "hexanal", "CCCCCC=O", 140, 12, 55, "2y", "1-phenylnona-2,3-dien-1-ol", "CCCCCC=C=CC(O)c1ccccc1"),
    (4, "1a", "1-phenylprop-2-yn-1-ol", "C#CC(O)c1ccccc1", "i-PrCH2", "3-methylbutanal", "CC(C)CC=O", 140, 12, 45, "2z", "6-methyl-1-phenylhepta-2,3-dien-1-ol", "CC(C)CC=C=CC(O)c1ccccc1"),
    (5, "1t", "prop-2-yn-1-ol", "C#CCO", "n-C7H15", "octanal", "CCCCCCCC=O", 130, 8, 41, "2aa", "undeca-2,3-dien-1-ol", "CCCCCCCC=C=CCO"),
]
for entry, s_label, s_name, s_smiles, rprime, aldehyde_name, aldehyde_smiles, temp, time, yld, p_label, p_name, p_smiles in table5:
    loading = 20 if entry == 5 else 10
    parts = [participant(s_label, "reactant", s_label, s_name, s_smiles, e3,
                         [field("amount", qty(1.0, "mmol"), e3)]),
             participant("aldehyde", "reactant", "R'CHO", aldehyde_name, aldehyde_smiles, e3,
                         [field("equivalents", qty(1.6, "equiv"), e3)]),
             participant("iBu2NH", "reagent", "i-Bu2NH", "diisobutylamine", "CC(C)CNCC(C)C", e3,
                         [field("equivalents", qty(1.4, "equiv"), e3)]),
             cui(e3, loading), participant("dioxane", "solvent", "dioxane", "1,4-dioxane", "O1CCOCC1", e3),
             participant(p_label, "product", p_label, p_name, p_smiles, e3),
             participant("isobutyral_derived_allene", "product", "isobutyral-derived allene",
                         "allene derived from the alkyne and isobutyral", None, e3)]
    records.append(record(f"table5_entry{entry}", "substrate_scope_entry", e3, parts,
                          std_step(e3, [s_label, "aldehyde", "iBu2NH", "CuI", "dioxane"], temp, time),
                          [field("isolated_yield", qty(yld, "%"), e3, [p_label]),
                           field("yield_measurement_basis", "isolated yield", e3, [p_label]),
                           field("isobutyral_derived_allene_content",
                                 {"number": 5, "unit": "%", "qualifier": "lt", "raw_text": "less than 5%, if any"},
                                 e3, ["isobutyral_derived_allene"])],
                          notes=[f"Table 5 R' group: {rprime}."],
                          unresolved=["The footnote's isobutyral-derived allene is not assigned a complete structure.",
                                      "Operational workup and purification are not stated in Table 5 on page 3.",
                                      "No supporting-information file was explicitly associated with this dataset."]))

# Proposed mechanism, explicitly not treated as a reported experiment.
emech = facts_ev(3, 4)
records.append(record("scheme3_proposed_mechanism", "mechanism", emech,
                      notes=["Proposed cycle: copper acetylide 4 reacts with iminium 5 to form propargylic amine 3; intramolecular hydride transfer gives the allene and regenerates CuI.",
                             "The authors propose hydrolysis of imine 7 as the source of butanal/byproduct in Equation 1."],
                      unresolved=["Scheme 3 is a mechanistic proposal, not an independently reported batch experiment."]))

OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(records), "output": str(OUT)}, ensure_ascii=False))
