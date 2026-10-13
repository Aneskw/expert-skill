import json
from pathlib import Path


DOC = "doc_74147be4817c1957"
OUT = Path(__file__).with_name("records_pages_0007_0010.json")


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


def step(step_id, page, participant_ids, conditions=()):
    return {
        "step_id": step_id,
        "participant_ids": list(participant_ids),
        "conditions": [field(name, value, page) for name, value in conditions],
    }


def record(suffix, page, kind, parts=(), steps=(), outcomes=(), notes=(), unresolved=()):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence(page),
        "participants": [
            participant(p[0], p[1], p[2], page, p[3] if len(p) == 4 else ())
            for p in parts
        ],
        "steps": [step(s[0], page, s[1], s[2] if len(s) == 3 else ()) for s in steps],
        "outcomes": [field(name, value, page, targets) for name, value, targets in outcomes],
        "notes": [fact(note, page) for note in notes],
        "review": {
            "method": "none",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": list(unresolved) or [
                "This Account summarizes cited prior work; the original experimental article and SI were not supplied.",
                "Generic R-group and stereochemical structures retain source labels; no SMILES was assigned.",
            ],
        },
    }


R = []

# Page 7, Scheme 24: generic cited scope.
R.append(record(
    "scheme24_z_iodohydroxylation_allenyl_butenolides", 7, "general_scheme",
    parts=(
        ("butenolide_35", "reactant", "beta-(1,2-allenyl)butenolides 35 (R-group scope shown)"),
        ("iodine", "reagent", "I2", (("equivalents", {"number": 1.5, "unit": "equiv"}),)),
        ("men02_water", "solvent", "MeNO2:H2O (5:1)"),
        ("product_36", "product", "Z-iodohydroxylation products 36"),
    ),
    steps=(("step1", ("butenolide_35", "iodine", "men02_water", "product_36"), (
        ("solvent", "MeNO2:H2O (5:1)"),
        ("atmosphere", "Ar"),
        ("temperature", "r.t."),
        ("time", {"minimum": 1, "maximum": 51, "unit": "h", "raw_text": "1–51 h"}),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 49, "maximum": 80, "unit": "%", "raw_text": "49–80%"}, ("product_36",)),
        ("yield_measurement_basis", None, None),
    ),
))
R.append(record(
    "scheme25_steric_rationale_iodohydroxylation", 7, "mechanism",
    notes=(
        "Proposed reversible iodine addition gives iodonium intermediates 37A and 37B; less-hindered water attack through 37A is used to rationalize formation of the Z product, while the E product is not formed.",
    ),
))

# Page 7, Scheme 26: generic cited scope.
R.append(record(
    "scheme26_fluorohydroxylation_3_aryl_allenes", 7, "general_scheme",
    parts=(
        ("allene_38", "reactant", "3-aryl-1,2-allenes 38, R=H/alkyl/aryl"),
        ("selectfluor", "reagent", "Selectfluor", (("equivalents", {"number": 1.2, "unit": "equiv"}),)),
        ("mecn_water", "solvent", "MeCN:H2O (10:1)"),
        ("product_39", "product", "regioselective fluorohydroxylation products 39"),
    ),
    steps=(("step1", ("allene_38", "selectfluor", "mecn_water", "product_39"), (
        ("solvent", "MeCN:H2O (10:1)"),
        ("temperature", "r.t."),
        ("time", {"minimum": 2, "maximum": 24, "unit": "h", "raw_text": "2–24 h"}),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 37, "maximum": 78, "unit": "%", "raw_text": "37–78%"}, ("product_39",)),
        ("yield_measurement_basis", None, None),
    ),
))

