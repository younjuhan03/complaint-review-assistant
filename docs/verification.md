# Verification record

Checked 2026-10-27 in Python 3.12. Initial tested package versions appear in `evidence/initial_run_2026-10-27.json`. The current `summary.json` records Juhan's October 29 reproduction environment; the original nine-test result is not being attributed to that environment.

- Official bounded archives downloaded and parsed; eligibility and duplicate exclusions recorded.
- One classifier fitted using training rows only. Development policy fixed before test metrics.
- Full test and fixed 100-case baseline metrics computed from real narratives and public labels.
- `python -m pytest -q`: **9 passed**. Includes policy enforcement, denominator edge cases, duplicate handling, cache invalidation, unauthorized tools, API failure, truncated output, successful mocked two-tool exchange, and first-screen/no-key app behavior.
- Streamlit AppTest: first page and a prepared card example rendered without exceptions; live action disabled without a key.
- `python -m cra.cli preview`: 100 cases, maximum 300 requests, planning cost $2.284464 at documented configured prices. This preview makes no API calls.
- Real API calls: **0**. Live compatibility, actual tool adherence, semantic explanation quality, injection robustness, cost and latency remain untested.
- GitHub: repository created by Juhan and source/aggregates uploaded afterward. No app deployment is claimed.

Mocks test software mechanics only. A fake response is never included as research evidence.

October 29 aggregate check: confusion-matrix total 1,022; classifier errors 140; routed errors 63; reviews 145; base errors deferred 77. Counts and reported fractions are internally consistent. Protocol, cleaned-data and fixed-sample hashes match the initial run. No real LLM call was made during this comparison.
