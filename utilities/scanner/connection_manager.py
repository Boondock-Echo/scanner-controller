import logging
import serial
from functools import partial

from utilities.core.command_registry import build_command_table
from utilities.io.timeout_utils import with_timeout
from utilities.scanner.factory import get_scanner_adapter

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage multiple scanner connections."""

    def __init__(self):
        self._connections = {}
        self._next_id = 1
        self._active_id = None

    @property
    def active_id(self):
        return self._active_id

    @active_id.setter
    def active_id(self, conn_id):
        if conn_id is not None and conn_id not in self._connections:
            raise KeyError(f"Connection ID {conn_id} not found")
        self._active_id = conn_id

    def open_connection(self, port, model, machine_mode=False):
        """Open a scanner connection and register it.

        Parameters
        ----------
        port : str
            Serial port to open.
        model : str
            Scanner model identifier.
        machine_mode : bool, optional
            Whether to initialize the adapter in machine mode.

        Returns
        -------
        int
            ID assigned to the new connection.
        """
        ser = serial.Serial(port, 115200, timeout=1.0, write_timeout=1.0)

        @with_timeout(30)
        def initialize_adapter():
            return get_scanner_adapter(model, machine_mode)

        adapter = initialize_adapter()
        if not adapter:
            ser.close()
            raise RuntimeError(f"No adapter implemented for {model}")

        commands, help_text = build_command_table(adapter, ser)
        bound_commands = {
            name: partial(func, ser, adapter) for name, func in commands.items()
        }

        conn_id = self._next_id
        self._next_id += 1
        self._connections[conn_id] = (ser, adapter, bound_commands, help_text)
        self._active_id = conn_id
        logger.info(f"Opened connection {conn_id} on {port} ({model})")
        return conn_id

    def close_connection(self, conn_id):
        """Close and remove a connection."""
        conn = self._connections.pop(conn_id, None)
        if not conn:
            return
        ser = conn[0]
        try:
            if ser and ser.is_open:
                ser.close()
        except Exception as exc:
            logger.error(f"Error closing connection {conn_id}: {exc}")
        if self._active_id == conn_id:
            self._active_id = next(iter(self._connections), None)

    def get(self, conn_id=None):
        """Retrieve a connection tuple by ID."""
        if conn_id is None:
            conn_id = self._active_id
        return self._connections.get(conn_id)

    def list_all(self):
        """Return a list of all managed connections."""
        return list(self._connections.items())
