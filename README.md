# Anthropic Models on Amazon Bedrock

**Last Updated 22 Sept 2026**

Welcome to Anthropic Models on Amazon Bedrock! This repo serves as the source for your lab guides.

## Course Overview

This course teaches developers and cloud practitioners to deploy Anthropic's Claude models using Amazon Bedrock's managed infrastructure. Through hands-on labs, you will build production applications that use Claude's reasoning capabilities, including RAG with Knowledge Bases, tool use, guardrails, and monitoring.

## Labs

### Lab 1: Claude on Bedrock with RAG

**Duration:** 45 minutes | [Open the lab](labs/lab1/)

You invoke Claude Opus 4.6, Sonnet 4.6, and Haiku 4.5 through the Amazon Bedrock InvokeModel API using boto3, comparing how each model classifies the same customer support ticket. You then pull token counts and latency out of the API responses, calculate the real per-invocation cost, and project it to production volumes, so that choosing a model becomes a measured decision rather than a guess. The lab closes on Amazon Bedrock Knowledge Bases, where you query a shared knowledge base with `retrieve_and_generate` and verify that every claim in Claude's answer traces back to a cited source document.

### Lab 2: Claude Code on Bedrock

**Duration:** 75 minutes | [Open the lab](labs/lab2/)

You install Claude Code, connect it to Amazon Bedrock through your AWS profile, and pin the exact inference profiles it will call. The lab works through Plan mode with Claude Opus for architectural decisions and Claude Sonnet for execution, which is how you control cost by matching the model to the task, then through CLAUDE.md and skills, which are plain files you commit to git so that an entire team inherits the same conventions and procedures. You finish by auditing and fixing a production devcontainer, the configuration that lets Claude Code run autonomously in CI/CD pipelines or regulated environments without exposing your credentials or your filesystem.

### Lab 3: Production Tool Use and Guardrails with Claude

**Duration:** 90 minutes | [Open the lab](labs/lab3/)

You design and implement custom tools for Claude, then work through the agentic loop that decides when to call a tool, when to query the Knowledge Base from Lab 1, and when to answer directly from the model's own knowledge. You configure Amazon Bedrock Guardrails with content filters, denied topics, and PII masking, giving you a protection layer that sits outside your prompt and cannot be talked around by a prompt injection attempt. The lab ends with a real deployment, where AWS SAM packages the application onto AWS Lambda behind Amazon API Gateway, and you trace a live request through Amazon CloudWatch logs to confirm your tool code ran in production.

## Prerequisites

- AWS user with Amazon Bedrock access enabled (provided by Instructor)
- Claude model access (Opus 4.6, Sonnet 4.6, Haiku 4.5) approved in Bedrock (enabled on provided AWS user)
- Python 3.11+ installed (pre-installed on RVC)
- AWS CLI configured (pre-installed on RVC)
- AWS SAM CLI installed (for Lab 3 deployment)

## Course Delivery

This repository is maintained by [ROI Training](https://www.roitraining.com) for instructor-led delivery on AWS.

---

*Materials prepared for ROI Training delivery.*
