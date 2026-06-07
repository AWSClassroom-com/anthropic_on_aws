# Instructor Pre-Setup Guide: Lab 1
## Anthropic Models on AWS Bedrock

**Complete these steps before students arrive. Allow 20 minutes.**

---

## What You Are Setting Up

Before class you will create one shared Knowledge Base that all students use during Lab 1. Students receive the Knowledge Base ID from you and use it to run RAG queries. They do not create their own Knowledge Base.

You need to complete three things:

1. Create the Knowledge Base via the Bedrock console
2. Sync the S3 documents into it
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

1. Go to **AWS Console** -- **Amazon Bedrock**
2. In the left sidebar under **Builder tools**, click **Knowledge Bases**
3. Click **Create Knowledge Base**

**Knowledge Base details:**

| Field | Value |
|-------|-------|
| Name | `lab1-shared-kb` |
| Description | Shared Lab 1 e-commerce product documentation |
| IAM permissions | Select **Create and use a new service role** |

Click **Next**

**Configure data source:**

| Field | Value |
|-------|-------|
| Data source name | `lab1-documents` |
| S3 URI | `s3://bedrock-training-399707825894/lab1-documents/` |

Leave all other data source settings at their defaults.

Click **Next**

**Configure embeddings model:**

| Field | Value |
|-------|-------|
| Embeddings model | **Titan Text Embeddings V2** |
| Vector dimensions | 1024 (default) |

Click **Next**

**Configure vector store:**

Select **Quick create a new vector store**. Bedrock creates and manages the OpenSearch Serverless collection automatically.

Click **Next**

**Review and create:**

Confirm:
- Knowledge Base name is `lab1-shared-kb`
- S3 URI is `s3://bedrock-training-399707825894/lab1-documents/`
- Embeddings model is Titan Text Embeddings V2

Click **Create Knowledge Base**

Wait for status to show **Active**. This takes 5-10 minutes.

---

## Step 2: Sync the Documents

Once the Knowledge Base shows **Active**:

1. Click the **Data sources** tab
2. Select **lab1-documents**
3. Click **Sync**

Wait for sync status to show **Available** and document count to show **5**.

> **Sync failed?** Confirm the S3 URI is exactly `s3://bedrock-training-399707825894/lab1-documents/` with no trailing characters.

---

## Step 3: Copy and Share the Knowledge Base ID

1. On the Knowledge Base detail page, find the **Knowledge Base ID**
2. It is a string of letters and numbers such as `ABCDEF1234`
3. Share this ID with students before Lab 1 begins -- paste it in the course chat alongside their AWS credentials

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
python scripts\query_knowledge_base.py --query "What is the return policy?"
```

Replace "YOUR_KB_ID" (NO QUOTES!) with the actual Knowledge Base ID from Step 3.

**Expected result:** `verify_knowledge_base.py` shows Status ACTIVE and 5 documents synced. `query_knowledge_base.py` returns an answer with citations.

---

## After Class: Cleanup

> **Cost note:** The OpenSearch Serverless collection created automatically by Bedrock costs approximately $700/month minimum while running. Delete the Knowledge Base immediately after class.

**Delete the Knowledge Base:**

1. Go to **AWS Console** -- **Amazon Bedrock** -- **Knowledge Bases**
2. Select `lab1-shared-kb`
3. Click **Delete**
4. Confirm deletion

Deleting the Knowledge Base also removes the associated OpenSearch Serverless collection Bedrock created automatically.

---

## Quick Reference: Pre-Class Checklist

| Item | Action | Frequency |
|------|--------|-----------|
| IAM user credentials | Already done | Once |
| S3 bucket with documents | Already done | Once |
| Knowledge Base `lab1-shared-kb` | Create before each delivery | Every delivery |
| Document sync | Run after KB creation | Every delivery |
| Knowledge Base ID | Share in course chat | Every delivery |
| Test run | Verify KB before students arrive | Every delivery |
