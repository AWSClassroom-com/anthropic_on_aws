# Lab 2: Claude Code on Bedrock

**Course:** Anthropic Models on AWS Bedrock
**Duration:** 65 minutes

---

## The Problem You Are Solving

This lab introduces a different way to work. Claude Code is an agentic developer tool that reads your project, writes code, runs tests, and fixes failures without you stepping through each action manually.

But knowing how to operate Claude Code is not the same as knowing how to work with it effectively on a real project. This lab covers both. You will plan a Bedrock integration before writing a single line of code, build it iteratively with team-wide standards enforced automatically, understand how to recover safely when generated code goes wrong, and leave with a production-ready devcontainer configuration and a reusable debugging skill.

---

## Objectives

By completing this lab, you will:

1. Install and launch Claude Code connected to Amazon Bedrock
2. Use Plan mode and model switching to plan before you build
3. Use CLAUDE.md to enforce project-wide coding and writing standards
4. Scaffold and iterate on a Bedrock integration using agentic workflows
5. Understand how to use git safely with AI-generated code
6. Manage session context using /compact and /clear
7. Create a reusable Claude Code skill
8. Inspect, audit, and improve a production devcontainer configuration

---

## Prerequisites

- [ ] AWS login completed (`aws login` done, `aws sts get-caller-identity` returns your account)
- [ ] Terminal access on your workstation

> **Course repository location:** The course repo was cloned in Lab 1 and is at `~/anthropic_on_aws/` on macOS/Linux and `$env:USERPROFILE\anthropic_on_aws\` on Windows. You will need this path in Part 7. If you cloned it elsewhere, note your actual path.

**Course Repository:** **https://github.com/AWSClassroom-com/anthropic_on_aws**

---

## Part 1: Setup and Connect to Bedrock

Claude Code authenticates using your AWS credentials and routes model calls through Amazon Bedrock. The setup wizard handles all of this interactively on first launch.

> **Optional:** Setting `AWS_REGION=us-east-1` in your terminal before launching pre-fills the region field in the wizard.

**macOS/Linux:**
```bash
export AWS_REGION=us-east-1
```

**Windows (PowerShell):**
```powershell
$env:AWS_REGION="us-east-1"
```

### Step 1: Confirm AWS Credentials Are Active

```bash
aws sts get-caller-identity
```

**Expected result:** Your account ID and IAM user ARN. If this fails, run `aws login` and complete the browser prompt before continuing.

### Step 2: Install Claude Code

Make a folder off the root directory for this lab:

```bash
cd /
mkdir claude-code-lab
cd claude-code-lab
```

Check whether Claude Code is already installed:

```bash
claude --version
```

If a version number appears, skip to Step 3.

If not, install using the native installer:

**macOS/Linux:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows (CMD):**
```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

> **Native install is recommended.** It auto-updates in the background and avoids permission issues.

> **Fallback -- install via npm:** If the native installer is not available, run `npm install -g @anthropic-ai/claude-code`. Do not use `sudo npm install -g` -- this causes permission issues.

### Step 3: Add Claude to Your PATH (Windows only)

The Claude Code installer does not automatically add the executable to your PATH to avoid unintended shell override issues. On Windows, you need to add it manually so the `claude` command is available in any terminal session.

**Windows (PowerShell or CMD):**
```powershell
setx PATH "%PATH%;C:\Users\%USERNAME%\.local\bin"
```

**Close and reopen your terminal** after running this command. `setx` writes to the permanent user environment variables but the change only takes effect in new terminal sessions.

Verify Claude is now on your PATH:
```powershell
claude --version
```

**Expected result:** A version number. If you see `claude is not recognized`, confirm the terminal was fully closed and reopened, not just refreshed.

> **macOS/Linux:** The native installer adds Claude to your PATH automatically. Skip this step.

### Step 4: Launch Claude Code

**macOS/Linux:**
```bash
claude
```

**Windows (PowerShell):**
```powershell
claude
```

