"""
Scanner controller module for interfacing with scanner command libraries.

This module provides a controller class that interfaces with various scanner
command libraries and adapters, allowing the GUI to communicate with different
scanner models through a consistent interface.
"""

import serial

from utilities.log_utils import get_logger

# Get a logger for this module with increased verbosity
logger = get_logger(__name__, level="DEBUG")


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
            from utilities.scanner.factory import get_scanner_adapter

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

    def _send_direct_command(self, command, log_prefix="Command"):
        """
        Send a command directly to the scanner, bypassing adapter methods.

        Args:
            command (str): Command string to send
            log_prefix (str): Prefix for log messages

        Returns:
            str: Response from scanner or empty string on error
        """
        if not self.ser or not self.ser.is_open:
            logger.error(f"{log_prefix}: No open serial connection")
            return ""

        try:
            from utilities.core.serial_utils import send_command

            logger.debug(f"{log_prefix}: Sending direct command: {command}")

            # Ensure command is properly formatted
            if not command.endswith('\r'):
                command = command + '\r'

            response = send_command(self.ser, command)
            logger.debug(
                f"{log_prefix}: Response: {response!r}"
            )  # Use !r to show raw string
            return response
        except Exception as e:
            logger.error(f"{log_prefix}: Error sending direct command: {e}")
            return ""

    def _get_volume_range(self):
        """
        Get the volume range for the current scanner model.

        Returns:
            tuple: (min, max) volume values for the current model
        """
        # Default range is 0-15 (common for many scanners)
        vol_min, vol_max = 0, 15

        # Model-specific ranges
        if self.model:
            model_upper = self.model.upper()

            # Handle known models with different ranges
            if model_upper in ['BC15', 'BC125AT', 'UBC125XLT']:
                vol_min, vol_max = 0, 15
            elif model_upper in ['BCD325P2', 'BCD396T']:
                vol_min, vol_max = 0, 15
            elif model_upper in ['BCD436HP', 'BCD536HP']:
                vol_min, vol_max = 0, 15
            # Add more models as needed

        logger.debug(f"Volume range for {self.model}: {vol_min}-{vol_max}")
        return vol_min, vol_max

    def send_key(self, key):
        """
        Send a key command to the scanner.

        Args:
            key (str): Key command to send.

        Returns:
            str: Response from the scanner or empty string on error.
        """
        if not self.adapter:
            return ""
        try:
            return self.adapter.send_key(self.ser, key)
        except Exception as e:
            logger.error(f"Error calling send_key: {e}")
            return ""

    def read_status(self):
        """
        Read the current status from the scanner.

        Returns:
            str: Status response from the scanner or empty string on error.
        """
        if not self.adapter:
            return ""

        try:
            status = self.adapter.read_status(self.ser)
        except Exception as e:
            logger.error(f"Error calling read_status: {e}")
            return ""

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
        Read the RSSI (Received Signal Strength Indicator) from the scanner.

        Returns:
            float: The RSSI value between 0.0 and 1.0, or 0.0 if not available.
        """
        if not self.adapter:
            return 0.0

        try:
            # Use PWR command to get current signal level
            # Response format: PWR,RSSI,FREQUENCY
            response = self.adapter.send_command(self.ser, "PWR")

            # Handle the response based on its type
            if response is not None:
                # Convert bytes to string if needed
                if isinstance(response, bytes):
                    response = response.decode('ascii', errors='replace')
                elif not isinstance(response, str):
                    # If it's neither bytes nor string, convert to string
                    response = str(response)

                # Now we can safely check if the string starts with "PWR,"
                if response.startswith("PWR,"):
                    parts = response.strip().split(',')
                    if len(parts) >= 2:
                        # Convert RSSI to float in range 0.0-1.0
                        # RSSI from scanner is 0-1023
                        try:
                            raw_rssi = int(parts[1])
                            normalized_rssi = raw_rssi / 1023.0
                            logger.debug(
                                f"Raw RSSI: {raw_rssi}, "
                                f"Normalized: {normalized_rssi}"
                            )
                            return normalized_rssi
                        except ValueError:
                            logger.debug(f"Invalid RSSI value: {parts[1]}")
                            return 0.0

            # If we got this far, something was wrong with the response
            logger.debug(f"Invalid RSSI response: {response!r}")
            return 0.0

        except Exception as e:
            logger.error(f"Error reading RSSI: {e}")
            return 0.0

    def set_volume(self, level):
        """
        Set the volume level on the scanner.

        Args:
            level (float): Volume level between 0.0 and 1.0.

        Returns:
            bool: True if successful, False otherwise.
        """
        # Ensure level is properly bounded
        level = max(0.0, min(1.0, level))

        # Log raw input value
        logger.debug(f"Volume input: raw={level}")

        # Get volume range for this scanner model
        vol_min, vol_max = self._get_volume_range()

        # Scale 0.0-1.0 to the scanner's actual range (e.g., 0-15)
        vol_int = int(round(level * vol_max))

        logger.debug(
            f"Setting volume to {level:.4f} (maps to {vol_int} in range "
            f"{vol_min}-{vol_max})"
        )

        # 1. Try direct VOL command
        logger.debug(f"Volume attempt #1: Direct VOL,{vol_int} command")
        response = self._send_direct_command(f"VOL,{vol_int}", "Volume")
        if response and "ERR" not in response:
            logger.info(f"Volume set to {vol_int} using direct VOL command")
            return True

        # 2. Try direct "V" command (some scanners use this format)
        logger.debug(f"Volume attempt #2: Direct V,{vol_int} command")
        response = self._send_direct_command(f"V,{vol_int}", "Volume")
        if response and "ERR" not in response:
            logger.info(f"Volume set to {vol_int} using direct V command")
            return True

        # 3. Try adapter method if available
        if self.adapter:
            logger.debug("Volume attempt #3: Using adapter methods")
            try:
                # Try send_command if available on adapter
                if hasattr(self.adapter, 'send_command'):
                    try:
                        # Try with bytes encoding to fix the error
                        logger.debug(
                            "Trying adapter.send_command with bytes: VOL,"
                            f"{vol_int}"
                        )
                        cmd_bytes = f"VOL,{vol_int}\r".encode('ascii')
                        result = self.adapter.send_command(self.ser, cmd_bytes)
                        if result and "ERR" not in str(result):
                            logger.info(
                                f"Volume set to {vol_int} using "
                                "adapter.send_command with bytes"
                            )
                            return True
                    except Exception as e:
                        logger.debug(f"Bytes command attempt failed: {e}")

                    # Try string version
                    try:
                        logger.debug(
                            "Trying adapter.send_command with string: VOL,"
                            f"{vol_int}"
                        )
                        result = self.adapter.send_command(
                            self.ser, f"VOL,{vol_int}"
                        )
                        if result and "ERR" not in str(result):
                            logger.info(
                                f"Volume set to {vol_int} using "
                                "adapter.send_command with string"
                            )
                            return True
                    except Exception as e:
                        logger.debug(f"String command attempt failed: {e}")

                # Try various method names
                for method_name in [
                    'set_volume',
                    'write_volume',
                    'volume',
                    'setVol',
                ]:
                    if hasattr(self.adapter, method_name):
                        logger.debug(
                            f"Trying adapter method: {method_name}({level})"
                        )
                        method = getattr(self.adapter, method_name)
                        result = method(self.ser, level)
                        logger.info(
                            f"Volume set to {level:.2f} using {method_name}"
                        )
                        return True
            except Exception as e:
                logger.error(f"Error with adapter volume methods: {e}")

        logger.error(
            f"All volume setting approaches failed for level {level:.2f}"
        )
        return False

    def set_squelch(self, level):
        """
        Set the squelch level on the scanner.

        Args:
            level (float): Squelch level between 0.0 and 1.0.

        Returns:
            bool: True if successful, False otherwise.
        """
        # Ensure level is properly bounded
        level = max(0.0, min(1.0, level))

        # Log raw input value
        logger.debug(f"Squelch input: raw={level}")

        # Most scanners use 0-15 range for squelch as well
        sql_max = 15
        sql_int = int(round(level * sql_max))

        logger.debug(
            f"Setting squelch to {level:.4f} (maps to {sql_int} in range 0-"
            f"{sql_max})"
        )

        # 1. Try direct SQL command
        logger.debug(f"Squelch attempt #1: Direct SQL,{sql_int} command")
        response = self._send_direct_command(f"SQL,{sql_int}", "Squelch")
        if response and "ERR" not in response:
            logger.info(f"Squelch set to {sql_int} using direct SQL command")
            return True

        # 2. Try direct "Q" command (some scanners use this format)
        logger.debug(f"Squelch attempt #2: Direct Q,{sql_int} command")
        response = self._send_direct_command(f"Q,{sql_int}", "Squelch")
        if response and "ERR" not in response:
            logger.info(f"Squelch set to {sql_int} using direct Q command")
            return True

        # 3. Try adapter method if available
        if self.adapter:
            logger.debug("Squelch attempt #3: Using adapter methods")
            try:
                # Try send_command if available on adapter with proper encoding
                if hasattr(self.adapter, 'send_command'):
                    try:
                        # Try with bytes encoding
                        logger.debug(
                            "Trying adapter.send_command with bytes: SQL,"
                            f"{sql_int}"
                        )
                        cmd_bytes = f"SQL,{sql_int}\r".encode('ascii')
                        result = self.adapter.send_command(self.ser, cmd_bytes)
                        if result and "ERR" not in str(result):
                            logger.info(
                                f"Squelch set to {sql_int} using "
                                "adapter.send_command with bytes"
                            )
                            return True
                    except Exception as e:
                        logger.debug(f"Bytes command attempt failed: {e}")

                # Try various method names
                for method_name in [
                    'set_squelch',
                    'write_squelch',
                    'squelch',
                    'setSql',
                ]:
                    if hasattr(self.adapter, method_name):
                        logger.debug(
                            f"Trying adapter method: {method_name}({level})"
                        )
                        method = getattr(self.adapter, method_name)
                        result = method(self.ser, level)
                        logger.info(
                            f"Squelch set to {level:.2f} using {method_name}"
                        )
                        return True
            except Exception as e:
                logger.error(f"Error with adapter squelch methods: {e}")

        logger.error(
            f"All squelch setting approaches failed for level {level:.2f}"
        )
        return False

    def read_volume(self):
        """
        Read the current volume level from the scanner.

        Returns:
            float: Volume level between 0.0 and 1.0, or 0.5 if not available
        """
        if not self.ser or not self.adapter:
            logger.warning("Cannot read volume: No connection established")
            return 0.5  # Default 50%

        try:
            # Get volume range for this model
            vol_min, vol_max = self._get_volume_range()

            # Try direct command first
            logger.debug("Reading volume via direct command")
            response = self._send_direct_command("VOL", "VolumeRead")

            # Response format is typically "VOL,X" where X is the volume level
            if response and response.startswith("VOL,"):
                try:
                    parts = response.strip().split(",")
                    if len(parts) >= 2:
                        raw_vol = int(parts[1])
                        normalized_vol = min(1.0, max(0.0, raw_vol / vol_max))
                        logger.debug(
                            f"Read volume: raw={raw_vol}, "
                            f"normalized={normalized_vol:.2f}"
                        )
                        return normalized_vol
                except (ValueError, IndexError) as e:
                    logger.debug(
                        f"Error parsing volume response '{response}': {e}"
                    )

            # Try adapter method if direct command failed
            if self.adapter:
                for method_name in [
                    'get_volume',
                    'read_volume',
                    'volume',
                    'getVol',
                ]:
                    if hasattr(self.adapter, method_name):
                        logger.debug(f"Trying adapter method: {method_name}")
                        method = getattr(self.adapter, method_name)
                        result = method(self.ser)
                        if result is not None:
                            if isinstance(result, (int, float)):
                                # Assume the result is already normalized or in
                                # raw form
                                if result > 1.0:
                                    # Raw value, normalize it
                                    normalized_vol = min(
                                        1.0, max(0.0, result / vol_max)
                                    )
                                else:
                                    # Already normalized
                                    normalized_vol = min(1.0, max(0.0, result))
                                logger.debug(
                                    "Read volume via {}: {:.2f}".format(
                                        method_name, normalized_vol
                                    )
                                )
                                return normalized_vol
                            else:
                                logger.debug(
                                    "Unexpected result type from {}: {}".format(
                                        method_name, type(result)
                                    )
                                )

            # If we get here, we couldn't read the volume
            logger.warning("Could not read volume, using default")
            return 0.5  # Default 50%

        except Exception as e:
            logger.error(f"Error reading volume: {e}")
            return 0.5  # Default 50%

    def read_squelch(self):
        """
        Read the current squelch level from the scanner.

        Returns:
            float: Squelch level between 0.0 and 1.0, or 0.2 if not available
        """
        if not self.ser or not self.adapter:
            logger.warning("Cannot read squelch: No connection established")
            return 0.2  # Default 20%

        try:
            # Most scanners use 0-15 range for squelch
            sql_max = 15

            # Try direct command first
            logger.debug("Reading squelch via direct command")
            response = self._send_direct_command("SQL", "SquelchRead")

            # Response format is typically "SQL,X" where X is the squelch level
            if response and response.startswith("SQL,"):
                try:
                    parts = response.strip().split(",")
                    if len(parts) >= 2:
                        raw_sql = int(parts[1])
                        normalized_sql = min(1.0, max(0.0, raw_sql / sql_max))
                        logger.debug(
                            f"Read squelch: raw={raw_sql}, "
                            f"normalized={normalized_sql:.2f}"
                        )
                        return normalized_sql
                except (ValueError, IndexError) as e:
                    logger.debug(
                        f"Error parsing squelch response '{response}': {e}"
                    )

            # Try adapter method if direct command failed
            if self.adapter:
                for method_name in [
                    'get_squelch',
                    'read_squelch',
                    'squelch',
                    'getSql',
                ]:
                    if hasattr(self.adapter, method_name):
                        logger.debug(f"Trying adapter method: {method_name}")
                        method = getattr(self.adapter, method_name)
                        result = method(self.ser)
                        if result is not None:
                            if isinstance(result, (int, float)):
                                # Assume the result is already normalized or in
                                # raw form
                                if result > 1.0:
                                    # Raw value, normalize it
                                    normalized_sql = min(
                                        1.0, max(0.0, result / sql_max)
                                    )
                                else:
                                    # Already normalized
                                    normalized_sql = min(1.0, max(0.0, result))
                                logger.debug(
                                    "Read squelch via {}: {:.2f}".format(
                                        method_name, normalized_sql
                                    )
                                )
                                return normalized_sql
                            else:
                                logger.debug(
                                    "Unexpected result type from {}: {}".format(
                                        method_name, type(result)
                                    )
                                )

            # If we get here, we couldn't read the squelch
            logger.warning("Could not read squelch, using default")
            return 0.2  # Default 20%

        except Exception as e:
            logger.error(f"Error reading squelch: {e}")
            return 0.2  # Default 20%


class ControllerRegistry:
    """Registry for managing multiple :class:`ScannerController` instances."""

    def __init__(self):
        self._controllers = {}
        self._next_id = 1
        self._active_id = None

    @property
    def active_id(self):
        return self._active_id

    @active_id.setter
    def active_id(self, controller_id):
        if controller_id is not None and controller_id not in self._controllers:
            raise KeyError(f"Controller ID {controller_id} not found")
        self._active_id = controller_id

    def open_controller(self, port, model, baudrate=115200):
        """Create and connect a new controller.

        Returns the assigned controller ID and the controller instance."""
        controller = ScannerController(baudrate=baudrate)
        if not controller.connect(port=port, model=model):
            raise RuntimeError(f"Failed to connect to {model} on {port}")
        controller_id = self._next_id
        self._next_id += 1
        self._controllers[controller_id] = controller
        self._active_id = controller_id
        return controller_id, controller

    def close_controller(self, controller_id):
        """Disconnect and remove a controller."""
        controller = self._controllers.pop(controller_id, None)
        if controller:
            try:
                controller.disconnect()
            finally:
                if self._active_id == controller_id:
                    self._active_id = next(iter(self._controllers), None)

    def get(self, controller_id=None):
        """Retrieve a controller by ID."""
        if controller_id is None:
            controller_id = self._active_id
        return self._controllers.get(controller_id)

    def list_all(self):
        """Return all registered controllers."""
        return list(self._controllers.items())


# Global registry instance for convenience
controller_registry = ControllerRegistry()
