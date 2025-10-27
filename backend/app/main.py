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
from .integrations.paywalls_client import bill_healing_event

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
    version="3.3"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 🩺 Health Check
# ============================================================
@app.get("/health")
def health():
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
# 📜 Healing Logs
# ============================================================
@app.get("/healing/logs")
def get_healing_logs(n: int = 50):
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
# 📊 Download Metrics CSV
# ============================================================
@app.get("/metrics/download")
def metrics_download():
    if not os.path.exists(settings.METRICS_LOG_PATH):
        raise HTTPException(status_code=404, detail="No metrics file found.")
    return FileResponse(settings.METRICS_LOG_PATH, media_type="text/csv", filename="metrics_log.csv")

# ============================================================
# ⚡ Manual Simulation
# ============================================================
@app.post("/simulate")
def simulate(event: str = "workflow_delay"):
    workflow = random.choice(["invoice_processing", "order_processing", "customer_support"])
    anomaly = event if event in policies.POLICY_MAP else random.choice(list(policies.POLICY_MAP.keys()))
    result = executor.heal(workflow, anomaly)

    billing_info = bill_healing_event("demo_client", anomaly, 0.05)

    # Log to metrics file
    try:
        recovery = result.get("recovery_pct", 0.0)
        reward = result.get("reward", 0.0)
        metrics_logger.log_metric(
            workflow=workflow,
            anomaly=anomaly,
            recovery_pct=recovery,
            reward=reward,
            status=result.get("status", "success"),
        )
    except Exception as e:
        print(f"[Simulate] ⚠️ Metrics logging skipped: {e}")

    return {
        "workflow": workflow,
        "anomaly": anomaly,
        "status": result.get("status"),
        "recovery_pct": result.get("recovery_pct"),
        "reward": result.get("reward"),
        "engine": "Watsonx.ai" if use_watsonx else ("Groq Local" if use_groq else "Offline"),
        "billing": billing_info,
    }

# ============================================================
# 🧪 Continuous Simulation
# ============================================================
@app.post("/sim/start")
def start_simulation():
    return sim.start()

@app.post("/sim/stop")
def stop_simulation():
    return sim.stop()

# ============================================================
# 📊 Metrics Summary
# ============================================================
@app.get("/metrics/summary")
def metrics_summary():
    summary = metrics_logger.summary()
    clean = {}
    for k, v in summary.items():
        try:
            val = float(v)
            clean[k] = round(val, 2) if not math.isnan(val) and not math.isinf(val) else 0.0
        except:
            clean[k] = v

    anomaly_mix = {}
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            if not df.empty and "anomaly" in df.columns:
                anomaly_mix = df["anomaly"].value_counts().to_dict()
        clean["healings"] = len(df)
    except Exception as e:
        print(f"[Metrics Summary] ⚠️ Failed to parse anomaly mix: {e}")
    clean["anomaly_mix"] = anomaly_mix
    return clean

# ============================================================
# 💹 Revenue and Heal Count — from metrics_log.csv
# ============================================================
@app.get("/metrics/revenue")
def get_revenue_data():
    """Compute revenue and total heals directly from metrics_log.csv"""
    if not os.path.exists(settings.METRICS_LOG_PATH):
        return {"total_revenue": 0.0, "total_heals": 0, "logs": []}

    try:
        df = pd.read_csv(settings.METRICS_LOG_PATH)
        if df.empty:
            return {"total_revenue": 0.0, "total_heals": 0, "logs": []}

        df["Cost ($)"] = 0.05 * (1 + df["recovery_pct"].fillna(0) / 100)
        total_revenue = df["Cost ($)"].sum()
        total_heals = len(df)

        logs = df[["timestamp", "workflow", "anomaly", "Cost ($)"]].rename(
            columns={"timestamp": "Timestamp", "workflow": "Workflow", "anomaly": "Anomaly"}
        ).to_dict(orient="records")

        return {
            "total_revenue": round(total_revenue, 2),
            "total_heals": total_heals,
            "logs": logs,
        }
    except Exception as e:
        print(f"[Revenue] ⚠️ Error reading metrics_log.csv: {e}")
        return {"total_revenue": 0.0, "total_heals": 0, "logs": []}
