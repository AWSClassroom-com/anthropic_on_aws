"""
test_tools.py
Tests the execute_tool() function students implement in Part 1 of Lab 3.

Run with:
    macOS/Linux:  python tests/test_tools.py
    Windows:      python tests\\test_tools.py
"""
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.tools import execute_tool

PASS = '✅'
FAIL = '❌'
results = []


def check(label: str, condition: bool, detail: str = '') -> None:
    status = PASS if condition else FAIL
    print(f'  {status} {label}')
    if not condition and detail:
        print(f'     → {detail}')
    results.append(condition)


print('\n' + '=' * 60)
print('Lab 3 — Part 1: Testing execute_tool()')
print('=' * 60)


# ── Test 1: lookup_order ──────────────────────────────────────────────────────
print('\nTest 1: lookup_order')
result = execute_tool('lookup_order', {'order_id': 'ORD-12345'})
check('Returns a dict', isinstance(result, dict))
check('No error key', 'error' not in result,
      f"Got error: {result.get('error')}")
check('Has order_id', result.get('order_id') == 'ORD-12345')
check('Has status', 'status' in result)
check('Has tracking_number', 'tracking_number' in result)


# ── Test 2: lookup_order with invalid ID ─────────────────────────────────────
print('\nTest 2: lookup_order with invalid order ID')
result = execute_tool('lookup_order', {'order_id': 'INVALID-999'})
check('Returns a dict', isinstance(result, dict))
check('Returns error for bad ID', 'error' in result,
      'Expected an error dict for an order ID that does not start with ORD-')


# ── Test 3: create_ticket ─────────────────────────────────────────────────────
print('\nTest 3: create_ticket')
result = execute_tool('create_ticket', {
    'customer_id': 'CUST-001',
    'issue_summary': 'Order ORD-12345 has not arrived after 10 days.',
    'priority': 'high'
})
check('Returns a dict', isinstance(result, dict))
check('No error key', 'error' not in result,
      f"Got error: {result.get('error')}")
check('Has ticket_id', 'ticket_id' in result)
check('ticket_id starts with TKT-', str(result.get('ticket_id', '')).startswith('TKT-'))
check('Priority is high', result.get('priority') == 'high')


# ── Test 4: create_ticket with default priority ───────────────────────────────
print('\nTest 4: create_ticket uses default priority when omitted')
result = execute_tool('create_ticket', {
    'customer_id': 'CUST-002',
    'issue_summary': 'General question about my order.'
    # priority intentionally omitted
})
check('Returns a dict', isinstance(result, dict))
check('No error key', 'error' not in result,
      f"Got error: {result.get('error')}")
check('Default priority is medium', result.get('priority') == 'medium',
      f"Expected 'medium', got '{result.get('priority')}'")


# ── Test 5: get_account_status ────────────────────────────────────────────────
print('\nTest 5: get_account_status')
result = execute_tool('get_account_status', {'customer_id': 'CUST-001'})
check('Returns a dict', isinstance(result, dict))
check('No error key', 'error' not in result,
      f"Got error: {result.get('error')}")
check('Has membership_tier', 'membership_tier' in result)
check('Has loyalty_points', 'loyalty_points' in result)
check('Has benefits list', isinstance(result.get('benefits'), list))


# ── Test 6: unknown tool ──────────────────────────────────────────────────────
print('\nTest 6: unknown tool name returns error dict')
result = execute_tool('nonexistent_tool', {})
check('Returns a dict', isinstance(result, dict))
check('Returns error key', 'error' in result,
      'Expected an error dict for an unknown tool name')


# ── Summary ───────────────────────────────────────────────────────────────────
passed = sum(results)
total = len(results)
print('\n' + '=' * 60)

if passed == total:
    print(f'All {total} checks passed! {PASS}')
    print('\nCheckpoint 1 complete — move on to Part 2.')
else:
    print(f'{passed} / {total} checks passed.')
    print('\nReview the failing checks above and update execute_tool() in')
    print('src/services/tools.py, then re-run this script.')

print('=' * 60 + '\n')

sys.exit(0 if passed == total else 1)
