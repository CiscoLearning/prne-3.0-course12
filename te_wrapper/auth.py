"""Authentication handling for the ThousandEyes API."""

import os
from typing import Dict

class ThousandEyesAuth:
    """Handles authentication for ThousandEyes API requests."""

    def __init__(self, api_token: str = None):
        """
        Initializes the authentication object.

        Args:
            api_token: The ThousandEyes API token. If not provided, it attempts
                       to read from the TE_API_TOKEN environment variable.
        Raises:
            ValueError: If no API token is provided and the environment variable
                        is not set.
        """
        self.api_token = api_token or os.getenv("TE_API_TOKEN")
        if not self.api_token:
            raise ValueError(
                "OAuth2 bearer token must be provided via api_token or TE_API_TOKEN environment variable"
            )

    def get_headers(self) -> Dict[str, str]:
        """
        Returns the necessary headers for API requests, including authorization.

        Returns:
            A dictionary containing the request headers.
        """
        return {
            "Content-Type": "application/hal+json",
            "Authorization": f"Bearer {self.api_token}",
        }
