"""
=============================================================================
Verification Test: Citizen Field Geo-Tagged Reporting & Folium Photo Popups
=============================================================================
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import folium
from utils.citizen_reporting_service import (
    init_reporting_database,
    save_citizen_report,
    get_all_citizen_reports,
    get_photo_data_uri,
    get_severity_badge_color
)


def test_database_init_and_seeding():
    print("--- [1] Testing SQLite Database Initialization & Demo Seeding ---")
    init_reporting_database()
    reports = get_all_citizen_reports()
    assert len(reports) >= 3, f"Expected at least 3 pre-seeded demo reports, found {len(reports)}"
    
    first = reports[0]
    print(f"Verified report count: {len(reports)}")
    print(f"Sample report: {first['report_id']} - {first['location_name']} ({first['severity']})")
    
    # Verify fields
    assert "latitude" in first and "longitude" in first
    assert "photo_filename" in first
    assert "hazard_type" in first
    print("[OK] Database initialization and seeding passed.\n")


def test_save_and_retrieve_report():
    print("--- [2] Testing Save & Retrieve Citizen Field Report ---")
    # Generate fake image bytes (simple 100x100 PNG)
    from PIL import Image
    import io
    
    img = Image.new("RGB", (120, 80), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    fake_img_bytes = buf.getvalue()
    
    new_rep = save_citizen_report(
        latitude=27.3500,
        longitude=88.6100,
        location_name="Tadong Urban Slope",
        state="Sikkim",
        hazard_type="Slope Subsidence & Sinking",
        severity="Critical",
        description="Retaining wall sheared; tension cracks widening near residential building foundations.",
        reporter_name="Civil Defense Field Volunteer",
        image_bytes=fake_img_bytes
    )
    
    assert new_rep["location_name"] == "Tadong Urban Slope"
    assert new_rep["state"] == "Sikkim"
    print(f"Created report: {new_rep['report_id']}")
    
    # Check data URI generation
    data_uri = get_photo_data_uri(new_rep["photo_filename"])
    assert data_uri.startswith("data:image/jpeg;base64,"), "Data URI malformed"
    assert len(data_uri) > 100, "Base64 payload too small"
    print(f"Generated base64 photo data URI: {len(data_uri)} chars")
    print("[OK] Save and retrieve test passed.\n")


def test_folium_marker_with_photo_popup():
    print("--- [3] Testing Folium Photo Popup Compilation ---")
    reports = get_all_citizen_reports()
    m = folium.Map(location=[26.1, 92.9], zoom_start=7)
    citizen_fg = folium.FeatureGroup(name="📸 Citizen Field Reports (Geo-Tagged)", show=True)
    
    for r in reports[:3]:
        mcolor = get_severity_badge_color(r["severity"])
        photo_uri = get_photo_data_uri(r["photo_filename"])
        
        img_tag = f"<img src='{photo_uri}' style='width: 100%; max-height: 140px; object-fit: cover; border-radius: 6px; margin-bottom: 8px;' />" if photo_uri else ""
        
        popup_html = f"""
        <div style='font-family: sans-serif; font-size: 12px; line-height: 1.45; min-width: 220px; max-width: 260px;'>
            {img_tag}
            <div style='font-size: 11px; color: #64748B; margin-bottom: 2px;'>{r['timestamp']}</div>
            <b style='font-size: 13px; color: #0F172A;'>{r['location_name']}</b><br>
            <span style='color: #64748B;'>{r['state']}</span>
            <div style='margin: 6px 0; padding: 4px 8px; border-radius: 4px; background: {mcolor}18; border-left: 3px solid {mcolor};'>
                <b style='color: {mcolor};'>{r['severity'].upper()}</b> &bull; {r['hazard_type']}
            </div>
            <div style='font-size: 11px; color: #334155; margin-bottom: 6px;'>
                {r['description']}
            </div>
            <div style='font-size: 10px; color: #94A3B8; border-top: 1px solid #E2E8F0; padding-top: 4px;'>
                Reported by: <b>{r['reporter_name']}</b> &bull; GPS: {r['latitude']:.4f}°N, {r['longitude']:.4f}°E
            </div>
        </div>
        """
        
        folium.Marker(
            location=[r["latitude"], r["longitude"]],
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"📸 Citizen Report: {r['location_name']} ({r['severity']})",
            icon=folium.Icon(color="red" if "critical" in r["severity"].lower() else "orange", icon="camera", prefix="fa")
        ).add_to(citizen_fg)
        
    citizen_fg.add_to(m)
    folium.LayerControl().add_to(m)
    
    html = m._repr_html_()
    assert len(html) > 1000, "Folium HTML output too short"
    assert "data:image/jpeg;base64" in html, "Base64 image missing from compiled Folium HTML"
    print("Folium map cleanly rendered citizen report markers with embedded photo popups!")
    print("[OK] Folium photo popup compilation test passed.\n")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING CITIZEN FIELD REPORTING TEST SUITE")
    print("==================================================\n")
    test_database_init_and_seeding()
    test_save_and_retrieve_report()
    test_folium_marker_with_photo_popup()
    print("ALL TESTS PASSED SUCCESSFULLY! [PASS]")
