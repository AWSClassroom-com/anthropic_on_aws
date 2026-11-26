# Lab 1: Claude on Bedrock with RAG

**Course:** Anthropic Models on AWS Bedrock
**Duration:** 40 minutes

---

## How This Lab Works

Everything is installed and ready on your lab VM. You do not edit any code and you do not type any configuration. For each part you:

1. **Explore** a script in VS Code to see how it works
2. **Run** it
3. **Read** the output, which ends with a self-check and a single pass line

When a script prints `All N checks passed! ✅`, that part of the lab is done.

## Prerequisites

- [ ] Modules 1 and 2 lecture completed
- [ ] ROI Virtual Classroom VM available and running (ask your instructor for your access credentials)
- [ ] AWS SSO credentials received from your instructor

> ## ⚠️ REGION: us-east-1 (N. Virginia) ONLY
>
> This lab, and Labs 2 and 3, only work in **us-east-1**. The shared Knowledge Base your instructor created lives there, and every script in this repo is hardcoded to it. Whenever you open the AWS Console, check the region selector in the top-right corner and confirm it reads **US East (N. Virginia)** before doing anything else. If you switch regions mid-lab, nothing you set up in this lab will be visible anymore.

---

## Part 1: Setup

### Step 1: Sign In to AWS

Signing in has two parts. First you authenticate to the AWS access portal in a browser, then you connect the AWS CLI in your terminal. Both use the same SSO credentials your instructor supplied.

#### Part A: Sign in to the AWS access portal

1. Inside the VM, open Google Chrome and go to **https://roi.awsapps.com/start/**
2. Enter your SSO credentials. You are redirected to the AWS access portal, which lists your account under the **AWS Accounts** card.
3. Select the account name to expand it, then click the **AnthropicClassroomUser** link.
4. You are signed in to the AWS console.

**Expected result:** an authenticated AWS console with your account active. If you land anywhere else, stop and ask your instructor before continuing.

#### Part B: Configure the AWS CLI for SSO

Part A authenticates the browser. Your terminal needs its own session, and before it can sign in, the CLI has to know where your SSO portal lives. You do this once.

Open a terminal and run:

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
| Configure AWS skills and the AWS MCP server for your AI coding agent(s)? [y/n/never] | `y` |
| Select agents to configure (space to toggle, up/down arrows to navigate, enter to confirm) | leave Claude Code selected, press Enter |
| Install 26 default AWS skills? [Y/n] | `y` |
| Configure AWS MCP server connection? [Y/n] | `n` (you build your own MCP server in Lab 2) |
| Keep AWS skills up to date automatically? [Y/n] | `y` |

A browser tab opens and asks **Allow botocore-client-AnthropicUser to access your data?** Click the orange **Allow access** button.

A confirmation screen reads "Your credentials have been shared successfully and can be used until your session expires." Close that tab and return to your terminal.

The CLI then finds your account and role automatically and asks three more questions. Read the warning on the profile name first: it **must** be `default` or the rest of the labs will not work.

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

> **`Unable to locate credentials`?** The profile is not named `default`. Re-run `aws configure sso` and type `default` at the profile name prompt.

> **Sign-in failed, or the browser did not open?** Ask your instructor before continuing. Every step in this lab needs valid AWS credentials.

> **SSO sessions expire after about 8 hours.** If commands start failing later in the day with an expired token error, run `aws sso login` again. You only run `aws configure sso` once, so a later sign-in is a single command.

---

### Step 2: Open the Lab and Check Your Environment

The course repository, Python, and every package the labs need are already on your VM. Open the Lab 1 folder in VS Code and run the environment check.

> **Expected: this step opens VS Code.** The `code .` command launches VS Code on the Lab 1 folder so you can read the lab files in later steps. A VS Code window appears while the terminal prompt comes straight back. That is normal. Leave VS Code open and keep using the terminal for the commands in this lab.

```bash
cd ~/anthropic_on_aws/labs/lab1
code .
python scripts/check_setup.py
```

