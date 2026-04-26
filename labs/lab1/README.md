# Lab 1: Claude on Bedrock with RAG

**Duration:** 30 minutes

---

## Objectives

By completing this lab, you will:

* Select and invoke different Claude models (Opus, Sonnet, Haiku) via the Bedrock console.
* Measure latency and token usage for text-generation prompts.
* Create a knowledge base from sample documents stored in S3.
* Test RAG queries and verify citation accuracy.

---

## Prerequisites

Before starting this lab, ensure you have:

- [ ] Access to the AWS Bedrock console in your training account
- [ ] Model access enabled for Claude models (Opus 4.6, Sonnet 4.6, Haiku 4.5)
- [ ] Access to the S3 bucket containing sample documents
- [ ] Lab instructions document open (this guide)

**Course Repository:** **https://github.com/AWSClassroom-com/anthropic_on_aws** — contains sample data and starter code for all labs.

**S3 Bucket Path:** `s3://bedrock-training-[account-id]/lab1-documents/`

> **How to find your Account ID:** In the AWS Console, click your username in the top-right corner. Your 12-digit Account ID is displayed in the dropdown. Replace `[account-id]` with this number (no dashes). Example: `s3://bedrock-training-123456789012/lab1-documents/`

> **Note:** The S3 bucket contains fictional product documentation files (product manuals, FAQs, return policies, warranty terms, support guides) that you will use to build your knowledge base.

---

## Part 1: Model Invocation and Comparison

### Task 1: Open the Bedrock Playground

1. Sign in to the AWS Management Console.
2. Navigate to **Amazon Bedrock** service.
3. In the left sidebar under **Test**, click **Playground**.
4. If prompted to accept cookies, click **Accept**.

**Expected Result:** The playground page loads showing "Select a model to get started" with a **Select model** button.

> **Note:** If the sidebar is collapsed, click the hamburger menu icon (three lines) at the top left to expand it.

---

### Task 2: Invoke Claude Sonnet

5. Click the orange **Select model** button in the center of the playground.
6. A **Select model** dialog opens with three panels: **Categories** (left), **Models** (middle), **Inference** (right).
7. In the left panel, click **Anthropic** to filter to Anthropic models.
8. In the middle panel, click **Claude Sonnet 4.6**.
9. In the right panel, select an inference profile (e.g., **US Anthropic Claude Sonnet 4.6** or **Global**).
10. Click the **Apply** button at the bottom right of the dialog.

> **Note:** If the Apply button doesn't respond on the first click, click it again—a tooltip overlay may be in the way.

11. The playground now shows **Claude Sonnet 4.6** at the top with **Input**, **Output**, and **Latency** metrics (showing "---" until you run a prompt).
12. In the text input area at the bottom of the page, type the following prompt:

```
You are a helpful assistant. Explain the concept of cloud computing in 3-4 sentences for someone who has never heard of it before.
```

13. Click the **Run** button (bottom right of the text input area).
14. Wait for the response to appear above the input area.

**Expected Result:**
| Metric | Expected Range |
|--------|----------------|
| Response | Clear, concise explanation of cloud computing |
| Latency | 1-5 seconds |
| Input tokens | 30-40 |
| Output tokens | 80-150 |

> **Where to find metrics:** The **Input**, **Output**, and **Latency** values appear in the header bar next to the model name (e.g., "Input: 37  Output: 145  Latency: 4797 ms").

15. **Record these values** — you will compare them with other models in the next steps.

> **Troubleshooting:** If you receive an error, navigate to **Configure and learn** > **Model access** in the left sidebar and verify Claude Sonnet access is enabled.

---

### Task 3: Compare with Claude Opus

16. Click the Options icon next to the Model name (**Claude Sonnet 4.6**) in the header bar to reopen the model picker.
17. Select the pencil icon next to the current Model name and select **Claude Opus 4.6**, then click **Apply**.
18. Click **Clear** (or delete the previous response) to start fresh.
19. Enter the same prompt from Step 2:
```
You are a helpful assistant. Explain the concept of cloud computing in 3-4 sentences for someone who has never heard of it before.
```
20. Click **Run** and record the metrics.

**Expected Result:**
| Metric | Expected Range |
|--------|----------------|
| Latency | 3-5+ seconds (slower than Sonnet) |
| Response quality | More detailed, more nuanced |
| Input tokens | Similar to Sonnet |
| Output tokens | May vary |

