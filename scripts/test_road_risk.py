"""
=============================================================================
Verification Test for OSMnx Road & Infrastructure Risk Layer
Tests network download, metric CRS projection, buffer intersection,
citizen report nearest-edge blockage marking, and GeoJSON serialization.
=============================================================================
"""

import sys
import os

# Add project root to sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
from utils.roads import get_hotspot_roads, mark_blocked_edges, sanitize_edges_for_folium


def main():
    print("=" * 70)
    print("TEST 1: Direct OSMnx Query & Metric Buffer Test (Shillong, Meghalaya)")
    print("=" * 70)
    lat, lon = 25.578, 91.893  # Shillong, Meghalaya
    print(f"Target Hotspot: Lat {lat}, Lon {lon} | Query Radius: 5000m")

    G = ox.graph_from_point((lat, lon), dist=5000, network_type="drive")
    print(f"Successfully downloaded road network: {len(G.nodes)} nodes, {len(G.edges)} edges")

    G_proj = ox.project_graph(G)
    edges_proj = ox.graph_to_gdfs(G_proj, nodes=False)
    print(f"Projected Graph CRS: {edges_proj.crs} (Metric)")

    hotspot_proj = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(edges_proj.crs).iloc[0]
    buffer = hotspot_proj.buffer(2000)  # 2 km risk radius
    edges_proj["at_risk"] = edges_proj.intersects(buffer)

    at_risk_count = edges_proj["at_risk"].sum()
    total_edges = len(edges_proj)
    print(f"Edges at risk (within 2km buffer): {at_risk_count} out of {total_edges} ({at_risk_count/total_edges*100:.1f}%)")
    assert at_risk_count > 0, "Expected at least one edge in 2km buffer!"

    print("\n" + "=" * 70)
    print("TEST 2: utils.roads get_hotspot_roads & mark_blocked_edges")
    print("=" * 70)
    graph, edges = get_hotspot_roads(lat, lon, radius_m=5000)
    assert graph is not None, "Graph should not be None"
    assert edges is not None, "Edges should not be None"
    print(f"get_hotspot_roads returned GeoDataFrame with columns: {list(edges.columns)}")
    assert "at_risk" in edges.columns, "Expected 'at_risk' in edges"
    assert "blocked" in edges.columns, "Expected 'blocked' in edges"

    # Simulate a citizen report near Shillong center
    simulated_reports = [
        {
            "lat": 25.575,
            "lon": 91.890,
            "report_type": "blocked_road",
            "description": "Massive rockfall blocking arterial road"
        },
        {
            "lat": 25.580,
            "lon": 91.895,
            "report_type": "minor_crack",  # Should NOT be marked as blocked
            "description": "Minor tension cracks"
        }
    ]

    edges = mark_blocked_edges(edges, graph, simulated_reports)
    blocked_count = edges["blocked"].sum()
    print(f"Blocked road edges marked: {blocked_count}")
    assert blocked_count > 0, "Expected at least one edge to be marked blocked!"

    print("\n" + "=" * 70)
    print("TEST 3: GeoJSON Serialization for Folium")
    print("=" * 70)
    clean_edges = sanitize_edges_for_folium(edges)
    json_str = clean_edges.to_json()
    print(f"Successfully serialized to GeoJSON ({len(json_str)} bytes)")
    assert len(json_str) > 1000, "GeoJSON payload should be substantial"

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! OSMnx ROAD RISK PIPELINE IS FULLY OPERATIONAL.")
    print("=" * 70)


if __name__ == "__main__":
    main()
