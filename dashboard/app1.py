# ============================================================
# 💰 Prototype-to-Profit: Workflow Healer (Streamlit Dashboard)
# AI-Powered Workflow Healing — Paywalls.ai × FlowXO Edition
# v4.4 — cache health; safe fetch; tidy downloads; single-call UX
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
body, .stApp {
  background: radial-gradient(circle at top left, var(--bg-1), var(--bg-2));
  color: var(--fg);
  font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, sans-serif;
}
h1,h2,h3,h4 { color: var(--accent) !important; text-align:center; }
.metric { text-align:center; padding:10px; border-radius:12px; margin:4px; }
.success { background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.3); }
.warning { background:rgba(250,204,21,0.08); border:1px solid rgba(250,204,21,0.3); }
.info    { background:rgba(59,130,246,0.08); border:1px solid rgba(59,130,246,0.3); }
.error   { background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); }
[data-testid="stMetricValue"] { color: var(--accent); font-weight: 700; }
section.main { padding: 1.2rem 2rem !important; }
.stDownloadButton button {
  width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔧 Helpers (global so they are available everywhere)
# ============================================================
def toast(kind: str, msg: str):
    if kind == "success": st.success(msg)
    elif kind == "warning": st.warning(msg)
    elif kind == "error": st.error(msg)
    else: st.info(msg)

def safe_json_get(url: str, timeout: int = 7, default=None):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
        toast("warning", f"GET {url} → {r.status_code}")
    except Exception as e:
        toast("error", f"GET {url} failed: {e}")
    return default

def safe_bytes_get(url: str, timeout: int = 7):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.content
        toast("warning", f"GET {url} → {r.status_code}")
    except Exception as e:
        toast("error", f"GET {url} failed: {e}")
    return None

@st.cache_data(ttl=8)
def cached_health():
    data = safe_json_get(f"{BACKEND}/health", default={"status": "offline", "mode": "Offline Simulation"})
    return data or {"status": "offline", "mode": "Offline Simulation"}

# ============================================================
# 🧠 Header
# ============================================================
st.markdown(f"""
<h1>💰 Prototype-to-Profit: AI Workflow Healer</h1>
<p style="text-align:center; color:#94a3b8;">
AI-Powered Workflow Healing using <b>Paywalls.ai</b> × <b>FlowXO</b><br>
Backend: <code>{BACKEND}</code>
</p>
""", unsafe_allow_html=True)

health = cached_health()
if str(health.get("mode","")).lower().startswith("offline"):
    st.warning("🧩 Running in **Offline Simulation Mode** (no webhook detected).")
elif "Watsonx" in str(health.get("mode","")):
    st.success("🤖 Connected to IBM watsonx.ai — Real-Time Healing Active.")
elif "Groq" in str(health.get("mode","")):
    st.info("⚡ Running on Groq Local AI Mode.")
else:
    st.info(f"Mode: {health.get('mode','N/A')}")

# ============================================================
# 🔁 Auto Refresh
# ============================================================
st_autorefresh(interval=6000, key="refresh")

# ============================================================
# ⚙️ Sidebar Controls
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Simulation & Webhook Controls")

    # ---- Health Check ----
    if st.button("🔎 Test Backend"):
        h = cached_health()
        if h and h.get("status") == "ok":
            st.success(
                f"✅ Backend OK — Mode: {h.get('mode', 'N/A')} | "
                f"Paywalls: {h.get('paywalls_ready', 'N/A')}"
            )
            st.json(h)
        else:
            st.error("❌ Backend not reachable")

    st.divider()
    st.markdown("### 🔁 Simulation Controls")

    if st.button("🚀 Start Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/start", timeout=7)
            toast("success" if res.status_code == 200 else "warning",
                  "✅ Healing simulation started!" if res.status_code == 200 else f"⚠️ Could not start ({res.status_code})")
        except Exception as e:
            toast("error", f"Failed to start: {e}")

    if st.button("🧊 Stop Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/stop", timeout=7)
            toast("warning" if res.status_code == 200 else "warning",
                  "🛑 Simulation stopped." if res.status_code == 200 else f"⚠️ Stop failed ({res.status_code})")
        except Exception as e:
            toast("error", f"Failed to stop: {e}")

    st.divider()
    st.markdown("### ⚡ Trigger Manual Healing")
    selected_event = st.selectbox("Select anomaly:", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])

    if st.button("💥 Trigger Healing"):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={selected_event}", timeout=7)
            if res.status_code == 200:
                rj = res.json()
                toast("success",
                      f"✅ {rj.get('workflow','N/A')} healed | Recovery: {rj.get('recovery_pct',0)}% | Billed via Paywalls.ai")
                st.json(rj)
            else:
                toast("warning", f"Healing trigger failed ({res.status_code})")
        except Exception as e:
            toast("error", f"Failed to trigger: {e}")

    st.divider()
    st.markdown("### 🌐 FlowXO Webhook (Manual / JSON)")

    wf = st.selectbox("Workflow", ["invoice_processing", "order_processing", "customer_support"])
    anomaly = st.selectbox("Anomaly Type", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])

    if st.button("🚨 Send Webhook (Quick Mode)"):
        try:
            payload = {"workflow_id": wf, "anomaly": anomaly, "user_id": "demo_client"}
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            if res.status_code == 200:
                toast("success", "FlowXO event processed successfully!")
                st.json(res.json())
            else:
                toast("warning", f"Webhook failed ({res.status_code})")
        except Exception as e:
            toast("error", f"FlowXO webhook error: {e}")

    st.markdown("#### 🧩 Custom JSON Payload")
    example_json = {
        "workflow_id": "invoice_processing",
        "anomaly": "queue_pressure",
        "user_id": "demo_client"
    }

    json_input = st.text_area(
        "Edit or paste your JSON payload:",
        value=json.dumps(example_json, indent=4),
        height=160
    )

    if st.button("📤 Send JSON Webhook"):
        try:
            payload = json.loads(json_input)
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            if res.status_code == 200:
                toast("success", "Custom JSON webhook sent successfully!")
                st.json(res.json())
            else:
                toast("warning", f"Failed ({res.status_code})")
        except json.JSONDecodeError:
            toast("error", "Invalid JSON format. Please check your input.")
        except Exception as e:
            toast("error", f"Webhook error: {e}")

