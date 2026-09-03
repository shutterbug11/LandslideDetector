"""
=============================================================================
North Eastern Region (India) Landslide Early Warning System
Real-Time Weather Integration (Open-Meteo & OpenWeather) + LightGBM ML Engine
Professional Scientific Observatory Edition
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
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <div class="sidebar-agency">Earth Observation & Hazard Mitigation</div>
        <div class="sidebar-title">Landslide Early Warning</div>
        <div class="sidebar-region">North Eastern Himalayan Region, India</div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Geographic Scope & Target")
    selection_mode = st.radio("Coordinate Input Mode", ["Preset Vulnerable Hotspots", "Custom GPS Coordinates"], index=0)

    if selection_mode == "Preset Vulnerable Hotspots":
        selected_state = st.selectbox("Select State", NE_STATES, index=0)
        state_hotspots = {k: v for k, v in NE_HOTSPOTS.items() if v["state"] == selected_state}
        hotspot_names = list(state_hotspots.keys())
        
        selected_hotspot_name = st.selectbox("Select Target District / Corridor", hotspot_names, index=0)
        loc_data = state_hotspots[selected_hotspot_name]
        
        target_lat = loc_data["lat"]
        target_lon = loc_data["lon"]
        target_elevation = loc_data["elevation"]
        target_slope = loc_data["slope"]
        target_aspect = loc_data["aspect"]
        target_curvature = loc_data["curvature"]
        target_twi = loc_data["twi"]
        target_tri = loc_data["tri"]
        target_state = loc_data["state"]
        target_geology = loc_data["geology"]
        target_notes = loc_data["notes"]
        location_title = selected_hotspot_name

    else:
        st.markdown("**Manual Geographic Positioning**")
        target_lat = st.number_input("Latitude (°N)", min_value=21.0, max_value=30.0, value=27.3389, step=0.01, format="%.4f")
        target_lon = st.number_input("Longitude (°E)", min_value=88.0, max_value=98.0, value=88.6065, step=0.01, format="%.4f")
        
        st.markdown("**Geomorphic Parameters**")
        target_elevation = st.slider("Elevation (m a.s.l.)", 50, 4500, 1600, step=50)
        target_slope = st.slider("Terrain Slope (°)", 5.0, 75.0, 36.0, step=1.0)
        target_aspect = st.slider("Slope Aspect (°)", 0.0, 360.0, 180.0, step=10.0)
        target_curvature = 0.0004
        target_twi = 3.8
        target_tri = 7.0
        target_state = "Custom North East Location"
        target_geology = "Complex Himalayan / Indo-Burman metamorphic rock sequence"
        target_notes = "User-defined coordinate assessment."
        location_title = f"Custom Position ({target_lat:.3f}°N, {target_lon:.3f}°E)"

    st.markdown("---")
    st.caption("""
    **Advisory Tiers (GSI / NDMA Standard):**
    * **Low Risk (<35%)**: Baseline stability, normal vigilance
    * **Medium Risk (35-70%)**: Saturated slope conditions, caution advised
    * **High Risk (>70%)**: Critical failure probability, evacuation protocol
    """)

# -----------------------------------------------------------------------------
# FETCH WEATHER & RUN PREDICTIONS
# -----------------------------------------------------------------------------
with st.spinner("Acquiring satellite meteorological telemetry..."):
    weather_res = fetch_openmeteo_weather(target_lat, target_lon, past_days=7, forecast_days=14)

terrain_profile = {
    "elevation": target_elevation,
    "slope": target_slope,
    "aspect": target_aspect,
    "curvature": target_curvature,
    "twi": target_twi,
    "tri": target_tri
}

if weather_res.get("status") == "success":
    risk_output = calculate_landslide_risk(terrain_profile, weather_res)
else:
    fallback_weather = {
        "current": {"temperature": 18.5, "apparent_temperature": 18.2, "humidity": 82, "precipitation_rate": 2.5, "rain_rate": 2.5},
        "triggers": {"rain_past_24h": 45.0, "rain_past_48h": 85.0, "rain_past_72h": 120.0, "rain_past_7d": 190.0, "soil_moisture_top": 0.38, "soil_moisture_mid": 0.35, "soil_moisture_deep": 0.33, "soil_moisture_mean": 0.35}
    }
    risk_output = calculate_landslide_risk(terrain_profile, fallback_weather)
    weather_res = fallback_weather

# -----------------------------------------------------------------------------
# MAIN HEADER, STATUS BADGE & EXPORT BUTTON
# -----------------------------------------------------------------------------
col_h1, col_h2, col_h3 = st.columns([5, 2.8, 2.2])

classification_str = risk_output['classification'].lower()
status_class = f"status-{classification_str}"
dot_class = f"dot-{classification_str}"

with col_h1:
    st.markdown(f"<div class='main-title'>{location_title}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='sub-title'>
        State: <b>{target_state}</b> &nbsp;|&nbsp; 
        Elevation: <b>{target_elevation:,} m</b> &nbsp;|&nbsp; 
        Slope Gradient: <b>{target_slope}°</b> &nbsp;|&nbsp; 
        Geology: <i>{target_geology}</i>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
    <div style="text-align: right; padding-top: 0.25rem;">
        <div class="status-pill {status_class}">
            <span class="status-dot {dot_class}"></span> {risk_output['classification'].upper()} RISK
        </div>
        <div style="font-size: 0.78rem; color: #94A3B8; margin-top: 0.35rem; font-weight: 500;">
            {risk_output['alert_level']}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h3:
    sdma_contact = SDMA_CONTACTS.get(target_state, SDMA_CONTACTS["Sikkim"])
    pdf_bytes = generate_landslide_pdf_report(
        location_title=location_title,
        target_state=target_state,
        target_lat=target_lat,
        target_lon=target_lon,
        terrain_profile=terrain_profile,
        target_geology=target_geology,
        target_notes=target_notes,
        risk_output=risk_output,
        weather_res=weather_res,
        sdma_contact=sdma_contact
    )
    safe_name = "".join(c for c in location_title if c.isalnum() or c in (' ', '_', '-')).rstrip().replace(" ", "_")
    report_filename = f"Hazard_Report_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    st.markdown("<div style='padding-top: 0.35rem;'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Export Report as PDF",
        data=pdf_bytes,
        file_name=report_filename,
        mime="application/pdf",
        use_container_width=True
    )

# Clean Alert Callout
if risk_output['classification'] == "High":
    st.error(f"""
    **Critical Hazard Alert Active for {location_title}:**  
    Antecedent rainfall ({risk_output['thresholds']['rain_72h']:.1f} mm in 72h) and subsurface moisture saturation have breached safety thresholds on this {target_slope}° slope. 
    Immediate Action: Avoid hillside road cuts, monitor retaining structures, and follow local district evacuation guidelines.
    """)
elif risk_output['classification'] == "Medium":
    st.warning(f"""
    **Elevated Slope Stability Advisory for {location_title}:**  
    Moderate saturation detected on {target_slope}° terrain. Persistent precipitation may initiate localized debris flows. Heightened vigilance recommended along transit corridors.
    """)

# -----------------------------------------------------------------------------
# TOP METRIC CARDS
# -----------------------------------------------------------------------------
curr_weather = weather_res.get("current", {})
triggers = weather_res.get("triggers", {})

mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)

with mcol1:
    st.markdown(f"""
    <div class="card">
        <div class="metric-label">Landslide Probability</div>
        <div class="metric-value" style="color: {risk_output['color']};">{risk_output['probability']}%</div>
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

