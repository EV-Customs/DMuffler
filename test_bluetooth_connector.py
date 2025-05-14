from unittest.mock import MagicMock
sys.modules['bluepy'] = MagicMock()
sys.modules['bluepy.btle'] = MagicMock()

import pytest
from BluetoothConnector import connect_with_retry
import sys

def test_connect_with_retry_success():
    mock_peripheral = MagicMock()
    with patch('bluepy.btle.Peripheral', return_value=mock_peripheral):
        with patch('BluetoothConnector.Peripheral', return_value=mock_peripheral):
            result = connect_with_retry('addr', 'addr_type', max_attempts=1, delay=0)
            assert result is not None

def test_connect_with_retry_failure():
    with patch('bluepy.btle.Peripheral', side_effect=Exception("fail")):
        with patch('BluetoothConnector.Peripheral', side_effect=Exception("fail")):
            result = connect_with_retry('addr', 'addr_type', max_attempts=2, delay=0)
            assert result is False
