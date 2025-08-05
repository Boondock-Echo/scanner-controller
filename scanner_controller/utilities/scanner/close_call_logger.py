"""Close Call logging utilities."""

import itertools
import logging
import sqlite3
import sys
import time
from typing import Optional

from scanner_controller.config.close_call_bands import CLOSE_CALL_BANDS
from scanner_controller.adapters.uniden.common.constants import SCANNER_UNITS_PER_MHZ

logger = logging.getLogger(__name__)


def _parse_float(value: object) -> Optional[float]:
    """Return a float from ``value`` if possible."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        digits = "".join(ch for ch in str(value) if ch.isdigit() or ch == ".")
        return float(digits) if digits else None
    except Exception:
        return None


def record_close_calls(
    adapter,
    ser,
    band,
    *,
    db_path="close_calls.db",
    lockout=False,
    max_records: Optional[int] = None,
    max_time: Optional[float] = None,
):
    """Monitor Close Call hits within a chosen band and log each hit.

    Parameters
    ----------
    max_records : int, optional
        Stop logging after this many hits have been recorded.
    max_time : float, optional
        Stop logging after this many seconds have elapsed.
    """
    band_key = str(band).lower()
    if band_key not in CLOSE_CALL_BANDS:
        raise KeyError(f"Unknown band: {band}")
    # Preserve current Close Call settings and mode so we can restore them later
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

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS close_calls (timestamp REAL, frequency REAL, tone TEXT, rssi REAL)"
    )
    conn.commit()

    record_count = 0
    total_records = 0
    start_time = time.time()
    locked = set()
    spinner = itertools.cycle("|/-\\")
    try:
        while True:
            if max_records is not None and total_records >= max_records:
                break
            if max_time is not None and time.time() - start_time >= max_time:
                break
            elapsed = time.time() - start_time
            sys.stdout.write(
                f"\r{next(spinner)} Hits: {total_records} Elapsed: {elapsed:0.1f}s"
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

                if (
                    freq is not None
                    and low_limit is not None
                    and high_limit is not None
                    and not (low_limit <= freq <= high_limit)
                ):
                    adapter.send_command(ser, f"LOF,{freq}")
                    locked.add(freq)
                    logger.info("Locked out frequency %s outside range", freq)
                    continue

                ts = time.time()
                cur.execute(
                    "INSERT INTO close_calls VALUES (?, ?, ?, ?)",
                    (ts, freq, tone, rssi),
                )
                record_count += 1
                total_records += 1

                # Commit after every 10 records
                if record_count >= 10:
                    conn.commit()
                    record_count = 0

                if lockout and freq is not None:
                    adapter.send_command(ser, f"LOF,{freq}")
                    locked.add(freq)
            except KeyboardInterrupt:
                break
    finally:
        sys.stdout.write("\n")
        if record_count > 0:
            try:
                conn.commit()
            except Exception:
                pass
        for freq in locked:
            try:
                adapter.send_command(ser, f"ULF,{freq}")
            except Exception:
                pass
        conn.close()
        # Restore previous Close Call settings and resume prior mode
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
