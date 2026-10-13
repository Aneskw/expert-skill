import json
from pathlib import Path

DOC = "doc_9e20305837d2ecc2"
P1 = [f"{DOC}:page1:text", f"{DOC}:page1:image"]
P2 = [f"{DOC}:page2:text", f"{DOC}:page2:image"]
P3 = [f"{DOC}:page3:text", f"{DOC}:page3:image"]
P4 = [f"{DOC}:page4:text", f"{DOC}:page4:image"]


def fact(value, ev):
    return {"value": value, "evidence_ids": list(ev),
            "verification": "missing" if value is None else "unreviewed"}


def fld(name, value, ev, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def qty(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def part(entity_id, role, label, ev, name=None, amounts=None, smiles=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name is not None else fact(None, []),
        "smiles": fact(smiles, ev) if smiles is not None else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def rec(suffix, kind, ev, participants, conditions, outcomes,
        notes=None, unresolved=None, source_id=None):
    return {
        "record_id": f"{DOC}:{suffix}",
        "document_id": DOC,
        "source_reaction_id": source_id or suffix,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": [{
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in participants],
            "conditions": conditions,
        }] if conditions or participants else [],
        "outcomes": outcomes,
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Supporting information was not provided or explicitly associated; omitted operational details remain missing.",
                "Complex depicted structures were retained by source label/name without a machine-certified SMILES.",
            ],
        },
    }


records = []

# Page 1 / Scheme 2: explicitly cited prior literature, not experiments of this paper.
records.append(rec(
    "scheme2_literature_step1", "literature_example", P1 + P2,
    [part("lit1_diyne", "reactant", "diyne shown in Scheme 2, step 1", P2),
     part("lit1_alkyne", "reactant", "alkyne component", P1),
     part("lit1_product", "product", "carbazole regioisomer mixture", P1 + P2),
     part("lit1_rh", "catalyst", "RhCl(PPh3)3", P2)],
    [fld("operation", "rhodium-catalyzed [2+2+2] cyclotrimerization", P1 + P2)],
    [fld("regioisomer_ratio", "3.8:1", P1 + P2, ["lit1_product"])],
    notes=["Reported work of Witulski et al. (reference 5); not performed in the present paper."],
    unresolved=["Only the summary scheme and prose are present; substrate quantities, time, temperature, and yield are not reported here."],
))
records.append(rec(
    "scheme2_literature_step2", "literature_example", P1 + P2,
    [part("lit2_aniline", "reactant", "3-methoxyaniline", P1),
     part("lit2_bromotoluene", "reactant", "1-bromo-4-methylbenzene", P1),
     part("lit2_product", "product", "2-oxygenated carbazole target framework", P2),
     part("lit2_pd", "catalyst", "Pd(OAc)2", P2, amounts=[fld("catalyst_loading", qty(10, "mol%"), P2)]),
     part("lit2_cu", "reagent", "Cu(OAc)2", P1 + P2, amounts=[fld("equivalents", qty(2.5, "equiv"), P1 + P2)]),
     part("lit2_hoac", "solvent", "HOAc", P2)],
    [fld("temperature", "reflux", P2),
     fld("operation", "intermolecular C–N formation followed by intramolecular C–C formation", P1 + P2)],
    [], notes=["Reported work of Knölker et al. (reference 6); not performed in the present paper."],
    unresolved=["The summary does not give all stage-specific quantities, times, temperatures, or product yields; arrows are a condensed literature route."],
))
records.append(rec(
    "scheme2_literature_step3", "literature_example", P1 + P2,
    [part("lit3_nitrobiaryl", "reactant", "methyl 3-(2-nitro-3-methoxyphenyl)benzoate", P1),
     part("lit3_product", "product", "carbazole regioisomer mixture", P1 + P2),
     part("lit3_pof", "reagent", "P(OEt)3", P2)],
    [fld("temperature", qty(200, "°C"), P2),
     fld("operation", "microwave-assisted reductive cyclization", P1 + P2)],
    [fld("regioisomer_ratio", "1.4:1", P1 + P2, ["lit3_product"])],
    notes=["Reported work of Kuethe et al. (reference 8); not performed in the present paper."],
    unresolved=["The summary does not provide reagent amount, reaction time, or yield."],
))
records.append(rec(
    "scheme3_general_strategy", "general_scheme", P2,
    [part("gs3_allenol", "reactant", "1-indolyl-2,3-allenol family", P2),
     part("gs3_carbazole", "product", "2-oxygenated carbazole family", P2),
     part("gs3_au", "catalyst", "Au catalyst (unspecified in strategy arrow)", P2)],
    [fld("operation", "proposed Au-catalyzed benzannulation strategy", P2)], [],
    notes=["Scheme 3 is a generic strategy with variable R groups, not a single batch experiment."],
    unresolved=["Generic R-group structures and unspecified Au species cannot be expanded into a unique reaction record."],
))

