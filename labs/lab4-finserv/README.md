# Lab 3: Fintech â AI-Powered Document Processing & Compliance

**Course:** Building AI Applications with Anthropic on AWS Bedrock
**Lab:** Industry-Specific (replaces standard Labs 1 & 2)
**Duration:** 60 minutes
**Level:** Intermediate

---

## Lab Overview

You work for a financial services firm that processes thousands of documents daily â KYC verification, transaction monitoring, and regulatory reporting. Manual processing creates bottlenecks and compliance risk. In this lab, you'll build an intelligent document processing platform using Claude on Bedrock that extracts data from identity documents, answers compliance questions from regulatory knowledge bases, and generates suspicious activity reports â all with guardrails ensuring financial advice restrictions and PII protection.

### What You Will Build

- A Knowledge Base from financial regulatory documents (S3 â Bedrock KB)
- RAG-powered compliance queries with cited regulatory sources
- Custom tools for transaction monitoring and SAR generation
- Guardrails blocking financial advice and masking PII (SSN, account numbers)
- CloudWatch monitoring for audit trail compliance

---

## Prerequisites

- [ ] AWS account with Amazon Bedrock access enabled
- [ ] Claude model access (Sonnet 4.6, Haiku 4.5) approved
- [ ] S3 bucket: `s3://bedrock-training-[account-id]/lab3-fintech/`
- [ ] Python 3.11+ installed with boto3
- [ ] AWS SAM CLI installed

**Course Repository:** **https://github.com/AWSClassroom-com/anthropic_on_aws**  contains sample data for all labs.

---

## Part 1: Financial Knowledge Base Setup (25 min)

> **Building Block:** Same process as Lab 1 â different documents.

### Step 1: Upload Financial Regulatory Documents to S3

Your instructor has provided sample regulatory documents. Upload them to your S3 bucket:

```bash
aws s3 sync ./lab3-documents/ s3://bedrock-training-[account-id]/lab3-fintech/
```

**Sample documents included:**
- `aml_policy.txt` â Anti-Money Laundering compliance procedures
- `kyc_requirements.txt` â Know Your Customer verification standards
- `transaction_monitoring.txt` â Suspicious activity detection thresholds
- `regulatory_reporting.txt` â BSA/SAR filing requirements and timelines
- `data_handling_policy.txt` â PII handling and encryption requirements

### Step 2: Create the Knowledge Base

1. Navigate to **Amazon Bedrock** â **Knowledge Bases**
2. Click **Create** â **Knowledge Base with vector store**
3. Configure:
   - **Name:** `lab3-fintech-compliance-kb`
   - **S3 URI:** `s3://bedrock-training-[account-id]/lab3-fintech/`
   - **Embedding model:** Titan Embeddings G1 - Text
   - **Vector store:** Amazon OpenSearch Serverless (Quick create)
4. Click **Create Knowledge Base** and wait for status: **Active**

### Step 3: Sync and Verify

1. Select the data source â click **Sync**
2. Wait for sync to complete
3. Verify document count matches your uploaded files

### Step 4: Test Compliance Queries

Open the **Test Knowledge Base** panel and try:

| Query | Expected Behavior |
|-------|-------------------|
| "What are the KYC verification requirements for new accounts?" | Detailed answer citing kyc_requirements.txt |
| "What transaction amount triggers a suspicious activity report?" | Specific thresholds from transaction_monitoring.txt |
| "What is the deadline for filing a SAR?" | Timeline from regulatory_reporting.txt |
| "What stocks should I buy?" | Should NOT find relevant information (out of scope) |

**Record your results.** Note which queries return citations and which don't.

---

## Part 2: Compliance Tool Use (25 min)

> **Building Block:** Same tool schema pattern as Lab 2 â different tools.

### Step 5: Define Financial Tools

In the Bedrock playground, test Claude's understanding of financial tools:

```
You are a compliance analyst with access to these tools:
- screen_transaction(transaction_id, amount, sender, receiver): Screens a transaction against AML rules
- generate_sar(transaction_id, reason, risk_level): Generates a Suspicious Activity Report
- verify_kyc(customer_id, document_type): Verifies customer identity documents

A transaction of $15,000 from account A-1234 to offshore account X-9999 was flagged. What tools would you use and in what order?
```

