import os
import random
import requests
import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ============================================================
# 🌐 Backend Configuration
# ============================================================
BACKEND = os.getenv("HEALER_BACKEND_URL", "http://127.0.0.1:8000")

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
# 🔍 Locate Paywalls.ai Revenue Log
# ============================================================
def find_revenue_log():
    possible_paths = [
        "../data/healing_revenue.log",
        "data/healing_revenue.log",
        "./data/healing_revenue.log",
    ]
    for path in possible_paths:
        if os.path.exists(path):
            st.sidebar.success(f"✅ Found Paywalls.ai log: {path}")
            return path
    st.sidebar.warning("⚠️ No Paywalls.ai log found.")
    return None

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

    # Health check
    if st.button("🔎 Test Backend"):
        try:
            health = requests.get(f"{BACKEND}/health", timeout=5).json()
            st.success(f"✅ Backend OK — Mode: {health.get('mode')} | Paywalls: {health.get('paywalls_ready')}")
        except Exception as e:
            st.error(f"❌ Backend not reachable: {e}")

    # Simulation start/stop
    if st.button("🚀 Start Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/start", timeout=5)
            st.success("✅ Healing simulation started!") if res.status_code == 200 else st.warning("⚠️ Could not start simulation.")
        except Exception as e:
            st.error(f"❌ Error starting: {e}")

    if st.button("🧊 Stop Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/stop", timeout=5)
            st.warning("🛑 Simulation stopped.") if res.status_code == 200 else st.warning("⚠️ Could not stop simulation.")
        except Exception as e:
            st.error(f"❌ Error stopping: {e}")

    st.divider()

    # Manual healing trigger
    st.markdown("### ⚡ Trigger Manual Healing")
    selected_event = st.selectbox("Select anomaly:", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])
    if st.button("💥 Trigger Healing"):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={selected_event}", timeout=7)
            if res.status_code == 200:
                rj = res.json()
                st.success(f"✅ {rj['workflow']} healed | Recovery: {rj['recovery_pct']}% | Billed via Paywalls.ai")
            else:
                st.warning("⚠️ Healing trigger failed.")
        except Exception as e:
            st.error(f"❌ Failed to trigger: {e}")

    st.divider()

    # 🔁 FlowXO Webhook trigger and display recent logs
    st.markdown("### 🔁 FlowXO Integration")
    wf = st.selectbox("Workflow:", ["invoice_processing", "order_processing", "customer_support"])
    anomaly = st.selectbox("Anomaly:", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])

    if st.button("🚨 Send FlowXO Webhook"):
        try:
            payload = {"workflow_id": wf, "anomaly": anomaly, "user_id": "demo_client"}
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            if res.status_code == 200:
                st.success("✅ FlowXO event processed and logged!")
                st.json(res.json())
            else:
                st.warning(f"⚠️ Webhook failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ FlowXO webhook error: {e}")

    # Display recent FlowXO events directly in sidebar
    st.markdown("#### 🗂️ Recent FlowXO Events")
    flow_log = "data/flowxo_events.log"
    if os.path.exists(flow_log):
        with open(flow_log, "r", encoding="utf-8") as f:
            lines = f.readlines()[-10:]
        if lines:
            for line in reversed(lines):
                st.caption(line.strip())
        else:
            st.info("📭 No FlowXO events yet.")
   
# ============================================================
# 🔁 Auto Refresh
# ============================================================
st_autorefresh(interval=5000, key="refresh")

# ============================================================
# 📊 Metrics & Monetization Dashboard
# ============================================================
try:
    metrics = requests.get(f"{BACKEND}/metrics/summary", timeout=7).json()
    logs = requests.get(f"{BACKEND}/healing/logs?n=60", timeout=7).json().get("logs", [])

    # ========================================================
    # 💡 Top KPIs
    # ========================================================
    st.markdown("### ⚡ Healing Performance Metrics")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🩺 Total Healings", metrics.get("healings", 0))
    k2.metric("⚡ Avg Recovery %", f"{metrics.get('avg_recovery_pct', 0):.2f}")
    k3.metric("🎯 Avg Reward", f"{metrics.get('avg_reward', 0):.2f}")
    k4.metric("📈 Revenue ($)", f"{metrics.get('healings', 0) * 0.05:.2f}")

    # ========================================================
    # 💰 Paywalls.ai Monetization
    # ========================================================
    st.divider()
    st.markdown("### 💰 Prototype → Profit (Paywalls.ai Monetization)")

    log_path = find_revenue_log()
    total_rev, total_heals = 0.0, 0
    parsed = []

    if log_path and os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines[-100:]:
            parts = line.strip().split("|")
            if len(parts) >= 4:
                ts, workflow, anomaly, cost, *_ = [p.strip() for p in parts]
                try:
                    cost_val = float(cost.replace("$", "").strip())
                except:
                    cost_val = 0.0
                total_rev += cost_val
                total_heals += 1
                parsed.append({
                    "Timestamp": ts,
                    "Workflow": workflow,
                    "Anomaly": anomaly,
                    "Cost ($)": cost_val
                })

    if parsed:
        df_rev = pd.DataFrame(parsed)
        df_rev["Timestamp"] = pd.to_datetime(df_rev["Timestamp"], errors="coerce")
        df_rev["Cumulative Revenue ($)"] = df_rev["Cost ($)"].cumsum()

        c1, c2, c3 = st.columns(3)
        c1.metric("💸 Total Revenue", f"${total_rev:.2f}")
        c2.metric("🩹 Total Heals", total_heals)
        c3.metric("📊 Avg $/Heal", f"${(total_rev/total_heals):.2f}" if total_heals else "$0.00")

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

        st.markdown("#### 💵 Detailed Revenue Table (No Status Column)")
        st.dataframe(
            df_rev.sort_values(by="Timestamp", ascending=False)
            .style.format({"Cost ($)": "${:.4f}", "Cumulative Revenue ($)": "${:.4f}"}),
            use_container_width=True
        )
    else:
        st.warning("📭 No Paywalls.ai log found yet — start the simulator or trigger healing.")

    # ========================================================
    # 🩹 Healing Logs
    # ========================================================
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