Your terminal prompt starts with `(venv)`. That means the lab's Python environment is active. If you do not see it, run `source ~/venv/bin/activate` and try again.

**Expected result:** (version numbers may vary)
```
=======================================================
  Lab 1 Setup Verification
  Anthropic Models on AWS Bedrock
=======================================================

  Python version...                        OK  (3.14.4)
  boto3 installed...                       OK  (1.43.24)
  python-dotenv installed...               OK
  AWS credentials...                       OK  (yourname@awsclassroom.com)
  S3 bucket access...                      OK  (s3://bedrock-training-your-acct-num-here)
  Sample documents...                      OK  (5 documents found)

All 6 checks passed! ✅
Setup complete. Ready to start Lab 1.
```

> **AWS credentials failed?** Run `aws sso login` again, then rerun the check.
> **S3 access denied, or 0 documents found?** Tell your instructor.

**What is boto3?** boto3 is the AWS SDK for Python, and it is how Python applications talk to AWS services. Instead of making raw HTTP requests and signing them yourself, you call a clean Python interface:

```python
import boto3
client = boto3.client('bedrock-runtime', region_name='us-east-1')
response = client.invoke_model(modelId='...', body='...')
```

boto3 handles authentication, request signing, retries, and error parsing. Every Python script in these labs uses it.

---

## Part 2: Bedrock Console Orientation (for those new to Bedrock, otherwise skip to Part 3)

### Step 3: Try One Prompt in the Playground

Before reading code, spend a few minutes in the Bedrock console. It gives you a visual reference for what the scripts do under the hood.

1. In the AWS console, navigate to **Amazon Bedrock**.
2. **Confirm you are in the us-east-1 (N. Virginia) region.** Check the region selector in the top-right corner.
3. In the left sidebar under **Test**, click **Playground**.
4. Click **Select model**, then choose **Anthropic**, then **Claude Sonnet 5.5**, then the **US** inference profile, and click **Apply**.
5. Paste this prompt into the input area:

```
A customer says: "I ordered three items two weeks ago and only two arrived.
The third item shows as delivered but it is not here. I want a refund
for the missing item immediately and I am very frustrated."

Classify this ticket. Respond with JSON only, no preamble and no extra fields.
Use exactly these three keys:
  "sentiment"           one of: positive, neutral, negative
  "priority"            one of: low, medium, high
  "recommended_action"  a single short sentence
```

6. Click **Run** and note the **Input**, **Output**, and **Latency** values in the header bar next to the model name.

> **What you are looking at:** The console is a wrapper around the same API your Python code calls. The Input and Output values are token counts, and the Latency is total round-trip time. The script in Part 3 extracts these same values programmatically.

---

## Part 3: Model Invocation and Comparison

The script sends this same prompt to all three Claude models and compares the results.

### Step 4: Explore the Comparison Script

In VS Code, open `scripts/compare_models.py`. There is nothing to edit. Read it from the top and find each item in the table. The comments marked `EXPLORE` point to the important lines.

| Find this | What to notice |
|-----------|----------------|
| `MODELS` | Three inference profile IDs. Each starts with `us.` and has no date in it. |
| `PRICING` | Dollars per million tokens, split into input and output. |
| `invoke_model()` | One call to `client.invoke_model()` wrapped in a `try` block. |
| The `except ClientError` branch | A failed call is returned as data instead of crashing the script. |
| The `return` dict | Token counts come from `result["usage"]`. The reply is found by type. |
| `calculate_cost()` | Tokens multiplied by the rate, then divided by 1,000,000. |
| `self_check()` | The script checks its own results and prints the pass line. |

> **Why the `us.` prefix matters:** Claude models on Bedrock require a cross-region inference profile ID, not a bare model ID. Calling `anthropic.claude-sonnet-5-5` without the prefix returns a `ValidationException`. The `us.` prefix routes across US regions. Use `us.` for every model in this lab. The `global.` prefix is not reliably enabled in the class account, so stay with `us.`.

