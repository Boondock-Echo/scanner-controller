"""Configuration for the Boondock Echo service."""

from __future__ import annotations

import os

# Default API endpoint for the Boondock Echo service. Override with the
# ``BOONDOCK_ECHO_API_URL`` environment variable.
DEFAULT_API_URL = "http://localhost:8000/audio"
API_URL = os.getenv("BOONDOCK_ECHO_API_URL", DEFAULT_API_URL)

# Authorization token used when communicating with the service. Override with
# the ``BOONDOCK_ECHO_AUTH_TOKEN`` environment variable.
AUTH_TOKEN = os.getenv("BOONDOCK_ECHO_AUTH_TOKEN", "")

__all__ = ["API_URL", "AUTH_TOKEN", "DEFAULT_API_URL"]
