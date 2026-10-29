# Methodology

## Source and permitted use

The dataset is the [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/). Its official page permits public use, analysis and building on its data. [Field definitions](https://cfpb.github.io/api/ccdb/fields.html) describe product as consumer-selected. These classifications are reference labels, not independently adjudicated routing truth.

On 2026-10-27, the current API was reachable but historical text was absent. Official [September 2026 release notes](https://cfpb.github.io/api/ccdb/release-notes.html) document narrative removal. We used the [official narrative archive](https://www.consumerfinance.gov/foia-requests/foia-electronic-reading-room/cfpb-consumer-complaint-database-narratives-archive/) instead. Only the September 2023–March 2024 and April–July 2024 ZIP partitions were downloaded (178,023,227 bytes combined); the complete database was not downloaded. Download provenance, checksums and counts appear in the aggregate evidence JSON.

The [website legal notice](https://www.consumerfinance.gov/privacy/website-privacy-policy/) distinguishes CFPB-created public-domain material from third-party material. This project does not claim that consumer-authored text has a separate blanket public-domain license. Raw archives, narratives, IDs and fitted vocabulary stay out of the public repository. Public examples are original illustrations, not copied complaints. No CFPB affiliation or endorsement is implied.

## Scope fixed before training

The user selected four categories before model evaluation: **Credit card; Checking or savings account; Mortgage; Debt collection**. These are product domains, not specific issue types, urgency or harm levels. The scope is January–June 2024. A small source inspection confirmed fields, label availability and plausible narrative text before fitting.

Eligibility is 80–12,000 stripped characters and at least three distinct words from `the, and, my, was, have, with, that, this, from, not, for`. This is an English screening heuristic, not a validated language detector. It can reject valid English or retain other-language text. Missing/short, long and heuristic-excluded counts are recorded separately during archive scanning.

For each month and product, retain the 150 lowest SHA256(`42:complaint_id`) values after eligibility checks. This capped sampling is reproducible but deliberately changes natural product frequencies. Coverage and error rates are not estimates for all CFPB complaints or a company's incoming queue. No replacement sampling is performed after deduplication.

Sort by date and ID, remove repeated IDs, then normalize case, repeated-X redactions, digits and whitespace. Remove exact normalized copies. Remove later near copies with character 3–5-gram cosine similarity at least 0.93, using a nonlearned HashingVectorizer with 2^18 features. Every retained earlier narrative is considered, across split boundaries. Retaining the earliest example avoids replacing training data with future text. This is a heuristic defense against templates and near copies, not proof that all related submissions have been identified.

From 3,600 selected rows, remove 252 exact normalized duplicates and 156 further near copies: **3,192 retained**. Train Jan–Mar: 1,681. Development April: 489. Test May–June: 1,022. Categories and protocol were not changed after seeing results. The later repeated training command merely completed metadata recording after installing a missing dependency; it used the same configuration.

## Classifier and policy

The model sees normalized narrative text only. TF-IDF uses word unigrams/bigrams, min_df=2, max_features=20,000. LogisticRegression uses C=1, max_iter=500, seed=42, without class weighting or model search. Vocabulary, IDF and coefficients are fitted only on training rows. Complaint ID, dates, product labels, companies and post-submission outcomes are not features.

Class scores are logistic regression `predict_proba` outputs; no calibration experiment was performed. They must not be interpreted as probability that the classification is correct.

Before inspecting test metrics, select from score thresholds `[0,.4,.5,.6,.7,.8,.9,1.01]` and top-two-score gaps `[0,.1,.2]`. Choose maximum development coverage subject to at least 20 suggestions and empirical routed error <=10%. Ties prefer lower error, then larger thresholds. If no candidate qualifies, defer all. This 10% is an illustrative development constraint, not a justified business tolerance or statistical guarantee.

The selected policy has **min_score=0 and min_margin=0.1**: the absolute-score restriction is inactive. The operative ambiguity rule is the top-two gap. Development: 433/489 suggested, 35/433 errors (8.08%). Invalid input also requires review. The frozen policy is applied unchanged to later test cases.

Teams are fictional mappings: Card support; Deposit account support; Mortgage support; Collections complaint review. The model does not detect all out-of-domain inputs or infer urgency, liability or customer harm.

## LLM comparison

A seeded uniform sample of 100 retained test rows is fixed and hashed before LLM execution. The all-route classifier, Python rules and real agent must use those same cases. Full-test numbers are supplementary; do not compare full-test classifier numbers to a 100-case agent result.

The LLM chooses which of two tools to call first, reads both outputs, and generates structured JSON. The Python tool adapter binds classification to the original complaint, with no replacement-text parameter exposed to the LLM. Two required tool calls and one final request are the maximum. A validator enforces category/team consistency and mandatory review, while allowing extra deferral. These guards are ordinary code; the LLM's added role is constrained tool orchestration and explanation, not a new classifier.

Untrusted complaint instructions cannot add tools or alter policy. Missing tools, unauthorized arguments, invalid JSON, rule overrides, truncation and API/tool failures become HUMAN_REVIEW, with a failure record. Such cases remain in the denominator. Tests use fake transports solely to test these software controls, not to measure real agent performance. The validator cannot prove that every free-text explanation is semantically sound; trace review is still needed. No live prompt-injection robustness claim is made.

Cache keys include input, model ID, model-artifact fingerprint, policy, prompt and tool schemas. Responses including failures are cached. Changing any of these creates a new experiment; do not silently replace inconvenient failures. Account access and provider integration remain unverified until an authorized real smoke test.

## Metric definitions

| Metric | Definition |
|---|---|
| Route rate | Suggested cases / all cases |
| Review rate | Deferred cases / all cases |
| Routed error | Wrong suggestions / suggested cases; undefined if none |
| Wrong routes per all cases | Wrong suggestions / all cases |
| Errors deferred | Base classifier errors sent to review / all base classifier errors; undefined if none |

No human correction is simulated. Agent failures, violations, recorded usage and original latency will be reported after real execution. Cached original usage is historical, not a new charge. Failed calls can have unknown usage; pricing calculations are estimates, not invoices. No operating-cost, time-saving, satisfaction or Human+AI superiority claims are supported.

## Reproduction record

The current aggregate file records Juhan's October 29 local run. Its protocol, cleaned-data and agent-sample file hashes match the initial development run, and the selected threshold pair remains (0, 0.1). Packages differ, including scikit-learn 1.8.0 → 1.9.1. The small change in predictions is consistent with environment differences, but no controlled test isolates the cause. Preserve the [initial aggregates](evidence/initial_run_2026-10-27.json) alongside [current aggregates](evidence/summary.json); this is not a new independent validation set.
