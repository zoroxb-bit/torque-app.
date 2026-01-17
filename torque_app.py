import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Eslam Mohamed | Master Bolting Pro", layout="centered")

# --- 2. SECURITY SYSTEM ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.title("🔐 Petrochemical Maintenance Login")
        user = st.text_input("Username / اسم المستخدم")
        password = st.text_input("Password / كلمة المرور", type="password")
        if st.button("Login"):
            if user == "admin" and password == "Petro2026":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid Credentials / بيانات خطأ")
        return False
    return True

if check_password():
    # --- 3. DATABASE INITIALIZATION ---
    if "history_db" not in st.session_state:
        st.session_state.history_db = pd.DataFrame(columns=[
            "Date", "Tag", "Flange", "Permit", "Tool", "Torque (Ft-Lb)", "Pressure (PSI)"
        ])

    # --- 4. TOP HEADLINE NAVIGATION ---
    lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    
    col_sop, col_safe, col_db = st.columns(3)
    if lang == "English":
        with col_sop: st.button("📖 SOP", on_click=lambda: st.info("ASME PCC-1: 30%-60%-100% Steps."))
        with col_safe: st.button("⚠️ Safety", on_click=lambda: st.warning("Hands Clear! Check Reaction Arm."))
        with col_db: view_history = st.checkbox("📂 Data Log")
        L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "print": "Print PDF", "save": "Save Data", "export": "Download Excel", "sign": "Signature:"}
    else:
        st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
        with col_sop: st.button("📖 الدليل", on_click=lambda: st.info("معيار ASME PCC-1: مراحل الربط ٣٠٪-٦٠٪-١٠٠٪"))
        with col_safe: st.button("⚠️ السلامة", on_click=lambda: st.warning("ابعد اليدين! تأكد من ذراع رد الفعل."))
        with col_db: view_history = st.checkbox("📂 سجل البيانات")
        L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "print": "طباعة PDF", "save": "حفظ البيانات", "export": "تصدير Excel", "sign": "التوقيع:"}

    # --- 5. EXPANDED DATABASES: ALL SIZES ---
    SIZES_DB = {
        "Imperial": {
            "3/4\"-10UNC": {"d": 0.750, "As": 0.334, "af": "1-1/4\""},
            "7/8\"-9UNC": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
            "1\"-8UN": {"d": 1.000, "As": 0.606, "af": "1-5/8\""},
            "1-1/8\"-8UN": {"d": 1.125, "As": 0.790, "af": "1-13/16\""},
            "1-1/4\"-8UN": {"d": 1.250, "As": 1.000, "af": "2\""},
            "1-3/8\"-8UN": {"d": 1.375, "As": 1.233, "af": "2-3/16\""},
            "1-1/2\"-8UN": {"d": 1.500, "As": 1.492, "af": "2-3/8\""},
            "1-5/8\"-8UN": {"d": 1.625, "As": 1.780, "af": "2-9/16\""},
            "1-3/4\"-8UN": {"d": 1.750, "As": 2.080, "af": "2-3/4\""},
            "1-7/8\"-8UN": {"d": 1.875, "As": 2.410, "af": "2-15/16\""},
            "2\"-8UN": {"d": 2.000, "As": 2.770, "af": "3-1/8\""},
            "2-1/4\"-8UN": {"d": 2.250, "As": 3.560, "af": "3-1/2\""},
            "2-1/2\"-8UN": {"d": 2.500, "As": 4.440, "af": "3-7/8\""},
            "2-3/4\"-8UN": {"d": 2.750, "As": 5.430, "af": "4-1/4\""},
            "3\"-8UN": {"d": 3.000, "As": 6.510, "af": "4-5/8\""},
            "3-1/4\"-8UN": {"d": 3.250, "As": 7.690, "af": "5\""},
            "3-1/2\"-8UN": {"d": 3.500, "As": 8.960, "af": "5-3/8\""},
            "3-3/4\"-8UN": {"d": 3.750, "As": 10.34, "af": "5-3/4\""},
            "4\"-8UN": {"d": 4.000, "As": 11.87, "af": "6-1/8\""}
        },
        "Metric": {
            "M20": {"d": 0.787, "As": 0.380, "af": "30mm"},
            "M24": {"d": 0.945, "As": 0.547, "af": "36mm"},
            "M27": {"d": 1.063, "As": 0.712, "af": "41mm"},
            "M30": {"d": 1.181, "As": 0.869, "af": "46mm"},
            "M33": {"d": 1.299, "As": 1.076, "af": "50mm"},
            "M36": {"d": 1.417, "As": 1.266, "af": "55mm"},
            "M39": {"d": 1.535, "As": 1.503, "af": "60mm"},
            "M42": {"d": 1.654, "As": 1.737, "af": "65mm"},
            "M45": {"d": 1.771, "As": 2.055, "af": "70mm"},
            "M48": {"d": 1.890, "As": 2.285, "af": "75mm"},
            "M52": {"d": 2.047, "As": 2.810, "af": "80mm"},
            "M56": {"d": 2.205, "As": 3.146, "af": "85mm"},
            "M60": {"d": 2.362, "As": 3.766, "af": "90mm"},
            "M64": {"d": 2.520, "As": 4.148, "af": "95mm"},
            "M72": {"d": 2.835, "As": 5.340, "af": "105mm"},
            "M76": {"d": 2.992, "As": 6.138, "af": "110mm"},
            "M80": {"d": 3.150, "As": 6.700, "af": "115mm"},
            "M90": {"d": 3.543, "As": 8.610, "af": "130mm"},
            "M100": {"d": 3.937, "As": 10.74, "af": "145mm"}
        }
    }

    ENERPAC_CATALOG = {
        "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
        "S-Series (X-Edition)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
        "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.8250, "W15000X": 1.512, "W22000X": 2.215, "W35000X": 3.515},
        "RSL-Series": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL5000": 0.5312, "RSL8000": 0.7831, "RSL11000": 1.112, "RSL19000": 1.895}
    }

    # --- 6. CALCULATOR UI ---
    st.header(L["title"])
    e_tag = st.text_input(L["tag"])
    e_flange = st.text_input("Flange ID / Joint ID")
    e_permit = st.text_input("Permit No / رقم التصريح")

    sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)", "Metric Grade 10.9 (mm)", "ASTM A320 L7 (Low Temp)"])
    u_type = "Imperial" if "Inch" in sel_mat or "L7" in sel_mat else "Metric"
    sy_val = 105000 if "B7" in sel_mat or "B16" in sel_mat or "L7" in sel_mat else 92800

    col1, col2 = st.columns(2)
    with col1:
        sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
        tool_fam = st.selectbox("Tool Series", list(ENERPAC_CATALOG.keys()))
    with col2:
        tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
        k_val = st.selectbox("Lube (K)", [0.11, 0.13, 0.15])

    # Math
    d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
    factor = ENERPAC_CATALOG[tool_fam][tool_mod]
    torque = (k_val * d * (sy_val * As * 0.50)) / 12
    psi = torque / factor

    st.info(f"Socket A/F: {SIZES_DB[u_type][sel_size]['af']}")
    st.metric("Target Torque", f"{round(torque)} Ft-Lb")
    st.metric("Pump Pressure", f"{round(psi)} PSI")

    # --- 7. SAVE & LOG ---
    if st.button(L["save"]):
        new_row = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), e_tag, e_flange, e_permit, tool_mod, round(torque), round(psi)]
        st.session_state.history_db.loc[len(st.session_state.history_db)] = new_row
        st.success("Data Saved!")

    if view_history:
        st.dataframe(st.session_state.history_db)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            st.session_state.history_db.to_excel(writer, index=False)
        st.download_button(L["export"], data=output.getvalue(), file_name="maintenance_log.xlsx")

    # --- 8. PRINT / PDF REPORT ---
    if st.button(L["print"]):
        st.markdown(f"""
        <div style="border:5px solid #000; padding:20px; background-color:#fff; color:#000;">
            <h1 style="text-align:center;">TORQUE FIELD REPORT</h1>
            <p style="text-align:right;">Date: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
            <p><b>Equipment Tag:</b> {e_tag} | <b>Permit:</b> {e_permit}</p>
            <hr>
            <h3>Engineering Parameters:</h3>
            <p><b>Size:</b> {sel_size} | <b>Material:</b> {sel_mat}</p>
            <p><b>Tool:</b> Enerpac {tool_mod} | <b>Socket A/F:</b> {SIZES_DB[u_type][sel_size]['af']}</p>
            <hr>
            <h2 style="color:blue;">Target Torque: {round(torque)} Ft-Lb</h2>
            <h2 style="color:red;">Pump PSI: {round(psi)} PSI</h2>
            <br><br>
            <p><b>{L['sign']}</b> __________________________</p>
        </div>
        """, unsafe_allow_html=True)
        "M36": {"d": 1.417, "As": 1.266, "af": "55 mm"},
        "M45": {"d": 1.771, "As": 2.055, "af": "70 mm"},
        "M52": {"d": 2.047, "As": 2.810, "af": "80 mm"},
        "M64": {"d": 2.520, "As": 4.148, "af": "95 mm"},
        "M100": {"d": 3.937, "As": 10.740, "af": "145 mm"}
    }
}

