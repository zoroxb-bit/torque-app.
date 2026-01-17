import streamlit as st

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed | Flange Integrity Master", layout="wide")

# --- 1. MATERIAL & SIZE DATABASE ---
STUDS_DB = {
    "ASTM A193 B7 (Inch)": {"type": "Imperial", "Sy": 105000},
    "ASTM A193 B16 (Inch)": {"type": "Imperial", "Sy": 105000},
    "ASTM A320 L7 (Inch)": {"type": "Imperial", "Sy": 105000},
    "Metric Grade 8.8 (mm)": {"type": "Metric", "Sy": 92800},
    "Metric Grade 10.9 (mm)": {"type": "Metric", "Sy": 130500},
    "Stainless B8/B8M (Inch)": {"type": "Imperial", "Sy": 30000}
}

SIZES_DB = {
    "Imperial": {
        "1\"-8UN": {"d": 1.0, "As": 0.606, "af": "1-5/8\""},
        "1-1/2\"-8UN": {"d": 1.5, "As": 1.492, "af": "2-3/8\""},
        "2\"-8UN": {"d": 2.0, "As": 2.770, "af": "3-1/8\""},
        "2-1/2\"-8UN": {"d": 2.5, "As": 4.440, "af": "3-7/8\""},
        "3\"-8UN": {"d": 3.0, "As": 6.510, "af": "4-5/8\""},
        "4\"-8UN": {"d": 4.0, "As": 11.87, "af": "6-1/8\""}
    },
    "Metric": {
        "M24": {"d": 0.94, "As": 0.54, "af": "36mm"},
        "M36": {"d": 1.41, "As": 1.26, "af": "55mm"},
        "M45": {"d": 1.77, "As": 2.05, "af": "70mm"},
        "M52": {"d": 2.04, "As": 2.81, "af": "80mm"},
        "M64": {"d": 2.52, "As": 4.14, "af": "95mm"},
        "M80": {"d": 3.15, "As": 6.70, "af": "115mm"},
        "M100": {"d": 3.93, "As": 10.7, "af": "145mm"}
    }
}

# --- 2. COMPLETE ENERPAC CATALOG ---
ENERPAC_CATALOG = {
    "S-Series (Square Drive)": {"S1500X": 0.1897, "S3000X": 0.3225, "S6000X": 0.6124, "S11000X": 1.1260, "S25000X": 2.5120},
    "W-Series (Low Profile)": {"W2000X": 0.2031, "W4000X": 0.4125, "W8000X": 0.8250, "W15000X": 1.5120, "W22000X": 2.2150},
    "RSL-Series (Slim Line)": {"RSL1500": 0.1411, "RSL3000": 0.3069, "RSL8000": 0.7831, "RSL19000": 1.8950}
}

# --- 3. STAR PATTERN GENERATOR ---
def get_star_pattern(n):
    if n == 4: return [1, 3, 2, 4]
    if n == 8: return [1, 5, 3, 7, 2, 6, 4, 8]
    if n == 12: return [1, 7, 4, 10, 2, 8, 5, 11, 3, 9, 6, 12]
    if n == 16: return [1, 9, 5, 13, 3, 11, 7, 15, 2, 10, 6, 14, 4, 12, 8, 16]
    if n == 24: return [1, 13, 7, 19, 4, 16, 10, 22, 2, 14, 8, 20, 5, 17, 11, 23, 3, 15, 9, 21, 6, 18, 12, 24]
    return list(range(1, n + 1))

# --- 4. TRANSLATIONS ---
T = {
    "English": {
        "title": "Industrial Bolting Master",
        "mat": "Stud Material",
        "size": "Stud Size",
        "tool": "Enerpac Model",
        "af": "Nut Socket (A/F)",
        "res_t": "Target Torque",
        "res_p": "Pump PSI",
        "seq": "Tightening Sequence",
        "bolts": "Number of Bolts",
        "footer": "Mechanical Maintenance - Eng. Islam Mohamed"
    },
    "Arabic": {
        "title": "نظام التحكم في الفلانجات المتقدم",
        "mat": "مادة المسمار",
        "size": "مقاس المسمار",
        "tool": "طراز Enerpac",
        "af": "مقاس اللقمة (A/F)",
        "res_t": "العزم المطلوب",
        "res_p": "ضبط المضخة (PSI)",
        "seq": "ترتيب عملية الربط",
        "bolts": "عدد المسامير",
        "footer": "قسم الصيانة الميكانيكية - م. إسلام محمد"
    }
}

# --- 5. UI INTERFACE ---
lang = st.sidebar.radio("Language / اللغة", ["English", "Arabic"])
L = T[lang]

st.title(L["title"])
st.caption(L["footer"])

# Selection Logic
sel_mat = st.selectbox(L["mat"], list(STUDS_DB.keys()))
u_type = STUDS_DB[sel_mat]["type"]
sy_val = STUDS_DB[sel_mat]["Sy"]

col1, col2 = st.columns(2)
with col1:
    sel_size = st.selectbox(L["size"], list(SIZES_DB[u_type].keys()))
    tool_fam = st.selectbox("Wrench Family", list(ENERPAC_CATALOG.keys()))
    tool_mod = st.selectbox(L["tool"], list(ENERPAC_CATALOG[tool_fam].keys()))
with col2:
    k_val = st.selectbox("Lubricant (K)", [0.11, 0.13, 0.15, 0.20])
    num_bolts = st.number_input(L["bolts"], min_value=4, step=4, value=12)
    st.info(f"{L['af']}: {SIZES_DB[u_type][sel_size]['af']}")

# Calculations
d = SIZES_DB[u_type][sel_size]["d"]
As = SIZES_DB[u_type][sel_size]["As"]
factor = ENERPAC_CATALOG[tool_fam][tool_mod]

torque = (k_val * d * (sy_val * As * 0.50)) / 12
psi = torque / factor

# Display Results
st.divider()
r1, r2 = st.columns(2)
r1.metric(L["res_t"], f"{round(torque)} Ft-Lb")
r2.metric(L["res_p"], f"{round(psi)} PSI")

if psi > 10000: st.error("⚠️ REDUCE YIELD OR INCREASE TOOL SIZE!")

st.divider()
st.subheader(L["seq"])
pattern = get_star_pattern(num_bolts)
st.success(" → ".join(map(str, pattern)))



