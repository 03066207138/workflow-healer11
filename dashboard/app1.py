# ============================================================
# 💰 Workflow Healer – Hackathon Edition
# IBM × Paywalls.ai × FlowXO — Self-Healing AI Automation
# Simplified Interface for Clear Demo Presentation
# ============================================================

import os, requests, pandas as pd, streamlit as st
from datetime import datetime

# ------------------------------------------------------------
# 🌐 Backend Configuration
# ------------------------------------------------------------
BACKEND = os.getenv("HEALER_BACKEND_URL", "https://workflow-healer11-2.onrender.com").rstrip("/")
st.set_page_config(page_title="💎 Workflow Healer", page_icon="💰", layout="wide")

# ------------------------------------------------------------
# 🎨 Minimal Dark Theme
# ------------------------------------------------------------
st.markdown("""
<style>
body, .stApp { background-color:#0f172a; color:#f8fafc; font-family:'Inter',sans-serif; }
h1, h2, h3 { color:#60a5fa; }
section[data-testid="stSidebar"] { background:#111827!important; border-right:1px solid rgba(255,255,255,.08); }
.stButton button { background:linear-gradient(135deg,#2563eb,#1d4ed8); color:white; border:none; border-radius:10px; font-weight:600; }
.stButton button:hover { background:linear-gradient(135deg,#1d4ed8,#2563eb); transform:scale(1.03); }
.metric-box { background:#1e293b; padding:1rem; border-radius:10px; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 🔧 Utility Functions
# ------------------------------------------------------------
def get_json(url):
    try:
        r = requests.get(url, timeout=8)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def post_json(url, data=None):
    try:
        r = requests.post(url, json=data, timeout=8)
        return r.status_code
    except: return None

# ------------------------------------------------------------
# ⚙️ Sidebar Controls
# ------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Controls")

    if st.button("🔎 Check Backend"):
        health = get_json(f"{BACKEND}/health")
        if health:
            st.success(f"✅ Connected — Mode: {health.get('mode','Offline')}")
            st.json(health)
        else:
            st.error("❌ Backend not reachable")

    st.divider()
    st.markdown("### 🔁 Simulation Control")
    if st.button("🚀 Start Simulation"): post_json(f"{BACKEND}/sim/start"); st.success("Simulation started.")
    if st.button("🧊 Stop Simulation"): post_json(f"{BACKEND}/sim/stop"); st.warning("Simulation stopped.")

    st.divider()
    st.markdown("### ⚡ Manual Healing")
    anomaly = st.selectbox("Select anomaly", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("💫 Run Healing"):
        code = post_json(f"{BACKEND}/simulate?event={anomaly}")
        st.success("Healing triggered!") if code == 200 else st.error("Failed to run healing.")

    st.divider()
    st.markdown("### 🌐 FlowXO Webhook")
    wf = st.selectbox("Workflow", ["invoice_processing","order_processing","customer_support"])
    a = st.selectbox("Anomaly Type", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("🚨 Send Webhook"):
        payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
        code = post_json(f"{BACKEND}/integrations/flowxo/webhook", payload)
        st.success("Webhook sent!") if code == 200 else st.error("Webhook failed.")

# ------------------------------------------------------------
# 🧠 Header
# ------------------------------------------------------------
st.title("💎 Workflow Healer – Self-Healing AI for Business Workflows")
st.caption("Automate, Heal, and Monetize enterprise workflows in real time — powered by Paywalls.ai & FlowXO.")

# ------------------------------------------------------------
# 📊 System Status
# ------------------------------------------------------------
health = get_json(f"{BACKEND}/health")
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Groq AI", "✅ Ready" if health.get("groq_ready") else "❌ Off")
col2.metric("💰 Paywalls.ai", "✅ Connected" if health.get("paywalls_ready") else "❌ Off")
col3.metric("🌐 FlowXO", "✅ Active" if health.get("flowxo_ready") else "❌ Off")

if health.get("paywalls_ready") and health.get("flowxo_ready"):
    st.success("🚀 Monetization & Automation loop active.")
else:
    st.warning("⚠️ Some integrations inactive — demo will run in simulation mode.")

st.caption(f"Backend: {BACKEND}")

# ------------------------------------------------------------
# 📈 Healing KPIs
# ------------------------------------------------------------
metrics = get_json(f"{BACKEND}/metrics/summary")
revenue = get_json(f"{BACKEND}/metrics/revenue").get("total_revenue", 0)
c1, c2, c3, c4 = st.columns(4)
c1.metric("🩺 Total Healings", metrics.get("healings", 0))
c2.metric("⚙️ Avg Recovery %", f"{metrics.get('avg_recovery_pct',0):.2f}")
c3.metric("🎯 Avg Reward", f"{metrics.get('avg_reward',0):.2f}")
c4.metric("💰 Total Revenue ($)", f"{float(revenue):.2f}")

# ------------------------------------------------------------
# 🚨 Recent Healing Logs
# ------------------------------------------------------------
st.subheader("🧾 Recent Healing Activity")
logs = get_json(f"{BACKEND}/healing/logs?n=20").get("logs", [])
if logs:
    st.text_area("Live Healing Log", "\n".join(logs[-8:]), height=180)
else:
    st.info("📭 No healing activity yet. Start a simulation to generate logs.")

# ------------------------------------------------------------
# 📥 Downloads
# ------------------------------------------------------------
st.subheader("📥 Export Data")
col1, col2 = st.columns(2)
if col1.button("📜 Download Healing Log"):
    txt = "\n".join(logs)
    st.download_button("Save Log", txt.encode(), "healing_log.txt")
if col2.button("💰 Download Metrics"):
    csv = get_json(f"{BACKEND}/metrics/download")
    st.download_button("Save CSV", str(csv).encode(), "metrics_log.csv")

st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}  |  © 2025 Workflow Healer by Saher Pervaiz")
