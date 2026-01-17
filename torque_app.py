import streamlit as st

st.set_page_config(page_title="Islam Mohamed | Maintenance Pro", layout="wide")

# --- DATABASE: STUDS & NUTS ---
STUDS_DB = {
    "Metric (Grade 8.8)": {"Sy": 92800, "units": "Metric"},
    "Metric (Grade 10.9)": {"Sy": 130500, "units": "Metric"},
    "ASTM A193 B7 (High Temp)": {"Sy": 105000, "units": "Imperial"},
    "ASTM A193 B16 (Alloy)": {"Sy": 105000, "units": "Imperial"},
    "ASTM A320 L7 (Low Temp)": {"Sy": 105000, "units": "Imperial"},
    "Stainless Steel (B8/B8M)": {"Sy": 30000, "units": "Imperial"}
}

SIZES_DB = {
    "M24": {"d": 0.945, "As": 0.547},
    "M27": {"d": 1.063, "As": 0.712},
    "M30": {"d": 1.181, "As": 0.869},
    "M33": {"d": 1.299, "As": 1.076},
    "M36": {"d": 1.417, "As": 1.266},
    "M45": {"d": 1.771, "As": 2.055},
    "M52": {"d": 2.047, "As": 2.810},
    "M64": {"d": 2.520, "As": 4.148},
    "1\"-8UN": {"d": 1.000, "As": 0.606},
    "1-1/8\"-8UN": {"d": 1.125, "As": 0.790},
    "1-1/4\"-8UN": {"d": 1.250, "As": 1.000},
    "1-1/2\"-8UN": {"d": 1.500, "As": 1.492},
    "2\"-8UN": {"d": 2.000, "As": 2.770}
}

# --- DATABASE: ALL ENERPAC WRENCHES ---
ENERPAC_TOOLS = {
    "S1500": 0.1897, "S3000": 0.3225, "S6000": 0.6124, "S11000": 1.1260, "S25000": 2.5120,
    "W2000": 0.2031, "W4000": 0.4125, "W8000": 0.8250, "W15000": 1.5120, "W22000": 2.2150,
    "RSQ1500": 0.1897, "RSQ3000": 0.3225, "RSQ6000": 0.6124
}

LUBRICANTS = {
    "Moly Paste (K=0.11)": 0.11,
    "Nickel Anti-Seize (K=0.13)": 0.13,
    "Copper Anti-Seize (K=0.15)": 0.15,
    "Zinc Plated / Dry (K=0.20)": 0.20
}

# --- TRANSLATIONS ---
T = {
    "English": {
        "title": "Master Torque System",
        "stud_type": "Stud/Nut Material",
        "size": "Select Size",
        "lube": "Lubricant Type",
        "tool": "Enerpac Model",
        "yield": "Target Yield %",
        "res_torque": "Target Torque",
        "res_psi": "Pump Pressure (PSI)",
        "footer": "Eng. Islam Mohamed - Mechanical Integrity"
    },
    "Arabic": {
        "title": "نظام التحكم في العزم المتقدم",
        "stud_type": "نوع المسمار / الصامولة",
        "size": "مقاس المسمار",
        "lube": "نوع التشحيم",
        "tool": "طراز Enerpac",
        "yield": "نسبة الشد المستهدفة %",
        "res_torque": "العزم المطلوب",
        "res_psi": "ضغط المضخة (PSI)",
        "footer": "م. إسلام محمد - قسم السلامة الميكانيكية"
    }
}

# --- APP UI ---
lang = st.sidebar.radio("Language", ["English", "Arabic"])
L = T[lang]

st.title(L["title"])
st.caption(L["footer"])

with st.container():
    c1, c2, c3 = st.columns(3)
    with c1:
        s_type = st.selectbox(L["stud_type"], list(STUDS_DB.keys()))
        s_size = st.selectbox(L["size"], list(SIZES_DB.keys()))
    with c2:
        s_lube = st.selectbox(L["lube"], list(LUBRICANTS.keys()))
        s_tool = st.selectbox(L["tool"], list(ENERPAC_TOOLS.keys()))
    with c3:
        s_yield = st.slider(L["yield"], 30, 90, 50)

# --- CALCULATIONS ---
K = LUBRICANTS[s_lube]
Sy = STUDS_DB[s_type]["Sy"]
d = SIZES_DB[s_size]["d"]
As = SIZES_DB[s_size]["As"]
factor = ENERPAC_TOOLS[s_tool]

target_torque = (K * d * (Sy * As * (s_yield/100))) / 12
psi = target_torque / factor

# --- DISPLAY ---
st.divider()
st.info(f"Engineering Reference: {s_type} | {s_size}")
r1, r2 = st.columns(2)
r1.metric(L["res_torque"], f"{round(target_torque)} Ft-Lb / {round(target_torque * 1.355)} Nm")
r2.metric(L["res_psi"], f"{round(psi)} PSI")

if psi > 10000:
    st.error("🚨 PRESSURE OVER LIMIT (10,000 PSI) - CHANGE TOOL SIZE!")

st.divider()

