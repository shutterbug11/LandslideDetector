"""
=============================================================================
GroundCheck Early Warning System - Alert Dispatch & Deliverability Service
Compliant with Gmail 2024 Bulk Sender Standards & SpamAssassin Heuristics
=============================================================================
"""

import os
import re
import socket
import smtplib
from datetime import datetime
from email.message import EmailMessage
from email.utils import make_msgid, formatdate

# Default SMTP Configuration (Can be overridden via environment variables)
DEFAULT_SMTP_HOST = os.getenv("ALERT_SMTP_HOST", "smtp.gmail.com")
DEFAULT_SMTP_PORT = int(os.getenv("ALERT_SMTP_PORT", 587))
DEFAULT_EMAIL_USER = os.getenv("ALERT_EMAIL_USER", "groundcheckalert@gmail.com")
DEFAULT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD", "groundcheck$2006")
DEFAULT_SENDER_NAME = "GroundCheck Observatory Alerts"

# =============================================================================
# SPAM FILTER KNOWLEDGE BASE & LINTER RULES
# =============================================================================
# Curated trigger terms categorized by Bayesian spam detection severity
SPAM_TRIGGER_TAXONOMY = {
    "urgency": [
        "urgent!!!", "act now", "immediate action required", "don't delay",
        "time is running out", "critical emergency alert!!!", "disaster imminent",
        "attention required right now", "call right now", "evacuate or die",
        "deadly danger", "hurry up", "fatal warning", "extreme panic"
    ],
    "commercial": [
        "free", "100% free", "guaranteed", "risk-free", "risk free",
        "click here", "exclusive offer", "special deal", "save now",
        "winner", "order now", "no cost", "best price", "earn money"
    ],
    "phishing": [
        "verify your account", "update details immediately", "security alert",
        "confirm your identity", "reset password", "login required",
        "account suspended", "billing notification"
    ]
}


def analyze_spam_risk(subject: str, body_text: str) -> dict:
    """
    Evaluates email subject and body against the Gmail Anti-Spam Knowledge Base.
    Computes a composite Deliverability Score (0 to 100) and returns flagged tokens.
    
    Scoring:
    - 90 - 100: Optimal Deliverability (High inbox confidence)
    - 70 - 89: Minor Advisory (Some wording or formatting could be refined)
    - < 70: High Spam Risk (Flagged keywords, excessive caps, or aggressive punctuation)
    """
    score = 100
    flagged_terms = []
    warnings = []
    
    combined_text = f"{subject} {body_text}".lower()
    
    # 1. Check for trigger terms from knowledge base with word-boundary accuracy
    for category, terms in SPAM_TRIGGER_TAXONOMY.items():
        for term in terms:
            # Avoid false positives like 'toll-free' or 'freeze' matching 'free'
            if term == "free":
                pattern = r'(?<!toll-)(?<!smoke-)\bfree\b'
            elif re.search(r'^\w.*\w$', term):
                pattern = r'\b' + re.escape(term) + r'\b'
            else:
                pattern = re.escape(term)
                
            if re.search(pattern, combined_text, re.IGNORECASE):
                penalty = 15 if category == "urgency" else 20
                score -= penalty
                flagged_terms.append({"term": term, "category": category, "penalty": penalty})
                warnings.append(f"Flagged '{term}' ({category} trigger, -{penalty} pts)")
                
    # 2. Check for repetitive exclamation marks or question marks
    exclamation_clusters = re.findall(r'!{2,}|\?{2,}|\${2,}', subject + " " + body_text)
    if exclamation_clusters:
        score -= 15
        warnings.append(f"Punctuation clustering detected: {exclamation_clusters[:3]} (-15 pts)")
        
    # 3. Check for excessive uppercase characters in subject
    if len(subject) > 0:
        uppercase_ratio_subj = sum(1 for c in subject if c.isupper()) / len(subject)
        if uppercase_ratio_subj > 0.35:
            score -= 20
            warnings.append(f"Subject has high uppercase ratio ({uppercase_ratio_subj*100:.0f}% > 35%, -20 pts)")

        
    score = max(0, min(100, score))
    
    status = "Optimal" if score >= 90 else ("Advisory" if score >= 70 else "High Spam Risk")
    
    return {
        "score": score,
        "status": status,
        "flagged_terms": flagged_terms,
        "warnings": warnings,
        "is_safe_to_send": score >= 70
    }


