"""Create scanner adapters dynamically based on model names.

This module provides a factory function to dynamically create and return
the appropriate scanner adapter instance based on the provided scanner
model name. It supports a variety of scanner models and allows for easy
extension by adding new models to the adapter mapping.

The factory function uses dynamic module importing to load the required
adapter class at runtime, ensuring flexibility and modularity. This is
particularly useful for managing multiple scanner models without
hardcoding dependencies.

Key Features:
- Dynamically maps scanner models to their respective adapter modules
  and classes.
- Provides error handling for missing or invalid adapter definitions.
- Supports an optional `machine_mode` argument for machine-friendly output.

Usage:
- Add new scanner models by extending the `adapter_mapping` dictionary with
    the appropriate module and class information.
- Call `get_scanner_adapter(scanner_model, machine_mode)` to retrieve an
    instance of the desired scanner adapter.

Dependencies:
- `importlib` for dynamic module importing.
- `logging` for error reporting and debugging.

Example:
        adapter = get_scanner_adapter("BC125AT", machine_mode=True)
        if adapter:
                adapter.perform_some_action()
"""

import logging


def get_scanner_adapter(model, machine_mode=False):
    """
    Get the appropriate scanner adapter for the given model.

    Args:
        model (str): Scanner model string
        machine_mode (bool): Whether to use machine-friendly output

    Returns:
        object: Scanner adapter instance
    """
    model = model.upper()

    try:
        if "BC125AT" in model:
            from scanner_controller.adapters.uniden.bc125at_adapter import BC125ATAdapter

            logging.info(f"Creating adapter for {model}")
            return BC125ATAdapter(machine_mode=machine_mode)
        elif "BCD325P2" in model:
            from scanner_controller.adapters.uniden.bcd325p2_adapter import BCD325P2Adapter

            logging.info(f"Creating adapter for {model}")
            return BCD325P2Adapter(machine_mode=machine_mode)
        elif "RTLSDR" in model:
            from scanner_controller.adapters.sdr.rtlsdr_adapter import RTLSDRAdapter

            logging.info(f"Creating adapter for {model}")
            return RTLSDRAdapter(machine_mode=machine_mode)
        elif "RX888" in model:
            from scanner_controller.adapters.sdr.rx888_adapter import RX888Adapter

            logging.info(f"Creating adapter for {model}")
            return RX888Adapter(machine_mode=machine_mode)
        else:
            prefixes = ("BC", "BCD", "UBC", "SDS")
            if any(model.startswith(prefix) for prefix in prefixes):
                from scanner_controller.adapters.uniden.generic_adapter import GenericUnidenAdapter

                logging.info(
                    f"Creating generic Uniden adapter for unrecognized model: {model}"
                )
                return GenericUnidenAdapter(machine_mode=machine_mode)

            logging.error(f"No adapter available for model: {model}")
            return None
    except Exception as e:
        logging.error(f"Error creating adapter for {model}: {str(e)}")
        return None