**The setup wizard runs on first launch.** Work through each prompt:

1. **Choose a display mode** -- select light or dark, your preference
2. **Select login method** -- select **3. 3rd-party platform**
3. **Select platform** -- select **1. Amazon Bedrock**
4. **How do you authenticate to AWS?** -- select **1. AWS profile (SSO or named profile)**
5. **AWS profile** -- select **1. default**
6. **AWS region** -- type `us-east-1` and press Enter
7. **Verification** -- wizard confirms your IAM user and lists available inference profiles. Select **1. Continue**
8. **Pin model versions** -- read the models shown before selecting.

   > **Are you in us-east-1?** If the Sonnet model shown is `us.anthropic.claude-sonnet-4-6`, select **1. Pin the working models** and continue to step 9.

   > **Not in us-east-1, or Sonnet shows a different version?** Select **3. Choose different models...** and update Sonnet to `us.anthropic.claude-sonnet-4-6`. Confirm the existing Opus and Haiku models are unchanged. You are returned to the same screen. Now select **1. Pin the working models**.
9. **Confirm and save** -- select **1. Save**
10. **Press Enter** to restart Claude Code

> **SSO session expiry:** SSO sessions last approximately 8 hours. If Claude Code stops working, run `aws sso login --profile default` and Claude Code picks up the refreshed credentials automatically.

> **Troubleshooting:** If verification fails, run `aws sts get-caller-identity`. If that fails, run `aws login` and relaunch.

### Step 5: Verify Bedrock is Active

```
/status
```

**Expected result:** Amazon Bedrock shown as API provider, `us-east-1` as region.

Now confirm the actual model string:

```
/model
```

**Expected result:** The full inference profile ID such as `us.anthropic.claude-sonnet-4-6`. The Claude Code screen shows a human-readable label but `/model` shows the actual string sent to Bedrock. Use `/model` any time you need to confirm the exact model in use.

> **If /status shows the Anthropic API instead of Bedrock:** Type `/logout`, relaunch `claude`, and select option 3 (3rd-party platform) at the login method screen.

### Step 6: Name Your Session

```
/rename lab2-session
```

Use any name you prefer. To resume this session if your terminal closes or your SSO expires:

**macOS/Linux:**
```bash
claude --resume lab2-session
```

**Windows (PowerShell):**
```powershell
claude --resume lab2-session
```

> **Why this matters:** If your SSO session expires mid-lab, run `aws sso login --profile default` in a new terminal, then `claude --resume lab2-session` to return exactly where you left off.

### Step 7: (Informational) Approve File and Command Permissions

In upcoming lab steps, Claude Code will ask for permission before creating files and running commands. You will see two prompt types during this lab:

**File edit prompt:**
```
Do you want to make this edit to filename.py?
1. Yes
2. Yes, allow all edits during this session (shift+tab)
3. No
```

**Bash command prompt:**
```
This command requires approval. Do you want to proceed?
1. Yes
2. Yes, and don't ask again for: python *
3. No
```

Select **option 2** for both when they first appear. This approves all file edits and Python commands for the rest of the session without interruption.

> Press Shift+Tab at any time to toggle permission mode.

---

## Part 2: (Informational) Plan Before You Build

### Concept: Why Standards Come First

Most developers jump straight to asking Claude Code to write code. This works for small tasks. For anything involving architecture decisions, multiple files, or significant refactoring, it produces code that technically works but may not be what you actually wanted.

The right sequence is: establish your standards first, then plan, then build. When CLAUDE.md exists before the plan is created, the plan output already reflects your conventions. When implementation follows the approved plan, every function is standards-compliant from the first line.

Model switching supports this. Claude Opus reasons more deeply about architecture, trade-offs, and edge cases. Claude Sonnet is faster and more cost-effective for iterative code edits once the thinking is done.

### Step 8: Create CLAUDE.md with Code and Writing Standards

Before planning or writing any code, establish the standards Claude Code will follow throughout this project:

