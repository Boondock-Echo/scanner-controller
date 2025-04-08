"""
Test script for BCD325P2 adapter to verify the fix for the machineMode attribute
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter

def test_machine_mode_attribute():
    """Test the machineMode attribute is present and has the correct value"""
    adapter = BCD325P2Adapter()
    
    # Verify the machineMode attribute exists
    assert hasattr(adapter, 'machineMode'), "machineMode attribute is missing"
    
    # Verify the machineMode has the correct value
    assert adapter.machineMode == 'BCD325P2', f"machineMode should be 'BCD325P2', got '{adapter.machineMode}'"
    
    print("✓ BCD325P2Adapter has the correct machineMode attribute")

def test_read_frequency():
    """Test the read_frequency method doesn't raise an AttributeError"""
    adapter = BCD325P2Adapter()
    
    try:
        # Just test that the method runs without AttributeError
        # (we don't need a real connection to test this)
        adapter.read_frequency()
        print("✓ read_frequency method doesn't raise AttributeError")
    except AttributeError as e:
        print(f"✗ read_frequency raised AttributeError: {e}")
        raise
    except Exception as e:
        # This is fine - we expect other errors without a real connection
        print(f"i Other exception occurred (expected without device): {e}")

if __name__ == "__main__":
    print("Testing BCD325P2Adapter fixes...")
    test_machine_mode_attribute()
    test_read_frequency()
    print("All tests passed!")
