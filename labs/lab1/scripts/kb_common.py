"""
Lab 1: Shared Knowledge Base helper
Anthropic Models on AWS Bedrock

Finds the shared Knowledge Base so nobody has to copy an ID by hand.

Order of lookup:
1. --kb-id on the command line (the ID your instructor shared in chat)
2. The Knowledge Base named "lab1-shared-kb" in this account (found by name)
3. KNOWLEDGE_BASE_ID in the environment or in lab1/.env

When an ID is found it is saved to lab1/.env and lab3/.env, so Lab 3
picks it up without any editing.
"""

import os
import sys
from pathlib import Path

import boto3
from dotenv import load_dotenv

REGION = "us-east-1"
KB_NAME = os.getenv("KB_NAME", "lab1-shared-kb")

LAB1_DIR = Path(__file__).resolve().parent.parent
LAB3_DIR = LAB1_DIR.parent / "lab3"
ENV_FILE = LAB1_DIR / ".env"


def find_kb_by_name(name: str = KB_NAME):
    """Return the ID of the single Knowledge Base with this name, or None."""
    client = boto3.client("bedrock-agent", region_name=REGION)
    matches = []
    for page in client.get_paginator("list_knowledge_bases").paginate():
        matches += [
            kb["knowledgeBaseId"]
            for kb in page.get("knowledgeBaseSummaries", [])
            if kb["name"] == name
        ]
    if len(matches) > 1:
        print(f"\n  More than one Knowledge Base is named '{name}'.")
        print("  Ask your instructor which ID to use, then run this script with --kb-id.\n")
        sys.exit(1)
    return matches[0] if matches else None


def _write_env_value(path: Path, key: str, value: str) -> None:
    """Set KEY=value in a .env file, keeping every other line."""
    lines = path.read_text().splitlines() if path.exists() else []
    out, found = [], False
    for line in lines:
        if line.startswith(f"{key}="):
            out.append(f"{key}={value}")
            found = True
        else:
            out.append(line)
    if not found:
        out.append(f"{key}={value}")
    path.write_text("\n".join(out) + "\n")


def save_kb_id(kb_id: str) -> None:
    """Save the ID to lab1/.env, and to lab3/.env when Lab 3 is present."""
    _write_env_value(ENV_FILE, "KNOWLEDGE_BASE_ID", kb_id)
    if LAB3_DIR.is_dir():
        lab3_env = LAB3_DIR / ".env"
        if not lab3_env.exists() and (LAB3_DIR / ".env.template").exists():
            lab3_env.write_text((LAB3_DIR / ".env.template").read_text())
        _write_env_value(lab3_env, "KNOWLEDGE_BASE_ID", kb_id)


def get_kb_id(cli_value: str = None) -> str:
    """Resolve the Knowledge Base ID using the lookup order above."""
    kb_id = (cli_value or "").strip()
    source = "--kb-id"

    if not kb_id:
        try:
            kb_id = find_kb_by_name() or ""
            source = f"found by name '{KB_NAME}'"
        except SystemExit:
            raise
        except Exception:
            kb_id = ""  # no permission to list, or no network: fall back below

    if not kb_id:
        load_dotenv(ENV_FILE)
        kb_id = os.getenv("KNOWLEDGE_BASE_ID", "").strip()
        source = "lab1/.env"

    if not kb_id or kb_id.lower().startswith("your-"):
        print("\nERROR: No Knowledge Base found.")
        print("Ask your instructor for the Knowledge Base ID, then run:")
        print("  python scripts/verify_knowledge_base.py --kb-id <the ID>\n")
        sys.exit(1)

    save_kb_id(kb_id)  # also carries an ID from lab1/.env over to lab3/.env
    return kb_id
