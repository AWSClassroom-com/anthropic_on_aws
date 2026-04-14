# Mini-Lab: Claude Code on Bedrock

**Course:** Building AI Applications with Anthropic on AWS Bedrock
**Duration:** 20 minutes
**Follows:** Module 8 (Claude Code lecture + demo)

---

## Objectives

By completing this mini-lab, you will:

1. Install and launch Claude Code connected to Amazon Bedrock
2. Use CLAUDE.md to steer AI-generated code
3. Scaffold a Bedrock function using natural language
4. Experience memory, permissions, and hooks firsthand

---

## Prerequisites

- [ ] Module 8 lecture completed
- [ ] Terminal / command line access on your workstation
- [ ] AWS credentials configured (`aws configure` done)
- [ ] Node.js 18+ installed (check: `node --version`)

**Course Repository:** [github.com/AWSClassroom-com/anthropic_on_aws](https://github.com/AWSClassroom-com/anthropic_on_aws)

---

## Part 1: Setup and Connect to Bedrock

### Step 1: Install Claude Code

Open your terminal and run:

```bash
npm install -g @anthropic-ai/claude-code
```

> **Already installed?** Skip to Step 2. Your instructor may have pre-installed this on training workstations.

### Step 2: Configure Bedrock Backend

Set these environment variables to route Claude Code through your AWS Bedrock account:

```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
```

### Step 3: Launch Claude Code

```bash
mkdir claude-code-lab && cd claude-code-lab
claude
```

**Expected Result:** Claude Code starts and shows a prompt. Type `/status` to verify Bedrock connection.

> **Troubleshooting:** If you see an authentication error, verify `aws sts get-caller-identity` returns your training account. Ask your instructor for help.

---

## Part 2: CLAUDE.md — Project Steering

### Step 4: Create a CLAUDE.md File

Without exiting Claude Code, type:

```
Create a CLAUDE.md file for a Bedrock application project. It should specify:
- Use the Converse API for all model calls
- All functions need type hints
- Region is us-east-1
- Never hardcode credentials
```

**Expected Result:** Claude Code creates a `CLAUDE.md` file in your project directory with the conventions you specified.

### Step 5: Verify Steering Works

Now ask Claude Code to generate code and watch it follow the CLAUDE.md rules:

```
Create a function called invoke_claude that takes a prompt string and returns the response text. Use boto3.
```

**Check:** Does the generated code use the Converse API (not Messages API)? Does it have type hints? Is the region us-east-1? If yes — CLAUDE.md is steering the output.

---

## Part 3: Agentic Workflows

### Step 6: Scaffold a RAG Function

```
Add a function called query_knowledge_base that takes a query string and a knowledge_base_id, calls Bedrock's retrieve_and_generate API, and returns the answer with citations.
```

**Expected Result:** Claude Code reads your existing `invoke_claude` function and creates a complementary `query_knowledge_base` function that matches the same patterns — same error handling, same style, same imports.

> **Key Observation:** Claude Code didn't just generate a snippet — it read your existing code and matched its patterns. That's the agentic difference.

### Step 7: Add Tests

```
Write unit tests for both functions. Mock the boto3 client.
```

**Expected Result:** Claude Code creates a test file, runs the tests, and shows the results. If a test fails, watch it fix the code and re-run.

---

## Part 4: Explore Features

### Step 8: Check Memory

```
/memory
```

**Observe:** Claude Code has already saved context about your project — the CLAUDE.md conventions, the functions you created, your preferences.

### Step 9: Check Permissions

```
/permissions
```

**Observe:** See what actions Claude Code is allowed to take without asking. In a team setting, these would be configured in `.claude/settings.json` and committed to the repo.

### Step 10: Try Extended Thinking

```
/thinking

Design an architecture for deploying this as a serverless API with guardrails, monitoring, and multi-region failover.
```

**Observe:** With thinking enabled, Claude Code reasons through the architecture step by step before responding. Compare the depth to a quick response without thinking.

---

## What You Built

In 20 minutes, you:

- Connected Claude Code to Bedrock (3 commands)
- Used CLAUDE.md to steer code generation (project conventions)
- Scaffolded a RAG function that matched existing code patterns (agentic)
- Generated and ran tests automatically
- Explored memory, permissions, and extended thinking

Everything you built manually in Labs 1 and 2 — Claude Code can help you build faster with the same quality and governance.

---

## Cleanup

No AWS resources were created in this mini-lab. You can delete the project directory:

```bash
cd .. && rm -rf claude-code-lab
```

---

*Mini-Lab Complete*
