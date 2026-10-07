# Lab 1: Claude on Bedrock with RAG

**Course:** Anthropic Models on AWS Bedrock
**Duration:** 45 minutes

---

## Prerequisites

- [ ] Modules 1 and 2 lecture completed
- [ ] ROI Virtual Classroom VM available and running (Ask your instructor for your access credentials for RVC)
- [ ] AWS SSO credentials received from your instructor

> ## ⚠️ REGION: us-east-1 (N. Virginia) ONLY
>
> This lab, and Labs 2 and 3, only work in **us-east-1**. The shared Knowledge Base your instructor created lives there, and every script in this repo is hardcoded to it. Whenever you open the AWS Console, check the region selector in the top-right corner and confirm it reads **US East (N. Virginia)** before doing anything else. If you switch regions mid-lab, nothing you set up in this lab will be visible anymore.

---

## Part 1: Setup

### Step 1: Sign In to AWS

Signing in has two parts. First you authenticate to the AWS access portal in a browser, then you connect the AWS CLI in your terminal. Both use the same SSO credentials your instructor supplied.

#### Part A: Sign in to the AWS access portal

1. Sign in to your RVC virtual machine with the SSO credentials your instructor supplied.
2. Inside the VM, open Google Chrome and go to **https://roi.awsapps.com/start/**
3. Enter the same credentials. You are redirected to the AWS access portal, which lists your account under the **AWS Accounts** card.
4. Select the account name to expand it, then click the **AnthropicClassroomUser** link.
5. You are signed in to the AWS console.

**Expected result:** an authenticated AWS console with your account active. If you land anywhere else, stop and ask your instructor before continuing.

#### Part B: Configure the AWS CLI for SSO

Part A authenticates the browser. Your terminal needs its own session, and before it can sign in, the CLI has to know where your SSO portal lives. You do this once.

```bash
aws configure sso
```

Answer the prompts:

| Prompt | Answer |
|--------|--------|
| SSO session name (Recommended) | `AnthropicUser` |
| SSO start URL [None] | `https://roi.awsapps.com/start/` |
| SSO region [None] | `us-east-1` |
| SSO registration scopes [sso:account:access] | leave blank, press Enter |

A browser tab opens and asks **Allow botocore-client-AnthropicUser to access your data?** Click the orange **Allow access** button.

A confirmation screen reads "Your credentials have been shared successfully and can be used until your session expires." Close that tab and return to your terminal.

The CLI then finds your account and role automatically and asks three more questions:

| Prompt | Answer |
|--------|--------|
| Default client Region [None] | `us-east-1` |
| CLI default output format (json if not specified) [None] | `json` |
| Profile name [AnthropicClassroomUser-...] | **type `default`** |

> ## ⚠️ Type `default` at the profile name prompt
>
> Do not press Enter to accept the suggested name. The suggested name contains your AWS account number, which is different for every student, and it is not the profile the lab scripts look for.
>
> Every Python script in these labs creates its boto3 client without naming a profile, which means they all read the `default` profile. The Claude Code setup in Lab 2 and the `sam deploy` in Lab 3 expect it too. Name the profile `default` here and everything downstream works with no extra flags.
>
> **Already pressed Enter?** Run `aws configure sso` again and type `default` at the profile name prompt. It is safe to run more than once.

**Expected result:** the CLI reports the account and role it selected, then confirms:

```
The AWS CLI is now configured to use the default profile.
Run the following command to verify your configuration:

aws sts get-caller-identity
```

If that last line instead shows `aws sts get-caller-identity --profile AnthropicClassroomUser-...`, the profile name did not take. Run `aws configure sso` again and type `default` at the profile name prompt.

#### Part C: Sign in to the CLI

```bash
aws sso login
```

If the browser does not open on its own, the terminal prints a URL and a code. Open the URL, enter the code, and complete the sign-in. If authentication pauses for more than two or three seconds, refresh the browser tab inside the VM, not the VM session window itself, and the success message appears.

Confirm the CLI is connected:

```bash
aws sts get-caller-identity
```

**Expected result:**
```json
{
    "UserId": "AROA3FSDOKSIM3Z7Q5TFY:yourname@awsclassroom.com",
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/AWSReservedSSO_AnthropicClassroomUser_1282bfbd9a140ecb/yourname@awsclassroom.com"
}
```

Your account number, user name, and the suffix on the role name will differ. The shape is what matters.

> **The ARN says `assumed-role`, not `user`.** SSO signs you in to a role rather than to an IAM user, so the ARN looks different from a long-lived access key. This is expected.

