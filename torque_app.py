import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. DATABASE CONNECTION ---
# This connects to your Google Sheet URL (defined in .streamlit/secrets.toml)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. AUTHENTICATION LOGIC ---
def auth_system():
    # Read existing users from Google Sheets
    existing_users = conn.read(worksheet="Users", usecols=[0, 1])
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Industrial Portal")
        tab1, tab2 = st.tabs(["Login", "Create Account"])
        
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Login"):
                user_match = existing_users[(existing_users['Username'] == u) & (existing_users['Password'] == p)]
                if not user_match.empty:
                    st.session_state.authenticated = True
                    st.session_state.current_user = u
                    st.rerun()
                else: st.error("Invalid Username or Password")
                
        with tab2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Sign Up"):
                # Add new user to the dataframe and update Google Sheets
                new_user_data = pd.DataFrame([{"Username": nu, "Password": np}])
                updated_df = pd.concat([existing_users, new_user_data], ignore_index=True)
                conn.update(worksheet="Users", data=updated_df)
                st.success("Account Created in Google Sheets! Please Login.")
        return False
    return True

if auth_system():
    # [Rest of your Bolt/Enerpac logic remains here...]
    st.write(f"Welcome, {st.session_state.current_user}")
    
    # --- 3. SAVING REPORTS PERMANENTLY ---
    if st.button("Save to Cloud"):
        report_data = conn.read(worksheet="Reports")
        new_entry = pd.DataFrame([{
            "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "Tag": "E-101", # Example
            "Torque": 1200, 
            "PSI": 3500,
            "Technician": st.session_state.current_user
        }])
        final_reports = pd.concat([report_data, new_entry], ignore_index=True)
        conn.update(worksheet="Reports", data=final_reports)
        st.success("Report Synced to Google Drive!")
        
