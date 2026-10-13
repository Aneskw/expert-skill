import json
from pathlib import Path

DOC = "doc_74147be4817c1957"
OUT = Path(__file__).with_name("records_pages_0001_0006.json")


def evidence(page):
    return [f"{DOC}:page{page}:image", f"{DOC}:page{page}:text"]


def fact(value, page):
    return {
        "value": value,
        "evidence_ids": evidence(page) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, page, targets=None):
    item = {"name": name, "fact": fact(value, page)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, page, amounts=()):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, page),
        "name": fact(None, page),
        "smiles": fact(None, page),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [field(name, value, page) for name, value in amounts],
    }


def record(suffix, page, kind, parts=(), conditions=(), outcomes=(), notes=(), unresolved=()):
    ps = [participant(p[0], p[1], p[2], page, p[3] if len(p) == 4 else ()) for p in parts]
    ids = [p[0] for p in parts]
    steps = []
    if conditions or (kind not in ("mechanism", "unresolved")):
        steps = [{
            "step_id": "step1",
            "participant_ids": ids,
            "conditions": [field(name, value, page) for name, value in conditions],
        }]
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence(page),
        "participants": ps,
        "steps": steps,
        "outcomes": [field(name, value, page, targets) for name, value, targets in outcomes],
        "notes": [fact(note, page) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "This Account summarizes cited prior work; original experimental article/SI was not provided.",
                "Generic or partially legible structures retain source labels and no SMILES.",
            ],
        },
    }


R = []

# Page 2: Scheme 1 is conceptual; Schemes 2 and 3 give specific prior-work examples.
R.append(record(
    "scheme1_possible_electrophilic_addition_products", 2, "general_scheme",
    parts=(("allene", "reactant", "generic allene RCH=C=CH2"),
           ("electrophile", "reagent", "E+"), ("nucleophile", "reagent", "Nu-"),
           ("products", "product", "possible regio-/stereoisomeric addition products")),
    conditions=(("operation", "1. electrophilic attack; 2. nucleophilic capture"),),
    notes=("Scheme 1 enumerates possible regio- and stereochemical outcomes, not a batch experiment.",),
))
R.append(record(
    "scheme2_nai_hoac_sulfoxide_1a_to_2a", 2, "literature_example",
    parts=(("sulfoxide_1a", "reactant", "propadienyl phenyl sulfoxide 1a"),
           ("nai", "reagent", "NaI"), ("oxygen", "reagent", "O2"),
           ("hoac", "solvent", "HOAc"),
           ("product_2a", "product", "3-acetoxy-2-iodo-1(Z)-propenyl phenyl sulfide 2a")),
    conditions=(("temperature", {"number": 80, "unit": "°C"}), ("solvent", "HOAc")),
    outcomes=(("reported_yield", {"number": 30, "unit": "%"}, ["product_2a"]),),
    notes=("The text reports a complicated mixture; 2a was one identified product. Scheme arrows marked with question marks are mechanistic hypotheses and are not additional experiments.",),
))
R.append(record(
    "scheme3_i2_hoac_sulfoxide_1a_to_3a", 2, "literature_example",
    parts=(("sulfoxide_1a", "reactant", "1,2-propadienyl phenyl sulfoxide 1a"),
           ("iodine", "reagent", "I2"), ("hoac", "solvent", "HOAc"),
           ("water", "reagent", "H2O"), ("product_3a", "product", "E-iodohydroxylation product 3a")),
    conditions=(("temperature", {"number": 60, "unit": "°C"}), ("solvent", "HOAc")),
    outcomes=(("reported_yield", {"number": 45, "unit": "%"}, ["product_3a"]),),
))

