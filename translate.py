"""
=============================================================================
GroundCheck Landslide Early Warning System - Multilingual Translation Engine
IndicTrans2 Distilled 200M (English -> Indic) Translation Service
Languages Supported: Assamese, Bengali, Nepali, Manipuri, English
=============================================================================
"""

import os
import streamlit as st
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

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
        # Cross-platform fallback for environments without C++ build tools (Windows)
        from utils.indic_processor import IndicProcessor

# Distilled 200M model variant for memory efficiency on Streamlit Cloud
MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"

# Supported North-Eastern regional languages and FLORES-200 language codes
LANG_OPTIONS = {
    "English": "eng_Latn",
    "অসমীয়া (Assamese)": "asm_Beng",
    "বাংলা (Bengali)": "ben_Beng",
    "नेपाली (Nepali)": "npi_Deva",
    "ꯃꯤꯇꯩꯂꯣꯟ (Manipuri)": "mni_Mtei",
}


@st.cache_resource
def load_model():
    """
    Loads and caches the IndicTrans2 distilled model, tokenizer, and processor.
    Uses @st.cache_resource to ensure single-instance loading across app reruns.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Fetch Hugging Face token from environment or Streamlit secrets if present
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGING_FACE_HUB_TOKEN")
    if not hf_token:
        try:
            hf_token = st.secrets.get("HF_TOKEN", None)
        except Exception:
            hf_token = None

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        token=hf_token
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        token=hf_token
    ).to(device)

    processor = IndicProcessor(inference=True)
    return tokenizer, model, processor, device


def translate_text(text: str, target_lang: str) -> str:
    """
    Translates input text from English into the specified Indic target language.
    
    Guarantees:
    - If target_lang is English ("eng_Latn") or input is empty, returns original text.
    - If any exception occurs (e.g. model download pending, network timeout, gated repo),
      gracefully catches the error and returns the original English text unchanged.
      A translation failure will NEVER crash the alert or early warning workflow.
    """
    if not text or not str(text).strip():
        return text

    if target_lang == "eng_Latn":
        return text

    try:
        tokenizer, model, ip, device = load_model()
        batch = ip.preprocess_batch([text], src_lang="eng_Latn", tgt_lang=target_lang)
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt").to(device)

        with torch.no_grad():
            generated = model.generate(
                **inputs,
                max_length=256,
                num_beams=5,
                use_cache=True
            )

        decoded = tokenizer.batch_decode(generated, skip_special_tokens=True)
        translated = ip.postprocess_batch(decoded, lang=target_lang)[0]
        return translated if translated and translated.strip() else text
    except Exception as e:
        # Fail-safe: Always fallback to original English text to preserve critical alert functionality
        return text
