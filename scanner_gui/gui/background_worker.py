"""Thread for background polling of the scanner status."""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import QThread, pyqtSignal


class BackgroundWorker(QThread):
    """Worker thread to poll scanner status without blocking the GUI."""

    status_received = pyqtSignal(str)
    rssi_received = pyqtSignal(float)

    def __init__(
        self, controller, interval: int = 250, parent: Optional[object] = None
    ):
        super().__init__(parent)
        self._controller = controller
        self._interval = interval
        self._running = False
        self._log = logging.getLogger(__name__)

    def run(self) -> None:
        self._running = True
        while self._running:
            if self._controller.adapter:
                try:
                    raw = self._controller.read_status()
                    self.status_received.emit(raw)
                    rssi = self._controller.read_rssi()
                    self.rssi_received.emit(rssi)
                except Exception as exc:  # pragma: no cover - log only
                    self._log.error("Worker error: %s", exc)
            self.msleep(self._interval)

    def stop(self) -> None:
        self._running = False
