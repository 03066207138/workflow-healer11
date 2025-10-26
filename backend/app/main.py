# ============================================================
# 🌐 IBM Workflow Healing Agent → Prototype-to-Profit Edition
# Hybrid: Watsonx.ai + Groq Local AI + Paywalls.ai + FlowXO
# ============================================================

from dotenv import load_dotenv
import os
import math
import random
import pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

# ============================================================
# 🔹 Load Environment Variables and Internal Imports
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

from .settings import settings
from .healing.executor import HealingExecutor
from .healing import policies
from .telemetry.simulator import sim
from .utils.metrics_logger import MetricsLogger
from .integrations.paywalls_client import bill_healing_event  # ✅ Monetization Integration

# ============================================================
# ⚙️ Initialize Core Components
# ============================================================
metrics_logger = MetricsLogger(Path(settings.METRICS_LOG_PATH))
executor = HealingExecutor()

use_groq = bool(os.getenv("GROQ_API_KEY"))
use_watsonx = bool(os.getenv("WATSONX_API_KEY")) and bool(os.getenv("WATSONX_PROJECT_ID"))
use_paywalls = bool(os.getenv("PAYWALLS_KEY"))

# ============================================================
# 🚀 Initialize FastAPI App
# ============================================================
app = FastAPI(
    title="IBM Workflow Healing Agent — Prototype-to-Profit Edition",
    version="3.0"
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
    """Check backend and orchestrator readiness"""
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
    """Fetch the latest healing logs for the dashboard"""
    log_path = settings.HEALING_LOG_PATH
    if not os.path.exists(log_path):
        return {"logs": []}
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        logs = [line.strip() for line in lines if line.strip()][-n:]
        logs.reverse()
        return {"logs": logs}
    except Exception as e:
        print(f"[Logs] ⚠️ Could not read logs: {e}")
        return {"logs": [f"⚠️ Error reading logs: {str(e)}"]}

# ============================================================
# 📊 Metrics Download Endpoint
# ============================================================
@app.get("/metrics/download")
def metrics_download():
    """Download healing metrics as CSV"""
    if not os.path.exists(settings.METRICS_LOG_PATH):
        raise HTTPException(status_code=404, detail="No metrics file found.")
    return FileResponse(
        settings.METRICS_LOG_PATH,
        media_type="text/csv",
        filename="metrics_log.csv",
    )

# ============================================================
# ⚡ Manual Healing Simulation (Prototype → Profit)
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
        cost=0.05,  # micro-billing for each healing
    )

    # Optional: local monetization log
    try:
        recovery_pct = result.get("recovery_pct", 0.0)
        success = result.get("status", "") == "success"
        log_revenue(workflow, anomaly, recovery_pct, success)
    except Exception as e:
        print(f"[Simulate] ⚠️ Local log skipped: {e}")

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
    """Start continuous background simulation"""
    print("🚀 Continuous simulation started.")
    return sim.start()

@app.post("/sim/stop")
def stop_simulation():
    """Stop continuous simulation"""
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
                df = df.dropna(subset=["anomaly"])
                anomaly_mix = df["anomaly"].value_counts().to_dict()
    except Exception as e:
        print(f"[Metrics Summary] ⚠️ Failed to parse anomaly mix: {e}")
    clean_summary["anomaly_mix"] = anomaly_mix

    # 🧠 Add last action
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            clean_summary["last_action"] = str(df["action"].iloc[-1]) if "action" in df.columns else "N/A"
    except Exception:
        clean_summary["last_action"] = "N/A"
    return clean_summary

# ============================================================
# 🔁 FlowXO Webhook Integration (Updated with Logging)
# ============================================================
@app.post("/integrations/flowxo/webhook")
async def flowxo_trigger(req: Request):
    """
    Triggered by FlowXO to execute healing externally.
    Example:
    {
        "workflow_id": "order_processing",
        "anomaly": "queue_pressure",
        "user_id": "client_001"
    }
    """
    data = await req.json()
    workflow_id = data.get("workflow_id", "unknown_workflow")
    anomaly = data.get("anomaly", "unknown_anomaly")
    user_id = data.get("user_id", "demo_client")

    # ✅ Log FlowXO event
    metrics_logger.log_flowxo_event(workflow_id, anomaly, user_id)

    # ✅ Execute healing logic
    result = executor.heal(workflow_id, anomaly)
    billing = bill_healing_event(user_id, anomaly, cost=0.05)

    # ✅ Print for debug clarity
    print(f"📂 [FlowXO] Logged → {metrics_logger.flowxo_log_path.resolve()}")

    return {
        "workflow": workflow_id,
        "anomaly": anomaly,
        "status": result.get("status"),
        "recovery_pct": result.get("recovery_pct"),
        "reward": result.get("reward"),
        "billing": billing,
    }

# ============================================================
# 🚀 Startup Message
# ============================================================
@app.on_event("startup")
def startup_event():
    print("\n🚀 IBM Workflow Healing Agent (Prototype-to-Profit Edition) started successfully!")
    print(f"   ▪ App: {settings.APP_NAME}")
    print(f"   ▪ FlowXO log path: {metrics_logger.flowxo_log_path.resolve()}")
    if use_watsonx:
        print("   ▪ Mode: IBM Watsonx.ai Cloud Reasoning 🧠")
    elif use_groq:
        print("   ▪ Mode: Groq Local Llama Inference ⚡")
    else:
        print("   ▪ Mode: Offline Fallback (Static Policies)")
    print(f"   ▪ Paywalls.ai Integrated: {use_paywalls}")
    print(f"   ▪ Loaded Policies: {list(policies.POLICY_MAP.keys())}\n")

# ============================================================
# 💰 Local Monetization Log (Backup)
# ============================================================
PAYWALL_LOG = "data/healing_revenue.log"
os.makedirs("data", exist_ok=True)

def log_revenue(workflow: str, anomaly: str, recovery_pct: float, success: bool):
    """
    Backup: simulate local monetization for each healing event.
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_price = 0.05
        multiplier = 1 + (recovery_pct / 100)
        cost = round(base_price * multiplier, 4)
        status = "success" if success else "partial"
        log_line = f"{timestamp} | {workflow} | {anomaly} | ${cost:.4f} | {status}\n"

        with open(PAYWALL_LOG, "a", encoding="utf-8") as f:
            f.write(log_line)
            f.flush()

        print(f"[Paywalls.ai] 💰 Logged ${cost:.4f} for {workflow}:{anomaly}")
    except Exception as e:
        print(f"[Paywalls.ai] ⚠️ Monetization log failed: {e}")
