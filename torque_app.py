import streamlit as st

# --- 1. INITIAL APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Flange Integrity Master", layout="centered")

# --- 2. TOP HEADLINE NAVIGATION & LOGO ---
# Logo and Headline Layout
top_col1, top_col2 = st.columns([1, 3])
with top_col1:
    # Use a professional icon or your company logo URL here
    st.title("⚙️") 
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
        if st.button("📝 Report"):
            st.success("QC Check: Record PSI, Tool SN, and take a photo of the witness marks.")
    
    L = {
        "title": "Industrial Bolting Master",
        "mat": "Stud Material", "size": "Stud Size", "tool": "Enerpac Model",
        "af": "Nut Socket (A/F)", "res_t": "Target Torque", "res_p": "Pump PSI",
        "seq": "Tightening Sequence", "bolts": "Number of Bolts",
        "footer": "Mechanical Maintenance - Eng. Islam Mohamed"
    }
else:
    # RTL and Arabic Support
    st.markdown('<style>body {direction: rtl; text-align: right;}</style>', unsafe_allow_html=True)
    with col_sop:
        if st.button("📖 دليل العمل"):
            st.info("ASME PCC-1: 1. تنظيف القلاوظ. 2. التشحيم. 3. الربط على مراحل ٣٠٪، ٦٠٪، ١٠٠٪.")
    with col_safe:
        if st.button("⚠️ السلامة"):
            st.warning("ابعد اليدين عن ذراع رد الفعل. استخدم تيلة الأمان. ارتدِ مهمات الوقاية.")
    with col_rep:
        if st.button("📝 التقرير"):
            st.success("فحص الجودة: سجل الضغط، رقم المعدة، وصور علامات المطابقة.")
            
    L = {
        "title": "نظام التحكم في الفلانجات المتقدم",
        "mat": "مادة المسمار", "size": "مقاس المسمار", "tool": "طراز Enerpac",
        "af": "مقاس اللقمة (A/F)", "res_t": "العزم المطلوب", "res_p": "ضبط المضخة (PSI)",
        "seq": "ترتيب عملية الربط", "bolts": "عدد المسامير",
        "footer": "قسم الصيانة الميكانيكية - م. إسلام محمد"
    }

# --- 3. FULL ENERPAC & STUD DATABASES ---
STUDS_DB = {
    "ASTM A193 B7 (Inch)": {"type": "Imperial", "Sy": 105000},
    "ASTM A193 B16 (Inch)": {"type": "Imperial", "Sy": 105000},
    "Metric Grade 8.8 (mm)": {"type": "Metric", "Sy": 92800},
    "Metric Grade 10.9 (mm)": {"type": "Metric", "Sy": 130500},
    "ASTM A320 L7 (Low Temp)": {"type": "Imperial", "Sy": 105000}
}

SIZES_DB = {
    "Imperial": {
        "1-1/2\"-8UN": {"d": 1.5, "As": 1.49, "af": "2-3/8\""},
        "2\"-8UN": {"d": 2.0, "As": 2.77, "af": "3-1/8\""},
        "2-1/2\"-8UN": {"d": 2.5, "As": 4.44, "af": "3-7/8\""},
        "3\"-8UN": {"d": 3.0, "As": 6.51, "af": "4-5/8\""},
        "4\"-8UN": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
    },
    "Metric": {
        "M36": {"d": 1.41, "As": 1.26, "af": "55mm"},
        "M45": {"d": 1.77, "As": 2.05, "af": "70mm"},
        "M52": {"d": 2.04, "As": 2.81, "af": "80mm"},
        "M64": {"d": 2.52, "As": 4.14, "af": "95mm"},
        "M80": {"d": 3.15, "As": 6.70, "af": "115mm"},
        "M100": {"d": 3.93, "As": 10.7, "af": "145mm"}
    }
}

ENERPAC_CATALOG = {
    "S-Series (Square Drive)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.1260, "S25000X": 2.5120},
    "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.8250, "W15000X": 1.5120, "W22000X": 2.2150},
    "RSL-Series (Slim Line)": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL5000": 0.5312, "RSL8000": 0.7831}
}

# --- 4. MAIN CALCULATOR ---
st.header(L["title"])
st.divider()

sel_mat = st.selectbox(L["mat"], list(STUDS_DB.keys()))
u_type = STUDS_DB[sel_mat]["type"]
sy_val = STUDS_DB[sel_mat]["Sy"]

col_input1, col_input2 = st.columns(2)
with col_input1:
    sel_size = st.selectbox(L["size"], list(SIZES_DB[u_type].keys()))
    tool_fam = st.selectbox("Tool Family", list(ENERPAC_CATALOG.keys()))
with col_input2:
    tool_mod = st.selectbox(L["tool"], list(ENERPAC_CATALOG[tool_fam].keys()))
    k_val = st.selectbox("Lube (K)", [0.11, 0.13, 0.15])

# Math
d = SIZES_DB[u_type][sel_size]["d"]
As = SIZES_DB[u_type][sel_size]["As"]
factor = ENERPAC_CATALOG[tool_fam][tool_mod]
torque = (k_val * d * (sy_val * As * 0.50)) / 12
psi = torque / factor

# --- 5. RESULTS ---
st.info(f"{L['af']}: {SIZES_DB[u_type][sel_size]['af']}")
res1, res2 = st.columns(2)
res1.metric(L["res_t"], f"{round(torque)} Ft-Lb")
res2.metric(L["res_p"], f"{round(psi)} PSI")

st.divider()
st.subheader(L["seq"])
num_bolts = st.number_input(L["bolts"], 4, 32, 12, step=4)
st.success("Sequence Generation: Standard Star Pattern Applied.")

st.caption(L["footer"])
