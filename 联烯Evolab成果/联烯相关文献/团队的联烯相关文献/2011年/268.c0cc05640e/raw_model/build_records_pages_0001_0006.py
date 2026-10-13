#!/usr/bin/env python3
"""Build machine-extracted records for Yu & Ma, Chem. Commun. 2011, PDF pages 1-6."""
import json
from pathlib import Path

DOC = "doc_e77fa99a0ade23d1"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def ev(*pages):
    ids = []
    for page in pages:
        ids.extend([f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"])
    return ids


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def qty(number=None, unit=None, minimum=None, maximum=None, raw_text=None, qualifier=None):
    value = {"unit": unit}
    if number is not None:
        value["number"] = number
    else:
        value["minimum"] = minimum
        value["maximum"] = maximum
    if raw_text is not None:
        value["raw_text"] = raw_text
    if qualifier is not None:
        value["qualifier"] = qualifier
    return value


def fld(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def part(entity_id, role, label, name, evidence, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [fld(n, v, evidence) for n, v in (amounts or [])],
    }


def step(step_id, participant_ids, evidence, conditions=None):
    conditions = list(conditions or [])
    names = {name for name, _ in conditions}
    if "temperature" not in names:
        conditions.append(("temperature", None))
    if "time" not in names:
        conditions.append(("time", None))
    return {
        "step_id": step_id,
        "participant_ids": participant_ids,
        "conditions": [fld(name, value, evidence) for name, value in conditions],
    }


def rec(rid, kind, evidence, participants, steps, outcomes=None, notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": participants,
        "steps": steps,
        "outcomes": outcomes or [],
        "notes": [fact(x, evidence) for x in (notes or [])],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "This feature article summarizes prior literature and does not provide a full batch procedure.",
                "Exact scale, atmosphere, workup, purification, and yield measurement basis are not reported here.",
                "Depicted structures and stereochemistry remain machine-unverified; generic R-group structures have null SMILES.",
                "Supporting Information was not supplied or explicitly associated.",
            ],
        },
    }


R = []

# Page 2: generic opening route.
E = ev(2)
p = [part("s1_vinyl", "reactant", "1-I", "vinyl precursor bearing leaving groups X/Y", E),
     part("s1_allene", "product", "1-II", "allene", E)]
R.append(rec("scheme1_general_1_2_elimination", "general_scheme", E, p,
             [step("s1", [x["entity_id"] for x in p], E)],
             notes=["Generic 1,2-elimination route; not a specific batch experiment."],
             unresolved=["Generic X/Y and R groups prevent unique structures or experimental conditions.",
                         "This is a general scheme, not a reported experiment."]))

# Schemes 2-9: prose on page 2, drawings on page 3.
E23 = ev(2, 3)
p = [part("s2_1", "reactant", "1", "2-bromo-3,3-difluoroallylic acetate derivative", E23),
     part("s2_nBuLi", "reagent", None, "n-butyllithium", E23),
     part("s2_hexane", "solvent", None, "hexane", E23),
     part("s2_2", "product", "2", "1,1-difluoroallene derivative", E23)]
R.append(rec("scheme2_difluoroallene_elimination", "literature_example", E23, p,
             [step("s1", [x["entity_id"] for x in p], E23,
                   [("temperature", qty(number=0, unit="°C")), ("time", qty(number=1, unit="min"))])],
             [fld("reported_yield", qty(minimum=65, maximum=90, unit="%", raw_text="65-90%"), E23, ["s2_2"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s3_4", "reactant", "4", "optically active ethyl 6-acetoxy-5-iodotetradeca-2,4-dienoate", E23),
     part("s3_iPrMgBr", "reagent", None, "isopropylmagnesium bromide", E23),
     part("s3_THF", "solvent", None, "tetrahydrofuran", E23),
     part("s3_5", "product", "5", "1,3-disubstituted allene", E23)]
R.append(rec("scheme3_mg_br_exchange_allene", "literature_example", E23, p,
             [step("s1", [x["entity_id"] for x in p], E23, [("temperature", qty(number=-78, unit="°C"))])],
             [fld("reported_yield", qty(number=89, unit="%"), E23, ["s3_5"]),
              fld("enantiomeric_excess", qty(number=91, unit="%"), E23, ["s3_5"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s4_6", "reactant", "6", "(Z)-3-phenylseleno-3-alkenyl methyl ether derivative", E23),
     part("s4_mCPBA", "reagent", None, "m-chloroperoxybenzoic acid", E23),
     part("s4_toluene", "solvent", None, "toluene", E23, smiles="Cc1ccccc1"),
     part("s4_DBU", "reagent", None, "DBU", E23),
     part("s4_7", "product", "7", "functionalized allene derivative", E23)]
R.append(rec("scheme4_selenoxide_elimination", "literature_example", E23, p,
             [step("oxidation", ["s4_6", "s4_mCPBA", "s4_toluene"], E23,
                   [("temperature", qty(number=0, unit="°C")), ("time", qty(number=1, unit="h"))]),
              step("elimination", ["s4_6", "s4_DBU", "s4_7"], E23,
                   [("temperature", qty(number=100, unit="°C")), ("time", qty(number=2, unit="h"))])],
             [fld("reported_yield", qty(minimum=85, maximum=92, unit="%", raw_text="85-92%"), E23, ["s4_7"]),
              fld("diastereoselectivity", "single diastereomer", E23, ["s4_7"]),
              fld("yield_measurement_basis", None, E23)],
             notes=["The review states that the corresponding E substrate gives alkyne rather than allene."]))

p = [part("s5_9", "reactant", "9", "1-chlorovinyl sulfoxide derivative", E23),
     part("s5_tBuMgCl", "reagent", None, "tert-butylmagnesium chloride", E23,
          [("equivalents", qty(number=0.13, unit="equiv"))]),
     part("s5_iPrMgCl", "reagent", None, "isopropylmagnesium chloride", E23,
          [("equivalents", qty(number=2.8, unit="equiv"))]),
     part("s5_lithiofuran", "reagent", None, "2-lithio-5-methoxyfuran", E23),
     part("s5_THF", "solvent", None, "tetrahydrofuran", E23, smiles="C1CCOC1"),
     part("s5_10", "product", "10", "functionalized allene", E23)]
R.append(rec("scheme5_sulfoxide_magnesium_exchange", "literature_example", E23, p,
             [step("exchange", ["s5_9", "s5_tBuMgCl", "s5_iPrMgCl", "s5_THF"], E23,
                   [("temperature", qty(number=-78, unit="°C"))]),
              step("trapping", ["s5_9", "s5_lithiofuran", "s5_THF", "s5_10"], E23,
                   [("temperature", qty(minimum=-78, maximum=-10, unit="°C", raw_text="-78 to -10 °C"))])],
             [fld("reported_yield", qty(minimum=40, maximum=54, unit="%", raw_text="40-54%"), E23, ["s5_10"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s6_13", "reactant", "13", "cyclic 1-chlorovinyl sulfoxide derivative", E23),
     part("s6_tBuMgCl", "reagent", None, "tert-butylmagnesium chloride", E23,
          [("equivalents", qty(number=0.13, unit="equiv"))]),
     part("s6_iPrMgCl", "reagent", None, "isopropylmagnesium chloride", E23,
          [("equivalents", qty(number=2.8, unit="equiv"))]),
     part("s6_enolate", "reactant", None, "lithium enolate of an alpha-chloroalkanoate", E23),
     part("s6_THF", "solvent", None, "tetrahydrofuran", E23, smiles="C1CCOC1"),
     part("s6_14", "product", "14", "fully substituted 2,3-allenoate", E23)]
R.append(rec("scheme6_allenoate_trapping", "literature_example", E23, p,
             [step("exchange", ["s6_13", "s6_tBuMgCl", "s6_iPrMgCl", "s6_THF"], E23,
                   [("temperature", qty(number=-78, unit="°C"))]),
              step("enolate_trapping", ["s6_13", "s6_enolate", "s6_THF", "s6_14"], E23,
                   [("temperature", qty(minimum=-78, maximum=-10, unit="°C", raw_text="-78 to -10 °C"))])],
             [fld("reported_yield", qty(minimum=17, maximum=51, unit="%", raw_text="17-51%"), E23, ["s6_14"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s7_17", "reactant", "17", "beta-ketoester derivative", E23),
     part("s7_LiHMDS_a", "reagent", None, "LiHMDS, first charge", E23,
          [("equivalents", qty(number=2, unit="equiv"))]),
     part("s7_Tf2O", "reagent", None, "triflic anhydride", E23,
          [("equivalents", qty(number=1, unit="equiv"))]),
     part("s7_LiHMDS_b", "reagent", None, "LiHMDS, second charge", E23,
          [("equivalents", qty(number=1, unit="equiv"))]),
     part("s7_HMPA", "reagent", None, "HMPA", E23,
          [("equivalents", qty(number=3, unit="equiv"))]),
     part("s7_ZnCl2", "reagent", None, "zinc chloride", E23),
     part("s7_18", "product", "18", "terminal 2,3-allenoate", E23)]
R.append(rec("scheme7_terminal_allenoate", "literature_example", E23, p,
             [step("vinyl_enolate_formation", ["s7_17", "s7_LiHMDS_a", "s7_Tf2O"], E23),
              step("allene_formation", [x["entity_id"] for x in p], E23,
                   [("temperature", qty(minimum=-78, maximum=20, unit="°C", raw_text="-78 °C to rt"))])],
             [fld("reported_yield", qty(minimum=68, maximum=78, unit="%", raw_text="68-78%"), E23, ["s7_18"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s8_20", "reactant", "20", "3-ethoxyspiro[3.5]non-2-en-1-one", E23),
     part("s8_Et3OBF4", "reagent", None, "triethyloxonium tetrafluoroborate", E23),
     part("s8_piperidine", "reactant", None, "piperidine (excess)", E23),
     part("s8_21", "product", "21", "cationic four-membered allene bearing two piperidino groups", E23)]
R.append(rec("scheme8_cationic_allene_21", "literature_example", E23, p,
             [step("alkylation_and_amination", [x["entity_id"] for x in p], E23)],
             [fld("reported_yield", qty(number=72, unit="%"), E23, ["s8_21"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s8b_21", "reactant", "21", "cationic four-membered allene precursor", E23),
     part("s8b_LDA", "reagent", None, "lithium diisopropylamide", E23),
     part("s8b_THF", "solvent", None, "tetrahydrofuran", E23, smiles="C1CCOC1"),
     part("s8b_22", "product", "22", "neutral cyclic four-membered allene", E23)]
R.append(rec("scheme8_lithiation_allene_22", "literature_example", E23, p,
             [step("lithiation", [x["entity_id"] for x in p], E23,
                   [("temperature", qty(number=-20, unit="°C"))])],
             [fld("reported_yield", None, E23, ["s8b_22"])],
             notes=["The product is reported stable for only several hours at -20 °C."]))

p = [part("s9_23", "reactant", "23", "five-membered cyclic allene cation precursor", E23),
     part("s9_pyrrolidine", "reactant", None, "pyrrolidine", E23),
     part("s9_nBuLi", "reagent", None, "n-butyllithium", E23),
     part("s9_THF", "solvent", None, "tetrahydrofuran", E23, smiles="C1CCOC1"),
     part("s9_24", "product", "24", "five-membered cyclic allene lithium tetrafluoroborate adduct", E23)]
R.append(rec("scheme9_cyclic_allene_24", "literature_example", E23, p,
             [step("formation", [x["entity_id"] for x in p], E23)],
             [fld("reported_yield", qty(number=26, unit="%"), E23, ["s9_24"]),
              fld("yield_measurement_basis", None, E23)]))

p = [part("s9b_23", "reactant", "23", "five-membered cyclic allene cation precursor", E23),
     part("s9b_ArOH", "reactant", None, "2,6-dimethylphenol", E23),
     part("s9b_Et3N", "reagent", None, "triethylamine", E23),
     part("s9b_KHMDS", "reagent", None, "KHMDS", E23),
     part("s9b_Et2O", "solvent", None, "diethyl ether", E23),
     part("s9b_25", "product", "25", "five-membered cyclic allene 25", E23)]
R.append(rec("scheme9_cyclic_allene_25", "literature_example", E23, p,
             [step("formation", [x["entity_id"] for x in p], E23)],
             [fld("reported_yield", qty(number=45, unit="%"), E23, ["s9b_25"]),
              fld("yield_measurement_basis", None, E23)]))

# Schemes 10-15: prose on page 2, drawings on page 4.
E24 = ev(2, 4)
p = [part("s10_26", "reactant", "26", "alpha,beta-unsaturated enone derivative", E24),
     part("s10_TsNHNH2", "reagent", None, "tosylhydrazine", E24),
     part("s10_EtOH", "solvent", None, "ethanol", E24),
     part("s10_NEt3", "reagent", None, "triethylamine", E24),
     part("s10_MS", "reagent", None, "4 angstrom molecular sieves", E24),
     part("s10_27", "product", "27", "allene derivative", E24)]
R.append(rec("scheme10_eliminative_h_migration", "literature_example", E24, p,
             [step("tosylhydrazone_formation", ["s10_26", "s10_TsNHNH2", "s10_EtOH"], E24,
                   [("temperature", "r.t.")]),
              step("diazene_elimination", ["s10_26", "s10_NEt3", "s10_MS", "s10_27"], E24,
                   [("temperature", "reflux")])],
             [fld("reported_yield", qty(minimum=33, maximum=93, unit="%", raw_text="33-93%"), E24, ["s10_27"]),
              fld("yield_measurement_basis", None, E24)],
             notes=["The review depicts tosylhydrazone 28 and diazene 29 as intermediates with loss of nitrogen."]))

p = [part("s11_30", "reactant", "30", "phosphorus ylide 30", E24),
     part("s11_31", "reactant", "31", "allylic carbonate 31", E24),
     part("s11_Pd", "catalyst", None, "allylpalladium chloride dimer", E24,
          [("catalyst_loading", qty(number=5, unit="mol%"))]),
     part("s11_ligand", "catalyst", None, "racemic Trost ligand shown in Scheme 11", E24,
          [("ligand_loading", qty(number=11, unit="mol%"))]),
     part("s11_Cs2CO3", "reagent", None, "cesium carbonate", E24),
     part("s11_dioxane", "solvent", None, "dioxane", E24),
     part("s11_ketene", "reactant", None, "substituted ketene shown in Scheme 11", E24),
     part("s11_32", "product", "32", "tetrasubstituted allene", E24)]
R.append(rec("scheme11_allylic_ylide_ketene", "literature_example", E24, p,
             [step("allylic_alkylation", ["s11_30", "s11_31", "s11_Pd", "s11_ligand", "s11_Cs2CO3", "s11_dioxane"], E24,
                   [("temperature", "reflux")]),
              step("ketene_olefination", ["s11_30", "s11_ketene", "s11_32"], E24,
                   [("temperature", "r.t."), ("time", qty(number=24, unit="h"))])],
             [fld("overall_reported_yield", qty(minimum=23, maximum=49, unit="%", raw_text="23-49%"), E24, ["s11_32"]),
              fld("yield_measurement_basis", None, E24)]))

p = [part("s12_36", "reactant", "36", "allylgallium reagent", E24),
     part("s12_alkynylMgBr", "reactant", None, "magnesium acetylide", E24),
     part("s12_THF", "solvent", None, "tetrahydrofuran", E24, smiles="C1CCOC1"),
     part("s12_ArCHO", "reactant", None, "aromatic aldehyde", E24),
     part("s12_37", "product", "37", "allyl allene", E24)]
R.append(rec("scheme12_allylgallation_allenylation", "literature_example", E24, p,
             [step("allylgallation", ["s12_36", "s12_alkynylMgBr", "s12_THF"], E24,
                   [("temperature", qty(number=60, unit="°C"))]),
              step("aldehyde_addition", [x["entity_id"] for x in p], E24)],
             [fld("reported_yield", qty(minimum=51, maximum=72, unit="%", raw_text="51-72%"), E24, ["s12_37"]),
              fld("yield_measurement_basis", None, E24)]))

p = [part("s13_39", "reactant", "39", "alpha-silyl alpha-diazo ketone", E24),
     part("s13_40", "reactant", "40", "silyl ketene", E24),
     part("s13_ether", "solvent", None, "ether", E24),
     part("s13_pentane", "solvent", None, "pentane", E24),
     part("s13_41", "product", "41", "1,3-diaryl-3-silyl-1-silyloxyallene", E24)]
R.append(rec("scheme13_diazo_ketone_silyl_ketene", "literature_example", E24, p,
             [step("cyclopropanonation_decarbonylation", [x["entity_id"] for x in p], E24,
                   [("temperature", "r.t."), ("time", qty(minimum=3, maximum=12, unit="h", raw_text="3-12 h")),
                    ("solvent_ratio", "ether/pentane")])],
             [fld("reported_yield", qty(minimum=51, maximum=83, unit="%", raw_text="51-83%"), E24, ["s13_41"]),
              fld("yield_measurement_basis", None, E24)],
             notes=["Intermediates 42 and 43 are proposed in the scheme and were not recorded as isolated products."]))

p = [part("s14_44", "reactant", "44", "beta-siloxy vinyl triflate derivative", E24),
     part("s14_TBAF", "reagent", None, "tetrabutylammonium fluoride", E24),
     part("s14_THF", "solvent", None, "tetrahydrofuran", E24, smiles="C1CCOC1"),
     part("s14_45", "product", "45", "trisubstituted allene", E24)]
R.append(rec("scheme14_c_c_fragmentation", "literature_example", E24, p,
             [step("fragmentation", [x["entity_id"] for x in p], E24, [("temperature", "r.t.")])],
             [fld("reported_yield", qty(minimum=52, maximum=78, unit="%", raw_text="52-78%"), E24, ["s14_45"]),
              fld("yield_measurement_basis", None, E24)]))

p = [part("s15_47", "reactant", "47", "vinylogous acyl triflate", E24),
     part("s15_NuH", "reactant", None, "nucleophile NuH listed in Scheme 15", E24),
     part("s15_Cs2CO3", "reagent", None, "cesium carbonate", E24),
     part("s15_DMA", "solvent", None, "DMA", E24),
     part("s15_48", "product", "48", "beta-functionalized trisubstituted allene", E24)]
R.append(rec("scheme15_grob_fragmentation", "literature_example", E24, p,
             [step("nucleophilic_fragmentation", [x["entity_id"] for x in p], E24,
                   [("temperature", qty(number=23, unit="°C"))])],
             [fld("reported_yield", qty(minimum=51, maximum=78, unit="%", raw_text="51-78%"), E24, ["s15_48"]),
              fld("yield_measurement_basis", None, E24)]))

# Schemes 16-17: page 3 discussion and page 4 drawings.
E34 = ev(3, 4)
p = [part("s16a_diene", "reactant", "1-III/1-IV", "2-halo-1,3-butadiene or alkylidene-pi-allylpalladium intermediate", E34),
     part("s16a_Nu", "reactant", None, "nucleophile", E34),
     part("s16a_diene_product", "product", "1-V", "substituted 1,3-butadiene", E34),
     part("s16a_allene", "product", "1-VI", "alpha-functionalized allene", E34)]
R.append(rec("scheme16_regiodivergent_substitution", "general_scheme", E34, p,
             [step("substitution", [x["entity_id"] for x in p], E34)],
             notes=["Scheme 16 contrasts SN2 and SN2-prime regioisomeric products for organocuprate/Pd pathways."],
             unresolved=["Generic Nu, X, R groups and alternative regioisomeric pathways prevent unique conditions and structures.",
                         "This is a general reaction/mechanistic scheme, not a batch experiment."]))

p = [part("s16b_1VII", "reactant", "1-VII", "2-halo-1,3-butadiene", E34),
     part("s16b_NuH", "reactant", None, "pronucleophile NuH", E34),
     part("s16b_Pd", "catalyst", None, "palladium(0) catalyst with chiral ligand", E34),
     part("s16b_base", "reagent", None, "base", E34),
     part("s16b_1VIII", "product", "1-VIII", "axially chiral alpha-functionalized allene", E34)]
R.append(rec("scheme16_pd_asymmetric_substitution", "general_scheme", E34, p,
             [step("asymmetric_substitution", [x["entity_id"] for x in p], E34)],
             unresolved=["Generic NuH, X, R, catalyst, ligand and base prevent unique structures or conditions.",
                         "This is a general reaction scheme, not a batch experiment."]))

p = [part("s17_50", "reactant", "50", "2-bromo-1,3-diene or related triflate", E34),
     part("s17_51", "reactant", "51", "fluorobis(phenylsulfonyl)methane", E34),
     part("s17_Pd", "catalyst", None, "allylpalladium chloride dimer", E34,
          [("catalyst_loading", qty(number=5, unit="mol%"))]),
     part("s17_dppb", "catalyst", None, "dppb", E34, [("ligand_loading", qty(number=5, unit="mol%"))]),
     part("s17_KOtBu", "reagent", None, "potassium tert-butoxide", E34),
     part("s17_CH2Cl2", "solvent", None, "dichloromethane", E34),
     part("s17_52", "product", "52", "fluorobis(phenylsulfonyl)methylated allene", E34)]
R.append(rec("scheme17_fluorobis_sulfonylmethylation", "literature_example", E34, p,
             [step("coupling", [x["entity_id"] for x in p], E34,
                   [("temperature", qty(number=40, unit="°C")), ("time", qty(number=12, unit="h"))])],
             [fld("reported_yield", qty(minimum=42, maximum=93, unit="%", raw_text="42-93%"), E34, ["s17_52"]),
              fld("yield_measurement_basis", None, E34)]))

p = [part("s17b_52", "reactant", "52", "fluorobis(phenylsulfonyl)methylated allene", E34),
     part("s17b_Mg", "reagent", None, "activated magnesium turnings", E34),
     part("s17b_MeOH", "solvent", None, "methanol", E34),
     part("s17b_THF", "solvent", None, "tetrahydrofuran", E34, smiles="C1CCOC1"),
     part("s17b_product", "product", None, "beta-fluoroallene", E34)]
R.append(rec("scheme17_reductive_desulfonylation", "literature_example", E34, p,
             [step("desulfonylation", [x["entity_id"] for x in p], E34,
                   [("solvent_ratio", "MeOH/THF 1/3")])],
             [fld("reported_yield", "high", E34, ["s17b_product"]),
              fld("yield_measurement_basis", None, E34)]))

# Page 5 Schemes 18-19.
E5 = ev(5)
p = [part("s18_2I", "reactant", "2-I", "activated propargylic compound FG-CH2-C≡C", E5),
     part("s18_base", "reagent", None, "base", E5),
     part("s18_2II", "product", "2-II", "allene", E5)]
R.append(rec("scheme18_propargyl_allene_isomerization", "general_scheme", E5, p,
             [step("isomerization", [x["entity_id"] for x in p], E5)],
             notes=["FG is listed generically as alkenyl, alkynyl, aryl, carbonyl, RO-, R2N-, RS-, or P(O)(OEt)2-."],
             unresolved=["Generic FG/R groups and base prevent unique structures and conditions.",
                         "This is a general scheme, not a batch experiment."]))

E45 = ev(4, 5)
p = [part("s19_54", "reactant", "54", "polychloro bridged bicyclic propargyl alcohol", E45),
     part("s19_KOH", "reagent", None, "powdered potassium hydroxide", E45),
     part("s19_benzene", "solvent", None, "benzene", E45, smiles="c1ccccc1"),
     part("s19_55", "product", "55", "polychloro bridged bicyclic allenol", E45)]
R.append(rec("scheme19_bicyclic_allenol_isomerization", "literature_example", E45, p,
             [step("isomerization", [x["entity_id"] for x in p], E45,
                   [("temperature", qty(number=80, unit="°C"))])],
             [fld("reported_yield", qty(minimum=80, maximum=85, unit="%", raw_text="80-85%"), E45, ["s19_55"]),
              fld("yield_measurement_basis", None, E45)]))

# Schemes 20-30: explanatory prose on page 5, drawings on page 6.
E56 = ev(5, 6)
p = [part("s20_56", "reactant", "56", "CF3-substituted propargylic tosylate", E56),
     part("s20_NaOH", "reagent", None, "sodium hydroxide", E56,
          [("equivalents", qty(number=3, unit="equiv"))]),
     part("s20_THF", "solvent", None, "tetrahydrofuran", E56, smiles="C1CCOC1"),
     part("s20_H2O", "solvent", None, "water", E56, smiles="O"),
     part("s20_57", "product", "57", "CF3-substituted allenyl tosylate", E56)]
R.append(rec("scheme20_cf3_propargyl_isomerization", "literature_example", E56, p,
             [step("isomerization", [x["entity_id"] for x in p], E56,
                   [("temperature", "r.t."), ("solvent_ratio", "THF/H2O 2/1")])],
             [fld("reported_yield", qty(minimum=78, maximum=99, unit="%", raw_text="78-99%"), E56, ["s20_57"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s21_58", "reactant", "58", "3-alkynoate", E56),
     part("s21_59", "catalyst", "59", "chiral bicyclic guanidine", E56,
          [("catalyst_loading_option_1", qty(number=2, unit="mol%")),
           ("catalyst_loading_option_2", qty(number=4, unit="mol%"))]),
     part("s21_THF", "solvent", None, "tetrahydrofuran", E56, smiles="C1CCOC1"),
     part("s21_hexane", "solvent", None, "hexane", E56),
     part("s21_60", "product", "60", "optically active 2,3-dienoate", E56)]
R.append(rec("scheme21_enantioselective_isomerization", "literature_example", E56, p,
             [step("isomerization", [x["entity_id"] for x in p], E56,
                   [("temperature", qty(number=-20, unit="°C")),
                    ("time", qty(minimum=30, maximum=34, unit="h", raw_text="30-34 h")),
                    ("solvent_choice", "THF or hexane")])],
             [fld("reported_yield", qty(minimum=39, maximum=94, unit="%", raw_text="39-94%"), E56, ["s21_60"]),
              fld("enantiomeric_excess", qty(minimum=86, maximum=95, unit="%", raw_text="86-95% ee"), E56, ["s21_60"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s22_61", "reactant", "61", "homopropargyl alcohol", E56),
     part("s22_RuCl3", "catalyst", None, "ruthenium(III) chloride", E56,
          [("catalyst_loading", qty(number=4, unit="mol%"))]),
     part("s22_TBHP", "reagent", None, "tert-butyl hydroperoxide", E56,
          [("equivalents", qty(number=4, unit="equiv"))]),
     part("s22_bmimPF6", "solvent", None, "[bmim]PF6 ionic liquid", E56),
     part("s22_62", "product", "62", "alpha-allenyl ketone", E56)]
R.append(rec("scheme22_oxidation_isomerization", "literature_example", E56, p,
             [step("oxidation_isomerization", [x["entity_id"] for x in p], E56,
                   [("temperature", qty(number=80, unit="°C"))])],
             [fld("reported_yield", qty(minimum=21, maximum=76, unit="%", raw_text="21-76%"), E56, ["s22_62"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s23_63", "reactant", "63", "1-bromoethylbenzene", E56, smiles="CC(Br)c1ccccc1"),
     part("s23_64", "reactant", "64", "trialkynylindium derivative of ethyl propiolate", E56),
     part("s23_Ni", "catalyst", None, "NiBr2·diglyme", E56,
          [("catalyst_loading", qty(number=10, unit="mol%"))]),
     part("s23_Pybox", "catalyst", None, "(S)-(iPr)-Pybox", E56,
          [("ligand_loading", qty(number=13, unit="mol%"))]),
     part("s23_DMA", "solvent", None, "DMA", E56),
     part("s23_THF", "solvent", None, "tetrahydrofuran", E56, smiles="C1CCOC1"),
     part("s23_65", "product", "65", "axially chiral allene", E56)]
R.append(rec("scheme23_nickel_asymmetric_coupling", "literature_example", E56, p,
             [step("coupling", [x["entity_id"] for x in p], E56,
                   [("temperature", "r.t."), ("time", qty(number=140, unit="h")),
                    ("solvent_ratio", "DMA/THF 1/1")])],
             [fld("reported_yield", qty(number=30, unit="%"), E56, ["s23_65"]),
              fld("enantiomeric_excess", qty(number=77, unit="%"), E56, ["s23_65"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s24_propargyl", "reactant", "2-III", "propargylic compound bearing a leaving group", E56),
     part("s24_Nu", "reactant", None, "nucleophile", E56),
     part("s24_allene", "product", "2-IV", "substituted allene", E56)]
R.append(rec("scheme24_sn2prime_general", "general_scheme", E56, p,
             [step("SN2_prime_substitution", [x["entity_id"] for x in p], E56)],
             unresolved=["Generic LG, Nu and R groups prevent unique structures and conditions.",
                         "This is a general substitution scheme, not a batch experiment."]))

p = [part("s25_66", "reactant", "66", "aryl-substituted propargyl alcohol", E56),
     part("s25_NXS", "reagent", None, "N-halosuccinimide", E56),
     part("s25_PPh3", "reagent", None, "triphenylphosphine", E56),
     part("s25_CH2Cl2", "solvent", None, "dichloromethane", E56),
     part("s25_68", "product", "68", "chloro- or bromoallene", E56)]
R.append(rec("scheme25_haloallene_appel", "literature_example", E56, p,
             [step("halogenation", [x["entity_id"] for x in p], E56, [("temperature", "r.t.")])],
             [fld("reported_yield", qty(minimum=55, maximum=88, unit="%", raw_text="55-88%"), E56, ["s25_68"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s26a_69", "reactant", "69", "1-arylpropargylic alcohol", E56),
     part("s26a_CBr4", "reagent", None, "carbon tetrabromide", E56,
          [("equivalents", qty(number=2, unit="equiv"))]),
     part("s26a_PPh3", "reagent", None, "triphenylphosphine", E56,
          [("equivalents", qty(number=2, unit="equiv"))]),
     part("s26a_DIPEA", "reagent", None, "diisopropylethylamine", E56,
          [("equivalents", qty(number=2, unit="equiv"))]),
     part("s26a_nBu3P", "reagent", None, "tributylphosphine", E56,
          [("equivalents", qty(number=0.1, unit="equiv"))]),
     part("s26a_PhMe", "solvent", None, "toluene", E56, smiles="Cc1ccccc1"),
     part("s26a_70", "product", "70", "allenyl bromide", E56)]
R.append(rec("scheme26_aryl_bromoallene", "literature_example", E56, p,
             [step("bromination", [x["entity_id"] for x in p], E56, [("temperature", "reflux")])],
             [fld("reported_yield", qty(minimum=31, maximum=82, unit="%", raw_text="31-82%"), E56, ["s26a_70"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s26b_71", "reactant", "71", "CF3-substituted propargylic alcohol", E56),
     part("s26b_CBr4", "reagent", None, "carbon tetrabromide", E56,
          [("equivalents", qty(number=1.2, unit="equiv"))]),
     part("s26b_PPh3", "reagent", None, "triphenylphosphine", E56,
          [("equivalents", qty(number=2.4, unit="equiv"))]),
     part("s26b_DMF", "solvent", None, "DMF", E56),
     part("s26b_72", "product", "72", "CF3-substituted bromoallene", E56)]
R.append(rec("scheme26_cf3_bromoallene", "literature_example", E56, p,
             [step("bromination", [x["entity_id"] for x in p], E56, [("temperature", "r.t.")])],
             [fld("reported_yield", qty(minimum=39, maximum=93, unit="%", raw_text="39-93%"), E56, ["s26b_72"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s27_73", "reactant", "73", "propargyl diethanolamine boronate", E56),
     part("s27_74", "reagent", "74", "N-halosuccinimide", E56),
     part("s27_CH2Cl2", "solvent", None, "dichloromethane", E56),
     part("s27_75", "product", "75", "allenyl halide", E56)]
R.append(rec("scheme27_boronate_haloallene", "literature_example", E56, p,
             [step("halogenation", [x["entity_id"] for x in p], E56,
                   [("temperature", qty(number=20, unit="°C"))])],
             [fld("reported_yield", qty(minimum=20, maximum=97, unit="%", raw_text="20-97%"), E56, ["s27_75"]),
              fld("regioselectivity", ">20/1", E56, ["s27_75"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s28_76", "reactant", "76", "secondary or tertiary propargylic alcohol", E56),
     part("s28_KH", "reagent", None, "potassium hydride", E56,
          [("equivalents", qty(number=1.2, unit="equiv"))]),
     part("s28_NbBr5", "reagent", None, "niobium pentabromide", E56,
          [("equivalents", qty(number=1.2, unit="equiv"))]),
     part("s28_dioxane", "solvent", None, "dioxane", E56),
     part("s28_78", "product", "78", "allenyl bromide", E56)]
R.append(rec("scheme28_nbbr5_bromination", "literature_example", E56, p,
             [step("bromination", [x["entity_id"] for x in p], E56, [("temperature", "r.t.")])],
             [fld("reported_yield", qty(minimum=53, maximum=78, unit="%", raw_text="53-78%"), E56, ["s28_78"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s29_79", "reactant", "79", "enantioenriched propargyl tosylate", E56),
     part("s29_CuBr", "reagent", None, "copper(I) bromide", E56),
     part("s29_LiBr", "reagent", None, "lithium bromide", E56),
     part("s29_CuOTf2", "reagent", None, "copper(II) triflate", E56,
          [("equivalents", qty(number=0.1, unit="equiv"))]),
     part("s29_Et2O", "solvent", None, "diethyl ether", E56),
     part("s29_80", "product", "80", "major axially chiral bromoallene", E56),
     part("s29_81", "product", "81", "propargylic bromide side product", E56)]
R.append(rec("scheme29_optically_active_bromoallene", "literature_example", E56, p,
             [step("bromide_substitution", [x["entity_id"] for x in p], E56, [("temperature", "r.t.")])],
             [fld("combined_reported_yield", qty(number=78, unit="%"), E56, ["s29_80", "s29_81"]),
              fld("regioselectivity", "3.8/1", E56, ["s29_80", "s29_81"]),
              fld("enantiomeric_excess", qty(number=96, unit="%"), E56, ["s29_80"]),
              fld("starting_material_enantiomeric_excess", qty(number=97.9, unit="%"), E56, ["s29_79"]),
              fld("yield_measurement_basis", None, E56)]))

p = [part("s30_82", "reactant", "82", "4-(benzylamino)-2-butynyl carbonate or benzoate", E56),
     part("s30_DBU", "reagent", None, "DBU", E56),
     part("s30_CO2", "reactant", None, "carbon dioxide", E56,
          [("pressure", "1 atm")], smiles="O=C=O"),
     part("s30_MeCN", "solvent", None, "acetonitrile", E56, smiles="CC#N"),
     part("s30_85", "product", "85", "5-vinylideneoxazolidin-2-one", E56)]
R.append(rec("scheme30_dbu_co2_cyclization", "literature_example", E56, p,
             [step("dbu_co2_cyclization", [x["entity_id"] for x in p], E56,
                   [("temperature", qty(number=80, unit="°C"))])],
             [fld("reported_yield", qty(minimum=81, maximum=99, unit="%", raw_text="81-99%"), E56, ["s30_85"]),
              fld("yield_measurement_basis", None, E56)],
             notes=["DBU-CO2 zwitterion 83 and anionic intermediate 84 are depicted as mechanistic intermediates; the reaction is described as palladium-free."]))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(R)}, ensure_ascii=False))
