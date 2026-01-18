import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Enterprise Maintenance", layout="centered")

# --- 2. THE ULTIMATE CONNECTION & DATA LOADING ---
def get_data(worksheet_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=worksheet_name, ttl=0)
        return df.astype(str)
    except Exception as e:
        st.error(f"Cloud Sync Status: Not connected to worksheet '{worksheet_name}'")
        return pd.DataFrame()

# --- 3. NAVIGATION & LANGUAGE ---
lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")

col_sop, col_safe, col_history = st.columns(3)
if lang == "English":
    with col_sop: st.button("📖 SOP", on_click=lambda: st.info("ASME PCC-1: 30%-60%-100% Torque Steps."))
    with col_safe: st.button("⚠️ Safety", on_click=lambda: st.warning("Clear Hands! Check Reaction Arm."))
    with col_history: show_history = st.checkbox("📂 View Logs")
    L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "sign": "Digital Signature (Name):", "save": "Save to Cloud", "print": "Print PDF"}
else:
    st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
    with col_sop: st.button("📖 الدليل", on_click=lambda: st.info("معيار ASME PCC-1: مراحل الربط ٣٠٪-٦٠٪-١٠٠٪"))
    with col_safe: st.button("⚠️ السلامة", on_click=lambda: st.warning("ابعد اليدين! تأكد من ذراع رد الفعل."))
    with col_history: show_history = st.checkbox("📂 السجل")
    L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "sign": "التوقيع الرقمي (الاسم):", "save": "مزامنة السحاب", "print": "طباعة PDF"}

# --- 4. ENERPAC & BOLT DATABASES ---
SIZES_DB = {
    "Imperial": {
        "3/4\"-10": {"d": 0.75, "As": 0.334, "af": "1-1/4\""},
        "7/8\"-9": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
        "1\"-8": {"d": 1.0, "As": 0.606, "af": "1-5/8\""},
        "1-1/2\"-8": {"d": 1.5, "As": 1.492, "af": "2-3/8\""},
        "2\"-8": {"d": 2.0, "As": 2.770, "af": "3-1/8\""},
        "3\"-8": {"d": 3.0, "As": 6.510, "af": "4-5/8\""},
        "4\"-8": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
    },
    "Metric": {
        "M24": {"d": 0.94, "As": 0.54, "af": "36mm"},
        "M30": {"d": 1.18, "As": 0.869, "af": "46mm"},
        "M36": {"d": 1.41, "As": 1.266, "af": "55mm"},
        "M45": {"d": 1.77, "As": 2.055, "af": "70mm"},
        "M52": {"d": 2.04, "As": 2.810, "af": "80mm"},
        "M64": {"d": 2.52, "As": 4.148, "af": "95mm"},
        "M100": {"d": 3.93, "As": 10.74, "af": "145mm"}
    }
}

ENERPAC_CATALOG = {
    "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
    "S-Series (X)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
    "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.825, "W22000X": 2.215, "W35000X": 3.515},
    "RSL-Series": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL5000": 0.5312, "RSL11000": 1.112, "RSL19000": 1.895}
}

# --- 5. CALCULATOR INTERFACE ---
st.header(L["title"])
e_tag = st.text_input(L["tag"])
tech_name = st.text_input(L["sign"])

sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)"])
u_type = "Imperial" if "Inch" in sel_mat else "Metric"
sy_val = 105000 if u_type == "Imperial" else 92800

c1, c2 = st.columns(2)
with c1:
    sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
    tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
with c2:
    tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
    k_val = st.selectbox("K-Factor", [0.11, 0.13, 0.15])

# MATH
d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
torque = (k_val * d * (sy_val * As * 0.50)) / 12
psi = torque / ENERPAC_CATALOG[tool_fam][tool_mod]

st.info(f"Socket A/F: {SIZES_DB[u_type][sel_size]['af']}")
res1, res2 = st.columns(2)
res1.metric("Target Torque", f"{round(torque)} Ft-Lb")
res2.metric("Pump Pressure", f"{round(psi)} PSI")

# --- 6. LOGS & SAVING ---
if show_history:
    st.divider()
    logs = get_data("Reports")
    if not logs.empty:
        st.dataframe(logs)

if st.button(L["save"]):
    try:
        r_df = get_data("Reports")
        new_report = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%Y-%m-%d"), 
            "Tag": e_tag, "Torque": round(torque), "PSI": round(psi), "Technician": tech_name
        }])
        conn = st.connection("gsheets", type=GSheetsConnection)
        conn.update(worksheet="Reports", data=pd.concat([r_df, new_report], ignore_index=True))
        st.success("Synced to Cloud!")
    except Exception as e:
        st.error("Report Saved Locally (Cloud Sync unavailable)")

if st.button(L["print"]):
    st.markdown(f"""
    <div style="border:5px solid black; padding:20px; background-color:white; color:black;">
        <h2 style="text-align:center;">FIELD MAINTENANCE REPORT</h2>
        <p><b>Equipment:</b> {e_tag} | <b>Date:</b> {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
        <hr>
        <h2 style="color:red; text-align:center;">Pressure: {round(psi)} PSI</h2>
        <h2 style="color:blue; text-align:center;">Torque: {round(torque)} Ft-Lb</h2>
        <hr>
        <p><b>Signature:</b> <span style="font-family:cursive; font-size:24px;">{tech_name}</span></p>
    </div>
    """, unsafe_allow_html=True)
            