# Scheme 4: two distinct debenzylation conditions.
records.append(rec(
    "scheme4_2a_to_3a_meli", "reported_experiment", P2,
    [part("s4_2a", "reactant", "carbazole 2a", P2),
     part("s4_3a", "product", "N-unprotected carbazole 3a", P2),
     part("s4_meli", "reagent", "MeLi", P2),
     part("s4_thf", "solvent", "THF", P2)],
    [fld("temperature", {"minimum": -40, "maximum": 20, "unit": "°C", "raw_text": "−40 °C–RT"}, P2)],
    [fld("reported_yield", qty(53, "%"), P2, ["s4_3a"])],
))
records.append(rec(
    "scheme4_2a_to_3a_tbuok", "reported_experiment", P2,
    [part("s4b_2a", "reactant", "carbazole 2a", P2),
     part("s4b_3a", "product", "N-unprotected carbazole 3a", P2),
     part("s4b_tbuok", "reagent", "tBuOK", P2),
     part("s4b_o2", "reagent", "O2", P2),
     part("s4b_dmso", "solvent", "DMSO", P2),
     part("s4b_thf", "solvent", "THF", P2)],
    [fld("operation", "oxidative N-debenzylation", P2)],
    [fld("reported_yield", qty(87, "%"), P2, ["s4b_3a"])],
))

