"""One text model and a separately selected, deterministic review policy."""
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from cra.data import normalize, english_like

TEAMS = {'Credit card': 'Card support', 'Checking or savings account': 'Deposit account support',
         'Mortgage': 'Mortgage support', 'Debt collection': 'Collections complaint review'}

def fit_model(train):
    """Learn word weights using training narratives only, never dates or product fields."""
    model = make_pipeline(TfidfVectorizer(ngram_range=(1,2), min_df=2, max_features=20000),
                          LogisticRegression(C=1.0, max_iter=500, random_state=42))
    model.fit(train.text.map(normalize), train.category)
    return model

def scores(model, texts):
    probabilities = model.predict_proba([normalize(t) for t in texts])
    ordered = np.sort(probabilities, axis=1)
    return model.classes_[probabilities.argmax(axis=1)], ordered[:,-1], ordered[:,-1]-ordered[:,-2]

def classify_complaint(text, model):
    """Return model scores and validity; scores are not calibrated correctness probabilities."""
    valid = isinstance(text, str) and 80 <= len(text.strip()) <= 12000 and english_like(text)
    if not valid:
        return {'suggested_category': None, 'scores': {}, 'top_score': None, 'margin': None,
                'valid_input': False, 'scores_calibrated': False,
                'input_note': 'Use 80–12,000 characters of English complaint text.'}
    p = model.predict_proba([normalize(text)])[0]
    rank = np.argsort(p)[::-1]
    return {'suggested_category': str(model.classes_[rank[0]]),
            'scores': {str(k): float(v) for k,v in zip(model.classes_,p)},
            'top_score': float(p[rank[0]]), 'margin': float(p[rank[0]]-p[rank[1]]),
            'valid_input': True, 'scores_calibrated': False,
            'input_note': 'English screening is heuristic; out-of-scope detection is not guaranteed.'}

def choose_policy(model, dev, config):
    """Maximize development coverage under a stated empirical error target; no guarantee."""
    prediction, top, margin = scores(model, dev.text)
    candidates=[]
    for threshold in config['score_grid']:
        for gap in config['margin_grid']:
            route=(top >= threshold) & (margin >= gap)
            error=float(np.mean(prediction[route] != dev.category.to_numpy()[route])) if route.any() else None
            if route.sum() >= config['minimum_development_routes'] and error <= config['development_routed_error_target']:
                candidates.append((int(route.sum()), -error, threshold, gap))
    if candidates:
        count, negerror, threshold, gap=max(candidates)
        error=-negerror
    else:
        count, error, threshold, gap=0,None,1.01,0.0
    return {'version':'1.0', 'min_score':threshold, 'min_margin':gap, 'teams':TEAMS,
            'score_note':'Uncalibrated model scores; not probability of being correct.',
            'development_routes':count, 'development_routed_error':error,
            'development_target':config['development_routed_error_target'],
            'team_note':'Illustrative mapping created for this project, not CFPB or company teams.'}

def rule_decision(result, policy):
    """Apply the fixed review policy and explain which check determined the action."""
    category=result['suggested_category']; reasons=[]
    if not result['valid_input']: reasons.append('Input failed the length or English screening check.')
    else:
        if result['top_score'] < policy['min_score']: reasons.append('The model score is below the review threshold.')
        if result['margin'] < policy['min_margin']: reasons.append('The two leading categories are too close.')
    return {'suggested_category': category, 'suggested_team':policy['teams'].get(category),
            'action':'HUMAN_REVIEW' if reasons else 'ROUTE_SUGGESTION',
            'reason':' '.join(reasons) if reasons else 'Model score and separation meet the fixed review rules.',
            'checks_used':['input_screen','classifier_scores','review_policy']}