```
Create a CLAUDE.md file for a Bedrock application project. It should specify:

CODE CONVENTIONS:
- Use the Bedrock Invoke API for all model calls
- All functions need type hints
- Region is us-east-1
- Never hardcode credentials

WRITING STYLE:
- FORBIDDEN: Never use em dashes. Replace with periods or commas.
- Use active voice in documentation
- Keep docstrings under 3 sentences
```

**Expected Result:** Claude Code creates a `CLAUDE.md` file in your working directory. Open it and read through it before continuing.

> **Key insight:** CLAUDE.md is not limited to code conventions. Commit message formats, error message tone, API naming patterns -- any team standard that can be described in plain language belongs here. Because CLAUDE.md is created before the plan, the plan output will already reflect these conventions.

### Step 9: Switch to Opus for Planning

```
/model
```

Note your current model. Then switch to Opus:

```
/model opus
```

Confirm the switch:

```
/model
```

**Expected result:** The model string now shows the Opus inference profile.

> **Cost note:** Opus costs significantly more per token than Sonnet. You will use it for one planning step only, then switch back. Check current rates at https://aws.amazon.com/bedrock/pricing/

### Step 10: Activate Plan Mode and Create the Project Plan

Activate Plan mode by pressing **Shift+Tab** twice to cycle to Plan mode, or type:

```
/plan
```

Now submit the planning request:

```
I am building a Bedrock integration project with the following requirements:

- A function to invoke Claude models via the Bedrock Invoke API
- A function to query a Bedrock Knowledge Base using retrieve_and_generate
- Unit tests for both functions with mocked boto3 clients
- All functions must use type hints
- Region is us-east-1
- No hardcoded credentials

Before writing any code, create a detailed plan covering:
1. File structure
2. Function signatures and return types
3. Error handling strategy
4. Testing approach
5. Any dependencies needed

Do not create any code without my implicit instruction to build.
```

**Expected result:** Claude Code produces a detailed plan that already reflects your CLAUDE.md conventions -- type hints, region, no hardcoded credentials. It does not write any code yet.

Read the plan carefully. At this point in the development lifecycle, if anything needs changing, you would change it now before execution begins. This is the cheapest time to change direction.

<details>
<summary>What good plan output looks like</summary>

A well-structured plan from Opus will typically include:

- Context and proposed file structure (e.g. `bedrock_client.py`, `knowledge_base.py`, `test_bedrock_client.py`)
- Dependencies and function signatures with typed parameters and return types
- Specific exception types to handle (`ClientError`, `ThrottlingException`)
- Implementation and test structure using `unittest.mock.patch` for boto3
- Any pip dependencies beyond the standard library
- Error handling strategy with mock patterns and verification

If a plan suggests a significantly different approach than you expect, this is the moment to redirect, before any files are created.
</details>

### Step 11: Tell Claude to wait and switch back to Sonnet

If the plan looks good, do not approve it using Opus! Instead, use option 3:

```
3. Do not execute this plan yet
```

The plan is auto-approved until executed OR you provide additional instructions OR you press shift+tab to exit plan mode. This last instruction allows you to pivot back to a more affordable model for actual code building that does not require the deep thinking Opus model.

Switch back to Sonnet now that Claude informs you "Understood. The plan is written and ready for your review at any time."

```
/model sonnet
```

Confirm:

```
/model
```

**Expected result:** Model string shows Sonnet inference profile. Claude Code will not implement the full plan -- both functions and tests -- using Sonnet.

> **Why switch back now:** Opus produced the architectural thinking. Sonnet executes it. Every line of code from this point forward uses Sonnet's speed and lower cost. The plan guides it -- the heavy reasoning is already done.

Execute the plan now, approving edits and python dependency installs as required:

```
Execute the plan
```

