import os
import sys
import time
import urllib.error
import urllib.request

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.audio.boondock_echo_client import BoondockEchoClient


class DummyResponse:
    def __init__(self, payload: bytes = b"ok"):
        self.payload = payload

    def read(self):
        return self.payload

    def __enter__(self):  # pragma: no cover - trivial
        return self

    def __exit__(self, exc_type, exc, tb):  # pragma: no cover - trivial
        return False


def test_post_audio_success(monkeypatch):
    captured = {}

    def fake_urlopen(request):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.headers)
        captured["data"] = request.data
        return DummyResponse(b"resp")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)

    client = BoondockEchoClient(api_url="http://example.com", auth_token="secret")
    pcm = b"audio-bytes"
    result = client.post_audio(pcm)

    assert result == b"resp"
    assert captured["url"] == "http://example.com"
    assert captured["headers"]["Authorization"] == "Bearer secret"
    # urllib normalizes header names to Title-Case
    assert captured["headers"]["Content-type"] == "application/octet-stream"
    assert captured["data"] == pcm


def test_post_audio_retries(monkeypatch):
    attempts = {"count": 0}

    def fake_urlopen(request):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise urllib.error.URLError("fail")
        return DummyResponse(b"ok")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(time, "sleep", lambda s: None)

    client = BoondockEchoClient(api_url="http://example.com", auth_token="token")
    result = client.post_audio(b"sound", retries=5)

    assert result == b"ok"
    assert attempts["count"] == 3
