"""Generic adapter for Uniden scanners."""

from scanner_controller.adapters.uniden.uniden_base_adapter import UnidenScannerAdapter
from scanner_controller.command_libraries.uniden.generic_commands import commands


class GenericUnidenAdapter(UnidenScannerAdapter):
    """A minimal adapter for Uniden scanners."""

    def __init__(self, machine_mode: bool = False):
        super().__init__(machine_mode, commands)
        self.machine_mode_id = "UNIDEN"

    def __str__(self) -> str:
        mode = "machine" if self.machine_mode else "human"
        return f"Uniden Adapter ({mode} mode)"
