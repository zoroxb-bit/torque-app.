import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Enterprise Maintenance", layout="centered")

# --- 2. GOOGLE SHEETS CONNECTION ---
try:
    # ttl=0 is mandatory to prevent the "Invalid Credentials" delay
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Cloud Connection Error: {e}")

# --- 3. THE "STRICT" AUTHENTICATION SYSTEM ---
def auth_system():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Maintenance Portal")
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            # .strip() removes accidental spaces from user input
            u_input = st.text_input("Username", key="l_user").strip()
            p_input = st.text_input("Password", type="password", key="l_pass").strip()
            
            if st.button("Login"):
                try:
                    # Clear internal cache to see the very latest sheet data
                    st.cache_data.clear() 
                    
                    # Read Users worksheet
                    df = conn.read(worksheet="Users", ttl=0)
                    
                    # --- CRITICAL FIX: DATA NORMALIZATION ---
                    # 1. Convert everything to String (prevents numeric password errors)
                    # 2. Strip all invisible spaces from the Sheet
                    df['Username'] = df['Username'].astype(str).str.strip()
                    df['Password'] = df['Password'].astype(str).str.strip()
                    
                    # 3. Check for match (Case-insensitive for Username)
                    user_match = df[
                        (df['Username'].str.lower() == u_input.lower()) & 
                        (df['Password'] == p_input)
                    ]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.current_user = u_input
                        st.rerun()
                    else:
                        # Debugging help for the Admin
                        st.error("❌ Invalid Credentials.")
                        if u_input == "admin":
                            st.info("Tip: Check if the 'Users' sheet has headers 'Username' and 'Password'.")
                except Exception as e:
                    st.error(f"System Error: {e}")

        with tab2:
            nu = st.text_input("New Username", key="s_user").strip()
            np = st.text_input("New Password", type="password", key="s_pass").strip()
            if st.button("Register Account"):
                try:
                    df = conn.read(worksheet="Users", ttl=0)
                    if nu.lower() in df['Username'].astype(str).str.lower().str.strip().values:
                        st.warning("Username already exists!")
                    else:
                        new_user = pd.DataFrame([{"Username": nu, "Password": np}])
                        updated_df = pd.concat([df, new_user], ignore_index=True)
                        conn.update(worksheet="Users", data=updated_df)
                        st.success("✅ Account created! Wait 3 seconds and Login.")
                except Exception as e:
                    st.error(f"Sync Failed: {e}")
        return False
    return True

if auth_system():
    # --- 4. NAVIGATION & ADMIN DASHBOARD ---
    lang = st.radio("Language", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")
    
    col_sop, col_safe, col_admin, col_logout = st.columns(4)
    with col_logout: 
        if st.button("Logout"): 
            st.session_state.authenticated = False
            st.rerun()
    
    if st.session_state.current_user.lower() == "admin":
        with col_admin: show_admin = st.checkbox("⚙️ Admin")
    else: show_admin = False

    # --- 5. DATA LOG (ADMIN ONLY) ---
    if show_admin:
        st.divider()
        st.subheader("🛠️ User Management")
        u_df = conn.read(worksheet="Users", ttl=0)
        st.dataframe(u_df) # This allows you to see exactly how passwords look in the sheet

    # --- 6. CALCULATOR (ALL ENERPAC & BOLT DATA KEPT) ---
    SIZES_DB = {
        "Imperial": {
            "3/4\"-10": {"d": 0.75, "As": 0.334, "af": "1-1/4\""}, "1\"-8": {"d": 1.0, "As": 0.606, "af": "1-5/8\""},
            "2\"-8": {"d": 2.0, "As": 2.77, "af": "3-1/8\""}, "3\"-8": {"d": 3.0, "As": 6.51, "af": "4-5/8\""},
            "4\"-8": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
        },
        "Metric": {
            "M30": {"d": 1.18, "As": 0.869, "af": "46mm"}, "M36": {"d": 1.41, "As": 1.266, "af": "55mm"},
            "M64": {"d": 2.52, "As": 4.148, "af": "95mm"}, "M100": {"d": 3.93, "As": 10.74, "af": "145mm"}
        }
    }

    ENERPAC_CATALOG = {
        "S-Series (Standard)": {"S1500": 0.1897, "S3000": 0.3225, "S11000": 1.126},
        "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W22000X": 2.215}
    }

    st.header("Industrial Bolting Master" if lang=="English" else "نظام إدارة العزم")
    e_tag = st.text_input("Tag / رقم المعدة")
    tech_name = st.text_input("Technician Name / اسم الفني")

    sel_mat = st.selectbox("Material", ["ASTM A193 B7", "Grade 8.8", "Grade 10.9"])
    u_type = "Imperial" if "ASTM" in sel_mat else "Metric"
    
    col1, col2 = st.columns(2)
    with col1:
        sel_size = st.selectbox("Size", list(SIZES_DB[u_type].keys()))
        tool_fam = st.selectbox("Series", list(ENERPAC_CATALOG.keys()))
    with col2:
        tool_mod = st.selectbox("Model", list(ENERPAC_CATALOG[tool_fam].keys()))
        k_val = st.selectbox("K-Factor", [0.11, 0.13, 0.15])

    # CALCULATIONS
    d, As = SIZES_DB[u_type][sel_size]["d"], SIZES_DB[u_type][sel_size]["As"]
    sy = 105000 if u_type=="Imperial" else 92800
    torque = (k_val * d * (sy * As * 0.50)) / 12
    psi = torque / ENERPAC_CATALOG[tool_fam][tool_mod]

    st.metric("Target Torque", f"{round(torque)} Ft-Lb")
    st.metric("Pump Pressure", f"{round(psi)} PSI")

    if st.button("Save Report"):
        try:
            r_df = conn.read(worksheet="Reports", ttl=0)
            new_row = pd.DataFrame([{"Date": datetime.datetime.now().strftime("%Y-%m-%d"), "Tag": e_tag, "Torque": round(torque), "PSI": round(psi), "Technician": tech_name}])
            conn.update(worksheet="Reports", data=pd.concat([r_df, new_row], ignore_index=True))
            st.success("Report Saved to Cloud!")
        except Exception as e: st.error(f"Save Failed: {e}")