**Expected result:** All 8 planned tests pass, and a summary of what was created:

  - bedrock_client.py — invoke_model and query_knowledge_base with full type hints, dependency-injected clients, custom
  exceptions, and no hardcoded credentials
  - test_bedrock_client.py — 8 unit tests covering success paths, custom parameters, ClientError, BotoCoreError, and
  malformed responses
  - requirements.txt — boto3, botocore, pytest

---

## Part 3: Build with Standards

### Concept: Verify, Commit, Persist

The plan implementation produced your project files. Part 3 has three goals: verify the generated code follows your CLAUDE.md standards, commit the first working milestone, and prove CLAUDE.md persists across session restarts.

### Step 12: Verify the Generated Code Against CLAUDE.md

Open `bedrock_client.py` in the tool of your choice and check the output against each CLAUDE.md rule:

- Type hints on all parameters and return types
- Bedrock Invoke API used, not the Messages API
- Region is us-east-1
- No hardcoded credentials
- No em dashes in docstrings
- Active voice in docstrings
- Docstrings under 3 sentences

> **If a rule was not followed:** Say "Rewrite the [function name] function following the CLAUDE.md standards." The standards were in place before the plan was created, so Claude Code should have followed them. If it did not, the rewrite prompt corrects it.

### Step 13: (Best Practice) Commit Your First Working Milestone

You now have an implementation boilerplate that follows your standards. This is a natural commit point.

> **Git and AI-generated code:** In a production environment, you would commit working code before asking Claude Code to make significant changes. If the next change breaks something, `git checkout` reverts you cleanly to this working state. AI-generated code is fast but not always correct -- git is your safety net.
>
> The workflow is: **get to working code, commit, then ask for the next change.** Never ask Claude Code to make a significant change to code you have not committed. You cannot cleanly undo what you cannot cleanly revert.
>
> Training VMs in this environment do not have git configured for commits. In your own environment, this would be: `git add . && git commit -m "Implement Bedrock integration from approved plan"`

### Step 14: Verify CLAUDE.md Persists Across Restarts

This step proves CLAUDE.md is persistent, not just a conversation setting.

Type `/exit` to quit Claude Code, then relaunch in the same directory:

**macOS/Linux:**
```bash
claude --resume lab2-session
```

**Windows (PowerShell):**
```powershell
claude --resume lab2-session
```

Now ask for a new function that was not in the original plan:

```
Add a function called check_model_access that takes a model_id string
and returns True if the model is accessible in us-east-1, False otherwise.
```

**Expected Result:** The new function follows the same CLAUDE.md conventions as the plan-generated code -- same type hints, same docstring style, same error handling approach -- without you restating the rules.

> **This is the proof point:** CLAUDE.md persisted through a session restart and is still steering output for code that was not part of the original plan. That is what makes it a team tool rather than a personal preference.

---

## Part 4: Iterate with Confidence

### Step 15: Add Tests

```
Write unit tests for both functions in bedrock_client.py. Mock the boto3 client.
```

**Expected Result:** If you plan did not include instructions to create tests, Claude Code creates a test file with unit tests for both functions.

> **Note:** Claude Code creates the test file. It may or may not run the tests automatically -- watch the output and follow any prompts if it asks for approval to run a bash command.

### Step 16: Commit Before a Risky Change

> **Before asking Claude Code to refactor existing code, commit what you have.**
>
> Refactoring is where AI-generated code most commonly goes wrong. Claude Code may change behavior it was not asked to change, introduce subtle bugs, or restructure code in a way that breaks downstream dependencies.
>
> The pattern: commit working tests, then ask for the refactor. If the refactor breaks something, you revert to the last commit and try a different approach.
>
> In your own (non-lab, real-world) environment: `git add . && git commit -m "Add unit tests for invoke_claude and query_knowledge_base"`

### Step 17: Interrupt and Steer

Submit this request:

```
Refactor the invoke_claude function to use async/await
```

Immediately after submitting, before Claude Code finishes, type:

```
Actually, keep it synchronous but add retry logic with exponential backoff
```

**Expected Result:** Claude Code stops the current approach and pivots to the new direction without completing the refactor you cancelled.

