# GroundCheck Observatory: Email Deliverability & Anti-Spam Knowledge Base

## 1. Executive Summary & Objective

Automated environmental hazard alerts must reach residents' primary inboxes immediately. If an email provider (such as Gmail, Yahoo, or Microsoft Outlook) classifies an early warning as **Spam** or routes it into the **Promotions** / **Junk** tab, the recipient may miss life-critical warnings.

This knowledge base details the technical architecture of **Gmail's Spam Detection Engine**, catalogs **high-risk trigger keywords**, provides **safe scientific substitutions**, and establishes **formatting and RFC compliance standards** to ensure that GroundCheck early warning emails achieve a $99\%+$ primary inbox placement rate.

---

## 2. Gmail Spam Filter Architecture & Mechanics

Gmail relies on multi-tiered, AI-augmented filtering pipelines combining:

1. **Authentication & Protocol Validation (SPF, DKIM, DMARC)**:
   - Verifies whether the sending server has authorization to send mail for the specified domain.
   - Requires valid Reverse DNS (PTR), aligned envelope sender (`Return-Path`), and RFC 5322 header compliance.
2. **Bayesian Text Classifiers & ML Content Scanners**:
   - Scores words, n-grams, and phrase combinations against known spam corpora.
   - Penalizes unnatural exclamation density, monetary symbols, aggressive imperative phrasing, and ALL CAPS blocks.
3. **Reputation & Engagement Metrics (Google Postmaster Tools)**:
   - High mark-as-spam rates ($> 0.10\%$) trigger automatic domain-level quarantine.
   - Emails that provide clean, one-click unsubscribe links (`List-Unsubscribe` header RFC 8058) are granted higher inbox trust.
4. **MIME Structure & Rendering Heuristics**:
   - Emails must supply both a clean `text/plain` alternative and well-structured, semantic `text/html`.
   - Hidden text, excessive font styling (bright red text, microscopic disclaimer text), or single-image emails with minimal text are heavily penalized.

---

## 3. The Spam Trigger Keyword Taxonomy

The following keywords and phrases are recognized by Bayesian filters and Google spam heuristics as high-risk flags. **Never use these terms in hazard alert subjects or message bodies.**

### 3.1. Artificial Urgency & Panic Triggers (High Risk)
| High-Risk Trigger Words | Why It Triggers Spam Filters | Safe Scientific Replacement |
| :--- | :--- | :--- |
| `URGENT!!!` / `ACT NOW` | Classic phishing and scam pattern | `Advisory Update` / `Safety Notice` |
| `IMMEDIATE ACTION REQUIRED` | Phishing keyword for banking alerts | `Precautionary Measures Recommended` |
| `DON'T DELAY` / `TIME IS RUNNING OUT`| Artificial scarcity tactic | `Observation Period: Active Monitoring` |
| `CRITICAL EMERGENCY ALERT!!!` | Overuse of exclamation and alarmism | `Elevated Risk Advisory: Level 3` |
| `DISASTER IMMINENT` | Sensationalist clickbait flag | `Hydrological Threshold Breached` |
| `ATTENTION REQUIRED RIGHT NOW` | Common malware delivery lure | `Regional Terrain Status Summary` |

### 3.2. Promotional, Financial & Marketing Vocabulary
| High-Risk Trigger Words | Why It Triggers Spam Filters | Safe Scientific Replacement |
| :--- | :--- | :--- |
| `Free` / `100% Free` | Top Bayesian commercial spam flag | `Complimentary Public Safety Service` |
| `Guaranteed` / `Risk Free` | Unverifiable claim trigger | `Model Confidence: High (Calibrated)` |
| `Click Here` / `Direct Link` | Generic CTA flag, common in phishing | `Review Live Observatory Station Data` |
| `Exclusive Offer` / `Special Deal` | Commercial promotion flag | `Targeted Regional Advisory` |
| `Save Now` / `Best Price` | E-commerce spam flag | `Mitigation Strategy` |

### 3.3. Account Verification & Security Scare Words
| High-Risk Trigger Words | Why It Triggers Spam Filters | Safe Scientific Replacement |
| :--- | :--- | :--- |
| `Verify Your Account` | Primary credential-harvesting phrase | `Manage Subscription Preferences` |
| `Update Details Immediately` | Phishing trigger | `Modify Regional Coordinates` |
| `Security Alert / Compromise` | Spoofing detection trigger | `Geomorphic Stability Observation` |
| `Confirm Your Identity` | Phishing heuristic flag | `Recipient Verification Completed` |

