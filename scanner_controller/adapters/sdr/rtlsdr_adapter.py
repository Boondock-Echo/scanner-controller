"""Adapter for RTL-SDR devices.

This adapter provides a thin wrapper around cross-platform SDR libraries
(SoapySDR or pyrtlsdr) exposing the small subset of functionality that the
scanner controller expects.  The implementation is intentionally light weight
so it can operate without the hardware present; methods fall back to cached
values when the device is unavailable.
"""

from __future__ import annotations

from scanner_controller.adapters.base_adapter import BaseScannerAdapter

RtlSdr = None  # type: ignore
try:  # pragma: no cover - optional dependency
    import SoapySDR  # type: ignore
    from SoapySDR import SOAPY_SDR_RX  # type: ignore
except Exception:  # pragma: no cover
    SoapySDR = None  # type: ignore
    SOAPY_SDR_RX = 0  # type: ignore
    try:  # pragma: no cover - optional dependency
        from pyrtlsdr import RtlSdr  # type: ignore
    except Exception:  # pragma: no cover
        RtlSdr = None  # type: ignore


class RTLSDRAdapter(BaseScannerAdapter):
    """Adapter implementation for RTL-SDR receivers."""

    def __init__(self, device_args: dict | None = None, machine_mode: bool = False):
        self.machine_mode = machine_mode
        self._volume = 0.0
        self._squelch = 0.0
        self._device = None
        if SoapySDR:  # pragma: no branch - executed when library available
            args = device_args or {"driver": "rtlsdr"}
            try:
                self._device = SoapySDR.Device(args)
            except Exception:  # pragma: no cover - runtime error if device missing
                self._device = None
        elif RtlSdr:  # pragma: no branch - executed when library available
            try:
                self._device = RtlSdr(**(device_args or {}))
            except Exception:  # pragma: no cover - runtime error if device missing
                self._device = None

    # ------------------------------------------------------------------
    # Frequency control
    def read_frequency(self, ser=None):  # pragma: no cover - hardware access
        if self._device:
            if SoapySDR:
                return self._device.getFrequency(SOAPY_SDR_RX, 0)
            try:
                return float(self._device.center_freq)
            except Exception:
                pass
        return 0.0

    def write_frequency(self, ser, freq):  # pragma: no cover - hardware access
        if self._device:
            if SoapySDR:
                self._device.setFrequency(SOAPY_SDR_RX, 0, freq)
            else:
                try:
                    self._device.center_freq = float(freq)
                except Exception:
                    pass
        return freq

    # ------------------------------------------------------------------
    # Volume control - mapped to overall RF gain
    def read_volume(self, ser=None):
        if self._device:  # pragma: no branch - hardware access
            try:
                if SoapySDR:
                    return float(self._device.getGain(SOAPY_SDR_RX, 0))
                return float(self._device.gain)
            except Exception:
                pass
        return float(self._volume)

    def write_volume(self, ser, value):
        self._volume = float(value)
        if self._device:  # pragma: no branch - hardware access
            try:
                if SoapySDR:
                    self._device.setGain(SOAPY_SDR_RX, 0, float(value))
                else:
                    self._device.gain = float(value)
            except Exception:
                pass
        return float(value)

    # ------------------------------------------------------------------
    # Squelch is not typically provided by SDR libraries.  We simply cache
    # the value so higher layers have somewhere to store it.
    def read_squelch(self, ser=None):
        return float(self._squelch)

    def write_squelch(self, ser, value):
        self._squelch = float(value)
        return float(value)
