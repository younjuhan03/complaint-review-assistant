# GitHub and local use

Public repository: https://github.com/younjuhan03/complaint-review-assistant

Juhan created the repository. Source code and aggregate evidence were prepared with AI assistance. Raw archives, complaint narratives, complaint IDs, fitted models, local traces, virtual environments and real API keys are excluded.

## Get a local copy without installing Git

1. Open the repository and choose **Code → Download ZIP**.
2. Extract the ZIP and open the extracted folder in VS Code.
3. Follow the separate PowerShell commands in the README.

The repository includes saved findings, but no fitted model. Data preparation and training create the local model needed for example inputs. No API key is required for local classifier + Python-rule mode.

If you already extracted the earlier project ZIP, you can use that folder instead. Do not copy these files into the RetailOS project.

## Updating the repository later

Publish source and aggregate evidence only. Browser uploads do not automatically respect `.gitignore`: do not select `data/`, `results/`, `.venv/`, `.env`, ZIP files or local caches. In particular, never upload real complaint text or private agent traces.

The live LLM evaluation remains pending. Update README and the results report only after a real authorized run and trace review. No public app deployment is included.
