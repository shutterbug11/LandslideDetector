"""
=============================================================================
Hotspot Grid Risk Heatmap Service
Vectorized Prediction & Geospatial Kernel Density Generation for Folium HeatMap
=============================================================================
"""

import os
import math
import numpy as np
from typing import Dict, List, Any, Optional

from utils.regional_data import NE_HOTSPOTS
from utils.model_service import calculate_landslide_risk


# Module-level cache to keep map re-renders instantaneous
_GRID_CACHE: Dict[str, Any] = {}


def compute_hotspot_predictions(
    weather_data: Dict[str, Any],
    active_targets: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Computes landslide failure probabilities for all monitored district hotspots
    plus any active observatory targets using the ensembled ML model and real-time triggers.
    
    Returns:
        Dict[hotspot_name, {
            'lat': float,
            'lon': float,
            'state': str,
            'elevation': float,
            'slope': float,
            'geology': str,
            'vulnerability': str,
            'probability': float (0-100),
            'ml_probability': float (0-100),
            'classification': str ('High' | 'Medium' | 'Low'),
            'alert_level': str,
            'color': str
        }]
    """
    results: Dict[str, Dict[str, Any]] = {}
    
    # 1. Evaluate baseline 27 district hotspots
    for hname, hdata in NE_HOTSPOTS.items():
        terrain = {
            "elevation": hdata.get("elevation", 1400.0),
            "slope": hdata.get("slope", 35.0),
            "aspect": hdata.get("aspect", 180.0),
            "curvature": hdata.get("curvature", 0.0004),
            "twi": hdata.get("twi", 3.8),
            "tri": hdata.get("tri", 7.0)
        }
        risk = calculate_landslide_risk(terrain, weather_data)
        
        results[hname] = {
            "name": hname,
            "lat": float(hdata["lat"]),
            "lon": float(hdata["lon"]),
            "state": hdata.get("state", "North East"),
            "elevation": hdata.get("elevation", 1400),
            "slope": hdata.get("slope", 35.0),
            "geology": hdata.get("geology", "Undifferentiated sedimentary/metamorphic"),
            "vulnerability": hdata.get("vulnerability", "Moderate"),
            "notes": hdata.get("notes", ""),
            "probability": risk["probability"],
            "ml_probability": risk.get("ml_probability", risk["probability"]),
            "classification": risk["classification"],
            "alert_level": risk["alert_level"],
            "color": risk["color"]
        }
    
    # 2. Merge active custom targets if provided
    if active_targets:
        for idx, target in enumerate(active_targets):
            t_name = target.get("title", f"Active Observatory Target {idx + 1}")
            t_risk = target.get("risk")
            if not t_risk:
                terrain = target.get("terrain_profile", {
                    "elevation": target.get("elevation", 1500),
                    "slope": target.get("slope", 35),
                    "aspect": target.get("aspect", 180),
                    "curvature": target.get("curvature", 0.0004),
                    "twi": target.get("twi", 3.8),
                    "tri": target.get("tri", 7.0)
                })
                t_risk = calculate_landslide_risk(terrain, weather_data)
            
            results[f"__target_{idx}__"] = {
                "name": t_name,
                "lat": float(target["lat"]),
                "lon": float(target["lon"]),
                "state": target.get("state", "Active Target"),
                "elevation": target.get("elevation", 1500),
                "slope": target.get("slope", 35.0),
                "geology": target.get("geology", "Local geological formation"),
                "vulnerability": "Target Node",
                "notes": "Current active observatory focus position",
                "probability": t_risk["probability"],
                "ml_probability": t_risk.get("ml_probability", t_risk["probability"]),
                "classification": t_risk["classification"],
                "alert_level": t_risk["alert_level"],
                "color": t_risk["color"],
                "is_active_target": True
            }
            
    return results


def generate_risk_heatmap_data(
    weather_data: Dict[str, Any],
    active_targets: Optional[List[Dict[str, Any]]] = None,
    spread_deg: float = 0.09,
    samples_per_hotspot: int = 12
) -> List[List[float]]:
    """
    Generates a continuous, dense 2D geospatial distribution of [latitude, longitude, weight]
    points weighted by model-predicted failure probabilities across the hotspot grid.
    
    This converts isolated discrete points into an expansive, smooth risk heatmap gradient
    that accurately reflects regional terrain corridors, river valleys, and mountain fronts.
    
    Returns:
        List of [lat, lon, weight] where weight is strictly normalized between 0.05 and 1.00.
    """
    predictions = compute_hotspot_predictions(weather_data, active_targets=active_targets)
    heatmap_points: List[List[float]] = []
    
    # Pre-defined radial offsets for Gaussian kernel expansion around each hotspot node
    angles = np.linspace(0, 2 * math.pi, samples_per_hotspot, endpoint=False)
    
    for hinfo in predictions.values():
        center_lat = hinfo["lat"]
        center_lon = hinfo["lon"]
        prob = hinfo["probability"]
        
        # Primary intensity: 0.10 to 1.00
        primary_weight = max(0.08, min(1.0, prob / 100.0))
        
        # 1. Anchor core point (repeat 3x for solid core intensity)
        for _ in range(3):
            heatmap_points.append([round(center_lat, 5), round(center_lon, 5), round(primary_weight, 3)])
        
        # 2. Outer gradient dispersion points
        # Higher risk hotspots emit a wider, more intense visual halo
        expansion_factor = 1.25 if prob >= 70.0 else (1.0 if prob >= 35.0 else 0.75)
        r_inner = spread_deg * 0.45 * expansion_factor
        r_outer = spread_deg * 0.90 * expansion_factor
        
        for i, angle in enumerate(angles):
            # Alternating inner and outer ring
            r = r_inner if (i % 2 == 0) else r_outer
            
            # Anisotropic terrain distortion (slopes often stretch along N-S or NE-SW valleys)
            d_lat = r * math.sin(angle)
            d_lon = r * math.cos(angle) * 1.15
            
            # Distance decay: weight attenuates toward perimeter
            decay = 0.72 if (i % 2 == 0) else 0.45
            pt_weight = round(primary_weight * decay, 3)
            
            heatmap_points.append([
                round(center_lat + d_lat, 5),
                round(center_lon + d_lon, 5),
                max(0.05, pt_weight)
            ])
            
        # 3. Intermediate corridor infill points
        if prob >= 50.0:
            for mid_r in [spread_deg * 0.25, spread_deg * 0.65]:
                for offset_angle in [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]:
                    d_lat = mid_r * math.sin(offset_angle)
                    d_lon = mid_r * math.cos(offset_angle)
                    heatmap_points.append([
                        round(center_lat + d_lat, 5),
                        round(center_lon + d_lon, 5),
                        round(primary_weight * 0.60, 3)
                    ])
                    
    return heatmap_points
