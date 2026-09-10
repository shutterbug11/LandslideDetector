"""
=============================================================================
GroundCheck Landslide Early Warning System - Multilingual Translation Engine
IndicTrans2 Distilled 200M (English -> Indic) Translation Service
Languages Supported: Assamese, Bengali, Nepali, Manipuri, English
=============================================================================
"""

import os
import re
import streamlit as st
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, AutoConfig

# SAFETY / COMPLIANCE NOTE:
# Safety-critical disaster phrases (e.g., "evacuate immediately",
# "critical hazard alert", "avoid hillside road cuts", "liquefaction threshold")
# should be regularly spot-checked for translation accuracy across regional
# dialects in the North Eastern Himalayan Region to prevent ambiguous instructions.

try:
    from IndicTransToolkit import IndicProcessor
except ImportError:
    try:
        from IndicTransToolkit.processor import IndicProcessor
    except ImportError:
        # Cross-platform pure-Python fallback for environments without C++ build tools (Windows)
        from utils.indic_processor import IndicProcessor

# Model variants: official AI4Bharat distilled 200M or public rotary 200M
PRIMARY_MODEL = "ai4bharat/indictrans2-en-indic-dist-200M"
FALLBACK_MODEL = "prajdabre/rotary-indictrans2-en-indic-dist-200M"

# Supported North-Eastern regional languages and FLORES-200 language codes
LANG_OPTIONS = {
    "English": "eng_Latn",
    "অসমীয়া (Assamese)": "asm_Beng",
    "বাংলা (Bengali)": "ben_Beng",
    "नेपाली (Nepali)": "npi_Deva",
    "ꯃꯤꯇꯩꯂꯣꯟ (Manipuri)": "mni_Mtei",
}

