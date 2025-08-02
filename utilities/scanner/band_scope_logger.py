"""Utilities for logging band scope sweeps."""

from __future__ import annotations

import csv
import json
import sqlite3
from typing import Sequence, Tuple

Record = Tuple[float, float]


def _write_csv(filename: str, records: Sequence[Record]) -> None:
    """Write ``records`` to ``filename`` in CSV format."""
    with open(filename, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["rssi", "freq"])
        for rssi, freq in records:
            writer.writerow([rssi, freq])


def _write_json(filename: str, records: Sequence[Record]) -> None:
    """Write ``records`` to ``filename`` in JSON format."""
    data = [{"rssi": rssi, "freq": freq} for rssi, freq in records]
    with open(filename, "w", encoding="utf-8") as fh:
        json.dump(data, fh)


def _write_db(filename: str, records: Sequence[Record]) -> None:
    """Persist ``records`` to a SQLite database at ``filename``."""
    conn = sqlite3.connect(filename)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS band_scope (rssi REAL, frequency REAL)"
    )
    cur.executemany("INSERT INTO band_scope VALUES (?, ?)", records)
    conn.commit()
    conn.close()


_FORMATTERS = {
    "csv": (_write_csv, ".csv"),
    "json": (_write_json, ".json"),
    "sqlite": (_write_db, ".db"),
    "db": (_write_db, ".db"),
}


def record_band_scope(
    adapter,
    ser,
    preset: str,
    sweeps: int = 1,
    format: str = "csv",
    path: str = "band_scope",
) -> None:
    """Record band scope sweeps using ``adapter.stream_custom_search``.

    Parameters
    ----------
    adapter : object
        Scanner adapter implementing ``configure_band_scope`` and
        ``stream_custom_search``.
    ser : serial.Serial
        Serial connection to the scanner.
    preset : str
        Band scope preset to configure before streaming.
    sweeps : int, optional
        Number of sweeps to capture. Default is ``1``.
    format : str, optional
        Output format: ``"csv"``, ``"json"``, or ``"sqlite"``.
        Default ``"csv"``.
    path : str, optional
        Base filename for output. Extensions are added automatically.
    """
    if preset and hasattr(adapter, "configure_band_scope"):
        resp = adapter.configure_band_scope(ser, preset)
        if resp and "OK" not in str(resp).upper():
            return

    width = getattr(adapter, "band_scope_width", None) or 1024
    count = width * sweeps

    records = [
        (rssi, freq)
        for rssi, freq, _ in adapter.stream_custom_search(ser, count)
    ]
    if not records:
        return

    fmt_key = format.lower()
    if fmt_key not in _FORMATTERS:
        raise ValueError(f"Unknown format: {format}")
    writer, suffix = _FORMATTERS[fmt_key]
    filename = f"{path}{suffix}"
    writer(filename, records)