**Expected:** Claude should identify the need to screen the transaction first, then potentially generate a SAR based on the amount and offshore destination.

### Step 6: Test Tool Routing

Try additional scenarios:

```
A new customer wants to open an account. They've submitted a passport and utility bill. What tools do you need?
```

**Expected:** Claude should call `verify_kyc` with the appropriate document types.

---

## Part 3: Financial Guardrails (25 min)

> **Building Block:** Same guardrail creation process as Lab 2 â different rules.

### Step 7: Create Compliance Guardrails

1. Navigate to **Bedrock** â **Guardrails** â **Create guardrail**
2. **Name:** `FinancialComplianceGuardrail`

### Step 8: Configure Content Filters

Set all content filters to **HIGH** for both input and output.

### Step 9: Configure Denied Topics

Add these denied topics:

| Topic | Definition | Sample Phrases |
|-------|------------|----------------|
| Investment Advice | Direct recommendations to buy, sell, or hold specific securities | "Should I buy Tesla stock?", "Is Bitcoin a good investment?" |
| Loan Approval | Promising or guaranteeing loan approval or specific terms | "You're approved for a loan", "I can guarantee a 3% rate" |

### Step 10: Configure PII Filters

| PII Type | Action |
|----------|--------|
| SSN | **BLOCK** |
| Credit/Debit Card Number | **BLOCK** |
| Bank Account Number | **ANONYMIZE** |
| Email | **ANONYMIZE** |
| Phone | **ANONYMIZE** |

### Step 11: Test Guardrails

Test with these prompts:

| Prompt | Expected Result |
|--------|----------------|
| "What is the KYC process for new accounts?" | **PASS** â normal compliance query |
| "Should I invest in cryptocurrency?" | **BLOCKED** â investment advice |
| "My SSN is 123-45-6789, can you check my account?" | **BLOCKED** â SSN detected |
| "Customer email is john@example.com and phone is 555-1234" | **ANONYMIZED** â PII masked |

---

## Part 4: Monitoring and Audit Trail (20 min)

> **Building Block:** Same CloudWatch pattern as Lab 2 â with audit focus.

### Step 12: Set Up CloudWatch Monitoring

Create a monitoring dashboard:
- **Dashboard name:** `Lab3-FinancialCompliance`
- **Metrics:** InvocationCount, InputTokenCount, OutputTokenCount, ResponseLatency, ErrorCount

### Step 13: Verify Audit Logging

Financial services require comprehensive audit trails. Verify:
1. CloudTrail is logging all Bedrock API calls
2. Guardrail violations are captured in logs
3. PII masking events are recorded

---

## Part 5: Application Deployment (25 min)

> **Building Block:** Same SAM deployment as Lab 2 â financial use case.

### Step 14: Build the Application

```bash
mkdir lab3-fintech-app
cd lab3-fintech-app
sam init --runtime python3.11 --name financial-compliance-assistant
```

### Step 15: Deploy

```bash
sam build
sam deploy --guided
```

Configure with:
- Stack name: `lab3-fintech-app`
- Region: `us-east-1`
- Confirm changes: Y

### Step 16: Test the Deployed API

```bash
curl -X POST https://[api-url]/compliance \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the SAR filing requirements?"}'
```

---

## Cleanup

Delete all resources created in this lab:

```bash
# Delete Knowledge Base (via Bedrock console)
# Delete OpenSearch Serverless collection
# Delete Guardrail
# Delete CloudWatch dashboard
aws cloudformation delete-stack --stack-name lab3-fintech-app
```

---

## Key Takeaways

1. **Same Bedrock building blocks** â Knowledge Bases, Guardrails, Tools, CloudWatch work identically across industries
2. **Domain-specific guardrails** are critical â financial advice restrictions and PII blocking prevent compliance violations
3. **Audit logging** is a regulatory requirement â CloudTrail + CloudWatch provide the trail
4. **RAG citations** provide the evidence trail that regulators require

---

*Lab materials prepared for ROI Training delivery.*
