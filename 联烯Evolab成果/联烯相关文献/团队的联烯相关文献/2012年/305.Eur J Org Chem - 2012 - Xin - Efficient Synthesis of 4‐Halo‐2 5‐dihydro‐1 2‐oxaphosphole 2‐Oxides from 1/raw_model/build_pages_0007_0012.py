import copy
import json
from pathlib import Path


DOC = "doc_7ae5e5fcbc06f350"
ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
DATASET = json.loads((ROOT / "dataset.json").read_text())
EXISTING = {r["source_reaction_id"]: r for r in DATASET["experiments"]}


def evidence(*pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, ev):
    return {
        "value": value,
        "evidence_ids": list(ev) if value is not None else [],
        "verification": "unreviewed" if value is not None else "missing",
    }


def quantity(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def field(name, value, ev, targets=None):
    result = {"name": name, "fact": fact(value, ev)}
    if targets:
        result["target_entity_ids"] = list(targets)
    return result


def record(rid, *pages):
    item = copy.deepcopy(EXISTING[rid])
    item["evidence_ids"] = list(dict.fromkeys(item["evidence_ids"] + evidence(*pages)))
    return item


def participant(item, entity_id):
    return next(p for p in item["participants"] if p["entity_id"] == entity_id)


def add_amount(item, entity_id, name, value, ev):
    amounts = participant(item, entity_id)["amounts"]
    for existing in amounts:
        if existing["name"] == name and existing["fact"]["value"] == value:
            existing["fact"]["evidence_ids"] = list(
                dict.fromkeys(existing["fact"]["evidence_ids"] + list(ev))
            )
            return
    amounts.append(field(name, value, ev))


def set_name(item, entity_id, name, ev):
    participant(item, entity_id)["name"] = fact(name, ev)


def set_smiles_candidate(item, entity_id, smiles, ev):
    p = participant(item, entity_id)
    p["smiles"] = fact(smiles, ev)
    p["smiles_parseable"] = None
    p["structure_verified"] = False


def add_condition(item, name, value, ev):
    item["steps"][0]["conditions"].append(field(name, value, ev))


def add_outcome(item, name, value, ev, targets):
    item["outcomes"].append(field(name, value, ev, targets))


def add_note(item, text, ev):
    item["notes"].append(fact(text, ev))


def add_unresolved(item, text):
    if text not in item["review"]["unresolved"]:
        item["review"]["unresolved"].append(text)


records = []


# Page 7 (and the page-8 continuation of 2k): detailed bromocyclization products.
bromo = [
    (3, "1c", 73.3, 147.5, "2c", 66.5,
     "3-allyl-4-bromo-2-ethoxy-2,5-dihydro-5,5-dimethyl-1,2-oxaphosphole 2-oxide", (7,)),
    (4, "1d", 77.5, 147.4, "2d", 70.9,
     "4-bromo-2-ethoxy-2,5-dihydro-5,5-dimethyl-3-(2′-methylallyl)-1,2-oxaphosphole 2-oxide", (7,)),
    (5, "1e", 83.4, 147.3, "2e", 78.2,
     "4-bromo-3-(2′-chloroallyl)-2-ethoxy-2,5-dihydro-5,5-dimethyl-1,2-oxaphosphole 2-oxide", (7,)),
    (6, "1f", 90.2, 147.2, "2f", 93.0,
     "4-bromo-3-butyl-2-ethoxy-1-oxa-2-phosphaspiro[4.5]dec-3-ene 2-oxide", (7,)),
    (7, "1g", 85.8, 148.0, "2g", 92.1,
     "4-bromo-3-butyl-2-ethoxy-1-oxa-2-phosphaspiro[4.4]non-3-ene 2-oxide", (7,)),
    (8, "1h", 96.1, 147.4, "2h", 94.4,
     "4-bromo-2-ethoxy-3-phenyl-1-oxa-2-phosphaspiro[4.5]dec-3-ene 2-oxide", (7,)),
    (9, "1i", 91.5, 147.6, "2i", 76.9,
     "4-bromo-2-ethoxy-3-phenyl-1-oxa-2-phosphaspiro[4.4]non-3-ene 2-oxide", (7,)),
    (10, "1j", 92.8, 147.5, "2j", 87.4,
     "4-bromo-2-ethoxy-5,5-diethyl-2,5-dihydro-3-phenyl-1,2-oxaphosphole 2-oxide", (7,)),
    (11, "1k", 95.0, 147.2, "2k", 94.2,
     "4-bromo-3-butyl-2-ethoxy-2,5-dihydro-5,5-dipropyl-1,2-oxaphosphole 2-oxide", (7, 8)),
]
for entry, substrate_label, substrate_mass, copper_mass, product_label, product_mass, product_name, pages in bromo:
    ev = evidence(*pages)
    item = record(f"table2_entry{entry}", *pages)
    add_amount(item, "substrate", "mass", quantity(substrate_mass, "mg"), ev)
    add_amount(item, "cubr2", "mass", quantity(copper_mass, "mg"), ev)
    add_amount(item, "product", "isolated_product_mass", quantity(product_mass, "mg"), ev)
    set_name(item, "product", product_name, ev)
    add_unresolved(item, "The abbreviated product paragraph does not restate workup or purification; shared Table 2 conditions are retained without inferring missing operations.")
    records.append(item)


# Pages 8–9: detailed chlorocyclization products corresponding to Table 4.
chloro = [
    (1, 78.0, 153.5, 68.0, "3-butyl-4-chloro-2-ethoxy-2,5-dihydro-5,5-dimethyl-1,2-oxaphosphole 2-oxide", (8,)),
    (2, 84.2, 153.5, 83.8, "4-chloro-2-ethoxy-2,5-dihydro-5,5-dimethyl-3-phenyl-1,2-oxaphosphole 2-oxide", (8,)),
    (3, 73.3, 153.5, 51.5, "3-allyl-4-chloro-2-ethoxy-2,5-dihydro-5,5-dimethyl-1,2-oxaphosphole 2-oxide", (8,)),
    (4, 77.9, 154.0, 69.4, "4-chloro-2-ethoxy-2,5-dihydro-5,5-dimethyl-3-(2′-methylallyl)-1,2-oxaphosphole 2-oxide", (8,)),
    (5, 90.0, 153.6, 75.1, "3-butyl-4-chloro-2-ethoxy-1-oxa-2-phosphaspiro[4.5]dec-3-ene 2-oxide", (8,)),
    (6, 85.9, 153.6, 63.6, "3-butyl-4-chloro-2-ethoxy-1-oxa-2-phosphaspiro[4.4]non-3-ene 2-oxide", (8,)),
    (7, 96.1, 153.3, 87.9, "4-chloro-2-ethoxy-3-phenyl-1-oxa-2-phosphaspiro[4.5]dec-3-ene 2-oxide", (8,)),
    (8, 91.8, 153.5, 77.8, "4-chloro-2-ethoxy-3-phenyl-1-oxa-2-phosphaspiro[4.4]non-3-ene 2-oxide", (8, 9)),
]
for entry, substrate_mass, copper_mass, product_mass, product_name, pages in chloro:
    ev = evidence(*pages)
    item = record(f"table4_entry{entry}", *pages)
    add_amount(item, "substrate", "mass", quantity(substrate_mass, "mg"), ev)
    add_amount(item, "cucl2_2h2o", "mass", quantity(copper_mass, "mg"), ev)
    add_amount(item, "product", "isolated_product_mass", quantity(product_mass, "mg"), ev)
    set_name(item, "product", product_name, ev)
    if entry == 1:
        add_condition(item, "operation", "reaction monitored by TLC using petroleum ether/ethyl acetate 3:1", ev)
        add_condition(item, "workup", "evaporate the solvent", ev)
        add_condition(item, "purification", "silica-gel column chromatography, petroleum ether/ethyl acetate 4:1", ev)
    else:
        add_unresolved(item, "The abbreviated product paragraph does not restate reaction time, workup or purification; Table 4 supplies time and shared conditions.")
    if entry == 8:
        # The only fully drawn structures in the inspected experimental pages were retained as candidates.
        set_smiles_candidate(item, "substrate", "CCOP(=O)(OCC)C(=C=C1CCCC1)c1ccccc1", [f"{DOC}:page8:image"])
        set_smiles_candidate(item, "product", "CCOP1(=O)C(c2ccccc2)=C(Cl)C2(CCCC2)O1", [f"{DOC}:page8:image"])
        add_unresolved(item, "Candidate SMILES for the fully drawn 1i→3h arrow are parseable but unverified and require chemical comparison to the source image.")
    records.append(item)


def enrich_diastereomer_record(rid, pages, substrate_id, substrate_mass, copper_mass,
                               products, substrate_name=None, input_ee=None):
    ev = evidence(*pages)
    item = record(rid, *pages)
    add_amount(item, "substrate", "mass", quantity(substrate_mass, "mg"), ev)
    add_amount(item, "substrate", "amount", quantity(0.3, "mmol"), ev)
    if input_ee is not None:
        add_amount(item, "substrate", "input_ee_experimental", input_ee, ev)
    if substrate_name:
        set_name(item, "substrate", substrate_name, ev)
    add_amount(item, "cucl2_2h2o", "mass", quantity(copper_mass, "mg"), ev)
    add_amount(item, "cucl2_2h2o", "amount", quantity(1.2, "mmol"), ev)
    add_amount(item, "toluene", "volume", quantity(2, "mL"), ev)
    for entity_id, product_mass, product_name in products:
        add_amount(item, entity_id, "isolated_product_mass", quantity(product_mass, "mg"), ev)
        set_name(item, entity_id, product_name, ev)
        add_outcome(item, f"yield_measurement_basis_{entity_id}", "isolated", ev, [entity_id])
    return item


# Pages 9–10: racemic and enantioenriched chlorocyclizations.
item = enrich_diastereomer_record(
    "scheme3_1l_diastereomers", (9,), "1l", 78.2, 204.9,
    [("product1", 36.1, "cis-3i"), ("product2", 39.4, "trans-3i")],
    "diethyl (nona-3,4-dien-5-yl)phosphonate (1l)")
ev9 = evidence(9)
add_condition(item, "operation", "reaction monitored by TLC using petroleum ether/ethyl acetate 3:1", ev9)
add_condition(item, "workup", "cool; add H2O and ether; separate; wash organic layer with brine; dry over anhydrous Na2SO4; filter and evaporate", ev9)
add_condition(item, "purification", "silica-gel chromatography, petroleum ether/ethyl acetate/dichloromethane 10:1:1, 40 cm column", ev9)
records.append(item)

records.append(enrich_diastereomer_record(
    "scheme5_chiral_1l_chlorocyclization", (9,), "(Sa)-(+)-1l", 78.0, 204.6,
    [("product1", 34.8, "(S,S)-3i"), ("product2", 37.9, "(S,R)-3i")],
    "(Sa)-(+)-diethyl (nona-3,4-dien-5-yl)phosphonate",
    quantity(99, "%", qualifier="gt", raw_text=">99%")))

item = enrich_diastereomer_record(
    "scheme3_1m_diastereomers", (9,), "1m", 82.2, 204.8,
    [("product1", 34.6, "cis-3j"), ("product2", 40.0, "trans-3j")],
    "diethyl (deca-5,6-dien-5-yl)phosphonate (1m)")
add_outcome(item, "experimental_isolated_yield_trans-3j", quantity(48, "%"), evidence(9), ["product2"])
add_note(item, "Scheme 3 reports trans-3j as 47%, whereas the page-9 experimental paragraph reports 48%; both statements are retained.", evidence(9))
add_unresolved(item, "Source discrepancy: trans-3j yield is 47% in Scheme 3 and 48% in the experimental paragraph.")
records.append(item)

records.append(enrich_diastereomer_record(
    "scheme5_chiral_1m_chlorocyclization", (9, 10), "(Sa)-(+)-1m", 82.3, 204.9,
    [("product1", 36.2, "(S,S)-3j"), ("product2", 42.4, "(S,R)-3j")],
    "(Sa)-(+)-diethyl (deca-5,6-dien-5-yl)phosphonate",
    quantity(99, "%", qualifier="gt", raw_text=">99%")))

records.append(enrich_diastereomer_record(
    "scheme3_1n_diastereomers", (10,), "1n", 84.1, 204.5,
    [("product1", 34.2, "cis-3k"), ("product2", 36.0, "trans-3k")],
    "diethyl (1-phenylpenta-1,2-dien-1-yl)phosphonate (1n)"))

item = enrich_diastereomer_record(
    "scheme4_chiral_1n_chlorocyclization", (10,), "(Sa)-(−)-1n", 84.3, 204.5,
    [("ss_3k", 37.7, "(S,S)-3k"), ("sr_3k", 38.9, "(S,R)-3k")],
    "(Sa)-(−)-diethyl (1-phenylpenta-1,2-dien-1-yl)phosphonate",
    quantity(96, "%"))
add_note(item, "The second product subheading on page 10 reads '(S,R)-4k', while the reaction heading, product family and Scheme 4 identify it as (S,R)-3k; the source typo is not silently corrected.", evidence(10))
add_unresolved(item, "Source product-label typo: page-10 subheading says (S,R)-4k although the reaction identifies (S,R)-3k.")
records.append(item)


def enrich_suzuki(rid, pages, substrate_mass, k_mass, boronic_mass, catalyst_mass,
                  product_mass, product_name, typical=False):
    ev = evidence(*pages)
    item = record(rid, *pages)
    add_amount(item, "substrate", "mass", quantity(substrate_mass, "mg"), ev)
    add_amount(item, "substrate", "amount", quantity(0.3, "mmol"), ev)
    add_amount(item, "k2co3", "mass", quantity(k_mass, "mg"), ev)
    add_amount(item, "k2co3", "amount", quantity(1.05, "mmol"), ev)
    add_amount(item, "phenylboronic_acid", "mass", quantity(boronic_mass, "mg"), ev)
    add_amount(item, "phenylboronic_acid", "amount", quantity(0.75, "mmol"), ev)
    add_amount(item, "pd_complex", "mass", quantity(catalyst_mass, "mg"), ev)
    add_amount(item, "pd_complex", "amount", quantity(0.015, "mmol"), ev)
    add_amount(item, "toluene", "volume", quantity(2, "mL"), ev)
    add_amount(item, "product", "isolated_product_mass", quantity(product_mass, "mg"), ev)
    set_name(item, "product", product_name, ev)
    add_outcome(item, "yield_measurement_basis_experimental", "isolated", ev, ["product"])
    if typical:
        add_condition(item, "atmosphere", "Ar", ev)
        add_condition(item, "operation", "charge dried K2CO3, phenylboronic acid, [PdCl2(LB-Phos)2], substrate and toluene sequentially; monitor by TLC with petroleum ether/ethyl acetate 3:1", ev)
        add_condition(item, "workup", "cool; add H2O and diethyl ether; separate; wash organic layer with brine; dry over anhydrous Na2SO4; filter and evaporate", ev)
        add_condition(item, "purification", "silica-gel chromatography, petroleum ether/ethyl acetate/dichloromethane 8:1:1, 40 cm column", ev)
    else:
        add_unresolved(item, "The abbreviated Suzuki product paragraph does not restate atmosphere, reaction time, workup or purification; the scheme/table supplies only its stated shared conditions and time.")
    return item


# Pages 10–11: Table 5 Suzuki products.
records.append(enrich_suzuki(
    "table5_entry1", (10,), 80.0, 145.1, 91.5, 13.5, 69.3,
    "3-butyl-2-ethoxy-2,5-dihydro-5,5-dimethyl-4-phenyl-1,2-oxaphosphole 2-oxide (4a)", True))
item = enrich_suzuki(
    "table5_entry2", (10, 11), 80.0, 145.1, 91.5, 13.5, 76.8,
    "2-ethoxy-2,5-dihydro-5,5-dimethyl-3,4-diphenyl-1,2-oxaphosphole 2-oxide (4b)")
add_note(item, "The page-10 experimental sentence says 'afforded 4a', but the heading, Table 5 and analytical data identify this product as 4b; the source typo is retained as an unresolved note.", evidence(10, 11))
add_unresolved(item, "Source product-label typo: the 4b experimental sentence says 'afforded 4a'.")
records.append(item)
records.append(enrich_suzuki(
    "table5_entry3", (11,), 75.2, 145.0, 91.6, 13.6, 48.1,
    "3-allyl-2-ethoxy-2,5-dihydro-5,5-dimethyl-4-phenyl-1,2-oxaphosphole 2-oxide (4c)"))


# Page 11: Scheme 7 diastereomer-specific Suzuki products.
scheme7 = [
    ("scheme7_cis-3i_to_cis-4d", 80.0, 145.0, 91.5, 13.6, 80.0,
     "cis-3-butyl-2-ethoxy-5-ethyl-2,5-dihydro-4-phenyl-1,2-oxaphosphole 2-oxide (cis-4d)"),
    ("scheme7_trans-3i_to_trans-4d", 80.0, 145.1, 91.6, 13.7, 77.8,
     "trans-3-butyl-2-ethoxy-5-ethyl-2,5-dihydro-4-phenyl-1,2-oxaphosphole 2-oxide (trans-4d)"),
    ("scheme7_cis-3j_to_cis-4e", 84.3, 145.0, 91.5, 13.6, 86.4,
     "cis-3-butyl-2-ethoxy-2,5-dihydro-4-phenyl-5-propyl-1,2-oxaphosphole 2-oxide (cis-4e)"),
    ("scheme7_cis-3k_to_cis-4f", 86.0, 145.0, 91.5, 13.6, 89.6,
     "cis-2-ethoxy-2,5-dihydro-3,4-diphenyl-1,2-oxaphosphole 2-oxide (cis-4f)"),
]
for values in scheme7:
    records.append(enrich_suzuki(values[0], (11,), *values[1:]))


# Pages 11–12: Scheme 8 enantioenriched Suzuki products.
records.append(enrich_suzuki(
    "scheme8_(2S,5S)-3i_to_(2S,5S)-4d", (11,), 80.1, 145.1, 91.5, 13.5, 87.2,
    "(S,S)-3-butyl-2-ethoxy-5-ethyl-2,5-dihydro-4-phenyl-1,2-oxaphosphole 2-oxide [(S,S)-4d]"))
records.append(enrich_suzuki(
    "scheme8_(2S,5S)-3j_to_(2S,5S)-4e", (11, 12), 84.0, 145.1, 91.5, 13.7, 86.7,
    "(S,S)-3-butyl-2-ethoxy-2,5-dihydro-4-phenyl-5-propyl-1,2-oxaphosphole 2-oxide [(S,S)-4e]"))


if len(records) != 32:
    raise RuntimeError(f"expected 32 updated records, got {len(records)}")
if len({r["record_id"] for r in records}) != len(records):
    raise RuntimeError("duplicate updated record_id")

(OUT / "records_pages_0007_0012.json").write_text(
    json.dumps(records, ensure_ascii=False, indent=2) + "\n"
)


def ids(*suffixes):
    return [f"{DOC}:{suffix}" for suffix in suffixes]


coverage = {
    "document_id": DOC,
    "semantic_accuracy_verified": False,
    "pages": [
        {
            "page": 7,
            "state": "attempted",
            "regions": [
                {
                    "region": "left column experimental paragraphs for 2c–2g",
                    "finding": "Detailed bromocyclization product paragraphs were visually checked and merged with the corresponding Table 2 scope records; exact reactant/reagent/product masses were added without duplicating the batches.",
                    "evidence_ids": evidence(7),
                },
                {
                    "region": "right column continuation of 2g and experimental paragraphs for 2h–2k",
                    "finding": "Products 2h–2j and the beginning of 2k were checked; the 2k analytical paragraph continues on page 8.",
                    "evidence_ids": evidence(7),
                },
            ],
            "record_ids": ids(*[f"table2_entry{i}" for i in range(3, 12)]),
            "unresolved": [
                "Abbreviated product paragraphs do not restate workup or purification.",
                "Structures are retained by labels/names; no structure was certified from analytical text.",
            ],
        },
        {
            "page": 8,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left continuation of 2k and chlorocyclization section heading",
                    "finding": "The 2k analytical continuation was linked to Table 2 entry 11; it is not a separate experiment.",
                    "evidence_ids": evidence(8),
                },
                {
                    "region": "left column typical procedure for 3a and abbreviated preparations of 3b–3d",
                    "finding": "The detailed 3a procedure and masses for 3b–3d were merged with Table 4 entries 1–4; the 3a TLC, evaporation and chromatography details were structured.",
                    "evidence_ids": evidence(8),
                },
                {
                    "region": "right column preparations of 3e–3h and drawn 1i→3h arrow",
                    "finding": "Entries 3e–3h were checked; page 8 contains a fully drawn 1i→3h reaction, so parseable but unverified candidate SMILES were retained for that arrow. The 3h analytical text continues on page 9.",
                    "evidence_ids": evidence(8),
                },
            ],
            "record_ids": ids("table2_entry11", *[f"table4_entry{i}" for i in range(1, 9)]),
            "unresolved": [
                "Candidate 1i/3h SMILES are not structure-verified.",
                "The abbreviated 3b–3h paragraphs do not restate workup or purification; 3h continues on page 9.",
            ],
        },
        {
            "page": 9,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left completion of 3h analytical data",
                    "finding": "The cross-page 3h paragraph was linked to Table 4 entry 8 and not counted again.",
                    "evidence_ids": evidence(9),
                },
                {
                    "region": "left column Typical Procedure II for cis/trans-3i and enantioenriched (S,S)/(S,R)-3i",
                    "finding": "Racemic and enantioenriched 1l chlorocyclizations were kept as distinct existing records; exact charges, isolated product masses, workup/purification for the typical procedure, yields and ee values were checked.",
                    "evidence_ids": evidence(9),
                },
                {
                    "region": "right column cis/trans-3j and beginning of enantioenriched 3j paragraphs",
                    "finding": "The 1m chlorocyclizations were linked to Scheme 3 and Scheme 5 records. The experimental paragraph gives trans-3j as 48%, while Scheme 3 gives 47%; both values are retained.",
                    "evidence_ids": evidence(9),
                },
            ],
            "record_ids": ids("table4_entry8", "scheme3_1l_diastereomers", "scheme5_chiral_1l_chlorocyclization", "scheme3_1m_diastereomers", "scheme5_chiral_1m_chlorocyclization"),
            "unresolved": [
                "Source discrepancy for trans-3j: 47% in Scheme 3 versus 48% in the experimental paragraph.",
                "The enantioenriched 3j paragraph continues on page 10.",
            ],
        },
        {
            "page": 10,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left completion of enantioenriched 3j and racemic cis/trans-3k",
                    "finding": "The chiral 1m continuation and racemic 1n chlorocyclization were merged with their existing scheme records, preserving exact masses and product-specific results.",
                    "evidence_ids": evidence(10),
                },
                {
                    "region": "middle-left to upper-right enantioenriched (S,S)/(S,R)-3k",
                    "finding": "The chiral 1n chlorocyclization was merged with Scheme 4. A source subheading says '(S,R)-4k' although the reaction identifies (S,R)-3k; the typo is retained as unresolved.",
                    "evidence_ids": evidence(10),
                },
                {
                    "region": "right column Suzuki section, typical 4a procedure and start of 4b paragraph",
                    "finding": "The full 4a procedure and the 4b charges/product mass were merged with Table 5 entries 1–2. The 4b sentence says 'afforded 4a'; heading/table context identifies 4b, and the typo is explicitly logged.",
                    "evidence_ids": evidence(10),
                },
            ],
            "record_ids": ids("scheme5_chiral_1m_chlorocyclization", "scheme3_1n_diastereomers", "scheme4_chiral_1n_chlorocyclization", "table5_entry1", "table5_entry2"),
            "unresolved": [
                "Source product-label typo '(S,R)-4k' versus (S,R)-3k.",
                "Source product-label typo in the 4b paragraph ('afforded 4a').",
                "The 4b analytical paragraph continues on page 11.",
            ],
        },
        {
            "page": 11,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left completion of 4b and preparation of 4c",
                    "finding": "The 4b analytical continuation and 4c preparation were linked to Table 5 entries 2–3; 4c exact reagent and product masses were added.",
                    "evidence_ids": evidence(11),
                },
                {
                    "region": "left/lower-left cis-4d, trans-4d and cis-4e experimental paragraphs",
                    "finding": "Three diastereomer-specific Suzuki batches were merged with Scheme 7 records using exact charges and product masses; their scheme-derived reaction times remain separate evidence.",
                    "evidence_ids": evidence(11),
                },
                {
                    "region": "right column cis-4e continuation, cis-4f, (S,S)-4d and beginning of (S,S)-4e",
                    "finding": "The remaining Scheme 7 batch and both Scheme 8 batches were checked. Product-specific yields/ee were preserved, and the (S,S)-4e analytical text continues on page 12.",
                    "evidence_ids": evidence(11),
                },
            ],
            "record_ids": ids("table5_entry2", "table5_entry3", "scheme7_cis-3i_to_cis-4d", "scheme7_trans-3i_to_trans-4d", "scheme7_cis-3j_to_cis-4e", "scheme7_cis-3k_to_cis-4f", "scheme8_(2S,5S)-3i_to_(2S,5S)-4d", "scheme8_(2S,5S)-3j_to_(2S,5S)-4e"),
            "unresolved": [
                "Abbreviated Suzuki paragraphs do not restate atmosphere, workup or purification.",
                "The (S,S)-4e analytical paragraph continues on page 12.",
            ],
        },
        {
            "page": 12,
            "state": "attempted",
            "regions": [
                {
                    "region": "upper-left completion of (S,S)-4e analytical characterization",
                    "finding": "This is the continuation of the Scheme 8 (S,S)-4e batch from page 11, not a new experiment; it was linked to the existing record.",
                    "evidence_ids": evidence(12),
                },
                {
                    "region": "Supporting Information statement, acknowledgments and references",
                    "finding": "No new reaction arrow, table row or experimental batch appears. The SI is mentioned but was not supplied or explicitly associated. Acknowledged reproductions are not counted as additional experiments.",
                    "evidence_ids": evidence(12),
                },
            ],
            "record_ids": ids("scheme8_(2S,5S)-3j_to_(2S,5S)-4e"),
            "unresolved": [
                "Supporting information is mentioned but remains unassociated and was not imported.",
                "Analytical and crystallographic reference material was not converted into extra reaction records.",
            ],
        },
    ],
}

(ROOT / "coverage").mkdir(parents=True, exist_ok=True)
(ROOT / "coverage" / "pages_0007_0012.json").write_text(
    json.dumps(coverage, ensure_ascii=False, indent=2) + "\n"
)


# Mark exactly this session's page tasks as attempted; this is coverage state, not accuracy certification.
tasks_path = ROOT / "tasks.json"
tasks = json.loads(tasks_path.read_text())
for task in tasks:
    if task["task_id"] in {f"{DOC}:page{page}:text" for page in range(7, 13)}:
        task["state"] = "attempted"
tasks_path.write_text(json.dumps(tasks, ensure_ascii=False, indent=2) + "\n")

print(json.dumps({"updated_records": len(records), "coverage_pages": len(coverage["pages"])}, ensure_ascii=False))