> **Model ID format.** The 5.5 models use a short ID with no date: `us.anthropic.claude-sonnet-5-5`, `us.anthropic.claude-opus-5-5` and `us.anthropic.claude-haiku-5-5`. Older models keep a dated, versioned ID, such as `us.anthropic.claude-haiku-4-5-20251001-v1:0`. Check the model card if you are unsure which form a model takes.

<details>
<summary>Why search for the text block instead of using position 0?</summary>

Some Claude models return a thinking block before the reply, so `content[0]` is not always the text. On those models, indexing position 0 raises `KeyError: 'text'`. The models in this lab usually answer with a single text block, but selecting by `type` works whether or not a thinking block is present, so the same code keeps working when you move to a newer model.
</details>

<details>
<summary>Why divide by 1,000,000?</summary>

Pricing is quoted per million tokens. Dividing converts individual token counts to the fraction of a million you actually used.
</details>

### Step 5: Run the Comparison

```bash
python scripts/compare_models.py
```

**Expected output:** (your results will vary)
```
============================================================
  Model Comparison Results
============================================================

Sonnet 5.5
  JSON valid:    YES
  Response:
    {
        "sentiment": "negative",
        "priority": "high",
        "recommended_action": "..."
    }
  Input tokens:  167
  Output tokens: 69
  Latency:       2185 ms
  Cost:          $0.001024

Opus 5.5
  ...

Haiku 5.5
  ...

============================================================
  Self-Check
============================================================
  ✅ Sonnet 5.5: call succeeded
  ✅ Sonnet 5.5: JSON has the three keys with allowed values
  ✅ Sonnet 5.5: cost equals tokens x rate
  ... (the same three checks for Opus 5.5 and Haiku 5.5)

All 9 checks passed! ✅
```

The cost projections table prints between the results and the self-check. You read it in Step 8.

> **Troubleshooting:** If a model is skipped with `AccessDeniedException`, or the message mentions AWS Marketplace, the class account does not currently allow that model. Tell your instructor. The script skips the model that failed and still runs the others, and the self-check tells you which one failed.

### Step 6: Analyze the Results

Look at your output and answer these questions before moving on:

1. Which model produced the most structured, accurate JSON?
2. Which model had the lowest cost? By how much compared to Sonnet?

> **Key insight:** All three models returned valid JSON with exactly the three keys the prompt asked for, and all three classified the ticket the same way: negative sentiment, high priority. Only the wording of `recommended_action` differs. That is the normal result for a well-specified task, and it is the finding. When the smallest model gives an answer a downstream system can parse and route, a larger model is not buying you a better answer on this task. It is only buying you a higher bill. For the same classification, Sonnet cost roughly twenty times what Haiku did and Opus roughly forty times.

### Step 7: See an Error Handled as Data

Run the script again with the `--demo-error` flag. It adds a fourth model whose ID does not exist:

```bash
python scripts/compare_models.py --demo-error
```

**What to look for:** a line like `SKIPPED Bad model ID: ValidationException ...` appears, the three real models still run, and the self-check adds one more line:

```
  ✅ Bad model ID was skipped and the run continued

All 10 checks passed! ✅
```

This is the `except ClientError` branch you found in Step 4. In production, one unavailable model, one throttled request, or one bad input must not take down the whole batch. Lab 3 uses the same pattern in the agentic loop.

---

## Part 4: Cost Calculation

### Step 8: Review the Cost Projections

The script calculated production-scale cost projections from your actual token counts. Scroll up in your Step 5 output and find the Cost Projections table.

It looks something like this (your numbers will vary):

```
============================================================
  Cost Projections -- Production Scale
============================================================

  Model         Tokens/req    10k/day/mo    100k/day/mo
  ------------  ----------  ------------  -------------
  Sonnet 5.5           236       $307.20      $3,072.00
  Opus 5.5             232       $590.40      $5,904.00
  Haiku 5.5            230        $14.46        $144.60

  Formula: cost_per_request x daily_volume x 30 days
  Verify current rates: https://aws.amazon.com/bedrock/pricing/
============================================================
```

