# ============================================================
# 🌐 FlowXO Notifier — Sends Healing Results to FlowXO Webhook
# ============================================================

import os
import requests

# 👇 Default FlowXO webhook (can also be set in .env)
FLOWXO_HOOK_URL = os.getenv("FLOWXO_HOOK_URL", "https://flowxo.com/hooks/b/7vy5v8yb")


def notify_flowxo(data: dict):
    """
    Send healing results to FlowXO webhook for real-time automation.

    Args:
        data (dict): JSON payload to send to FlowXO, e.g.
                     {"workflow": "order_processing", "status": "healed", "reward": 0.25}
    Returns:
        dict: Response status and details
    """
    try:
        response = requests.post(
            FLOWXO_HOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=8,
        )
        print(f"[FlowXO Notify] → Status {response.status_code}")
        return {
            "status": response.status_code,
            "response": response.text,
        }
    except Exception as e:
        print(f"[FlowXO Notify] ❌ Error: {e}")
        return {"error": str(e)}
