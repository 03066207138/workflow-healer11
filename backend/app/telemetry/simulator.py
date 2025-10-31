# ============================================================
# 🧠 Workflow Healing Simulator (Prototype-to-Profit Edition)
# Integrates: IBM Workflow Healing + Paywalls.ai + FlowXO
# ============================================================

import threading
import time
import random
import traceback
import os
from datetime import datetime

from ..healing.executor import HealingExecutor
from ..healing import policies
from ..integrations.paywalls_client import bill_healing_event
from ..utils.paywall_logger import log_revenue  # ✅ Local dashboard logger
from ..integrations.flowxo_notifier import notify_flowxo  # ✅ FlowXO integration

# ============================================================
# ⚙️ Healing Simulator Class
# ============================================================

class HealingSimulator:
    def __init__(self):
        self.executor = HealingExecutor()
        self.running = False
        self.thread = None
        self.user_id = os.getenv("PAYWALLS_USER_ID", "demo_client")
        self.cost_per_heal = float(os.getenv("HEAL_COST", "0.05"))  # $0.05 default

    # ============================================================
    # 🔁 Continuous Simulation Loop
    # ============================================================
    def _run_loop(self):
        """Continuously simulate healing events until stopped."""
        workflows = ["invoice_processing", "order_processing", "customer_support"]
        print("[Simulator] 🔁 Healing loop started (Paywalls.ai monetized).")

        while self.running:
            try:
                workflow = random.choice(workflows)
                anomaly = random.choice(list(policies.POLICY_MAP.keys()))
                print(f"[Simulator] 🧩 Healing {workflow} anomaly={anomaly}")

                # 🧠 Step 1: Run healing process
                result = self.executor.heal(workflow, anomaly)

                # 💰 Step 2: Monetize each healing event
                billing = bill_healing_event(
                    user_id=self.user_id,
                    heal_type=anomaly,
                    cost=self.cost_per_heal,
                )

                # 🧾 Step 3: Log result summary locally
                recovery_pct = result.get("recovery_pct", 0.0)
                status = result.get("status", "unknown")
                reward = result.get("reward", 0.0)

                log_revenue(workflow, anomaly, recovery_pct, status)

                print(
                    f"[Simulator] ✅ Healed: {workflow} | Anomaly: {anomaly} | "
                    f"Recovery: {recovery_pct}% | Reward: {reward} | "
                    f"Billed: ${self.cost_per_heal:.2f}"
                )

                # 📘 Step 4: Append to revenue log file
                with open("data/healing_revenue.log", "a", encoding="utf-8") as logf:
                    logf.write(
                        f"{datetime.utcnow().isoformat()} | {workflow} | {anomaly} | "
                        f"${self.cost_per_heal:.2f} | {billing.get('status', 'ok')}\n"
                    )

                # 🌐 Step 5: Notify FlowXO webhook for real-time automation
                try:
                    payload = {
                        "workflow": workflow,
                        "anomaly": anomaly,
                        "status": result.get("status", "healed"),
                        "recovery_pct": float(recovery_pct),
                        "reward": float(reward),
                        "billing_cost": self.cost_per_heal,
                        "billing_client": self.user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    notify_flowxo(payload)
                    print(f"[Simulator → FlowXO] ✅ Sent healing update: {payload}")
                except Exception as fx:
                    print(f"[Simulator → FlowXO] ⚠️ Failed to send update: {fx}")

                # ⏱️ Step 6: Wait before next cycle
                time.sleep(random.randint(5, 10))

            except Exception as e:
                print("[Simulator] ❌ Error during healing loop:", e)
                traceback.print_exc()
                time.sleep(3)

        print("[Simulator] 🧊 Healing simulation stopped.")

    # ============================================================
    # ▶️ Start Simulation
    # ============================================================
    def start(self):
        """Start continuous background healing simulation."""
        if self.running:
            print("[Simulator] ⚠️ Already running.")
            return {"status": "already_running"}

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("[Simulator] 🚀 Healing simulation started (Prototype-to-Profit).")
        return {"status": "started", "mode": "continuous", "monetized": True}

    # ============================================================
    # ⏹️ Stop Simulation
    # ============================================================
    def stop(self):
        """Stop continuous simulation."""
        if not self.running:
            return {"status": "not_running"}
        self.running = False
        print("[Simulator] 🛑 Healing simulation stopped.")
        return {"status": "stopped"}


# ============================================================
# 🧩 Singleton Instance
# ============================================================
sim = HealingSimulator()
