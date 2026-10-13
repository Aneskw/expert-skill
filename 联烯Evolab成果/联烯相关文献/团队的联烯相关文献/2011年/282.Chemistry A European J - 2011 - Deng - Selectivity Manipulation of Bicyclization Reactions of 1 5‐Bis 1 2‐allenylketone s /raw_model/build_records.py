import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOC = "doc_e36dffdee21ef0a9"


def ev(page, kind="image"):
    return f"{DOC}:page{page}:{kind}"


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": list(evidence) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def field(name, value, evidence, targets=None):
    item = {"name": name, "fact": fact(value, evidence)}
    if targets:
        item["target_entity_ids"] = targets
    return item


def participant(entity_id, role, label, evidence, name=None, smiles=None, amounts=None):
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence) if name else fact(None, []),
        "smiles": fact(smiles, evidence) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, evidence, participants=None, steps=None, outcomes=None,
           notes=None, unresolved=None):
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(evidence)),
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


def q(number, unit, **extra):
    return {"number": number, "unit": unit, **extra}


def solvent(label, evidence):
    names = {
        "DMF": ("N,N-dimethylformamide", "CN(C)C=O"),
        "DMA": ("N,N-dimethylacetamide", "CC(=O)N(C)C"),
        "DMSO": ("dimethyl sulfoxide", "CS(C)=O"),
        "CH3NO2": ("nitromethane", "C[N+](=O)[O-]"),
        "THF": ("tetrahydrofuran", "C1CCOC1"),
        "CH3CN": ("acetonitrile", "CC#N"),
        "acetone": ("acetone", "CC(=O)C"),
        "DCE": ("1,2-dichloroethane", "ClCCCl"),
        "DMF (prior work)": ("N,N-dimethylformamide", "CN(C)C=O"),
    }
    name, smiles = names[label]
    return participant("solvent", "solvent", label, evidence, name, smiles)


def catalyst(entity_id, label, evidence, loading=5):
    amounts = [] if loading is None else [field("catalyst_loading", q(loading, "mol%"), evidence)]
    return participant(entity_id, "catalyst", label, evidence, label, amounts=amounts)


def table1_record(entry, solvent_label, yield_value, ratio=None):
    evidence = [ev(2, "image"), ev(2, "text")]
    parts = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    "N-tethered 1,5-bis(1,2-allenylketone) 1a",
                    "C=C=C(CN(CC(=C=C)C(=O)CC)S(=O)(=O)c1ccc(C)cc1)C(=O)CC"),
        catalyst("pd_catalyst", "[PdCl2(MeCN)2]", evidence),
        solvent(solvent_label, evidence),
        participant("product_2a", "product", "2a", evidence, "furo[3,4-c]azepine regioisomer 2a"),
        participant("product_3a", "product", "3a", evidence, "C=C-bond regioisomer 3a"),
        participant("internal_standard", "reagent", "1,3,5-trimethylbenzene", evidence,
                    "1,3,5-trimethylbenzene", "Cc1cc(C)cc(C)c1"),
    ]
    temperature = "RT" if entry == 7 else {"minimum": 30, "maximum": 35, "unit": "°C", "raw_text": "30–35 °C"}
    cond = [
        field("solvent", solvent_label, evidence),
        field("concentration", q(0.1, "M"), evidence),
        field("temperature", temperature, evidence),
        field("time", q(5, "h"), evidence),
    ]
    outcomes = [field("combined_NMR_yield_2a_plus_3a", yield_value, evidence,
                      ["product_2a", "product_3a"]),
                field("yield_measurement_basis", "1H NMR using 1,3,5-trimethylbenzene as internal standard", evidence)]
    if ratio is not None:
        outcomes.append(field("NMR_ratio_2a_to_3a", ratio, evidence, ["product_2a", "product_3a"]))
    unresolved = ["Supporting information was not provided or explicitly associated.",
                  "Product structures were not independently transcribed to SMILES from the drawing."]
    if entry == 2:
        unresolved.append("The printed 2a/3a ratio is 89/19 and sums to 108; preserved without correction.")
    if yield_value == "trace":
        unresolved.append("The source reports trace combined product and gives no 2a/3a ratio.")
    return record(f"table1_entry{entry}", "optimization_entry", evidence, parts,
                  [{"step_id": "cyclization", "participant_ids": ["substrate_1a", "pd_catalyst", "solvent"], "conditions": cond},
                   {"step_id": "NMR_analysis", "participant_ids": ["product_2a", "product_3a", "internal_standard"],
                    "conditions": [field("operation", "1H NMR analysis using 1,3,5-trimethylbenzene as internal standard", evidence)]}],
                  outcomes, ["Table 1 solvent-screening row."], unresolved)


