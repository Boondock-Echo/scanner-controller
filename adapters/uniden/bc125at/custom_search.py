"""Custom search streaming for the BC125AT scanner."""

import logging

logger = logging.getLogger(__name__)


def stream_custom_search(self, ser, record_count=1024, debug=False):
    """Stream custom search data across the last configured band.

    Parameters
    ----------
    ser : serial.Serial
        Serial connection to the scanner.
    record_count : int, optional
        Maximum number of records to yield. Defaults to ``1024``.
    debug : bool, optional
        If ``True`` each result is logged at the debug level.

    Yields
    ------
    tuple
        ``(rssi, freq_mhz, 0)`` tuples for each frequency in the sweep.
    """
    center = getattr(self, "last_center", None)
    span = getattr(self, "last_span", None)
    step = getattr(self, "last_step", None)

    if None in (center, span, step):
        return

    start = center - span / 2.0
    end = center + span / 2.0
    freq = start
    count = 0

    while freq <= end + 1e-6 and count < record_count:
        try:
            self.enter_quick_frequency_hold(ser, freq)
            rssi = self.read_rssi(ser)
            rssi_scaled = int(rssi * 1023) if rssi is not None else 0
            if debug:
                logger.debug("freq=%s rssi=%s", freq, rssi_scaled)
            yield (rssi_scaled, freq, 0)
        except Exception as e:  # pragma: no cover - log and stop
            logger.error("Error during custom search: %s", e)
            break
        freq += step
        count += 1