> **Read the token counts, not just the rates.** Output tokens bill at five times the input rate on every current model, so how much a model writes moves the bill as much as which model you pick. That is why the prompt pins the response to three fields. Without that constraint a model is free to explain itself at length, which costs more and can exceed `max_tokens` and truncate the JSON.

> **Current pricing:** The `PRICING` dict in `compare_models.py` reflects rates at time of writing. Verify at https://aws.amazon.com/bedrock/pricing/ before making production cost decisions.

### Step 9: The Model Selection Decision

Look back at your own output and answer three questions.

**1. Did the models disagree?** Compare the three classifications. On a well-specified task like this one, they usually agree. If yours did, that is the finding, not a failure of the exercise.

**2. What does Haiku cost against Sonnet?** Read the two monthly figures from the projection table. For the same answer, Haiku normally costs about one twentieth of what Sonnet does.

**3. Opus charges double Sonnet's rate. Does your monthly figure show the same gap?** Compare the Opus and Sonnet monthly figures, then look at the input and output token counts for each model before you answer.

<details>
<summary>What the third question is getting at</summary>

Cost is rate multiplied by tokens. Here the tokens are almost identical: Sonnet and Opus report the same input count and wrote a similar number of output tokens. With the token counts matched, the rate card decides, so Opus lands about twice Sonnet, the same gap as its rates ($4 and $20 per million tokens against $2 and $10). If Opus happens to write noticeably more in your run, the gap widens.

Two things follow. The rate card only predicts the bill when the models write about the same amount, so a measured run is the way to check. And constraining the response, as the prompt in this lab does by naming exactly three keys, is what keeps the token counts level. Output tokens bill at five times the input rate, so a model that writes twice as much can cost as much as a model with double the rate.

Cost is not the only number that moves. In this lab's runs Haiku answered in about a second, Opus in one and a half to two seconds, and Sonnet was the slowest every time. Latency does not follow price, so measure it for your own workload.

All three models report the same input count, 167 tokens, because they share a tokenizer, so their token counts compare directly. That is not true across older generations: Haiku 4.5, for example, reports fewer input tokens for the same prompt because it tokenizes text differently.
</details>

There is no single right answer to the decision itself. The point is that you now have measured data rather than a guess, and you know which three things move the number.

---

## Part 5: RAG with the Shared Knowledge Base

Your instructor has created a shared Knowledge Base loaded with sample e-commerce product documentation. You do not create your own. This is the production pattern: developers consume an existing Knowledge Base rather than provisioning their own infrastructure. Your job is to connect to it and run queries against it.

### Step 10: Connect to the Knowledge Base

The verify script finds the shared Knowledge Base by name, confirms it is ready, and saves its ID for this lab and for Lab 3. There is no ID to copy and no file to edit.

```bash
python scripts/verify_knowledge_base.py
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
  Sync status:         COMPLETE
  Documents synced:    5

  ✅ Knowledge Base is ACTIVE
  ✅ Knowledge Base has a data source
  ✅ Last sync completed
  ✅ All 5 documents synced with none failed

All 4 checks passed! ✅
Knowledge Base ID saved for Lab 1 and Lab 3.
```

> **"No Knowledge Base found"?** Your instructor shares the Knowledge Base ID in the course chat. Run `python scripts/verify_knowledge_base.py --kb-id ABCDEF1234`, replacing `ABCDEF1234` with that ID.

> **Status shows anything other than ACTIVE?** Ask your instructor. The shared Knowledge Base may still be provisioning.

> **AccessDeniedException?** Your SSO role may be missing `bedrock-agent:*` permissions. Ask your instructor.

### Step 11: Explore the Query Script

In VS Code, open `scripts/query_knowledge_base.py`. There is nothing to edit. Find each item in the table.

| Find this | What to notice |
|-----------|----------------|
| `retrieve_chunks()` | Step one of RAG: `retrieve()` returns the best-matching chunks, each with a relevance score from 0 to 1. |
| `generate_answer()` | Step two: the chunks go to Claude as context, and Claude writes the answer. |
| The `prompt` in `generate_answer()` | "Only use information from the provided sources." This line keeps the answer grounded. |
| `build_citations()` | Each source file is listed once, with its highest score. |
| `run_demo()` | The four questions you run next, and the checks on what comes back. |

