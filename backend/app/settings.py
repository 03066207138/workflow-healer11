# ✅ FIXED version
from pydantic_settings import BaseSettings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "IBM Workflow Healing Agent"
    DEBUG: bool = True

    # IBM Orchestrate config
    IBM_ORCH_BASE_URL: str = "https://api.ibm.com/orchestrate/v1"
    IBM_ORCH_API_KEY: str = ""
    IBM_ORCH_SLACK_SKILL: str = "/skills/postToSlack"

    # Local Groq config
    GROQ_API_KEY: str = ""  
    MODEL: str = "llama-3.1-70b-versatile"

    # ✅ Use Path objects (not strings)
    METRICS_LOG_PATH: Path = DATA_DIR / "metrics_log.csv"
    HEALING_LOG_PATH: Path = DATA_DIR / "healing_log.txt"
    WORKFLOWS_PATH: Path = DATA_DIR / "workflows.json"

    class Config:
        env_file = Path(__file__).resolve().parents[1] / ".env"

settings = Settings()
