"""
config.py
Loads environment variables and exposes configuration to all services.
"""
import os
from dotenv import load_dotenv

# Load .env file if present (local development)
load_dotenv()


def get_required(key: str) -> str:
    """Return an environment variable or raise a clear error if missing."""
    value = os.environ.get(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Check your .env file."
        )
    return value


def get_optional(key: str, default: str = "") -> str:
    """Return an environment variable or a default if not set."""
    return os.environ.get(key, default)


# ── Required ──────────────────────────────────────────────────────────────────
KNOWLEDGE_BASE_ID: str = get_required("KNOWLEDGE_BASE_ID")
MODEL_ID: str = get_optional("MODEL_ID", "anthropic.claude-sonnet-4-5")
AWS_REGION: str = get_optional("AWS_REGION", "us-east-1")

# ── Guardrail (optional until Part 3 of the lab) ──────────────────────────────
GUARDRAIL_ID: str = get_optional("GUARDRAIL_ID", "")
GUARDRAIL_VERSION: str = get_optional("GUARDRAIL_VERSION", "1")

# ── Agentic loop ──────────────────────────────────────────────────────────────
MAX_ITERATIONS: int = int(get_optional("MAX_ITERATIONS", "10"))
