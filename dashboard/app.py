import os
import requests
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ============================================================
# 🌐 Backend Configuration (Render Backend)
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
h1,h2,h3,h4 { color: var(--accent) !important; }
.metric { text-align:center; padding:10px; border-radius:12px; margin:4px; }
.success { background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.3);}
.warning { background:rgba(250,204,21,0.08); border:1px solid rgba(250,204,21,0.3);}
.info    { background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.3);}
.error   { background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3);}
[data-testid="stMetricValue"] { color: var(--accent); font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🧠 Header
# ============================================================
st.markdown("""
<h1 style="text-align:center;">💰 Prototype-to-Profit: AI Workflow Healer</h1>
<p style="text-align:center; color:#94a3b8;">
Monetized AI Automation powered by <b>Paywalls.ai</b> × <b>FlowXO</b>
</p>
""", unsafe_allow_html=True)

# ============================================================
# ⚙️ Sidebar Controls
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Simulation Controls")

    def safe_json_get(url, timeout=5):
        """Safely get JSON response or None"""
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
            if res.status_code == 200:
                st.success("✅ Healing simulation started!")
            else:
                st.warning(f"⚠️ Could not start simulation: {res.status_code}")
        except Exception as e:
            st.error(f"❌ Error starting: {e}")

    if st.button("🧊 Stop Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/stop", timeout=5)
            if res.status_code == 200:
                st.warning("🛑 Simulation stopped.")
            else:
                st.warning(f"⚠️ Could not stop simulation ({res.status_code})")
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
            if res.status_code == 200:
                st.success("✅ FlowXO event processed!")
                st.json(res.json())
            else:
                st.warning(f"⚠️ Webhook failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ FlowXO webhook error: {e}")

# ============================================================
# 🔁 Auto Refresh
# ============================================================
st_autorefresh(interval=5000, key="refresh")

# ============================================================
# 📊 Unified Metrics & Monetization Dashboard
# ============================================================
try:
    metrics = requests.get(f"{BACKEND}/metrics/summary", timeout=7).json()
    rev_resp = requests.get(f"{BACKEND}/metrics/revenue", timeout=7)
    revenue_data = rev_resp.json() if rev_resp.status_code == 200 else {}
    logs_resp = requests.get(f"{BACKEND}/healing/logs?n=60", timeout=7)
    logs = logs_resp.json().get("logs", []) if logs_resp.status_code == 200 else []

    st.markdown("### ⚡ Healing Performance Metrics")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🩺 Total Healings", metrics.get("healings", 0))
    k2.metric("⚡ Avg Recovery %", f"{metrics.get('avg_recovery_pct', 0):.2f}")
    k3.metric("🎯 Avg Reward", f"{metrics.get('avg_reward', 0):.2f}")
    k4.metric("📈 Revenue ($)", f"{revenue_data.get('total_revenue', 0.0):.2f}")

    st.divider()
    st.markdown("### 💰 Prototype → Profit (Paywalls.ai Monetization)")

    parsed = revenue_data.get("logs", [])
    if parsed:
        df_rev = pd.DataFrame(parsed)
        df_rev["Timestamp"] = pd.to_datetime(df_rev["Timestamp"], errors="coerce")
        df_rev["Cumulative Revenue ($)"] = df_rev["Cost ($)"].cumsum()

        c1, c2, c3 = st.columns(3)
        c1.metric("💸 Total Revenue", f"${revenue_data.get('total_revenue', 0.0):.2f}")
        c2.metric("🩹 Total Heals", revenue_data.get("total_heals", 0))
        avg_per_heal = revenue_data.get("total_revenue", 0.0) / max(1, revenue_data.get("total_heals", 1))
        c3.metric("📊 Avg $/Heal", f"${avg_per_heal:.2f}")

        chart = alt.Chart(df_rev).mark_area(
            line={"color": "#34d399"},
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="#34d399", offset=0),
                       alt.GradientStop(color="#0f172a", offset=1)],
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X("Timestamp:T", title=None),
            y=alt.Y("Cumulative Revenue ($):Q", title="Cumulative Revenue ($)"),
            tooltip=["Timestamp", "Workflow", "Anomaly", "Cost ($)", "Cumulative Revenue ($)"]
        ).properties(height=250)

        st.altair_chart(chart, use_container_width=True)
        st.dataframe(df_rev.sort_values(by="Timestamp", ascending=False), use_container_width=True)
    else:
        st.warning("📭 No revenue logs found — start simulation or trigger healing.")

    st.divider()
    st.markdown("### 🩹 Real-Time Healing Queue")

    if logs:
        for line in logs[:40]:
            if "⚠️" in line:
                st.markdown(f"<div class='metric warning'>🟡 {line}</div>", unsafe_allow_html=True)
            elif "✅" in line:
                st.markdown(f"<div class='metric success'>🟢 {line}</div>", unsafe_allow_html=True)
            elif "❌" in line:
                st.markdown(f"<div class='metric error'>🔴 {line}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='metric info'>💡 {line}</div>", unsafe_allow_html=True)
    else:
        st.info("📭 No healing logs yet — run the simulator to view events.")

    st.caption(f"⏱️ Auto-refresh every 5s — Last update: {datetime.now().strftime('%H:%M:%S')}")

except Exception as e:
    st.error(f"⚠️ Backend not reachable or invalid response: {e}")
