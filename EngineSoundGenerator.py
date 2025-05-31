#!/usr/bin/env python3
"""
Create pitch varying audio of a library of cars in real-time on low processing power CPUs
"""

import os
import time
import GlobalConstants as GC # Moved to module level
from logging_utils import log_info, log_warning, log_error # Moved to module level
import simpleaudio as sa

class EngineSoundGenerator:
    """
    Generates and plays engine sounds for a library of cars.
    Sound files are loaded based on configurations in GlobalConstants.py.
    """

    # Class attributes for sound filenames and local engine_sounds_dict were previously removed.
    # This class uses GlobalConstants.EngineSoundsDict (mapping filenames to IDs)
    # and GlobalConstants.SOUNDS_BASE_PATH (a Path object for the base sound directory).

    def __init__(self, base_audio_filename: str | None):
        """
        Initialize the EngineSoundGenerator.

        Args:
            base_audio_filename (str | None): The filename of the base audio to use
                                              (e.g., "mclaren_f1.wav"), or None to initialize without a sound.
        """
        self.engine_sound_wave_object = None
        self.engine_sound_id = None
        self.base_audio_filename = None # Stores the currently loaded sound filename

        if base_audio_filename:
            self.set_engine_sound(base_audio_filename)
        else:
            log_info("EngineSoundGenerator initialized without a base audio file.")

    def start_audio(self) -> sa.PlayObject | None:
        """
        Play the currently loaded sound once and return the play object.
        Returns None if no sound is loaded.
        """
        if self.engine_sound_wave_object:
            play_obj = self.engine_sound_wave_object.play()
            return play_obj
        else:
            log_warning("Cannot start audio: no sound loaded.")
            return None

    def start_audio_loop(self):
        """
        Play the currently loaded sound in a loop forever.

        **WARNING**: This is a BLOCKING call. It will run an infinite loop
        and the program will not proceed past this call unless the process
        is interrupted or the sound file is extremely short (not typical for engine sounds).
        Ensure this is run in a separate thread or process if non-blocking behavior is needed.
        """
        if not self.engine_sound_wave_object:
            log_error("Cannot start audio loop: no sound loaded.")
            return

        log_info(f"Starting audio loop for {self.base_audio_filename}. This will block.")
        while True:
            play_obj = self.engine_sound_wave_object.play()
            play_obj.wait_done() # Blocks until the sound has finished playing

    def stop_audio(self, play_obj: sa.PlayObject | None):
        """
        Stop the provided play object if it's currently playing.

        Args:
            play_obj (sa.PlayObject | None): The play object returned by start_audio().
                                             If None, the function does nothing.
        """
        if play_obj and play_obj.is_playing():
            play_obj.stop()
            log_info("Audio stopped.")
        elif play_obj:
            log_info("Audio play object provided but was not playing.")
        else:
            log_warning("Stop audio called with no play object.")


    def set_engine_sound(self, new_sound_filename: str):
        """
        Change the sound configured to play. Loads the new sound file.
        If loading fails, the previously loaded sound (if any) is retained.

        Args:
            new_sound_filename (str): The filename of the new sound to use (e.g., "mclaren_f1.wav").
                                      This filename must be a key in GlobalConstants.EngineSoundsDict.
        """
        # Store current sound state in case the new one fails to load
        previous_sound_filename = self.base_audio_filename
        previous_wave_object = self.engine_sound_wave_object
        previous_sound_id = self.engine_sound_id

        if new_sound_filename in GC.EngineSoundsDict:
            # Construct the full, absolute path using GC.SOUNDS_BASE_PATH (which is a Path object)
            # GC.SOUNDS_BASE_PATH is already an absolute path: PROJECT_ROOT / "static" / "sounds"
            sound_file_path: GC.Path = GC.SOUNDS_BASE_PATH / new_sound_filename

            log_info(f"Attempting to load sound: {new_sound_filename} from {sound_file_path}")
            try:
                # simpleaudio expects a string path
                wave_obj = sa.WaveObject.from_wave_file(str(sound_file_path))

                self.engine_sound_wave_object = wave_obj
                self.base_audio_filename = new_sound_filename
                self.engine_sound_id = GC.EngineSoundsDict[new_sound_filename]
                log_info(f"Engine sound successfully changed to {new_sound_filename}.")
            except FileNotFoundError:
                log_error(f"ERROR: Sound file not found at {sound_file_path}. Engine sound not changed.")
                self._revert_to_previous_sound(previous_sound_filename, previous_wave_object, previous_sound_id)
            except Exception as e: # Catch other simpleaudio errors or general exceptions
                log_error(f"ERROR: Could not load sound file {sound_file_path} for {new_sound_filename}: {e}. Engine sound not changed.")
                self._revert_to_previous_sound(previous_sound_filename, previous_wave_object, previous_sound_id)
        else:
            log_warning(f"WARNING: Sound filename '{new_sound_filename}' is not defined in GlobalConstants.EngineSoundsDict. Engine sound not changed.")
            if self.base_audio_filename:
                 log_warning(f"Keeping current sound: {self.base_audio_filename}")

    def _revert_to_previous_sound(self, prev_filename, prev_wave_obj, prev_id):
        """Helper to revert sound state if loading a new sound fails."""
        log_info("Reverting to previous sound state (if any).")
        self.base_audio_filename = prev_filename
        self.engine_sound_wave_object = prev_wave_obj
        self.engine_sound_id = prev_id


    def get_base_audio_filename(self) -> str | None:
        """
        Return the filename of the currently loaded engine sound.
        Returns None if no sound is loaded.
        """
        return self.base_audio_filename

    @staticmethod
    def unit_test():
        """
        Run the unit test for the EngineSoundGenerator. Uses mocked simpleaudio.
        """
        from unittest.mock import patch, MagicMock
        # sa is already imported at module level as simpleaudio

        log_info("STARTING EngineSoundGenerator.py Unit Test with Mocks")

        with patch('simpleaudio.WaveObject') as MockWaveObjectConstructor:
            mock_wave_instance = MagicMock()
            MockWaveObjectConstructor.from_wave_file.return_value = mock_wave_instance
            mock_play_object = MagicMock()
            mock_wave_instance.play.return_value = mock_play_object

            # Test 1: Initialization with a valid sound filename
            valid_sound_1 = GC.MCLAREN_F1_FILENAME
            log_info(f"Test 1: Initializing with valid sound: {valid_sound_1}")
            gen1 = EngineSoundGenerator(valid_sound_1)

            expected_path_1 = str(GC.SOUNDS_BASE_PATH / valid_sound_1)
            MockWaveObjectConstructor.from_wave_file.assert_called_with(expected_path_1)
            assert gen1.get_base_audio_filename() == valid_sound_1,                 f"Test 1 FAIL: Expected {valid_sound_1}, got {gen1.get_base_audio_filename()}"

            play_obj1 = gen1.start_audio()
            if play_obj1: # Check if play_obj was returned (sound loaded)
                mock_wave_instance.play.assert_called_once()
                gen1.stop_audio(play_obj1)
                mock_play_object.stop.assert_called_once()
            log_info(f"Test 1 PASS: Correctly processed {valid_sound_1}")

            MockWaveObjectConstructor.from_wave_file.reset_mock()
            mock_wave_instance.play.reset_mock()
            if mock_play_object: mock_play_object.stop.reset_mock()

            # Test 2: Initialization with None
            log_info(f"Test 2: Initializing with None")
            gen2 = EngineSoundGenerator(None)
            MockWaveObjectConstructor.from_wave_file.assert_not_called()
            assert gen2.get_base_audio_filename() is None,                 f"Test 2 FAIL: Expected None for init with None, got {gen2.get_base_audio_filename()}"
            log_info(f"Test 2 PASS: Correctly handled init with None. Current sound: {gen2.get_base_audio_filename()}")

            # Test 3: Simulating FileNotFoundError when loading a valid dictionary sound
            valid_sound_for_error_sim = GC.BMW_M4_FILENAME
            MockWaveObjectConstructor.from_wave_file.side_effect = FileNotFoundError("Simulated File Not Found")
            log_info(f"Test 3: Simulating FileNotFoundError for {valid_sound_for_error_sim}")
            gen3 = EngineSoundGenerator(valid_sound_for_error_sim)
            expected_path_3 = str(GC.SOUNDS_BASE_PATH / valid_sound_for_error_sim)
            MockWaveObjectConstructor.from_wave_file.assert_called_with(expected_path_3)
            assert gen3.get_base_audio_filename() is None,                  f"Test 3 FAIL: Expected None after FileNotFoundError on init, got {gen3.get_base_audio_filename()}"
            log_info(f"Test 3 PASS: Correctly handled FileNotFoundError on init. Current sound: {gen3.get_base_audio_filename()}")

            MockWaveObjectConstructor.from_wave_file.side_effect = None
            MockWaveObjectConstructor.from_wave_file.return_value = mock_wave_instance
            MockWaveObjectConstructor.from_wave_file.reset_mock()

            # Test 4: Setting a new valid sound after initial valid sound (gen1)
            valid_sound_2 = GC.PORSCHE_911_FILENAME
            log_info(f"Test 4: Setting from {gen1.get_base_audio_filename()} to new valid sound: {valid_sound_2}")
            gen1.set_engine_sound(valid_sound_2)
            expected_path_4 = str(GC.SOUNDS_BASE_PATH / valid_sound_2)
            MockWaveObjectConstructor.from_wave_file.assert_called_with(expected_path_4)
            assert gen1.get_base_audio_filename() == valid_sound_2,                 f"Test 4 FAIL: Expected {valid_sound_2}, got {gen1.get_base_audio_filename()}"
            log_info(f"Test 4 PASS: Successfully set new sound to {valid_sound_2}")

            # Test 5: Attempting to set a sound not in dict, after a valid sound was set (gen1)
            invalid_sound_dict = "sound_not_in_dict.wav"
            current_valid_sound_in_gen1 = gen1.get_base_audio_filename()
            log_info(f"Test 5: Attempting to set sound not in dict '{invalid_sound_dict}' over '{current_valid_sound_in_gen1}'")
            MockWaveObjectConstructor.from_wave_file.reset_mock()
            gen1.set_engine_sound(invalid_sound_dict)
            MockWaveObjectConstructor.from_wave_file.assert_not_called()
            assert gen1.get_base_audio_filename() == current_valid_sound_in_gen1,                 f"Test 5 FAIL: Expected sound to remain {current_valid_sound_in_gen1}, got {gen1.get_base_audio_filename()}"
            log_info(f"Test 5 PASS: Sound correctly remained {current_valid_sound_in_gen1}")

        log_info("EngineSoundGenerator.py Unit Test (with mocks) Finished.")

if __name__ == "__main__":
    EngineSoundGenerator.unit_test()
