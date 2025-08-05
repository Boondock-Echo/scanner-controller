"""Boondock Echo service configuration."""

import os


API_URL = os.getenv("BOONDOCK_API_URL", "http://localhost:8000/audio")
AUTH_TOKEN = os.getenv("BOONDOCK_AUTH_TOKEN", "")


__all__ = ["API_URL", "AUTH_TOKEN"]

