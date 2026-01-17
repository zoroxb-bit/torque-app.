import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Enterprise Bolting Pro", layout="centered")

# --- 2. AUTHENTICATION & SIGN-UP ---
def auth_system():
    if "users" not in st.session_state:
        st.session_state.users = {"admin": "Petro2026"} 
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Maintenance Portal")
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login"):
                if u in st.session_state.users and st.session_state.users[u] == p:
                    st.session_state.authenticated = True
                    st.session_state.current_user = u
                    st.rerun()
                else: st.error("Access Denied")
        with tab2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Sign Up"):
                st.session_state.users[nu] = np
                st.success("Account created! Please Login.")
        return False
    return True

if auth_system():
    # --- 3. DATABASES ---
    SIZES_DB = {
        "Imperial": {
            "3/4\"-10": {"d": 0.75, "As": 0.334, "af": "1-1/4\""}, "7/8\"-9": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
            "1\"-8": {"d": 1.0, "As": 0.606, "af": "1-5/8\""}, "1-1/8\"-8": {"d": 1.125, "As": 0.79, "af": "1-13/16\""},
            "1-1/4\"-8": {"d": 1.25, "As": 1.0, "af": "2\""}, "1-1/2\"-8": {"d": 1.5, "As": 1.49, "af": "2-3/8\""},
            "1-3/4\"-8": {"d": 1.75, "As": 2.08, "af": "2-3/4\""}, "2\"-8": {"d": 2.0, "As": 2.77, "af": "3-1/8\""},
            "2-1/2\"-8": {"d": 2.5, "As": 4.44, "af": "3-7/8\""}, "3\"-8": {"d": 3.0, "As": 6.51, "af": "4-5/8\""},
            "3-1/2\"-8": {"d": 3.5, "As": 8.96, "af": "5-3/8\""}, "4\"-8": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
        },
        "Metric": {
            "M20": {"d": 0.78, "As": 0.38, "af": "30mm"}, "M24": {"d": 0.94, "As": 0.54, "af": "36mm"},
            "M30": {"d": 1.18, "As": 0.86, "af": "46mm"}, "M36": {"d": 1.41, "As": 1.26, "af": "55mm"},
            "M45": {"d": 1.77, "As": 2.05, "af": "70mm"}, "M52": {"d": 2.04, "As": 2.81, "af": "80mm"},
            "M64": {"d": 2.52, "As": 4.14, "af": "95mm"}, "M72": {"d": 2.83, "As": 5.34, "af": "105mm"},
            "M80": {"d": 3.15, "As": 6.7, "af": "115mm"}, "M100": {"d": 3.93, "As": 10.7, "af": "145mm"}
        }
    }

    ENERPAC_CATALOG = {
        "S-Series (Std)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
        "S-Series (X)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
        "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.825, "W22000X": 2.215, "W35000X": 3.515},
        "RSL-Series": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL8000": 0.7831, "RSL19000": 1.895},
        "DSX-Series": {"DSX1500": 0.1897, "DSX3000": 0.3225, "DSX11000": 1.126}
    }

    # --- 4. TOP NAV & TRANSLATIONS ---
    lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    if lang == "Arabic": st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
    
    L = {"title": "Industrial Bolting Master" if lang=="English" else "نظام التحكم في العزم المتقدم",
         "sign": "Employee Name (Digital Signature)" if lang=="English" else "اسم الموظف (توقيع إلكتروني)"}

    # --- 5. CALCULATOR ---
    st.header(L["title"])
    e_tag = st.text_input("Tag / رقم المعدة")
    tech_name = st.text_input(L["sign"])

    sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)", "ASTM A320 L7 (Low Temp)"])
    u_type = "Imperial" if "Inch" in sel_mat or "L7" in sel_mat else "Metric"
    sy_val = 105000 if any(x in sel_mat for x in ["B7", "B16", "L7"]) else 92800

    c1, c2 = st.columns(2)
    with c1:
        sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
        tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
    with c2:
        tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
        k_val = st.selectbox("K-Factor", [0.11, 0.13, 0.15])

    # Math
    d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
    torque = (k_val * d * (sy_val * As * 0.50)) / 12
    psi = torque / ENERPAC_CATALOG[tool_fam][tool_mod]

    st.info(f"Socket Size: {SIZES_DB[u_type][sel_size]['af']}")
    st.metric("Target Torque", f"{round(torque)} Ft-Lb")
    st.metric("Pump Pressure", f"{round(psi)} PSI")

    # --- 6. REPORT ---
    if st.button("Generate Report / إصدار تقرير"):
        st.markdown(f"""
        <div style="border:5px solid black; padding:20px; background-color:white; color:black;">
            <h2 style="text-align:center;">FIELD MAINTENANCE REPORT</h2>
            <p><b>Date:</b> {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
            <p><b>Equipment:</b> {e_tag} | <b>Tool:</b> {tool_mod}</p>
            <hr>
            <h2 style="color:red; text-align:center;">{round(psi)} PSI</h2>
            <hr>
            <p><b>Digital Signature:</b> <span style="font-family:cursive; font-size:24px;">{tech_name}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