# =============================================================================
# EMAIL CONTENT GENERATOR (RFC-COMPLIANT MULTIPART)
# =============================================================================
def generate_alert_email_payload(
    recipient_email: str,
    location_title: str,
    state: str,
    risk_output: dict,
    weather_data: dict,
    sdma_contact: dict,
    subscription_id: str = "sub_default"
) -> dict:
    """
    Constructs an authoritative, scientific early-warning email payload
    adhering strictly to anti-spam vocabulary guidelines.
    Returns subject, plain-text body, and responsive HTML body.
    """
    prob = risk_output.get("probability", 70.0)
    classification = risk_output.get("classification", "High")
    alert_level = risk_output.get("alert_level", "Critical Hazard Advisory")
    
    triggers = weather_data.get("triggers", {}) if weather_data else {}
    curr = weather_data.get("current", {}) if weather_data else {}
    
    rain_24h = triggers.get("rain_past_24h", 0.0)
    rain_72h = triggers.get("rain_past_72h", 0.0)
    soil_top = triggers.get("soil_moisture_top", 0.25) * 100.0
    soil_deep = triggers.get("soil_moisture_deep", 0.30) * 100.0
    temp = curr.get("temperature", 20.0)
    rain_rate = curr.get("precipitation_rate", 0.0)
    
    now_str = datetime.now().strftime("%d %B %Y, %I:%M %p IST")
    
    # 1. Formulate Spam-Safe Subject Line
    # Avoid: ALL CAPS, exclamation points, words like URGENT or EMERGENCY
    subject = f"GroundCheck Advisory: Landslide Risk Threshold Exceeded for {location_title}, {state}"
    
    # 2. Formulate Plain-Text Alternative (RFC 5322)
    plain_text = f"""GroundCheck Observatory - Geomorphic Early Warning System
Scientific Hazard Advisory for {location_title}, {state}
Issued: {now_str}
======================================================================

ADVISORY STATUS: {classification.upper()} RISK ({prob:.1f}% Probability)
Classification: {alert_level}

Real-time hydrometeorological telemetry for {location_title} has surpassed
your designated early warning threshold.

METEOROLOGICAL & STABILITY TELEMETRY:
- 24-Hour Cumulative Rainfall: {rain_24h:.1f} mm
- 72-Hour Cumulative Rainfall: {rain_72h:.1f} mm
- Current Precipitation Rate: {rain_rate:.1f} mm/h
- Topsoil Moisture Saturation (0-9 cm): {soil_top:.1f}%
- Subsurface Deep Saturation (27-81 cm): {soil_deep:.1f}%
- Ambient Surface Temperature: {temp:.1f} °C

RECOMMENDED PRECAUTIONARY PROTOCOLS:
1. Exercise heightened vigilance near steep natural slopes and highway cuts.
2. Observe local drainage channels for unusual siltation, mudflow, or sudden blockages.
3. Keep emergency communication channels accessible.
4. Adhere strictly to local District Magistrate and SDMA civil advisories.

AUTHORIZED STATE DISASTER MANAGEMENT AUTHORITY ({state}):
- Operating Agency: {sdma_contact.get('dept', 'Disaster Management Division')}
- State Emergency Helpline (Toll-Free): {sdma_contact.get('helpline', '1070')}
- Direct Control Room Telephone: {sdma_contact.get('phone', 'N/A')}
- National Disaster Response Force (NDRF): 1078 / 112

======================================================================
SUBSCRIPTION MANAGEMENT & TRANSPARENCY:
You received this automated notification because this email ({recipient_email})
was enrolled in the GroundCheck Observatory Early Warning Registry for {location_title}.
Subscription Reference: {subscription_id}

To pause or update your warning preferences:
Reply with 'Unsubscribe' in the subject line or manage preferences via GroundCheck.
GroundCheck Observatory | North Eastern Himalayan Disaster Risk Reduction
"""

    # 3. Formulate Responsive HTML Body (Clean, professional, high text-to-code ratio)
    accent_color = "#EF4444" if classification == "High" else ("#F59E0B" if classification == "Medium" else "#10B981")
    
    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #E2E8F0;">
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #0F172A; padding: 24px 12px;">
        <tr>
            <td align="center">
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #1E293B; border-radius: 12px; border: 1px solid #334155; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.3);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #0F172A; padding: 20px 28px; border-bottom: 1px solid #334155;">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td>
                                        <div style="font-size: 11px; font-weight: 700; color: #38BDF8; letter-spacing: 0.1em; text-transform: uppercase;">GroundCheck Observatory</div>
                                        <div style="font-size: 18px; font-weight: 700; color: #FFFFFF; margin-top: 4px;">North Eastern Himalayan Landslide Early Warning</div>
                                    </td>
                                    <td align="right">
                                        <span style="display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3);">STATION TELEMETRY</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Advisory Banner -->
                    <tr>
                        <td style="padding: 24px 28px 16px 28px;">
                            <div style="background-color: rgba(15, 23, 42, 0.6); border-left: 4px solid {accent_color}; border-radius: 6px; padding: 16px 20px;">
                                <div style="font-size: 11px; font-weight: 700; color: {accent_color}; letter-spacing: 0.08em; text-transform: uppercase;">
                                    {classification.upper()} RISK ADVISORY ISSUED
                                </div>
                                <div style="font-size: 22px; font-weight: 800; color: #FFFFFF; margin-top: 4px;">
                                    {location_title}
                                </div>
                                <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                                    State: <b>{state}</b> &bull; Issued: {now_str}
                                </div>
                                <div style="margin-top: 14px; font-size: 28px; font-weight: 800; color: {accent_color};">
                                    {prob:.1f}% <span style="font-size: 14px; font-weight: 500; color: #94A3B8;">Landslide Probability</span>
                                </div>
                                <div style="font-size: 13px; color: #CBD5E1; margin-top: 4px;">
                                    {alert_level}
                                </div>
                            </div>
                        </td>
                    </tr>

                    <!-- Telemetry Metrics Grid -->
                    <tr>
                        <td style="padding: 0 28px 20px 28px;">
                            <div style="font-size: 13px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 10px;">Hydrometeorological Observation Data</div>
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse; font-size: 13px;">
                                <tr style="border-bottom: 1px solid #334155;">
                                    <td style="padding: 9px 0; color: #94A3B8;">Past 24h Cumulative Precipitation</td>
                                    <td align="right" style="padding: 9px 0; font-weight: 600; color: #FFFFFF;">{rain_24h:.1f} mm</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #334155;">
                                    <td style="padding: 9px 0; color: #94A3B8;">Past 72h Antecedent Rainfall</td>
                                    <td align="right" style="padding: 9px 0; font-weight: 600; color: #FFFFFF;">{rain_72h:.1f} mm</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #334155;">
                                    <td style="padding: 9px 0; color: #94A3B8;">Topsoil Saturation (0-9 cm)</td>
                                    <td align="right" style="padding: 9px 0; font-weight: 600; color: #FFFFFF;">{soil_top:.1f}%</td>
                                </tr>
                                <tr style="border-bottom: 1px solid #334155;">
                                    <td style="padding: 9px 0; color: #94A3B8;">Deep Subsurface Saturation (27-81 cm)</td>
                                    <td align="right" style="padding: 9px 0; font-weight: 600; color: #FFFFFF;">{soil_deep:.1f}%</td>
                                </tr>
                                <tr>
                                    <td style="padding: 9px 0; color: #94A3B8;">Surface Temperature</td>
                                    <td align="right" style="padding: 9px 0; font-weight: 600; color: #FFFFFF;">{temp:.1f} °C</td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Emergency Contact Box -->
                    <tr>
                        <td style="padding: 0 28px 24px 28px;">
                            <div style="background-color: #0F172A; border: 1px solid #334155; border-radius: 8px; padding: 16px 20px;">
                                <div style="font-size: 12px; font-weight: 700; color: #F1F5F9; letter-spacing: 0.05em; text-transform: uppercase;">
                                    {state} State Disaster Management Authority (SDMA)
                                </div>
                                <div style="font-size: 12px; color: #94A3B8; margin-top: 3px;">
                                    {sdma_contact.get('dept', 'Disaster Control Operations')}
                                </div>
                                <div style="margin-top: 12px; font-size: 13px; color: #E2E8F0;">
                                    &bull; <b>Toll-Free Helpline:</b> <code style="color: #38BDF8; background: #1E293B; padding: 2px 6px; border-radius: 4px;">{sdma_contact.get('helpline', '1070')}</code><br>
                                    &bull; <b>Control Room Direct:</b> <code style="color: #38BDF8; background: #1E293B; padding: 2px 6px; border-radius: 4px;">{sdma_contact.get('phone', 'N/A')}</code><br>
                                    &bull; <b>National Emergency Dispatch:</b> <code style="color: #38BDF8; background: #1E293B; padding: 2px 6px; border-radius: 4px;">1078 / 112</code>
                                </div>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer & Transparency -->
                    <tr>
                        <td style="background-color: #0F172A; padding: 20px 28px; border-top: 1px solid #334155; font-size: 11px; color: #64748B; line-height: 1.6;">
                            This automated message was dispatched to <b>{recipient_email}</b> based on your active early-warning threshold subscription for {location_title}.<br>
                            Subscription ID: <code>{subscription_id}</code> | Sender: <code>{DEFAULT_EMAIL_USER}</code><br>
                            To unsubscribe or modify preferences at any time, reply to this email with "Unsubscribe" in the subject.<br>
                            GroundCheck Observatory &bull; North Eastern Himalayan Landslide Hazard Mitigation Service
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
    return {
        "subject": subject,
        "plain_text": plain_text,
        "html_body": html_body
    }


