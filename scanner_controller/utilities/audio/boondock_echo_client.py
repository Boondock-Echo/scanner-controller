"""Client for the Boondock Echo audio service."""

from __future__ import annotations

import time
import urllib.request
from typing import Optional

from scanner_controller.config import boondock_echo as config

try:  # pragma: no cover - optional dependency for websocket usage
    import websocket
except Exception:  # pragma: no cover - allow import failures if unused
    websocket = None


class BoondockEchoClient:
    """Client for posting audio frames to the Boondock Echo service."""

    def __init__(self, api_url: Optional[str] = None, auth_token: Optional[str] = None) -> None:
        self.api_url = api_url or config.API_URL
        self.auth_token = auth_token or config.AUTH_TOKEN

    def post_audio(self, pcm: bytes, retries: int = 3, use_websocket: bool = False):
        """Post raw PCM audio to the Boondock Echo service.

        Args:
            pcm: Raw PCM byte data to send.
            retries: Number of attempts before giving up.
            use_websocket: If ``True`` use a WebSocket connection instead of HTTP.

        Returns:
            The response payload from the service.

        Raises:
            Exception: Propagates any exception from the underlying transport after all retries have been exhausted.
        """

        last_exc: Optional[Exception] = None
        for attempt in range(1, retries + 1):
            try:
                if use_websocket:
                    return self._post_websocket(pcm)
                return self._post_http(pcm)
            except Exception as exc:  # pragma: no cover - error path
                last_exc = exc
                if attempt == retries:
                    break
                time.sleep(attempt)  # simple incremental backoff
        if last_exc:
            raise last_exc

    def _post_http(self, pcm: bytes):
        """Send audio via HTTP POST using ``urllib.request``."""

        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/octet-stream",
        }
        request = urllib.request.Request(
            self.api_url,
            data=pcm,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            return response.read()

    def _post_websocket(self, pcm: bytes):  # pragma: no cover - requires websocket server
        """Send audio via WebSocket using ``websocket-client``."""

        if websocket is None:
            raise RuntimeError("websocket-client library is required for WebSocket support")

        ws = websocket.create_connection(
            self.api_url,
            header=[f"Authorization: Bearer {self.auth_token}"],
        )
        try:
            ws.send(pcm, opcode=websocket.ABNF.OPCODE_BINARY)
            return ws.recv()
        finally:
            ws.close()
