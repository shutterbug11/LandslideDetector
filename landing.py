"""
GroundCheck — Welcome & System Overview
Operational Landslide Early Warning & Infrastructure Risk Intelligence
for the North Eastern Himalayan Region of India.
"""

import os
import streamlit as st


def _render_html(html_str: str):
    """
    Renders pure HTML / CSS blocks safely into Streamlit without markdown
    interference. Strips blank lines and leading/trailing indentation so CommonMark
    never breaks the HTML block or interprets lines as raw code snippets.
    """
    clean = "\n".join([line.strip() for line in html_str.splitlines() if line.strip()])
    st.markdown(clean, unsafe_allow_html=True)


def render_landing():
    """
    Renders the institutional GroundCheck landing page in an authoritative,
    modern light theme with polished typography, crisp cards, and clear language.
    """
    # -------------------------------------------------------------------------
    # 1. Institutional CSS Design System (Light Theme, Modern Micro-Interactions)
    # -------------------------------------------------------------------------
    css_block = """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
<style>
/* Suppress default Streamlit header, menu, footer, and sidebar on landing */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }

/* Container layout */
.block-container {
    padding-top: 1.75rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1180px !important;
}

/* Typography & Institutional Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #0F172A;
    background-color: #F8FAFC;
}

/* Institutional Hero Section */
.inst-hero {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 3rem 2.5rem 2.5rem 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
    text-align: center;
    position: relative;
    overflow: hidden;
}

.inst-hero::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #1B4965 0%, #0284C7 50%, #0EA5E9 100%);
}

.inst-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 9999px;
    background: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #166534;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

.inst-badge i {
    color: #16A34A;
    font-size: 0.8rem;
}

.inst-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.85rem;
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
    font-size: 1.22rem;
    font-weight: 600;
    color: #1E293B;
    max-width: 860px;
    margin: 0 auto 1.25rem auto;
    line-height: 1.45;
}

.inst-desc {
    font-size: 0.95rem;
    color: #475569;
    max-width: 840px;
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
    border-top: 3px solid #1B4965;
    border-radius: 8px;
    padding: 1.35rem 1rem;
    text-align: center;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.stat-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(15, 23, 42, 0.07);
}

.stat-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #1B4965;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
    line-height: 1.1;
}

.stat-txt {
    font-size: 0.78rem;
    font-weight: 600;
    color: #475569;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    line-height: 1.35;
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
    color: #0284C7;
    margin-bottom: 0.35rem;
}

.inst-section-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.85rem;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.02em;
    margin-bottom: 0.45rem;
}

.inst-section-sub {
    font-size: 0.94rem;
    color: #64748B;
    max-width: 700px;
    margin: 0 auto;
    line-height: 1.55;
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
    border-radius: 10px;
    padding: 1.75rem 1.5rem;
    position: relative;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.step-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 24px -4px rgba(15, 23, 42, 0.08);
    border-color: #CBD5E1;
}

.step-num-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    background: #E0F2FE;
    color: #0369A1;
    font-size: 0.92rem;
    font-weight: 800;
    margin-bottom: 1.1rem;
    border: 1px solid #BAE6FD;
}

.step-head {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.55rem;
    display: flex;
    align-items: center;
    gap: 9px;
}

.step-head i {
    color: #0284C7;
    font-size: 1rem;
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
    border-radius: 10px;
    padding: 1.75rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    display: flex;
    flex-direction: column;
}

.feature-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.08);
    border-color: #CBD5E1;
}

.feature-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
}

.feature-icon-wrap {
    width: 42px;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: #F1F5F9;
    color: #1B4965;
    font-size: 1.18rem;
    border: 1px solid #E2E8F0;
}

.feature-tag {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 6px;
    background: #F8FAFC;
    color: #334155;
    border: 1px solid #E2E8F0;
}

.feature-name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.45rem;
}

.feature-summary {
    font-size: 0.88rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 1rem;
    flex-grow: 1;
}

.feature-list {
    list-style: none;
    padding: 0;
    margin: 0;
    font-size: 0.84rem;
    color: #334155;
    border-top: 1px solid #F1F5F9;
    padding-top: 0.95rem;
}

.feature-list li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 8px;
    line-height: 1.45;
}

.feature-list li:last-child {
    margin-bottom: 0;
}

.feature-list li i {
    color: #0284C7;
    font-size: 0.8rem;
    margin-top: 3px;
    flex-shrink: 0;
}

/* Action Launch Button */
div[data-testid="stButton"] button[kind="primary"] {
    background: #1B4965 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    padding: 0.85rem 2.25rem !important;
    border-radius: 8px !important;
    border: 1px solid #1B4965 !important;
    box-shadow: 0 4px 12px rgba(27, 73, 101, 0.25) !important;
    transition: all 0.2s ease-in-out !important;
    letter-spacing: 0.01em !important;
}

div[data-testid="stButton"] button[kind="primary"]:hover {
    background: #13374D !important;
    border-color: #13374D !important;
    color: #FFFFFF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(27, 73, 101, 0.35) !important;
}

/* Bottom Callout Banner */
.bottom-callout {
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-left: 5px solid #1B4965;
    border-radius: 10px;
    padding: 2.25rem 2.5rem;
    margin-bottom: 2.5rem;
    text-align: center;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
}

.bottom-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.55rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 0.5rem;
}

.bottom-sub {
    font-size: 0.94rem;
    color: #475569;
    max-width: 720px;
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
    color: #0284C7;
    text-decoration: none;
    font-weight: 600;
}

.inst-footer a:hover {
    text-decoration: underline;
}

.inst-footer-sources {
    margin-top: 8px;
    font-size: 0.77rem;
    color: #94A3B8;
}

/* Responsive Mobile Layout */
@media (max-width: 768px) {
    .inst-title { font-size: 2.2rem; }
    .inst-tagline { font-size: 1.05rem; }
    .stats-grid { grid-template-columns: repeat(2, 1fr); }
    .step-row { grid-template-columns: 1fr; }
    .feature-row { grid-template-columns: 1fr; }
}
</style>
"""
    _render_html(css_block)

    # -------------------------------------------------------------------------
    # 2. Hero Section
    # -------------------------------------------------------------------------
    hero_html = (
'<div class="inst-hero">'
'<div class="inst-badge">'
'<i class="fa-solid fa-satellite-dish"></i> OPERATIONAL EARLY WARNING OBSERVATORY &bull; NORTH EAST HIMALAYAN REGION'
'</div>'
'<div class="inst-title">'
'Ground<span class="inst-subbrand">Check</span>'
'</div>'
'<div class="inst-tagline">'
'AI-Powered Landslide Hazard Intelligence, Road Vulnerability Mapping & Population Evacuation Prioritization'
'</div>'
'<div class="inst-desc">'
'GroundCheck delivers real-time hazard decision support for State Disaster Management Authorities (SDMAs), district disaster cells, and emergency responders across India\'s 8 North Eastern states. By fusing physics-based terrain modeling with live satellite rainfall, subsurface soil moisture, and high-resolution settlement data, the platform turns raw meteorological telemetry into clear, proactive evacuation directives.'
'</div>'
'</div>'
    )
    _render_html(hero_html)

    # Hero Action Button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.4, 1])
    with btn_col2:
        if st.button("Launch Observatory Dashboard", key="hero_launch_btn", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    _render_html("<div style='margin-bottom: 2rem;'></div>")

    # -------------------------------------------------------------------------
    # 3. Verified System Statistics
    # -------------------------------------------------------------------------
    stats_html = (
'<div class="stats-grid">'
'<div class="stat-box">'
'<div class="stat-num">8</div>'
'<div class="stat-txt">Monitored Himalayan States</div>'
'</div>'
'<div class="stat-box">'
'<div class="stat-num">27</div>'
'<div class="stat-txt">Critical Corridor Hotspots</div>'
'</div>'
'<div class="stat-box">'
'<div class="stat-num">100m</div>'
'<div class="stat-txt">WorldPop Human Settlement Grid</div>'
'</div>'
'<div class="stat-box">'
'<div class="stat-num">5</div>'
'<div class="stat-txt">Subsurface Soil Depth Horizons</div>'
'</div>'
'</div>'
    )
    _render_html(stats_html)

    # -------------------------------------------------------------------------
    # 4. Operational Workflow (3-Step Pipeline)
    # -------------------------------------------------------------------------
    workflow_html = (
'<div class="inst-section-head">'
'<div class="inst-section-label">Analytical Pipeline</div>'
'<div class="inst-section-title">How GroundCheck Operates</div>'
'<div class="inst-section-sub">A continuous 3-stage intelligence loop connecting meteorological satellites, geomorphic AI modeling, and community vulnerability analysis.</div>'
'</div>'
'<div class="step-row">'
'<div class="step-box">'
'<div class="step-num-pill">1</div>'
'<div class="step-head"><i class="fa-solid fa-cloud-showers-heavy"></i> Live Weather & Soil Telemetry</div>'
'<div class="step-body">'
'Polls Open-Meteo satellite streams hourly to measure active precipitation intensity, 24h/48h/72h rainfall accumulation, and volumetric moisture saturation across 5 distinct soil horizons (0 to 81 cm deep).'
'</div>'
'</div>'
'<div class="step-box">'
'<div class="step-num-pill">2</div>'
'<div class="step-head"><i class="fa-solid fa-microchip"></i> Terrain Susceptibility Modeling</div>'
'<div class="step-body">'
'Combines Geological Survey of India (GSI) slope profiles, elevation, aspect, and curvature with live moisture triggers inside a trained LightGBM machine learning classifier to predict localized failure probability (0 to 100%).'
'</div>'
'</div>'
'<div class="step-box">'
'<div class="step-num-pill">3</div>'
'<div class="step-head"><i class="fa-solid fa-person-shelter"></i> Evacuation & Transit Prioritization</div>'
'<div class="step-body">'
'Overlays active hazard zones with OpenStreetMap road networks and 100m WorldPop population rasters to calculate Priority Scores (<span style="font-family:monospace;font-weight:600;">Risk % &times; Exposed Population</span>) for targeted evacuation staging.'
'</div>'
'</div>'
'</div>'
    )
    _render_html(workflow_html)

    # -------------------------------------------------------------------------
    # 5. Core Operational Modules (Polished, Natural, Clean HTML Rendering)
    # -------------------------------------------------------------------------
    modules_html = (
'<div class="inst-section-head">'
'<div class="inst-section-label">Core Capabilities</div>'
'<div class="inst-section-title">Operational System Modules</div>'
'<div class="inst-section-sub">Integrated tools engineered to empower disaster managers, field crews, and communities with clear, actionable hazard intelligence.</div>'
'</div>'
'<div class="feature-row">'
'<div class="feature-box">'
'<div class="feature-top">'
'<div class="feature-icon-wrap"><i class="fa-solid fa-mountain"></i></div>'
'<div class="feature-tag">AI Hazard Engine</div>'
'</div>'
'<div class="feature-name">Terrain Susceptibility & Risk Prediction</div>'
'<div class="feature-summary">'
'Evaluates real-time slope stability and failure probability using trained gradient-boosted trees fused with live meteorological telemetry.'
'</div>'
'<ul class="feature-list">'
'<li><i class="fa-solid fa-circle-check"></i> Real-time landslide probability calculation and standardized hazard tier assignment (Low, Medium, High)</li>'
'<li><i class="fa-solid fa-circle-check"></i> Transparent risk attribution separating static slope steepness from acute rainfall saturation</li>'
'<li><i class="fa-solid fa-circle-check"></i> 14-day forward risk trajectory forecasting driven by multi-day precipitation projections</li>'
'</ul>'
'</div>'
'<div class="feature-box">'
'<div class="feature-top">'
'<div class="feature-icon-wrap"><i class="fa-solid fa-road"></i></div>'
'<div class="feature-tag">OSMnx &bull; OpenStreetMap</div>'
'</div>'
'<div class="feature-name">Road Network Vulnerability & Transit Safety</div>'
'<div class="feature-summary">'
'Monitors drivable highways and arterial mountain roads within 5km of high-risk landslide zones to safeguard transit and emergency access.'
'</div>'
'<ul class="feature-list">'
'<li><i class="fa-solid fa-circle-check"></i> Automated 2,000m geodesic risk buffers highlighting vulnerable mountain corridors in amber</li>'
'<li><i class="fa-solid fa-circle-check"></i> Real-time integration of citizen and road patrol alerts to flag impassable, debris-blocked routes in red</li>'
'<li><i class="fa-solid fa-circle-check"></i> Interactive Folium geospatial map layer displaying segment-level road names, surface types, and hazard proximity</li>'
'</ul>'
'</div>'
'<div class="feature-box">'
'<div class="feature-top">'
'<div class="feature-icon-wrap"><i class="fa-solid fa-users"></i></div>'
'<div class="feature-tag">WorldPop 100m Gridded Data</div>'
'</div>'
'<div class="feature-name">Population-Weighted Evacuation Prioritization</div>'
'<div class="feature-summary">'
'Identifies high-urgency rescue and evacuation targets by weighting physical landslide probability against human settlement density.'
'</div>'
'<ul class="feature-list">'
'<li><i class="fa-solid fa-circle-check"></i> Transparent priority ranking formula: <span style="font-family:monospace;font-weight:600;">(Risk % / 100) &times; Exposed Population (within 2km)</span></li>'
'<li><i class="fa-solid fa-circle-check"></i> "Evacuate First" decision table sorting regional hotspots by expected impacted resident count</li>'
'<li><i class="fa-solid fa-circle-check"></i> State-level filtering and critical threshold counters to guide rapid NDRF and civil defense deployment</li>'
'</ul>'
'</div>'
'<div class="feature-box">'
'<div class="feature-top">'
'<div class="feature-icon-wrap"><i class="fa-solid fa-camera"></i></div>'
'<div class="feature-tag">Field Telemetry & SQLite</div>'
'</div>'
'<div class="feature-name">Citizen & Field Incident Geo-Reporting</div>'
'<div class="feature-summary">'
'Enables ground patrols, highway engineers, and local residents to report emerging fissures, debris flows, and road blocks in real time.'
'</div>'
'<ul class="feature-list">'
'<li><i class="fa-solid fa-circle-check"></i> Captures device GPS coordinates, hazard category, severity level, road status, and on-site photos</li>'
'<li><i class="fa-solid fa-circle-check"></i> Instant visualization of verified field reports as interactive map pins with photo preview popups</li>'
'<li><i class="fa-solid fa-circle-check"></i> Resilient SQLite local storage designed for reliable field logging even during network dropouts</li>'
'</ul>'
'</div>'
'<div class="feature-box">'
'<div class="feature-top">'
'<div class="feature-icon-wrap"><i class="fa-solid fa-envelope-circle-check"></i></div>'
'<div class="feature-tag">Automated SMTP Dispatch</div>'
'</div>'
'<div class="feature-name">Early Warning Subscriber Notifications</div>'
'<div class="feature-summary">'
'Dispatches automated, high-priority meteorological and geomorphic hazard warnings directly to enrolled residents and local authorities.'
'</div>'
'<ul class="feature-list">'
'<li><i class="fa-solid fa-circle-check"></i> Flexible alert subscriptions customized to specific states, districts, and trigger thresholds</li>'
'<li><i class="fa-solid fa-circle-check"></i> Strict email deliverability compliance (SPF/DKIM headers, RFC 8058 one-click opt-out) to avoid spam folders</li>'
'<li><i class="fa-solid fa-circle-check"></i> Instant test dispatch interface allowing subscribers to verify delivery straight into their primary inbox</li>'
'</ul>'
'</div>'
'<div class="feature-box">'
'<div class="feature-top">'
'<div class="feature-icon-wrap"><i class="fa-solid fa-language"></i></div>'
'<div class="feature-tag">AI4Bharat Translation</div>'
'</div>'
'<div class="feature-name">Multilingual Advisories & Emergency Directory</div>'
'<div class="feature-summary">'
'Delivers instant translations of warnings and emergency protocols across 5 regional languages to eliminate communication barriers.'
'</div>'
'<ul class="feature-list">'
'<li><i class="fa-solid fa-circle-check"></i> Native UI and advisory translation across English, Assamese, Bengali, Nepali, and Manipuri (Meitei Mayek)</li>'
'<li><i class="fa-solid fa-circle-check"></i> Official State Disaster Management Authority (SDMA) verified emergency phone numbers and control rooms</li>'
'<li><i class="fa-solid fa-circle-check"></i> National Disaster Response Force (NDRF) 1078 helpline and NDMA standard operating procedures (SOP)</li>'
'</ul>'
'</div>'
'</div>'
    )
    _render_html(modules_html)

    # -------------------------------------------------------------------------
    # 6. Bottom Action Banner
    # -------------------------------------------------------------------------
    bottom_html = (
'<div class="bottom-callout">'
'<div class="bottom-title">Ready to Explore the Live Observatory?</div>'
'<div class="bottom-sub">'
'Inspect real-time risk heatmaps, explore highway exposure buffers, review population-weighted evacuation rankings, and monitor 27 Himalayan district hotspots across North East India.'
'</div>'
'</div>'
    )
    _render_html(bottom_html)

    btn_b1, btn_b2, btn_b3 = st.columns([1, 1.4, 1])
    with btn_b2:
        if st.button("Enter GroundCheck Dashboard", key="bottom_launch_btn", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    # -------------------------------------------------------------------------
    # 7. Institutional Footer
    # -------------------------------------------------------------------------
    footer_html = (
'<div class="inst-footer">'
'<div><strong>GroundCheck</strong> &bull; Operational Landslide Early Warning System for the North Eastern Himalayan Region</div>'
'<div>Open source scientific software available on <a href="https://github.com/shutterbug11/LandslideDetector" target="_blank">GitHub</a></div>'
'<div class="inst-footer-sources">'
'Meteorological telemetry: Open-Meteo API &bull; '
'Population density: WorldPop (CC-BY 4.0) &bull; '
'Road network data: OpenStreetMap contributors (OSMnx) &bull; '
'Regional translation: AI4Bharat IndicTrans2 &bull; '
'Geomorphic baselines: Geological Survey of India (GSI)'
'</div>'
'</div>'
    )
    _render_html(footer_html)
