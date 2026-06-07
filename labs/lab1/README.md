# Lab 1: Claude on Bedrock with RAG

**Course:** Anthropic Models on AWS Bedrock
**Duration:** 45 minutes

---

## Prerequisites

- [ ] Modules 1 and 2 lecture completed
- [ ] ROI Virtual Classroom VM available and running (Ask your instructor for your access credentials for RVC)
- [ ] AWS credentials received from your instructor

---

## Part 1: Setup

### Step 1: Log In to AWS

Your instructor has shared AWS credentials in the course chat. Use them to log in now.

Run the following command in your terminal (Windows Command Prompt):

```bash
aws login
```

A browser window opens. Enter the username and password your instructor provided and complete the login.

If the browser does not open automatically, the terminal will display a URL and a code. Open the URL manually, enter the code, and complete the login with your instructor credentials. If there is a delay of more than 2-3 seconds during authentication, refresh the browser screen (just the local VM browser, not the entire VM session browser!) and you should see a successful authrntication message.

Once login is complete, return to your terminal and verify the connection:

```bash
aws sts get-caller-identity
```

**Expected result:**
```json
{
    "UserId": "AIDA...",
    "Account": "your-acct-num-here",
    "Arn": "arn:aws:iam::your-acct-num-here:user/your-username"
}
```

> **Login failed or browser did not open?** Ask your instructor for assistance before continuing. Every step in this lab requires valid AWS credentials.

---

### Step 2: Clone the Course Repository

The course repository contains the starter scripts and sample data for all three labs. Clone it now and navigate to the Lab 1 directory. From this point, instruction are provided for Mac and Windows environments. If you wish to run these labs locally on your own machine, you may do so, but your instructor can only support running labs on RVC VMs, which run on Windows (follow the PowerShell instructions for RVC).

**macOS/Linux:**
```bash
git clone https://github.com/AWSClassroom-com/anthropic_on_aws.git ~/anthropic_on_aws
cd ~/anthropic_on_aws/labs/lab1
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/AWSClassroom-com/anthropic_on_aws.git C:\anthropic_on_aws
cd C:\anthropic_on_aws\labs\lab1
```

> **Keep note of this path.** Labs 2 and 3 reference files from this repository. The full path on macOS/Linux is `~/anthropic_on_aws/` and on Windows is `C:\anthropic_on_aws\`.

---

### Step 3: Verify Python

This lab requires Python 3.11 or higher. The RVC VM has Python pre-installed. Confirm the version:

```bash
python --version
```

**Expected result:** `Python 3.11.x` or higher.

> **Wrong version or command not found?** Try `python3 --version` on macOS/Linux. If neither works, ask your instructor.

---

### Step 4: Install Dependencies

The lab uses several Python packages. Install them now from the requirements file included in the lab 1 repository at C:\anthropic_on_aws\labs\lab1:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Confirm `(venv)` appears in your terminal prompt before continuing. All subsequent Python commands in this lab run inside this virtual environment.

**What you just installed -- boto3:**

The most important package in `requirements.txt` is **boto3**, the AWS SDK for Python. boto3 is how Python applications talk to AWS services. Instead of making raw HTTP requests to AWS APIs, boto3 gives you a clean Python interface:

```python
# Without boto3 -- raw HTTP, authentication headers, request signing
# Complex, error-prone, hundreds of lines

# With boto3 -- clean Python
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.invoke_model(modelId='...', body='...')
```

boto3 handles authentication, request signing, retries, and error parsing automatically. In this lab you will use it to invoke Claude models directly and to query your Knowledge Base. In Lab 3 you will use it to deploy a serverless API. It is the foundation of nearly every Python application built on AWS.

> **Verify boto3 installed correctly:**
> ```bash
> pip show boto3
> ```
> Expected: `Name: boto3` with a version number.

---

### Step 5: Confirm the S3 Documents Are Available

Your instructor has pre-loaded sample e-commerce documents into a shared S3 bucket. Confirm you can access them:

```bash
python scripts/check_setup.py
```

**Expected result:** (version numbers may vary)
```
=======================================================
  Lab 1 Setup Verification
  Anthropic Models on AWS Bedrock
