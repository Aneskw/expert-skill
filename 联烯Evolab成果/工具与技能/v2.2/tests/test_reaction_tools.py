import argparse
import copy
import importlib.util
from pathlib import Path

import pytest
from pypdf import PdfWriter

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "reaction_tools", ROOT / "skills/chemical-reaction-extraction/scripts/reaction_tools.py"
)
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


@pytest.fixture
def dataset(tmp_path):
    pdf = tmp_path / "fixture.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(pdf)
    base = tmp_path / "dataset"
    tools.prepare(argparse.Namespace(
        pdf=str(pdf), folder=None, manifest=None, supplement=None,
        render=True, chem_only=False, out=str(base),
    ))
    return base, tools.read(base / "dataset.json")


def record(data, suffix="entry1"):
    doc = data["documents"][0]
    evidence = doc["evidence"][0]["evidence_id"]
    item = tools.empty_record(doc["document_id"], suffix, [evidence], "optimization_entry")
    item["outcomes"] = [{"name": "yield", "fact": tools.fact(
        {"number": 82, "unit": "%"}, [evidence], "source_checked"
    )}]
    item["status"] = "reviewed"
    item["review"]["method"] = "assistant_visual"
    return item


def merge(base, records):
    path = base / "submitted.json"
    tools.write(path, records)
    tools.merge(argparse.Namespace(dataset=str(base / "dataset.json"), records=str(path)))


def test_machine_merge_quarantines_self_certification_and_keeps_rows(dataset):
    base, data = dataset
    first = record(data)
    second = record(data, "entry2")
    second["outcomes"][0]["fact"]["value"]["number"] = 95
    merge(base, [first, second])
    saved = tools.read(base / "dataset.json")
    assert len(saved["experiments"]) == 2
    assert all(r["status"] == "needs_review" for r in saved["experiments"])
    assert all(r["outcomes"][0]["fact"]["verification"] == "unreviewed"
               for r in saved["experiments"])
    assert tools.validate(saved, base) == []
    assert not tools.read(base / "summary.json")["semantic_coverage_complete"]


def test_bad_evidence_is_rejected_atomically(dataset):
    base, data = dataset
    item = record(data)
    item["outcomes"][0]["fact"]["evidence_ids"] = ["fabricated"]
    before = (base / "dataset.json").read_bytes()
    with pytest.raises(ValueError, match="invalid or unrelated evidence"):
        merge(base, [item])
    assert (base / "dataset.json").read_bytes() == before


def test_existing_review_and_raw_candidates_are_preserved(dataset):
    base, data = dataset
    item = record(data)
    data["experiments"] = [item]
    raw = copy.deepcopy(item)
    raw["status"] = "candidate"
    data["candidates"] = [raw]
    tools.write(base / "dataset.json", data)
    before = (base / "dataset.json").read_bytes()
    with pytest.raises(ValueError, match="Cannot overwrite"):
        merge(base, [item])
    assert (base / "dataset.json").read_bytes() == before


def test_source_tampering_and_outside_assets_are_rejected(dataset, tmp_path):
    base, data = dataset
    doc = data["documents"][0]
    (base / doc["source_pdf"]).write_bytes(b"tampered")
    assert any("hash mismatch" in e for e in tools.validate(data, base))
    external = tmp_path / "external.png"
    external.write_bytes(b"not-an-image")
    doc["evidence"][1]["asset"] = str(external)
    assert any("asset missing" in e for e in tools.validate(data, base))


def test_crop_has_source_lineage_and_rejects_invalid_box(dataset):
    base, data = dataset
    evidence = data["documents"][0]["evidence"][1]["evidence_id"]
    target = base / "crop.png"
    args = argparse.Namespace(dataset=str(base / "dataset.json"), evidence=evidence,
                              box=[0, 0, 100, 100], out=str(target))
    tools.crop(args)
    receipt = tools.read(str(target) + ".evidence.json")
    assert receipt["page"] == 1
    assert receipt["crop_sha256"] == tools.sha(target)
    args.box = [-1, 0, 100, 100]
    with pytest.raises(ValueError, match="outside image"):
        tools.crop(args)