def table2_record(entry, catalyst_label, temperature, nmr_yield, ratio, recovery=None):
    evidence = [ev(2, "image"), ev(2, "text")]
    cat_id = f"rh_catalyst_{entry}"
    parts = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    "N-tethered 1,5-bis(1,2-allenylketone) 1a",
                    "C=C=C(CN(CC(=C=C)C(=O)CC)S(=O)(=O)c1ccc(C)cc1)C(=O)CC"),
        catalyst(cat_id, catalyst_label, evidence), solvent("acetone", evidence),
        participant("product_2a", "product", "2a", evidence, "furo[3,4-c]azepine regioisomer 2a"),
        participant("product_3a", "product", "3a", evidence, "C=C-bond regioisomer 3a"),
    ]
    outcomes = [field("NMR_yield_2a", q(nmr_yield, "%"), evidence, ["product_2a"]),
                field("yield_measurement_basis", "NMR yield", evidence)]
    if ratio == "dash":
        outcomes.append(field("product_ratio_2a_to_3a_source_marker", "table dash (–)", evidence, ["product_2a", "product_3a"]))
    else:
        outcomes.append(field("ratio_2a_to_3a", ratio, evidence, ["product_2a", "product_3a"]))
    if recovery is not None:
        outcomes.append(field("recovered_starting_material_yield", q(recovery, "%"), evidence, ["substrate_1a"]))
    return record(f"table2_entry{entry}", "optimization_entry", evidence, parts,
                  [{"step_id": "cyclization", "participant_ids": ["substrate_1a", cat_id, "solvent"],
                    "conditions": [field("solvent", "acetone", evidence), field("concentration", q(0.05, "M"), evidence),
                                   field("temperature", temperature, evidence), field("time", q(1, "h"), evidence)]}],
                  outcomes, ["Table 2 catalyst-screening row."],
                  ["Supporting information was not provided or explicitly associated.",
                   "Product structures were not independently transcribed to SMILES from the drawing."])


