"""Reproducible commands; paid evaluation is separate and explicitly budget-gated."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from cra.data import download, clean
from cra.model import fit_model, choose_policy, scores
from cra.evaluate import compare, metrics

ROOT=Path(__file__).resolve().parents[1]
LOCAL=ROOT/'results/local'; EVIDENCE=ROOT/'docs/evidence'

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def load_assets():
    return joblib.load(LOCAL/'model.joblib'),json.loads((LOCAL/'policy.json').read_text())

def prepare(config):
    frame, manifest=download(config,ROOT/'data/raw')
    frame.to_json(ROOT/'data/sample.jsonl',orient='records',lines=True)
    frame,audit=clean(frame,config)
    frame.to_json(ROOT/'data/clean.jsonl',orient='records',lines=True)
    write(ROOT/'data/manifest.json',manifest);write(ROOT/'data/audit.json',audit)
    print(json.dumps(audit,indent=2))

def train(config):
    """Freeze policy using development rows before opening test metrics."""
    frame=pd.read_json(ROOT/'data/clean.jsonl',lines=True,dtype={'id':str,'date':str},convert_dates=False)
    train=frame[frame.split=='train'];dev=frame[frame.split=='development']
    model=fit_model(train); policy=choose_policy(model,dev,config)
    LOCAL.mkdir(parents=True,exist_ok=True);joblib.dump(model,LOCAL/'model.joblib')
    write(LOCAL/'policy.json',policy);write(LOCAL/'protocol_snapshot.json',config)
    test=frame[frame.split=='test'].sort_values(['date','id'])
    sample=test.sample(n=min(config['agent_sample_size'],len(test)),random_state=config['seed']).sort_values(['date','id'])
    sample.to_json(LOCAL/'agent_sample.jsonl',orient='records',lines=True)
    full,_,_=compare(test,model,policy);matched,tools,decisions=compare(sample,model,policy)
    pred,_,_=scores(model,test.text)
    write(LOCAL/'sample_decisions.json', [{'id':str(i),'truth':y,'tool':t,'python_decision':d}
        for i,y,t,d in zip(sample.id,sample.category,tools,decisions)])
    report=classification_report(test.category,pred,output_dict=True,zero_division=0)
    summary={'status':'classifier and Python rules evaluated; agent evaluation pending',
             'utc':datetime.now(timezone.utc).isoformat(), 'protocol':config,'policy':policy,
             'cleaning':json.loads((ROOT/'data/audit.json').read_text()),
             'sources':json.loads((ROOT/'data/manifest.json').read_text()),
             'protocol_sha256':digest(ROOT/'protocol.json'),'model_sha256':digest(LOCAL/'model.joblib'),
             'clean_data_sha256':digest(ROOT/'data/clean.jsonl'),
             'agent_sample_sha256':digest(LOCAL/'agent_sample.jsonl'),
             'full_test':full,'matched_agent_sample':matched,
             'matched_sample_class_counts':sample.category.value_counts().to_dict(),
             'classification_report':report,
             'confusion_matrix':{'labels':list(model.classes_), 'rows_true_columns_predicted':confusion_matrix(test.category,pred,labels=model.classes_).tolist()},
             'agent':{'status':'pending','attempted':0,'reason':'No API key configured; no paid calls authorized or made.'},
             'versions':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','joblib','streamlit']}}
    write(EVIDENCE/'summary.json',summary)
    print(json.dumps({'policy':policy,'full_test':full,'matched_sample':matched},indent=2))

def agent_command(command, approved):
    from cra.agent import run_agent,cost_preview
    summary=json.loads((EVIDENCE/'summary.json').read_text())
    if digest(LOCAL/'agent_sample.jsonl')!=summary['agent_sample_sha256']: raise ValueError('Frozen sample changed')
    if digest(LOCAL/'model.joblib')!=summary['model_sha256']: raise ValueError('Model artifact changed')
    sample=pd.read_json(LOCAL/'agent_sample.jsonl',lines=True,convert_dates=False)
    model_name=os.environ.get('CRA_MODEL')
    if not model_name: raise ValueError('Set CRA_MODEL; verify tool and JSON-schema support and current prices')
    ip=float(os.environ['CRA_INPUT_USD_PER_MILLION']);op=float(os.environ['CRA_OUTPUT_USD_PER_MILLION'])
    if not all(math.isfinite(p) and p > 0 for p in [ip,op]): raise ValueError('Verified positive finite prices are required')
    preview=cost_preview(sample.text,ip,op);preview['model']=model_name
    print(json.dumps(preview,indent=2))
    if command=='preview': return
    if approved is None or not math.isfinite(approved) or approved<preview['planning_cost_usd']:
        raise ValueError('No calls made: --approve-usd must cover the displayed planning allowance')
    if not os.environ.get('OPENAI_API_KEY'): raise ValueError('No calls made: configure key locally, never in chat')
    model,policy=load_assets();_,tools,_=compare(sample,model,policy);records=[]
    for text in sample.text:
        records.append(run_agent(text,model,policy,summary['model_sha256']))
        print(f'{len(records)}/{len(sample)} recorded',flush=True)
    prediction=[t['suggested_category'] for t in tools]
    outcome=metrics(sample.category,prediction,[r['output']['action']=='ROUTE_SUGGESTION' for r in records])
    uses=[u for r in records for u in r['usage']]
    input_tokens=sum(u.get('prompt_tokens',0) for u in uses);output_tokens=sum(u.get('completion_tokens',0) for u in uses)
    summary['agent']={'status':'evaluated','cases':len(records),'model':model_name,'prompt_version':'1.0',
        'utc':datetime.now(timezone.utc).isoformat(),'metrics':outcome,
        'failures':sum(r['failure'] is not None for r in records),
        'output_or_policy_failures':sum(r['failure_kind']=='output_or_policy' for r in records),
        'api_or_tool_failures':sum(r['failure_kind']=='api_or_tool' for r in records),
        'cached_cases':sum(r['source']=='cached LLM response' for r in records),
        'historical_prompt_tokens':input_tokens,'historical_completion_tokens':output_tokens,
        'estimated_historical_cost_usd':(input_tokens*ip+output_tokens*op)/1e6,
        'cost_note':'Recorded usage at configured prices; cached records are not charged again. Failed requests may have unreported usage.',
        'mean_original_latency_seconds':sum(r['latency_seconds'] for r in records)/len(records),
        'additional_deferrals_vs_rules':sum(r['output']['action']=='HUMAN_REVIEW' and d['action']=='ROUTE_SUGGESTION' for r,d in zip(records,compare(sample,model,policy)[2]))}
    summary['status']='classifier, Python rules and real LLM evaluated on the matched sample'
    write(EVIDENCE/'summary.json',summary)
    print(json.dumps(summary['agent'],indent=2))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','train','preview','agent-evaluate'])
    parser.add_argument('--approve-usd',type=float)
    args=parser.parse_args();config=json.loads((ROOT/'protocol.json').read_text())
    if args.command=='prepare': prepare(config)
    elif args.command=='train':train(config)
    else:agent_command(args.command,args.approve_usd)

if __name__=='__main__':main()