> **`Unable to locate credentials`?** The profile is not named `default`. Re-run `aws configure sso` and type `default` at the profile name prompt. As a one-off check you can add `--profile AnthropicClassroomUser-<your-account-number>` to the command, but the lab scripts cannot use that, so fix the profile name rather than working around it.

> **Sign-in failed, or the browser did not open?** Ask your instructor before continuing. Every step in this lab needs valid AWS credentials.

> **SSO sessions expire after about 8 hours.** If commands start failing later in the day with an expired token error, run `aws sso login` again. You only run `aws configure sso` once, so a later sign-in is a single command.

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

**What you just installed: boto3**

The most important package in `requirements.txt` is **boto3**, the AWS SDK for Python. boto3 is how Python applications talk to AWS services. Instead of making raw HTTP requests to AWS APIs, boto3 gives you a clean Python interface:

```python
# Without boto3: raw HTTP, authentication headers, request signing
# Complex, error-prone, hundreds of lines

# With boto3: less code
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

> **S3 access denied?** Your SSO role may be missing S3 read permissions. Ask your instructor.
> **0 documents found?** The S3 bucket path may differ from the script default. Ask your instructor for the correct bucket name and prefix.

---

## Part 1: Bedrock Console Orientation (For those new to Bedrock, otherwise, skip to Part 2)

Before writing code, spend a few minutes in the Bedrock console. This gives you a visual reference for what your Python scripts are doing under the hood.

### Step 1: Open the Playground

1. Sign in to the AWS Management Console and navigate to **Amazon Bedrock**.
2. **Confirm you are in the us-east-1 (N. Virginia) region.** Check the region selector in the top-right corner. This is not optional. The shared Knowledge Base and every model you invoke in this lab only exist in this region.
3. In the left sidebar under **Test**, click **Playground**.
4. Click the orange **Select model** button.
5. In the model picker, select **Anthropic**, then **Claude Sonnet 5.5**, then choose the **US** inference profile.
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

Open `scripts/compare_models.py` from the lab directory in Notepad (PC) or TextEdit (Mac). The script is partially complete. You will find two clearly marked sections to fill in, commented `TODO 1` and `TODO 2`.

The script structure:

```python
import boto3
import json
import time

from botocore.exceptions import ClientError

# TODO 1: Add the three model IDs here
MODELS = {
    "Sonnet 5.5": "us.anthropic.claude-sonnet-5-5",
    # Add Opus 5.5 and Haiku 4.5 here
}

PROMPT = """A customer says: "I ordered three items two weeks ago and only two arrived.
..."""

PRICING = {
    # already filled in for you
}


def invoke_model(client, model_id: str, prompt: str) -> dict:
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    })

    start = time.time()

    try:
        response = client.invoke_model(...)
    except ClientError as e:
        # errors are returned as data, already written for you
        ...

    latency_ms = round((time.time() - start) * 1000)

    result = json.loads(response["body"].read())

    return {
    # TODO 2: Add the model response return dict here

}
```

You complete the two TODOs in order: `TODO 1` in Step 4 and `TODO 2` in Step 5.

### Step 4: Complete the MODELS Dict

Find the commented `TODO 1` and fill in the `MODELS` dict with the correct inference profile IDs for all three models. Use the format shown below for Sonnet as your guide:

```python
MODELS = {
    "Sonnet 5.5": "us.anthropic.claude-sonnet-5-5",
    # Add Opus 5.5 and Haiku 4.5 here
}
```

> **Why the `us.` prefix matters:** Claude models on Bedrock require a cross-region inference profile ID, not a bare model ID. Calling `anthropic.claude-sonnet-5-5` without the prefix returns a `ValidationException`. The `us.` prefix routes across US regions.

> **Two ID formats, both current.** Newer models use a short ID with no date, such as `us.anthropic.claude-sonnet-5-5`. Older models keep a dated, versioned ID. Haiku 4.5 is one of them, so its ID is `us.anthropic.claude-haiku-4-5-20251001-v1:0`. You will use both in this exercise. Check the model card if you are unsure which form a model takes.

<details>
<summary>Model IDs for reference</summary>

```python
MODELS = {
    "Sonnet 5.5": "us.anthropic.claude-sonnet-5-5",
    "Opus 5.5":   "us.anthropic.claude-opus-5-5",
    "Haiku 4.5":  "us.anthropic.claude-haiku-4-5-20251001-v1:0",
}
```
</details>

### Step 5: Complete the Return Dict

Find the commented `TODO 2` inside `invoke_model()` and fill in the section. The `return {` and its closing `}` are already written for you, so you are adding only the dict contents. The function should return a dict containing:

- `model_id` - the model string passed in
- `response_text` - the text content of Claude's reply
- `input_tokens` - from `result["usage"]["input_tokens"]`
- `output_tokens` - from `result["usage"]["output_tokens"]`
- `latency_ms` - already calculated above
- `cost_usd` - calculated using the `PRICING` dict already defined in the script

<details>
<summary>Expected contents of the return dict</summary>

The script already has `return {` and its closing `}`. Paste this between them, replacing the `TODO 2` comment line.

```python
    "model_id":      model_id,
    "response_text": result["content"][0]["text"],
    "input_tokens":  result["usage"]["input_tokens"],
    "output_tokens": result["usage"]["output_tokens"],
    "latency_ms":    latency_ms,
    "cost_usd":      (
        result["usage"]["input_tokens"]  * PRICING[model_id]["input"]  +
        result["usage"]["output_tokens"] * PRICING[model_id]["output"]
    ) / 1_000_000
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

