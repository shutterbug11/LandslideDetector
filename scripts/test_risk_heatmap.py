"""
=============================================================================
Verification Test: Dynamic Risk Heatmap Generation & Folium Compilation
=============================================================================
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import folium
from folium.plugins import HeatMap
from utils.heatmap_service import compute_hotspot_predictions, generate_risk_heatmap_data
from utils.regional_data import NE_HOTSPOTS


def test_hotspot_predictions():
    print("--- [1] Testing Hotspot Grid Vectorized Risk Predictions ---")
    mock_weather = {
        "triggers": {
            "rain_past_24h": 65.0,
            "rain_past_72h": 140.0,
            "soil_moisture_top": 0.41,
            "soil_moisture_mean": 0.38
        }
    }
    
    preds = compute_hotspot_predictions(mock_weather)
    assert len(preds) == len(NE_HOTSPOTS), f"Expected {len(NE_HOTSPOTS)} hotspots, got {len(preds)}"
    
    for hname, info in preds.items():
        assert "probability" in info, f"Missing probability for {hname}"
        assert "ml_probability" in info, f"Missing ml_probability for {hname}"
        assert "classification" in info, f"Missing classification for {hname}"
        assert "color" in info, f"Missing color for {hname}"
        assert 0.0 <= info["probability"] <= 100.0, f"Probability out of range: {info['probability']}"
        assert info["classification"] in ["High", "Medium", "Low"], f"Invalid classification: {info['classification']}"
        
    print(f"Successfully computed predictions for all {len(preds)} hotspots.")
    high_count = sum(1 for p in preds.values() if p["classification"] == "High")
    med_count = sum(1 for p in preds.values() if p["classification"] == "Medium")
    low_count = sum(1 for p in preds.values() if p["classification"] == "Low")
    print(f"Classification Breakdown: {high_count} High, {med_count} Medium, {low_count} Low")
    print("[OK] Hotspot predictions test passed.\n")


def test_risk_heatmap_data_generation():
    print("--- [2] Testing Risk HeatMap Geospatial Distribution ---")
    mock_weather = {
        "triggers": {
            "rain_past_24h": 80.0,
            "rain_past_72h": 175.0,
            "soil_moisture_top": 0.44,
            "soil_moisture_mean": 0.40
        }
    }
    active_target = [{
        "title": "Observatory Station A",
        "lat": 27.3389,
        "lon": 88.6065,
        "risk": {"probability": 84.5, "classification": "High", "color": "#EF4444", "alert_level": "Critical"}
    }]
    
    pts = generate_risk_heatmap_data(mock_weather, active_targets=active_target)
    assert len(pts) > 200, f"Expected dense continuous grid (>200 points), got {len(pts)}"
    
    for pt in pts:
        assert len(pt) == 3, f"Invalid point structure: {pt}"
        lat, lon, weight = pt
        assert 21.0 <= lat <= 30.0, f"Latitude out of bounds: {lat}"
        assert 88.0 <= lon <= 98.0, f"Longitude out of bounds: {lon}"
        assert 0.0 < weight <= 1.0, f"Weight out of [0, 1] range: {weight}"
        
    print(f"Generated {len(pts)} continuous weighted risk points across North East region.")
    print(f"Sample points: {pts[:3]}")
    print("[OK] Heatmap points generation test passed.\n")


def test_folium_heatmap_compilation():
    print("--- [3] Testing Folium HeatMap Layer Assembly ---")
    mock_weather = {
        "triggers": {
            "rain_past_24h": 40.0,
            "rain_past_72h": 90.0,
            "soil_moisture_top": 0.32,
            "soil_moisture_mean": 0.30
        }
    }
    pts = generate_risk_heatmap_data(mock_weather)
    
    m = folium.Map(location=[26.1, 92.9], zoom_start=7, tiles="CartoDB positron")
    heat_fg = folium.FeatureGroup(name="🔥 Dynamic Landslide Risk Heatmap (Model Weighted)", show=True)
    
    HeatMap(
        pts,
        min_opacity=0.45,
        max_zoom=14,
        radius=25,
        blur=16,
        gradient={
            0.15: '#10B981',
            0.35: '#38BDF8',
            0.55: '#F59E0B',
            0.75: '#F97316',
            0.90: '#EF4444',
            1.00: '#7F1D1D'
        }
    ).add_to(heat_fg)
    heat_fg.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Ensure map compiles HTML without exception
    html = m._repr_html_()
    assert len(html) > 1000, "Folium HTML output too short"
    assert "leaflet-heatmap" in html or "heatlayer" in html.lower() or "folium" in html.lower()
    print("Folium HTML map generated cleanly with HeatMap plugin!")
    print("[OK] Folium compilation test passed.\n")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING RISK HEATMAP SERVICE VERIFICATION SUITE")
    print("==================================================\n")
    test_hotspot_predictions()
    test_risk_heatmap_data_generation()
    test_folium_heatmap_compilation()
    print("ALL TESTS PASSED SUCCESSFULLY! [PASS]")
