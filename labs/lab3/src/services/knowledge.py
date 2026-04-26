"""
knowledge.py
Retrieval-Augmented Generation (RAG) via Amazon Bedrock Knowledge Bases.
Connects to the Knowledge Base created in Lab 1.
"""
import logging
from typing import Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

from src.config import AWS_REGION, KNOWLEDGE_BASE_ID, MODEL_ID

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Handles document retrieval from Bedrock Knowledge Bases."""

    def __init__(self) -> None:
        self.client = boto3.client('bedrock-agent-runtime', region_name=AWS_REGION)
        self.knowledge_base_id = KNOWLEDGE_BASE_ID
        self.model_arn = f'arn:aws:bedrock:{AWS_REGION}::foundation-model/{MODEL_ID}'

    def retrieve_and_generate(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Query the Knowledge Base and return an answer with source citations.

        Args:
            query:      The customer question to answer from documentation.
            session_id: Optional session ID for multi-turn conversations.

        Returns:
            Dict with 'answer' (str) and 'citations' (list of source references).
        """
        try:
            params: Dict = {
                'input': {'text': query},
                'retrieveAndGenerateConfiguration': {
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': self.knowledge_base_id,
                        'modelArn': self.model_arn
                    }
                }
            }

            if session_id:
                params['sessionId'] = session_id

            response = self.client.retrieve_and_generate(**params)

            answer = response.get('output', {}).get('text', '')
            citations = self._extract_citations(response)

            return {
                'answer': answer,
                'citations': citations,
                'session_id': response.get('sessionId', '')
            }

        except ClientError as e:
            logger.error('Knowledge Base retrieval failed: %s', e)
            return {
                'answer': 'I was unable to retrieve information from our documentation at this time.',
                'citations': [],
                'error': str(e)
            }

    def retrieve(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Retrieve relevant document chunks without generating an answer.
        Useful for feeding context into a custom prompt.

        Args:
            query:       The search query.
            max_results: Maximum number of document chunks to return.

        Returns:
            List of retrieved chunks with text and source location.
        """
        try:
            response = self.client.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            )

            return [
                {
                    'text': r.get('content', {}).get('text', ''),
                    'score': r.get('score', 0),
                    'source': r.get('location', {}).get('s3Location', {}).get('uri', 'unknown')
                }
                for r in response.get('retrievalResults', [])
            ]

        except ClientError as e:
            logger.error('Knowledge Base retrieval failed: %s', e)
            return []

    def _extract_citations(self, response: Dict) -> List[Dict]:
        """Extract source citations from a retrieve_and_generate response."""
        citations = []
        for citation in response.get('citations', []):
            for ref in citation.get('retrievedReferences', []):
                uri = ref.get('location', {}).get('s3Location', {}).get('uri', '')
                text_snippet = ref.get('content', {}).get('text', '')[:200]
                if uri:
                    citations.append({
                        'source': uri,
                        'snippet': text_snippet
                    })
        return citations
