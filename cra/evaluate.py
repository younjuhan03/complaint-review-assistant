"""Coverage and error together, including every deferred case."""
import numpy as np

def metrics(truth, prediction, routed):
    truth=np.asarray(truth); prediction=np.asarray(prediction); routed=np.asarray(routed,dtype=bool)
    if len(truth) == 0 or len(truth)!=len(prediction) or len(truth)!=len(routed):
        raise ValueError('Nonempty, aligned evaluation arrays are required')
    wrong=truth!=prediction; bad=wrong & routed
    return {'cases':len(truth), 'route_suggestions':int(routed.sum()), 'human_reviews':int((~routed).sum()),
            'route_rate':float(routed.mean()), 'review_rate':float((~routed).mean()),
            'routed_error_rate':float(bad.sum()/routed.sum()) if routed.any() else None,
            'wrong_routes_per_all_cases':float(bad.mean()),
            'classifier_errors':int(wrong.sum()),
            'classifier_errors_deferred':int((wrong & ~routed).sum()),
            'fraction_classifier_errors_deferred':float((wrong & ~routed).sum()/wrong.sum()) if wrong.any() else None}

def compare(frame, model, policy):
    from cra.model import classify_complaint, rule_decision
    classifications=[classify_complaint(t,model) for t in frame.text]
    prediction=[r['suggested_category'] for r in classifications]
    decisions=[rule_decision(r,policy) for r in classifications]
    return {'classifier_only':metrics(frame.category,prediction,[True]*len(frame)),
            'python_review_rules':metrics(frame.category,prediction,[d['action']=='ROUTE_SUGGESTION' for d in decisions])}, classifications, decisions