Retrieval and generation are separate calls, so you can see the relevance score for every chunk before Claude writes a word. That is what makes the citations auditable.

### Step 12: Run the Four Questions

```bash
python scripts/query_knowledge_base.py --demo
```

The script asks four questions and checks the results. Retrieval scores come from the embedding model, so they stay steady from run to run. The wording of each answer will vary.

**Expected output:** (answers shortened here)
```
============================================================
  1. A question the documents answer
============================================================

Query: What is the return policy for damaged products?

Answer:
## Return Policy for Damaged Products
...
- **Return Window:** Damaged products may be returned within **60 days** of purchase
...

Citations:
  [1] return-policy.txt (score: 0.71)
  [2] support-procedures.txt (score: 0.41)
  [3] warranty-coverage.txt (score: 0.39)

============================================================
  2. The same question, asked vaguely and then specifically
============================================================

Query: How do I return something?
...
Citations:
  [1] return-policy.txt (score: 0.47)
...

Query: What is the step-by-step process for initiating a product return, including required documentation and timelines?
...
Citations:
  [1] return-policy.txt (score: 0.74)
...

============================================================
  3. A question the documents do not answer
============================================================

Query: What is the CEO's favorite color?
...
Citations:
  [1] ... (score: 0.35)
...

============================================================
  Self-Check
============================================================
  ✅ Top citation for the damaged-products question is return-policy.txt
  ✅ That top score is 0.60 or higher
  ✅ The answer states the 60-day window found in the source
  ✅ The specific question scores at least 0.20 above the vague one (gap +0.27)
  ✅ Every score for the out-of-scope question is 0.40 or lower

All 5 checks passed! ✅
```

### Step 13: Read the Results

Use your output to answer each question.

**Citation accuracy (question 1).**
- Does Claude's answer match what `return-policy.txt` says?
- Did Claude add anything the citations do not support?
- Which document scored highest, and does that make sense for the query?

Relevance scores range from 0 to 1. A score below 0.5 often signals weak retrieval: the system found something, but it may not be directly relevant.

> **Citations are not decoration.** In production applications, especially regulated ones, citations are the audit trail. A high-quality RAG system traces every claim to a source. If you cannot verify a claim against its citation, the system is hallucinating.

**Query phrasing (question 2).** The vague question's top score was about 0.47 and the specific question's was about 0.74, both from `return-policy.txt`. The same underlying question scored about 0.27 higher when it was specific.

> **Why this matters in production:** Users ask vague questions. Your application should preprocess or expand queries before sending them to the retrieval layer. You will implement this pattern in Lab 3.

**The boundary (question 3).** The CEO question is not in any document. Claude should say it does not have that information, and every score sits at about 0.35, which is the lowest value this scoring produces, so no document stands out.

This is correct behavior. A RAG system that answers out-of-scope questions confidently is more dangerous than one that says it does not know.

### Step 14 (Optional): Ask Your Own Question

Ask the Knowledge Base anything about the sample documents, such as returns, warranties, or product support:

```bash
python scripts/query_knowledge_base.py --query "How long is the warranty on electronics?"
```

Check the citations against the answer, the way you did in Step 13.

---

## What You Built

In 40 minutes, you:

- Invoked three Claude models programmatically and compared their output on a real support ticket classification task
- Extracted token counts and latency from API responses and calculated actual per-invocation cost
- Scaled those costs to production volumes to make a real model selection decision
- Saw an error handled as data so that one bad model does not stop a batch
- Connected to a shared Knowledge Base of e-commerce product documentation and queried it using the Bedrock API
- Ran RAG queries and evaluated citation accuracy, query phrasing, and out-of-scope behavior

**The Knowledge Base ID was saved for Lab 3 automatically.** Do not delete `.env`.

---

## Cleanup

The Knowledge Base and its OpenSearch vector store incur ongoing costs when left running. Your instructor will clean up shared resources after class.

---

*Lab 1 Complete*
