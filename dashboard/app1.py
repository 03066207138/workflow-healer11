# ============================================================
# 💰 Prototype-to-Profit: Workflow Healer (Streamlit Dashboard)
# IBM × Paywalls.ai × FlowXO — AI-Powered Workflow Healing
# v4.8 — Dark Optimized • Stable Sidebar • Alerts + Slip Download
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
    initial_sidebar_state="expanded"  # 👈 ensures sidebar stays visible
)

# ============================================================
# 🎨 Complete Dark Theme Styling
# ============================================================
st.markdown("""
<style>
:root {
  --bg-1: #0f172a;
  --bg-2: #1e293b;
  --fg: #f8fafc;
  --accent: #60a5fa;
  --green: #34d399;
  --red: #f87171;
  --yellow: #fde047;
}
body, .stApp {
  background: radial-gradient(circle at top left, var(--bg-1), var(--bg-2));
  color: var(--fg);
  font-family: "Inter", system-ui, sans-serif;
}
/* Headings & general text */
h1, h2, h3, h4, h5, h6, p, label, span, div { color: var(--fg) !important; }
/* Sidebar */
section[data-testid="stSidebar"] {
  background:#0f172a !important;
  color:var(--fg)!important;
  border-right:1px solid rgba(255,255,255,.08);
}
section[data-testid="stSidebar"] * { color:var(--fg)!important; }
/* Buttons (labels forced white) */
.stButton button {
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color:#ffffff !important;
  text-shadow:0 0 2px rgba(0,0,0,.4);
  border:none; border-radius:10px;
  padding:.55rem 1.1rem;
  font-weight:600; font-size:.95rem;
  transition:all .3s ease;
  box-shadow:0 0 10px rgba(96,165,250,.25);
}
.stButton button:hover {
  background: linear-gradient(135deg,#1d4ed8,#2563eb);
  box-shadow:0 0 14px rgba(96,165,250,.5);
  transform:translateY(-1px);
}
/* Selects */
div[data-baseweb="select"] > div {
  background-color:#1e293b !important;
  color:var(--fg)!important;
  border:1px solid rgba(96,165,250,.35)!important;
  border-radius:8px;
}
div[data-baseweb="select"] svg { fill:var(--fg); }
/* Download buttons */
.stDownloadButton button{
  background: linear-gradient(135deg,#22c55e,#16a34a);
  color:#fff !important;
  border:none; border-radius:10px;
  padding:.5rem 1rem;
  font-weight:600; transition:.3s;
  box-shadow:0 0 8px rgba(52,211,153,.3);
}
.stDownloadButton button:hover{
  background:linear-gradient(135deg,#16a34a,#22c55e);
  transform:translateY(-1px);
  box-shadow:0 0 12px rgba(52,211,153,.5);
}
/* Inputs / Textareas */
textarea, input {
  background-color:#1e293b !important;
  color:var(--fg)!important;
  border:1px solid rgba(96,165,250,.35)!important;
  border-radius:8px!important;
}
/* ---------- TABLE VISIBILITY FIX ---------- */
.stDataFrame { background-color: #0f172a !important; }
.stDataFrame table { border-collapse: collapse !important; width: 100% !important; }
.stDataFrame th {
  background-color: #1e293b !important;
  color: #f8fafc !important;
  font-weight: 700 !important;
  border-bottom: 2px solid rgba(96,165,250,0.5) !important;
}
.stDataFrame td {
  color: #e2e8f0 !important;
  border-bottom: 1px solid rgba(255,255,255,0.08) !important;
}
.stDataFrame tr:nth-child(even) td {
  background-color: rgba(30,41,59,0.6) !important;
}
.stDataFrame tr:hover td {
  background-color: rgba(96,165,250,0.15) !important;
}
/* Metric chips */
.metric{
  text-align:center;
  padding:10px;
  border-radius:12px;
  margin:6px;
  box-shadow:0 0 12px rgba(96,165,250,.15);
}
.success{ background:rgba(52,211,153,.12); border:1px solid rgba(52,211,153,.4);}
.warning{ background:rgba(250,204,21,.12); border:1px solid rgba(250,204,21,.4);}
.info{ background:rgba(96,165,250,.12); border:1px solid rgba(96,165,250,.4);}
.error{ background:rgba(239,68,68,.12); border:1px solid rgba(239,68,68,.4);}
[data-testid="stMetricValue"]{ color:var(--accent); font-weight:700; }
/* JSON viewer */
[data-testid="stJson"] pre, .stJson, .stJson > div, .stJson pre code{
  background:#1e293b !important;
  color:#e2e8f0 !important;
  font-family:"JetBrains Mono",monospace;
  font-size:.85rem;
  line-height:1.4;
  border-radius:8px;
  border:1px solid rgba(96,165,250,.3);
  padding:10px;
}
.stJson span{ color:#93c5fd !important; }
.stJson span.string{ color:#86efac !important; }
.stJson span.number{ color:#facc15 !important; }
.stJson span.boolean{ color:#f87171 !important; }
.stAlert{ border-radius:10px; box-shadow:0 0 10px rgba(96,165,250,.25); }
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
# ⚙️ Sidebar Controls
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Controls Panel")

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
            r = requests.post(f"{BACKEND}/sim/start", timeout=6)
            toast("success" if r.status_code == 200 else "warning", "Simulation started!" if r.status_code == 200 else f"Failed ({r.status_code})")
        except Exception as e:
            toast("error", str(e))

    if st.button("🧊 Stop Simulation"):
        try:
            r = requests.post(f"{BACKEND}/sim/stop", timeout=6)
            toast("warning" if r.status_code == 200 else "error", "Simulation stopped.")
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
                toast("success", f"✅ {j.get('workflow','?')} healed — Recovery {j.get('recovery_pct',0)}% — Billed via Paywalls.ai")
                st.json(j)
            else:
                toast("warning", f"Healing trigger failed ({res.status_code})")
        except Exception as e:
            toast("error", str(e))

    st.divider()
    st.markdown("### 🌐 FlowXO Webhook")
    wf = st.selectbox("Workflow", ["invoice_processing","order_processing","customer_support"])
    a = st.selectbox("Anomaly Type", ["workflow_delay","queue_pressure","data_error","api_failure"])
    if st.button("🚨 Send Quick Webhook"):
        payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
        try:
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            toast("success" if res.status_code == 200 else "warning", "Webhook processed!" if res.status_code == 200 else f"Failed ({res.status_code})")
            if res.status_code == 200:
                st.json(res.json())
        except Exception as e:
            toast("error", f"Webhook error: {e}")

# ============================================================
# 🧠 Header & Backend Status
# ============================================================
st.markdown("""
<h1>💎 Prototype-to-Profit: AI Workflow Healer</h1>
<p style="text-align:center; color:#cbd5e1;">
Heal, Automate, and Monetize Workflows — Powered by <b>Paywalls.ai</b> & <b>FlowXO</b>.
</p>
""", unsafe_allow_html=True)

health = cached_health()
mode = str(health.get("mode", "Offline Simulation"))

if "offline" in mode.lower():
    st.warning("🧩 Running in **Offline Simulation Mode** — Real-Time APIs inactive.")
elif "Watsonx" in mode:
    st.success("🤖 Connected to **IBM Watsonx.ai** — Live Healing Active.")
elif "Groq" in mode:
    st.info("⚡ Local AI Mode via **Groq** — Fast Local Testing.")
else:
    st.info(f"⚙️ Mode: {mode}")

paywalls_ready = health.get("paywalls_ready", False)
flowxo_ready = health.get("flowxo_ready", False)
groq_ready = health.get("groq_ready", False)

st.markdown("### 🔗 Integration Status")
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Groq Local AI", "✅ Ready" if groq_ready else "❌ Not Found")
col2.metric("💰 Paywalls.ai", "✅ Connected" if paywalls_ready else "❌ Not Found")
col3.metric("🌐 FlowXO Webhook", "✅ Active" if flowxo_ready else "❌ Inactive")

if paywalls_ready and flowxo_ready:
    st.success("🚀 Full monetization and automation loop active — Paywalls.ai + FlowXO connected successfully!")
elif paywalls_ready:
    st.warning("💰 Paywalls.ai active — waiting for FlowXO live webhook connection.")
elif flowxo_ready:
    st.warning("🌐 FlowXO webhook active — waiting for Paywalls.ai integration.")
else:
    st.error("⚠️ Both FlowXO and Paywalls.ai are inactive. Check backend or API keys.")

st.caption(f"🌐 Backend Endpoint: `{BACKEND}`")

# ============================================================
# 🔁 Auto Refresh
# ============================================================
st_autorefresh(interval=10000, key="refresh")

# ============================================================
# 📊 Fetch Data
# ============================================================
metrics = safe_json_get(f"{BACKEND}/metrics/summary", default={}) or {}
revenue_payload = safe_json_get(f"{BACKEND}/metrics/revenue", default={}) or {}
logs_resp = safe_json_get(f"{BACKEND}/healing/logs?n=80", default={"logs":[]}) or {"logs":[]}
logs = logs_resp.get("logs", [])

# ---- Normalize revenue rows ----
def normalize_revenue_rows(rows):
    normalized = []
    for r in rows or []:
        ts = r.get("Timestamp") or r.get("ts") or ""
        user = r.get("User") or r.get("user") or r.get("Workflow") or "N/A"
        heal_type = r.get("Healing Type") or r.get("heal_type") or r.get("Anomaly") or r.get("anomaly") or "N/A"
        cost = r.get("Cost ($)") or r.get("amount") or r.get("cost") or 0
        if isinstance(cost, str):
            cost = cost.replace("$", "").strip()
            try:
                cost = float(cost)
            except:
                cost = 0.0
        normalized.append({"Timestamp": ts, "User": user, "Healing Type": heal_type, "Cost ($)": float(cost)})
    return pd.DataFrame(normalized)

rev_df = normalize_revenue_rows(revenue_payload.get("logs", []))
total_revenue = float(revenue_payload.get("total_revenue", 0) or 0.0)

# ============================================================
# ⚡ KPIs
# ============================================================
st.markdown("### ⚡ Healing & Monetization KPIs")
c1, c2, c3, c4 = st.columns(4)
c1.metric("🩺 Total Healings", f"{float(metrics.get('healings',0)):.0f}")
c2.metric("⚙️ Avg Recovery %", f"{float(metrics.get('avg_recovery_pct',0)):.2f}")
c3.metric("🎯 Avg Reward", f"{float(metrics.get('avg_reward',0)):.2f}")
c4.metric("💰 Total Revenue ($)", f"{total_revenue:.2f}")
st.divider()

# ============================================================
# 📈 Anomaly Distribution
# ============================================================
st.markdown("### 📊 Anomaly Distribution")
mix = metrics.get("anomaly_mix", {}) or {}
if mix:
    df = pd.DataFrame(list(mix.items()), columns=["Anomaly","Count"])
    st.bar_chart(df.set_index("Anomaly"))
else:
    st.info("📭 No anomaly data yet. Run healings to populate metrics.")

# ============================================================
# 🚨 Real-Time Healing Alerts
# ============================================================
st.divider()
st.markdown("### 🚨 Real-Time Healing Alerts")
if not rev_df.empty:
    latest_tx = rev_df.iloc[-1]
    st.info(
        f"💰 **New Healing Revenue Recorded!**\n\n"
        f"**Client:** `{latest_tx['User']}`  \n"
        f"**Workflow Healed:** `{latest_tx['Healing Type']}`  \n"
        f"**Billed Amount:** `${latest_tx['Cost ($)']:.4f}`  \n"
        f"**Timestamp:** `{latest_tx['Timestamp']}`  \n"
        f"🧾 Healing slip available for download below."
    )
else:
    st.warning("⚠️ No recent billing records — start a healing simulation to generate revenue logs.")

# ============================================================
# 📥 Downloads & Healing Slip
# ============================================================
st.divider()
st.markdown("### 📂 Download Logs & Reports")
col1, col2, col3 = st.columns(3)
with col1:
    st.download_button("📜 Healing Log", data="\n".join(logs).encode("utf-8"), file_name="healing_log.txt", mime="text/plain", use_container_width=True)
with col2:
    csv_bytes = safe_bytes_get(f"{BACKEND}/metrics/download")
    st.download_button("📊 Metrics CSV", data=csv_bytes or b"", file_name="metrics_log.csv", mime="text/csv", disabled=(csv_bytes is None), use_container_width=True)
with col3:
    rev_text = "\n".join(
        f"{row['Timestamp']} | {row['User']} | {row['Healing Type']} | ${row['Cost ($)']:.4f}"
        for _, row in rev_df.iterrows()
    ) if not rev_df.empty else "No revenue yet."
    st.download_button("💰 Revenue Log", data=rev_text.encode("utf-8"), file_name="healing_revenue.txt", mime="text/plain", use_container_width=True)

st.markdown("### 🧾 Active / Latest Healing Slip")
if not rev_df.empty:
    latest = rev_df.iloc[-1].to_dict()
    slip_text = f"""
🧾 Workflow Healer — Healing Slip
=====================================
Client/User: {latest['User']}
Workflow / Healing Type: {latest['Healing Type']}
Cost Billed: ${latest['Cost ($)']:.4f}
Timestamp: {latest['Timestamp']}

✅ Healing completed successfully.
💰 Payment processed via Paywalls.ai
=====================================
""".strip()
    st.text_area("Current Healing Slip", slip_text, height=180)
    st.download_button("💾 Download Latest Healing Slip", data=slip_text.encode("utf-8"), file_name=f"healing_slip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", mime="text/plain", use_container_width=True)
else:
    st.success("✅ All workflows stable — no active anomalies detected.")

st.caption(f"⏱️ Auto-refresh every 10s — Last updated: {datetime.now().strftime('%H:%M:%S')}")

# ============================================================
# 🩺 Healing Activity Logs
# ============================================================
st.markdown("## 🩺 Healing Activity Logs")
if logs:
    for line in logs[:50]:
        style, icon = "info", "💡"
        if "⚠️" in line: style, icon = "warning", "🟡"
        elif "✅" in line: style, icon = "success", "🟢"
        elif "❌" in line: style, icon = "error", "🔴"
        st.markdown(f"<div class='metric {style}'>{icon} {line}</div>", unsafe_allow_html=True)
else:
    st.info("📭 No healing logs yet — start simulation to see updates.")
