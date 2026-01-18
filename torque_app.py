import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime
from io import BytesIO

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Flange Integrity Ecosystem", layout="centered")

# --- 2. CONNECTION & DATA LOADING ---
def get_data(worksheet_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=worksheet_name, ttl=0)
        return df.astype(str)
    except Exception as e:
        return pd.DataFrame()

# --- 3. LUBRICANT K-FACTOR DATABASE ---
LUBE_DB = {
    "Molykote G-n Paste (K=0.11)": 0.11,
    "Nickel Anti-Seize (K=0.13)": 0.13,
    "Copper / Silver Paste (K=0.15)": 0.15,
    "Machine Oil / WD40 (K=0.20)": 0.20,
    "Dry / No Lube (K=0.30)": 0.30
}

# --- 4. NAVIGATION & LANGUAGE ---
lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")

col_sop, col_safe, col_history = st.columns(3)
if lang == "English":
    with col_sop: st.button("📖 SOP", on_click=lambda: st.info("ASME PCC-1: 30%-60%-100% Torque Steps."))
    with col_safe: st.button("⚠️ Safety", on_click=lambda: st.warning("Clear Hands! Check Reaction Arm."))
    with col_history: show_history = st.checkbox("📂 View Logs & Export")
    L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "sign": "Digital Signature:", "save": "Save to Cloud", "print": "Save as PDF", "export": "Download Excel", "yield": "Target Yield (%)"}
else:
    st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
    with col_sop: st.button("📖 الدليل", on_click=lambda: st.info("معيار ASME PCC-1: مراحل الربط ٣٠٪-٦٠٪-١٠٠٪"))
    with col_safe: st.button("⚠️ السلامة", on_click=lambda: st.warning("ابعد اليدين! تأكد من ذراع رد الفعل."))
    with col_history: show_history = st.checkbox("📂 السجل والتصدير")
    L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "sign": "التوقيع الرقمي:", "save": "مزامنة السحاب", "print": "حفظ كـ PDF", "export": "تحميل Excel", "yield": "نسبة إجهاد الخضوع (%)"}

# --- 5. COMPREHENSIVE SIZES DATABASE ---
SIZES_DB = {
    "Imperial": {
        "3/4\"-10": {"d": 0.750, "As": 0.334, "af": "1-1/4\""},
        "7/8\"-9": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
        "1\"-8": {"d": 1.000, "As": 0.606, "af": "1-5/8\""},
        "1-1/8\"-8": {"d": 1.125, "As": 0.790, "af": "1-13/16\""},
        "1-1/4\"-8": {"d": 1.250, "As": 1.000, "
                      
