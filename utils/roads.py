"""
=============================================================================
Road & Infrastructure Risk Layer Service
Integrates OpenStreetMap (OSMnx) to identify roads intersecting landslide
buffer zones and citizen-reported road blockages.
=============================================================================
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
import streamlit as st
import osmnx as ox
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

logger = logging.getLogger(__name__)


@st.cache_data(show_spinner="Loading nearby road network...")
def _load_hotspot_roads_cached(lat: float, lon: float, radius_m: int = 5000) -> Tuple[Any, Any]:
    """
    Downloads the drivable road network around (lat, lon) within radius_m meters.
    Projects to a metric CRS to calculate a true metric buffer (2000m),
    and flags intersecting edges with at_risk=True.
    Returns (graph, edges_gdf_latlon).
    """
    try:
        # 1. Download drivable street network
        G = ox.graph_from_point((lat, lon), dist=radius_m, network_type="drive")
        if G is None or len(G.nodes) == 0:
            logger.warning(f"No road nodes found within {radius_m}m of ({lat}, {lon})")
            return None, None
    except Exception as e:
        logger.warning(f"Road network unavailable for ({lat}, {lon}): {e}")
        try:
            st.warning(f"Road network unavailable for this hotspot: {e}")
        except Exception:
            pass
        return None, None

    try:
        # 2. Project to metric CRS for accurate meter-based buffering
        G_proj = ox.project_graph(G)
        edges_proj = ox.graph_to_gdfs(G_proj, nodes=False)

        # 3. Create ~2000m risk buffer around hotspot in projected CRS
        hotspot_proj = gpd.GeoSeries([Point(lon, lat)], crs="EPSG:4326").to_crs(edges_proj.crs).iloc[0]
        buffer = hotspot_proj.buffer(2000)  # 2 km risk radius
        edges_proj["at_risk"] = edges_proj.intersects(buffer)

        # 4. Extract unprojected edges (EPSG:4326) for Folium
        edges_latlon = ox.graph_to_gdfs(G, nodes=False)
        edges_latlon["at_risk"] = edges_proj["at_risk"].values
        edges_latlon["blocked"] = False

        return G, edges_latlon
    except Exception as e:
        logger.warning(f"Error processing road network for ({lat}, {lon}): {e}")
        return None, None


def get_hotspot_roads(lat: float, lon: float, radius_m: int = 5000) -> Tuple[Any, Any]:
    """
    Retrieves the road network around (lat, lon) within radius_m meters.
    Keys on rounded (lat, lon, radius_m) to prevent repeated downloads on
    minor coordinate adjustments and Streamlit reruns.
    Returns (graph, edges_gdf) where edges_gdf is in EPSG:4326.
    """
    lat_rounded = round(float(lat), 3)
    lon_rounded = round(float(lon), 3)
    G, edges = _load_hotspot_roads_cached(lat_rounded, lon_rounded, radius_m=radius_m)
    if edges is not None:
        # Return a copy to avoid in-place mutations of cached GeoDataFrame
        return G, edges.copy()
    return None, None


def mark_blocked_edges(edges_gdf: gpd.GeoDataFrame, graph: Any, reports: List[Dict[str, Any]]) -> gpd.GeoDataFrame:
    """
    For each citizen report with report_type == 'blocked_road', finds the nearest
    edge in graph and sets blocked=True on that edge in edges_gdf.
    """
    if edges_gdf is None or graph is None or not reports:
        return edges_gdf

    edges_gdf = edges_gdf.copy()
    if "blocked" not in edges_gdf.columns:
        edges_gdf["blocked"] = False

    for r in reports:
        # Check report type
        rtype = r.get("report_type")
        if rtype != "blocked_road":
            continue

        lat = r.get("lat") if "lat" in r else r.get("latitude")
        lon = r.get("lon") if "lon" in r else r.get("longitude")
        if lat is None or lon is None:
            continue

        try:
            res = ox.distance.nearest_edges(graph, X=float(lon), Y=float(lat))
            # Handle return format (u, v, key) or (u, v)
            if isinstance(res, (tuple, list)):
                u, v = res[0], res[1]
            else:
                continue

            if isinstance(edges_gdf.index, pd.MultiIndex):
                match = (edges_gdf.index.get_level_values(0) == u) & \
                        (edges_gdf.index.get_level_values(1) == v)
            elif "u" in edges_gdf.columns and "v" in edges_gdf.columns:
                match = (edges_gdf["u"] == u) & (edges_gdf["v"] == v)
            else:
                continue

            edges_gdf.loc[match, "blocked"] = True
        except Exception as e:
            logger.debug(f"Could not map report at ({lat}, {lon}) to road edge: {e}")
            continue

    return edges_gdf


def sanitize_edges_for_folium(edges_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Cleans up GeoDataFrame columns that may contain lists or dictionaries
    (common in OSMnx attributes like 'highway', 'lanes', 'ref') so that
    Folium's GeoJSON serializer executes cleanly without TypeError.
    """
    if edges_gdf is None:
        return edges_gdf

    clean = edges_gdf.copy()
    for col in clean.columns:
        if col == "geometry":
            continue
        clean[col] = clean[col].apply(
            lambda v: ", ".join(map(str, v)) if isinstance(v, list) else (str(v) if isinstance(v, dict) else v)
        )

    # Provide friendly default names
    if "name" not in clean.columns:
        clean["name"] = "Transit Corridor"
    else:
        clean["name"] = clean["name"].fillna("Transit Corridor")

    if "highway" not in clean.columns:
        clean["highway"] = "road"
    else:
        clean["highway"] = clean["highway"].fillna("road")

    return clean