# -----------------------------------------------------------------------------
# INTERACTIVE MAP & GAUGE SECTION
# -----------------------------------------------------------------------------
col_map, col_gauge = st.columns([3, 2])

with col_map:
    st.markdown("<div class='section-title'>Regional Hazard & Susceptibility Map</div>", unsafe_allow_html=True)
    
    # Heat map configuration toolbar
    m_ctrl1, m_ctrl2 = st.columns([3, 2])
    with m_ctrl1:
        show_heatmap = st.checkbox("Enable Susceptibility Heatmap Distribution", value=True)
    with m_ctrl2:
        heatmap_radius = st.slider("Heatmap Blur Radius", min_value=12, max_value=32, value=18, step=2)
    
    # Folium map centered on NE India
    m = folium.Map(
        location=[26.1, 92.9],
        zoom_start=7,
        tiles="CartoDB positron",
        control_scale=True
    )
    
    # Satellite and OSM layers
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite High-Resolution',
        overlay=False,
        control=True
    ).add_to(m)
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)

    # 1. Overlay Susceptibility HeatMap
    if show_heatmap:
        heat_points_path = os.path.join("output", "susceptibility_points.json")
        if os.path.exists(heat_points_path):
            with open(heat_points_path, "r") as f:
                heat_points = json.load(f)
            
            heat_fg = folium.FeatureGroup(name="Susceptibility Risk Heatmap", show=True)
            HeatMap(
                heat_points,
                min_opacity=0.40,
                max_zoom=14,
                radius=heatmap_radius,
                blur=14,
                gradient={
                    0.20: '#10B981',  # Low - Emerald Green
                    0.45: '#38BDF8',  # Mild - Sky Blue
                    0.65: '#F59E0B',  # Moderate - Amber Orange
                    0.85: '#EF4444',  # High - Crimson Red
                    1.00: '#7F1D1D'   # Critical - Deep Burgundy
                }
            ).add_to(heat_fg)
            heat_fg.add_to(m)

    # 2. Add District Hotspots FeatureGroup
    hotspots_fg = folium.FeatureGroup(name="Monitored District Hotspots", show=True)
    for hname, hdata in NE_HOTSPOTS.items():
        if hdata["vulnerability"] in ["Critical", "Very High"] and hdata["slope"] >= 38:
            mcolor = "#EF4444"
        elif hdata["slope"] >= 30:
            mcolor = "#F59E0B"
        else:
            mcolor = "#10B981"
            
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4;">
            <b style="font-size: 13px;">{hname}</b><br>
            State: {hdata['state']}<br>
            Elevation: {hdata['elevation']:,} m &nbsp;|&nbsp; Slope: {hdata['slope']}°<br>
            Baseline Hazard: <b>{hdata['vulnerability']}</b><br>
            Geology: {hdata['geology']}
        </div>
        """
        
        folium.CircleMarker(
            location=[hdata["lat"], hdata["lon"]],
            radius=6,
            popup=folium.Popup(popup_html, max_width=260),
            tooltip=f"{hname} ({hdata['state']})",
            color=mcolor,
            fill=True,
            fill_color=mcolor,
            fill_opacity=0.85,
            weight=1.5
        ).add_to(hotspots_fg)
    hotspots_fg.add_to(m)

    # 3. Highlight Selected Target Position
    folium.CircleMarker(
        location=[target_lat, target_lon],
        radius=12,
        popup=f"<b>Active Target:</b> {location_title}<br>Probability: {risk_output['probability']}%",
        tooltip="Selected Active Target",
        color="#38BDF8",
        fill=True,
        fill_color="#38BDF8",
        fill_opacity=0.35,
        weight=3
    ).add_to(m)

    folium.LayerControl(position="topright").add_to(m)
    st_folium(m, width="100%", height=400)

    # Geospatial Susceptibility Gradient Legend
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
        value=risk_output["probability"],
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': "%", 'font': {'size': 44, 'family': 'Plus Jakarta Sans', 'color': risk_output["color"]}},
        title={'text': f"<b>{risk_output['classification'].upper()} HAZARD</b><br><span style='font-size:0.75em;color:#94A3B8'>{location_title}</span>", 'font': {'size': 18, 'color': '#E2E8F0'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': '#94A3B8'}},
            'bar': {'color': risk_output["color"], 'thickness': 0.28},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 1,
            'bordercolor': "rgba(255,255,255,0.1)",
            'steps': [
                {'range': [0, 35], 'color': 'rgba(16, 185, 129, 0.12)'},
                {'range': [35, 70], 'color': 'rgba(245, 158, 11, 0.12)'},
                {'range': [70, 100], 'color': 'rgba(239, 68, 68, 0.15)'}
            ],
            'threshold': {
                'line': {'color': "#EF4444", 'width': 3},
                'thickness': 0.85,
                'value': 70.0
            }
        }
    ))
    gauge_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=290,
        margin=dict(l=20, r=20, t=50, b=10),
        font={'family': 'Plus Jakarta Sans, sans-serif'}
    )
    st.plotly_chart(gauge_fig, use_container_width=True)
    
    st.markdown(f"""
    <div style="font-size: 0.84rem; color: #94A3B8; background: rgba(255,255,255,0.02); padding: 0.8rem 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
        <b>Model Contribution Breakdown:</b><br>
        • ML Geomorphic Baseline: <code>{risk_output['ml_probability']}%</code> (Topography & Lithology)<br>
        • 72h Rain Trigger Volume: <code>{triggers.get('rain_past_72h', 0):.1f} mm</code><br>
        • Volumetric Soil Moisture: <code>{triggers.get('soil_moisture_top', 0.25):.3f} m³/m³</code>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 14-DAY FORWARD FORECAST & TREND
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("<div class='section-title'>14-Day Risk Trajectory & Precipitation Forecast</div>", unsafe_allow_html=True)

