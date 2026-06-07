# Anthropic Models on Amazon Bedrock

Student lab materials for the **Anthropic Models on Amazon Bedrock** course.

## Course Overview

This course teaches developers and cloud practitioners to deploy Anthropic's Claude models using Amazon Bedrock's managed infrastructure. Through hands-on labs, you'll build production applications leveraging Claude's advanced reasoning capabilities — including RAG with Knowledge Bases, tool use, guardrails, and monitoring.

## Labs

### Standard Labs

| Lab | Name | Duration | Description |
|-----|------|----------|-------------|
| Lab 1 | [Claude on Bedrock with RAG](labs/lab1/) | 45 min | Model invocation, Knowledge Base connection, RAG queries |
| Lab 2 | [Claude Code on Bedrock](labs/lab2/) | 65 min | Project Standards, Plan Mode, Model Switching, Agentic Workflows, Skills |
| Lab 3 | [Build a Complete Claude Application](labs/lab3/) | 95 min | Tool use, guardrails, CloudWatch, SAM deployment |

### Industry-Specific Labs (Optional — replace standard labs)

| Lab | Industry | Duration | Description |
|-----|----------|----------|-------------|
| Lab 3 | [Fintech: Document Processing & Compliance](labs/lab3-fintech/) | 120 min | KYC, AML compliance, transaction monitoring |
| Lab 4 | [Healthcare: HIPAA-Compliant AI Assistant](labs/lab4-healthcare/) | 120 min | Clinical reference, scheduling, PHI protection |
| Lab 5 | [Media: Content Intelligence Platform](labs/lab5-media/) | 120 min | Recommendations, classification, content moderation |

## Prerequisites

- AWS user with Amazon Bedrock access enabled (provided by Instructor)
- Claude model access (Opus 4.6, Sonnet 4.6, Haiku 4.5) approved in Bedrock (enabled on provided AWS user)
- Python 3.11+ installed (pre-installed on RVC)
- AWS CLI configured (pre-installed on RVC)
- AWS SAM CLI installed (for Lab 2 deployment)

## Quick Start

```bash
# Clone this repo
git clone https://github.com/AWSClassroom-com/anthropic_on_aws.git
cd anthropic_on_aws


## Course Delivery

This repository is maintained by [ROI Training](https://www.roitraining.com) for instructor-led delivery on AWS.

---

*Materials prepared for ROI Training delivery.*