---

### Task 4: Compare with Claude Haiku

21. Reopen the model picker as you did in the previous step.
22. Select **Claude Haiku 4.5** and click **Apply**.
23. Clear the conversation and enter the same prompt:
```
You are a helpful assistant. Explain the concept of cloud computing in 3-4 sentences for someone who has never heard of it before.
```
24. Click **Run** and record the metrics.

**Expected Result:**
| Metric | Expected Range |
|--------|----------------|
| Latency | Under 1 second (fastest) |
| Response quality | Shorter, more direct, still accurate |
| Input tokens | Similar to other models |
| Output tokens | Typically fewer |

---

### Task 5: Model Comparison Summary

**Patterns to observe:**
- **Opus:** Highest quality, highest latency, typically more output tokens
- **Sonnet:** Balanced quality and speed
- **Haiku:** Fastest, most concise

> **Common Pitfall:** Running different prompts on different models makes comparison invalid. Always use the identical prompt for fair comparison.

---

### Task 6: Observe Streaming Behavior

> **Note:** The streaming toggle location varies by console version. Follow the options below in order until you find it.

25. Switch Models back to **Claude Opus** and look for a **three-dot menu** (⋮) in the top-right area of the playground, near the **Compare mode** toggle.
26. Click the three-dot menu to reveal a context menu.
27. Select the **Streaming preference** option.

> **Alternative locations:** If you don't see a three-dot menu, look for a **hamburger icon** (☰) next to the **Build** button, or a **gear icon** in the playground header. The streaming setting may also be in the **Configurations** section on the right side panel.

28. Toggle **stream responses** OFF, and select **confirm**.
29. Enter the prompt "What is cloud computing?" and click **Run**.
30. Observe that you wait for the **complete response** before seeing anything. The Model no longer incrementally streams a response.
31. Toggle streaming back **ON** and run the same prompt again.
32. Observe how tokens appear **incrementally** as they are generated.

**Key Insight:** For interactive applications (chatbots, assistants), streaming provides a more responsive user experience. For batch processing, non-streaming is acceptable.

---

## Part 2: Token Usage and Latency Measurement

### Task 7: Measure with Different Prompt Complexities

33. Click the model name at the top of the playground to change models.
34. Select **Claude Sonnet 4.6** (follow the same model picker steps from Step 2).
35. Run these three prompts in sequence and record the metrics for each:

**Prompt 1 (Simple):**
```
What is AWS?
```

**Prompt 2 (Moderate):**
```
Explain the difference between IaaS, PaaS, and SaaS. Include one example of each.
```

**Prompt 3 (Complex):**
```
You are a cloud architect. Design a high-level architecture for a web application that needs to handle 1 million daily active users, requires high availability across multiple regions, and must comply with GDPR. List the key AWS services you would use and explain why.
```

---

### Task 8: Record Your Results

Record your results from Step 7 on the scratchpad of your choice (the values below are approximate — your results will vary):

**Typical ranges:**
| Prompt | Input Tokens | Output Tokens | Latency |
|--------|--------------|---------------|---------|
| Simple | ~10 | 50-100 | < 1 sec |
| Moderate | ~25 | 150-250 | 1-2 sec |
| Complex | ~60 | 400-600 | 3-5 sec |

---

### Step 9: Calculate Approximate Costs

Using Claude Sonnet 4.6 pricing:
- **Input:** $3 per million tokens
- **Output:** $15 per million tokens

Calculate the cost for each prompt:

**Formula:**
```
Cost = (input_tokens × $3 / 1,000,000) + (output_tokens × $15 / 1,000,000)
```

| Prompt | Approximate Cost |
|--------|------------------|
| Simple | ~$0.00015 |
| Moderate | ~$0.004 |
| Complex | ~$0.01 |

**Key Insight:** Individual requests are inexpensive, but costs multiply at scale. Understanding token economics is critical for production applications.

> **Troubleshooting:** If complex prompts produce truncated responses, check your **max_tokens** setting. Ensure it is set to at least 1000 for these exercises.

---

## Part 3: Creating a Knowledge Base

### Task 10: Navigate to Knowledge Bases