=======================================================

  Python version...                        OK  (3.14.4)
  boto3 installed...                       OK  (1.43.24)
  python-dotenv installed...               OK
  AWS credentials...                       OK  (user01)
  S3 bucket access...                      OK  (s3://bedrock-training-your-acct-num-here)
  Sample documents...                      OK  (5 documents found)

=======================================================
  Setup complete. Ready to start Lab 1.
=======================================================
```

> **S3 access denied?** Your IAM user may be missing S3 read permissions. Ask your instructor.
> **0 documents found?** The S3 bucket path may differ from the script default. Ask your instructor for the correct bucket name and prefix.

---

## Part 1: Bedrock Console Orientation (For those new to Bedrock, otherwise, skip to Part 2)

Before writing code, spend a few minutes in the Bedrock console. This gives you a visual reference for what your Python scripts are doing under the hood.

### Step 1: Open the Playground

1. Sign in to the AWS Management Console and navigate to **Amazon Bedrock**.
2. Confirm you are in the **us-east-1 (N. Virginia)** region. Check the region selector in the top-right corner.
3. In the left sidebar under **Test**, click **Playground**.
4. Click the orange **Select model** button.
5. In the model picker, select **Anthropic**, then **Claude Sonnet 4.6**, then choose the **US** inference profile.
6. Click **Apply**.

### Step 2: Run One Prompt and Observe

7. Paste this prompt into the input area:

```
A customer says: "I ordered three items two weeks ago and only two arrived.
The third item shows as delivered but it is not here. I want a refund
for the missing item immediately and I am very frustrated."

Classify this ticket: sentiment, priority, recommended action.
Respond in JSON only.
```

8. Click **Run** and observe the response.
9. Note the **Input**, **Output**, and **Latency** values in the header bar next to the model name.

> **What you are looking at:** The console is a wrapper around the same API your Python code will call. The Input and Output values are token counts. The Latency is total round-trip time. In Step 5 you will extract these same values programmatically.

---

## Part 2: Model Invocation and Comparison

Now you will do the same thing in code across all three Claude models and capture structured output for comparison.

### Step 3: Open the Comparison Script

Open `scripts/compare_models.py` from the lab directory in your text editor of choice. The script is partially complete. You will find two clearly marked sections to fill in.

The script structure:

```python
import boto3
import json
import time

MODELS = {
    # TODO: Add the three model IDs here
}

PROMPT = """A customer says: "I ordered three items two weeks ago and only two arrived.
The third item shows as delivered but it is not here. I want a refund
for the missing item immediately and I am very frustrated."

Classify this ticket: sentiment, priority, recommended action.
Respond in JSON only."""

def invoke_model(client, model_id: str, prompt: str) -> dict:
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    })

    start = time.time()
    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body
    )
    latency_ms = round((time.time() - start) * 1000)

    result = json.loads(response["body"].read())

    return {
        # TODO: Return a dict with model_id, response text, input_tokens,
        # output_tokens, latency_ms, and cost_usd
        # Hint: response text is at result["content"][0]["text"]
        # Hint: token counts are at result["usage"]["input_tokens"] and ["output_tokens"]
        # Hint: calculate cost using the PRICING dict defined below
    }
```

### Step 4: Complete the MODELS Dict

Fill in the `MODELS` dict with the correct inference profile IDs for all three models. Use the format shown below for Sonnet as your guide:

```python
MODELS = {
    "Sonnet 4.6": "us.anthropic.claude-sonnet-4-6",
    # Add Opus 4.6 and Haiku 4.5 here
}
```

> **Why the `us.` prefix matters:** Claude 4 models on Bedrock require cross-region inference profile IDs, not direct model IDs. Using `anthropic.claude-sonnet-4-6` without the prefix returns a `ValidationException`. This is the inference profile format for US regions.

<details>
<summary>Model IDs for reference</summary>

```python
MODELS = {
    "Sonnet 4.6": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "Opus 4.6":   "us.anthropic.claude-opus-4-6-v1",
    "Haiku 4.5":  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
}
```
</details>

### Step 5: Complete the Return Dict

Fill in the `TODO` section inside `invoke_model()`. The function should return a dict containing:

- `model_id` - the model string passed in
- `response_text` - the text content of Claude's reply
- `input_tokens` - from `result["usage"]["input_tokens"]`
- `output_tokens` - from `result["usage"]["output_tokens"]`
- `latency_ms` - already calculated above
- `cost_usd` - calculated using the `PRICING` dict already defined in the script

<details>
<summary>Expected return dict structure</summary>

```python
return {
    "model_id":      model_id,
    "response_text": result["content"][0]["text"],
    "input_tokens":  result["usage"]["input_tokens"],
    "output_tokens": result["usage"]["output_tokens"],
    "latency_ms":    latency_ms,
    "cost_usd":      (
        result["usage"]["input_tokens"]  * PRICING[model_id]["input"]  +
        result["usage"]["output_tokens"] * PRICING[model_id]["output"]
    ) / 1_000_000
}
```

**Why divide by 1,000,000:** Pricing is quoted per million tokens. Dividing converts individual token counts to the fraction of a million you actually used.
</details>

### Step 6: Run the Comparison

**macOS/Linux:**
```bash
python compare_models.py
```

**Windows (PowerShell):**
```powershell
python scripts/compare_models.py
```

**Expected output:**
```
============================================================
Model Comparison Results (your results may vary)
============================================================