# Scheme 5 and its prose; page 4 evidence is merged into the two 1b -> 2b batches.
records.append(rec(
    "scheme5_a_prepare_1b", "reported_experiment", P2 + P3,
    [part("s5a_4b", "reactant", "1-benzyl-5-methylindole-2-carbaldehyde (4b)", P2 + P3),
     part("s5a_allene", "reactant", "1-methoxypropa-1,2-diene", P2 + P3, smiles="COC=C=C"),
     part("s5a_nBuLi", "reagent", "nBuLi", P2 + P3),
     part("s5a_ether", "solvent", "Et2O", P3),
     part("s5a_1b", "product", "methoxy-substituted 2,3-allenol 1b", P2 + P3)],
    [fld("temperature", qty(-40, "°C"), P3),
     fld("operation", "in situ generation of 1-methoxypropa-1,2-dienyllithium followed by addition to aldehyde 4b", P2)],
    [fld("reported_yield", qty(70, "%"), P2 + P3, ["s5a_1b"])],
))
records.append(rec(
    "scheme5_1b_to_2b_ptcl2", "reported_experiment", P2 + P3 + P4,
    [part("pt_1b", "reactant", "allenol 1b", P2 + P3 + P4, amounts=[fld("mass", qty(64.0, "mg"), P4), fld("amount", qty(0.20, "mmol"), P4)]),
     part("pt_ptcl2", "catalyst", "PtCl2", P2 + P3 + P4, amounts=[fld("mass", qty(2.8, "mg"), P4), fld("amount", qty(0.01, "mmol"), P4), fld("catalyst_loading", qty(5, "mol%"), P3)]),
     part("pt_toluene", "solvent", "toluene", P2 + P3 + P4, amounts=[fld("volume", qty(2, "mL"), P4)]),
     part("pt_2b", "product", "9-benzyl-6-methyl-2-methoxy-9H-carbazole (2b)", P2 + P3 + P4, amounts=[fld("mass", qty(36.7, "mg"), P4)])],
    [fld("atmosphere", "nitrogen", P4), fld("temperature", "r.t.", P3 + P4), fld("time", qty(24, "h"), P4),
     fld("operation", "sequential addition to a dry Schlenk tube; stirred until TLC completion", P4),
     fld("workup", "evaporation", P4), fld("purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 20:1", P4)],
    [fld("isolated_yield", qty(61, "%"), P2 + P3 + P4, ["pt_2b"]), fld("yield_measurement_basis", "isolated after chromatography", P4, ["pt_2b"])],
    unresolved=["Supporting information was not explicitly provided; the main-text batch is otherwise transcribed.", "The complex structures of 1b and 2b are retained by label/name without a verified SMILES."],
))
records.append(rec(
    "scheme5_1b_to_2b_aucl", "reported_experiment", P2 + P3 + P4,
    [part("au_1b", "reactant", "allenol 1b", P2 + P3 + P4, amounts=[fld("mass", qty(604.5, "mg"), P4), fld("amount", qty(2.0, "mmol"), P4)]),
     part("au_aucl", "catalyst", "AuCl", P2 + P3 + P4, amounts=[fld("mass", qty(21.4, "mg"), P4), fld("amount", qty(0.092, "mmol"), P4)]),
     part("au_toluene", "solvent", "toluene", P2 + P3 + P4, amounts=[fld("volume", qty(10, "mL"), P4)]),
     part("au_2b", "product", "9-benzyl-6-methyl-2-methoxy-9H-carbazole (2b)", P2 + P3 + P4, amounts=[fld("mass", qty(481.6, "mg"), P4)])],
    [fld("temperature", "r.t.", P3 + P4), fld("time", qty(8, "h"), P4),
     fld("purification", "petroleum ether/ethyl acetate 40:1", P4)],
    [fld("isolated_yield", qty(81, "%"), P2 + P3 + P4, ["au_2b"]), fld("yield_measurement_basis", "product mass reported; chromatographic eluent specified", P4, ["au_2b"])],
))
records.append(rec(
    "scheme5_b_2b_to_5b", "reported_experiment", P2 + P3,
    [part("b_2b", "reactant", "carbazole 2b", P2 + P3), part("b_nbs", "reagent", "NBS", P3),
     part("b_ccl4", "solvent", "CCl4", P3), part("b_5b", "product", "3-bromocarbazole 5b", P2 + P3)],
    [fld("temperature", "reflux", P3), fld("time", qty(30, "min"), P3), fld("operation", "electrophilic bromination", P2)],
    [fld("reported_yield", qty(88, "%"), P2 + P3, ["b_5b"]), fld("selectivity", "only product", P2, ["b_5b"])],
))
records.append(rec(
    "scheme5_c_5b_to_6b", "reported_experiment", P2 + P3,
    [part("c_5b", "reactant", "N-benzyl carbazole 5b", P2 + P3), part("c_tbuok", "reagent", "tBuOK", P2 + P3),
     part("c_o2", "reagent", "O2", P2 + P3, amounts=[fld("pressure", "1 atm", P3)]),
     part("c_dmso", "solvent", "DMSO", P2 + P3), part("c_6b", "product", "N-debenzylated carbazole 6b", P2 + P3)],
    [fld("temperature", "r.t.", P3), fld("time", qty(5, "h"), P3), fld("operation", "oxidative N-debenzylation", P2)],
    [fld("reported_yield", qty(80, "%"), P2 + P3, ["c_6b"])],
))
records.append(rec(
    "scheme5_d_5b_to_7b", "reported_experiment", P2 + P3,
    [part("d_5b", "reactant", "3-bromocarbazole 5b", P2 + P3),
     part("d_prenylB", "reactant", "pinacol prenylboronate", P2 + P3, amounts=[fld("equivalents", qty(2, "equiv"), P3)]),
     part("d_pd", "catalyst", "Pd(PPh3)4", P3, amounts=[fld("catalyst_loading", qty(5, "mol%"), P3)]),
     part("d_naoh", "reagent", "NaOH", P3, amounts=[fld("equivalents", qty(20, "equiv"), P3)]),
     part("d_tol", "solvent", "toluene", P3), part("d_7b", "product", "prenylated carbazole 7b", P2 + P3)],
    [fld("temperature", qty(90, "°C"), P3), fld("time", qty(1, "h"), P3), fld("operation", "Suzuki cross-coupling", P2)],
    [fld("reported_yield", qty(72, "%"), P2 + P3, ["d_7b"])],
))

