# Anthropic on Amazon Bedrock
## Student Reference Sheet

---

## Claude Model IDs (Bedrock)

| Model | Bedrock Model ID | Input/Output | Context |
|-------|------------------|--------------|---------|
| Claude Opus 4.6 | `anthropic.claude-opus-4-6-v1:0` | $5/$25 per MTok | 1M / 128k out |
| Claude Sonnet 4.6 | `anthropic.claude-sonnet-4-6-v1:0` | $3/$15 per MTok | 1M / 64k out |
| Claude Haiku 4.5 | `anthropic.claude-haiku-4-5-v1:0` | $1/$5 per MTok | 200k / 64k out |

> **Pricing Note:** Verify current pricing at [aws.amazon.com/bedrock/pricing](https://aws.amazon.com/bedrock/pricing/). MTok = million tokens.

**Model Selection Guide:**
- **Opus 4.6** - Complex reasoning, agents, coding tasks
- **Sonnet 4.6** - Best speed/intelligence balance (default choice)
- **Haiku 4.5** - High-volume, latency-sensitive, cost-optimized

---

## Key API Parameters

### Required Headers
```
anthropic_version: "bedrock-2023-05-31"
Content-Type: "application/json"
```

### Common Request Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `max_tokens` | int | Maximum output tokens (required) |
| `messages` | array | Conversation messages |
| `system` | string | System prompt |
| `temperature` | float | 0.0-1.0, controls randomness |
| `top_p` | float | Nucleus sampling threshold |
| `stop_sequences` | array | Stop generation strings |

### Stop Reasons
| Value | Meaning |
|-------|---------|
| `end_turn` | Normal completion |
| `max_tokens` | Hit token limit |
| `stop_sequence` | Hit stop sequence |
| `tool_use` | Requesting tool execution |

---

## Boto3 Code Snippets

### Basic Invocation
```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')

response = bedrock.invoke_model(
    modelId='anthropic.claude-sonnet-4-6',
    contentType='application/json',
    accept='application/json',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "system": "You are a helpful assistant.",
        "messages": [
            {"role": "user", "content": "Hello, Claude!"}
        ]
    })
)
result = json.loads(response['body'].read())
print(result['content'][0]['text'])
```

### Streaming Response
```python
response = bedrock.invoke_model_with_response_stream(
    modelId='anthropic.claude-sonnet-4-6',
    contentType='application/json',
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "Explain RAG"}]
    })
)
for event in response['body']:
    chunk = json.loads(event['chunk']['bytes'])
    if chunk['type'] == 'content_block_delta':
        print(chunk['delta'].get('text', ''), end='')
```

### Tool Use Definition
```python
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"}
        },
        "required": ["location"]
    }
}]

body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "tools": tools,
    "messages": [{"role": "user", "content": "What's the weather in Seattle?"}]
}
```

---

## Bedrock Console URLs

| Resource | URL |
|----------|-----|
| Bedrock Console | `console.aws.amazon.com/bedrock/` |
| Model Playground | `console.aws.amazon.com/bedrock/home#/chat-playground` |
| Knowledge Bases | `console.aws.amazon.com/bedrock/home#/knowledge-bases` |
| Agents | `console.aws.amazon.com/bedrock/home#/agents` |
| Guardrails | `console.aws.amazon.com/bedrock/home#/guardrails` |
| Model Access | `console.aws.amazon.com/bedrock/home#/modelaccess` |

**Primary Regions:** us-east-1, us-west-2, eu-west-1, ap-northeast-1

---

## IAM Permissions

### Minimum Bedrock Invocation
```json
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": [
            "bedrock:InvokeModel",
            "bedrock:InvokeModelWithResponseStream"
        ],
        "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }]
}
```

### Knowledge Base Access
```json
{
    "Action": [
        "bedrock:Retrieve",
        "bedrock:RetrieveAndGenerate"
    ],
    "Resource": "arn:aws:bedrock:REGION:ACCOUNT:knowledge-base/KB_ID"
}
```

### Agent Invocation
```json
{
    "Action": [
        "bedrock:InvokeAgent"
    ],
    "Resource": "arn:aws:bedrock:REGION:ACCOUNT:agent-alias/AGENT_ID/ALIAS_ID"
}
```

### Guardrails
```json
{
    "Action": [
        "bedrock:ApplyGuardrail"
    ],
    "Resource": "arn:aws:bedrock:REGION:ACCOUNT:guardrail/GUARDRAIL_ID"
}
```

---

## Guardrails Configuration

### Content Filter Categories
| Category | Description |
|----------|-------------|
| `HATE` | Hate speech, discrimination |
| `INSULTS` | Personal attacks, demeaning content |
| `SEXUAL` | Sexually explicit content |
| `VIOLENCE` | Violent or graphic content |
| `MISCONDUCT` | Illegal activity, harmful advice |
| `PROMPT_ATTACK` | Jailbreak attempts |

### Filter Strengths
`NONE` | `LOW` | `MEDIUM` | `HIGH`

### PII Types (Sensitive Info Filters)
`ADDRESS` | `AGE` | `CREDIT_DEBIT_CARD_NUMBER` | `DATE_TIME` | `DRIVER_ID` | `EMAIL` | `IP_ADDRESS` | `NAME` | `PASSPORT_NUMBER` | `PHONE` | `SSN` | `URL` | `USERNAME`

### Actions
- `BLOCK` - Reject request/response
- `ANONYMIZE` - Mask PII with placeholder

---

## CloudWatch Metrics

### Namespace
`AWS/Bedrock`

### Key Metrics
| Metric | Description |
|--------|-------------|
| `Invocations` | Total API calls |
| `InvocationLatency` | Response time (ms) |
| `InputTokenCount` | Tokens in request |
| `OutputTokenCount` | Tokens in response |
| `InvocationClientErrors` | 4xx errors |
| `InvocationServerErrors` | 5xx errors |

### Useful Dimensions
- `ModelId` - Filter by specific model
- `Region` - Filter by region

### Sample CloudWatch Query
```
SELECT AVG(InvocationLatency)
FROM "AWS/Bedrock"
WHERE ModelId = 'anthropic.claude-sonnet-4-6'
GROUP BY ModelId
```

---

## AWS CLI Commands

### List Available Claude Models
```bash
aws bedrock list-foundation-models \
    --by-provider Anthropic \
    --query 'modelSummaries[*].[modelId,modelName]' \
    --output table
```

### Check Model Access Status
```bash
aws bedrock get-foundation-model-availability \
    --model-identifier anthropic.claude-sonnet-4-6
```

### Invoke Model (CLI)
```bash
aws bedrock-runtime invoke-model \
    --model-id anthropic.claude-sonnet-4-6 \
    --content-type application/json \
    --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":256,"messages":[{"role":"user","content":"Hi"}]}' \
    output.json
```

### List Knowledge Bases
```bash
aws bedrock-agent list-knowledge-bases \
    --query 'knowledgeBaseSummaries[*].[knowledgeBaseId,name,status]' \
    --output table
```

### Query Knowledge Base
```bash
aws bedrock-agent-runtime retrieve \
    --knowledge-base-id KB_ID \
    --retrieval-query '{"text":"your query here"}'
```

### List Guardrails
```bash
aws bedrock list-guardrails \
    --query 'guardrails[*].[id,name,status]' \
    --output table
```

### List Agents
```bash
aws bedrock-agent list-agents \
    --query 'agentSummaries[*].[agentId,agentName,agentStatus]' \
    --output table
```

---

## Quick Prompt Patterns

### XML Structure (Claude Best Practice)
```xml
<context>
Background information here
</context>

<instructions>
Task description here
</instructions>

<examples>
Few-shot examples here
</examples>
```

### Chain-of-Thought
```
Think through this step by step:
1. First, analyze...
2. Then, consider...
3. Finally, conclude...
```

### Tool Choice Options
| Value | Behavior |
|-------|----------|
| `auto` | Claude decides when to use tools |
| `any` | Force tool use (any tool) |
| `tool` | Force specific tool by name |
| `none` | Disable tool use |

---

## Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `ValidationException` | Invalid request format | Check JSON structure |
| `AccessDeniedException` | Missing IAM permissions | Add required actions |
| `ThrottlingException` | Rate limit exceeded | Implement backoff/retry |
| `ModelNotReadyException` | Model not available | Check model access |
| `ResourceNotFoundException` | Resource not found | Verify ARN/ID |

---

## Cross-Region Inference

### Global Endpoint
Dynamic routing across regions for maximum availability.

### Regional Endpoint
Guaranteed data routing through specific regions.

**Inference Profile ARN Format:**
```
arn:aws:bedrock:REGION:ACCOUNT:inference-profile/PROFILE_ID
```

---

*Course: Building AI Applications with Anthropic on AWS Bedrock*
*Reference Sheet v1.0 - April 2026*