def standard_1a_record():
    evidence = [ev(2, "image"), ev(2, "text"), ev(3, "image"), ev(3, "text"), ev(4, "image"), ev(4, "text")]
    parts = [
        participant("substrate_1a", "reactant", "1a", evidence,
                    "N-tethered 1,5-bis(1,2-allenylketone) 1a",
                    "C=C=C(CN(CC(=C=C)C(=O)CC)S(=O)(=O)c1ccc(C)cc1)C(=O)CC",
                    [field("mass", q(38.0, "mg"), [ev(4, "image"), ev(4, "text")]),
                     field("amount", q(0.10, "mmol"), [ev(4, "image"), ev(4, "text")])]),
        participant("rh_catalyst", "catalyst", "[RhCl(CO)2]2", evidence, "[RhCl(CO)2]2", amounts=[
            field("catalyst_loading", q(5, "mol%"), [ev(2, "image"), ev(3, "image"), ev(4, "image")]),
            field("mass", q(2.2, "mg"), [ev(4, "image"), ev(4, "text")]),
            field("amount", q(0.0057, "mmol"), [ev(4, "image"), ev(4, "text")]),
        ]),
        participant("solvent", "solvent", "acetone", evidence, "acetone", "CC(=O)C",
                    [field("volume", q(2, "mL"), [ev(4, "image"), ev(4, "text")])]),
        participant("product_2a", "product", "2a", evidence, "furo[3,4-c]azepine derivative 2a",
                    amounts=[field("mass", q(30.3, "mg"), [ev(4, "image"), ev(4, "text")])]),
        participant("product_3a", "product", "3a", evidence, "C=C-bond regioisomer 3a"),
    ]
    steps = [{"step_id": "cyclization", "participant_ids": ["substrate_1a", "rh_catalyst", "solvent"],
              "conditions": [field("solvent", "acetone", evidence), field("concentration", q(0.05, "M"), [ev(2, "image"), ev(2, "text")]),
                             field("temperature_table2_and_experimental", "RT", evidence),
                             field("temperature_table3_scheme", q(25, "°C"), [ev(3, "image"), ev(3, "text")]),
                             field("time", q(1, "h"), evidence),
                             field("operation", "stirred until complete as monitored by TLC", [ev(4, "image"), ev(4, "text")])]},
             {"step_id": "isolation", "participant_ids": ["product_2a"],
              "conditions": [field("workup", "evaporation", [ev(4, "image"), ev(4, "text")]),
                             field("purification", "silica-gel column chromatography; petroleum ether/ethyl acetate 5:1", [ev(4, "image"), ev(4, "text")])]}]
    outcomes = [field("NMR_yield_2a", q(83, "%"), [ev(2, "image"), ev(2, "text")], ["product_2a"]),
                field("isolated_yield_2a", q(80, "%"), evidence, ["product_2a"]),
                field("ratio_2a_to_3a", ">99:1", [ev(2, "image"), ev(2, "text")], ["product_2a", "product_3a"]),
                field("physical_form", "solid", [ev(4, "image"), ev(4, "text")]),
                field("melting_point", {"minimum": 110, "maximum": 111, "unit": "°C", "raw_text": "110–111 °C"}, [ev(4, "image"), ev(4, "text")])]
    return record("table2_entry5_table3_entry1_standard_1a", "reported_experiment", evidence, parts, steps, outcomes,
                  ["Table 2 entry 5, Table 3 entry 1, and the Experimental Section describe the same standard 1a batch/outcome and are merged."],
                  ["Supporting information is mentioned by the paper but was not provided or explicitly associated.",
                   "The product drawing was not independently transcribed to SMILES.",
                   "The source uses RT in Table 2/Experimental Section and 25 °C in the Table 3 scheme; both source expressions are retained.",
                   "Reaction atmosphere is not reported."])


def scheme3_failure(label, x_value, r_value):
    evidence = [ev(2, "image"), ev(2, "text")]
    parts = [participant("substrate", "reactant", label, evidence, f"1,5-bis(1,2-allenylketone) {label}; X={x_value}, R={r_value}"),
             catalyst("pd_catalyst", "[PdCl2(MeCN)2]", evidence), solvent("CH3CN", evidence),
             participant("expected_product_2", "product", "expected bicyclic product 2", evidence)]
    return record(f"scheme3_{label}_no_reaction", "substrate_scope_entry", evidence, parts,
                  [{"step_id": "attempted_cyclization", "participant_ids": ["substrate", "pd_catalyst", "solvent"],
                    "conditions": [field("solvent", "CH3CN", evidence), field("temperature", {"minimum": 30, "maximum": 35, "unit": "°C", "raw_text": "30–35 °C"}, evidence), field("time", q(10, "h"), evidence)]}],
                  [field("reaction_result", "no reaction occurred", evidence, ["expected_product_2"])],
                  [f"Scheme 3 row: X={x_value}; R={r_value}."],
                  ["No product yield or recovered-starting-material amount is reported.", "Substrate and expected-product SMILES are not independently verified."])


def table3_record(entry, x_value, r_value, substrate, product, yield_number, temp=None, time_h=1, solv="acetone", conflict=False):
    evidence = [ev(3, "image"), ev(3, "text")]
    temp = temp if temp is not None else q(25, "°C")
    parts = [participant("substrate", "reactant", substrate, evidence, f"1,5-bis(1,2-allenylketone) {substrate}; X={x_value}, R={r_value}"),
             catalyst("rh_catalyst", "[RhCl(CO)2]2", evidence), solvent(solv, evidence),
             participant("product", "product", product, evidence, f"fused bicyclic furan {product}")]
    unresolved = ["Supporting information was not provided or explicitly associated.",
                  "Substrate and product SMILES were not independently transcribed from the variable-group table drawing."]
    if conflict:
        unresolved.append("Table 3 marks entry 10 with footnote [c] (DCE, 70 °C, 1 h), while the prose describes the 44% result before introducing the new DCE conditions; the row-specific table footnote is retained and the inconsistency is unresolved.")
    return record(f"table3_entry{entry}", "substrate_scope_entry", evidence, parts,
                  [{"step_id": "cyclization", "participant_ids": ["substrate", "rh_catalyst", "solvent"],
                    "conditions": [field("solvent", solv, evidence), field("temperature", temp, evidence), field("time", q(time_h, "h"), evidence)]}],
                  [field("isolated_yield", q(yield_number, "%"), evidence, ["product"]), field("yield_measurement_basis", "isolated yield", evidence)],
                  [f"Table 3 row: X={x_value}; R={r_value}."], unresolved)


