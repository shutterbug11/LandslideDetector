"""
=============================================================================
GroundCheck Early Warning System - Visitor Subscription & Alert Orchestrator
Persists and manages alert triggers for state and regional residents.
=============================================================================
"""

import os
import re
import json
import uuid
from datetime import datetime, timedelta
from utils.alert_service import generate_alert_email_payload, send_smtp_email

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
SUBSCRIBERS_FILE = os.path.join(OUTPUT_DIR, 'subscribers.json')

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def ensure_storage_exists():
    """Ensure the output directory and subscribers.json file exist."""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)


def validate_email_address(email: str) -> bool:
    """Validates basic email formatting."""
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def load_subscribers() -> list:
    """Loads the list of registered hazard alert subscribers."""
    ensure_storage_exists()
    try:
        with open(SUBSCRIBERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def save_subscribers(subscribers: list) -> bool:
    """Persists subscriber list to JSON storage."""
    ensure_storage_exists()
    try:
        with open(SUBSCRIBERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(subscribers, f, indent=2, default=str)
        return True
    except Exception:
        return False


def add_subscriber(email: str, state: str, region: str, threshold: float = 70.0) -> dict:
    """
    Registers a visitor for automated early warning alerts.
    If the email and region already exist, updates the threshold and state.
    """
    cleaned_email = email.strip().lower()
    if not validate_email_address(cleaned_email):
        return {
            "status": "error",
            "message": f"Invalid email format: '{email}'. Please provide a valid email address."
        }
        
    subscribers = load_subscribers()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Check for existing subscription for this email & region
    for sub in subscribers:
        if sub["email"].lower() == cleaned_email and sub["region"] == region:
            sub["state"] = state
            sub["threshold"] = round(float(threshold), 1)
            sub["updated_at"] = now_str
            save_subscribers(subscribers)
            return {
                "status": "success",
                "action": "updated",
                "message": f"Updated existing subscription for {cleaned_email} in {region} (Threshold: {threshold:.0f}%).",
                "subscriber": sub
            }
            
    # New Subscription
    new_sub = {
        "id": f"sub_{uuid.uuid4().hex[:8]}",
        "email": cleaned_email,
        "state": state,
        "region": region,
        "threshold": round(float(threshold), 1),
        "created_at": now_str,
        "last_alert_sent_at": None,
        "last_alert_risk": None
    }
    subscribers.append(new_sub)
    save_subscribers(subscribers)
    
    return {
        "status": "success",
        "action": "created",
        "message": f"Successfully subscribed {cleaned_email} for hazard alerts in {region} at threshold {threshold:.0f}%.",
        "subscriber": new_sub
    }


def remove_subscriber(email: str, region: str = None) -> dict:
    """
    Unsubscribes a visitor from hazard alerts.
    If region is None, removes all subscriptions for that email.
    """
    cleaned_email = email.strip().lower()
    subscribers = load_subscribers()
    initial_len = len(subscribers)
    
    if region:
        subscribers = [s for s in subscribers if not (s["email"].lower() == cleaned_email and s["region"] == region)]
    else:
        subscribers = [s for s in subscribers if s["email"].lower() != cleaned_email]
        
    removed_count = initial_len - len(subscribers)
    if removed_count > 0:
        save_subscribers(subscribers)
        return {
            "status": "success",
            "message": f"Successfully unsubscribed {cleaned_email} ({removed_count} subscription(s) removed)."
        }
    else:
        return {
            "status": "warning",
            "message": f"No active subscription found for email '{cleaned_email}'."
        }


def get_subscribers_for_region(region_title: str) -> list:
    """Retrieves all active subscribers registered for a specific hotspot/region."""
    subscribers = load_subscribers()
    return [s for s in subscribers if s.get("region") == region_title]


def check_and_dispatch_alerts(
    region_title: str,
    state_name: str,
    risk_output: dict,
    weather_data: dict,
    sdma_contact: dict,
    cooldown_hours: float = 6.0
) -> list:
    """
    Evaluates current predicted risk against all registered subscribers for this region.
    If risk >= threshold, dispatches email alert unless throttled by cooldown.
    
    Returns list of dispatch result dicts.
    """
    current_risk_prob = float(risk_output.get("probability", 0.0))
    current_classification = risk_output.get("classification", "Low")
    
    subscribers = load_subscribers()
    relevant_subs = [s for s in subscribers if s.get("region") == region_title]
    
    if not relevant_subs:
        return []
        
    results = []
    updated_subs = False
    now = datetime.now()
    
    for sub in relevant_subs:
        threshold = float(sub.get("threshold", 70.0))
        
        # Check if risk exceeds visitor's threshold
        if current_risk_prob >= threshold:
            last_sent_str = sub.get("last_alert_sent_at")
            last_risk = sub.get("last_alert_risk")
            
            should_send = True
            if last_sent_str:
                try:
                    last_sent_dt = datetime.strptime(last_sent_str, "%Y-%m-%d %H:%M:%S")
                    hours_elapsed = (now - last_sent_dt).total_seconds() / 3600.0
                    
                    # Cooldown logic: enforce interval unless risk escalated dramatically
                    if hours_elapsed < cooldown_hours:
                        if current_classification == "High" and (last_risk is None or last_risk < 70.0):
                            # Risk escalated from Medium to High -> bypass cooldown
                            should_send = True
                        else:
                            should_send = False
                            results.append({
                                "email": sub["email"],
                                "status": "throttled",
                                "message": f"Alert throttled for {sub['email']} (Last sent {hours_elapsed:.1f}h ago; cooldown is {cooldown_hours}h)"
                            })
                except Exception:
                    should_send = True
                    
            if should_send:
                payload = generate_alert_email_payload(
                    recipient_email=sub["email"],
                    location_title=region_title,
                    state=state_name,
                    risk_output=risk_output,
                    weather_data=weather_data,
                    sdma_contact=sdma_contact,
                    subscription_id=sub.get("id", "sub_generic")
                )
                
                dispatch_res = send_smtp_email(
                    to_email=sub["email"],
                    subject=payload["subject"],
                    text_body=payload["plain_text"],
                    html_body=payload["html_body"],
                    subscription_id=sub.get("id", "sub_generic")
                )
                
                if dispatch_res.get("status") == "success":
                    sub["last_alert_sent_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    sub["last_alert_risk"] = current_risk_prob
                    updated_subs = True
                    
                results.append({
                    "email": sub["email"],
                    "status": dispatch_res.get("status"),
                    "message": dispatch_res.get("message"),
                    "deliverability_score": dispatch_res.get("deliverability_score")
                })
                
    if updated_subs:
        # Save updated alert timestamps
        save_subscribers(subscribers)
        
    return results
