#!/usr/bin/env python3
"""Source-linked extraction specification for review PDF pages 37--42."""
import json
import re
from pathlib import Path

DOC = "doc_a46c3871d27d020b"
BASE = Path(__file__).parents[1]
OUT = Path(__file__).with_name("records_pages_0037_0042.json")
records = []


def ev(pages):
    result = []
    for page in pages:
        result.extend([f"{DOC}:page{page}:text", f"{DOC}:page{page}:image"])
    return result


def fact(value, evidence):
    return {
        "value": value,
        "evidence_ids": [] if value is None else list(evidence),
        "verification": "missing" if value is None else "unreviewed",
    }


def slug(value):
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()[:40] or "entity"


def P(role, label, name=None, smiles=None, amounts=None):
    return role, label, name, smiles, amounts or []


def participant(index, spec, evidence):
    role, label, name, smiles, amounts = spec
    return {
        "entity_id": f"p{index}_{slug(label)}",
        "role": role,
        "label": fact(label, evidence),
        "name": fact(name, evidence),
        "smiles": fact(smiles, evidence),
        "smiles_parseable": None,
        "structure_verified": False,
        "amounts": [
            {"name": name, "fact": fact(value, evidence)} for name, value in amounts
        ],
    }


def add(rid, source_id, pages, parts, conditions=None, outcomes=None, notes=None,
        unresolved=None, kind="literature_example"):
    evidence = ev(pages)
    ps = [participant(i, item, evidence) for i, item in enumerate(parts, 1)]
    ids = {p["label"]["value"]: p["entity_id"] for p in ps}
    cond = list(conditions or [])
    if kind == "literature_example":
        if not any(name == "temperature" for name, _ in cond):
            cond.append(("temperature", None))
        if not any(name == "time" for name, _ in cond):
            cond.append(("time", None))
    fields = []
    has_yield = False
    for name, value, targets in outcomes or []:
        field = {"name": name, "fact": fact(value, evidence)}
        if targets:
            if isinstance(targets, str):
                targets = [targets]
            field["target_entity_ids"] = [ids[target] for target in targets]
        fields.append(field)
        has_yield |= name == "yield" and value is not None
    if kind == "literature_example" and not any(x["name"] == "yield" for x in fields):
        product_ids = [p["entity_id"] for p in ps if p["role"] == "product"]
        missing = {"name": "yield", "fact": fact(None, evidence)}
        if product_ids:
            missing["target_entity_ids"] = product_ids
        fields.append(missing)
    if has_yield and not any(x["name"] == "yield_measurement_basis" for x in fields):
        fields.append({"name": "yield_measurement_basis", "fact": fact(None, evidence)})
    steps = []
    if cond:
        steps.append({
            "step_id": "step1",
            "participant_ids": [p["entity_id"] for p in ps if p["role"] != "product"],
            "conditions": [{"name": name, "fact": fact(value, evidence)} for name, value in cond],
        })
    records.append({
        "record_id": f"{DOC}:{rid}",
        "document_id": DOC,
        "source_reaction_id": source_id,
        "record_kind": kind,
        "status": "candidate",
        "completeness": "partial",
        "evidence_ids": evidence,
        "participants": ps,
        "steps": steps,
        "outcomes": fields,
        "notes": [fact(note, evidence) for note in notes or []],
        "review": {
            "method": "none", "reviewer": None, "checked_fields": [],
            "unresolved": list(unresolved or []) + [
                "This is a secondary-review example; the cited primary article and SI were not supplied.",
                "Complex, generic, or stereochemically uncertain drawings remain label-only; all structures are unverified.",
            ],
        },
    })
    return records[-1]


def mechanism(rid, source_id, pages, sequence, conditions=None, notes=None, unresolved=None):
    parts = []
    for index, label in enumerate(sequence):
        role = "reactant" if index == 0 else ("product" if index == len(sequence) - 1 else "unspecified_agent")
        parts.append(P(role, label))
    return add(rid, source_id, pages, parts, conditions=conditions, notes=notes,
               unresolved=list(unresolved or []) + [
                   "The arrows depict a proposed pathway, not independently reported experimental operations."
               ], kind="mechanism")


def q(number, unit, **extra):
    value = {"number": number, "unit": unit}
    value.update(extra)
    return value


def qr(minimum, maximum, unit, raw_text):
    return {"minimum": minimum, "maximum": maximum, "unit": unit, "raw_text": raw_text}


