# ============================================================
# 🌐 IBM Workflow Healing Agent → Prototype-to-Profit Edition
# Hybrid: Watsonx.ai + Groq Local AI + Paywalls.ai + FlowXO
# ============================================================

from dotenv import load_dotenv
import os, math, random, pandas as pd
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

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
# 🧩 Internal Imports (Safe Relative / Absolute Handling)
# ============================================================
try:
    from app.settings import settings
    from app.healing.executor import HealingExecutor
    from app.healing import policies
    from app.telemetry.simulator import sim
    from app.utils.metrics_logger import MetricsLogger
    from app.integrations.paywalls_client import bill_healing_event
except ModuleNotFoundError:
    # fallback for flat structure (Render / local)
    from settings import settings
    from healing.executor import HealingExecutor
    from healing import policies
    from telemetry.simulator import sim
    from utils.metrics_logger import MetricsLogger
    from integrations.paywalls_client import bill_healing_event

# ============================================================
# ⚙️ Initialize Core Components
# ============================================================
metrics_logger = MetricsLogger(Path(settings.METRICS_LOG_PATH))
executor = HealingExecutor()

use_groq = bool(os.getenv("GROQ_API_KEY"))
use_watsonx = bool(os.getenv("WATSONX_API_KEY")) and bool(os.getenv("WATSONX_PROJECT_ID"))
use_paywalls = bool(os.getenv("PAYWALLS_KEY"))

# ============================================================
# 🚀 FastAPI App Setup
# ============================================================
app = FastAPI(
    title="IBM Workflow Healing Agent — Prototype-to-Profit Edition",
    version="3.0",
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
# 📊 Metrics Download
# ============================================================
@app.get("/metrics/download")
def metrics_download():
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
    workflow = random.choice(["invoice_processing", "order_processing", "customer_support"])
    anomaly = event if event in policies.POLICY_MAP else random.choice(list(policies.POLICY_MAP.keys()))
    result = executor.heal(workflow, anomaly)

    # 💰 Monetization
    billing_info = bill_healing_event(
        user_id="demo_client",
        heal_type=anomaly,
        cost=0.05,
    )

    # Local backup log
    try:
        recovery_pct = result.get("recovery_pct", 0.0)
        success = result.get("status", "") == "success"
        log_revenue(workflow, anomaly, recovery_pct, success)
    except Exception as e:
        print(f"[Simulate] ⚠️ Monetization log skipped: {e}")

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
# 🧪 Continuous Simulation
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
# 📊 Metrics Summary
# ============================================================
@app.get("/metrics/summary")
def metrics_summary():
    summary = metrics_logger.summary()
    clean_summary = {}
    for k, v in summary.items():
        try:
            val = float(v)
            clean_summary[k] = round(val, 2) if math.isfinite(val) else 0.0
        except Exception:
            clean_summary[k] = v

    # 🧩 Anomaly Distribution
    anomaly_mix = {}
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            if "anomaly" in df.columns and not df.empty:
                df = df.dropna(subset=["anomaly"])
                anomaly_mix = df["anomaly"].value_counts().to_dict()
    except Exception as e:
        print(f"[Metrics Summary] ⚠️ Failed anomaly mix: {e}")
    clean_summary["anomaly_mix"] = anomaly_mix

    # 🧠 Last Action
    try:
        if os.path.exists(settings.METRICS_LOG_PATH):
            df = pd.read_csv(settings.METRICS_LOG_PATH)
            clean_summary["last_action"] = str(df["action"].iloc[-1]) if "action" in df.columns else "N/A"
    except Exception:
        clean_summary["last_action"] = "N/A"
    return clean_summary

# ============================================================
# 🔁 FlowXO Webhook
# ============================================================
@app.post("/integrations/flowxo/webhook")
async def flowxo_trigger(req: Request):
    data = await req.json()
    workflow_id = data.get("workflow_id", "unknown_workflow")
    anomaly = data.get("anomaly", "unknown_anomaly")
    user_id = data.get("user_id", "demo_client")

    metrics_logger.log_flowxo_event(workflow_id, anomaly, user_id)
    result = executor.heal(workflow_id, anomaly)
    billing = bill_healing_event(user_id, anomaly, cost=0.05)

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
# 💰 Local Monetization Backup
# ============================================================
PAYWALL_LOG = "data/healing_revenue.log"
os.makedirs("data", exist_ok=True)

def log_revenue(workflow: str, anomaly: str, recovery_pct: float, success: bool):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        base_price = 0.05
        multiplier = 1 + (recovery_pct / 100)
        cost = round(base_price * multiplier, 4)
        status = "success" if success else "partial"
        with open(PAYWALL_LOG, "a", encoding="utf-8") as f:
            f.write(f"{timestamp} | {workflow} | {anomaly} | ${cost:.4f} | {status}\n")
        print(f"[Paywalls.ai] 💰 Logged ${cost:.4f} for {workflow}:{anomaly}")
    except Exception as e:
        print(f"[Paywalls.ai] ⚠️ Log failed: {e}")

# ============================================================
# 💹 Revenue Data Endpoint
# ============================================================
@app.get("/metrics/revenue")
def get_revenue_data():
    data, total_revenue, total_heals = [], 0.0, 0
    today_marker = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(PAYWALL_LOG):
        with open(PAYWALL_LOG, "r", encoding="utf-8") as f:
            for line in f:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4 and today_marker in parts[0]:
                    ts, workflow, anomaly, cost, *_ = parts
                    try:
                        val = float(cost.replace("$", ""))
                    except:
                        val = 0.0
                    total_revenue += val
                    total_heals += 1
                    data.append({
                        "Timestamp": ts,
                        "Workflow": workflow,
                        "Anomaly": anomaly,
                        "Cost ($)": val
                    })
    return {
        "total_revenue": round(total_revenue, 4),
        "total_heals": total_heals,
        "logs": data
    }

# ============================================================
# 🚀 Startup Log
# ============================================================
@app.on_event("startup")
def startup_event():
    print("\n🚀 IBM Workflow Healing Agent (Prototype-to-Profit Edition) started successfully!")
    print(f"   ▪ App: {settings.APP_NAME}")
    print(f"   ▪ FlowXO log path: {metrics_logger.flowxo_log_path.resolve()}")
    print(f"   ▪ Mode: {'Watsonx.ai' if use_watsonx else ('Groq Local' if use_groq else 'Offline Simulation')}")
    print(f"   ▪ Paywalls.ai Integrated: {use_paywalls}")
    print(f"   ▪ Loaded Policies: {list(policies.POLICY_MAP.keys())}\n")
