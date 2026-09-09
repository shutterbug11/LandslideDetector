"""
=============================================================================
Citizen & Field Geo-Tagged Reporting Service
SQLite Database Storage + Local Media Management + Folium Photo Popups
=============================================================================
"""

import os
import io
import uuid
import base64
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
DB_PATH = os.path.join(OUTPUT_DIR, 'citizen_reports.db')
PHOTOS_DIR = os.path.join(OUTPUT_DIR, 'report_photos')


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict-like row access."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_reporting_database() -> None:
    """Initializes SQLite table and pre-seeds realistic demo field reports if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizen_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id TEXT UNIQUE NOT NULL,
        timestamp TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        location_name TEXT NOT NULL,
        state TEXT NOT NULL,
        hazard_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        description TEXT,
        reporter_name TEXT,
        photo_filename TEXT,
        status TEXT DEFAULT 'Verified Hazard'
    )
    """)
    conn.commit()
    
    # Check if table is empty, seed demo reports
    cursor.execute("SELECT COUNT(*) FROM citizen_reports")
    count = cursor.fetchone()[0]
    
    if count == 0:
        _seed_demo_reports(conn)
        
    conn.close()


def _create_demo_photo(filename: str, title: str, subtitle: str, color_hex: str) -> str:
    """Generates an illustrative realistic field photo for demonstration."""
    os.makedirs(PHOTOS_DIR, exist_ok=True)
    photo_path = os.path.join(PHOTOS_DIR, filename)
    if os.path.exists(photo_path):
        return filename
        
    width, height = 480, 320
    # Gradient background simulating landslide slope/rockfall
    img = Image.new("RGB", (width, height), color=(30, 41, 59))
    draw = ImageDraw.Draw(img)
    
    # Draw stylized mountainous slope
    draw.polygon([(0, 180), (140, 90), (320, 140), (480, 60), (480, 320), (0, 320)], fill=(71, 85, 105))
    draw.polygon([(0, 240), (160, 160), (300, 210), (480, 150), (480, 320), (0, 320)], fill=(51, 65, 85))
    
    # Draw rock debris & mudslide slip surface
    draw.polygon([(80, 240), (220, 190), (280, 260), (120, 310)], fill=(120, 53, 15))
    draw.ellipse([(140, 210), (180, 240)], fill=(180, 83, 9))
    draw.ellipse([(200, 220), (250, 255)], fill=(146, 64, 14))
    draw.ellipse([(100, 260), (160, 295)], fill=(217, 119, 6))
    
    # Header overlay bar
    draw.rectangle([(0, 0), (width, 50)], fill=(15, 23, 42, 220))
    draw.rectangle([(0, 48), (width, 52)], fill=(239, 68, 68) if "Critical" in color_hex else (245, 158, 11))
    
    # Text labels
    draw.text((15, 12), f"FIELD REPORT: {title.upper()}", fill=(255, 255, 255))
    draw.text((15, 28), subtitle, fill=(148, 163, 184))
    
    # Timestamp stamp at bottom right
    draw.rectangle([(width - 190, height - 30), (width - 10, height - 8)], fill=(15, 23, 42))
    draw.text((width - 180, height - 26), "GEO-TAGGED OBSERVER", fill=(56, 189, 248))
    
    img.save(photo_path, format="JPEG", quality=85)
    return filename