# =============================================================================
# CURATED ZERO-LATENCY TRANSLATION CATALOG
# Provides instantaneous, human-verified disaster alerts, headings, and labels
# across Assamese, Bengali, Nepali, and Manipuri.
# =============================================================================
TRANSLATION_CATALOG = {
    # System Branding & Header
    "Earth Observation & Hazard Mitigation": {
        "asm_Beng": "পৃথিৱী পৰ্যবেক্ষণ আৰু বিপদাশংকা প্ৰশমন",
        "ben_Beng": "ভূ-পর্যবেক্ষণ ও দুর্যোগ প্রশমন",
        "npi_Deva": "पृथ्वी अवलोकन तथा प्रकोप न्यूनीकरण",
        "mni_Mtei": "ꯃꯂꯦꯝ ꯌꯦꯡꯁꯤꯅꯕꯥ ꯑꯃꯁꯨꯡ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯍꯟꯊꯍꯅꯕꯥ",
    },
    "Landslide Early Warning": {
        "asm_Beng": "ভূমিস্খলন আগতীয় সতৰ্কবাৰ্তা",
        "ben_Beng": "ভূমিধস প্রাথমিক সতর্কতা",
        "npi_Deva": "पहिरो पूर्व चेतावनी",
        "mni_Mtei": "ꯂꯩꯈꯥꯡꯕꯒꯤ ꯃꯃꯥꯡ ꯆꯦꯀꯁꯤꯟ-ꯊꯧꯔꯥꯡ",
    },
    "North Eastern Himalayan Region, India": {
        "asm_Beng": "উত্তৰ-পূব হিমালয় অঞ্চল, ভাৰত",
        "ben_Beng": "উত্তর-পূর্ব হিমালয় অঞ্চল, ভারত",
        "npi_Deva": "उत्तर-पूर्वी हिमालय क्षेत्र, भारत",
        "mni_Mtei": "ꯑꯋꯥꯡ-ꯅꯣꯡꯄꯣꯛ ꯍꯤꯃꯥꯂꯌ ꯂꯃꯗꯝ, ꯏꯟꯗꯤꯌꯥ",
    },
    "Observation Mode": {
        "asm_Beng": "পৰ্যবেক্ষণ ম'ড",
        "ben_Beng": "পর্যবেক্ষণ মোড",
        "npi_Deva": "अवलोकन मोड",
        "mni_Mtei": "ꯌꯦꯡꯁꯤꯅꯕꯒꯤ ꯃꯣꯗ",
    },
    "Single Location Observatory": {
        "asm_Beng": "একক স্থান মানমন্দিৰ",
        "ben_Beng": "একক অবস্থান পর্যবেক্ষণ কেন্দ্র",
        "npi_Deva": "एकल स्थान वेधशाला",
        "mni_Mtei": "ꯃꯐꯝ ꯑꯃꯈꯛ ꯌꯦꯡꯁꯤꯅꯕꯥ",
    },
    "Compare Locations (Dual Mode)": {
        "asm_Beng": "স্থান তুলনা কৰক (দ্বৈত ম'ড)",
        "ben_Beng": "অবস্থান তুলনা করুন (দ্বৈত মোড)",
        "npi_Deva": "स्थानहरू तुलना गर्नुहोस् (दोहोरो मोड)",
        "mni_Mtei": "ꯃꯐꯝ ꯑꯅꯤ ꯆꯥꯡꯗꯝꯅꯕꯥ",
    },
    "Geographic Scope & Target": {
        "asm_Beng": "ভৌগোলিক পৰিসৰ আৰু লক্ষ্য",
        "ben_Beng": "ভৌগোলিক পরিসর ও লক্ষ্য",
        "npi_Deva": "भौगोलिक दायरा र लक्ष्य",
        "mni_Mtei": "ꯂꯩꯐꯝ ꯑꯃꯁꯨꯡ ꯄꯥꯟꯗꯝ",
    },
    "Pin Two Locations to Compare": {
        "asm_Beng": "তুলনাৰ বাবে দুটা স্থান পিন কৰক",
        "ben_Beng": "তুলনার জন্য দুটি অবস্থান পিন করুন",
        "npi_Deva": "तुलना गर्न दुई स्थानहरू पिन गर्नुहोस्",
        "mni_Mtei": "ꯆꯥꯡꯗꯝꯅꯅꯕꯥ ꯃꯐꯝ ꯑꯅꯤ ꯈꯅꯕꯤꯌꯨ",
    },
    "Quick Comparison Preset": {
        "asm_Beng": "দ্ৰুত তুলনা পূৰ্বনিৰ্ধাৰণ",
        "ben_Beng": "দ্রুত তুলনা প্রিসেট",
        "npi_Deva": "द्रुत तुलना पूर्वसेट",
        "mni_Mtei": "ꯌꯥꯡꯅꯥ ꯆꯥꯡꯗꯝꯅꯕꯥ",
    },
    "Location A (Primary Pin)": {
        "asm_Beng": "স্থান ক (প্ৰাথমিক পিন)",
        "ben_Beng": "অবস্থান ক (প্রাথমিক পিন)",
        "npi_Deva": "स्थान क (प्राथमिक पिन)",
        "mni_Mtei": "ꯃꯐꯝ ꯑ (ꯑꯍꯥꯅꯕꯥ ꯄꯤꯟ)",
    },
    "Location B (Comparison Pin)": {
        "asm_Beng": "স্থান খ (তুলনামূলক পিন)",
        "ben_Beng": "অবস্থান খ (তুলনামূলক পিন)",
        "npi_Deva": "स्थान ख (तुलनात्मक पिन)",
        "mni_Mtei": "ꯃꯐꯝ ꯕ (ꯆꯥꯡꯗꯝꯅꯕꯥ ꯄꯤꯟ)",
    },
    "Target Location": {
        "asm_Beng": "লক্ষ্যস্থান",
        "ben_Beng": "লক্ষ্য অবস্থান",
        "npi_Deva": "लक्षित स्थान",
        "mni_Mtei": "ꯇꯥꯔꯒꯦꯠ ꯃꯐꯝ",
    },
    "Pinned Location A": {
        "asm_Beng": "পিন কৰা স্থান ক",
        "ben_Beng": "পিন করা অবস্থান ক",
        "npi_Deva": "पिन गरिएको स्थान क",
        "mni_Mtei": "ꯄꯤꯟ ꯇꯧꯔꯕꯥ ꯃꯐꯝ ꯑ",
    },
    "Pinned Location B": {
        "asm_Beng": "পিন কৰা স্থান খ",
        "ben_Beng": "পিন করা অবস্থান খ",
        "npi_Deva": "पिन गरिएको स्थान ख",
        "mni_Mtei": "ꯄꯤꯟ ꯇꯧꯔꯕꯥ ꯃꯐꯝ ꯕ",
    },

    # Risk Classifications & Status Pills
    "High Risk": {
        "asm_Beng": "উচ্চ বিপদাশংকা",
        "ben_Beng": "উচ্চ ঝুঁকি",
        "npi_Deva": "उच्च जोखिम",
        "mni_Mtei": "ꯌꯥꯝꯅꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ",
    },
    "Medium Risk": {
        "asm_Beng": "মধ্যম বিপদাশংকা",
        "ben_Beng": "মাঝারি ঝুঁকি",
        "npi_Deva": "मध्यम जोखिम",
        "mni_Mtei": "ꯃꯌꯥꯏ ꯑꯣꯏꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ",
    },
    "Low Risk": {
        "asm_Beng": "নিম্ন বিপদাশংকা",
        "ben_Beng": "কম ঝুঁকি",
        "npi_Deva": "कम जोखिम",
        "mni_Mtei": "ꯅꯦꯝꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ",
    },
    "Critical Advisory - High Failure Probability": {
        "asm_Beng": "জৰুৰীকালীন সতৰ্কবাৰ্তা - ভূমিস্খলনৰ অতি উচ্চ সম্ভাৱনা",
        "ben_Beng": "জরুরি পরামর্শ - অত্যন্ত উচ্চ ভূমিধস সম্ভাবনা",
        "npi_Deva": "गम्भीर चेतावनी - उच्च पहिरो सम्भावना",
        "mni_Mtei": "ꯌꯥꯝꯅꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ - ꯂꯩꯈꯥꯡꯕꯒꯤ ꯑꯋꯥꯡꯕꯥ ꯆꯥꯡ",
    },
    "Heightened Vigilance - Saturated Slopes": {
        "asm_Beng": "সতৰ্কতা বৃদ্ধি - সংপৃক্ত পাহাৰীয়া ঢাল",
        "ben_Beng": "উচ্চ সতর্কতা - স্যাঁতসেঁতে পাহাড়ি ঢাল",
        "npi_Deva": "उच्च सतर्कता - संतृप्त भिरालो जमिन",
        "mni_Mtei": "ꯆꯦꯀꯁꯤꯟ-ꯊꯧꯔꯥꯡ ꯂꯧꯈꯠꯄꯥ - ꯏꯁꯤꯡ ꯆꯨꯝꯂꯕꯥ ꯆꯤꯡꯖꯥꯎ",
    },
    "Normal Baseline - Low Susceptibility": {
        "asm_Beng": "স্বাভাৱিক স্থিতি - নিম্ন বিপদাশংকা",
        "ben_Beng": "স্বাভাবিক অবস্থা - কম সংবেদনশীলতা",
        "npi_Deva": "सामान्य अवस्था - कम संवेदनशीलता",
        "mni_Mtei": "ꯅꯣꯔꯃꯦꯜ ꯑꯣꯏꯕꯥ - ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯅꯦꯝꯕꯥ",
    },

    # Alert Headers
    "Critical Hazard Alert Active": {
        "asm_Beng": "জৰুৰীকালীন বিপদাশংকা সতৰ্কবাৰ্তা সক্ৰিয়",
        "ben_Beng": "জরুরি বিপদাশঙ্কা সতর্কতা সক্রিয়",
        "npi_Deva": "गम्भीर प्रकोप चेतावनी सक्रिय",
        "mni_Mtei": "ꯌꯥꯝꯅꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯒꯤ ꯆꯦꯀꯁꯤꯟ-ꯊꯧꯔꯥꯡ ꯆꯠꯅꯔꯦ",
    },
    "Elevated Slope Stability Advisory": {
        "asm_Beng": "উচ্চ পাহাৰীয়া ঢাল স্থিৰতা পৰামৰ্শ",
        "ben_Beng": "উচ্চ পাহাড়ি ঢাল স্থিতিশীলতা পরামর্শ",
        "npi_Deva": "उच्च भीर स्थिरता सल्लाह",
        "mni_Mtei": "ꯆꯤꯡꯖꯥꯎ ꯂꯩꯈꯥꯡꯕꯒꯤ ꯆꯦꯀꯁꯤꯟ ꯋꯥꯐꯝ",
    },
    "Normal Baseline Stability": {
        "asm_Beng": "স্বাভাৱিক স্থিৰতা অৱস্থা",
        "ben_Beng": "স্বাভাবিক স্থিতিশীল অবস্থা",
        "npi_Deva": "सामान्य स्थिरता अवस्था",
        "mni_Mtei": "ꯅꯣꯔꯃꯦꯜ ꯑꯣꯏꯕꯥ ꯐꯤꯚꯝ",
    },
    "Comparative Hazard Assessment Summary": {
        "asm_Beng": "তুলনামূলক বিপদাশংকা নিৰূপণ সাৰাংশ",
        "ben_Beng": "তুলনামূলক ঝুঁকি মূল্যায়ন সারসংক্ষেপ",
        "npi_Deva": "तुलनात्मक जोखिम मूल्याङ्कन सारांश",
        "mni_Mtei": "ꯆꯥꯡꯗꯝꯅꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯒꯤ ꯋꯥꯔꯦꯞ",
    },

    # Metric Cards
    "Landslide Probability": {
        "asm_Beng": "ভূমিস্খলনৰ সম্ভাৱনা",
        "ben_Beng": "ভূমিধসের সম্ভাবনা",
        "npi_Deva": "पहिरोको सम्भावना",
        "mni_Mtei": "ꯂꯩꯈꯥꯡꯕꯒꯤ ꯆꯥꯡ",
    },
    "24h Rainfall Total": {
        "asm_Beng": "২৪ ঘণ্টাত মুঠ বৰষুণ",
        "ben_Beng": "২৪ ঘণ্টায় মোট বৃষ্টিপাত",
        "npi_Deva": "२४ घण्टाको कुल वर्षा",
        "mni_Mtei": "ꯄꯨꯡ ২৪ꯒꯤ ꯅꯣꯡ ꯆꯨꯕꯒꯤ ꯆꯥꯡ",
    },
    "Topsoil Saturation (0-9cm)": {
        "asm_Beng": "ওপৰৰ মাটিৰ আৰ্দ্ৰতা (০-৯ চেমি)",
        "ben_Beng": "উপরিভাগের মাটির আর্দ্রতা (০-৯ সেমি)",
        "npi_Deva": "माथिल्लो माटोको संतृप्ति (०-९ सेमी)",
        "mni_Mtei": "ꯂꯩꯃꯥꯏꯒꯤ ꯏꯁꯤꯡ ꯆꯥꯡ (০-৯cm)",
    },
    "Surface Temperature": {
        "asm_Beng": "পৃষ্ঠৰ উষ্ণতা",
        "ben_Beng": "পৃষ্ঠের তাপমাত্রা",
        "npi_Deva": "सतहको तापक्रम",
        "mni_Mtei": "ꯃꯂꯪ ꯑꯌꯤꯡ-ꯑꯁꯥ",
    },
    "Relative Humidity": {
        "asm_Beng": "আপেক্ষিক আৰ্দ্ৰতা",
        "ben_Beng": "আপেক্ষিক আর্দ্রতা",
        "npi_Deva": "सापेक्ष आर्द्रता",
        "mni_Mtei": "ꯅꯣꯡꯂꯩ ꯑꯌꯤꯡ",
    },
    "Ensemble Geo-Hydrological": {
        "asm_Beng": "যৌথ ভূ-জলবিজ্ঞান মডেল",
        "ben_Beng": "যৌথ ভূ-জলতাত্ত্বিক মডেল",
        "npi_Deva": "समूह भू-जलवैज्ञानिक",
        "mni_Mtei": "ꯖꯤꯑꯣ-ꯍꯥꯏꯗ꯭ꯔꯣꯂꯣꯖꯤꯀꯦꯜ",
    },
    "Weather Telemetry Summary": {
        "asm_Beng": "বতৰৰ টেলিমেট্ৰি সাৰাংশ",
        "ben_Beng": "আবহাওয়া টেলিমেট্রি সারসংক্ষেপ",
        "npi_Deva": "मौसम टेलिमेट्री सारांश",
        "mni_Mtei": "ꯅꯣꯡ-ꯆꯤꯡꯒꯤ ꯐꯤꯚꯝ ꯋꯥꯔꯦꯞ",
    },
    "Comparative Weather Telemetry": {
        "asm_Beng": "তুলনামূলক বতৰৰ টেলিমেট্ৰি",
        "ben_Beng": "তুলনামূলক আবহাওয়া টেলিমেট্রি",
        "npi_Deva": "तुलनात्मक मौसम टेलिमेट्री",
        "mni_Mtei": "ꯆꯥꯡꯗꯝꯅꯕꯥ ꯅꯣꯡ-ꯆꯤꯡꯒꯤ ꯐꯤꯚꯝ",
    },
    "Landslide Risk %": {
        "asm_Beng": "ভূমিস্খলনৰ বিপদাশংকা %",
        "ben_Beng": "ভূমিধস ঝুঁকি %",
        "npi_Deva": "पहिरो जोखिम %",
        "mni_Mtei": "ꯂꯩꯈꯥꯡꯕꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ %",
    },
    "Elevation Delta": {
        "asm_Beng": "উচ্চতাৰ পাৰ্থক্য",
        "ben_Beng": "উচ্চতার পার্থক্য",
        "npi_Deva": "उचाइको अन्तर",
        "mni_Mtei": "ꯑꯋꯥꯡꯕꯒꯤ ꯈꯦꯠꯅꯕꯥ",
    },
    "72h Antecedent Rain": {
        "asm_Beng": "৭২ ঘণ্টাৰ পূৰ্ববৰ্তী বৰষুণ",
        "ben_Beng": "৭২ ঘণ্টার পূর্ববর্তী বৃষ্টি",
        "npi_Deva": "७२ घण्टाको पूर्व वर्षा",
        "mni_Mtei": "ꯄꯨꯡ ৭২ꯒꯤ ꯃꯃꯥꯡꯒꯤ ꯅꯣꯡ",
    },
    "Deep Subsoil (27-81cm)": {
        "asm_Beng": "গভীৰ অন্তৰ্ভাগৰ মাটি (২৭-৮১ চেমি)",
        "ben_Beng": "গভীর অভ্যন্তরীণ মাটি (২৭-৮১ সেমি)",
        "npi_Deva": "गहिरो भित्री माटो (२७-८१ सेमी)",
        "mni_Mtei": "ꯂꯨꯝꯅꯥ ꯂꯩꯕꯥ ꯃꯅꯨꯡꯒꯤ ꯂꯩ (২৭-৮১cm)",
    },

    # Section Titles & Maps
    "Regional Hazard & Susceptibility Map": {
        "asm_Beng": "আঞ্চলিক বিপদাশংকা আৰু সংবেদনশীলতা মানচিত্ৰ",
        "ben_Beng": "আঞ্চলিক ঝুঁকি ও সংবেদনশীলতার মানচিত্র",
        "npi_Deva": "क्षेत्रीय जोखिम तथा संवेदनशीलता नक्सा",
        "mni_Mtei": "ꯂꯃꯗꯝꯁꯤꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯒꯤ ꯃꯦꯞ",
    },
    "Dual-Station Regional Geospatial Map": {
        "asm_Beng": "দ্বৈত-কেন্দ্ৰীয় আঞ্চলিক ভৌগোলিক মানচিত্ৰ",
        "ben_Beng": "দ্বৈত-স্টেশন আঞ্চলিক ভূ-স্থানিক মানচিত্র",
        "npi_Deva": "दोहोरो-स्टेशन क्षेत्रीय भू-स्थानिक नक्सा",
        "mni_Mtei": "ꯁ꯭ꯇꯦꯁꯟ ꯑꯅꯤꯒꯤ ꯖꯤꯑꯣꯁ꯭ꯄꯦꯁꯤꯑꯦꯜ ꯃꯦꯞ",
    },
    "14-Day Risk Trajectory & Precipitation Forecast": {
        "asm_Beng": "১৪ দিনৰ বিপদাশংকা আৰু বৰষুণৰ পূৰ্বাভাস",
        "ben_Beng": "১৪ দিনের ঝুঁকি গতিপথ ও বৃষ্টিপাতের পূর্বাভাস",
        "npi_Deva": "१४ दिने जोखिम प्रक्षेपण तथा वर्षा पूर्वानुमान",
        "mni_Mtei": "ꯅꯨꯃꯤꯠ ১৪ꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯑꯃꯁꯨꯡ ꯅꯣꯡ ꯆꯨꯕꯒꯤ ꯋꯥꯔꯦꯞ",
    },
    "Dual Location Comparative Observatory": {
        "asm_Beng": "দ্বৈত স্থান তুলনামূলক মানমন্দিৰ",
        "ben_Beng": "দ্বৈত অবস্থান তুলনামূলক পর্যবেক্ষণ কেন্দ্র",
        "npi_Deva": "दोहोरो स्थान तुलनात्मक वेधशाला",
        "mni_Mtei": "ꯃꯐꯝ ꯑꯅꯤ ꯆꯥꯡꯗꯝꯅꯕꯥ ꯌꯦꯡꯁꯤꯟ ꯃꯐꯝ",
    },

    # Tabs
    "Risk Drivers Breakdown": {
        "asm_Beng": "বিপদাশংকাৰ কাৰক বিশ্লেষণ",
        "ben_Beng": "ঝুঁকির নিয়ামকসমূহ",
        "npi_Deva": "जोखिम कारकहरूको विश्लेषण",
        "mni_Mtei": "ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯊꯣꯛꯍꯅꯕꯥ ꯃꯔꯃꯁꯤꯡ",
    },
    "Subsurface Hydrology": {
        "asm_Beng": "ভূগৰ্ভস্থ জলবিজ্ঞান",
        "ben_Beng": "ভূগর্ভস্থ জলবিদ্যা",
        "npi_Deva": "भू-सतह जलविज्ञान",
        "mni_Mtei": "ꯂꯩꯃꯥꯏ ꯃꯅꯨꯡꯒꯤ ꯏꯁꯤꯡ",
    },
    "Emergency Protocols & SDMA": {
        "asm_Beng": "জৰুৰীকালীন প্ৰট'কল আৰু SDMA",
        "ben_Beng": "জরুরি প্রোটোকল ও এসডিএমএ",
        "npi_Deva": "आपतकालीन प्रोटोकल तथा SDMA",
        "mni_Mtei": "ꯏꯃꯔꯖꯦꯟꯁꯤ ꯄ꯭ꯔꯣꯇꯣꯀꯣꯜ ꯑꯃꯁꯨꯡ SDMA",
    },
    "Resident Alert Dispatch": {
        "asm_Beng": "নাগৰিক সতৰ্কবাৰ্তা প্ৰেৰণ",
        "ben_Beng": "বাসিন্দা সতর্কতা প্রেরণ",
        "npi_Deva": "बासिन्दा चेतावनी प्रेषण",
        "mni_Mtei": "ꯃꯤꯌꯥꯃꯗꯥ ꯄꯥꯎ ꯐꯥꯎꯍꯅꯕꯥ",
    },
    "Topographic Baseline": {
        "asm_Beng": "ভূসংস্থানিক ভিত্তি",
        "ben_Beng": "টপোগ্রাফিক ভিত্তি",
        "npi_Deva": "स्थलाकृतिक आधार रेखा",
        "mni_Mtei": "ꯇꯣꯄꯣꯒ꯭ꯔꯥꯐꯤꯛ ꯕꯦꯁꯂꯥꯏꯟ",
    },
    "Hydrological Triggers": {
        "asm_Beng": "জলবিজ্ঞান সংক্ৰান্তিয় কাৰক",
        "ben_Beng": "জলতাত্ত্বিক কারণসমূহ",
        "npi_Deva": "जलवैज्ञानिक कारकहरू",
        "mni_Mtei": "ꯏꯁꯤꯡꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯁꯤꯡ",
    },
    "14-Day Trajectory": {
        "asm_Beng": "১৪ দিনৰ গতিপথ",
        "ben_Beng": "১৪ দিনের গতিপথ",
        "npi_Deva": "१४ दिने प्रक्षेपण",
        "mni_Mtei": "ꯅꯨꯃꯤꯠ ১৪ꯒꯤ ꯄꯥꯎ",
    },
    "Emergency Contacts & SDMA": {
        "asm_Beng": "জৰুৰীকালীন যোগাযোগ আৰু SDMA",
        "ben_Beng": "জরুরি যোগাযোগ ও এসডিএমএ",
        "npi_Deva": "आपतकालीन सम्पर्क तथा SDMA",
        "mni_Mtei": "ꯏꯃꯔꯖꯦꯟꯁꯤ ꯀꯟꯇꯦꯛꯇ ꯑꯃꯁꯨꯡ SDMA",
    },
    "Alert Dispatch System": {
        "asm_Beng": "সতৰ্কবাৰ্তা প্ৰেৰণ ব্যৱস্থা",
        "ben_Beng": "সতর্কবার্তা প্রেরণ ব্যবস্থা",
        "npi_Deva": "चेतावनी प्रेषण प्रणाली",
        "mni_Mtei": "ꯄꯥꯎ ꯐꯥꯎꯍꯅꯕꯒꯤ ꯁꯤꯁ꯭ꯇꯦꯝ",
    },

    # Emergency Services & NDMA SOP
    "State Disaster Management Authority (SDMA) Emergency Contacts": {
        "asm_Beng": "ৰাজ্যিক দুৰ্যোগ ব্যৱস্থাপনা প্ৰাধিকৰণ (SDMA) জৰুৰীকালীন যোগাযোগ",
        "ben_Beng": "রাজ্য দুর্যোগ ব্যবস্থাপনা কর্তৃপক্ষ (SDMA) জরুরি যোগাযোগ",
        "npi_Deva": "राज्य विपद् व्यवस्थापन प्राधिकरण (SDMA) आपतकालीन सम्पर्क",
        "mni_Mtei": "ꯁ꯭ꯇꯦꯠ ꯗꯤꯖꯥꯁ꯭ꯇꯔ ꯃꯦꯅꯦꯖꯃꯦꯟꯇ (SDMA) ꯏꯃꯔꯖꯦꯟꯁꯤ ꯀꯟꯇꯦꯛꯇ",
    },
    "State Disaster Management Authorities & Emergency Protocols": {
        "asm_Beng": "ৰাজ্যিক দুৰ্যোগ ব্যৱস্থাপনা কৰ্তৃপক্ষ আৰু জৰুৰীকালীন নিৰ্দেশনা",
        "ben_Beng": "রাজ্য দুর্যোগ ব্যবস্থাপনা কর্তৃপক্ষ ও জরুরি প্রোটোকল",
        "npi_Deva": "राज्य विपद् व्यवस्थापन प्राधिकरण तथा आपतकालीन नियमहरू",
        "mni_Mtei": "ꯁ꯭ꯇꯦꯠ ꯗꯤꯖꯥꯁ꯭ꯇꯔ ꯑꯣꯊꯣꯔꯤꯇꯤ ꯑꯃꯁꯨꯡ ꯏꯃꯔꯖꯦꯟꯁꯤ ꯄ꯭ꯔꯣꯇꯣꯀꯣꯜ",
    },
    "Authorized State Agency": {
        "asm_Beng": "অনুমোদিত ৰাজ্যিক সংস্থা",
        "ben_Beng": "অনুমোদিত রাষ্ট্রীয় সংস্থা",
        "npi_Deva": "अधिकृत राज्य निकाय",
        "mni_Mtei": "ꯑꯌꯥꯕꯥ ꯄꯤꯔꯕꯥ ꯁ꯭ꯇꯦꯠ ꯑꯦꯖꯦꯟꯁꯤ",
    },
    "Authorized Agency": {
        "asm_Beng": "অনুমোদিত সংস্থা",
        "ben_Beng": "অনুমোদিত সংস্থা",
        "npi_Deva": "अधिकृत निकाय",
        "mni_Mtei": "ꯑꯌꯥꯕꯥ ꯄꯤꯔꯕꯥ ꯑꯦꯖꯦꯟꯁꯤ",
    },
    "State Toll-Free Emergency Helpline": {
        "asm_Beng": "ৰাজ্যিক শুল্কমুক্ত জৰুৰীকালীন হেল্পলাইন",
        "ben_Beng": "রাজ্য টোল-ফ্রি জরুরি হেল্পলাইন",
        "npi_Deva": "राज्य टोल-फ्री आपतकालीन हेल्पलाइन",
        "mni_Mtei": "ꯁ꯭ꯇꯦꯠ ꯇꯣꯜ-ꯐ꯭ꯔꯤ ꯏꯃꯔꯖꯦꯟꯁꯤ ꯍꯦꯜꯄꯂꯥꯏꯟ",
    },
    "Direct Control Room": {
        "asm_Beng": "প্ৰত্যক্ষ নিয়ন্ত্ৰণ কক্ষ",
        "ben_Beng": "সরাসরি নিয়ন্ত্রণ কক্ষ",
        "npi_Deva": "प्रत्यक्ष नियन्त्रण कक्ष",
        "mni_Mtei": "ꯀꯟꯠꯔꯣꯜ ꯔꯨꯝ",
    },
    "National Disaster Response Force (NDRF)": {
        "asm_Beng": "ৰাষ্ট্ৰীয় দুৰ্যোগ প্ৰশমন বাহিনী (NDRF)",
        "ben_Beng": "জাতীয় দুর্যোগ প্রতিক্রিয়া বাহিনী (NDRF)",
        "npi_Deva": "राष्ट्रिय विपद् प्रतिकार्य बल (NDRF)",
        "mni_Mtei": "ꯅꯦꯁꯅꯦꯜ ꯗꯤꯖꯥꯁ꯭ꯇꯔ ꯔꯦꯁꯄꯣꯟꯁ ꯐꯣꯔ꯭ꯁ (NDRF)",
    },
    "NDMA Standard Operating Procedure (SOP):": {
        "asm_Beng": "NDMA মানক কাৰ্যপ্ৰণালী (SOP):",
        "ben_Beng": "এনডিএমএ স্ট্যান্ডার্ড অপারেটিং পদ্ধতি (SOP):",
        "npi_Deva": "NDMA मानक सञ्चालन प्रक्रिया (SOP):",
        "mni_Mtei": "NDMA ꯁ꯭ꯇꯦꯟꯗꯔ꯭ꯗ ꯑꯣꯄꯔꯦꯇꯤꯡ ꯄ꯭ꯔꯣꯁꯤꯗ꯭ꯌꯨꯔ (SOP):",
    },
    "Pre-Warning Signs": {
        "asm_Beng": "পূৰ্ব-সতৰ্কতা লক্ষণসমূহ",
        "ben_Beng": "পূর্ব-সতর্কতামূলক লক্ষণসমূহ",
        "npi_Deva": "पूर्व-चेतावनी संकेतहरू",
        "mni_Mtei": "ꯃꯃꯥꯡꯗꯥ ꯈꯪꯗꯣꯛꯅꯕꯥ ꯈꯨꯗꯝꯁꯤꯡ",
    },
    "Safe Refuge": {
        "asm_Beng": "সুৰক্ষিত আশ্ৰয়",
        "ben_Beng": "নিরাপদ আশ্রয়",
        "npi_Deva": "सुरक्षित आश्रय",
        "mni_Mtei": "ꯉꯥꯛꯊꯣꯛꯅꯕꯥ ꯃꯐꯝ",
    },
    "Valley Hazards": {
        "asm_Beng": "উপত্যকা বিপদাশংকা",
        "ben_Beng": "উপত্যকা বিপদ",
        "npi_Deva": "उपत्यका जोखिम",
        "mni_Mtei": "ꯇꯝꯄꯥꯛꯀꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯁꯤꯡ",
    },
    "Highway Transit": {
        "asm_Beng": "ৰাজপথ যাতায়াত",
        "ben_Beng": "মহাসড়ক যাতায়াত",
        "npi_Deva": "राजमार्ग यात्रा",
        "mni_Mtei": "ꯂꯝꯕꯤ-ꯆꯠꯊꯣꯛ-ꯆꯠꯁꯤꯟ",
    },

    # Controls & Checkboxes
    "Export Report as PDF": {
        "asm_Beng": "পিডিএফ প্ৰতিবেদন ডাউনলোড কৰক",
        "ben_Beng": "পিডিএফ রিপোর্ট ডাউনলোড করুন",
        "npi_Deva": "पीडीएफ रिपोर्ट डाउनलोड गर्नुहोस्",
        "mni_Mtei": "PDF ꯔꯤꯄꯣꯔ꯭ꯠ ꯗꯥꯎꯅꯂꯣꯗ ꯇꯧꯕꯤꯌꯨ",
    },
    "PDF: Pin A": {
        "asm_Beng": "পিডিএফ: পিন ক",
        "ben_Beng": "পিডিএফ: পিন ক",
        "npi_Deva": "पीडीएफ: पिन क",
        "mni_Mtei": "PDF: ꯄꯤꯟ ꯑ",
    },
    "PDF: Pin B": {
        "asm_Beng": "পিডিএফ: পিন খ",
        "ben_Beng": "পিডিএফ: পিন খ",
        "npi_Deva": "पीडीएफ: पिन ख",
        "mni_Mtei": "PDF: ꯄꯤꯟ ꯕ",
    },
    "Resident Alert Registry": {
        "asm_Beng": "নাগৰিক সতৰ্কবাৰ্তা পঞ্জীয়ন",
        "ben_Beng": "বাসিন্দা সতর্কতা রেজিস্ট্রি",
        "npi_Deva": "बासिन्दा चेतावनी दर्ता",
        "mni_Mtei": "ꯃꯤꯌꯥꯃꯒꯤ ꯄꯥꯎ ꯔꯦꯖꯤꯁ꯭ꯇ꯭ꯔꯤ",
    },
    "Enrolled Subscribers": {
        "asm_Beng": "পঞ্জীভুক্ত নাগৰিক",
        "ben_Beng": "নিবন্ধিত গ্রাহক",
        "npi_Deva": "दर्ता भएका बासिन्दाहरू",
        "mni_Mtei": "ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯔꯕꯥ ꯃꯤꯌꯥꯝ",
    },
    "Geodetic Separation": {
        "asm_Beng": "ভৌগোলিক দূৰত্ব",
        "ben_Beng": "ভৌগোলিক দূরত্ব",
        "npi_Deva": "भौगोलिक दूरी",
        "mni_Mtei": "ꯂꯥꯞꯅꯕꯒꯤ ꯆꯥꯡ",
    },
    # UI Controls, Sidebar, and Subheaders
    "Preset Vulnerable Hotspots": {
        "asm_Beng": "পূৰ্বনিৰ্ধাৰিত সংবেদনশীল হটস্পট",
        "ben_Beng": "পূর্বনির্ধারিত সংবেদনশীল হটস্পট",
        "npi_Deva": "पूर्वसेट संवेदनशील हटस्पटहरू",
        "mni_Mtei": "ꯍꯥꯟꯅꯥ ꯈꯪꯗꯣꯛꯂꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯃꯐꯝ",
    },
    "Custom GPS Coordinates": {
        "asm_Beng": "কাষ্টম জিপিএছ স্থানাংক",
        "ben_Beng": "কাস্টম জিপিএস স্থানাঙ্ক",
        "npi_Deva": "अनुकूलित GPS निर्देशांक",
        "mni_Mtei": "ꯀꯁ꯭ꯇꯃ GPS ꯀꯣꯑꯣꯔꯗꯤꯅꯦꯠ",
    },
    "State": {
        "asm_Beng": "ৰাজ্য",
        "ben_Beng": "রাজ্য",
        "npi_Deva": "राज्य",
        "mni_Mtei": "ꯁ꯭ꯇꯦꯠ",
    },
    "District / Corridor": {
        "asm_Beng": "জিলা / কৰিডৰ",
        "ben_Beng": "জেলা / করিডোর",
        "npi_Deva": "जिल्ला / करिडोर",
        "mni_Mtei": "ꯗꯤꯁ꯭ꯇ꯭ꯔꯤꯛꯠ / ꯂꯝꯕꯤ",
    },
    "Manual Coordinates": {
        "asm_Beng": "মেনুৱেল স্থানাংক",
        "ben_Beng": "ম্যানুয়াল স্থানাঙ্ক",
        "npi_Deva": "म्यानुअल निर्देशांक",
        "mni_Mtei": "ꯃꯦꯅꯨꯑꯦꯜ ꯀꯣꯑꯣꯔꯗꯤꯅꯦꯠ",
    },
    "Latitude °N": {
        "asm_Beng": "অক্ষাংশ °উত্তৰ",
        "ben_Beng": "অক্ষাংশ °উত্তর",
        "npi_Deva": "अक्षांश °उत्तर",
        "mni_Mtei": "ꯂꯦꯇꯤꯆ꯭ꯌꯨꯗ °N",
    },
    "Longitude °E": {
        "asm_Beng": "দ্ৰাঘিমাংশ °পূব",
        "ben_Beng": "দ্রাঘিমাংশ °পূর্ব",
        "npi_Deva": "देशान्तर °पूर्व",
        "mni_Mtei": "ꯂꯣꯡꯒꯤꯆ꯭ꯌꯨꯗ °E",
    },
    "Elevation": {
        "asm_Beng": "উচ্চতা",
        "ben_Beng": "উচ্চতা",
        "npi_Deva": "उचाइ",
        "mni_Mtei": "ꯑꯋꯥꯡꯕꯥ",
    },
    "Elevation m": {
        "asm_Beng": "উচ্চতা মি",
        "ben_Beng": "উচ্চতা মি",
        "npi_Deva": "उचाइ मिटर",
        "mni_Mtei": "ꯑꯋꯥꯡꯕꯥ m",
    },
    "Slope Gradient": {
        "asm_Beng": "ঢালৰ মাত্ৰা",
        "ben_Beng": "ঢালের নতি",
        "npi_Deva": "भीरको झुकाव",
        "mni_Mtei": "ꯆꯤꯡꯁꯤꯟ",
    },
    "Terrain Slope": {
        "asm_Beng": "ভূভাগৰ ঢাল",
        "ben_Beng": "ভূখণ্ডের ঢাল",
        "npi_Deva": "भू-भाग भीर",
        "mni_Mtei": "ꯆꯤꯡꯖꯥꯎꯒꯤ ꯆꯤꯡꯁꯤꯟ",
    },
    "Terrain Slope °": {
        "asm_Beng": "ভূভাগৰ ঢাল °",
        "ben_Beng": "ভূখণ্ডের ঢাল °",
        "npi_Deva": "भू-भागको भीर °",
        "mni_Mtei": "ꯆꯤꯡꯖꯥꯎꯒꯤ ꯆꯤꯡꯁꯤꯟ °",
    },
    "Slope Aspect": {
        "asm_Beng": "ঢালৰ দিশ",
        "ben_Beng": "ঢালের দিক",
        "npi_Deva": "भीरको दिशा",
        "mni_Mtei": "ꯆꯤꯡꯁꯤꯟ ꯃꯥꯏꯀꯩ",
    },
    "Slope Aspect °": {
        "asm_Beng": "ঢালৰ দিশ °",
        "ben_Beng": "ঢালের দিক °",
        "npi_Deva": "भीरको दिशा °",
        "mni_Mtei": "ꯆꯤꯡꯁꯤꯟ ꯃꯥꯏꯀꯩ °",
    },
    "Geology": {
        "asm_Beng": "ভূতত্ত্ব",
        "ben_Beng": "ভূতত্ত্ব",
        "npi_Deva": "भूगर्भशास्त्र",
        "mni_Mtei": "ꯖꯤꯑꯣꯂꯣꯖꯤ",
    },
    "Corridor": {
        "asm_Beng": "কৰিডৰ",
        "ben_Beng": "করিডোর",
        "npi_Deva": "करिडोर",
        "mni_Mtei": "ꯂꯝꯕꯤ",
    },
    "Advisory Tiers (GSI / NDMA Standard):": {
        "asm_Beng": "পৰামৰ্শ স্তৰ (GSI / NDMA মানক):",
        "ben_Beng": "পরামর্শের স্তর (GSI / NDMA মানক):",
        "npi_Deva": "सल्लाहकार तहहरू (GSI / NDMA मानक):",
        "mni_Mtei": "ꯆꯦꯀꯁꯤꯟ ꯊꯧꯔꯥꯡꯒꯤ ꯊꯥꯛ (GSI / NDMA ꯁ꯭ꯇꯦꯟꯗꯔ꯭ꯗ):",
    },
    "Low Risk (<35%): Baseline stability, normal vigilance": {
        "asm_Beng": "নিম্ন বিপদাশংকা (<৩৫%): স্বাভাৱিক স্থিৰতা, নিয়মীয়া সতৰ্কতা",
        "ben_Beng": "কম ঝুঁকি (<৩৫%): স্বাভাবিক স্থিতিশীলতা, নিয়মিত সতর্কতা",
        "npi_Deva": "कम जोखिम (<३५%): सामान्य स्थिरता, नियमित सतर्कता",
        "mni_Mtei": "ꯅꯦꯝꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ (<35%): ꯅꯣꯔꯃꯦꯜ ꯐꯤꯚꯝ",
    },
    "Medium Risk (35-70%): Saturated slope conditions, caution advised": {
        "asm_Beng": "মধ্যম বিপদাশংকা (৩৫-৭০%): সংপৃক্ত ঢালৰ অৱস্থা, সতৰ্কতাৰ পৰামৰ্শ",
        "ben_Beng": "মাঝারি ঝুঁকি (৩৫-৭০%): স্যাঁতসেঁতে ঢাল, সতর্কতা কাম্য",
        "npi_Deva": "मध्यम जोखिम (३५-७०%): संतृप्त भीर अवस्था, सावधानी अपनाउनुहोस्",
        "mni_Mtei": "ꯃꯌꯥꯏ ꯑꯣꯏꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ (35-70%): ꯆꯦꯀꯁꯤꯅꯕꯥ ꯃꯊꯧ ꯇꯥꯏ",
    },
    "High Risk (>70%): Critical failure probability, evacuation protocol": {
        "asm_Beng": "উচ্চ বিপদাশংকা (>৭০%): গুৰুতৰ খহনীয়াৰ সম্ভাৱনা, স্থান ত্যাগ প্ৰট'কল",
        "ben_Beng": "উচ্চ ঝুঁকি (>৭০%): সংকটজনক ভূমিধসের আশঙ্কা, নিরাপদ আশ্রয়ে যাওয়ার প্রোটোকল",
        "npi_Deva": "उच्च जोखिम (>७०%): गम्भीर पहिरो सम्भावना, सुरक्षित स्थानमा सर्ने प्रोटोकल",
        "mni_Mtei": "ꯌꯥꯝꯅꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ (>70%): ꯈꯨꯗꯛꯇꯥ ꯉꯥꯛꯊꯣꯛꯅꯕꯥ ꯃꯐꯃꯗꯥ ꯆꯠꯄꯥ",
    },
    "Enrolled Subscribers:": {
        "asm_Beng": "পঞ্জীভুক্ত নাগৰিক:",
        "ben_Beng": "নিবন্ধিত গ্রাহক:",
        "npi_Deva": "दर्ता भएका बासिन्दाहरू:",
        "mni_Mtei": "ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯔꯕꯥ ꯃꯤꯑꯣꯏꯁꯤꯡ:",
    },
    "72h Total": {
        "asm_Beng": "৭২ ঘণ্টাত মুঠ",
        "ben_Beng": "৭২ ঘণ্টায় মোট",
        "npi_Deva": "७२ घण्टाको कुल",
        "mni_Mtei": "ꯄꯨꯡ ৭২ꯒꯤ ꯃꯄꯨꯡꯐꯥꯕꯥ",
    },
    "Subsoil": {
        "asm_Beng": "অন্তৰ্ভাগৰ মাটি",
        "ben_Beng": "অভ্যন্তরীণ মাটি",
        "npi_Deva": "भित्री माटो",
        "mni_Mtei": "ꯃꯅꯨꯡꯒꯤ ꯂꯩ",
    },
    "Apparent": {
        "asm_Beng": "অনুভূত",
        "ben_Beng": "অনুভূত",
        "npi_Deva": "अनुभूत",
        "mni_Mtei": "ꯐꯥꯑꯣꯕꯥ",
    },
    "Current Rain Rate": {
        "asm_Beng": "বৰ্তমান বৰষুণৰ হাৰ",
        "ben_Beng": "বর্তমান বৃষ্টিপাতের হার",
        "npi_Deva": "हालको वर्षा दर",
        "mni_Mtei": "ꯍꯧꯖꯤꯛ ꯅꯣꯡ ꯆꯨꯕꯒꯤ ꯆꯥꯡ",
    },
    "Landslide Probability Index": {
        "asm_Beng": "ভূমিস্খলন সম্ভাৱনা সূচক",
        "ben_Beng": "ভূমিধস সম্ভাবনা সূচক",
        "npi_Deva": "पहिरो सम्भावना सूचकांक",
        "mni_Mtei": "ꯂꯩꯈꯥꯡꯕꯒꯤ ꯆꯥꯡꯒꯤ ꯏꯟꯗꯦꯛꯁ",
    },
    "Comparative Risk Probability Gauges": {
        "asm_Beng": "তুলনামূলক বিপদাশংকা সম্ভাৱনা গজ",
        "ben_Beng": "তুলনামূলক ঝুঁকি সম্ভাবনা গজ",
        "npi_Deva": "तुलनात्मक जोखिम सम्भावना गेजहरू",
        "mni_Mtei": "ꯆꯥꯡꯗꯝꯅꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯒꯦꯖ",
    },
    "Multi-Horizon Subsurface Soil Moisture Comparison": {
        "asm_Beng": "বহু-স্তৰীয় ভূগৰ্ভস্থ মাটিৰ আৰ্দ্ৰতা তুলনা",
        "ben_Beng": "বহু-স্তরীয় ভূগর্ভস্থ মাটির আর্দ্রতা তুলনা",
        "npi_Deva": "बहु-तह भू-सतह माटोको आर्द्रता तुलना",
        "mni_Mtei": "ꯂꯩꯃꯥꯏ ꯃꯅꯨꯡꯒꯤ ꯏꯁꯤꯡ ꯆꯥꯡꯗꯝꯅꯕꯥ",
    },
    "14-Day Comparative Forward Precipitation & Risk Trajectory": {
        "asm_Beng": "১৪ দিনৰ তুলনামূলক বৰষুণ আৰু বিপদাশংকাৰ গতিপথ",
        "ben_Beng": "১৪ দিনের তুলনামূলক বৃষ্টিপাত ও ঝুঁকির গতিপথ",
        "npi_Deva": "१४ दिने तुलनात्मक वर्षा तथा जोखिम प्रक्षेपण",
        "mni_Mtei": "ꯅꯨꯃꯤꯠ ১৪ꯒꯤ ꯆꯥꯡꯗꯝꯅꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ",
    },
    "Risk Factor Attribution": {
        "asm_Beng": "বিপদাশংকাৰ কাৰক বিশ্লেষণ",
        "ben_Beng": "ঝুঁকির কারণ বিশ্লেষণ",
        "npi_Deva": "जोखिम कारक विश्लेषण",
        "mni_Mtei": "ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯊꯣꯛꯍꯅꯕꯥ ꯃꯔꯃꯁꯤꯡ",
    },
    "Automated Email Alerts": {
        "asm_Beng": "স্বয়ংক্ৰিয় ইমেইল সতৰ্কবাৰ্তা",
        "ben_Beng": "স্বয়ংক্রিয় ইমেইল সতর্কতা",
        "npi_Deva": "स्वचालित इमेल चेतावनी",
        "mni_Mtei": "ꯑꯣꯇꯣꯃꯦꯇꯤꯛ ꯏ-ꯃꯦꯜ ꯆꯦꯀꯁꯤꯟ-ꯄꯥꯎ",
    },
    "Citizen / Field Geo-Reporting": {
        "asm_Beng": "নাগৰিক / ফিল্ড ভূ-প্ৰতিবেদন",
        "ben_Beng": "নাগরিক / মাঠপর্যায়ের ভূ-প্রতিবেদন",
        "npi_Deva": "नागरिक / क्षेत्रीय भू-प्रतिवेदन",
        "mni_Mtei": "ꯃꯤꯌꯥꯃꯒꯤ ꯂꯩꯈꯥꯡꯕꯥ ꯔꯤꯄꯣꯔ꯭ꯠ",
    },
    "Side-by-Side Risk Drivers": {
        "asm_Beng": "পাৰ্শ্ববৰ্তী বিপদাশংকা চালকসমূহ",
        "ben_Beng": "পাশাপাশি ঝুঁকির নিয়ামকসমূহ",
        "npi_Deva": "समानान्तर जोखिम कारकहरू",
        "mni_Mtei": "ꯅꯥꯀꯜ ꯑꯅꯤꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯃꯔꯃꯁꯤꯡ",
    },
    "Geomorphic & Terrain Matrix": {
        "asm_Beng": "ভূসংস্থান আৰু ভূভাগ মেট্ৰিক্স",
        "ben_Beng": "ভূ-প্রাকৃতিক ও ভূখণ্ড ম্যাট্রিক্স",
        "npi_Deva": "भू-आकृतिक तथा भू-भाग म्याट्रिक्स",
        "mni_Mtei": "ꯂꯩꯃꯥꯏ ꯑꯃꯁꯨꯡ ꯆꯤꯡꯖꯥꯎ ꯃꯦꯇ꯭ꯔꯤꯛꯁ",
    },
    "Weather Triggers Breakdown": {
        "asm_Beng": "বতৰৰ প্ৰৰোচক কাৰক বিশ্লেষণ",
        "ben_Beng": "আবহাওয়া প্রভাবকসমূহের বিশ্লেষণ",
        "npi_Deva": "मौसम ट्रिगरहरूको विश्लेषण",
        "mni_Mtei": "ꯅꯣꯡ-ꯆꯤꯡꯒꯤ ꯃꯔꯃꯁꯤꯡ",
    },
    "Primary Drivers Influencing Current Assessment": {
        "asm_Beng": "বৰ্তমান মূল্যায়নক প্ৰভাৱিত কৰা মুখ্য কাৰকসমূহ",
        "ben_Beng": "বর্তমান মূল্যায়নকে প্রভাবিতকারী মূল উপাদানসমূহ",
        "npi_Deva": "हालको मूल्याङ्कनलाई प्रभाव पार्ने मुख्य कारकहरू",
        "mni_Mtei": "ꯍꯧꯖꯤꯛ ꯑꯣꯏꯔꯤꯕꯥ ꯐꯤꯚꯝ ꯊꯣꯛꯍꯅꯕꯥ ꯃꯔꯨꯑꯣꯏꯕꯥ ꯃꯔꯃꯁꯤꯡ",
    },
    "Lithological & Terrain Overview:": {
        "asm_Beng": "শিলাতাত্ত্বিক আৰু ভূভাগৰ সংক্ষিপ্ত বিৱৰণ:",
        "ben_Beng": "শিলাতাত্ত্বিক ও ভূখণ্ডের সংক্ষিপ্ত বিবরণ:",
        "npi_Deva": "शिलातत्व तथा भू-भागको संक्षिप्त विवरण:",
        "mni_Mtei": "ꯅꯨꯡ ꯑꯃꯁꯨꯡ ꯂꯩꯃꯥꯏꯒꯤ ꯑꯄꯨꯅꯕꯥ ꯋꯥꯔꯦꯞ:",
    },
    "Geological Formation:": {
        "asm_Beng": "ভূতাত্ত্বিক গঠন:",
        "ben_Beng": "ভূতাত্ত্বিক গঠন:",
        "npi_Deva": "भूवैज्ञानिक संरचना:",
        "mni_Mtei": "ꯂꯩꯄꯥꯛꯀꯤ ꯂꯩꯐꯝ:",
    },
    "Critical Slope Threshold:": {
        "asm_Beng": "সংকটজনক ঢালৰ সীমা:",
        "ben_Beng": "সংকটজনক ঢালের সীমা:",
        "npi_Deva": "गम्भीर भीरको सीमा:",
        "mni_Mtei": "ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯆꯤꯡꯁꯤꯟ:",
    },
    "Relief Energy:": {
        "asm_Beng": "উচ্চতাৰ শক্তি:",
        "ben_Beng": "উচ্চতাগত শক্তি:",
        "npi_Deva": "उचाइ शक्ति:",
        "mni_Mtei": "ꯑꯋꯥꯡꯕꯥ ꯏꯅꯔꯖꯤ:",
    },
    "Corridor Assessment:": {
        "asm_Beng": "কৰিডৰ মূল্যায়ন:",
        "ben_Beng": "করিডোর মূল্যায়ন:",
        "npi_Deva": "करिडोर मूल्याङ्कन:",
        "mni_Mtei": "ꯂꯝꯕꯤꯒꯤ ꯋꯥꯔꯦꯞ:",
    },
    "Multi-Horizon Subsurface Soil Moisture Distribution": {
        "asm_Beng": "বহু-স্তৰীয় ভূগৰ্ভস্থ মাটিৰ আৰ্দ্ৰতা বিতৰণ",
        "ben_Beng": "বহু-স্তরীয় ভূগর্ভস্থ মাটির আর্দ্রতা বণ্টন",
        "npi_Deva": "बहु-तह भू-सतह माटोको आर्द्रता वितरण",
        "mni_Mtei": "ꯂꯩꯃꯥꯏ ꯃꯅꯨꯡꯒꯤ ꯏꯁꯤꯡ ꯌꯦꯟꯊꯣꯛꯄꯥ",
    },
    "Model Contribution Breakdown:": {
        "asm_Beng": "মডেল অৱদান বিশ্লেষণ:",
        "ben_Beng": "মডেল অবদান বিশ্লেষণ:",
        "npi_Deva": "मोडेल योगदान विश्लेषण:",
        "mni_Mtei": "ꯃꯣꯗꯦꯜꯒꯤ ꯃꯔꯨꯑꯣꯏꯕꯥ ꯃꯔꯃꯁꯤꯡ:",
    },
    "ML Geomorphic Baseline:": {
        "asm_Beng": "এমএল ভূ-ৰূপতাত্ত্বিক ভিত্তি:",
        "ben_Beng": "এমএল ভূ-প্রাকৃতিক ভিত্তি:",
        "npi_Deva": "ML भू-आकृतिक आधार रेखा:",
        "mni_Mtei": "ML ꯖꯤꯑꯣꯃꯣꯔꯐꯤꯛ ꯕꯦꯁꯂꯥꯏꯟ:",
    },
    "72h Rain Trigger Volume:": {
        "asm_Beng": "৭২ ঘণ্টাৰ বৰষুণৰ পৰিমাণ:",
        "ben_Beng": "৭২ ঘণ্টার বৃষ্টিপাতের পরিমাণ:",
        "npi_Deva": "७२ घण्टाको वर्षा मात्रा:",
        "mni_Mtei": "ꯄꯨꯡ ৭২ꯒꯤ ꯅꯣꯡ ꯆꯨꯕꯒꯤ ꯆꯥꯡ:",
    },
    "Volumetric Soil Moisture:": {
        "asm_Beng": "আয়তনিক মাটিৰ আৰ্দ্ৰতা:",
        "ben_Beng": "আয়তনিক মাটির আর্দ্রতা:",
        "npi_Deva": "आयतनिक माटोको आर्द्रता:",
        "mni_Mtei": "ꯂꯩꯃꯥꯏꯒꯤ ꯏꯁꯤꯡ ꯆꯥꯡ:",
    },
    "Model Driver Comparison:": {
        "asm_Beng": "মডেল নিয়ামক তুলনা:",
        "ben_Beng": "মডেল নিয়ামক তুলনা:",
        "npi_Deva": "मोडेल कारक तुलना:",
        "mni_Mtei": "ꯃꯣꯗꯦꯜ ꯃꯔꯃꯁꯤꯡ ꯆꯥꯡꯗꯝꯅꯕꯥ:",
    },
    "72h Rainfall Stress:": {
        "asm_Beng": "৭২ ঘণ্টাৰ বৰষুণৰ চাপ:",
        "ben_Beng": "৭২ ঘণ্টার বৃষ্টিপাতের চাপ:",
        "npi_Deva": "७२ घण्टाको वर्षा तनाव:",
        "mni_Mtei": "ꯄꯨꯡ ৭২ꯒꯤ ꯅꯣꯡ ꯆꯨꯕꯒꯤ ꯄ꯭ꯔꯦꯁꯔ:",
    },
    "Topsoil Moisture:": {
        "asm_Beng": "ওপৰৰ মাটিৰ আৰ্দ্ৰতা:",
        "ben_Beng": "উপরিভাগের মাটির আর্দ্রতা:",
        "npi_Deva": "माथिल्लो माटोको आर्द्रता:",
        "mni_Mtei": "ꯂꯩꯃꯥꯏꯒꯤ ꯏꯁꯤꯡ:",
    },
    "Risk Heatmap": {
        "asm_Beng": "বিপদাশংকা হিটমেপ",
        "ben_Beng": "ঝুঁকি হিটম্যাপ",
        "npi_Deva": "जोखिम हिटम्याप",
        "mni_Mtei": "ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯍꯤꯠꯃꯦꯞ",
    },
    "Hotspot Pins": {
        "asm_Beng": "হটস্পট পিন",
        "ben_Beng": "হটস্পট পিন",
        "npi_Deva": "हटस्पट पिनहरू",
        "mni_Mtei": "ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯃꯐꯃꯁꯤꯡ",
    },
    "Field Reports": {
        "asm_Beng": "ফিল্ড প্ৰতিবেদন",
        "ben_Beng": "মাঠের প্রতিবেদন",
        "npi_Deva": "क्षेत्रीय प्रतिवेदनहरू",
        "mni_Mtei": "ꯃꯐꯝ ꯑꯗꯨꯒꯤ ꯔꯤꯄꯣꯔ꯭ꯠ",
    },
    "Blur Radius": {
        "asm_Beng": "ব্লার ব্যাসাৰ্ধ",
        "ben_Beng": "ব্লার ব্যাসার্ধ",
        "npi_Deva": "ब्लर त्रिज्या",
        "mni_Mtei": "ꯕ꯭ꯂꯔ ꯔꯦꯗꯤꯌꯁ",
    },
    "Automated Early Warning Email Alert Service": {
        "asm_Beng": "স্বয়ংক্ৰিয় আগতীয় সতৰ্কবাৰ্তা ইমেইল সেৱা",
        "ben_Beng": "স্বয়ংক্রিয় প্রাথমিক সতর্কতা ইমেইল সেবা",
        "npi_Deva": "स्वचालित पूर्व चेतावनी इमेल सेवा",
        "mni_Mtei": "ꯑꯣꯇꯣꯃꯦꯇꯤꯛ ꯆꯦꯀꯁꯤꯟ-ꯄꯥꯎ ꯏ-ꯃꯦꯜ ꯁꯔꯚꯤꯁ",
    },
    "Resident & Visitor Safety Network": {
        "asm_Beng": "নাগৰিক আৰু দৰ্শনাৰ্থী সুৰক্ষা নেটৱৰ্ক",
        "ben_Beng": "বাসিন্দা ও দর্শনার্থী সুরক্ষা নেটওয়ার্ক",
        "npi_Deva": "बासिन्दा तथा आगन्तुक सुरक्षा सञ्जाल",
        "mni_Mtei": "ꯃꯤꯌꯥꯝ ꯑꯃꯁꯨꯡ ꯈꯣꯡꯆꯠꯄꯁꯤꯡꯒꯤ ꯉꯥꯛꯊꯣꯛꯅꯕꯥ",
    },
    "1. Register Resident Alert Preferences": {
        "asm_Beng": "১. নাগৰিক সতৰ্কবাৰ্তা পচন্দ পঞ্জীয়ন কৰক",
        "ben_Beng": "১. বাসিন্দার সতর্কবার্তা পছন্দ নিবন্ধন করুন",
        "npi_Deva": "१. बासिन्दा चेतावनी प्राथमिकता दर्ता गर्नुहोस्",
        "mni_Mtei": "১. ꯆꯦꯀꯁꯤꯟ-ꯄꯥꯎ ꯐꯪꯅꯕꯥ ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯕꯤꯌꯨ",
    },
    "Recipient Email Address": {
        "asm_Beng": "গ্ৰাহকৰ ইমেইল ঠিকনা",
        "ben_Beng": "প্রাপকের ইমেইল ঠিকানা",
        "npi_Deva": "प्राप्तकर्ताको इमेल ठेगाना",
        "mni_Mtei": "ꯏ-ꯃꯦꯜ ꯑꯦꯗ꯭ꯔꯦꯁ",
    },
    "State of Residence": {
        "asm_Beng": "বসবাসৰ ৰাজ্য",
        "ben_Beng": "বসবাসের রাজ্য",
        "npi_Deva": "बसोबास गर्ने राज्य",
        "mni_Mtei": "ꯂꯩꯔꯤꯕꯥ ꯁ꯭ꯇꯦꯠ",
    },
    "Living Region / Corridor": {
        "asm_Beng": "আবাসিক অঞ্চল / কৰিডৰ",
        "ben_Beng": "আবাসিক অঞ্চল / করিডোর",
        "npi_Deva": "बसोबास क्षेत्र / करिडोर",
        "mni_Mtei": "ꯂꯩꯔꯤꯕꯥ ꯃꯐꯝ / ꯂꯝꯕꯤ",
    },
    "Trigger Threshold Policy": {
        "asm_Beng": "সতৰ্কবাৰ্তা সীমা নীতি",
        "ben_Beng": "সতর্কবার্তা সীমা নীতিমালা",
        "npi_Deva": "चेतावनी सीमा नीति",
        "mni_Mtei": "ꯆꯦꯀꯁꯤꯟ-ꯄꯥꯎꯒꯤ ꯊꯥꯛ ꯊꯧꯔꯥꯡ",
    },
    "Critical High Risk (≥ 70%) — Recommended (NDMA / GSI Evacuation Advisory)": {
        "asm_Beng": "গুৰুতৰ উচ্চ বিপদাশংকা (≥ ৭০%) — পৰামৰ্শপ্ৰাপ্ত (NDMA / GSI স্থান ত্যাগ নিৰ্দেশনা)",
        "ben_Beng": "সংকটজনক উচ্চ ঝুঁকি (≥ ৭০%) — প্রস্তাবিত (NDMA / GSI নিরাপদ আশ্রয়ে যাওয়ার পরামর্শ)",
        "npi_Deva": "गम्भीर उच्च जोखिम (≥ ७०%) — सिफारिस गरिएको (NDMA / GSI सुरक्षित स्थानमा सर्ने सल्लाह)",
        "mni_Mtei": "ꯌꯥꯝꯅꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ (≥ 70%) — NDMA / GSI ꯉꯥꯛꯊꯣꯛꯅꯕꯥ ꯃꯐꯃꯗꯥ ꯆꯠꯄꯥ",
    },
    "Elevated Medium Risk (≥ 35%) — Precautionary Saturated Slope Vigilance": {
        "asm_Beng": "মধ্যম বিপদাশংকা (≥ ৩৫%) — সতৰ্কতামূলক ঢাল নিৰীক্ষণ",
        "ben_Beng": "মাঝারি ঝুঁকি (≥ ৩৫%) — সতর্কতামূলক পাহাড়ি ঢাল নজরদারি",
        "npi_Deva": "मध्यम जोखिम (≥ ३५%) — पूर्वसावधानी संतृप्त भीर सतर्कता",
        "mni_Mtei": "ꯃꯌꯥꯏ ꯑꯣꯏꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ (≥ 35%) — ꯆꯦꯀꯁꯤꯟ ꯊꯧꯔꯥꯡ",
    },
    "Custom Probability Threshold (%)": {
        "asm_Beng": "কাষ্টম সম্ভাৱনা সীমা (%)",
        "ben_Beng": "কাস্টম সম্ভাবনা সীমা (%)",
        "npi_Deva": "अनुकूलित सम्भावना सीमा (%)",
        "mni_Mtei": "ꯀꯁ꯭ꯇꯃ ꯆꯥꯡ (%)",
    },
    "🔔 Subscribe to Early Warning Alerts": {
        "asm_Beng": "🔔 আগতীয় সতৰ্কবাৰ্তাৰ বাবে পঞ্জীয়ন কৰক",
        "ben_Beng": "🔔 আগাম সতর্কবার্তার জন্য সাবস্ক্রাইব করুন",
        "npi_Deva": "🔔 पूर्व चेतावनीको लागि सदस्यता लिनुहोस्",
        "mni_Mtei": "🔔 ꯆꯦꯀꯁꯤꯟ-ꯄꯥꯎꯒꯤꯗꯃꯛ ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯕꯤꯌꯨ",
    },
    "2. Verify Delivery & Anti-Spam Compliance": {
        "asm_Beng": "২. ডেলিভাৰী আৰু এণ্টি-স্পেম অনুপালন পৰীক্ষা কৰক",
        "ben_Beng": "২. ডেলিভারি ও অ্যান্টি-স্প্যাম কমপ্লায়েন্স যাচাই করুন",
        "npi_Deva": "२. डेलिभरी र एन्टि-स्प्याम अनुपालन प्रमाणीकरण गर्नुहोस्",
        "mni_Mtei": "২. ꯏ-ꯃꯦꯜ ꯌꯧꯕꯥ ꯆꯦꯛ ꯇꯧꯕꯤꯌꯨ",
    },
    "📨 Send Immediate Test Alert Email": {
        "asm_Beng": "📨 তাৎক্ষণিক পৰীক্ষামূলক সতৰ্কবাৰ্তা ইমেইল প্ৰেৰণ কৰক",
        "ben_Beng": "📨 তাৎক্ষণিক পরীক্ষামূলক সতর্কতা ইমেইল পাঠান",
        "npi_Deva": "📨 तत्काल परीक्षण चेतावनी इमेल पठाउनुहोस्",
        "mni_Mtei": "📨 ꯍꯧꯖꯤꯛ ꯇꯦꯁ꯭ꯠ ꯏ-ꯃꯦꯜ ꯊꯥꯕꯤꯌꯨ",
    },
    "Real-Time Citizen & Ground Crew Landslide Reporting": {
        "asm_Beng": "প্ৰকৃত-সময়ৰ নাগৰিক আৰু ফিল্ড ক্ৰু ভূমিস্খলন প্ৰতিবেদন",
        "ben_Beng": "রিয়েল-টাইম নাগরিক ও মাঠপর্যায়ের কর্মী ভূমিধস প্রতিবেদন",
        "npi_Deva": "वास्तविक समयको नागरिक तथा क्षेत्रीय टोली पहिरो प्रतिवेदन",
        "mni_Mtei": "ꯔꯤꯑꯦꯜ-ꯇꯥꯏꯝ ꯃꯤꯌꯥꯃꯒꯤ ꯂꯩꯈꯥꯡꯕꯥ ꯔꯤꯄꯣꯔ꯭ꯠ",
    },
    "1. Capture or Upload Field Photo": {
        "asm_Beng": "১. ফিল্ডৰ ফটো তোলক বা আপলোড কৰক",
        "ben_Beng": "১. মাঠের ছবি তুলুন বা আপলোড করুন",
        "npi_Deva": "१. फिल्डको फोटो लिनुहोस् वा अपलोड गर्नुहोस्",
        "mni_Mtei": "১. ꯐꯣꯇꯣ ꯀꯦꯞꯆꯔ ꯅꯠꯇ꯭ꯔꯒꯥ ꯑꯄꯂꯣꯗ ꯇꯧꯕꯤꯌꯨ",
    },
    "2. Geolocation & Incident Telemetry": {
        "asm_Beng": "২. ভৌগোলিক অৱস্থান আৰু ঘটনাৰ টেলিমেট্ৰি",
        "ben_Beng": "২. ভৌগোলিক অবস্থান ও ঘটনার টেলিমেট্রি",
        "npi_Deva": "२. भौगोलिक स्थान र घटना टेलिमेट्री",
        "mni_Mtei": "২. ꯃꯐꯝ ꯑꯃꯁꯨꯡ ꯊꯧꯗꯣꯛꯀꯤ ꯐꯤꯚꯝ",
    },
    "Recent Field Incidents Log (SQLite Database)": {
        "asm_Beng": "শেহতীয়া ফিল্ড ঘটনাৰ লগ (SQLite ডেটাবেছ)",
        "ben_Beng": "সাম্প্রতিক মাঠের ঘটনার লগ (SQLite ডেটাবেস)",
        "npi_Deva": "हालका क्षेत्रीय घटनाहरूको लग (SQLite डाटाबेस)",
        "mni_Mtei": "ꯍꯟꯗꯛ ꯊꯣꯛꯈꯤꯕꯥ ꯊꯧꯗꯣꯛꯁꯤꯡ (SQLite ꯗꯥꯇꯥꯕꯦꯁ)",
    },
    "North Eastern Region Landslide Early Warning System | Dual-Station Satellite Telemetry (Open-Meteo) | LightGBM ML Geomorphic Engine | Developed for Scientific Disaster Risk Reduction": {
        "asm_Beng": "উত্তৰ-পূব অঞ্চল ভূমিস্খলন আগতীয় সতৰ্কবাৰ্তা ব্যৱস্থা | দ্বৈত-কেন্দ্ৰীয় উপগ্ৰহীয় টেলিমেট্ৰি | LightGBM এমএল ইঞ্জিন | বৈজ্ঞানিক দুৰ্যোগ বিপদাশংকা প্ৰশমনৰ বাবে বিকশিত",
        "ben_Beng": "উত্তর-পূর্ব অঞ্চল ভূমিধস প্রাথমিক সতর্কতা ব্যবস্থা | দ্বৈত-স্টেশন স্যাটেলাইট টেলিমেট্রি | LightGBM এমএল ইঞ্জিন | বৈজ্ঞানিক দুর্যোগ ঝুঁকি হ্রাসের লক্ষ্যে তৈরি",
        "npi_Deva": "उत्तर-पूर्वी क्षेत्र पहिरो पूर्व चेतावनी प्रणाली | दोहोरो स्टेशन उपग्रह टेलिमेट्री | LightGBM ML इन्जिन | वैज्ञानिक प्रकोप जोखिम न्यूनीकरणको लागि विकसित",
        "mni_Mtei": "ꯑꯋꯥꯡ-ꯅꯣꯡꯄꯣꯛ ꯂꯃꯗꯝꯒꯤ ꯂꯩꯈꯥꯡꯕꯒꯤ ꯃꯃꯥꯡ ꯆꯦꯀꯁꯤꯟ-ꯊꯧꯔꯥꯡ ꯁꯤꯁ꯭ꯇꯦꯝ | ꯁꯦꯇꯦꯂꯥꯏꯠ ꯇꯦꯂꯤꯃꯦꯇ꯭ꯔꯤ | LightGBM ML ꯃꯣꯗꯦꯜ",
    },
    "100% SPAM-SAFE DELIVERABILITY": {
        "asm_Beng": "১০০% স্পেম-মুক্ত নিৰাপদ প্ৰেৰণ",
        "ben_Beng": "১০০% স্প্যাম-মুক্ত নিরাপদ বিতরণ",
        "npi_Deva": "१००% स्प्याम-मुक्त सुरक्षित वितरण",
        "mni_Mtei": "100% ꯁ꯭ꯄꯥꯝ-ꯐ꯭ꯔꯤ ꯑꯣꯏꯕꯥ",
    },
    "Register your email address to receive immediate meteorological and geomorphic hazard warnings when predicted landslide failure probability surpasses your customized risk threshold.": {
        "asm_Beng": "পূৰ্বানুমান কৰা ভূমিস্খলনৰ বিপদাশংকা নিৰ্ধাৰিত সীমা অতিক্ৰম কৰিলে লগে লগে বতৰ আৰু ভূ-ৰূপতাত্ত্বিক সতৰ্কবাৰ্তা লাভ কৰিবলৈ ইমেইল পঞ্জীয়ন কৰক।",
        "ben_Beng": "পূর্বাভাসকৃত ভূমিধসের ঝুঁকি আপনার নির্ধারিত সীমা অতিক্রম করলে তাৎক্ষণিক আবহাওয়া ও ভূ-প্রাকৃতিক সতর্কতা পেতে ইমেইল নিবন্ধন করুন।",
        "npi_Deva": "पहिरोको जोखिम तपाईंको अनुकूलित सीमाभन्दा बढी भएमा तत्काल मौसम तथा भू-आकृतिक चेतावनी प्राप्त गर्न आफ्नो इमेल दर्ता गर्नुहोस्।",
        "mni_Mtei": "ꯂꯩꯈꯥꯡꯕꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯊꯥꯛ ꯍꯦꯟꯒꯠꯂꯛꯄꯥ ꯃꯇꯃꯗꯥ ꯈꯨꯗꯛꯇꯥ ꯏ-ꯃꯦꯜ ꯄꯥꯎ ꯐꯪꯅꯕꯥ ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯕꯤꯌꯨ।",
    },
    "Perform an immediate SMTP test dispatch to verify that GroundCheck alerts arrive directly into your primary inbox (not Spam or Promotions).": {
        "asm_Beng": "গ্ৰাউণ্ডচেক সতৰ্কবাৰ্তা স্পেম বা প্ৰম'চনৰ সলনি প্ৰাথমিক ইনবক্সত প্ৰৱেশ কৰাটো নিশ্চিত কৰিবলৈ তাৎক্ষণিক SMTP পৰীক্ষা কৰক।",
        "ben_Beng": "গ্রাউন্ডচেক সতর্কতা স্প্যাম বা প্রমোশনের বদলে সরাসরি প্রাথমিক ইনবক্সে পৌঁছানো নিশ্চিত করতে তাত্ক্ষণিক SMTP পরীক্ষা চালান।",
        "npi_Deva": "ग्राउन्डचेक चेतावनीहरू स्प्यामको सट्टा सिधै तपाईंको प्राथमिक इनबक्समा आइपुग्छ भनी प्रमाणित गर्न तत्काल SMTP परीक्षण पठाउनुहोस्।",
        "mni_Mtei": "GroundCheck ꯄꯥꯎ ꯑꯁꯤ ꯏꯟꯕꯣꯛꯁꯇꯥ ꯍꯛꯊꯦꯡꯅꯅꯥ ꯌꯧꯕꯥ ꯆꯦꯛ ꯇꯧꯅꯕꯥ SMTP ꯇꯦꯁ꯭ꯠ ꯇꯧꯕꯤꯌꯨ।",
    },
    "Send Instant Verification To:": {
        "asm_Beng": "তাৎক্ষণিক সত্যাসত্য নিৰূপণ প্ৰেৰণ কৰক:",
        "ben_Beng": "তাত্ক্ষণিক যাচাইকরণ পাঠান:",
        "npi_Deva": "तत्काल प्रमाणीकरण पठाउनुहोस्:",
        "mni_Mtei": "ꯇꯦꯁ꯭ꯠ ꯄꯥꯎ ꯊꯥꯅꯕꯥ:",
    },
    "Select Custom Alert Threshold (%)": {
        "asm_Beng": "কাষ্টম সতৰ্কবাৰ্তা সীমা নিৰ্বাচন কৰক (%)",
        "ben_Beng": "কাস্টম সতর্কতা সীমা নির্বাচন করুন (%)",
        "npi_Deva": "अनुकूलित चेतावनी सीमा चयन गर्नुहोस् (%)",
        "mni_Mtei": "ꯀꯁ꯭ꯇꯃ ꯆꯦꯀꯁꯤꯟ-ꯊꯥꯛ ꯈꯅꯕꯤꯌꯨ (%)",
    },
    "Gmail Spam Prevention Knowledge Base & Standards": {
        "asm_Beng": "Gmail স্পেম প্ৰতিৰোধ জ্ঞানকোষ আৰু মানক",
        "ben_Beng": "Gmail স্প্যাম প্রতিরোধ জ্ঞানকোষ ও মানক",
        "npi_Deva": "Gmail स्प्याम रोकथाम ज्ञान आधार तथा मानकहरू",
        "mni_Mtei": "Gmail ꯁ꯭ꯄꯥꯝ ꯊꯤꯡꯕꯒꯤ ꯃꯔꯨꯑꯣꯏꯕꯥ ꯋꯥꯐꯃꯁꯤꯡ",
    },
    "Manage Active Subscriptions & Opt-Out": {
        "asm_Beng": "সক্ৰিয় পঞ্জীয়ন পৰিচালনা আৰু অপ্ট-আউট",
        "ben_Beng": "সক্রিয় সাবস্ক্রিপশন পরিচালনা ও অপ্ট-আউট",
        "npi_Deva": "सक्रिय सदस्यताहरू व्यवस्थापन तथा अप्ट-आउट",
        "mni_Mtei": "ꯁꯕꯁ꯭ꯛꯔꯤꯄꯁꯟ ꯃꯦꯅꯦꯖ ꯇꯧꯕꯥ",
    },
    "Total Registered Subscribers:": {
        "asm_Beng": "মুঠ পঞ্জীভুক্ত নাগৰিক:",
        "ben_Beng": "মোট নিবন্ধিত গ্রাহক:",
        "npi_Deva": "कुल दर्ता भएका बासिन्दाहरू:",
        "mni_Mtei": "ꯑꯄꯨꯅꯕꯥ ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯔꯕꯥ ꯃꯤꯌꯥꯝ:",
    },
    "Unsubscribe Email": {
        "asm_Beng": "আনচাবস্ক্ৰাইব ইমেইল",
        "ben_Beng": "আনসাবস্ক্রাইব ইমেইল",
        "npi_Deva": "सदस्यता रद्द गर्ने इमेल",
        "mni_Mtei": "ꯑꯅꯁꯕꯁ꯭ꯛꯔꯥꯏꯕ ꯏ-ꯃꯦꯜ",
    },
    "Unsubscribe": {
        "asm_Beng": "আনচাবস্ক্ৰাইব কৰক",
        "ben_Beng": "আনসাবস্ক্রাইব করুন",
        "npi_Deva": "सदस्यता रद्द गर्नुहोस्",
        "mni_Mtei": "ꯑꯅꯁꯕꯁ꯭ꯛꯔꯥꯏꯕ ꯇꯧꯕꯤꯌꯨ",
    },
    "Why GroundCheck Emails Bypass Spam Filters:": {
        "asm_Beng": "গ্ৰাউণ্ডচেক ইমেইলবোৰে স্পেম ফিল্টাৰ কিয় এৰাই চলে:",
        "ben_Beng": "কেন গ্রাউন্ডচেক ইমেইল স্প্যাম ফিল্টার এড়িয়ে যায়:",
        "npi_Deva": "किन ग्राउन्डचेक इमेलहरूले स्प्याम फिल्टरहरू बाइपास गर्छन्:",
        "mni_Mtei": "GroundCheck ꯏ-ꯃꯦꯜ ꯁ꯭ꯄꯥꯃꯗꯥ ꯆꯪꯗꯕꯒꯤ ꯃꯔꯝ:",
    },
    "Zero Panic Terminology:": {
        "asm_Beng": "আতংকজনক শব্দবৰ্জন:",
        "ben_Beng": "আতঙ্কজনক শব্দবর্জন:",
        "npi_Deva": "शून्य आतंक शब्दावली:",
        "mni_Mtei": "ꯄꯦꯅꯤꯛ ꯋꯥꯍꯩ ꯌꯥꯑꯣꯗꯕꯥ:",
    },
    "RFC 8058 Compliant:": {
        "asm_Beng": "RFC ৮০৫৮ অনুপালন:",
        "ben_Beng": "RFC ৮০৫৮ সামঞ্জস্যপূর্ণ:",
        "npi_Deva": "RFC ८०५८ अनुरूप:",
        "mni_Mtei": "RFC 8058 ꯒꯥ ꯆꯨꯅꯕꯥ:",
    },
    "No Tracking Anchors:": {
        "asm_Beng": "ট্ৰেকিংহীন নিৰাপদ লিংক:",
        "ben_Beng": "ট্র্যাকিংহীন লিঙ্ক:",
        "npi_Deva": "कुनै ट्र्याकिङ लिङ्कहरू छैनन्:",
        "mni_Mtei": "ꯇ꯭ꯔꯦꯛ ꯇꯧꯗꯕꯥ ꯂꯤꯡꯛ:",
    },
    "Take Live Ground Photo": {
        "asm_Beng": "প্ৰত্যক্ষ ফিল্ড ফটো তোলক",
        "ben_Beng": "সরাসরি মাঠের ছবি তুলুন",
        "npi_Deva": "प्रत्यक्ष फिल्ड फोटो लিনुहोस्",
        "mni_Mtei": "ꯍꯧꯖꯤꯛ ꯐꯣꯇꯣ ꯀꯦꯞꯆꯔ ꯇꯧꯕꯤꯌꯨ",
    },
    "Or Upload Existing Photo (JPG/PNG)": {
        "asm_Beng": "বা বৰ্তমানৰ ফটো আপলোড কৰক (JPG/PNG)",
        "ben_Beng": "অথবা বিদ্যমান ছবি আপলোড করুন (JPG/PNG)",
        "npi_Deva": "वा अवस्थित फोटो अपलोड गर्नुहोस् (JPG/PNG)",
        "mni_Mtei": "ꯅꯠꯇ꯭ꯔꯒꯥ ꯐꯣꯇꯣ ꯑꯄꯂꯣꯗ ꯇꯧꯕꯤꯌꯨ (JPG/PNG)",
    },
    "Corridor / Landmark Name": {
        "asm_Beng": "কৰিডৰ / পৰিচিত স্থানৰ নাম",
        "ben_Beng": "করিডোর / পরিচিত স্থানের নাম",
        "npi_Deva": "करिडोर / स्थलचिन्ह नाम",
        "mni_Mtei": "ꯂꯝꯕꯤ / ꯃꯃꯤꯡ ꯂꯩꯕꯥ ꯃꯐꯝ",
    },
    "Observed Hazard Type": {
        "asm_Beng": "প্ৰত্যক্ষ কৰা বিপদাশংকাৰ প্ৰকাৰ",
        "ben_Beng": "প্রত্যক্ষকৃত বিপদের ধরন",
        "npi_Deva": "प्रत्यक्ष देखिएको प्रकोप प्रकार",
        "mni_Mtei": "ꯎꯕꯥ ꯐꯪꯂꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ",
    },
    "Incident Severity": {
        "asm_Beng": "ঘটনাৰ গুৰুত্ব",
        "ben_Beng": "ঘটনার তীব্রতা",
        "npi_Deva": "घटनाको गम्भीरता",
        "mni_Mtei": "ꯊꯧꯗꯣꯛꯀꯤ ꯀꯟꯅꯕꯥ",
    },
    "Field Description & Road Status": {
        "asm_Beng": "ফিল্ড বিৱৰণ আৰু পথৰ অৱস্থা",
        "ben_Beng": "মাঠের বিবরণ ও রাস্তার অবস্থা",
        "npi_Deva": "फिल्ड विवरण तथा सडक स्थिति",
        "mni_Mtei": "ꯃꯐꯝ ꯑꯗꯨꯒꯤ ꯋꯥꯔꯣꯜ ꯑꯃꯁꯨꯡ ꯂꯝꯕꯤꯒꯤ ꯐꯤꯚꯝ",
    },
    "Reporter Name / Agency": {
        "asm_Beng": "প্ৰতিবেদকৰ নাম / সংস্থা",
        "ben_Beng": "প্রতিবেদনকারীর নাম / সংস্থা",
        "npi_Deva": "प्रतिवेदकको नाम / निकाय",
        "mni_Mtei": "ꯔꯤꯄꯣꯔ꯭ꯠ ꯇꯧꯔꯤꯕꯥ ꯃꯤꯑꯣꯏ / ꯑꯦꯖꯦꯟꯁꯤ",
    },
    "🚀 Transmit Geo-Tagged Field Report": {
        "asm_Beng": "🚀 জিঅ'-টেগযুক্ত ফিল্ড প্ৰতিবেদন প্ৰেৰণ কৰক",
        "ben_Beng": "🚀 জিও-ট্যাগযুক্ত মাঠের প্রতিবেদন প্রেরণ করুন",
        "npi_Deva": "🚀 भू-ट्याग गरिएको फिल्ड प्रतिवेदन पठाउनुहोस्",
        "mni_Mtei": "🚀 ꯖꯤꯑꯣ-ꯇꯦꯒ ꯇꯧꯔꯕꯥ ꯔꯤꯄꯣꯔ꯭ꯠ ꯊꯥꯕꯤꯌꯨ",
    },
    "Comprehensive Terrain & Geomorphic Profile Matrix": {
        "asm_Beng": "বিস্তৃত ভূভাগ আৰু ভূ-ৰূপতাত্ত্বিক প্ৰ'ফাইল মেট্ৰিক্স",
        "ben_Beng": "বিস্তারিত ভূখণ্ড ও ভূ-প্রাকৃতিক প্রোফাইল ম্যাট্রিক্স",
        "npi_Deva": "विस्तृत भू-भाग तथा भू-आकृतिक प्रोफाइल म्याट्रिक्स",
        "mni_Mtei": "ꯂꯩꯃꯥꯏ ꯑꯃꯁꯨꯡ ꯆꯤꯡꯖꯥꯎꯒꯤ ꯑꯄꯨꯅꯕꯥ ꯃꯦꯇ꯭ꯔꯤꯛꯁ",
    },
    "Detailed Meteorological & Hydrological Telemetry Breakdown": {
        "asm_Beng": "বিস্তাৰিত বতৰবিজ্ঞান আৰু জলবিজ্ঞান টেলিমেট্ৰি বিশ্লেষণ",
        "ben_Beng": "বিস্তারিত আবহাওয়া ও জলতাত্ত্বিক টেলিমেট্রি বিশ্লেষণ",
        "npi_Deva": "विस्तृत मौसम तथा जलविज्ञान टेलिमेट्री विश्लेषण",
        "mni_Mtei": "ꯅꯣꯡ-ꯆꯤꯡ ꯑꯃꯁꯨꯡ ꯏꯁꯤꯡꯒꯤ ꯐꯤꯚꯝ ꯋꯥꯔꯦꯞ",
    },
    "Empower frontline patrols, village disaster volunteers, and motorists to capture and transmit geo-tagged photographic evidence directly to the active geospatial database.": {
        "asm_Beng": "সক্ৰিয় ভৌগোলিক ডেটাবেছলৈ প্ৰত্যক্ষভাৱে জিঅ'-টেগযুক্ত ফটো প্ৰেৰণ কৰিবলৈ ফ্ৰন্টলাইন পেট্ৰ'ল, গাঁৱৰ দুৰ্যোগ স্বেচ্ছাসেৱক আৰু চালকসকলক সৱলীকৰণ কৰক।",
        "ben_Beng": "সক্রিয় ভূ-স্থানিক ডেটাবেসে সরাসরি জিও-ট্যাগযুক্ত ছবি পাঠাতে ফ্রন্টলাইন টহলদার, গ্রামের দুর্যোগ স্বেচ্ছাসেবক এবং চালকদের ক্ষমতায়ন করুন।",
        "npi_Deva": "सक्रिय भू-स्थानिक डाटाबेसमा सिधै भू-ट्याग गरिएका तस्बिरहरू पठाउन अग्रपङ्क्ति गस्ती, गाउँका विपद् स्वयंसेवक र चालकहरूलाई सशक्त बनाउनुहोस्।",
        "mni_Mtei": "ꯃꯐꯃꯒꯤ ꯐꯣꯇꯣ ꯀꯦꯞꯆꯔ ꯇꯧꯗꯨꯅꯥ ꯗꯥꯇꯥꯕꯦꯁꯇꯥ ꯊꯥꯅꯕꯥ ꯃꯤꯌꯥꯃꯗꯥ ꯈꯨꯗꯣꯡꯆꯥꯕꯥ ꯄꯤꯕꯥ।",
    },
    "Primary Hazard Contributing Factors Comparison": {
        "asm_Beng": "মুখ্য বিপদাশংকা কাৰকসমূহৰ তুলনা",
        "ben_Beng": "প্রধান ঝুঁকি নিয়ামকসমূহের তুলনা",
        "npi_Deva": "मुख्य जोखिम कारकहरूको तुलना",
        "mni_Mtei": "ꯃꯔꯨꯑꯣꯏꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯃꯔꯃꯁꯤꯡ ꯆꯥꯡꯗꯝꯅꯕꯥ",
    },
}


