# Lab 2: Claude Code on Bedrock

**Course:** Anthropic Models on AWS Bedrock  
**Duration:** 35 minutes

---

## Objectives

By completing this lab, you will:

1. Install and launch Claude Code connected to Amazon Bedrock
2. Use CLAUDE.md to enforce project-wide coding and writing standards
3. Scaffold a Bedrock function using natural language
4. Experience agentic workflows, memory systems, and collaboration techniques
5. Understand production deployment strategies with development containers

---

## Prerequisites

- [ ] Terminal / command line access on your workstation
- [ ] AWS credentials configured (`aws configure` done)
- [ ] Node.js 18+ installed (check: `node --version`)

**Course Repository:** **https://github.com/AWSClassroom-com/anthropic_on_aws**

---
## Before beginning this lab, verify if you already have Claude Code installed on your device. Open your terminal and run:

```bash
claude --version
```

If Claude responds with a version number like 2.1.116 (Claude Code), you can skip to Step 2. Otherwise, proceed to Step 1.

## Part 1: Setup and Connect to Bedrock

### Step 1: Install Claude Code

Open your terminal and run:

```bash
npm install -g @anthropic-ai/claude-code
```

> **Already installed?** Skip to Step 2. Your instructor may have pre-installed this on training workstations.

### Step 2: Configure Bedrock Backend

Set these environment variables to route Claude Code through your AWS Bedrock account:

**macOS/Linux:**
```bash
export CLAUDE_CODE_USE_BEDROCK=1
export AWS_REGION=us-east-1
```

**Windows (PowerShell):**
```powershell
$env:CLAUDE_CODE_USE_BEDROCK=1
$env:AWS_REGION="us-east-1"
```

> **Note:** `AWS_REGION` is required. Claude Code does not read from `.aws/config` for this setting.

### Step 3: Launch Claude Code

```bash
mkdir claude-code-lab && cd claude-code-lab
claude
```

**Expected Result:** Claude Code starts and shows a prompt. Type `/status` to verify Bedrock connection.

> **Troubleshooting:** If you see an authentication error, verify `aws sts get-caller-identity` returns your training account. Ask your instructor for help.

---

## Part 2: CLAUDE.md — Project-Wide Standards

### Concept: Persistent Memory for Teams

**CLAUDE.md** is Claude Code's persistent memory system. Unlike conversation memory (which lives in one session), CLAUDE.md:

- Persists across sessions and restarts
- Can be committed to git (team-wide standards)
- Controls both code conventions AND writing style
- Works like a `.editorconfig` file for AI

### Step 4: Create CLAUDE.md with Code + Writing Standards

Without exiting Claude Code, type:

```
Create a CLAUDE.md file for a Bedrock application project. It should specify:

CODE CONVENTIONS:
- Use the Bedrock Invoke API for all model calls
- All functions need type hints
- Region is us-east-1
- Never hardcode credentials

WRITING STYLE:
- FORBIDDEN: Never use em dashes (—). Replace with periods or commas.
- Use active voice in documentation
- Keep docstrings under 3 sentences
```

**Expected Result:** Claude Code creates a `CLAUDE.md` file in your project directory with both code and writing conventions.

> **Key Insight:** CLAUDE.md isn't just for code — it enforces ANY team convention (commit messages, error message style, API naming, etc.).

### Step 5: Verify Both Standards Work

Now ask Claude Code to generate code and watch it follow BOTH sets of rules:

```
Create a function called invoke_claude that takes a prompt string and 
returns the response text. Include type hints and a docstring.
```

**Check the output:**
- Uses type hints (`: str`, `-> str`)
- Uses Bedrock Invoke API (not Messages API)
- Region is us-east-1
- No hardcoded credentials
- No em dashes in docstring
- Active voice ("Invokes the model" not "The model will be invoked")
- Under 3 sentences

> **Important:** This file persists across sessions. If you restarted Claude Code right now, it would still follow these rules. That's why it's perfect for team environments — check CLAUDE.md into git and everyone gets the same standards.

---

## Part 3: Agentic Workflows

### Step 6: Scaffold a RAG Function

```
Add a function called query_bedrock that takes a prompt string and model_id, 
returns the response using boto3 bedrock-runtime client.
```

**Expected Result:** Claude Code reads your existing `invoke_claude` function and creates a complementary `query_bedrock` function that matches the same patterns — same error handling, same style, same imports.

> **Key Observation:** Claude Code didn't just generate a snippet — it read your existing code and matched its patterns. That's the agentic difference.

### Step 7: Add Tests

```
Write unit tests for both functions. Mock the boto3 client.
```

**Expected Result:** Claude Code creates a test file, runs the tests, and shows the results. If a test fails, watch it fix the code and re-run automatically.

---

## Part 4: Explore Features

### Step 8: Check Memory

```
/memory
```

**Observe:** Claude Code has already saved context about your project — the CLAUDE.md conventions, the functions you created, your preferences.

**Two Memory Systems:**

| Memory Type | Scope | Persists | Use Case |
|-------------|-------|----------|----------|
| **CLAUDE.md** | Project-wide | Across restarts | Team standards (code, style, architecture) |
| **Auto memory** | Session | Within session | Your preferences, project context, conversation history |

