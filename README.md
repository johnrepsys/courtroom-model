# Courtroom Model

This repository accompanies the paper  
**“The Courtroom Challenge — A Conjecture on the Unavoidable Cost of LLM Verification”**  
[local `paper/main.pdf`](paper/main.pdf)) &nbsp;© 2025.

| Folder / file | Purpose |
|---------------|---------|
| `paper/` | LaTeX sources, figures, and bibliography |
| `notebooks/courtroom.ipynb` | Reproducibility notebook that<br>• fetches SEC data via EDGAR<br>• builds the 100-query ground-truth set<br>• reproduces all KPI figures |
| `data/inputs/benchmark_queries_100_FY2021_FY2023.csv` | Static benchmark ledger (ticker × metric queries) |
| `data/outputs/ground_truth.csv` | Canonical answers scraped from EDGAR |
| `results/` | Frozen snapshots of the executed notebook — e.g.<br>&nbsp;&nbsp;• `courtroom-20250620.html` (rendered view)<br>&nbsp;&nbsp;• `courtroom-20250620.pdf` |
| `requirements.txt` | Minimal Python dependencies |
| `LICENSE` | MIT License |

---

## Quick start

```bash
git clone https://github.com/johnrepsys/courtroom-model.git
cd courtroom-model
python -m venv venv                # optional virtualenv
source venv/bin/activate
pip install -r requirements.txt
jupyter lab notebooks/courtroom.ipynb
```

The notebook will prompt for two values:
| Variable         | Purpose                                         | How to supply                                                    |
| ---------------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| `USER_AGENT`     | Polite identifier for EDGAR requests            | `export USER_AGENT="Ada <ada@ex.com>"` **or** type when prompted |
| `OPENAI_API_KEY` | Needed only if you run the GPT explanation cell | `export OPENAI_API_KEY="sk-..."` **or** paste when prompted      |


Requires Python 3.10+.
All code and data released under the MIT License; see LICENSE for terms.
