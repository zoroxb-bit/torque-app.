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
            st.warning("ابعد اليدين عن ذراع رد الفعل. استخدم تيلة الأمان. ارتدِ مهمات الوقاية.")
    with col_rep:
        if st.button("📝 مساعدة التقرير"):
            st.success("املأ بيانات المعدة، ارفع الصورة، ثم اضغط على طباعة التقرير.")
            
    L = {
        "title": "نظام التحكم في الفلانجات المتقدم",
        "eq_header": "بيانات المعدة وتصريح العمل",
        "tag": "رقم المعدة", "flange": "رقم الفلانجة", "permit": "رقم تصريح العمل",
        "mat": "مادة المسمار", "size": "مقاس المسمار", "tool": "طراز Enerpac",
        "af": "مقاس اللقمة (A/F)", "res_t": "العزم المطلوب", "res_p": "ضبط المضخة (PSI)",
        "seq": "ترتيب عملية الربط", "bolts": "عدد المسامير", "print": "طباعة التقرير النهائي",
        "sign": "توقيع الفني:", "footer": "قسم الصيانة الميكانيكية - م. إسلام محمد"
    }

# --- 3. EXPANDED DATABASES ---
SIZES_DB = {
    "Imperial": {
        "3/4\"-10UNC": {"d": 0.750, "As": 0.334, "af": "1-1/4\""},
        "7/8\"-9UNC": {"d": 0.875, "As": 0.462, "af": "1-7/16\""},
        "1\"-8UN": {"d": 1.000, "As": 0.606, "af": "1-5/8\""},
        "1-1/2\"-8UN": {"d": 1.500, "As": 1.492, "af": "2-3/8\""},
        "2\"-8UN": {"d": 2.000, "As": 2.770, "af": "3-1/8\""},
        "3\"-8UN": {"d": 3.000, "As": 6.510, "af": "4-5/8\""},
        "4\"-8UN": {"d": 4.000, "As": 11.870, "af": "6-1/8\""}
    },
    "Metric": {
        "M30": {"d": 1.181, "As": 0.869, "af": "46 mm"},
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
