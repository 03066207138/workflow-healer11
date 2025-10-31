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
h1, h2, h3, h4, h5, h6, p, label, span, div {
  color: var(--fg) !important;
}

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
  border:none;
  border-radius:10px;
  padding:.55rem 1.1rem;
  font-weight:600;
  font-size:.95rem;
  transition:all .3s ease;
  box-shadow:0 0 10px rgba(96,165,250,.25);
}
.stButton button:hover {
  background: linear-gradient(135deg,#1d4ed8,#2563eb);
  box-shadow:0 0 14px rgba(96,165,250,.5);
  transform:translateY(-1px);
}

/* =========================
   🔥 TAB BAR STYLING
   ========================= */
[data-baseweb="tab-list"] {
  background-color: rgba(15, 23, 42, 0.9) !important;
  border-radius: 14px !important;
  padding: 0.4rem 0.6rem !important;
  border: 1px solid rgba(96,165,250,0.3) !important;
  box-shadow: 0 0 14px rgba(96,165,250,0.15) !important;
  justify-content: center !important;
}

button[data-baseweb="tab"] {
  color: #cbd5e1 !important;
  font-weight: 600 !important;
  font-size: 0.95rem !important;
  border-radius: 10px !important;
  margin: 0 6px !important;
  transition: all 0.25s ease-in-out !important;
  padding: 0.4rem 0.9rem !important;
  text-transform: none !important;
}

/* Active tab */
button[data-baseweb="tab"][aria-selected="true"] {
  background: linear-gradient(135deg, #2563eb, #60a5fa) !important;
  color: #ffffff !important;
  box-shadow: 0 0 12px rgba(96,165,250,0.4) !important;
  transform: translateY(-1px);
}

/* Hover effect */
button[data-baseweb="tab"]:hover {
  background: rgba(96,165,250,0.15) !important;
  color: #ffffff !important;
  transform: translateY(-1px);
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
.stDownloadButton button {
  background: linear-gradient(135deg,#22c55e,#16a34a);
  color:#fff !important;
  border:none;
  border-radius:10px;
  padding:.5rem 1rem;
  font-weight:600;
  transition:.3s;
  box-shadow:0 0 8px rgba(52,211,153,.3);
}
.stDownloadButton button:hover {
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
.stDataFrame tr:nth-child(even) td { background-color: rgba(30,41,59,0.6) !important; }
.stDataFrame tr:hover td { background-color: rgba(96,165,250,0.15) !important; }

/* Metric chips */
.metric {
  text-align:center;
  padding:10px;
  border-radius:12px;
  margin:6px;
  box-shadow:0 0 12px rgba(96,165,250,.15);
}
.success { background:rgba(52,211,153,.12); border:1px solid rgba(52,211,153,.4); }
.warning { background:rgba(250,204,21,.12); border:1px solid rgba(250,204,21,.4); }
.info { background:rgba(96,165,250,.12); border:1px solid rgba(96,165,250,.4); }
.error { background:rgba(239,68,68,.12); border:1px solid rgba(239,68,68,.4); }

[data-testid="stMetricValue"] {
  color:var(--accent);
  font-weight:700;
}


/* Auto-refresh control buttons */
button[kind="primary"] {
  background: linear-gradient(135deg,#3b82f6,#1d4ed8) !important;
  color:#fff !important;
  border-radius:8px !important;
  box-shadow:0 0 10px rgba(59,130,246,.3) !important;
}


/* JSON viewer */
[data-testid="stJson"] pre, .stJson, .stJson > div, .stJson pre code {
  background:#1e293b !important;
  color:#e2e8f0 !important;
  font-family:"JetBrains Mono",monospace;
  font-size:.85rem;
  line-height:1.4;
  border-radius:8px;
  border:1px solid rgba(96,165,250,.3);
  padding:10px;
}
.stJson span { color:#93c5fd !important; }
.stJson span.string { color:#86efac !important; }
.stJson span.number { color:#facc15 !important; }
.stJson span.boolean { color:#f87171 !important; }

.stAlert {
  border-radius:10px;
  box-shadow:0 0 10px rgba(96,165,250,.25);
}
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
# ⚙️ Sidebar Controls (Unified Panel)
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Control Center")

    # -----------------------------------------
    # 🔍 Backend Check
    # -----------------------------------------
    if st.button("🔎 Check Backend Connection"):
        h = cached_health()
        if h and h.get("status") == "ok":
            st.success(f"✅ Connected — Mode: {h.get('mode')}")
            st.json(h)
        else:
            st.error("❌ Backend not reachable")

    st.divider()

    # -----------------------------------------
    # 🔁 Simulation Control
    # -----------------------------------------
    st.markdown("### 🔁 Simulation Control")
    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        if st.button("🚀 Start Simulation", use_container_width=True):
            try:
                requests.post(f"{BACKEND}/sim/start", timeout=6)
                st.session_state.auto_refresh = True  # start auto-refresh
                st.success("✅ Simulation started & auto-refresh enabled!")
            except Exception as e:
                st.error(f"❌ Failed to start simulation: {e}")
    with sim_col2:
        if st.button("🧊 Stop Simulation", use_container_width=True):
            try:
                requests.post(f"{BACKEND}/sim/stop", timeout=6)
                st.session_state.auto_refresh = False  # stop auto-refresh
                st.warning("⏸ Simulation stopped & auto-refresh paused.")
            except Exception as e:
                st.error(f"❌ Failed to stop simulation: {e}")

    st.divider()

    # -----------------------------------------
    # ⚙️ Manual Healing Trigger
    # -----------------------------------------
    st.markdown("### ⚡ Manual Healing Trigger")
    anomaly = st.selectbox(
        "Select Anomaly Type",
        ["workflow_delay", "queue_pressure", "data_error", "api_failure"],
        key="manual_anomaly"
    )
    if st.button("💥 Run Healing Cycle", use_container_width=True):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={anomaly}", timeout=7)
            if res.status_code == 200:
                j = res.json()
                toast("success", f"✅ {j.get('workflow','?')} healed — Recovery {j.get('recovery_pct',0)}%")
                st.json(j)
            else:
                st.warning(f"⚠️ Healing trigger failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.divider()

    # -----------------------------------------
    # 🌐 FlowXO Webhook Trigger
    # -----------------------------------------
    st.markdown("### 🌐 Send FlowXO Webhook")
    wf = st.selectbox("Workflow", ["invoice_processing", "order_processing", "customer_support"], key="flowxo_wf")
    a = st.selectbox("Anomaly Type", ["workflow_delay", "queue_pressure", "data_error", "api_failure"], key="flowxo_anomaly")
    if st.button("🚨 Send Webhook", use_container_width=True):
        try:
            payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            if res.status_code == 200:
                st.success("🌐 Webhook successfully sent to FlowXO!")
                st.json(res.json())
            else:
                st.warning(f"⚠️ Webhook failed ({res.status_code})")
        except Exception as e:
            st.error(f"❌ Webhook error: {e}")

    st.divider()

    # -----------------------------------------
    # 🔄 Auto Refresh Control
    # -----------------------------------------
    st.markdown("### 🔄 Auto Refresh Control")
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False

    col_auto1, col_auto2 = st.columns(2)
    with col_auto1:
        if st.button("▶ Start Auto Refresh", use_container_width=True):
            st.session_state.auto_refresh = True
            st.success("🔄 Auto refresh started (every 6s).")
    with col_auto2:
        if st.button("⏹ Stop Auto Refresh", use_container_width=True):
            st.session_state.auto_refresh = False
            st.warning("⏸ Auto refresh stopped.")

    # 🔁 Only run when enabled
    if st.session_state.auto_refresh:
        st_autorefresh(interval=6000, key="sidebar_auto_refresh")

# ============================================================
# 📊 Main Dashboard Tabs
# ============================================================
tabs = st.tabs(["📊 Dashboard", "💾 Logs & Reports", "🧾 Healing Slips", "🎟️ Tickets", "⚙️ Controls"])

# ============================================================
# 📊 DASHBOARD TAB
# ============================================================
with tabs[0]:
    st.subheader("⚡ Healing & Monetization KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🩺 Total Healings", f"{metrics.get('healings',0):.0f}")
    c2.metric("⚙️ Avg Recovery %", f"{metrics.get('avg_recovery_pct',0):.2f}")
    c3.metric("🎯 Avg Reward", f"{metrics.get('avg_reward',0):.2f}")
    c4.metric("💰 Total Revenue ($)", f"{total_revenue:.2f}")

    st.divider()
    st.markdown("### 🚨 Real-Time Healing Alerts")
    if not rev_df.empty:
        latest_tx = rev_df.iloc[-1]
        st.info(
            f"💰 **New Healing Recorded!**\n\n"
            f"**Client:** `{latest_tx['User']}`  \n"
            f"**Workflow Healed:** `{latest_tx['Healing Type']}`  \n"
            f"**Billed Amount:** `${latest_tx['Cost ($)']:.4f}`  \n"
            f"**Timestamp:** `{latest_tx['Timestamp']}`"
        )
    else:
        st.warning("⚠️ No healing events recorded yet — start simulation to generate data.")


# ============================================================
# 💾 LOGS & REPORTS TAB
# ============================================================
with tabs[1]:
    st.subheader("📂 Download Logs & Reports")
    col1, col2 = st.columns(2)
    col1.download_button("📜 Healing Log", "\n".join(logs), "healing_log.txt")
    col2.download_button("💰 Revenue Log", rev_df.to_csv(index=False).encode(), "revenue.csv")

    st.subheader("🩺 Healing Activity Logs")
    if logs:
        for line in logs[-30:]:
            st.markdown(f"<div class='metric info'>💡 {line}</div>", unsafe_allow_html=True)
    else:
        st.info("📭 No healing logs yet.")

    st.subheader("📊 Anomaly Distribution")
    mix = metrics.get("anomaly_mix", {}) or {}
    if mix:
        df = pd.DataFrame(list(mix.items()), columns=["Anomaly","Count"])
        st.bar_chart(df.set_index("Anomaly"))
    else:
        st.info("📭 No anomaly data yet. Run healings to populate metrics.")


# ============================================================
# 🧾 HEALING SLIPS TAB
# ============================================================
with tabs[2]:
    st.subheader("🧾 Healing Slip Generator")
    if not rev_df.empty:
        latest_tx = rev_df.iloc[-1]
        slip_text = f"""
        🧾 Workflow Healer — Healing Slip
        =====================================
        Client/User: {latest_tx['User']}
        Workflow Healed: {latest_tx['Healing Type']}
        Cost Billed: ${latest_tx['Cost ($)']:.4f}
        Timestamp: {latest_tx['Timestamp']}

        ✅ Healing completed successfully.
        💰 Payment processed via Paywalls.ai
        =====================================
        """.strip()
        st.text_area("📄 Healing Slip", slip_text, height=180)
        st.download_button(
            "💾 Download Healing Slip",
            data=slip_text.encode("utf-8"),
            file_name=f"healing_slip_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.warning("⚠️ No billing records yet — start healing cycle to generate slip.")


# ============================================================
# 🎟️ TICKETS TAB
# ============================================================
with tabs[3]:
    st.subheader("🎟️ Create a Support Ticket")
    issue = st.text_input("Issue Title", placeholder="e.g. Healing failed or anomaly not recovered")
    details = st.text_area("Describe the issue", placeholder="Provide context or recovery failure details...")

    if st.button("🧾 Create Ticket"):
        ticket = {
            "ticket_id": f"TCKT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "issue": issue or "Unnamed Issue",
            "details": details or "No details provided",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "Open"
        }

        os.makedirs("data", exist_ok=True)
        with open("data/tickets.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(ticket) + "\n")

        st.success(f"🎫 Ticket Created — ID: {ticket['ticket_id']}")
        st.json(ticket)

    st.subheader("📋 All Tickets")
    if os.path.exists("data/tickets.json"):
        with open("data/tickets.json", "r", encoding="utf-8") as f:
            tickets = [json.loads(line) for line in f.readlines() if line.strip()]
        if tickets:
            st.dataframe(pd.DataFrame(tickets))
        else:
            st.info("✅ No tickets yet — system stable.")
    else:
        st.info("✅ Ticket system initialized — no tickets yet.")


# ============================================================
# ⚙️ CONTROLS TAB
# ============================================================
with tabs[4]:
    st.subheader("⚙️ Simulation & Webhook Controls")
    st.write("Use the sidebar or buttons here to trigger actions manually.")
    st.button("🚀 Start Simulation", on_click=lambda: requests.post(f"{BACKEND}/sim/start"))
    st.button("🧊 Stop Simulation", on_click=lambda: requests.post(f"{BACKEND}/sim/stop"))
    st.button("💥 Run Healing Cycle", on_click=lambda: requests.post(f"{BACKEND}/simulate?event=workflow_delay"))