> **Key point:** Interrupting Claude Code mid-execution is how you course-correct efficiently. You do not need to wait for a wrong direction to finish before changing it.

### Step 18: Provide Verification Criteria

```
Create a function validate_bedrock_region that checks if a region supports Bedrock.
Test cases:
- 'us-east-1' should return True
- 'invalid-region' should return False
Run tests after implementing.
```

**Expected Result:** Claude Code writes the function, creates tests using your exact cases, runs them, and reports results. If a test fails it corrects the implementation and re-runs.

> **Key learning:** Test cases upfront give Claude Code a clear definition of done. Without them, Claude Code has to guess what correct looks like.

### Step 19: Delegate, Don't Dictate

```
The invoke_claude function should handle rate limiting from Bedrock.
When we hit ThrottlingException, it should wait and retry. Can you add this?
```

**Expected Result:** Claude Code reads the current implementation before acting. If retry logic with ThrottlingException handling already exists from the exponential backoff step, it will explain what is already there rather than duplicating it.

> **Key insight:** Claude Code reads and understands your existing code before acting. It does not blindly implement what you ask if the behavior already exists. This code comprehension is what makes it useful on real projects rather than just greenfield code.

### Step 20: Rollback When Things Go Wrong

> **When generated code breaks something, git is your recovery path.**
>
> The pattern when Claude Code produces a bad result:
>
> 1. Do not ask Claude Code to fix it -- you may be three layers deep in a broken state
> 2. Revert to your last known-good commit: `git checkout .`
> 3. Restart with a more specific prompt that constrains what Claude Code can change
>
> The most common mistake with AI-generated code is asking Claude Code to fix a broken change rather than reverting and starting over. Fixing compounds the problem. Reverting resets it.
>
> This is why the commit-before-change habit from Step 15 matters. You cannot revert to a commit that does not exist.

---

## Part 5: Manage Your Session

### Concept: Context Has a Cost

Every message, every function, every file Claude Code reads accumulates in the context window. By this point in the lab, your session carries everything from Parts 1-4. That context is useful for continuity -- but it also means every new request costs more tokens and takes slightly longer to process.

In production, unmanaged context leads to higher costs and eventually to Claude Code losing track of early conversation details as the window fills.

### Step 21: Compact Your Context

You have completed the core build. This is a natural point to summarize accumulated context before moving to the devcontainer work.

```
/compact Focus on the functions we built, the CLAUDE.md standards, and the test coverage. Discard the planning discussion.
```

**Expected Result:** Claude Code replaces the full conversation history with a focused summary. Your CLAUDE.md and files remain on disk unchanged. Only the conversation history is compressed.

> **When to use /compact:** At natural task boundaries -- when you finish one phase and start another. The instruction after `/compact` tells Claude Code what to preserve in the summary.

> **When to use /clear instead:** When starting a completely unrelated task in the same directory. `/clear` discards all history and starts fresh. Use it when the accumulated context is actively misleading rather than just large.

---

## Part 6: Skills

### Concept: Skills as Reusable Playbooks

CLAUDE.md defines conventions. Skills define procedures.

A skill is a `SKILL.md` file that gives Claude Code a detailed playbook for a specific task. When the skill is relevant, Claude Code loads it automatically. You can also invoke any skill directly with a `/slash-command`.

Skills persist across sessions and can be committed to git so the whole team shares the same playbooks. They load only when used, so long reference material costs nothing until needed.

### Step 22: Create a Bedrock Debug Skill

You will use this skill in Lab 3 whenever a test fails. Creating it now means you have a working debugging tool before you need it.

