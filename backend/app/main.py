# ============================================================
# 🌐 IBM Workflow Healing Agent → Prototype-to-Profit Edition
# Hybrid: Watsonx.ai + Groq Local AI + Paywalls.ai + FlowXO
# ============================================================

import os
import math
import random
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

# ============================================================
# 🔹 Load Environment Variables
# ============================================================
load_dotenv()

print(
    "🔑 Loaded keys — Watsonx:",
    str(os.getenv("WATSONX_API_KEY"))[:10],
    "| Groq:",
    str(os.getenv("GROQ_API_KEY"))[:10],
    "| Paywalls:",
    str(os.getenv("PAYWALLS_KEY"))[:10],
    "..."
)

# ============================================================
# 📦 Internal Imports (Safe Relative)
# ============================================================
try:
    from .settings import settings
    from .healing.executor import HealingExecutor
    from .healing import policies
    from .telemetry.simulator import sim
    from .utils.metrics_logger import MetricsLogger
    from .integrations.paywalls_client import bill_healing_event
except ImportError:
    # Fallback for local execution
    from settings import settings
    from healing.executor import HealingExecutor
    from healing import policies
    from telemetry.simulator import sim
    from utils.metrics_logger import MetricsLogger
    from integrations.paywalls_client import bill_healing_event

# ============================================================
# ⚙️ Initialize Core Components
# ============================================================
os.makedirs("data", exist_ok=True)
metrics_logger = MetricsLogger(Path(settings.METRICS_LOG_PATH))
executor = HealingExecutor()

use_groq = bool(os.getenv("GROQ_API_KEY"))
use_watsonx = bool(os.getenv("WATSONX_API_KEY")) and bool(os.getenv("WATSONX_PROJECT_ID"))
use_paywalls = bool(os.getenv("PAYWALLS_KEY"))

PAYWALL_LOG = "data/healing_revenue.log"

# ============================================================
# 🚀 Initialize FastAPI App
# ============================================================
app = FastAPI(
    title="IBM Workflow Healing Agent — Prototype-to-Profit Edition",
    version="3.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🩺 Health Check Endpoint
# ============================================================
@app.get("/health")
def health():
    """Check backend and orchestrator readiness."""
    return {
        "status": "ok",
        "watsonx_ready": use_watsonx,
        "groq_ready": use_groq,
        "paywalls_ready": use_paywalls,
        "mode": (
            "Watsonx.ai"
            if use_watsonx
            else ("Groq Local AI" if use_groq else "Offline Simulation")
        ),
    }

# ============================================================
# 📜 Healing Logs Endpoint
# ============================================================
@app.get("/healing/logs")
def get_healing_logs(n: int = 50):
    """Fetch the latest healing logs for the dashboard."""
    log_path = settings.HEALING_LOG_PATH
    if not os.path.exists(log_path):
        return {"logs": []}

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        logs = lines[-n:][::-1]  # last n lines, reversed (newest first)
        return {"logs": logs}
    except Exception as e:
        return {"logs": [f"⚠️ Error reading logs: {e}"]}

# ============================================================
# 📊 Metrics Download Endpoint
# ============================================================
@app.get("/metrics/download")
def metrics_download():
    """Download healing metrics as CSV."""
    if not os.path.exists(settings.METRICS_LOG_PATH):
        raise HTTPException(status_code=404, detail="No metrics file found.")
    return FileResponse(
        settings.METRICS_LOG_PATH,
        media_type="text/csv",
        filename="metrics_log.csv",
    )

# ============================================================
# ⚡ Manual Healing Simulation
# ============================================================
@app.post("/simulate")
def simulate(event: str = "workflow_delay"):
    """
    Simulate one healing cycle using either Watsonx.ai or Groq backend.
    Monetize each healing event through Paywalls.ai.
    """
    workflow = random.choice(["invoice_processing", "order_processing", "customer_support"])
    anomaly = event if event in policies.POLICY_MAP else random.choice(list(policies.POLICY_MAP.keys()))

    result = executor.heal(workflow, anomaly)

    # 💰 Monetization: charge per healing
    billing_info = bill_healing_event(
        user_id="demo_client",
        heal_type=anomaly,
        cost=0.05,  # micro-billing per healing
    )

    return {
        "workflow": workflow,
        "anomaly": anomaly,
        "suggested_actions": result.get("actions", []),
        "status": result.get("status"),
        "recovery_pct": result.get("recovery_pct"),
        "reward": result.get("reward"),
        "engine": "Watsonx.ai" if use_watsonx else ("Groq Local" if use_groq else "Fallback"),
        "billing": billing_info,
    }

# ============================================================
# 🧪 Continuous Simulation Routes
# ============================================================
@app.post("/sim/start")
def start_simulation():
    """Start continuous background simulation."""
    print("🚀 Continuous simulation started.")
    return sim.start()

@app.post("/sim/stop")
def stop_simulation():
    """Stop continuous simulation."""
    print("🧊 Simulation stopped.")
    return sim.stop()

# ============================================================
# 📊 Metrics Summary for Dashboard
# ============================================================
@app.get("/metrics/summary")
def metrics_summary():
    """Return summarized healing performance for dashboard."""
    summary = metrics_logger.summary()
    clean_summary = {}

    for k, v in summary.items():
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val):
                val = 0.0
            clean_summary[k] = round(val, 2)
        except Exception:
            clean_summary[k] = v

    # 🧩 Anomaly Distribution
    anomaly_mix = {}
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            if not df.empty and "anomaly" in df.columns:
                anomaly_mix = df["anomaly"].dropna().value_counts().to_dict()
    except Exception as e:
        print(f"[Metrics Summary] ⚠️ Failed to parse anomaly mix: {e}")

    clean_summary["anomaly_mix"] = anomaly_mix

    # 🧠 Add last action
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            clean_summary["last_action"] = (
                str(df["action"].iloc[-1]) if "action" in df.columns else "N/A"
            )
    except Exception:
        clean_summary["last_action"] = "N/A"

    return clean_summary

