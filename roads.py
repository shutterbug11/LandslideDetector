"""
=============================================================================
Road & Infrastructure Risk Layer Interface
Re-exports core functions from utils.roads for convenient top-level access.
=============================================================================
"""

from utils.roads import (
    get_hotspot_roads,
    mark_blocked_edges,
    sanitize_edges_for_folium
)

__all__ = [
    "get_hotspot_roads",
    "mark_blocked_edges",
    "sanitize_edges_for_folium"
]
