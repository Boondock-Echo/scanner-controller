"""Simple command abstractions for generic SDR devices.

These commands mirror the traditional command interfaces used by hardware
scanners, allowing the rest of the application to interact with SDR based
receivers using the same patterns.  They are intentionally minimal – the
actual I/O is performed by the adapter using libraries such as SoapySDR or
pyrtlsdr, but these command objects provide a consistent API surface so that
high level utilities can remain largely unchanged.
"""

from scanner_controller.command_libraries.base_command import BaseCommand

# In the SDR context the commands do not correspond to serial strings.
# They simply serve as placeholders to keep the command/adapter architecture
# consistent with the rest of the project.

READ_FREQUENCY = BaseCommand("READ_FREQUENCY")
WRITE_FREQUENCY = BaseCommand("WRITE_FREQUENCY")
READ_VOLUME = BaseCommand("READ_VOLUME")
WRITE_VOLUME = BaseCommand("WRITE_VOLUME")
