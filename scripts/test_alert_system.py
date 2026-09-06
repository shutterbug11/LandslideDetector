"""
=============================================================================
Verification Script: Hazard Early Warning Email Alerts & Spam Linter Test
=============================================================================
"""

import os
import sys

# Ensure parent directory is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.alert_service import (
    analyze_spam_risk,
    generate_alert_email_payload,
    send_smtp_email
)
from utils.subscription_service import (
    add_subscriber,
    remove_subscriber,
    load_subscribers,
    check_and_dispatch_alerts,
    validate_email_address
)
from utils.regional_data import SDMA_CONTACTS


def test_spam_linter():
    print("--- [1] Testing Spam Keyword Linter ---")
    
    # Test 1A: Safe scientific alert
    safe_subject = "GroundCheck Advisory: Landslide Risk Threshold Exceeded for Gangtok, Sikkim"
    safe_body = "This automated meteorological observation alert is issued for Gangtok. Cumulative 72-hour precipitation is 142.0 mm."
    res_safe = analyze_spam_risk(safe_subject, safe_body)
    print(f"Safe alert score: {res_safe['score']} / 100 ({res_safe['status']})")
    assert res_safe["score"] >= 90, f"Expected safe alert score >= 90, got {res_safe['score']}"
    assert res_safe["is_safe_to_send"] is True
    
    # Test 1B: Spammy marketing / panic subject
    spam_subject = "URGENT EMERGENCY ALERT: EVACUATE RIGHT NOW OR FACE CATASTROPHIC DEATH!!!"
    spam_body = "Click here to claim your 100% free disaster kit and update details immediately!!! Act now!"
    res_spam = analyze_spam_risk(spam_subject, spam_body)
    print(f"Spam alert score: {res_spam['score']} / 100 ({res_spam['status']})")
    print(f"Flagged warnings: {res_spam['warnings']}")
    assert res_spam["score"] < 70, f"Expected spam alert score < 70, got {res_spam['score']}"
    assert res_spam["is_safe_to_send"] is False
    print("[OK] Spam Keyword Linter passed.\n")


def test_subscription_storage():
    print("--- [2] Testing Subscription Management ---")
    
    test_email = "test.visitor.alert@groundcheck.test"
    test_state = "Sikkim"
    test_region = "Gangtok (East Sikkim)"
    
    # Cleanup beforehand
    remove_subscriber(test_email)
    
    # Add subscription
    res_add = add_subscriber(test_email, test_state, test_region, threshold=65.0)
    print("Add subscription response:", res_add["message"])
    assert res_add["status"] == "success"
    assert res_add["subscriber"]["threshold"] == 65.0
    
    # Verify loaded
    subs = load_subscribers()
    matching = [s for s in subs if s["email"] == test_email and s["region"] == test_region]
    assert len(matching) == 1, "Subscription was not saved properly"
    
    # Update subscription threshold
    res_up = add_subscriber(test_email, test_state, test_region, threshold=75.0)
    print("Update subscription response:", res_up["message"])
    assert res_up["action"] == "updated"
    assert res_up["subscriber"]["threshold"] == 75.0
    
    # Remove subscription
    res_rem = remove_subscriber(test_email)
    print("Remove subscription response:", res_rem["message"])
    assert res_rem["status"] == "success"
    
    subs_after = load_subscribers()
    matching_after = [s for s in subs_after if s["email"] == test_email]
    assert len(matching_after) == 0, "Subscription was not deleted properly"
    print("[OK] Subscription Management passed.\n")


def test_payload_generation():
    print("--- [3] Testing RFC Email Payload Generation ---")
    
    mock_risk = {
        "probability": 78.4,
        "classification": "High",
        "alert_level": "Critical Hazard Advisory - Evacuation Protocol",
        "thresholds": {"rain_24h": 72.0, "rain_72h": 165.0}
    }
    mock_weather = {
        "current": {"temperature": 17.5, "precipitation_rate": 5.2},
        "triggers": {
            "rain_past_24h": 72.0,
            "rain_past_72h": 165.0,
            "soil_moisture_top": 0.44,
            "soil_moisture_deep": 0.39
        }
    }
    sdma = SDMA_CONTACTS["Sikkim"]
    
    payload = generate_alert_email_payload(
        recipient_email="resident@sikkim.gov.in",
        location_title="Gangtok (East Sikkim)",
        state="Sikkim",
        risk_output=mock_risk,
        weather_data=mock_weather,
        sdma_contact=sdma,
        subscription_id="sub_test123"
    )
    
    assert "Gangtok (East Sikkim)" in payload["subject"]
    assert "78.4%" in payload["plain_text"]
    assert "<!DOCTYPE html>" in payload["html_body"]
    assert "1070" in payload["plain_text"]  # SDMA helpline
    print(f"Generated Subject: {payload['subject']}")
    
    # Check generated email against spam linter
    linter = analyze_spam_risk(payload["subject"], payload["plain_text"])
    print(f"Generated email deliverability score: {linter['score']} / 100")
    assert linter["score"] >= 90, "Generated email failed high-deliverability standard"
    print("[OK] Email Payload Generation passed.\n")


def test_threshold_dispatch_mock():
    print("--- [4] Testing Threshold Evaluation Logic ---")
    test_email = "observer@example.com"
    add_subscriber(test_email, "Sikkim", "Gangtok (East Sikkim)", threshold=70.0)
    
    # Case A: Risk is 50.0% (below 70.0% threshold)
    low_risk = {"probability": 50.0, "classification": "Medium", "alert_level": "Advisory"}
    sdma = SDMA_CONTACTS["Sikkim"]
    res_low = check_and_dispatch_alerts("Gangtok (East Sikkim)", "Sikkim", low_risk, {}, sdma)
    assert len(res_low) == 0, "Dispatched alert when risk was below threshold!"
    
    # Cleanup
    remove_subscriber(test_email)
    print("[OK] Threshold Evaluation passed.\n")


if __name__ == "__main__":
    print("==================================================")
    print("RUNNING GROUNDCHECK ALERT & ANTI-SPAM TEST SUITE")
    print("==================================================\n")
    test_spam_linter()
    test_subscription_storage()
    test_payload_generation()
    test_threshold_dispatch_mock()
    print("ALL TESTS PASSED SUCCESSFULLY! [PASS]")

