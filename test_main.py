import unittest
from unittest.mock import patch
import time # Keep for time.time() if used, but be careful with sleep mocking

# Import the function to be tested
from Main import demo_delay # play_external_audio is removed

class TestMainFunctions(unittest.TestCase):

    # test_play_external_audio_runs is removed as play_external_audio was removed from Main.py

    @patch('time.sleep')
    def test_demo_delay(self, mock_sleep):
        # Test that demo_delay calls time.sleep with the correct argument
        delay_duration = 0.1
        demo_delay(delay_duration)
        mock_sleep.assert_called_once_with(delay_duration)

        # The original assertion `assert time.time() - start < 0.1` is not reliable
        # when time.sleep is mocked, as the actual time passage isn't what's being tested.
        # The key is that sleep was called with the correct parameter.

if __name__ == '__main__':
    unittest.main()
    # The lines below this were problematic and are removed:
    # from Main import demo_delay
    # demo_delay(0.1)
    # assert time.time() - start >= 0.1 # This would cause NameError: name 'start' is not defined
                                      # and is not part of the unittest structure.