# Page 7, Scheme 27: alternative arrows are distinct condition records.
R.append(record(
    "scheme27_i2_lactonization_23_allenoic_acids", 7, "general_scheme",
    parts=(
        ("allenoic_acid_40", "reactant", "2,3-allenoic acids 40, R=alkyl"),
        ("iodine", "reagent", "I2"),
        ("thf", "solvent", "THF"),
        ("k2co3", "reagent", "K2CO3"),
        ("iodobutenolide_41", "product", "beta-iodobutenolides 41, X=I"),
    ),
    steps=(
        ("step1_iodination", ("allenoic_acid_40", "iodine", "thf"), (
            ("solvent", "THF"),
            ("temperature", {"number": 0, "unit": "°C"}),
            ("time", {"number": 1, "unit": "h"}),
        )),
        ("step2_base_treatment", ("k2co3", "iodobutenolide_41"), (
            ("time", {"number": 10, "unit": "h"}),
            ("temperature", None),
        )),
    ),
    outcomes=(
        ("reported_yield_range", {"minimum": 81, "maximum": 91, "unit": "%", "raw_text": "81–91% (combined Scheme 27 range)"}, ("iodobutenolide_41",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "The K2CO3 amount and second-stage temperature are not stated.",
        "The 81–91% range is printed for the I2/NBS alternatives and is not assigned to a single substrate row or route.",
        "The original experimental article and SI were not supplied.",
    ),
))
R.append(record(
    "scheme27_nbs_lactonization_23_allenoic_acids", 7, "general_scheme",
    parts=(
        ("allenoic_acid_40", "reactant", "2,3-allenoic acids 40, R=alkyl"),
        ("nbs", "reagent", "NBS"),
        ("k2co3", "reagent", "K2CO3"),
        ("water", "solvent", "H2O"),
        ("bromobutenolide_41", "product", "beta-bromobutenolides 41, X=Br"),
    ),
    steps=(("step1", ("allenoic_acid_40", "nbs", "k2co3", "water", "bromobutenolide_41"), (
        ("solvent", "H2O"),
        ("temperature", "r.t."),
        ("time", {"number": 6, "unit": "h"}),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 81, "maximum": 91, "unit": "%", "raw_text": "81–91% (combined Scheme 27 range)"}, ("bromobutenolide_41",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "NBS and K2CO3 amounts are not stated.",
        "The 81–91% range is printed for the I2/NBS alternatives and is not assigned to a single substrate row or route.",
        "The original experimental article and SI were not supplied.",
    ),
))
R.append(record(
    "scheme27_phxcl_lactonization_23_allenoic_acids", 7, "general_scheme",
    parts=(
        ("allenoic_acid_42", "reactant", "2,3-allenoic acids 42 (R-group scope shown)"),
        ("phxcl", "reagent", "PhXCl, X=Se or S"),
        ("mecn", "solvent", "MeCN"),
        ("butenolide_43", "product", "beta-phenylseleno/phenylthio butenolides 43"),
    ),
    steps=(("step1", ("allenoic_acid_42", "phxcl", "mecn", "butenolide_43"), (
        ("solvent", "MeCN"),
        ("atmosphere", "N2"),
        ("temperature", {"number": 0, "unit": "°C"}),
        ("time", {"minimum": 7, "maximum": 19.5, "unit": "h", "raw_text": "7–19.5 h"}),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 49, "maximum": 98, "unit": "%", "raw_text": "49–98%"}, ("butenolide_43",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "PhSeCl and PhSCl are presented as alternatives with a combined scope range; route-specific loadings and yields are not shown.",
        "Generic R-group structures retain source labels and no SMILES.",
        "The original experimental article and SI were not supplied.",
    ),
))
R.append(record(
    "scheme27_selectfluor_lactonization_23_allenoic_acids", 7, "general_scheme",
    parts=(
        ("allenoic_acid_42", "reactant", "2,3-allenoic acids 42 (R-group scope shown)"),
        ("selectfluor", "reagent", "Selectfluor", (("equivalents", {"minimum": 1.1, "maximum": 1.5, "unit": "equiv", "raw_text": "1.1–1.5 equiv"}),)),
        ("water", "reagent", "H2O (10 equiv with MeCN; alternatively H2O is the medium)", (("equivalents", {"number": 10, "unit": "equiv"}),)),
        ("mecn_or_water", "solvent", "MeCN with H2O (10 equiv), or H2O"),
        ("fluorobutenolide_44", "product", "beta-fluorobutenolides 44"),
    ),
    steps=(("step1", ("allenoic_acid_42", "selectfluor", "water", "mecn_or_water", "fluorobutenolide_44"), (
        ("solvent", "MeCN with H2O (10 equiv), or H2O"),
        ("temperature", {"minimum": 80, "maximum": 100, "unit": "°C", "raw_text": "80–100 °C"}),
        ("time", None),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 39, "maximum": 96, "unit": "%", "raw_text": "39–96%"}, ("fluorobutenolide_44",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "Reaction time is not stated; the 10-equivalent H2O amount applies to the MeCN option, not to neat/aqueous H2O as medium.",
        "The original experimental article and SI were not supplied.",
        "Generic R-group structures retain source labels and no SMILES.",
    ),
))

# Page 7, Scheme 28.
R.append(record(
    "scheme28_iodolactonization_45_allenoic_acids", 7, "general_scheme",
    parts=(
        ("allenoic_acid_45", "reactant", "4,5-allenoic acids 45 (R-group scope shown)"),
        ("iodine", "reagent", "I2", (("equivalents", {"number": 1.5, "unit": "equiv"}),)),
        ("k2co3", "reagent", "K2CO3", (("equivalents", {"minimum": 0, "maximum": 1.0, "unit": "equiv", "raw_text": "0 or 1.0 equiv"}),)),
        ("cyclohexane", "solvent", "cyclohexane"),
        ("lactone_46", "product", "five-membered iodolactones 46"),
    ),
    steps=(("step1", ("allenoic_acid_45", "iodine", "k2co3", "cyclohexane", "lactone_46"), (
        ("solvent", "cyclohexane"),
        ("temperature", "r.t."),
        ("time", {"number": 1, "unit": "h"}),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 75, "maximum": 88, "unit": "%", "raw_text": "75–88%"}, ("lactone_46",)),
        ("reported_Z_E_ratio_range", "Z/E 97:3 to 99:1", ("lactone_46",)),
        ("yield_measurement_basis", None, None),
    ),
))

# Page 8, Scheme 29: two substrate-specific iodocyclizations and two kinetic-resolution stages.
for suffix, r_label, yield_value, ee_value, ze_ratio in (
    ("n_c6h13", "n-C6H13", 86, 99, "Z/E = 85:15"),
    ("n_c5h11", "n-C5H11", 91, 98, "Z/E = 79:21"),
):
    R.append(record(
        f"scheme29_nis_iodolactonization_{suffix}", 8, "literature_example",
        parts=(
            ("allenoic_acid_47", "reactant", f"optically active 4,5-allenoic acid 47, R={r_label}"),
            ("nis", "reagent", "NIS", (("equivalents", {"number": 2, "unit": "equiv"}),)),
            ("cs2co3", "reagent", "Cs2CO3", (("equivalents", {"number": 1, "unit": "equiv"}),)),
            ("ch2cl2", "solvent", "CH2Cl2"),
            ("lactone_48a", "product", f"Z-iodolactone 48A, R={r_label}"),
            ("lactone_48b", "product", f"E-iodolactone 48B, R={r_label}"),
        ),
        steps=(("step1", ("allenoic_acid_47", "nis", "cs2co3", "ch2cl2", "lactone_48a", "lactone_48b"), (
            ("solvent", "CH2Cl2"),
            ("temperature", {"number": -60, "unit": "°C"}),
            ("time", None),
        )),),
        outcomes=(
            ("reported_combined_yield_48a_48b", {"number": yield_value, "unit": "%"}, ("lactone_48a", "lactone_48b")),
            ("reported_ee", {"number": ee_value, "unit": "%"}, ("lactone_48a", "lactone_48b")),
            ("reported_Z_E_ratio", ze_ratio, ("lactone_48a", "lactone_48b")),
            ("yield_measurement_basis", None, None),
        ),
        unresolved=(
            "Reaction time and yield measurement basis are not printed in Scheme 29.",
            "The single ee value is printed for the depicted 48A/48B outcome and is not separately assigned to each isomer.",
            "Absolute structures and stereochemistry remain unverified; no SMILES was assigned.",
            "The original experimental article and SI were not supplied.",
        ),
    ))

for suffix, r_label, recovery, ee_value, ze_ratio in (
    ("n_c6h13", "n-C6H13", 74, 99, "Z/E = 99:1"),
    ("n_c5h11", "n-C5H11", 63, 98, "Z/E = 96:4"),
):
    R.append(record(
        f"scheme29_sonogashira_kinetic_resolution_{suffix}", 8, "literature_example",
        parts=(
            ("iodolactone_mixture", "reactant", f"iodolactone mixture 48A/48B, R={r_label}"),
            ("pd_catalyst", "catalyst", "PdCl2(PPh3)2", (("catalyst_loading", {"minimum": 3.5, "maximum": 4.5, "unit": "mol%", "raw_text": "3.5–4.5 mol%"}),)),
            ("cui", "catalyst", "CuI", (("catalyst_loading", {"minimum": 3.5, "maximum": 4.5, "unit": "mol%", "raw_text": "3.5–4.5 mol%"}),)),
            ("et2nh", "reagent", "Et2NH", (("equivalents", {"minimum": 0.35, "maximum": 0.45, "unit": "equiv", "raw_text": "0.35–0.45 equiv"}),)),
            ("propargyl_alcohol", "reagent", "propargyl alcohol", (("equivalents", {"minimum": 0.35, "maximum": 0.45, "unit": "equiv", "raw_text": "0.35–0.45 equiv"}),)),
            ("cross_coupled_product", "product", f"Sonogashira-coupled alkynyl lactone, R={r_label}"),
            ("recovered_48a", "product", f"enriched Z-iodolactone 48A, R={r_label}"),
        ),
        steps=(("step1", ("iodolactone_mixture", "pd_catalyst", "cui", "et2nh", "propargyl_alcohol", "cross_coupled_product", "recovered_48a"), (
            ("solvent", None),
            ("temperature", None),
            ("time", None),
        )),),
        outcomes=(
            ("recovered_48a_yield", {"number": recovery, "unit": "%"}, ("recovered_48a",)),
            ("reported_ee", {"number": ee_value, "unit": "%"}, ("recovered_48a",)),
            ("reported_Z_E_ratio", ze_ratio, ("recovered_48a",)),
            ("recovery_measurement_basis", None, None),
        ),
        unresolved=(
            "Temperature, duration, solvent, workup, purification, cross-coupled-product yield, and recovery measurement basis are not printed in Scheme 29.",
            "The loading ranges are shared across the two depicted substrate cases; exact case-specific values are not assigned.",
            "Absolute structures and stereochemistry remain unverified; no SMILES was assigned.",
            "The original experimental article and SI were not supplied.",
        ),
    ))

R.append(record(
    "scheme30_anti_iodolactonization_rationale", 8, "mechanism",
    notes=(
        "Scheme 30 proposes anti iodolactonization pathways to rationalize Z/E selectivity and axial-to-central chirality transfer; the depicted cationic paths are mechanistic, not separate batch experiments.",
    ),
))

# Page 8, Scheme 31: reaction scope plus separately classified proposed intermediate.
R.append(record(
    "scheme31_chiral_induction_iodolactonization", 8, "general_scheme",
    parts=(
        ("allenoic_acid_49", "reactant", "3-substituted optically active 4,5-allenoic acids 49, R1/R2=alkyl"),
        ("iodine", "reagent", "I2", (("equivalents", {"number": 1.5, "unit": "equiv"}),)),
        ("cyclohexane", "solvent", "cyclohexane"),
        ("lactone_50", "product", "trans iodolactones 50"),
    ),
    steps=(("step1", ("allenoic_acid_49", "iodine", "cyclohexane", "lactone_50"), (
        ("solvent", "cyclohexane"),
        ("temperature", "r.t."),
        ("time", None),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 72, "maximum": 86, "unit": "%", "raw_text": "72–86%"}, ("lactone_50",)),
        ("reported_ee", {"number": 99, "unit": "%"}, ("lactone_50",)),
        ("reported_Z_E_ratio_range", "Z/E 96:4 to 98:2", ("lactone_50",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "Reaction time and yield measurement basis are not printed in Scheme 31.",
        "The substrate-level assignment within the 72–86% and Z/E ranges is not shown in this Account.",
        "Generic R-group and stereochemical structures retain source labels; no SMILES was assigned.",
        "The original experimental article and SI were not supplied.",
    ),
))
R.append(record(
    "scheme31_pi_allyl_cation_intermediate_51", 8, "mechanism",
    notes=(
        "The 1,2-chiral induction is rationalized through proposed pi-allyl cationic intermediate 51; intermediate 51 is not a separately reported isolated product or experiment.",
    ),
))

# Page 8, Scheme 32: iodolactonization, general selenolactonization, and a special solvent row.
R.append(record(
    "scheme32_iodolactonization_23_allenoates", 8, "general_scheme",
    parts=(
        ("allenoate_52", "reactant", "ethyl 2,3-allenoates 52 (R-group scope shown)"),
        ("iodine", "reagent", "I2", (("equivalents", {"number": 2, "unit": "equiv"}),)),
        ("mecn_water", "solvent", "MeCN:H2O (15:1)"),
        ("iodobutenolide_53", "product", "beta-iodobutenolides 53"),
    ),
    steps=(("step1", ("allenoate_52", "iodine", "mecn_water", "iodobutenolide_53"), (
        ("solvent", "MeCN:H2O (15:1)"),
        ("temperature", "r.t."),
        ("time", None),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 60, "maximum": 94, "unit": "%", "raw_text": "60–94%"}, ("iodobutenolide_53",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "Reaction time, yield measurement basis, and substrate-level assignments within the scope range are not printed.",
        "Generic R-group structures retain source labels and no SMILES.",
        "The original experimental article and SI were not supplied.",
    ),
))
R.append(record(
    "scheme32_phsecl_lactonization_23_allenoates", 8, "general_scheme",
    parts=(
        ("allenoate_52", "reactant", "ethyl 2,3-allenoates 52 (R-group scope shown)"),
        ("phsecl", "reagent", "PhSeCl", (("equivalents", {"number": 2, "unit": "equiv"}),)),
        ("mecn_water", "solvent", "MeCN:H2O (10:1)"),
        ("selenobutenolide_54", "product", "beta-phenylselenobutenolides 54"),
    ),
    steps=(("step1", ("allenoate_52", "phsecl", "mecn_water", "selenobutenolide_54"), (
        ("solvent", "MeCN:H2O (10:1)"),
        ("temperature", "r.t."),
        ("time", {"minimum": 1, "maximum": 3.5, "unit": "h", "raw_text": "1–3.5 h"}),
    )),),
    outcomes=(
        ("reported_yield_range", {"minimum": 48, "maximum": 100, "unit": "%", "raw_text": "48–100%"}, ("selenobutenolide_54",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "The special R1=R2=H, R3=n-C3H7 row uses MeCN:H2O (1:1) and is represented separately.",
        "Yield measurement basis and substrate-level assignments within the general scope range are not printed.",
        "Generic R-group structures retain source labels and no SMILES.",
        "The original experimental article and SI were not supplied.",
    ),
))
R.append(record(
    "scheme32_phsecl_special_1_to_1_solvent", 8, "literature_example",
    parts=(
        ("allenoate_52_special", "reactant", "ethyl 2,3-allenoate 52, R1=R2=H and R3=n-C3H7"),
        ("phsecl", "reagent", "PhSeCl", (("equivalents", {"number": 2, "unit": "equiv"}),)),
        ("mecn_water", "solvent", "MeCN:H2O (1:1)"),
        ("selenobutenolide_54_special", "product", "beta-phenylselenobutenolide 54, R1=R2=H and R3=n-C3H7"),
    ),
    steps=(("step1", ("allenoate_52_special", "phsecl", "mecn_water", "selenobutenolide_54_special"), (
        ("solvent", "MeCN:H2O (1:1)"),
        ("temperature", "r.t."),
        ("time", {"minimum": 1, "maximum": 3.5, "unit": "h", "raw_text": "1–3.5 h"}),
    )),),
    outcomes=(
        ("reported_yield", {"number": 49, "unit": "%"}, ("selenobutenolide_54_special",)),
        ("yield_measurement_basis", None, None),
    ),
    unresolved=(
        "The shared Scheme 32 duration range is retained because the special line overrides solvent and yield but does not print a time override; exact substrate-specific duration and yield measurement basis remain unknown.",
        "The substrate and product drawings are fully substituted but their stereochemical/connectivity encoding remains unverified; no SMILES was assigned.",
        "The original experimental article and SI were not supplied.",
    ),
))


OUT.write_text(json.dumps(R, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"records": len(R), "output": str(OUT)}, ensure_ascii=False))
