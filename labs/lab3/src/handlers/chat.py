"""
chat.py
AWS Lambda handler for the customer support chat API.

Receives POST /chat requests from API Gateway, routes to the appropriate
Bedrock invocation path (with or without guardrail), and returns a response.
"""
import json
import logging
import os
from typing import Any, Dict

from src.config import GUARDRAIL_ID, GUARDRAIL_VERSION
from src.services.bedrock import BedrockService
from src.services.knowledge import KnowledgeService
from src.services.monitoring import MonitoringService, Timer
from src.services.tools import TOOLS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialise services once per Lambda container (not per invocation)
bedrock = BedrockService()
knowledge = KnowledgeService()
monitoring = MonitoringService()

SYSTEM_PROMPT = """You are a helpful customer support assistant for an e-commerce company.

You have access to tools that let you look up real-time information:
- lookup_order: Check the status of a specific order
- create_ticket: Create a support ticket for issues needing human follow-up
- get_account_status: Retrieve a customer's account and loyalty information

You also have access to company documentation via your knowledge base for
questions about policies, shipping, returns, and general information.

Always be polite, concise, and helpful. If you cannot resolve an issue,
create a support ticket and let the customer know what to expect."""


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda entry point.

    Expected request body:
        {
            "message": "What is the status of my order ORD-12345?",
            "customer_id": "CUST-001",          # optional
            "session_id": "abc123"              # optional, for conversation continuity
        }

    Returns:
        {
            "response": "Your order ORD-12345 has been shipped...",
            "blocked": false,
            "session_id": "abc123"
        }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        message = body.get('message', '').strip()
        customer_id = body.get('customer_id', '')
        session_id = body.get('session_id', '')

        if not message:
            return _response(400, {'error': 'Request body must include a non-empty "message" field.'})

        # Build user message, optionally including customer context
        user_content = message
        if customer_id:
            user_content = f'[Customer ID: {customer_id}]\n\n{message}'

        messages = [{'role': 'user', 'content': user_content}]

        with Timer() as timer:
            # Route to guardrail-protected path if GUARDRAIL_ID is configured
            if GUARDRAIL_ID:
                result = bedrock.invoke_with_tools_and_guardrail(
                    messages=messages,
                    tools=TOOLS,
                    guardrail_id=GUARDRAIL_ID,
                    guardrail_version=GUARDRAIL_VERSION,
                    system_prompt=SYSTEM_PROMPT
                )
            else:
                result = bedrock.invoke_with_tools(
                    messages=messages,
                    tools=TOOLS,
                    system_prompt=SYSTEM_PROMPT
                )

        was_blocked = result.get('was_blocked', False)
        tool_count = _count_tool_calls(result)

        monitoring.record_request(
            was_blocked=was_blocked,
            tool_count=tool_count,
            latency_ms=timer.elapsed_ms
        )

        response_text = _extract_text(result)

        return _response(200, {
            'response': response_text,
            'blocked': was_blocked,
            'session_id': session_id
        })

    except Exception as e:
        logger.error('Unhandled error in chat handler: %s', e, exc_info=True)
        return _response(500, {'error': 'An internal error occurred. Please try again.'})


def _extract_text(result: Dict) -> str:
    """Extract the text response from a Bedrock result."""
    for block in result.get('content', []):
        if block.get('type') == 'text':
            return block['text']
    return 'I was unable to generate a response. Please try again.'


def _count_tool_calls(result: Dict) -> int:
    """Count tool_use blocks in a Bedrock result."""
    return sum(
        1 for block in result.get('content', [])
        if block.get('type') == 'tool_use'
    )


def _response(status_code: int, body: Dict) -> Dict:
    """Format an API Gateway response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }
