import os
import json
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
    st.markdown("## ⚙️ Simulation & Webhook Controls")

    def safe_json_get(url, timeout=5):
        try:
            r = requests.get(url, timeout=timeout)
            return r.json() if r.status_code == 200 else None
        except Exception as e:
            st.error(f"❌ Error contacting backend: {e}")
            return None

    # ---- Health Check ----
    if st.button("🔎 Test Backend"):
        health = safe_json_get(f"{BACKEND}/health")
        if health:
            st.success(f"✅ Backend OK — Mode: {health.get('mode')} | Paywalls: {health.get('paywalls_ready')}")

    # ---- Simulation ----
    st.divider()
    st.markdown("### 🔁 Simulation Controls")

    if st.button("🚀 Start Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/start", timeout=5)
            st.success("✅ Healing simulation started!" if res.status_code == 200 else f"⚠️ Could not start ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Error starting: {e}")

    if st.button("🧊 Stop Simulation"):
        try:
            res = requests.post(f"{BACKEND}/sim/stop", timeout=5)
            st.warning("🛑 Simulation stopped." if res.status_code == 200 else f"⚠️ Stop failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Error stopping: {e}")

    # ---- Manual Healing ----
    st.divider()
    st.markdown("### ⚡ Trigger Manual Healing")
    selected_event = st.selectbox("Select anomaly:", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])
    heal_data = None

    if st.button("💥 Trigger Healing"):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={selected_event}", timeout=7)
            if res.status_code == 200:
                heal_data = res.json()
                st.session_state["last_heal"] = heal_data  # ✅ store for download
                st.success(f"✅ {heal_data['workflow']} healed | Recovery: {heal_data['recovery_pct']}% | Billed via Paywalls.ai")
                st.json(heal_data)
            else:
                st.warning(f"⚠️ Healing trigger failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Failed to trigger: {e}")

    # ---- FlowXO Webhook ----
    st.divider()
    st.markdown("### 🌐 FlowXO Webhook")

    wf = st.selectbox("Workflow", ["invoice_processing", "order_processing", "customer_support"])
    anomaly = st.selectbox("Anomaly Type", ["workflow_delay", "queue_pressure", "data_error", "api_failure"])

    if st.button("🚨 Send Webhook (Quick Mode)"):
        try:
            payload = {"workflow_id": wf, "anomaly": anomaly, "user_id": "demo_client"}
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            if res.status_code == 200:
                st.success("✅ FlowXO event processed successfully!")
                st.json(res.json())
            else:
                st.warning(f"⚠️ Webhook failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ FlowXO webhook error: {e}")

# ============================================================
# 🔁 Auto Refresh
# ============================================================
st_autorefresh(interval=6000, key="refresh")

# ============================================================
# 📊 Unified Metrics & Download Heal Slip
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

    st.markdown("### ⚡ Unified Healing & Monetization KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🩺 Total Healings", f"{total_heals:.0f}")
    c2.metric("⚙️ Avg Recovery %", f"{avg_recovery:.2f}")
    c3.metric("🎯 Avg Reward", f"{avg_reward:.2f}")
    c4.metric("💰 Total Revenue ($)", f"{total_revenue:.2f}")

    # ============================================================
    # 📄 Download Heal Slip Button
    # ============================================================
    if "last_heal" in st.session_state:
        heal = st.session_state["last_heal"]
        st.divider()
        st.markdown("### 📄 Download Current Heal Slip")

        def generate_heal_slip(heal):
            """Create a PDF slip for the latest healing."""
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            story.append(Paragraph("<b>IBM Workflow Healing Slip</b>", styles["Title"]))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"🕓 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
            story.append(Paragraph(f"🏷 Workflow: {heal.get('workflow')}", styles["Normal"]))
            story.append(Paragraph(f"⚙️ Anomaly: {heal.get('anomaly')}", styles["Normal"]))
            story.append(Paragraph(f"📊 Recovery %: {heal.get('recovery_pct', 0.0)}", styles["Normal"]))
            story.append(Paragraph(f"🎯 Reward: {heal.get('reward', 0.0)}", styles["Normal"]))
            story.append(Paragraph(f"💰 Billing: {heal.get('billing', {})}", styles["Normal"]))
            story.append(Spacer(1, 12))
            story.append(Paragraph("<i>Generated by Prototype-to-Profit — Powered by Paywalls.ai × FlowXO</i>", styles["Italic"]))
            doc.build(story)
            pdf = buffer.getvalue()
            buffer.close()
            return pdf

        pdf_bytes = generate_heal_slip(st.session_state["last_heal"])
        st.download_button(
            label="📥 Download Heal Slip (PDF)",
            data=pdf_bytes,
            file_name=f"HealSlip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
        )

    # ============================================================
    # 🩹 Healing Logs
    # ============================================================
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