def scheme4_record(condition, temp, y2, y3, basis, selectivity=False):
    evidence = [ev(3, "image"), ev(3, "text")]
    parts = [participant("substrate_1k", "reactant", "1k", evidence, "oxygen-tethered 1,5-bis(1,2-allenylketone) 1k"),
             catalyst("rh_catalyst", "[RhCl(CO)2]2", evidence), solvent(condition, evidence),
             participant("product_2k", "product", "2k", evidence), participant("product_3k", "product", "3k", evidence)]
    outcomes = [field(f"{basis}_yield_2k", q(y2, "%"), evidence, ["product_2k"]),
                field(f"{basis}_yield_3k", q(y3, "%"), evidence, ["product_3k"]),
                field("yield_measurement_basis", basis, evidence)]
    if selectivity:
        outcomes.append(field("NMR_ratio_2k_to_3k", ">99:1", evidence, ["product_2k", "product_3k"]))
    return record(f"scheme4_{condition.lower()}", "optimization_entry", evidence, parts,
                  [{"step_id": "cyclization", "participant_ids": ["substrate_1k", "rh_catalyst", "solvent"],
                    "conditions": [field("solvent", condition, evidence), field("temperature", temp, evidence), field("time", q(1, "h"), evidence)]}],
                  outcomes, ["Scheme 4 solvent/temperature comparison."],
                  ["Supporting information was not provided or explicitly associated.", "Structures were not independently transcribed to SMILES."])


def table4_record(entry, aryl, alkyl, substrate, time_min, p1, y1, p2, y2, y2_basis="isolated"):
    evidence = [ev(3, "image"), ev(3, "text")]
    parts = [participant("substrate", "reactant", substrate, evidence, f"unsymmetrical 1,5-bis(1,2-allenylketone) {substrate}; Aryl={aryl}, Alkyl={alkyl}"),
             catalyst("rh_catalyst", "[RhCl(CO)2]2", evidence), solvent("DCE", evidence),
             participant("product_2", "product", p1, evidence), participant("product_2prime", "product", p2, evidence)]
    return record(f"table4_entry{entry}", "substrate_scope_entry", evidence, parts,
                  [{"step_id": "cyclization", "participant_ids": ["substrate", "rh_catalyst", "solvent"],
                    "conditions": [field("solvent", "DCE", evidence), field("temperature", "RT", evidence), field("time", q(time_min, "min"), evidence)]}],
                  [field("isolated_yield_2", q(y1, "%"), evidence, ["product_2"]),
                   field(f"{y2_basis}_yield_2prime", q(y2, "%"), evidence, ["product_2prime"]),
                   field("yield_measurement_basis_2", "isolated yield", evidence),
                   field("yield_measurement_basis_2prime", f"{y2_basis} yield", evidence)],
                  [f"Table 4 row: Aryl={aryl}; Alkyl={alkyl}."],
                  ["Supporting information was not provided or explicitly associated.", "Structures were not independently transcribed to SMILES."])


