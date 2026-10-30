"""Software tests use small fixtures; the published study uses real CFPB data."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from cra.data import clean
from cra.model import rule_decision, choose_policy, classify_complaint
from cra.evaluate import metrics

POLICY={'min_score':0.0,'min_margin':.1,'teams':{'Credit card':'Card support'}}

def test_coverage_error_and_deferral_are_counted_together():
    result=metrics(['a','b','b','a'],['a','a','a','a'],[True,False,True,False])
    assert result['route_rate']==.5
    assert result['routed_error_rate']==.5
    assert result['wrong_routes_per_all_cases']==.25
    assert result['fraction_classifier_errors_deferred']==.5
    assert result['human_reviews']==2

def test_zero_denominators_remain_undefined():
    result=metrics(['a','b'],['a','a'],[False,False])
    assert result['routed_error_rate'] is None
    assert result['fraction_classifier_errors_deferred']==1
    assert metrics(['a'],['a'],[True])['fraction_classifier_errors_deferred'] is None
    with pytest.raises(ValueError):metrics([],[],[])
    with pytest.raises(ValueError):metrics(['a'],['a'],[])

def test_review_boundary_and_illustrative_team():
    classification={'valid_input':True,'suggested_category':'Credit card','top_score':.6,'margin':.099}
    decision=rule_decision(classification,POLICY)
    assert decision['action']=='HUMAN_REVIEW'
    assert decision['suggested_team']=='Card support'
    classification['margin']=.1
    assert rule_decision(classification,POLICY)['action']=='ROUTE_SUGGESTION'

def test_invalid_text_never_calls_the_model():
    class Forbidden:
        def predict_proba(self,text):pytest.fail('Invalid input reached the model')
    for text in ['', 'short', None, '1234567890 '*20]:
        result=classify_complaint(text,Forbidden())
        assert result['valid_input'] is False
        assert rule_decision(result,POLICY)['action']=='HUMAN_REVIEW'
        assert rule_decision(result,POLICY)['suggested_team'] is None

def test_policy_selection_uses_development_scores(monkeypatch):
    monkeypatch.setattr('cra.model.scores',lambda model,texts:(np.array(['a','a','b','b']),np.array([.9]*4),np.array([.4,.05,.4,.05])))
    dev=pd.DataFrame({'text':['x']*4,'category':['a','b','b','a']})
    config={'score_grid':[0.0],'margin_grid':[0.0,.1], 'minimum_development_routes':2,'development_routed_error_target':.1}
    policy=choose_policy(None,dev,config)
    assert policy['min_margin']==.1
    assert policy['development_routes']==2
    assert policy['development_routed_error']==0

def test_policy_defers_everything_if_no_candidate_qualifies(monkeypatch):
    monkeypatch.setattr('cra.model.scores',lambda m,t:(np.array(['a','a']),np.array([.9,.9]),np.array([.4,.4])))
    dev=pd.DataFrame({'text':['x','y'],'category':['b','b']})
    config={'score_grid':[0.0],'margin_grid':[0.0,.1],'minimum_development_routes':1,'development_routed_error_target':.1}
    policy=choose_policy(None,dev,config)
    assert policy['min_score']>1 and policy['development_routes']==0

def test_duplicates_keep_earliest_and_split_by_time():
    base='The mortgage payment was not applied to my account and I have asked for an explanation. '
    frame=pd.DataFrame([
        {'id':'1','date':'2024-01-01','category':'Mortgage','text':base*2},
        {'id':'2','date':'2024-04-01','category':'Mortgage','text':base*2},
        {'id':'3','date':'2024-04-01','category':'Mortgage','text':'The escrow insurance has changed after the property tax adjustment and my mortgage bill is incorrect.'},
        {'id':'4','date':'2024-05-01','category':'Mortgage','text':'I cannot obtain my payoff statement from the servicer after selling my house and closing the loan.'}])
    config={'min_characters':80,'near_duplicate_cosine':.93,'train_before':'2024-04-01','test_from':'2024-05-01','categories':['Mortgage']}
    result,audit=clean(frame,config)
    assert '2' not in set(result.id)
    assert result.set_index('id').loc['1','split']=='train'
    assert result.set_index('id').loc['4','split']=='test'
    assert audit['exact_normalized_duplicates_removed']==1

def test_published_aggregate_arithmetic():
    s=json.loads((Path(__file__).resolve().parents[1]/'docs/evidence/summary.json').read_text())
    a=s['full_test']['classifier_only'];b=s['full_test']['python_review_rules']
    cm=s['confusion_matrix']['rows_true_columns_predicted']
    assert sum(map(sum,cm))==a['cases']==b['cases']
    assert sum(sum(row)-row[i] for i,row in enumerate(cm))==a['classifier_errors']
    wrong=a['classifier_errors']-b['classifier_errors_deferred']
    assert b['routed_error_rate']==wrong/b['route_suggestions']
    assert b['wrong_routes_per_all_cases']==wrong/b['cases']
    assert b['route_suggestions']+b['human_reviews']==b['cases']
    assert s['status'].startswith('completed')
