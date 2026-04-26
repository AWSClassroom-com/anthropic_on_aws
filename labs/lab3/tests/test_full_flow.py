"""
test_full_flow.py
Tests the full agentic loop end-to-end against Amazon Bedrock.

Requires valid AWS credentials and Bedrock model access.
Run AFTER completing Part 1 (all test_tools.py checks passing).

Run with:
    macOS/Linux:  python tests/test_full_flow.py
    Windows:      python tests\\test_full_flow.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.bedrock import BedrockService
from src.services.tools import TOOLS

PASS = '✅'
FAIL = '❌'
results = []

bedrock = BedrockService()


def check(label: str, condition: bool, detail: str = '') -> None:
    status = PASS if condition else FAIL
    print(f'  {status} {label}')
    if not condition and detail:
        print(f'     → {detail}')
    results.append(condition)


def run_test(label: str, message: str, customer_id: str = '') -> dict:
    print(f'\n{label}')
    print(f'  User: "{message}"')

    user_content = message
    if customer_id:
        user_content = f'[Customer ID: {customer_id}]\n\n{message}'

    messages = [{'role': 'user', 'content': user_content}]

    result = bedrock.invoke_with_tools(
        messages=messages,
        tools=TOOLS,
        system_prompt=(
            'You are a helpful e-commerce customer support assistant. '
            'Use the available tools to answer customer questions.'
        )
    )

    response_text = ''
    for block in result.get('content', []):
        if block.get('type') == 'text':
            response_text = block['text']
            break

    print(f'  Claude: "{response_text[:200]}{"..." if len(response_text) > 200 else ""}"')
    return result


print('\n' + '=' * 60)
print('Lab 3 — Part 2: Full Agentic Loop Tests')
print('=' * 60)
print('\nConnecting to Amazon Bedrock...')

# ── Test 1: Single tool call ──────────────────────────────────────────────────
try:
    result = run_test(
        'Test 1: Single tool call — order lookup',
        'What is the status of my order ORD-12345?',
        customer_id='CUST-001'
    )
    response_text = next(
        (b['text'] for b in result.get('content', []) if b.get('type') == 'text'), ''
    )
    check('stop_reason is end_turn', result.get('stop_reason') == 'end_turn',
          f"Got: {result.get('stop_reason')}")
    check('Response mentions ORD-12345', 'ORD-12345' in response_text,
          'Expected order ID in response')
    check('Response mentions shipping or delivery',
          any(w in response_text.lower() for w in ['ship', 'deliver', 'track']),
          'Expected shipping info in response')

except Exception as e:
    print(f'  {FAIL} Test 1 failed with exception: {e}')
    results.extend([False, False, False])


# ── Test 2: Multi-tool call ───────────────────────────────────────────────────
try:
    result = run_test(
        'Test 2: Multi-tool call — order lookup + create ticket',
        'My order ORD-99999 has not arrived. Please create a support ticket.',
        customer_id='CUST-002'
    )
    response_text = next(
        (b['text'] for b in result.get('content', []) if b.get('type') == 'text'), ''
    )
    check('stop_reason is end_turn', result.get('stop_reason') == 'end_turn',
          f"Got: {result.get('stop_reason')}")
    check('Response mentions a ticket',
          any(w in response_text.lower() for w in ['ticket', 'tkt', 'support', 'agent']),
          'Expected ticket confirmation in response')

except Exception as e:
    print(f'  {FAIL} Test 2 failed with exception: {e}')
    results.extend([False, False])


# ── Test 3: Account status ────────────────────────────────────────────────────
try:
    result = run_test(
        'Test 3: Account status tool',
        'What is my membership tier and how many loyalty points do I have?',
        customer_id='CUST-001'
    )
    response_text = next(
        (b['text'] for b in result.get('content', []) if b.get('type') == 'text'), ''
    )
    check('stop_reason is end_turn', result.get('stop_reason') == 'end_turn',
          f"Got: {result.get('stop_reason')}")
    check('Response mentions membership or points',
          any(w in response_text.lower() for w in ['gold', 'platinum', 'points', 'member']),
          'Expected account info in response')

except Exception as e:
    print(f'  {FAIL} Test 3 failed with exception: {e}')
    results.extend([False, False])


# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(results)
total = len(results)
print('\n' + '=' * 60)

if passed == total:
    print(f'All {total} checks passed! {PASS}')
    print('\nCheckpoint 2 complete — move on to Part 3 (Guardrails).')
else:
    print(f'{passed} / {total} checks passed.')
    print('\nIf Bedrock returned an error, check:')
    print('  - AWS credentials: aws sts get-caller-identity')
    print('  - Model access: Bedrock Console → Model access')
    print('  - KNOWLEDGE_BASE_ID in your .env file')

print('=' * 60 + '\n')

sys.exit(0 if passed == total else 1)
