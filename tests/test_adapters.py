"""
Tests for scanner adapters
"""
import pytest
import importlib
import sys
from unittest.mock import patch, MagicMock

def test_base_adapter_interface():
    """Test that BaseScannerAdapter defines the expected interface"""
    try:
        base_module = importlib.import_module('adapters.base_adapter')
        BaseAdapter = base_module.BaseScannerAdapter
        
        # Check if it's an ABC
        from abc import ABC
        assert issubclass(BaseAdapter, ABC)
        
        # Check for required abstract methods
        abstract_methods = ['connect', 'disconnect', 'send_command']
        for method in abstract_methods:
            assert method in BaseAdapter.__abstractmethods__
    except ImportError:
        pytest.skip("Base adapter module not available")

def test_bc125at_adapter_init():
    """Test that BC125ATAdapter initializes correctly"""
    try:
        adapter_module = importlib.import_module('adapters.uniden.bc125at_adapter')
        BC125ATAdapter = adapter_module.BC125ATAdapter
        
        adapter = BC125ATAdapter()
        assert hasattr(adapter, 'machineMode')
        assert adapter.machineMode == 'BC125AT'
    except ImportError:
        pytest.skip("BC125AT adapter module not available")

def test_bc125at_send_command(mock_serial_port):
    """Test sending command through the BC125AT adapter"""
    try:
        adapter_module = importlib.import_module('adapters.uniden.bc125at_adapter')
        BC125ATAdapter = adapter_module.BC125ATAdapter
        
        with patch('serial.Serial', return_value=mock_serial_port):
            adapter = BC125ATAdapter()
            adapter.ser = mock_serial_port
            
            # Test sending a valid command
            response = adapter.send_command("MDL")
            assert "BC125AT" in response
            
            # Verify write was called with correct command
            mock_serial_port.write.assert_called_with(b"MDL\r")
            
    except ImportError:
        pytest.skip("BC125AT adapter module not available")
