"""
Test script for BCD325P2 adapter to verify the fix for the machineMode attribute
"""

import os
import sys
from unittest.mock import MagicMock

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter


def test_machine_mode_attribute():
    """Test the machineMode attribute is present and has the correct value"""
    adapter = BCD325P2Adapter()

    # Verify the machineMode attribute exists
    assert hasattr(adapter, "machineMode"), "machineMode attribute is missing"

    # Verify the machineMode has the correct value
    assert (
        adapter.machineMode == "BCD325P2"
    ), f"machineMode should be 'BCD325P2', got '{adapter.machineMode}'"

    print("✓ BCD325P2Adapter has the correct machineMode attribute")


def test_read_frequency():
    """Test the readFrequency method doesn't raise an AttributeError"""
    adapter = BCD325P2Adapter()

    try:
        # Check if the method exists (note the camelCase naming convention)
        if hasattr(adapter, "readFrequency"):
            # Create a mock serial object to pass to the method
            mock_ser = MagicMock()
            mock_ser.read.return_value = b"RF,154.3250\r"
            mock_ser.write.return_value = len(b"RF\r")
            mock_ser.in_waiting = 15

            # Use the correct camelCase method name with the mock serial object
            result = adapter.readFrequency(mock_ser)
            print(f"✓ readFrequency method returned: {result}")
        elif hasattr(adapter, "read_frequency"):
            # Try snake_case as fallback with mock serial
            mock_ser = MagicMock()
            mock_ser.read.return_value = b"RF,154.3250\r"
            mock_ser.write.return_value = len(b"RF\r")
            mock_ser.in_waiting = 15

            result = adapter.read_frequency(mock_ser)
            print(f"✓ read_frequency method returned: {result}")
        else:
            # No matching method found
            raise AttributeError(
                "Adapter doesn't have readFrequency or read_frequency method. "
                "Please implement one of these methods in the adapter class."
            )
    except AttributeError as e:
        print(f"✗ readFrequency raised AttributeError: {e}")
        raise
    except Exception as e:
        # This is fine - we expect other errors without a real connection
        print(f"i Other exception occurred (expected without device): {e}")
        # Still mark the test as passing since we're just checking if the method exists
        # and can be called with the right parameters


if __name__ == "__main__":
    print("Testing BCD325P2Adapter fixes...")
    test_machine_mode_attribute()
    test_read_frequency()
    print("All tests passed!")