Sonnet 4.6
  Response:      {"sentiment": "negative", "priority": "high", ...}
  Input tokens:  76
  Output tokens: 179
  Latency:       3986 ms
  Cost:          $0.002913

Opus 4.6
  Response:      {"sentiment": "negative", "priority": "high", ...}
  Input tokens:  76
  Output tokens: 67
  Latency:       2080 ms
  Cost:          $0.006165

Haiku 4.5
  Response:      {"sentiment": "negative", "priority": "high", ...}
  Input tokens:  76
  Output tokens: 52
  Latency:       1027 ms
  Cost:          $0.000269

============================================================
```

> **Troubleshooting:** If you see `ValidationException`, check that your model IDs use the `us.` prefix. If you see `AccessDeniedException`, verify model access is enabled in the Bedrock console under **Model access**.

### Step 7: Analyze the Results

Look at your output and answer these questions before moving on:

1. Which model produced the most structured, accurate JSON?
2. Which model had the lowest cost? By how much compared to Sonnet?


> **Key insight:** All three returned valid JSON, which is a good baseline, but they are meaningfully different in ways that matter for a production classification system. The prompt asked for three specific fields: sentiment, priority, recommended action. Haiku returned exactly those three fields with clean, machine-readable values. A downstream system can parse this response, route it, and act on it without any additional processing. Sonnet over-engineered it. In a production ticket classifier, unexpected fields in the response schema break parsers, require additional handling, and add cost. Sonnet used 175 output tokens to return data nobody asked for. Opus got the schema right but the value wrong. recommended_action should be a machine-readable code like investigate_and_refund, not a prose paragraph. A downstream routing system cannot act on a sentence. Opus also cost 25x more than Haiku for an inferior result.

---

## Part 3: Cost Calculation

### Step 8: Review the Cost Projections

The script calculated production-scale cost projections from your actual token counts and printed them after the model comparison results. Find the Cost Projections table in your terminal output.

It looks something like this (your numbers may vary):

```
============================================================
  Cost Projections -- Production Scale
============================================================

  Model         Tokens/req    10k/day/mo    100k/day/mo
  ------------  ----------  ------------  -------------
  Sonnet 4.6           251       $855.90      $8,559.00
  Opus 4.6             152     $2,052.00     $20,520.00
  Haiku 4.5            128        $80.70        $807.00

  Formula: cost_per_request x daily_volume x 30 days
  Verify current rates: https://aws.amazon.com/bedrock/pricing/
============================================================
```

> **Your numbers will differ** from the example above based on the actual token counts in your run. The formula the script used is:
>
> `monthly_cost = cost_per_request x daily_volume x 30`

> **Current pricing:** The `PRICING` dict in `compare_models.py` reflects rates at time of writing. Verify at https://aws.amazon.com/bedrock/pricing/ before making production cost decisions.

### Step 9: The Model Selection Decision

Based on your calculations, answer: at 10,000 tickets per day, what is the monthly cost difference between Sonnet and Haiku? Is that difference worth the quality gap you observed in Step 7?

There is no single right answer. The point is that you now have the data to make the decision rather than guessing.

---

## Part 4: Connecting to the Knowledge Base

Your instructor has created a shared Knowledge Base loaded with sample e-commerce product documentation. You do not need to create your own. You connect to the shared KB using an ID your instructor provided in the course chat.

This is the production pattern -- developers consume an existing Knowledge Base rather than provisioning their own infrastructure. Your job is to connect to it and run queries against it.

### Step 10: Add the Knowledge Base ID to Your Environment

Your instructor shared a Knowledge Base ID in the course chat. It is a string of letters and numbers such as `ABCDEF1234`.

Open `.env` in your editor. It is at `anthropic_on_aws/labs/lab1/.env`.

If the file does not exist, create it with the name `.env` within the \lab1 folder.:

Open `.env` and set your Knowledge Base ID:

```
KNOWLEDGE_BASE_ID=ABCDEF1234
```

Replace `ABCDEF1234` with the actual ID shared by your instructor in the course chat. Save the file.

---

### Step 11: Verify the Knowledge Base

Confirm you can access the shared Knowledge Base:

**macOS/Linux:**
```bash
python scripts/verify_knowledge_base.py
```

**Windows (PowerShell):**
```powershell
python scripts\verify_knowledge_base.py
```

**Expected output:**
```
=======================================================
  Lab 1: Knowledge Base Verification
  Anthropic Models on AWS Bedrock
=======================================================

  Knowledge Base ID:   ABCDEF1234
  Name:                lab1-shared-kb
  Status:              ACTIVE
  Data source:         lab1-documents
  Sync status:         AVAILABLE
  Documents synced:    5

