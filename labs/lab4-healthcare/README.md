# Lab 4: Healthcare â HIPAA-Compliant AI Assistant

**Course:** Building AI Applications with Anthropic on AWS Bedrock
**Lab:** Industry-Specific (replaces standard Labs 1 & 2)
**Duration:** 60 minutes
**Level:** Intermediate

---

## Lab Overview

You work for a telemedicine platform that needs an AI assistant to help clinicians access medical knowledge, document patient encounters, and manage scheduling â without exposing protected health information. In this lab, you'll build a HIPAA-aware clinical assistant using Claude on Bedrock with RAG for medical knowledge retrieval, guardrails for PHI/PII protection, and tools for appointment management â all with comprehensive audit logging.

### What You Will Build

- A Knowledge Base from medical reference documentation (S3 â Bedrock KB)
- RAG-powered medical knowledge queries with cited references
- Custom tools for appointment scheduling and prescription management
- Guardrails with strict PHI/PII blocking (HIPAA compliance)
- CloudWatch monitoring with audit trail for compliance

---

## Prerequisites

- [ ] AWS account with Amazon Bedrock access enabled
- [ ] Claude model access (Sonnet 4.6) approved
- [ ] S3 bucket: `s3://bedrock-training-[account-id]/lab4-healthcare/`
- [ ] Python 3.11+ installed with boto3
- [ ] AWS SAM CLI installed

**Course Repository:** **https://github.com/AWSClassroom-com/anthropic_on_aws**  contains sample data for all labs.

---

## Part 1: Medical Knowledge Base Setup (25 min)

> **Building Block:** Same process as Lab 1 â different documents.

### Step 1: Upload Medical Reference Documents to S3

Upload the provided sample medical reference documents:

```bash
aws s3 sync ./lab4-documents/ s3://bedrock-training-[account-id]/lab4-healthcare/
```

**Sample documents included:**
- `clinical_guidelines.txt` â Evidence-based treatment guidelines for common conditions
- `medication_reference.txt` â Drug interactions, dosing guidelines, contraindications
- `telehealth_protocols.txt` â Telemedicine visit procedures and documentation requirements
- `hipaa_compliance.txt` â PHI handling, minimum necessary standard, breach notification
- `scheduling_policy.txt` â Appointment types, durations, cancellation/no-show policies

> **Important:** These are fictional reference documents for training purposes. They should NOT be used for actual medical decision-making.

### Step 2: Create the Knowledge Base

1. Navigate to **Amazon Bedrock** â **Knowledge Bases**
2. Click **Create** â **Knowledge Base with vector store**
3. Configure:
   - **Name:** `lab4-clinical-reference-kb`
   - **S3 URI:** `s3://bedrock-training-[account-id]/lab4-healthcare/`
   - **Embedding model:** Titan Embeddings G1 - Text
   - **Vector store:** Amazon OpenSearch Serverless (Quick create)
4. Click **Create Knowledge Base** and wait for status: **Active**

### Step 3: Sync and Verify

1. Select the data source â click **Sync**
2. Wait for sync to complete
3. Verify document count matches uploaded files

### Step 4: Test Medical Knowledge Queries

Open the **Test Knowledge Base** panel and try:

| Query | Expected Behavior |
|-------|-------------------|
| "What are the first-line treatments for hypertension?" | Answer citing clinical_guidelines.txt |
| "What drug interactions should I check for metformin?" | Answer citing medication_reference.txt |
| "What documentation is required for a telehealth visit?" | Answer citing telehealth_protocols.txt |
| "What is patient John Smith's blood pressure?" | Should NOT find info (no patient data in KB) |

**Record your results.** Note how the system handles the out-of-scope patient query.

---

## Part 2: Clinical Tools (25 min)

> **Building Block:** Same tool schema pattern as Lab 2 â healthcare tools.

### Step 5: Define Clinical Tools

Test Claude's understanding of clinical workflow tools:

```
You are a clinical assistant with access to these tools:
- schedule_appointment(patient_id, provider_id, appointment_type, preferred_date): Schedules a patient appointment
- request_refill(patient_id, medication_name, pharmacy_id): Submits a prescription refill request
- check_availability(provider_id, date_range): Checks provider schedule availability

A patient calls requesting a follow-up appointment with Dr. Martinez next week and also needs a refill for their blood pressure medication. What tools would you use?
```

**Expected:** Claude should call `check_availability` first, then `schedule_appointment`, then `request_refill`.

