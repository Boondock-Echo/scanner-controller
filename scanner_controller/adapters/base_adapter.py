"""
Base Adapter module.

This module provides functionality related to base adapter.
"""

# Third-party imports
from abc import ABC, abstractmethod


class BaseScannerAdapter(ABC):
    """Base class for all scanner adapters.

    This class defines the interface that all scanner adapters must implement.
    All method names use snake_case to follow Python conventions.
    """

    @abstractmethod
    def __init__(self):
        """Initialize the scanner adapter."""
        pass

    # Core volume and squelch methods - abstract to force implementation
    @abstractmethod
    def read_volume(self, ser):
        """Read the volume level (0-29 or normalized 0.0-1.0)."""
        pass

    @abstractmethod
    def write_volume(self, ser, value):
        """Set the volume level (0-29 or normalized 0.0-1.0)."""
        pass

    @abstractmethod
    def read_squelch(self, ser):
        """Read the squelch level (0-29 or normalized 0.0-1.0)."""
        pass

    @abstractmethod
    def write_squelch(self, ser, value):
        """Set the squelch level (0-29 or normalized 0.0-1.0)."""
        pass

    # Additional methods may be optional or have default implementations
    def get_help(self, command):
        """Get help for a specific command."""
        return f"No help available for {command}"

    def read_model(self, ser):
        """Read the scanner model."""
        return "Generic Scanner"

    def read_sw_ver(self, ser):
        """Read the scanner firmware version."""
        return "Unknown Version"

    def read_rssi(self, ser):
        """Read the current signal strength."""
        return "RSSI not supported"

    def read_s_meter(self, ser):
        """Read the S-meter value."""
        return "S-meter not supported"

    def read_frequency(self, ser):
        """Read the current frequency."""
        return "Frequency reading not supported"

    def write_frequency(self, ser, freq):
        """Set the frequency."""
        return "Frequency writing not supported"

    def read_battery_voltage(self, ser):
        """Read the battery voltage."""
        return "Battery voltage reading not supported"

    def read_window_voltage(self, ser):
        """Read the window voltage."""
        return "Window voltage reading not supported"

    def read_status(self, ser):
        """Read the scanner status."""
        return "Status reading not supported"

    def send_key(self, ser, key_seq):
        """Simulate key presses on the scanner."""
        return "Key simulation not supported"

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        """Enter frequency hold mode."""
        return "Frequency hold not supported"

    def dump_memory_to_file(
        self,
        ser,
        filename="memorydump.txt",
        start=0x00000000,
        end=0x0000FFFF,
        step=16,
    ):
        """Dump scanner memory to a file."""
        return "Memory dump not supported"

    def read_global_lockout(self, ser):
        """Read global lockout list."""
        return "Global lockout reading not supported"

    def read_channel_info(self, ser, index):
        """Read channel information."""
        return "Channel info reading not supported"

    def write_channel_info(
        self, ser, index, name, freq_khz, mod, ctcss, delay, lockout, priority
    ):
        """Write channel information."""
        return "Channel info writing not supported"

    def enter_programming_mode(self, ser):
        """Enter programming mode."""
        return "Programming mode not supported"

    def exit_programming_mode(self, ser):
        """Exit programming mode."""
        return "Programming mode not supported"
