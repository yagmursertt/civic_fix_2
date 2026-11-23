# Dataset availability and reproducibility status

**Do not treat reported legacy metrics as leakage-safe or newly rerun results.**

| Input/validation material | In repository? | Impact |
| --- | --- | --- |
| Original NYC 311 2025 extract `nyc311_infra_2025.csv` | No | Cannot recreate historical train/test counts or scores exactly |
| Original NOAA 2025 precipitation file `nyc_centralpark_2025.csv` | No | Cannot rerun revised classifier as supplied |
| Original COP30 raster (`rasters_COP30.tar`, including `output_hh.tif`) | No | Cannot reproduce terrain raster/map from raw inputs |
| Raw OSM waterway geometries (GeoJSON) | No | Cannot recreate geographic index exactly |
| Independently annotated Turkish complaint labels | No | Reported 96% agreement applies only to author-assigned provisional labels |
| Verified Istanbul flood-event labels and NYC-to-Istanbul transfer results | No | No validated Istanbul flood-performance or transfer claim |

What **is** included: historical NYC metrics JSON and scripts; 25 Turkish samples and predictions with pilot metrics; a 20-day Istanbul rainfall CSV, map image, metadata and GIS script; final report and presentation.

## How to improve reproducibility

1. Save **versioned original** NYC complaint and NOAA rainfall raw files and document the extraction date, schema, filtering and provenance. Public data downloads made later are not necessarily the same snapshot.
2. Run `run_analysis_leakage_checked.py` against those inputs, store its fresh output under a new name, and update the report/slides **only with the newly observed scores**.
3. Archive original COP30 raster and corresponding OSM geometries with appropriate attribution/licensing; regenerate the GIS map.
4. Verify dates/URLs for the Turkish complaints, collect independent labels, and evaluate blind samples.
5. Test on time-stamped Istanbul complaints and independent flood observations before any cross-city claims.

## Known method details

The revised NYC script drops late-August training examples whose 30-day recurrence label would cross the September 1 test boundary, and uses rainfall from previous days only. That script has **not** been run against the missing original datasets in this repository.
