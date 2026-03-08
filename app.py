"""
SagaBreaker — Agentic Novel Writer
Entry point: python app.py
"""
from dotenv import load_dotenv
load_dotenv()

from src.orchestrator import run

if __name__ == "__main__":
    run()
