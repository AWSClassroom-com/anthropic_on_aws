"""
bedrock.py
Pre-built agentic loop for invoking Claude on Amazon Bedrock with tool use.

Students do not need to modify this file.
Read invoke_with_tools() after class to understand how the loop works.
"""
import json
import logging
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from src.config import AWS_REGION, MAX_ITERATIONS, MODEL_ID
from src.services.tools import execute_tool

logger = logging.getLogger(__name__)


class BedrockService:
    """Handles all Claude invocations via Amazon Bedrock."""

    def __init__(self) -> None:
        self.client = boto3.client('bedrock-runtime', region_name=AWS_REGION)
        self.model_id = MODEL_ID

    # ── Basic invocation (no tools) ───────────────────────────────────────────

    def invoke(
        self,
        messages: List[Dict],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invoke Claude without tools. Used for simple Q&A and RAG responses.

        Args:
            messages:      Conversation history in Bedrock message format.
            system_prompt: Optional system prompt to guide Claude's behavior.

        Returns:
            The full Bedrock response dict.
        """
        body: Dict[str, Any] = {
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2048,
            'messages': messages
        }

        if system_prompt:
            body['system'] = system_prompt

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            return json.loads(response['body'].read())

        except ClientError as e:
            logger.error('Bedrock invocation failed: %s', e)
            raise

    # ── Agentic loop (tools, no guardrail) ────────────────────────────────────

    def invoke_with_tools(
        self,
        messages: List[Dict],
        tools: List[Dict],
        system_prompt: Optional[str] = None,
        max_iterations: int = MAX_ITERATIONS
    ) -> Dict[str, Any]:
        """
        Invoke Claude with tool use. Runs the agentic loop until Claude
        returns stop_reason='end_turn' or max_iterations is reached.

        How the loop works:
          1. Call Claude with the current message history and tool definitions.
          2. If stop_reason is 'end_turn', Claude is done — return the response.
          3. If stop_reason is 'tool_use', Claude wants to call one or more tools:
               a. Append Claude's response (with tool_use blocks) to messages.
               b. Execute each requested tool via execute_tool().
               c. Append all tool results as a 'user' message.
               d. Loop — call Claude again with the updated message history.
          4. If max_iterations is reached without end_turn, return the last response.

        Args:
            messages:       Conversation history in Bedrock message format.
            tools:          List of tool definitions (from tools.TOOLS).
            system_prompt:  Optional system prompt.
            max_iterations: Safety cap on loop iterations.

        Returns:
            The final Bedrock response dict when stop_reason is 'end_turn'.
        """
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.debug('Agentic loop iteration %d / %d', iteration, max_iterations)

            # ── Step 1: Call Claude ───────────────────────────────────────────
            body: Dict[str, Any] = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2048,
                'messages': messages,
                'tools': tools
            }

            if system_prompt:
                body['system'] = system_prompt

            try:
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body)
                )
                result = json.loads(response['body'].read())

            except ClientError as e:
                logger.error('Bedrock invocation failed on iteration %d: %s', iteration, e)
                raise

            stop_reason = result.get('stop_reason', '')
            logger.debug('stop_reason: %s', stop_reason)

            # ── Step 2: Claude is done ────────────────────────────────────────
            if stop_reason == 'end_turn':
                return result

            # ── Step 3: Claude wants to use tools ─────────────────────────────
            if stop_reason == 'tool_use':

                # 3a. Add Claude's response (including tool_use blocks) to history
                messages.append({
                    'role': 'assistant',
                    'content': result['content']
                })

                # 3b + 3c. Execute each requested tool and collect results
                tool_results = []

                for block in result['content']:
                    if block.get('type') == 'tool_use':
                        tool_name = block['name']
                        tool_input = block['input']
                        tool_use_id = block['id']

                        logger.info('Executing tool: %s with input: %s', tool_name, tool_input)
                        print(f'[Executing tool: {tool_name}]')

                        tool_output = execute_tool(tool_name, tool_input)

                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': tool_use_id,
                            'content': json.dumps(tool_output)
                        })

                # Add all tool results as a single user message
                messages.append({
                    'role': 'user',
                    'content': tool_results
                })

                # 3d. Loop — Claude will use the tool results to form its answer
                continue

            # ── Unexpected stop_reason ────────────────────────────────────────
            logger.warning('Unexpected stop_reason: %s', stop_reason)
            return result

        # Max iterations reached
        logger.warning('Agentic loop reached max_iterations (%d) without end_turn.', max_iterations)
        return result

    # ── Agentic loop with guardrail ────────────────────────────────────────────

    def invoke_with_tools_and_guardrail(
        self,
        messages: List[Dict],
        tools: List[Dict],
        guardrail_id: str,
        guardrail_version: str,
        system_prompt: Optional[str] = None,
        max_iterations: int = MAX_ITERATIONS
    ) -> Dict[str, Any]:
        """
        Same as invoke_with_tools but applies a Bedrock Guardrail to every
        Claude invocation in the loop.

        Guardrail blocking is detected via the response header
        'x-amzn-bedrock-guardrail-action'. When blocked, a safe response
        is returned immediately without continuing the loop.

        Args:
            messages:         Conversation history.
            tools:            Tool definitions.
            guardrail_id:     Bedrock Guardrail identifier.
            guardrail_version: Guardrail version string (usually '1').
            system_prompt:    Optional system prompt.
            max_iterations:   Safety cap on loop iterations.

        Returns:
            The final response dict, or a blocked-response dict if guardrail fires.
        """
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.debug('Guardrail loop iteration %d / %d', iteration, max_iterations)

            body: Dict[str, Any] = {
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2048,
                'messages': messages,
                'tools': tools
            }

            if system_prompt:
                body['system'] = system_prompt

            try:
                response = self.client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps(body),
                    guardrailIdentifier=guardrail_id,
                    guardrailVersion=guardrail_version
                )

            except ClientError as e:
                logger.error('Bedrock guardrail invocation failed: %s', e)
                raise

            # Check if the guardrail blocked this request
            headers = response.get('ResponseMetadata', {}).get('HTTPHeaders', {})
            guardrail_action = headers.get('x-amzn-bedrock-guardrail-action', '')

            if guardrail_action == 'BLOCKED':
                logger.info('Request blocked by guardrail %s', guardrail_id)
                return {
                    'content': [{
                        'type': 'text',
                        'text': (
                            'I\'m sorry, I\'m not able to help with that request. '
                            'Please contact our support team if you need further assistance.'
                        )
                    }],
                    'stop_reason': 'guardrail_blocked',
                    'was_blocked': True
                }

            result = json.loads(response['body'].read())
            stop_reason = result.get('stop_reason', '')

            if stop_reason == 'end_turn':
                return result

            if stop_reason == 'tool_use':
                messages.append({
                    'role': 'assistant',
                    'content': result['content']
                })

                tool_results = []

                for block in result['content']:
                    if block.get('type') == 'tool_use':
                        tool_name = block['name']
                        tool_input = block['input']
                        tool_use_id = block['id']

                        logger.info('Executing tool: %s', tool_name)
                        print(f'[Executing tool: {tool_name}]')

                        tool_output = execute_tool(tool_name, tool_input)

                        tool_results.append({
                            'type': 'tool_result',
                            'tool_use_id': tool_use_id,
                            'content': json.dumps(tool_output)
                        })

                messages.append({
                    'role': 'user',
                    'content': tool_results
                })

                continue

            logger.warning('Unexpected stop_reason: %s', stop_reason)
            return result

        logger.warning('Guardrail loop reached max_iterations (%d).', max_iterations)
        return result
