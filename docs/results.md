# When should a complaint classifier ask for human review?

**Completed local study · October 29, 2026**

## The question

A complaint classifier can suggest a support team, but some complaints are ambiguous. I explored whether a simple review rule could reduce wrong suggestions while making the amount of work left for people visible.

## What I tried

Using CFPB's official historical complaint archive, I selected four product categories before fitting: Credit card; Checking or savings account; Mortgage; Debt collection. Fixed screening, sampling and duplicate checks left 3,192 narratives. A TF-IDF + logistic regression model learned from 1,681 January–March 2024 cases. April's 489 cases selected review thresholds; May–June's 1,022 cases evaluated the fixed policy. Only narrative text entered the model.

The baseline classified every case. The review policy deferred invalid inputs and cases where the two leading model scores were less than 0.1 apart. The chosen absolute-score threshold was zero, so that restriction was inactive. Scores were not calibrated as probabilities of correct classification. A company's acceptable error tolerance was not established.

## What I found

| Later test set: 1,022 cases | Classify every case | Use review rules |
|---|---:|---:|
| Team suggestions | 1,022 (100%) | 877 (85.8%) |
| Human review | 0 | 145 (14.2%) |
| Wrong suggestions | 140 | 63 |
| Wrong / suggested | 13.7% | 7.2% |
| Wrong / all cases | 13.7% | 6.2% |
| Original classifier errors deferred | 0/140 | 77/140 (55%) |

The rule deferred 77 errors but also 68 predictions that agreed with the public product label. It therefore reduced wrong automatic suggestions at the expense of additional review. It still issued 63 wrong suggestions. Deferred cases were not assumed to be corrected by a person.

## What this establishes

For this sample and fixed policy, review rules created a measurable trade-off between automatic coverage and disagreement with reference labels. This is a local text-classification and decision-rule experiment. It is complete without an external language model.

Public product selections are imperfect routing reference labels. Product domains can overlap in one complaint, and the capped sample does not reproduce a real company's complaint mix. Language screening, template removal and out-of-scope input detection are imperfect. Team names are project-defined examples. Neither category nor score establishes urgency, harm or liability.

No actual reviewer corrections, employee time, customer satisfaction or operating cost savings were measured. The experiment cannot show that human+AI outperforms AI alone or that the policy should be deployed.

## Reflection draft for Juhan

I learned to show coverage and error together. A system can appear more reliable simply by refusing more cases, so the work left for people must be counted. I want to learn how the costs of wrong routing and reviewer capacity should shape the review boundary. This experiment is a starting point for that question, not a production recommendation.

This is an AI-assisted reflection draft for Juhan to assess and revise in his own words.

## Reproduction and final scope

Headline results use Juhan's October 29 Windows run. Its protocol, cleaned-data and fixed audit-sample hashes match the initial development run; the thresholds are unchanged. Package versions differ, including scikit-learn 1.8.0 → 1.9.1, and a few predictions differ. Environment differences are a plausible explanation, not an experimentally isolated cause. Both original run files are archived, and the newer figures were not chosen for better performance. This is the same test data, not new independent validation.

An optional LLM extension was removed from the final scope after setup exploration. An unsuccessful optional connection attempt is not included as evidence of model performance or of agent effectiveness. The completed comparison above uses only the classifier and Python rules. Scope simplification did not retune the model, alter the review thresholds, or select different test cases.