Sonnet 5.5
  Response:      {"sentiment": "negative", "priority": "high", ...}
  Input tokens:  76
  Output tokens: 179
  Latency:       3986 ms
  Cost:          $0.001942

Opus 5.5
  Response:      {"sentiment": "negative", "priority": "high", ...}
  Input tokens:  76
  Output tokens: 67
  Latency:       2080 ms
  Cost:          $0.001644

Haiku 4.5
  Response:      {"sentiment": "negative", "priority": "high", ...}
  Input tokens:  76
  Output tokens: 52
  Latency:       1027 ms
  Cost:          $0.000336

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
  Sonnet 5.5           255       $582.60      $5,826.00
  Opus 5.5             143       $493.20      $4,932.00
  Haiku 4.5            128       $100.80      $1,008.00

  Formula: cost_per_request x daily_volume x 30 days
  Verify current rates: https://aws.amazon.com/bedrock/pricing/
============================================================
```

> **Notice what happened to Opus.** In this sample run Opus costs less per month than Sonnet, even though its token rate is twice as high. Opus answered in 67 output tokens where Sonnet used 179. Output tokens are billed at five times the input rate on every current model, so response length moves the bill as much as model choice does. Your own run will differ. Read the token counts before you read the rates.

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

This is the production pattern. Developers consume an existing Knowledge Base rather than provisioning their own infrastructure. Your job is to connect to it and run queries against it.

### Step 10: Add the Knowledge Base ID to Your Environment

Your instructor shared a Knowledge Base ID in the course chat. It is a string of letters and numbers such as `ABCDEF1234`.

Open `.env` in Notepad (PC) or TextEdit (Mac). It is at `anthropic_on_aws/labs/lab1/.env`.

If the file does not exist, create it with the name `.env` within the \lab1 folder. In Windows Explorer, choose the VIEW options and select SHOW > FILE NAME EXTENSIONS to ensure your new file does not have a .txt file extension (it should be named `.env`, not `.env.txt`)

Open `.env` and set your Knowledge Base ID by adding the following text string:

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

> **Status shows anything other than ACTIVE?** Ask your instructor. The shared Knowledge Base may still be provisioning.

> **AccessDeniedException?** Your SSO role may be missing `bedrock-agent-runtime:*` permissions. Ask your instructor.



## Part 5: Testing RAG Queries

> **Windows: `UnicodeEncodeError: 'charmap' codec can't encode character`?** Claude's answer text can include characters the default Windows console codepage can't print. This does not happen on every query, only when the model's response happens to include one of those characters, so it can appear to work fine and then fail later. Set `$env:PYTHONIOENCODING="utf-8"` once per terminal session before running any `query_knowledge_base.py` command in this part, to avoid it entirely:
> ```powershell
> $env:PYTHONIOENCODING="utf-8"
> ```

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

Relevance scores range from 0 to 1. Higher scores mean the chunk matched your query more closely. A score below 0.5 often signals weak retrieval. The system found something, but it may not be directly relevant.

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
- Connected to a shared Knowledge Base of e-commerce product documentation and queried it using the Bedrock API
- Ran RAG queries and evaluated citation accuracy against source documents

**The Knowledge Base ID written to your `.env` file carries forward into Lab 3.** Do not delete it.

---

## Cleanup

The Knowledge Base and its OpenSearch vector store incur ongoing costs when left running. Your instructor will clean up shared resources after class.

---

*Lab 1 Complete*
