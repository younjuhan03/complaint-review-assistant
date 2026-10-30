# GitHub and local use

Repository: https://github.com/younjuhan03/complaint-review-assistant

Choose **Code → Download ZIP**, extract, and open the folder containing `pyproject.toml` in VS Code. Follow the README commands. No Git installation, API key, credits or cloud deployment is required.

For an existing local project, stop Streamlit and copy the current source ZIP contents into your existing folder, replacing source files while retaining `.venv/`, `data/` and `results/`. Launch the app again with the environment's Python. Existing local model and policy files remain usable. The current app ignores historical optional-agent fields in old aggregate files.

Publish source and aggregate evidence only. Browser uploads do not automatically apply `.gitignore`: do not upload `data/`, `results/`, `.venv/`, `.env`, raw narratives, model files, ZIP packages or private execution traces. Old local optional API files are unused by the final app and CLI; they need not be executed or uploaded.
