"""
Population estimation and hotspot prioritization module using WorldPop gridded population data for India (NER).
Computes exposed population within a geodesic buffer radius around landslide hotspots and derives priority action ranking.

Formula:
    Priority Score = (Risk Probability [0 - 1]) * Exposed Population (~2km buffer)

Attribution:
    Population data: WorldPop (CC-BY 4.0)
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import pandas as pd
import pyproj
from shapely.geometry import Polygon
import streamlit as st

# Base path for clipped NER population raster
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_RASTER_PATH = BASE_DIR / "data" / "ner_population_2020.tif"


def get_geodesic_buffer_polygon(lat: float, lon: float, radius_m: float = 2000.0, n_points: int = 64) -> Polygon:
    """
    Generate an accurate geodesic circle polygon (WGS84 coordinates: lon, lat)
    without latitude distortion using pyproj.Geod.
    """
    geod = pyproj.Geod(ellps="WGS84")
    angles = np.linspace(0, 360, n_points, endpoint=False)
    lons2, lats2, _ = geod.fwd(
        [lon] * n_points,
        [lat] * n_points,
        angles,
        [radius_m] * n_points
    )
    return Polygon(zip(lons2, lats2))


@st.cache_data(show_spinner=False)
def get_exposed_population(
    lat: float,
    lon: float,
    radius_m: int = 2000,
    raster_path: Optional[str] = None
) -> float:
    """
    Estimate exposed population within a `radius_m` meter radius of (lat, lon)
    using WorldPop gridded raster data and zonal statistics.

    Parameters
    ----------
    lat : float
        Latitude of the hotspot (WGS84)
    lon : float
        Longitude of the hotspot (WGS84)
    radius_m : int, default 2000
        Buffer radius in meters (geodesic distance)
    raster_path : str, optional
        Path to population GeoTIFF. Defaults to data/ner_population_2020.tif

    Returns
    -------
    float
        Sum of estimated population in the buffer zone, or 0.0 if data unavailable.
    """
    try:
        from rasterstats import zonal_stats

        target_path = Path(raster_path) if raster_path else DEFAULT_RASTER_PATH
        if not target_path.exists():
            return 0.0

        poly = get_geodesic_buffer_polygon(lat=lat, lon=lon, radius_m=float(radius_m))
        stats = zonal_stats(poly, str(target_path), stats=["sum"], all_touched=True)

        if stats and len(stats) > 0:
            val = stats[0].get("sum")
            if val is not None and not np.isnan(val):
                return max(0.0, float(val))

        return 0.0
    except Exception:
        # Fail gracefully to 0.0 without breaking app execution
        return 0.0


def calculate_hotspot_prioritization(
    hotspot_preds: Dict[str, Dict[str, Any]],
    radius_m: int = 2000
) -> pd.DataFrame:
    """
    Computes priority evacuation score for all monitored hotspots.
    
    Priority Score = (raw_risk_percentage / 100.0) * exposed_population
    Represents expected directly affected population in the active zone.
    """
    rows: List[Dict[str, Any]] = []

    for hname, hinfo in hotspot_preds.items():
        lat = float(hinfo.get("lat", 0.0))
        lon = float(hinfo.get("lon", 0.0))
        raw_prob = float(hinfo.get("probability", 0.0))
        risk_float = raw_prob / 100.0  # Normalized 0 - 1

        pop = get_exposed_population(lat, lon, radius_m=radius_m)
        priority_score = risk_float * pop

        classification = hinfo.get("classification", "Medium")
        state = hinfo.get("state", "North East")
        is_active = hinfo.get("is_active_target", False)

        display_name = f"{hname} [Active Target]" if is_active else hname

        rows.append({
            "Hotspot": display_name,
            "State": state,
            "Hazard Level": f"{classification.title()} Hazard",
            "Raw Risk %": round(raw_prob, 1),
            "Exposed Population (~2km)": int(round(pop)),
            "Priority Score": int(round(priority_score)),
            "_raw_priority": priority_score,
            "_raw_risk": raw_prob,
            "_raw_pop": pop,
            "_state": state,
        })

    if not rows:
        return pd.DataFrame(columns=[
            "Rank", "Hotspot", "State", "Hazard Level", "Raw Risk %",
            "Exposed Population (~2km)", "Priority Score"
        ])

    df = pd.DataFrame(rows).sort_values(by="_raw_priority", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", [f"#{i+1}" for i in range(len(df))])
    return df


def render_population_prioritization_section(
    hotspot_preds: Dict[str, Dict[str, Any]],
    target_lang: str = "English",
    key_prefix: str = "main"
) -> None:
    """
    Renders the 'Evacuate First' population-weighted prioritization dashboard section.
    Displays KPI summary cards, interactive state filter, ranked data table, and WorldPop attribution.
    """
    try:
        from translate import translate_text
    except ImportError:
        def translate_text(text: str, *args, **kwargs) -> str:
            return text

    st.markdown("---")
    title_text = translate_text("Evacuate First: Population-Weighted Hotspot Prioritization", target_lang)
    st.markdown(f"<div class='section-title'>{title_text}</div>", unsafe_allow_html=True)

    desc_text = translate_text(
        "Identifies emergency evacuation and NDRF staging priorities by weighting model failure probabilities "
        "against human settlement density from WorldPop gridded population data within a 2km radius.",
        target_lang
    )
    formula_note = translate_text(
        "Priority Score = Risk Probability (0 - 1) × Exposed Population (~2km geodesic buffer). "
        "Represents expected affected individuals requiring immediate protective action.",
        target_lang
    )

    st.markdown(f"""
    <div style="font-size: 0.84rem; color: #334155; background: #FFFFFF; padding: 0.85rem 1.1rem; border-radius: 6px; border: 1px solid #CBD5E1; border-left: 4px solid #1B4965; margin-bottom: 1.1rem;">
        <strong style="color: #1B4965;">Operational Protocol:</strong> {desc_text}<br>
        <span style="font-size: 0.78rem; color: #64748B;"><strong>Formula:</strong> {formula_note}</span>
    </div>
    """, unsafe_allow_html=True)

    df = calculate_hotspot_prioritization(hotspot_preds, radius_m=2000)
    if df.empty:
        st.info("No hotspot telemetry available for prioritization analysis.")
        return

    # Top KPI Metrics
    top_row = df.iloc[0]
    total_exposed = df["_raw_pop"].sum()
    total_expected_affected = df["_raw_priority"].sum()
    high_hazard_count = len(df[df["_raw_risk"] >= 70.0])

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        top_name = str(top_row["Hotspot"]).replace("[Active Target]", "").strip()
        st.metric(
            label=translate_text("Top Evacuation Priority", target_lang),
            value=top_name[:18] + ("…" if len(top_name) > 18 else ""),
            delta=f"{top_row['Priority Score']:,} score"
        )
    with kpi2:
        st.metric(
            label=translate_text("Total Expected Affected", target_lang),
            value=f"{int(round(total_expected_affected)):,}",
            help="Sum of Priority Scores across all monitored locations"
        )
    with kpi3:
        st.metric(
            label=translate_text("Total Population in Zones", target_lang),
            value=f"{int(round(total_exposed)):,}",
            help="Total individuals residing within 2km of all monitored hotspots"
        )
    with kpi4:
        st.metric(
            label=translate_text("High Hazard Nodes (>70%)", target_lang),
            value=f"{high_hazard_count} of {len(df)}",
            delta=f"{round((high_hazard_count/len(df))*100, 1)}% of grid" if len(df) > 0 else None,
            delta_color="inverse"
        )

    # Filtering controls
    fcol1, fcol2 = st.columns([2, 2])
    with fcol1:
        all_states = ["All States"] + sorted(list(df["_state"].unique()))
        selected_state = st.selectbox(
            translate_text("Filter by Region / State", target_lang),
            all_states,
            index=0,
            key=f"{key_prefix}_prio_state_filter"
        )
    with fcol2:
        display_limit = st.radio(
            translate_text("Display View", target_lang),
            ["Top 5 Urgent", "Top 10 Critical", "All Hotspots"],
            index=1,
            horizontal=True,
            key=f"{key_prefix}_prio_limit_radio"
        )

    filtered_df = df.copy()
    if selected_state != "All States":
        filtered_df = filtered_df[filtered_df["_state"] == selected_state].reset_index(drop=True)
        # Recalculate rank for state-filtered slice
        filtered_df["Rank"] = [f"#{i+1}" for i in range(len(filtered_df))]

    if display_limit == "Top 5 Urgent":
        filtered_df = filtered_df.head(5)
    elif display_limit == "Top 10 Critical":
        filtered_df = filtered_df.head(10)

    # Clean display columns
    display_columns = [
        "Rank", "Hotspot", "State", "Hazard Level",
        "Raw Risk %", "Exposed Population (~2km)", "Priority Score"
    ]
    render_df = filtered_df[display_columns]

    st.dataframe(
        render_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rank": st.column_config.TextColumn("Rank", width="small"),
            "Hotspot": st.column_config.TextColumn("Hotspot / Target", width="large"),
            "State": st.column_config.TextColumn("State", width="medium"),
            "Hazard Level": st.column_config.TextColumn("Hazard Level", width="medium"),
            "Raw Risk %": st.column_config.ProgressColumn(
                "Raw Risk %",
                help="Real-time model failure probability",
                format="%.1f%%",
                min_value=0.0,
                max_value=100.0,
                width="medium"
            ),
            "Exposed Population (~2km)": st.column_config.NumberColumn(
                "Exposed Pop (~2km)",
                help="Estimated population within 2km geodesic radius from WorldPop 2020",
                format="%d",
                width="medium"
            ),
            "Priority Score": st.column_config.NumberColumn(
                "Priority Score",
                help="Priority Score = (Raw Risk % / 100) × Exposed Population (~2km)",
                format="%d",
                width="medium"
            ),
        }
    )

    # Attribution caption
    st.caption(translate_text("Population data: WorldPop (CC-BY 4.0) · 100m Gridded UN-Adjusted Dataset for India", target_lang))
