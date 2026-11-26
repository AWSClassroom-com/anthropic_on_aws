"""
Lab 1: Knowledge Base Query Script
Anthropic Models on AWS Bedrock

Nothing to edit. Open this file in VS Code, read it, then run it.

Queries the Knowledge Base in two steps:
1. retrieve()     -- fetches relevant chunks with real relevance scores
2. invoke_model() -- passes the chunks to Claude to write the answer

Run:  python scripts/query_knowledge_base.py --demo
      python scripts/query_knowledge_base.py --query "Your question here"
"""

import argparse
import json
import sys

import boto3

from kb_common import REGION, get_kb_id

MODEL_ID = "us.anthropic.claude-sonnet-5-5"
MAX_RESULTS = 5

# The questions --demo runs, and what a healthy Knowledge Base returns for them.
DEMO_GROUNDED = "What is the return policy for damaged products?"
DEMO_VAGUE = "How do I return something?"
DEMO_SPECIFIC = (
    "What is the step-by-step process for initiating a product return, "
    "including required documentation and timelines?"
)
DEMO_OUT_OF_SCOPE = "What is the CEO's favorite color?"


def retrieve_chunks(query: str, kb_id: str, client) -> list:
    """
    Step 1: Retrieve relevant chunks from the Knowledge Base.
    Returns chunks with real relevance scores.
    """
    # EXPLORE: a Knowledge Base with its own vector store (OpenSearch Serverless,
    # for example) takes vectorSearchConfiguration. A managed knowledge base takes
    # managedSearchConfiguration instead. Both use the same numberOfResults key,
    # so try the vector form first and fall back to the managed form.
    for config_key in ("vectorSearchConfiguration", "managedSearchConfiguration"):
        try:
            response = client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    config_key: {"numberOfResults": MAX_RESULTS}
                }
            )
            return response.get("retrievalResults", [])
        except client.exceptions.ValidationException as e:
            if config_key == "managedSearchConfiguration" or "only supported" not in str(e):
                raise
    return []


def generate_answer(query: str, chunks: list) -> str:
    """
    Step 2: Pass retrieved chunks to Claude to generate an answer.
    Uses invoke_model with the chunks as context.
    """
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)

    # EXPLORE: the context is built only from the retrieved chunks, and each
    # one is labeled with its source file so the answer can be traced back.
    context = "\n\n".join([
        f"[Source: {chunk.get('location', {}).get('s3Location', {}).get('uri', 'unknown').split('/')[-1]}]\n"
        f"{chunk.get('content', {}).get('text', '')}"
        for chunk in chunks
    ])

    # EXPLORE: "Only use information from the provided sources" is what keeps
    # the answer grounded. Remove it and the model may fill gaps from memory.
    prompt = f"""Use the following source documents to answer the question.
Only use information from the provided sources. If the answer is not in the sources, say so.

Sources:
{context}

Question: {query}

Answer:"""

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    })

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=body
    )

    result = json.loads(response["body"].read())

    # Claude 5.x models think before answering, so content[0] can be a
    # thinking block. Pick the text block by type rather than by position.
    return next(
        b["text"] for b in result["content"] if b.get("type") == "text"
    )


def build_citations(chunks: list) -> list:
    """
    Build deduplicated citation list with real relevance scores.
    Keeps the highest score when the same file appears multiple times.
    """
    seen = {}
    for chunk in chunks:
        uri = chunk.get("location", {}).get("s3Location", {}).get("uri", "unknown")
        filename = uri.split("/")[-1] if "/" in uri else uri
        score = round(chunk.get("score", 0), 2)

        if filename not in seen or score > seen[filename]:
            seen[filename] = score

    return [{"filename": f, "score": s} for f, s in seen.items()]


def query_knowledge_base(query: str, kb_id: str) -> dict:
    """Query the Knowledge Base and return answer with citations."""

    agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)
    chunks = retrieve_chunks(query, kb_id, agent_runtime)

    if not chunks:
        return {
            "query": query,
            "answer": "No relevant documents found for this query.",
            "citations": []
        }

    return {
        "query": query,
        "answer": generate_answer(query, chunks),
        "citations": build_citations(chunks)
    }


def print_result(result: dict, max_answer_chars: int = None) -> None:
    """Print query result in a readable format."""

    answer = result["answer"]
    if max_answer_chars and len(answer) > max_answer_chars:
        answer = answer[:max_answer_chars].rstrip() + " ..."

    print()
    print(f"Query: {result['query']}")
    print()
    print("Answer:")
    print(answer)
    print()

    if result["citations"]:
        print("Citations:")
        for i, ref in enumerate(result["citations"], 1):
            print(f"  [{i}] {ref['filename']} (score: {ref['score']})")
    else:
        print("Citations: none returned")

    print()


def top_score(result: dict) -> float:
    return max((c["score"] for c in result["citations"]), default=0.0)


def top_file(result: dict) -> str:
    cites = result["citations"]
    return max(cites, key=lambda c: c["score"])["filename"] if cites else ""


def run_demo(kb_id: str) -> bool:
    """Run the four lab questions and check what the Knowledge Base returns."""

    print("\nRunning four questions against the Knowledge Base...")
    print("=" * 60)
    print("  1. A question the documents answer")
    print("=" * 60)
    grounded = query_knowledge_base(DEMO_GROUNDED, kb_id)
    print_result(grounded)

    print("=" * 60)
    print("  2. The same question, asked vaguely and then specifically")
    print("=" * 60)
    vague = query_knowledge_base(DEMO_VAGUE, kb_id)
    specific = query_knowledge_base(DEMO_SPECIFIC, kb_id)
    print_result(vague, max_answer_chars=300)
    print_result(specific, max_answer_chars=300)

    print("=" * 60)
    print("  3. A question the documents do not answer")
    print("=" * 60)
    outside = query_knowledge_base(DEMO_OUT_OF_SCOPE, kb_id)
    print_result(outside, max_answer_chars=300)

    gap = round(top_score(specific) - top_score(vague), 2)
    checks = [
        ("Top citation for the damaged-products question is return-policy.txt",
         top_file(grounded) == "return-policy.txt"),
        ("That top score is 0.60 or higher",
         top_score(grounded) >= 0.60),
        ("The answer states the 60-day window found in the source",
         "60" in grounded["answer"]),
        (f"The specific question scores at least 0.20 above the vague one (gap {gap:+.2f})",
         gap >= 0.20),
        ("Every score for the out-of-scope question is 0.40 or lower",
         bool(outside["citations"]) and top_score(outside) <= 0.40),
    ]

    print("=" * 60)
    print("  Self-Check")
    print("=" * 60)
    for label, ok in checks:
        print(f"  {'✅' if ok else '❌'} {label}")
    print()

    passed = sum(ok for _, ok in checks)
    if passed == len(checks):
        print(f"All {len(checks)} checks passed! ✅")
        print()
        return True
    print(f"{passed} / {len(checks)} checks passed. Tell your instructor.")
    print()
    return False


def main():
    parser = argparse.ArgumentParser(description="Query the Lab 1 Knowledge Base")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true",
                       help="Run the four lab questions and check the results")
    group.add_argument("--query", help="Ask your own question")
    args = parser.parse_args()

    kb_id = get_kb_id()

    try:
        if args.demo:
            sys.exit(0 if run_demo(kb_id) else 1)
        print_result(query_knowledge_base(args.query, kb_id))
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  - Run 'python scripts/verify_knowledge_base.py' to confirm KB status")
        print("  - Tell your instructor if the message mentions model access\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