def _seed_demo_reports(conn: sqlite3.Connection) -> None:
    """Pre-seeds 3 realistic demo field reports across North East India."""
    demo_data = [
        {
            "report_id": "CR-SKM-2026-001",
            "timestamp": "2026-09-08 14:25 IST",
            "latitude": 27.2345,
            "longitude": 88.5021,
            "location_name": "NH-10 Corridor (Singtam-Rangpo Section)",
            "state": "Sikkim",
            "hazard_type": "Active Debris Slide & Boulders",
            "severity": "Critical",
            "description": "Massive debris flow following intense monsoon rain; highway blocked both directions. Active rockfalls ongoing from upper quartzitic cut-slope.",
            "reporter_name": "BRO Patrol Crew (Unit 84)",
            "photo_filename": "demo_sikkim_nh10.jpg",
            "title": "NH-10 Debris Flow Blockage",
            "subtitle": "Teesta River Valley Corridor - KM 48.2"
        },
        {
            "report_id": "CR-MEG-2026-002",
            "timestamp": "2026-09-08 17:40 IST",
            "latitude": 25.2890,
            "longitude": 91.7180,
            "location_name": "Cherrapunji / Sohra Gorge Escarpment",
            "state": "Meghalaya",
            "hazard_type": "Escarpment Rockfall & Mudslide",
            "severity": "High",
            "description": "Heavy water saturation caused deep rotational slope cracks; limestone scarp debris encroaching village access road and drainage culvert.",
            "reporter_name": "Trekking Guide & Eco-Tourism Field Observer",
            "photo_filename": "demo_meghalaya_sohra.jpg",
            "title": "Sohra Escarpment Rockfall",
            "subtitle": "East Khasi Hills Valley Scarp"
        },
        {
            "report_id": "CR-ASM-2026-003",
            "timestamp": "2026-09-09 09:15 IST",
            "latitude": 25.1812,
            "longitude": 93.0185,
            "location_name": "Haflong Hill Cut (Dima Hasao)",
            "state": "Assam",
            "hazard_type": "Slope Subsidence & Sinking",
            "severity": "Moderate",
            "description": "Lateral tension cracks observed propagating across road verge; minor mudflow accumulating on shoulder after prolonged 48h drizzle.",
            "reporter_name": "State Highway Patrol Inspector",
            "photo_filename": "demo_assam_haflong.jpg",
            "title": "Haflong Hill Subsidence",
            "subtitle": "Barail Range Arterial Link"
        }
    ]
    
    cursor = conn.cursor()
    for item in demo_data:
        _create_demo_photo(item["photo_filename"], item["title"], item["subtitle"], item["severity"])
        cursor.execute("""
        INSERT INTO citizen_reports (
            report_id, timestamp, latitude, longitude, location_name,
            state, hazard_type, severity, description, reporter_name, photo_filename, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["report_id"], item["timestamp"], item["latitude"], item["longitude"],
            item["location_name"], item["state"], item["hazard_type"], item["severity"],
            item["description"], item["reporter_name"], item["photo_filename"], "Verified Hazard"
        ))
    conn.commit()


def save_citizen_report(
    latitude: float,
    longitude: float,
    location_name: str,
    state: str,
    hazard_type: str,
    severity: str,
    description: str,
    reporter_name: str = "Anonymous Citizen",
    image_bytes: Optional[bytes] = None
) -> Dict[str, Any]:
    """
    Saves an uploaded/captured photo to disk and inserts the record into SQLite.
    Returns the created report record dict.
    """
    init_reporting_database()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    report_id = f"CR-{state[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M IST")
    photo_filename = f"{report_id}.jpg"
    photo_path = os.path.join(PHOTOS_DIR, photo_filename)
    
    # Process & optimize image
    if image_bytes:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Resize max 960x720 while maintaining aspect ratio
            img.thumbnail((960, 720), Image.Resampling.LANCZOS)
            img.save(photo_path, format="JPEG", quality=85)
        except Exception as e:
            # Fallback: write bytes directly
            with open(photo_path, "wb") as f:
                f.write(image_bytes)
    else:
        # Generate placeholder image
        _create_demo_photo(photo_filename, location_name, f"GPS: {latitude:.3f}°N, {longitude:.3f}°E", severity)
        
    cursor.execute("""
    INSERT INTO citizen_reports (
        report_id, timestamp, latitude, longitude, location_name,
        state, hazard_type, severity, description, reporter_name, photo_filename, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        report_id, timestamp_str, float(latitude), float(longitude),
        location_name, state, hazard_type, severity,
        description, reporter_name, photo_filename, "Pending Verification"
    ))
    conn.commit()
    conn.close()
    
    return {
        "report_id": report_id,
        "timestamp": timestamp_str,
        "latitude": latitude,
        "longitude": longitude,
        "location_name": location_name,
        "state": state,
        "hazard_type": hazard_type,
        "severity": severity,
        "description": description,
        "reporter_name": reporter_name,
        "photo_filename": photo_filename,
        "status": "Pending Verification"
    }


def get_all_citizen_reports() -> List[Dict[str, Any]]:
    """Retrieves all citizen field reports ordered chronologically by submission."""
    init_reporting_database()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM citizen_reports ORDER BY id DESC")
    rows = cursor.fetchall()
    
    reports = []
    for r in rows:
        reports.append({
            "id": r["id"],
            "report_id": r["report_id"],
            "timestamp": r["timestamp"],
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "location_name": r["location_name"],
            "state": r["state"],
            "hazard_type": r["hazard_type"],
            "severity": r["severity"],
            "description": r["description"],
            "reporter_name": r["reporter_name"],
            "photo_filename": r["photo_filename"],
            "status": r["status"]
        })
    conn.close()
    return reports


def get_photo_data_uri(photo_filename: str) -> str:
    """
    Encodes stored image into base64 data URI format (e.g. data:image/jpeg;base64,...).
    Ensures safe, instantaneous rendering inside Leaflet / Folium iframe popups.
    """
    if not photo_filename:
        return ""
    photo_path = os.path.join(PHOTOS_DIR, photo_filename)
    if not os.path.exists(photo_path):
        return ""
    try:
        with open(photo_path, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64_str}"
    except Exception:
        return ""


def get_severity_badge_color(severity: str) -> str:
    """Returns color associated with report hazard severity."""
    sev = severity.lower()
    if "critical" in sev or "severe" in sev:
        return "#EF4444"
    elif "moderate" in sev or "high" in sev:
        return "#F59E0B"
    else:
        return "#10B981"
