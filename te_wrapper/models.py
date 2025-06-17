"""Data models for ThousandEyes API responses."""

from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class TestResult:
    """
    Represents the result of a ThousandEyes test.
    """

    test_id: int
    test_name: str
    status: Optional[str] = None
    timestamp: Optional[str] = None
    metrics: Dict[str, Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestResult":
        """
        Creates a TestResult object from a dictionary (API response).

        Args:
            data: A dictionary containing the test result data from the API.

        Returns:
            A TestResult object.

        Raises:
            TypeError: If `data` isn't a dict.
            ValueError: If no results are found at all, or required test fields are missing.
        """
        if not isinstance(data, dict):
            raise TypeError(f"Expected dict, got {type(data).__name__!r}")

        results = data.get("results") or data.get("testResults") or []
        if not isinstance(results, list) or not results:
            raise ValueError("API response contains no test results")

        latest = results[0]
        if not isinstance(latest, dict):
            raise ValueError("Latest result entry is malformed")

        test_info = data.get("test")
        if not isinstance(test_info, dict):
            raise ValueError("Missing or invalid 'test' section")

        raw_id = test_info.get("testId")
        if raw_id is None:
            raise ValueError("Missing 'testId' in test metadata")
        try:
            test_id = int(raw_id)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid 'testId': {raw_id!r}")

        test_name = test_info.get("testName")
        if not test_name:
            raise ValueError("Missing 'testName' in test metadata")

        status = latest.get("status")
        timestamp = latest.get("date")

        metrics = {}
        for key in ("avgLatency", "jitter", "loss"):
            if key in latest:
                metrics[key] = latest[key]

        return cls(
            test_id=test_id,
            test_name=test_name,
            status=status,
            timestamp=timestamp,
            metrics=metrics,
        )

    def __str__(self):
        return (
            f"TestResult(test_id={self.test_id}, "
            f"name={self.test_name!r}, "
            f"status={self.status!r}, "
            f"at={self.timestamp!r}, "
            f"metrics={self.metrics})"
        )
