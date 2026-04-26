"""
tools.py
Defines the tools Claude can use and the logic to execute them.

YOUR TASK: Complete the execute_tool() function in Part 1 of the lab.
Everything else in this file is pre-built and ready to use.
"""
from datetime import datetime, timedelta
from typing import Dict


# ── Tool Definitions ──────────────────────────────────────────────────────────
# Claude reads these definitions to decide when and how to call each tool.
# The 'description' field is critical — vague descriptions cause incorrect routing.

TOOLS = [
    {
        'name': 'lookup_order',
        'description': (
            'Retrieves the current status and details of a customer order. '
            'Use this when the customer asks about order status, delivery, '
            'shipping, or tracking. Returns order status, items, total, '
            'tracking number, and estimated delivery date.'
        ),
        'input_schema': {
            'type': 'object',
            'properties': {
                'order_id': {
                    'type': 'string',
                    'description': (
                        'The order ID to look up. Format is ORD- followed '
                        'by numbers, e.g. ORD-12345.'
                    )
                }
            },
            'required': ['order_id']
        }
    },
    {
        'name': 'create_ticket',
        'description': (
            'Creates a customer support ticket for issues that need human follow-up. '
            'Use this when the customer reports a problem, requests a refund, '
            'or asks to speak with someone. Returns a ticket ID and estimated '
            'response time.'
        ),
        'input_schema': {
            'type': 'object',
            'properties': {
                'customer_id': {
                    'type': 'string',
                    'description': 'The customer ID. Format is CUST- followed by numbers.'
                },
                'issue_summary': {
                    'type': 'string',
                    'description': 'A brief description of the customer issue.'
                },
                'priority': {
                    'type': 'string',
                    'enum': ['low', 'medium', 'high'],
                    'description': (
                        'Ticket priority. Use high for lost orders or billing issues, '
                        'medium for general complaints, low for questions.'
                    )
                }
            },
            'required': ['customer_id', 'issue_summary']
        }
    },
    {
        'name': 'get_account_status',
        'description': (
            'Retrieves a customer account summary including membership tier, '
            'loyalty points, and recent order count. Use this when the customer '
            'asks about their account, rewards, points balance, or membership benefits.'
        ),
        'input_schema': {
            'type': 'object',
            'properties': {
                'customer_id': {
                    'type': 'string',
                    'description': 'The customer ID. Format is CUST- followed by numbers.'
                }
            },
            'required': ['customer_id']
        }
    }
]


# ── Tool Execution ─────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: Dict) -> Dict:
    """
    Execute a tool by name and return the result.

    The pre-built agentic loop calls this function automatically when Claude
    requests a tool. Your job is to route each tool_name to the correct
    helper function below.

    Args:
        tool_name:  The name of the tool Claude wants to call.
        tool_input: A dict of parameters Claude is passing to the tool.

    Returns:
        A dict with the tool result. Return errors as data (see helper
        functions below) rather than raising exceptions.

    -------------------------------------------------------------------------
    YOUR TASK: Complete this function.

    - Handle 'lookup_order' by calling _lookup_order()
    - Handle 'create_ticket' by calling _create_ticket()
    - Handle 'get_account_status' by calling _get_account_status()
    - Return an error dict for any unknown tool_name

    The helper functions are already implemented below.
    Check their signatures to see what parameters they expect.
    -------------------------------------------------------------------------
    """

    if tool_name == 'lookup_order':
        return _lookup_order(tool_input['order_id'])

    # TODO: Add create_ticket handler

    # TODO: Add get_account_status handler

    else:
        return {'error': f"Unknown tool: '{tool_name}'"}


# ── Helper Functions (pre-built) ───────────────────────────────────────────────
# These simulate real API/database calls.
# In production these would query your actual order management system.

def _lookup_order(order_id: str) -> Dict:
    """Look up an order by ID and return its current status."""
    if not order_id.startswith('ORD-'):
        return {
            'error': f"Order '{order_id}' not found.",
            'suggestion': 'Order IDs start with ORD- followed by numbers, e.g. ORD-12345.'
        }

    return {
        'order_id': order_id,
        'status': 'shipped',
        'items': [
            {'name': 'Widget Pro', 'quantity': 2, 'unit_price': 49.99},
            {'name': 'Gadget Max', 'quantity': 1, 'unit_price': 79.99}
        ],
        'subtotal': 179.97,
        'tax': 14.40,
        'total': 194.37,
        'shipped_date': (datetime.now() - timedelta(days=2)).strftime('%B %d, %Y'),
        'estimated_delivery': (datetime.now() + timedelta(days=3)).strftime('%B %d, %Y'),
        'tracking_number': 'TRK' + str(abs(hash(order_id)))[:9],
        'carrier': 'FastShip Express'
    }


def _create_ticket(
    customer_id: str,
    issue_summary: str,
    priority: str = 'medium'
) -> Dict:
    """Create a support ticket and return the ticket details."""
    if not customer_id.startswith('CUST-'):
        return {
            'error': f"Customer '{customer_id}' not found.",
            'suggestion': 'Customer IDs start with CUST- followed by numbers.'
        }

    ticket_id = 'TKT-' + str(abs(hash(customer_id + issue_summary)))[:6].upper()
    response_times = {'low': '48 hours', 'medium': '24 hours', 'high': '4 hours'}

    return {
        'ticket_id': ticket_id,
        'customer_id': customer_id,
        'issue_summary': issue_summary,
        'priority': priority,
        'status': 'open',
        'created_at': datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        'estimated_response': response_times.get(priority, '24 hours'),
        'message': (
            f"Ticket {ticket_id} has been created. A support agent will "
            f"contact you within {response_times.get(priority, '24 hours')}."
        )
    }


def _get_account_status(customer_id: str) -> Dict:
    """Return a customer account summary."""
    if not customer_id.startswith('CUST-'):
        return {
            'error': f"Customer '{customer_id}' not found.",
            'suggestion': 'Customer IDs start with CUST- followed by numbers.'
        }

    return {
        'customer_id': customer_id,
        'membership_tier': 'Gold',
        'loyalty_points': 2450,
        'points_value_usd': 24.50,
        'member_since': 'March 2022',
        'total_orders': 18,
        'orders_last_90_days': 3,
        'benefits': [
            'Free standard shipping on all orders',
            'Early access to sales',
            '10% discount on accessories',
            'Dedicated support queue'
        ],
        'next_tier': 'Platinum',
        'points_to_next_tier': 550
    }
