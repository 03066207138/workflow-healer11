# ============================================================
# 💰 Paywalls.ai Client — Prototype-to-Profit Edition
# ============================================================
# This file bridges your AI workflow healing backend with Paywalls.ai monetization.
# It supports both local (simulated) billing and real API integration when a key is provided.

import os
import json
import requests
from datetime import datetime

# Local fallback log file
os.makedirs("data", exist_ok=True)
LOG_FILE = "data/healing_revenue.log"


def bill_healing_event(user_id: str, heal_type: str, cost: float = 0.05):
    """
    Simulate or perform a Paywalls.ai billing transaction.
    Called after each healing cycle to record micro-revenue.
    
    Args:
        user_id (str): Unique user identifier (e.g. from FlowXO or app).
        heal_type (str): Type of healing anomaly handled.
        cost (float): Billing amount (default $0.05).
    
    Returns:
        dict: Billing record or API response.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    paywalls_key = os.getenv("PAYWALLS_KEY")

    # Case 1: No Paywalls key → Local Simulation
    if not paywalls_key:
        try:
            log_line = f"{timestamp} | {user_id} | {heal_type} | ${cost:.4f} | success\n"
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_line)
            print(f"[Paywalls.ai] 💰 Simulated billing for {heal_type} (${cost:.4f})")
            return {
                "timestamp": timestamp,
                "user": user_id,
                "heal_type": heal_type,
                "amount": cost,
                "currency": "USD",
                "status": "simulated",
                "mode": "local",
            }
        except Exception as e:
            print(f"[Paywalls.ai] ⚠️ Logging error: {e}")
            return {"status": "failed", "error": str(e)}

    # Case 2: Real API billing (future-ready)
    try:
        payload = {
            "user_id": user_id,
            "amount": cost,
            "currency": "USD",
            "description": f"Healing service for {heal_type}",
        }

        response = requests.post(
            "https://api.paywalls.ai/v1/charge",
            headers={
                "Authorization": f"Bearer {paywalls_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            print(f"[Paywalls.ai] ✅ Billed ${cost:.4f} for {heal_type}")
            return {"status": "success", "response": data}

        else:
            print(f"[Paywalls.ai] ⚠️ API charge failed ({response.status_code}), fallback logged.")
            _fallback_log(user_id, heal_type, cost)
            return {"status": "fallback_logged", "code": response.status_code}

    except Exception as e:
        print(f"[Paywalls.ai] ❌ Exception during billing: {e}")
        _fallback_log(user_id, heal_type, cost)
        return {"status": "fallback_logged", "error": str(e)}


def _fallback_log(user_id: str, heal_type: str, cost: float):
    """Write fallback billing record if API call fails."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"{timestamp} | {user_id} | {heal_type} | ${cost:.4f} | fallback\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as err:
        print(f"[Paywalls.ai] ⚠️ Fallback log error: {err}")


def read_billing_history(limit: int = 100):
    """Read recent billing events from local log."""
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        return [line.strip() for line in lines if line.strip()]
    except Exception as e:
        print(f"[Paywalls.ai] ⚠️ Read error: {e}")
        return []
