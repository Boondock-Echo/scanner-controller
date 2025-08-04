"""Adapters for software-defined radios (SDR)."""
from .rtlsdr_adapter import RTLSDRAdapter
from .rx888_adapter import RX888Adapter

__all__ = ["RTLSDRAdapter", "RX888Adapter"]