```
Create a project skill at .claude/skills/bedrock-debug/SKILL.md.

The skill should teach Claude Code to:
1. Read a Python traceback from a boto3 or Bedrock API call
2. Identify which Bedrock API operation failed
3. Check for the most common causes in this order:
   - Model ID missing inference profile prefix (us.)
   - Guardrail version not published
   - IAM permission missing for the operation
   - Wrong region
4. Suggest the corrected boto3 call with exact syntax
5. Explain why the original call failed

Name the skill bedrock-debug with description:
"Diagnose and fix Bedrock API errors from Python tracebacks.
Use when a boto3 or Bedrock call fails with ValidationException,
AccessDeniedException, or ResourceNotFoundException."
```

**Expected Result:** Claude Code creates `.claude/skills/bedrock-debug/SKILL.md` in your project directory.

Verify the skill is available:

```
/bedrock-debug
```

**Expected result:** Claude Code acknowledges the skill and describes what it does.

> **In the upcoming Lab 3:** When a test fails, type `/bedrock-debug` and paste the error. Claude Code diagnoses the issue and suggests the fix using the exact patterns for this account -- instead of you searching documentation manually.

> **Skills vs CLAUDE.md:**
>
> | | CLAUDE.md | Skill |
> |--|-----------|-------|
> | Content | Facts and conventions | Procedures and playbooks |
> | Loading | Every session | Only when invoked or relevant |
> | Token cost | Every request | Only when used |
> | Best for | "Always use type hints" | "When debugging Bedrock, do this..." |

---

## Part 7: Production Configuration

### Concept: The Security Problem with Local Development

When Claude Code runs on your laptop it has access to your AWS credentials, your entire filesystem, your git credentials, and unrestricted network access. That is appropriate for personal development on trusted projects.

It is not appropriate for team environments, CI/CD pipelines, regulated workloads, or any situation where you want Claude Code to run autonomously.

The solution is a development container: an isolated sandbox with a network firewall, sandboxed credentials, and a reproducible environment that every team member gets identically.

### Step 23: Copy the Devcontainer Files

### If you have not cloned the course repo in Lab 1, you'll need to copy the pre-built `.devcontainer/` folder from the course repo into your working directory:

**macOS/Linux:**
```bash
cp -r ~/anthropic_on_aws/labs/lab2/.devcontainer/ ~/claude-code-lab/.devcontainer/
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse "$env:USERPROFILE\anthropic_on_aws\labs\lab2\.devcontainer" "$env:USERPROFILE\claude-code-lab\.devcontainer"
```

> **Cloned the repo elsewhere?** Replace the path with your actual repo location.

> **On RVC?** Your RVC has the .devcontainer files already on the vm. You can copy over using Powershell:

```powershell
Copy-Item -Recurse "\anthropic_on_aws\labs\lab2\.devcontainer" "\claude-code-lab\.devcontainer"
```

> **Alternative:** Download `devcontainer.json` and `init-firewall.sh` from the course repository on GitHub and paste them into a new `.devcontainer/` folder inside `claude-code-lab/`.

Verify the files are in place:

**macOS/Linux:**
```bash
ls .devcontainer/
```

**Windows (PowerShell):**
```powershell
ls .devcontainer\
```

**Expected result:** Both `devcontainer.json` and `init-firewall.sh` listed.

### Step 24: Inspect the Devcontainer Configuration

```
Read the files in .devcontainer/ and explain what each one does
and why it matters for a production Claude Code deployment.
```

**Expected Result:** Claude Code reads `devcontainer.json` and `init-firewall.sh` and explains each setting: the sandboxed credential mount, the environment variables, and the firewall initialization script.

> **Look for the mounts entry in devcontainer.json.** It points to `~/.aws/sandbox` rather than `~/.aws`. This means the container gets sandbox credentials only. Your production AWS account credentials are never mounted into the container.

### Step 25: Investigate a Firewall Rule

```
Look at the ALLOW rules in .devcontainer/init-firewall.sh.
Pick one rule and explain it in plain English. What traffic does
it allow? What would happen if it were removed?
```

**Expected Result:** Claude Code explains the selected rule and its purpose. Without the rule, the corresponding service would be unreachable from inside the container.

