# Anthropic Models on Amazon Bedrock

Student lab materials for the **Anthropic Models on Amazon Bedrock** course.

## Course Overview

This course teaches developers and cloud practitioners to deploy Anthropic's Claude models using Amazon Bedrock's managed infrastructure. Through hands-on labs, you'll build production applications leveraging Claude's advanced reasoning capabilities — including RAG with Knowledge Bases, tool use, guardrails, and monitoring.

## Labs

### Standard Labs

| Lab | Name | Duration | Description |
|-----|------|----------|-------------|
| Lab 1 | [Claude on Bedrock with RAG](labs/lab1/) | 30 min | Model invocation, Knowledge Base creation, RAG queries |
| Lab 2 | [Build a Complete Claude Application](labs/lab2/) | 95 min | Tool use, guardrails, CloudWatch, SAM deployment |

### Industry-Specific Labs (Optional — replace standard labs)

| Lab | Industry | Duration | Description |
|-----|----------|----------|-------------|
| Lab 3 | [Fintech: Document Processing & Compliance](labs/lab3-fintech/) | 120 min | KYC, AML compliance, transaction monitoring |
| Lab 4 | [Healthcare: HIPAA-Compliant AI Assistant](labs/lab4-healthcare/) | 120 min | Clinical reference, scheduling, PHI protection |
| Lab 5 | [Media: Content Intelligence Platform](labs/lab5-media/) | 120 min | Recommendations, classification, content moderation |

## Prerequisites

- AWS account with Amazon Bedrock access enabled
- Claude model access (Opus 4.6, Sonnet 4.6, Haiku 4.5) approved in Bedrock
- Python 3.11+ installed
- AWS CLI configured
- AWS SAM CLI installed (for Lab 2 deployment)

## Quick Start

```bash
# Clone this repo
git clone https://github.com/AWSClassroom-com/anthropic_on_aws.git
cd anthropic_on_aws

# Upload sample documents for your lab
# Lab 1 (Standard):
aws s3 sync sample-data/lab1/ s3://bedrock-training-[YOUR-ACCOUNT-ID]/lab1-documents/

# Lab 3 (Fintech):
aws s3 sync sample-data/lab3-fintech/ s3://bedrock-training-[YOUR-ACCOUNT-ID]/lab3-fintech/
```

Replace `[YOUR-ACCOUNT-ID]` with your 12-digit AWS account ID (no dashes).

## Repository Structure

```
anthropic_on_aws/
├── README.md                    # This file
├── labs/
│   ├── lab1/                    # Lab 1: Claude on Bedrock with RAG
│   │   └── README.md            # Lab guide
│   ├── lab2/                    # Lab 2: Complete Claude Application
│   │   ├── README.md            # Lab guide
│   │   └── starter/             # Starter code template
│   ├── lab3-fintech/            # Lab 3: Fintech Compliance
│   │   └── README.md
│   ├── lab4-healthcare/         # Lab 4: Healthcare HIPAA
│   │   └── README.md
│   └── lab5-media/              # Lab 5: Media Content Intelligence
│       └── README.md
├── sample-data/                 # S3 upload documents for each lab
│   ├── lab1/
│   ├── lab3-fintech/
│   ├── lab4-healthcare/
│   └── lab5-media/
└── docs/
    └── student_reference_sheet.md
```

## Course Delivery

This repository is maintained by [ROI Training](https://www.roitraining.com) for instructor-led delivery on AWS.

---

*Materials prepared for ROI Training delivery.*
