# Verification record

Checked 2026-10-27 in Python 3.12. Tested package versions appear in `evidence/summary.json`.

- Official bounded archives downloaded and parsed; eligibility and duplicate exclusions recorded.
- One classifier fitted using training rows only. Development policy fixed before test metrics.
- Full test and fixed 100-case baseline metrics computed from real narratives and public labels.
- `python -m pytest -q`: **9 passed**. Includes policy enforcement, denominator edge cases, duplicate handling, cache invalidation, unauthorized tools, API failure, truncated output, successful mocked two-tool exchange, and first-screen/no-key app behavior.
- Streamlit AppTest: first page and a prepared card example rendered without exceptions; live action disabled without a key.
- `python -m cra.cli preview`: 100 cases, maximum 300 requests, planning cost $2.284464 at documented configured prices. This preview makes no API calls.
- Real API calls: **0**. Live compatibility, actual tool adherence, semantic explanation quality, injection robustness, cost and latency remain untested.
- GitHub: authenticated login `younjuhan03`; target repository not found through the connector. No source upload or deployment is claimed.

Mocks test software mechanics only. A fake response is never included as research evidence.
