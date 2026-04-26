"""
monitoring.py
Publishes custom CloudWatch metrics for the Lab 3 application.
"""
import logging
import time
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from src.config import AWS_REGION

logger = logging.getLogger(__name__)

NAMESPACE = 'Lab3/CustomerSupport'


class MonitoringService:
    """Publishes operational metrics to Amazon CloudWatch."""

    def __init__(self) -> None:
        self.client = boto3.client('cloudwatch', region_name=AWS_REGION)

    def record_request(
        self,
        was_blocked: bool = False,
        tool_count: int = 0,
        latency_ms: Optional[float] = None
    ) -> None:
        """
        Record metrics for a single chat request.

        Args:
            was_blocked:  True if the guardrail blocked this request.
            tool_count:   Number of tool calls made during the request.
            latency_ms:   End-to-end latency in milliseconds.
        """
        metric_data = [
            {
                'MetricName': 'RequestCount',
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'BlockedRequestCount',
                'Value': 1 if was_blocked else 0,
                'Unit': 'Count'
            },
            {
                'MetricName': 'ToolCallCount',
                'Value': tool_count,
                'Unit': 'Count'
            }
        ]

        if latency_ms is not None:
            metric_data.append({
                'MetricName': 'RequestLatency',
                'Value': latency_ms,
                'Unit': 'Milliseconds'
            })

        try:
            self.client.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=metric_data
            )
        except ClientError as e:
            # Never let monitoring failures affect the user experience
            logger.warning('Failed to publish CloudWatch metrics: %s', e)


class Timer:
    """Simple context manager for measuring latency."""

    def __init__(self) -> None:
        self._start: float = 0.0
        self.elapsed_ms: float = 0.0

    def __enter__(self) -> 'Timer':
        self._start = time.time()
        return self

    def __exit__(self, *args) -> None:
        self.elapsed_ms = (time.time() - self._start) * 1000
