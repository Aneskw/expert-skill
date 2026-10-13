import json
from pathlib import Path

DOC = "doc_7ae5e5fcbc06f350"
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

AUTO_SMILES = {
    "EtOH": "CCO", "ethanol": "CCO", "iPrOH": "CC(O)C", "PrOH": "CCCO",
    "DMF": "CN(C)C=O", "CH2Cl2": "ClCCl", "THF": "C1CCOC1",
    "MeCN": "CC#N", "toluene": "Cc1ccccc1", "Et3N": "CCN(CC)CC",
    "P(OEt)2Cl": "CCOP(=O)(Cl)OCC", "PCl(OEt)2": "CCOP(=O)(Cl)OCC",
    "phenylboronic acid": "OB(O)c1ccccc1", "PhB(OH)2": "OB(O)c1ccccc1",
    "K2CO3": "[K+].[K+].[O-]C([O-])=O",
    "CuBr2": "[Cu+2].[Br-].[Br-]", "CuCl2·2H2O": "O.O.[Cu+2].[Cl-].[Cl-]",
}


def evid(page):
    return [f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"]


def fact(value, ev):
    return {"value": value, "evidence_ids": list(ev) if value is not None else [],
            "verification": "unreviewed" if value is not None else "missing"}


def qty(number, unit, **extra):
    result = {"number": number, "unit": unit}
    result.update(extra)
    return result


def field(name, value, ev, targets=None):
    item = {"name": name, "fact": fact(value, ev)}
    if targets:
        item["target_entity_ids"] = list(targets)
    return item


def part(entity_id, role, label, ev, name=None, amounts=None, smiles=None):
    smiles = smiles or AUTO_SMILES.get(label)
    return {
        "entity_id": entity_id,
        "role": role,
        "label": fact(label, ev),
        "name": fact(name, ev) if name else fact(None, []),
        "smiles": fact(smiles, ev) if smiles else fact(None, []),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": amounts or [],
    }


def record(rid, kind, ev, participants=None, conditions=None, outcomes=None,
           notes=None, unresolved=None):
    participants = participants or []
    return {
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": rid,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": list(dict.fromkeys(ev)),
        "participants": participants,
        "steps": ([{"step_id": "step1",
                    "participant_ids": [p["entity_id"] for p in participants],
                    "conditions": conditions or []}] if participants else []),
        "outcomes": outcomes or [],
        "notes": [fact(x, ev) for x in (notes or [])],
        "review": {
            "method": "model",
            "reviewer": None,
            "checked_fields": [],
            "unresolved": unresolved or [
                "Molecular structures were not encoded as SMILES and require source-level chemical review.",
                "Supporting information is mentioned by the article but was not explicitly supplied or associated.",
            ],
        },
    }


records = []

# Page 1: generic and cited chemistry is classified, not promoted to paper experiments.
ev = evid(1)
records.append(record(
    "scheme1_prior_cux2_halocyclizations", "literature_example", ev,
    [part("generic_allene", "reactant", "functionalized allene (generic R groups)", ev),
     part("cux2", "reagent", "CuX2 (X = Br or Cl)", ev),
     part("generic_halocycle", "product", "halocyclized heterocycle(s), generic", ev)],
    notes=["Scheme 1 summarizes previously reported CuX2 halocyclizations of 2,3-allenoic acids/allenoates and 2,3-allenamides; it is not a new batch experiment in this paper."],
))
records.append(record(
    "scheme2_general_allenylphosphonate_preparation", "general_scheme", ev,
    [part("propargylic_alcohol", "reactant", "propargylic alcohol (generic R groups)", ev),
     part("pcloet2", "reagent", "PCl(OEt)2", ev),
     part("et3n", "reagent", "Et3N", ev),
     part("thf", "solvent", "THF", ev),
     part("allenylphosphonate_1", "product", "diethyl 1,2-allenylphosphonate 1 (generic)", ev)],
    [field("operation", "temperature program: 0 °C to reflux", ev), field("time", "overnight", ev)],
    notes=["Generic Claisen-rearrangement route shown in Scheme 2; individual starting-material batches are recorded from pages 5–6 when reported."],
))
records.append(record(
    "scheme2_previous_monoester_halocyclization", "literature_example", ev,
    [part("allenylphosphonate_generic", "reactant", "diethyl 1,2-allenylphosphonate (generic)", ev),
     part("naoh", "reagent", "NaOH", ev),
     part("monoester", "product", "monoester of 1,2-allenylphosphonic acid", ev),
     part("cux2_prev", "reagent", "CuX2", ev),
     part("halo_oxaphosphole_prev", "product", "4-halo-2,5-dihydro-1,2-oxaphosphole 2-oxide", ev)],
    notes=["The hydrolysis/halocyclization branch is explicitly marked previous work and is not treated as a new experiment."],
))
records.append(record(
    "scheme2_direct_halocyclization_this_work", "general_scheme", ev,
    [part("allenylphosphonate_1", "reactant", "diethyl 1,2-allenylphosphonate 1 (generic)", ev),
     part("cux2", "reagent", "CuX2", ev),
     part("halo_oxaphosphole", "product", "4-halo-2,5-dihydro-1,2-oxaphosphole 2-oxide (generic)", ev)],
    notes=["Scheme 2's direct arrow is the general transformation developed in this work; individual batches are represented by table rows and experimental paragraphs."],
))

# Page 2, Table 1: optimization of bromocyclization of 1a.
ev2 = evid(2)
table1 = [
    (1, 4.0, "DMF", 1, 82), (2, 4.0, "iPrOH", 2, 76),
    (3, 4.0, "PrOH", 2, 60), (4, 4.0, "EtOH", 2, 86),
    (5, 4.0, "CH2Cl2", 17, 6), (6, 4.0, "THF", 1, 94),
    (7, 4.0, "MeCN", 2, 64), (8, 4.0, "toluene", 1, 55),
    (9, 1.5, "EtOH", 13, 89), (10, 2.2, "EtOH", 1, 91),
    (11, 3.0, "EtOH", 1, 86),
]
for entry, equiv, solvent, hours, yld in table1:
    rev = ev2 + (evid(6) if entry == 10 else [])
    participants = [
        part("substrate_1a", "reactant", "1a", rev,
             "diethyl (2-methylocta-2,3-dien-4-yl)phosphonate",
             [field("amount", qty(0.3, "mmol"), rev)]),
        part("cubr2", "reagent", "CuBr2", rev,
             amounts=[field("equivalents", qty(equiv, "equiv"), rev)]),
        part("solvent", "solvent", solvent, rev,
             amounts=[field("volume", qty(2, "mL"), rev)]),
        part("product_2a", "product", "2a", rev,
             "4-bromo-3-butyl-5,5-dimethyl-2-ethoxy-2,5-dihydro-1,2-oxaphosphole 2-oxide"),
    ]
    notes = []
    if entry == 6:
        notes.append("Product 2a was contaminated with inseparable impurities and had approximately 90% purity.")
    if entry == 10:
        participants[0]["amounts"].append(field("mass", qty(78.1, "mg"), rev))
        participants[1]["amounts"].extend([field("amount", qty(0.66, "mmol"), rev),
                                             field("mass", qty(147.4, "mg"), rev)])
        participants[3]["amounts"].append(field("isolated_product_mass", qty(84.9, "mg"), rev))
        notes.append("This row is the same 1a→2a standard batch shown in Table 2 entry 1 and detailed on page 6; evidence is merged rather than duplicated.")
        notes.append("Page 6 reports TLC monitoring and silica-gel chromatography with petroleum ether/ethyl acetate 5:1.")
    row_outcomes = [field("isolated_yield", qty(yld, "%"), rev, ["product_2a"]),
                    field("yield_measurement_basis", "isolated", rev, ["product_2a"])]
    if entry == 6:
        row_outcomes.append(field("product_purity", qty(90, "%", qualifier="approx", raw_text="ca. 90%"), rev, ["product_2a"]))
    records.append(record(
        f"table1_entry{entry}", "optimization_entry", rev, participants,
        [field("temperature", qty(60, "°C"), rev), field("time", qty(hours, "h"), rev)],
        row_outcomes, notes=notes,
    ))

# Page 2, Table 2: substrate scope. Entry 1 is already Table 1 entry 10.
table2 = [
    (2, "1b", "2b", "Ph", "Me", "Me", 3, 69),
    (3, "1c", "2c", "allyl", "Me", "Me", 1, 75),
    (4, "1d", "2d", "2-methylallyl", "Me", "Me", 1, 77),
    (5, "1e", "2e", "2-chloroallyl", "Me", "Me", 1, 79),
    (6, "1f", "2f", "nBu", "-(CH2)5-", "-(CH2)5-", 1, 88),
    (7, "1g", "2g", "nBu", "-(CH2)4-", "-(CH2)4-", 1, 91),
    (8, "1h", "2h", "Ph", "-(CH2)5-", "-(CH2)5-", 3, 85),
    (9, "1i", "2i", "Ph", "-(CH2)4-", "-(CH2)4-", 3, 72),
    (10, "1j", "2j", "Ph", "Et", "Et", 3, 81),
    (11, "1k", "2k", "nBu", "nPr", "nPr", 5, 85),
]
for entry, sub, prod, r1, r2, r3, hours, yld in table2:
    rev = ev2 + (evid(6) if entry == 2 else [])
    ps = [
        part("substrate", "reactant", sub, rev, amounts=[field("amount", qty(0.3, "mmol"), rev)]),
        part("cubr2", "reagent", "CuBr2", rev, amounts=[field("amount", qty(0.66, "mmol"), rev)]),
        part("ethanol", "solvent", "EtOH", rev, amounts=[field("volume", qty(2, "mL"), rev)]),
        part("product", "product", prod, rev),
    ]
    notes = [f"Table substituents: R1={r1}; R2={r2}; R3={r3}."]
    if entry == 2:
        ps[0]["amounts"].append(field("mass", qty(84.1, "mg"), rev))
        ps[1]["amounts"].append(field("mass", qty(147.9, "mg"), rev))
        ps[3]["amounts"].append(field("isolated_product_mass", qty(68.8, "mg"), rev))
        notes.append("Page 6 gives the matching detailed 1b→2b batch; evidence is merged with Table 2 entry 2.")
    records.append(record(
        f"table2_entry{entry}", "substrate_scope_entry", rev, ps,
        [field("temperature", qty(60, "°C"), rev), field("time", qty(hours, "h"), rev)],
        [field("isolated_yield", qty(yld, "%"), rev, ["product"]),
         field("yield_measurement_basis", "isolated", rev, ["product"])], notes=notes,
    ))

# Page 2, Table 3: chlorocyclization optimization.
table3 = [
    (1, 4.0, "CH2Cl2", 4, 70, 83), (2, 4.0, "EtOH", 8, 70, 84),
    (3, 4.0, "toluene", 2, 70, 86), (4, 4.0, "MeCN", 1, 70, 76),
    (5, 4.0, "THF", 4, 70, 81), (6, 3.0, "toluene", 5, 70, 87),
    (7, 2.2, "toluene", 5, 70, 84), (8, 3.0, "toluene", 4, 80, 78),
    (9, 3.0, "toluene", 7, 60, 84),
]
for entry, equiv, solvent, hours, temp, yld in table3:
    ps = [part("substrate_1a", "reactant", "1a", ev2, amounts=[field("amount", qty(0.3, "mmol"), ev2)]),
          part("cucl2_2h2o", "reagent", "CuCl2·2H2O", ev2, amounts=[field("equivalents", qty(equiv, "equiv"), ev2)]),
          part("solvent", "solvent", solvent, ev2, amounts=[field("volume", qty(2, "mL"), ev2)]),
          part("product_3a", "product", "3a", ev2)]
    records.append(record(
        f"table3_entry{entry}", "optimization_entry", ev2, ps,
        [field("temperature", qty(temp, "°C"), ev2), field("time", qty(hours, "h"), ev2)],
        [field("isolated_yield", qty(yld, "%"), ev2, ["product_3a"]),
         field("yield_measurement_basis", "isolated", ev2, ["product_3a"])],
    ))

# Page 3, Table 4: chlorocyclization scope.
ev3 = evid(3)
table4 = [
    (1, "1a", "3a", "nBu", "Me", "Me", 5, 85),
    (2, "1b", "3b", "Ph", "Me", "Me", 24, 97),
    (3, "1c", "3c", "allyl", "Me", "Me", 22.5, 68),
    (4, "1d", "3d", "2-methylallyl", "Me", "Me", 22.5, 87),
    (5, "1f", "3e", "nBu", "-(CH2)5-", "-(CH2)5-", 5, 82),
    (6, "1g", "3f", "nBu", "-(CH2)4-", "-(CH2)4-", 5, 72),
    (7, "1h", "3g", "Ph", "-(CH2)5-", "-(CH2)5-", 7, 90),
    (8, "1i", "3h", "Ph", "-(CH2)4-", "-(CH2)4-", 7, 83),
]
for entry, sub, prod, r1, r2, r3, hours, yld in table4:
    ps = [part("substrate", "reactant", sub, ev3, amounts=[field("amount", qty(0.3, "mmol"), ev3)]),
          part("cucl2_2h2o", "reagent", "CuCl2·2H2O", ev3, amounts=[field("amount", qty(0.9, "mmol"), ev3)]),
          part("toluene", "solvent", "toluene", ev3, amounts=[field("volume", qty(2, "mL"), ev3)]),
          part("product", "product", prod, ev3)]
    records.append(record(
        f"table4_entry{entry}", "substrate_scope_entry", ev3, ps,
        [field("temperature", qty(70, "°C"), ev3), field("time", qty(hours, "h"), ev3)],
        [field("isolated_yield", qty(yld, "%"), ev3, ["product"]),
         field("yield_measurement_basis", "isolated", ev3, ["product"])],
        notes=[f"Table substituents: R1={r1}; R2={r2}; R3={r3}."],
    ))

# Page 3, Scheme 3: three diastereomer-resolved batches.
scheme3 = [
    ("1l", 12, [("cis-3i", 45), ("trans-3i", 49)]),
    ("1m", 19, [("cis-3j", 41), ("trans-3j", 47)]),
    ("1n", 28, [("cis-3k", 40), ("trans-3k", 42)]),
]
for sub, hours, products in scheme3:
    ps = [part("substrate", "reactant", sub, ev3),
          part("cucl2_2h2o", "reagent", "CuCl2·2H2O", ev3, amounts=[field("equivalents", qty(4.0, "equiv"), ev3)]),
          part("toluene", "solvent", "toluene", ev3)]
    outs = []
    for index, (label, yld) in enumerate(products, 1):
        eid = f"product{index}"
        ps.append(part(eid, "product", label, ev3))
        outs.append(field(f"reported_yield_{label}", qty(yld, "%"), ev3, [eid]))
    records.append(record(
        f"scheme3_{sub}_diastereomers", "reported_experiment", ev3, ps,
        [field("temperature", qty(70, "°C"), ev3), field("time", qty(hours, "h"), ev3)], outs,
        notes=["cis/trans refer to the orientation of P=O and the substituent at the 5-position."],
    ))

# Page 3 / page 6, Scheme 4 starting-material preparation.
ev36 = ev3 + evid(6)
ps = [
    part("alcohol", "reactant", "(S)-1-phenylpenta-1-yn-3-ol", ev36,
         amounts=[field("mass", qty(801.1, "mg"), ev36), field("amount", qty(5, "mmol"), ev36),
                  field("input_ee", qty(99, "%", qualifier="gt", raw_text=">99%"), ev3)]),
    part("pcloet2", "reagent", "P(OEt)2Cl", ev36,
         amounts=[field("mass", qty(1174.2, "mg"), evid(6)), field("amount", qty(7.5, "mmol"), evid(6))]),
    part("et3n", "reagent", "Et3N", ev36,
         amounts=[field("mass", qty(758.9, "mg"), evid(6)), field("amount", qty(7.5, "mmol"), evid(6))]),
    part("ch2cl2", "solvent", "CH2Cl2", ev3),
    part("product", "product", "(Sa)-(−)-1n", ev36,
         "diethyl (1-phenylpenta-1,2-dien-1-yl)phosphonate",
         [field("isolated_product_mass", qty(580.6, "mg"), evid(6))]),
]
records.append(record(
    "scheme4_prepare_sa_1n", "reported_experiment", ev36, ps, outcomes=[
        field("isolated_yield", qty(41, "%"), evid(6), ["product"]),
        field("yield_measurement_basis", "isolated", evid(6), ["product"]),
        field("product_ee_scheme4", qty(96, "%"), ev3, ["product"]),
        field("product_ee_experimental", qty(97, "%"), evid(6), ["product"]),
    ], notes=["Scheme 4 labels the product ee as 96%, while the page-6 experimental paragraph reports 97%; both source statements are retained as an unresolved discrepancy."],
    unresolved=["Scheme 4 gives 96% ee for (Sa)-(−)-1n, whereas the page-6 experimental paragraph gives 97% ee.",
                "Detailed temperature, duration, workup and purification are not restated for this abbreviated preparation.",
                "Molecular structures were not encoded as SMILES and require source-level chemical review.",
                "Supporting information was not explicitly supplied or associated."],
))
ps = [part("substrate", "reactant", "(Sa)-(−)-1n", ev3, amounts=[field("input_ee", qty(96, "%"), ev3)]),
      part("cucl2_2h2o", "reagent", "CuCl2·2H2O", ev3, amounts=[field("equivalents", qty(4.0, "equiv"), ev3)]),
      part("toluene", "solvent", "toluene", ev3),
      part("ss_3k", "product", "(S,S)-3k", ev3),
      part("sr_3k", "product", "(S,R)-3k", ev3)]
records.append(record(
    "scheme4_chiral_1n_chlorocyclization", "reported_experiment", ev3, ps,
    [field("temperature", qty(70, "°C"), ev3), field("time", qty(28, "h"), ev3)],
    [field("reported_yield_ss_3k", qty(44, "%"), ev3, ["ss_3k"]),
     field("product_ee_ss_3k", qty(95, "%"), ev3, ["ss_3k"]),
     field("reported_yield_sr_3k", qty(45, "%"), ev3, ["sr_3k"]),
     field("product_ee_sr_3k", qty(94, "%"), ev3, ["sr_3k"])],
))

# Page 4, Scheme 5: optically active chlorocyclizations.
ev4 = evid(4)
scheme5 = [
    ("1l", 12, [("(2S,5S)-3i", 44, 98), ("(2R,5S)-3i", 47, 98)]),
    ("1m", 19, [("(2S,5S)-3j", 43, 98), ("(2R,5S)-3j", 50, 98)]),
]
for sub, hours, products in scheme5:
    ps = [part("substrate", "reactant", f"(Sa)-(+)-{sub}", ev4, amounts=[field("input_ee", qty(99, "%", qualifier="gt", raw_text=">99%"), ev4)]),
          part("cucl2_2h2o", "reagent", "CuCl2·2H2O", ev4, amounts=[field("equivalents", qty(4.0, "equiv"), ev4)]),
          part("toluene", "solvent", "toluene", ev4)]
    outs = []
    for i, (label, yld, ee) in enumerate(products, 1):
        eid = f"product{i}"; ps.append(part(eid, "product", label, ev4))
        outs.extend([field(f"reported_yield_{i}", qty(yld, "%"), ev4, [eid]),
                     field(f"product_ee_{i}", qty(ee, "%"), ev4, [eid])])
    records.append(record(f"scheme5_chiral_{sub}_chlorocyclization", "reported_experiment", ev4, ps,
                          [field("temperature", qty(70, "°C"), ev4), field("time", qty(hours, "h"), ev4)], outs))

# Page 4, Scheme 6 mechanism.
records.append(record(
    "scheme6_proposed_halocyclization_mechanism", "mechanism", ev4,
    [part("generic_allenylphosphonate", "reactant", "allenylphosphonate 2 (generic)", ev4),
     part("cux2", "reagent", "CuX2", ev4),
     part("generic_product", "product", "halocyclized product 3/4 (generic)", ev4)],
    notes=["Proposed coordination, anti-oxy-metalation, Arbuzov-type dealkylation and C–X bond formation sequence; intermediates M1–M4A/M4B are mechanistic, not independent reported experiments."],
))

# Page 4, Table 5: Suzuki scope.
table5 = [(1, "3a", "4a", "nBu", 5, 75), (2, "3b", "4b", "Ph", 17, 78),
          (3, "3c", "4c", "allyl", 10.5, 55)]
for entry, sub, prod, r1, hours, yld in table5:
    ps = [part("substrate", "reactant", sub, ev4, amounts=[field("amount", qty(0.3, "mmol"), ev4)]),
          part("phenylboronic_acid", "reactant", "phenylboronic acid", ev4, amounts=[field("amount", qty(0.75, "mmol"), ev4)]),
          part("pd_complex", "catalyst", "[PdCl2(LB-Phos)2]", ev4, amounts=[field("amount", qty(0.015, "mmol"), ev4)]),
          part("k2co3", "reagent", "K2CO3", ev4, amounts=[field("amount", qty(1.05, "mmol"), ev4)]),
          part("toluene", "solvent", "toluene", ev4, amounts=[field("volume", qty(2, "mL"), ev4)]),
          part("product", "product", prod, ev4)]
    records.append(record(f"table5_entry{entry}", "substrate_scope_entry", ev4, ps,
                          [field("temperature", "reflux", ev4), field("time", qty(hours, "h"), ev4)],
                          [field("isolated_yield", qty(yld, "%"), ev4, ["product"]),
                           field("yield_measurement_basis", "isolated", ev4, ["product"])],
                          notes=[f"Table substituent R1={r1}." ]))

# Page 4, Scheme 7: diastereomer-specific Suzuki batches.
scheme7 = [
    ("cis-3i", "cis-4d", 9, 86), ("trans-3i", "trans-4d", 9, 84),
    ("cis-3j", "cis-4e", 8, 89), ("cis-3k", "cis-4f", 6, 91),
]
for sub, prod, hours, yld in scheme7:
    ps = [part("substrate", "reactant", sub, ev4),
          part("phenylboronic_acid", "reactant", "PhB(OH)2", ev4, amounts=[field("equivalents", qty(2.5, "equiv"), ev4)]),
          part("pd_complex", "catalyst", "PdCl2(LB-Phos)2", ev4, amounts=[field("catalyst_loading", qty(5, "mol%"), ev4)]),
          part("k2co3", "reagent", "K2CO3", ev4, amounts=[field("equivalents", qty(3.5, "equiv"), ev4)]),
          part("toluene", "solvent", "toluene", ev4),
          part("product", "product", prod, ev4)]
    records.append(record(f"scheme7_{sub}_to_{prod}", "reported_experiment", ev4, ps,
                          [field("temperature", "reflux", ev4), field("time", qty(hours, "h"), ev4)],
                          [field("reported_yield", qty(yld, "%"), ev4, ["product"])]))

# Page 4, Scheme 8: optically active Suzuki batches.
scheme8 = [("(2S,5S)-3i", "(2S,5S)-4d", 9, 94), ("(2S,5S)-3j", "(2S,5S)-4e", 8, 90)]
for sub, prod, hours, yld in scheme8:
    ps = [part("substrate", "reactant", sub, ev4, amounts=[field("input_ee", qty(98, "%"), ev4)]),
          part("phenylboronic_acid", "reactant", "PhB(OH)2", ev4, amounts=[field("equivalents", qty(2.5, "equiv"), ev4)]),
          part("pd_complex", "catalyst", "PdCl2(LB-Phos)2", ev4, amounts=[field("catalyst_loading", qty(5, "mol%"), ev4)]),
          part("k2co3", "reagent", "K2CO3", ev4, amounts=[field("equivalents", qty(3.5, "equiv"), ev4)]),
          part("toluene", "solvent", "toluene", ev4),
          part("product", "product", prod, ev4)]
    records.append(record(f"scheme8_{sub}_to_{prod}", "reported_experiment", ev4, ps,
                          [field("temperature", "reflux", ev4), field("time", qty(hours, "h"), ev4)],
                          [field("reported_yield", qty(yld, "%"), ev4, ["product"]),
                           field("product_ee", qty(98, "%"), ev4, ["product"]),
                           ]))

# Pages 5–6: preparations of starting materials. Abbreviated examples retain missing operations.
ev5, ev6 = evid(5), evid(6)

def prep_starting(rid, ev, alcohol, alcohol_mass, alcohol_mmol, pcl_mass, pcl_mmol,
                  et3n_mass, et3n_mmol, product, product_mass, yld, extra_conditions=None,
                  extra_parts=None, notes=None, unresolved=None):
    ps = [part("alcohol", "reactant", alcohol, ev,
               amounts=[field("mass", qty(alcohol_mass, "mg"), ev),
                        field("amount", qty(alcohol_mmol, "mmol"), ev)]),
          part("pcloet2", "reagent", "P(OEt)2Cl", ev,
               amounts=[field("mass", qty(pcl_mass, "mg"), ev), field("amount", qty(pcl_mmol, "mmol"), ev)]),
          part("et3n", "reagent", "Et3N", ev,
               amounts=[field("mass", qty(et3n_mass, "mg"), ev), field("amount", qty(et3n_mmol, "mmol"), ev)]),
          part("product", "product", product, ev,
               amounts=[field("isolated_product_mass", qty(product_mass, "mg"), ev)])]
    if extra_parts: ps.extend(extra_parts)
    records.append(record(rid, "reported_experiment", ev, ps, extra_conditions or [],
                          [field("isolated_yield", qty(yld, "%"), ev, ["product"]),
                           field("yield_measurement_basis", "isolated", ev, ["product"])],
                          notes=notes, unresolved=unresolved))

# 1e typical procedure: source masses expressed in g for alcohol/product; keep exact original units.
ps = [part("alcohol", "reactant", "6-chloro-2-methylhepta-6-en-3-yn-2-ol", ev5,
           amounts=[field("mass", qty(1.2645, "g"), ev5), field("amount", qty(8, "mmol"), ev5)]),
      part("et3n", "reagent", "Et3N", ev5, amounts=[field("mass", qty(1295.2, "mg"), ev5), field("amount", qty(12.8, "mmol"), ev5)]),
      part("pcloet2", "reagent", "P(OEt)2Cl", ev5, amounts=[field("mass", qty(2003.8, "mg"), ev5), field("amount", qty(12.8, "mmol"), ev5)]),
      part("ch2cl2", "solvent", "CH2Cl2", ev5, amounts=[field("volume", qty(24, "mL", raw_text="15 mL + 9 mL"), ev5)]),
      part("product", "product", "1e", ev5, "diethyl (6-chloro-2-methylhepta-2,3,6-trien-4-yl)phosphonate",
           [field("isolated_product_mass", qty(1.1147, "g"), ev5)])]
records.append(record(
    "experimental_prepare_1e", "reported_experiment", ev5, ps,
    [field("initial_temperature", qty(-78, "°C"), ev5), field("warm_to", "room temperature", ev5),
     field("time_at_room_temperature", "overnight", ev5),
     field("operation", "dropwise addition of P(OEt)2Cl solution", ev5),
     field("workup", "evaporate; add H2O and ethyl acetate; separate; wash with brine; dry over anhydrous Na2SO4; filter and evaporate", ev5),
     field("purification", "silica-gel chromatography, petroleum ether/ethyl acetate 5:1", ev5)],
    [field("isolated_yield", qty(50, "%"), ev5, ["product"]),
     field("yield_measurement_basis", "isolated", ev5, ["product"])],
    notes=["TLC eluent petroleum ether/ethyl acetate 3:1 was used to monitor conversion."],
))

prep_specs = [
    ("experimental_prepare_1h", ev5, "1,1-pentamethylene-3-phenylprop-2-yn-1-ol", 1001.5, 5, 1174.2, 7.5, 758.9, 7.5, "1h", 1369.6, 85),
    ("experimental_prepare_1i", ev5, "1,1-tetramethylene-3-phenylprop-2-yn-1-ol", 931.3, 5, 1174.1, 7.5, 708.3, 7, "1i", 714.4, 47),
    ("experimental_prepare_1j", ev5, "3-ethyl-1-phenylpenta-1-yn-3-ol", 941.0, 5, 1174.1, 7.5, 708.3, 7, "1j", 854.1, 55),
    ("experimental_prepare_1k", ev5, "4-propyldeca-5-yn-4-ol", 1980.0, 10, 2348.2, 15, 1416.8, 14, "1k", 1610.9, 51),
    ("experimental_prepare_1l", ev5 + ev6, "non-4-yn-3-ol", 1822.9, 13, 3256.2, 20.8, 2104.8, 20.8, "1l", 1176.6, 55),
    ("experimental_prepare_1m", ev6, "dec-5-yn-4-ol", 2743.0, 10, 2348.2, 15, 1416.7, 14, "1m", 1690.5, 62),
    ("experimental_prepare_1n", ev6, "1-phenylpenta-1-yn-3-ol", 1602.3, 10, 2348.2, 15, 1416.7, 14, "1n", 1910.9, 68),
]
for spec in prep_specs:
    prep_starting(*spec, notes=["Abbreviated experimental paragraph reports charged materials and isolated product; operational details are not restated."],
                  unresolved=["Temperature, duration, solvent, workup and purification are not restated in this abbreviated paragraph.",
                              "Molecular structures were not encoded as SMILES and require source-level chemical review.",
                              "Supporting information was not explicitly supplied or associated."])

# Page 6: enantioenriched 1l and 1m preparations (1n is merged with Scheme 4 above).
chiral_preps = [
    ("experimental_prepare_sa_1l", "(S)-non-4-yn-3-ol", 1402.5, 10, 2348.2, 15, 1517.8, 15, "(Sa)-(+)-1l", 1133.1, 44, 99, "gt"),
    ("experimental_prepare_sa_1m", "(S)-dec-5-yn-4-ol", 925.5, 6, 1408.9, 9, 911.0, 9, "(Sa)-(+)-1m", 1028.3, 62, 99, "gt"),
]
for rid, alcohol, amass, ammol, pmass, pmmol, emass, emmol, prod, prodmass, yld, ee, qualifier in chiral_preps:
    before = len(records)
    prep_starting(rid, ev6, alcohol, amass, ammol, pmass, pmmol, emass, emmol, prod, prodmass, yld,
                  notes=["Abbreviated experimental paragraph reports charged materials, isolated product and chiral HPLC result; operational details are not restated."],
                  unresolved=["Temperature, duration, solvent, workup and purification are not restated in this abbreviated paragraph.",
                              "Absolute structure and SMILES require source-level chemical review.",
                              "Supporting information was not explicitly supplied or associated."])
    records[before]["outcomes"].append(field("product_ee", qty(ee, "%", qualifier=qualifier, raw_text=">99%"), ev6, ["product"]))

# Write raw model output.
(OUT / "records_pages_0001_0006.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")

# Coverage ledger: exactly pages 1–6, with image evidence for every region.
ids = lambda *suffixes: [f"{DOC}:{s}" for s in suffixes]
coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {"page": 1, "state": "attempted", "regions": [
            {"region": "full page title, abstract, introduction and right-column Scheme 1",
             "finding": "Scheme 1 and cited prose summarize prior CuX2 halocyclizations; recorded as literature context, not new experiments.",
             "evidence_ids": evid(1)},
            {"region": "lower-right Scheme 2 and opening Results and Discussion",
             "finding": "Generic allenylphosphonate preparation, previous hydrolysis route, and this-work direct halocyclization were classified separately; no row-level batch is claimed here.",
             "evidence_ids": evid(1)}],
         "record_ids": ids("scheme1_prior_cux2_halocyclizations", "scheme2_general_allenylphosphonate_preparation", "scheme2_previous_monoester_halocyclization", "scheme2_direct_halocyclization_this_work"),
         "unresolved": ["Generic R-group structures are not encoded as complete molecules.", "The article mentions SI availability, but no SI file was explicitly associated."]},
        {"page": 2, "state": "attempted", "regions": [
            {"region": "left column Table 1 and surrounding optimization prose",
             "finding": "All 11 CuBr2 optimization rows extracted independently; the THF impurity/purity footnote is retained.",
             "evidence_ids": evid(2)},
            {"region": "upper-right Table 2 and footnotes",
             "finding": "All 11 scope rows accounted for; entry 1 is merged with identical Table 1 entry 10 and page-6 detailed 2a batch, while entries 2–11 remain independent.",
             "evidence_ids": evid(2)},
            {"region": "middle/lower-right Table 3 and adjacent prose",
             "finding": "All 9 CuCl2·2H2O optimization rows extracted with row-specific loading, solvent, time, temperature and isolated yield.",
             "evidence_ids": evid(2)}],
         "record_ids": ids(*[f"table1_entry{i}" for i in range(1,12)], *[f"table2_entry{i}" for i in range(2,12)], *[f"table3_entry{i}" for i in range(1,10)]),
         "unresolved": ["Table drawings were not converted to verified SMILES.", "Table 2 entry 1 has no duplicate record because it is the same stated 1a→2a batch as Table 1 entry 10."]},
        {"page": 3, "state": "attempted", "regions": [
            {"region": "upper-left Table 4 and footnotes",
             "finding": "All 8 chlorocyclization scope rows extracted with shared conditions and row-specific times/yields.",
             "evidence_ids": evid(3)},
            {"region": "left-column Scheme 3",
             "finding": "Three separate 1l/1m/1n chlorocyclizations extracted; cis and trans product yields remain product-specific outcomes.",
             "evidence_ids": evid(3)},
            {"region": "upper/middle-right Scheme 4 and ORTEP figures",
             "finding": "Optically active 1n preparation and its chlorocyclization extracted as successive experiments; ORTEP figures support configuration discussion but are not experiments.",
             "evidence_ids": evid(3)},
            {"region": "lower-right mechanism discussion continuing to Scheme 6",
             "finding": "Mechanistic prose was inspected and linked to the Scheme 6 mechanism record on page 4, not split into batch experiments.",
             "evidence_ids": evid(3)}],
         "record_ids": ids(*[f"table4_entry{i}" for i in range(1,9)], "scheme3_1l_diastereomers", "scheme3_1m_diastereomers", "scheme3_1n_diastereomers", "scheme4_prepare_sa_1n", "scheme4_chiral_1n_chlorocyclization", "scheme6_proposed_halocyclization_mechanism"),
         "unresolved": ["Scheme 4 gives 96% ee for (Sa)-(−)-1n, whereas the page-6 experimental paragraph gives 97% ee.", "Stereochemical structures remain unverified machine interpretations."]},
        {"page": 4, "state": "attempted", "regions": [
            {"region": "upper-left Scheme 5",
             "finding": "Two optically active chlorocyclization arrows extracted with product-specific yields and ee values.",
             "evidence_ids": evid(4)},
            {"region": "middle-left Scheme 6",
             "finding": "Proposed M1–M4A/M4B sequence classified as one mechanism record; intermediates are not reported experiments.",
             "evidence_ids": evid(4)},
            {"region": "lower-left Table 5 and footnotes",
             "finding": "Three Suzuki scope rows extracted with all shared reagent quantities and isolated yields.",
             "evidence_ids": evid(4)},
            {"region": "middle-right Scheme 7",
             "finding": "Four diastereomer-specific Suzuki arrows extracted independently.",
             "evidence_ids": evid(4)},
            {"region": "lower-right Scheme 8",
             "finding": "Two enantioenriched Suzuki arrows extracted with input/product ee and isolated yields.",
             "evidence_ids": evid(4)}],
         "record_ids": ids("scheme5_chiral_1l_chlorocyclization", "scheme5_chiral_1m_chlorocyclization", "scheme6_proposed_halocyclization_mechanism", *[f"table5_entry{i}" for i in range(1,4)], "scheme7_cis-3i_to_cis-4d", "scheme7_trans-3i_to_trans-4d", "scheme7_cis-3j_to_cis-4e", "scheme7_cis-3k_to_cis-4f", "scheme8_(2S,5S)-3i_to_(2S,5S)-4d", "scheme8_(2S,5S)-3j_to_(2S,5S)-4e"),
         "unresolved": ["Reflux is preserved qualitatively; no numerical boiling temperature was inferred.", "LB-Phos/catalyst structures remain unverified."]},
        {"page": 5, "state": "attempted", "regions": [
            {"region": "left column Experimental Section and typical preparation of 1e",
             "finding": "Detailed 1e batch extracted with charges, temperature program, monitoring, workup, purification, mass and isolated yield.",
             "evidence_ids": evid(5)},
            {"region": "lower-left through right column preparations of 1h–1k",
             "finding": "Four abbreviated starting-material batches extracted separately with explicit charged quantities, product masses and yields.",
             "evidence_ids": evid(5)},
            {"region": "lower-right beginning of preparation of 1l",
             "finding": "Cross-page 1l preparation linked to its completion on page 6 as one record.",
             "evidence_ids": evid(5)}],
         "record_ids": ids("experimental_prepare_1e", "experimental_prepare_1h", "experimental_prepare_1i", "experimental_prepare_1j", "experimental_prepare_1k", "experimental_prepare_1l"),
         "unresolved": ["Abbreviated 1h–1l paragraphs do not restate temperature, solvent, duration, workup or purification.", "Analytical characterization was not expanded into reaction conditions."]},
        {"page": 6, "state": "attempted", "regions": [
            {"region": "upper-left completion of 1l and preparations of 1m/1n",
             "finding": "1l completion merged across pages; 1m and 1n batches extracted separately.",
             "evidence_ids": evid(6)},
            {"region": "lower-left and upper-right optically active 1l/1m/1n preparations",
             "finding": "Enantioenriched 1l and 1m batches extracted; (Sa)-1n is merged with Scheme 4 and the 96/97% ee discrepancy is retained.",
             "evidence_ids": evid(6)},
            {"region": "right-column detailed bromocyclizations to 2a and 2b",
             "finding": "Detailed 2a and 2b batches were merged into Table 1 entry 10 and Table 2 entry 2 respectively, adding exact masses and 2a operations without duplicate records.",
             "evidence_ids": evid(6)}],
         "record_ids": ids("experimental_prepare_1l", "experimental_prepare_1m", "experimental_prepare_1n", "experimental_prepare_sa_1l", "experimental_prepare_sa_1m", "scheme4_prepare_sa_1n", "table1_entry10", "table2_entry2"),
         "unresolved": ["The 2b paragraph does not restate reaction time or workup; Table 2 supplies its 3 h time.", "Detailed operations for abbreviated chiral starting-material preparations are missing.", "Page 6 ends after 2b; later products were not claimed as covered."]},
    ],
}
(ROOT / "coverage").mkdir(parents=True, exist_ok=True)
(ROOT / "coverage" / "pages_0001_0006.json").write_text(json.dumps(coverage, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
