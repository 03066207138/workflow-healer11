# ============================================================
# 💰 Prototype-to-Profit: Workflow Healer (Streamlit Dashboard)
# IBM × Paywalls.ai × FlowXO — AI-Powered Workflow Healing
# v4.5 — Polished UI • Real-Time Integration • Single-Click Demo Ready
# ============================================================

import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ============================================================
# 🌐 Backend Configuration
# ============================================================
BACKEND = os.getenv("HEALER_BACKEND_URL", "https://workflow-healer11-2.onrender.com").rstrip("/")

st.set_page_config(
    page_title="💰 Prototype to Profit – Workflow Healer",
    layout="wide",
    page_icon="💎",
)

# ============================================================
# 🎨 Elegant Theme (Dark Gradient + Glass Cards)
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
  --yellow: #facc15;
}
body, .stApp {
  background: radial-gradient(circle at top left, var(--bg-1), var(--bg-2));
  color: var(--fg);
  font-family: "Inter", system-ui, sans-serif;
}
h1, h2, h3, h4 { color: var(--accent) !important; text-align:center; }
.metric {
  text-align:center; 
  padding:10px; 
  border-radius:12px; 
  margin:6px; 
  box-shadow: 0 0 10px rgba(96,165,250,0.1);
}
.success { background:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.3); }
.warning { background:rgba(250,204,21,0.1); border:1px solid rgba(250,204,21,0.3); }
.info    { background:rgba(96,165,250,0.1); border:1px solid rgba(96,165,250,0.3); }
.error   { background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); }
[data-testid="stMetricValue"] { color: var(--accent); font-weight:700; }
section.main { padding: 1rem 2rem !important; }
.stDownloadButton button { width: 100%; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🧩 Utility Helpers
# ============================================================
def toast(kind: str, msg: str):
    {"success": st.success, "warning": st.warning, "error": st.error}.get(kind, st.info)(msg)

def safe_json_get(url, timeout=8, default=None):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        toast("warning", f"GET {url} → {r.status_code}")
    except Exception as e:
        toast("error", f"GET {url} failed: {e}")
    return default

def safe_bytes_get(url, timeout=8):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.content
    except Exception as e:
        toast("error", f"GET {url} failed: {e}")
    return None

@st.cache_data(ttl=8)
def cached_health():
    return safe_json_get(f"{BACKEND}/health", default={"status":"offline","mode":"Offline Simulation"})

# ============================================================
# 🧠 Header & System Mode
# ============================================================
st.markdown(f"""
<h1>💎 Prototype-to-Profit: AI Workflow Healer</h1>
<p style="text-align:center; color:#a1a1aa;">
Seamlessly Heal Workflows, Automate Recovery, and Monetize AI Actions.<br>
Powered by <b>IBM watsonx.ai</b>, <b>Paywalls.ai</b>, and <b>FlowXO</b>.
</p>
""", unsafe_allow_html=True)

health = cached_health()
mode = str(health.get("mode", "Offline Simulation"))
if "offline" in mode.lower():
    st.warning("🧩 Running in Offline Simulation Mode — Real-Time APIs disabled.")
elif "Watsonx" in mode:
    st.success("🤖 Connected to IBM Watsonx.ai — Live Healing Enabled.")
elif "Groq" in mode:
    st.info("⚡ Local AI Mode via Groq — Fast Offline Testing.")
else:
    st.info(f"System Mode: {mode}")

st.caption(f"🌐 Backend: {BACKEND}")

# ============================================================
# 🔁 Auto Refresh (6 seconds)
# ============================================================
st_autorefresh(interval=6000, key="auto_refresh")

# ============================================================
# ⚙️ Sidebar — Simulation & Webhook Controls
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Controls Panel")

    if st.button("🔎 Test Backend"):
        h = cached_health()
        if h and h.get("status") == "ok":
            st.success(f"✅ Connected — Mode: {h.get('mode')} | Paywalls: {h.get('paywalls_ready')}")
            st.json(h)
        else:
            st.error("❌ Backend unreachable")

    st.divider()
    st.markdown("### 🔁 Simulation Control")
    if st.button("🚀 Start Simulation"):
        try:
            r = requests.post(f"{BACKEND}/sim/start", timeout=6)
            toast("success" if r.status_code == 200 else "warning",
                  "Simulation started!" if r.status_code == 200 else f"Failed ({r.status_code})")
        except Exception as e:
            toast("error", str(e))

    if st.button("🧊 Stop Simulation"):
        try:
            r = requests.post(f"{BACKEND}/sim/stop", timeout=6)
            toast("warning" if r.status_code == 200 else "error", "Simulation stopped.")
        except Exception as e:
            toast("error", str(e))

    st.divider()
    st.markdown("### ⚡ Trigger Healing")
    anomaly = st.selectbox("Choose Anomaly", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("💥 Run Healing Cycle"):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={anomaly}", timeout=7)
            if res.status_code == 200:
                j = res.json()
                toast("success", f"✅ {j['workflow']} healed — Recovery {j['recovery_pct']}% — Billed via Paywalls.ai")
                st.json(j)
            else:
                toast("warning", f"Healing trigger failed ({res.status_code})")
        except Exception as e:
            toast("error", str(e))

    st.divider()
    st.markdown("### 🌐 FlowXO Webhook Trigger")
    wf = st.selectbox("Workflow", ["invoice_processing", "order_processing", "customer_support"])
    a = st.selectbox("Anomaly Type", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("🚨 Send Quick Webhook"):
        payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
        try:
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            toast("success" if res.status_code == 200 else "warning", "Webhook processed!" if res.status_code == 200 else "Failed")
            if res.status_code == 200: st.json(res.json())
        except Exception as e:
            toast("error", f"Webhook error: {e}")

# ============================================================
# 📊 Data Fetch
# ============================================================
metrics = safe_json_get(f"{BACKEND}/metrics/summary", default={}) or {}
revenue = safe_json_get(f"{BACKEND}/metrics/revenue", default={}) or {}
logs = (safe_json_get(f"{BACKEND}/healing/logs?n=80", default={"logs":[]}) or {"logs":[]})["logs"]

# ============================================================
# 🧮 KPI Metrics
# ============================================================
st.markdown("### ⚡ Healing & Monetization Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🩺 Total Healings", f"{float(metrics.get('healings', 0)):.0f}")
c2.metric("⚙️ Avg Recovery %", f"{float(metrics.get('avg_recovery_pct', 0)):.2f}")
c3.metric("🎯 Avg Reward", f"{float(metrics.get('avg_reward', 0)):.2f}")
c4.metric("💰 Total Revenue ($)", f"{float(revenue.get('total_revenue', 0)):.2f}")

st.divider()

# ============================================================
# 📊 Charts & Logs
# ============================================================
st.markdown("### 📈 Anomaly Distribution")
mix = metrics.get("anomaly_mix", {}) or {}
if mix:
    df = pd.DataFrame(list(mix.items()), columns=["Anomaly", "Count"])
    st.bar_chart(df.set_index("Anomaly"))
else:
    st.info("📭 No anomaly data yet. Trigger healings to populate charts.")

# ============================================================
# 💹 Revenue Logs
# ============================================================
st.markdown("## 💹 Monetization History")
rev = revenue.get("logs", [])
if rev:
    df_rev = pd.DataFrame(rev)
    st.dataframe(df_rev, use_container_width=True)
else:
    st.info("📭 No revenue records yet.")

# ============================================================
# 🩺 Healing Activity Log
# ============================================================
st.markdown("## 🩺 Healing Activity Feed")
if logs:
    for line in logs[:50]:
        style, icon = "info", "💡"
        if "⚠️" in line: style, icon = "warning", "🟡"
        elif "✅" in line: style, icon = "success", "🟢"
        elif "❌" in line: style, icon = "error", "🔴"
        st.markdown(f"<div class='metric {style}'>{icon} {line}</div>", unsafe_allow_html=True)
else:
    st.info("📭 No healing logs yet — start simulation to see events.")

# ============================================================
# 📥 Downloads Section
# ============================================================
st.divider()
st.markdown("### 📂 Download Logs & Reports")

col1, col2, col3 = st.columns(3)
with col1:
    st.download_button(
        "📜 Healing Log",
        data="\n".join(logs).encode("utf-8"),
        file_name="healing_log.txt",
        mime="text/plain"
    )
with col2:
    csv = safe_bytes_get(f"{BACKEND}/metrics/download")
    st.download_button(
        "📊 Metrics CSV",
        data=csv or b"",
        file_name="metrics_log.csv",
        mime="text/csv",
        disabled=(csv is None)
    )
with col3:
    rev_str = "\n".join(f"{r['Timestamp']} | {r['User']} | {r['Healing Type']} | ${r['Cost ($)']}" for r in rev) if rev else "No revenue yet."
    st.download_button(
        "💰 Revenue Log",
        data=rev_str.encode("utf-8"),
        file_name="healing_revenue.txt",
        mime="text/plain"
    )

# ============================================================
# 🧾 Active Healing Slip
# ============================================================
st.markdown("### 🧾 Active Healing Slip")
active = [l for l in logs if "⚠️" in l or "anomaly" in l.lower()]
if active:
    slip = "\n".join(active[-20:])
    st.text_area("Current Healings", slip, height=180)
    st.download_button(
        "🧾 Download Healing Slip",
        data=slip.encode("utf-8"),
        file_name=f"healing_slip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
else:
    st.success("✅ All workflows stable — no active anomalies.")

st.caption(f"⏱️ Auto-refresh every 6s — Last updated: {datetime.now().strftime('%H:%M:%S')}")
