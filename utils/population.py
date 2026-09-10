"""
Re-export of population estimation utilities from population.py.
"""
from population import (
    get_exposed_population,
    get_geodesic_buffer_polygon,
    calculate_hotspot_prioritization,
    render_population_prioritization_section,
    DEFAULT_RASTER_PATH
)

__all__ = [
    "get_exposed_population",
    "get_geodesic_buffer_polygon",
    "calculate_hotspot_prioritization",
    "render_population_prioritization_section",
    "DEFAULT_RASTER_PATH"
]
