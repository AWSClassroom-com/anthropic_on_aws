"""
test_deployed_api.py
Tests the deployed API Gateway + Lambda endpoint after SAM deployment.

Usage:
    macOS/Linux:
        python tests/test_deployed_api.py https://YOUR-ENDPOINT/prod/chat

    Windows (PowerShell):
        python tests\\test_deployed_api.py https://YOUR-ENDPOINT/prod/chat

Replace YOUR-ENDPOINT with the ApiEndpoint value from sam deploy output.
"""
import json
import sys
import urllib.request
import urllib.error

PASS = '✅'
FAIL = '❌'
results = []


def check(label: str, condition: bool, detail: str = '') -> None:
    status = PASS if condition else FAIL
    print(f'  {status} {label}')
    if not condition and detail:
        print(f'     → {detail}')
    results.append(condition)


def post(url: str, payload: dict) -> dict:
    """Send a POST request and return the parsed JSON response."""
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def main() -> None:
    if len(sys.argv) < 2:
        print('\nUsage: python tests/test_deployed_api.py <API_ENDPOINT_URL>')
        print('Example: python tests/test_deployed_api.py https://abc123.execute-api.us-east-1.amazonaws.com/prod/chat')
        sys.exit(1)

    api_url = sys.argv[1].rstrip('/')
    print('\n' + '=' * 60)
    print('Lab 3 — Part 4: Deployed API Tests')
    print('=' * 60)
    print(f'\nTesting endpoint: {api_url}')

    # ── Test 1: Order lookup ──────────────────────────────────────────────────
    print('\nTest 1: Order lookup via deployed API')
    try:
        response = post(api_url, {
            'message': 'What is the status of order ORD-12345?',
            'customer_id': 'CUST-001'
        })
        check('HTTP 200 and response received', 'response' in response,
              f'Unexpected response: {response}')
        check('Not blocked by guardrail', not response.get('blocked', False))
        check('Response mentions order or shipping',
              any(w in response.get('response', '').lower()
                  for w in ['order', 'ship', 'deliver', 'track']),
              f"Response: {response.get('response', '')[:200]}")
    except urllib.error.HTTPError as e:
        print(f'  {FAIL} HTTP {e.code}: {e.reason}')
        results.extend([False, False, False])
    except Exception as e:
        print(f'  {FAIL} Exception: {e}')
        results.extend([False, False, False])

    # ── Test 2: Guardrail block ───────────────────────────────────────────────
    print('\nTest 2: Guardrail blocks denied topic via deployed API')
    try:
        response = post(api_url, {
            'message': 'Which stocks should I invest in right now?'
        })
        check('Response received', 'response' in response,
              f'Unexpected response: {response}')
        check('Request was blocked', response.get('blocked', False),
              'Investment advice should be blocked by guardrail')
    except urllib.error.HTTPError as e:
        print(f'  {FAIL} HTTP {e.code}: {e.reason}')
        results.extend([False, False])
    except Exception as e:
        print(f'  {FAIL} Exception: {e}')
        results.extend([False, False])

    # ── Test 3: Empty message validation ─────────────────────────────────────
    print('\nTest 3: Empty message returns 400 error')
    try:
        urllib.request.urlopen(
            urllib.request.Request(
                api_url,
                data=json.dumps({'message': ''}).encode(),
                headers={'Content-Type': 'application/json'},
                method='POST'
            ),
            timeout=30
        )
        print(f'  {FAIL} Expected HTTP 400 but got 200')
        results.append(False)
    except urllib.error.HTTPError as e:
        check('Returns HTTP 400 for empty message', e.code == 400,
              f'Expected 400, got {e.code}')
    except Exception as e:
        print(f'  {FAIL} Exception: {e}')
        results.append(False)

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = sum(results)
    total = len(results)
    print('\n' + '=' * 60)

    if passed == total:
        print(f'All {total} checks passed! {PASS}')
        print('\nLab 3 complete. Your production API is working correctly.')
    else:
        print(f'{passed} / {total} checks passed.')
        print('\nTroubleshooting:')
        print('  - Confirm SAM deployment completed: check CloudFormation in AWS Console')
        print('  - Check Lambda logs: CloudWatch → Log groups → /aws/lambda/lab3-chat-handler')
        print('  - Verify KNOWLEDGE_BASE_ID and GUARDRAIL_ID are correct in SAM parameters')
        print('  - Confirm Bedrock model access is enabled in your region')

    print('=' * 60 + '\n')
    sys.exit(0 if passed == total else 1)


if __name__ == '__main__':
    main()
