"""Utility to perform a Close Call search and return hits."""

from __future__ import annotations

import itertools
import select
import sys
import time
from typing import IO, List, Optional, Set, Tuple

from scanner_controller.config.close_call_bands import CLOSE_CALL_BANDS
from scanner_controller.adapters.uniden.common.constants import SCANNER_UNITS_PER_MHZ


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
    """Return ``True`` if the user pressed Enter or ``q`` to cancel."""
    try:
        if sys.platform == "win32":
            import msvcrt  # type: ignore

            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                return ch in {"q", "Q", "\n", "\r"}
        else:
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

    Press ``Enter`` or ``q`` while the search is running to stop early. The
    scanner's previous Close Call and mode settings are restored before
    returning.

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
    # Save current Close Call settings and scanner mode so we can restore them
    # after the search completes.
    current_settings = adapter.get_close_call(ser)
    try:
        current_mode = adapter.jump_mode(ser, "")
    except Exception:  # pragma: no cover - best effort only
        current_mode = None

    mask = CLOSE_CALL_BANDS[band_key]
    adapter.set_close_call(ser, mask)
    adapter.jump_mode(ser, "CC_MODE")

    try:
        from scanner_controller.config.band_scope_presets import BAND_SCOPE_PRESETS

        low_str, high_str, *_ = BAND_SCOPE_PRESETS.get(band_key, (None, None))
        if low_str is not None and high_str is not None:
            low_limit = int(low_str) / SCANNER_UNITS_PER_MHZ
            high_limit = int(high_str) / SCANNER_UNITS_PER_MHZ
        else:
            low_limit = high_limit = None
    except Exception:
        low_limit = high_limit = None

    hits: List[Tuple[float, Optional[float], str, Optional[float]]] = []
    start_time = time.time()
    cancelled = False
    stream = input_stream if input_stream is not None else sys.stdin
    locked: Set[float] = set()
    spinner = itertools.cycle("|/-\\")

    try:
        while True:
            if max_hits is not None and len(hits) >= max_hits:
                break
            if max_time is not None and time.time() - start_time >= max_time:
                break
            if _user_requested_exit(stream):
                cancelled = True
                break
            elapsed = time.time() - start_time
            sys.stdout.write(
                f"\r{next(spinner)} Hits: {len(hits)} Elapsed: {elapsed:0.1f}s"
                " (press Enter or 'q' to stop)"
            )
            sys.stdout.flush()
            try:
                freq_raw = adapter.read_frequency(ser)
                freq = _parse_float(freq_raw)
                tone = ""
                if hasattr(adapter, "read_tone"):
                    tone = adapter.read_tone(ser)
                rssi_raw = adapter.read_rssi(ser)
                rssi = _parse_float(rssi_raw)
                ts = time.time()
                if (
                    freq is not None
                    and low_limit is not None
                    and high_limit is not None
                    and not (low_limit <= freq <= high_limit)
                ):
                    adapter.send_command(ser, f"LOF,{freq}")
                    locked.add(freq)
                    continue
                hits.append((ts, freq, tone, rssi))
                if lockout and freq is not None:
                    adapter.send_command(ser, f"LOF,{freq}")
                    locked.add(freq)
            except KeyboardInterrupt:
                cancelled = True
                break
    finally:
        sys.stdout.write("\n")
        for freq in locked:
            try:
                adapter.send_command(ser, f"ULF,{freq}")
            except Exception:
                pass

        # Restore original Close Call settings and resume prior mode
        try:
            adapter.set_close_call(ser, current_settings)
        except Exception:  # pragma: no cover - best effort only
            pass
        try:
            if current_mode == "SCN_MODE":
                adapter.start_scanning(ser)
            elif current_mode:
                adapter.jump_mode(ser, current_mode)
            else:
                adapter.start_scanning(ser)
        except Exception:  # pragma: no cover - best effort only
            try:
                adapter.start_scanning(ser)
            except Exception:
                pass

    return hits, not cancelled
