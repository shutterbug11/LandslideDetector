"""
Dual-Location Comparison Service for Landslide Early Warning System.
Provides geodetic distance calculations, risk and weather deltas,
and comparative Plotly visualizers for side-by-side location analysis.
"""

import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Compute great-circle distance between two GPS points in kilometers using Haversine formula.
    """
    r_earth = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return round(r_earth * c, 1)


def compute_comparison_deltas(
    loc_a: dict,
    loc_b: dict,
    risk_a: dict,
    risk_b: dict,
    weather_a: dict,
    weather_b: dict
) -> dict:
    """
    Calculate quantitative differences between Location A and Location B.
    """
    prob_a = risk_a.get("probability", 0.0)
    prob_b = risk_b.get("probability", 0.0)
    prob_delta = round(prob_b - prob_a, 1)

    trig_a = weather_a.get("triggers", {})
    trig_b = weather_b.get("triggers", {})

    rain24_a = trig_a.get("rain_past_24h", 0.0)
    rain24_b = trig_b.get("rain_past_24h", 0.0)
    rain24_delta = round(rain24_b - rain24_a, 1)

    rain72_a = trig_a.get("rain_past_72h", 0.0)
    rain72_b = trig_b.get("rain_past_72h", 0.0)
    rain72_delta = round(rain72_b - rain72_a, 1)

    soil_top_a = trig_a.get("soil_moisture_top", 0.25) * 100.0
    soil_top_b = trig_b.get("soil_moisture_top", 0.25) * 100.0
    soil_top_delta = round(soil_top_b - soil_top_a, 1)

    soil_deep_a = trig_a.get("soil_moisture_deep", 0.30) * 100.0
    soil_deep_b = trig_b.get("soil_moisture_deep", 0.30) * 100.0
    soil_deep_delta = round(soil_deep_b - soil_deep_a, 1)

    slope_a = loc_a.get("slope", 0.0)
    slope_b = loc_b.get("slope", 0.0)
    slope_delta = round(slope_b - slope_a, 1)

    elev_a = loc_a.get("elevation", 0)
    elev_b = loc_b.get("elevation", 0)
    elev_delta = elev_b - elev_a

    distance_km = calculate_haversine_distance(
        loc_a.get("lat", 0.0), loc_a.get("lon", 0.0),
        loc_b.get("lat", 0.0), loc_b.get("lon", 0.0)
    )

    # Determine higher risk location
    if prob_a > prob_b:
        higher_risk = "A"
        higher_name = loc_a.get("title", "Location A")
        lower_name = loc_b.get("title", "Location B")
        margin = round(prob_a - prob_b, 1)
    elif prob_b > prob_a:
        higher_risk = "B"
        higher_name = loc_b.get("title", "Location B")
        lower_name = loc_a.get("title", "Location A")
        margin = round(prob_b - prob_a, 1)
    else:
        higher_risk = "EQUAL"
        higher_name = "Both Locations"
        lower_name = ""
        margin = 0.0

    return {
        "distance_km": distance_km,
        "prob_a": prob_a,
        "prob_b": prob_b,
        "prob_delta": prob_delta,
        "rain24_a": rain24_a,
        "rain24_b": rain24_b,
        "rain24_delta": rain24_delta,
        "rain72_a": rain72_a,
        "rain72_b": rain72_b,
        "rain72_delta": rain72_delta,
        "soil_top_a": soil_top_a,
        "soil_top_b": soil_top_b,
        "soil_top_delta": soil_top_delta,
        "soil_deep_a": soil_deep_a,
        "soil_deep_b": soil_deep_b,
        "soil_deep_delta": soil_deep_delta,
        "slope_a": slope_a,
        "slope_b": slope_b,
        "slope_delta": slope_delta,
        "elev_a": elev_a,
        "elev_b": elev_b,
        "elev_delta": elev_delta,
        "higher_risk": higher_risk,
        "higher_name": higher_name,
        "lower_name": lower_name,
        "margin": margin
    }


def create_comparative_soil_moisture_chart(
    weather_a: dict,
    weather_b: dict,
    name_a: str = "Location A",
    name_b: str = "Location B"
) -> go.Figure:
    """
    Generate a grouped horizontal bar chart comparing volumetric soil moisture
    across 5 horizons between Location A and Location B.
    """
    depth_labels = [
        "0 - 1 cm (Surface)",
        "1 - 3 cm (Topsoil)",
        "3 - 9 cm (Root Zone)",
        "9 - 27 cm (Mid Stratum)",
        "27 - 81 cm (Deep Interface)"
    ]

    def extract_vals(w):
        hourly = w.get("hourly_df", None)
        if hourly is not None and not hourly.empty:
            latest = hourly.iloc[-1]
            return [
                float(latest.get("soil_moisture_0_to_1cm", 0.25)),
                float(latest.get("soil_moisture_1_to_3cm", 0.26)),
                float(latest.get("soil_moisture_3_to_9cm", 0.27)),
                float(latest.get("soil_moisture_9_to_27cm", 0.29)),
                float(latest.get("soil_moisture_27_to_81cm", 0.31))
            ]
        trig = w.get("triggers", {})
        top = trig.get("soil_moisture_top", 0.25)
        mid = trig.get("soil_moisture_mid", 0.28)
        deep = trig.get("soil_moisture_deep", 0.30)
        return [top * 0.95, top, mid, deep * 0.95, deep]

    vals_a = extract_vals(weather_a)
    vals_b = extract_vals(weather_b)

    fig = go.Figure()

    # Location A trace (Cyan / Blue theme)
    fig.add_trace(go.Bar(
        y=depth_labels,
        x=vals_a,
        name=f"A: {name_a}",
        orientation='h',
        marker=dict(
            color='rgba(56, 189, 248, 0.85)',
            line=dict(color='#0284C7', width=1.5)
        ),
        text=[f"{v:.3f}" for v in vals_a],
        textposition='auto',
        textfont=dict(color='#FFFFFF', size=11)
    ))

    # Location B trace (Amber / Rose theme)
    fig.add_trace(go.Bar(
        y=depth_labels,
        x=vals_b,
        name=f"B: {name_b}",
        orientation='h',
        marker=dict(
            color='rgba(244, 63, 94, 0.85)',
            line=dict(color='#BE123C', width=1.5)
        ),
        text=[f"{v:.3f}" for v in vals_b],
        textposition='auto',
        textfont=dict(color='#FFFFFF', size=11)
    ))

    # Liquefaction critical limit
    fig.add_vline(
        x=0.40,
        line_dash="dash",
        line_color="#EF4444",
        line_width=2.5,
        annotation_text="Liquefaction Saturation Limit (0.40 m³/m³)",
        annotation_position="top right",
        annotation_font=dict(color="#EF4444", size=11)
    )

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8"),
        xaxis=dict(
            title=dict(text="Volumetric Moisture Content (m³/m³)", font=dict(color="#CBD5E1")),
            range=[0, 0.58],
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.06)',
            tickfont=dict(color="#94A3B8")
        ),
        yaxis=dict(
            autorange="reversed",
            showgrid=False,
            tickfont=dict(color="#E2E8F0", size=12)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="center",
            x=0.5,
            font=dict(color="#E2E8F0", size=12)
        ),
        height=320,
        margin=dict(l=20, r=20, t=25, b=20)
    )

    return fig


def create_comparative_forecast_chart(
    weather_a: dict,
    weather_b: dict,
    risk_a: dict,
    risk_b: dict,
    name_a: str = "Location A",
    name_b: str = "Location B"
) -> go.Figure:
    """
    Generate a 14-day comparative precipitation and risk probability trajectory chart.
    """
    daily_a = weather_a.get("daily_df", None)
    daily_b = weather_b.get("daily_df", None)

    dates = [
        (pd.Timestamp.now() + pd.Timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(14)
    ]

    def prep_daily(daily, risk, base_precip=15.0):
        if daily is not None and not daily.empty:
            df = daily.copy().head(14)
            d_dates = df['date'].astype(str).tolist()
            precip = df['total_precip_mm'].tolist()
            base_geo = risk.get('ml_probability', 40.0)
            probs = []
            for _, row in df.iterrows():
                p_mm = row['total_precip_mm']
                sm = row['soil_moist_top']
                f_risk = 0.50 * (base_geo / 100.0) + 0.35 * np.clip(p_mm / 60.0, 0, 1.0) + 0.15 * np.clip((sm - 0.20) / 0.25, 0, 1.0)
                probs.append(round(float(np.clip(f_risk * 100, 5, 95)), 1))
            return d_dates, precip, probs
        else:
            base_p = risk.get('probability', 30.0)
            precip = [max(0.0, base_precip + 5.0 * np.sin(i)) for i in range(14)]
            probs = [round(float(np.clip(base_p + 10.0 * np.sin(i / 2.0), 5, 95)), 1) for i in range(14)]
            return dates, precip, probs

    dates_a, precip_a, probs_a = prep_daily(daily_a, risk_a, base_precip=20.0)
    dates_b, precip_b, probs_b = prep_daily(daily_b, risk_b, base_precip=18.0)

    fig = go.Figure()

    # Precipitation bars for Location A
    fig.add_trace(go.Bar(
        x=dates_a,
        y=precip_a,
        name=f"Rain: {name_a} (mm)",
        marker_color='rgba(56, 189, 248, 0.40)',
        marker_line=dict(color='#38BDF8', width=1),
        yaxis='y'
    ))

    # Precipitation bars for Location B
    fig.add_trace(go.Bar(
        x=dates_b,
        y=precip_b,
        name=f"Rain: {name_b} (mm)",
        marker_color='rgba(251, 146, 60, 0.40)',
        marker_line=dict(color='#FB923C', width=1),
        yaxis='y'
    ))

    # Risk curve for Location A
    fig.add_trace(go.Scatter(
        x=dates_a,
        y=probs_a,
        name=f"Risk %: {name_a}",
        mode='lines+markers',
        line=dict(color='#0284C7', width=3),
        marker=dict(size=6, color='#0284C7'),
        yaxis='y2'
    ))

    # Risk curve for Location B
    fig.add_trace(go.Scatter(
        x=dates_b,
        y=probs_b,
        name=f"Risk %: {name_b}",
        mode='lines+markers',
        line=dict(color='#F43F5E', width=3, dash='dot'),
        marker=dict(size=6, color='#F43F5E'),
        yaxis='y2'
    ))

    # Critical threshold line
    fig.add_hline(
        y=70,
        line_dash="dash",
        line_color="rgba(239, 68, 68, 0.8)",
        line_width=2,
        annotation_text="High Risk Threshold (70%)",
        annotation_position="top right",
        yref='y2',
        annotation_font=dict(color="#EF4444", size=10)
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Plus Jakarta Sans, sans-serif", color="#94A3B8"),
        xaxis=dict(
            title=dict(text="Forecast Date", font=dict(color="#CBD5E1")),
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
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="center",
            x=0.5,
            font=dict(color="#CBD5E1", size=11)
        ),
        height=380,
        margin=dict(l=40, r=40, t=30, b=30),
        hovermode="x unified"
    )

    return fig


def create_side_by_side_gauge(
    prob_val: float,
    title_text: str,
    color: str,
    classification: str
) -> go.Figure:
    """
    Generate an individual sleek radial gauge for side-by-side risk score display.
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob_val,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={'suffix': "%", 'font': {'size': 38, 'family': 'Plus Jakarta Sans', 'color': color}},
        title={'text': f"<b>{classification.upper()} RISK</b><br><span style='font-size:0.75em;color:#94A3B8'>{title_text}</span>", 'font': {'size': 16, 'color': '#E2E8F0'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': '#94A3B8', 'size': 10}},
            'bar': {'color': color, 'thickness': 0.28},
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

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=240,
        margin=dict(l=15, r=15, t=40, b=10),
        font={'family': 'Plus Jakarta Sans, sans-serif'}
    )

    return fig
