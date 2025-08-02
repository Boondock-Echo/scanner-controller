"""Band scope logging utilities."""

from __future__ import annotations

import csv
import json
import logging
import sqlite3
import os
from typing import Iterable, Tuple

logger = logging.getLogger(__name__)


def record_band_scope(
    records: Iterable[Tuple[float, float]], summary: str, fmt: str, path: str
):
    """Record band scope data in various formats.

    Parameters
    ----------
    records:
        Iterable of ``(frequency, rssi)`` pairs where ``rssi`` is normalized
        between 0.0 and 1.0.
    summary:
        Summary line describing the sweep.
    fmt:
        One of ``"csv"``, ``"json"``, or ``"db"``.
    path:
        Destination file path.
    """
    fmt = fmt.lower()
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    if fmt == "csv":
        with open(path, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["frequency", "rssi"])
            writer.writerows(records)
            writer.writerow([])
            writer.writerow([summary])
    elif fmt == "json":
        data = {
            "records": [
                {"frequency": freq, "rssi": rssi} for freq, rssi in records
            ],
            "summary": summary,
        }
        with open(path, "w") as fh:
            json.dump(data, fh)
    elif fmt == "db":
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS band_scope (frequency REAL, rssi REAL)"
        )
        cur.executemany("INSERT INTO band_scope VALUES (?, ?)", records)
        cur.execute("CREATE TABLE IF NOT EXISTS metadata (summary TEXT)")
        cur.execute("INSERT INTO metadata VALUES (?)", (summary,))
        conn.commit()
        conn.close()
    else:  # pragma: no cover - defensive programming
        raise ValueError(f"Unsupported format: {fmt}")

    logger.info("Band scope data recorded to %s", path)
    return path


__all__ = ["record_band_scope"]
