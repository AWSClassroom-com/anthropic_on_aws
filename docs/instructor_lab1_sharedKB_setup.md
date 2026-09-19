# Instructor Pre-Setup Guide: Lab 1
## Anthropic Models on AWS Bedrock

**Complete these steps before students arrive. Allow 20 minutes.**

---

> ## ⚠️ REGION: us-east-1 (N. Virginia) ONLY
>
> Every script and instruction in Labs 1, 2, and 3 is hardcoded to **us-east-1**. Create the shared Knowledge Base in **us-east-1** and nowhere else. Before you click anything in the AWS Console below, check the region selector in the top-right corner and confirm it reads **US East (N. Virginia)**.
>
> If you create the Knowledge Base in a different region, students' scripts will not find it. `KNOWLEDGE_BASE_ID` alone is not enough. A Knowledge Base ID only resolves correctly when the client is also pointed at the same region it was created in.

---

## What You Are Setting Up

Before class you will create one shared Knowledge Base that all students use during Lab 1. Students receive the Knowledge Base ID from you and use it to run RAG queries. They do not create their own Knowledge Base.

You need to complete three things:

1. Create the Knowledge Base via the Bedrock console (using the correct, non-default option, see Step 1)
2. Create the data source and sync the S3 documents into it via the AWS CLI (the console's own data source creation is currently broken, see Step 2)
3. Share the Knowledge Base ID with students

---
## Step 0: Make sure 'attendee' users of your Instructor AWS account (the users you provide to students) cannot delete your shared KB and associated resources. Modify the GenAIPowerUser policy for attendees with:

{
    "Sid": "DenyKnowledgeBaseDelete",
    "Effect": "Deny",
    "Action": [
            "bedrock:DeleteKnowledgeBase",
            "bedrock:DeleteDataSource",
            "bedrock:DeleteKnowledgeBaseDocuments",
            "bedrock:DeleteAgent",
            "bedrock:DeleteGuardrail",
            "aoss:DeleteCollection",
            "aoss:DeleteIndex"
        ],
        "Resource": "*"
}


## Step 1: Create the Knowledge Base

> ## ⚠️ Do not click the big orange "Create Managed KB" button
>
> As of this writing, the Bedrock console's primary, most obvious button creates a **Managed Knowledge Base**, which **cannot use a plain S3 data source at all**. Every attempt to attach your S3 bucket to a Managed KB fails with `DATA_SOURCE_OPERATION_FAILED`, and the console's own data source list silently shows "(0)" even after the KB itself reports "Available", making it look like nothing happened rather than showing a clear error. This is a real product behavior, not a mistake you can make correctly by being more careful with that button. You need the dropdown arrow next to it instead. Follow the exact steps below.

1. Go to **AWS Console**, then **Amazon Bedrock**
2. **Confirm the region selector in the top-right corner reads US East (N. Virginia), us-east-1.** Switch it now if it shows anything else.
3. In the left sidebar under **Builder tools**, click **Knowledge Bases**
4. Click the small **dropdown arrow** next to the orange **Create Managed KB** button (not the button itself)
5. Under **Self-managed KB**, click **Unstructured Vector Store KB**

This opens a 4-step wizard: "Provide Knowledge Base details" → "Configure data source" → "Configure data storage and processing" → "Review and create." This is the flow that matches everything described below.

**Step "Provide Knowledge Base details":**

| Field | Value |
|-------|-------|
| KB name | `lab1-shared-kb` |
| Description | Shared Lab 1 e-commerce product documentation |

Click **Next**.

**Step "Configure data source":**

| Field | Value |
|-------|-------|
| Data source name | `lab1-documents` |
| Data source type | Amazon S3 (should already be selected) |
| S3 URI | `s3://bedrock-training-399707825894/lab1-documents/` |

> **Confirm this S3 bucket is also in us-east-1.** Bedrock requires the S3 data source to be in the same region as the Knowledge Base. If this bucket lives in a different region, the sync step in Step 2 will fail.

Leave all other data source settings at their defaults. Click **Next**.

**Step "Configure data storage and processing":**

Under **Embeddings model**, click **Select model** and choose:

| Field | Value |
|-------|-------|
| Embeddings model | **Titan Text Embeddings V2** |
| Inference | On-demand |

Click **Apply**. Under **Vector store**, leave **Quick create a new vector store - Recommended** selected, and set **Vector store type** to **Amazon OpenSearch Serverless**. Click **Next**.

**Step "Review and create":**

Confirm the summary shows KB name `lab1-shared-kb`, embeddings model Titan Text Embeddings V2, and vector store Amazon OpenSearch Serverless. Click **Create Knowledge Base**.

> ## ⚠️ Expect a data source error here. This is normal right now.
>
> The KB and its OpenSearch Serverless vector store will be created successfully, but you will very likely see a red banner reading **"Failed to add datasource 'lab1-documents' to the Knowledge Base. MANAGED_KNOWLEDGE_BASE_CONNECTOR data source is only supported for MANAGED knowledge base type."** This is a second, separate console bug: even in the correct self-managed flow, the console's own data source creation currently fails. Don't troubleshoot this in the console. Skip straight to the CLI workaround in Step 2 below, which creates the data source directly against a working API and takes under a minute.

Wait for the Knowledge Base status to show **Active** in the console (this may display as "Available" — both mean the same underlying `ACTIVE` state). This takes a few minutes while the OpenSearch Serverless collection provisions.

---

## Step 2: Create the Data Source and Sync (via CLI)

Because the console's data source creation is currently broken for this KB type (see the warning above), create the data source and start the sync using the AWS CLI instead. You need the **Knowledge Base ID** from the KB's detail page (a string like `Y8CM65UEUH`) and the ARN of your S3 bucket.

Save this as `ds-config.json` in your working directory:

```json
{
  "type": "S3",
  "s3Configuration": {
    "bucketArn": "arn:aws:s3:::bedrock-training-399707825894",
    "inclusionPrefixes": ["lab1-documents/"]
  }
}
```

Create the data source:

```bash
aws bedrock-agent create-data-source \
  --knowledge-base-id YOUR_KB_ID \
  --name lab1-documents \
  --data-source-configuration file://ds-config.json \
  --region us-east-1
```

Note the `dataSourceId` in the response, then start the sync:

```bash
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id YOUR_KB_ID \
  --data-source-id YOUR_DATA_SOURCE_ID \
  --region us-east-1
```

Check on it after a few seconds:

```bash
aws bedrock-agent get-ingestion-job \
  --knowledge-base-id YOUR_KB_ID \
  --data-source-id YOUR_DATA_SOURCE_ID \
  --ingestion-job-id YOUR_INGESTION_JOB_ID \
  --region us-east-1
```

Wait for `"status": "COMPLETE"` and confirm `"numberOfDocumentsScanned": 5` with `"numberOfDocumentsFailed": 0`. This whole step normally finishes in under a minute.

> **Sync failed?** Confirm the S3 URI is exactly `s3://bedrock-training-399707825894/lab1-documents/` with no trailing characters, and that the bucket is in us-east-1.

---

## Step 3: Copy and Share the Knowledge Base ID

1. On the Knowledge Base detail page, find the **Knowledge Base ID**
2. It is a string of letters and numbers such as `ABCDEF1234`
3. Share this ID with students before Lab 1 begins. Paste it in the course chat alongside their AWS credentials.

Students will add this ID to their `.env` file as `KNOWLEDGE_BASE_ID=ABCDEF1234`.

---

## Step 4: Test the Knowledge Base

Before students arrive, run a quick test to confirm the KB returns results:

**macOS/Linux:**
```bash
cd labs/lab1
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
KNOWLEDGE_BASE_ID="YOUR_KB_ID" python scripts/verify_knowledge_base.py
python scripts/query_knowledge_base.py --query "What is the return policy?"
```

**Windows (PowerShell):**
```powershell
cd labs\lab1
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
$env:KNOWLEDGE_BASE_ID="YOUR_KB_ID"; python scripts\verify_knowledge_base.py
$env:PYTHONIOENCODING="utf-8"; python scripts\query_knowledge_base.py --query "What is the return policy?"
```

Replace "YOUR_KB_ID" (NO QUOTES!) with the actual Knowledge Base ID from Step 3.

> **`UnicodeEncodeError: 'charmap' codec can't encode character` on Windows?** Claude's answer text can include characters the default Windows console codepage can't print. Set `$env:PYTHONIOENCODING="utf-8"` before running `query_knowledge_base.py`, as shown above. This can affect students during Lab 1 too if they hit the same error.

**Expected result:** `verify_knowledge_base.py` shows Status ACTIVE and 5 documents synced. `query_knowledge_base.py` returns an answer with citations.

---

## After Class: Cleanup

> **Cost note:** The OpenSearch Serverless collection created automatically by Bedrock costs approximately $700/month minimum while running. Delete the Knowledge Base immediately after class.

**Delete the Knowledge Base:**

1. Go to **AWS Console**, then **Amazon Bedrock**, then **Knowledge Bases**
2. Select `lab1-shared-kb`
3. Click **Delete**
4. Confirm deletion

Deleting the Knowledge Base also removes the associated OpenSearch Serverless collection Bedrock created automatically.

---

## Quick Reference: Pre-Class Checklist

| Item | Action | Frequency |
|------|--------|-----------|
| Console region | Confirm **us-east-1 (N. Virginia)** before creating anything | Every delivery |
| IAM user credentials | Already done | Once |
| S3 bucket with documents | Already done, confirm it is in us-east-1 | Once |
| Knowledge Base `lab1-shared-kb` | Create via **dropdown → Self-managed KB → Unstructured Vector Store KB**, not the default "Create Managed KB" button, in us-east-1 | Every delivery |
| Data source and sync | Create via AWS CLI, not the console (see Step 2 workaround) | Every delivery |
| Knowledge Base ID | Share in course chat | Every delivery |
| Test run | Verify KB before students arrive; set `PYTHONIOENCODING=utf-8` on Windows | Every delivery |
