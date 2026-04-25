# Lab 5: Media & Entertainment â Content Intelligence Platform

**Course:** Building AI Applications with Anthropic on AWS Bedrock
**Lab:** Industry-Specific (replaces standard Labs 1 & 2)
**Duration:** 60 minutes
**Level:** Intermediate

---

## Lab Overview

You work for a streaming service that manages a vast content library requiring metadata enrichment, personalized recommendations, and content moderation at scale. In this lab, you'll build a content intelligence platform using Claude on Bedrock that analyzes content metadata, powers recommendation conversations from a content catalog, and enforces content moderation policies â enabling AI-driven content operations across the platform.

### What You Will Build

- A Knowledge Base from a content catalog and viewer data (S3 â Bedrock KB)
- RAG-powered content recommendation queries
- Custom tools for content classification and metadata enrichment
- Guardrails for content moderation (age-appropriate, no spoilers, no piracy)
- CloudWatch monitoring for content operations

---

## Prerequisites

- [ ] AWS account with Amazon Bedrock access enabled
- [ ] Claude model access (Sonnet 4.6, Haiku 4.5) approved
- [ ] S3 bucket: `s3://bedrock-training-[account-id]/lab5-media/`
- [ ] Python 3.11+ installed with boto3
- [ ] AWS SAM CLI installed

**Course Repository:** **https://github.com/AWSClassroom-com/anthropic_on_aws**  contains sample data for all labs.

---

## Part 1: Content Catalog Knowledge Base (25 min)

> **Building Block:** Same process as Lab 1 â different documents.

### Step 1: Upload Content Catalog Documents to S3

Upload the provided sample content catalog:

```bash
aws s3 sync ./lab5-documents/ s3://bedrock-training-[account-id]/lab5-media/
```

**Sample documents included:**
- `content_catalog.txt` â Titles, genres, ratings, descriptions for 50 fictional shows/movies
- `viewer_preferences.txt` â Anonymized viewing patterns and preference profiles
- `content_guidelines.txt` â Age rating criteria, content warnings, and classification rules
- `moderation_policy.txt` â User-generated content rules, escalation procedures, and banned content
- `recommendation_rules.txt` â Personalization logic, diversity requirements, and promotional rules

### Step 2: Create the Knowledge Base

1. Navigate to **Amazon Bedrock** â **Knowledge Bases**
2. Click **Create** â **Knowledge Base with vector store**
3. Configure:
   - **Name:** `lab5-content-catalog-kb`
   - **S3 URI:** `s3://bedrock-training-[account-id]/lab5-media/`
   - **Embedding model:** Titan Embeddings G1 - Text
   - **Vector store:** Amazon OpenSearch Serverless (Quick create)
4. Click **Create Knowledge Base** and wait for status: **Active**

### Step 3: Sync and Verify

1. Select the data source â click **Sync**
2. Wait for sync to complete
3. Verify document count matches uploaded files

### Step 4: Test Content Queries

Open the **Test Knowledge Base** panel and try:

| Query | Expected Behavior |
|-------|-------------------|
| "Recommend a sci-fi show for someone who liked Stranger Things" | Answer citing content_catalog.txt with relevant matches |
| "What content is appropriate for viewers under 13?" | Answer citing content_guidelines.txt with age-rated titles |
| "What are the most popular genres this month?" | Answer citing viewer_preferences.txt |
| "Where can I download this show for free?" | Should NOT provide piracy information |

---

## Part 2: Content Intelligence Tools (25 min)

> **Building Block:** Same tool schema pattern as Lab 2 â media tools.

### Step 5: Define Content Tools

Test Claude's understanding of content operations tools:

```
You are a content intelligence assistant with access to these tools:
- classify_content(title, description, visual_themes): Assigns genre tags, age ratings, and content warnings
- enrich_metadata(content_id, fields_to_update): Updates catalog metadata with AI-generated descriptions, keywords, and categories
- get_recommendations(viewer_profile, count, filters): Returns personalized content recommendations based on viewing history

A new show called "Cosmic Wanderers" was just added to the platform. The description says it's an animated space adventure with mild cartoon violence and themes of friendship. What tools would you use to onboard this content?
```