# ============================================================
# 🔁 FlowXO Webhook Integration
# ============================================================
@app.post("/integrations/flowxo/webhook")
async def flowxo_trigger(req: Request):
    """Triggered by FlowXO to execute healing externally."""
    try:
        data = await req.json()
        workflow_id = data.get("workflow_id", "unknown_workflow")
        anomaly = data.get("anomaly", "unknown_anomaly")
        user_id = data.get("user_id", "demo_client")

        metrics_logger.log_flowxo_event(workflow_id, anomaly, user_id)
        result = executor.heal(workflow_id, anomaly)
        billing = bill_healing_event(user_id, anomaly, cost=0.05)

        print(f"📂 [FlowXO] Logged → {metrics_logger.flowxo_log_path.resolve()}")
        return JSONResponse(
            {
                "workflow": workflow_id,
                "anomaly": anomaly,
                "status": result.get("status"),
                "recovery_pct": result.get("recovery_pct"),
                "reward": result.get("reward"),
                "billing": billing,
            }
        )
    except Exception as e:
        print(f"[FlowXO] ❌ Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 💹 Unified Revenue Data Endpoint
# ============================================================
@app.get("/metrics/revenue")
def get_revenue_data():
    """Provides monetization data for Streamlit dashboard."""
    data = []
    total_revenue = 0.0
    total_heals = 0

    if os.path.exists(PAYWALL_LOG):
        with open(PAYWALL_LOG, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.strip().split("|")]
                if len(parts) >= 4:
                    ts, workflow, anomaly, cost, *_ = parts
                    try:
                        cost_val = float(cost.replace("$", "").strip())
                    except:
                        cost_val = 0.0
                    total_revenue += cost_val
                    total_heals += 1
                    data.append({
                        "Timestamp": ts,
                        "Workflow": workflow,
                        "Anomaly": anomaly,
                        "Cost ($)": cost_val
                    })

    return {
        "total_revenue": round(total_revenue, 4),
        "total_heals": total_heals,
        "logs": data
    }

# ============================================================
# 🚀 Startup Message
# ============================================================
@app.on_event("startup")
def startup_event():
    print("\n🚀 IBM Workflow Healing Agent (Prototype-to-Profit Edition) started!")
    print(f"▪ App: {settings.APP_NAME}")
    print(f"▪ FlowXO log path: {metrics_logger.flowxo_log_path.resolve()}")
    print(f"▪ Mode: {'Watsonx.ai' if use_watsonx else ('Groq Local' if use_groq else 'Offline Simulation')}")
    print(f"▪ Paywalls.ai Integrated: {use_paywalls}")
    print(f"▪ Loaded Policies: {list(policies.POLICY_MAP.keys())}\n")
