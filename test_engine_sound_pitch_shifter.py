import unittest
from unittest.mock import patch, MagicMock
import os # For path joining

# Import the class to be tested
from EngineSoundPitchShifter import EngineSoundPitchShifter
# Assuming GlobalConstants defines MC_LAREN_F1 or a similar default sound
import GlobalConstants as GC 

# Mocking pynput.keyboard.Key for on_press/on_release tests
class MockKey:
    def __init__(self, char=None, name=None):
        self.char = char
        self.name = name # For special keys like 'esc'

    def __eq__(self, other):
        if isinstance(other, MockKey):
            return self.char == other.char and self.name == other.name
        elif isinstance(other, str): # Allow comparison with string for char
            return self.char == other
        return False

class TestEngineSoundPitchShifterActual(unittest.TestCase):

    def setUp(self):
        # Basic setup that might be common for multiple tests
        # Ensure a dummy sound file exists for tests that might reach librosa.load
        # This is important if librosa.load is not always mocked.
        self.test_sound_filename = "test_dummy_sound.wav"
        # Create a dummy WAV file for librosa.load to potentially use if not mocked.
        # This path assumes the test is run from a directory where 'static/sounds' can be created or accessed.
        # For true unit tests, librosa.load should always be mocked.
        # However, if we want to test the path construction logic in EngineSoundPitchShifter,
        # the base directory needs to be correct. EngineSoundPitchShifter uses `os.path.dirname(os.path.abspath(__file__))`
        # so it refers to the EngineSoundPitchShifter.py's directory.
        # For tests, we might need to ensure a file exists relative to that.
        # For now, assume librosa.load will be mocked in most constructor tests.
        
        # Default sound file for initialization
        # Try to use a constant from GlobalConstants if available, otherwise a placeholder.
        self.default_sound = getattr(GC, 'MC_LAREN_F1', 'mc_laren_f1.wav')


    @patch('EngineSoundPitchShifter.sd.OutputStream')
    @patch('EngineSoundPitchShifter.librosa.load')
    def test_constructor_initialization_success(self, mock_librosa_load, mock_sd_output_stream):
        # Configure mocks for successful initialization
        mock_librosa_load.return_value = (MagicMock(), 44100) # dummy audio time series, sample rate
        mock_sd_output_stream.return_value = MagicMock() # dummy stream object

        # Path setup for EngineSoundPitchShifter
        # EngineSoundPitchShifter constructs path like:
        # os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "sounds", baseAudioFilename)
        # We need to ensure the mocked librosa.load is what's called, not a real file load.
        
        shifter = EngineSoundPitchShifter(self.default_sound)

        self.assertTrue(shifter.audioFilepath.endswith(os.path.join("static", "sounds", self.default_sound)))
        self.assertEqual(shifter.sampleRate, 44100)
        self.assertFalse(shifter.playing)
        self.assertEqual(shifter.currentFrame, 0)
        self.assertEqual(shifter.pitchFactor, 1.0)
        self.assertTrue(shifter.running) # Should be true if all initializations succeed
        mock_librosa_load.assert_called_once()
        mock_sd_output_stream.assert_called_once()
        shifter.stream.start.assert_called_once() # Ensure stream.start() was called

    @patch('EngineSoundPitchShifter.sd.OutputStream')
    @patch('EngineSoundPitchShifter.librosa.load')
    def test_constructor_librosa_load_failure(self, mock_librosa_load, mock_sd_output_stream):
        # Configure librosa.load to raise an exception
        mock_librosa_load.side_effect = Exception("Failed to load audio")

        shifter = EngineSoundPitchShifter(self.default_sound)
        
        self.assertFalse(shifter.running, "Shifter should not be running if librosa.load fails.")
        # stream may or may not be initialized depending on where the return is,
        # but if it is, it should not be started.
        # Based on current EngineSoundPitchShifter, sd.OutputStream is not called if librosa.load fails.
        mock_sd_output_stream.assert_not_called()


    @patch('EngineSoundPitchShifter.sd.OutputStream')
    @patch('EngineSoundPitchShifter.librosa.load')
    def test_constructor_sounddevice_outputstream_failure(self, mock_librosa_load, mock_sd_output_stream):
        # Configure mocks for successful librosa.load but failing OutputStream
        mock_librosa_load.return_value = (MagicMock(), 44100)
        mock_sd_output_stream.side_effect = Exception("Failed to create OutputStream")

        shifter = EngineSoundPitchShifter(self.default_sound)

        self.assertFalse(shifter.running, "Shifter should not be running if sd.OutputStream fails.")
        # Ensure stream.start() was not called if stream creation failed
        # Accessing shifter.stream might be problematic if it's not set on failure.
        # The current EngineSoundPitchShifter sets self.stream and then tries to start it.
        # If self.stream.start() is what fails (after a successful stream object creation part of the mock),
        # then self.running should also be False.
        # If sd.OutputStream itself fails, then self.stream might be None or not have start method.
        # Let's assume sd.OutputStream constructor itself fails.
        # No, the current code is: self.stream = sd.OutputStream(...); self.stream.start().
        # So, if sd.OutputStream fails, self.stream is not assigned.
        # If self.stream.start() fails, then self.stream exists.
        # The mock_sd_output_stream.side_effect is on the constructor.
        
        # Based on current EngineSoundPitchShifter, if sd.OutputStream(...) fails,
        # self.running is set to False, and stream.start() is not reached for the created stream.
        # If sd.OutputStream is mocked to raise an exception on construction,
        # then self.stream.start() should not be called.
        # We need to check what happens to self.stream if the constructor fails.
        # In the code: self.stream = sd.OutputStream(...); self.stream.start()
        # If the first part fails, self.stream is not assigned.
        # The current code would throw an AttributeError if self.stream is not assigned before .start()
        # However, the exception is caught, and self.running becomes False.

        # Let's refine the check: if sd.OutputStream constructor throws error, stream object won't be assigned.
        self.assertIsNone(shifter.stream, "Stream object should ideally be None if its creation failed.")
        # Or, if the design is to assign it then it fails, then check stream.start was not called.
        # Given the current structure, the error is caught, self.running = False.
        # And self.stream might not be set or if it was partially set, its start() method might not be called.
        # The critical part is self.running is False.


    @patch('EngineSoundPitchShifter.librosa.load') # Mock librosa.load for constructor
    @patch('EngineSoundPitchShifter.sd.OutputStream') # Mock OutputStream for constructor
    def test_on_press_and_release(self, mock_sd_output_stream, mock_librosa_load):
        # Setup for successful object creation
        mock_librosa_load.return_value = (MagicMock(), 44100)
        mock_stream = MagicMock()
        mock_sd_output_stream.return_value = mock_stream

        shifter = EngineSoundPitchShifter(self.default_sound)
        
        # Test initial state
        self.assertFalse(EngineSoundPitchShifter.isWPressed, "isWPressed should be initially False.")

        # Test on_press
        mock_w_key = MockKey(char='w') # Using simplified mock for pynput.keyboard.Key
        shifter.on_press(mock_w_key)
        self.assertTrue(EngineSoundPitchShifter.isWPressed, "isWPressed should be True after 'W' press.")

        # Test on_release
        shifter.on_release(mock_w_key)
        self.assertFalse(EngineSoundPitchShifter.isWPressed, "isWPressed should be False after 'W' release.")

        # Test on_press with different character (uppercase 'W')
        mock_upper_w_key = MockKey(char='W')
        shifter.on_press(mock_upper_w_key)
        self.assertTrue(EngineSoundPitchShifter.isWPressed, "isWPressed should be True after uppercase 'W' press.")
        shifter.on_release(mock_upper_w_key)
        self.assertFalse(EngineSoundPitchShifter.isWPressed, "isWPressed should be False after uppercase 'W' release.")

        # Test special key (AttributeError expected and handled in on_press/on_release)
        mock_esc_key = MockKey(name='esc') # No char attribute
        try:
            shifter.on_press(mock_esc_key)
            shifter.on_release(mock_esc_key)
        except AttributeError:
            self.fail("on_press/on_release should handle AttributeError for special keys")
        
        # Cleanup globals if they are modified by tests (important for test isolation)
        EngineSoundPitchShifter.isWPressed = False
        EngineSoundPitchShifter.isEscPressed = False


    @patch('EngineSoundPitchShifter.librosa.load') # Mock librosa.load for constructor
    @patch('EngineSoundPitchShifter.sd.OutputStream') # Mock OutputStream for constructor
    def test_cleanup(self, mock_sd_output_stream, mock_librosa_load):
        # Setup for successful object creation
        mock_librosa_load.return_value = (MagicMock(), 44100)
        mock_stream_obj = MagicMock() # This will be our self.stream
        mock_sd_output_stream.return_value = mock_stream_obj
        
        shifter = EngineSoundPitchShifter(self.default_sound)
        self.assertTrue(shifter.running) # Should be running initially

        # Call cleanup
        shifter.cleanup()

        # Assertions
        self.assertFalse(shifter.running, "Shifter should not be running after cleanup.")
        mock_stream_obj.stop.assert_called_once()
        mock_stream_obj.close.assert_called_once()

    @patch('EngineSoundPitchShifter.librosa.load')
    @patch('EngineSoundPitchShifter.sd.OutputStream')
    def test_cleanup_when_stream_not_active(self, mock_sd_output_stream, mock_librosa_load):
        mock_librosa_load.return_value = (MagicMock(), 44100)
        mock_stream_obj = MagicMock()
        mock_stream_obj.active = False # Simulate stream not being active
        mock_sd_output_stream.return_value = mock_stream_obj
        
        shifter = EngineSoundPitchShifter(self.default_sound)
        shifter.running = True # Assume it was running

        shifter.cleanup()

        self.assertFalse(shifter.running)
        mock_stream_obj.stop.assert_not_called() # Should not be called if not active
        mock_stream_obj.close.assert_not_called() # Should not be called if not active

    @patch('EngineSoundPitchShifter.librosa.load')
    @patch('EngineSoundPitchShifter.sd.OutputStream')
    def test_cleanup_no_stream_attribute(self, mock_sd_output_stream, mock_librosa_load):
        # Test scenario where self.stream might not have been initialized (e.g. error in constructor)
        mock_librosa_load.return_value = (MagicMock(), 44100)
        # Simulate sd.OutputStream failing and self.stream not being set
        mock_sd_output_stream.side_effect = Exception("Stream creation failed")

        shifter = EngineSoundPitchShifter(self.default_sound)
        self.assertFalse(shifter.running) # Should not be running
        
        # Ensure cleanup doesn't crash if self.stream is None or missing
        try:
            shifter.cleanup() 
        except AttributeError:
            self.fail("cleanup() raised AttributeError when stream was not initialized.")
        
        self.assertFalse(shifter.running) # Still should be false

if __name__ == '__main__':
    unittest.main()
