import sys, os
from fastapi import APIRouter, Request

router = APIRouter()
executor = HealingExecutor()

@router.post("/flowxo/webhook")
async def flowxo_trigger(req: Request):
    """
    Webhook called by FlowXO when an anomaly occurs.
    Example payload:
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

    result = executor.heal(workflow_id, anomaly)

    billing_info = bill_healing_event(user_id, anomaly, cost=0.05)

    return {
        "workflow": workflow_id,
        "anomaly": anomaly,
        "healing_status": result.get("status"),
        "recovery_pct": result.get("recovery_pct"),
        "reward": result.get("reward"),
        "billing": billing_info
    }
