"""
Lab 1: Knowledge Base Query Script
Anthropic Models on AWS Bedrock
 
Queries the Knowledge Base using a two-step approach:
1. retrieve() -- fetches relevant chunks with real relevance scores
2. invoke_model() -- passes chunks to Claude to generate the answer
 
Displays the answer and deduplicated citations with accurate scores.
Reads the Knowledge Base ID from .env
 
Run: python scripts/query_knowledge_base.py --query "Your question here"
"""
 
import argparse
import boto3
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
 
REGION = "us-east-1"
MODEL_ID = "us.anthropic.claude-sonnet-4-6"
ENV_FILE = Path(__file__).parent.parent / ".env"
MAX_RESULTS = 5
 
 
def get_kb_id() -> str:
    """Read Knowledge Base ID from .env file."""
    load_dotenv(ENV_FILE)
    kb_id = os.getenv("KNOWLEDGE_BASE_ID", "").strip()
    if not kb_id:
        print("\nERROR: KNOWLEDGE_BASE_ID not found in .env")
        print("Add your Knowledge Base ID to .env -- check the course chat for the ID your instructor shared.\n")
        sys.exit(1)
    return kb_id
 
 
def retrieve_chunks(query: str, kb_id: str, client) -> list:
    """
    Step 1: Retrieve relevant chunks from the Knowledge Base.
    Returns chunks with real relevance scores.
    """
    response = client.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": MAX_RESULTS
            }
        }
    )
    return response.get("retrievalResults", [])
 
 
def generate_answer(query: str, chunks: list, account_id: str) -> str:
    """
    Step 2: Pass retrieved chunks to Claude to generate an answer.
    Uses invoke_model with the chunks as context.
    """
    bedrock = boto3.client("bedrock-runtime", region_name=REGION)
 
    # Build context from retrieved chunks
    context = "\n\n".join([
        f"[Source: {chunk.get('location', {}).get('s3Location', {}).get('uri', 'unknown').split('/')[-1]}]\n"
        f"{chunk.get('content', {}).get('text', '')}"
        for chunk in chunks
    ])
 
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
        modelId=f"us.anthropic.claude-sonnet-4-6",
        contentType="application/json",
        accept="application/json",
        body=body
    )
 
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
 
 
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
 
        # Keep highest score for each unique file
        if filename not in seen or score > seen[filename]:
            seen[filename] = score
 
    return [{"filename": f, "score": s} for f, s in seen.items()]
 
 
def query_knowledge_base(query: str, kb_id: str) -> dict:
    """Query the Knowledge Base and return answer with citations."""
 
    sts = boto3.client("sts", region_name=REGION)
    account_id = sts.get_caller_identity()["Account"]
 
    agent_runtime = boto3.client("bedrock-agent-runtime", region_name=REGION)
 
    chunks = retrieve_chunks(query, kb_id, agent_runtime)
 
    if not chunks:
        return {
            "query": query,
            "answer": "No relevant documents found for this query.",
            "citations": []
        }
 
    answer = generate_answer(query, chunks, account_id)
    citations = build_citations(chunks)
 
    return {
        "query": query,
        "answer": answer,
        "citations": citations
    }
 
 
def print_result(result: dict) -> None:
    """Print query result in a readable format."""
 
    print()
    print(f"Query: {result['query']}")
    print()
    print("Answer:")
    print(result["answer"])
    print()
 
    if result["citations"]:
        print("Citations:")
        for i, ref in enumerate(result["citations"], 1):
            print(f"  [{i}] {ref['filename']} (score: {ref['score']})")
    else:
        print("Citations: none returned")
 
    print()
 
 
def main():
    parser = argparse.ArgumentParser(
        description="Query the Lab 1 Knowledge Base"
    )
    parser.add_argument(
        "--query",
        required=True,
        help="The question to ask the Knowledge Base"
    )
    args = parser.parse_args()
 
    kb_id = get_kb_id()
 
    try:
        result = query_knowledge_base(args.query, kb_id)
        print_result(result)
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        print("\nTroubleshooting:")
        print("  - Run 'python scripts/verify_knowledge_base.py' to confirm KB status")
        print("  - Confirm model access is enabled in Bedrock Model Access")
        print("  - Check that documents have finished syncing\n")
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()