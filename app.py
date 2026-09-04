"""
=============================================================================
North Eastern Region (India) Landslide Early Warning System
Real-Time Weather Integration (Open-Meteo & OpenWeather) + LightGBM ML Engine
Professional Scientific Observatory Edition - Dual Location Comparison
=============================================================================
"""

import os
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium

from datetime import datetime
from utils.regional_data import NE_STATES, NE_HOTSPOTS, SDMA_CONTACTS
from utils.weather_service import fetch_openmeteo_weather
from utils.model_service import calculate_landslide_risk, load_assets
from utils.pdf_generator import generate_landslide_pdf_report
from utils.comparison_service import (
    calculate_haversine_distance,
    compute_comparison_deltas,
    create_comparative_soil_moisture_chart,
    create_comparative_forecast_chart,
    create_side_by_side_gauge
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NE India Landslide Early Warning System",
    page_icon="assets/favicon.png" if False else None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# CUSTOM PROFESSIONAL CSS STYLING
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Typography */
    .main-title {
        font-size: 2.15rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        margin-bottom: 0.25rem;
        line-height: 1.2;
    }
    .sub-title {
        font-size: 0.92rem;
        color: #94A3B8;
        margin-bottom: 1.35rem;
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* Professional Card System */
    .card {
        background: rgba(128, 128, 128, 0.06);
        border: 1px solid rgba(128, 128, 128, 0.16);
        border-radius: 10px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        margin-bottom: 0.75rem;
        transition: all 0.2s ease-in-out;
    }
    .card:hover {
        border-color: rgba(128, 128, 128, 0.32);
        background: rgba(128, 128, 128, 0.10);
    }
    
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.025em;
        line-height: 1.2;
        margin-top: 0.2rem;
    }
    .metric-label {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    .metric-sub {
        font-size: 0.76rem;
        color: #64748B;
        margin-top: 0.35rem;
    }

    /* Comparison Pin Badges & Cards */
    .pin-badge-a {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(2, 132, 199, 0.18);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.45);
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .pin-badge-b {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(244, 63, 94, 0.18);
        color: #FB7185;
        border: 1px solid rgba(251, 113, 133, 0.45);
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    
    .compare-card {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.18);
        border-radius: 10px;
        padding: 1.1rem 1.25rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
        margin-bottom: 0.75rem;
    }
    
    .compare-delta-pill {
        display: inline-block;
        padding: 0.15rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.72rem;
        font-weight: 700;
        margin-top: 0.35rem;
    }
    .delta-higher {
        background: rgba(239, 68, 68, 0.18);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.35);
    }
    .delta-lower {
        background: rgba(16, 185, 129, 0.18);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .delta-neutral {
        background: rgba(148, 163, 184, 0.15);
        color: #94A3B8;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
    
    /* Status Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.4rem 1rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .status-low {
        background: rgba(16, 185, 129, 0.12);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.32);
    }
    .status-medium {
        background: rgba(245, 158, 11, 0.12);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.32);
    }
    .status-high {
        background: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .dot-low { background-color: #10B981; box-shadow: 0 0 8px #10B981; }
    .dot-medium { background-color: #F59E0B; box-shadow: 0 0 8px #F59E0B; }
    .dot-high { background-color: #EF4444; box-shadow: 0 0 10px #EF4444; }

    /* Download Report Button Styling */
    .stDownloadButton button {
        background: rgba(128, 128, 128, 0.08) !important;
        border: 1px solid rgba(128, 128, 128, 0.25) !important;
        color: var(--text-color, #F8FAFC) !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.02em !important;
        border-radius: 8px !important;
        padding: 0.42rem 0.9rem !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    }
    .stDownloadButton button:hover {
        background: rgba(2, 132, 199, 0.15) !important;
        border-color: #0284C7 !important;
        color: #0284C7 !important;
        transform: translateY(-1px) !important;
    }

    /* Section Headings */
    .section-title {
        font-size: 1.15rem;
        font-weight: 600;
        letter-spacing: -0.015em;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* System Header Banner in Sidebar */
    .sidebar-header {
        padding: 0.4rem 0 1rem 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 1rem;
    }
    .sidebar-agency {
        font-size: 0.68rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #0284C7;
        font-weight: 700;
    }
    .sidebar-title {
        font-size: 1.22rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-top: 0.25rem;
    }
    .sidebar-region {
        font-size: 0.78rem;
        color: #64748B;
        margin-top: 0.15rem;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# HELPER: SIDEBAR LOCATION INPUT COMPONENT
# -----------------------------------------------------------------------------
def get_location_profile_from_sidebar(
    key_prefix: str,
    label: str,
    pin_badge_class: str,
    default_state_idx: int = 0,
    default_hotspot_idx: int = 0
) -> dict:
    """
    Renders sidebar inputs for either preset hotspots or custom coordinates
    and returns a structured location profile dictionary.
    """
    st.markdown(f"<div class='{pin_badge_class}'>● {label}</div>", unsafe_allow_html=True)
    
    sel_mode = st.radio(
        f"Input Mode ({label})",
        ["Preset Vulnerable Hotspots", "Custom GPS Coordinates"],
        key=f"{key_prefix}_sel_mode",
        label_visibility="collapsed"
    )

    if sel_mode == "Preset Vulnerable Hotspots":
        sel_state = st.selectbox(
            f"State ({label})",
            NE_STATES,
            index=min(default_state_idx, len(NE_STATES) - 1),
            key=f"{key_prefix}_state"
        )
        state_hotspots = {k: v for k, v in NE_HOTSPOTS.items() if v["state"] == sel_state}
        hotspot_names = list(state_hotspots.keys())
        
        idx = min(default_hotspot_idx, len(hotspot_names) - 1) if hotspot_names else 0
        sel_hotspot = st.selectbox(
            f"District / Corridor ({label})",
            hotspot_names,
            index=idx,
            key=f"{key_prefix}_hotspot"
        )
        
        loc_data = state_hotspots.get(sel_hotspot, list(NE_HOTSPOTS.values())[0])
        return {
            "title": sel_hotspot,
            "lat": loc_data["lat"],
            "lon": loc_data["lon"],
            "elevation": loc_data["elevation"],
            "slope": loc_data["slope"],
            "aspect": loc_data["aspect"],
            "curvature": loc_data["curvature"],
            "twi": loc_data["twi"],
            "tri": loc_data["tri"],
            "state": loc_data["state"],
            "geology": loc_data["geology"],
            "notes": loc_data["notes"],
            "vulnerability": loc_data.get("vulnerability", "Moderate"),
            "terrain_profile": {
                "elevation": loc_data["elevation"],
                "slope": loc_data["slope"],
                "aspect": loc_data["aspect"],
                "curvature": loc_data["curvature"],
                "twi": loc_data["twi"],
                "tri": loc_data["tri"]
            }
        }
    else:
        st.markdown(f"**Manual Coordinates ({label})**")
        lat = st.number_input(
            f"Latitude °N ({label})",
            min_value=21.0, max_value=30.0,
            value=27.3389 if key_prefix == "loc_a" else 27.5042,
            step=0.01, format="%.4f",
            key=f"{key_prefix}_lat"
        )
        lon = st.number_input(
            f"Longitude °E ({label})",
            min_value=88.0, max_value=98.0,
            value=88.6065 if key_prefix == "loc_a" else 88.5298,
            step=0.01, format="%.4f",
            key=f"{key_prefix}_lon"
        )
        elev = st.slider(f"Elevation m ({label})", 50, 4500, 1600 if key_prefix == "loc_a" else 1310, step=50, key=f"{key_prefix}_elev")
        slope = st.slider(f"Terrain Slope ° ({label})", 5.0, 75.0, 36.0 if key_prefix == "loc_a" else 44.0, step=1.0, key=f"{key_prefix}_slope")
        aspect = st.slider(f"Slope Aspect ° ({label})", 0.0, 360.0, 180.0, step=10.0, key=f"{key_prefix}_aspect")
        
        return {
            "title": f"Custom Position ({lat:.3f}°N, {lon:.3f}°E)",
            "lat": lat,
            "lon": lon,
            "elevation": elev,
            "slope": slope,
            "aspect": aspect,
            "curvature": 0.0004,
            "twi": 3.8,
            "tri": 7.0,
            "state": "Custom North East Location",
            "geology": "Complex Himalayan / Indo-Burman metamorphic rock sequence",
            "notes": "User-defined coordinate assessment.",
            "vulnerability": "High" if slope >= 35 else "Moderate",
            "terrain_profile": {
                "elevation": elev,
                "slope": slope,
                "aspect": aspect,
                "curvature": 0.0004,
                "twi": 3.8,
                "tri": 7.0
            }
        }


# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS & WORKFLOW MODE
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-agency">Earth Observation & Hazard Mitigation</div>
        <div class="sidebar-title">Landslide Early Warning</div>
        <div class="sidebar-region">North Eastern Himalayan Region, India</div>
    </div>
    """, unsafe_allow_html=True)

    app_mode = st.radio(
        "Observation Mode",
        ["Single Location Observatory", "Compare Locations (Dual Mode)"],
        index=0,
        help="Select between monitoring a single high-priority sector or pinning two locations simultaneously for a side-by-side risk and meteorological comparison."
    )

    st.markdown("---")

    if app_mode == "Single Location Observatory":
        st.subheader("Geographic Scope & Target")
        loc_a = get_location_profile_from_sidebar("loc_single", "Target Location", "pin-badge-a", default_state_idx=0, default_hotspot_idx=0)
        loc_b = None
    else:
        st.subheader("Pin Two Locations to Compare")

        # Preset Pair Quick Selector
        preset_pairs = {
            "Custom Pair Selection": None,
            "Gangtok vs Mangan (Sikkim High Altitude)": ("Sikkim", 0, "Sikkim", 1),
            "Shillong vs Cherrapunji (Meghalaya Plateau)": ("Meghalaya", 0, "Meghalaya", 1),
            "Kohima vs Dimapur (Nagaland Rift Corridor)": ("Nagaland", 0, "Nagaland", 1),
            "Aizawl vs Lunglei (Mizoram Fold Belts)": ("Mizoram", 0, "Mizoram", 1),
            "Itanagar vs Tawang (Arunachal Foothills vs Ridge)": ("Arunachal Pradesh", 0, "Arunachal Pradesh", 1),
        }
        selected_pair_key = st.selectbox("Quick Comparison Preset", list(preset_pairs.keys()), index=0)

        # Handle Preset Selection
        pair_val = preset_pairs[selected_pair_key]
        if pair_val is not None:
            state_a_name, idx_a, state_b_name, idx_b = pair_val
            st_a_idx = NE_STATES.index(state_a_name) if state_a_name in NE_STATES else 0
            st_b_idx = NE_STATES.index(state_b_name) if state_b_name in NE_STATES else 0
        else:
            st_a_idx, idx_a = 0, 0
            st_b_idx, idx_b = 0, 1

        # Pin A & Pin B in separate expanders or sections
        st.markdown("#### Location A (Primary Pin)")
        loc_a = get_location_profile_from_sidebar("loc_a", "Pinned Location A", "pin-badge-a", default_state_idx=st_a_idx, default_hotspot_idx=idx_a)

        st.markdown("---")
        st.markdown("#### Location B (Comparison Pin)")
        loc_b = get_location_profile_from_sidebar("loc_b", "Pinned Location B", "pin-badge-b", default_state_idx=st_b_idx, default_hotspot_idx=idx_b)

    st.markdown("---")
    st.caption("""
    **Advisory Tiers (GSI / NDMA Standard):**
    * **Low Risk (<35%)**: Baseline stability, normal vigilance
    * **Medium Risk (35-70%)**: Saturated slope conditions, caution advised
    * **High Risk (>70%)**: Critical failure probability, evacuation protocol
    """)


# =============================================================================
# DATA FETCHING & PREDICTION ENGINE
# =============================================================================
fallback_weather = {
    "current": {"temperature": 18.5, "apparent_temperature": 18.2, "humidity": 82, "precipitation_rate": 2.5, "rain_rate": 2.5},
    "triggers": {"rain_past_24h": 45.0, "rain_past_48h": 85.0, "rain_past_72h": 120.0, "rain_past_7d": 190.0, "soil_moisture_top": 0.38, "soil_moisture_mid": 0.35, "soil_moisture_deep": 0.33, "soil_moisture_mean": 0.35}
}

if app_mode == "Single Location Observatory":
    with st.spinner(f"Acquiring satellite meteorological telemetry for {loc_a['title']}..."):
        weather_a = fetch_openmeteo_weather(loc_a["lat"], loc_a["lon"], past_days=7, forecast_days=14)
    if weather_a.get("status") == "success":
        risk_a = calculate_landslide_risk(loc_a["terrain_profile"], weather_a)
    else:
        risk_a = calculate_landslide_risk(loc_a["terrain_profile"], fallback_weather)
        weather_a = fallback_weather
    weather_b, risk_b = None, None
else:
    with st.spinner("Acquiring dual-station satellite meteorological telemetry..."):
        weather_a = fetch_openmeteo_weather(loc_a["lat"], loc_a["lon"], past_days=7, forecast_days=14)
        weather_b = fetch_openmeteo_weather(loc_b["lat"], loc_b["lon"], past_days=7, forecast_days=14)

    if weather_a.get("status") == "success":
        risk_a = calculate_landslide_risk(loc_a["terrain_profile"], weather_a)
    else:
        risk_a = calculate_landslide_risk(loc_a["terrain_profile"], fallback_weather)
        weather_a = fallback_weather

    if weather_b.get("status") == "success":
        risk_b = calculate_landslide_risk(loc_b["terrain_profile"], weather_b)
    else:
        risk_b = calculate_landslide_risk(loc_b["terrain_profile"], fallback_weather)
        weather_b = fallback_weather


# =============================================================================
# VIEW 1: SINGLE LOCATION OBSERVATORY (ORIGINAL FLOW)
# =============================================================================
if app_mode == "Single Location Observatory":
    col_h1, col_h2, col_h3 = st.columns([5, 2.8, 2.2])

    classification_str = risk_a['classification'].lower()
    status_class = f"status-{classification_str}"
    dot_class = f"dot-{classification_str}"

    with col_h1:
        st.markdown(f"<div class='main-title'>{loc_a['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='sub-title'>
            State: <b>{loc_a['state']}</b> &nbsp;|&nbsp; 
            Elevation: <b>{loc_a['elevation']:,} m</b> &nbsp;|&nbsp; 
            Slope Gradient: <b>{loc_a['slope']}°</b> &nbsp;|&nbsp; 
            Geology: <i>{loc_a['geology']}</i>
        </div>
        """, unsafe_allow_html=True)

    with col_h2:
        st.markdown(f"""
        <div style="text-align: right; padding-top: 0.25rem;">
            <div class="status-pill {status_class}">
                <span class="status-dot {dot_class}"></span> {risk_a['classification'].upper()} RISK
            </div>
            <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 0.35rem; font-weight: 500;">
                {risk_a['alert_level']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_h3:
        sdma_contact = SDMA_CONTACTS.get(loc_a['state'], SDMA_CONTACTS["Sikkim"])
        pdf_bytes = generate_landslide_pdf_report(
            location_title=loc_a['title'],
            target_state=loc_a['state'],
            target_lat=loc_a['lat'],
            target_lon=loc_a['lon'],
            terrain_profile=loc_a['terrain_profile'],
            target_geology=loc_a['geology'],
            target_notes=loc_a['notes'],
            risk_output=risk_a,
            weather_res=weather_a,
            sdma_contact=sdma_contact
        )
        safe_name = "".join(c for c in loc_a['title'] if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
        report_filename = f"Hazard_Report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        st.markdown("<div style='padding-top: 0.35rem;'></div>", unsafe_allow_html=True)
        st.download_button(
            label="Export Report as PDF",
            data=pdf_bytes,
            file_name=report_filename,
            mime="application/pdf",
            use_container_width=True
        )

    # Alert Callout
    if risk_a['classification'] == "High":
        st.error(f"""
        **Critical Hazard Alert Active for {loc_a['title']}:**  
        Antecedent rainfall ({risk_a['thresholds']['rain_72h']:.1f} mm in 72h) and subsurface moisture saturation have breached safety thresholds on this {loc_a['slope']}° slope. 
        Immediate Action: Avoid hillside road cuts, monitor retaining structures, and follow local district evacuation guidelines.
        """)
    elif risk_a['classification'] == "Medium":
        st.warning(f"""
        **Elevated Slope Stability Advisory for {loc_a['title']}:**  
        Moderate saturation detected on {loc_a['slope']}° terrain. Persistent precipitation may initiate localized debris flows. Heightened vigilance recommended along transit corridors.
        """)

    # Top Metric Cards
    curr_weather = weather_a.get("current", {})
    triggers = weather_a.get("triggers", {})

    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    with mcol1:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Landslide Probability</div>
            <div class="metric-value" style="color: {risk_a['color']};">{risk_a['probability']}%</div>
            <div class="metric-sub">Ensemble Geo-Hydrological</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol2:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">24h Rainfall Total</div>
            <div class="metric-value">{triggers.get('rain_past_24h', 0.0):.1f} mm</div>
            <div class="metric-sub">72h Total: {triggers.get('rain_past_72h', 0.0):.1f} mm</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol3:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Topsoil Saturation (0-9cm)</div>
            <div class="metric-value">{triggers.get('soil_moisture_top', 0.25)*100:.1f}%</div>
            <div class="metric-sub">Subsoil: {triggers.get('soil_moisture_deep', 0.30)*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol4:
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Surface Temperature</div>
            <div class="metric-value">{curr_weather.get('temperature', 20.0):.1f} °C</div>
            <div class="metric-sub">Apparent: {curr_weather.get('apparent_temperature', 20.0):.1f} °C</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol5:
        humidity_val = curr_weather.get('humidity', 75)
        st.markdown(f"""
        <div class="card">
            <div class="metric-label">Relative Humidity</div>
            <div class="metric-value">{humidity_val:.0f}%</div>
            <div class="metric-sub">Current Rain Rate: {curr_weather.get('precipitation_rate', 0.0):.1f} mm/h</div>
        </div>
        """, unsafe_allow_html=True)

    # Map & Gauge Section
    col_map, col_gauge = st.columns([3, 2])
    with col_map:
        st.markdown("<div class='section-title'>Regional Hazard & Susceptibility Map</div>", unsafe_allow_html=True)
        m_ctrl1, m_ctrl2 = st.columns([3, 2])
        with m_ctrl1:
            show_heatmap = st.checkbox("Enable Susceptibility Heatmap Distribution", value=True)
        with m_ctrl2:
            heatmap_radius = st.slider("Heatmap Blur Radius", min_value=12, max_value=32, value=18, step=2)

        m = folium.Map(location=[26.1, 92.9], zoom_start=7, tiles="CartoDB positron", control_scale=True)
        folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite High-Resolution', overlay=False, control=True).add_to(m)
        folium.TileLayer(tiles='OpenStreetMap', name='OpenStreetMap', overlay=False, control=True).add_to(m)

        if show_heatmap:
            heat_points_path = os.path.join("output", "susceptibility_points.json")
            if os.path.exists(heat_points_path):
                with open(heat_points_path, "r") as f:
                    heat_points = json.load(f)
                heat_fg = folium.FeatureGroup(name="Susceptibility Risk Heatmap", show=True)
                HeatMap(heat_points, min_opacity=0.40, max_zoom=14, radius=heatmap_radius, blur=14,
                        gradient={0.20: '#10B981', 0.45: '#38BDF8', 0.65: '#F59E0B', 0.85: '#EF4444', 1.00: '#7F1D1D'}).add_to(heat_fg)
                heat_fg.add_to(m)

        hotspots_fg = folium.FeatureGroup(name="Monitored District Hotspots", show=True)
        for hname, hdata in NE_HOTSPOTS.items():
            if hdata["vulnerability"] in ["Critical", "Very High"] and hdata["slope"] >= 38:
                mcolor = "#EF4444"
            elif hdata["slope"] >= 30:
                mcolor = "#F59E0B"
            else:
                mcolor = "#10B981"
            popup_html = f"<div style='font-family: sans-serif; font-size: 12px; line-height: 1.4;'><b style='font-size: 13px;'>{hname}</b><br>State: {hdata['state']}<br>Elevation: {hdata['elevation']:,} m &nbsp;|&nbsp; Slope: {hdata['slope']}°<br>Baseline Hazard: <b>{hdata['vulnerability']}</b><br>Geology: {hdata['geology']}</div>"
            folium.CircleMarker(location=[hdata["lat"], hdata["lon"]], radius=6, popup=folium.Popup(popup_html, max_width=260), tooltip=f"{hname} ({hdata['state']})", color=mcolor, fill=True, fill_color=mcolor, fill_opacity=0.85, weight=1.5).add_to(hotspots_fg)
        hotspots_fg.add_to(m)

        folium.CircleMarker(
            location=[loc_a['lat'], loc_a['lon']],
            radius=12,
            popup=f"<b>Active Target:</b> {loc_a['title']}<br>Probability: {risk_a['probability']}%",
            tooltip=f"Selected Active Target: {loc_a['title']}",
            color="#38BDF8", fill=True, fill_color="#38BDF8", fill_opacity=0.35, weight=3
        ).add_to(m)

        folium.LayerControl(position="topright").add_to(m)
        st_folium(m, width="100%", height=400)

        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.74rem; color: #94A3B8; margin-top: 0.35rem; padding: 0.4rem 0.85rem; background: rgba(128,128,128,0.06); border-radius: 6px; border: 1px solid rgba(128,128,128,0.15);">
            <span><b>Susceptibility Density:</b></span>
            <span style="color: #10B981;">● Low (&lt;35%)</span>
            <span style="color: #38BDF8;">● Mild</span>
            <span style="color: #F59E0B;">● Moderate (35-70%)</span>
            <span style="color: #EF4444;">● High / Critical (&gt;70%)</span>
        </div>
        """, unsafe_allow_html=True)

    with col_gauge:
        st.markdown("<div class='section-title'>Landslide Probability Index</div>", unsafe_allow_html=True)
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_a["probability"],
            domain={'x': [0, 1], 'y': [0, 1]},
            number={'suffix': "%", 'font': {'size': 44, 'family': 'Plus Jakarta Sans', 'color': risk_a["color"]}},
            title={'text': f"<b>{risk_a['classification'].upper()} HAZARD</b><br><span style='font-size:0.75em;color:#94A3B8'>{loc_a['title']}</span>", 'font': {'size': 18, 'color': '#E2E8F0'}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': '#94A3B8'}},
                'bar': {'color': risk_a["color"], 'thickness': 0.28},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 1,
                'bordercolor': "rgba(255,255,255,0.1)",
                'steps': [
                    {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.12)'},
                    {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.12)'},
                    {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
                ],
                'threshold': {'line': {'color': "#EF4444", 'width': 3}, 'thickness': 0.85, 'value': 70.0}
            }
        ))
        gauge_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=290, margin=dict(l=20, r=20, t=50, b=10), font={'family': 'Plus Jakarta Sans, sans-serif'})
        st.plotly_chart(gauge_fig, use_container_width=True)

        st.markdown(f"""
        <div style="font-size: 0.84rem; color: #94A3B8; background: rgba(255,255,255,0.02); padding: 0.8rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <b>Model Contribution Breakdown:</b><br>
            • ML Geomorphic Baseline: <code>{risk_a['ml_probability']}%</code> (Topography & Lithology)<br>
            • 72h Rain Trigger Volume: <code>{triggers.get('rain_past_72h', 0):.1f} mm</code><br>
            • Volumetric Soil Moisture: <code>{triggers.get('soil_moisture_top', 0.25):.3f} m³/m³</code>
        </div>
        """, unsafe_allow_html=True)

    # Forward 14-Day Trajectory
    st.markdown("---")
    st.markdown("<div class='section-title'>14-Day Risk Trajectory & Precipitation Forecast</div>", unsafe_allow_html=True)
    daily_df = weather_a.get("daily_df", None)
    if daily_df is not None and not daily_df.empty:
        forecast_probs = []
        base_geomorph = risk_a['ml_probability']
        for _, row in daily_df.iterrows():
            p_mm = row['total_precip_mm']
            sm = row['soil_moist_top']
            f_risk = 0.50 * (base_geomorph / 100.0) + 0.35 * np.clip(p_mm / 60.0, 0, 1.0) + 0.15 * np.clip((sm - 0.20) / 0.25, 0, 1.0)
            forecast_probs.append(round(float(np.clip(f_risk * 100, 5, 95)), 1))
        daily_df['predicted_risk_pct'] = forecast_probs

        trend_fig = go.Figure()
        trend_fig.add_trace(go.Bar(x=daily_df['date'].astype(str), y=daily_df['total_precip_mm'], name='Projected Precipitation (mm)', marker_color='rgba(56, 189, 248, 0.55)', yaxis='y'))
        trend_fig.add_trace(go.Scatter(x=daily_df['date'].astype(str), y=daily_df['predicted_risk_pct'], name='Predicted Risk Probability (%)', mode='lines+markers', line=dict(color='#F43F5E', width=2.5), marker=dict(size=6, color='#F43F5E'), yaxis='y2'))
        trend_fig.add_hline(y=70, line_dash="dash", line_color="rgba(239, 68, 68, 0.7)", annotation_text="High Risk Threshold (70%)", annotation_position="top right", yref='y2', annotation_font=dict(color="#EF4444", size=10))
        trend_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8"),
            xaxis=dict(title=dict(text="Forecast Date", font=dict(color="#94A3B8")), showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', tickfont=dict(color="#94A3B8")),
            yaxis=dict(title=dict(text="Precipitation (mm/day)", font=dict(color="#38BDF8")), side="left", showgrid=True, gridcolor='rgba(255, 255, 255, 0.05)', tickfont=dict(color="#38BDF8")),
            yaxis2=dict(title=dict(text="Probability (%)", font=dict(color="#F43F5E")), side="right", overlaying="y", range=[0, 100], showgrid=False, tickfont=dict(color="#F43F5E")),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#CBD5E1")),
            height=360, margin=dict(l=40, r=40, t=30, b=30), hovermode="x unified"
        )
        st.plotly_chart(trend_fig, use_container_width=True)

    # Detailed Tabs
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["Risk Factor Attribution", "Subsurface Hydrology", "Emergency Protocols & SDMA"])
    with tab1:
        st.markdown("##### Primary Drivers Influencing Current Assessment")
        driver_df = pd.DataFrame(risk_a["drivers"])
        dcol1, dcol2 = st.columns([3, 2])
        with dcol1:
            bar_fig = px.bar(driver_df, x="contribution", y="factor", orientation='h', text="value", labels={"contribution": "Weight Contribution (%)", "factor": "Hazard Driver"}, color="contribution", color_continuous_scale="Reds")
            bar_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Plus Jakarta Sans", color="#94A3B8"), xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), yaxis=dict(showgrid=False), height=260, showlegend=False, margin=dict(l=10, r=20, t=10, b=10))
            st.plotly_chart(bar_fig, use_container_width=True)
        with dcol2:
            st.markdown(f"""
            <div style="font-size: 0.88rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <b>Lithological & Terrain Overview:</b><br>
                • Geological Formation: <i>{loc_a['geology']}</i><br>
                • Critical Slope Threshold: <b>{loc_a['slope']}°</b> (Instability threshold: > 35°)<br>
                • Relief Energy: <b>{loc_a['elevation']:,} m a.s.l.</b><br>
                • Corridor Assessment: {loc_a['notes']}
            </div>
            """, unsafe_allow_html=True)
    with tab2:
        st.markdown("##### Multi-Horizon Subsurface Soil Moisture Distribution")
        hourly_df = weather_a.get("hourly_df", None)
        if hourly_df is not None and not hourly_df.empty:
            latest = hourly_df.iloc[-1]
            depth_labels = ["0 - 1 cm (Surface)", "1 - 3 cm (Topsoil)", "3 - 9 cm (Root Zone)", "9 - 27 cm (Mid Stratum)", "27 - 81 cm (Deep Interface)"]
            depth_vals = [latest.get("soil_moisture_0_to_1cm", 0.25), latest.get("soil_moisture_1_to_3cm", 0.26), latest.get("soil_moisture_3_to_9cm", 0.27), latest.get("soil_moisture_9_to_27cm", 0.29), latest.get("soil_moisture_27_to_81cm", 0.31)]
            soil_df = pd.DataFrame({"Horizon": depth_labels, "Volumetric Moisture (m³/m³)": depth_vals})
            fig_soil = px.bar(soil_df, x="Volumetric Moisture (m³/m³)", y="Horizon", orientation='h', color="Volumetric Moisture (m³/m³)", color_continuous_scale="Blues", range_x=[0, 0.6])
            fig_soil.add_vline(x=0.40, line_dash="dash", line_color="#EF4444", annotation_text="Liquefaction Saturation Limit (0.40 m³/m³)", annotation_font=dict(color="#EF4444", size=10))
            fig_soil.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Plus Jakarta Sans", color="#94A3B8"), xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), yaxis=dict(showgrid=False), height=250, margin=dict(l=20, r=20, t=10, b=10))
            st.plotly_chart(fig_soil, use_container_width=True)
        else:
            st.write("Soil moisture horizon data currently unavailable.")
    with tab3:
        st.markdown("##### State Disaster Management Authority (SDMA) Emergency Contacts")
        sdma = SDMA_CONTACTS.get(loc_a['state'], SDMA_CONTACTS["Sikkim"])
        ecol1, ecol2 = st.columns(2)
        with ecol1:
            st.markdown(f"""
            <div style="font-size: 0.88rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 1.1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <b>Authorized State Agency:</b><br>{sdma['dept']}<br><br>
                • State Toll-Free Emergency Helpline: <code>{sdma['helpline']}</code><br>
                • Direct Control Room: <code>{sdma['phone']}</code><br>
                • National Disaster Response Force (NDRF): <code>1078 / 112</code>
            </div>
            """, unsafe_allow_html=True)
        with ecol2:
            st.markdown("""
            <div style="font-size: 0.88rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 1.1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
                <b>NDMA Standard Operating Procedure (SOP):</b><br>
                1. <b>Pre-Warning Signs:</b> Listen for unusual ground rumble, tensile slope fissures, or sudden stream muddiness.<br>
                2. <b>Safe Refuge:</b> During High Advisory, relocate away from channel gullies to designated ridge spurs.<br>
                3. <b>Valley Hazards:</b> Never seek shelter in stream depressions; mudslides accelerate in natural drainage chutes.<br>
                4. <b>Highway Transit:</b> Restrict non-essential vehicular movement during sustained rainfall episodes.
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# VIEW 2: DUAL LOCATION SIDE-BY-SIDE COMPARISON
# =============================================================================
else:
    deltas = compute_comparison_deltas(loc_a, loc_b, risk_a, risk_b, weather_a, weather_b)

    # 1. Dual Header with Status Badges & PDF Exporters
    col_h_left, col_h_mid, col_h_right = st.columns([5, 3.5, 3.5])

    with col_h_left:
        st.markdown("<div class='main-title'>Dual Location Comparative Observatory</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='sub-title'>
            Geodetic Separation: <b style="color: #38BDF8;">{deltas['distance_km']} km</b> &nbsp;|&nbsp; 
            Corridor: <span class='pin-badge-a'>Pin A: {loc_a['title']}</span> ⇄ <span class='pin-badge-b'>Pin B: {loc_b['title']}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_h_mid:
        class_a = risk_a['classification'].lower()
        class_b = risk_b['classification'].lower()
        st.markdown(f"""
        <div style="padding-top: 0.2rem;">
            <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.35rem;">
                <span class="pin-badge-a">PIN A</span>
                <span class="status-pill status-{class_a}" style="padding: 0.25rem 0.65rem; font-size: 0.72rem;">
                    <span class="status-dot dot-{class_a}"></span> {risk_a['classification'].upper()} ({risk_a['probability']}%)
                </span>
            </div>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <span class="pin-badge-b">PIN B</span>
                <span class="status-pill status-{class_b}" style="padding: 0.25rem 0.65rem; font-size: 0.72rem;">
                    <span class="status-dot dot-{class_b}"></span> {risk_b['classification'].upper()} ({risk_b['probability']}%)
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_h_right:
        # Dual PDF Export Buttons
        sdma_a = SDMA_CONTACTS.get(loc_a['state'], SDMA_CONTACTS["Sikkim"])
        sdma_b = SDMA_CONTACTS.get(loc_b['state'], SDMA_CONTACTS["Sikkim"])
        pdf_bytes_a = generate_landslide_pdf_report(
            location_title=f"{loc_a['title']} [Pin A]", target_state=loc_a['state'], target_lat=loc_a['lat'], target_lon=loc_a['lon'],
            terrain_profile=loc_a['terrain_profile'], target_geology=loc_a['geology'], target_notes=loc_a['notes'],
            risk_output=risk_a, weather_res=weather_a, sdma_contact=sdma_a
        )
        pdf_bytes_b = generate_landslide_pdf_report(
            location_title=f"{loc_b['title']} [Pin B]", target_state=loc_b['state'], target_lat=loc_b['lat'], target_lon=loc_b['lon'],
            terrain_profile=loc_b['terrain_profile'], target_geology=loc_b['geology'], target_notes=loc_b['notes'],
            risk_output=risk_b, weather_res=weather_b, sdma_contact=sdma_b
        )
        safe_a = "".join(c for c in loc_a['title'] if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
        safe_b = "".join(c for c in loc_b['title'] if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
        
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.download_button(label="PDF: Pin A", data=pdf_bytes_a, file_name=f"Report_PinA_{safe_a}.pdf", mime="application/pdf", use_container_width=True)
        with c_exp2:
            st.download_button(label="PDF: Pin B", data=pdf_bytes_b, file_name=f"Report_PinB_{safe_b}.pdf", mime="application/pdf", use_container_width=True)

    # 2. Executive Comparative Delta Alert Callout
    if deltas["higher_risk"] != "EQUAL":
        st.info(f"""
        **Comparative Hazard Assessment Summary:**  
        **{deltas['higher_name']}** exhibits a **+{deltas['margin']}% higher landslide risk** compared to {deltas['lower_name']}.  
        • **Primary Driver Differences:** Slope gradient delta is **{deltas['slope_delta']:+.1f}°**, 72h antecedent rainfall difference is **{deltas['rain72_delta']:+.1f} mm**, and topsoil volumetric saturation differs by **{deltas['soil_top_delta']:+.1f}%**.
        """)
    else:
        st.info(f"""
        **Comparative Hazard Assessment Summary:**  
        Both **{loc_a['title']}** and **{loc_b['title']}** demonstrate equal aggregate landslide failure probabilities (**{risk_a['probability']}%**).
        """)

    # 3. Top 5 Side-by-Side Metric Comparison Cards
    trig_a = weather_a.get("triggers", {})
    trig_b = weather_b.get("triggers", {})
    curr_a = weather_a.get("current", {})
    curr_b = weather_b.get("current", {})

    cm1, cm2, cm3, cm4, cm5 = st.columns(5)

    with cm1:
        delta_class = "delta-higher" if deltas["prob_delta"] > 0 else ("delta-lower" if deltas["prob_delta"] < 0 else "delta-neutral")
        sign = "+" if deltas["prob_delta"] > 0 else ""
        st.markdown(f"""
        <div class="compare-card">
            <div class="metric-label">Landslide Risk %</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.2rem;">
                <span style="font-size: 1.35rem; font-weight: 700; color: #38BDF8;">{risk_a['probability']}%</span>
                <span style="font-size: 0.8rem; color: #94A3B8;">vs</span>
                <span style="font-size: 1.35rem; font-weight: 700; color: #FB7185;">{risk_b['probability']}%</span>
            </div>
            <div class="compare-delta-pill {delta_class}">Δ {sign}{deltas['prob_delta']}% (B - A)</div>
            <div class="metric-sub">Pin A: {risk_a['classification']} | Pin B: {risk_b['classification']}</div>
        </div>
        """, unsafe_allow_html=True)

    with cm2:
        r24_a = trig_a.get("rain_past_24h", 0.0)
        r24_b = trig_b.get("rain_past_24h", 0.0)
        delta_r24 = deltas["rain24_delta"]
        delta_class = "delta-higher" if delta_r24 > 0 else ("delta-lower" if delta_r24 < 0 else "delta-neutral")
        sign = "+" if delta_r24 > 0 else ""
        st.markdown(f"""
        <div class="compare-card">
            <div class="metric-label">24h Rainfall Total</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.2rem;">
                <span style="font-size: 1.35rem; font-weight: 700; color: #38BDF8;">{r24_a:.1f} <span style="font-size: 0.75rem;">mm</span></span>
                <span style="font-size: 0.8rem; color: #94A3B8;">vs</span>
                <span style="font-size: 1.35rem; font-weight: 700; color: #FB7185;">{r24_b:.1f} <span style="font-size: 0.75rem;">mm</span></span>
            </div>
            <div class="compare-delta-pill {delta_class}">Δ {sign}{delta_r24:.1f} mm</div>
            <div class="metric-sub">Rate: A {curr_a.get('precipitation_rate', 0.0):.1f} | B {curr_b.get('precipitation_rate', 0.0):.1f} mm/h</div>
        </div>
        """, unsafe_allow_html=True)

    with cm3:
        r72_a = trig_a.get("rain_past_72h", 0.0)
        r72_b = trig_b.get("rain_past_72h", 0.0)
        delta_r72 = deltas["rain72_delta"]
        delta_class = "delta-higher" if delta_r72 > 0 else ("delta-lower" if delta_r72 < 0 else "delta-neutral")
        sign = "+" if delta_r72 > 0 else ""
        st.markdown(f"""
        <div class="compare-card">
            <div class="metric-label">72h Antecedent Rain</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.2rem;">
                <span style="font-size: 1.35rem; font-weight: 700; color: #38BDF8;">{r72_a:.1f} <span style="font-size: 0.75rem;">mm</span></span>
                <span style="font-size: 0.8rem; color: #94A3B8;">vs</span>
                <span style="font-size: 1.35rem; font-weight: 700; color: #FB7185;">{r72_b:.1f} <span style="font-size: 0.75rem;">mm</span></span>
            </div>
            <div class="compare-delta-pill {delta_class}">Δ {sign}{delta_r72:.1f} mm</div>
            <div class="metric-sub">7d Totals: A {trig_a.get('rain_past_7d', 0):.0f}mm | B {trig_b.get('rain_past_7d', 0):.0f}mm</div>
        </div>
        """, unsafe_allow_html=True)

    with cm4:
        st_a = deltas["soil_top_a"]
        st_b = deltas["soil_top_b"]
        delta_st = deltas["soil_top_delta"]
        delta_class = "delta-higher" if delta_st > 0 else ("delta-lower" if delta_st < 0 else "delta-neutral")
        sign = "+" if delta_st > 0 else ""
        st.markdown(f"""
        <div class="compare-card">
            <div class="metric-label">Topsoil Saturation (0-9cm)</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.2rem;">
                <span style="font-size: 1.35rem; font-weight: 700; color: #38BDF8;">{st_a:.1f}%</span>
                <span style="font-size: 0.8rem; color: #94A3B8;">vs</span>
                <span style="font-size: 1.35rem; font-weight: 700; color: #FB7185;">{st_b:.1f}%</span>
            </div>
            <div class="compare-delta-pill {delta_class}">Δ {sign}{delta_st:.1f}%</div>
            <div class="metric-sub">Critical Saturation: &gt;40.0%</div>
        </div>
        """, unsafe_allow_html=True)

    with cm5:
        sd_a = deltas["soil_deep_a"]
        sd_b = deltas["soil_deep_b"]
        delta_sd = deltas["soil_deep_delta"]
        delta_class = "delta-higher" if delta_sd > 0 else ("delta-lower" if delta_sd < 0 else "delta-neutral")
        sign = "+" if delta_sd > 0 else ""
        st.markdown(f"""
        <div class="compare-card">
            <div class="metric-label">Deep Subsoil (27-81cm)</div>
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-top: 0.2rem;">
                <span style="font-size: 1.35rem; font-weight: 700; color: #38BDF8;">{sd_a:.1f}%</span>
                <span style="font-size: 0.8rem; color: #94A3B8;">vs</span>
                <span style="font-size: 1.35rem; font-weight: 700; color: #FB7185;">{sd_b:.1f}%</span>
            </div>
            <div class="compare-delta-pill {delta_class}">Δ {sign}{delta_sd:.1f}%</div>
            <div class="metric-sub">Mean: A {trig_a.get('soil_moisture_mean', 0.3)*100:.1f}% | B {trig_b.get('soil_moisture_mean', 0.3)*100:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Interactive Map & Side-by-Side Gauges
    st.markdown("---")
    col_map_dual, col_gauges_dual = st.columns([3, 2])

    with col_map_dual:
        st.markdown("<div class='section-title'>Dual-Station Regional Geospatial Map</div>", unsafe_allow_html=True)
        
        m_ctrl1, m_ctrl2 = st.columns([3, 2])
        with m_ctrl1:
            show_heatmap = st.checkbox("Overlay Regional Susceptibility Heatmap", value=True, key="dual_heatmap")
        with m_ctrl2:
            heatmap_radius = st.slider("Heatmap Blur Radius", min_value=12, max_value=32, value=18, step=2, key="dual_radius")

        # Center map at midpoint between Pin A and Pin B
        mid_lat = (loc_a['lat'] + loc_b['lat']) / 2.0
        mid_lon = (loc_a['lon'] + loc_b['lon']) / 2.0
        
        m_dual = folium.Map(location=[mid_lat, mid_lon], zoom_start=7, tiles="CartoDB positron", control_scale=True)
        folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', attr='Esri', name='Satellite High-Resolution', overlay=False, control=True).add_to(m_dual)
        folium.TileLayer(tiles='OpenStreetMap', name='OpenStreetMap', overlay=False, control=True).add_to(m_dual)

        # 1. Overlay Heatmap
        if show_heatmap:
            heat_points_path = os.path.join("output", "susceptibility_points.json")
            if os.path.exists(heat_points_path):
                with open(heat_points_path, "r") as f:
                    heat_points = json.load(f)
                heat_fg = folium.FeatureGroup(name="Susceptibility Risk Heatmap", show=True)
                HeatMap(heat_points, min_opacity=0.40, max_zoom=14, radius=heatmap_radius, blur=14,
                        gradient={0.20: '#10B981', 0.45: '#38BDF8', 0.65: '#F59E0B', 0.85: '#EF4444', 1.00: '#7F1D1D'}).add_to(heat_fg)
                heat_fg.add_to(m_dual)

        # 2. Add District Hotspots
        hotspots_fg = folium.FeatureGroup(name="Regional Hotspots", show=True)
        for hname, hdata in NE_HOTSPOTS.items():
            if hdata["vulnerability"] in ["Critical", "Very High"] and hdata["slope"] >= 38:
                mcolor = "#EF4444"
            elif hdata["slope"] >= 30:
                mcolor = "#F59E0B"
            else:
                mcolor = "#10B981"
            popup_html = f"<div style='font-family: sans-serif; font-size: 12px; line-height: 1.4;'><b style='font-size: 13px;'>{hname}</b><br>State: {hdata['state']}<br>Elevation: {hdata['elevation']:,} m &nbsp;|&nbsp; Slope: {hdata['slope']}°<br>Baseline Hazard: <b>{hdata['vulnerability']}</b></div>"
            folium.CircleMarker(location=[hdata["lat"], hdata["lon"]], radius=5, popup=folium.Popup(popup_html, max_width=250), tooltip=f"{hname}", color=mcolor, fill=True, fill_color=mcolor, fill_opacity=0.75, weight=1).add_to(hotspots_fg)
        hotspots_fg.add_to(m_dual)

        # 3. Add Geodesic Connection Line
        folium.PolyLine(
            locations=[[loc_a['lat'], loc_a['lon']], [loc_b['lat'], loc_b['lon']]],
            color="#38BDF8",
            weight=3,
            opacity=0.8,
            dash_array="6, 8",
            tooltip=f"Corridor Separation: {deltas['distance_km']} km"
        ).add_to(m_dual)

        # Midpoint indicator
        folium.CircleMarker(
            location=[mid_lat, mid_lon],
            radius=4,
            color="#F8FAFC",
            fill=True,
            fill_color="#38BDF8",
            popup=f"Geodesic Distance: <b>{deltas['distance_km']} km</b>",
            tooltip=f"Distance: {deltas['distance_km']} km"
        ).add_to(m_dual)

        # 4. Highlight Pin A (Cyan Blue)
        folium.CircleMarker(
            location=[loc_a['lat'], loc_a['lon']],
            radius=13,
            popup=f"<b>PIN A:</b> {loc_a['title']}<br>State: {loc_a['state']}<br>Risk: <b>{risk_a['probability']}%</b> ({risk_a['classification']})<br>Slope: {loc_a['slope']}°",
            tooltip=f"Pin A: {loc_a['title']} ({risk_a['probability']}%)",
            color="#0284C7",
            fill=True,
            fill_color="#38BDF8",
            fill_opacity=0.45,
            weight=3
        ).add_to(m_dual)

        # 5. Highlight Pin B (Rose Red)
        folium.CircleMarker(
            location=[loc_b['lat'], loc_b['lon']],
            radius=13,
            popup=f"<b>PIN B:</b> {loc_b['title']}<br>State: {loc_b['state']}<br>Risk: <b>{risk_b['probability']}%</b> ({risk_b['classification']})<br>Slope: {loc_b['slope']}°",
            tooltip=f"Pin B: {loc_b['title']} ({risk_b['probability']}%)",
            color="#BE123C",
            fill=True,
            fill_color="#FB7185",
            fill_opacity=0.45,
            weight=3
        ).add_to(m_dual)

        folium.LayerControl(position="topright").add_to(m_dual)
        st_folium(m_dual, width="100%", height=400, key="st_folium_dual")

        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; font-size: 0.74rem; color: #94A3B8; margin-top: 0.35rem; padding: 0.4rem 0.85rem; background: rgba(128,128,128,0.06); border-radius: 6px; border: 1px solid rgba(128,128,128,0.15);">
            <span style="color: #38BDF8;">● <b>Pin A:</b> {loc_a['title']}</span>
            <span style="color: #FB7185;">● <b>Pin B:</b> {loc_b['title']}</span>
            <span style="color: #E2E8F0;">↔ Separation: <b>{deltas['distance_km']} km</b></span>
        </div>
        """, unsafe_allow_html=True)

    with col_gauges_dual:
        st.markdown("<div class='section-title'>Comparative Risk Probability Gauges</div>", unsafe_allow_html=True)
        
        gcol1, gcol2 = st.columns(2)
        with gcol1:
            st.plotly_chart(
                create_side_by_side_gauge(risk_a["probability"], loc_a['title'], risk_a["color"], risk_a["classification"]),
                use_container_width=True
            )
        with gcol2:
            st.plotly_chart(
                create_side_by_side_gauge(risk_b["probability"], loc_b['title'], risk_b["color"], risk_b["classification"]),
                use_container_width=True
            )

        st.markdown(f"""
        <div style="font-size: 0.83rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 0.85rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <b>Model Driver Comparison:</b><br>
            • <b>ML Geomorphic Baseline:</b> Pin A <code>{risk_a['ml_probability']}%</code> vs Pin B <code>{risk_b['ml_probability']}%</code><br>
            • <b>72h Rainfall Stress:</b> Pin A <code>{trig_a.get('rain_past_72h', 0):.1f} mm</code> vs Pin B <code>{trig_b.get('rain_past_72h', 0):.1f} mm</code><br>
            • <b>Topsoil Moisture:</b> Pin A <code>{trig_a.get('soil_moisture_top', 0.25):.3f} m³/m³</code> vs Pin B <code>{trig_b.get('soil_moisture_top', 0.25):.3f} m³/m³</code>
        </div>
        """, unsafe_allow_html=True)

    # 5. Side-by-Side Soil Moisture Levels
    st.markdown("---")
    st.markdown("<div class='section-title'>Multi-Horizon Subsurface Soil Moisture Comparison</div>", unsafe_allow_html=True)
    st.caption("Volumetric moisture content (m³/m³) across 5 stratigraphic horizons compared to the 0.40 m³/m³ liquefaction instability threshold.")
    st.plotly_chart(
        create_comparative_soil_moisture_chart(weather_a, weather_b, loc_a['title'], loc_b['title']),
        use_container_width=True
    )

    # 6. Forward 14-Day Trajectory Comparison
    st.markdown("---")
    st.markdown("<div class='section-title'>14-Day Comparative Forward Precipitation & Risk Trajectory</div>", unsafe_allow_html=True)
    st.caption("Simultaneous daily precipitation forecasts (bars) and projected dynamic landslide failure probabilities (curves).")
    st.plotly_chart(
        create_comparative_forecast_chart(weather_a, weather_b, risk_a, risk_b, loc_a['title'], loc_b['title']),
        use_container_width=True
    )

    # 7. Detailed Comparison Tabs
    st.markdown("---")
    dtab1, dtab2, dtab3, dtab4 = st.tabs([
        "Side-by-Side Risk Drivers",
        "Geomorphic & Terrain Matrix",
        "Weather Triggers Breakdown",
        "Emergency Contacts & SDMA"
    ])

    with dtab1:
        st.markdown("##### Primary Hazard Contributing Factors Comparison")
        dr_col1, dr_col2 = st.columns(2)
        
        with dr_col1:
            st.markdown(f"<span class='pin-badge-a'>Pin A: {loc_a['title']}</span>", unsafe_allow_html=True)
            df_drivers_a = pd.DataFrame(risk_a["drivers"])
            bar_fig_a = px.bar(
                df_drivers_a, x="contribution", y="factor", orientation='h', text="value",
                labels={"contribution": "Weight (%)", "factor": "Factor"},
                color="contribution", color_continuous_scale="Blues"
            )
            bar_fig_a.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Plus Jakarta Sans", color="#94A3B8"), xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), yaxis=dict(showgrid=False), height=250, showlegend=False, margin=dict(l=10, r=20, t=10, b=10))
            st.plotly_chart(bar_fig_a, use_container_width=True)

        with dr_col2:
            st.markdown(f"<span class='pin-badge-b'>Pin B: {loc_b['title']}</span>", unsafe_allow_html=True)
            df_drivers_b = pd.DataFrame(risk_b["drivers"])
            bar_fig_b = px.bar(
                df_drivers_b, x="contribution", y="factor", orientation='h', text="value",
                labels={"contribution": "Weight (%)", "factor": "Factor"},
                color="contribution", color_continuous_scale="Reds"
            )
            bar_fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Plus Jakarta Sans", color="#94A3B8"), xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'), yaxis=dict(showgrid=False), height=250, showlegend=False, margin=dict(l=10, r=20, t=10, b=10))
            st.plotly_chart(bar_fig_b, use_container_width=True)

    with dtab2:
        st.markdown("##### Comprehensive Terrain & Geomorphic Profile Matrix")
        matrix_data = {
            "Geomorphic Attribute": [
                "Target District / Corridor",
                "State Jurisdiction",
                "GPS Coordinates",
                "Elevation (a.s.l.)",
                "Terrain Slope Gradient",
                "Slope Aspect",
                "Terrain Curvature",
                "Topographic Wetness Index (TWI)",
                "Terrain Ruggedness Index (TRI)",
                "Underlying Lithology / Geology",
                "Baseline Vulnerability Tier",
                "Corridor Field Notes"
            ],
            f"Pin A ({loc_a['title']})": [
                loc_a['title'],
                loc_a['state'],
                f"{loc_a['lat']:.4f}°N, {loc_a['lon']:.4f}°E",
                f"{loc_a['elevation']:,} m",
                f"{loc_a['slope']}°",
                f"{loc_a['aspect']}°",
                f"{loc_a['curvature']:.5f}",
                f"{loc_a['twi']:.2f}",
                f"{loc_a['tri']:.2f}",
                loc_a['geology'],
                loc_a.get('vulnerability', 'Moderate'),
                loc_a['notes']
            ],
            f"Pin B ({loc_b['title']})": [
                loc_b['title'],
                loc_b['state'],
                f"{loc_b['lat']:.4f}°N, {loc_b['lon']:.4f}°E",
                f"{loc_b['elevation']:,} m",
                f"{loc_b['slope']}°",
                f"{loc_b['aspect']}°",
                f"{loc_b['curvature']:.5f}",
                f"{loc_b['twi']:.2f}",
                f"{loc_b['tri']:.2f}",
                loc_b['geology'],
                loc_b.get('vulnerability', 'Moderate'),
                loc_b['notes']
            ],
            "Variance / Delta": [
                "—",
                "Same State" if loc_a['state'] == loc_b['state'] else "Inter-State",
                f"Separation: {deltas['distance_km']} km",
                f"{deltas['elev_delta']:+d} m",
                f"{deltas['slope_delta']:+.1f}°",
                f"{loc_b['aspect'] - loc_a['aspect']:+.1f}°",
                f"{loc_b['curvature'] - loc_a['curvature']:+.5f}",
                f"{loc_b['twi'] - loc_a['twi']:+.2f}",
                f"{loc_b['tri'] - loc_a['tri']:+.2f}",
                "—",
                "—",
                "—"
            ]
        }
        st.dataframe(pd.DataFrame(matrix_data), use_container_width=True, hide_index=True)

    with dtab3:
        st.markdown("##### Detailed Meteorological & Hydrological Telemetry Breakdown")
        weather_table_data = {
            "Meteorological Parameter": [
                "Current Surface Temperature",
                "Apparent Temperature (Feels Like)",
                "Relative Humidity",
                "Instantaneous Precipitation Rate",
                "Past 24 Hours Cumulative Rain",
                "Past 48 Hours Cumulative Rain",
                "Past 72 Hours Cumulative Rain",
                "Past 7 Days Cumulative Rain",
                "Surface Soil Moisture (0-1 cm)",
                "Topsoil Moisture (1-3 cm)",
                "Root Zone Moisture (3-9 cm)",
                "Mid Stratum Moisture (9-27 cm)",
                "Deep Interface Moisture (27-81 cm)"
            ],
            f"Pin A ({loc_a['title']})": [
                f"{curr_a.get('temperature', 20.0):.1f} °C",
                f"{curr_a.get('apparent_temperature', 20.0):.1f} °C",
                f"{curr_a.get('humidity', 75):.0f}%",
                f"{curr_a.get('precipitation_rate', 0.0):.1f} mm/h",
                f"{trig_a.get('rain_past_24h', 0.0):.1f} mm",
                f"{trig_a.get('rain_past_48h', 0.0):.1f} mm",
                f"{trig_a.get('rain_past_72h', 0.0):.1f} mm",
                f"{trig_a.get('rain_past_7d', 0.0):.1f} mm",
                f"{trig_a.get('soil_moisture_top', 0.25)*0.95:.3f} m³/m³",
                f"{trig_a.get('soil_moisture_top', 0.25):.3f} m³/m³",
                f"{trig_a.get('soil_moisture_mid', 0.28):.3f} m³/m³",
                f"{trig_a.get('soil_moisture_deep', 0.30)*0.95:.3f} m³/m³",
                f"{trig_a.get('soil_moisture_deep', 0.30):.3f} m³/m³"
            ],
            f"Pin B ({loc_b['title']})": [
                f"{curr_b.get('temperature', 20.0):.1f} °C",
                f"{curr_b.get('apparent_temperature', 20.0):.1f} °C",
                f"{curr_b.get('humidity', 75):.0f}%",
                f"{curr_b.get('precipitation_rate', 0.0):.1f} mm/h",
                f"{trig_b.get('rain_past_24h', 0.0):.1f} mm",
                f"{trig_b.get('rain_past_48h', 0.0):.1f} mm",
                f"{trig_b.get('rain_past_72h', 0.0):.1f} mm",
                f"{trig_b.get('rain_past_7d', 0.0):.1f} mm",
                f"{trig_b.get('soil_moisture_top', 0.25)*0.95:.3f} m³/m³",
                f"{trig_b.get('soil_moisture_top', 0.25):.3f} m³/m³",
                f"{trig_b.get('soil_moisture_mid', 0.28):.3f} m³/m³",
                f"{trig_b.get('soil_moisture_deep', 0.30)*0.95:.3f} m³/m³",
                f"{trig_b.get('soil_moisture_deep', 0.30):.3f} m³/m³"
            ],
            "Delta (B - A)": [
                f"{curr_b.get('temperature', 20.0) - curr_a.get('temperature', 20.0):+.1f} °C",
                f"{curr_b.get('apparent_temperature', 20.0) - curr_a.get('apparent_temperature', 20.0):+.1f} °C",
                f"{curr_b.get('humidity', 75) - curr_a.get('humidity', 75):+.0f}%",
                f"{curr_b.get('precipitation_rate', 0.0) - curr_a.get('precipitation_rate', 0.0):+.1f} mm/h",
                f"{deltas['rain24_delta']:+.1f} mm",
                f"{trig_b.get('rain_past_48h', 0.0) - trig_a.get('rain_past_48h', 0.0):+.1f} mm",
                f"{deltas['rain72_delta']:+.1f} mm",
                f"{trig_b.get('rain_past_7d', 0.0) - trig_a.get('rain_past_7d', 0.0):+.1f} mm",
                f"{(trig_b.get('soil_moisture_top', 0.25) - trig_a.get('soil_moisture_top', 0.25))*0.95:+.3f} m³/m³",
                f"{(trig_b.get('soil_moisture_top', 0.25) - trig_a.get('soil_moisture_top', 0.25)):+.3f} m³/m³",
                f"{(trig_b.get('soil_moisture_mid', 0.28) - trig_a.get('soil_moisture_mid', 0.28)):+.3f} m³/m³",
                f"{(trig_b.get('soil_moisture_deep', 0.30) - trig_a.get('soil_moisture_deep', 0.30))*0.95:+.3f} m³/m³",
                f"{(trig_b.get('soil_moisture_deep', 0.30) - trig_a.get('soil_moisture_deep', 0.30)):+.3f} m³/m³"
            ]
        }
        st.dataframe(pd.DataFrame(weather_table_data), use_container_width=True, hide_index=True)

    with dtab4:
        st.markdown("##### State Disaster Management Authorities & Protocols")
        sdma_a = SDMA_CONTACTS.get(loc_a['state'], SDMA_CONTACTS["Sikkim"])
        sdma_b = SDMA_CONTACTS.get(loc_b['state'], SDMA_CONTACTS["Sikkim"])

        ecol_a, ecol_b = st.columns(2)
        with ecol_a:
            st.markdown(f"""
            <div style="font-size: 0.88rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 1.1rem; border-radius: 8px; border: 1px solid rgba(56,189,248,0.25);">
                <span class='pin-badge-a'>Pin A: {loc_a['state']} SDMA</span><br><br>
                <b>Authorized Agency:</b><br>{sdma_a['dept']}<br><br>
                • State Toll-Free Emergency Helpline: <code>{sdma_a['helpline']}</code><br>
                • Direct Control Room: <code>{sdma_a['phone']}</code><br>
                • NDRF Emergency Dispatch: <code>1078 / 112</code>
            </div>
            """, unsafe_allow_html=True)
        with ecol_b:
            st.markdown(f"""
            <div style="font-size: 0.88rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 1.1rem; border-radius: 8px; border: 1px solid rgba(251,113,133,0.25);">
                <span class='pin-badge-b'>Pin B: {loc_b['state']} SDMA</span><br><br>
                <b>Authorized Agency:</b><br>{sdma_b['dept']}<br><br>
                • State Toll-Free Emergency Helpline: <code>{sdma_b['helpline']}</code><br>
                • Direct Control Room: <code>{sdma_b['phone']}</code><br>
                • NDRF Emergency Dispatch: <code>1078 / 112</code>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("North Eastern Region Landslide Early Warning System | Dual-Station Satellite Telemetry (Open-Meteo) | LightGBM ML Geomorphic Engine | Developed for Scientific Disaster Risk Reduction")