# Page 3: Schemes 4-8. Alternative condition sets in Scheme 5 are separate records.
R.append(record(
    "scheme4_general_e_iodohydroxylation_allenyl_sulfoxides", 3, "general_scheme",
    parts=(("allenyl_sulfoxide_1", "reactant", "1,2-allenyl sulfoxides 1 (R-group scope shown)"),
           ("iodine", "reagent", "I2", (("equivalents", {"minimum": 1.2, "maximum": 2.4, "unit": "equiv", "raw_text": "1.2–2.4 equiv"}),)),
           ("lioac", "reagent", "LiOAc", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (7:1)"),
           ("product_3", "product", "E-iodohydroxylation products 3")),
    conditions=(("solvent", "MeCN:H2O (7:1)"), ("temperature", "r.t."),
                ("time", {"minimum": 0.3, "maximum": 3.2, "unit": "h", "raw_text": "0.3–3.2 h"})),
    outcomes=(("reported_yield_range", {"minimum": 74, "maximum": 92, "unit": "%", "raw_text": "74–92%"}, ["product_3"]),),
))
R.append(record(
    "scheme4_unsubstituted_special_condition", 3, "literature_example",
    parts=(("allenyl_sulfoxide_1", "reactant", "allenyl sulfoxide 1, R1=R2=R3=H"),
           ("iodine", "reagent", "I2", (("equivalents", {"minimum": 1.2, "maximum": 2.4, "unit": "equiv", "raw_text": "1.2–2.4 equiv"}),)),
           ("lioac", "reagent", "LiOAc", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("product_3", "product", "unsubstituted E-iodohydroxylation product 3")),
    conditions=(("solvent", "MeCN:H2O (7:1)"), ("temperature", {"number": 55, "unit": "°C"}),
                ("time", {"number": 1, "unit": "h"})),
    outcomes=(("reported_yield", {"number": 96, "unit": "%"}, ["product_3"]),),
))
R.append(record(
    "scheme5_condition_a_cubr2_bromohydroxylation", 3, "general_scheme",
    parts=(("allenyl_sulfoxide_1", "reactant", "1,2-allenyl sulfoxides 1 (R-group scope shown)"),
           ("cubr2", "reagent", "CuBr2", (("equivalents", {"number": 4, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "acetone:H2O (2:1)"),
           ("product", "product", "E-bromohydroxylation products")),
    conditions=(("solvent", "acetone:H2O (2:1)"),
                ("temperature", {"minimum": 40, "maximum": 45, "unit": "°C", "raw_text": "40–45 °C"}),),
    outcomes=(("reported_yield_range", {"minimum": 49, "maximum": 98, "unit": "%", "raw_text": "49–98%"}, ["product"]),
              ("reported_E_selectivity", {"number": 100, "unit": "%"}, ["product"])),
))
R.append(record(
    "scheme5_condition_b_nbs_or_br2_bromohydroxylation", 3, "general_scheme",
    parts=(("allenyl_sulfoxide_1", "reactant", "1,2-allenyl sulfoxides 1 (R-group scope shown)"),
           ("brominating_agent", "reagent", "NBS or Br2", (("equivalents", {"number": 1.2, "unit": "equiv"}),)),
           ("lioac_hydrate", "reagent", "LiOAc·2H2O"),
           ("solvent_mix", "solvent", "MeCN:H2O (7:1)"),
           ("product", "product", "E-bromohydroxylation products")),
    conditions=(("solvent", "MeCN:H2O (7:1)"), ("temperature", "r.t."), ("time", None)),
    outcomes=(("reported_yield_range", {"minimum": 49, "maximum": 98, "unit": "%", "raw_text": "49–98%"}, ["product"]),
              ("reported_E_selectivity", {"number": 100, "unit": "%"}, ["product"])),
    unresolved=("Scheme 5 does not state the LiOAc·2H2O amount or reaction time for condition B.",
                "NBS and Br2 are presented as alternatives, not separable row-level outcomes in this Account."),
))
R.append(record(
    "scheme5_condition_c_cucl2_chlorohydroxylation", 3, "general_scheme",
    parts=(("allenyl_sulfoxide_1", "reactant", "1,2-allenyl sulfoxides 1 (R-group scope shown)"),
           ("cucl2_hydrate", "reagent", "CuCl2·2H2O", (("equivalents", {"number": 4, "unit": "equiv"}),)),
           ("silica", "reagent", "silica gel"),
           ("product", "product", "E-chlorohydroxylation products")),
    conditions=(("operation", "solvent free; mixed with silica gel; temperature rt–65 °C"),
                ("time", None)),
    outcomes=(("reported_yield_range", {"minimum": 49, "maximum": 98, "unit": "%", "raw_text": "49–98% (combined Scheme 5 range)"}, ["product"]),
              ("reported_E_selectivity", {"number": 100, "unit": "%"}, ["product"])),
    unresolved=("The qualitative temperature program 'rt–65 °C' cannot be represented as a numeric range without assuming a room-temperature value.",
                "The 49–98% range is printed for the combined Scheme 5 scope and is not assigned to a particular condition-C substrate."),
))
R.append(record(
    "scheme6_optically_active_sulfoxide_sequence", 3, "general_scheme",
    parts=(("propargylic_alcohol", "reactant", "optically active propargylic alcohol (96 to >99% ee)"),
           ("phscl", "reagent", "PhSCl"), ("et3n", "reagent", "Et3N"),
           ("ch2cl2", "solvent", "CH2Cl2"), ("chiral_allene", "product", "optically active 1,2-allenyl sulfoxide"),
           ("halogenating_agent", "reagent", "X2 or CuX2"),
           ("halohydroxylation_product", "product", "E-halohydroxylation product, X=Cl, Br, I")),
    conditions=(("stage_1_temperature", {"minimum": -85, "maximum": -80, "unit": "°C", "raw_text": "−80 to −85 °C"}),
                ("stage_1_solvent", "CH2Cl2"), ("stage_2_temperature", "r.t."),
                ("stage_1_time", None), ("stage_2_time", None)),
    outcomes=(("allene_de_expression", "96–99% de", ["chiral_allene"]),
              ("product_yield_range", {"minimum": 69, "maximum": 99, "unit": "%", "raw_text": "69–99%"}, ["halohydroxylation_product"]),
              ("product_de_expression", "95 to >99% de", ["halohydroxylation_product"])),
))
R.append(record(
    "scheme7_chiral_1b_to_crystalline_3b", 3, "literature_example",
    parts=(("substrate_1b", "reactant", "optically active allenyl sulfoxide 1b"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 1.2, "unit": "equiv"}),)),
           ("lioac_hydrate", "reagent", "LiOAc·2H2O"),
           ("solvent_mix", "solvent", "MeCN:H2O (7:1)"),
           ("product_3b", "product", "crystalline iodohydroxylation product 3b")),
    conditions=(("solvent", "MeCN:H2O (7:1)"), ("temperature", "r.t."), ("time", None)),
    outcomes=(("reported_yield", {"number": 97, "unit": "%"}, ["product_3b"]),),
    notes=("X-ray studies support axial-to-central chirality transfer and inversion at sulfur.",),
))
R.append(record(
    "scheme7_proposed_iodohydroxylation_mechanism", 3, "mechanism",
    notes=("Proposed path: iodinonium intermediate 4, intramolecular sulfoxide-oxygen attack to five-membered intermediate 5, then water attack at sulfur with inversion to product 3.",),
))
R.append(record(
    "scheme8_bnsh_reductive_iodohydroxylation", 3, "general_scheme",
    parts=(("allenyl_sulfoxide_1", "reactant", "1,2-allenyl sulfoxides 1 (R-group scope shown)"),
           ("iodine", "reagent", "I2", (("equivalents", {"minimum": 1.2, "maximum": 1.5, "unit": "equiv", "raw_text": "1.2–1.5 equiv"}),)),
           ("bnsh", "reagent", "BnSH", (("equivalents", {"number": 1, "unit": "equiv"}),)),
           ("mecn", "solvent", "MeCN"), ("product_6", "product", "E-2-iodo-3-hydroxy-1-alkenyl sulfides 6"),
           ("bnbns", "product", "BnSSBn")),
    conditions=(("solvent", "MeCN"), ("temperature", {"number": -40, "unit": "°C"}),
                ("operation", "subsequent temperature −20 °C or 5 °C"), ("time", None)),
    outcomes=(("reported_yield_range", {"minimum": 50, "maximum": 80, "unit": "%", "raw_text": "50–80%"}, ["product_6"]),
              ("reported_E_Z_ratio_range", "E/Z 94:6 to >99:1", ["product_6"])),
))

# Page 4: Schemes 9-13 and the explicit failed sulfone experiment.
R.append(record(
    "scheme9_proposed_bnsh_reduction_mechanism", 4, "mechanism",
    notes=("Scheme 9 proposes BnSH attack on cyclic intermediate 5, sulfur reduction through intermediates 7, and formation of BnSSBn and product 6.",),
))
R.append(record(
    "scheme10_selenohydroxylation_allenyl_sulfoxides", 4, "general_scheme",
    parts=(("allenyl_sulfoxide_1", "reactant", "1,2-allenyl sulfoxides 1 (R-group scope shown)"),
           ("phsecl", "reagent", "PhSeCl", (("equivalents", {"number": 1.5, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (10:1)"),
           ("product_8", "product", "E-selenohydroxylation products 8")),
    conditions=(("solvent", "MeCN:H2O (10:1)"), ("temperature", "r.t."),
                ("time", {"minimum": 10, "maximum": 60, "unit": "min", "raw_text": "10–60 min"})),
    outcomes=(("reported_yield_range", {"minimum": 48, "maximum": 93, "unit": "%", "raw_text": "48–93%"}, ["product_8"]),),
))
R.append(record(
    "prose_failed_propadienyl_phenyl_sulfone_halohydroxylation", 4, "literature_example",
    parts=(("starting_allene", "reactant", "1,2-propadienyl phenyl sulfone"),
           ("expected_product", "product", "expected halohydroxylation product")),
    conditions=(("operation", "conditions used for sulfoxide halohydroxylation (not restated)"),
                ("temperature", None), ("time", None)),
    outcomes=(("expected_product_outcome", "not obtained", ["expected_product"]),
              ("recovered_starting_material_yield", {"number": 80, "unit": "%"}, ["starting_allene"])),
    unresolved=("The Account does not restate the exact halogenating reagent, solvent, time, or temperature for this failed trial.",),
))
R.append(record(
    "scheme11_monosubstituted_sulfone_bromohydroxylation", 4, "general_scheme",
    parts=(("allenyl_sulfone_9", "reactant", "3-monosubstituted 1,2-allenyl phenyl sulfones 9"),
           ("bromine", "reagent", "Br2", (("equivalents", {"minimum": 1.2, "maximum": 2.0, "unit": "equiv", "raw_text": "1.2–2.0 equiv"}),)),
           ("mecn", "solvent", "MeCN"),
           ("water", "reagent", "H2O (1 equiv in the R1=n-C6H13 special case)", (("equivalents", {"number": 1, "unit": "equiv"}),)),
           ("product_10", "product", "E-bromohydroxylation products 10")),
    conditions=(("stage_1_solvent", "MeCN"), ("stage_1_time", {"number": 30, "unit": "min"}),
                ("operation", "stage 1 at r.t.; 0 °C when R1=Me"),
                ("stage_2_time", {"number": 30, "unit": "min"}),
                ("stage_2_temperature", "r.t.")),
    outcomes=(("reported_yield_range", {"minimum": 53, "maximum": 85, "unit": "%", "raw_text": "53–85%"}, ["product_10"]),
              ("reported_E_selectivity", {"number": 100, "unit": "%"}, ["product_10"])),
    notes=("For R1=n-C6H13 the scheme specifies MeCN:EtOH (40:1) plus the separately structured conditional water addition.",),
))
R.append(record(
    "scheme11_disubstituted_sulfone_diene_formation", 4, "general_scheme",
    parts=(("disubstituted_allenyl_sulfone", "reactant", "3,3-disubstituted 1,2-allenyl phenyl sulfones"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("mecn_etoh", "solvent", "MeCN:EtOH (40:1)"),
           ("water", "reagent", "H2O", (("equivalents", {"number": 1, "unit": "equiv"}),)),
           ("diene_product", "product", "2-bromo-1(E),3(E)-alkadienyl sulfones")),
    conditions=(("solvent", "MeCN:EtOH (40:1)"), ("operation", "reaction at r.t.; −40 °C when R2,R3=(CH2)4"),
                ("time", None)),
    outcomes=(("reported_yield_range", {"minimum": 63, "maximum": 80, "unit": "%", "raw_text": "63–80%"}, ["diene_product"]),),
))
R.append(record(
    "scheme12_isolation_of_cyclic_intermediate_11a", 4, "literature_example",
    parts=(("sulfone_9a", "reactant", "p-bromophenyl-substituted allenyl sulfone 9a"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("mecn", "solvent", "MeCN"), ("intermediate_11a", "product", "five-membered cyclic intermediate 11a")),
    conditions=(("solvent", "MeCN"), ("temperature", "r.t."), ("time", None)),
    outcomes=(("reported_cis_trans_ratio", "cis/trans = 1:1", ["intermediate_11a"]),),
    notes=("The cis/trans mixture was isolated; pure cis-11a was obtained by recrystallization and characterized by X-ray diffraction.",),
))
R.append(record(
    "scheme12_hydrolysis_11a_to_10a", 4, "literature_example",
    parts=(("intermediate_11a", "reactant", "cyclic intermediate 11a, cis/trans=1:1"),
           ("water", "reagent", "H2O"), ("mecn", "solvent", "MeCN"),
           ("product_10a", "product", "E-bromohydroxylation product 10a")),
    conditions=(("solvent", "MeCN"), ("temperature", {"number": 0, "unit": "°C"}),
                ("time", {"number": 30, "unit": "min"})),
    outcomes=(("reported_yield", {"number": 63, "unit": "%"}, ["product_10a"]),),
))
R.append(record(
    "scheme13_optically_active_thiirane_sequence", 4, "general_scheme",
    parts=(("chiral_allenyl_sulfoxide", "reactant", "optically active 1,2-allenyl sulfoxide"),
           ("mcpba", "reagent", "m-CPBA"), ("thf", "solvent", "THF"),
           ("chiral_allenyl_sulfone_9", "product", "optically active 1,2-allenyl sulfone 9"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("water", "reagent", "H2O"), ("na2s2o3", "reagent", "saturated aqueous Na2S2O3"),
           ("thiirane_12", "product", "optically active alkylidenethiirane 12")),
    conditions=(("oxidation_solvent", "THF"), ("oxidation_temperature", {"number": 0, "unit": "°C"}),
                ("thiiranation_solvent", "MeCN"), ("bromination_temperature", "r.t."),
                ("bromination_time", {"minimum": 10, "maximum": 25, "unit": "min", "raw_text": "10–25 min"}),
                ("water_temperature", "r.t."), ("quench_temperature", "r.t.")),
    outcomes=(("sulfone_ee_expression", "96 to >99% ee", ["chiral_allenyl_sulfone_9"]),
              ("thiirane_yield_range", {"minimum": 57, "maximum": 74, "unit": "%", "raw_text": "57–74%"}, ["thiirane_12"]),
              ("thiirane_ee_expression", "96–99% ee", ["thiirane_12"])),
))

# Page 5: Schemes 14-17 and the failed iodohydroxylation trial.
R.append(record(
    "scheme14_proposed_thiirane_mechanism", 5, "mechanism",
    notes=("Proposed sequence: cyclic intermediate 11, thiosulfate ring opening to 13, SO3 elimination to sulfide anion 14, conjugate addition and beta-bromide elimination through 15 to thiirane 12.",),
))
R.append(record(
    "scheme15_phosphine_oxide_16a_iodohydroxylation", 5, "general_scheme",
    parts=(("phosphine_oxide_16a", "reactant", "1,2-allenyl diphenylphosphine oxides 16A"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 4, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (1:5)"),
           ("product_17a", "product", "E-iodohydroxylation products 17A")),
    conditions=(("solvent", "MeCN:H2O (1:5)"), ("temperature", "r.t."),
                ("time", {"minimum": 5, "maximum": 24, "unit": "h", "raw_text": "5–24 h"})),
    outcomes=(("reported_yield_range", {"minimum": 56, "maximum": 93, "unit": "%", "raw_text": "56–93%"}, ["product_17a"]),
              ("reported_E_selectivity", {"number": 100, "unit": "%"}, ["product_17a"])),
))
R.append(record(
    "scheme15_phosphine_oxide_16b_iodohydroxylation", 5, "general_scheme",
    parts=(("phosphine_oxide_16b", "reactant", "aryl-substituted allenyl diphenylphosphine oxide 16B"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 4, "unit": "equiv"}),)),
           ("agno3", "reagent", "AgNO3", (("equivalents", {"number": 6, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (1:5)"),
           ("product_17b", "product", "iodohydroxylation products 17B")),
    conditions=(("solvent", "MeCN:H2O (1:5)"), ("temperature", "r.t."),
                ("time", {"minimum": 24, "maximum": 61, "unit": "h", "raw_text": "24–61 h"})),
    outcomes=(("reported_yield_range", {"minimum": 57, "maximum": 84, "unit": "%", "raw_text": "57–84%"}, ["product_17b"]),),
    notes=("The text states AgNO3 was used to avoid diiodide formation.",),
))
R.append(record(
    "scheme16_o18_iodohydroxylation_mechanism", 5, "mechanism",
    notes=("18O-labeling and chiral-substrate experiments support neighboring phosphine-oxide participation through five-membered intermediate 18 and incorporation of labeled water oxygen into product 17-18O.",),
))
R.append(record(
    "scheme16_optically_active_phosphine_oxide_sequence", 5, "general_scheme",
    parts=(("propargylic_alcohol", "reactant", "optically active propargylic alcohol"),
           ("ph2pcl", "reagent", "Ph2PCl"), ("et3n", "reagent", "Et3N"),
           ("thf", "solvent", "THF"), ("chiral_16", "product", "optically active allenyl phosphine oxide 16"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 4, "unit": "equiv"}),)),
           ("aqueous_mecn", "solvent", "MeCN:H2O (1:5)"),
           ("chiral_product", "product", "chiral E-iodohydroxylation product")),
    conditions=(("stage_1_solvent", "THF"), ("operation", "stage 1 temperature program −78 °C to r.t."),
                ("stage_2_solvent", "MeCN:H2O (1:5)"), ("stage_1_time", None), ("stage_2_time", None)),
    outcomes=(("allene_ee_expression", "94–98% ee", ["chiral_16"]),
              ("product_yield_range", {"minimum": 72, "maximum": 84, "unit": "%", "raw_text": "72–84%"}, ["chiral_product"]),
              ("product_ee_expression", "94–97% ee", ["chiral_product"])),
))
R.append(record(
    "prose_failed_23_allenoate_iodohydroxylation", 5, "literature_example",
    parts=(("allenoate", "reactant", "2,3-allenoate"),
           ("expected_product", "product", "expected iodohydroxylation product")),
    conditions=(("operation", "attempted extension of the iodohydroxylation"),
                ("temperature", None), ("time", None)),
    outcomes=(("reported_outcome", "complicated mixture", ["expected_product"]),),
    unresolved=("The substrate identity, iodine loading, solvent, time, temperature, and product distribution are not specified in the Account.",),
))
R.append(record(
    "scheme17_allenoate_phsecl_to_ketone_and_lactone", 5, "general_scheme",
    parts=(("allenoate_19", "reactant", "2,3-allenoates 19 (R-group scope shown)"),
           ("phsecl", "reagent", "PhSeCl", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("li2co3", "reagent", "Li2CO3", (("equivalents", {"number": 3, "unit": "equiv"}),)),
           ("mecn", "solvent", "MeCN"), ("ketone_20", "product", "E-3-phenylseleno-4-oxo-2-alkenoates 20"),
           ("lactone_21", "product", "phenylselenobutenolides 21")),
    conditions=(("solvent", "MeCN"), ("temperature", "r.t."), ("time", {"number": 1, "unit": "h"})),
    outcomes=(("ketone_reported_yield_range", {"minimum": 63, "maximum": 93, "unit": "%", "raw_text": "63–93%"}, ["ketone_20"]),
              ("lactone_reported_yield_range", {"minimum": 1, "maximum": 3, "unit": "%", "raw_text": "1–3%"}, ["lactone_21"])),
))
R.append(record(
    "scheme17_proposed_allenoate_phsecl_mechanism", 5, "mechanism",
    notes=("Scheme 17 proposes intermediates 22 and 23, water capture to alcohol 24, and PhSeCl/Li2CO3 oxidation through 25 to ketone 20; electrophilic trapping can instead give lactone 21.",),
))

# Page 6: Schemes 18-23. Shared-condition rows in Scheme 21 are kept separate.
R.append(record(
    "scheme18_26a_iodohydroxylation_aqueous_acetone", 6, "literature_example",
    parts=(("sulfide_26a", "reactant", "1,2-allenyl sulfide 26a"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "acetone:H2O (4:1)"),
           ("alcohol_27a", "product", "Z-iodohydroxylation product 27a"),
           ("aldehyde", "product", "2-iodo-3-methyl-4-phenyl-2-butenal")),
    conditions=(("solvent", "acetone:H2O (4:1)"), ("temperature", "r.t."),
                ("time", {"number": 13, "unit": "h"})),
    outcomes=(("alcohol_reported_yield", {"number": 68, "unit": "%"}, ["alcohol_27a"]),
              ("alcohol_Z_E_ratio", "Z/E >99:1", ["alcohol_27a"]),
              ("aldehyde_reported_yield", {"number": 16, "unit": "%"}, ["aldehyde"]),
              ("aldehyde_E_Z_ratio", "E/Z = 52:48", ["aldehyde"])),
))
R.append(record(
    "prose_26a_iodination_aqueous_mecn_aldehyde", 6, "literature_example",
    parts=(("sulfide_26a", "reactant", "1,2-allenyl sulfide 26a"),
           ("iodine", "reagent", "I2"), ("aqueous_mecn", "solvent", "aqueous MeCN"),
           ("aldehyde", "product", "2-iodo-3-methyl-4-phenyl-2-butenal")),
    conditions=(("solvent", "aqueous MeCN"), ("temperature", None), ("time", None)),
    outcomes=(("aldehyde_reported_yield", {"number": 16, "unit": "%"}, ["aldehyde"]),
              ("aldehyde_E_Z_ratio", "E/Z = 0.32:1", ["aldehyde"])),
    unresolved=("The Account does not state iodine loading, MeCN:H2O ratio, time, or temperature for this comparison.",),
))
R.append(record(
    "scheme19_general_sulfide_iodohydroxylation", 6, "general_scheme",
    parts=(("sulfide_26", "reactant", "1,2-allenyl sulfides 26 (R-group scope shown)"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "acetone:H2O (4:1)"),
           ("alcohol_27", "product", "Z-iodohydroxylation products 27")),
    conditions=(("solvent", "acetone:H2O (4:1)"), ("temperature", "r.t."),
                ("time", {"minimum": 8, "maximum": 13.5, "unit": "h", "raw_text": "8–13.5 h"})),
    outcomes=(("reported_yield_range", {"minimum": 41, "maximum": 94, "unit": "%", "raw_text": "41–94%"}, ["alcohol_27"]),
              ("reported_Z_E_ratio_range", "Z/E 94:6 to >99:1", ["alcohol_27"])),
))
R.append(record(
    "scheme19_general_sulfide_bromohydroxylation", 6, "general_scheme",
    parts=(("sulfide_26", "reactant", "substituted 1,2-allenyl sulfides 26"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("na2co3", "reagent", "Na2CO3", (("equivalents", {"number": 1, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (4:1)"),
           ("alcohol_28", "product", "Z-bromohydroxylation products 28")),
    conditions=(("solvent", "MeCN:H2O (4:1)"), ("temperature", {"number": 0, "unit": "°C"}),
                ("time", {"minimum": 2, "maximum": 9, "unit": "h", "raw_text": "2–9 h"})),
    outcomes=(("reported_yield_range", {"minimum": 47, "maximum": 86, "unit": "%", "raw_text": "47–86%"}, ["alcohol_28"]),
              ("reported_Z_E_ratio_range", "Z/E 31:1 to >99:1", ["alcohol_28"])),
))
R.append(record(
    "scheme19_26b_bromohydroxylation_without_base", 6, "literature_example",
    parts=(("sulfide_26b", "reactant", "propadienyl phenyl sulfide 26b"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (4:1)"),
           ("product_28b", "product", "bromohydroxylation product 28b")),
    conditions=(("solvent", "MeCN:H2O (4:1)"), ("temperature", {"number": 25, "unit": "°C"}),
                ("time", {"number": 9, "unit": "h"})),
    outcomes=(("reported_yield", {"number": 47, "unit": "%"}, ["product_28b"]),
              ("reported_Z_E_ratio", "Z/E = 99:1", ["product_28b"])),
    notes=("The prose specifies that propadienyl sulfide is reacted without Na2CO3.",),
))
R.append(record(
    "scheme20_propadenyl_selenide_iodohydroxylation", 6, "general_scheme",
    parts=(("selenide_29", "reactant", "propadienyl selenides 29, R=aryl/alkyl/benzyl"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 4, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (4:1)"),
           ("product_30", "product", "Z-iodohydroxylation products 30")),
    conditions=(("solvent", "MeCN:H2O (4:1)"), ("temperature", {"number": 0, "unit": "°C"}),
                ("atmosphere", "N2"), ("time", None)),
    outcomes=(("reported_yield_range", {"minimum": 33, "maximum": 74, "unit": "%", "raw_text": "33–74%"}, ["product_30"]),
              ("reported_Z_E_ratio_range", "Z/E 25:1 to >99:1", ["product_30"])),
))
R.append(record(
    "prose_1968_allene_methoxy_bromination", 6, "literature_example",
    parts=(("allene", "reactant", "allene substrate from cited 1968 study"),
           ("bromine", "reagent", "Br2"), ("meoh", "reagent", "MeOH"),
           ("product", "product", "methoxy-bromination product")),
    conditions=(("operation", "bromination in the presence of MeOH"), ("temperature", None), ("time", None)),
    outcomes=(("reported_Z_E_ratio", "Z/E = 87:13", ["product"]),),
    unresolved=("This is an external literature precedent; the Account does not reproduce substrate identity, amounts, temperature, time, or yield.",),
))
R.append(record(
    "scheme21_26c_bromohydroxylation", 6, "literature_example",
    parts=(("sulfide_26c", "reactant", "1-alkyl propadienyl sulfide 26c, R1=n-C4H9"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("na2co3", "reagent", "Na2CO3", (("equivalents", {"number": 1, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (4:1)"),
           ("product_28c", "product", "Z-bromohydroxylation product 28c")),
    conditions=(("solvent", "MeCN:H2O (4:1)"), ("temperature", None), ("time", None)),
    outcomes=(("reported_yield", {"number": 35, "unit": "%"}, ["product_28c"]),
              ("reported_Z_E_ratio", "Z/E = 43:1", ["product_28c"])),
))
R.append(record(
    "scheme21_26d_bromohydroxylation", 6, "literature_example",
    parts=(("sulfide_26d", "reactant", "1-alkyl propadienyl sulfide 26d, R1=CH3"),
           ("bromine", "reagent", "Br2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("na2co3", "reagent", "Na2CO3", (("equivalents", {"number": 1, "unit": "equiv"}),)),
           ("solvent_mix", "solvent", "MeCN:H2O (4:1)"),
           ("product_28d", "product", "Z-bromohydroxylation product 28d")),
    conditions=(("solvent", "MeCN:H2O (4:1)"), ("temperature", None), ("time", None)),
    outcomes=(("reported_yield", {"number": 44, "unit": "%"}, ["product_28d"]),
              ("reported_Z_E_ratio", "Z/E = 36:1", ["product_28d"])),
))
R.append(record(
    "scheme21_soft_lewis_acid_base_intermediate_31", 6, "mechanism",
    notes=("Intermediate 31 is a stereochemical rationale based on soft Lewis acid-base interaction between sulfur/selenium and X+; it is not a separately reported experiment.",),
))
R.append(record(
    "scheme22_iodoalkoxylation_allenyl_sulfides_selenides", 6, "general_scheme",
    parts=(("allene", "reactant", "propadienyl sulfides or selenides, X=S or Se"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("alcohol", "reagent", "R2OH"), ("mecn_alcohol", "solvent", "MeCN:R2OH (20:1)"),
           ("ether_32", "product", "Z-iodoalkoxylation products 32")),
    conditions=(("solvent", "MeCN:R2OH (20:1)"), ("temperature", "r.t."), ("time", None)),
    outcomes=(("reported_yield_range", {"minimum": 40, "maximum": 80, "unit": "%", "raw_text": "40–80%"}, ["ether_32"]),),
))
R.append(record(
    "scheme23_ritter_iodoamidation", 6, "general_scheme",
    parts=(("selenide_allene", "reactant", "propadienyl aryl selenides"),
           ("iodine", "reagent", "I2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
           ("water", "reagent", "H2O"), ("nitrile", "reagent", "RCN"),
           ("hexane", "solvent", "n-hexane"), ("amide_34", "product", "Z-iodoamidation products 34")),
    conditions=(("solvent", "RCN:n-hexane (1:1)"), ("temperature", {"number": 25, "unit": "°C"}),
                ("atmosphere", "N2"),
                ("time", {"minimum": 9.5, "maximum": 21, "unit": "h", "raw_text": "9.5–21 h"})),
    outcomes=(("reported_yield_range", {"minimum": 46, "maximum": 62, "unit": "%", "raw_text": "46–62%"}, ["amide_34"]),
              ("reported_Z_E_ratio_range", "Z/E 18:1 to 65:1", ["amide_34"])),
))
R.append(record(
    "scheme23_ritter_iodoamidation_mechanism", 6, "mechanism",
    notes=("Scheme 23 proposes iodine addition to intermediate 31a, nitrile capture to nitrilium intermediate 33, and hydrolysis to amide 34.",),
))

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(R), "output": str(OUT)}, ensure_ascii=False))
