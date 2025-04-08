import importlib
import logging

def get_scanner_adapter(scanner_model, machine_mode=False):
    """
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
            "class": "BC125ATAdapter"
        },
        "BCD325P2": {
            "module": "adapters.uniden.bcd325p2_adapter",
            "class": "BCD325P2Adapter"
        },
        "AOR-DV1": {
            "module": "adapters.aor.aordv1_adapter",
            "class": "AORDV1Adapter"
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
        logging.error(f"Failed to import adapter module {adapter_info['module']}: {e}")
        return None
    except AttributeError as e:
        logging.error(f"Failed to find adapter class {adapter_info['class']} in module {adapter_info['module']}: {e}")
        return None
    except Exception as e:
        logging.error(f"Error creating adapter for {scanner_model}: {e}")
        return None
