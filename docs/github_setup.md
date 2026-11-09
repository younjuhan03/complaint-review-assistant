# Running my local app

## Open the app — Windows / VS Code

Download **Code → Download ZIP**, extract it, and open the folder containing `pyproject.toml` in VS Code. Open **Terminal → New Terminal**. Python 3.11+ is required. Run each command separately:

```powershell
python -m venv .venv
```
```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```
```powershell
.\.venv\Scripts\python.exe -m cra.cli prepare
```
```powershell
.\.venv\Scripts\python.exe -m cra.cli train
```
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
```powershell
.\.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

Open the **Local URL** printed in the terminal. Keep the terminal running; **Ctrl+C** stops the app. Calling the environment's Python directly avoids PowerShell activation restrictions.

First-time preparation reads two official CFPB date archives, about **178 MB total**, and keeps a small sample. Cleaning can take several minutes. Later launches need only the final command.

### Updating an existing project folder

Stop the app. Extract the current source ZIP and copy its contents into your existing project folder, replacing source files. Keep your existing `.venv/`, `data/` and `results/` folders so you can reuse your model. Restart with the final command above. Do not rerun data preparation or training just to update the interface.


I publish source and aggregate evidence. Raw narratives, model artifacts, credentials and local environments remain outside the repository.
