# ============================================================
# 💎 Workflow Healer – Simplified Streamlit Dashboard
# Powered by Paywalls.ai × FlowXO × Groq (v5.0 – Clean UI)
# ============================================================

import os, requests, pandas as pd, streamlit as st
from datetime import datetime

BACKEND = os.getenv("HEALER_BACKEND_URL", "https://workflow-healer11-2.onrender.com").rstrip("/")
st.set_page_config(page_title="💎 Workflow Healer", layout="wide", page_icon="💰")

# ============================================================
# 🎨 Simplified Theme
# ============================================================
st.markdown("""
<style>
body, .stApp {
  background-color: #0f172a;
  color: #f8fafc;
  font-family: 'Inter', sans-serif;
}
h1, h2, h3, h4 { color: #60a5fa; }
section[data-testid="stSidebar"] {
  background-color: #111827 !important;
  color: #e2e8f0 !important;
  border-right: 1px solid rgba(255,255,255,0.08);
}
.stButton button {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white; font-weight: 600;
  border-radius: 10px; border: none; padding: .5rem 1rem;
}
.stButton button:hover {
  background: linear-gradient(135deg, #1d4ed8, #2563eb);
  transform: scale(1.02);
}
.metric-card {
  background: #1e293b; padding: 1rem; border-radius: 12px;
  text-align: center; margin: 5px; box-shadow: 0 0 8px rgba(96,165,250,.25);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔧 Utility Functions
# ============================================================
def safe_get(url):
    try:
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def safe_post(url, json_data=None):
    try:
        r = requests.post(url, json=json_data, timeout=8)
        return r.status_code
    except:
        return None

# ============================================================
# 🧭 Sidebar Controls
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Controls")
    
    if st.button("🔍 Check Backend"):
        health = safe_get(f"{BACKEND}/health")
        if health:
            st.success(f"✅ Connected — {health.get('mode','Simulation Mode')}")
            st.json(health)
        else:
            st.error("❌ Backend not reachable")

    st.divider()
    st.markdown("### 🔁 Simulation Control")
    if st.button("🚀 Start Simulation"): safe_post(f"{BACKEND}/sim/start"); st.info("Simulation started.")
    if st.button("🧊 Stop Simulation"): safe_post(f"{BACKEND}/sim/stop"); st.warning("Simulation stopped.")

    st.divider()
    st.markdown("### 💥 Run Healing Manually")
    event = st.selectbox("Select anomaly", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("💫 Run Healing Cycle"):
        code = safe_post(f"{BACKEND}/simulate?event={event}")
        if code == 200: st.success("Healing executed successfully!")
        else: st.warning("Could not run healing. Check backend.")

    st.divider()
    st.markdown("### 🌐 Trigger via FlowXO")
    wf = st.selectbox("Workflow", ["invoice_processing","order_processing","customer_support"])
    a = st.selectbox("Anomaly Type", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("🚨 Send Webhook"):
        payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
        code = safe_post(f"{BACKEND}/integrations/flowxo/webhook", payload)
        st.success("Webhook sent!") if code == 200 else st.error("Webhook failed.")

# ============================================================
# 🧠 Header
# ============================================================
st.title("💰 Workflow Healer – AI-Powered Automation")
st.caption("Heal, Automate, and Monetize workflows in real time using AI, Paywalls.ai & FlowXO.")

# ============================================================
# 🔗 System Status
# ============================================================
health = safe_get(f"{BACKEND}/health")
mode = health.get("mode", "Offline")
paywalls = health.get("paywalls_ready", False)
flowxo = health.get("flowxo_ready", False)
groq = health.get("groq_ready", False)

col1, col2, col3 = st.columns(3)
col1.metric("⚡ Groq Local AI", "✅ Ready" if groq else "❌ Off")
col2.metric("💰 Paywalls.ai", "✅ Connected" if paywalls else "❌ Off")
col3.metric("🌐 FlowXO Webhook", "✅ Active" if flowxo else "❌ Off")

if paywalls and flowxo:
    st.success("🚀 Monetization and automation fully active.")
else:
    st.warning("⚠️ Some integrations are inactive.")

# ============================================================
# 📊 Metrics Overview
# ============================================================
st.subheader("📈 Healing & Monetization Summary")
metrics = safe_get(f"{BACKEND}/metrics/summary")
rev = safe_get(f"{BACKEND}/metrics/revenue")
revenue = float(rev.get("total_revenue", 0))
cols = st.columns(4)
cols[0].metric("Total Healings", f"{metrics.get('healings',0)}")
cols[1].metric("Avg Recovery %", f"{metrics.get('avg_recovery_pct',0):.2f}")
cols[2].metric("Avg Reward", f"{metrics.get('avg_reward',0):.2f}")
cols[3].metric("Total Revenue ($)", f"{revenue:.2f}")

# ============================================================
# 🚨 Latest Healing Info
# ============================================================
st.subheader("🧾 Latest Healing Activity")
logs = safe_get(f"{BACKEND}/healing/logs?n=40").get("logs", [])
if logs:
    st.success("✅ Healing events successfully executed.")
    st.text_area("Recent Healing Log", "\n".join(logs[-8:]), height=200)
else:
    st.info("📭 No healing logs yet — start a simulation to see updates.")

# ============================================================
# 📥 Export Data
# ============================================================
st.subheader("📥 Export Data")
c1, c2 = st.columns(2)
if c1.button("📜 Download Healing Log"):
    txt = "\n".join(logs)
    st.download_button("Save Log", data=txt.encode("utf-8"), file_name="healing_log.txt")
if c2.button("💰 Download Revenue Report"):
    csv = safe_get(f"{BACKEND}/metrics/download")
    st.download_button("Save CSV", data=str(csv).encode("utf-8"), file_name="metrics_log.csv")

st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')} | Backend: {BACKEND}")
