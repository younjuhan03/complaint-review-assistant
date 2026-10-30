"""Visitor-facing flow tests; fixture responses are not study evidence."""
from pathlib import Path
import joblib
from streamlit.testing.v1 import AppTest
import cra.cli as cli

APP=Path(__file__).resolve().parents[1]/'app/streamlit_app.py'

class FixtureClassifier:
    classes_=['Checking or savings account','Credit card','Debt collection','Mortgage']
    def predict_proba(self,texts):
        import numpy as np
        # A controlled fixture exercises both UI branches; no demo output is hardcoded in the app.
        return np.array([[.05,.85,.05,.05] if 'credit card' in text.lower() else [.4,.35,.15,.1] for text in texts])

def test_findings_visible_without_model_or_key(tmp_path,monkeypatch):
    monkeypatch.setattr(cli,'LOCAL',tmp_path)
    at=AppTest.from_file(str(APP)).run(timeout=30)
    assert not at.exception
    assert at.title[0].value=='When should a complaint classifier ask for human review?'
    assert len(at.radio)==0
    assert len(at.checkbox)==0
    assert at.button[0].disabled
    assert len(at.metric)==3

def test_local_suggestion_and_review_with_no_network(tmp_path,monkeypatch):
    import json
    from cra.model import TEAMS
    monkeypatch.setattr(cli,'LOCAL',tmp_path)
    joblib.dump(FixtureClassifier(),tmp_path/'model.joblib')
    (tmp_path/'policy.json').write_text(json.dumps({'min_score':0.0,'min_margin':.1,'teams':TEAMS}))
    monkeypatch.setattr('urllib.request.urlopen',lambda *a,**kw: (_ for _ in ()).throw(AssertionError('Unexpected network call')))
    at=AppTest.from_file(str(APP)).run(timeout=30)
    at.selectbox[0].select('Prepared example: card billing').run()
    at.button[0].click().run()
    assert not at.exception
    assert at.subheader[0].value=='Team suggestion available'
    at.selectbox[0].select('Prepared example: deliberately unclear').run()
    at.button[0].click().run()
    assert not at.exception
    assert at.subheader[0].value=='Human review needed'
