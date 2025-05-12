import unittest
from unittest.mock import patch
from Main import play_external_audio, demo_delay

class TestMainFunctions(unittest.TestCase):

    @patch('subprocess.Popen')
    def test_play_external_audio_runs(self, mock_popen):
        # This test only checks that the function runs without error for a dummy file
        # Replace 'dummy.mp3' with a real file path for integration testing
        play_external_audio('dummy.mp3')
        mock_popen.assert_called_once()

    @patch('time.sleep')
    def test_demo_delay(self, mock_sleep):
        start = time.time()
        demo_delay(0.1)
        mock_sleep.assert_called_once_with(0.1)
        assert time.time() - start < 0.1  # since sleep is mocked, time shouldn't pass

if __name__ == '__main__':
    unittest.main()
    from Main import demo_delay
    demo_delay(0.1)
    assert time.time() - start >= 0.1
