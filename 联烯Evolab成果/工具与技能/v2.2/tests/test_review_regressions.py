import importlib.util
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1]/'skills/chemical-reaction-extraction/scripts'
sys.path.insert(0,str(SCRIPTS))
from record_quality import category, warnings
spec=importlib.util.spec_from_file_location('review_tools',SCRIPTS/'reaction_tools.py')
tools=importlib.util.module_from_spec(spec);spec.loader.exec_module(tools)

def test_operation_does_not_match_ratio_substring():
    assert category('warming_operation')=='operation'
    assert category('CO2_operation')=='operation'
    assert category('separation')=='other'
    assert category('product_ratio')=='selectivity'
    assert category('diastereomeric_ratio')=='selectivity'
    assert category('n_BuLi_solution_solvent')=='solvent'

def test_markdown_retains_reagent_doses_and_source_conflict(tmp_path):
    rec=tools.empty_record('doc_example','example',['p1'],'reported_experiment')
    rec['participants']=[{'entity_id':'AuCl','role':'catalyst','label':tools.fact('AuCl',['p1']),
                         'name':tools.fact(None),'smiles':tools.fact(None),
                         'amounts':[{'name':'amount','fact':tools.fact({'number':0.23,'unit':'mmol'},['p1'])}]}]
    rec['notes']=[tools.fact('Source conflict: figure 5 mol%; text 0.23 mmol',['p1'])]
    tools.write(tmp_path/'dataset.json',{'documents':[{'document_id':'doc_example','evidence':[{'evidence_id':'p1','page':1}]}],
                                        'experiments':[rec],'candidates':[]})
    tools.report(tmp_path)
    md=(tmp_path/'文献实验记录.md').read_text()
    assert '0.23' in md and 'mmol' in md and 'Source conflict' in md

def test_temperature_name_is_not_a_structured_temperature():
    r={'steps':[{'conditions':[{'name':'time_at_minus_20','category':'time','fact':{'value':{'number':22,'unit':'h'}}}]}]}
    assert any('paired temperature' in w for w in warnings(r))
    r['steps'][0]['conditions'].append({'name':'temperature','category':'temperature','fact':{'value':{'number':-20,'unit':'°C'}}})
    assert warnings(r)==[]
