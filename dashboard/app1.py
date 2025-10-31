# ============================================================
# 💰 Prototype-to-Profit: Workflow Healer (Streamlit Dashboard)
# IBM × Paywalls.ai × FlowXO — AI-Powered Workflow Healing
# v4.9 — Crash-safe KPIs • Tabbed UI • Sidebar Auto-Refresh
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
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎨 Styles
# ============================================================
st.markdown("""
<style>
:root { --bg-1:#0f172a; --bg-2:#1e293b; --fg:#f8fafc; --accent:#60a5fa; --green:#34d399; --red:#f87171; --yellow:#fde047; }
body, .stApp { background: radial-gradient(circle at top left, var(--bg-1), var(--bg-2)); color: var(--fg); font-family:"Inter",system-ui,sans-serif; }
h1,h2,h3,h4,h5,h6,p,label,span,div{ color:var(--fg) !important; }
section[data-testid="stSidebar"]{ background:#0f172a !important; color:var(--fg) !important; border-right:1px solid rgba(255,255,255,.08); }
section[data-testid="stSidebar"] * { color:var(--fg)!important; }
.stButton button{ background:linear-gradient(135deg,#2563eb,#1d4ed8); color:#fff!important; border:none; border-radius:10px; padding:.55rem 1.1rem; font-weight:600; font-size:.95rem; box-shadow:0 0 10px rgba(96,165,250,.25); }
.stButton button:hover{ background:linear-gradient(135deg,#1d4ed8,#2563eb); box-shadow:0 0 14px rgba(96,165,250,.5); transform:translateY(-1px); }
[data-baseweb="tab-list"]{ background-color:rgba(15,23,42,.9)!important; border-radius:14px!important; padding:.4rem .6rem!important; border:1px solid rgba(96,165,250,.3)!important; box-shadow:0 0 14px rgba(96,165,250,.15)!important; justify-content:center!important; }
button[data-baseweb="tab"]{ color:#cbd5e1!important; font-weight:600!important; font-size:.95rem!important; border-radius:10px!important; margin:0 6px!important; transition:all .25s ease-in-out!important; padding:.4rem .9rem!important; }
button[data-baseweb="tab"][aria-selected="true"]{ background:linear-gradient(135deg,#2563eb,#60a5fa)!important; color:#fff!important; box-shadow:0 0 12px rgba(96,165,250,.4)!important; transform:translateY(-1px); }
div[data-baseweb="select"]>div{ background-color:#1e293b!important; color:var(--fg)!important; border:1px solid rgba(96,165,250,.35)!important; border-radius:8px; }
.stDownloadButton button{ background:linear-gradient(135deg,#22c55e,#16a34a); color:#fff!important; border:none; border-radius:10px; padding:.5rem 1rem; font-weight:600; box-shadow:0 0 8px rgba(52,211,153,.3); }
.stDataFrame{ background-color:#0f172a!important; } .stDataFrame th{ background:#1e293b!important; color:#f8fafc!important; border-bottom:2px solid rgba(96,165,250,.5)!important; }
.stDataFrame td{ color:#e2e8f0!important; border-bottom:1px solid rgba(255,255,255,.08)!important; }
.metric{ text-align:center; padding:10px; border-radius:12px; margin:6px; box-shadow:0 0 12px rgba(96,165,250,.15); }
/* ===============================
   🎨 JSON Viewer Styling (Dark)
   =============================== */
[data-testid="stJson"] pre,
.stJson,
.stJson > div,
.stJson pre code {
  background: #1e293b !important;
  color: #e2e8f0 !important;
  font-family: "JetBrains Mono", monospace;
  font-size: 0.85rem;
  line-height: 1.4;
  border-radius: 8px;
  border: 1px solid rgba(96, 165, 250, 0.3);
  padding: 10px;
}

/* Default key/value text color */
.stJson span {
  color: #93c5fd !important; /* bluish-gray for keys */
}

/* String values */
.stJson span.string {
  color: #86efac !important; /* soft green */
}

/* Numeric values */
.stJson span.number {
  color: #facc15 !important; /* warm yellow */
}

/* Boolean values (true/false) */
.stJson span.boolean {
  color: #f87171 !important; /* coral red */
}

.success{background:rgba(52,211,153,.12);border:1px solid rgba(52,211,153,.4)} .info{background:rgba(96,165,250,.12);border:1px solid rgba(96,165,250,.4)}
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
        else:
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
    return safe_json_get(f"{BACKEND}/health", default={"status": "offline", "mode": "Offline Simulation"}) or {}

# ============================================================
# ⚙️ Sidebar Controls (Unified Panel + Auto-Refresh)
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Control Center")

    if st.button("🔎 Check Backend Connection"):
        st.json(cached_health())

    st.divider()
    st.markdown("### 🔁 Simulation Control")
    cA, cB = st.columns(2)
    with cA:
        if st.button("🚀 Start", use_container_width=True):
            try:
                requests.post(f"{BACKEND}/sim/start", timeout=6)
                st.session_state.auto_refresh = True
                st.success("Started + Auto-refresh ON")
            except Exception as e:
                st.error(f"Start failed: {e}")
    with cB:
        if st.button("🧊 Stop", use_container_width=True):
            try:
                requests.post(f"{BACKEND}/sim/stop", timeout=6)
                st.session_state.auto_refresh = False
                st.warning("Stopped + Auto-refresh OFF")
            except Exception as e:
                st.error(f"Stop failed: {e}")

    st.divider()
    st.markdown("### ⚡ Manual Healing")
    anomaly = st.selectbox("Anomaly", ["workflow_delay","queue_pressure","data_error","api_failure"], key="manual_anomaly")
    if st.button("💥 Run Healing", use_container_width=True):
        try:
            res = requests.post(f"{BACKEND}/simulate?event={anomaly}", timeout=7)
            st.json(res.json() if res.status_code == 200 else {"error": res.status_code})
        except Exception as e:
            st.error(f"Healing error: {e}")

    st.divider()
    st.markdown("### 🌐 FlowXO Webhook")
    wf = st.selectbox("Workflow", ["invoice_processing","order_processing","customer_support"], key="flowxo_wf")
    a = st.selectbox("Anomaly Type", ["workflow_delay","queue_pressure","data_error","api_failure"], key="flowxo_anomaly")
    if st.button("🚨 Send Webhook", use_container_width=True):
        try:
            payload = {"workflow_id": wf, "anomaly": a, "user_id": "demo_client"}
            res = requests.post(f"{BACKEND}/integrations/flowxo/webhook", json=payload, timeout=10)
            st.json(res.json() if res.status_code == 200 else {"error": res.status_code})
        except Exception as e:
            st.error(f"Webhook error: {e}")

    st.divider()
    st.markdown("### 🔄 Auto Refresh")
    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = False
    d1, d2 = st.columns(2)
    with d1:
        if st.button("▶ Start", use_container_width=True):
            st.session_state.auto_refresh = True
    with d2:
        if st.button("⏹ Stop", use_container_width=True):
            st.session_state.auto_refresh = False

    if st.session_state.auto_refresh:
        st_autorefresh(interval=6000, key="sidebar_auto_refresh")

# ============================================================
# 🧠 Header & Integration Status
# ============================================================
st.title("💎 Prototype-to-Profit: AI Workflow Healer(No Human in the Loop)")
st.caption("Heal, Automate, and Monetize Workflows — Powered by Paywalls.ai & FlowXO.")

health = cached_health()
mode = str(health.get("mode", "Offline Simulation"))
col1, col2, col3 = st.columns(3)
col1.metric("⚡ Groq Local AI", "✅ Ready" if health.get("groq_ready") else "❌ Off")
col2.metric("💰 Paywalls.ai", "✅ Connected" if health.get("paywalls_ready") else "❌ Off")
col3.metric("🌐 FlowXO Webhook", "✅ Active" if health.get("flowxo_ready") else "❌ Inactive")
st.info(f"⚙️ Mode: {mode}")

# ============================================================
# 📥 Data Fetch (Crash-safe, before tabs)
# ============================================================
def normalize_revenue_rows(rows):
    df_rows = []
    for r in rows or []:
        ts = r.get("Timestamp") or r.get("ts") or ""
        user = r.get("User") or r.get("user") or r.get("Workflow") or "N/A"
        heal_type = r.get("Healing Type") or r.get("heal_type") or r.get("Anomaly") or r.get("anomaly") or "N/A"
        cost = r.get("Cost ($)") or r.get("amount") or r.get("cost") or 0
        try:
            cost = float(str(cost).replace("$", "").strip())
        except Exception:
            cost = 0.0
        df_rows.append({"Timestamp": ts, "User": user, "Healing Type": heal_type, "Cost ($)": cost})
    return pd.DataFrame(df_rows)

# Fetch with guards
try:
    metrics = safe_json_get(f"{BACKEND}/metrics/summary", default={}) or {}
except Exception:
    metrics = {}

try:
    revenue_payload = safe_json_get(f"{BACKEND}/metrics/revenue", default={}) or {}
    rev_df = normalize_revenue_rows(revenue_payload.get("logs", []))
    total_revenue = float(revenue_payload.get("total_revenue", 0) or 0.0)
except Exception:
    rev_df = pd.DataFrame(columns=["Timestamp","User","Healing Type","Cost ($)"])
    total_revenue = 0.0

try:
    logs_resp = safe_json_get(f"{BACKEND}/healing/logs?n=80", default={"logs":[]}) or {"logs":[]}
    logs = logs_resp.get("logs", []) or []
except Exception:
    logs = []

# Safe KPI values
healings = float(metrics.get("healings", 0) or 0)
avg_recovery = float(metrics.get("avg_recovery_pct", 0) or 0)
avg_reward = float(metrics.get("avg_reward", 0) or 0)
anomaly_mix = metrics.get("anomaly_mix", {}) or {}

# ============================================================
# 📊 Tabs
# ============================================================
tabs = st.tabs(["📊 Dashboard", "💾 Logs & Reports", "🧾 Healing Slips", "🎟️ Tickets", "⚙️ Controls"])

# ---------------- Dashboard ----------------
with tabs[0]:
    st.subheader("⚡ Healing & Monetization KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🩺 Total Healings", f"{healings:.0f}")
    c2.metric("⚙️ Avg Recovery %", f"{avg_recovery:.2f}")
    c3.metric("🎯 Avg Reward", f"{avg_reward:.2f}")
    c4.metric("💰 Total Revenue ($)", f"{total_revenue:.2f}")

    st.divider()
    st.markdown("### 🚨 Real-Time Healing Alerts")
    if not rev_df.empty:
        latest_tx = rev_df.iloc[-1]
        st.info(
            f"💰 **New Healing Recorded!**  \n"
            f"**Client:** `{latest_tx['User']}`  \n"
            f"**Workflow Healed:** `{latest_tx['Healing Type']}`  \n"
            f"**Billed Amount:** `${latest_tx['Cost ($)']:.4f}`  \n"
            f"**Timestamp:** `{latest_tx['Timestamp']}`"
        )
    else:
        st.warning("⚠️ No healing events recorded yet — start simulation to generate data.")

# ---------------- Logs & Reports ----------------
with tabs[1]:
    st.subheader("📂 Download Logs & Reports")
    colA, colB = st.columns(2)
    colA.download_button("📜 Healing Log", "\n".join(logs), "healing_log.txt")
    colB.download_button("💰 Revenue Log (CSV)", rev_df.to_csv(index=False).encode(), "revenue.csv")

    st.subheader("🩺 Healing Activity Logs")
    if logs:
        for line in logs[-30:]:
            st.markdown(f"<div class='metric info'>💡 {line}</div>", unsafe_allow_html=True)
    else:
        st.info("📭 No healing logs yet.")

    st.subheader("📊 Anomaly Distribution")
    if anomaly_mix:
        df_mix = pd.DataFrame(list(anomaly_mix.items()), columns=["Anomaly","Count"])
        st.bar_chart(df_mix.set_index("Anomaly"))
    else:
        st.info("📭 No anomaly data yet. Run healings to populate metrics.")

# ---------------- Healing Slips ----------------
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
        st.warning("⚠️ No billing records yet — start a healing cycle to generate a slip.")

# ---------------- Tickets ----------------
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
            tickets = [json.loads(line) for line in f if line.strip()]
        if tickets:
            st.dataframe(pd.DataFrame(tickets))
        else:
            st.info("✅ No tickets yet — system stable.")
    else:
        st.info("✅ Ticket system initialized — no tickets yet.")

# ---------------- Controls ----------------
with tabs[4]:
    st.subheader("⚙️ Simulation & Webhook Controls")
    st.write("Use the sidebar or quick actions here.")
    st.button("🚀 Start Simulation", on_click=lambda: requests.post(f"{BACKEND}/sim/start"))
    st.button("🧊 Stop Simulation", on_click=lambda: requests.post(f"{BACKEND}/sim/stop"))
    st.button("💥 Run Healing (workflow_delay)", on_click=lambda: requests.post(f"{BACKEND}/simulate?event=workflow_delay"))
