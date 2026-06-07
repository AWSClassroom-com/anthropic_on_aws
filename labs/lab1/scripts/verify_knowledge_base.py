"""
Lab 1: Knowledge Base Verification Script
Anthropic Models on AWS Bedrock
 
Confirms the Knowledge Base is active and documents are synced.
Reads the Knowledge Base ID from .env
 
Run: python scripts/verify_knowledge_base.py
"""
 
import boto3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
 
REGION = "us-east-1"
ENV_FILE = Path(__file__).parent.parent / ".env"
 
 
def get_kb_id() -> str:
    """Read Knowledge Base ID from .env file."""
    load_dotenv(ENV_FILE)
    kb_id = os.getenv("KNOWLEDGE_BASE_ID", "").strip()
    if not kb_id:
        print("\nERROR: KNOWLEDGE_BASE_ID not found in .env")
        print("Add your Knowledge Base ID to .env -- check the course chat for the ID your instructor shared.\n")
        sys.exit(1)
    return kb_id
 
 
def main():
    print()
    print("=" * 55)
    print("  Lab 1: Knowledge Base Verification")
    print("  Anthropic Models on AWS Bedrock")
    print("=" * 55)
    print()
 
    kb_id = get_kb_id()
    client = boto3.client("bedrock-agent", region_name=REGION)
 
    # Build bucket path dynamically from account ID
    try:
        sts = boto3.client("sts", region_name=REGION)
        account_id = sts.get_caller_identity()["Account"]
        bucket_path = f"s3://bedrock-training-{account_id}/lab1-documents/"
    except Exception:
        bucket_path = "s3://bedrock-training-[your-account-id]/lab1-documents/"
 
    try:
        # Check Knowledge Base status
        response = client.get_knowledge_base(knowledgeBaseId=kb_id)
        kb = response["knowledgeBase"]
        status = kb["status"]
        name = kb["name"]
 
        print(f"  Knowledge Base ID:   {kb_id}")
        print(f"  Name:                {name}")
        print(f"  Status:              {status}")
 
        if status != "ACTIVE":
            print()
            print(f"  WARNING: Status is '{status}', expected 'ACTIVE'.")
            if status == "CREATING":
                print("  Still provisioning -- wait a few more minutes and retry.")
            elif status == "FAILED":
                print("  Creation failed. Ask your instructor for help.")
            print()
            sys.exit(1)
 
        # Check data sources
        ds_response = client.list_data_sources(knowledgeBaseId=kb_id)
        data_sources = ds_response.get("dataSourceSummaries", [])
 
        if not data_sources:
            print()
            print("  WARNING: No data sources found.")
            print("  Ask your instructor -- the shared Knowledge Base may need to be reconfigured.\n")
            sys.exit(1)
 
        ds = data_sources[0]
        ds_name = ds["name"]
        ds_status = ds["status"]
        ds_id = ds["dataSourceId"]
 
        print(f"  Data source:         {ds_name}")
        print(f"  Sync status:         {ds_status}")
 
        # Check ingestion jobs -- use get_ingestion_job for full statistics
        jobs_response = client.list_ingestion_jobs(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id
        )
        jobs = jobs_response.get("ingestionJobSummaries", [])
 
        if jobs:
            latest_job = jobs[0]
            job_status = latest_job.get("status", "UNKNOWN")
            stats = latest_job.get("statistics", {})
            docs_indexed = (
                stats.get("numberOfNewDocumentsIndexed", 0) +
                stats.get("numberOfModifiedDocumentsIndexed", 0)
            )
            docs_failed = stats.get("numberOfDocumentsFailed", 0)
 
            print(f"  Documents synced:    {docs_indexed}")
 
            if docs_failed > 0:
                print(f"  Documents failed:    {docs_failed}")
                print()
                print("  WARNING: Some documents failed to sync.")
                print("  Ask your instructor to check the S3 bucket contents.\n")
 
            if job_status == "IN_PROGRESS":
                print()
                print("  Sync still in progress -- wait a few minutes and retry.\n")
                sys.exit(1)
 
            if docs_indexed == 0:
                print()
                print("  WARNING: No documents indexed.")
                print(f"  Verify documents exist at {bucket_path}")
                print("  Ask your instructor if the S3 bucket is empty.\n")
                sys.exit(1)
        else:
            print(f"  Documents synced:    0 (no ingestion job found)")
 
        print()
        print("=" * 55)
        print("  Knowledge Base is active and ready.")
        print("=" * 55)
        print()
 
    except client.exceptions.ResourceNotFoundException:
        print(f"\n  ERROR: Knowledge Base '{kb_id}' not found.")
        print("  Check the Knowledge Base ID in your .env file matches the ID your instructor shared.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR: {type(e).__name__}: {e}\n")
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()