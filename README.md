# Complaint Review Assistant
### When should a complaint classifier ask for human review?

**My finding:** a fixed review rule deferred 77 of 140 classification errors, while also sending 68 correctly classified cases for review. I evaluate that reduction alongside the additional workload it creates.

I compared classifying every complaint with reserving uncertain cases for a person. My study uses public CFPB complaints, a local TF-IDF + logistic regression model, and fixed Python review rules.

**Explore:** [findings](docs/results.md) · [methods](docs/methodology.md) · [my analytical reasoning](docs/learning_ko.md) · [local app instructions](docs/github_setup.md)

## My project in plain English

I asked **which complaints I should leave for a person instead of accepting a model's category suggestion**. I used public consumer-finance complaints to compare automatic classification with a policy that sends uncertain cases for human review.

- **What I built:** I combined a local text classifier, explicit review rules and a Streamlit app that runs without an API key.
- **How I evaluated it:** I trained on earlier complaints, selected my rules on the next month and evaluated them on later complaints.
- **What I learned:** I deferred 77 errors, but I also sent 68 correct classifications for review. I need to weigh fewer automatic errors against the extra work I create.

I use **deferral** to mean leaving a case for human review. I do not assume that a reviewer subsequently corrected it.

## What I found

On **1,022 complaints received in May–June 2024**:

| Policy | Team suggestions | Human review | Wrong / suggested | Wrong / all cases |
|---|---:|---:|---:|---:|
| Classify every case | 1,022 (100%) | 0 | 13.7% (140/1,022) | 13.7% |
| Apply review rules | 877 (85.8%) | 145 (14.2%) | 7.2% (63/877) | 6.2% |

I count disagreement with the public product label as an error. Deferring a case does not mean a person corrected it; I did not measure reviewer outcomes.

## My analytical decisions

- **Compare a policy with its baseline.** I use the same later complaints for both policies, so I can identify which errors are deferred and which correct predictions create extra work.
- **Select thresholds before later evaluation.** January–March data fit the model, April data select review thresholds, and May–June data evaluate the fixed policy.
- **Keep denominators visible.** The 7.2% error rate concerns the 877 suggestions; 6.2% uses all 1,022 cases. Neither figure alone describes the workload tradeoff.
- **Treat scores carefully.** A small gap between the two leading categories triggers review. I do not interpret the uncalibrated model scores as verified probabilities of correctness.

## What I learned and want to deepen

I learned that deciding when a model should defer can matter as much as its classification accuracy. My analysis counted the errors and workload shifted to review, but I had not measured the cost of different mistakes or what reviewers actually corrected. I want to learn more about probability calibration, cost-sensitive decisions and human–AI workflows, so I can choose and evaluate a review policy around the capacity and outcomes of a real team.

## My next validation step

For my next evaluation, I would fix a review-capacity limit and error-cost assumptions in advance, then measure actual reviewer corrections and time alongside automatic errors on a later sample.

## Explore the implementation

- `cra/data.py`: sampling, screening, duplicate checks and chronological splits.
- `cra/model.py`: text classification, threshold selection and review checks.
- `cra/evaluate.py`: coverage, errors and deferral accounting.
- `app/streamlit_app.py`: saved findings and local examples.

The app runs locally and requires no API key. First-time data preparation downloads about 178 MB of official archives. [Setup and launch instructions](docs/github_setup.md) explain the process.

## Evidence and limits

My headline figures come from my October 29 Windows run. The [evidence archive](docs/evidence/README.md) preserves both original runs and documents environment differences. The [verification record](docs/verification.md) separates software checks from model-performance evidence.

The sample covers four product categories. Public product labels are imperfect routing references, and team names are illustrative. I have not measured actual reviewer corrections, time savings or customer outcomes. A practical policy would require a company's own case mix, error costs and capacity.

## AI-assisted development

I used AI tools to support project development, including code and documentation. I take responsibility for the analytical choices and interpretations presented here, and I document the data, comparisons, assumptions and limitations behind my conclusions. I distinguish AI assistance during development from the models I actually implement; I describe those models in the methods rather than imply that I built an LLM-based system.
