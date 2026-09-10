"""
Integration test suite for GroundCheck Exposed Population Prioritization Engine.
Tests geodesic buffering, WorldPop zonal stats raster queries, priority score calculation,
and edge cases.
"""

import time
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from population import (
    get_exposed_population,
    get_geodesic_buffer_polygon,
    calculate_hotspot_prioritization,
    DEFAULT_RASTER_PATH
)
from utils.regional_data import NE_HOTSPOTS


def test_geodesic_buffer():
    print("--- [1] Testing Geodesic Buffer Generation ---")
    lat, lon = 25.5788, 91.8933  # Shillong
    poly = get_geodesic_buffer_polygon(lat, lon, radius_m=2000.0, n_points=64)
    assert poly.is_valid, "Geodesic polygon should be valid"
    assert len(poly.exterior.coords) == 65, "Expected 64 points + closed loop vertex"
    minx, miny, maxx, maxy = poly.bounds
    # ~2000m is ~0.018 degrees latitude
    lat_span = maxy - miny
    assert 0.030 < lat_span < 0.045, f"Unexpected latitude span for 2000m buffer: {lat_span}"
    print(f"[OK] Geodesic polygon generated with bounds: {poly.bounds}")


def test_exposed_population_queries():
    print("\n--- [2] Testing WorldPop Zonal Stats Queries ---")
    assert DEFAULT_RASTER_PATH.exists(), f"Expected raster at {DEFAULT_RASTER_PATH}"
    
    test_cases = [
        ("Gangtok (East Sikkim)", 27.3389, 88.6065),
        ("Shillong (East Khasi Hills)", 25.5788, 91.8933),
        ("Kohima (Nagaland)", 25.6751, 94.1086),
        ("Guwahati (Assam)", 26.1445, 91.7362),
    ]

    for name, lat, lon in test_cases:
        pop = get_exposed_population(lat, lon, radius_m=2000)
        print(f"  {name} ({lat}, {lon}) -> Exposed Pop: {pop:,.1f}")
        assert pop > 1000.0, f"Expected substantial population in {name}, got {pop}"

    # Missing raster path edge case
    fallback = get_exposed_population(27.3389, 88.6065, raster_path="non_existent.tif")
    assert fallback == 0.0, f"Expected 0.0 on missing raster, got {fallback}"
    print("[OK] Zonal stats queries and fallback tested successfully.")


def test_hotspot_prioritization_engine():
    print("\n--- [3] Testing Prioritization Ranking Across All Monitored Hotspots ---")
    t0 = time.time()
    
    mock_preds = {}
    for hname, hdata in NE_HOTSPOTS.items():
        mock_preds[hname] = {
            "name": hname,
            "lat": float(hdata["lat"]),
            "lon": float(hdata["lon"]),
            "state": hdata.get("state", "North East"),
            "probability": 72.5,
            "classification": "High",
            "is_active_target": False
        }

    df = calculate_hotspot_prioritization(mock_preds, radius_m=2000)
    elapsed = time.time() - t0
    print(f"Computed prioritization across {len(df)} hotspots in {elapsed:.2f} seconds.")

    assert len(df) == len(NE_HOTSPOTS), f"Expected {len(NE_HOTSPOTS)} rows, got {len(df)}"
    assert list(df.columns[:7]) == [
        "Rank", "Hotspot", "State", "Hazard Level",
        "Raw Risk %", "Exposed Population (~2km)", "Priority Score"
    ]

    # Verify descending order of priority score
    scores = df["_raw_priority"].tolist()
    assert scores == sorted(scores, reverse=True), "Scores are not sorted in descending order"

    # Verify mathematical formula: Priority Score = (Raw Risk % / 100) * Exposed Pop
    for _, row in df.iterrows():
        expected_score = int(round((row["Raw Risk %"] / 100.0) * row["Exposed Population (~2km)"]))
        assert abs(row["Priority Score"] - expected_score) <= 1, (
            f"Score mismatch: got {row['Priority Score']}, expected {expected_score}"
        )

    print("\nTop 5 Evacuate-First Hotspots:")
    for _, row in df.head(5).iterrows():
        print(f"  {row['Rank']} {row['Hotspot']} ({row['State']}) | "
              f"Risk: {row['Raw Risk %']}% | "
              f"Pop: {row['Exposed Population (~2km)']:,} | "
              f"Priority Score: {row['Priority Score']:,}")

    print("\n[OK] Prioritization Engine validated successfully.")


if __name__ == "__main__":
    test_geodesic_buffer()
    test_exposed_population_queries()
    test_hotspot_prioritization_engine()
    print("\n=======================================================")
    print(" ALL POPULATION PRIORITIZATION TESTS PASSED WITH 100% SUCCESS")
    print("=======================================================")