### 3.4. Deceptive Formatting & Punctuation Patterns
- **Excessive Punctuation**: Using `!!!`, `???`, `$$$`, or emojis like 🚨🚨🚨 in the subject line increases spam score by up to $40\%$.
- **ALL CAPS**: Words like `WARNING`, `DANGER`, `NOTICE`, `CRITICAL` in all uppercase trigger SpamAssassin rule `SUBJ_ALL_CAPS`.
- **URL Shorteners**: Links from `bit.ly`, `tinyurl.com`, `t.co` are flagged as suspicious redirections. Always use full, transparent HTTPS URLs.
- **Mismatched Hyperlinks**: Displaying `https://groundcheck.org` as the anchor text while pointing to an IP address or different domain triggers Google's Phishing classifier.

---

## 4. GroundCheck Authoritative Phrasing Dictionary

To maintain official authority while avoiding spam filters, GroundCheck adheres to the following vocabulary standards:

| Context | Unsafe / Spam-Prone Phrasing | Approved Scientific Formulation |
| :--- | :--- | :--- |
| **Email Subject** | `URGENT LANDSLIDE WARNING FOR SIKKIM!!!` | `GroundCheck Advisory: Landslide Risk Threshold Exceeded for Gangtok, Sikkim` |
| **Subject (Medium Risk)**| `BEWARE: HIGH RAIN AND LANDSLIDE CHANCE!` | `Geomorphic Advisory: Elevated Slope Saturation Detected in East Khasi Hills` |
| **Opening Line** | `Dear resident, you are in grave danger!` | `This automated meteorological observation alert is issued for your registered location.` |
| **Trigger Explanation**| `Massive rainfall is about to cause catastrophic landslides!` | `Telemetry sensors recorded cumulative 72-hour precipitation of 142.0 mm, surpassing regional slope stability thresholds.` |
| **Instructions** | `Evacuate your house immediately or face the consequences!` | `Recommended Protocol: Observe local administrative advisories, maintain distance from steep highway cuts, and keep emergency contact lines accessible.` |
| **Authority Reference**| `Call 911 right now!` | `State Disaster Management Authority (SDMA) Contact: Toll-Free Helpline 1070 / Direct Control Room 03592-202720.` |
| **Footer & Opt-out** | `Click here to stop emails` | `You received this advisory because this address was enrolled in the GroundCheck Early Warning System. To pause alerts, use the one-click unsubscribe link.` |

---

## 5. Technical Delivery & RFC Standards

### 5.1. Multi-Part MIME Structure
Every email dispatched must include both representations:
1. `text/plain`: Clean UTF-8 plaintext with tabular ASCII metrics.
2. `text/html`: Clean, inline-styled semantic HTML with no external scripts, no tracking iframes, and high text-to-code ratio ($> 60\%$).

### 5.2. Mandatory Email Headers
To satisfy **Google and Yahoo 2024 Bulk Sender Requirements**:
```http
From: GroundCheck Observatory Alerts <groundcheckalert@gmail.com>
To: recipient@example.com
Subject: GroundCheck Advisory: Landslide Risk Threshold Exceeded for [Region, State]
Date: Sun, 06 Sep 2026 14:15:00 +0530
Message-ID: <alert-20260906-abc123xyz@groundcheck.internal>
List-Unsubscribe: <mailto:groundcheckalert+unsubscribe@gmail.com?subject=unsubscribe-sub_123>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
MIME-Version: 1.0
Content-Type: multipart/alternative; boundary="===============..."
X-Priority: 3 (Normal)
X-Entity-Ref-ID: groundcheck-alert-loc_a
```

> **Important Note on `X-Priority`**:
> Avoid setting `X-Priority: 1 (Highest)`. Mail servers often consider `X-Priority: 1` as a marker for spam or aggressive sales campaigns. Setting `X-Priority: 3 (Normal)` or omitting it yields better inbox placement.

---

## 6. Real-Time Anti-Spam Verification Linter

The GroundCheck software integrates an in-memory spam risk evaluator (`utils/alert_service.py:analyze_spam_risk`) that executes before every email transmission:
- Tokenizes subject and body.
- Matches against the trigger taxonomy.
- Calculates total capital letter ratio (must be $< 15\%$).
- Verifies absence of repetitive exclamation marks.
- Returns a composite **Deliverability Score (0-100)**:
  - **90 - 100**: Optimal Deliverability (Ready for dispatch)
  - **70 - 89**: Warning (Minor formatting adjustments recommended)
  - **< 70**: Blocked (Contains critical spam triggers; requires reformatting)