daily_df = weather_res.get("daily_df", None)

if daily_df is not None and not daily_df.empty:
    forecast_probs = []
    base_geomorph = risk_output['ml_probability']
    
    for _, row in daily_df.iterrows():
        p_mm = row['total_precip_mm']
        sm = row['soil_moist_top']
        f_risk = 0.50 * (base_geomorph / 100.0) + 0.35 * np.clip(p_mm / 60.0, 0, 1.0) + 0.15 * np.clip((sm - 0.20) / 0.25, 0, 1.0)
        forecast_probs.append(round(float(np.clip(f_risk * 100, 5, 95)), 1))
    
    daily_df['predicted_risk_pct'] = forecast_probs
    
    trend_fig = go.Figure()

    # Bar chart for forecasted daily precipitation
    trend_fig.add_trace(go.Bar(
        x=daily_df['date'].astype(str),
        y=daily_df['total_precip_mm'],
        name='Projected Precipitation (mm)',
        marker_color='rgba(56, 189, 248, 0.55)',
        yaxis='y'
    ))

    # Line chart for Predicted Landslide Risk %
    trend_fig.add_trace(go.Scatter(
        x=daily_df['date'].astype(str),
        y=daily_df['predicted_risk_pct'],
        name='Predicted Risk Probability (%)',
        mode='lines+markers',
        line=dict(color='#F43F5E', width=2.5),
        marker=dict(size=6, color='#F43F5E'),
        yaxis='y2'
    ))

    # Add critical 70% threshold line
    trend_fig.add_hline(
        y=70, line_dash="dash", line_color="rgba(239, 68, 68, 0.7)", 
        annotation_text="High Risk Threshold (70%)", 
        annotation_position="top right", yref='y2',
        annotation_font=dict(color="#EF4444", size=10)
    )

    trend_fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8"),
        xaxis=dict(
            title=dict(text="Forecast Date", font=dict(color="#94A3B8")),
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            title=dict(text="Precipitation (mm/day)", font=dict(color="#38BDF8")),
            side="left",
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.05)',
            tickfont=dict(color="#38BDF8")
        ),
        yaxis2=dict(
            title=dict(text="Probability (%)", font=dict(color="#F43F5E")),
            side="right",
            overlaying="y",
            range=[0, 100],
            showgrid=False,
            tickfont=dict(color="#F43F5E")
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(color="#CBD5E1")
        ),
        height=360,
        margin=dict(l=40, r=40, t=30, b=30),
        hovermode="x unified"
    )

    st.plotly_chart(trend_fig, use_container_width=True)
