# CivicFix AI — Assignment 2: Model Exploration & Results

**Group 8:** Tunahan Onur Direk · Yağmur Sert · Sezin Naz Sarı  
**Presentation:** 24 November 2026  
**Related SDG:** SDG 11 — Sustainable Cities and Communities (focus: 11.5)

## Purpose

CivicFix AI explores how AI and geographic data could help prioritize urban infrastructure complaints. The main *evaluated* supervised task is to predict whether a new NYC 311 infrastructure complaint occurs within 30 days in the same approximately 0.001-degree coordinate cell. **This is not a validated flood-prediction model.**

## Three project components

| Component | Method | What has actually been evaluated? |
| --- | --- | --- |
| NYC complaint recurrence | `HistGradientBoostingClassifier` on NYC 311 complaints + precipitation | Retrospective legacy test metrics; the legacy split has known look-ahead/leakage risks |
| Turkish complaint triage | GPT-6 in-chat classification into critical, high, routine, not actionable | 25-example pilot: agreement against author-assigned labels, **not** an independent benchmark |
| Istanbul geographic screening | Copernicus GLO-30 terrain + OSM waterway-distance heuristic | Exploratory map, **not** a trained model or calibrated flood probability |

## Reported results (legacy; NOT leakage-safe re-evaluation)

- NYC test ROC-AUC: **0.672**
- NYC average precision (AP): **0.585**
- NYC F1 at threshold 0.50: **0.474**
- NYC highest-ranked 10% recurrence rate: **71.6%**, vs **39.9%** overall on the reported test set
- Turkish text pilot: **24/25 = 96%** agreement with provisional author labels; macro-F1 **0.971**

These numbers are *reported historic outputs* from the included `results_legacy.json` and `gpt6_pilot_metrics.json`. They have **not** been re-established using a fully independent, leakage-safe evaluation.

## Files

- `direk_sert_assignment2.pdf`: one-page results report (submission artifact)
- `CivicFix_Assignment2_FINAL.pptx` / `.pdf`: presentation / viewing copy
- `run_analysis_legacy.py`, `results_legacy.json`: original NYC experiment and its recorded metrics
- `run_analysis_leakage_checked.py`: revised NYC evaluation script (requires missing raw CSVs)
- `turkish_complaints_25_anonymized.csv`, `gpt6_pilot_predictions_25.csv`, `gpt6_pilot_metrics.json`: Turkish pilot material
- `istanbul_daily_rain_oct2026.csv`, `Istanbul_Geo_Metadata.json`, `Istanbul_DEM_OSM_screening.png`, `geo_osm_extension.py`: Istanbul pilot material
- `README_AUDIT.md`, `SIX_CRITERIA_CHECK.md`, `audit_consistency.json`: audit and limitations
- `DATA_AVAILABILITY.md`: exact reproduction limits and required missing inputs

## Reproduce what can be reproduced

Python 3.10+ is recommended. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To run the corrected NYC evaluation, **you must first provide the original source files** in a local `raw_data/` directory:

```text
raw_data/
  nyc311_infra_2025.csv
  nyc_centralpark_2025.csv
```

Then run:

```bash
python run_analysis_leakage_checked.py --data-dir raw_data --out checked_run
```

Expected outputs *after a successful run*: `checked_run/results_checked.json`, ROC curve, precision-recall curve, and confusion matrix. **They have not been generated from original raw data in this submission.** A new download may not match the historical 2025 extract, so resulting metrics can differ.

Istanbul map regeneration requires the original COP30 raster archive and raw OSM geometries; see `DATA_AVAILABILITY.md`. The shipped figure is an already-created result.

## Limitations and next steps

1. The legacy NYC train/test split allows some training labels to depend on later-period complaints; same-day accumulated rainfall may also be unavailable at complaint time. Re-run the revised script using frozen and documented raw inputs.
2. The Turkish pilot is small and its labels are author-assigned. Evaluate on larger independently annotated and blinded data.
3. The NYC model has **not** been evaluated in Istanbul. The Istanbul map is not confirmed by observed inundation; the 20-day rain point is outside the map's DEM footprint.
4. Secure timestamped, verified Istanbul complaint/flood observations and evaluate model transfer, calibration and fairness before any operational use.

## Data sources

NYC Open Data (311), NOAA (Central Park precipitation), Open-Meteo, Copernicus GLO-30, OpenStreetMap. See `CivicFix_Data_Provenance.pdf` and `README_AUDIT.md` for detailed provenance and missing sources.

**Academic use only.** No production flood-warning or municipal decision-making capability is claimed.
