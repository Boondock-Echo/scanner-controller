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
    model_name = model_name.lower()

    # Map model names to adapter modules
    adapter_map = {
        'bc125at': 'adapters.uniden.bc125at_adapter',
        'bcd325p2': 'adapters.uniden.bcd325p2_adapter',
        # Add more models as needed
    }

    class_map = {
        'bc125at': 'BC125ATAdapter',
        'bcd325p2': 'BCD325P2Adapter',
        # Add more models as needed
    }

    try:
        if model_name not in adapter_map:
            raise ValueError(f"No adapter implemented for {model_name.upper()}")

        module_path = adapter_map[model_name]
        class_name = class_map[model_name]

        logger.debug(f"Loading adapter module: {module_path}")
        module = importlib.import_module(module_path)
        adapter_class = getattr(module, class_name)

        logger.info(f"Creating adapter for {model_name.upper()}")
        return adapter_class(machine_mode=machine_mode)
    except Exception as e:
        logger.error(
            f"Error creating adapter for {model_name.upper()}: {str(e)}"
        )
        raise
