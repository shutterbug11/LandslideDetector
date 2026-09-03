# 🏔️ Sikkim Landslide Prediction

## Overview

Machine learning model for predicting **landslide susceptibility** in Sikkim, India using satellite-derived geospatial features from Sentinel-1 (SAR) and Sentinel-2 (optical) imagery.

## Problem

Binary classification of terrain pixels as **landslide-prone (1)** or **stable (0)** using 30+ geospatial features including spectral indices, topographic parameters, hydrological attributes, and textural metrics.

## Dataset

| Property | Value |
|---|---|
| Total samples | ~4,000,000 |
| Features | 30 satellite-derived + 4 engineered |
| Target | `Decision` (binary: 0/1) |
| Class imbalance | ~98.5% negative / ~1.5% positive |
| Source | Sentinel-1 & Sentinel-2 satellite imagery |

### Feature Categories

- **Spectral** (12): NDVI, MSAVI, SAVI, EVI, GNDVI, GRVI, ARVI, mNDMI, NDWI, NDTI, mNDWI, BSI
- **Topographical** (8): elevation, slope, aspect, curvature, plan/profile curvature, TWI, TRI
- **Hydrological** (2): SPI, FDR
- **Textural** (8): GLCM Mean, Contrast, Correlation, Energy, Entropy, ASM, Dissimilarity, Homogeneity

## Project Structure

```
LandslidePredictionSoftware/
├── Sikkim/
│   ├── Sikkim_dataset.csv          # Main dataset (~1.3 GB)
│   ├── Sikkim/                     # Event-level data
│   ├── feature images/             # Satellite feature images
│   ├── raw_tiles/                  # Raw satellite tiles
│   └── subsets/                    # Temporal subsets
├── notebooks/
│   └── landslide_prediction.ipynb  # Complete ML workflow
├── artifacts/                      # EDA visualizations
├── output/                         # Final model outputs
└── README.md
```

## Approach

1. **Stratified subsampling**: ~250K rows (all positives retained)
2. **Preprocessing**: Imputation, outlier clipping, scaling — fitted on training data only
3. **Feature engineering**: Domain-driven interaction features
4. **Models compared**: Logistic Regression, Random Forest, XGBoost, LightGBM
5. **Hyperparameter tuning**: Optuna with 50 trials
6. **Evaluation**: F1, ROC-AUC, PR-AUC (imbalance-aware)
7. **Explainability**: Built-in + permutation feature importance

## Key Outputs

### Artifacts (EDA)
- `target_distribution.png` — Class imbalance visualization
- `missing_values.png` — Missing value analysis
- `correlation_matrix.png` — Feature correlations
- `feature_distributions_*.png` — Feature distributions by class
- `outlier_analysis.png` — Box plots for extreme features
- `feature_target_relationships.png` — Top features vs target
- `feature_category_analysis.png` — Category importance overview

### Output (Model Results)
- `confusion_matrix.png` — Test set confusion matrix
- `roc_curve.png` — ROC curves for all models
- `precision_recall_curve.png` — PR curves
- `feature_importance.png` — Built-in + permutation importance
- `prediction_distribution.png` — Probability distributions
- `model_performance.png` — Summary card
- `model_comparison.png` — All models comparison
- `results_summary.json` — Machine-readable results

## 🚀 Interactive Streamlit Web Application

A full-featured real-time **Landslide Early Warning & Risk Classification Web Application** is included for the **North Eastern Region (NER) of India**:

```bash
# Launch the web application
streamlit run app.py
```

### App Capabilities
* **Real-Time Weather Integration**: Connects to **Open-Meteo API** (hourly precipitation, multi-depth soil moisture down to 81cm, apparent temperature, humidity, cloud cover) with cache & retry mechanisms, plus **OpenWeather API** live weather telemetry cross-validation.
* **North Eastern Region Coverage**: Covers all 8 states (Sikkim, Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura) with curated high-risk corridors (e.g., Gangtok, Mangan, Haflong/Dima Hasao, Shillong, Cherrapunji, Tawang, Kohima NH-29, Tupul/Noney, Aizawl, Jampui Hills) or custom GPS coordinate input.
* **Risk Classification**:
  * 🟢 **LOW RISK (< 35%)**: Normal Vigilance
  * 🟡 **MEDIUM RISK (35% – 70%)**: Saturated Slopes / Caution
  * 🔴 **HIGH RISK (> 70%)**: Critical Failure Risk / Evacuation Advisory
* **Interactive Foliated Map**: Displays all regional hotspot circles color-coded by vulnerability with satellite imagery toggle.
* **Dynamic Probability Gauge & Metrics**: Live gauge chart, 24h & 72h antecedent rainfall accumulation, volumetric soil moisture saturation across 5 depth horizons.
* **14-Day Forward Risk Forecast**: Dual-axis projection comparing predicted precipitation against projected landslide risk trajectory.
* **Explainability & Hazard Drivers**: Quantitative breakdown of slope steepness, soil moisture, rainfall trigger, and geological susceptibility.
* **Emergency Response**: Instant toll-free SDMA emergency contact numbers and NDMA landslide standard operating procedures.

## How to Run

```bash
# 1. Install dependencies
pip install openmeteo-requests requests-cache retry-requests streamlit folium streamlit-folium plotly numpy pandas scikit-learn lightgbm joblib

# 2. Launch the Streamlit Web Application
streamlit run app.py

# 3. View the complete ML Notebook
jupyter notebook notebooks/landslide_prediction.ipynb
```

## Requirements

- Python 3.10+
- NumPy, Pandas
- Scikit-learn
- XGBoost, LightGBM
- Optuna
- imbalanced-learn
- Seaborn, Matplotlib

## Limitations

1. **Spatial autocorrelation** — adjacent pixels are not independent
2. **Temporal generalization** — trained on specific events
3. **Binary classification** — may oversimplify gradual susceptibility
4. **Subsampled training** — results based on ~250K of 4M rows

## License

Academic/research use.
