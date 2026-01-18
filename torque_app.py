import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime
from io import BytesIO

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Enterprise Maintenance", layout="centered")

# --- 2. GOOGLE SHEETS CONNECTION ---
try:
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
            u = st.text_input("Username", key="l_user")
            p = st.text_input("Password", type="password", key="l_pass")
            if st.button("Login"):
                try:
                    users_df = conn.read(worksheet="Users")
                    users_df['Username'] = users_df['Username'].astype(str).str.strip()
                    users_df['Password'] = users_df['Password'].astype(str).str.strip()
                    user_match = users_df[(users_df['Username'] == u) & (users_df['Password'] == p)]
                    
                    if not user_match.empty:
                        st.session_state.authenticated = True
                        st.session_state.current_user = u
                        st.rerun()
                    else:
                        st.error("❌ Invalid Credentials.")
                except Exception as e:
                    st.error(f"System Error: {e}")

        with tab2:
            nu = st.text_input("New Username", key="s_user")
            np = st.text_input("New Password", type="password", key="s_pass")
            if st.button("Register Account"):
                try:
                    users_df = conn.read(worksheet="Users")
                    if nu in users_df['Username'].values:
                        st.warning("Username already exists!")
                    else:
                        new_user = pd.DataFrame([{"Username": nu, "Password": np}])
                        updated_users = pd.concat([users_df, new_user], ignore_index=True)
                        conn.update(worksheet="Users", data=updated_users)
                        st.success("✅ Account created! Please Login.")
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
    
    # Show Admin Dashboard ONLY for 'admin' user
    is_admin = st.session_state.current_user == "admin"
    if is_admin:
        with col_admin:
            show_admin = st.checkbox("⚙️ Admin")
    else:
        show_admin = False

    if lang == "Arabic":
        st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
        L = {"title": "نظام إدارة العزم الصناعي", "tag": "رقم المعدة", "print": "طباعة PDF", "save": "مزامنة السحاب", "sign": "التوقيع الرقمي (الاسم):"}
    else:
        L = {"title": "Industrial Bolting Master", "tag": "Equipment Tag", "print": "Print PDF", "save": "Cloud Sync", "sign": "Digital Signature (Name):"}

    # --- 5. ADMIN VIEW ---
    if show_admin:
        st.divider()
        
