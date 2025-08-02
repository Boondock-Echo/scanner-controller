"""Band scope logging utilities."""

from __future__ import annotations

import csv
import json
import logging
import sqlite3
from typing import Iterable, Tuple

logger = logging.getLogger(__name__)

#: Column/key name used to store the frequency value across all formats.
FREQ_FIELD = "frequency"


def _write_csv(
    records: Iterable[Tuple[float, float]], summary: str, path: str
) -> str:
    """Write band scope data to ``path`` in CSV format."""
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow([FREQ_FIELD, "rssi"])
        writer.writerows(records)
        writer.writerow([])
        writer.writerow([summary])
    return path


def _write_json(
    records: Iterable[Tuple[float, float]], summary: str, path: str
) -> str:
    """Write band scope data to ``path`` in JSON format."""
    data = {
        "records": [{FREQ_FIELD: freq, "rssi": rssi} for freq, rssi in records],
        "summary": summary,
    }
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path


def _write_db(
    records: Iterable[Tuple[float, float]], summary: str, path: str
) -> str:
    """Write band scope data to ``path`` in SQLite format."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS band_scope ({FREQ_FIELD} REAL, rssi REAL)"
    )
    cur.executemany("INSERT INTO band_scope VALUES (?, ?)", records)
    cur.execute("CREATE TABLE IF NOT EXISTS metadata (summary TEXT)")
    cur.execute("INSERT INTO metadata VALUES (?)", (summary,))
    conn.commit()
    conn.close()
    return path


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
    if fmt == "csv":
        result = _write_csv(records, summary, path)
    elif fmt == "json":
        result = _write_json(records, summary, path)
    elif fmt == "db":
        result = _write_db(records, summary, path)
    else:  # pragma: no cover - defensive programming
        raise ValueError(f"Unsupported format: {fmt}")

    logger.info("Band scope data recorded to %s", path)
    return result


__all__ = ["record_band_scope", "FREQ_FIELD"]
