"""Utility to perform a Close Call search and return hits."""

from __future__ import annotations

import select
import sys
import time
from typing import IO, List, Optional, Set, Tuple

from config.close_call_bands import CLOSE_CALL_BANDS


def _parse_float(value: object) -> Optional[float]:
    """Return a float from ``value`` if possible."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        digits = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
        return float(digits) if digits else None
    except Exception:
        return None


def _user_requested_exit(stream: IO[str]) -> bool:
    """Return ``True`` if the user requested cancellation."""
    try:
        if hasattr(stream, "fileno"):
            r, _, _ = select.select([stream], [], [], 0)
            if r:
                ch = stream.read(1)
                return ch in {"q", "Q", "\n", "\r"}
        else:
            ch = stream.read(1)
            return ch in {"q", "Q", "\n", "\r"}
    except Exception:
        return False
    return False


def close_call_search(
    adapter,
    ser,
    band,
    *,
    max_hits: Optional[int] = None,
    max_time: Optional[float] = None,
    input_stream: Optional[IO[str]] = None,
    lockout: bool = False,
) -> Tuple[List[Tuple[float, Optional[float], str, Optional[float]]], bool]:
    """Collect Close Call hits within a band.

    Parameters
    ----------
    max_hits : int, optional
        Stop searching after this many hits have been collected.
    max_time : float, optional
        Stop searching after this many seconds have elapsed.
    input_stream : IO, optional
        Stream to poll for user cancellation; defaults to ``sys.stdin``.

    Returns
    -------
    hits : list of tuples
        Each tuple contains ``(timestamp, frequency, tone, rssi)``.
    completed : bool
        ``True`` if the search completed normally, ``False`` if cancelled.
    """
    band_key = str(band).lower()
    if band_key not in CLOSE_CALL_BANDS:
        raise KeyError(f"Unknown band: {band}")

    mask = CLOSE_CALL_BANDS[band_key]
    adapter.set_close_call(ser, mask)
    adapter.jump_mode(ser, "CC_MODE")

    hits: List[Tuple[float, Optional[float], str, Optional[float]]] = []
    start_time = time.time()
    cancelled = False
    stream = input_stream if input_stream is not None else sys.stdin
    locked: Set[float] = set()

    try:
        while True:
            if max_hits is not None and len(hits) >= max_hits:
                break
            if max_time is not None and time.time() - start_time >= max_time:
                break
            if _user_requested_exit(stream):
                cancelled = True
                break
            try:
                freq_raw = adapter.read_frequency(ser)
                freq = _parse_float(freq_raw)
                tone = ""
                if hasattr(adapter, "read_tone"):
                    tone = adapter.read_tone(ser)
                rssi_raw = adapter.read_rssi(ser)
                rssi = _parse_float(rssi_raw)
                ts = time.time()
                hits.append((ts, freq, tone, rssi))
                if lockout and freq is not None:
                    adapter.send_command(ser, f"LOF,{freq}")
                    locked.add(freq)
            except KeyboardInterrupt:
                cancelled = True
                break
    finally:
        for freq in locked:
            try:
                adapter.send_command(ser, f"ULF,{freq}")
            except Exception:
                pass

    return hits, not cancelled
