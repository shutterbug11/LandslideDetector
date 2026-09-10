"""
GroundCheck — Welcome & System Overview
Operational Landslide Early Warning & Infrastructure Risk Intelligence
for the North Eastern Himalayan Region of India.
"""

import os
import streamlit as st

def render_landing():
    """
    Renders the institutional GroundCheck landing page in an authoritative light theme,
    modeled after disaster-management and hazard-monitoring agencies (NDMA, ReliefWeb, USGS).
    """
    # -------------------------------------------------------------------------
    # 1. Institutional CSS Design System (Light Theme, No Emojis, No Gradients)
    # -------------------------------------------------------------------------
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        /* Suppress default Streamlit header, menu, footer, and sidebar on landing */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
        [data-testid="stSidebar"] { display: none; }
        
        /* Container layout */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3.5rem !important;
            max-width: 1180px !important;
        }

        /* Typography & Institutional Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0F172A;
            background-color: #F8F9FA;
        }

        /* Institutional Hero Section */
        .inst-hero {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 3rem 2.5rem 2.5rem 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            text-align: center;
        }

        .inst-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 4px;
            background: #F1F5F9;
            border: 1px solid #CBD5E1;
            color: #1B4965;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 1.5rem;
        }

        .inst-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 2.75rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: #0F172A;
            line-height: 1.15;
            margin-bottom: 0.85rem;
        }

        .inst-title .inst-subbrand {
            color: #1B4965;
        }

        .inst-tagline {
            font-size: 1.18rem;
            font-weight: 500;
            color: #334155;
            max-width: 860px;
            margin: 0 auto 1.25rem auto;
            line-height: 1.5;
        }

        .inst-desc {
            font-size: 0.94rem;
            color: #64748B;
            max-width: 820px;
            margin: 0 auto 2rem auto;
            line-height: 1.65;
        }

        /* Stats Strip */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            max-width: 1040px;
            margin: 0 auto 2.5rem auto;
        }

        .stat-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 6px;
            padding: 1.25rem 1rem;
            text-align: center;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .stat-num {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 2rem;
            font-weight: 800;
            color: #1B4965;
            letter-spacing: -0.02em;
            margin-bottom: 4px;
        }

        .stat-txt {
            font-size: 0.78rem;
            font-weight: 600;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        /* Section Headers */
        .inst-section-head {
            text-align: center;
            margin: 3.5rem 0 1.75rem 0;
        }

        .inst-section-label {
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #1B4965;
            margin-bottom: 0.35rem;
        }

        .inst-section-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1.75rem;
            font-weight: 700;
            color: #0F172A;
            letter-spacing: -0.02em;
            margin-bottom: 0.4rem;
        }

        .inst-section-sub {
            font-size: 0.92rem;
            color: #64748B;
            max-width: 680px;
            margin: 0 auto;
            line-height: 1.5;
        }

        /* How It Works - Step Cards */
        .step-row {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 3.5rem;
        }

        .step-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1.75rem 1.5rem;
            position: relative;
        }

        .step-num-pill {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            border-radius: 6px;
            background: #F1F5F9;
            color: #1B4965;
            font-size: 0.88rem;
            font-weight: 800;
            margin-bottom: 1.1rem;
            border: 1px solid #CBD5E1;
        }

        .step-head {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .step-head i {
            color: #1B4965;
            font-size: 0.95rem;
        }

        .step-body {
            font-size: 0.88rem;
            color: #475569;
            line-height: 1.6;
        }

        /* Feature Matrix Cards */
        .feature-row {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 22px;
            margin-bottom: 3.5rem;
        }

        .feature-box {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1.75rem;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }

        .feature-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .feature-icon-wrap {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 6px;
            background: #F1F5F9;
            color: #1B4965;
            font-size: 1.15rem;
            border: 1px solid #E2E8F0;
        }

        .feature-tag {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 4px;
            background: #F8FAFC;
            color: #475569;
            border: 1px solid #E2E8F0;
        }

        .feature-name {
            font-size: 1.12rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.5rem;
        }

        .feature-summary {
            font-size: 0.88rem;
            color: #475569;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .feature-list {
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 0.84rem;
            color: #334155;
            border-top: 1px solid #F1F5F9;
            padding-top: 0.85rem;
        }

        .feature-list li {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 8px;
            line-height: 1.45;
        }

        .feature-list li i {
            color: #1B4965;
            font-size: 0.75rem;
            margin-top: 4px;
        }

        /* Action Launch Button */
        div[data-testid="stButton"] button[kind="primary"] {
            background: #1B4965 !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            padding: 0.8rem 2.25rem !important;
            border-radius: 6px !important;
            border: 1px solid #1B4965 !important;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
            transition: background-color 0.15s ease-in-out !important;
            letter-spacing: 0.01em !important;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: #13374D !important;
            border-color: #13374D !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
        }

        /* Bottom Callout Banner */
        .bottom-callout {
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            border-left: 4px solid #1B4965;
            border-radius: 6px;
            padding: 2rem 2.5rem;
            margin-bottom: 2.5rem;
            text-align: center;
        }

        .bottom-title {
            font-size: 1.45rem;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 0.5rem;
        }

        .bottom-sub {
            font-size: 0.92rem;
            color: #475569;
            max-width: 680px;
            margin: 0 auto 1.5rem auto;
            line-height: 1.6;
        }

        /* Institutional Footer */
        .inst-footer {
            text-align: center;
            padding-top: 2rem;
            border-top: 1px solid #E2E8F0;
            color: #64748B;
            font-size: 0.82rem;
            line-height: 1.65;
        }

        .inst-footer a {
            color: #1B4965;
            text-decoration: none;
            font-weight: 600;
        }

        .inst-footer a:hover {
            text-decoration: underline;
        }

        .inst-footer-sources {
            margin-top: 6px;
            font-size: 0.76rem;
            color: #94A3B8;
        }

        /* Responsive Mobile Layout */
        @media (max-width: 768px) {
            .inst-title { font-size: 2.1rem; }
            .inst-tagline { font-size: 1.05rem; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .step-row { grid-template-columns: 1fr; }
            .feature-row { grid-template-columns: 1fr; }
        }
    </style>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Hero Section
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="inst-hero">
        <div class="inst-badge">
            <i class="fa-solid fa-tower-broadcast"></i> OPERATIONAL EARLY WARNING OBSERVATORY &bull; NORTH EAST INDIA
        </div>
        <div class="inst-title">
            Ground<span class="inst-subbrand">Check</span>
        </div>
        <div class="inst-tagline">
            Landslide Hazard Early Warning, Road Infrastructure Risk Assessment, and Population-Weighted Evacuation Prioritization
        </div>
        <div class="inst-desc">
            An operational decision-support platform for State Disaster Management Authorities (SDMAs), district administrations, and emergency response teams across the 8 North Eastern states of India. Integrates machine learning terrain susceptibility modeling, real-time Open-Meteo precipitation and soil moisture data, OpenStreetMap road networks, and WorldPop settlement density.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Action Button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.4, 1])
    with btn_col2:
        if st.button("Launch Dashboard", key="hero_launch_btn", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. Verified System Statistics (Sourced Directly from Codebase Config)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-box">
            <div class="stat-num">8</div>
            <div class="stat-txt">Himalayan States</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">27</div>
            <div class="stat-txt">Monitored Hotspots</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">100m</div>
            <div class="stat-txt">Population Grid (WorldPop)</div>
        </div>
        <div class="stat-box">
            <div class="stat-num">5</div>
            <div class="stat-txt">Soil Moisture Horizons</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. Operational Workflow (3-Step Pipeline)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="inst-section-head">
        <div class="inst-section-label">System Architecture</div>
        <div class="inst-section-title">How GroundCheck Operates</div>
        <div class="inst-section-sub">A three-stage analytical workflow connecting meteorological telemetry, geomorphic susceptibility modeling, and community impact analysis.</div>
    </div>
    
    <div class="step-row">
        <div class="step-box">
            <div class="step-num-pill">1</div>
            <div class="step-head">
                <i class="fa-solid fa-cloud-showers-heavy"></i> Meteorological Ingestion
            </div>
            <div class="step-body">
                Queries Open-Meteo hourly to obtain current precipitation rates, 24h, 48h, and 72h antecedent rainfall accumulation, and volumetric soil moisture content across 5 stratigraphic depths (0 to 81 cm).
            </div>
        </div>
        <div class="step-box">
            <div class="step-num-pill">2</div>
            <div class="step-head">
                <i class="fa-solid fa-chart-line"></i> Susceptibility Modeling
            </div>
            <div class="step-body">
                Evaluates static terrain variables (slope gradient, elevation, aspect, topographic wetness index, curvature, lithology) fused with live hydrological triggers via a LightGBM classification engine to predict hazard probability (0 to 100%).
            </div>
        </div>
        <div class="step-box">
            <div class="step-num-pill">3</div>
            <div class="step-head">
                <i class="fa-solid fa-users-viewfinder"></i> Exposure & Prioritization
            </div>
            <div class="step-body">
                Overlays active hazard zones with OpenStreetMap road networks and 100m WorldPop population rasters to calculate Priority Scores (<span style="font-family:monospace;font-weight:600;">Risk % × Exposed Population within 2km</span>) for evacuation ranking.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. Core Modules (Truthful, Codebase-Verified Platform Capabilities)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="inst-section-head">
        <div class="inst-section-label">Functional Capabilities</div>
        <div class="inst-section-title">Operational System Modules</div>
        <div class="inst-section-sub">Tools implemented in GroundCheck to support real-time hazard monitoring, disaster relief planning, and public safety.</div>
    </div>
    
    <div class="feature-row">
        <div class="feature-box">
            <div class="feature-top">
                <div class="feature-icon-wrap"><i class="fa-solid fa-mountain"></i></div>
                <div class="feature-tag">Machine Learning Engine</div>
            </div>
            <div class="feature-name">Terrain Susceptibility & Risk Prediction</div>
            <div class="feature-summary">
                LightGBM model evaluating geomorphic features derived from Geological Survey of India (GSI) slope profiles.
            </div>
            <ul class="feature-list">
                <li><i class="fa-solid fa-check"></i> Real-time landslide probability calculation and hazard level categorization</li>
                <li><i class="fa-solid fa-check"></i> Multi-factor attribution separating static slope vulnerability from rainfall triggers</li>
                <li><i class="fa-solid fa-check"></i> 14-day forward risk trajectory forecasting based on precipitation projections</li>
            </ul>
        </div>
        
        <div class="feature-box">
            <div class="feature-top">
                <div class="feature-icon-wrap"><i class="fa-solid fa-road"></i></div>
                <div class="feature-tag">OSMnx &bull; OpenStreetMap</div>
            </div>
            <div class="feature-name">Road Network Vulnerability Layer</div>
            <div class="feature-summary">
                Extracts drivable highway and local road segments within 5km of monitored hotspots using OpenStreetMap data.
            </div>
            <ul class="feature-list">
                <li><i class="fa-solid fa-check"></i> Geodesic 2,000m circular risk buffer intersection marking at-risk segments in amber</li>
                <li><i class="fa-solid fa-check"></i> Citizen and patrol incident reports integrated to mark blocked road segments in red</li>
                <li><i class="fa-solid fa-check"></i> Interactive Folium map layer with segment metadata tooltips</li>
            </ul>
        </div>
        
        <div class="feature-box">
            <div class="feature-top">
                <div class="feature-icon-wrap"><i class="fa-solid fa-users"></i></div>
                <div class="feature-tag">WorldPop 2020 Gridded Data</div>
            </div>
            <div class="feature-name">Population-Weighted Evacuation Prioritization</div>
            <div class="feature-summary">
                Zonal statistics engine calculating human population exposure within a 2km radius using 100m gridded data for India.
            </div>
            <ul class="feature-list">
                <li><i class="fa-solid fa-check"></i> Priority score formula: <span style="font-family:monospace;font-weight:600;">(Risk % / 100) × Exposed Population</span></li>
                <li><i class="fa-solid fa-check"></i> "Evacuate First" ranked table sorting hotspots by expected affected population</li>
                <li><i class="fa-solid fa-check"></i> State-level filtering and critical threshold counters for rescue team allocation</li>
            </ul>
        </div>

        <div class="feature-box">
            <div class="feature-top">
                <div class="feature-icon-wrap"><i class="fa-solid fa-camera"></i></div>
                <div class="feature-tag">SQLite Database</div>
            </div>
            <div class="feature-name">Citizen & Field Incident Reporting</div>
            <div class="feature-summary">
                Ground telemetry interface enabling patrols, highway engineers, and citizens to file geo-referenced incident reports.
            </div>
            <ul class="feature-list">
                <li><i class="fa-solid fa-check"></i> GPS coordinates, hazard type, incident severity, and live photo upload</li>
                <li><i class="fa-solid fa-check"></i> Automatic plotting of field incident pins with base64 photo popups on the Folium map</li>
                <li><i class="fa-solid fa-check"></i> Local SQLite database persistence for offline and field compliance</li>
            </ul>
        </div>

        <div class="feature-box">
            <div class="feature-top">
                <div class="feature-icon-wrap"><i class="fa-solid fa-envelope"></i></div>
                <div class="feature-tag">SMTP Alert Pipeline</div>
            </div>
            <div class="feature-name">Early Warning Subscriber Notifications</div>
            <div class="feature-summary">
                Automated email alert engine dispatching high-risk advisories to registered residents and local authorities.
            </div>
            <ul class="feature-list">
                <li><i class="fa-solid fa-check"></i> State and district subscriber registry with one-click registration and removal</li>
                <li><i class="fa-solid fa-check"></i> Pre-send spam taxonomy scoring (SPF/DKIM/DMARC headers, clean payload validation)</li>
                <li><i class="fa-solid fa-check"></i> Immediate test dispatch verification interface with delivery status reporting</li>
            </ul>
        </div>

        <div class="feature-box">
            <div class="feature-top">
                <div class="feature-icon-wrap"><i class="fa-solid fa-language"></i></div>
                <div class="feature-tag">AI4Bharat Translation</div>
            </div>
            <div class="feature-name">Multilingual Advisories & SDMA Directory</div>
            <div class="feature-summary">
                Instant translation of alerts, emergency protocols, and weather summaries across 5 regional languages.
            </div>
            <ul class="feature-list">
                <li><i class="fa-solid fa-check"></i> Full UI and advisory support in English, Assamese, Bengali, Nepali, and Manipuri</li>
                <li><i class="fa-solid fa-check"></i> State Disaster Management Authority (SDMA) verified contact numbers and control rooms</li>
                <li><i class="fa-solid fa-check"></i> National Disaster Response Force (NDRF) 1078 helpline and emergency protocols</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 6. Bottom Action Banner
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="bottom-callout">
        <div class="bottom-title">Access the Operational Observatory</div>
        <div class="bottom-sub">
            Monitor real-time hazard indices, view continuous risk heatmaps, inspect OSMnx road network exposures, and review population-weighted evacuation rankings across 27 Himalayan district hotspots.
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_b1, btn_b2, btn_b3 = st.columns([1, 1.4, 1])
    with btn_b2:
        if st.button("Enter GroundCheck Dashboard", key="bottom_launch_btn", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    # -------------------------------------------------------------------------
    # 7. Institutional Footer
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="inst-footer">
        <div><strong>GroundCheck</strong> &bull; North Eastern Himalayan Landslide Early Warning System</div>
        <div>Open source research software available on <a href="https://github.com/shutterbug11/LandslideDetector" target="_blank">GitHub</a></div>
        <div class="inst-footer-sources">
            Meteorological data: Open-Meteo API &bull; 
            Population data: WorldPop (CC-BY 4.0) &bull; 
            Road network data: OpenStreetMap contributors (OSMnx) &bull; 
            Translation engine: AI4Bharat IndicTrans2 &bull; 
            Geomorphic baseline: Geological Survey of India (GSI)
        </div>
    </div>
    """, unsafe_allow_html=True)