36. In the Bedrock console left sidebar under **Build**, click **Knowledge Bases**.
37. Click the **Create** button (orange, with dropdown arrow).
38. Select **Knowledge Base with vector store** from the dropdown menu.

---

### Task 11: Configure Basic Settings

39. **Name:** `lab1-[your-initials]-kb` (e.g., `lab1-jd-kb`).
40. **Description:** `Lab 1 knowledge base for product documentation`.
41. **IAM role:** Select **Create and use a new service role**.

---

### Task 12: Configure Data Source

42. Ensure **Amazon S3** is the selected data source type and click **Next** on the bottom right of this screen to proceed to the data source configuration step.
43. In the **S3 URI** field, enter the bucket path below. Replace the entire **[account-id]** portion of the URI below with your training account ID:
   ```
   s3://bedrock-training-[account-id]/lab1-documents/
   ```
44. Skip to **Chunking strategy:** and ensure **Default chunking** is selected.
45. Click **Next** on the bottom right of this screen to proceed.

---

### Task 13: Configure Embeddings Model

46. Click the **Select model** button in the Embeddings model section.
47. In the model picker, select **Amazon** as the provider.
48. Select **Titan Embeddings G1 - Text** (or **Titan Text Embeddings V2** if available).
49. Click **Apply** to confirm the selection.

---

### Task 14: Configure Vector Store and Create

50. Ensure **Quick create a new vector store - Recommended** is selected.
51. From the **Select a vector store** dropdown, choose **Amazon OpenSearch Serverless**.
52. Click **Next** to proceed to the review page and quickly ensure all settings are aligned to this instructions. You will use this KB both in this lab, and in the upcoming Lab 3, so it's very important to get this right.
53. Scroll to the bottom of the review page.
54. Click the orange **Create Knowledge Base** button and **do not navigate from this page!**.

**Expected Result:** A blue banner appears at the top of the same screen (you might have to scroll up): "Preparing vector database in Amazon OpenSearch Serverless. This process may take several minutes to complete." Take a quick break, you've earned it!

> **Troubleshooting:** If creation takes more than 10 minutes, notify your instructor. Do not navigate away from the page during provisioning.

---

### Task 15: Sync the Data Source

55. Wait for the knowledge base status to show **Active** (2-5 minutes after creation).
56. Once Active, you should see the knowledge base detail page with a **Data source** section.
57. In the Data source table, select the radio button next to your S3 data source.
58. Click the **Sync** button.
59. Wait for the sync status to show **Available** (typically 1-2 minutes).

**Expected Result:**
- Sync status: **Available**
- Document count: Shows number of processed files (typically 5 for sample docs)

> **What happens during sync:** Bedrock reads documents from S3, chunks them, passes each chunk through the embedding model, and stores the resulting vectors in OpenSearch. This is all handled automatically.

> **Common Pitfall:** Forgetting to trigger sync results in empty query results. The knowledge base being "Active" only means infrastructure is ready — you must sync to process documents.

---

## Part 4: Testing RAG Queries

### Task 16: Open the Test Interface

60. On the knowledge base detail page, click the **Test Knowledge Base** button (top right, next to the **Delete** button).
61. A test panel opens on the right side of the page with a text input area.

> **Note:** If you see a message "One or more data sources need to be synced," go back to Step 15 and ensure sync completed successfully.

---

### Task 17: Run Your First RAG Query

62. In the API section, select **Claude Sonnet 4.6** as your model, and then within the Preview section, find the **Write a prompt** input field and type:
   ```
   What is the return policy for damaged products?
   ```
63. Press ENTER or click the submit button.

**Expected Result:**
- A natural language answer about return policies
- Source citations displayed below the answer (select **details** to reveal citation chunks)
- Each citation shows document name and relevance score

> **Troubleshooting:** If you see "No relevant information found," verify that sync completed successfully and document count is greater than zero.

---

### Task 18: Verify Citation Accuracy

64. In the test panel response, look for **source citations** displayed below the answer (shown as expandable sections or document references).
65. Click on one of the citations to expand it.
66. Review the source text and compare it to Claude's answer.

**Ask yourself:**
- Is the answer supported by the source text?
- Did Claude add information not in the document?
- Are there any misinterpretations?

---

### Task 19: Test Another Query

67. In the test panel input, clear the previous query and type:
   ```
   What warranty coverage is included with the premium product tier?
   ```