# ---------------------------------------------------------------------------
# Page 37: Schemes 174--177. Two page-36 boundary records are enriched here.
# ---------------------------------------------------------------------------
add("p0036_s174_text_only", "Scheme 174 methanol quench", [36, 37], [
    P("reactant", "propadiene", "propadiene", "C=C=C"),
    P("reagent", "PhMe2SiCu·LiCN", "silylcupration reagent"),
    P("unspecified_agent", "815", "vinylic copper intermediate"),
    P("reagent", "MeOH", "methanol", "CO"),
    P("product", "816", "allyl silane"),
], conditions=[("temperature", q(-40, "°C")), ("time", q(1, "h")),
               ("operation", "silylcupration, then MeOH quench at −40 °C")])

for suffix, electrophile, name, smiles, yld, detail in [
    ("epoxide", "epoxide (drawn)", None, None, 57, None),
    ("cyclohexenone", "2-cyclohexenone", "cyclohex-2-en-1-one", "O=C1C=CCCC1", 68, "1,4-addition"),
    ("cinnamoyl_chloride", "PhCH=CHCOCl", "cinnamoyl chloride", "O=C(Cl)/C=C/c1ccccc1", 65, None),
    ("acetyl_chloride", "MeCOCl", "acetyl chloride", "CC(=O)Cl", 79, None),
    ("methyl_iodide", "MeI", "methyl iodide", "CI", 88, None),
    ("butyl_iodide", "BuI", "1-iodobutane", "CCCCI", 64, None),
]:
    product = f"817 ({electrophile})"
    add(f"p0037_s174_{suffix}", f"Scheme 174 trapping with {electrophile}", [36, 37], [
        P("reactant", "propadiene", "propadiene", "C=C=C"),
        P("reagent", "PhMe2SiCu·LiCN", "silylcupration reagent"),
        P("unspecified_agent", "815", "vinylic copper intermediate"),
        P("reagent", electrophile, name, smiles),
        P("product", product, "electrophile-trapped allyl silane"),
    ], conditions=[("temperature", q(-40, "°C")), ("time", q(1, "h")),
                   ("operation", "silylcupration followed by electrophile trapping")],
        outcomes=[("yield", q(yld, "%"), product)] + ([ ("addition_mode", detail, product) ] if detail else []),
        unresolved=["The trapping-arrow temperature and time are not separately printed; −40 °C and 1 h belong to formation of intermediate 815."])

add("p0036_s175_text_only", "Scheme 175 substrate 818", [36, 37], [
    P("reactant", "818", "stereochemically defined cyclic allene"),
    P("reagent", "(PhMe2Si)2Cu·LiCN", "silylcupration reagent"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "819", "stereospecific syn-addition product"),
], conditions=[("temperature", {"minimum": -40, "maximum": 25, "unit": "°C", "raw_text": "−40 °C to 25 °C"})],
    outcomes=[("stereochemical_result", "stereospecific syn-addition", "819")])
add("p0037_s175_820", "Scheme 175 substrate 820", [36, 37], [
    P("reactant", "820", "stereochemically defined cyclic allene"),
    P("reagent", "(PhMe2Si)2Cu·LiCN", "silylcupration reagent"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "821", "stereospecific syn-addition product"),
], conditions=[("temperature", {"minimum": -40, "maximum": 25, "unit": "°C", "raw_text": "−40 °C to 25 °C"}),
               ("operation", "conditions marked ibid")],
    outcomes=[("stereochemical_result", "stereospecific syn-addition", "821")])

add("p0037_s176_823_scope", "Scheme 176 product 823 scope", [37], [
    P("reactant", "allene (R=Me or R,R=(CH2)5)"),
    P("reagent", "(PhMe2Si)2Cu·LiCN", "silylcupration reagent"),
    P("unspecified_agent", "822", "allylic copper intermediate"),
    P("reactant", "allylic phosphate (R1=H or alkyl; R2=H or Me)"),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("product", "823", "1,4-diene"),
], conditions=[("temperature", q(-40, "°C")),
               ("operation", "sequential silylcupration and allylic-phosphate trapping")])
