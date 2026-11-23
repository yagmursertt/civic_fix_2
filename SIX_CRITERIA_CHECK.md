# Assignment 2 — six required items, checked against actual output

| Assignment item | Where it is covered | Assessment |
|---|---|---|
| 1. Model Selection & Justification | Report §1; presentation slides 3–4 | Yes: named trained NYC classifier, separate GPT-6 pilot, rationale and SDG 11.5 relation; GIS correctly not called ML |
| 2. Data Preparation | Report §2; slide 4; audit & `run_analysis` sources | Yes: time split, one-hot encoding, feature engineering, missing coordinates, no numerical normalization with tree justification. Temporal leakage flaw is documented, not concealed. |
| 3. Model Training & Evaluation | Report §§2–4; slides 4–6; metrics charts and pilot confusion matrix | Historical NYC model trained; metrics from `results_legacy.json` reported, **not independently reproduced from raw data**. Corrected code supplied but requires NYC inputs. |
| 4. Interpretation of Results | Report §§3–6; slides 5, 6, 7, 8, 9, 10 | Yes: top-decile interpretation, small GPT-6 sample bias, GIS heuristic, limitations and next steps. |
| 5. In-Class Presentation (24 Nov) | 11-slide PPTX and PDF | Yes: model choices, metrics, chart, Istanbul rainfall and map, reasoning/trade-offs. |
| 6. Results Report (1 page, PDF) | `direk_sert_assignment2.pdf` | Yes: exactly one A4 page with model, results, conclusion and limitations; 2-surname filename pattern. |

**Residual blockers to stronger validation:** original NYC 311 CSV; original NOAA CSV version; COP30 raster and raw OSM GeoJSON; independently checked Turkish labels; verified Istanbul flood ground truth. These do not prevent reporting the completed work accurately but do prevent claiming full reproducing or confirmed transfer.
