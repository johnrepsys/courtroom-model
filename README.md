# Courtroom Model

This repository accompanies the paper **“The Courtroom Challenge—A Conjecture on the Unavoidable Cost of LLM Verification”** (2025).

| Folder / file | Purpose |
|---------------|---------|
| `paper/` | LaTeX sources, figures, and bibliography |
| `notebooks/courtroom.ipynb` | Reproducibility notebook that<br>• fetches SEC data via EDGAR<br>• builds the 100-query ground-truth set<br>• reproduces all KPI figures |
| `requirements.txt` | Minimal Python dependencies |

---

## Quick start

```bash
git clone https://github.com/johnrepsys/courtroom-model.git
cd courtroom-model
python -m venv venv              # optional virtualenv
source venv/bin/activate
pip install -r requirements.txt
jupyter lab notebooks/courtroom.ipynb
```
