__version__ = "0.1.0"

from .auth import ThousandEyesAuth

class ThousandEyes:
    """
    A wrapper class for the ThousandEyes API.
    """

    def __init__(self, api_token: str = None):
        """
        Initializes the ThousandEyes wrapper.

        Args:
            api_token: The ThousandEyes API token. If not provided, it attempts
                       to read from the TE_API_TOKEN environment variable.
        """
        self.auth = ThousandEyesAuth(api_token=api_token)


__all__ = [
    "ThousandEyes",
    "__version__",
]
