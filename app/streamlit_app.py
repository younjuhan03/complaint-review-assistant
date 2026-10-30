"""A short local study: one classifier, one review policy, no external inference service."""
from pathlib import Path
import hashlib
import json
import sys
import pandas as pd
import streamlit as st
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cra.cli import LOCAL, EVIDENCE, load_assets
from cra.model import classify_complaint, rule_decision

st.set_page_config(page_title='Complaint Review Assistant',page_icon='📨',layout='centered')
st.caption('A SMALL TEXT ANALYTICS PROJECT · JUHAN YOUN')
st.title('When should a complaint classifier ask for human review?')
st.header('The question')
st.write('A customer complaint arrives. When should a system suggest a support team, and when should a person check it first?')
st.header('What I tried')
st.write('I used public consumer complaints to compare two approaches: suggest a team for every complaint, or leave closely competing predictions for human review.')
st.caption('One text classifier and fixed Python rules. All predictions run on your computer. Four product categories; team names are illustrative.')
summary_path=EVIDENCE/'summary.json'
summary=json.loads(summary_path.read_text()) if summary_path.exists() else None
st.header('What I found')
if summary:
    comparison=summary['full_test'];a=comparison['classifier_only'];b=comparison['python_review_rules']
    def percent(value):return 'Not defined' if value is None else f'{value:.1%}'
    c1,c2,c3=st.columns(3)
    c1.metric('All cases classified: error',percent(a['routed_error_rate']))
    c2.metric('With review: error among suggestions',percent(b['routed_error_rate']))
    c3.metric('Left for human review',percent(b['review_rate']))
    st.write(f"On {a['cases']:,} later complaints, the review rule suggested a team for {b['route_suggestions']:,} and left {b['human_reviews']:,} for a person. It deferred {b['classifier_errors_deferred']:,} of the classifier's {a['classifier_errors']:,} errors.")
    correct_reviews=b['human_reviews']-b['classifier_errors_deferred']
    st.info(f"The trade-off: fewer wrong suggestions, with more cases for people to check. {correct_reviews:,} deferred cases already matched the public label. Sending a case to review does not mean it was corrected.")
    st.caption('“Error” means disagreement with a public product label. These labels are not perfect business-routing truth. This is an offline study, not measured business savings.')
    with st.expander('See the full comparison and methods'):
        rows=[{'Method':'Classify every case' if name=='classifier_only' else 'Use review rules',
               'Cases':v['cases'],'Team suggestions':v['route_suggestions'],'Human review':v['human_reviews'],
               'Error among suggestions':percent(v['routed_error_rate']),
               'Wrong suggestions / all cases':percent(v['wrong_routes_per_all_cases']),
               'Base errors deferred':percent(v['fraction_classifier_errors_deferred'])} for name,v in comparison.items()]
        st.dataframe(pd.DataFrame(rows),hide_index=True)
        st.write('Train: January–March 2024. Review-rule selection: April. Evaluation: May–June. Only narrative text enters the model. TF-IDF + logistic regression; no model search.')
        st.write('The rule and error target were chosen using development data. They are not a business-approved risk policy or a future guarantee.')
        st.json(summary['policy'])
        cm=summary['confusion_matrix'];st.caption('Rows: public labels. Columns: predictions.')
        st.dataframe(pd.DataFrame(cm['rows_true_columns_predicted'],index=cm['labels'],columns=cm['labels']))
        st.caption('The published findings use the October 29 Windows run. Data and threshold choices matched the initial run; a few predictions differed across library versions. Archived runs are retained in the repository.')
else:st.info('Study results are not installed yet. Follow the README preparation and training steps.')

st.header('Try an example')
examples={
 'Write my own':'',
 'Prepared example: card billing':'My credit card statement shows a purchase I did not make. I contacted the card issuer to dispute the charge, but the amount still appears on my bill.',
 'Prepared example: mortgage payment':'I sent my monthly mortgage payment before the due date. The mortgage servicer has not credited the payment to my home loan account and keeps adding late fees.',
 'Prepared example: deliberately unclear':'I have contacted the company several times about my account. The explanation is confusing and I still do not understand why the amount is wrong.'}
choice=st.selectbox('Choose an illustrative example or write your own',list(examples))
text=st.text_area('English complaint (80–12,000 characters)',value=examples[choice],height=130,max_chars=12000,key='text_'+choice)
st.caption('Prepared examples were written for this demo, not copied from consumers or used as evaluation evidence. Example results may vary; no example is forced to a particular action. Avoid entering personal information.')
st.caption('Local execution · no API key or usage charge · entered text is not sent to an external AI service or saved by this app.')
assets_ready=(LOCAL/'model.joblib').exists() and (LOCAL/'policy.json').exists()
if not assets_ready:st.warning('The saved study is available above. To try examples, prepare the data and train the local model using the README commands.')
if st.button('Check this complaint',type='primary',disabled=not assets_ready):
    try:
        model,policy=load_assets()
        classification=classify_complaint(text,model)
        output=rule_decision(classification,policy)
        review=output['action']=='HUMAN_REVIEW'
        st.subheader('Human review needed' if review else 'Team suggestion available')
        st.write('**Provisional category:**' if review else '**Suggested category:**',output['suggested_category'] or 'No valid suggestion')
        st.write('**Illustrative team:**',output['suggested_team'] or 'Unassigned')
        st.write('**Reason:**',output['reason'])
        if review and output['suggested_category']:st.caption('The category is a candidate only. A person needs to check before routing.')
        st.caption('No complaint has been sent. This model does not establish urgency, harm, liability or a correct resolution, and cannot reliably reject every out-of-scope input.')
        with st.expander('See model scores and review checks'):
            if classification['valid_input']:
                table=pd.DataFrame([{'Category':k,'Model score':v} for k,v in classification['scores'].items()]).sort_values('Model score',ascending=False)
                st.dataframe(table,hide_index=True)
                st.write(f"Top-two score gap: {classification['margin']:.3f}; required gap: {policy['min_margin']:.3f}.")
                st.caption('Scores are uncalibrated. They are not verified probabilities of being correct.')
            st.json({'classification':classification,'review_policy':policy,'decision':output})
            current_hash=hashlib.sha256((LOCAL/'model.joblib').read_bytes()).hexdigest()
            if summary and current_hash!=summary.get('model_sha256'):st.caption('This local model differs from the model fingerprint of the saved study. Example behavior may differ; retraining updates the local aggregate file.')
    except Exception:
        st.error('The local model could not complete this check. Leave the case for human review and check the model installation; no team suggestion was issued.')

st.header('What I learned')
st.write('A classifier does not need to handle every case. Review rules can reduce wrong suggestions, but people must check more cases—including some the model already classified correctly.')
st.write('I want to learn how to choose that boundary using the costs of wrong routing and the capacity of human reviewers. This study measures the trade-off; it does not establish the best policy for a real company.')
st.caption('Reflection draft for Juhan to review in his own words. Implementation and initial writing were AI-assisted. Public complaint data: CFPB; no affiliation or endorsement.')
