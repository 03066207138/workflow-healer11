# ============================================================
# 🌐 FlowXO Notifier — Sends Healing Results to FlowXO Webhook
# ============================================================

import os
import json
import requests

# 👇 Load webhook from environment (.env) or fallback URL
FLOWXO_HOOK_URL = os.getenv("FLOWXO_HOOK_URL", "https://flowxo.com/hooks/a/9rxmp73b")


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
        # ✅ Convert payload to JSON string (for debug readability)
        payload_str = json.dumps(data, indent=2)
        print(f"[FlowXO Notify] 📤 Sending payload:\n{payload_str}")

        response = requests.post(
            FLOWXO_HOOK_URL,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=8,
        )

        print(f"[FlowXO Notify] ✅ Status: {response.status_code}")
        print(f"[FlowXO Notify] 🔁 Response: {response.text[:120]}")

        # ✅ Return structured response for debugging
        return {
            "status_code": response.status_code,
            "response_text": response.text,
            "payload_sent": data,
        }

    except Exception as e:
        print(f"[FlowXO Notify] ❌ Error while notifying FlowXO: {e}")
        return {"error": str(e), "payload_attempted": data}
