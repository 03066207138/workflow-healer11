# ============================================================
# 🌐 IBM Workflow Healing Agent — Prototype-to-Profit Edition v4.2
# Real-Time Healing + Paywalls.ai Monetization + FlowXO Integration
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
    from .integrations.flowxo_notifier import notify_flowxo
except ImportError:
    # Fallback for local execution
    from settings import settings
    from healing.executor import HealingExecutor
    from healing import policies
    from telemetry.simulator import sim
    from utils.metrics_logger import MetricsLogger
    from integrations.paywalls_client import bill_healing_event
    from integrations.flowxo_notifier import notify_flowxo


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
# 🚀 FastAPI App Initialization
# ============================================================
app = FastAPI(
    title="IBM Workflow Healing Agent — Prototype-to-Profit Edition",
    version="4.2",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





# ============================================================
# 🔗 Include FlowXO Webhook Router
# ============================================================
from app.integrations import flowxo_client
app.include_router(flowxo_client.router, prefix="/integrations", tags=["FlowXO"])





# ============================================================
# 🩺 Health Check
# ============================================================
@app.get("/health")
def health():
    """Check service readiness."""
    return {
        "status": "ok",
        "watsonx_ready": use_watsonx,
        "groq_ready": use_groq,
        "paywalls_ready": use_paywalls,
        "flowxo_ready": True,  # ✅ Added — confirm webhook integration
        "mode": (
            "Watsonx.ai"
            if use_watsonx
            else ("Groq Local AI" if use_groq else "Offline Simulation")
        ),
    }

# ============================================================
# 📜 Healing Logs
# ============================================================
@app.get("/healing/logs")
def get_healing_logs(n: int = 50):
    """Fetch recent healing logs."""
    log_path = settings.HEALING_LOG_PATH
    if not os.path.exists(log_path):
        return {"logs": []}

    try:
        with open(log_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return {"logs": lines[-n:][::-1]}
    except Exception as e:
        return {"logs": [f"⚠️ Error reading logs: {e}"]}

# ============================================================
# 📊 Metrics Download
# ============================================================
@app.get("/metrics/download")
def download_metrics():
    if not os.path.exists(settings.METRICS_LOG_PATH):
        raise HTTPException(status_code=404, detail="No metrics file found.")
    return FileResponse(
        settings.METRICS_LOG_PATH,
        media_type="text/csv",
        filename="metrics_log.csv",
    )

# ============================================================
# ⚡ Manual Healing Simulation (6s-limited)
# ============================================================
@app.post("/simulate")
def simulate(event: str = "workflow_delay"):
    """Simulate a single healing cycle, log metrics, monetize, and notify FlowXO."""

    # 🎯 Step 1: Pick workflow and anomaly
    workflow = random.choice(["invoice_processing", "order_processing", "customer_support"])
    anomaly = event if event in policies.POLICY_MAP else random.choice(list(policies.POLICY_MAP.keys()))

    # 🧠 Step 2: Perform healing
    result = executor.heal(workflow, anomaly)

    # 📊 Step 3: Log metrics (with 6s guard inside MetricsLogger)
    metrics_logger.log({
        "workflow": workflow,
        "anomaly": anomaly,
        "action": result.get("actions", ["none"])[0] if result.get("actions") else "none",
        "status": result.get("status", "unknown"),
        "latency_ms": random.randint(2000, 6000),
        "recovery_pct": result.get("recovery_pct", 0.0),
        "reward": result.get("reward", 0.0),
    })

    # 💰 Step 4: Monetize through Paywalls.ai (real or simulated)
    billing = bill_healing_event("demo_client", anomaly, cost=0.05)

    # 🔁 Step 5: Notify FlowXO webhook (if configured)
    try:
        from .integrations.flowxo_notifier import notify_flowxo
        notify_flowxo({
            "workflow": workflow,
            "anomaly": anomaly,
            "status": result.get("status"),
            "recovery_pct": result.get("recovery_pct"),
            "reward": result.get("reward"),
            "billing": billing,
        })
    except Exception as e:
        print(f"[FlowXO Notify] ⚠️ Failed to send update: {e}")

    # 🧾 Step 6: Return full response
    return {
        "workflow": workflow,
        "anomaly": anomaly,
        "status": result.get("status"),
        "recovery_pct": result.get("recovery_pct"),
        "reward": result.get("reward"),
        "engine": "Watsonx.ai" if use_watsonx else ("Groq Local" if use_groq else "Simulation"),
        "billing": billing,
    }

# ============================================================
# 🧪 Continuous Simulation Routes
# ============================================================
@app.post("/sim/start")
def start_simulation():
    print("🚀 Continuous simulation started.")
    return sim.start()

@app.post("/sim/stop")
def stop_simulation():
    print("🧊 Simulation stopped.")
    return sim.stop()

# ============================================================
# 📊 Metrics Summary for Dashboard
# ============================================================
@app.get("/metrics/summary")
def metrics_summary():
    """Summarized healing performance."""
    summary = metrics_logger.summary()
    clean = {}

    for k, v in summary.items():
        try:
            val = float(v)
            if math.isnan(val) or math.isinf(val):
                val = 0.0
            clean[k] = round(val, 2)
        except Exception:
            clean[k] = v

    # 🧩 Anomaly mix
    anomaly_mix = {}
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            if not df.empty and "anomaly" in df.columns:
                anomaly_mix = df["anomaly"].value_counts().to_dict()
    except Exception as e:
        print(f"[Metrics Summary] ⚠️ Failed anomaly mix: {e}")

    clean["anomaly_mix"] = anomaly_mix
    return clean

# ============================================================
# 🔁 FlowXO Webhook Integration
# ============================================================
@app.post("/integrations/flowxo/webhook")
async def flowxo_webhook(req: Request):
    """Triggered by FlowXO for live healing."""
    try:
        data = await req.json()
        workflow = data.get("workflow_id", "unknown_workflow")
        anomaly = data.get("anomaly", "unknown_anomaly")
        user = data.get("user_id", "flowxo_user")

        metrics_logger.log_flowxo_event(workflow, anomaly, user)
        result = executor.heal(workflow, anomaly)
        billing = bill_healing_event(user, anomaly, cost=0.05)

        return JSONResponse({
            "workflow": workflow,
            "anomaly": anomaly,
            "status": result.get("status"),
            "recovery_pct": result.get("recovery_pct"),
            "reward": result.get("reward"),
            "billing": billing,
        })
    except Exception as e:
        print(f"[FlowXO] ❌ Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# 💹 Monetization Data
# ============================================================
@app.get("/metrics/revenue")
def revenue_data():
    """Fetch revenue logs for dashboard."""
    data = []
    total_revenue = 0.0
    total_heals = 0

    if os.path.exists(PAYWALL_LOG):
        with open(PAYWALL_LOG, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4:
                    ts, user, heal_type, cost, *_ = parts
                    try:
                        val = float(cost.replace("$", "").strip())
                    except:
                        val = 0.0
                    total_revenue += val
                    total_heals += 1
                    data.append({
                        "Timestamp": ts,
                        "User": user,
                        "Healing Type": heal_type,
                        "Cost ($)": val
                    })

    return {
        "total_revenue": round(total_revenue, 4),
        "total_heals": total_heals,
        "logs": data,
    }

# ============================================================
# 🚀 Startup Log
# ============================================================
@app.on_event("startup")
def startup():
    print("\n🚀 IBM Workflow Healing Agent (v4.2) started successfully!")
    print(f"▪ App: {settings.APP_NAME}")
    print(f"▪ Mode: {'Watsonx.ai' if use_watsonx else ('Groq Local' if use_groq else 'Offline')}")
    print(f"▪ Paywalls.ai Enabled: {use_paywalls}")
    print(f"▪ Metrics Path: {metrics_logger.path.resolve()}")
    print(f"▪ FlowXO Log Path: {metrics_logger.flowxo_log_path.resolve()}")
    print(f"▪ Loaded Policies: {list(policies.POLICY_MAP.keys())}\n")
