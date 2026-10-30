# Verification — local completed scope

Checked October 29, 2026.

- `python -m pytest -q`: **10 passed**. Tests cover coverage/error/deferral arithmetic, undefined denominators, review-threshold boundaries, invalid input, development-only policy selection, all-review fallback, duplicate/time split behavior, published aggregate arithmetic, the saved-findings screen without a model, and both example UI branches with network access blocked.
- The simplified training command was also run in an isolated temporary directory using the original real cleaned CFPB data. It completed a 1,022-case evaluation and generated the local-only summary schema. Published Windows evidence was not overwritten by this integration check.
- Streamlit AppTest using that actual fitted model: card billing produced a team suggestion; the unclear example produced human review. No exceptions occurred. Fixture-based UI tests are software tests, not evidence of model accuracy.
- CLI exposes only `prepare` and `train`. The active code has no external inference client, API key lookup, paid evaluation command, live-model selector or optional-agent import.
- Current aggregate values exactly preserve Juhan's source Windows run: 1,022 cases, 140 baseline errors, 877 suggestions and 145 reviews under the rules, 63 remaining wrong suggestions, and 77 original errors deferred.
- The final scope removes the optional LLM path. A prior unsuccessful connection attempt is not reported as agent-performance evidence. No new paid calls were made during finalization.

## Verification environment

```json
{
  "python": "3.12.14",
  "numpy": "2.3.5",
  "pandas": "2.2.3",
  "scikit-learn": "1.8.0",
  "joblib": "1.5.3",
  "streamlit": "1.66.1",
  "pytest": "9.2.0"
}
```

These are the software-verification versions, not the Windows study-run versions. Study provenance and run-specific package versions remain in the evidence JSON. Model specification, sampling, thresholds and held-out cases were not changed to improve results.
