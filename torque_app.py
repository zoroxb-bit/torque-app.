import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import datetime

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Enterprise Maintenance", layout="centered")

# --- 2. THE ULTIMATE CONNECTION & DATA LOADING ---
# We use ttl=0 to ensure we always get fresh data from Google Sheets
def get_data(worksheet_name):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=worksheet_name, ttl=0)
        # Force all data to strings to prevent numeric password mismatch (e.g., 10015 vs "10015")
        return df.astype(str)
    except Exception as e:
        st.error(f"Failed to connect to worksheet '{worksheet_name}': {e}")
        return pd.DataFrame()

# --- 3. AUTHENTICATION & SIGN-UP SYSTEM ---
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
                users_df = get_data("Users")
                if not users_df.empty:
                    # Clean the data: remove any invisible spaces from the Google Sheet
                    users_df['Username'] = users_df['Username'].str.strip()
                    users_df['Password'] = users_df['Password'].str.strip()
                    
                    # Check for match (case-insensitive for username)
                    match = users_df[(users_df['Username'].str.lower() == u_input.lower()) & 
                                     (users_df['Password'] == p_input)]
                    
                    if not match.empty:
                        st.session_state.authenticated = True
                        st.session_state.current_user = u_input
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials. Check your Password or Username.")
                else:
                    st.error("Could not retrieve user database.")

        with tab2:
            nu = st.text_input("New Username", key="s_user").strip()
            np = st.text_input("New Password", type="password", key="s_pass").strip()
            confirm_np = st.text_input("Confirm New Password", type="password").strip()
            
            if st.button("Register Account"):
                users_df = get_data("Users")
                if nu.lower() in users_df['Username'].str.lower().str.strip().values:
                    st.warning("Username already exists!")
                elif np != confirm_np:
                    st.error("Passwords do not match.")
                else:
                    try:
                        new_user = pd.DataFrame([{"Username": nu, "Password": np}])
                        updated_df = pd.concat([users_df, new_user], ignore_index=True)
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        conn.update(worksheet="Users", data=updated_df)
                        st.success("✅ Account created! Please login now.")
                    except Exception as e:
                        st.error(f"Sign-up failed: {e}")
        return False
    return True

if auth_system():
    # --- 4. NAVIGATION & LANGUAGE ---
    lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    
    col_sop, col_safe, col_logout = st.columns(3)
    with col_logout: 
        if st.button("Logout"): 
            st.session_state.authenticated = False
            st.rerun()
    
    if lang == "Arabic":
        st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
        L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "sign": "التوقيع الرقمي:"}
    else:
        L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "sign": "Digital Signature:"}

    # --- 5. ENERPAC & BOLT DATABASES (Full Catalog Merged) ---
    SIZES_DB = {
        "Imperial": {
            "3/4\"-10": {"d": 0.75, "As": 0.334, "af": "1-1/4\""},
            "7/8\"-9": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
            "1\"-8": {"d": 1.0, "As": 0.606, "af": "1-5/8\""},
            "1-1/2\"-8": {"d": 1.5, "As": 1.492, "af": "2-3/8\""},
            "2\"-8": {"d": 2.0, "As": 2.77, "af": "3-1/8\""},
            "3\"-8": {"d": 3.0, "As": 6.51, "af": "4-5/8\""},
            "4\"-8": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
        },
        "Metric": {
            "M30": {"d": 1.18, "As": 0.869, "af": "46mm"},
            "M36": {"d": 1.41, "As": 1.266, "af": "55mm"},
            "M45": {"d": 1.77, "As": 2.055, "af": "70mm"},
            "M52": {"d": 2.04, "As": 2.81, "af": "80mm"},
            "M64": {"d": 2.52, "As": 4.148, "af": "95mm"},
            "M100": {"d": 3.93, "As": 10.74, "af": "145mm"}
        }
    }

    ENERPAC_CATALOG = {
        "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.126, "S25000": 2.512},
        "S-Series (X)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.126, "S25000X": 2.512},
        "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.825, "W22000X": 2.215, "W35000X": 3.515},
        "RSL-Series": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL5000": 0.5312, "RSL8000": 0.7831, "RSL11000": 1.112}
    }

    # --- 6. CALCULATOR INTERFACE ---
    st.header(L["title"])
    e_tag = st.text_input(L["tag"])
    tech_name = st.text_input(L["sign"])

    sel_mat = st.selectbox("Material", ["ASTM A193 B7 (Inch)", "Metric Grade 8.8 (mm)", "ASTM A193 B16 (Inch)"])
    u_type = "Imperial" if "Inch" in sel_mat else "Metric"
    sy_val = 105000 if u_type == "Imperial" else 92800

    col1, col2 = st.columns(2)
    with col1:
        sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
        tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
    with col2:
        tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
        k_val = st.selectbox("K-Factor", [0.11, 0.13, 0.15])

    # MATH
    d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
    torque = (k_val * d * (sy_val * As * 0.50)) / 12
    psi = torque / ENERPAC_CATALOG[tool_fam][tool_mod]

    st.info(f"Socket A/F: {SIZES_DB[u_type][sel_size]['af']}")
    st.metric("Target Torque", f"{round(torque)} Ft-Lb")
    st.metric("Pump Pressure", f"{round(psi)} PSI")

    # --- 7. SAVE TO CLOUD ---
    if st.button("Save Report"):
        try:
            r_df = get_data("Reports")
            new_report = pd.DataFrame([{
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"), 
                "Tag": e_tag, 
                "Torque": round(torque), 
                "PSI": round(psi), 
                "Technician": tech_name
            }])
            conn = st.connection("gsheets", type=GSheetsConnection)
            conn.update(worksheet="Reports", data=pd.concat([r_df, new_report], ignore_index=True))
            st.success("Report Synced to Google Sheets!")
        except Exception as e:
            st.error(f"Save failed: {e}")
                
