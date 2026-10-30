# Evidence files

- `summary.json`: current local-study presentation, retaining the actual classifier/rule results from Juhan's October 29 Windows run. Optional LLM and 100-case extension fields are omitted. `utc`, package versions, hashes, policy and full-test values refer to that source run, not a new run of the simplified code.
- `windows_run_2026-10-29.json`: unmodified source run provided by Juhan, before the final scope simplification.
- `initial_run_2026-10-27.json`: initial development run, also retained unmodified.

The two archived runs include historical optional-agent status and fixed-sample metadata. Those fields are provenance, not a pending task or a live feature in the final project. No agent performance was measured by those files. The final project compares only a local classifier and deterministic review rules.

Data, thresholds and model specification were not changed in response to evaluation outcomes. Small cross-environment differences are reported, not hidden. Raw complaints, IDs and fitted model artifacts are not included here.
