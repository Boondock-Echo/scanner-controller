"""Close Call logging utilities."""

import logging
import sqlite3
import time
from typing import Optional

from config.close_call_bands import CLOSE_CALL_BANDS

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

    mask = CLOSE_CALL_BANDS[band_key]
    adapter.set_close_call(ser, mask)
    adapter.jump_mode(ser, "CC_MODE")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS close_calls (timestamp REAL, frequency REAL, tone TEXT, rssi REAL)"
    )
    conn.commit()

    record_count = 0
    total_records = 0
    start_time = time.time()
    try:
        while True:
            if max_records is not None and total_records >= max_records:
                break
            if max_time is not None and time.time() - start_time >= max_time:
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
            except KeyboardInterrupt:
                break
        # Commit any remaining records
        if record_count > 0:
            conn.commit()
    finally:
        conn.close()