### Step 6: Test Clinical Tool Routing

```
A patient reports their symptoms have worsened since their last visit and wants to see their doctor as soon as possible. They also mention they ran out of their prescribed medication.
```

**Expected:** Claude should prioritize checking availability for an urgent appointment, then handle the refill.

---

## Part 3: HIPAA-Compliant Guardrails (25 min)

> **Building Block:** Same guardrail creation process as Lab 2 â HIPAA-specific rules.

### Step 7: Create HIPAA Guardrails

1. Navigate to **Bedrock** â **Guardrails** â **Create guardrail**
2. **Name:** `HIPAAComplianceGuardrail`

### Step 8: Configure Content Filters

Set all content filters to **HIGH** for both input and output.

### Step 9: Configure Denied Topics

| Topic | Definition | Sample Phrases |
|-------|------------|----------------|
| Diagnosis | Providing definitive medical diagnoses without physician involvement | "You have diabetes", "This is definitely cancer" |
| Prescribing | Recommending specific medications or dosage changes without physician authorization | "You should take 20mg of lisinopril", "Switch to a different medication" |

### Step 10: Configure PII/PHI Filters

HIPAA requires strict protection of all 18 PHI identifiers:

| PII/PHI Type | Action |
|--------------|--------|
| SSN | **BLOCK** |
| Name (patient) | **ANONYMIZE** |
| Phone | **ANONYMIZE** |
| Email | **ANONYMIZE** |
| Address | **ANONYMIZE** |
| Date of Birth | **ANONYMIZE** |
| Medical Record Number | **BLOCK** |

### Step 11: Test HIPAA Guardrails

| Prompt | Expected Result |
|--------|----------------|
| "What are the guidelines for treating hypertension?" | **PASS** â general medical knowledge |
| "Patient John Smith, DOB 03/15/1980, MRN 12345, has diabetes" | **BLOCKED/ANONYMIZED** â PHI detected |
| "You definitely have strep throat and need antibiotics" | **BLOCKED** â diagnosis without physician |
| "What documentation is needed for a telehealth visit?" | **PASS** â procedural question |

---

## Part 4: Monitoring and HIPAA Audit Trail (20 min)

> **Building Block:** Same CloudWatch pattern as Lab 2 â with HIPAA audit requirements.

### Step 12: Set Up CloudWatch Monitoring

Create a monitoring dashboard:
- **Dashboard name:** `Lab4-ClinicalAssistant`
- **Metrics:** InvocationCount, InputTokenCount, OutputTokenCount, ResponseLatency, ErrorCount

### Step 13: Verify HIPAA Audit Logging

HIPAA requires audit controls (Â§164.312(b)):
1. Verify CloudTrail logs all Bedrock API calls
2. Confirm guardrail violations are logged (PHI exposure attempts)
3. Check that all access to the Knowledge Base is logged
4. Verify no PHI appears in CloudWatch logs (guardrails mask it before logging)

---

## Part 5: Application Deployment (25 min)

> **Building Block:** Same SAM deployment as Lab 2 â clinical use case.

### Step 14: Build the Application

```bash
mkdir lab4-clinical-assistant
cd lab4-clinical-assistant
sam init --runtime python3.11 --name clinical-assistant
```

### Step 15: Deploy

```bash
sam build
sam deploy --guided
```

Configure with:
- Stack name: `lab4-clinical-assistant`
- Region: `us-east-1`

### Step 16: Test the Deployed API

```bash
curl -X POST https://[api-url]/clinical \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the telehealth visit documentation requirements?"}'
```

---

## Cleanup

```bash
# Delete Knowledge Base (via Bedrock console)
# Delete OpenSearch Serverless collection
# Delete Guardrail
# Delete CloudWatch dashboard
aws cloudformation delete-stack --stack-name lab4-clinical-assistant
```

---

## Key Takeaways

1. **HIPAA compliance is about guardrails AND architecture** â PII filters block PHI at the model layer, but you also need encryption at rest (KMS), in transit (TLS), and audit logging (CloudTrail)
2. **Same Bedrock building blocks** â KB creation, guardrails, tools, deployment are identical across industries
3. **Denied topics prevent liability** â blocking diagnosis and prescribing protects against the AI practicing medicine
4. **Audit trail is non-negotiable** â every interaction must be logged for compliance reviews

---

*Lab materials prepared for ROI Training delivery.*
