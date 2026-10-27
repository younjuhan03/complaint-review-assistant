# Optional real agent evaluation

**Pending:** No key was configured in the development environment; no real API calls or paid experiments were executed. Existing agent-flow tests use synthetic transport fixtures, not a substitute LLM. The API integration is implemented but still needs an authorized live smoke test.

## Fixed evaluation

Use the 100 rows in `results/local/agent_sample.jsonl` produced by the frozen training procedure. Do not select successful examples, silently retry failures or change thresholds after viewing agent results. Text only is sent; the product label is not. The CLI checks the saved sample and model fingerprints against published evidence.

The proposed model is `gpt-5.4-mini-2026-03-17` with `reasoning_effort=none`. Official [model documentation](https://developers.openai.com/api/docs/models/gpt-5.4-mini) lists Chat Completions, function calling and structured outputs. The [function calling guide](https://developers.openai.com/api/docs/guides/function-calling) documents the implemented tool/result exchange. Account access has not been tested. This is one model choice, not a model comparison.

Standard prices checked 2026-10-27: $0.75 input and $4.50 output per million tokens. Recheck before execution. The fixed 100-case sample has a **$2.285 planning allowance**, at most 300 requests and 180,000 output tokens. It uses a conservative input allowance based on UTF-8 bytes plus overhead, not a precise token count or billing guarantee. A live single-example smoke test is separate and must also be consented to. No retries occur automatically.

## Set up locally

Use the activated project terminal. The `.env.example` file documents variables; it does not load a key. Set the model and prices, one line at a time:

```powershell
$env:CRA_MODEL = "gpt-5.4-mini-2026-03-17"
```
```powershell
$env:CRA_INPUT_USD_PER_MILLION = "0.75"
```
```powershell
$env:CRA_OUTPUT_USD_PER_MILLION = "4.50"
```

Enter the key privately in your own terminal using a hidden prompt, never in chat:

```powershell
$secret = Read-Host "OpenAI API key" -AsSecureString
```
```powershell
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $secret).Password
```

This lasts for the terminal session and is inherited by Streamlit started there. Do not print the variable or commit it.

Compute the preview (no API call):

```powershell
python -m cra.cli preview
```

For an explicitly consented live smoke test, start the app, choose Live LLM assistant, inspect the displayed cost and check the consent box. Prepared examples are illustrative and separate from the evaluation sample. The assistant can defer on failure, so inspect the failure record and tool trace before proceeding.

**Only after agreeing to a paid allowance of $3 for the fixed 100-case evaluation**, run:

```powershell
python -m cra.cli agent-evaluate --approve-usd 3
```

The number is an explicit local spending authorization, not a provider-enforced billing cap. The CLI refuses to start if its planning allowance exceeds that number. Provider prices and configured variables must be accurate. Original cache usage is reported historically; cached cases are not charged again. Errors remain in the evaluation denominator. Do not erase a failed cache entry to improve the result.

## Reading the outcome

`docs/evidence/summary.json` gains agent metrics, failure counts, historical token usage and original latency. `results/local/agent/` contains private traces and cached responses; never upload that directory. Only the aggregate JSON is publishable. README and `docs/results.md` are the initial pending report: after the real run, update those narratives to match the new aggregate numbers and review explanations for unsupported claims. Do not describe the project as agent-evaluated until that step is complete.

The validator preserves the classifier category and team and enforces required review. Any added agent deferral must be counted. If agent decisions simply match Python rules, that is a legitimate result; do not add features to manufacture a win.