=======================================================
  Knowledge Base is active and ready.
=======================================================
```

> **KNOWLEDGE_BASE_ID not found?** Check that `.env` exists and contains the correct ID with no extra spaces.

> **Status shows anything other than ACTIVE?** Ask your instructor -- the shared Knowledge Base may still be provisioning.

> **AccessDeniedException?** Your IAM user may be missing `bedrock-agent-runtime:*` permissions. Ask your instructor.



## Part 5: Testing RAG Queries

### Step 12: Run Your First Query

With the KB active and documents synced, run a query against it:

**macOS/Linux:**
```bash
python scripts/query_knowledge_base.py --query "What is the return policy for damaged products?"
```

**Windows (PowerShell):**
```powershell
python scripts/query_knowledge_base.py --query "What is the return policy for damaged products?"
```

**Expected output:**
```
Query: What is the return policy for damaged products?

Answer:
## Return Policy for Damaged Products

Based on the ACME Corp Return Policy, here are the details for returning damaged products:

- **Return Window:** Damaged products may be returned within **60 days** of purchase (double the standard 30-day window)
- **Documentation Required:** You must provide **photo documentation** of the damage
- **Return Shipping:** ACME Corp **covers the return shipping costs** for damaged items
- **Replacement Timeline:** Replacements are shipped within **3-5 business days** after the return is received

### How to Initiate a Damaged Product Return:
1. Log into your account at **acmecorp.com/returns**
2. Select the order containing the damaged item
3. Choose the reason for return from the dropdown menu
4. Print the prepaid shipping label
5. Ship the item within **7 days** of initiating the return
6. Refund will be processed within **5-7 business days** after the item is received

For additional assistance, you can contact ACME Corp at **support@acmecorp.com** or call **1-800-ACME-HELP**.

Citations:
  [1] return-policy.txt (score: 0.45)
  [2] support-procedures.txt (score: 0.41)
  [3] warranty-coverage.txt (score: 0.39)
```

### Step 13: Verify Citation Accuracy

Look at the citations returned. Ask yourself:

- Does Claude's answer reflect what the source document actually says?
- Did Claude add anything not supported by the citations?
- Which document scored highest? Does that make sense given the query?
- Are there any claims in the answer you cannot trace back to a cited source?

Relevance scores range from 0 to 1. Higher scores mean the chunk matched your query more closely. A score below 0.5 often signals a weak retrieval -- the system found something but it may not be directly relevant.

> **Citations are not decoration.** In production applications, especially regulated ones, citations are the audit trail. A high-quality RAG system traces every claim to a source. If you cannot verify a claim against its citation, the system is hallucinating.

### Step 14: Test Query Phrasing

Run the same underlying question two ways and compare results:

**Vague:**

**macOS/Linux:**
```bash
python query_knowledge_base.py --query "How do I return something?"
```

**Windows (PowerShell):**
```powershell
python query_knowledge_base.py --query "How do I return something?"
```

**Specific:**

**macOS/Linux:**
```bash
python scripts/query_knowledge_base.py --query "What is the step-by-step process for initiating a product return, including required documentation and timelines?"
```

**Windows (PowerShell):**
```powershell
python scripts/query_knowledge_base.py --query "What is the step-by-step process for initiating a product return, including required documentation and timelines?"
```

Look at the citation scores for each. The specific query should return higher scores and more targeted chunks.

> **Why this matters in production:** Users ask vague questions. Your application should preprocess or expand queries before sending them to the retrieval layer. You will implement this pattern in Lab 3.

### Step 15: Test the Boundaries

Run a query about something not in the documents:

**macOS/Linux:**
```bash
python scripts/query_knowledge_base.py --query "What is the CEO's favorite color?"
```

**Windows (PowerShell):**
```powershell
python scripts/query_knowledge_base.py --query "What is the CEO's favorite color?"
```

**Expected result:** Claude indicates it does not have that information, or retrieval returns no relevant chunks with scores near zero.

This is correct behavior. A RAG system that answers out-of-scope questions confidently is more dangerous than one that says it does not know.

---

## What You Built

In 45 minutes, you:

- Invoked three Claude models programmatically and compared their output on a real support ticket classification task
- Extracted token counts and latency from API responses and calculated actual per-invocation cost
- Scaled those costs to production volumes to make a real model selection decision
- Created a Knowledge Base from e-commerce product documentation using the Bedrock API
- Ran RAG queries and evaluated citation accuracy against source documents

**The Knowledge Base ID written to your `.env` file carries forward into Lab 3.** Do not delete it.

---

## Cleanup

The Knowledge Base and its OpenSearch vector store incur ongoing costs when left running. Your instructor will clean up shared resources after class.

---

*Lab 1 Complete*
