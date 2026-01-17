import streamlit as st

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Islam Mohamed - Torque Pro", layout="wide")

# --- BILINGUAL DATABASE ---
DATA = {
    "Sizes": {
        "M24": {"d": 0.945, "As": 0.547},
        "M30": {"d": 1.181, "As": 0.869},
        "M36": {"d": 1.417, "As": 1.266},
        "M64": {"d": 2.520, "As": 4.148},
    },
    "Tools": {
        "Enerpac S3000": {"factor": 0.3225, "unit": "PSI"},
        "Unior 1700/3": {"factor": 4.81, "unit": "Bar"}
    }
}

# --- TRANSLATIONS ---
LANG = {
    "English": {
        "title": "Industrial Torque Manager",
        "size": "Select Stud Size",
        "tool": "Select Hydraulic Tool",
        "calc": "Calculate Pressure",
        "torque": "Target Torque",
        "pressure": "Pump Setting",
        "safety": "Safety Warning: Keep hands clear of reaction arm!",
        "footer": "Designed by: Eng. Islam Mohamed"
    },
    "Arabic": {
        "title": "مدير العزم الصناعي",
        "size": "اختر مقاس المسمار",
        "tool": "اختر المعدة الهيدروليكية",
        "calc": "احسب الضغط",
        "torque": "العزم المطلوب",
        "pressure": "ضبط المضخة",
        "safety": "تحذير سلامة: ابعد اليدين عن ذراع رد الفعل!",
        "footer": "تصميم المهندس: إسلام محمد"
    }
}

# --- UI INTERFACE ---
sel_lang = st.sidebar.radio("Language / اللغة", ["English", "Arabic"])
T = LANG[sel_lang]

st.title(T["title"])
st.write(f"### {T['footer']}")

col1, col2 = st.columns(2)

with col1:
    size = st.selectbox(T["size"], list(DATA["Sizes"].keys()))
    tool = st.selectbox(T["tool"], list(DATA["Tools"].keys()))

# --- CALCULATION LOGIC ---
# Standard B7 Grade, Moly Lubricant (K=0.11), 50% Yield Target
K = 0.11
Sy = 105000
d = DATA["Sizes"][size]["d"]
As = DATA["Sizes"][size]["As"]

target_torque = (K * d * (Sy * As * 0.50)) / 12
tool_factor = DATA["Tools"][tool]["factor"]
unit = DATA["Tools"][tool]["unit"]

if "Enerpac" in tool:
    pump_res = target_torque / tool_factor
else:
    # Convert Ft-Lbs to Nm for Unior
    pump_res = (target_torque * 1.355) / tool_factor

with col2:
    st.metric(T["torque"], f"{round(target_torque)} Ft-Lbs")
    st.metric(T["pressure"], f"{round(pump_res)} {unit}")

st.divider()
st.error(T["safety"])

# --- VISUAL GUIDES ---
st.subheader("Tightening Sequence / ترتيب الربط")
st.write("Follow the Star Pattern (ASME PCC-1)")

