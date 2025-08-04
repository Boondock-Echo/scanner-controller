"""Adapter for RX888 based SDR receivers."""

from __future__ import annotations

from adapters.base_adapter import BaseScannerAdapter

try:  # pragma: no cover - optional dependency
    import SoapySDR  # type: ignore
    from SoapySDR import SOAPY_SDR_RX  # type: ignore
except Exception:  # pragma: no cover
    SoapySDR = None  # type: ignore
    SOAPY_SDR_RX = 0  # type: ignore


class RX888Adapter(BaseScannerAdapter):
    """Adapter implementation for RX888 receivers."""

    def __init__(self, device_args: dict | None = None, machine_mode: bool = False):
        self.machine_mode = machine_mode
        self._volume = 0.0
        self._squelch = 0.0
        self._device = None
        if SoapySDR:  # pragma: no branch
            args = device_args or {"driver": "rx888"}
            try:
                self._device = SoapySDR.Device(args)
            except Exception:  # pragma: no cover
                self._device = None

    # Frequency control
    def read_frequency(self, ser=None):  # pragma: no cover
        if self._device:
            return self._device.getFrequency(SOAPY_SDR_RX, 0)
        return 0.0

    def write_frequency(self, ser, freq):  # pragma: no cover
        if self._device:
            self._device.setFrequency(SOAPY_SDR_RX, 0, freq)
        return freq

    # Volume control via gain
    def read_volume(self, ser=None):
        if self._device:  # pragma: no branch
            try:
                return float(self._device.getGain(SOAPY_SDR_RX, 0))
            except Exception:
                pass
        return float(self._volume)

    def write_volume(self, ser, value):
        self._volume = float(value)
        if self._device:  # pragma: no branch
            try:
                self._device.setGain(SOAPY_SDR_RX, 0, float(value))
            except Exception:
                pass
        return float(value)

    # Squelch placeholders
    def read_squelch(self, ser=None):
        return float(self._squelch)

    def write_squelch(self, ser, value):
        self._squelch = float(value)
        return float(value)
