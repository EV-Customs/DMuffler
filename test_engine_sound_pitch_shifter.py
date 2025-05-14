import unittest
from unittest.mock import patch
from EngineSoundPitchShifter import example_pitch_shift

class TestEngineSoundPitchShifter(unittest.TestCase):

    @patch('EngineSoundPitchShifter.peek')
    def test_example_pitch_shift_runs(self, mock_peek):
        dummy_data = [1, 2, 3]
        result = example_pitch_shift(dummy_data, 1.2)
        assert result == dummy_data

if __name__ == '__main__':
    unittest.main()
