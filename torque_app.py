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

# --- 5. COMPREHENSIVE SIZES DATABASE (IMPERIAL & METRIC) ---
SIZES_DB = {
    "Imperial": {
        "3/4\"-10": {"d": 0.750, "As": 0.334, "af": "1-1/4\""},
        "7/8\"-9": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
        "1\"-8": {"d": 1.000, "As": 0.606, "af": "1-5/8\""},
        "1-1/8\"-8": {"d": 1.125, "As": 0.790, "af": "1-13/16\""},
        "1-1/4\"-8": {"d": 1.250, "As": 1.000, "af": "2\""},
        "1-1/2\"-8": {"d": 1.500, "As": 1.492, "af": "2-3/8\""},
        "1-3/4\"-8": {"d": 1.750, "As": 2.080, "af": "2-3/4\""},
        "2\"-8": {"d": 2.000, "As": 2.770, "af": "3-1/8\""},
        "2-1/2\"-8": {"d": 2.500, "As": 4.440, "af": "3-7/8\""},
        "3\"-8": {"d": 3.000, "As": 6.510, "af": "4-5/8\""},
        "3-1/2\"-8": {"d": 3.500, "As": 8.960, "af": "5-3/8\""},
        "4\"-8": {"d": 4.000, "As": 11.87, "af": "6-1/8\""}
    },
    "Metric": {
        "M20": {"d": 0.787, "As": 0.380, "af": "30mm"},
        "M24": {"d": 0.945, "As": 0.547, "af": "36mm"},
        "M30": {"d": 1.181, "As": 0.869, "af": "46mm"},
        "M36": {"d": 1.417, "As": 1.266, "af": "55mm"},
        "M45": {"d": 1.771, "As": 2.055, "af": "70mm"},
        "M52": {"d": 2.047, "As": 2.810, "af": "80mm"},
        "M64": {"d": 2.520, "As": 4.148, "af": "95mm"},
        "M72": {"d": 2.835, "As": 5.340, "af": "105mm"},
        "M80": {"d": 3.150, "As": 6.700, "af": "115mm"},
        "M90": {"d": 3.543, "As": 8.610, "af": "130mm"},
        "M100": {"d": 3.937, "As": 10.74, "af": "145mm"}
    }
}

ENERPAC_CATALOG = {
    "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
    "S-Series (X)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
    "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.8250, "W22000X": 2.215, "W35000X": 3.515},
    "RSL-Series": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL5000": 0.5312, "RSL11000": 1.112, "RSL19000": 1.895}
}

# --- 6. CALCULATOR INTERFACE ---
st.header(L["title"])
e_tag = st.text_input(L["tag"])
tech_name = st.text_input(L["sign"])

# Yield Control Feature (Default 70%)
yield_pct = st.slider(L["yield"], min_value=30, max_value=90, value=70, step=5)

sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)", "Metric Grade 10.9 (mm)", "ASTM A320 L7 (Low Temp)"])
u_type = "Imperial" if "Inch" in sel_mat or "L7" in sel_mat else "Metric"
sy_val = 105000 if "B7" in sel_mat or "B16" in sel_mat or "L7" in sel_mat else 92800

c1, c2 = st.columns(2)
with c1:
    sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
    tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
with c2:
    tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
    lube_type = st.selectbox("Lubricant Type", list(LUBE_DB.keys()))
    k_val = LUBE_DB[lube_type]

# --- MATH LOGIC ---
d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
torque = (k_val * d * (sy_val * As * (yield_pct / 100))) / 12
psi = torque / ENERPAC_CATALOG[tool_fam][tool_mod]

st.info(f"Socket A/F: {SIZES_DB[u_type][sel_size]['af']}")
res1, res2 = st.columns(2)
res1.metric("Target Torque", f"{round(torque)} Ft-Lb")
res2.metric("Pump Pressure", f"{round(psi)} PSI")

# --- 7. EXPORT & DATA LOGGING ---
if show_history:
    st.divider()
    logs = get_data("Reports")
    if not logs.empty:
        st.dataframe(logs)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            logs.to_excel(writer, index=False, sheet_name='Log')
        st.download_button(label=L["export"], data=output.getvalue(), file_name="Bolting_Log_Export.xlsx")

col_save, col_print = st.columns(2)
with col_save:
    if st.button(L["save"]):
        try:
            r_df = get_data("Reports")
            new_report = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"), 
                "Tag": e_tag, "Torque": round(torque), "PSI": round(psi), 
                "Yield%": yield_pct, "Technician": tech_name, "Lube": lube_type
            }])
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(worksheet="Reports", data=pd.concat([r_df, new_report], ignore_index=True))
            st.success("Synced to Cloud!")
        except: st.error("Save Failed - Check Connection")

with col_print:
    if st.button(L["print"]):
        st.markdown(f"""
        <div style="border:5px solid black; padding:20px; background-color:white; color:black;">
            <h2 style="text-align:center;">FIELD MAINTENANCE REPORT</h2>
            <p><b>Equipment:</b> {e_tag} | <b>Date:</b> {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
            <hr>
            <p><b>Load Control:</b> {yield_pct}% of Yield Strength | <b>Lube:</b> {lube_type}</p>
            <h2 style="color:red; text-align:center;">Pressure: {round(psi)} PSI</h2>
            <h2 style="color:blue; text-align:center;">Torque: {round(torque)} Ft-Lb</h2>
            <hr>
            <p><b>Signature:</b> <span style="font-family:cursive; font-size:24px;">{tech_name}</span></p>
        </div>
        """, unsafe_allow_html=True)
        st.write("To save as PDF: Use Browser Print (Ctrl+P).")
