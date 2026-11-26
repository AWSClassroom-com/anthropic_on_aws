"""
Lab 1: Knowledge Base Verification Script
Anthropic Models on AWS Bedrock

Finds the shared Knowledge Base, confirms it is active and its documents are
synced, and saves its ID for the rest of Lab 1 and for Lab 3.
Nothing to edit.

Run:  python scripts/verify_knowledge_base.py
      python scripts/verify_knowledge_base.py --kb-id ABCDEF1234
"""

import argparse
import sys

import boto3

from kb_common import REGION, get_kb_id

EXPECTED_DOCUMENTS = 5


def main():
    parser = argparse.ArgumentParser(description="Verify the shared Knowledge Base")
    parser.add_argument("--kb-id", help="Knowledge Base ID, if you were given one")
    args = parser.parse_args()

    print()
    print("=" * 55)
    print("  Lab 1: Knowledge Base Verification")
    print("  Anthropic Models on AWS Bedrock")
    print("=" * 55)
    print()

    kb_id = get_kb_id(args.kb_id)
    client = boto3.client("bedrock-agent", region_name=REGION)
    checks = []

    try:
        kb = client.get_knowledge_base(knowledgeBaseId=kb_id)["knowledgeBase"]
        print(f"  Knowledge Base ID:   {kb_id}")
        print(f"  Name:                {kb['name']}")
        print(f"  Status:              {kb['status']}")
        checks.append(("Knowledge Base is ACTIVE", kb["status"] == "ACTIVE"))

        sources = client.list_data_sources(knowledgeBaseId=kb_id).get("dataSourceSummaries", [])
        checks.append(("Knowledge Base has a data source", bool(sources)))

        scanned, failed, job_status = 0, 0, "NONE"
        if sources:
            ds = sources[0]
            print(f"  Data source:         {ds['name']}")
            # Sort newest first: without a sort order the API returns jobs in
            # no particular order, so jobs[0] is not always the latest.
            jobs = client.list_ingestion_jobs(
                knowledgeBaseId=kb_id,
                dataSourceId=ds["dataSourceId"],
                sortBy={"attribute": "STARTED_AT", "order": "DESCENDING"},
            ).get("ingestionJobSummaries", [])
            if jobs:
                job_status = jobs[0].get("status", "UNKNOWN")
                stats = jobs[0].get("statistics", {})
                scanned = stats.get("numberOfDocumentsScanned", 0)
                failed = stats.get("numberOfDocumentsFailed", 0)
            print(f"  Sync status:         {job_status}")
            print(f"  Documents synced:    {max(scanned - failed, 0)}")

        checks.append(("Last sync completed", job_status == "COMPLETE"))
        checks.append((
            f"All {EXPECTED_DOCUMENTS} documents synced with none failed",
            scanned - failed >= EXPECTED_DOCUMENTS and failed == 0,
        ))

    except client.exceptions.ResourceNotFoundException:
        print(f"\n  ERROR: Knowledge Base '{kb_id}' not found.")
        print("  Ask your instructor to confirm the ID.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n  ERROR: {type(e).__name__}: {e}\n")
        sys.exit(1)

    print()
    for label, ok in checks:
        print(f"  {'✅' if ok else '❌'} {label}")
    print()

    passed = sum(ok for _, ok in checks)
    if passed == len(checks):
        print(f"All {len(checks)} checks passed! ✅")
        print("Knowledge Base ID saved for Lab 1 and Lab 3.")
        print()
        return
    print(f"{passed} / {len(checks)} checks passed. Tell your instructor.")
    print()
    sys.exit(1)


if __name__ == "__main__":
    main()
