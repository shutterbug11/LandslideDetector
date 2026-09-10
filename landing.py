"""
=============================================================================
GroundCheck — Landing & Welcome Experience
AI-Powered Landslide Early Warning & Infrastructure Risk Intelligence
for the North Eastern Himalayan Region of India.
=============================================================================
"""

import streamlit as st


def render_landing():
    """
    Renders the modern, immersive GroundCheck hero landing page.
    Hides default Streamlit chrome (sidebar, hamburger menu, footer)
    and presents the problem statement, 3-step workflow, real feature
    cards, and interactive CTA launchers into the observatory dashboard.
    """
    # -------------------------------------------------------------------------
    # 1. Custom Responsive CSS & Chrome Suppression
    # -------------------------------------------------------------------------
    st.markdown("""
    <style>
        /* Suppress default Streamlit header, menu, footer, and sidebar on landing */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { visibility: hidden; }
        [data-testid="stSidebar"] { display: none; }
        
        /* Container layout */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 1240px !important;
        }

        /* Typography & Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
        
        body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hero Wrapper */
        .hero-section {
            text-align: center;
            padding: 3.5rem 1.5rem 2.5rem 1.5rem;
            background: radial-gradient(circle at 50% 20%, rgba(56, 189, 248, 0.12) 0%, rgba(15, 23, 42, 0) 70%);
            border-radius: 20px;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 14px;
            border-radius: 9999px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38BDF8;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 1.25rem;
        }

        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            letter-spacing: -0.035em;
            color: #F8FAFC;
            line-height: 1.1;
            margin-bottom: 0.75rem;
        }

        .hero-title span {
            background: linear-gradient(135deg, #38BDF8 0%, #818CF8 50%, #C084FC 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero-tagline {
            font-size: 1.28rem;
            font-weight: 500;
            color: #E2E8F0;
            max-width: 820px;
            margin: 0 auto 1.25rem auto;
            line-height: 1.55;
        }

        .hero-desc {
            font-size: 0.95rem;
            color: #94A3B8;
            max-width: 760px;
            margin: 0 auto 2rem auto;
            line-height: 1.65;
        }

        /* Metric Pill Strip */
        .stats-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            max-width: 960px;
            margin: 0 auto 2.5rem auto;
        }

        .stat-card {
            background: rgba(30, 41, 59, 0.55);
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 12px;
            padding: 1rem 0.8rem;
            text-align: center;
            backdrop-filter: blur(8px);
        }

        .stat-value {
            font-size: 1.65rem;
            font-weight: 800;
            color: #F8FAFC;
            letter-spacing: -0.02em;
            margin-bottom: 2px;
        }

        .stat-value.accent-cyan { color: #38BDF8; }
        .stat-value.accent-amber { color: #F59E0B; }
        .stat-value.accent-emerald { color: #10B981; }
        .stat-value.accent-purple { color: #A855F7; }

        .stat-label {
            font-size: 0.76rem;
            font-weight: 600;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Section Headings */
        .section-header {
            text-align: center;
            margin: 3.5rem 0 1.75rem 0;
        }

        .section-badge {
            display: inline-block;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #38BDF8;
            margin-bottom: 0.4rem;
        }

        .section-title {
            font-size: 1.85rem;
            font-weight: 700;
            color: #F8FAFC;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
        }

        .section-subtitle {
            font-size: 0.92rem;
            color: #94A3B8;
            max-width: 620px;
            margin: 0 auto;
        }

        /* How it Works Strip */
        .step-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 18px;
            margin-bottom: 3.5rem;
        }

        .step-card {
            position: relative;
            background: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 14px;
            padding: 1.6rem 1.4rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .step-card:hover {
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.4);
            background: rgba(30, 41, 59, 0.7);
        }

        .step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 8px;
            background: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            font-size: 0.88rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }

        .step-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 0.5rem;
        }

        .step-desc {
            font-size: 0.86rem;
            color: #94A3B8;
            line-height: 1.6;
        }

        /* Feature Cards Grid */
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 3.5rem;
        }

        .feature-card {
            background: rgba(30, 41, 59, 0.45);
            border: 1px solid rgba(148, 163, 184, 0.16);
            border-radius: 16px;
            padding: 1.8rem;
            position: relative;
            overflow: hidden;
            transition: all 0.25s ease;
        }

        .feature-card:hover {
            border-color: rgba(56, 189, 248, 0.45);
            transform: translateY(-2px);
            box-shadow: 0 12px 30px -10px rgba(15, 23, 42, 0.6);
        }

        .feature-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }

        .feature-icon {
            font-size: 1.75rem;
            width: 48px;
            height: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: rgba(56, 189, 248, 0.12);
        }

        .feature-badge {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 4px 10px;
            border-radius: 9999px;
            background: rgba(148, 163, 184, 0.12);
            color: #CBD5E1;
            border: 1px solid rgba(148, 163, 184, 0.2);
        }

        .feature-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 0.6rem;
        }

        .feature-desc {
            font-size: 0.88rem;
            color: #94A3B8;
            line-height: 1.6;
            margin-bottom: 1.1rem;
        }

        .feature-points {
            list-style: none;
            padding: 0;
            margin: 0;
            font-size: 0.82rem;
            color: #CBD5E1;
        }

        .feature-points li {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }

        .feature-points li::before {
            content: "•";
            color: #38BDF8;
            font-weight: bold;
            font-size: 1.2rem;
            line-height: 1;
        }

        /* Bottom CTA Banner */
        .bottom-banner {
            text-align: center;
            padding: 3rem 1.5rem;
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 20px;
            margin-bottom: 2.5rem;
        }

        /* Launch CTA Button Styling */
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #0284C7 0%, #38BDF8 100%) !important;
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 1.12rem !important;
            padding: 0.85rem 2.2rem !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255, 255, 255, 0.3) !important;
            box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.45) !important;
            transition: all 0.25s ease !important;
            letter-spacing: -0.01em !important;
        }

        div[data-testid="stButton"] button[kind="primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 14px 30px -4px rgba(56, 189, 248, 0.65) !important;
            border-color: rgba(255, 255, 255, 0.6) !important;
        }

        /* Footer */
        .landing-footer {
            text-align: center;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(148, 163, 184, 0.12);
            color: #64748B;
            font-size: 0.82rem;
            line-height: 1.6;
        }

        .landing-footer a {
            color: #38BDF8;
            text-decoration: none;
            font-weight: 600;
        }

        .landing-footer a:hover {
            text-decoration: underline;
        }

        /* Responsive Mobile Handling */
        @media (max-width: 768px) {
            .hero-title { font-size: 2.5rem; }
            .hero-tagline { font-size: 1.1rem; }
            .stats-strip { grid-template-columns: repeat(2, 1fr); }
            .step-grid { grid-template-columns: 1fr; }
            .feature-grid { grid-template-columns: 1fr; }
        }
    </style>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 2. Hero Section
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="hero-section">
        <div class="hero-badge">
            <span>📡</span> REAL-TIME EARLY WARNING OBSERVATORY &bull; NORTH EAST INDIA
        </div>
        <div class="hero-title">
            Ground<span>Check</span>
        </div>
        <div class="hero-tagline">
            AI-Powered Landslide Hazard Early Warning & Infrastructure Risk Intelligence for the North Eastern Himalayan Region
        </div>
        <div class="hero-desc">
            Synthesizing real-time satellite meteorological telemetry (Open-Meteo), a dual-pillar LightGBM geomorphic susceptibility engine, OpenStreetMap road network risk buffering (OSMnx), and community geo-reporting to protect critical mountain transit corridors.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Primary Hero Launch Button
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1.6, 1])
    with btn_col2:
        if st.button("🚀 Launch Observatory Dashboard", key="hero_launch_btn", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)

    # Metric Statistics Pill Strip
    st.markdown("""
    <div class="stats-strip">
        <div class="stat-card">
            <div class="stat-value accent-cyan">8</div>
            <div class="stat-label">Himalayan States</div>
        </div>
        <div class="stat-card">
            <div class="stat-value accent-amber">27</div>
            <div class="stat-label">Monitored Hotspots</div>
        </div>
        <div class="stat-card">
            <div class="stat-value accent-emerald">34+</div>
            <div class="stat-label">Sensory Features</div>
        </div>
        <div class="stat-card">
            <div class="stat-value accent-purple">Live</div>
            <div class="stat-label">Satellite Telemetry</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3. How It Works (3-Step Pipeline Strip)
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="section-header">
        <div class="section-badge">Architecture & Pipeline</div>
        <div class="section-title">How GroundCheck Works</div>
        <div class="section-subtitle">A multi-scale early warning pipeline designed for complex Himalayan terrain.</div>
    </div>
    
    <div class="step-grid">
        <div class="step-card">
            <div class="step-number">01</div>
            <div class="step-title">🛰️ Satellite Telemetry Ingestion</div>
            <div class="step-desc">
                Pulls live meteorological telemetry via Open-Meteo: 24h/72h antecedent rainfall, precipitation rates, and Sentinel-derived volumetric topsoil and subsoil moisture saturation.
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">02</div>
            <div class="step-title">🧠 Dual-Pillar ML Geomorphic Model</div>
            <div class="step-desc">
                Evaluates static slope topography (elevation, slope angle, aspect, TWI, lithology) fused dynamically with hydrological saturation thresholds to compute an exact failure probability index (0–100%).
            </div>
        </div>
        <div class="step-card">
            <div class="step-number">03</div>
            <div class="step-title">🗺️ GIS Heatmap & Rapid Alerts</div>
            <div class="step-desc">
                Plots dynamic Folium hazard heatmaps, projects local OSMnx road networks within 5km for 2km risk buffering, and triggers multilingual early warning alerts in 8 Indic languages.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 4. Verified Core Feature Cards
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="section-header">
        <div class="section-badge">Platform Capabilities</div>
        <div class="section-title">Fully Operational System Modules</div>
        <div class="section-subtitle">Real-time tools engineered specifically for state disaster authorities, district administrations, and citizens.</div>
    </div>
    
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon">⚡</div>
                <div class="feature-badge">LightGBM Machine Learning</div>
            </div>
            <div class="feature-title">Predictive Landslide Risk Modeling</div>
            <div class="feature-desc">
                Trained on millions of terrain pixels with imbalanced hazard handling. Decomposes risk into static geomorphic vulnerability vs dynamic 72h antecedent precipitation triggers.
            </div>
            <ul class="feature-points">
                <li>Real-time probability index & hazard level classification</li>
                <li>Hydrological breach threshold telemetry breakdown</li>
                <li>Forward 14-day landslide risk trajectory forecasting</li>
            </ul>
        </div>
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon">🛣️</div>
                <div class="feature-badge">Folium &bull; OSMnx &bull; GeoPandas</div>
            </div>
            <div class="feature-title">GIS Heatmap & Road Risk Layer</div>
            <div class="feature-desc">
                Continuous model-weighted spatial heatmaps across North East India combined with live drivable road networks dynamically pulled via OpenStreetMap Overpass APIs.
            </div>
            <ul class="feature-points">
                <li>True metric 2,000m buffer intersection for transit corridors</li>
                <li>Color-coded road edges: Normal (Gray), At-Risk (Orange), Blocked (Red)</li>
                <li>Interactive Folium layer toggles with detailed road metadata tooltips</li>
            </ul>
        </div>
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon">🌐</div>
                <div class="feature-badge">AI4Bharat IndicTrans2</div>
            </div>
            <div class="feature-title">Multilingual Alerts & SDMA Protocols</div>
            <div class="feature-desc">
                Instant translation of meteorological summaries, early warning bulletins, and State Disaster Management Authority (SDMA) instructions across 8 regional Indic languages.
            </div>
            <ul class="feature-points">
                <li>Native Bengali, Assamese, Hindi, Nepali, and Bodo translations</li>
                <li>Automated SMTP subscriber alerts with Bayesian spam filter compliance</li>
                <li>Direct one-click emergency control room & NDRF dispatch contacts</li>
            </ul>
        </div>
        <div class="feature-card">
            <div class="feature-header">
                <div class="feature-icon">📸</div>
                <div class="feature-badge">SQLite &bull; Field Telemetry</div>
            </div>
            <div class="feature-title">Citizen Field Incident Geo-Reporting</div>
            <div class="feature-desc">
                Empowers field patrols, highway authorities (BRO), and local communities to transmit geo-tagged hazard observations with live photo proof and blockage warnings.
            </div>
            <ul class="feature-points">
                <li>Integrated camera capture & photo upload with Base64 popup rendering</li>
                <li>Automatic integration with the OSMnx road network blockage marker</li>
                <li>Offline-first local SQLite persistence with verified hazard audits</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. Bottom Call to Action
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="bottom-banner">
        <div style="font-size: 1.8rem; font-weight: 800; color: #F8FAFC; margin-bottom: 0.5rem;">
            Ready to Explore the Hazard Observatory?
        </div>
        <div style="font-size: 0.95rem; color: #94A3B8; max-width: 600px; margin: 0 auto 1.75rem auto;">
            Launch into the live interactive map, query any of the 27 monitored hotspots across North East India, or simulate dual-station corridor stability.
        </div>
    </div>
    """, unsafe_allow_html=True)

    btn_b1, btn_b2, btn_b3 = st.columns([1, 1.6, 1])
    with btn_b2:
        if st.button("🚀 Enter GroundCheck Observatory", key="bottom_launch_btn", type="primary", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()

    # -------------------------------------------------------------------------
    # 6. Landing Footer
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="landing-footer">
        <div><b>GroundCheck</b> &bull; North Eastern Region Landslide Early Warning System</div>
        <div>Developed for Geological &amp; Climate Disaster Risk Reduction | Open Source on <a href="https://github.com/shutterbug11/LandslideDetector" target="_blank">GitHub</a></div>
        <div style="margin-top: 4px; font-size: 0.74rem; color: #475569;">Satellite data powered by Open-Meteo &bull; Road network infrastructure via OpenStreetMap (OSMnx) &bull; Multilingual engine by AI4Bharat</div>
    </div>
    """, unsafe_allow_html=True)