def scheme6_record(hours):
    evidence = [ev(4, "image"), ev(4, "text")]
    parts = [participant("starting_2a", "reactant", "2a", evidence, amounts=[field("mixture_fraction", q(87, "%"), evidence)]),
             participant("starting_3a", "reactant", "3a", evidence, amounts=[field("mixture_fraction", q(13, "%"), evidence)]),
             catalyst("rh_catalyst", "[RhCl(CO)2]2", evidence), solvent("acetone", evidence),
             participant("observed_2a", "product", "2a after treatment", evidence), participant("observed_3a", "product", "3a after treatment", evidence)]
    return record(f"scheme6_isomerization_{hours}h", "reported_experiment", evidence, parts,
                  [{"step_id": "isomerization_test", "participant_ids": ["starting_2a", "starting_3a", "rh_catalyst", "solvent"],
                    "conditions": [field("solvent", "acetone", evidence), field("temperature", q(25, "°C"), evidence), field("time", q(hours, "h"), evidence)]}],
                  [field("starting_ratio_2a_to_3a", "87:13", evidence, ["starting_2a", "starting_3a"]),
                   field("ratio_2a_to_3a_after_treatment", "87:13", evidence, ["observed_2a", "observed_3a"]),
                   field("isomerization_result", "unchanged 2a/3a ratio", evidence, ["observed_2a", "observed_3a"])],
                  ["Scheme 6 control experiment; no isomerization was observed at the reported ratio resolution."],
                  ["No isolated mass/yield is reported.", "Structures were not independently transcribed to SMILES."])


records = []

# Page 1: explicitly classify prior work and the conceptual product map.
e1 = [ev(1, "image"), ev(1, "text")]
records.append(record("equation1_prior_bisallenol_bicyclization", "literature_example", e1,
    [participant("generic_bisallenol", "reactant", "symmetrical 1,ω-bisallenol", e1), catalyst("pdii", "Pd(II)", e1),
     solvent("DMF (prior work)", e1), participant("generic_product", "product", "2,5-dihydrofuran-fused bicyclic product", e1)],
    [{"step_id": "prior_literature_transformation", "participant_ids": ["generic_bisallenol", "pdii", "solvent"],
      "conditions": [field("solvent", "DMF", e1)]}], [],
    ["Equation (1) is cited prior work (reference 7), not a new experiment in this paper."],
    ["Generic R groups, X and leaving group prevent assignment of a unique structure; time, temperature and outcome yield are not shown."]))
records.append(record("scheme2_possible_products", "general_scheme", e1,
    [participant("generic_substrate_1", "reactant", "generic bis(allenylketone) 1", e1),
     *[participant(f"possible_product_{n}", "product", f"possible product {n}", e1) for n in [2, 3, 4, 5]]],
    [], [], ["Scheme 2 is a prospective selectivity map of possible products, not a reported batch experiment."],
    ["Generic R1/R2/X groups prevent unique structures; no experimental conditions or yields are assigned."]))

# Page 2: Table 1, Scheme 3 and Table 2.
for args in [
    (1, "DMF", q(16, "%"), "69:31"), (2, "DMA", q(21, "%"), "89:19"),
    (3, "DMSO", q(53, "%"), "83:17"), (4, "CH3NO2", "trace", None),
    (5, "THF", q(26, "%"), "85:15"), (6, "CH3CN", q(68, "%"), "90:10"),
    (7, "acetone", q(54, "%"), "83:17")]:
    records.append(table1_record(*args))
records.append(scheme3_failure("1f", "C(CO2Me)2", "n-C6H13"))
records.append(scheme3_failure("1g", "CH2", "C2H5"))
records.extend([
    table2_record(1, "[RhCl(PPh3)3]", "reflux", 0, "dash", 95),
    table2_record(2, "[RhCl(CO)(PPh3)2]", "reflux", 0, "dash", 71),
    table2_record(3, "[RhCl(COD)]2", "reflux", 52, "95:5"),
    table2_record(4, "[RhCl(CO)2]2", "reflux", 85, ">99:1"),
    standard_1a_record(),
])