68. Click **Run** to submit the query.
69. Review the response and citations—verify the answer is supported by the source documents.

---

### Task 20: Test for Hallucinations

70. Run a query about something NOT in the documents:
   ```
   What is the CEO's favorite color?
   ```

**Expected Result:** Claude should indicate it does not have that information, or retrieval should return no relevant chunks.

**Key Insight:** Testing with out-of-scope queries helps you understand how the system behaves when information is not available.

---

### Task 21: Observe Query Phrasing Effects

Run these two queries about the same topic:

**Query A (Vague):**
```
How do I return something?
```

**Query B (Specific):**
```
What is the step-by-step process for initiating a product return, including any required documentation and timelines?
```

**Compare the results:**
- Which query retrieved more targeted chunks?
- Which answer was more detailed and useful?

**Key Insight:** Specific queries retrieve more targeted chunks and produce better answers. In production applications, you may want to preprocess user queries to expand them or add context.

---

## Checkpoint: Verify Your Progress

Before finishing, confirm you have completed:

- [ ] Invoked all three Claude models (Opus, Sonnet, Haiku) with the same prompt
- [ ] Recorded latency and token metrics for each model
- [ ] Tested three prompts of varying complexity on Sonnet
- [ ] Calculated approximate costs for each prompt
- [ ] Created a knowledge base we will use in Lab 3
- [ ] Successfully synced documents from S3 to the KB
- [ ] Ran at least three RAG queries
- [ ] Verified citation accuracy on at least one query
- [ ] Tested a query for non-existent information

---

## Troubleshooting Reference

| Issue | Symptom | Solution |
|-------|---------|----------|
| Model access not enabled | `AccessDeniedException` error | Navigate to Model access, request access for Claude models |
| S3 bucket access denied | Sync fails with permission error | Verify IAM role has S3 read permissions |
| Knowledge base stuck creating | Status stays "Creating" > 10 min | Check CloudWatch logs; may need to delete and recreate |
| Sync returns zero documents | Document count is 0 | Verify S3 prefix is correct; check file formats |
| RAG queries return no results | "No relevant information found" | Confirm sync completed; verify documents match query topics |
| High latency on all models | > 10 second response times | Check region; may be networking issue or quota throttling |
| Truncated responses | Output cuts off mid-sentence | Increase max_tokens setting (set to 1000+) |

---

## Optional Code Reference: boto3 Examples

The following code snippets show how to perform these same operations **programmatically**.

### Invoke Claude Model

```python
import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_claude(prompt, model_id='anthropic.claude-sonnet-4-6'):
    """Invoke a Claude model via Bedrock."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=body
    )

    response_body = json.loads(response['body'].read())
    return response_body

# Example usage
result = invoke_claude("Explain cloud computing in 3 sentences.")
print(result['content'][0]['text'])
print(f"Input tokens: {result['usage']['input_tokens']}")
print(f"Output tokens: {result['usage']['output_tokens']}")
```

### Invoke with Streaming

```python
import boto3
import json

bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def invoke_claude_streaming(prompt, model_id='anthropic.claude-sonnet-4-6'):
    """Invoke Claude with streaming response."""
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    response = bedrock_runtime.invoke_model_with_response_stream(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=body
    )

    # Process streaming response
    for event in response['body']:
        chunk = json.loads(event['chunk']['bytes'].decode())
        if chunk['type'] == 'content_block_delta':
            print(chunk['delta']['text'], end='', flush=True)
    print()  # Newline at end

# Example usage
invoke_claude_streaming("What is AWS?")
```

### Query Knowledge Base

```python
import boto3

bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')

def query_knowledge_base(query, knowledge_base_id, model_arn):
    """Query a Bedrock knowledge base with RAG."""
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={
            'text': query
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': knowledge_base_id,
                'modelArn': model_arn
            }
        }
    )

    # Extract answer and citations
    answer = response['output']['text']
    citations = response.get('citations', [])

    return {
        'answer': answer,
        'citations': citations
    }

# Example usage
result = query_knowledge_base(
    query="What is the return policy?",
    knowledge_base_id="YOUR_KB_ID",
    model_arn="arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-sonnet-4-6"
)
print(result['answer'])
```

---

*Lab 1 Complete*