for suffix, reagent_label, extra_parts in [
    ("scheme5_pathA_7b_licl_failed", "LiCl", []),
    ("scheme5_pathA_7b_etsna_failed", "EtSNa", []),
    ("scheme5_pathA_7b_phsh_failed", "PhSH", [part("pa_k2co3", "catalyst", "K2CO3 (catalytic amount)", P2)]),
]:
    solvent = "DMF" if "phsh" not in suffix else "NMP"
    records.append(rec(
        suffix, "optimization_entry", P2 + P3,
        [part(suffix+"_7b", "reactant", "carbazole 7b", P2 + P3),
         part(suffix+"_reagent", "reagent", reagent_label, P2),
         part(suffix+"_solvent", "solvent", solvent, P2),
         *extra_parts,
         part(suffix+"_target", "product", "siamenol (target, not obtained)", P2 + P3)],
        [fld("temperature", "reflux", P2), fld("operation", "attempted O-demethylation", P2)],
        [fld("reaction_result", "decomposition; siamenol not obtained", P2, [suffix+"_target"])],
        unresolved=["Exact reagent loading and duration are not reported in the main text; decomposition products are unidentified."],
    ))

records.append(rec(
    "scheme5_e_5b_to_8b_two_step", "reported_experiment", P2 + P3,
    [part("e_5b", "reactant", "3-bromocarbazole 5b", P2 + P3),
     part("e_prenylB", "reactant", "pinacol prenylboronate", P2 + P3, amounts=[fld("equivalents", qty(2, "equiv"), P3)]),
     part("e_pd", "catalyst", "Pd(PPh3)4", P3, amounts=[fld("catalyst_loading", qty(5, "mol%"), P3)]),
     part("e_naoh", "reagent", "NaOH", P3, amounts=[fld("equivalents", qty(20, "equiv"), P3)]),
     part("e_tol", "solvent", "toluene", P3),
     part("e_etsna", "reagent", "EtSNa", P2 + P3, amounts=[fld("equivalents", qty(6, "equiv"), P3)]),
     part("e_dmf", "solvent", "DMF", P2 + P3), part("e_8b", "product", "phenolic carbazole 8b", P2 + P3)],
    [fld("stage_1_temperature", qty(90, "°C"), P3), fld("stage_1_time", qty(1, "h"), P3),
     fld("stage_1_operation", "Suzuki cross-coupling", P2 + P3), fld("stage_2_temperature", "reflux", P2 + P3),
     fld("stage_2_operation", "O-demethylation with EtSNa", P2 + P3)],
    [fld("two_step_reported_yield", qty(60, "%"), P2 + P3, ["e_8b"])],
))

for suffix, reagent, solvent, operation in [
    ("scheme5_pathB_8b_tbuok_failed", "tBuOK / O2", "DMSO", "attempted oxidative N-debenzylation"),
    ("scheme5_pathB_8b_ddq_failed", "DDQ", "CH2Cl2", "attempted N-debenzylation"),
    ("scheme5_pathB_8b_meli_failed", "MeLi", "THF", "attempted N-debenzylation"),
]:
    records.append(rec(
        suffix, "optimization_entry", P2 + P3,
        [part(suffix+"_8b", "reactant", "N-benzyl carbazole 8b", P2 + P3),
         part(suffix+"_reagent", "reagent", reagent, P2),
         part(suffix+"_solvent", "solvent", solvent, P2),
         part(suffix+"_target", "product", "siamenol (target, not obtained)", P2 + P3)],
        [fld("operation", operation, P2)],
        [fld("reaction_result", "failed to generate siamenol", P2, [suffix+"_target"])],
        unresolved=["Exact reagent loading, temperature, duration, and observed material are not reported in the main text."],
    ))