@st.cache_resource
def load_model():
    """
    Loads and caches the IndicTrans2 model, tokenizer, and processor.
    Uses @st.cache_resource to ensure single-instance loading across app reruns.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not hf_token:
        try:
            hf_token = st.secrets.get("HF_TOKEN", None)
        except Exception:
            hf_token = None

    # Step 1: Try official model if token is available
    if hf_token:
        try:
            tokenizer = AutoTokenizer.from_pretrained(PRIMARY_MODEL, trust_remote_code=True, token=hf_token)
            model = AutoModelForSeq2SeqLM.from_pretrained(PRIMARY_MODEL, trust_remote_code=True, token=hf_token).to(device)
            processor = IndicProcessor(inference=True)
            return tokenizer, model, processor, device
        except Exception:
            pass

    # Step 2: Use public ungated rotary model with dynamic tie_weights compatibility patch
    try:
        from transformers.models.auto.auto_factory import get_class_from_dynamic_module
        cls = get_class_from_dynamic_module(
            "modeling_rotary_indictrans.RotaryIndicTransForConditionalGeneration",
            FALLBACK_MODEL
        )
        # Patch tie_weights for Transformers 5.x compatibility
        cls.tie_weights = lambda self, *a, **kw: setattr(
            self.lm_head, "weight", self.model.decoder.embed_tokens.weight
        ) if hasattr(self, "lm_head") and hasattr(self, "model") else None

        tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL, trust_remote_code=True)
        model = AutoModelForSeq2SeqLM.from_pretrained(FALLBACK_MODEL, trust_remote_code=True).to(device)
        processor = IndicProcessor(inference=True)
        return tokenizer, model, processor, device
    except Exception as err:
        return None, None, None, None


def translate_text(text: str, target_lang: str) -> str:
    """
    Translates input text from English into the specified Indic target language.
    
    Architecture:
    1. Instant Catalog Lookup: Standard disaster alerts, risk phrases, headings, and SOP
       are translated with zero latency (<1ms) using verified native scripts.
    2. Prefix/Suffix Normalization: Strips bullets and colons for resilient matching.
    3. Dynamic IndicTrans2 Engine: Freeform or dynamic text is passed to the neural model.
    4. Fail-Safe: Always falls back cleanly to the original English text on any error.
    """
    if not text or not str(text).strip():
        return text

    if target_lang == "eng_Latn":
        return text

    raw_text = str(text).strip()

    # Normalize known prefix decorators
    prefix = ""
    clean_text = raw_text
    for p in ["● ", "🔥 ", "📸 ", "🔔 ", "🌤️ ", "🚨 ", "⚠️ ", "📍 ", "🌐 "]:
        if clean_text.startswith(p):
            prefix = p
            clean_text = clean_text[len(p):].strip()
            break

    # Normalize trailing colons
    suffix = ""
    if clean_text.endswith(":"):
        suffix = ":"
        clean_text = clean_text[:-1].strip()

    # 1. Check exact catalog match
    if clean_text in TRANSLATION_CATALOG:
        lang_dict = TRANSLATION_CATALOG[clean_text]
        if target_lang in lang_dict:
            return f"{prefix}{lang_dict[target_lang]}{suffix}"

    # 2. Check case-insensitive match
    for k, v in TRANSLATION_CATALOG.items():
        if k.lower() == clean_text.lower():
            if target_lang in v:
                return f"{prefix}{v[target_lang]}{suffix}"

    # Check un-normalized raw_text in catalog as fallback
    if raw_text in TRANSLATION_CATALOG:
        if target_lang in TRANSLATION_CATALOG[raw_text]:
            return TRANSLATION_CATALOG[raw_text][target_lang]

    # 3. Dynamic Template Translations for GroundCheck Alerts
    # Critical Hazard Alert Active
    if clean_text.startswith("Critical Hazard Alert Active"):
        translations = {
            "asm_Beng": "জৰুৰীকালীন ভূমিস্খলন সতৰ্কবাৰ্তা: বৰষুণ আৰু মাটিৰ আৰ্দ্ৰতাই বিপদসীমা অতিক্ৰম কৰিছে। পাহাৰীয়া পথ আৰু খহনীয়া অঞ্চল এৰক। প্ৰশাসনে নিৰ্দেশ দিলে তৎক্ষণাৎ স্থান ত্যাগ কৰক (Evacuate Immediately)।",
            "ben_Beng": "জরুরি ভূমিধস সতর্কতা: অতিরিক্ত বৃষ্টিপাত ও মাটির আর্দ্রতা বিপদসীমা অতিক্রম করেছে। পাহাড়ি ঢাল এড়িয়ে চলুন। স্থানীয় কর্তৃপক্ষের নির্দেশ মোতাবেক অবিলম্বে নিরাপদ আশ্রয়ে যান (Evacuate Immediately)।",
            "npi_Deva": "गम्भीर पहिरो चेतावनी: अत्यधिक वर्षा र माटोको संतृप्तिले सुरक्षा सीमा पार गरेको छ। भिरालो सडकहरूबाट टाढा रहनुहोस्। निर्देशन दिइएमा तुरुन्तै सुरक्षित स्थानमा जानुहोस् (Evacuate Immediately)।",
            "mni_Mtei": "ꯌꯥꯝꯅꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯒꯤ ꯆꯦꯀꯁꯤꯟ-ꯊꯧꯔꯥꯡ: ꯅꯣꯡ ꯌꯥꯝꯅꯥ ꯆꯨꯕꯅꯥ ꯂꯩꯈꯥꯡꯕꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯂꯩꯔꯦ। ꯂꯝꯕꯤ-ꯆꯤꯡꯖꯥꯎꯗꯥ ꯂꯩꯕꯤꯒꯅꯨ। ꯈꯨꯗꯛꯇꯥ ꯉꯥꯛꯊꯣꯛꯅꯕꯥ ꯃꯐꯃꯗꯥ ꯆꯠꯂꯨ (Evacuate Immediately)।",
        }
        return translations.get(target_lang, clean_text)

    # Elevated Slope Stability Advisory
    if clean_text.startswith("Elevated Slope Stability Advisory"):
        translations = {
            "asm_Beng": "পাহাৰীয়া ঢাল স্থিৰতা পৰামৰ্শ: মাটিত মজলীয়া আৰ্দ্ৰতা ধৰা পৰিছে। ধাৰাবাহিক বৰষুণে স্থানীয় খহনীয়া সৃষ্টি কৰিব পাৰে। যাতায়াতৰ সময়ত সতৰ্কতা অৱলম্বন কৰক।",
            "ben_Beng": "উচ্চ পাহাড়ি ঢাল স্থিতিশীলতা পরামর্শ: মাটিতে মাঝারি মাত্রার আর্দ্রতা শনাক্ত হয়েছে। একটানা বৃষ্টিতে স্থানীয় ভূমিধস ঘটতে পারে। যাতায়াতের পথে সতর্ক থাকুন।",
            "npi_Deva": "उच्च भीर स्थिरता सल्लाह: माटोमा मध्यम संतृप्ति पाइएको छ। निरन्तर वर्षाले पहिरो निम्त्याउन सक्छ। सडक यात्रामा विशेष सतर्कता अपनाउनुहोस्।",
            "mni_Mtei": "ꯆꯤꯡꯖꯥꯎ ꯂꯩꯈꯥꯡꯕꯒꯤ ꯆꯦꯀꯁꯤꯟ ꯋꯥꯐꯝ: ꯂꯩꯃꯥꯏꯗꯥ ꯏꯁꯤꯡ ꯂꯩꯕꯅꯥ ꯂꯩꯈꯥꯡꯕꯥ ꯌꯥꯏ। ꯂꯝꯕꯤ-ꯆꯠꯊꯣꯛ-ꯆꯠꯁꯤꯟ ꯇꯧꯕꯗꯥ ꯆꯦꯀꯁꯤꯅꯕꯤꯌꯨ।",
        }
        return translations.get(target_lang, clean_text)

    # Normal Baseline Stability
    if clean_text.startswith("Normal Baseline Stability"):
        translations = {
            "asm_Beng": "স্বাভাৱিক স্থিৰতা অৱস্থা: বৰ্তমান বতৰত ভূমিস্খলনৰ সম্ভাৱনা কম। স্বাভাৱিক সতৰ্কতা বৰ্তাই ৰাখক।",
            "ben_Beng": "স্বাভাবিক স্থিতিশীল অবস্থা: বিদ্যমান আবহাওয়ায় ভূমিধসের ঝুঁকি কম। স্বাভাবিক সতর্কতা বজায় রাখুন।",
            "npi_Deva": "सामान्य स्थिरता अवस्था: हालको मौसममा पहिरोको जोखिम न्यून छ। सामान्य सतर्कता कायम राख्नुहोस्।",
            "mni_Mtei": "ꯅꯣꯔꯃꯦꯜ ꯑꯣꯏꯕꯥ ꯐꯤꯚꯝ: ꯅꯣꯡ-ꯆꯤꯡꯒꯤ ꯐꯤꯚꯝꯗꯥ ꯂꯩꯈꯥꯡꯕꯒꯤ ꯈꯨꯗꯣꯡꯊꯤꯕꯥ ꯅꯦꯝꯃꯤ।",
        }
        return translations.get(target_lang, clean_text)

    # Comparative Hazard Assessment Summary
    if clean_text.startswith("Comparative Hazard Assessment Summary"):
        translations = {
            "asm_Beng": "তুলনামূলক বিপদাশংকা নিৰূপণ সাৰাংশ: পিন কৰা স্থান দুটাৰ ঢাল, পূৰ্ববৰ্তী বৰষুণ আৰু মাটিৰ আৰ্দ্ৰতাৰ তথ্য বিশ্লেষণ কৰি বিপদাশংকা নিৰ্ণয় কৰা হৈছে।",
            "ben_Beng": "তুলনামূলক ঝুঁকি মূল্যায়ন সারসংক্ষেপ: পিন করা দুটি অবস্থানের ঢাল, পূর্ববর্তী বৃষ্টিপাত ও মাটির আর্দ্রতা বিশ্লেষণ করে ঝুঁকির তারতম্য নির্ণয় করা হয়েছে।",
            "npi_Deva": "तुलनात्मक जोखिम मूल्याङ्कन सारांश: पिन गरिएका दुई स्थानहरूको भिरालोपन, पूर्व वर्षा र माटोको संतृप्तिको विश्लेषण गरी जोखिम निर्धारण गरिएको छ।",
            "mni_Mtei": "ꯆꯥꯡꯗꯝꯅꯕꯥ ꯈꯨꯗꯣꯡꯊꯤꯕꯒꯤ ꯋꯥꯔꯦꯞ: ꯄꯤꯟ ꯇꯧꯔꯕꯥ ꯃꯐꯝ ꯑꯅꯤꯒꯤ ꯆꯤꯡꯖꯥꯎ, ꯅꯣꯡ ꯆꯨꯕꯥ ꯑꯃꯁꯨꯡ ꯂꯩꯃꯥꯏꯒꯤ ꯏꯁꯤꯡ ꯆꯥꯡ ꯌꯦꯡꯗꯨꯅꯥ ꯈꯦꯠꯅꯕꯥ ꯎꯠꯂꯤ।",
        }
        return translations.get(target_lang, clean_text)

    # Automated Early Warning Dispatched
    if "Automated Early Warning Dispatched" in clean_text:
        translations = {
            "asm_Beng": "স্বয়ংক্ৰিয় সতৰ্কবাৰ্তা প্ৰেৰণ কৰা হৈছে: পঞ্জীভুক্ত নাগৰিকসকললৈ ইমেইলযোগে সতৰ্কবাৰ্তা প্ৰেৰণ কৰা হ'ল।",
            "ben_Beng": "স্বয়ংক্রিয় প্রাক-সতর্কবার্তা প্রেরিত: নিবন্ধিত বাসিন্দাদের ইমেইলে সতর্কতা বার্তা পাঠানো হয়েছে।",
            "npi_Deva": "स्वचालित पूर्व चेतावनी प्रेषित: दर्ता भएका बासिन्दाहरूलाई इमेल मार्फत चेतावनी पठाइयो।",
            "mni_Mtei": "ꯑꯣꯇꯣꯃꯦꯇꯤꯛ ꯆꯦꯀꯁꯤꯟ-ꯄꯥꯎ ꯊꯥꯈ꯭ꯔꯦ: ꯔꯦꯖꯤꯁ꯭ꯇꯔ ꯇꯧꯔꯕꯥ ꯃꯤꯑꯣꯏꯁꯤꯡꯗꯥ ꯏ-ꯃꯦꯜ ꯊꯥꯈ꯭ꯔꯦ।",
        }
        return translations.get(target_lang, clean_text)

    # 4. If not in catalog, fallback to IndicTrans2 neural model
    try:
        tokenizer, model, ip, device = load_model()
        if tokenizer is None or model is None:
            return text

        batch = ip.preprocess_batch([clean_text], src_lang="eng_Latn", tgt_lang=target_lang)
        inputs = tokenizer(batch, padding="longest", truncation=True, max_length=256, return_tensors="pt").to(device)

        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_length=256,
                num_beams=4,
                early_stopping=True
            )

        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translated = ip.postprocess_batch(decoded, lang=target_lang)[0]
        return translated if translated and translated.strip() else text
    except Exception:
        return text