> **Key insight:** Each ACCEPT rule is intentional and minimal. This whitelist approach is what makes `--dangerously-skip-permissions` safe inside a devcontainer. Claude Code can edit files freely but cannot reach arbitrary internet endpoints.

### Step 26: Audit for Security Gaps

```
Review .devcontainer/init-firewall.sh for security issues.
Are there any missing rules, over-permissive settings, or gaps
that could expose the host environment?
```

**Expected Result:** Claude Code produces a structured security audit with multiple findings across severity levels. Expect output similar to:

| Issue | Severity | Effect if Exploited |
|-------|----------|-------------------|
| No default-deny rule | Critical | Firewall is entirely unenforced |
| Rules apply to host, not container | Critical | Container is unrestricted |
| Unrestricted DNS destination | High | DNS tunneling / data exfiltration |
| No IPv6 rules | High | Full bypass via IPv6 |
| GitHub as egress path | Medium | Data exfiltration to any repo |

> **Key learning:** Claude Code functions as a security review tool as well as a code generation tool. Asking it to audit infrastructure before committing to git catches issues across multiple severity levels that a manual review can easily miss.

### Step 27: Fix the Security Issues

```
Fix the Critical and High security issues you identified in
.devcontainer/init-firewall.sh. Explain each change you make
and why it addresses the vulnerability.
```

**Expected Result:** Claude Code updates `init-firewall.sh` addressing the Critical and High findings, explaining each change as it makes it.

### Step 28: Generate the Dockerfile

```
Generate a Dockerfile that completes the devcontainer configuration
based on what you read in devcontainer.json. It should be
production-ready for a Claude Code deployment on Amazon Bedrock.
```

**Expected Result:** Claude Code generates a `Dockerfile` inside `.devcontainer/` that matches the base image and dependencies referenced in `devcontainer.json`.

> **Note:** You cannot run this Dockerfile in the training environment. You now have a complete, corrected devcontainer configuration -- the original two files plus a fixed `init-firewall.sh` and a new `Dockerfile` -- ready to use in a production deployment.

---

### When to Use Devcontainers

**Use devcontainers when:**
- Deploying Claude Code to a team environment
- Running Claude Code in CI/CD pipelines
- Working with untrusted or shared repositories
- Operating in regulated environments (SOC 2, HIPAA, FedRAMP)

**Not required when:**
- Doing solo development on personal trusted projects
- Running quick experiments like this lab

---

## What You Built

In just over an hour, you moved from setup to a complete, production-patterned Claude Code workflow:

**Part 1:** Configured Claude Code with Bedrock, verified the active model, named your session for safe recovery.

**Part 2:** Used Opus for architectural planning and Plan mode to verify intent before writing code. Switched to Sonnet for all iterative work.

**Part 3:** Enforced team-wide standards through CLAUDE.md and proved they persist across session restarts.

**Part 4:** Built iteratively using interrupt and steer, verification criteria, and delegation. Understood why committing before risky changes is essential and how to recover when AI-generated code goes wrong.

**Part 5:** Compacted session context at a natural task boundary -- a production habit that controls cost and keeps Claude Code focused.

**Part 6:** Created a reusable `/bedrock-debug` skill you will use in Lab 3.

**Part 7:** Inspected, audited, fixed, and completed a production devcontainer configuration.

**Key takeaways:**

- Plan mode and Opus are for architectural decisions. Sonnet is for execution.
- CLAUDE.md is team memory. Skills are team playbooks. Both belong in git.
- Commit working code before every significant change. Revert rather than fix when things go wrong.
- /compact at task boundaries. /clear when starting something unrelated.
- Claude Code reads existing code before acting. Use that to your advantage.

---

## Cleanup

No AWS resources were created in this lab. Delete the working directory when you are finished:

**macOS/Linux:**
```bash
cd ..
rm -rf claude-code-lab
```

**Windows (PowerShell):**
```powershell
cd ..
Remove-Item -Recurse -Force claude-code-lab
```

---

*Lab 2 Complete*