# Page 3: Table 3 rows other than row 1 (merged above), Scheme 4, Table 4 and Scheme 5.
for args in [
    (2, "NTs", "CH3", "1b", "2b", 84, None, 1, "acetone", False),
    (3, "NTs", "i-C3H7", "1c", "2c", 77, None, 1, "acetone", False),
    (4, "NTs", "n-C5H11", "1d", "2d", 75, None, 1, "acetone", False),
    (5, "SO2", "C2H5", "1e", "2e", 76, None, 1, "acetone", False),
    (6, "C(CO2Me)2", "n-C6H13", "1f", "2f", 77, "reflux", 1, "acetone", False),
    (7, "CH2", "C2H5", "1g", "2g", 65, None, 1, "acetone", False),
    (8, "CH2", "i-C3H7", "1h", "2h", 72, None, 2, "acetone", False),
    (9, "CH2", "n-C4H9", "1i", "2i", 66, None, 1, "acetone", False),
    (10, "CH2", "Ph", "1j", "2j", 44, q(70, "°C"), 1, "DCE", True),
    (11, "CH2", "Ph", "1j", "2j", 66, q(70, "°C"), 1, "DCE", False),
]: records.append(table3_record(*args))
records.append(scheme4_record("acetone", "RT", 28, 5, "NMR", False))
records.append(scheme4_record("DCE", q(70, "°C"), 58, 0, "isolated", True))
records.extend([
    table4_record(1, "Ph", "nBu", "1l", 20, "2l", 74, "2l'", 8),
    table4_record(2, "p-O2NC6H4", "Bn", "1m", 60, "2m", 55, "2m'", 3, "NMR"),
    table4_record(3, "p-O2NC6H4", "nBu", "1n", 20, "2n", 77, "2n'", 0),
    table4_record(4, "p-O2NC6H4", "iPr", "1o", 20, "2o", 60, "2o'", 0),
])
e3 = [ev(3, "image"), ev(3, "text")]
records.append(record("scheme5_unsymmetrical_1p", "substrate_scope_entry", e3,
    [participant("substrate_1p", "reactant", "1p", e3, "unsymmetrical p-nitrophenyl/p-methoxyphenyl bis(allenylketone) 1p"),
     catalyst("rh_catalyst", "[RhCl(CO)2]2", e3), solvent("DCE", e3),
     participant("product_2p", "product", "2p", e3), participant("product_2p_prime", "product", "2p'", e3)],
    [{"step_id": "cyclization", "participant_ids": ["substrate_1p", "rh_catalyst", "solvent"],
      "conditions": [field("solvent", "DCE", e3), field("temperature", "RT", e3), field("time", q(20, "min"), e3)]}],
    [field("isolated_yield_2p", q(55, "%"), e3, ["product_2p"]), field("isolated_yield_2p_prime", q(7, "%"), e3, ["product_2p_prime"]), field("yield_measurement_basis", "isolated yield", e3)],
    ["The electron-donating p-methoxyphenyl allenyl ketone cyclizes, while the p-nitrophenyl side serves as Michael acceptor for major product 2p."],
    ["Supporting information was not provided or explicitly associated.", "Structures were not independently transcribed to SMILES."]))

# Page 4: two duration-specific isomerization controls and the proposed mechanism.
records.extend([scheme6_record(1), scheme6_record(12)])
e4 = [ev(4, "image"), ev(4, "text")]
records.append(record("scheme7_proposed_mechanism", "mechanism", e4,
    [participant("generic_substrate_1", "reactant", "generic substrate 1", e4),
     participant("intermediate_M1", "unspecified_agent", "M1", e4),
     participant("intermediate_M2a", "unspecified_agent", "M2a (Pd pathway)", e4),
     participant("intermediate_M2b", "unspecified_agent", "M2b (Rh pathway)", e4),
     participant("products_2_and_3", "product", "products 2 and 3", e4)],
    [], [], ["Scheme 7 is the authors' proposed oxymetallation/carbometallation/protonolysis mechanism, not a batch experiment."],
    ["Generic R1/R2/X and metal-ligand notation prevent unique structures; intermediates are mechanistic proposals."]))

raw_path = BASE / "raw_model" / "records_pages_0001_0005.json"
raw_path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

