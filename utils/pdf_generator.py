"""
PDF Report Generator for Landslide Early Warning System.
Generates an executive-grade, concise hazard assessment report in PDF format.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable


def generate_landslide_pdf_report(
    location_title: str,
    target_state: str,
    target_lat: float,
    target_lon: float,
    terrain_profile: dict,
    target_geology: str,
    target_notes: str,
    risk_output: dict,
    weather_res: dict,
    sdma_contact: dict
) -> bytes:
    """
    Generate an in-memory PDF report buffer for the current location's hazard analysis.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0F172A")
    secondary_color = colors.HexColor("#334155")
    accent_blue = colors.HexColor("#0284C7")
    slate_bg = colors.HexColor("#F8FAFC")
    border_color = colors.HexColor("#E2E8F0")

    # Risk badge color
    risk_tier = risk_output.get("classification", "Low").upper()
    if risk_tier == "HIGH":
        badge_bg = colors.HexColor("#FEE2E2")
        badge_text_color = colors.HexColor("#B91C1C")
        badge_border = colors.HexColor("#EF4444")
    elif risk_tier == "MEDIUM":
        badge_bg = colors.HexColor("#FEF3C7")
        badge_text_color = colors.HexColor("#B45309")
        badge_border = colors.HexColor("#F59E0B")
    else:
        badge_bg = colors.HexColor("#D1FAE5")
        badge_text_color = colors.HexColor("#047857")
        badge_border = colors.HexColor("#10B981")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        "DocSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#64748B")
    )

    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=primary_color,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11.5,
        textColor=secondary_color
    )

    bold_body_style = ParagraphStyle(
        "BoldBody",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11.5,
        textColor=primary_color
    )

    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=13,
        alignment=1,
        textColor=badge_text_color
    )

    # 1. Header Banner
    now_str = datetime.now().strftime("%d %B %Y, %H:%M IST")
    header_table_data = [
        [
            Paragraph("<b>NORTH EASTERN REGION LANDSLIDE OBSERVATORY</b><br/><font color='#0284C7'>HAZARD ASSESSMENT & EARLY WARNING TECHNICAL REPORT</font>", title_style),
            Paragraph(f"<b>REPORT ISSUED:</b><br/>{now_str}<br/><b>REF ID:</b> NER-LSM-{int(datetime.now().timestamp())}", subtitle_style)
        ]
    ]
    header_table = Table(header_table_data, colWidths=[4.2 * inch, 3.3 * inch])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_blue, spaceAfter=10))

    # 2. Executive Risk Summary Block
    prob_val = risk_output.get("probability", 0.0)
    alert_text = risk_output.get("alert_level", "Standard Monitoring")
    ml_prob = risk_output.get("ml_probability", 0.0)

    risk_box_data = [
        [
            Paragraph(f"<b>TARGET LOCATION:</b><br/><b><font size='13'>{location_title}</font></b><br/>{target_state}, India ({target_lat:.4f}°N, {target_lon:.4f}°E)", body_style),
            Paragraph(f"<b>HAZARD LEVEL</b><br/>{risk_tier} RISK", badge_style),
            Paragraph(f"<b>LANDSLIDE PROBABILITY</b><br/><b><font size='16'>{prob_val}%</font></b><br/>Ensemble Geo-Hydrological", body_style)
        ],
        [
            Paragraph(f"<b>Advisory Status:</b> {alert_text}", bold_body_style),
            Paragraph("", body_style),
            Paragraph(f"<b>ML Geomorphic Baseline:</b> {ml_prob}%", body_style)
        ]
    ]
    risk_box = Table(risk_box_data, colWidths=[3.2 * inch, 2.0 * inch, 2.3 * inch])
    risk_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), slate_bg),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('BACKGROUND', (1, 0), (1, 0), badge_bg),
        ('BOX', (1, 0), (1, 0), 1.5, badge_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('SPAN', (0, 1), (1, 1)),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(risk_box)
    story.append(Spacer(1, 12))

    # 3. Terrain & Geological Profile + Real-Time Telemetry Side-by-Side
    elevation = terrain_profile.get("elevation", 0)
    slope = terrain_profile.get("slope", 0)
    aspect = terrain_profile.get("aspect", 0)
    twi = terrain_profile.get("twi", 0)
    tri = terrain_profile.get("tri", 0)

    triggers = weather_res.get("triggers", {})
    curr = weather_res.get("current", {})

    geo_data = [
        [Paragraph("<b>GEOMORPHIC & LITHOLOGICAL PROFILE</b>", h2_style), Paragraph("<b>HYDROMETEOROLOGICAL TELEMETRY</b>", h2_style)],
        [
            Paragraph(f"""
            <b>Elevation Relief:</b> {elevation:,} m a.s.l.<br/>
            <b>Slope Gradient:</b> {slope}° (Failure threshold: &gt;35°)<br/>
            <b>Slope Aspect:</b> {aspect}°<br/>
            <b>Topographic Wetness (TWI):</b> {twi}<br/>
            <b>Terrain Ruggedness (TRI):</b> {tri}<br/>
            <b>Geological Unit:</b> <i>{target_geology}</i><br/>
            <b>Corridor Notes:</b> {target_notes}
            """, body_style),
            Paragraph(f"""
            <b>Ambient Temperature:</b> {curr.get('temperature', 0):.1f} °C (Feels like: {curr.get('apparent_temperature', 0):.1f} °C)<br/>
            <b>Relative Humidity:</b> {curr.get('humidity', 0):.0f}%<br/>
            <b>Current Precipitation Rate:</b> {curr.get('precipitation_rate', 0):.1f} mm/h<br/>
            <b>24h Cumulative Rainfall:</b> <b>{triggers.get('rain_past_24h', 0):.1f} mm</b><br/>
            <b>48h Cumulative Rainfall:</b> <b>{triggers.get('rain_past_48h', 0):.1f} mm</b><br/>
            <b>72h Cumulative Rainfall:</b> <b>{triggers.get('rain_past_72h', 0):.1f} mm</b><br/>
            <b>7-Day Antecedent Total:</b> {triggers.get('rain_past_7d', 0):.1f} mm
            """, body_style)
        ]
    ]
    geo_table = Table(geo_data, colWidths=[3.75 * inch, 3.75 * inch])
    geo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#F1F5F9")),
        ('BACKGROUND', (1, 0), (1, 0), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(geo_table)
    story.append(Spacer(1, 10))

    # 4. Multi-Horizon Subsurface Soil Moisture Breakdown
    story.append(Paragraph("<b>SUBSURFACE SOIL MOISTURE SATURATION PROFILE</b>", h2_style))
    hourly_df = weather_res.get("hourly_df", None)
    latest = hourly_df.iloc[-1] if (hourly_df is not None and not hourly_df.empty) else {}

    s_0_1 = latest.get("soil_moisture_0_to_1cm", 0.25)
    s_1_3 = latest.get("soil_moisture_1_to_3cm", 0.26)
    s_3_9 = latest.get("soil_moisture_3_to_9cm", 0.27)
    s_9_27 = latest.get("soil_moisture_9_to_27cm", 0.29)
    s_27_81 = latest.get("soil_moisture_27_to_81cm", 0.31)

    soil_table_data = [
        ["Soil Depth Horizon", "Volumetric Moisture", "Saturation %", "Status Relative to Liquefaction (0.40 m³/m³)"],
        ["Surface Layer (0 - 1 cm)", f"{s_0_1:.3f} m³/m³", f"{s_0_1*100:.1f}%", "Saturated" if s_0_1 >= 0.38 else ("Elevated" if s_0_1 >= 0.30 else "Normal")],
        ["Topsoil Horizon (1 - 3 cm)", f"{s_1_3:.3f} m³/m³", f"{s_1_3*100:.1f}%", "Saturated" if s_1_3 >= 0.38 else ("Elevated" if s_1_3 >= 0.30 else "Normal")],
        ["Root Zone (3 - 9 cm)", f"{s_3_9:.3f} m³/m³", f"{s_3_9*100:.1f}%", "Saturated" if s_3_9 >= 0.38 else ("Elevated" if s_3_9 >= 0.30 else "Normal")],
        ["Mid Stratum (9 - 27 cm)", f"{s_9_27:.3f} m³/m³", f"{s_9_27*100:.1f}%", "Saturated" if s_9_27 >= 0.38 else ("Elevated" if s_9_27 >= 0.30 else "Normal")],
        ["Bedrock Interface (27 - 81 cm)", f"{s_27_81:.3f} m³/m³", f"{s_27_81*100:.1f}%", "Critical Saturation" if s_27_81 >= 0.38 else ("High Pore Pressure" if s_27_81 >= 0.32 else "Stable")]
    ]
    soil_table = Table(soil_table_data, colWidths=[2.3 * inch, 1.6 * inch, 1.4 * inch, 2.2 * inch])
    soil_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (1, 0), (2, -1), 'CENTER'),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, slate_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(soil_table)
    story.append(Spacer(1, 10))

    # 5. Risk Factor Attribution Table
    story.append(Paragraph("<b>PRIMARY HAZARD DRIVERS & WEIGHT ATTRIBUTION</b>", h2_style))
    drivers = risk_output.get("drivers", [])
    driver_table_data = [["Hazard Factor", "Recorded Metric", "Model Weight Attribution (%)"]]
    for d in drivers:
        driver_table_data.append([d.get("factor", ""), d.get("value", ""), f"{d.get('contribution', 0.0)}%"])

    driver_table = Table(driver_table_data, colWidths=[3.2 * inch, 2.1 * inch, 2.2 * inch])
    driver_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('BOX', (0, 0), (-1, -1), 1, border_color),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, slate_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(driver_table)
    story.append(Spacer(1, 10))

    # 6. Emergency Contacts & NDMA Protocol
    story.append(Paragraph("<b>EMERGENCY RESPONSE PROTOCOLS & AUTHORITIES</b>", h2_style))
    agency_name = sdma_contact.get("dept", "State Disaster Management Authority")
    helpline = sdma_contact.get("helpline", "1070")
    phone = sdma_contact.get("phone", "N/A")

    emergency_data = [
        [
            Paragraph(f"""
            <b>Authorized State Agency:</b> {agency_name}<br/>
            <b>State Disaster Helpline (Toll-Free):</b> <b>{helpline}</b><br/>
            <b>Emergency Operation Centre:</b> {phone}<br/>
            <b>National Emergency / NDRF:</b> <b>112 / 1078</b>
            """, body_style),
            Paragraph("""
            <b>Standard Action Directives:</b><br/>
            • <b>High Hazard:</b> Immediate evacuation of active gully channels and toe-cut slopes.<br/>
            • <b>Moderate Hazard:</b> Inspect tensile soil cracks; restrict mountain highway travel.<br/>
            • <b>Low Hazard:</b> Standard vigilance; maintain drainage channel clear of debris.
            """, body_style)
        ]
    ]
    em_table = Table(emergency_data, colWidths=[3.75 * inch, 3.75 * inch])
    em_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF2F2") if risk_tier == "HIGH" else slate_bg),
        ('BOX', (0, 0), (-1, -1), 1, badge_border if risk_tier == "HIGH" else border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(em_table)
    story.append(Spacer(1, 10))

    # 7. Document Footer Note
    footer_text = (
        "<i>Disclaimer: This hazard advisory is generated by the NE India Landslide Early Warning System using "
        "satellite telemetry (Open-Meteo) combined with a LightGBM geomorphic susceptibility model trained on "
        "Sentinel-1/2 geospatial datasets. For binding executive evacuation orders, consult the district administration.</i>"
    )
    story.append(Paragraph(footer_text, subtitle_style))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