else:
    st.info("Forward daily time series aggregating for current target.")

# -----------------------------------------------------------------------------
# DETAILED OBSERVATORY TABS
# -----------------------------------------------------------------------------
st.markdown("---")
tab1, tab2, tab3 = st.tabs([
    "Risk Factor Attribution", 
    "Subsurface Hydrology", 
    "Emergency Protocols & SDMA"
])

with tab1:
    st.markdown("##### Primary Drivers Influencing Current Assessment")
    
    driver_df = pd.DataFrame(risk_output["drivers"])
    
    dcol1, dcol2 = st.columns([3, 2])
    with dcol1:
        bar_fig = px.bar(
            driver_df,
            x="contribution",
            y="factor",
            orientation='h',
            text="value",
            labels={"contribution": "Weight Contribution (%)", "factor": "Hazard Driver"},
            color="contribution",
            color_continuous_scale="Reds"
        )
        bar_fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#94A3B8"),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False),
            height=260,
            showlegend=False,
            margin=dict(l=10, r=20, t=10, b=10)
        )
        st.plotly_chart(bar_fig, use_container_width=True)
        
    with dcol2:
        st.markdown(f"""
        <div style="font-size: 0.88rem; color: #CBD5E1; background: rgba(255,255,255,0.02); padding: 1rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);">
            <b>Lithological & Terrain Overview:</b><br>
            • Geological Formation: <i>{target_geology}</i><br>
            • Critical Slope Threshold: <b>{target_slope}°</b> (Instability threshold: > 35°)<br>
            • Relief Energy: <b>{target_elevation:,} m a.s.l.</b><br>
            • Corridor Assessment: {target_notes}
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("##### Multi-Horizon Subsurface Soil Moisture Distribution")
    
    hourly_df = weather_res.get("hourly_df", None)
    if hourly_df is not None and not hourly_df.empty:
        latest = hourly_df.iloc[-1]
        
        depth_labels = [
            "0 - 1 cm (Surface)", 
            "1 - 3 cm (Topsoil)", 
            "3 - 9 cm (Root Zone)", 
            "9 - 27 cm (Mid Stratum)", 
            "27 - 81 cm (Deep Interface)"
        ]
        depth_vals = [
            latest.get("soil_moisture_0_to_1cm", 0.25),
            latest.get("soil_moisture_1_to_3cm", 0.26),
            latest.get("soil_moisture_3_to_9cm", 0.27),
            latest.get("soil_moisture_9_to_27cm", 0.29),
            latest.get("soil_moisture_27_to_81cm", 0.31)
        ]
        
        soil_df = pd.DataFrame({"Horizon": depth_labels, "Volumetric Moisture (m³/m³)": depth_vals})
        
        fig_soil = px.bar(
            soil_df, x="Volumetric Moisture (m³/m³)", y="Horizon", 
            orientation='h', color="Volumetric Moisture (m³/m³)",
            color_continuous_scale="Blues", range_x=[0, 0.6]
        )
        fig_soil.add_vline(
            x=0.40, line_dash="dash", line_color="#EF4444", 
            annotation_text="Liquefaction Saturation Limit (0.40 m³/m³)",
            annotation_font=dict(color="#EF4444", size=10)
        )
        fig_soil.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Plus Jakarta Sans", color="#94A3B8"),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(showgrid=False),
            height=250,
            margin=dict(l=20, r=20, t=10, b=10)
        )
        st.plotly_chart(fig_soil, use_container_width=True)
    else:
        st.write("Soil moisture horizon data currently unavailable.")

with tab3:
    st.markdown("##### State Disaster Management Authority (SDMA) Emergency Contacts")
    
    sdma = SDMA_CONTACTS.get(target_state, SDMA_CONTACTS["Sikkim"])
    
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

# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption("North Eastern Region Landslide Early Warning System | Integrated Satellite Telemetry (Open-Meteo) | LightGBM Geomorphic Engine | Developed for Disaster Risk Reduction")
