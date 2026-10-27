# When should an AI assistant ask for human review?

**Offline findings · 2026-10-27 · real LLM evaluation pending**

I explored a narrow business question: when classifying an incoming complaint, when should a system suggest a team and when should a person check the case? The aim was to connect a prediction to a decision, using tools I could learn to explain before graduate study.

## What was tested

The source is CFPB's official historical complaint narrative archive. Four product domains were chosen before evaluation. After fixed eligibility, sampling and duplicate checks, 3,192 narratives remained. A TF-IDF + logistic regression model learned from 1,681 January–March 2024 complaints. April's 489 cases selected a review rule. The rule was then frozen for 1,022 May–June cases. Only complaint text was used as input.

The classifier-only method always suggested one category. The Python comparator deferred cases whose two leading model scores were less than 0.1 apart. Invalid inputs also require review. Model scores have not been calibrated. Reference labels are public product selections, not guaranteed business-routing truth.

## What the numbers say

| Later test set: 1,022 cases | Classifier only | Classifier + Python rules |
|---|---:|---:|
| Suggested cases | 1,022 (100%) | 877 (85.8%) |
| Human review | 0 | 145 (14.2%) |
| Wrong suggestions | 141 | 62 |
| Wrong / suggested | 13.8% | 7.1% |
| Wrong / all cases | 13.8% | 6.1% |
| Base errors deferred | 0/141 | 79/141 (56.0%) |

The rule reduced wrong automatic suggestions while giving up some automatic coverage. It did not remove all errors. It also deferred 66 cases that agreed with the public label. Those cases illustrate the additional review workload; actual reviewer time was not measured.

For the **fixed 100-case sample reserved for the LLM comparison**, the classifier made 10 wrong suggestions out of 100. The Python rules suggested 84, including 4 wrong suggestions; 16 were deferred, including 6 of the original 10 errors. These sample results differ from the full test set and must be the baselines used for the real agent comparison.

## What the agent has and has not demonstrated

The implementation allows an LLM to call a classifier tool and a review-policy tool and return a validated structured result. The LLM cannot replace the category, invent a team or loosen mandatory review. A deterministic rule can already make the basic boundary decision.

**No real LLM calls have been made.** Agent error rates, extra deferrals, rule violations, output failures, API failures, usage and latency are pending. Software tests verify mocked tool-flow and failure controls, not agent quality. There is no evidence yet that the LLM adds business value. Its explanation quality would also need human inspection.

## Interpretation and limits

This is a small, capped, roughly balanced public-data sample. It is not a representative customer queue. The source is historical and public narratives may be selective; language screening and near-copy removal are imperfect. Product domains can overlap in a single complaint. Neither labels nor scores establish urgency, harm or liability. Team names are illustrative project choices.

The development target of <=10% suggested-case error was an exploratory choice. It is not a company's acceptable-risk policy or a guarantee for future data. We did not measure actual human corrections, task time, satisfaction or cost savings.

## Reflection draft for Juhan to review

A useful result was learning to show coverage and error together. A system can appear safer simply by refusing more cases, so I need to show what remains for people. I would like to learn how business costs and reviewer capacity should shape that boundary, and whether a tool-using assistant earns its additional cost through useful, reliable explanations.

This paragraph is a draft, not a statement that Juhan has already independently interpreted every result. Implementation and initial writing were AI-assisted. The next learning step is to explain one routed case, one deferred case and one error using the code and recorded evidence.
