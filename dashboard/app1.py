import os
import requests
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ============================================================
# 🌐 Backend Configuration
# ============================================================
BACKEND = os.getenv("HEALER_BACKEND_URL", "https://workflow-healer11-2.onrender.com")

st.set_page_config(
    page_title="Prototype to Profit – Workflow Healer",
    layout="wide",
    page_icon="💰"
)

# ============================================================
# 🎨 Global Theme
# ============================================================
st.markdown("""
<style>
:root {
  --bg-1: #0f172a;
  --bg-2: #1e293b;
  --fg: #e2e8f0;
  --accent: #60a5fa;
  --green: #34d399;
  --red: #f87171;
  --yellow: #fde047;
}
body {
  background: radial-gradient(circle at top left, var(--bg-1), var(--bg-2));
  color: var(--fg);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, sans-serif;
}
h1,h2,h3,h4 { color: var(--accent) !important; text-align:center; }
.metric { text-align:center; padding:10px; border-radius:12px; margin:4px; }
.success { background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.3); }
.warning { background:rgba(250,204,21,0.08); border:1px solid rgba(250,204,21,0.3); }
.info { background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.3); }
.error { background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); }
[data-testid="stMetricValue"] { color: var(--accent); font-weight: 700; }
section.main { padding: 1.2rem 2rem !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🧠 Header
# ============================================================
st.markdown("""
<h1>💰 Prototype-to-Profit: AI Workflow Healer</h1>
<p style="text-align:center; color:#94a3b8;">
AI-Powered Workflow Healing with <b>Paywalls.ai</b> × <b>FlowXO</b>
</p>
""", unsafe_allow_html=True)

# ============================================================
# ⚙️ Sidebar Controls
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Simulation Controls")

    def safe_json_get(url, timeout=5):
        try:
            r = requests.get(url, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            else:
                st.warning(f"⚠️ {url} → {r.status_code}")
                return None
        except Exception as e:
            st.error(f"❌ Error contacting backend: {e}")
            return None

    if st.button("🔎 Test Backend"):
        health = safe_json_get(f"{BACKEND}/health")
        if health:
            st.success(f"✅ Backend OK — Mode: {health.get('mode')} | Paywalls: {health.get('paywalls_ready')}")

    if st.button("🚀 Start Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/start", timeout=5)
            st.success("✅ Healing simulation started!" if res.status_code == 200 else f"⚠️ Could not start: {res.status_code}")
        except Exception as e:
            st.error(f"❌ Error starting: {e}")

    if st.button("🧊 Stop Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/stop", timeout=5)
            st.warning("🛑 Simulation stopped." if res.status_code == 200 else f"⚠️ Stop failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Error stopping: {e}")

    st.divider()
    st.markdown("### ⚡ Trigger Manual Healing")

    selected_event = st.selectbox("Select anomaly:", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])
    if st.button("💥 Trigger Healing"):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={selected_event}", timeout=7)
            if res.status_code == 200:
                rj = res.json()
                st.success(f"✅ {rj['workflow']} healed | Recovery: {rj['recovery_pct']}% | Billed via Paywalls.ai")
            else:
                st.warning(f"⚠️ Healing trigger failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Failed to trigger: {e}")

    st.divider()
    st.markdown("### 🔁 FlowXO Integration")

    wf = st.selectbox("Workflow:", ["invoice_processing", "order_processing", "customer_support"])
    anomaly = st.selectbox("Anomaly:", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])

    if st.button("🚨 Send FlowXO Webhook"):
        try:
            payload = {"workflow_id": wf, "anomaly": anomaly, "user_id": "demo_client"}
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            st.success("✅ FlowXO event processed!" if res.status_code == 200 else f"⚠️ Webhook failed ({res.status_code})")
            if res.status_code == 200:
                st.json(res.json())
        except Exception as e:
            st.error(f"❌ FlowXO webhook error: {e}")

# ============================================================
# 🔁 Auto Refresh
# ============================================================
st_autorefresh(interval=6000, key="refresh")

# ============================================================
# 📊 Unified Metrics & Monetization Dashboard
# ============================================================
try:
    metrics = requests.get(f"{BACKEND}/metrics/summary", timeout=7).json()
    rev_resp = requests.get(f"{BACKEND}/metrics/revenue", timeout=7)
    revenue_data = rev_resp.json() if rev_resp.status_code == 200 else {}
    logs_resp = requests.get(f"{BACKEND}/healing/logs?n=60", timeout=7)
    logs = logs_resp.json().get("logs", []) if logs_resp.status_code == 200 else []

    total_heals = float(metrics.get("healings", 0))
    avg_recovery = float(metrics.get("avg_recovery_pct", 0))
    avg_reward = float(metrics.get("avg_reward", 0))
    total_revenue = float(revenue_data.get("total_revenue", 0.0))
    avg_cost = total_revenue / max(total_heals, 1)

    # ---- Unified KPI Grid ----
    st.markdown("### ⚡ Unified Healing & Monetization KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🩺 Total Healings", f"{total_heals:.0f}")
    c2.metric("⚙️ Avg Recovery %", f"{avg_recovery:.2f}")
    c3.metric("🎯 Avg Reward", f"{avg_reward:.2f}")
    c4.metric("💰 Total Revenue ($)", f"{total_revenue:.2f}")

    # ---- Revenue Trend ----
  
  
  
        st.info("📭 No revenue logs found — start simulation or trigger healing.")

    # ---- Logs ----
    st.divider()
    st.markdown("### 🩹 Real-Time Healing Logs")
    if logs:
        for line in logs[:40]:
            style = "info"; icon = "💡"
            if "⚠️" in line: style, icon = "warning", "🟡"
            elif "✅" in line: style, icon = "success", "🟢"
            elif "❌" in line: style, icon = "error", "🔴"
            st.markdown(f"<div class='metric {style}'>{icon} {line}</div>", unsafe_allow_html=True)
    else:
        st.info("📭 No healing logs yet — run the simulator to view events.")

    st.caption(f"⏱️ Auto-refresh every 6s — Last update: {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.error(f"⚠️ Backend not reachable or invalid response: {e}")