records.append(rec(
    "scheme5_f_6b_to_9b", "reported_experiment", P2 + P3,
    [part("f_6b", "reactant", "methoxy carbazole 6b", P2 + P3),
     part("f_bbr3", "reagent", "BBr3", P2 + P3, amounts=[fld("equivalents", qty(2, "equiv"), P3)]),
     part("f_dcm", "solvent", "CH2Cl2", P2 + P3), part("f_9b", "product", "phenolic bromocarbazole 9b", P2 + P3)],
    [fld("temperature", {"minimum": -78, "maximum": 20, "unit": "°C", "raw_text": "−78 °C–RT"}, P3), fld("operation", "O-demethylation", P2)],
    [fld("reported_yield", qty(88, "%"), P2 + P3, ["f_9b"])],
))
records.append(rec(
    "scheme5_9b_direct_suzuki_failed", "optimization_entry", P2,
    [part("fd_9b", "reactant", "phenolic bromocarbazole 9b", P2), part("fd_prenylB", "reactant", "pinacol prenylboronate", P2),
     part("fd_pd", "catalyst", "Pd(0) catalyst (unspecified)", P2), part("fd_target", "product", "prenylated coupling product (not obtained)", P2)],
    [fld("operation", "attempted direct Suzuki cross-coupling", P2)],
    [fld("reaction_result", "failed", P2, ["fd_target"])],
    unresolved=["Exact palladium species, quantities, solvent, temperature, duration, and observed products are absent from the main text."],
))
records.append(rec(
    "scheme5_9b_tbs_route_failed", "optimization_entry", P2,
    [part("ft_9b", "reactant", "phenolic bromocarbazole 9b", P2), part("ft_tbs", "reagent", "TBS protecting group reagent (unspecified)", P2),
     part("ft_prenylB", "reactant", "pinacol prenylboronate", P2), part("ft_target", "product", "Suzuki coupling product (not obtained)", P2)],
    [fld("operation", "TBS protection followed by attempted Suzuki coupling", P2)],
    [fld("reaction_result", "Suzuki coupling did not occur", P2, ["ft_target"])],
    unresolved=["TBS reagent, catalyst, quantities, conditions, and fate of the protected intermediate are not reported in the main text."],
))
records.append(rec(
    "scheme5_g_9b_to_10b", "reported_experiment", P3,
    [part("g_9b", "reactant", "phenolic bromocarbazole 9b", P3), part("g_ac2o", "reagent", "Ac2O", P3),
     part("g_dmap", "catalyst", "DMAP", P3), part("g_et3n", "reagent", "Et3N", P3),
     part("g_ether", "solvent", "Et2O", P3), part("g_10b", "product", "O-acetyl/N-acetyl intermediate 10b", P3)],
    [fld("time", qty(11, "h"), P3), fld("operation", "acetylation/protection", P3)],
    [fld("reported_yield", qty(90, "%"), P3, ["g_10b"])],
))
records.append(rec(
    "scheme5_h_10b_to_siamenol", "reported_experiment", P3,
    [part("h_10b", "reactant", "protected bromocarbazole 10b", P3),
     part("h_prenylB", "reactant", "pinacol prenylboronate", P3, amounts=[fld("equivalents", qty(2, "equiv"), P3)]),
     part("h_pd", "catalyst", "Pd(PPh3)4", P3, amounts=[fld("catalyst_loading", qty(5, "mol%"), P3)]),
     part("h_naoh1", "reagent", "NaOH (coupling stage)", P3, amounts=[fld("equivalents", qty(20, "equiv"), P3)]),
     part("h_tol", "solvent", "toluene", P3),
     part("h_naoh2", "reagent", "NaOH (deprotection stage)", P3, amounts=[fld("equivalents", qty(20, "equiv"), P3)]),
     part("h_meoh", "solvent", "CH3OH", P3), part("h_siamenol", "product", "siamenol", P3)],
    [fld("stage_1_temperature", qty(90, "°C"), P3), fld("stage_1_time", qty(1, "h"), P3),
     fld("stage_1_operation", "Suzuki coupling", P3), fld("stage_2_temperature", qty(90, "°C"), P3),
     fld("stage_2_time", qty(1, "h"), P3), fld("stage_2_operation", "base-mediated deprotection", P3)],
    [fld("one_pot_reported_yield", qty(66, "%"), P3, ["h_siamenol"])],
))

