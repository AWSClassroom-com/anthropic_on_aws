"""
Lab 1: Model Comparison Script
Anthropic Models on AWS Bedrock

Nothing to edit. Open this file in VS Code, read it top to bottom, then run it.

What it does:
1. Sends the same support-ticket prompt to three Claude models
2. Records tokens, latency, and cost for each call
3. Projects the cost to production volumes
4. Checks its own results and prints a single PASS line

Run:  python scripts/compare_models.py
      python scripts/compare_models.py --demo-error
"""

import argparse
import json
import sys
import time

import boto3
from botocore.exceptions import ClientError

REGION = "us-east-1"

# The three models to compare. The "us." prefix selects a cross-region
# inference profile, which Claude models on Bedrock require.
# The 5.5 models use a short ID with no date.
MODELS = {
    "Sonnet 5.5": "us.anthropic.claude-sonnet-5-5",
    "Opus 5.5":   "us.anthropic.claude-opus-5-5",
    "Haiku 5.5":  "us.anthropic.claude-haiku-5-5",
}

# Added only by --demo-error. This ID does not exist on purpose.
BAD_MODEL = {"Bad model ID": "us.anthropic.claude-does-not-exist"}

PROMPT = """A customer says: "I ordered three items two weeks ago and only two arrived.
The third item shows as delivered but it is not here. I want a refund
for the missing item immediately and I am very frustrated."

Classify this ticket. Respond with JSON only, no preamble and no extra fields.
Use exactly these three keys:
  "sentiment"           one of: positive, neutral, negative
  "priority"            one of: low, medium, high
  "recommended_action"  a single short sentence"""

# Pricing per million tokens -- verify at https://aws.amazon.com/bedrock/pricing/
PRICING = {
    "us.anthropic.claude-sonnet-5-5": {"input": 2.00, "output": 10.00},
    "us.anthropic.claude-opus-5-5":   {"input": 4.00, "output": 20.00},
    "us.anthropic.claude-haiku-5-5":  {"input": 0.10, "output": 0.50},
}

# What a valid answer looks like, used by the self-check at the end.
ALLOWED_VALUES = {
    "sentiment": {"positive", "neutral", "negative"},
    "priority":  {"low", "medium", "high"},
}
EXPECTED_KEYS = {"sentiment", "priority", "recommended_action"}


def invoke_model(client, model_id: str, prompt: str) -> dict:
    """Invoke a Bedrock model and return results with token counts and cost."""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    })

    start = time.time()

    # EXPLORE: errors are returned as data rather than raised, so one
    # unavailable model does not stop the comparison. Lab 3 uses the same pattern.
    try:
        response = client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=body
        )
    except ClientError as e:
        return {
            "model_id":   model_id,
            "error_code": e.response["Error"]["Code"],
            "error":      e.response["Error"]["Message"],
        }
    latency_ms = round((time.time() - start) * 1000)

    result = json.loads(response["body"].read())

    # EXPLORE: the reply is found by type, not by position. Some models return
    # a thinking block first, so content[0] is not always the text.
    # EXPLORE: usage holds the token counts that cost is calculated from.
    return {
        "model_id":      model_id,
        "response_text": next(
            b["text"] for b in result["content"] if b.get("type") == "text"
        ),
        "input_tokens":  result["usage"]["input_tokens"],
        "output_tokens": result["usage"]["output_tokens"],
        "latency_ms":    latency_ms,
        "cost_usd":      calculate_cost(
            model_id,
            result["usage"]["input_tokens"],
            result["usage"]["output_tokens"],
        ),
    }


def calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """Pricing is quoted per million tokens, so divide by 1,000,000."""
    return (
        input_tokens * PRICING[model_id]["input"] +
        output_tokens * PRICING[model_id]["output"]
    ) / 1_000_000