@pytest.mark.parametrize('value', ['150%', {'number':-3,'unit':'days'}, {'number':-1,'unit':'μmol'}])
def test_invalid_quantities_cannot_bypass_machine_merge(dataset,value):
    base,data=dataset
    item=record(data)
    if isinstance(value,dict) and value['unit']=='days':
        item['outcomes']=[]
        item['steps']=[{'step_id':'s1','participant_ids':[],'conditions':[{'name':'time','fact':tools.fact(value,[item['evidence_ids'][0]])}]}]
    else:
        item['outcomes'][0]['fact']['value']=value
    before=(base/'dataset.json').read_bytes()
    with pytest.raises(ValueError):merge(base,[item])
    assert (base/'dataset.json').read_bytes()==before


def test_range_bounds_qualitative_and_negative_temperature_survive(dataset):
    base,data=dataset
    item=record(data)
    eid=item['evidence_ids'][0]
    item['outcomes'][0]['fact']['value']='<5%'
    item['steps']=[{'step_id':'s1','participant_ids':[],'conditions':[
        {'name':'temperature','fact':tools.fact('-20–0 °C',[eid])},
        {'name':'time','fact':tools.fact('2 days',[eid])}]}]
    merge(base,[item])
    saved=tools.read(base/'dataset.json')['experiments'][0]
    assert saved['outcomes'][0]['fact']['value']['qualifier']=='lt'
    assert saved['steps'][0]['conditions'][0]['fact']['value']['minimum']==-20
    assert saved['steps'][0]['conditions'][1]['fact']['value']['unit']=='d'
    saved['outcomes'][0]['fact']['value']='trace'
    saved['steps'][0]['conditions'][0]['fact']['value']='r.t.'
    merge(base,[saved])
    assert tools.read(base/'dataset.json')['experiments'][0]['outcomes'][0]['fact']['value']=='trace'


def test_completeness_and_missing_state_are_checked(dataset):
    base,data=dataset
    item=record(data)
    item['completeness']='complete'
    data['documents'][0]['supplementary_material']={'status':'not_applicable','note':'no SI'}
    data['experiments']=[item]
    assert any('reactant, product' in e for e in tools.validate(data,base))
    item['completeness']='partial'
    item['outcomes'][0]['fact']['verification']='missing'
    assert any('non-null fact cannot be missing' in e for e in tools.validate(data,base))


def test_duplicate_evidence_and_steps_are_rejected(dataset):
    base,data=dataset
    data['documents'][0]['evidence'].append(copy.deepcopy(data['documents'][0]['evidence'][0]))
    assert any('duplicate evidence_id' in e for e in tools.validate(data,base))
    data['documents'][0]['evidence'].pop()
    item=record(data)
    item['steps']=[{'step_id':'s','participant_ids':[],'conditions':[]}, {'step_id':'s','participant_ids':[],'conditions':[]}]
    with pytest.raises(ValueError,match='duplicate step_id'):merge(base,[item])


def test_notes_quantity_warning_and_product_target_validation(dataset):
    base,data=dataset
    item=record(data)
    item['notes']=[tools.fact('10 equiv HOAc added',[item['evidence_ids'][0]])]
    assert tools.warnings(item)
    item['outcomes'][0]['target_entity_ids']=['fake-product']
    with pytest.raises(ValueError,match='unknown target'):merge(base,[item])


def test_numeric_without_unit_is_not_silently_inferred(dataset):
    base,data=dataset
    item=record(data)
    item['outcomes'][0]['fact']['value']='<5'
    with pytest.raises(ValueError,match='explicit structured quantity'):merge(base,[item])


def test_prepare_does_not_import_review_answers(dataset):
    base,data=dataset
    folder=base/'input';(folder/'化学解析').mkdir(parents=True)
    raw={'molecule_table':{'data':[]},'reaction_table':{'data':[]}}
    tools.write(folder/'化学解析/demonstration_tables.json',raw)
    tools.write(folder/'化学解析/反应_校正版.json',{'gold':'answer'})
    tools.write(folder/'化学解析/质量核对.json',{'gold':'answer'})
    assert tools.import_chem(data['documents'][0],folder,base)==[]
    assert not list((base/'assets').rglob('反应_校正版.json'))
    assert not list((base/'assets').rglob('质量核对.json'))


