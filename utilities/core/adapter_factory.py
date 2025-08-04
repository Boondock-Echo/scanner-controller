"""
Main module for the scanner GUI.

This module contains the adapter factory function that creates scanner adapters.
It also includes the logic for loading the appropriate adapter based on the
model name.
"""

# Import statements
import importlib
import logging

logger = logging.getLogger(__name__)


def create_adapter(model_name, machine_mode=False):
    """
    Create an adapter for the specified scanner model.

    Args:
        model_name: The model name of the scanner (e.g., 'bc125at', 'bcd325p2')
        machine_mode: Whether to use machine-readable output format

    Returns:
        An adapter instance for the specified scanner model
    """
    model_key = model_name.lower()

    # Map model names to adapter modules
    adapter_map = {
        'bc125at': 'adapters.uniden.bc125at_adapter',
        'bcd325p2': 'adapters.uniden.bcd325p2_adapter',
        # Add more models as needed
        'rtlsdr': 'adapters.sdr.rtlsdr_adapter',
        'rx888': 'adapters.sdr.rx888_adapter',
    }

    class_map = {
        'bc125at': 'BC125ATAdapter',
        'bcd325p2': 'BCD325P2Adapter',
        # Add more models as needed
        'rtlsdr': 'RTLSDRAdapter',
        'rx888': 'RX888Adapter',
    }

    try:
        if model_key in adapter_map:
            module_path = adapter_map[model_key]
            class_name = class_map[model_key]

            logger.debug(f"Loading adapter module: {module_path}")
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)

            logger.info(f"Creating adapter for {model_name.upper()}")
            return adapter_class(machine_mode=machine_mode)

        prefixes = ("bc", "bcd", "ubc", "sds")
        if any(model_key.startswith(prefix) for prefix in prefixes):
            from adapters.uniden.generic_adapter import GenericUnidenAdapter

            logger.info(
                f"Creating generic Uniden adapter for unrecognized model: {model_name.upper()}"
            )
            return GenericUnidenAdapter(machine_mode=machine_mode)

        raise ValueError(f"No adapter implemented for {model_name.upper()}")
    except Exception as e:
        logger.error(
            f"Error creating adapter for {model_name.upper()}: {str(e)}"
        )
        raise
