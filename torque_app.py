import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from io import BytesIO

# --- 1. إعدادات التطبيق الأساسية ---
st.set_page_config(page_title="Islam Mohamed | Flange Integrity Ecosystem", layout="centered")

# --- 2. الربط بقواعد بيانات GOOGLE SHEETS ---
# يتطلب إعداد الـ Secrets في Streamlit Cloud كما شرحنا سابقاً
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Connection to Google Sheets failed. Check your Secrets configuration.")

# --- 3. نظام التأمين وتسجيل الدخول ---
def auth_system():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Maintenance Portal | بوابة الصيانة")
        tab1, tab2 = st.tabs(["Login | دخول", "Sign Up | تسجيل جديد"])
        
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login"):
                # محاولة قراءة بيانات المستخدمين من الشيت
                try:
                    users_df = conn.read(worksheet="Users")
                    user_match = users_df[(users_df['Username'] == u) & (users_df['Password'] == p)]
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.current_user = u
                        st.rerun()
                    else: st.error("Invalid Credentials")
                except:
                    # دخول اضطراري في حال فشل الاتصال بالشيت لأول مرة
                    if u == "admin" and p == "Petro2026":
                        st.session_state.authenticated = True
                        st.session_state.current_user = u
                        st.rerun()

        with tab2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Register Account"):
                try:
                    users_df = conn.read(worksheet="Users")
                    new_user = pd.DataFrame([{"Username": nu, "Password": np}])
                    updated_users = pd.concat([users_df, new_user], ignore_index=True)
                    conn.update(worksheet="Users", data=updated_users)
                    st.success("Registration successful! Please login.")
                except:
                    st.error("Could not save to Google Sheets. Check Sheet permissions.")
        return False
    return True

if auth_system():
    # --- 4. العناوين العلوية والأدوات ---
    lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    
    col_sop, col_safe, col_logout = st.columns(3)
    if lang == "English":
        with col_sop: st.button("📖 SOP", on_click=lambda: st.info("ASME PCC-1: 30%-60%-100% Torque Steps."))
        with col_safe: st.button("⚠️ Safety", on_click=lambda: st.warning("Clear Hands! Check Reaction Arm."))
        with col_logout: 
            if st.button("Logout"): 
                st.session_state.authenticated = False
                st.rerun()
        L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "print": "Print PDF", "save": "Cloud Sync", "sign": "Digital Signature (Name):"}
    else:
        st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
        with col_sop: st.button("📖 الدليل", on_click=lambda: st.info("معيار ASME PCC-1: مراحل الربط ٣٠٪-٦٠٪-١٠٠٪"))
        with col_safe: st.button("⚠️ السلامة", on_click=lambda: st.warning("ابعد اليدين! تأكد من ذراع رد الفعل."))
        with col_logout: 
            if st.button("خروج"): 
                st.session_state.authenticated = False
                st.rerun()
        L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "print": "طباعة PDF", "save": "مزامنة السحاب", "sign": "التوقيع الرقمي (الاسم):"}

    # --- 5. قواعد البيانات الكاملة (SIZES & ENERPAC) ---
    SIZES_DB = {
        "Imperial": {
            "3/4\"-10": {"d": 0.75, "As": 0.334, "af": "1-1/4\""},
            "1\"-8": {"d": 1.0, "As": 0.606, "af": "1-5/8\""},
            "1-1/2\"-8": {"d": 1.5, "As": 1.492, "af": "2-3/8\""},
            "2\"-8": {"d": 2.0, "As": 2.770, "af": "3-1/8\""},
            "3\"-8": {"d": 3.0, "As": 6.510, "af": "4-5/8\""},
            "4\"-8": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
        },
        "Metric": {
            "M30": {"d": 1.18, "As": 0.869, "af": "46mm"},
            "M36": {"d": 1.41, "As": 1.266, "af": "55mm"},
            "M45": {"d": 1.77, "As": 2.055, "af": "70mm"},
            "M64": {"d": 2.52, "As": 4.148, "af": "95mm"},
            "M100": {"d": 3.93, "As": 10.74, "af": "145mm"}
        }
    }

    ENERPAC_CATALOG = {
        "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
        "S-Series (X-Edition)": {"S1500X": 0.1897, "S3000X": 0.3225, "S11000X": 1.126, "S25000X": 2.512},
        "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.825, "W22000X": 2.215, "W35000X": 3.515},
        "RSL-Series": {"RSL3000": 0.3069, "RSL11000": 1.112}
    }

    # --- 6. واجهة الحاسبة ---
    st.header(L["title"])
    e_tag = st.text_input(L["tag"])
    tech_name = st.text_input(L["sign"])

    sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)", "ASTM A320 L7 (Low Temp)"])
    u_type = "Imperial" if "Inch" in sel_mat or "L7" in sel_mat else "Metric"
    sy_val = 105000 if any(x in sel_mat for x in ["B7", "B16", "L7"]) else 92800

    col1, col2 = st.columns(2)
    with col1:
        sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
        tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
    with col2:
        tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
        k_val = st.selectbox("Lube (K)", [0.11, 0.13, 0.15])

    # العمليات الحسابية
    d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
    torque = (k_val * d * (sy_val * As * 0.50)) / 12
    psi = torque / ENERPAC_CATALOG[tool_fam][tool_mod]

    st.info(f"Socket A/F: {SIZES_DB[u_type][sel_size]['af']}")
    st.metric("Target Torque", f"{round(torque)} Ft-Lb")
    st.metric("Pump Pressure", f"{round(psi)} PSI")

    # --- 7. الحفظ السحابي والتقارير ---
    if st.button(L["save"]):
        try:
            reports_df = conn.read(worksheet="Reports")
            new_report = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "Tag": e_tag, "Torque": round(torque), "PSI": round(psi), "Technician": tech_name
            }])
            updated_reports = pd.concat([reports_df, new_report], ignore_index=True)
            conn.update(worksheet="Reports", data=updated_reports)
            st.success("Synced to Google Sheets Successfully!")
        except:
            st.error("Cloud Sync Failed. Check Connection.")

    if st.button(L["print"]):
        st.markdown(f"""
        <div style="border:5px solid black; padding:20px; background-color:white; color:black;">
            <h2 style="text-align:center;">FIELD MAINTENANCE REPORT</h2>
            <p><b>Equipment Tag:</b> {e_tag} | <b>Date:</b> {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
            <hr>
            <h2 style="color:red; text-align:center;">Pressure: {round(psi)} PSI</h2>
            <h2 style="color:blue; text-align:center;">Torque: {round(torque)} Ft-Lb</h2>
            <hr>
            <p><b>Digital Signature:</b> <span style="font-family:cursive; font-size:24px;">{tech_name}</span></p>
            <p>Verified by: {st.session_state.current_user}</p>
        </div>
        """, unsafe_allow_html=True)
                    