**Expected:** Claude should call `classify_content` first (assign ratings/tags), then `enrich_metadata` (generate keywords, SEO descriptions).

### Step 6: Test Recommendation Logic

```
A viewer has watched 5 sci-fi shows and 3 documentaries in the last month. They rated the sci-fi shows 4-5 stars and the documentaries 3 stars. What would you recommend and why?
```

**Expected:** Claude should favor sci-fi recommendations with some documentary diversity.

---

## Part 3: Content Moderation Guardrails (25 min)

> **Building Block:** Same guardrail creation process as Lab 2 â content moderation rules.

### Step 7: Create Content Moderation Guardrails

1. Navigate to **Bedrock** â **Guardrails** â **Create guardrail**
2. **Name:** `ContentModerationGuardrail`

### Step 8: Configure Content Filters

Set all content filters to **HIGH** for both input and output.

### Step 9: Configure Denied Topics

| Topic | Definition | Sample Phrases |
|-------|------------|----------------|
| Piracy/Illegal Streaming | Requests for illegal downloads, torrents, or unauthorized streaming | "Where can I download for free?", "What torrent sites work?" |
| Spoilers | Revealing major plot points without user consent | "The twist ending is...", "The main character dies when..." |
| Competitor Promotion | Directing users to competing streaming platforms | "You should watch it on Netflix instead", "Disney+ has a better version" |

### Step 10: Configure PII Filters

| PII Type | Action |
|----------|--------|
| Email | **ANONYMIZE** |
| Credit/Debit Card | **BLOCK** |
| Address | **ANONYMIZE** |

### Step 11: Test Content Guardrails

| Prompt | Expected Result |
|--------|----------------|
| "Recommend something like Breaking Bad" | **PASS** â normal recommendation query |
| "Where can I torrent the latest episode?" | **BLOCKED** â piracy topic |
| "Tell me how the show ends" | **BLOCKED** â spoiler topic (if configured with content warnings) |
| "My credit card is 4111-1111-1111-1111" | **BLOCKED** â PII detected |

---

## Part 4: Monitoring and Analytics (20 min)

> **Building Block:** Same CloudWatch pattern as Lab 2 â content analytics focus.

### Step 12: Set Up CloudWatch Monitoring

Create a monitoring dashboard:
- **Dashboard name:** `Lab5-ContentIntelligence`
- **Metrics:** InvocationCount, InputTokenCount, OutputTokenCount, ResponseLatency, ErrorCount

### Step 13: Content Analytics Insights

Review the dashboard to understand:
- Which query types generate the most tokens (recommendations vs. classification)
- Average latency for content moderation checks
- Error rates for guardrail blocks (indicates user behavior patterns)

---

## Part 5: Application Deployment (25 min)

> **Building Block:** Same SAM deployment as Lab 2 â content platform use case.

### Step 14: Build the Application

```bash
mkdir lab5-content-platform
cd lab5-content-platform
sam init --runtime python3.11 --name content-intelligence
```

### Step 15: Deploy

```bash
sam build
sam deploy --guided
```

Configure with:
- Stack name: `lab5-content-platform`
- Region: `us-east-1`

### Step 16: Test the Deployed API

```bash
curl -X POST https://[api-url]/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "Recommend a family-friendly adventure movie"}'
```

---

## Cleanup

```bash
# Delete Knowledge Base (via Bedrock console)
# Delete OpenSearch Serverless collection
# Delete Guardrail
# Delete CloudWatch dashboard
aws cloudformation delete-stack --stack-name lab5-content-platform
```

---

## Key Takeaways

1. **Content moderation at scale** â guardrails handle content policy enforcement without custom code
2. **RAG for recommendations** â Knowledge Bases turn your content catalog into a conversational recommendation engine
3. **Same building blocks, different data** â the KB + Guardrails + Tools pattern works identically for any industry
4. **Multimodal potential** â Claude's vision capabilities (not covered in this lab) could analyze thumbnails and posters for automated metadata

---

*Lab materials prepared for ROI Training delivery.*
