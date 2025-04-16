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

import importlib
import logging


def get_scanner_adapter(scanner_model, machine_mode=False):
    """Create the appropriate scanner adapter for the given model.

    Factory function to create the appropriate scanner adapter
    based on the model name.

    Args:
        scanner_model (str): The scanner model name
        machine_mode (bool): Whether to use machine-friendly output

    Returns:
        An instance of the appropriate scanner adapter
    """
    # Define adapter mapping
    adapter_mapping = {
        "BC125AT": {
            "module": "adapters.uniden.bc125at_adapter",
            "class": "BC125ATAdapter",
        },
        "BCD325P2": {
            "module": "adapters.uniden.bcd325p2_adapter",
            "class": "BCD325P2Adapter",
        },
        "AOR-DV1": {
            "module": "adapters.aor.aordv1_adapter",
            "class": "AORDV1Adapter",
        },
        # Add new scanner models here
    }

    # Get adapter info
    adapter_info = adapter_mapping.get(scanner_model)
    if not adapter_info:
        logging.error(f"No adapter defined for scanner model: {scanner_model}")
        return None

    # Dynamically import the module and create the adapter
    try:
        module = importlib.import_module(adapter_info["module"])
        adapter_class = getattr(module, adapter_info["class"])
        return adapter_class(machine_mode=machine_mode)
    except ImportError as e:
        logging.error(
            f"Failed to import adapter module {adapter_info['module']}: {e}"
        )
        return None
    except AttributeError as e:
        logging.error(
            f"Failed to find adapter class {adapter_info['class']} "
            f"in module {adapter_info['module']}: {e}"
        )
        return None
    except Exception as e:
        logging.error(f"Error creating adapter for {scanner_model}: {e}")
        return None