**Why both?**
- CLAUDE.md = Shared team standards (commit to git)
- Auto memory = Personal workflow preferences (stays local)

### Step 9: Check Permissions

Press `Shift+Tab` to cycle through permission modes:
- **Default** → Claude asks before editing files
- **Auto-accept edits** → Claude edits without asking
- **Plan mode** → Claude plans without executing

---

## Part 5: Working Effectively

### Step 10: Interrupt and Steer

Try this: Start typing a request, then change your mind mid-execution.

```
Refactor the invoke_claude function to use async/await
```

**While Claude is working**, immediately type:

```
Actually, keep it synchronous but add retry logic with exponential backoff
```

**Expected Result:** Claude stops its current approach mid-execution and pivots to your new direction.

> **Key Point:** Interrupting isn't rude — it's how you collaborate efficiently. Course-correct in real-time.

### Step 11: Provide Verification Criteria

Claude performs better when it can check its own work.

```
Create a function validate_bedrock_region that checks if a region supports Bedrock.
Test cases:
- 'us-east-1' → True
- 'invalid-region' → False
Run tests after implementing.
```

**Expected Result:** Claude writes the function, creates tests with your exact test cases, runs them, and reports results. If any tests fail, it fixes automatically.

> **Key Learning:** Test cases upfront = Claude can self-verify without asking "does this look right?"

### Step 12: Delegate, Don't Dictate

Trust Claude to figure out implementation details.

```
The invoke_claude function should handle rate limiting from Bedrock.
When we hit ThrottlingException, it should wait and retry. Can you add this?
```

**Expected Result:** Claude:
1. Reads the function to understand current implementation
2. Searches for boto3 exception handling patterns
3. Implements retry logic
4. Tests the implementation
5. Reports what it did

> **Key Insight:** You provide the WHAT and CONTEXT. Claude figures out the HOW.

---

## Part 6: Production Deployment

### The Challenge

When Claude Code runs on your laptop, it has access to:
- Your AWS credentials (including production accounts)
- Your entire filesystem
- Network access to any service
- Git credentials and SSH keys

**How do you deploy this safely to a team?**

### The Solution: Development Containers

A devcontainer runs Claude Code in an isolated sandbox with:

1. **Firewall rules** → Only allow Bedrock, npm, GitHub (block everything else)
2. **Credential isolation** → Mount only sandbox AWS credentials (not production)
3. **Reproducible environments** → Everyone gets identical setup

**Key Architecture:**

```
.devcontainer/
├── devcontainer.json    # Container configuration
├── Dockerfile           # Image definition with Claude Code installed
└── init-firewall.sh     # Network security rules (whitelist only)
```

**Why This Matters:**

The firewall + sandboxed credentials make it safe to run `claude --dangerously-skip-permissions`, which enables:
- Faster development (no permission prompts)
- Claude Code in CI/CD pipelines
- Team onboarding (5-minute setup)
- Multi-client isolation (separate containers per client)

### When to Use Devcontainers

**Use devcontainers when:**
- Team deployments requiring consistency
- CI/CD automation
- Untrusted repositories
- Multi-tenancy / client isolation
- Regulated environments (SOC 2, HIPAA, FedRAMP)

**Don't need devcontainers when:**
- Solo developer on trusted personal projects
- Quick experiments or learning (like this lab)
- Already using VM-based sandboxing

### Production Readiness Checklist

Before deploying Claude Code + Bedrock to production:

- [ ] Devcontainer with firewall configured
- [ ] Sandbox AWS credentials (not production)
- [ ] CLAUDE.md with team standards checked into git
- [ ] CloudWatch monitoring + cost alerts
- [ ] Bedrock Guardrails configured

---

## What You Built

In 35 minutes, you:

**Technical Skills:**
- Configured Claude Code to route through Amazon Bedrock
- Created CLAUDE.md with project-wide coding AND writing standards
- Scaffolded Bedrock API integration using natural language
- Generated and ran tests with automatic error fixing
- Understood two memory systems (CLAUDE.md vs auto memory)

**Collaboration Skills:**
- Learned to interrupt and steer Claude in real-time
- Used verification criteria (test cases) to improve first-attempt quality
- Delegated implementation details instead of micromanaging

**Production Skills:**
- Understood the devcontainer architecture for safe deployment
- Learned when devcontainers enable safe `--dangerously-skip-permissions` usage
- Created a production readiness checklist

**Key Insights:**

1. **CLAUDE.md is persistent team memory** → Coding standards that survive across sessions and can be committed to git
2. **Claude Code is conversational and agentic** → Treat it like a capable colleague, not a rigid tool
3. **Devcontainers enable safe automation** → Firewall + sandboxed credentials = production-ready

Everything you built manually in Labs 1 and 2 — Claude Code can help you build faster **with the same quality and governance**.

---

## Cleanup

No AWS resources were created in this mini-lab. You can delete the project directory:

```bash
cd .. && rm -rf claude-code-lab
```

---

*Lab 2 Complete*
