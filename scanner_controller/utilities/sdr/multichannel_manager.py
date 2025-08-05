"""Manage multiple virtual channels on an SDR device."""

from __future__ import annotations

from typing import List, Sequence

from scanner_controller.utilities.core.command_registry import build_command_table
from scanner_controller.utilities.scanner.connection_manager import ConnectionManager


class MultiChannelManager:
    """Monitor multiple frequencies using a single SDR adapter.

    Additional channels either share the provided adapter through digital
    down-conversion or spawn new adapter instances when that capability is
    unavailable.  Each channel is registered with the :class:`ConnectionManager`
    as a distinct logical connection.
    """

    def __init__(self, adapter):
        self.adapter = adapter

    def monitor_frequencies(
        self, frequencies: Sequence[float], connection_manager: ConnectionManager
    ) -> List[int]:
        """Tune one or more frequencies and register them as connections."""

        conn_ids: List[int] = []
        base = self.adapter
        for idx, freq in enumerate(frequencies):
            if idx == 0 or getattr(base, "supports_ddc", False):
                adapter = base
                hardware = base
            else:
                # Spawn a new device instance for this channel
                adapter = type(base)(machine_mode=getattr(base, "machine_mode", False))
                hardware = adapter
            adapter.write_frequency(None, freq)
            commands, help_text = build_command_table(adapter, None)
            conn_id = connection_manager.register_virtual_connection(
                ser=None,
                adapter=adapter,
                commands=commands,
                help_text=help_text,
                hardware=hardware,
            )
            conn_ids.append(conn_id)
        return conn_ids


def monitor_frequencies(
    frequencies: Sequence[float],
    adapter=None,
    connection_manager: ConnectionManager | None = None,
) -> List[int]:
    """High level helper used by CLI/GUI components.

    Parameters
    ----------
    frequencies:
        Frequencies to monitor (Hz).
    adapter:
        Optional SDR adapter instance.  When omitted an RTL-SDR adapter is
        created.
    connection_manager:
        :class:`ConnectionManager` instance used to track the channels.  A new
        instance is created if one is not supplied.
    """

    if adapter is None:
        from scanner_controller.adapters.sdr.rtlsdr_adapter import RTLSDRAdapter

        adapter = RTLSDRAdapter()
    cm = connection_manager or ConnectionManager()
    manager = MultiChannelManager(adapter)
    return manager.monitor_frequencies(frequencies, cm)