def test_time_at_room_temperature_remains_a_duration(dataset):
    base,data=dataset
    item=record(data)
    item['steps']=[{'step_id':'s1','participant_ids':[],'conditions':[
        {'name':'time_at_room_temperature','fact':tools.fact({'number':6,'unit':'h'},item['evidence_ids'])}]}]
    merge(base,[item])
    assert tools.read(base/'dataset.json')['experiments'][0]['steps'][0]['conditions'][0]['category']=='time'


def test_molecule_labels_are_text_and_smiles_parse_flag_is_computed(dataset):
    base,data=dataset
    item=record(data)
    eid=item['evidence_ids'][0]
    participant={'entity_id':'p1','role':'product','label':tools.fact('p1',[eid]),
                 'name':tools.fact(None),'smiles':tools.fact('CCO',[eid]),
                 'smiles_parseable':False,'structure_verified':True,'amounts':[]}
    item['participants']=[participant]
    merge(base,[item])
    saved=tools.read(base/'dataset.json')['experiments'][0]['participants'][0]
    assert saved['smiles_parseable'] is True
    assert saved['structure_verified'] is False
    participant['label']=tools.fact({'number':2,'unit':'mg'},[eid])
    with pytest.raises(ValueError):merge(base,[item])


def test_product_yield_recovery_and_conversion_stay_separate(dataset):
    base,data=dataset
    item=record(data)
    eid=item['evidence_ids'][0]
    item['outcomes']=[{'name':name,'fact':tools.fact({'number':number,'unit':'%'},[eid])}
                      for name,number in [('reported_yield_3a',8),('recovered_starting_material_yield',67),('reported_conversion',33)]]
    merge(base,[item])
    saved=tools.read(base/'dataset.json')['experiments'][0]
    assert [(f['category'],f['fact']['value']['number']) for f in saved['outcomes']]==[('yield',8),('recovery',67),('conversion',33)]


def test_stage_yield_is_not_recovery_based_on_global_role(dataset):
    base,data=dataset
    item=record(data)
    item['outcomes'][0]['name']='stage_1_yield'
    merge(base,[item])
    assert tools.read(base/'dataset.json')['experiments'][0]['outcomes'][0]['category']=='yield'


def test_loading_discussion_is_not_missing_amount_when_represented(dataset):
    base,data=dataset
    item=record(data)
    eid=item['evidence_ids'][0]
    item['participants']=[{'entity_id':'additive','role':'reagent','label':tools.fact('LiOAc·2H2O',[eid]),
        'name':tools.fact(None),'smiles':tools.fact(None),'smiles_parseable':None,'structure_verified':False,
        'amounts':[{'name':'equivalents','fact':tools.fact({'number':0.5,'unit':'equiv'},[eid])}]}]
    item['notes']=[tools.fact('No yield improvement was observed with more than 0.5 equiv LiOAc·2H2O.',[eid])]
    assert tools.warnings(item)==[]
    item['participants'][0]['amounts']=[]
    assert tools.warnings(item)


def test_legacy_query_projects_recovery_without_rewriting_original(dataset,capsys):
    base,data=dataset
    item=record(data)
    item['status']='needs_review'
    item['outcomes'][0]['name']='recovered_starting_material_yield'
    item['outcomes'][0]['category']='yield'
    data['experiments']=[item]
    tools.write(base/'dataset.json',data)
    before=(base/'dataset.json').read_bytes()
    capsys.readouterr()
    tools.query(argparse.Namespace(dataset=str(base/'dataset.json'),text='',include_unreviewed=True,category='yield'))
    assert tools.read(base/'dataset.json')==data
    import json
    assert json.loads(capsys.readouterr().out)==[]
    tools.query(argparse.Namespace(dataset=str(base/'dataset.json'),text='',include_unreviewed=True,category='recovery'))
    projected=json.loads(capsys.readouterr().out)
    assert projected[0]['matched_fields'][0]['category']=='recovery'
    assert projected[0]['matched_fields'][0]['stored_category']=='yield'
    assert (base/'dataset.json').read_bytes()==before


def test_table_dash_is_preserved_as_source_marker(dataset):
    base,data=dataset
    item=record(data)
    item['outcomes'][0]['fact']['value']='table dash (–)'
    merge(base,[item])
    assert tools.read(base/'dataset.json')['experiments'][0]['outcomes'][0]['fact']['value']=='table dash (–)'
