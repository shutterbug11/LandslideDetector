"""
Train and export the final LightGBM model and feature pipeline for the Streamlit app.
"""
import os, json, joblib
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'Sikkim', 'Sikkim_dataset.csv')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

FEATURE_CATEGORIES = {
    'Spectral': ['ARVI', 'BSI', 'EVI', 'GNDVI', 'GRVI', 'MSAVI', 
                 'NDTI', 'NDVI', 'NDWI', 'SAVI', 'mNDMI', 'mNDWI'],
    'Topographical': ['aspect', 'curvature', 'elevation', 'plan_curvature', 
                      'profile_curvature', 'slope', 'tri', 'twi'],
    'Hydrological': ['fdr', 'spi'],
    'Textural': ['ASM', 'Contrast', 'Dissimilarity', 'Energy', 'Entropy', 
                 'GLCMCorrelation', 'GLCMMean', 'Homogeneity'],
}
BASE_FEATURES = [f for feats in FEATURE_CATEGORIES.values() for f in feats]

print("Loading dataset for model export...")
chunk_size = 500_000
positives = []
negatives = []
for chunk in pd.read_csv(DATASET_PATH, chunksize=chunk_size):
    positives.append(chunk[chunk['Decision'] == 1])
    negatives.append(chunk[chunk['Decision'] == 0])

df_pos = pd.concat(positives, ignore_index=True)
df_neg = pd.concat(negatives, ignore_index=True)
df_neg_sampled = df_neg.sample(n=min(200_000, len(df_neg)), random_state=42)

df = pd.concat([df_pos, df_neg_sampled], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
print(f"Dataset assembled: {df.shape[0]:,} rows. Positive ratio: {df['Decision'].mean():.3f}")

X = df[BASE_FEATURES].copy()
y = df['Decision'].copy()

# Feature engineering
X['slope_ndvi_interaction'] = X['slope'] * X['NDVI']
X['elevation_curvature'] = X['elevation'] * X['curvature']
X['twi_slope'] = X['twi'] * X['slope']
X['vegetation_stress'] = 1 - X['NDVI'].clip(0, 1)

ALL_FEATURES = list(X.columns)

# Imputer
imputer = SimpleImputer(strategy='median')
X_imputed = pd.DataFrame(imputer.fit_transform(X), columns=ALL_FEATURES)

# Outlier clipping bounds
clip_bounds = {}
for col in ALL_FEATURES:
    clip_bounds[col] = (float(X_imputed[col].quantile(0.01)), float(X_imputed[col].quantile(0.99)))
    X_imputed[col] = X_imputed[col].clip(clip_bounds[col][0], clip_bounds[col][1])

# Load optimal parameters from results_summary.json
with open(os.path.join(OUTPUT_DIR, 'results_summary.json'), 'r') as f:
    summary = json.load(f)
best_params = summary.get('best_params', {})

scale_pos_weight = float((y == 0).sum() / (y == 1).sum())

model_params = {
    'n_estimators': best_params.get('n_estimators', 400),
    'max_depth': best_params.get('max_depth', 15),
    'learning_rate': best_params.get('learning_rate', 0.25),
    'num_leaves': best_params.get('num_leaves', 150),
    'subsample': best_params.get('subsample', 0.8),
    'colsample_bytree': best_params.get('colsample_bytree', 0.9),
    'min_child_samples': best_params.get('min_child_samples', 25),
    'reg_alpha': best_params.get('reg_alpha', 0.002),
    'reg_lambda': best_params.get('reg_lambda', 0.008),
    'scale_pos_weight': scale_pos_weight,
    'random_state': 42,
    'verbose': -1,
    'n_jobs': -1
}

print("Fitting final LightGBM model...")
model = lgb.LGBMClassifier(**model_params)
model.fit(X_imputed, y)

# Save artifacts
model_path = os.path.join(OUTPUT_DIR, 'landslide_model.joblib')
imputer_path = os.path.join(OUTPUT_DIR, 'imputer.joblib')
joblib.dump(model, model_path)
joblib.dump(imputer, imputer_path)

# Compute feature statistics to serve as baseline reference profiles
stats = {}
for col in ALL_FEATURES:
    stats[col] = {
        'mean': float(X_imputed[col].mean()),
        'median': float(X_imputed[col].median()),
        'std': float(X_imputed[col].std()),
        'min': float(X_imputed[col].min()),
        'max': float(X_imputed[col].max()),
        'q25': float(X_imputed[col].quantile(0.25)),
        'q75': float(X_imputed[col].quantile(0.75)),
        'clip_low': clip_bounds[col][0],
        'clip_high': clip_bounds[col][1]
    }

metadata = {
    'features': ALL_FEATURES,
    'base_features': BASE_FEATURES,
    'feature_categories': FEATURE_CATEGORIES,
    'stats': stats,
    'scale_pos_weight': scale_pos_weight,
    'best_params': best_params
}

meta_path = os.path.join(OUTPUT_DIR, 'model_metadata.json')
with open(meta_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Model exported to {model_path}")
print(f"Imputer exported to {imputer_path}")
print(f"Metadata exported to {meta_path}")
