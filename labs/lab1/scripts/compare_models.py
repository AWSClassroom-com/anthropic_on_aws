"""
Lab 1: Model Comparison Script
Anthropic Models on AWS Bedrock
 
Students complete two TODO sections:
1. Fill in the MODELS dict with inference profile IDs
2. Complete the return dict in invoke_model()
 
Run: python scripts/compare_models.py
"""
 
import boto3
import json
import time
 
REGION = "us-east-1"
 
# TODO: Add the three model IDs here
# Use inference profile format: us.anthropic.claude-[model]
MODELS = {
    "Sonnet 4.6": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    # Add Opus 4.6 and Haiku 4.5 here
}
 
PROMPT = """A customer says: "I ordered three items two weeks ago and only two arrived.
The third item shows as delivered but it is not here. I want a refund
for the missing item immediately and I am very frustrated."
 
Classify this ticket: sentiment, priority, recommended action.
Respond in JSON only."""
 
# Pricing per million tokens -- verify at https://aws.amazon.com/bedrock/pricing/
PRICING = {
    "us.anthropic.claude-sonnet-4-5-20250929-v1:0": {"input": 3.00,  "output": 15.00},
    "us.anthropic.claude-opus-4-6-v1":              {"input": 15.00, "output": 75.00},
    "us.anthropic.claude-haiku-4-5-20251001-v1:0":  {"input": 0.80,  "output": 4.00},
}
 
 
def invoke_model(client, model_id: str, prompt: str) -> dict:
    """Invoke a Bedrock model and return results with token counts and cost."""
 
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    })
 
    start = time.time()
    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        accept="application/json",
        body=body
    )
    latency_ms = round((time.time() - start) * 1000)
 
    result = json.loads(response["body"].read())
 
    return {
    #TODO 2
    # Add model response return DICT here
	
}
 
 
def strip_fences(text: str) -> str:
    """Remove markdown code fences from model response."""
    text = text.strip()
    if text.startswith("```"):
        # Remove opening fence (```json or ``` etc)
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        # Remove closing fence
        text = text.rsplit("```", 1)[0]
    return text.strip()
 
 
def parse_json(text: str) -> tuple:
    """
    Attempt to parse text as JSON.
    Returns (parsed_dict, error_string).
    """
    import json as _json
    try:
        parsed = _json.loads(text)
        return parsed, None
    except _json.JSONDecodeError as e:
        return None, str(e)
 
 
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
        display_name = next(
            (k for k, v in MODELS.items() if v == r["model_id"]),
            r["model_id"]
        )
        tokens_per_req = r["input_tokens"] + r["output_tokens"]
        cost_per_req = r["cost_usd"]
 
        monthly_costs = []
        for volume in volumes:
            monthly = cost_per_req * volume * days_per_month
            monthly_costs.append(f"${monthly:,.2f}")
 
        print(
            f"  {display_name:<12}  "
            f"{tokens_per_req:>10,}  "
            f"{monthly_costs[0]:>12}  "
            f"{monthly_costs[1]:>13}"
        )
 
    print()
    print("  Formula: cost_per_request x daily_volume x 30 days")
    print("  Verify current rates: https://aws.amazon.com/bedrock/pricing/")
    print("=" * width)
    print()
    print("  Step 9 question: At 10,000 tickets per day, what is the")
    print("  monthly cost difference between Sonnet and Haiku?")
    print("  Is that difference worth the quality gap you observed?")
    print()
 
 
def print_results(results: list) -> None:
    """Print comparison results in a readable format."""
 
    import json as _json
    width = 60
    print()
    print("=" * width)
    print("  Model Comparison Results")
    print("=" * width)
 
    for r in results:
        # Get display name from MODELS dict
        display_name = next(
            (k for k, v in MODELS.items() if v == r["model_id"]),
            r["model_id"]
        )
        print(f"\n{display_name}")
 
        # Strip markdown fences and attempt JSON parse
        clean_text = strip_fences(r["response_text"])
        parsed, error = parse_json(clean_text)
 
        if parsed:
            print(f"  JSON valid:    YES")
            print(f"  Response:")
            formatted = _json.dumps(parsed, indent=4)
            for line in formatted.splitlines():
                print(f"    {line}")
        else:
            print(f"  JSON valid:    NO -- {error}")
            print(f"  Response (raw):")
            for line in clean_text.splitlines():
                print(f"    {line}")
 
        print(f"  Input tokens:  {r['input_tokens']}")
        print(f"  Output tokens: {r['output_tokens']}")
        print(f"  Latency:       {r['latency_ms']} ms")
        print(f"  Cost:          ${r['cost_usd']:.6f}")
 
    print()
    print("=" * width)
 
 
def main():
    if not MODELS:
        print("\nERROR: MODELS dict is empty.")
        print("Complete Step 4 in the lab -- add the three model IDs to the MODELS dict.\n")
        return
 
    print(f"\nConnecting to Amazon Bedrock in {REGION}...")
    client = boto3.client("bedrock-runtime", region_name=REGION)
 
    results = []
    for name, model_id in MODELS.items():
        print(f"Invoking {name}...")
        try:
            result = invoke_model(client, model_id, PROMPT)
            if result is None:
                print(f"  ERROR: invoke_model returned None for {name}.")
                print("  Complete Step 5 -- add the return dict to invoke_model().")
                return
            results.append(result)
        except Exception as e:
            print(f"  ERROR invoking {name}: {type(e).__name__}: {e}")
            return
 
    print_results(results)
    cost_projection(results)
 
 
if __name__ == "__main__":
    main()
