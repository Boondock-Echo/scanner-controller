"""
Scanner controller module for interfacing with scanner command libraries.

This module provides a controller class that interfaces with various scanner
command libraries and adapters, allowing the GUI to communicate with different
scanner models through a consistent interface.
"""

import serial

from utilities.log_utils import get_logger

# Get a logger for this module
logger = get_logger(__name__)


class ScannerController:
    """
    Controller for interfacing with scanner devices through command libraries.

    This class provides a unified interface for the GUI to access scanner
    functionality, handling the details of communicating with different
    scanner models.
    """

    def __init__(self, port=None, model=None, baudrate=115200):
        """
        Initialize the scanner controller.

        Args:
            port (str, optional): Serial port for the scanner.
            model (str, optional): Scanner model identifier.
            baudrate (int, optional): Serial port baudrate.
        """
        self.port = port
        self.model = model
        self.baudrate = baudrate
        self.ser = None
        self.adapter = None
        self.commands = {}

    def connect(self, port=None, model=None):
        """
        Connect to a scanner device.

        Args:
            port (str, optional): Serial port to connect to.
            model (str, optional): Scanner model to connect to.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        if port:
            self.port = port
        if model:
            self.model = model

        if not self.port or not self.model:
            logger.error("Port and model must be specified")
            return False

        try:
            # Close existing connection if any
            if self.ser and self.ser.is_open:
                self.ser.close()

            # Open new connection
            self.ser = serial.Serial(
                self.port, self.baudrate, timeout=1.0, write_timeout=1.0
            )

            # Load appropriate adapter
            self.adapter = self._get_scanner_adapter()
            if not self.adapter:
                logger.error(f"No adapter available for model {self.model}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error connecting to scanner: {e}")
            return False

    def _get_scanner_adapter(self):
        """
        Get the appropriate scanner adapter for the current model.

        Returns:
            object: Scanner adapter instance or None if not available.
        """
        try:
            # Use the scanner factory from utilities
            from utilities.scanner_factory import get_scanner_adapter

            return get_scanner_adapter(self.model, self.ser)
        except ImportError:
            logger.error("Could not import scanner factory")
            return None
        except Exception as e:
            logger.error(f"Error getting scanner adapter: {e}")
            return None

    def disconnect(self):
        """Close the connection to the scanner."""
        if self.ser and self.ser.is_open:
            self.ser.close()

    def _call_adapter_method(
        self, snake_case_name, camel_case_name, *args, default_return=None
    ):
        """
        Call a method on the adapter with fallback between naming conventions.

        Args:
            snake_case_name (str): The snake_case name of the method
            camel_case_name (str): The camelCase name of the method (legacy)
            *args: Arguments to pass to the method
            default_return: Value to return if the method cannot be called

        Returns:
            The result of the method call or default_return on error
        """
        if not self.adapter or not self.ser:
            return default_return

        try:
            if hasattr(self.adapter, snake_case_name):
                method = getattr(self.adapter, snake_case_name)
                return method(self.ser, *args)
            elif hasattr(self.adapter, camel_case_name):
                method = getattr(self.adapter, camel_case_name)
                return method(self.ser, *args)
            else:
                logger.error(
                    f"No suitable method found: {snake_case_name} or "
                    f"{camel_case_name}"
                )
                return default_return
        except Exception as e:
            logger.error(f"Error calling {snake_case_name}: {e}")
            return default_return

    def send_key(self, key):
        """
        Send a key command to the scanner.

        Args:
            key (str): Key command to send.

        Returns:
            str: Response from the scanner or empty string on error.
        """
        return self._call_adapter_method(
            'send_key', 'sendKey', key, default_return=""
        )

    def read_status(self):
        """
        Read the current status from the scanner.

        Returns:
            str: Status response from the scanner or empty string on error.
        """
        status = self._call_adapter_method(
            'read_status', 'readStatus', default_return=""
        )

        # Sanitize the response to ensure it only contains valid ASCII
        if status:
            # Replace non-ASCII characters with spaces
            sanitized_status = ''.join(
                c if ord(c) < 128 else ' ' for c in status
            )

            # If the sanitization made significant changes, log a debug message
            if sanitized_status != status:
                logger.debug(f"Sanitized status response: {sanitized_status}")

            return sanitized_status
        return ""

    def read_rssi(self):
        """
        Read RSSI (signal strength) from the scanner.

        Returns:
            float: RSSI value between 0.0 and 1.0 or 0.0 on error.
        """
        return self._call_adapter_method(
            'read_rssi', 'readRSSI', default_return=0.0
        )

    def set_volume(self, level):
        """
        Set the volume level on the scanner.

        Args:
            level (float): Volume level between 0.0 and 1.0.

        Returns:
            bool: True if successful, False otherwise.
        """
        result = self._call_adapter_method(
            'set_volume', 'writeVolume', level, default_return=False
        )
        return result is not False

    def set_squelch(self, level):
        """
        Set the squelch level on the scanner.

        Args:
            level (float): Squelch level between 0.0 and 1.0.

        Returns:
            bool: True if successful, False otherwise.
        """
        result = self._call_adapter_method(
            'set_squelch', 'writeSquelch', level, default_return=False
        )
        return result is not False
