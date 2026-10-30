"""Prepare public data, fit one classifier, and evaluate a fixed review policy locally."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from cra.data import download, clean
from cra.model import fit_model, choose_policy, scores
from cra.evaluate import compare

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
    # Explicit JSON rows keep dates as strings without pandas date-conversion warnings.
    with (ROOT/'data/clean.jsonl').open(encoding='utf-8') as source:
        frame=pd.DataFrame(json.loads(line) for line in source if line.strip())
    train=frame[frame.split=='train'];dev=frame[frame.split=='development']
    model=fit_model(train); policy=choose_policy(model,dev,config)
    LOCAL.mkdir(parents=True,exist_ok=True);joblib.dump(model,LOCAL/'model.joblib')
    write(LOCAL/'policy.json',policy);write(LOCAL/'protocol_snapshot.json',config)
    test=frame[frame.split=='test'].sort_values(['date','id'])
    full,_,_=compare(test,model,policy)
    pred,_,_=scores(model,test.text)
    report=classification_report(test.category,pred,output_dict=True,zero_division=0)
    summary={'status':'completed: local classifier and review-rule evaluation','schema_version':'1.1',
             'utc':datetime.now(timezone.utc).isoformat(), 'protocol':config,'policy':policy,
             'cleaning':json.loads((ROOT/'data/audit.json').read_text()),
             'sources':json.loads((ROOT/'data/manifest.json').read_text()),
             'protocol_sha256':digest(ROOT/'protocol.json'),'model_sha256':digest(LOCAL/'model.joblib'),
             'clean_data_sha256':digest(ROOT/'data/clean.jsonl'),
             'full_test':full,
             'classification_report':report,
             'confusion_matrix':{'labels':list(model.classes_), 'rows_true_columns_predicted':confusion_matrix(test.category,pred,labels=model.classes_).tolist()},
             'versions':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','joblib','streamlit']}}
    write(EVIDENCE/'summary.json',summary)
    print(json.dumps({'policy':policy,'full_test':full},indent=2))

def main():
    parser=argparse.ArgumentParser(description='Prepare data or train and evaluate the local classifier.')
    parser.add_argument('command',choices=['prepare','train'])
    args=parser.parse_args();config=json.loads((ROOT/'protocol.json').read_text())
    if args.command=='prepare': prepare(config)
    else: train(config)

if __name__=='__main__': main()
