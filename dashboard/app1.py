# ============================================================
# 💰 Prototype-to-Profit: Workflow Healer (Streamlit Dashboard)
# IBM × Paywalls.ai × FlowXO — AI-Powered Workflow Healing
# v4.8 — Sidebar Restored • Stable Refresh • Clean Layout
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
    initial_sidebar_state="expanded"  # 👈 ensures sidebar is visible
)

# ============================================================
# 🎨 Theme Styling
# ============================================================
st.markdown("""
<style>
:root {
  --bg-1:#0f172a; --bg-2:#1e293b; --fg:#f8fafc; --accent:#60a5fa;
  --green:#34d399; --red:#f87171; --yellow:#fde047;
}
body,.stApp{background:radial-gradient(circle at top left,var(--bg-1),var(--bg-2));
color:var(--fg);font-family:"Inter",system-ui,sans-serif;}
section[data-testid="stSidebar"]{background:#0f172a!important;color:var(--fg)!important;
border-right:1px solid rgba(255,255,255,.08);}
section[data-testid="stSidebar"] *{color:var(--fg)!important;}
.stButton button{background:linear-gradient(135deg,#2563eb,#1d4ed8);
color:#fff!important;border:none;border-radius:10px;padding:.55rem 1.1rem;
font-weight:600;transition:.3s;box-shadow:0 0 10px rgba(96,165,250,.25);}
.stButton button:hover{transform:translateY(-1px);
box-shadow:0 0 14px rgba(96,165,250,.5);}
.metric{padding:10px;border-radius:12px;margin:6px;
box-shadow:0 0 12px rgba(96,165,250,.15);}
.success{background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.4);}
.warning{background:rgba(250,204,21,.12);border:1px solid rgba(250,204,21,.4);}
.info{background:rgba(96,165,250,.12);border:1px solid rgba(96,165,250,.4);}
.error{background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.4);}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🔧 Helpers
# ============================================================
def toast(kind: str, msg: str):
    {"success": st.success, "warning": st.warning, "error": st.error}.get(kind, st.info)(msg)

def safe_json_get(url, timeout=8, default=None):
    try:
        r = requests.get(url, timeout=timeout)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.warning(f"⚠️ Failed {url}: {e}")
    return default

@st.cache_data(ttl=8)
def cached_health():
    return safe_json_get(f"{BACKEND}/health", default={"status":"offline","mode":"Offline Simulation"})

# ============================================================
# 🧭 Sidebar Controls — Always Visible
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Controls Panel")

    # Backend check
    if st.button("🔎 Check Backend"):
        h = cached_health()
        if h and h.get("status") == "ok":
            st.success(f"✅ Connected — Mode: {h.get('mode')}")
            st.json(h)
        else:
            st.error("❌ Backend not reachable")

    st.divider()
    st.markdown("### 🔁 Simulation Control")
    if st.button("🚀 Start Simulation"):
        try:
            requests.post(f"{BACKEND}/sim/start", timeout=6)
            toast("success", "Simulation started!")
        except Exception as e:
            toast("error", str(e))

    if st.button("🧊 Stop Simulation"):
        try:
            requests.post(f"{BACKEND}/sim/stop", timeout=6)
            toast("warning", "Simulation stopped.")
        except Exception as e:
            toast("error", str(e))

    st.divider()
    st.markdown("### ⚡ Trigger Manual Healing")
    anomaly = st.selectbox("Select anomaly", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("💥 Run Healing Cycle"):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={anomaly}", timeout=7)
            if res.status_code == 200:
                j = res.json()
                toast("success", f"✅ {j.get('workflow')} healed — {j.get('recovery_pct')}% recovery")
                st.json(j)
            else:
                toast("warning", f"Failed ({res.status_code})")
        except Exception as e:
            toast("error", str(e))

    st.divider()
    st.markdown("### 🌐 FlowXO Webhook")
    wf = st.selectbox("Workflow", ["invoice_processing","order_processing","customer_support"])
    a = st.selectbox("Anomaly", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("🚨 Send Webhook"):
        payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
        try:
            r = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            if r.status_code == 200:
                toast("success", "Webhook processed successfully!")
                st.json(r.json())
            else:
                toast("warning", f"Webhook failed ({r.status_code})")
        except Exception as e:
            toast("error", f"Webhook error: {e}")

# ============================================================
# 🧠 Header + Integration Status
# ============================================================
st.markdown("""
<h1>💎 Prototype-to-Profit: AI Workflow Healer</h1>
<p style="text-align:center;color:#cbd5e1;">Heal, Automate, and Monetize Workflows — powered by
<b>Paywalls.ai</b> & <b>FlowXO</b>.</p>
""", unsafe_allow_html=True)

health = cached_health()
mode = str(health.get("mode", "Offline Simulation"))

if "offline" in mode.lower():
    st.warning("🧩 Offline Simulation Mode — APIs inactive.")
elif "Watsonx" in mode:
    st.success("🤖 Connected to IBM Watsonx.ai — Live Healing Active.")
elif "Groq" in mode:
    st.info("⚡ Local AI Mode via Groq — Fast Testing.")
else:
    st.info(f"⚙️ Mode: {mode}")

paywalls_ready = health.get("paywalls_ready", False)
flowxo_ready = health.get("flowxo_ready", False)
groq_ready = health.get("groq_ready", False)

st.markdown("### 🔗 Integration Status")
c1, c2, c3 = st.columns(3)
c1.metric("⚡ Groq Local AI", "✅ Ready" if groq_ready else "❌ Inactive")
c2.metric("💰 Paywalls.ai", "✅ Connected" if paywalls_ready else "❌ Missing")
c3.metric("🌐 FlowXO", "✅ Active" if flowxo_ready else "❌ Inactive")

if paywalls_ready and flowxo_ready:
    st.success("🚀 Full monetization and automation loop active!")
elif paywalls_ready:
    st.warning("💰 Paywalls.ai ready — waiting for FlowXO webhook.")
elif flowxo_ready:
    st.warning("🌐 FlowXO active — waiting for Paywalls.ai link.")
else:
    st.error("⚠️ Both integrations inactive. Check backend or keys.")

st.caption(f"🌐 Backend Endpoint: `{BACKEND}`")

# ============================================================
# 🩺 Metrics and KPIs
# ============================================================
metrics = safe_json_get(f"{BACKEND}/metrics/summary", default={}) or {}
revenue_payload = safe_json_get(f"{BACKEND}/metrics/revenue", default={}) or {}
logs_resp = safe_json_get(f"{BACKEND}/healing/logs?n=80", default={"logs":[]}) or {"logs":[]}
logs = logs_resp.get("logs", [])

total_revenue = float(revenue_payload.get("total_revenue", 0))
st.divider()
st.markdown("### ⚡ Healing & Monetization KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🩺 Healings", f"{float(metrics.get('healings',0)):.0f}")
c2.metric("⚙️ Recovery %", f"{float(metrics.get('avg_recovery_pct',0)):.2f}")
c3.metric("🎯 Reward", f"{float(metrics.get('avg_reward',0)):.2f}")
c4.metric("💰 Revenue ($)", f"{total_revenue:.2f}")

# ============================================================
# 🩺 Logs Display
# ============================================================
st.markdown("## 🩺 Healing Logs")
if logs:
    for line in logs[:50]:
        style, icon = "info", "💡"
        if "⚠️" in line: style, icon = "warning", "🟡"
        elif "✅" in line: style, icon = "success", "🟢"
        elif "❌" in line: style, icon = "error", "🔴"
        st.markdown(f"<div class='metric {style}'>{icon} {line}</div>", unsafe_allow_html=True)
else:
    st.info("📭 No healing logs yet — run a simulation to see updates.")

st.caption(f"⏱️ Auto-refresh every 10s — Last updated: {datetime.now().strftime('%H:%M:%S')}")
st_autorefresh(interval=10000, key="refresh")
