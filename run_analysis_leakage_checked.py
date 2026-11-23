#!/usr/bin/env python3
"""Re-evaluate CivicFix NYC complaint recurrence with an honest temporal holdout.

REQUIRES original 2025 NYC 311 CSV and 2025 Central Park NOAA CSV.
This file is supplied as a CORRECTED METHOD, not as a previously completed experiment.
Its scores must NOT be substituted for the historical metrics unless the script is run.

Usage:
  python run_analysis_leakage_checked.py --data-dir ./inputs --out ./checked_run

Input filenames: nyc311_infra_2025.csv, nyc_centralpark_2025.csv
The NYC file must contain a complete year through 2025-12-31 for the November test labels.
"""
from pathlib import Path
import argparse, json, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score,
                             confusion_matrix, ConfusionMatrixDisplay,
                             RocCurveDisplay, PrecisionRecallDisplay)

CRITICAL=['Cave-in', 'Sidewalk Collapsed', 'Manhole Cover Missing', 'Catch Basin Grating Missing', 'Plate Condition - Open', 'Street Flooding', 'Highway Flooding', 'Manhole Overflow', 'Sewer Backup', 'Cellar Door Open/Unprotected', 'Guard Rail - Street', 'Crash Cushion Defect', 'Unsafe Worksite', 'Sidewalk Grating - Missing', 'Metal Protruding - Sign Stump']
HIGH=['Pothole', 'Catch Basin Clogged/Flooding', 'Broken Sidewalk', 'Failed Street Repair', 'Plate Condition - Shifted', 'Catch Basin Sunken/Damaged/Raised', 'Pedestrian Ramp Defective', 'Culvert Blocked/Needs Cleaning', 'Defective Hardware', 'Rough, Pitted or Cracked Roads', 'Sidewalk Grating - Defective', 'Sidewalk Staircase', 'Defective/Missing Curb Piece', 'Affecting Sewer or Foundation', 'Depression Maintenance', 'Hummock', 'Cellar Door Defective']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=Path('checked_run'))
    args=parser.parse_args()
    src=args.data_dir
    for required in ['nyc311_infra_2025.csv','nyc_centralpark_2025.csv']:
        if not (src/required).is_file():
            parser.error(f'Missing original input: {src/required}. Historical summary metrics are not a substitute.')
    args.out.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(src/'nyc311_infra_2025.csv',parse_dates=['created_date'],low_memory=False)
    raw_n=len(df)
    needed={'unique_key','created_date','complaint_type','descriptor','borough','location_type','latitude','longitude'}
    missing=needed-set(df.columns)
    if missing: raise ValueError(f'NYC data missing required columns: {sorted(missing)}')
    df=df.drop_duplicates('unique_key')
    df=df[df.borough.ne('Unspecified')].copy()
    clean_n=len(df)
    df=df.dropna(subset=['created_date','latitude','longitude']).copy()
    df=df.sort_values(['created_date','unique_key'],kind='stable').copy()
    df['cell']=df.latitude.round(3).astype(str)+'_'+df.longitude.round(3).astype(str)
    df['next']=df.groupby('cell').created_date.shift(-1)
    df['recur30']=((df['next']-df.created_date).dt.total_seconds() / 86400 <= 30).astype(int)
    # Only use counts that were observable when each complaint was created.
    df['_one']=1
    df['prior_any']=df.groupby('cell').cumcount()
    df=df.set_index('created_date')
    df['prior_90d']=df.groupby('cell')['_one'].transform(lambda z:z.rolling('90D').count()-1)
    df=df.reset_index()
    df['issue']=df.descriptor.fillna('Unknown').str.replace(r'\s*\((Use Comments|Emergency)\)','',regex=True).str.replace(r'\s*\([A-Z0-9]+\)$','',regex=True).str.strip()
    df['tier']=np.select([df.issue.isin(CRITICAL),df.issue.isin(HIGH)],['Critical','High'],default='Routine')
    df['date']=df.created_date.dt.normalize()
    df['month']=df.created_date.dt.month
    df['dow']=df.created_date.dt.dayofweek
    weather=pd.read_csv(src/'nyc_centralpark_2025.csv',parse_dates=['DATE'])[['DATE','PRCP']]
    weather=weather.rename(columns={'DATE':'date','PRCP':'rain_mm'}).sort_values('date')
    weather['rain_mm']=pd.to_numeric(weather['rain_mm'],errors='coerce')
    if weather.date.duplicated().any():raise ValueError('Weather CSV contains duplicate dates.')
    if len(weather[weather.date.between('2025-01-01','2025-12-31')])<350:
        warnings.warn('Weather data has <350 calendar days; validate missing periods.')
    # Shift one full calendar day before aggregating; same-day future rain is removed.
    calendar=pd.DataFrame({'date':pd.date_range('2025-01-01','2025-12-31',freq='D')})
    calendar=calendar.merge(weather,on='date',how='left',validate='one_to_one')
    calendar['rain_prev3d']=calendar.rain_mm.shift(1).rolling(3,min_periods=1).sum()
    df=df.merge(calendar[['date','rain_prev3d']],on='date',how='left',validate='many_to_one')
    df['missing_rain_prev3d']=df.rain_prev3d.isna().astype(int)
    df['rain_prev3d']=df.rain_prev3d.fillna(0)
    # 30-day LABEL embargo: Aug 2–31 rows must not be training examples when testing Sep 1+.
    # Training labels from <=Aug 1 depend only on dates before Sep 1.
    train=df[df.created_date < '2025-08-02'].copy()
    test=df[(df.created_date >= '2025-09-01') & (df.created_date < '2025-12-01')].copy()
    # December observations remain in df solely to label test outcomes.
    if train.empty or test.empty:raise ValueError('Empty train/test split; check original NYC input dates.')
    if df.created_date.max() < pd.Timestamp('2025-12-31'):
        warnings.warn('NYC extract ends before Dec 31; test labels may be right-censored.')
    cat=['complaint_type','issue','tier','borough','location_type']
    num=['month','dow','rain_prev3d','missing_rain_prev3d','prior_90d','prior_any']
    train[cat]=train[cat].fillna('Unknown');test[cat]=test[cat].fillna('Unknown')
    train[num]=train[num].fillna(0);test[num]=test[num].fillna(0)
    preprocess=ColumnTransformer([('categorical',OneHotEncoder(handle_unknown='ignore',min_frequency=20,sparse_output=False),cat),('numeric','passthrough',num)])
    model=make_pipeline(preprocess,HistGradientBoostingClassifier(max_iter=120,learning_rate=.08,max_leaf_nodes=21,random_state=42))
    model.fit(train[cat+num],train.recur30)
    prob=model.predict_proba(test[cat+num])[:,1]
    pred=(prob>=0.5).astype(int)
    cut=np.quantile(prob,0.90)
    top=prob>=cut
    metrics={
      'method':'Chronological split with 30-day label embargo and prior-day-only precipitation',
      'original_raw_count':int(raw_n),'cleaned_count_before_coordinate_filter':int(clean_n),
      'train':int(len(train)),'test':int(len(test)),'test_prevalence':float(test.recur30.mean()),
      'roc_auc':float(roc_auc_score(test.recur30,prob)),
      'average_precision':float(average_precision_score(test.recur30,prob)),
      'f1_threshold_0_5':float(f1_score(test.recur30,pred)),
      'top_decile_precision':float(test.recur30[top].mean()),
      'top_decile_n':int(top.sum()),
      'confusion_matrix_0_5':confusion_matrix(test.recur30,pred,labels=[0,1]).tolist(),
      'input_version_note':'Scores depend on the specific NYC extract snapshot; do not merge with legacy metrics.'}
    (args.out/'results_checked.json').write_text(json.dumps(metrics,indent=2),encoding='utf-8')
    RocCurveDisplay.from_predictions(test.recur30,prob)
    plt.title('NYC recurrence ROC curve — leakage-checked experiment');plt.tight_layout();plt.savefig(args.out/'nyc_roc_checked.png',dpi=170);plt.close()
    PrecisionRecallDisplay.from_predictions(test.recur30,prob)
    plt.title('NYC recurrence precision-recall — leakage-checked experiment');plt.tight_layout();plt.savefig(args.out/'nyc_pr_checked.png',dpi=170);plt.close()
    ConfusionMatrixDisplay.from_predictions(test.recur30,pred,display_labels=['No recurrence','Recurrence'])
    plt.title('NYC confusion matrix (threshold .50)');plt.tight_layout();plt.savefig(args.out/'nyc_cm_checked.png',dpi=170);plt.close()
    print(json.dumps(metrics,indent=2))

if __name__=='__main__':main()
