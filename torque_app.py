import streamlit as st

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Flange Integrity Ecosystem", layout="centered")

# --- 2. TOP HEADLINE NAVIGATION & LOGO ---
top_col1, top_col2 = st.columns([1, 3])
with top_col1:
    st.title("⚙️Semadco⚙️") 
with top_col2:
    lang = st.radio("Language / اللغة", ["English", "Arabic"], horizontal=True, label_visibility="collapsed")

# Top Navigation Buttons (Bilingual Headlines)
col_sop, col_safe, col_rep = st.columns(3)

if lang == "English":
    with col_sop:
        if st.button("📖 View SOP"):
            st.info("ASME PCC-1: 1. Clean threads. 2. Apply Lube. 3. Tighten in 30%, 60%, 100% stages.")
    with col_safe:
        if st.button("⚠️ Safety"):
            st.warning("Keep hands clear of reaction arm. Use safety pin on sockets. Wear PPE.")
    with col_rep:
        if st.button("📝 Report Help"):
            st.success("Fill the Equipment info, upload photo, then click Print Report.")
    
    L = {
        "title": "Industrial Bolting Master",
        "eq_header": "Equipment & Permit Information",
        "tag": "Equipment Tag", "flange": "Flange ID", "permit": "Work Permit No.",
        "mat": "Stud Material", "size": "Stud Size", "tool": "Enerpac Model",
        "af": "Nut Socket (A/F)", "res_t": "Target Torque", "res_p": "Pump PSI",
        "seq": "Tightening Sequence", "bolts": "Number of Bolts", "print": "Print Final Report",
        "sign": "Technician Signature:", "footer": "Mechanical Maintenance - Eng. Islam Mohamed"
    }
else:
    st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
    with col_sop:
        if st.button("📖 دليل العمل"):
            st.info("ASME PCC-1: 1. تنظيف القلاوظ. 2. التشحيم. 3. الربط على مراحل ٣٠٪، ٦٠٪، ١٠٠٪.")
    with col_safe:
        if st.button("⚠️ السلامة"):
            st.warning("ابعد اليدين عن ذراع
                       