for suffix, subs, yld in [("h_h", "R1=R2=H", 75), ("propyl_h", "R1=n-C3H7; R2=H", 70)]:
    product = f"824 ({subs})"
    add(f"p0037_s176_824_{suffix}", f"Scheme 176 product 824 {subs}", [37], [
        P("reactant", "phenylpropadiene"),
        P("reagent", "(PhMe2Si)2Cu·LiCN", "silylcupration reagent"),
        P("reactant", f"allylic phosphate ({subs})"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("product", product, "1,4-diene Z/E mixture"),
    ], conditions=[("temperature", q(-40, "°C")), ("operation", "conditions marked ibid")],
        outcomes=[("yield", q(yld, "%"), product), ("stereochemical_result", "Z/E mixture", product)])

add("p0037_s177_825", "Scheme 177 substrate 825 scope", [37], [
    P("reactant", "825 (R=Et, n-Pr, i-Pr, or Bn)", "2,3-allenol benzazepine precursor"),
    P("reagent", "n-BuLi or (TMS)2NLi or (TMS)2NNa", "printed base options", None,
      [("amount", q(1.2, "equiv"))]),
    P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
    P("reagent", "10% HCl", "hydrochloric acid", None, [("concentration", q(10, "%"))]),
    P("product", "829", "3-methylenebenz[c]azepine"),
], conditions=[("initial_temperature", q(0, "°C")), ("then_temperature", "r.t."),
               ("final_temperature", "reflux"),
               ("operation", "base treatment followed by 10% HCl")],
    outcomes=[("yield", qr(32, 80, "%", "32–80%"), "829")],
    unresolved=["The three base choices are not mapped to individual R substituents on the review page."])
mechanism("p0037_s177_825_mechanism", "Scheme 177 proposed ring-expansion pathway", [37],
          ["825", "826", "827", "828", "829"],
          notes=["The review depicts ring opening followed by intramolecular conjugate addition and protonation."])
add("p0037_s177_830", "Scheme 177 substrate 830 scope", [37], [
    P("reactant", "830 (R=Me, Et, n-Pr, or Bn)", "benzocyclopentanone-derived allenol"),
    P("reagent", "(TMS)2NLi (or K, Na)", "hexamethyldisilazide base options", None,
      [("amount", q(1.2, "equiv"))]),
    P("solvent", "THF/HMPA", "tetrahydrofuran/hexamethylphosphoramide"),
    P("reagent", "H2O", "water", "O"),
    P("product", "831", "ring-expanded product"),
], conditions=[("temperature", "reflux"), ("operation", "base treatment followed by water")],
    outcomes=[("yield", qr(42, 80, "%", "42–80%"), "831")],
    unresolved=["The Li/K/Na base choices are not mapped to individual R substituents."])
for suffix, subs, yld in [
    ("h_h", "R1=R2=H", 75), ("me_h", "R1=Me; R2=H", 68),
    ("h_me", "R1=H; R2=Me", 53), ("ome_h", "R1=OMe; R2=H", 69),
    ("ome_ome", "R1=R2=OMe", 73),
]:
    product = f"834 ({subs})"
    add(f"p0037_s177_832_{suffix}", f"Scheme 177 substrate 832 {subs}", [37], [
        P("reactant", f"832 ({subs})", "benzocyclotetrahydropyran"),
        P("reagent", "lithiated methoxyallene reagent (drawn)"),
        P("solvent", "THF", "tetrahydrofuran", "C1CCOC1"),
        P("reagent", "H2O", "water", "O"),
        P("product", product, "ring-expanded product"),
    ], conditions=[("temperature", q(-30, "°C")), ("operation", "addition followed by water")],
        outcomes=[("yield", q(yld, "%"), product)])
mechanism("p0037_s177_832_mechanism", "Scheme 177 substrate 832 proposed pathway", [37],
          ["832 + lithiated methoxyallene", "833", "hydrated intermediate", "834"],
          conditions=[("temperature", q(-30, "°C"))])


# ---------------------------------------------------------------------------
# Page 38: Schemes 178--183.
# ---------------------------------------------------------------------------
add("p0038_s178_835", "Scheme 178 formation of 836", [37, 38], [
    P("reactant", "835", "polycyclic ketone"),
    P("reagent", "lithiated methoxyallene reagent (drawn)"),
    P("reagent", "NaHCO3", "sodium bicarbonate", "[Na+].O=C([O-])O"),
    P("reagent", "H2O", "water", "O"),
    P("product", "836", "1,2,6-triene alcohol"),
], conditions=[("temperature", {"minimum": -78, "maximum": 25, "unit": "°C", "raw_text": "−78 °C to r.t."}),
               ("operation", "addition followed by NaHCO3/H2O")])
add("p0038_s178_838", "Scheme 178 oxy-Cope/condensation branch", [37, 38], [
    P("reactant", "836", "1,2,6-triene"),
    P("unspecified_agent", "837", "oxy-Cope ring-expansion intermediate"),
    P("product", "838", "fused bicyclic product"),
], conditions=[("operation", "oxy-Cope rearrangement then intramolecular condensation")],
    outcomes=[("yield", q(21, "%"), "838")])
add("p0038_s178_839", "Scheme 178 protonolysis branch", [37, 38], [
    P("reactant", "836", "1,2,6-triene"),
    P("unspecified_agent", "837", "oxy-Cope ring-expansion intermediate"),
    P("product", "839", "fused bicyclic protonolysis product"),
], conditions=[("operation", "oxy-Cope rearrangement followed by direct protonolysis")],
    outcomes=[("yield", q(34, "%"), "839")])
mechanism("p0038_s178_mechanism", "Scheme 178 proposed rearrangement pathways", [37, 38],
          ["836", "837", "838 or 839"],
          notes=["The two branches are intramolecular condensation to 838 and direct protonolysis to 839."])

add("p0038_s179_general", "Scheme 179 general Claisen rearrangement", [38], [
    P("reactant", "1,2-allenyl allyl ether (R1/R2 generic)"),
    P("solvent", "DMF or benzene", "dimethylformamide or benzene"),
    P("product", "840", "2-methylene-4-alkenal"),
], conditions=[("DMF_temperature", q(120, "°C")), ("benzene_temperature", "reflux")],
    outcomes=[("yield", qr(63, 94, "%", "63–94%"), "840")], kind="general_scheme",
    unresolved=["The solvent/temperature choices are not mapped to individual examples."])
for suffix, label, yld in [
    ("acyclic", "acyclic terpene-like allenyl allyl ether", 94),
    ("bicyclic", "bicyclic allenyl allyl ether", 81),
    ("bromophenoxy", "bromophenoxy-tethered allenyl allyl ether", 90),
]:
    product = f"840 example ({suffix})"
    add(f"p0038_s179_{suffix}", f"Scheme 179 {suffix} example", [38], [
        P("reactant", label), P("product", product, "2-methylene-4-alkenal"),
    ], conditions=[("DMF_temperature", q(120, "°C")), ("benzene_temperature", "reflux")],
        outcomes=[("yield", q(yld, "%"), product)],
        unresolved=["The review does not map this example to DMF/120 °C versus benzene/reflux."])

add("p0038_s180_841", "Scheme 180 allenyl carbonyl scope", [37, 38], [
    P("reactant", "841 (X=NTs, C(CO2Et)2, or O; R=H, Me, or Et; n=1 or 2)", "allenyl aldehyde/ketone"),
    P("reagent", "Et3SiH", "triethylsilane", "CC[SiH](CC)CC"),
    P("catalyst", "Rh(acac)(CO)2", None, None, [("catalyst_loading", q(1, "mol%"))]),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("solvent", "Et2O", "diethyl ether", "CCOCC"),
    P("product", "cis-842", "2-vinylic cyclic alcohol"),
], conditions=[("temperature", q(70, "°C")), ("atmosphere", "CO, 10 atm")],
    outcomes=[("yield", qr(54, 74, "%", "54–74%"), "cis-842")])
add("p0038_s180_843", "Scheme 180 allenyne scope", [37, 38], [
    P("reactant", "843 (R1=Me, n-Bu, or Ph; Z=NTs, O, or C(CO2Et)2)", "6,7-allen-1-yne"),
    P("reagent", "(R2O)3SiH (R2=Me or Et)", "trialkoxysilane", None, [("amount", q(3, "equiv"))]),
    P("catalyst", "Rh(acac)(CO)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "toluene", "toluene", "Cc1ccccc1"),
    P("reagent", "CO", "carbon monoxide", "[C-]#[O+]"),
    P("product", "844", "2-(1-silylvinyl)alkylidenecyclopentane"),
], conditions=[("temperature", q(60, "°C")), ("atmosphere", "CO, 1 atm")])

add("p0038_s181", "Scheme 181 Pd(II) coupling", [37, 38], [
    P("reactant", "1,2-allenyl phenyl sulfoxide (R1=alkyl; R2=CH2R1)"),
    P("reactant", "allyl bromide", "3-bromoprop-1-ene", "C=CCBr"),
    P("catalyst", "PdCl2(MeCN)2", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "LiOAc", "lithium acetate", "[Li+].CC(=O)[O-]"),
    P("product", "845", "2-vinylic-1(E),4-alkadienyl phenyl sulfoxide"),
], conditions=[("temperature", "reflux")], outcomes=[
    ("yield", qr(35, 78, "%", "35–78%"), "845"),
    ("E_Z_ratio", "92:8 to 97:3", "845"),
])

add("p0038_s182_productive", "Scheme 182 productive cross-metathesis", [37, 38], [
    P("reactant", "monosubstituted allene (R nonaryl)"),
    P("catalyst", "drawn Ru carbene catalyst", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "1,3-disubstituted allene", "cross-metathesis product"),
], conditions=[("temperature", q(20, "°C"))],
    outcomes=[("yield", qr(10, 100, "%", "10–100%"), "1,3-disubstituted allene")])
add("p0038_s182_aryl_failure", "Scheme 182 aryl-allene failure", [37, 38], [
    P("reactant", "monosubstituted allene (R=Ar)"),
    P("catalyst", "drawn Ru carbene catalyst", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "polymeric products only", "polymer"),
], conditions=[("temperature", q(20, "°C"))],
    outcomes=[("result", "only polymeric products were formed", "polymeric products only")])

add("p0038_s183_846", "Scheme 183 allenol 846 scope", [38], [
    P("reactant", "846 (printed R1–R5 scope)", "2,3-allenol"),
    P("reactant", "o-tolylboronic acid (drawn)"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "847", "1,3-diene"),
], conditions=[("temperature", q(80, "°C"))], outcomes=[
    ("yield", qr(91, 99, "%", "91–99%"), "847"),
    ("E_Z_ratio", "1.5:1 to >20:1", "847"),
])
add("p0038_s183_848", "Scheme 183 allenol 848 scope", [38], [
    P("reactant", "848", "1-ethynylcyclohexanol-derived allenol"),
    P("reactant", "RB(OH)2 (printed aryl/alkenyl scope)", "organic boronic acid"),
    P("catalyst", "Pd(PPh3)4", None, None, [("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "dioxane", "1,4-dioxane", "O1CCOCC1"),
    P("product", "849", "1,3-diene"),
], conditions=[("temperature", q(80, "°C"))],
    outcomes=[("yield", qr(63, 99, "%", "63–99%"), "849")],
    notes=["R list: 4-MeC6H4, 2-MeOC6H4, 4-MeOC6H4, Ph, 1-naphthyl, 4-AcC6H4, 3-O2NC6H4, and two drawn alkenyl groups."])
mechanism("p0038_s183_mechanism", "Scheme 183 proposed Pd pathway", [38],
          ["allenol + boronic acid + Pd(0)", "dienyl-Pd intermediate", "1,3-diene + Pd(0)"],
          notes=["The prose proposes hydrogen-bond-assisted oxidative addition, transmetalation, and reductive elimination."])


# ---------------------------------------------------------------------------
# Page 39: Schemes 184--187; the remainder is nonexperimental back matter.
# ---------------------------------------------------------------------------
add("p0039_s184", "Scheme 184 vanadium aldol-type addition", [38, 39], [
    P("reactant", "850 (R1 generic)", "2,3-allenic alcohol"),
    P("reactant", "R2CHO", "aldehyde"),
    P("catalyst", "VO(OSiPh3)3", None, None, [("catalyst_loading", q(5, "mol%"))]),
    P("reagent", "Ph3SiOH", "triphenylsilanol"),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "854", "aldol-type addition product"),
], conditions=[("temperature", "r.t.")])
mechanism("p0039_s184_mechanism", "Scheme 184 proposed vanadium cycle", [38, 39],
          ["850 + VO(OSiPh3)3", "851", "852", "853", "854 + VO(OSiPh3)3"],
          conditions=[("temperature", "r.t.")],
          notes=["Aldehyde addition gives 853; Ph3SiOH hydrolysis releases 854 and regenerates catalyst."])

add("p0039_s185_scope", "Scheme 185 double cyclopropanation scope", [38, 39], [
    P("reactant", "855 (R=H or alkyl; or R,R=(CH2)n, n=4 or 5)", "2,3-allenol"),
    P("reagent", "Zn(CH2I)2·DME", "Simmons–Smith-type reagent", None, [("amount", q(3.0, "equiv"))]),
    P("unspecified_agent", "chiral dioxaborolane reagent (drawn; R'=t-Bu or Me)", None, None,
      [("amount", q(1.2, "equiv"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "857", "spiropentane"),
], conditions=[("initial_temperature", q(-10, "°C")), ("warm_to", "r.t.")], outcomes=[
    ("yield", qr(86, 97, "%", "86–97%"), "857"),
    ("enantiomeric_excess", qr(55, 91, "%", "55–91% ee"), "857"),
])
add("p0039_s185_ph_low_yield", "Scheme 185 R=Ph low-yield result", [38, 39], [
    P("reactant", "855 (R=Ph)", "2,3-allenol"),
    P("reagent", "Zn(CH2I)2·DME", "Simmons–Smith-type reagent", None, [("amount", q(3.0, "equiv"))]),
    P("unspecified_agent", "chiral dioxaborolane reagent (drawn)", None, None, [("amount", q(1.2, "equiv"))]),
    P("solvent", "CH2Cl2", "dichloromethane", "ClCCl"),
    P("product", "857 (R=Ph)", "spiropentane"),
], conditions=[("initial_temperature", q(-10, "°C")), ("warm_to", "r.t.")],
    outcomes=[("yield", q(7, "%"), "857 (R=Ph)")])

add("p0039_s186_858", "Scheme 186 two-component coupling", [39], [
    P("reactant", "ethyl butadienoate", "ethyl 2,3-butadienoate", "C=C=CC(=O)OCC"),
    P("reactant", "beta-substituted alpha,beta-unsaturated enone (R=aryl or alkyl)"),
    P("catalyst", "quinuclidine", "quinuclidine", None, [("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "PhCH3", "toluene", "Cc1ccccc1"),
    P("product", "858", "2-substituted 2,3-alkadienoate"),
], conditions=[("temperature", "r.t.")],
    outcomes=[("yield", qr(50, 98, "%", "50–98%"), "858")])
add("p0039_s186_alpha_failure", "Scheme 186 alpha-substituted-enone failure", [39], [
    P("reactant", "ethyl butadienoate", "ethyl 2,3-butadienoate", "C=C=CC(=O)OCC"),
    P("reactant", "alpha-substituted alpha,beta-unsaturated enone"),
    P("catalyst", "quinuclidine", "quinuclidine", None, [("catalyst_loading", q(10, "mol%"))]),
    P("solvent", "PhCH3", "toluene", "Cc1ccccc1"),
    P("product", "858 not formed", "no reaction product"),
], conditions=[("temperature", "r.t.")],
    outcomes=[("result", "no reaction was observed", "858 not formed")])
for suffix, r_group, yld in [
    ("phenethyl", "R=Ph(CH2)2", 88), ("propyl", "R=n-C3H7", 80),
    ("i_bn", "R=i-Bn (as printed)", 60), ("ethyl", "R=Et", 65),
]:
    product = f"859 ({r_group})"
    add(f"p0039_s186_859_{suffix}", f"Scheme 186 three-component row {r_group}", [39], [
        P("reactant", "ethyl butadienoate", "ethyl 2,3-butadienoate", "C=C=CC(=O)OCC"),
        P("reactant", "chiral-auxiliary acrylate (drawn)"),
        P("reactant", f"aldehyde ({r_group})"),
        P("catalyst", "quinuclidine", "quinuclidine", None, [("catalyst_loading", q(20, "mol%"))]),
        P("solvent", "MeCN", "acetonitrile", "CC#N"),
        P("product", product, "three-component coupling product"),
    ], outcomes=[("yield", q(yld, "%"), product)],
        unresolved=["The third row is printed as 'i-Bn'; its intended substituent identity is not inferred."] if suffix == "i_bn" else None)

add("p0039_s187", "Scheme 187 enantioselective dihydroxylation", [39], [
    P("reactant", "arylpropadiene (Ar printed scope)"),
    P("reagent", "ADMX (as printed)"),
    P("product", "860", "chiral 1-hydroxy-1-aryl acetone"),
], outcomes=[
    ("yield", qr(45, 79, "%", "45–79%"), "860"),
    ("enantiomeric_excess", qr(82, 92, "%", "82–92% ee"), "860"),
    ("absolute_configuration", "R", "860"),
], notes=["Ar scope: C6H5, 4-MeC6H4, 4-MeOC6H4, 4-ClC6H4, 2-MeC6H4, and 2-naphthyl."],
    unresolved=["The reagent abbreviation is preserved exactly as printed ('ADMX'); its formulation is not expanded from the review page."])


OUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"output": str(OUT), "records": len(records)}, ensure_ascii=False))
