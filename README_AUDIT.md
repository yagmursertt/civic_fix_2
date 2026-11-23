# CivicFix AI — Assignment 2 audited submission (23 November 2026)

## What to submit
- **direk_sert_assignment2.pdf** — one-page report; the surname1_surname2_assignment2.pdf naming format is followed.
- **CivicFix_Assignment2_FINAL.pptx** — 11-slide presentation for 24 November 2026.
- **CivicFix_Assignment2_FINAL.pdf** — noneditable viewing copy of the same 11-slide presentation.

## What inputs are actually in this package

| Source | Included? | Why it matters |
|---|---|---|
| NYC 311 2025 raw data (`nyc311_infra_2025.csv`) | **NO** | Original city-level input to the historical classifier; missing from user's provided attachment bundle and this ZIP. Public extraction script: https://github.com/yagmursertt/civicfix-ai/blob/main/fetch_data.sh. Downloads today may differ from the old snapshot. |
| NOAA Central Park 2025 precipitation raw (`nyc_centralpark_2025.csv`) | **NO** | Used by original NYC experiment; downloadable from https://github.com/yagmursertt/civicfix-ai/blob/main/nyc_centralpark_2025.csv |
| NYC model legacy results and code | **YES** | `inputs/results_legacy.json`, `code/run_analysis_legacy.py` |
| Istanbul daily rain, 1–20 October 2026 | **YES** | Actual 20-row `inputs/istanbul_daily_rain_oct2026.csv` recovered from the user's previous files |
| Istanbul DEM/OSM figure and GIS metadata | **YES** | `inputs/Istanbul_DEM_OSM_screening.png` and `inputs/Istanbul_Geo_Metadata.json` |
| Original DEM TIFF/TAR and actual OSM geometries | **NO** | Needed to regenerate the Istanbul map exactly, not provided |
| Turkish sample, predictions and metrics | **YES** | 25 paraphrases and 25 GPT-6 pilot labels + metrics (`inputs/`) |

## What model was chosen and why?
The **HistGradientBoostingClassifier** was the main supervised learning model trained on NYC tabular data; the supplied `run_analysis.py` has one-hot preprocessing followed by `HistGradientBoostingClassifier(max_iter=120, learning_rate=0.08, max_leaf_nodes=21)`. The model supports nonlinear combinations of complaint type, history and weather. Numerical standardization was not performed because it is not required for this tree-based learner.

The second AI method was **GPT-6 in ChatGPT** for provisional text triage, **not** a separately trained classifier. A geospatial screening score combines DEM features and distance to mapped OSM waterways; this is a **hand-built heuristic**, not a learned model or flood probability. Both are exploratory.

## Known substantive limitations and fixes
- In the legacy NYC training procedure, records just before the September 1 split can have recurrence **labels** determined by complaints in September. This prevents treating the 2025 split as completely prospective.
- The original `rain_mm` and 3-day rolling rain features include **the whole current calendar day**, which might only be observed after the complaint was created. This is a look-ahead problem for real-time triage.
- The included **`code/run_analysis_leakage_checked.py`** fixes these two issues by (1) excluding August 2–31 training records, so their 30-day outcomes cannot cross the September 1 test boundary, and (2) using only earlier days' rain. It also generates a ROC curve, PR curve and NYC confusion matrix **if original raw inputs are supplied**. The code was smoke-tested on artificial internal data **only**. No corrected NYC accuracy is claimed.
- Reported model values (ROC-AUC 0.672, AP 0.585, F1 0.474, top-decile precision 71.6%) are from the user's `results 2.json`, **not a new run**. `pr_auc` in the old JSON was calculated with `average_precision_score`; technically it is Average Precision, often summarized alongside a PR curve.
- The GitHub README lists **132,653** original NYC rows, while `results 2.json` lists **132,648**. These are two different reported snapshots or runs; the actual cause of the discrepancy is not verified. Only the latter is used consistently in this report and deck.
- GPT-6's **24/25 agreement, 96%, macro-F1 0.971** is with **provisional author labels**, not an independent test set. No public source URL timestamps were verified.
- The Istanbul map uses 99 OSM waterway geometries over a limited area. The 20-day rain series describes a single point **outside** the map bounds; not spatially joined to the DEM. There is no validated Istanbul flood occurrence target or city-transfer metric.

## Reproducibility status
Model summary and Turkish pilot measurements were independently checked against the provided JSON/CSVs. NYC raw dataset and DEM/OSM raw raster inputs are absent, so the historical full NYC training and GIS map **cannot** be independently rerun from this ZIP. Do not describe this package as full raw-data reproduction.

This package is suitable as the Assignment 2 model exploration/report and class presentation **with the stated methodological limitations**. It does not make claims of flood forecasting, deployment, or a fully validated prospective holdout.
