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
## Part 1: Setup and Connect to Bedrock

### Before beginning this lab, verify if you already have Claude Code installed on your device. Open your terminal and run:

```bash
claude --version
```

If Claude responds with a version number like 2.1.116 (Claude Code), you can skip to Step 2. Otherwise, proceed to Step 1.

### Step 1: Install Claude Code

Open your terminal and run:

```bash
npm install -g @anthropic-ai/claude-code
```

> **Already installed?** Skip to Step 2.

### Step 2: Launch Claude Code

```bash
mkdir claude-code-lab && cd claude-code-lab
claude
```

**Expected Result:** Claude Code starts and shows a prompt.

### Step 2:Configure the Amazon Bedrock Backend

From Claude Code, set these environment variables to route Claude Code through your AWS Bedrock account:

```
set CLAUDE_CODE_USE_BEDROCK=1
set AWS_REGION=us-east-1
```

> **Note:** Claude will prompt you for your preferred settings update session variables. Choose your preferences and proceed.

### Step 3:Verify the API Provider is now Amazon Bedrock

```
/status
```

> **Note:** Ensure your API provider is now: Amazon Bedrock. The next status line should show the AWS region is us-east-1.

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

**Expected Result:** Claude Code reads your existing `invoke_claude` function and creates a complementary `query_bedrock` function that matches the same patterns — same error handling, same style, same imports. At this point your CLI is getting busy, consider resizing the window, zooming in out out, and scrolling through the results at will.

> **Key Observation:** Claude Code didn't just generate a snippet — it read your existing code and matched its patterns. That's the agentic difference.

### Step 7: Add Tests

```
Write unit tests for both functions. Mock the boto3 client.
```

**Expected Result:** Claude Code creates a test file, runs the tests, and shows the results. If a test fails, watch it fix the code and re-run automatically.

---

## Part 4: Explore Features

### Step 8: Check Memory

Claude maintains multiple memory settings, which you can prompt Claude to show in your default text editor via the /memory command:

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

### Step 9: Close any open memory files to return to Claude Code

---

## Part 5: Working Effectively

### Step 10: Interrupt and Steer

Try this: Start typing a request, then change your mind mid-execution. This will take some dexterity as you want to 

```
Refactor the invoke_claude function to use async/await
```

**While Claude is working**, immediately type:

```
Actually, keep it synchronous but add retry logic with exponential backoff
```

**Expected Result:** Claude stops its current approach mid-execution and pivots to your new direction.

> **Key Point:** Interrupting Claude isn't rude, it's how you collaborate efficiently. Feel free to course-correct in real-time.

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

Trust Claude to figure out implementation details. You may be asked to install common python utilities like pip, and take note of how Claude will always ask about your installation preferences to ensure there are no surprises.

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

The .devcontainer/ folder in the course repo has a pre-built example.
In the next three steps you will use Claude Code to inspect it, investigate
a firewall rule, and audit it for security issues.

---

### Step 13: Inspect the Devcontainer Config

Ask Claude Code to read and explain the provided configuration:

```bash
Read the files in .devcontainer/ and explain what each one does
and why it matters for a production Claude Code deployment.
```

Expected Result: Claude Code reads devcontainer.json and init-firewall.sh
and explains each setting — the sandboxed AWS credential mount, the
environment variables, and the firewall initialisation script.

> **Key Insight:** Notice the mounts entry in devcontainer.json. It points to ~/.aws/sandbox rather than ~/.aws. This means the container gets sandbox credentials only — not your production AWS account.

---

### Step 14: Investigate the Firewall Rule

Point Claude Code at a specific section of the firewall script and ask it to explain:

```bash
Read the files in .devcontaLook at the ALLOW rules in .devcontainer/init-firewall.sh.
Pick one rule and explain it in plain English. What traffic does
it allow? What would happen if it were removed?
```

Expected Result: Claude Code explains the selected rule — for example,
the Bedrock rule allows outbound HTTPS only to the Bedrock endpoint in
us-east-1. Without it, Claude Code could not call the model at all.

> **Key Insight:** Each ACCEPT rule is intentional and minimal. This is why --dangerously-skip-permissions becomes safe inside a devcontainer. Claude Code can edit files freely, but it cannot reach arbitrary internet endpoints even if it tried.

---

### Step 15: Validate the Environment Security

Now ask Claude Code to audit the full configuration for security issues:

```bash
Review .devcontainer/init-firewall.sh for security issues.
Are there any missing rules, over-permissive settings, or gaps
that could expose the host environment?
```

Expected Result: Claude Code identifies the flaw — the script whitelists
specific endpoints but never sets a default DROP rule for unmatched outbound
traffic. Without it, any traffic that does not match an ACCEPT rule falls
through to the system default, which may be ACCEPT rather than DROP.

The fix is one line added at the end of the whitelist rules:

```bash
# Block all other outbound traffic
iptables -A OUTPUT -j DROP
```

> **Key Insight:** Claude Code can function as a security review tool, not just a code generator. Asking it to audit infrastructure config before committing to git catches gaps a manual review might miss.

---

When to Use Devcontainers
Use devcontainers when:

Team deployments requiring consistency.
CI/CD automation with Claude Code.
Untrusted or shared repositories.
Regulated environments (SOC 2, HIPAA, FedRAMP).

Not required when:

Solo development on personal trusted projects.
Quick experiments (like this lab).

---

## Cleanup

No AWS resources were created in this. You can safely delete the project folder.

---

*Lab 2 Complete*