def strip_fences(text: str) -> str:
    """Remove markdown code fences from model response."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def parse_json(text: str) -> tuple:
    """Attempt to parse text as JSON. Returns (parsed_dict, error_string)."""
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, str(e)


def display_name(model_id: str) -> str:
    return next((k for k, v in MODELS.items() if v == model_id), model_id)


def print_results(results: list) -> None:
    """Print comparison results in a readable format."""

    width = 60
    print()
    print("=" * width)
    print("  Model Comparison Results")
    print("=" * width)

    for r in results:
        print(f"\n{display_name(r['model_id'])}")

        parsed, error = parse_json(strip_fences(r["response_text"]))

        if parsed:
            print("  JSON valid:    YES")
            print("  Response:")
            for line in json.dumps(parsed, indent=4).splitlines():
                print(f"    {line}")
        else:
            print(f"  JSON valid:    NO -- {error}")
            print("  Response (raw):")
            for line in strip_fences(r["response_text"]).splitlines():
                print(f"    {line}")

        print(f"  Input tokens:  {r['input_tokens']}")
        print(f"  Output tokens: {r['output_tokens']}")
        print(f"  Latency:       {r['latency_ms']} ms")
        print(f"  Cost:          ${r['cost_usd']:.6f}")

    print()
    print("=" * width)


def cost_projection(results: list) -> None:
    """Print cost projections at production scale from actual token counts."""

    volumes = [10_000, 100_000]
    days_per_month = 30
    width = 60

    print()
    print("=" * width)
    print("  Cost Projections -- Production Scale")
    print("=" * width)
    print()
    print(f"  {'Model':<12}  {'Tokens/req':>10}  {'10k/day/mo':>12}  {'100k/day/mo':>13}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*12}  {'-'*13}")

    for r in results:
        tokens_per_req = r["input_tokens"] + r["output_tokens"]
        monthly_costs = [
            f"${r['cost_usd'] * volume * days_per_month:,.2f}" for volume in volumes
        ]
        print(
            f"  {display_name(r['model_id']):<12}  "
            f"{tokens_per_req:>10,}  "
            f"{monthly_costs[0]:>12}  "
            f"{monthly_costs[1]:>13}"
        )

    print()
    print("  Formula: cost_per_request x daily_volume x 30 days")
    print("  Verify current rates: https://aws.amazon.com/bedrock/pricing/")
    print("=" * width)
    print()


def self_check(results: list, skipped: dict, demo_error: bool) -> bool:
    """Check the run against what the lab expects and print one PASS line."""

    checks = []

    for name, model_id in MODELS.items():
        got = next((r for r in results if r["model_id"] == model_id), None)
        checks.append((f"{name}: call succeeded", got is not None))
        if got is None:
            continue

        parsed, _ = parse_json(strip_fences(got["response_text"]))
        valid = (
            isinstance(parsed, dict)
            and set(parsed) == EXPECTED_KEYS
            and all(parsed[k] in ALLOWED_VALUES[k] for k in ALLOWED_VALUES)
        )
        checks.append((f"{name}: JSON has the three keys with allowed values", valid))

        expected_cost = calculate_cost(model_id, got["input_tokens"], got["output_tokens"])
        checks.append((
            f"{name}: cost equals tokens x rate",
            got["input_tokens"] > 0 and abs(got["cost_usd"] - expected_cost) < 1e-12,
        ))

    if demo_error:
        bad_id = next(iter(BAD_MODEL.values()))
        checks.append(("Bad model ID was skipped and the run continued", bad_id in skipped))

    width = 60
    print("=" * width)
    print("  Self-Check")
    print("=" * width)
    for label, ok in checks:
        print(f"  {'✅' if ok else '❌'} {label}")
    print()

    passed = sum(ok for _, ok in checks)
    if passed == len(checks):
        print(f"All {len(checks)} checks passed! ✅")
        print()
        return True

    print(f"{passed} / {len(checks)} checks passed.")
    if skipped:
        print("Skipped models:")
        for model_id, message in skipped.items():
            print(f"  {display_name(model_id)}: {message}")
    print("If a model was skipped, tell your instructor.")
    print()
    return False


def main():
    parser = argparse.ArgumentParser(description="Compare Claude models on one prompt")
    parser.add_argument(
        "--demo-error",
        action="store_true",
        help="Add a model ID that does not exist, to see an error handled as data",
    )
    args = parser.parse_args()

    models = dict(MODELS)
    if args.demo_error:
        models.update(BAD_MODEL)

    print(f"\nConnecting to Amazon Bedrock in {REGION}...")
    client = boto3.client("bedrock-runtime", region_name=REGION)

    results = []
    skipped = {}
    for name, model_id in models.items():
        print(f"Invoking {name}...")
        result = invoke_model(client, model_id, PROMPT)
        if "error" in result:
            skipped[model_id] = f"{result['error_code']}: {result['error']}"
            print(f"  SKIPPED {name}: {skipped[model_id]}")
            continue
        results.append(result)

    if results:
        print_results(results)
        cost_projection(results)

    ok = self_check(results, skipped, args.demo_error)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
