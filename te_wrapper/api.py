"""API client for interacting with the ThousandEyes API."""

from typing import Any, Dict

import requests

from .auth import ThousandEyesAuth

class ThousandEyesAPI:
    """
    A client for making requests to the ThousandEyes API.
    """

    BASE_URL = "https://api.thousandeyes.com/v7"

    def __init__(self, auth: ThousandEyesAuth):
        """
        Initializes the API client with an authentication object.

        Args:
            auth: An instance of ThousandEyesAuth for handling authentication.
        """
        self._auth = auth

    def _request(
        self, method: str, endpoint: str, params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Makes a request to the ThousandEyes API.

        Args:
            method: The HTTP method (e.g., "GET", "POST").
            endpoint: The API endpoint (e.g., "tests"). Can be a full URL.
            params: Optional dictionary of query parameters.

        Returns:
            A dictionary containing the JSON response data.

        Raises:
            RuntimeError: If JSON parsing fails.
            requests.exceptions.RequestException: For other request errors.
        """
        url = endpoint if endpoint.startswith("http") else f"{self.BASE_URL}/{endpoint}"
        if method.upper() == "POST":
            resp = requests.request(
                method, url, headers=self._auth.get_headers(), json=params, params=None
            )
        else:
            resp = requests.request(
                method, url, headers=self._auth.get_headers(), params=params
            )
        try:
            data = resp.json()
        except ValueError:
            raise RuntimeError(
                f"Error parsing JSON (status {resp.status_code}): {resp.text!r}"
            )

        if resp.status_code == 400:
            raise requests.exceptions.RequestException(
                f"Rate limit exceeded (status {resp.status_code}): {resp.text!r}"
            )

        resp.raise_for_status()
        return data

    def list_tests(self) -> Dict[int, Dict[str, Any]]:
        """
        Lists all available tests.

        Returns:
            A dictionary where keys are test IDs and values are dictionaries
            containing test name and results links.
        """
        data = self._request("GET", "tests")
        return {
            int(item["testId"]): {
                "testName": item["testName"],
                "testResultsLinks": item.get("_links", {}).get("testResults", []),
            }
            for item in data.get("tests", [])
        }

    def test_exists(self, name: str = None, test_id: int = None) -> bool:
        """
        Checks if a test with the given name or ID exists.

        Args:
            name: The name of the test to check for.
            test_id: The ID of the test to check for.

        Returns:
            True if the test exists, False otherwise.

        Raises:
            ValueError: If neither name nor test_id is provided.
        """
        if name is None and test_id is None:
            raise ValueError("Either name or test_id must be provided.")

        existing_tests = self.list_tests()

        if test_id is not None:
            if test_id in existing_tests:
                return True

        if name is not None:
            for test_info in existing_tests.values():
                if test_info["testName"] == name:
                    return True

        return False

    def create_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a new ThousandEyes test.

        Args:
            test_config: A dictionary containing the configuration for the new test.
                         Refer to the ThousandEyes API documentation for the required structure.

        Returns:
            A dictionary containing the details of the newly created test.
        """
        return self._request("POST", "tests/http-server", params=test_config)

    def get_first_agent_id(self) -> int:
        """
        Fetches the ID of the first available agent in the account.

        Returns:
            The ID of the first agent.

        Raises:
            RuntimeError: If no agents are found or the API request fails.
        """
        try:
            data = self._request("GET", "agents")
            agents = data.get("agents", [])
            if agents:
                agent = agents[0]
                print(
                    f"Using agent: {agent.get('agentName')} (ID: {agent.get('agentId')})"
                )
                return int(agent.get("agentId"))
            else:
                raise RuntimeError("No agents found in your account.")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch agents: {e}")