ids = lambda prefixes: [r["record_id"] for r in records if any(r["source_reaction_id"].startswith(p) for p in prefixes)]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "upper-right Equation (1)", "finding": "Pd(II)-catalyzed bisallenol bicyclization is explicitly prior work (reference 7); classified as a literature example, not a present-paper experiment.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
            {"region": "middle-left Scheme 1", "finding": "Pharmacologically active example structures only; no reaction arrow or present-paper experiment.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
            {"region": "lower-right Scheme 2", "finding": "Prospective map of possible products 2–5 and selectivity challenges; classified as a general scheme.", "evidence_ids": [ev(1, "image"), ev(1, "text")]},
        ], "record_ids": ids(["equation1_", "scheme2_"]), "unresolved": ["Generic R1/R2/X/LG structures are not uniquely specifiable; Equation (1) omits time, temperature and yield."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "upper-left Table 1 and footnotes", "finding": "Seven solvent-screening rows extracted separately with shared Pd catalyst, concentration, time, temperature/RT override, NMR yields, ratios and trace result.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            {"region": "middle-left Scheme 3", "finding": "Two distinct Pd-catalyzed substrate-scope attempts (1f and 1g) extracted as no-reaction results.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            {"region": "upper-right Table 2 and footnotes", "finding": "Five catalyst/temperature rows extracted separately; zero yields, recovered 1a, selectivity, NMR yield and isolated yield kept distinct. Entry 5 is merged with Table 3 entry 1 and the detailed page-4 procedure.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
            {"region": "lower columns Results and Discussion", "finding": "Narrative confirms Table 1/2 interpretations and begins Table 3 scope discussion; no additional independent batch beyond the linked rows.", "evidence_ids": [ev(2, "image"), ev(2, "text")]},
        ], "record_ids": ids(["table1_", "scheme3_", "table2_"]), "unresolved": ["Printed Table 1 entry 2 ratio is 89/19 and is preserved as printed despite summing to 108.", "No SI was supplied or associated."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 3 and footnotes", "finding": "Eleven scope rows inventoried; row 1 is the same standard 1a experiment as Table 2 entry 5/page-4 procedure, while rows 2–11 are separate records with reflux/time/DCE overrides.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            {"region": "upper-right Scheme 4", "finding": "Acetone/RT and DCE/70 °C conditions extracted as two experiments with product-specific 2k and 3k yields and measurement bases.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            {"region": "middle-right Table 4 and footnotes", "finding": "Four unsymmetrical-substrate rows extracted separately with time and product-specific yields; the 3% 2m' result is retained as NMR yield.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            {"region": "lower Scheme 5", "finding": "One 1p experiment extracted with two isolated product yields (2p 55%, 2p' 7%).", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
            {"region": "Figure 2", "finding": "ORTEP of 2o supports structure assignment discussion but is not an independent reaction experiment.", "evidence_ids": [ev(3, "image"), ev(3, "text")]},
        ], "record_ids": ids(["table2_entry5_", "table3_", "scheme4_", "table4_", "scheme5_"]), "unresolved": ["Table 3 entry 10 is marked [c] like entry 11, but prose describes the 44% result before introducing the new DCE conditions; preserved as a source inconsistency.", "Structures were not independently converted from variable-group drawings."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 6", "finding": "The 1 h and 12 h isomerization controls are represented as separate duration-specific experiments; both retain the 87:13 2a/3a ratio.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            {"region": "middle-left Scheme 7 and mechanism prose", "finding": "Proposed Pd/Rh mechanism classified as mechanism, not as a reported batch reaction.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
            {"region": "right-column Experimental Section", "finding": "Detailed 1a standard experiment merged into Table 2 entry 5/Table 3 entry 1 with exact masses, amounts, acetone volume, time, TLC endpoint, evaporation, chromatography, product mass and isolated yield.", "evidence_ids": [ev(4, "image"), ev(4, "text")]},
        ], "record_ids": ids(["table2_entry5_", "scheme6_", "scheme7_"]), "unresolved": ["Reaction atmosphere is absent; SI was not supplied; spectroscopy is characterization rather than a separate experiment and was not decomposed into reaction records."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "entire page: references 1–15 and publication metadata", "finding": "No new present-paper reaction arrow, table row or experimental procedure. References 9–10 describe prior literature only; references 11–12 are crystallographic data; reference 15 points to SI of reference 7 rather than supplying SI here.", "evidence_ids": [ev(5, "image"), ev(5, "text")]},
        ], "record_ids": [], "unresolved": ["The cited supporting information was not provided or explicitly associated, so referenced preparation details were not imported."]},
    ],
}
(BASE / "coverage" / "pages_0001_0005.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

tasks_path = BASE / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task.get("document_id") == DOC and 1 <= int(task["evidence_id"].split(":page")[1].split(":")[0]) <= 5:
        task["state"] = "attempted"
        task["reason"] = "Original page image and text inspected; records and coverage ledger generated for this bounded page range."
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "raw": str(raw_path), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
