import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from io import BytesIO

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Enterprise Maintenance", layout="centered")

# --- 2. GOOGLE SHEETS CONNECTION ---
try:
    # We set ttl=0 to ensure we always get fresh data from the cloud
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Cloud Connection Error: {e}")

# --- 3. AUTHENTICATION & ADMIN SYSTEM ---
def auth_system():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Maintenance Portal")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            u_input = st.text_input("Username", key="l_user").strip()
            p_input = st.text_input("Password", type="password", key="l_pass").strip()
            
            if st.button("Login"):
                try:
                    # Clear cache to ensure we see the latest sign-ups
                    st.cache_data.clear() 
                    
                    # Read Users worksheet
                    users_df = conn.read(worksheet="Users", ttl=0)
                    
                    # Clean data: Remove spaces and convert everything to strings
                    users_df['Username'] = users_df['Username'].astype(str).str.strip()
                    users_df['Password'] = users_df['Password'].astype(str).str.strip()
                    
                    # Search for match
                    user_match = users_df[(users_df['Username'] == u_input) & (users_df['Password'] == p_input)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.current_user = u_input
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials. If you just signed up, wait 5 seconds and try again.")
                except Exception as e:
                    st.error(f"System Error: {e}")

        with tab2:
            nu = st.text_input("New Username", key="s_user").strip()
            np = st.text_input("New Password", type="password", key="s_pass").strip()
            if st.button("Register Account"):
                try:
                    users_df = conn.read(worksheet="Users", ttl=0)
                    if nu in users_df['Username'].astype(str).values:
                        st.warning("Username already exists!")
                    else:
                        new_user = pd.DataFrame([{"Username": nu, "Password": np}])
                        updated_users = pd.concat([users_df, new_user], ignore_index=True)
                        conn.update(worksheet="Users", data=updated_users)
                        st.success("✅ Account created! Please wait a moment for the cloud to sync, then Login.")
                except Exception as e:
                    st.error(f"Sync Failed: {e}")
        return False
    return True

if auth_system():
    # --- 4. NAVIGATION & ADMIN DASHBOARD ---
    lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    
    col_sop, col_safe, col_admin, col_logout = st.columns(4)
    with col_logout: 
        if st.button("Logout"): 
            st.session_state.authenticated = False
            st.rerun()
    
    is_admin = st.session_state.current_user == "admin"
    if is_admin:
        with col_admin:
            show_admin = st.checkbox("⚙️ Admin")
    else:
        show_admin = False

    if lang == "Arabic":
        st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
        L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "print": "طباعة PDF", "save": "مزامنة السحاب", "sign": "التوقيع الرقمي:"}
    else:
        L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "print": "Print PDF", "save": "Cloud Sync", "sign": "Digital Signature:"}

    # --- 5. ADMIN VIEW ---
    if show_admin:
        st.divider()
        st.subheader("🛠️ Admin Control Center")
        admin_tab1, admin_tab2 = st.tabs(["Manage Users", "Manage Reports"])
        with admin_tab1:
            u_df = conn.read(worksheet="Users", ttl=0)
            st.dataframe(u_df)
        with admin_tab2:
            r_df = conn.read(worksheet="Reports", ttl=0)
            st.dataframe(r_df)

    # --- 6. CALCULATOR (COMPLETE DATA) ---
    SIZES_DB = {
        "Imperial": {
            "3/4\"-10": {"d": 0.75, "As": 0.334, "af": "1-1/4\""}, "1\"-8": {"d": 1.0, "As": 0.606, "af": "1-5/8\""},
            "1-1/2\"-8": {"d": 1.5, "As": 1.49, "af": "2-3/8\""}, "2\"-8": {"d": 2.0, "As": 2.77, "af": "3-1/8\""},
            "3\"-8": {"d": 3.0, "As": 6.51, "af": "4-5/8\""}, "4\"-8": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
        },
        "Metric": {
            "M30": {"d": 1.18, "As": 0.869, "af": "46mm"}, "M36": {"d": 1.41, "As": 1.266, "af": "55mm"},
            "M64": {"d": 2.52, "As": 4.148, "af": "95mm"}, "M100": {"d": 3.93, "As": 10.74, "af": "145mm"}
        }
    }

    ENERPAC_CATALOG = {
        "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
        "S-Series (X)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
        "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W22000X": 2.215},
        "RSL-Series": {"RSL3000": 0.3069, "RSL11000": 1.112}
    }

    st.header(L["title"])
    e_tag = st.text_input(L["tag"])
    tech_name = st.text_input(L["sign"])

    sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)"])
    u_type = "Imperial" if "Inch" in sel_mat else "Metric"
    sy_val = 105000 if "B7" in sel_mat or "B16" in sel_mat else 92800

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
    st.metric("Target Torque", f"{round(torque)} Ft-Lb")
    st.metric("Pump Pressure", f"{round(psi)} PSI")

    # --- 7. REPORTS ---
    if st.button(L["save"]):
        try:
            reports_df = conn.read(worksheet="Reports", ttl=0)
            new_row = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"), 
                "Tag": e_tag, "Torque": round(torque), "PSI": round(psi), 
                "Technician": tech_name
            }])
            conn.update(worksheet="Reports", data=pd.concat([reports_df, new_row], ignore_index=True))
            st.success("Synced!")
        except Exception as e: st.error(f"Error: {e}")

    if st.button(L["print"]):
        st.markdown(f"""
        <div style="border:5px solid black; padding:20px; background-color:white; color:black;">
            <h2 style="text-align:center;">OFFICIAL FIELD REPORT</h2>
            <p><b>Equipment:</b> {e_tag} | <b>PSI:</b> {round(psi)} | <b>Torque:</b> {round(torque)}</p>
            <p><b>Technician:</b> {tech_name}</p>
        </div>
        """, unsafe_allow_html=True)
    