# ============================================================
# 📊 Unified Metrics & Logs
# ============================================================
metrics = safe_json_get(f"{BACKEND}/metrics/summary", default={}) or {}
revenue_data = safe_json_get(f"{BACKEND}/metrics/revenue", default={}) or {}
logs_data = safe_json_get(f"{BACKEND}/healing/logs?n=60", default={"logs": []}) or {"logs": []}
logs = logs_data.get("logs", [])

total_heals = float(metrics.get("healings", 0) or 0)
avg_recovery = float(metrics.get("avg_recovery_pct", 0) or 0)
avg_reward = float(metrics.get("avg_reward", 0) or 0)
total_revenue = float(revenue_data.get("total_revenue", 0.0) or 0)

st.markdown("### ⚡ Healing & Monetization KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🩺 Total Healings", f"{total_heals:.0f}")
c2.metric("⚙️ Avg Recovery %", f"{avg_recovery:.2f}")
c3.metric("🎯 Avg Reward", f"{avg_reward:.2f}")
c4.metric("💰 Total Revenue ($)", f"{total_revenue:.2f}")

st.divider()

# ============================================================
# 📊 Anomaly Mix
# ============================================================
st.markdown("### ⚙️ Anomaly Distribution")
mix = metrics.get("anomaly_mix", {}) or {}
if mix:
    df_mix = pd.DataFrame(list(mix.items()), columns=["Anomaly", "Count"])
    st.bar_chart(df_mix.set_index("Anomaly"))
else:
    st.info("📭 No anomaly data yet — run a few healings first.")

# ============================================================
# 💹 Revenue & Healing Logs + Downloads
# ============================================================
st.markdown("## 💹 Monetization & Revenue Logs")
rev_logs = revenue_data.get("logs", []) or []
if rev_logs:
    st.dataframe(pd.DataFrame(rev_logs), use_container_width=True)
else:
    st.info("📭 No revenue logs yet.")

st.markdown("## 📜 Healing Activity Logs")
if logs:
    for line in logs[:40]:
        style, icon = "info", "💡"
        if "⚠️" in line: style, icon = "warning", "🟡"
        elif "✅" in line: style, icon = "success", "🟢"
        elif "❌" in line: style, icon = "error", "🔴"
        st.markdown(f"<div class='metric {style}'>{icon} {line}</div>", unsafe_allow_html=True)
else:
    st.info("📭 No healing logs yet — run the simulator to view events.")

st.divider()
st.markdown("### 📂 Download Logs / Generate Healing Slip")

col1, col2, col3 = st.columns(3)
with col1:
    st.download_button(
        "📥 Download Healing Log",
        data="\n".join(logs).encode("utf-8"),
        file_name="healing_log.txt",
        mime="text/plain"
    )
with col2:
    csv_bytes = safe_bytes_get(f"{BACKEND}/metrics/download", timeout=7)
    st.download_button(
        "📊 Download Metrics CSV",
        data=csv_bytes or b"",
        file_name="metrics_log.csv",
        mime="text/csv",
        disabled=(csv_bytes is None)
    )
with col3:
    # Render revenue log text (from API payload) for download
    rev_str = "No revenue data yet."
    if rev_logs:
        rev_str = "\n".join(
            f"{x.get('Timestamp','')} | {x.get('Workflow','')} | {x.get('Anomaly','')} | ${x.get('Cost ($)',0)}"
            for x in rev_logs
        )
    st.download_button(
        "💰 Download Revenue Log",
        data=rev_str.encode("utf-8"),
        file_name="healing_revenue.txt",
        mime="text/plain"
    )

st.markdown("### 🧾 Healing Slip (Active Healings)")
active_logs = [l for l in logs if "⚠️" in l or "anomaly detected" in l]
if active_logs:
    slip_text = "\n".join(active_logs[-20:])
    st.text_area("📋 Current Healing Slip", slip_text, height=200)
    st.download_button(
        "🧾 Download Healing Slip",
        data=slip_text.encode("utf-8"),
        file_name=f"healing_slip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
else:
    st.info("✅ No currently running healings detected.")

st.caption(f"⏱️ Auto-refresh every 6s — Last update: {datetime.now().strftime('%H:%M:%S')}")
