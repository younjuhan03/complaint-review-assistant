"""A short visitor-facing story, with technical detail kept optional."""
from pathlib import Path
import json
import math
import os
import sys
import pandas as pd
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cra.cli import ROOT, LOCAL, EVIDENCE, load_assets
from cra.model import classify_complaint, rule_decision
from cra.agent import run_agent, cost_preview

st.set_page_config(page_title='Complaint Review Assistant',page_icon='📨',layout='centered')
st.caption('A SMALL TEXT ANALYTICS PROJECT · JUHAN YOUN')
st.title('When should an AI assistant ask for human review?')
st.header('The question')
st.write('A complaint arrives. Should a system suggest a support team, or leave it for a person to check?')
st.header('What I tried')
st.write('I trained a simple text classifier on public consumer complaints, then added review rules. A small LLM assistant is implemented to call the classifier and read those same rules.')
st.caption('Four product categories. Team names are illustrative. No complaint is sent to a company and no customer receives a reply.')
summary_path=EVIDENCE/'summary.json'
summary=json.loads(summary_path.read_text()) if summary_path.exists() else None
st.header('What I found')
if summary:
    comparison=summary['full_test']; a=comparison['classifier_only'];b=comparison['python_review_rules']
    c1,c2=st.columns(2)
    c1.metric('All cases classified: error rate',f"{a['routed_error_rate']:.1%}")
    c2.metric('With rules: share sent for review',f"{b['review_rate']:.1%}")
    rate='not defined (no routed cases)' if b['routed_error_rate'] is None else f"{b['routed_error_rate']:.1%}"
    st.write(f"On {a['cases']:,} later complaints, the Python rules suggested a team for {b['route_suggestions']:,} cases. Among those suggestions, {rate} disagreed with the public product label.")
    st.caption('This is classifier + Python-rule evidence, not LLM-agent performance. Review does not mean a person corrected the case.')
    if summary['agent']['status']=='pending':st.info('Agent evaluation pending. No real LLM calls have been made in the published study.')
    else:
        st.write('Real LLM evaluation on the same fixed sample:')
        st.json(summary['agent'])
    with st.expander('See matched sample, all metrics and methods'):
        rows=[]
        for scope in ['full_test','matched_agent_sample']:
            for name,metrics in summary[scope].items():rows.append({'scope':scope,'method':name,**metrics})
        st.dataframe(pd.DataFrame(rows),hide_index=True)
        st.json(summary['policy'])
        st.write('Train: Jan–Mar 2024. Development: Apr 2024. Test: May–Jun 2024. No label, date, company response or other metadata is a model input. Model scores are uncalibrated.')
        cm=summary['confusion_matrix'];st.dataframe(pd.DataFrame(cm['rows_true_columns_predicted'],index=cm['labels'],columns=cm['labels']))
        st.caption('Confusion matrix: rows are public labels; columns are classifier predictions. This is a capped, roughly balanced sample, not the operational complaint mix.')
else:st.info('Results pending. Run the data preparation and training commands in README.')
st.header('Try an example')
examples={
 'Write my own':'',
 'Prepared example: card billing':'My credit card statement shows a purchase I did not make. I contacted the card issuer to dispute the charge, but the amount still appears on my bill.',
 'Prepared example: mortgage payment':'I sent my monthly mortgage payment before the due date. The mortgage servicer has not credited the payment to my home loan account and keeps adding late fees.',
 'Prepared example: deliberately unclear':'I have contacted the company several times about my account. The explanation is confusing and I still do not understand why the amount is wrong.'}
choice=st.selectbox('Choose an original illustrative example or write your own',list(examples))
text=st.text_area('English complaint (80–12,000 characters)',value=examples[choice],height=130,max_chars=12000,key='text_'+choice)
st.caption('Prepared examples were written for this demo; they are not copied consumer narratives or evaluation evidence. Do not enter names, account numbers or other personal information.')
mode=st.radio('Run mode',['Local Python review rules (no LLM)','Live LLM assistant'],horizontal=True)
assets_ready=(LOCAL/'model.joblib').exists() and (LOCAL/'policy.json').exists()
if not assets_ready:st.warning('The local model is not installed. Follow the README training steps; the saved findings above remain available.')
consent=False; live_ready=False
if mode=='Live LLM assistant':
    st.warning('A live run sends your entered complaint to OpenAI. It can incur API charges. A prior response may be loaded from the local cache. This is not a general chatbot.')
    live_ready=bool(os.environ.get('OPENAI_API_KEY') and os.environ.get('CRA_MODEL'))
    if not live_ready:st.info('Configure OPENAI_API_KEY and CRA_MODEL locally. Do not paste a key into this page or chat.')
    try:
        ip=float(os.environ['CRA_INPUT_USD_PER_MILLION']);op=float(os.environ['CRA_OUTPUT_USD_PER_MILLION'])
        if not all(math.isfinite(p) and p > 0 for p in [ip,op]): raise ValueError('Invalid price')
        estimate=cost_preview([text],ip,op)['planning_cost_usd']
        st.caption(f"Model: {os.environ.get('CRA_MODEL','not set')}. Planning allowance for one example: ${estimate:.4f} at configured prices. Maximum 3 requests.")
        consent=st.checkbox('I agree to send this text and incur the displayed API cost allowance.')
    except (KeyError,ValueError):
        st.info('Configure the two verified API price variables to show a cost preview before live execution.')
if st.button('Check this complaint',type='primary',disabled=not assets_ready or (mode=='Live LLM assistant' and not(live_ready and consent))):
    model,policy=load_assets()
    if mode.startswith('Local'):
        tool=classify_complaint(text,model);output=rule_decision(tool,policy)
        st.caption('Source: local classifier + Python rules. No LLM was called.')
        trace={'classify_complaint':tool,'get_review_policy':policy}
    else:
        with st.spinner('The LLM is calling tools and checking the review rules…'):
            import hashlib
            fingerprint=hashlib.sha256((LOCAL/'model.joblib').read_bytes()).hexdigest()
            record=run_agent(text,model,policy,fingerprint)
        output=record['output'];trace=record
        st.caption('Source: '+record['source'])
    st.subheader('Human review needed' if output['action']=='HUMAN_REVIEW' else 'Team suggestion available')
    st.write('**Suggested category:**',output['suggested_category'] or 'No valid suggestion')
    st.write('**Illustrative team:**',output['suggested_team'] or 'Unassigned')
    st.write('**Reason:**',output['reason'])
    st.caption('A suggestion is not a sent complaint. This demo does not establish urgency, harm, liability or a correct resolution. It cannot reliably identify every out-of-scope input.')
    with st.expander('Tool results and execution record'):st.json(trace)
st.header('What I learned')
st.write('A review rule can trade automatic suggestions for fewer wrong suggestions. That trade-off needs both numbers: how much the system handles, and how often those suggestions are wrong.')
st.write('I want to learn how to choose that boundary using business costs and real reviewer feedback. The LLM comparison is still pending; the rules already perform the basic boundary decision.')
st.caption('Reflection draft for Juhan to review in his own words. Implementation was developed with AI assistance. Findings are offline comparisons with public product labels, not measured business outcomes.')
