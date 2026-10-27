"""A visitor can read saved findings without local data or a key."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

def test_first_screen_and_live_consent(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    app=Path(__file__).resolve().parents[1]/'app/streamlit_app.py'
    at=AppTest.from_file(str(app)).run(timeout=30)
    assert not at.exception
    assert at.title[0].value=='When should an AI assistant ask for human review?'
    at.radio[0].set_value('Live LLM assistant').run()
    assert not at.exception
    assert at.button[0].disabled