# =============================================================================
# SMTP TRANSMISSION DISPATCHER (GMAIL OPTIMIZED)
# =============================================================================
def send_smtp_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str = None,
    subscription_id: str = "sub_generic"
) -> dict:
    """
    Dispatches an email through SMTP (defaulting to Gmail) with full RFC compliance
    and anti-spam validation.
    
    Returns:
    {
        "status": "success" | "error",
        "message": str,
        "deliverability_score": int,
        "warnings": list
    }
    """
    # 1. Run Anti-Spam Linter Verification
    linter_res = analyze_spam_risk(subject, text_body)
    
    # 2. Build RFC-Compliant MIME Message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['To'] = to_email
    
    # Format Sender with Display Name
    sender_addr = DEFAULT_EMAIL_USER
    msg['From'] = f"{DEFAULT_SENDER_NAME} <{sender_addr}>"
    msg['Reply-To'] = sender_addr
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid(domain="groundcheck.org")
    
    # Google 2024 Bulk Sender RFC 8058 Compliance
    msg['List-Unsubscribe'] = f"<mailto:{sender_addr}?subject=Unsubscribe-{subscription_id}>"
    msg['List-Unsubscribe-Post'] = "List-Unsubscribe=One-Click"
    msg['X-Entity-Ref-ID'] = f"groundcheck-{subscription_id}"
    msg['X-Auto-Response-Suppress'] = "OOF, AutoReply"
    
    # Set Plain-Text Content
    msg.set_content(text_body)
    
    # Attach Rich HTML Alternative if provided
    if html_body:
        msg.add_alternative(html_body, subtype='html')
        
    # 3. SMTP TLS Handshake & Dispatch
    try:
        # 10s socket timeout to avoid hanging UI
        server = smtplib.SMTP(DEFAULT_SMTP_HOST, DEFAULT_SMTP_PORT, timeout=12)
        server.ehlo()
        server.starttls()
        server.ehlo()
        
        server.login(DEFAULT_EMAIL_USER, DEFAULT_EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return {
            "status": "success",
            "message": f"Advisory email successfully dispatched to {to_email}",
            "deliverability_score": linter_res["score"],
            "deliverability_status": linter_res["status"],
            "warnings": linter_res["warnings"]
        }
        
    except smtplib.SMTPAuthenticationError as e:
        error_msg = (
            f"Gmail Authentication Error: {str(e)}. "
            "Note: Google requires a 16-character 'App Password' if 2-Step Verification "
            "is enabled on groundcheckalert@gmail.com. You can configure this via the "
            "ALERT_EMAIL_PASSWORD environment variable or Google Account Security settings."
        )
        return {
            "status": "error",
            "message": error_msg,
            "deliverability_score": linter_res["score"],
            "deliverability_status": linter_res["status"],
            "warnings": linter_res["warnings"]
        }
        
    except (smtplib.SMTPConnectError, socket.timeout) as e:
        return {
            "status": "error",
            "message": f"SMTP Connection Failed: Unable to reach {DEFAULT_SMTP_HOST}:{DEFAULT_SMTP_PORT} ({str(e)})",
            "deliverability_score": linter_res["score"],
            "deliverability_status": linter_res["status"],
            "warnings": linter_res["warnings"]
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Email Dispatch Failed: {str(e)}",
            "deliverability_score": linter_res["score"],
            "deliverability_status": linter_res["status"],
            "warnings": linter_res["warnings"]
        }


def send_test_alert_email(recipient_email: str, location_title: str, state: str, sdma_contact: dict) -> dict:
    """
    Sends an immediate verification test advisory email with simulated telemetry.
    """
    mock_risk = {
        "probability": 76.5,
        "classification": "High",
        "alert_level": "Critical Hazard Advisory - Saturated Slope Failure Risk",
        "thresholds": {"rain_24h": 68.0, "rain_72h": 142.5}
    }
    mock_weather = {
        "current": {"temperature": 18.2, "precipitation_rate": 4.5},
        "triggers": {
            "rain_past_24h": 68.0,
            "rain_past_72h": 142.5,
            "soil_moisture_top": 0.42,
            "soil_moisture_deep": 0.38
        }
    }
    
    payload = generate_alert_email_payload(
        recipient_email=recipient_email,
        location_title=location_title,
        state=state,
        risk_output=mock_risk,
        weather_data=mock_weather,
        sdma_contact=sdma_contact,
        subscription_id="test_verification"
    )
    
    return send_smtp_email(
        to_email=recipient_email,
        subject=payload["subject"],
        text_body=payload["plain_text"],
        html_body=payload["html_body"],
        subscription_id="test_verification"
    )