ENERPAC_CATALOG = {
    "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
    "S-Series (X-Edition)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
    "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.8250, "W22000X": 2.215},
    "RSL-Series (Slim Line)": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL8000": 0.7831}
}

# --- 4. EQUIPMENT INFO SECTION ---
st.subheader(L["eq_header"])
e_tag = st.text_input(L["tag"])
e_flange = st.text_input(L["flange"])
e_permit = st.text_input(L["permit"])
uploaded_file = st.file_uploader("Upload Flange Photo / ارفع صورة الوصلة", type=['jpg', 'png', 'jpeg'])

# --- 5. CALCULATOR ---
st.divider()
sel_mat = st.selectbox(L["mat"], ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)", "Metric Grade 10.9 (mm)"])
u_type = "Imperial" if "Inch" in sel_mat else "Metric"
sy_val = 105000 if "B7" in sel_mat or "B16" in sel_mat else 92800

c1, c2 = st.columns(2)
with c1:
    sel_size = st.selectbox(L["size"], list(SIZES_DB[u_type].keys()))
    tool_fam = st.selectbox("Tool Series", list(ENERPAC_CATALOG.keys()))
with c2:
    tool_mod = st.selectbox(L["tool"], list(ENERPAC_CATALOG[tool_fam].keys()))
    k_val = st.selectbox("Lube (K)", [0.11, 0.13, 0.15])

# Math Logic
d = SIZES_DB[u_type][sel_size]["d"]
As = SIZES_DB[u_type][sel_size]["As"]
factor = ENERPAC_CATALOG[tool_fam][tool_mod]
torque = (k_val * d * (sy_val * As * 0.50)) / 12
psi = torque / factor

st.info(f"{L['af']}: {SIZES_DB[u_type][sel_size]['af']}")
res1, res2 = st.columns(2)
res1.metric(L["res_t"], f"{round(torque)} Ft-Lb")
res2.metric(L["res_p"], f"{round(psi)} PSI")

# --- 6. REPORT SECTION ---
st.divider()
if st.button(L["print"]):
    st.markdown(f"### 📝 FIELD REPORT: {e_tag}")
    if uploaded_file: st.image(uploaded_file, caption="Verified Flange", width=300)
    st.write(f"**Permit:** {e_permit} | **Joint ID:** {e_flange}")
    st.write(f"**Tool:** Enerpac {tool_mod} | **Pressure:** {round(psi)} PSI")
    st.write(f"**Target Torque:** {round(torque)} Ft-Lb")
    st.write(f"**{L['sign']}** __________________________")

st.caption(L["footer"])
