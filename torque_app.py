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
        "1-1/4\"-8": {"d": 1.250, "As": 1.000, "af": "2\""},
        "1-1/2\"-8": {"d": 1.500, "As": 1.492, "af": "2-3/8\""},
        "2\"-8": {"d": 2.000, "As": 2.770, "af": "3-1/8\""},
        "3\"-8": {"d": 3.000, "As": 6.510, "af": "4-5/8\""},
        "4\"-8": {"d": 4.000, "As": 11.87, "af": "6-1/8\""}
    },
    "Metric": {
        "M20": {"d": 0.787, "As": 0.380, "af": "30mm"},
        "M30": {"d": 1.181, "As": 0.869, "af": "46mm"},
        "M36": {"d": 1.417, "As": 1.266, "af": "55mm"},
        "M64": {"d": 2.520, "As": 4.148, "af": "95mm"},
        "M100": {"d": 3.937, "As": 10.74, "af": "145mm"}
    }
}

ENERPAC_CATALOG = {
    "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S11000": 1.126, "S25000": 2.512},
    "S-Series (X)": {"S1500X": 0.1897, "S3000X": 0.3225, "S11000X": 1.126, "S25000X": 2.512},
    "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W22000X": 2.215, "W35000X": 3.515},
    "RSL-Series": {"RSL3000": 0.3069, "RSL11000": 1.112}
}

# --- 6. CALCULATOR INTERFACE ---
st.header(L["title"])
e_tag = st.text_input(L["tag"])
tech_name = st.text_input(L["sign"])

yield_pct = st.slider(L["yield"], min_value=30, max_value=90, value=70, step=5)

sel_mat = st.selectbox("Material", ["ASTM A193 B7", "Metric Grade 8.8", "ASTM A193 B16", "ASTM A320 L7"])
u_type = "Imperial" if "ASTM" in sel_mat or "L7" in sel_mat else "Metric"
sy_val = 105000 if "B7" in sel_mat or "B16" in sel_mat or "L7" in sel_mat else 92800

c1, c2 = st.columns(2)
with c1:
    sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
    tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
with c2:
    tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
    lube_type = st.selectbox("Lubricant Type", list(LUBE_DB.keys()))
    k_val = LUBE_DB[lube_type]

# --- 7. MATH & UNIT CONVERSION ---
d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
torque_ftlb = (k_val * d * (sy_val * As * (yield_pct / 100))) / 12
psi = torque_ftlb / ENERPAC_CATALOG[tool_fam][tool_mod]

# Conversions
torque_nm = torque_ftlb * 1.35582
bar = psi * 0.0689476

st.info(f"Socket A/F: {SIZES_DB[u_type][sel_size]['af']}")

# Multi-Unit Metrics
col_t, col_p = st.columns(2)
with col_t:
    st.metric("Torque", f"{round(torque_ftlb)} Ft-Lb")
    st.caption(f"≈ {round(torque_nm)} N.m")
with col_p:
    st.metric("Pressure", f"{round(psi)} PSI")
    st.caption(f"≈ {round(bar)} Bar")

# --- 8. LOGS & EXPORT ---
if show_history:
    st.divider()
    logs = get_data("Reports")
    if not logs.empty:
        st.dataframe(logs)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            logs.to_excel(writer, index=False, sheet_name='Logs')
        st.download_button(label=L["export"], data=output.getvalue(), file_name="Bolting_Export.xlsx")

# --- 9. SAVE & PRINT ---
col_save, col_print = st.columns(2)
with col_save:
    if st.button(L["save"]):
        try:
            r_df = get_data("Reports")
            new_report = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"), 
                "Tag": e_tag, 
                "Torque_FtLb": round(torque_ftlb), "Torque_Nm": round(torque_nm),
                "Pressure_PSI": round(psi), "Pressure_Bar": round(bar),
                "Yield%": yield_pct, "Lube": lube_type, "Technician": tech_name
            }])
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(worksheet="Reports", data=pd.concat([r_df, new_report], ignore_index=True))
            st.success("Synced to Cloud!")
        except:
            st.error("Cloud Sync Failed.")

with col_print:
    if st.button(L["print"]):
        st.markdown(f"""
        <div style="border:5px solid black; padding:20px; background-color:white; color:black;">
            <h2 style="text-align:center;">FIELD MAINTENANCE REPORT</h2>
            <p><b>Equipment:</b> {e_tag} | <b>Date:</b> {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
            <hr>
            <p><b>Yield:</b> {yield_pct}% | <b>Lube:</b> {lube_type}</p>
            <div style="display: flex; justify-content: space-around;">
                <div>
                    <h3 style="color:red;">{round(psi)} PSI</h3>
                    <p>({round(bar)} Bar)</p>
                </div>
                <div>
                    <h3 style="color:blue;">{round(torque_ftlb)} Ft-Lb</h3>
                    <p>({round(torque_nm)} N.m)</p>
                </div>
            </div>
            <hr>
            <p><b>Signature:</b> <span style="font-family:cursive; font-size:24px;">{tech_name}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