# Scheme 6.
records.append(rec(
    "scheme6_a_prepare_1c", "reported_experiment", P3,
    [part("s6a_4c", "reactant", "6-bromo-1-benzylindole-2-carbaldehyde (4c)", P3),
     part("s6a_allene", "reactant", "1-methoxypropa-1,2-diene", P3, smiles="COC=C=C"),
     part("s6a_nbu", "reagent", "nBuLi", P3), part("s6a_ether", "solvent", "Et2O", P3),
     part("s6a_1c", "product", "methoxy-substituted allenol 1c", P3)],
    [fld("temperature", qty(-40, "°C"), P3)],
    [fld("reported_yield", qty(68, "%"), P3, ["s6a_1c"])],
))
records.append(rec(
    "scheme6_1c_to_2c_aucl", "reported_experiment", P3,
    [part("s6cy_1c", "reactant", "allenol 1c", P3), part("s6cy_au", "catalyst", "AuCl", P3),
     part("s6cy_tol", "solvent", "toluene", P3), part("s6cy_2c", "product", "brominated carbazole 2c", P3)],
    [fld("temperature", "r.t.", P3), fld("operation", "AuCl-catalyzed cyclization/benzannulation", P3)],
    [fld("reported_yield", qty(83, "%"), P3, ["s6cy_2c"]), fld("selectivity", "exclusive formation of 2c", P3, ["s6cy_2c"])],
))
records.append(rec(
    "scheme6_b_2c_to_3c", "reported_experiment", P3,
    [part("s6b_2c", "reactant", "N-benzyl carbazole 2c", P3), part("s6b_tbuok", "reagent", "tBuOK", P3),
     part("s6b_o2", "reagent", "O2", P3, amounts=[fld("pressure", "1 atm", P3)]),
     part("s6b_dmso", "solvent", "DMSO", P3), part("s6b_thf", "solvent", "THF", P3),
     part("s6b_3c", "product", "6-bromo-2-methoxy-9H-carbazole (3c)", P3)],
    [fld("temperature", "r.t.", P3), fld("operation", "oxidative N-debenzylation", P3)],
    [fld("reported_yield", qty(72, "%"), P3, ["s6b_3c"])],
))
records.append(rec(
    "scheme6_c_3c_to_clauszoline_k", "reported_experiment", P3,
    [part("s6c_3c", "reactant", "carbazole 3c", P3), part("s6c_kh", "reagent", "KH", P3),
     part("s6c_tbu", "reagent", "tBuLi", P3), part("s6c_dmf", "reagent", "DMF", P3),
     part("s6c_thf", "solvent", "THF", P3), part("s6c_prod", "product", "clauszoline-K", P3)],
    [fld("stage_1_temperature", "r.t.", P3), fld("stage_1_operation", "treatment with KH in THF", P3),
     fld("stage_2_temperature", qty(-40, "°C"), P3), fld("stage_2_operation", "tBuLi treatment and formylation with DMF", P3)],
    [fld("reported_yield", qty(54, "%"), P3, ["s6c_prod"])],
))
records.append(rec(
    "scheme6_d_3c_to_clausine_n", "reported_experiment", P3,
    [part("s6d_3c", "reactant", "carbazole 3c", P3), part("s6d_kh", "reagent", "KH", P3),
     part("s6d_tbu", "reagent", "tBuLi", P3), part("s6d_co2", "reagent", "CO2", P3),
     part("s6d_thf", "solvent", "THF", P3), part("s6d_prod", "product", "clausine-N", P3)],
    [fld("stage_1_temperature", "r.t.", P3), fld("stage_1_operation", "treatment with KH in THF", P3),
     fld("stage_2_temperature", qty(-78, "°C"), P3), fld("stage_2_operation", "Li–Br exchange with tBuLi and carboxylation with CO2", P3)],
    [fld("reported_yield", qty(84, "%"), P3, ["s6d_prod"])],
))
records.append(rec(
    "scheme6_e_3c_to_clauszoline_l", "reported_experiment", P3,
    [part("s6e_3c", "reactant", "carbazole 3c", P3), part("s6e_kh", "reagent", "KH", P3),
     part("s6e_tbu", "reagent", "tBuLi", P3), part("s6e_clcoome", "reagent", "ClCOOMe", P3),
     part("s6e_naoh", "reagent", "NaOH", P3), part("s6e_thf", "solvent", "THF", P3),
     part("s6e_meoh", "solvent", "CH3OH", P3), part("s6e_prod", "product", "clausine-C (clauszoline-L)", P3)],
    [fld("stage_1_temperature", qty(-78, "°C"), P3), fld("stage_1_operation", "KH/tBuLi treatment followed by ClCOOMe", P3),
     fld("stage_2_temperature", qty(90, "°C"), P3), fld("stage_2_operation", "NaOH treatment in CH3OH", P3)],
    [fld("two_step_reported_yield", qty(42, "%"), P3, ["s6e_prod"])],
))
records.append(rec(
    "scheme6_f_clausine_n_to_clauszoline_l", "reported_experiment", P3,
    [part("s6f_n", "reactant", "clausine-N", P3), part("s6f_mei", "reagent", "MeI", P3),
     part("s6f_base", "reagent", "NaHCO3", P3), part("s6f_dmf", "solvent", "DMF", P3),
     part("s6f_prod", "product", "clausine-C (clauszoline-L)", P3)],
    [fld("operation", "methylation of the carboxylic acid", P3)],
    [fld("reported_yield", qty(95, "%"), P3, ["s6f_prod"])],
))
records.append(rec(
    "scheme6_g_clauszoline_l_to_clausine_m", "reported_experiment", P3,
    [part("s6g_l", "reactant", "clauszoline-L", P3),
     part("s6g_bbr", "reagent", "BBr3", P3, amounts=[fld("equivalents", qty(4.3, "equiv"), P3)]),
     part("s6g_dcm", "solvent", "CH2Cl2", P3), part("s6g_m", "product", "clausine-M", P3)],
    [fld("temperature", {"minimum": -78, "maximum": -20, "unit": "°C", "raw_text": "−78 °C to −20 °C"}, P3),
     fld("operation", "O-demethylation", P3)],
    [fld("reported_yield", qty(60, "%"), P3, ["s6g_m"])],
))
records.append(rec(
    "scheme6_h_clauszoline_k_to_3formyl7hydroxy", "reported_experiment", P3,
    [part("s6h_k", "reactant", "clauszoline-K", P3),
     part("s6h_bbr", "reagent", "BBr3", P3, amounts=[fld("equivalents", qty(4.5, "equiv"), P3)]),
     part("s6h_dcm", "solvent", "CH2Cl2", P3), part("s6h_prod", "product", "3-formyl-7-hydroxycarbazole", P3)],
    [fld("temperature", {"minimum": -78, "maximum": -20, "unit": "°C", "raw_text": "−78 °C to −20 °C"}, P3),
     fld("operation", "O-demethylation", P3)],
    [fld("reported_yield", qty(54, "%"), P3, ["s6h_prod"])],
))

out = Path(__file__).with_name("records_pages_0001_0004.json")
out.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(f"wrote {len(records)} records to {out}")
