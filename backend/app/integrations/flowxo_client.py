# ============================================================
# 🌐 FlowXO Webhook Integration
# ============================================================

import os, sys
from fastapi import APIRouter, Request

# --- Safe Import Path Handling for Render & Local Run ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

try:
    from app.healing.executor import HealingExecutor
    from app.integrations.paywalls_client import bill_healing_event
except ModuleNotFoundError:
    # fallback if 'app' package isn't recognized (Render case)
    from healing.executor import HealingExecutor
    from integrations.paywalls_client import bill_healing_event

# ============================================================
# ⚙️ Initialize Router and Executor
# ============================================================
router = APIRouter()
executor = HealingExecutor()

# ============================================================
# 🚀 Webhook Endpoint
# ============================================================
@router.post("/flowxo/webhook")
async def flowxo_trigger(req: Request):
    """
    🌐 Triggered by FlowXO webhook to heal workflows automatically.
    Example payload:
    {
        "workflow_id": "order_processing",
        "anomaly": "queue_pressure",
        "user_id": "client_001"
    }
    """
    try:
        data = await req.json()
    except Exception:
        return {"error": "Invalid JSON payload"}

    workflow_id = data.get("workflow_id", "unknown_workflow")
    anomaly = data.get("anomaly", "unknown_anomaly")
    user_id = data.get("user_id", "demo_client")

    # 🧠 Execute healing logic
    try:
        result = executor.heal(workflow_id, anomaly)
    except Exception as e:
        return {"error": f"Healing failed: {e}"}

    # 💰 Monetize via Paywalls.ai
    try:
        billing_info = bill_healing_event(user_id, anomaly, cost=0.05)
    except Exception as e:
        billing_info = {"error": str(e)}

    return {
        "workflow": workflow_id,
        "anomaly": anomaly,
        "healing_status": result.get("status"),
        "recovery_pct": result.get("recovery_pct"),
        "reward": result.get("reward"),
        "billing": billing_info
    }
